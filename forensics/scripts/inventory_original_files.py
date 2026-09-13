#!/usr/bin/env python3
"""Inventory immutable local source bytes; write metadata only outside orginal/."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]


def inspect_bytes(data):
    """Detect package contents before assigning extension-derived roles."""
    stream = io.BytesIO(data)
    if zipfile.is_zipfile(stream):
        with zipfile.ZipFile(stream) as archive:
            names = archive.namelist()
            bad = archive.testzip()
            if "[Content_Types].xml" in names and "xl/workbook.xml" in names:
                return "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "OOXML ZIP container", "CRC OK" if bad is None else f"bad CRC: {bad}"
            return "zip", "application/zip", "archive", "CRC OK" if bad is None else f"bad CRC: {bad}"
    if data.startswith(b"%PDF-"):
        try:
            reader = PdfReader(io.BytesIO(data))
            return "pdf", "application/pdf", "not archive", f"parsed {len(reader.pages)} pages"
        except Exception as error:
            return "pdf", "application/pdf", "not archive", f"parse error: {error}"
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*"):
            return "tar", "application/x-tar", "archive", "headers parsed"
    except (tarfile.TarError, OSError):
        pass
    try:
        decoded = data.decode("utf-8")
        if "\x00" not in decoded:
            return "text", "text/plain; charset=utf-8", "not archive", "UTF-8 decoded"
    except UnicodeDecodeError:
        pass
    return "binary", "application/octet-stream", "not recognized", "unclassified"


def infer_role(relative_path, kind):
    name = Path(relative_path).name
    match = re.search(r"41929_2025_1291_MOESM(\d+)_ESM", name)
    package = f"MOESM{match.group(1)}" if match else ""
    number = int(match.group(1)) if match else None
    if name == "s41929-025-01291-z.pdf" and kind == "pdf":
        return package, "article PDF", "Identity from paper filename; article text audited separately"
    if number == 1 and kind == "pdf":
        return package, "Supplementary Information PDF", "Publisher-package identifier encoded in filename"
    if number == 2 and kind == "xlsx":
        return package, "Supplementary Data 1 workbook", "Supplementary figure source data; detailed workbook audit separate"
    if number in range(3, 9) and kind == "text":
        label = {3: "GS", 4: "TI1", 5: "MS", 6: "TI2", 7: "TI3", 8: "TI4"}[number]
        return package, "optimized computational structure", f"Supplementary Data {number - 1}: {label}; direct publisher package description"
    if number in range(11, 14) and kind == "xlsx":
        return package, f"Source Data Fig. {number - 10} workbook", "Figure-package mapping checked separately against publisher page"
    if number == 14 and kind == "xlsx":
        return package, "Source Data Extended Data Fig. 4 (publisher label)", "Workbook sheet says Extended Data Fig. 3; publisher/workbook label discrepancy"
    if relative_path.startswith("MD_configurations/") and kind == "text":
        return "MOESM9 (inferred extracted package)", "MD initial/final structure", "Local expanded directory; original downloaded archive is not present"
    return package, kind, "No role established"


def archive_rows(data, parent, rows):
    """Read nested archives in memory; never extract publisher contents to disk."""
    kind, _, _, _ = inspect_bytes(data)
    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = [(member.filename, archive.read(member)) for member in archive.infolist() if not member.is_dir()]
    elif kind == "tar":
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = [(member.name, archive.extractfile(member).read()) for member in archive if member.isfile()]
    else:
        return
    for name, content in members:
        child_kind, mime, status, parse_status = inspect_bytes(content)
        full_name = f"{parent}!/{name}"
        package, role, note = infer_role(name, child_kind)
        rows.append({"container": parent, "member_path": name, "byte_size": len(content), "sha256": hashlib.sha256(content).hexdigest(), "detected_type": child_kind, "mime_type": mime, "archive_status": status, "parse_status": parse_status, "package_id": package, "inferred_role": role, "notes": note})
        archive_rows(content, full_name, rows)


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    source = args.root / "orginal"
    output = args.root / "data/manifests"
    output.mkdir(parents=True, exist_ok=True)
    rows, members = [], []
    hashes = defaultdict(list)
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        hashes[digest].append(relative)
        kind, mime, archive_status, parse_status = inspect_bytes(data)
        package, role, note = infer_role(relative, kind)
        rows.append({"relative_path": relative, "filename": path.name, "extension": path.suffix.lower(), "byte_size": len(data), "sha256": digest, "detected_type": kind, "mime_type": mime, "archive_status": archive_status, "parse_status": parse_status, "package_id": package, "inferred_role": role, "notes": note})
        archive_rows(data, relative, members)
    write_csv(output / "original-files.csv", rows)
    if members:
        write_csv(output / "archive-contents.csv", members)
    duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    summary = {"source_directory": "orginal", "file_count": len(rows), "total_bytes": sum(row["byte_size"] for row in rows), "detected_types": dict(sorted(Counter(row["detected_type"] for row in rows).items())), "roles": dict(sorted(Counter(row["inferred_role"] for row in rows).items())), "archive_count": sum(row["archive_status"] == "archive" for row in rows), "archive_member_count": len(members), "ooxml_container_count": sum(row["detected_type"] == "xlsx" for row in rows), "duplicate_byte_groups": duplicates, "maximum_file_bytes": max(row["byte_size"] for row in rows), "over_100_mib_count": sum(row["byte_size"] > 100 * 1024**2 for row in rows), "pdf_parse_status": {row["relative_path"]: row["parse_status"] for row in rows if row["detected_type"] == "pdf"}, "notes": ["Every original file was hashed and inspected by content, not extension alone.", "XLSX internal ZIP packages are CRC checked; their XML, relationships and embedded objects are audited by inspect_workbooks.py.", "No original-source contents are written by this script.", "Package roles are metadata interpretations and must be reconciled with publisher documentation."]}
    (output / "original-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("file_count", "total_bytes", "detected_types", "archive_count", "archive_member_count", "maximum_file_bytes")}, indent=2))


if __name__ == "__main__":
    main()
