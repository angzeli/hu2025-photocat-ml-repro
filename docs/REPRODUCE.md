# Reproduce the released-data analysis

This guide reproduces the evaluation and analytic results described in the
[ML reproduction note](ML_REPRODUCTION_NOTE.md). It performs ordinary CPU array
analysis and plotting. It does not run MD, QM, TDDFT, structure optimization,
model training, or scientific jobs. The [optional compute plan](COMPUTE_PLAN.md)
is a separate project extension and is not required here.

Run commands from the repository root. The source files are deliberately absent
from a public clone; synthetic tests and public figures can be regenerated without them.

## 1. Environment

Use Python 3.12; the reference analysis environment is Python 3.12.14. Select that
interpreter before creating the environment (`python3` below must resolve to it).
The tested dependencies are pinned in [requirements.txt](../requirements.txt).
They provide NumPy, workbook/PDF readers and Matplotlib, without a neural-network
framework, GPU stack, or molecular simulation package.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The activation command is for a POSIX shell. `.venv/` is ignored. Installation
obtains software dependencies only; no command in this guide downloads publisher
evidence automatically. The reference array/readers are NumPy 2.3.5, openpyxl 3.1.5
and pypdf 6.10.0; the tested renderer is Matplotlib 3.10.8. These four direct
dependencies are pinned in the requirements file.

## 2. Tests and figures without publisher inputs

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/build_public_figures.py
```

Tests use entirely synthetic values. They check physical coupling, unit conversions,
vector/rank metrics, exact error decomposition and the disclosed untrained architecture
specification, plus the narrow publication-artifact boundary. The local candidate
passed all 34 tests: 28 analytical/architecture tests and six publication-boundary
regressions. A passing architecture test does not create or train a model.

The figure script reads the committed analytical JSON/CSV summaries, so `orginal/`
is unnecessary for this step. It regenerates these original analytical figures as
PNG and PDF pairs under `figures/derived/`:

- `reproducibility_ladder`: recoverability classes and their boundaries.
- `ml_quality`: normalized vector errors and angular fidelity.
- `coupling_error_decomposition`: error terms with covariance-aware interpretation.
- `screening_sensitivity`: counts and membership stability on the bounded threshold grid.

These figures visualize existing analysis, not the publisher's individual scatter
points. Regenerating them from committed summaries is a presentation check; it does
not independently recheck the original workbooks. Missing analytical inputs should
be restored from the same repository version, not substituted with publisher tables.

Two builds, including a fresh plotting cache, produced byte-identical copies of all
eight figure files in the tested reference environment, and PNG/PDF renderings were
visually checked. This is not a universal byte-identity guarantee across platforms,
fonts or transitive rendering libraries. The publication guard accepts only reviewed
path-and-hash combinations; investigate a changed rendering before any controlled
allowlist update, rather than bypassing the guard.

## 3. Minimum local publisher inputs

Obtain the following files lawfully from the [article's supplementary/source-data
listing](https://www.nature.com/articles/s41929-025-01291-z), and place them locally
under the existing name `orginal/`. Its spelling is intentional. Keep their original
filenames and do not resave, edit or convert them in place.

| Local filename | Publisher role | Required analysis |
|---|---|---|
| `41929_2025_1291_MOESM2_ESM.xlsx` | Supplementary Data 1 | Figs. 5–9 dipole/coupling analysis; optional first descriptor screen |
| `41929_2025_1291_MOESM11_ESM.xlsx` | Source Data Fig. 1 | Fig. 1d threshold sensitivity and Fig. 1e measured validation |
| `41929_2025_1291_MOESM1_ESM.pdf` | Supplementary Information | Table 3 group/measurement cross-check; optional descriptor identity checks |

The three-file layout is:

```text
orginal/
  41929_2025_1291_MOESM2_ESM.xlsx
  41929_2025_1291_MOESM11_ESM.xlsx
  41929_2025_1291_MOESM1_ESM.pdf
