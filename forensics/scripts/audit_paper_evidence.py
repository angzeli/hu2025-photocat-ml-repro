#!/usr/bin/env python3
"""Cross-check selected SI tables against workbooks; save only derived summaries."""

import csv
import json
import re
from pathlib import Path

from openpyxl import load_workbook
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "orginal"
OUTPUT = ROOT / "forensics/outputs/paper_table_checks.json"


def main():
    si = PdfReader(SOURCE / "41929_2025_1291_MOESM1_ESM.pdf")
    # PDF page numbers are one-based; printed SI numbers are one lower.
    cat_text = "\n".join(si.pages[i].extract_text() for i in range(72, 75))
    catalysts = {
        int(index): float(value.replace("−", "-"))
        for index, value in re.findall(r"CAT\s+(\d+)\s+([−-]?\d+\.\d+)", cat_text)
    }
    photosensitizers = {
        int(index): int(value)
        for index, value in re.findall(r"PS\s+(\d+)\s+(\d+)", si.pages[75].extract_text())
    }
    assert set(catalysts) == set(range(1, 85))
    assert set(photosensitizers) == set(range(1, 42))

    supplemental = load_workbook(SOURCE / "41929_2025_1291_MOESM2_ESM.xlsx", read_only=True, data_only=True)
    descriptor_values = {}
    for number, label in [(1, "catalyst"), (2, "photosensitizer")]:
        descriptor_values[label] = [
            row[0] for row in supplemental[f"Supplementary Fig. {number}"].iter_rows(min_row=2, values_only=True)
            if isinstance(row[0], (int, float))
        ]
    assert len(descriptor_values["catalyst"]) == 84
    assert len(descriptor_values["photosensitizer"]) == 41
    cat_rounding_mismatches = [
        i for i, value in enumerate(descriptor_values["catalyst"], 1)
        if abs(value - catalysts[i]) > 0.00005001
    ]
    ps_rounding_mismatches = [
        i for i, value in enumerate(descriptor_values["photosensitizer"], 1)
        if abs(value - photosensitizers[i]) > 0.500001
    ]

    table_text = "\n".join(si.pages[i].extract_text() for i in (76, 77))
    values = r"(?:\d+(?:\.\d+)?|−)"
    pattern = re.compile(rf"CAT\s+(\d+)\s+PS\s+(\d+)\s+({values})\s+({values})\s+({values})\s+({values})")
    table_rows = []
    for cat, ps, ton, tof, selectivity, time in pattern.findall(table_text):
        table_rows.append({
            "cat": int(cat), "ps": int(ps),
            "ton": None if ton == "−" else float(ton),
            "tof_per_hour": None if tof == "−" else float(tof),
            "selectivity": None if selectivity == "−" else float(selectivity),
            "irradiation_hours": None if time == "−" else float(time),
        })
    assert len(table_rows) == 44
    assert (table_rows[3]["cat"], table_rows[3]["ps"], table_rows[3]["ton"]) == (50, 41, None)
    # Membership is the visually checked group boundary in SI Table 3, not performance rank.
    measured_filtered = [row for row in table_rows[:7] if row["ton"] is not None]
    ruled_out = table_rows[7:]
    local_only = ROOT / "forensics/local_only"
    local_only.mkdir(parents=True, exist_ok=True)
    with (local_only / "si_table3_source.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0]))
        writer.writeheader()
        writer.writerows(table_rows)
    assert len(measured_filtered) == 6 and len(ruled_out) == 37
    measured_by_id = {(row["cat"], row["ps"]): row for row in table_rows if row["ton"] is not None}
    fig1 = load_workbook(SOURCE / "41929_2025_1291_MOESM11_ESM.xlsx", read_only=True, data_only=True)
    workbook_rows = [row for row in fig1["Fig.1e"].iter_rows(min_row=2, values_only=True) if row[0] is not None]
    discrepancies = []
    for cat_label, ps_label, ton, selectivity in workbook_rows:
        key = (int(cat_label.split()[-1]), int(ps_label.split()[-1]))
        si_row = measured_by_id[key]
        if ton != si_row["ton"] or selectivity != si_row["selectivity"]:
            discrepancies.append({"cat_id": key[0], "ps_id": key[1]})
    assert len(workbook_rows) == len(measured_by_id) == 43

    # Illustrative joint rule suggested by the prose/figure, not an author-disclosed classifier.
    good = lambda row: row["ton"] > 1370 and row["selectivity"] > 72
    true_positives = sum(map(good, measured_filtered))
    false_positives = len(measured_filtered) - true_positives
    false_negatives = sum(map(good, ruled_out))
    true_negatives = len(ruled_out) - false_negatives
    ruled_out_except_exception = [row for row in ruled_out if (row["cat"], row["ps"]) != (61, 33)]
    result = {
        "sources": {
            "si": "orginal/41929_2025_1291_MOESM1_ESM.pdf; PDF pages 73-78, printed SI pages 72-77",
            "descriptors": "orginal/41929_2025_1291_MOESM2_ESM.xlsx; Supplementary Fig. 1 and 2",
            "validation": "orginal/41929_2025_1291_MOESM11_ESM.xlsx; Fig.1e",
        },
        "table1_count": len(catalysts), "table2_count": len(photosensitizers),
        "cat_index_order_rounding_mismatches": cat_rounding_mismatches,
        "ps_index_order_rounding_mismatches": ps_rounding_mismatches,
        "table3": {
            "rows_including_unmeasured": len(table_rows), "filtered": 7, "filtered_measured": 6,
            "ruled_out_measured": 37, "fig1e_measured_rows": len(workbook_rows),
            "workbook_si_value_discrepancies": discrepancies,
            "unmeasured_identity": {"cat_id": 50, "ps_id": 41},
            "additional_source_columns": ["TOF_CO (h^-1)", "irradiation time (h)"],
            "complete_table_storage": "ignored forensics/local_only/si_table3_source.csv only",
            "illustrative_joint_rule": "TON_CO > 1370 AND CO selectivity (%) > 72; not uniquely specified by authors",
            "true_positive": true_positives, "false_positive": false_positives,
            "false_negative": false_negatives, "true_negative": true_negatives,
            "conditional_precision": true_positives / (true_positives + false_positives),
            "conditional_recall": true_positives / (true_positives + false_negatives),
            "other_ruled_out_TON_not_below_1370": sum(row["ton"] >= 1370 for row in ruled_out_except_exception),
            "other_ruled_out_selectivity_not_below_72": sum(row["selectivity"] >= 72 for row in ruled_out_except_exception),
        },
        "boundary": "Tracked outputs contain counts/concordance/classifications; complete table extraction remains in ignored local_only.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
