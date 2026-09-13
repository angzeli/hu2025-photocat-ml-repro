#!/usr/bin/env python3
"""Reconstruct released coupling numerics without exporting source arrays.

Reads only Figs. 5--9 of the ignored workbook. The scalar is fitted once, to
the first 900 calculated intrinsic rows. All other channels are held fixed.
OOXML precision is inspected independently of Excel display formatting.
"""

from collections import Counter
from decimal import Decimal
from itertools import permutations, product
from pathlib import Path
import json
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hu2025_repro.coupling import conversion_factor  # noqa: E402

SOURCE = ROOT / "orginal/41929_2025_1291_MOESM2_ESM.xlsx"
OUTPUT = ROOT / "forensics/outputs/phase1_coupling.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
WEIGHTS = np.array([-2.0, 1.0, 1.0])


def read_cells():
    """Return numeric XML tokens and format IDs; never write extracted cells."""
    sheets = {}
    with ZipFile(SOURCE) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relations}
        styles = ET.fromstring(archive.read("xl/styles.xml"))
        format_ids = [int(x.attrib["numFmtId"])
                      for x in styles.findall("m:cellXfs/m:xf", NS)]
        for sheet in workbook.findall("m:sheets/m:sheet", NS):
            name = sheet.attrib["name"]
            if name not in {f"Supplementary Fig. {i}" for i in range(5, 10)}:
                continue
            target = targets[sheet.attrib[RID]]
            member = target.lstrip("/") if target.startswith("/") else "xl/" + target
            xml = ET.fromstring(archive.read(member))
            cells = {}
            for cell in xml.findall(".//m:c", NS):
                value = cell.find("m:v", NS)
                if value is not None and cell.attrib.get("t", "n") == "n":
                    cells[cell.attrib["r"]] = (
                        value.text, format_ids[int(cell.attrib.get("s", "0"))])
            sheets[int(name.split()[-1])] = cells
    return sheets


def effective_decimals(token):
    """Shortest decimal count after allowing up to eight binary-float ulps.

    This detects serialization tails, not the author's unrounded accuracy.
    Shortened trailing zeros make this an ambiguous, conservative diagnostic.
    """
    value = float(token)
    tolerance = 8 * abs(np.spacing(abs(value)))
    for digits in range(16):
        if abs(value - round(value, digits)) <= tolerance:
            return digits
    return 16


def precision_summary(cells):
    tokens = [cell[0] for cell in cells]
    return {
        "n_values": len(tokens),
        "literal_xml_decimal_exponents": dict(sorted(Counter(
            str(Decimal(t).as_tuple().exponent) for t in tokens).items())),
        "effective_decimal_places_after_binary_tail_tolerance": dict(sorted(Counter(
            str(effective_decimals(t)) for t in tokens).items())),
        "scientific_notation_token_count": sum("e" in t.lower() for t in tokens),
        "number_format_counts": dict(sorted(Counter(
            "General" if cell[1] == 0 else "0.00E+00" if cell[1] == 11
            else str(cell[1]) for cell in cells).items())),
    }