```

The article itself supplies the scientific Methods and interpretation, but its PDF
and the coordinate packages are not additional machine inputs to the three Phase-2
commands below. This minimum set also suffices for the optional Phase-1 coupling
check and first-screen command shown later.

`orginal/` and `forensics/local_only/` are ignored, as are raw source formats.
Do not force-add source files or use Git LFS to bypass the boundary. A clone contains
the compact Phase-0/1 baselines used by later verification: preserve
`data/derived/ml_metrics.csv`, `forensics/outputs/screening_analysis.json` and
`forensics/outputs/phase1_coupling.json`. These are analytical comparison records,
not missing downloads or replacements for the workbooks.

## 4. Rerun the source-data ML reproduction

With the three originals present and the environment active:

```sh
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_ml_vectors.py
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_error_propagation.py
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_screening_sensitivity.py
```

The scripts read source values in memory and write compact analytical summaries.
They do not save the workbooks, write into `orginal/`, fit a model, or refit the
Phase-1 scalar. Their outputs and success conditions are:

| Command | Principal outputs | Expected verification |
|---|---|---|
| `analyze_ml_vectors.py` | `data/derived/ml_scalar_metrics.csv`, `ml_vector_metrics.csv`, `coupling_rank_metrics.csv`; `forensics/outputs/phase2_ml_vectors.json` | 32 scalar records match Phase 0; 24 threshold-specific vector summaries; six coupling block summaries |
| `analyze_error_propagation.py` | `data/derived/ml_error_propagation.csv`; `forensics/outputs/phase2_error_propagation.json` | Frozen tensor/scalar reproduce the four coupling channels to recorded residuals; CAT/PS/cross expansion closes to floating-point precision |
| `analyze_screening_sensitivity.py` | `data/derived/screening_sensitivity.csv`; `forensics/outputs/phase2_screening.json` | 34 positive points; seven pass the compatibility probe; 49 grid cells; all 43 measured SI/workbook rows agree |

Then regenerate the figures with the same command from step 2. Curated scientific
reports are not automatically rewritten by these scripts. If a result changes,
inspect the source edition, dependency environment and specific numerical difference
before updating a baseline or narrative; do not overwrite the expected result to
make a check pass.

The [Phase-2 report](../forensics/reports/PHASE2_ZERO_COMPUTE_ML_REPRODUCTION.md)
gives the reference values: `r(J) = 0.9129259525`, `r(J*) = 0.7475491726`,
error-expansion closure at approximately `1.03e-12` and `1.34e-15`, respectively,
and measured-set precision/recall `6/6` and `6/7`. Numerical tolerances and counting
conventions are recorded in the JSON outputs. Small platform differences in the
last floating-point digits are distinct from scientific disagreement.

## 5. Optional earlier-stage checks

After the Phase-2 baseline comparisons, these bounded commands independently
recompute the earlier tensor inference and descriptor-screen evidence:

```sh
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/reconstruct_coupling.py
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_screening.py
```

The first repeats the Phase-1 diagnostic scalar fit using only the first 900
calculated intrinsic rows and writes `forensics/outputs/phase1_coupling.json`.
This is the declared analytic calibration check, not neural-network training.
The second reconstructs 18 CAT × 10 PS = 180 identities from the strict descriptor
thresholds and refreshes Phase-0 screening outputs. Its complete table extracts
are written exclusively to ignored `forensics/local_only/`.

These optional reruns overwrite their earlier analytical outputs; compare resulting
changes before treating them as revised evidence. The public narrative remains
bounded by unknown physical units, missing geometry/model records and partial
screening coverage. Do not run the complete original-file inventory merely to
evaluate these three source files.

## 6. Archive integrity is a separate audit

The original project audited 6,901 files. Its committed
[source manifest](../data/manifests/original-files.csv) and
`forensics/scripts/validate_phase0.py` describe that exact local evidence collection.
The full validator requires the complete recorded path set and exact hashes/sizes;
its optional `--baseline` additionally checks against a pre-analysis mtime snapshot.
It is not a three-file setup check and will correctly reject an incomplete archive.

The supplied MOESM2 and MOESM11 workbooks had been locally resaved before Phase 0.
A separate publisher-copy comparison found different file bytes but identical
nonempty cell contents. Consequently, a fresh publisher download can fail this
historical hash comparison without being corrupt or numerically different. See the
[Phase-0 provenance finding](../forensics/reports/PHASE0_DATA_FORENSICS.md) and
[comparison summary](../forensics/outputs/publisher_comparison.json).
Record and investigate that provenance difference; do not replace originals,
force-add files, or edit the historical manifest to claim byte identity.

For a new local collection, preserve its own before/after metadata separately from
the shipped historical record. Numerical rerun success establishes agreement of the
analyzed data under the stated checks; it does not establish byte identity of the
entire original collection. Public-source exclusion and sensitive-information
review are additional boundaries, not substitutes for either test.

The maintainer's `forensics/scripts/audit_publication.py` inspects reachable history,
the index and proposed files. Public-email exceptions must be independently verified
project metadata, not accepted merely because an email triggers the scanner. Review
its findings alongside the [source policy](SOURCE_POLICY.md); neither a passing
pattern scan nor an ignored filename proves that every transformed source table is safe
to distribute. No publisher or author source material is relicensed by this project.

The [local candidate validation record](../forensics/outputs/phase3_validation.json)
documents the 34 passing tests, three successful source-analysis reruns with unchanged
Phase-2 output bytes, repeat figure builds, visual review, unchanged hashes/sizes/mtimes
for all 6,901 originals, and zero source/privacy findings across the audited files and
history. These are local candidate checks, not remote CI results or release publication.
