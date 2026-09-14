# v0.1.0 release candidate

Status: prepared for review, not a published release. [CITATION.cff](../CITATION.cff)
is the canonical version declaration. No version tag, GitHub Release, package-registry
publication or DOI deposit is created by this candidate.

## Scope

Independent source-data reproduction and forensic reimplementation of the ML
evaluation and downstream dipole-coupling/screening workflow in
[Hu et al., Nature Catalysis (2025)](https://doi.org/10.1038/s41929-025-01291-z).
The candidate packages completed analytical results with a
[scientific note](ML_REPRODUCTION_NOTE.md), reproducible derived figures,
[external-reader instructions](REPRODUCE.md), citation metadata and a scoped MIT
license. It does not regenerate the underlying physical dataset or trained network.

## Major reproduced results

- All 32 released scalar metric records reproduce to floating-point precision;
  vector magnitude, direction and residual analyses expose limitations concealed
  by pooled Cartesian correlations.
- The recovered relation is `J = s*(-2*Cx*Px + Cy*Py + Cz*Pz)` with
  `s = 5.034063649307054`, applying to intrinsic and transition validation channels.
  Debye/cm⁻¹ and an effective separation of approximately 10.000035 Å are a
  conditional, non-unique physical interpretation, not disclosed author settings.
- CAT/PS/cross prediction-error decomposition closes within approximately
  `1.03e-12` for J and `1.34e-15` for J*. This exact algebra is distinct from the
  small source-precision residuals against separately rounded Fig. 9 columns.
- On the 1,000 released validation rows, J/J* Pearson correlations are
  0.912926/0.747549, predictive R² values 0.829605/0.558007, sign agreement
  74.7%/74.3%, and signed top-100 overlap 80/100 versus 65/100.
- Transition errors are larger relative to vector signal: test normalized CAT
  error increases from 0.267 to 0.481 and PS from 0.260 to 0.504. CAT median angular
  error improves while PS worsens. Cross terms have greater relative magnitude
  for J* but reduce total MSE through negative covariation; a simple sign-flip or
  second-order explanation is insufficient.
- The supplied screening map has 34 positive points. The 50/0.01 probe selects
  seven, but six sampled threshold cells give that count and only three preserve
  the same seven members. This is partial screening reconstruction.
- Measured-set precision/recall reproduce as `6/6 = 100%` and `6/7 = 85.714%`.
  The selected but unsynthesized CAT50/PS41 system is outside measured precision.

## Limitations

Original X, geometry-to-label joins, exact atom selection/preprocessing, model
count/grouping, complete training settings and weights remain unavailable. The
architecture module represents only the disclosed family, without trained parameters.
Full trajectories, the complete 180-system score table and the pair-level aggregation
rule are not recovered. Validation-row ranking is not 180-system ranking, and the
tested-set experimental arithmetic is not global precision/recall.

The unit/distance interpretation and author screening thresholds remain conditional.
New MD, QM, TDDFT or ML training is unnecessary for this bounded evaluation scope;
the retained [full-computation plan](COMPUTE_PLAN.md) is optional and unexecuted.

## Provenance and license

No publisher PDFs, source workbooks, author coordinates, archives or full numerical
extracts are distributed. Originals remain immutable and local-only under `orginal/`;
full extracts remain ignored. The public figures are generated from committed
analytical summaries and do not republish the original scatter-point tables.

The repository's [MIT license](../LICENSE) covers its original code and documentation.
It does not grant rights over or relicense the original paper or supplementary data.
The [source policy](SOURCE_POLICY.md) remains in force, including for Git history.

## Validation

The [local candidate validation record](../forensics/outputs/phase3_validation.json)
records:

- 34/34 synthetic tests passed, including six publication-boundary regressions.
- All three Phase-2 analyses passed; their outputs matched the committed Phase-2 bytes.
- Repeat figure generation with a fresh plotting cache reproduced all eight files
  byte for byte in the tested reference environment; all PNG/PDF renderings passed
  visual review. Cross-platform renderer byte identity is not claimed.
- All 6,901 originals retained their hashes, sizes and modification times.
- Source-exclusion and sensitive-information audits reported zero findings across
  proposed content and reachable history, including the separately inspected local
  auxiliary objects. Figure exceptions require exact reviewed path/hash bindings.

These are local candidate checks, not remote CI results, a published release or
independent scientific approval. The reference Python and four direct dependency
pins are documented in [the reproduction guide](REPRODUCE.md) and
[requirements.txt](../requirements.txt).

No new molecular trajectory, quantum label or trained ML model is produced by this
candidate. Final tagging and GitHub Release creation require separate authorization
after human review.