def unpack(sheets):
    vectors, precisions, xml_errors, decimal_errors = {}, {}, {}, {}
    for figure in range(5, 9):
        vectors[figure], xml_errors[figure], decimal_errors[figure] = [], [], []
        for label, train, test in (("calculated", "AFK", "CHM"),
                                   ("predicted", "BGL", "DIN")):
            rows = [[sheets[figure][f"{column}{row}"] for column in columns]
                    for columns, count in ((train, 900), (test, 100))
                    for row in range(4, 4 + count)]
            tokens = [[cell[0] for cell in row] for row in rows]
            values = np.array(tokens, dtype=float)
            if values.shape != (1000, 3) or not np.isfinite(values).all():
                raise ValueError(f"Incomplete figure {figure} {label}")
            vectors[figure].append(values)
            xml_errors[figure].append(np.array([
                [0.5 * 10.0 ** Decimal(t).as_tuple().exponent for t in row]
                for row in tokens]))
            decimal_errors[figure].append(np.array([
                [0.5 * 10.0 ** -effective_decimals(t) for t in row]
                for row in tokens]))
            precisions[f"figure_{figure}_{label}"] = precision_summary(
                [cell for row in rows for cell in row])
    coupling_cells = [[sheets[9][f"{column}{row}"] for column in "ABDE"]
                      for row in range(3, 1003)]
    coupling = np.array([[c[0] for c in row] for row in coupling_cells], dtype=float)
    if coupling.shape != (1000, 4) or not np.isfinite(coupling).all():
        raise ValueError("Incomplete figure 9")
    coupling_xml_error = np.array([
        [0.5 * 10.0 ** Decimal(c[0]).as_tuple().exponent for c in row]
        for row in coupling_cells])
    for index, label in enumerate(("J_calculated", "J_predicted",
                                   "Jstar_calculated", "Jstar_predicted")):
        precisions[label] = precision_summary([row[index] for row in coupling_cells])
    return vectors, coupling, precisions, xml_errors, decimal_errors, coupling_xml_error


def fit_scalar(q, actual):
    return float(np.dot(q[:900], actual[:900]) / np.dot(q[:900], q[:900]))


def metrics(actual, predicted):
    residual = predicted - actual
    centered = actual - actual.mean()
    abs_residual = np.abs(residual)
    return {
        "n_rows": len(actual),
        "r2": float(1 - np.dot(residual, residual) / np.dot(centered, centered)),
        "rmse": float(np.sqrt(np.mean(residual ** 2))),
        "mae": float(np.mean(abs_residual)),
        "mean_signed_residual": float(np.mean(residual)),
        "max_absolute_residual": float(np.max(abs_residual)),
        "absolute_residual_quantiles": {str(p): float(np.quantile(abs_residual, p))
                                        for p in (0.5, 0.9, 0.95, 0.99)},
        "residual_correlation_with_observed": float(np.corrcoef(residual, actual)[0, 1]),
    }


def numerator(cat, ps, weights=WEIGHTS):
    return np.sum(cat * ps * weights, axis=-1)


def product_error(cat, ps, error_cat, error_ps):
    """First-order and exact second-order box bounds for the tensor numerator."""
    first = np.sum(abs(WEIGHTS) * (abs(ps) * error_cat + abs(cat) * error_ps), axis=-1)
    cross = np.sum(abs(WEIGHTS) * error_cat * error_ps, axis=-1)
    return first, cross


def mixed_export_error(values):
    """Test a five-decimal / three-significant-digit export-rounding hypothesis.

    Only cells numerically compatible with three significant digits receive
    the coarser half step. This avoids treating a displayed integer as uncertain
    by half a whole unit merely because insignificant zeros were omitted.
    """
    magnitude = np.where(values == 0, 1, abs(values))
    quantum = 10.0 ** (np.floor(np.log10(magnitude)) - 2)
    compatible = abs(values - np.round(values / quantum) * quantum) <= 8 * np.spacing(abs(values))
    return np.maximum(0.5e-5, np.where(compatible, 0.5 * quantum, 0))


def bound_summary(cat, ps, actual, scale, error_cat, error_ps, error_j):
    first, cross = product_error(cat, ps, error_cat, error_ps)
    q = numerator(cat, ps)
    residual = abs(scale * q - actual)
    # Conservative arithmetic allowance, distinct from source decimal rounding.
    floating = 64 * np.finfo(float).eps * (
        abs(scale) * np.sum(abs(cat * ps * WEIGHTS), axis=-1) + abs(actual))
    bound = abs(scale) * (first + cross) + error_j + floating
    outside = residual > bound
    return {
        "within_bound": int(np.sum(~outside)), "outside_bound": int(np.sum(outside)),
        "first_900_outside_bound": int(np.sum(outside[:900])),
        "last_100_outside_bound": int(np.sum(outside[900:])),
        "max_first_order_coupling_bound": float(np.max(abs(scale) * first)),
        "max_cross_term_coupling_bound": float(np.max(abs(scale) * cross)),
        "max_total_bound": float(np.max(bound)),
        "median_total_bound": float(np.median(bound)),
        "max_residual_to_bound_ratio": float(np.max(residual / bound)),
    }


