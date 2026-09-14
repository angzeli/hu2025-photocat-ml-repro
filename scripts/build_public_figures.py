#!/usr/bin/env python3
"""Build four analytical PNG/PDF pairs from tracked Phase-2 summaries only.

No publisher files, full extracted arrays, model training or network access are
needed. Run from any directory; relative output paths are repository relative.
Byte reproducibility assumes the same Python and plotting libraries. DejaVu Sans
is selected explicitly from Matplotlib's bundled fonts so a host's Arial
installation cannot change layout or embedded glyphs.
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
import numpy as np  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
INTRINSIC = "#0072B2"
TRANSITION = "#D55E00"
NEUTRAL = "#4D4D4D"
VECTOR_SUMMARY = "data/derived/ml_vector_metrics.csv"
ERROR_SUMMARY = "forensics/outputs/phase2_error_propagation.json"
SCREENING_SUMMARY = "data/derived/screening_sensitivity.csv"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "savefig.edgecolor": "white",
    "legend.facecolor": "white", "legend.edgecolor": "black",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "mathtext.fontset": "stixsans", "text.color": "black",
    "axes.edgecolor": "black", "axes.labelcolor": "black",
    "axes.labelsize": 22, "axes.labelweight": "bold",
    "axes.titlesize": 18, "axes.titleweight": "bold", "axes.linewidth": 1.8,
    "axes.grid": False, "axes.spines.left": True, "axes.spines.right": True,
    "axes.spines.bottom": True, "axes.spines.top": True,
    "xtick.labelsize": 14, "ytick.labelsize": 14,
    "xtick.color": "black", "ytick.color": "black",
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.major.width": 1.8, "ytick.major.width": 1.8,
    "xtick.major.size": 4, "ytick.major.size": 4,
    "xtick.bottom": True, "ytick.left": True,
    "xtick.top": False, "ytick.right": False,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "lines.linewidth": 2.0, "legend.fontsize": 10,
    "legend.frameon": True, "legend.framealpha": 1.0,
    "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.transparent": False,
    "pdf.fonttype": 42, "pdf.compression": 9,
})


def style_axes(ax):
    """Apply the same scientific axes treatment throughout the figure set."""
    ax.grid(False, which="both")
    ax.minorticks_off()
    ax.tick_params(direction="in", width=1.8, length=4, top=False, right=False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.8)
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontsize(14)
        label.set_fontweight("bold")
    # ax.set_title("...", fontsize=18, fontweight="bold")


def read_csv(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise SystemExit(f"Missing tracked summary: {relative_path}. Use a complete repository checkout.")
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def read_json(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise SystemExit(f"Missing tracked summary: {relative_path}. Use a complete repository checkout.")
    return json.loads(path.read_text())


def save_pair(fig, destination, stem):
    """Write fixed-metadata PNG/PDF files; no dates or machine metadata."""
    options = {"bbox_inches": "tight", "facecolor": "white", "transparent": False}
    fig.savefig(destination / f"{stem}.png", dpi=600,
                metadata={"Software": "hu2025-repro"}, **options)
    fig.savefig(destination / f"{stem}.pdf", metadata={
        "Creator": "hu2025-repro", "Producer": "Matplotlib",
        "CreationDate": None, "ModDate": None, "Title": stem.replace("_", " "),
    }, **options)
    plt.close(fig)


def panel_label(ax, letter):
    ax.text(-0.03, 1.025, letter, transform=ax.transAxes,
            fontsize=18, fontweight="bold", va="bottom")


def family_legend(ax, coupling=False):
    labels = (r"Intrinsic $J$", r"Transition $J^*$") if coupling else ("Intrinsic", "Transition")
    handles = [Patch(facecolor=INTRINSIC, edgecolor="black", label=labels[0]),
               Patch(facecolor=TRANSITION, edgecolor="black", hatch="//", label=labels[1])]
    ax.legend(handles=handles, loc="upper right", prop={"weight": "bold", "size": 10})


def paired_bars(ax, intrinsic, transition, labels, *, xlim, xlabel, decimals=3):
    positions = np.arange(len(labels))
    for values, offset, colour, hatch in ((intrinsic, -.16, INTRINSIC, None),
                                           (transition, .16, TRANSITION, "//")):
        ax.barh(positions + offset, values, height=.29, color=colour,
                edgecolor="black", linewidth=.8, hatch=hatch)
        padding = (xlim[1] - xlim[0]) * .023
        for position, value in zip(positions + offset, values):
            ax.text(value + (padding if value >= 0 else -padding), position,
                    f"{value:.{decimals}f}", fontsize=10, fontweight="bold",
                    va="center", ha="left" if value >= 0 else "right")
    ax.set(yticks=positions, yticklabels=labels, xlim=xlim,
           ylim=(len(labels) - .48, -1.0), xlabel=xlabel)
    style_axes(ax)


def reproducibility_ladder(destination):
    """Qualitative classes from the Phase-2 report and claim scorecard."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set(xlim=(0, 8), ylim=(0, 6))
    ax.axis("off")
    bands = [
        ("EXACT SOURCE-DATA REPRODUCTION",
         "Descriptor screen; released prediction metrics and coupling validation\n"
         "Exact error propagation; measured-set precision and recall arithmetic"),
        ("ALGORITHMIC REIMPLEMENTATION",
         "Disclosed MLP architecture family; analytical coupling and error APIs\n"
         "Original trained weights and the training process are not recovered"),
        ("PARTIAL",
         "Near-exact dipole-to-coupling match; conditional physical convention\n"
         "34-point screening map; incomplete score-to-identity correspondence"),
        ("UNAVAILABLE FROM RELEASED EVIDENCE",
         "Original geometry inputs, preprocessing and trained weights\n"
         "Full trajectories, all 180 system scores and pair-level aggregation"),
    ]
    for index, (heading, description) in enumerate(bands):
        bottom = 4.65 - index * 1.36
        ax.add_patch(Rectangle((.08, bottom), 7.84, 1.23, facecolor="#F4F4F4",
                               edgecolor="black", linewidth=1.3))
        ax.text(.27, bottom + .99, heading, fontsize=14, fontweight="bold", va="top")
        ax.text(.27, bottom + .58, description, fontsize=11, linespacing=1.5, va="top")
    ax.text(4, .16, "Released evaluation is reproducible; original neural-network training is not.",
            ha="center", fontsize=10, fontweight="bold")
    fig.tight_layout(pad=.5)
    save_pair(fig, destination, "reproducibility_ladder")


