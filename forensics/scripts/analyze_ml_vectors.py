#!/usr/bin/env python3
"""Analyze released scalar/vector predictions and validation-row ranks only.

Full publisher arrays are read in memory through the existing OOXML reader.
Outputs contain compact summaries, never full dipole/coupling tables. No model
is constructed or trained, and no scientific job is launched.
"""

from pathlib import Path
import csv
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hu2025_repro.ml_metrics import (  # noqa: E402
    rank_sign_metrics, residual_matrices, scalar_metrics, top_k_overlap, vector_metrics,
)
from reconstruct_coupling import read_cells, unpack  # noqa: E402

TARGETS = {5: "catalyst_intrinsic", 6: "photosensitizer_intrinsic",
           7: "catalyst_transition", 8: "photosensitizer_transition"}
SPLITS = {"train": slice(0, 900), "test": slice(900, 1000)}
NORM_THRESHOLDS = (1e-4, 1e-3, 1e-2)
DEFAULT_THRESHOLD = 1e-3


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def residual_summary(actual, predicted, *, figure, split):
    """Four fixed quartiles and three error-only row locators per target/split."""
    norm = np.linalg.norm(actual, axis=1)
    error = np.linalg.norm(predicted - actual, axis=1)
    edges = np.quantile(norm, (0, 0.25, 0.5, 0.75, 1))
    groups = np.searchsorted(edges[1:-1], norm, side="right")
    bins = []
    for index in range(4):
        selected = groups == index
        summary = (vector_metrics(actual[selected], predicted[selected], norm_threshold=DEFAULT_THRESHOLD)
                   if np.any(selected) else None)
        bins.append({"quartile": index + 1, "n_rows": int(np.sum(selected)),
                     "calculated_norm_lower": float(edges[index]),
                     "calculated_norm_upper": float(edges[index + 1]),
                     "lower_inclusive": True, "upper_inclusive": index == 3,
                     "vector_error_norm_rms": summary["vector_error_norm_rms"] if summary else None,
                     "vector_error_rms_over_calculated_norm_rms": summary["vector_error_rms_over_calculated_norm_rms"] if summary else None,
                     "angle_median_degrees": summary["angle_median_degrees"] if summary else None})
    largest = np.argsort(-error, kind="stable")[:3]
    q1, q4 = bins[0]["vector_error_norm_rms"], bins[-1]["vector_error_norm_rms"]
    return {
        **residual_matrices(actual, predicted),
        "magnitude_error_norm_pearson_r": scalar_metrics(norm, error)["pearson_r"],
        "quartile_rule": "Within each target/split: calculated-norm empirical quartiles; ties assigned to the upper bin; last upper bound inclusive.",
        "magnitude_quartiles": bins,
        "q4_over_q1_absolute_vector_error_rms": q4 / q1 if q1 and q4 is not None else None,
        "largest_error_rows": [{"figure": figure, "split": split,
                                "source_excel_row": int(i + 4),
                                "vector_error_norm": float(error[i])} for i in largest],
        "largest_error_scope": "Three locators and derived error norms only; no source vectors or molecule/conformation identity is implied.",
    }


def verify_phase0(scalar_rows):
    """Compare fresh calculations to compact Phase-0 metrics, never copy them."""
    with (ROOT / "data/derived/ml_metrics.csv").open() as handle:
        baseline = {(r["target"], r["split"], r["component"]): r for r in csv.DictReader(handle)}
    max_difference = {name: 0.0 for name in ("pearson_r", "r2", "mae", "rmse")}
    for row in scalar_rows:
        old = baseline[row["target"], row["split"], row["component"]]
        if int(old["n_samples"]) != row["n_samples"]:
            raise ValueError("Phase-0 sample count mismatch")
        for name in max_difference:
            difference = abs(row[name] - float(old[name]))
            max_difference[name] = max(max_difference[name], difference)
            if not np.isclose(row[name], float(old[name]), rtol=2e-12, atol=2e-12):
                raise ValueError(f"Phase-0 metric mismatch: {row['target']} {row['split']} {name}")
    return {"matched_rows": len(scalar_rows), "maximum_absolute_differences": max_difference,
            "relative_tolerance": 2e-12, "absolute_tolerance": 2e-12}