def admissible_scale_interval(q, actual, error_q, error_j):
    """Intersection of positive-scale intervals under independent rounding boxes.

    Row intervals do not certify one jointly achievable set of hidden dipoles;
    they test whether rounding bounds alone can rule out a common scalar.
    """
    low, high = 0.0, float("inf")
    used = 0
    for qi, yi, dq, dy in zip(q[:900], actual[:900], error_q[:900], error_j[:900]):
        if abs(qi) <= dq or abs(yi) <= dy:
            continue
        endpoints = [(yi + sy * dy) / (qi + sq * dq)
                     for sy in (-1, 1) for sq in (-1, 1)]
        low, high = max(low, min(endpoints)), min(high, max(endpoints))
        used += 1
    return {"minimum": float(low), "maximum": float(high),
            "nonempty": bool(low <= high), "fit_rows_used": used}


def axis_tests(cat, ps, actual):
    result = []
    for index, axis in enumerate("xyz"):
        weights = np.ones(3)
        weights[index] = -2
        q = numerator(cat, ps, weights)
        scale = fit_scalar(q, actual)
        result.append({"axis": axis, "weights": weights.tolist(), "fitted_scalar": scale,
                       "positive_physical_scalar": bool(scale > 0),
                       "first_900": metrics(actual[:900], scale * q[:900]),
                       "last_100": metrics(actual[900:], scale * q[900:]),
                       "all_1000": metrics(actual, scale * q)})
    alternatives = []
    for permutation in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            q = numerator(cat, ps[:, permutation] * signs)
            scale = fit_scalar(q, actual)
            alternatives.append({"ps_component_order": "".join("xyz"[i] for i in permutation),
                                 "ps_component_signs": list(signs), "fitted_scalar": scale,
                                 "first_900_rmse": metrics(actual[:900], scale * q[:900])["rmse"],
                                 "last_100_rmse": metrics(actual[900:], scale * q[900:])["rmse"]})
    alternatives.sort(key=lambda row: row["first_900_rmse"])
    return result, {
        "candidate_count": len(alternatives), "selection_uses": "first 900 calculated J only",
        "definition": "All six PS-only component permutations and eight relative sign patterns; fixed x tensor and one signed scalar each",
        "best_four": alternatives[:4],
        "positive_scalar_best": next(row for row in alternatives if row["fitted_scalar"] > 0),
        "equivalences": [
            "+x and -x separation are identical because the tensor depends on r r^T.",
            "Simultaneously reversing either Cartesian component in both dipoles leaves its product unchanged.",
            "Simultaneously swapping y and z, or applying any common rotation in the yz plane, preserves the x tensor.",
            "An overall relative dipole sign can be absorbed by a signed fitted scalar; physical positive conversion fixes this convention.",
            "A simultaneous relabelling of axes and separation gives the same physical tensor; x refers to the released component labels.",
        ],
    }