def ml_quality(destination, rows):
    chosen = {row["target"]: row for row in rows
              if row["split"] == "test" and float(row["norm_threshold"]) == .001}
    keys = [(f"{species}_intrinsic", f"{species}_transition")
            for species in ("catalyst", "photosensitizer")]
    if len(chosen) != 4 or any(int(row["n_rows"]) != 100 for row in chosen.values()):
        raise ValueError("Expected four tracked 100-row test-vector summaries")
    fig, axes = plt.subplots(1, 2, figsize=(8, 6), layout="constrained")
    fig.get_layout_engine().set(rect=(0, .20, 1, .78), wspace=.13)
    for ax, field, limit, xlabel, decimals in (
            (axes[0], "vector_error_rms_over_calculated_norm_rms", (0, .66),
             "Normalized\nvector error", 3),
            (axes[1], "angle_median_degrees", (0, 65), "Median angular\nerror (°)", 1)):
        intrinsic = [float(chosen[key[0]][field]) for key in keys]
        transition = [float(chosen[key[1]][field]) for key in keys]
        paired_bars(ax, intrinsic, transition, ["CAT", "PS"], xlim=limit,
                    xlabel=xlabel, decimals=decimals)
    axes[0].set_xticks([0, .2, .4, .6])
    axes[1].set_xticks([0, 20, 40, 60])
    for letter, ax in zip("ab", axes):
        style_axes(ax)
        panel_label(ax, letter)
    family_legend(axes[0])
    fig.text(.5, .125, r"Normalized error = RMS($\|\hat{\mu}-\mu\|$) / RMS($\|\mu\|$).",
             ha="center", fontsize=10, fontweight="bold")
    fig.text(.5, .08, "100 test vectors/target; source signs retained; norms > 0.001 source units.",
             ha="center", fontsize=10, fontweight="bold")
    fig.text(.5, .035, "Transition-vector errors increase, while the CAT median angle improves.",
             ha="center", fontsize=10, fontweight="bold")
    save_pair(fig, destination, "ml_quality")


def coupling_error_decomposition(destination, summary):
    blocks = [summary["channels"][family]["all_1000"] for family in ("J", "Jstar")]
    if any(block["n_rows"] != 1000 for block in blocks) or summary["scalar_refitted"]:
        raise ValueError("Expected frozen-scalar, 1000-row error summaries")
    fig, axes = plt.subplots(1, 2, figsize=(8, 6), layout="constrained")
    fig.get_layout_engine().set(rect=(0, .20, 1, .78), wspace=.16)
    rms = [[block["term_rms_over_calculated_coupling_sd"][term]
            for term in ("cat", "ps", "cross")] for block in blocks]
    paired_bars(axes[0], *rms, ["CAT", "PS", "Cross"], xlim=(0, .67),
                xlabel="Term RMS / SD")
    moments = []
    for block in blocks:
        variance = block["normalization_calculated_coupling_population_variance"]
        second = block["second_order_importance"]
        moments.append([second[key] / variance for key in (
            "first_order_error_mse", "cross_second_moment",
            "twice_first_cross_moment", "exact_error_mse")])
    paired_bars(axes[1], *moments, [r"$E[F^2]$", r"$E[c^2]$", r"$2E[Fc]$", "Exact"],
                xlim=(-.63, .94), xlabel="MSE / variance")
    axes[0].set_xticks([0, .2, .4, .6])
    axes[1].set_xticks([-.4, 0, .4, .8])
    axes[1].axvline(0, color="black", linewidth=1.0, zorder=0)
    for letter, ax in zip("ab", axes):
        style_axes(ax)
        panel_label(ax, letter)
    family_legend(axes[0], coupling=True)
    fig.text(.5, .125, "All 1,000 validation rows; SD and variance use each family's calculated coupling.",
             ha="center", fontsize=10, fontweight="bold")
    fig.text(.5, .078, r"a  RMS terms are nonadditive.  b  Exact MSE = $E[F^2]+E[c^2]+2E[Fc]$.",
             ha="center", fontsize=10, fontweight="bold")
    fig.text(.5, .03, r"$F$ = CAT + PS; $c$ = cross. Negative covariation reduces total MSE.",
             ha="center", fontsize=10, fontweight="bold")
    save_pair(fig, destination, "coupling_error_decomposition")