def main():
    vectors, coupling, *_ = unpack(read_cells())
    scalar_rows, vector_rows, rank_rows = [], [], []
    targets = {}
    for figure, target in TARGETS.items():
        blocks = {}
        for split, slc in SPLITS.items():
            actual, predicted = vectors[figure][0][slc], vectors[figure][1][slc]
            scalar = {}
            for component, axis in enumerate(("x", "y", "z", "pooled_xyz")):
                a, p = ((actual, predicted) if component == 3 else (actual[:, component], predicted[:, component]))
                values = scalar_metrics(a, p)
                scalar[axis] = values
                scalar_rows.append({"figure": figure, "target": target, "split": split,
                                    "component": axis, "n_samples": len(actual),
                                    "units": "released_numeric_units_unspecified", **values})
            sensitivity = [vector_metrics(actual, predicted, norm_threshold=threshold)
                           for threshold in NORM_THRESHOLDS]
            for result in sensitivity:
                vector_rows.append({"figure": figure, "target": target, "split": split,
                                    "units": "released_numeric_units_unspecified", **result})
            blocks[split] = {"scalar": scalar,
                             "vector": next(row for row in sensitivity if row["norm_threshold"] == DEFAULT_THRESHOLD),
                             "norm_threshold_sensitivity": sensitivity,
                             "residual": residual_summary(actual, predicted, figure=figure, split=split)}
        blocks["test_minus_train"] = {
            "scalar_error_gaps": {axis: {metric: blocks["test"]["scalar"][axis][metric] - blocks["train"]["scalar"][axis][metric]
                                          for metric in ("mae", "rmse", "bias")}
                                  for axis in ("x", "y", "z", "pooled_xyz")},
            "vector_gaps": {metric: blocks["test"]["vector"][metric] - blocks["train"]["vector"][metric]
                            if blocks["test"]["vector"][metric] is not None and blocks["train"]["vector"][metric] is not None else None
                            for metric in ("magnitude_mae", "magnitude_rmse", "vector_error_norm_rms",
                                           "vector_error_rms_over_calculated_norm_rms", "angle_median_degrees", "angle_mean_degrees")},
        }
        targets[target] = blocks

    rank_results = {}
    for index, label in enumerate(("J", "Jstar")):
        by_block = {}
        for block, slc in (("all_1000", slice(None)), ("first_900", slice(0, 900)), ("final_100", slice(900, 1000))):
            actual, predicted = coupling[slc, 2 * index], coupling[slc, 2 * index + 1]
            ranks = rank_sign_metrics(actual, predicted)
            stats = scalar_metrics(actual, predicted)
            csv_row = {"coupling": label, "block": block,
                       **{key: value for key, value in ranks.items() if not isinstance(value, dict)},
                       "r2": stats["r2"], "mae": stats["mae"], "rmse": stats["rmse"], "bias": stats["bias"]}
            comparisons = []
            for mode, absolute, bottom in (("signed_top", False, False), ("absolute_top", True, False), ("signed_bottom", False, True)):
                for k in (10, 25, 50, 100):
                    overlap = top_k_overlap(actual, predicted, k, absolute=absolute, bottom=bottom)
                    comparisons.append({"mode": mode, **overlap, "trivial_full_set": k == len(actual)})
                    csv_row[f"{mode}_{k}_overlap_count"] = overlap["overlap_count"]
                    csv_row[f"{mode}_{k}_overlap_fraction"] = overlap["overlap_fraction"]
            rank_rows.append(csv_row)
            by_block[block] = {"scalar": stats, "rank_and_sign": ranks, "top_bottom_k": comparisons}
        rank_results[label] = by_block

    result = {
        "source": "orginal/41929_2025_1291_MOESM2_ESM.xlsx",
        "classification": "COMPUTED FROM RELEASED DATA",
        "scope": "Existing predictions only. No trained model, generated label, MD, QM, TDDFT or optimizer step.",
        "sample_convention": "Figs. 5-8 each have 900 training and 100 test vector rows. Pooled 2700/300 counts scalar components, not independent molecular conformations.",
        "metric_definitions": {
            "residual": "predicted minus calculated",
            "r2": "1-SSE/SST, predictive R2, not Pearson squared",
            "normalized_vector_error": "sqrt(mean(||predicted-calculated||^2))/sqrt(mean(||calculated||^2)); invariant to a common rigid rotation and common unit rescaling",
            "relative_magnitude_error": "abs(||predicted||-||calculated||)/||calculated|| when calculated norm exceeds threshold",
            "angles": "Signed vector directions, arccos clipped dot product, degrees; require both norms above threshold",
            "auxiliary_axis_angle": "min(theta,180-theta), an explicitly phase-insensitive orientation diagnostic only; no source vector signs or coupling calculations are changed",
            "undefined": "None in JSON or blank CSV, never replaced with zero",
        },
        "norm_threshold_choice": {"classification": "REIMPLEMENTATION CHOICE", "default": DEFAULT_THRESHOLD,
                                  "sensitivity": list(NORM_THRESHOLDS), "units": "released numeric dipole units",
                                  "meaning": "Absolute numerical stability cutoff, not an inferred author preprocessing step or physically calibrated scale"},
        "targets": targets,
        "coupling_validation_ranks": rank_results,
        "rank_scope": "Fig. 9 validation-row ranking, not the 180 photocatalytic-system ranking. First 900/final 100 inherit conditional algebraic alignment; Fig. 9 itself does not explicitly label a split.",
        "rank_ties": "Spearman uses ascending average exact-tie ranks; Kendall is tau-b. Top/bottom-k select exactly k with a stable original-row tie break. Counts and denominators are retained; k=n is trivial.",
        "phase0_metric_validation": verify_phase0(scalar_rows),
        "array_storage": "In-memory source arrays only. Tracked outputs are 32 scalar rows, 24 vector summaries, 6 coupling-rank summaries and compact matrices/quartiles/error-only locators.",
    }
    write_csv(ROOT / "data/derived/ml_scalar_metrics.csv", scalar_rows)
    write_csv(ROOT / "data/derived/ml_vector_metrics.csv", vector_rows)
    write_csv(ROOT / "data/derived/coupling_rank_metrics.csv", rank_rows)
    (ROOT / "forensics/outputs/phase2_ml_vectors.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("Recomputed 32 scalar metrics, 24 vector summaries and 6 validation-rank summaries; Phase-0 agreement verified; no source arrays exported.")


if __name__ == "__main__":
    main()
