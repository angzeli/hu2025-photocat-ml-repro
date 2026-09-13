#!/usr/bin/env python3
"""Summarize exact released-vector error propagation with the frozen Phase-1 scalar.

Only compact statistics are written. Publisher vectors remain in memory, and
no scientific simulation, model training or scalar fitting is performed.
"""

from pathlib import Path
import csv
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hu2025_repro.error_propagation import (  # noqa: E402
    decompose_coupling_error, magnitude_direction_error, squared_error_expansion,
)
from hu2025_repro.ml_metrics import scalar_metrics  # noqa: E402
from reconstruct_coupling import read_cells, unpack  # noqa: E402


def basic(values):
    return {"mean_absolute": float(np.mean(abs(values))),
            "rms": float(np.sqrt(np.mean(values ** 2))),
            "bias": float(np.mean(values))}


def comparison(actual, predicted):
    return {**scalar_metrics(actual, predicted),
            "max_absolute_residual": float(np.max(abs(predicted - actual)))}


def largest_axis(scores):
    # Split exact ties equally so the three fractions sum to one.
    winners = scores == scores.max(axis=1, keepdims=True)
    fractions = np.mean(winners / winners.sum(axis=1, keepdims=True), axis=0)
    return {"fractions": dict(zip("xyz", map(float, fractions))),
            "tied_rows": int(np.sum(winners.sum(axis=1) > 1))}


def expansion(terms, labels):
    result = squared_error_expansion(terms)
    return {"term_order": labels,
            **{key: value.tolist() if isinstance(value, np.ndarray) else value
               for key, value in result.items()}}


def analyze_block(cat, ps, predicted_cat, predicted_ps, released, scale):
    terms = decompose_coupling_error(cat, ps, predicted_cat, predicted_ps, scale=scale)
    total, first, cross = terms["total"], terms["first"], terms["cross"]
    closure = terms["sum_terms"] - total
    bound = 64 * np.finfo(float).eps * (
        np.sum(abs(terms["cat_axis"]) + abs(terms["ps_axis"]) + abs(terms["cross_axis"]), axis=1)
        + abs(terms["predicted"]) + abs(terms["calculated"]))
    if np.any(abs(closure) > bound):
        raise ValueError("Exact coupling decomposition exceeds floating-point closure bound")
    term_summaries = {}
    for term in ("cat", "ps", "cross", "first", "total"):
        term_summaries[term] = {"sum_xyz": basic(terms[term]),
                                **{axis: basic(terms[term + "_axis"][:, index])
                                   for index, axis in enumerate("xyz")}}
    source_error = released[:, 1] - released[:, 0]
    total_mse = float(np.mean(total ** 2))
    first_mse = float(np.mean(first ** 2))
    cross_mse = float(np.mean(cross ** 2))
    first_cross = float(np.mean(first * cross))
    target_variance = float(np.var(terms["calculated"]))

    modified = decompose_coupling_error(cat, ps, predicted_cat, predicted_ps,
                                        scale=scale, tensor=(-1, 1, 1))
    modified_mse = float(np.mean(modified["total"] ** 2))
    u = modified["total_axis"][:, 0]
    transverse = modified["total_axis"][:, 1:].sum(axis=1)
    coefficient_delta = float(3 * np.mean(u ** 2) + 2 * np.mean(u * transverse))

    magnitude_direction = magnitude_direction_error(cat, ps, predicted_cat, predicted_ps,
                                                     scale=scale, norm_threshold=1e-12)
    valid = magnitude_direction["valid"]
    md_terms = magnitude_direction["terms"]
    md_summary = {"norm_threshold_in_source_dipole_units": 1e-12,
                  "n_valid": int(valid.sum()), "n_excluded": int((~valid).sum())}
    if valid.any():
        md_labels = ["cat_magnitude", "cat_direction", "ps_magnitude", "ps_direction"]
        magnitudes = md_terms[:, 0] + md_terms[:, 2]
        directions = md_terms[:, 1] + md_terms[:, 3]
        md_closure = md_terms.sum(axis=1) - total[valid]
        md_bound = 64 * np.finfo(float).eps * (np.sum(abs(md_terms), axis=1)
                    + abs(terms["predicted"][valid]) + abs(terms["calculated"][valid]))
        if np.any(abs(md_closure) > md_bound):
            raise ValueError("Magnitude/direction decomposition exceeds arithmetic closure bound")
        md_summary.update(
            closure_max_absolute=float(np.max(abs(md_closure))),
            closure_rows_outside_arithmetic_bound=int(np.sum(abs(md_closure) > md_bound)),
            channel_statistics={label: basic(md_terms[:, index]) for index, label in enumerate(md_labels)},
            grouped_statistics={"magnitude": basic(magnitudes), "direction": basic(directions)},
            grouped_squared_error=expansion(np.column_stack([magnitudes, directions]), ["magnitude", "direction"]),
            channel_rms_over_calculated_coupling_sd={
                label: basic(md_terms[:, index])["rms"] / np.sqrt(target_variance)
                for index, label in enumerate(md_labels)},
        )
    return {
        "n_rows": len(cat),
        "reconstruction": {"calculated_vs_released": comparison(released[:, 0], terms["calculated"]),
                           "predicted_vs_released": comparison(released[:, 1], terms["predicted"])},
        "released_prediction_metrics": comparison(released[:, 0], released[:, 1]),
        "reconstructed_prediction_metrics": comparison(terms["calculated"], terms["predicted"]),
        "closure_max_absolute": float(np.max(abs(closure))),
        "closure_rows_outside_arithmetic_bound": int(np.sum(abs(closure) > bound)),
        "source_error_vs_reconstructed_error": comparison(source_error, total),
        "normalization_calculated_coupling_population_variance": target_variance,
        "term_rms_over_calculated_coupling_sd": {
            term: term_summaries[term]["sum_xyz"]["rms"] / np.sqrt(target_variance)
            for term in term_summaries},
        "term_statistics": term_summaries,
        "first_order_largest_axis": {
            "net_CAT_plus_PS_absolute": largest_axis(abs(terms["first_axis"])),
            "sum_of_absolute_CAT_and_PS": largest_axis(abs(terms["cat_axis"]) + abs(terms["ps_axis"])),
        },
        "term_squared_error_expansion": expansion(np.column_stack([terms["cat"], terms["ps"], cross]),
                                                    ["cat", "ps", "cross"]),
        "axis_squared_error_expansion": expansion(terms["total_axis"], list("xyz")),
        "first_order_vs_exact_error": comparison(total, first),
        "second_order_importance": {
            "cross_rms_over_total_error_rms": float(np.sqrt(cross_mse / total_mse)),
            "exact_error_mse": total_mse, "first_order_error_mse": first_mse,
            "cross_second_moment": cross_mse,
            "twice_first_cross_moment": 2 * first_cross,
            "exact_minus_first_mse": total_mse - first_mse,
            "delta_from_cross_and_signed_covariation": cross_mse + 2 * first_cross,
            "coupling_error_rmse_over_calculated_sd": float(np.sqrt(total_mse / target_variance)),
        },
        "x_weight_arithmetic_counterfactual": {
            "modified_tensor": [-1, 1, 1],
            "x_axis_term_rms_multiplier_in_original_tensor": 2.0,
            "original_total_error_mse": total_mse, "modified_total_error_mse": modified_mse,
            "original_to_modified_mse_ratio": total_mse / modified_mse,
            "mse_difference": total_mse - modified_mse,
            "mse_difference_from_x_and_signed_covariation": coefficient_delta,
            "relative_mse_increase_over_modified": (total_mse - modified_mse) / modified_mse,
        },
        "symmetric_magnitude_direction_diagnostic": md_summary,
    }


