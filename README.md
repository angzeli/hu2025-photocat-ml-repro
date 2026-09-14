# Hu 2025 Photocatalysis ML Reproduction

Independent source-data reproduction and forensic reimplementation of the machine-learning
evaluation and downstream dipole-coupling/screening workflow in
[Hu et al., *Nature Catalysis* **8**, 126–136 (2025)](https://doi.org/10.1038/s41929-025-01291-z).
The project evaluates released predictions and reconstructs their downstream algebra
without rerunning molecular dynamics, quantum chemistry or neural-network training.
**Version 0.1.0 is an unreleased candidate for human review.**

Start with the [scientific reproduction note](docs/ML_REPRODUCTION_NOTE.md),
[claim scorecard](forensics/reports/ML_CLAIM_SCORECARD.md) and
[reproduction guide](docs/REPRODUCE.md).

## Key result

The released scalar metrics reproduce to floating-point precision. A common tensor
nearly exactly reconstructs the dipole-to-coupling transformation, and exact error
propagation explains how poorer signal-relative transition-vector fidelity carries
into J*. Original network training remains unreproducible because feature matrices,
weights and essential training settings were not released. New MD/QM is unnecessary
for this bounded evaluation.

| Metric over 1,000 released validation rows | J | J* |
|---|---:|---:|
| Pearson r | 0.912926 | 0.747549 |
| Predictive R² | 0.829605 | 0.558007 |
| RMSE, respective source numerical units | 224.144248 | 0.494508 |
| Sign agreement | 74.7% | 74.3% |
| Signed Spearman ρ | 0.777783 | 0.692213 |
| Signed top-100 overlap | 80/100 | 65/100 |

These are validation-row metrics, **not rankings of the 180 photocatalytic systems**.
Raw RMSEs on different numerical scales cannot establish relative difficulty.

## What this repository reproduces

- The descriptor screen: 18 catalysts × 10 photosensitizers = 180 candidate identities.
- All 32 dipole scalar-metric records recomputed from released predictions, with vector magnitude/direction reanalysis.
- The numerical dipole-to-coupling transform and exact CAT/PS/cross error decomposition.
- Sign and ranking fidelity on the 1,000 released coupling-validation rows.
- Partial screening-map reconstruction and measured-set validation arithmetic.
- The disclosed architecture family as an untrained, dependency-light specification.

![Recoverability of the released workflow](figures/derived/reproducibility_ladder.png)

The ladder distinguishes exact released-data arithmetic from numerical reimplementation,
partial recovery and unavailable original computation; it does not imply retraining.

## What it does not reproduce

Original X, authenticated labelled geometries, atom selection/preprocessing, full model
grouping and training settings, trained weights, full trajectories, all 180 pair scores
and the pair-level aggregation rule remain unavailable. Released endpoint coordinates
do not supply those missing joins. The retained [full-computation plan](docs/COMPUTE_PLAN.md)
is a separate optional project and has not been executed.

## Main findings

The recovered relation is `J = s*(-2*Cx*Px + Cy*Py + Cz*Pz)`, with
`s = 5.034063649307054`; it also applies to transition dipoles for J*.
Debye/cm⁻¹ with an effective distance of approximately 10.000035 Å is a strong,
conditional interpretation. Units and distance are not uniquely identifiable, and
exactly 10 Å with modern constants does not fully explain the stored precision.

For 100 test vectors per family, normalized CAT error rises from 0.267 to 0.481
and PS error from 0.260 to 0.504 for transition targets. CAT median angular error
improves while PS worsens. Cross terms are relatively larger for J*, but negative
covariation reduces total MSE. The loss of fidelity is therefore more nuanced than
more sign flips or an additive second-order penalty.

The released screening map contains 34 positive points. The compatible
`J > 50, J* > 0.01` probe selects seven, but six tested threshold cells give seven
points and only three preserve the same membership. Measured-set precision is
`6/6 = 100%` and recall `6/7 = 85.714%`; neither is a global estimate across 180
or 3,444 systems. See the [note and its four analytical figures](docs/ML_REPRODUCTION_NOTE.md)
for equations, identities and evidence limits.

## Reproduce the analysis

Use Python 3.12. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/build_public_figures.py
```

Tests use synthetic inputs; figures use committed analytical summaries. Neither
requires publisher files. Dependencies are NumPy, openpyxl, pypdf and Matplotlib.
To independently rerun the workbook analyses, obtain the three local inputs listed
in [REPRODUCE.md](docs/REPRODUCE.md), then run:

```sh
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_ml_vectors.py
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_error_propagation.py
PYTHONDONTWRITEBYTECODE=1 python forensics/scripts/analyze_screening_sensitivity.py
```

The guide distinguishes numerical agreement from the separate historical archive
integrity check and explains why fresh publisher copies may have different bytes.

## Repository structure

| Location | Contents |
|---|---|
| `docs/` | Main note, rerun guide, algorithm contract and candidate notes |
| `src/hu2025_repro/`, `tests/` | Numerical analysis, untrained architecture specification and synthetic tests |
| `scripts/`, `figures/derived/` | Deterministic figure builder and original analytical illustrations |
| `data/derived/` | Computed metrics, reconstructed identities and classification decisions |
| `forensics/reports/`, `forensics/outputs/` | Evidence reports and compact analytical summaries |
| `data/manifests/` | Source provenance, filenames and integrity metadata |
| `configs/` | Disclosed/unknown settings and optional unexecuted compute contracts |
| `orginal/`, `forensics/local_only/` | Immutable local sources and complete extracts; ignored |

## Source-data policy

Publisher PDFs, source workbooks, author coordinates, archives and full numerical
extracts are intentionally excluded from Git and its history. `orginal/` preserves
its existing spelling. Do not force-add, relocate, convert or use Git LFS to bypass
that boundary. Public figures summarize derived statistics, without republishing
source-point arrays. See the [source policy](docs/SOURCE_POLICY.md).

## Citation

Original article: Hu, Y. et al. Identifying a highly efficient molecular photocatalytic
CO₂ reduction system via descriptor-based high-throughput screening. *Nature Catalysis*
**8**, 126–136 (2025). [DOI](https://doi.org/10.1038/s41929-025-01291-z).

Repository: Squiddy. *Hu 2025 Photocatalysis ML Reproduction*, version 0.1.0
(unreleased review candidate). [Repository](https://github.com/angzeli/hu2025-photocat-ml-repro).
[CITATION.cff](CITATION.cff) is the single canonical version declaration and supplies
machine-readable repository and article citations. No release DOI or tag is claimed.

## License

[MIT](LICENSE) covers this repository's original code and documentation, including
its analytical illustrations. Publisher/source materials are not distributed and
are not relicensed. See the [candidate notes](docs/RELEASE_NOTES_v0.1.0.md) for scope,
limitations and validation.
