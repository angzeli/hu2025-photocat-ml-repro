#!/usr/bin/env python3
"""Recompute released dipole/coupling metrics; keep source arrays local-only."""

from pathlib import Path
import csv
import json

import numpy as np
import openpyxl


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "orginal/41929_2025_1291_MOESM2_ESM.xlsx"
TARGETS = {5: "catalyst_intrinsic", 6: "photosensitizer_intrinsic",
           7: "catalyst_transition", 8: "photosensitizer_transition"}


def metrics(actual, predicted):
    actual, predicted = np.asarray(actual).ravel(), np.asarray(predicted).ravel()
    if actual.shape != predicted.shape or not np.isfinite([actual, predicted]).all():
        raise ValueError("Paired, finite numerical data required")
    residual = predicted - actual
    sst = np.sum((actual - actual.mean()) ** 2)
    return {
        "n_values": len(actual),
        "pearson_r": float(np.corrcoef(actual, predicted)[0, 1]),
        "r2": float(1 - np.sum(residual ** 2) / sst),
        "mae": float(np.mean(np.abs(residual))),
        "rmse": float(np.sqrt(np.mean(residual ** 2))),
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def tensor_product(catalyst, photosensitizer):
    """Fixed x-axis dipole-tensor numerator, tested as a forensic hypothesis."""
    return np.sum(catalyst * photosensitizer * [-2, 1, 1], axis=1)


def main():
    workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    dipoles, metric_rows = {}, []
    for figure, target in TARGETS.items():
        sheet = workbook[f"Supplementary Fig. {figure}"]
        values = list(sheet.values)
        local_rows = []
        for split, first, count in (("train", 0, 900), ("test", 2, 100)):
            positions = [first + offset for offset in (0, 1, 5, 6, 10, 11)]
            rows = [(i, [row[c] for c in positions])
                    for i, row in enumerate(values[3:], 4)
                    if any(row[c] is not None for c in positions)]
            matrix = np.array([numbers for _, numbers in rows], dtype=float)
            if matrix.shape != (count, 6) or not np.isfinite(matrix).all():
                raise ValueError(f"Unexpected or incomplete layout: figure {figure} {split}")
            actual, predicted = matrix[:, ::2], matrix[:, 1::2]
            dipoles[figure, split] = (actual, predicted)
            for j, component in enumerate(("x", "y", "z", "pooled_xyz")):
                x, y = (actual, predicted) if j == 3 else (actual[:, j], predicted[:, j])
                metric_rows.append({"figure": figure, "target": target, "split": split,
                    "component": component, "n_samples": count, "units": "not_specified",
                    **metrics(x, y)})
            for i, (source_row, numbers) in enumerate(rows, 1):
                local_rows.append({"split": split, "index_within_split": i,
                    "source_excel_row": source_row,
                    **dict(zip(("calculated_x", "predicted_x", "calculated_y",
                                "predicted_y", "calculated_z", "predicted_z"), numbers))})
        write_csv(ROOT / f"forensics/local_only/supfig{figure}_dipoles.csv", local_rows)
    write_csv(ROOT / "data/derived/ml_metrics.csv", metric_rows)

    values = list(workbook["Supplementary Fig. 9"].values)
    coupling = np.array([[row[c] for c in (0, 1, 3, 4)] for row in values[2:]], dtype=float)
    if coupling.shape != (1000, 4) or not np.isfinite(coupling).all():
        raise ValueError("Supplementary Fig. 9 is not a complete 1000 by 4 numerical block")
    write_csv(ROOT / "forensics/local_only/supfig9_couplings.csv", [
        {"source_excel_row": i, **dict(zip(("J_calculated", "J_predicted",
                                           "Jstar_calculated", "Jstar_predicted"), row))}
        for i, row in enumerate(coupling, 3)])
    coupling_rows = []
    for j, name in enumerate(("J", "Jstar")):
        actual, predicted = coupling[:, 2*j], coupling[:, 2*j+1]
        row = {"coupling": name, "units": "not_specified", **metrics(actual, predicted)}
        for label, series in (("calculated", actual), ("predicted", predicted)):
            row.update({f"{label}_min": float(series.min()), f"{label}_max": float(series.max()),
                f"{label}_negative": int(np.sum(series < 0)),
                f"{label}_zero": int(np.sum(series == 0)),
                f"{label}_positive": int(np.sum(series > 0))})
        row["opposite_sign_pairs"] = int(np.sum(actual * predicted < 0))
        coupling_rows.append(row)
    write_csv(ROOT / "data/derived/supfig9_coupling_metrics.csv", coupling_rows)

    # One scalar determined from the first 900 calculated intrinsic rows is held
    # fixed for all other channels and rows. This tests numerical provenance,
    # not a trained predictor or a recovered physical distance/unit convention.
    vectors = {figure: tuple(np.vstack([dipoles[figure, s][k] for s in ("train", "test")])
                             for k in (0, 1)) for figure in TARGETS}
    numerator = tensor_product(vectors[5][0], vectors[6][0])
    scale = float(np.dot(numerator[:900], coupling[:900, 0]) / np.dot(numerator[:900], numerator[:900]))
    probes = []
    rng = np.random.default_rng(20250913)
    permutations = [rng.permutation(1000) for _ in range(100)]
    for j, (name, cat, ps) in enumerate((("J", 5, 6), ("Jstar", 7, 8))):
        for channel, k in (("calculated", 0), ("predicted", 1)):
            observed = coupling[:, 2*j+k]
            f = tensor_product(vectors[cat][k], vectors[ps][k])
            reconstructed = scale * f
            free_scale = float(np.dot(f, observed) / np.dot(f, f))
            permuted_r = [metrics(observed, reconstructed[p])["pearson_r"] for p in permutations]
            probe = {"coupling": name, "channel": channel,
                "shared_fixed_scale_metrics": metrics(observed, reconstructed),
                "first_900_metrics": metrics(observed[:900], reconstructed[:900]),
                "last_100_metrics": metrics(observed[900:], reconstructed[900:]),
                "channel_descriptive_scale": free_scale,
                "maximum_absolute_residual": float(np.max(np.abs(observed - reconstructed))),
                "absolute_residual_quantiles": {str(q): float(np.quantile(abs(observed-reconstructed), q))
                                                for q in (0.5, 0.95, 0.99)},
                "test_then_train_control": metrics(observed, np.concatenate([reconstructed[900:], reconstructed[:900]])),
                "one_row_shift_control": metrics(observed, np.roll(reconstructed, 1)),
                "permutation_control": {"count": 100, "seed": 20250913,
                    "min_pearson_r": min(permuted_r), "max_pearson_r": max(permuted_r)},
            }
            probes.append(probe)
    workbook.close()

    result = {
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_axis_interpretation": "SI PDF pp13-17: horizontal calculated; vertical predicted; a/b/c=x/y/z.",
        "source_ranges": {"fig5_to_8_train": ["A4:B903", "F4:G903", "K4:L903"],
                          "fig5_to_8_test": ["C4:D103", "H4:I103", "M4:N103"],
                          "fig9": ["A3:B1002", "D3:E1002"]},
        "metric_definitions": {"r2": "1 - sum((predicted-calculated)^2)/sum((calculated-mean(calculated))^2)",
            "pearson_r": "Centered Pearson correlation, not squared",
            "mae": "mean(abs(predicted-calculated))", "rmse": "sqrt(mean((predicted-calculated)^2))",
            "pooled_xyz": "Flatten all three components: 2700 train values or 300 test values; not independent conformations."},
        "unit_status": "Not specified in workbook labels or SI Fig.5-9 axes/captions. Do not assign Debye or energy units.",
        "ml_metrics": metric_rows, "coupling_metrics": coupling_rows,
        "row_alignment": {
            "classification": "strongly supported for numerical pairing within intrinsic and transition blocks; common structural identity unproven",
            "sequence": "Train rows 4:903 followed by test rows 4:103, independently for every dipole sheet",
            "equation": "J_or_Jstar = s * (-2*CAT_x*PS_x + CAT_y*PS_y + CAT_z*PS_z)",
            "shared_scale": scale,
            "scale_estimation": "Zero-intercept scalar proportionality from first 900 calculated J rows only",
            "probes": probes,
            "physical_interpretation": "Consistent with a fixed dipole tensor whose separation axis is x. It does not recover distance, units, dielectric factor, or original coordinate convention.",
            "within_intrinsic_5_6_to_9a": "strongly supported",
            "within_transition_7_8_to_9b": "strongly supported",
            "all_four_targets_same_structural_conformation_pair": "plausible",
            "missing": ["Molecule/conformation/snapshot IDs in dipole and coupling rows",
                        "A mapping from released numerical rows to coordinate files",
                        "Explicit correspondence between intrinsic and transition structural samples",
                        "Original train/test assignment indices before separate plotted blocks"],
            "limitation": "Numerical row consistency is strong evidence of calculation ordering, not proof of shared physical conformations or recovery of ML input X.",
        },
        "source_array_storage": "Complete recovered arrays only in ignored forensics/local_only/; never stage or commit these CSV files.",
    }
    output = ROOT / "forensics/outputs/ml_analysis.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    write_report(result)
    print("Computed 32 dipole metric rows, 2 coupling summaries, and 4 alignment probes; raw arrays remain local-only.")


def write_report(result):
    audit_path = ROOT / "forensics/outputs/workbook_audit.json"
    audit = json.loads(audit_path.read_text())
    lines = ["# Workbook and ML source-data audit", "",
        "All workbooks were read without saving or modifying the source. The OOXML pass parsed every XML/relationship part and checked ZIP CRC integrity. The full metadata output is `forensics/outputs/workbook_audit.json`.", "",
        "## Workbook coverage", "", "| Workbook package | Sheets | Nonempty cells | Formula cells |",
        "| --- | ---: | ---: | ---: |"]
    for book in audit["workbooks"]:
        sheets = book["sheets"]
        lines.append(f"| {Path(book['source']).name} | {len(sheets)} | {sum(s['nonempty_cells'] for s in sheets)} | {sum(s['formula_count'] for s in sheets)} |")
    lines += ["", "All 65 sheets are visible. No hidden rows/columns, defined names, comments, external relationships, chart objects/caches, embedded data, drawings, macros, or formulas were found. There are ordinary merged headings and formatting. The source arrays are stored numeric values; there are no missing formula caches to recover. All packages pass CRC and XML parsing.", "",
        "Fig.1d illustrates a formatting trap: stored OOXML dimension A1:B172 and parsed cell extent A1:B141, but only 70 nonempty cells (two headings and 34 numerical pairs). The audit records stored dimension, parsed extent and actual nonempty bounds separately. Metadata does not supply missing candidate IDs or extra screening points.", "",
        "**Local-copy provenance caveat:** MOESM11 and MOESM2 have `lastModifiedBy=Li, Angze`, Macintosh Excel application metadata, and recorded modification times 2026-09-13T11:03:52Z and 2026-09-13T11:04:07Z. These are observations about files supplied before this audit, not changes made by the audit. Their current hashes identify the supplied local copies; metadata alone cannot prove byte identity with the publisher download. Metadata contains no useful hidden sample mapping.", "",
        "## Dipole arrays and independently computed metrics", "",
        "SI PDF pp13–16 establishes Fig.5 catalyst intrinsic, Fig.6 photosensitizer intrinsic, Fig.7 catalyst transition and Fig.8 photosensitizer transition. Panels a/b/c are Cartesian x/y/z. Plot horizontal values are calculated and vertical values are predicted; workbook column labels `x` and `y` denote plot axes, not the Cartesian target. No dipole unit is given in these axes/captions or worksheet labels.", "",
        "Every figure contains exactly 900 training and 100 test samples for every component, with no missing/nonfinite numerical values. Training ranges are A4:B903, F4:G903, K4:L903; test ranges are C4:D103, H4:I103, M4:N103. Source order is preserved. All underlying values are recoverable, but sample geometries and IDs are not encoded in these blocks.", "",
        "The table below pools x/y/z (2700 train or 300 test scalar values); these are 900/100 conformations per target, not 2700/300 independent conformations. `data/derived/ml_metrics.csv` also reports each component separately. R² is predictive coefficient of determination, not Pearson r squared.", "",
        "| Target | Split | Samples | Pearson r | R² | MAE | RMSE |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in result["ml_metrics"]:
        if row["component"] == "pooled_xyz":
            lines.append(f"| {row['target']} | {row['split']} | {row['n_samples']} | {row['pearson_r']:.6f} | {row['r2']:.6f} | {row['mae']:.6f} | {row['rmse']:.6f} |")
    lines += ["", "## Coupling arrays", "",
        "Supplementary Fig.9 contains 1000 paired values for each coupling: J in A3:B1002 and J* in D3:E1002. The calculated/predicted axis direction comes from SI PDF p17. Units are unspecified in the released worksheet and figure axes/caption, so reported errors retain the source numerical scale.", "",
        "| Coupling | Calculated range | Predicted range | Pearson r | R² | MAE | RMSE |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in result["coupling_metrics"]:
        lines.append(f"| {row['coupling']} | {row['calculated_min']:.8g} to {row['calculated_max']:.8g} | {row['predicted_min']:.8g} to {row['predicted_max']:.8g} | {row['pearson_r']:.9f} | {row['r2']:.9f} | {row['mae']:.9g} | {row['rmse']:.9g} |")
    lines += ["", "The recomputed correlations round to the published 0.913 (J) and 0.748 (J*). Both couplings have both signs. Sign counts and disagreements are in `data/derived/supfig9_coupling_metrics.csv`. Signed values are preserved; no absolute-value transformation was applied.", "",
        "## Numerical ordering evidence", "",
        "Concatenating the 900 training rows followed by the 100 test rows reveals a strong algebraic correspondence. A single common scale in the expression below nearly reconstructs all four calculated/predicted J/J* columns:", "",
        "`coupling = s × (−2 CAT_x PS_x + CAT_y PS_y + CAT_z PS_z)`", "",
        f"The scale is `{result['row_alignment']['shared_scale']:.12g}`, estimated solely from the first 900 calculated intrinsic-coupling rows. It is then fixed for the remaining 100 rows, both predicted channels, and both transition channels. This is an algebraic provenance test; no neural network or predictive ML model was trained.", "",
        "| Coupling channel | All-row R² | Last-100 R² | RMSE | Largest absolute residual |", "| --- | ---: | ---: | ---: | ---: |"]
    for probe in result["row_alignment"]["probes"]:
        lines.append(f"| {probe['coupling']} {probe['channel']} | {probe['shared_fixed_scale_metrics']['r2']:.15f} | {probe['last_100_metrics']['r2']:.15f} | {probe['shared_fixed_scale_metrics']['rmse']:.8g} | {probe['maximum_absolute_residual']:.8g} |")
    lines += ["", "Negative controls reorder the reconstructed coupling by test-first order, a one-row cyclic shift, and 100 fixed-seed permutations. The full metrics and residual summaries are in `forensics/outputs/ml_analysis.json`. These controls distinguish specific numerical ordering from merely equal sample counts.", "",
        "**Classification:** the numeric row pairing Fig.5+Fig.6→Fig.9a is **strongly supported**, and Fig.7+Fig.8→Fig.9b is **strongly supported**. The expression is consistent with a dipole tensor with fixed separation axis along x. It does not establish the original physical distance, unit conversion, dielectric factor, or coordinate convention. Residuals are nonzero; the stored values do not establish their cause.", "",
        "A common physical conformation pair across all four targets remains **plausible**, not proven. The two coupling identities separately connect intrinsic and transition blocks to adjacent Fig.9 columns; they do not independently establish that those columns use the same underlying geometries. There are no molecule/snapshot IDs, structure-file joins, or original split indices in these blocks, hidden workbook structures or metadata. The missing coordinate mapping prevents recovery of input X from these tables alone.", "",
        "## Reproduction and redistribution boundary", "",
        "Run `forensics/scripts/inspect_workbooks.py`, then `forensics/scripts/analyze_ml.py` with Python containing numpy and openpyxl. Both read source workbooks only. The first emits metadata; the second emits computed metrics and this report. Complete numerical extracts are written exclusively under ignored `forensics/local_only/supfig5_dipoles.csv` through `supfig8_dipoles.csv` and `supfig9_couplings.csv`. These source-derived extracts must never be staged, committed, or uploaded. The tracked metrics/reports are compact analytical summaries and do not substitute for the source tables.", ""]
    comparison = ROOT / "forensics/outputs/publisher_comparison.json"
    if comparison.exists():
        compared = json.loads(comparison.read_text())["comparisons"]
        if all(c["all_nonempty_cell_content_identical"] and not c["structural_differences"] for c in compared):
            lines += ["## Publisher-copy comparison", "",
                "A separately downloaded publisher copy of each locally re-saved workbook (MOESM2 and MOESM11) was compared against the supplied local evidence. Both ZIP byte sequences differ, but **every nonempty cell agrees exactly**: numerical XML values were compared as exact decimal values, text was resolved through shared strings, and formulas/cached values were included. Sheet order/state, nonempty bounds, merged ranges, hidden rows/columns, defined names, comments, links and object counts also agree. Thus the audit found no local cell-content alteration.", "",
                "Both publisher packages were separately CRC-checked and all XML parts inspected. They contain no additional hidden sample identifiers, orphan shared strings, chart caches, or embedded datasets. Custom properties record office-software build/version identifiers, not conformation IDs. Hashes and a per-sheet comparison are in `forensics/outputs/publisher_comparison.json`. Publisher downloads remain temporary local-only evidence. This comparison strengthens the workbook-specific absence findings; it does not establish absence from unreleased author materials.", ""]
    path = ROOT / "forensics/reports/WORKBOOK_ML_AUDIT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