def screening_sensitivity(destination, rows):
    j_values = sorted({float(row["J_threshold_exclusive"]) for row in rows})
    js_values = sorted({float(row["Jstar_threshold_exclusive"]) for row in rows})
    if len(rows) != 49 or len(j_values) != 7 or len(js_values) != 7:
        raise ValueError("Expected the tracked 7 by 7 screening summary")
    matrix = np.full((7, 7), np.nan)
    lookup = {}
    for row in rows:
        column = j_values.index(float(row["J_threshold_exclusive"]))
        index = js_values.index(float(row["Jstar_threshold_exclusive"]))
        if (index, column) in lookup or int(row["supplied_point_count"]) != 34:
            raise ValueError("Duplicated or incompatible screening-summary cell")
        matrix[index, column] = int(row["selected_count"])
        lookup[index, column] = row
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = LinearSegmentedColormap.from_list("selected_count", ["#F3F3F3", NEUTRAL])
    display = ax.imshow(matrix, origin="lower", aspect="auto", cmap=cmap,
                        vmin=0, vmax=20, interpolation="nearest")
    ax.set(xticks=np.arange(7), xticklabels=[f"{value:g}" for value in j_values],
           yticks=np.arange(7), yticklabels=[f"{value:g}" for value in js_values],
           xlabel=r"$J$ threshold", ylabel=r"$J^*$ threshold", ylim=(-.5, 8.6))
    for (index, column), row in lookup.items():
        count = int(row["selected_count"])
        ax.text(column, index, str(count), ha="center", va="center", fontsize=10,
                fontweight="bold", color="white" if count >= 13 else "black")
        if count == 7:
            same = row["same_seven_point_set"] == "True"
            ax.add_patch(Rectangle((column - .46, index - .46), .92, .92, fill=False,
                                   edgecolor="black", linewidth=2.0 if same else 1.4,
                                   linestyle="-" if same else "--"))
    ax.plot(j_values.index(50.) + .27, js_values.index(.01) + .28, marker="*",
            markersize=10, color="black", markeredgecolor="white", markeredgewidth=.65,
            linestyle="none")
    handles = [Patch(facecolor="white", edgecolor="black", linewidth=2, label="Same seven points"),
               Patch(facecolor="white", edgecolor="black", linestyle="--", linewidth=1.4,
                     label="Seven points, different set"),
               Line2D([], [], marker="*", color="black", linestyle="none", markersize=10,
                      label="50 / 0.01 compatibility probe")]
    ax.legend(handles=handles, loc="upper center", prop={"weight": "bold", "size": 10})
    colourbar = fig.colorbar(display, ax=ax, pad=.035, ticks=[0, 5, 10, 15, 20])
    colourbar.set_label("Selected points", fontsize=22, fontweight="bold")
    colourbar.outline.set_linewidth(1.8)
    colourbar.ax.tick_params(direction="in", width=1.8, length=4)
    for label in colourbar.ax.get_yticklabels():
        label.set_fontsize(14)
        label.set_fontweight("bold")
    style_axes(ax)
    fig.text(.5, .025, "34 released points; strict > thresholds; sampled grid, not a 180-system ranking.",
             ha="center", fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, .06, 1, 1))
    save_pair(fig, destination, "screening_sensitivity")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("figures/derived"))
    args = parser.parse_args()
    destination = (ROOT / args.output_dir).resolve()
    for protected in ((ROOT / "orginal").resolve(), (ROOT / ".git").resolve()):
        if destination == protected or protected in destination.parents:
            parser.error("Figure output must be outside immutable sources and Git internals")
    vectors = read_csv(VECTOR_SUMMARY)
    errors = read_json(ERROR_SUMMARY)
    screening = read_csv(SCREENING_SUMMARY)
    destination.mkdir(parents=True, exist_ok=True)
    reproducibility_ladder(destination)
    ml_quality(destination, vectors)
    coupling_error_decomposition(destination, errors)
    screening_sensitivity(destination, screening)
    print("Generated four analytical PNG/PDF pairs from tracked summaries; no publisher inputs required.")


if __name__ == "__main__":
    main()
