#!/usr/bin/env python3
"""Compare separately downloaded publisher workbooks with immutable local copies."""

from collections import Counter
from decimal import Decimal
from pathlib import Path
import argparse
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

from inspect_workbooks import ROOT, NS, inspect


def cell_content(path):
    """Resolve cells in memory; never serialize source values into audit outputs."""
    with zipfile.ZipFile(path) as archive:
        xml = {n: ET.fromstring(archive.read(n)) for n in archive.namelist() if n.endswith(".xml")}
    shared = xml.get("xl/sharedStrings.xml")
    strings = ["".join(t.text or "" for t in element.findall(".//s:t", NS)) for element in shared]
    output = {}
    for name, node in xml.items():
        if not name.startswith("xl/worksheets/sheet"):
            continue
        content = {}
        for cell in node.findall("s:sheetData/s:row/s:c", NS):
            typ, val = cell.get("t", "n"), cell.find("s:v", NS)
            formula, inline = cell.find("s:f", NS), cell.find("s:is", NS)
            if formula is not None:
                content[cell.get("r")] = ("f", formula.text, None if val is None else val.text)
            elif inline is not None:
                content[cell.get("r")] = ("text", "".join(inline.itertext()))
            elif val is not None and val.text is not None:
                if typ == "s":
                    content[cell.get("r")] = ("text", strings[int(val.text)])
                elif typ == "n":
                    content[cell.get("r")] = ("number", Decimal(val.text))
                else:
                    content[cell.get("r")] = (typ, val.text)
        output[name] = content
    return output


def compare(local_path, publisher_path, local_metadata, recorded_hash):
    publisher_hash = hashlib.file_digest(publisher_path.open("rb"), "sha256").hexdigest()
    publisher_metadata = inspect(publisher_path, source_label=publisher_path.name)
    left, right = cell_content(local_path), cell_content(publisher_path)
    sheets = []
    for name in sorted(left.keys() | right.keys()):
        lc, pc = left.get(name, {}), right.get(name, {})
        mismatches, types, maximum_delta = [], Counter(), Decimal(0)
        for cell in sorted(lc.keys() | pc.keys()):
            if lc.get(cell) == pc.get(cell):
                continue
            lv, pv = lc.get(cell), pc.get(cell)
            if lv and pv and lv[0] == pv[0] == "number":
                delta = abs(lv[1]-pv[1])
                maximum_delta = max(maximum_delta, delta)
                kind = "numeric_serialized_value"
            else:
                kind = "text_formula_type_or_presence"
            types[kind] += 1
            if len(mismatches) < 20:
                mismatches.append(cell)
        sheets.append({"part": name, "local_nonempty_cells": len(lc),
            "publisher_nonempty_cells": len(pc), "different_cells": sum(types.values()),
            "difference_types": dict(types), "first_difference_coordinates": mismatches,
            "maximum_absolute_numeric_difference": str(maximum_delta)})
    structure_fields = ("name", "order", "state", "actual_nonempty_bounds", "formula_count",
        "formula_cache_nonempty_count", "merged_ranges", "hidden_rows", "hidden_columns",
        "comments", "hyperlink_cells", "chart_count", "image_count", "tables", "sheet_defined_names")
    ls, ps = local_metadata["sheets"], publisher_metadata["sheets"]
    structural_differences = []
    for lsheet, psheet in zip(ls, ps):
        for field in structure_fields:
            if lsheet[field] != psheet[field]:
                structural_differences.append({"sheet": lsheet["name"], "field": field})
    if len(ls) != len(ps):
        structural_differences.append({"field": "sheet_count"})
    return {"local_source": local_path.relative_to(ROOT).as_posix(),
        "publisher_download_filename": publisher_path.name,
        "publisher_url": "https://media.springernature.com/original/springer-static/esm/"
            "art%3A10.1038%2Fs41929-025-01291-z/MediaObjects/" + local_path.name,
        "local_sha256_from_manifest": recorded_hash,
        "publisher_download_sha256": publisher_hash,
        "byte_identical": publisher_hash == recorded_hash,
        "all_nonempty_cell_content_identical": all(s["different_cells"] == 0 for s in sheets),
        "sheet_comparisons": sheets,
        "structural_differences": structural_differences,
        "publisher_metadata": publisher_metadata["metadata"],
        "publisher_package_scan": publisher_metadata["package"],
        "publisher_workbook_settings": publisher_metadata["workbook_xml_settings"],
        "publisher_defined_names": publisher_metadata["defined_names"],
        "publisher_integrity": {"zip_crc_error": publisher_metadata["zip_crc_error"]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", nargs=2, action="append", required=True,
                        metavar=("LOCAL_XLSX", "PUBLISHER_DOWNLOAD"))
    parser.add_argument("--output", type=Path, default=ROOT / "forensics/outputs/publisher_comparison.json")
    args = parser.parse_args()
    destination = args.output.resolve()
    protected = [(ROOT / "orginal").resolve(), (ROOT / ".git").resolve()]
    inputs = {Path(path).resolve() for pair in args.pair for path in pair}
    if destination in inputs or any(destination == path or path in destination.parents for path in protected):
        parser.error("--output must not overwrite source inputs or Git internals")
    local_audit = json.loads((ROOT / "forensics/outputs/workbook_audit.json").read_text())
    metadata = {Path(w["source"]).name: w for w in local_audit["workbooks"]}
    with (ROOT / "data/manifests/original-files.csv").open() as handle:
        hashes = {row["relative_path"]: row["sha256"] for row in csv.DictReader(handle)}
    results = [compare(Path(local).resolve(), Path(publisher).resolve(), metadata[Path(local).name],
                       hashes[Path(local).name]) for local, publisher in args.pair]
    args.output.write_text(json.dumps({"method": "All nonempty cells compared as resolved strings, formulas or exact decimal numbers. No cell values exported.",
        "comparisons": results}, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps([{k: r[k] for k in ("local_source", "byte_identical",
                        "all_nonempty_cell_content_identical", "structural_differences")} for r in results]))


if __name__ == "__main__":
    main()