def physical_analysis(scale, interval):
    factors = {unit: float(conversion_factor(unit)) for unit in ("J", "eV", "meV", "cm^-1")}
    constants = {
        "epsilon_0_F_per_m": 8.8541878188e-12,
        "epsilon_0_standard_uncertainty_F_per_m": 1.4e-21,
        "planck_J_s": 6.62607015e-34,
        "speed_of_light_m_per_s": 299792458.0,
        "elementary_charge_C": 1.602176634e-19,
        "bohr_radius_m": 5.29177210544e-11,
        "debye_C_m": 1e-21 / 299792458.0,
    }
    atomic_dipole_in_debye = (constants["elementary_charge_C"] * constants["bohr_radius_m"]
                             / constants["debye_C_m"])
    alternatives = []
    for dipole_unit, multiplier in (("Debye", 1.0), ("e a0", atomic_dipole_in_debye)):
        for energy_unit, factor in factors.items():
            distance = (factor * multiplier ** 2 / scale) ** (1 / 3)
            alternatives.append({"both_dipoles_unit": dipole_unit, "coupling_unit": energy_unit,
                                 "effective_distance_angstrom": float(distance),
                                 "effective_distance_bohr": float(distance * 1e-10 / constants["bohr_radius_m"])})
    c = factors["cm^-1"]
    distance = (c / scale) ** (1 / 3)
    nominal = c / 10.0 ** 3
    distance_interval = [(c / interval["maximum"]) ** (1 / 3),
                         (c / interval["minimum"]) ** (1 / 3)] if interval["nonempty"] else None
    return {
        "constants": constants,
        "primary_sources": ["https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
                            "https://cccbdb.nist.gov/dipunitsx.asp"],
        "coefficient_per_debye_squared_per_angstrom_cubed": factors,
        "debye_cm_inverse_hypothesis": {
            "effective_distance_angstrom": float(distance),
            "signed_discrepancy_from_10_angstrom": float(distance - 10.0),
            "absolute_discrepancy_from_10_angstrom": float(abs(distance - 10.0)),
            "relative_discrepancy_from_10": float((distance - 10.0) / 10.0),
            "nominal_10_angstrom_scalar": float(nominal),
            "empirical_minus_nominal_scalar": float(scale - nominal),
            "relative_scalar_discrepancy": float((scale - nominal) / nominal),
            "nominal_scalar_within_uniform_5dp_rounding_interval": bool(interval["minimum"] <= nominal <= interval["maximum"]),
            "effective_distance_interval_uniform_5dp_rounding_angstrom": distance_interval,
            "relative_distance_standard_uncertainty_from_epsilon0_only":
                constants["epsilon_0_standard_uncertainty_F_per_m"] / constants["epsilon_0_F_per_m"] / 3,
        },
        "alternative_unit_hypotheses": alternatives,
        "limits": "Vacuum prefactor with relative permittivity one is a hypothesis. Units, length units and dielectric factors remain jointly confounded; natural distance alone does not prove a unique convention.",
    }