def main():
    frozen = json.loads((ROOT / "forensics/outputs/phase1_coupling.json").read_text())
    scale = frozen["scalar"]
    vectors, coupling, *_ = unpack(read_cells())
    blocks, rows = {}, []
    for family, cat_figure, ps_figure, columns in (("J", 5, 6, slice(0, 2)),
                                                 ("Jstar", 7, 8, slice(2, 4))):
        blocks[family] = {}
        for label, selection in (("all_1000", slice(None)), ("first_900", slice(0, 900)),
                                 ("last_100", slice(900, 1000))):
            summary = analyze_block(vectors[cat_figure][0][selection], vectors[ps_figure][0][selection],
                                    vectors[cat_figure][1][selection], vectors[ps_figure][1][selection],
                                    coupling[selection, columns], scale)
            blocks[family][label] = summary
            for term, components in summary["term_statistics"].items():
                for component, statistics in components.items():
                    rows.append({"coupling": family, "row_block": label, "n_rows": summary["n_rows"],
                                 "term": term, "component": component, **statistics})
    report = {
        "classification": "COMPUTED FROM RELEASED DATA",
        "source": "orginal/41929_2025_1291_MOESM2_ESM.xlsx",
        "frozen_scalar_source": "forensics/outputs/phase1_coupling.json",
        "scalar": scale, "scalar_refitted": False, "tensor": [-2, 1, 1],
        "units": "released numerical coupling units; cm^-1 is a conditional Phase-1 inference",
        "row_blocks": "first_900 and last_100 follow train-then-test dipole rows; Fig.9 itself has no split labels",
        "row_identity_limit": "within-family numerical alignment; no confirmed shared geometry join between intrinsic and transition families",
        "largest_axis_definition": "net absolute CAT+PS versus sum of absolute CAT and PS; ties share weight equally",
        "second_moment_convention": "population mean E[ab], covariance divisor n; signed cross moments retained, no independent variance fractions",
        "x_counterfactual_limit": "arithmetic coefficient diagnostic changes both calculated and predicted couplings; not an alternate physical model or an accuracy optimization",
        "magnitude_direction_definition": "symmetric endpoint norm/direction split combined with midpoint partner vectors; cross term shared equally between CAT/PS; algebraic attribution, not causal physics",
        "new_scientific_jobs": False, "models_trained": False,
        "array_storage": "source arrays in memory only; outputs contain aggregate statistics",
        "channels": blocks,
    }
    output = ROOT / "forensics/outputs/phase2_error_propagation.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    with (ROOT / "data/derived/ml_error_propagation.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"summary_rows": len(rows), "scalar_refitted": False,
                      "channels": {family: {"closure_max_absolute": value["all_1000"]["closure_max_absolute"],
                                             "first_order_r2": value["all_1000"]["first_order_vs_exact_error"]["r2"],
                                             "cross_rms_over_total": value["all_1000"]["second_order_importance"]["cross_rms_over_total_error_rms"]}
                                   for family, value in blocks.items()}}, indent=2))


if __name__ == "__main__":
    main()
