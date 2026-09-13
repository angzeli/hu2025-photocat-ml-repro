# Phase 1: forensic coupling reconstruction

Hu et al., *Nature Catalysis* **8**, 126–136 (2025),
[DOI 10.1038/s41929-025-01291-z](https://doi.org/10.1038/s41929-025-01291-z).
Audit date: 2026-09-13. The [deterministic script](../scripts/reconstruct_coupling.py)
reads the ignored local MOESM2 workbook directly as OOXML. Its
[compact output](../outputs/phase1_coupling.json) contains statistics, not source arrays.

Evidence categories: **DIRECTLY OBSERVED** (including what a source says),
**COMPUTED FROM RELEASED DATA**, **STRONG INFERENCE**, **SPECULATION**, and
**REIMPLEMENTATION CHOICE**. Source statements and inferred conventions are not
independent scientific validation. No MD, QM or neural-network training was run.

## 1. Executive conclusion

**COMPUTED FROM RELEASED DATA:** Fitting only the first 900 calculated intrinsic
rows independently recovers `s = 5.034063649307054` in
`J = s*(-2*mu_CAT_x*mu_PS_x + mu_CAT_y*mu_PS_y + mu_CAT_z*mu_PS_z)`.
The same scalar nearly reconstructs the final 100 calculated intrinsic rows and
all predicted intrinsic, calculated transition and predicted transition rows.
The released-label x tensor overwhelmingly outperforms y and z.

**STRONG INFERENCE, CONDITIONAL:** Debye dipoles, coupling in cm⁻¹, vacuum
permittivity and a fixed effective separation near 10 Å give a natural physical
interpretation. Independently evaluated constants imply **10.00003503953813 Å**.
The scalar does not identify units and distance separately: meV with Debye dipoles
instead implies a plausible 4.98644 Å. Exactly 10 Å with modern constants is outside
the conditional five-decimal rounding interval. Neither exact 10 Å nor the authors'
trajectory/frame processing has been established.

**REIMPLEMENTATION CHOICE:** Freeze a physical coupling API with declared units,
both actual-COM and explicitly standardized-distance evaluations, four candidate
aggregations, and documented future defaults. The contract is ready for pilot
pipeline implementation; calculation launch requires the remaining chemistry and
resource gates. Exact author-model reproduction remains unavailable.

## 2. Starting evidence

The authoritative Phase-0 basis is [data forensics](PHASE0_DATA_FORENSICS.md),
[reproducibility matrix](REPRODUCIBILITY_MATRIX.md), [methods](PAPER_METHODS_AUDIT.md),
[workbooks](WORKBOOK_ML_AUDIT.md), and [structures](STRUCTURE_INVENTORY.md).

**DIRECTLY OBSERVED:** The initial branch was `main`, with two unpublished commits:
`accb925f374f31fed6f8c6943933136dbecb684d` and
`994778306d61d774ad08137c0bfce87e005e1552`. The configured public origin was empty
when inspected at Phase-1 entry. On explicit user authorization, only the latter
commit was amended to `bf130ce19c68afd4415bd15fce1ebf44d3433a6e`, sanitizing paths in
`docs/PHASE0_REPRODUCTION.md` and `PAPER_METHODS_AUDIT.md`. Its parent and scientific
content were preserved. Publication checks and scope are recorded
[separately](PHASE1_PUBLICATION_AUDIT.md).

**COMPUTED FROM RELEASED DATA:** Bounded Phase-0 screening and ML reruns confirmed
18 CAT × 10 PS = 180 retained identities; four 1,000-vector tables with 900/100
train/test blocks; and 1,000 J plus 1,000 J* calculated/predicted comparisons.
The original 6,901-file baseline remained unchanged in hashes, sizes and mtimes.
The missing full trajectories, geometry-to-label joins, weights and aggregation
map were not recreated by this check.

**DIRECTLY OBSERVED:** MOESM2 Supplementary Figs. 5/6 hold intrinsic CAT/PS vectors;
Figs. 7/8 hold transition CAT/PS vectors. For each figure, training calculated and
predicted components occupy A/B, F/G and K/L, rows 4–903; test components occupy
C/D, H/I and M/N, rows 4–103. Fig. 9 uses A/B for J and D/E for J*, rows 3–1002.
Concatenate training then test; do not interleave or sort by value.

## 3. Reproduced tensor relation

**REIMPLEMENTATION CHOICE FOR THE DIAGNOSTIC:** Define component-product numerator
`q_i = -2*c_ix*p_ix + c_iy*p_iy + c_iz*p_iz` and fit one zero-intercept scalar:

```text
s = sum(i=1..900, q_i * J_i) / sum(i=1..900, q_i^2)
```

**COMPUTED FROM RELEASED DATA:** The result is `5.034063649307054`. No remaining
row or channel enters its fit. Residuals below mean reconstructed minus released;
R² means `1 − SSE/SST`, with the observed mean recomputed within each stated block.
Errors are in the released numeric coupling units, whose physical identity is inferred.

| Channel | All-1,000 R² | All-1,000 RMSE | Final-100 RMSE | Maximum absolute residual |
|---|---:|---:|---:|---:|
| Calculated J | 0.9999999999996017 | 0.000342697862 | 0.000303256551 | 0.002111578645 |
| Predicted J | 0.999999991169988 | 0.043528852936 | 0.137646862436 | 0.666477879087 |
| Calculated J* | 0.999999145488319 | 0.000687582344 | 0.000678640877 | 0.009762905537 |
| Predicted J* | 0.999999247022084 | 0.000463991357 | 0.000468726507 | 0.005837998124 |

Calculated-J fit-900 RMSE is 0.000346803452; final-100 R² is
0.9999999999996879. These are reconstruction metrics, not new ML test performance.
The independent OOXML reader reproduces the Phase-0 scalar and channel errors.

**STRONG INFERENCE:** Released numerical row correspondence is supported within
each intrinsic or transition pairing. Matching row numbers across both families
does not prove that their labels share one physical geometry or electronic-state provenance.

## 4. Axis-uniqueness tests

**COMPUTED FROM RELEASED DATA:** Each axis gets its own scalar fit on the same
first 900 calculated-J rows, with no matrix fitting or holdout selection.

| Released-label separation | Diagonal weights | Fitted scalar | All-1,000 R² | Fit-900 RMSE | Final-100 R² | Final-100 RMSE |
|---|---|---:|---:|---:|---:|---:|
| x | −2, +1, +1 | 5.034063649307054 | 0.9999999999996017 | 0.000346803452 | 0.9999999999996879 | 0.000303256551 |
| y | +1, −2, +1 | −3.784051522420018 | 0.508511771 | 387.132768 | 0.659609578 | 316.699574 |
| z | +1, +1, −2 | −3.095221527378613 | 0.224528982 | 482.141004 | 0.340510767 | 440.821399 |

Even allowing unphysical negative prefactors, y/z fail by orders of magnitude.
With a nonnegative scalar their least-squares optimum is the zero boundary, since
their unconstrained numerator–response inner products are negative. Residual
means, quantiles and response correlations are retained in the JSON; y/z errors
are structural, not comparable to the x result's rounding-scale residuals.

**COMPUTED FROM RELEASED DATA:** All six PS-only permutations × eight relative
component sign patterns were evaluated (48 candidates), still with only one scalar.
The original relative components and their global sign reversal are degenerate
when a signed scalar is allowed. The next nonequivalent candidate has fit RMSE
178.218168 and final-100 RMSE 114.117629. Requiring a positive physical prefactor
selects the original relative sign convention among these probes.

**STRONG INFERENCE WITH SYMMETRIES:** x is overwhelmingly favored in the released
component labels; it is not an absolute laboratory-axis identification. The tensor
is unchanged by `r → −r`, a common transverse rotation, simultaneous y/z exchange,
or simultaneous reflection of corresponding components in both dipoles. Consistent
relabelling of both vector axes and separation is also equivalent. These symmetries
cannot be resolved by the scalar validation data.

## 5. Physical-constant/unit reconstruction

**DIRECTLY OBSERVED IN PRIMARY REFERENCES:** Use CODATA 2022
`epsilon0 = 8.8541878188e-12 F/m` (standard uncertainty `1.4e-21 F/m`), exact
`h = 6.62607015e-34 J s`, `c = 299792458 m/s`, and `e = 1.602176634e-19 C`.
The atomic-unit alternative uses `a0 = 5.29177210544e-11 m`.
[NIST constants table](https://physics.nist.gov/cuu/Constants/Table/allascii.txt).
Use the conventional Debye conversion `D = 1e-21/c C m` and `Å = 1e-10 m`.
[NIST dipole units](https://cccbdb.nist.gov/dipunitsx.asp).

**COMPUTED FROM RELEASED DATA (primary constants):** Strictly, D²/Å³ becomes an energy only after
including the Coulomb prefactor. For unit dipole-component product and unit distance,

```text
C_J    = D^2 / (4*pi*epsilon0*(1e-10 m)^3)
C_eV   = C_J/e
C_meV  = 1000*C_eV
C_cm-1 = C_J/(h*c*100)
```

| Energy representation | Coefficient per D² Å⁻³, including Coulomb prefactor |
|---|---:|
| J | 9.999999998667733 × 10⁻²⁰ |
| eV | 0.6241509073629228 |
| meV | 624.1509073629228 |
| cm⁻¹ | 5034.116566872031 |

These constants are evaluated by the physical API independently of the fitted
scalar. This row is an analytic computation, not a source-data-derived setting.
No relative dielectric multiplier is introduced implicitly.

## 6. Effective-distance inference

**COMPUTED FROM RELEASED DATA AND CONSTANTS, CONDITIONAL ON UNITS:** With both
dipoles in Debye and energy in cm⁻¹, `r_eff = (C/s)^(1/3)` gives:

- Effective distance: **10.00003503953813 Å**.
- Absolute excess over 10 Å: **0.0000350395381297 Å**.
- Relative excess: **3.50395381297 × 10⁻⁶** (3.504 ppm).
- Modern-constant scalar at exactly 10 Å: **5.034116566872031**.
- Empirical minus nominal scalar: **−0.0000529175649771**, or **−10.5118 ppm**.

The epsilon0 uncertainty alone contributes relative distance uncertainty
`5.27e-11`, far smaller than this discrepancy. Section 7 shows why five-decimal
rounding of calculated intrinsic inputs does not erase the exact-10 discrepancy.

**COMPUTED FROM RELEASED DATA AND CONSTANTS:** Plausible alternate interpretations
must be retained; these all assume vacuum screening and both dipoles in the same unit.

| Dipole unit | Coupling unit | Implied distance / Å |
|---|---|---:|
| Debye | eV | 0.498644 |
| Debye | meV | 4.986437 |
| Debye | cm⁻¹ | 10.000035 |
| Atomic (`e*a0`) | meV | 9.287064 |
| Atomic (`e*a0`) | cm⁻¹ | 18.624717 |

**STRONG INFERENCE, NOT UNIQUE:** Debye/cm⁻¹/near-10 Å is a natural round-distance
interpretation of the x tensor. Debye/meV/near-5 Å is also natural, so the numerics
do not support calling the first convention overwhelmingly unique. Literal eV/Debye
would imply unusually small molecular COM separation, but that alone proves no unit.
Changing length units or dielectric screening adds further degeneracy. A shared
intrinsic/transition scalar does not naturally support intrinsic Debye plus
transition atomic units at one common distance/energy unit without a compensating
conversion: the squared dipole conversion would otherwise differ by about 6.46.

## 7. Residual/rounding analysis

**DIRECTLY OBSERVED:** OOXML stores numeric tokens, often with binary-serialization
tails out to roughly 17 significant digits. Most values are compatible with five
decimal places after an eight-ULP tail tolerance. Some dipole blocks instead show
three-significant-digit precision. General and `0.00E+00` cell formats only control
display; they do not specify the error in stored values. A shortened trailing zero
does not establish coarse precision by itself. Histograms are in the compact output.

**REIMPLEMENTATION CHOICE FOR BOUNDED DIAGNOSTICS:** With component error bounds
`e_c`, `e_p` and coupling bound `e_J`, use the deterministic product bound

```text
|delta J| <= |s| sum_k |w_k| (|p_k|*e_ck + |c_k|*e_pk + e_ck*e_pk) + e_J
```

The first two terms are first order; the product term makes the box bound
conservative to second order. A separate floating-point arithmetic allowance is
included. No hidden unrounded values are estimated or optimized. Test nearest
five-decimal rounding with half steps `0.5e-5`, and a looser full-step truncation
box. Literal XML last-digit errors are recorded only as a serialization diagnostic.

**COMPUTED FROM RELEASED DATA:** For calculated J, all 1,000 residuals satisfy
the five-decimal nearest-rounding bounds. The maximum first-order contribution is
0.004168202688, maximum cross term `5.034063649e-10`, and maximum total bound
0.004173203381. Compare maximum observed residual 0.002111578645, median absolute
residual 0.000230037827, 95th percentile 0.000647680286 and 99th percentile
0.001040488809. Mean signed residual is 0.000016094815; residual/observed correlation
is −0.02935. The maximum rowwise residual/bound ratio is 0.8548. Truncation boxes
also accommodate the errors but cannot distinguish truncation from nearest rounding.
Rounding the fitted scalar to `5.03406364931` adds at most `2.83e-9` to J, so scalar
display rounding alone cannot explain the observed residual scale.

| Channel | Rows inside uniform-5dp bounds | Rows inside mixed-precision bounds | Largest mixed residual/bound |
|---|---:|---:|---:|
| Calculated J | 1,000/1,000 | 1,000/1,000 | 0.8548 |
| Predicted J | 906/1,000 | 1,000/1,000 | 0.8730 |
| Calculated J* | 404/1,000 | 1,000/1,000 | 0.9792 |
| Predicted J* | 372/1,000 | 1,000/1,000 | 0.9530 |

**STRONG INFERENCE / CONDITIONAL COMPATIBILITY:** Uniform five-decimal precision
is inadequate for every channel. The larger predicted-J residuals are concentrated
in its test block, whose CAT-z and PS-y values predominantly match three significant
digits. Transition columns also contain coarser blocks. A mixed diagnostic grants
a three-significant-digit half step only to cells numerically compatible with that
precision, keeping at least a five-decimal bound elsewhere and five-decimal J bounds.
It accommodates all 4,000 residuals. Coincidentally short numbers remain ambiguous;
this bounds-based compatibility does not recover the authors' rounding code or
joint latent values. No additional tensor transformation is demanded by these bounds.

**COMPUTED FROM RELEASED DATA, CONDITIONAL:** Intersecting the positive-scalar
rounding-box intervals from the first 900 calculated-J rows gives
`[5.034062503876238, 5.034066337226311]`, corresponding under Debye/cm⁻¹ to
`[10.000033259711792, 10.000035797994308] Å`. These are compatibility intervals,
not statistical confidence intervals. Exactly 10 Å with modern constants lies
outside: 721/1,000 rows exceed its five-decimal bounds (649 fit, 72 held out),
with RMSE about 0.00571309 and strongly scale-correlated residuals. A slightly
different effective scalar is supported; its origin is not identified.

**SPECULATION:** Rounded historical conversion constants, a slightly different
distance or another normalization could explain that remaining prefactor difference.
The evidence does not select among them. This limitation does not undermine the
overwhelming numerical support for the common x tensor.

## 8. Implications for the published MD→coupling story

**DIRECTLY OBSERVED:** The Methods calls `r_CP` the CAT-to-PS COM vector. Released
validation rows have no authenticated geometry/displacement join.

| Interpretation | Compatibility and evidence boundary |
|---|---|
| A. All validation geometries shared a fixed separation near 10 Å | **SPECULATION, compatible conditionally:** Would work in the aligned frame under the stated units. The rows do not show that freely sampled MD geometries actually had this separation. Exact modern-constant 10 Å is not established. |
| B. MD supplied conformations/orientations, then centres were standardized | **SPECULATION, compatible:** Constant direction and distance at coupling evaluation naturally give the recovered tensor; no source script documents the operation. |
| C. Dipoles were transformed to an x-aligned pair frame | **SPECULATION, compatible but insufficient alone:** Alignment gives the diagonal tensor, but variable COM distance still changes `r^-3`; a constant effective distance or compensating convention is also required. |
| D. An equivalent numerical convention produced the same tensor | **SPECULATION, compatible and underdetermined:** Unit conversion, displacement normalization or rescaled vectors can produce an equivalent effective scalar; released data cannot identify the hidden route. |

**STRONG INFERENCE:** One effective tensor describes these validation arrays.
A general variable-distance, variable-direction lab-frame calculation on the
released dipoles would ordinarily require row-dependent coefficients. Algebraic
coincidences or hidden transformations prevent a proof of impossibility for every
other geometry story. The result neither authenticates the MD trajectories nor
establishes that all 180,000 screening conformations used this same preprocessing.

## 9. What is now algorithmically recoverable

**COMPUTED FROM RELEASED DATA:** The first-screen identity set; released validation
block membership and prediction metrics; a fixed diagonal tensor, scalar and channel
errors; bounded orientation controls; and conditional unit/distance and rounding
compatibility are reproducible locally without distributing the underlying arrays.

**REIMPLEMENTATION CHOICE:** The minimal [coupling API](../../src/hu2025_repro/coupling.py)
provides full-vector and fixed-axis coupling with Debye/Å inputs, J/eV/meV/cm⁻¹
conversion, NumPy broadcasting, and explicit signed mean, mean absolute,
absolute signed mean and RMS operations. It rejects invalid/nonfinite inputs and
zero displacement; aggregation mode is required. Entirely
[synthetic tests](../../tests/test_coupling.py) cover parallel/perpendicular vectors,
x/y/z, sign, inverse-cube scaling, rotational covariance, batches, conversions and
all four aggregations. The fitted scalar is not embedded as a production constant.

## 10. What remains unknowable from the available release

**DIRECTLY OBSERVED ABSENCE / UNKNOWN:** Exact ML geometries and input schema,
original sample IDs and geometry joins, full trajectories, original weights and
complete hyperparameters, actual dipole/coupling units, COM separation processing,
charged-species origins, electronic-state/root and transition-phase conventions,
pair-level aggregation, full 180-pair scores, and most score-to-identity assignments
remain missing or underdetermined. The published adsorption-energy plus sign and
separate-molecule versus paired-conformation accounting remain unresolved.

**STRONG INFERENCE BOUNDARY:** Recovering the validation transformation does not
repair those omissions or make exact author-model reproduction possible. Future
training, trajectories and ranking comparisons must be described as independent.

## 11. Frozen Phase-2 contract

The [11-stage specification](../../docs/ALGORITHM_SPEC.md) separates published
statements, recovered evidence, missing pieces and reproduction consequences.
The [authoritative contract](../../docs/REIMPLEMENTATION_CONTRACT.md) and matching
[configuration](../../configs/reimplementation_v1.yaml) separate three sources of settings:

- **DIRECTLY OBSERVED:** Published candidate/screening counts, MD conditions,
  named quantum methods, partial NN architecture/optimizer and split counts.
- **COMPUTED FROM RELEASED DATA / STRONG INFERENCE:** The tensor and scalar,
  released row structure, and conditional near-10 Å interpretation.
- **REIMPLEMENTATION CHOICE:** Four vector regressors; explicit features, atom
  order, frames, normalization, loss/L1/training controls and seeds; bounded
  state/solvent/root candidates; physical units; both distance conventions;
  all four aggregation rules. Unknown chemical inputs remain null and block jobs.

For own standardized calculations, rotate both dipoles together so the actual
minimum-image COM vector aligns with +x, then set its magnitude to 10 Å. This is
a chosen normalization, not a recovered author operation. Preserve COM-origin
charged dipoles and consistently undo molecular feature rotations; phase tracking
uses aligned molecular frames. Temporal grouping reduces within-block split mixing
but does not remove correlation across block boundaries. No aggregation is promoted
to an author setting, and no pilot is a surrogate-validation benchmark.

## 12. Recommended first compute experiment

**REIMPLEMENTATION CHOICE, NOT EXECUTED:** The [compute plan](../../docs/COMPUTE_PLAN.md)
starts with CAT1/PS1 and CAT61/PS33, both retained identities with contrasting known
experimental classifications. First implement source-backed identity/state manifests,
synthetic frame checks and local-only dry-run MD/QM input generation. Resolve charge,
spin, counterions, topology/UFF, installed programs, PCM assignment and transition roots
before launch. Propose at most two 10.4 ps trajectories, four snapshots each, 16
molecule-geometry records and 32 total QM attempts including retries and sensitivities.
No NN training belongs to this pilot. Resource ceilings are proposals, not reservations.

The minimal subsequent path reuses released descriptors and independently regenerates
downstream data; the full path additionally recomputes adsorption and lifetime
descriptors after their definition gates. Neither path is authorized by this report.

Phase-1 validation uses the bounded screening/ML reruns, the reconstruction script,
all eight synthetic coupling test groups, configuration parsing/consistency checks,
the original integrity baseline, and Git-aware source/privacy review. Reproduction
commands require an environment with NumPy, openpyxl and pypdf; source workbooks
remain local prerequisites, while synthetic tests need only NumPy:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 forensics/scripts/reconstruct_coupling.py
```

These checks validate the released-table reconstruction and the analytic API.
They do not establish successful or scientifically accepted future MD/QM/ML runs.