def main():
    sheets = read_cells()
    vectors, coupling, precision, xml_error, decimal_error, coupling_xml_error = unpack(sheets)
    q_fit = numerator(vectors[5][0], vectors[6][0])
    scale = fit_scalar(q_fit, coupling[:, 0])
    axes, alternatives = axis_tests(vectors[5][0], vectors[6][0], coupling[:, 0])
    channels = {}
    for index, (name, cat_figure, ps_figure, channel) in enumerate((
            ("J_calculated", 5, 6, 0), ("J_predicted", 5, 6, 1),
            ("Jstar_calculated", 7, 8, 0), ("Jstar_predicted", 7, 8, 1))):
        cat, ps, actual = vectors[cat_figure][channel], vectors[ps_figure][channel], coupling[:, index]
        q = numerator(cat, ps)
        calculated = scale * q
        uniform = np.full_like(cat, 0.5e-5)
        error_j = np.full_like(actual, 0.5e-5)
        adaptive_cat, adaptive_ps = mixed_export_error(cat), mixed_export_error(ps)
        channels[name] = {
            "first_900": metrics(actual[:900], calculated[:900]),
            "last_100": metrics(actual[900:], calculated[900:]),
            "all_1000": metrics(actual, calculated),
            "rounding_bounds": {
                "literal_xml_last_digit": bound_summary(cat, ps, actual, scale,
                    xml_error[cat_figure][channel], xml_error[ps_figure][channel], coupling_xml_error[:, index]),
                "uniform_5dp_nearest": bound_summary(cat, ps, actual, scale, uniform, uniform, error_j),
                "uniform_5dp_truncation": bound_summary(cat, ps, actual, scale, 2*uniform, 2*uniform, 2*error_j),
                "mixed_5dp_3significant_digit_nearest": bound_summary(cat, ps, actual, scale, adaptive_cat, adaptive_ps, error_j),
            },
            "scale_display_rounded_11_decimal_places_max_added_error": float(np.max(abs(q) * abs(round(scale, 11) - scale))),
            "rows_with_dipole_decimal_step_coarser_than_5dp": int(np.sum(np.any(
                np.maximum(decimal_error[cat_figure][channel], decimal_error[ps_figure][channel]) > 0.5e-5, axis=1))),
            "cells_compatible_with_coarser_3significant_digit_export": {
                species: {split: {axis: int(np.sum(error[slc, component] > 0.5e-5))
                                  for component, axis in enumerate("xyz")}
                          for split, slc in (("first_900", slice(0, 900)), ("last_100", slice(900, None)))}
                for species, error in (("CAT", adaptive_cat), ("PS", adaptive_ps))},
        }
        if name == "J_calculated":
            nominal_scale = conversion_factor("cm^-1") / 10.0 ** 3
            channels[name]["modern_constants_exact_10_angstrom"] = {
                "all_1000": metrics(actual, nominal_scale * q),
                "uniform_5dp_nearest": bound_summary(cat, ps, actual, nominal_scale,
                                                      uniform, uniform, error_j),
            }
    uniform = np.full_like(vectors[5][0], 0.5e-5)
    first, cross = product_error(vectors[5][0], vectors[6][0], uniform, uniform)
    interval = admissible_scale_interval(q_fit, coupling[:, 0], first + cross, np.full(1000, 0.5e-5))
    result = {
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "classification": "COMPUTED FROM RELEASED DATA",
        "array_storage": "Source arrays exist in memory only; output contains aggregate statistics and hypotheses.",
        "row_layout": "Figs 5-8: 900 train rows A/F/K or B/G/L, then 100 test rows C/H/M or D/I/N, starting row 4. Fig9: A/B/D/E rows 3:1002.",
        "tensor": "q = -2*CAT_x*PS_x + CAT_y*PS_y + CAT_z*PS_z",
        "scalar": scale,
        "fit_contract": "Zero intercept; first 900 calculated intrinsic rows only; one scalar fixed for every other row and channel.",
        "metric_convention": "Residual=reconstructed-source. R2=1-SSE/SST; each block uses its own observed mean.",
        "axis_tests": axes, "sign_permutation_tests": alternatives,
        "channels": channels, "source_precision": precision,
        "rounding_model": {
            "classification": "REIMPLEMENTATION CHOICE for diagnostic bounds; author rounding not documented",
            "formula": "|delta J| <= |s| sum_i |w_i| (|p_i| e_ci + |c_i| e_pi + e_ci e_pi) + e_J + floating_arithmetic_allowance",
            "assumptions": [
                "Nearest-rounding half steps, or full steps in the explicit truncation scenario; independent per-cell errors.",
                "General and scientific Excel formats are display instructions, not stored-value rounding.",
                "Literal XML half-last-digit bounds are serialization diagnostics, not certified pre-export precision.",
                "Uniform five decimals is a bounded hypothesis motivated by most values, not a universal observed precision.",
                "The mixed export hypothesis permits a three-significant-digit half step only where the stored value is consistent with three significant digits; every other dipole retains the five-decimal bound. Coincidental short values remain ambiguous and this does not recover author rounding code.",
                "No latent values are imputed or optimized. No arbitrary tensor is fitted.",
            ],
            "uniform_5dp_positive_scalar_interval_first_900": interval,
        },
        "physical_unit_analysis": physical_analysis(scale, interval),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"Reconstructed 4 x 1000 rows; fitted scalar {scale:.15g}; compact summary: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
