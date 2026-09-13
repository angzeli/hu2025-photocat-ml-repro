#!/usr/bin/env python3
"""Read local XLSX evidence without saving source data or modifying workbooks."""

from collections import Counter
from pathlib import Path
import argparse
import json
import posixpath
import xml.etree.ElementTree as ET
import zipfile

import openpyxl
from openpyxl.utils.cell import get_column_letter


ROOT = Path(__file__).resolve().parents[2]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def local_tag(tag):
    return tag.rsplit("}", 1)[-1]


def inspect(path, source_label=None):
    result = {"source": source_label or path.relative_to(ROOT).as_posix()}
    with zipfile.ZipFile(path) as archive:
        result["zip_crc_error"] = archive.testzip()
        parts = archive.namelist()
        xml = {}
        for name in parts:
            if name.endswith((".xml", ".rels")):
                xml[name] = ET.fromstring(archive.read(name))
        result["package"] = {
            "part_count": len(parts),
            "parsed_xml_parts": len(xml),
            "external_relationships": [],
            "relationships": [],
            "special_parts": [],
        }
        for name, node in xml.items():
            if name.endswith(".rels"):
                for rel in node:
                    entry = {"part": name, **rel.attrib}
                    result["package"]["relationships"].append(entry)
                    if rel.get("TargetMode") == "External":
                        result["package"]["external_relationships"].append(entry)
        for name in parts:
            if any(x in name.lower() for x in (
                "chart", "embedding", "externallink", "comment", "vba", "customxml",
                "connection", "pivot", "query", "drawing", "media/", "metadata.xml",
            )):
                info = archive.getinfo(name)
                entry = {"part": name, "bytes": info.file_size}
                if name in xml:
                    counts = Counter(local_tag(e.tag) for e in xml[name].iter())
                    entry["element_counts"] = dict(sorted(counts.items()))
                result["package"]["special_parts"].append(entry)
        result["metadata"] = {}
        for name in ("docProps/core.xml", "docProps/app.xml", "docProps/custom.xml"):
            if name in xml:
                result["metadata"][name] = {
                    local_tag(child.tag): child.text
                    for child in xml[name] if child.text and child.text.strip()
                }
        if "docProps/custom.xml" in xml:
            result["metadata"]["docProps/custom.xml"] = {
                child.get("name"): "".join(child.itertext())
                for child in xml["docProps/custom.xml"]
            }
        shared = xml.get("xl/sharedStrings.xml")
        if shared is not None:
            strings = list(shared)
            used = {int(cell.find("s:v", NS).text)
                    for name, node in xml.items() if name.startswith("xl/worksheets/sheet")
                    for cell in node.findall("s:sheetData/s:row/s:c", NS)
                    if cell.get("t") == "s"}
            orphaned = [i for i in range(len(strings)) if i not in used]
            result["package"]["shared_strings"] = {
                "unique_entries": len(strings), "referenced_entries": len(used),
                "unreferenced_entries": len(orphaned),
                "unreferenced_text_lengths": [len("".join(strings[i].itertext())) for i in orphaned],
            }
        wb_xml = xml["xl/workbook.xml"]
        result["workbook_xml_settings"] = {
            local_tag(n.tag): n.attrib for n in wb_xml
            if local_tag(n.tag) in ("fileVersion", "workbookPr", "calcPr", "workbookProtection")
        }
        rels = {n.get("Id"): n.get("Target") for n in xml["xl/_rels/workbook.xml.rels"]}
        sheet_parts = {}
        for node in wb_xml.find("s:sheets", NS):
            rid = next(v for k, v in node.attrib.items() if local_tag(k) == "id")
            target = rels[rid]
            sheet_parts[node.get("name")] = (
                target.lstrip("/") if target.startswith("/")
                else posixpath.normpath(posixpath.join("xl", target))
            )

        workbook = openpyxl.load_workbook(path, data_only=False, keep_links=True)
        result["defined_names"] = [
            {"name": key, "type": value.type, "target": value.attr_text}
            for key, value in workbook.defined_names.items()
        ]
        result["sheets"] = []
        for index, sheet in enumerate(workbook, 1):
            node = xml[sheet_parts[sheet.title]]
            cells = list(node.findall("s:sheetData/s:row/s:c", NS))
            formulas = [c for c in cells if c.find("s:f", NS) is not None]
            useful = [c for row in sheet for c in row if c.value is not None]
            by_column = {}
            for col in sorted({c.column for c in useful}):
                occupied = [c for c in useful if c.column == col]
                numeric = [c for c in occupied if isinstance(c.value, (int, float))]
                by_column[get_column_letter(col)] = {
                    "nonempty_count": len(occupied), "numeric_count": len(numeric),
                    "first_nonempty_row": min(c.row for c in occupied),
                    "last_nonempty_row": max(c.row for c in occupied),
                    "numeric_row_span": [min(c.row for c in numeric), max(c.row for c in numeric)]
                    if numeric else None,
                }
            entry = {
                "name": sheet.title, "order": index, "state": sheet.sheet_state,
                "ooxml_dimension": node.find("s:dimension", NS).get("ref"),
                "parsed_cell_extent": sheet.calculate_dimension(),
                "actual_nonempty_bounds": [min(c.row for c in useful), min(c.column for c in useful),
                                           max(c.row for c in useful), max(c.column for c in useful)]
                if useful else None,
                "nonempty_cells": len(useful), "serialized_cells": len(cells),
                "empty_serialized_cells": sum(c.find("s:v", NS) is None and c.find("s:is", NS) is None
                                              and c.find("s:f", NS) is None for c in cells),
                "cell_type_counts": dict(sorted(Counter(c.data_type for c in useful).items())),
                "formula_count": len(formulas),
                "formula_cache_nonempty_count": sum(c.find("s:v", NS) is not None
                    and c.find("s:v", NS).text is not None for c in formulas),
                "formula_cache_missing_count": sum(c.find("s:v", NS) is None
                    or c.find("s:v", NS).text is None for c in formulas),
                "merged_ranges": sorted(str(r) for r in sheet.merged_cells.ranges),
                "hidden_rows": [i for i, dim in sheet.row_dimensions.items() if dim.hidden],
                "hidden_columns": [{"key": i, "min": d.min, "max": d.max}
                                   for i, d in sheet.column_dimensions.items() if d.hidden],
                "comments": [{"cell": c.coordinate, "length": len(c.comment.text),
                              "author": c.comment.author} for c in useful if c.comment],
                "hyperlink_cells": [c.coordinate for c in useful if c.hyperlink],
                "chart_count": len(sheet._charts), "image_count": len(sheet._images),
                "tables": list(sheet.tables),
                "autofilter_ref": sheet.auto_filter.ref,
                "sheet_defined_names": [{"name": k, "target": v.attr_text}
                                        for k, v in sheet.defined_names.items()],
                "data_validation_count": len(sheet.data_validations.dataValidation),
                "conditional_format_count": len(sheet.conditional_formatting),
                "columns": by_column,
                # Header metadata only; never export numerical rows or full text tables.
                "top_header_labels": [{"cell": c.coordinate, "label": c.value}
                    for c in useful if c.row <= 3 and c.data_type == "s"],
            }
            result["sheets"].append(entry)
        workbook.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "orginal")
    parser.add_argument("--output", type=Path, default=ROOT / "forensics/outputs/workbook_audit.json")
    args = parser.parse_args()
    books = [inspect(p) for p in sorted(args.source_dir.rglob("*.xlsx"))]
    other = [p.relative_to(ROOT).as_posix() for p in sorted(args.source_dir.rglob("*"))
             if p.suffix.lower() in (".xls", ".csv", ".tsv")]
    output = {"method": "Read-only openpyxl plus complete OOXML XML/relationship scan; no source export.",
              "workbook_count": len(books), "other_top_level_tabular_files": other,
              "workbooks": books}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"Inspected {len(books)} workbooks; metadata only: {args.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
