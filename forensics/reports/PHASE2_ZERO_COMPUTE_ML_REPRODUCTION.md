# Phase 2: zero-new-scientific-compute ML reproduction

Hu et al., *Nature Catalysis* **8**, 126–136 (2025),
[DOI](https://doi.org/10.1038/s41929-025-01291-z). Audit date: 2026-09-13.
This report concerns deterministic evaluation of released predictions. “Zero compute”
means zero new MD, QM, TDDFT, label generation or ML training; ordinary CPU arithmetic
is necessary to reproduce metrics and is not a new scientific simulation.

## 1. Executive conclusion

**COMPUTED FROM RELEASED DATA:** All 32 Phase-0 scalar metric records are
independently reproduced, with maximum difference 4.45e-16. Coupling correlations
are **r(J)=0.9129259525** and **r(J*)=0.7475491726**. The frozen tensor reconstructs
the four Fig. 9 channels to the same small source-precision residuals as Phase 1.
Its exact CAT/PS/cross error expansion closes within **1.03e-12 for J** and
**1.34e-15 for J***, without fitting anything.

Transition predictions have larger errors relative to their signal: test normalized
vector errors are 0.481/0.504 for CAT/PS transition versus 0.267/0.260 for intrinsic.
Both coupling-weighted magnitude and direction channels are larger relative to J*'s
signal. This is not uniformly worse angular prediction: CAT transition's median angle
is better, while PS transition's is worse. Sign agreement is almost unchanged
(74.7% versus 74.3%). Second-order terms are relatively larger for J* but **reduce**
total MSE through negative covariation, so they cannot simply be blamed for the loss.

The 34-point screening map supports a seven-point compatibility probe, not a unique
classifier or a complete 180-system ranking. Six grid cells yield seven points;
only three preserve the probe's same seven members. Measured-set precision/recall
are independently reproduced as 6/6 and 6/7.

The repository now distinguishes source-data metric reproduction from an executable
author training pipeline. Exact original training, physical dataset regeneration,
the full 180-system ranking and trajectory aggregation remain unavailable. These
limitations do not require launching new calculations for the present bounded task.

## 2. Scope and zero-compute boundary

**DIRECTLY OBSERVED:** Local `main`, upstream `origin/main` and the remote main ref
all started at `8d672db7a56cbe2be533ebb8f8c77cfbd5fbe77d`, with a clean working tree.
The previous phases' original-file baseline passed at entry. This task is authorized
to make a local commit only; it does not push or rewrite published history.

Allowed work was NumPy/standard-library statistics, workbook/PDF reading, exact
algebra, a dependency-free architecture specification, documentation and synthetic
tests. No TensorFlow/Keras import, model fitting, optimizer step, GPU operation,
scientific-job submission, geometry generation or optimization was needed.
All full source values remain in memory or previously ignored local-only extracts.
Tracked CSV/JSON outputs contain aggregate metrics, small error-row locators and
bounded sensitivity results, not full source tables. Compact comparison tables and
the threshold grid below carry the numerical conclusions without duplicating the
publisher's scatter plots or changing the source-exclusion policy.

Evidence labels remain **DIRECTLY OBSERVED**, **COMPUTED FROM RELEASED DATA**,
**STRONG INFERENCE**, **SPECULATION**, and **REIMPLEMENTATION CHOICE**. R² below is
predictive `1 − SSE/SST`; it is not Pearson r squared. Error means predicted minus
calculated. Original numerical dipole/coupling units are unidentified, so raw errors
retain source-number units; cross-family conclusions use normalized measures.

## 3. Released ML dataset structure

**DIRECTLY OBSERVED / COMPUTED FROM RELEASED DATA:** MOESM2 Supplementary Figs. 5–8
respectively contain CAT intrinsic, PS intrinsic, CAT transition and PS transition
dipoles. Each family provides calculated/predicted x/y/z components for 900 training
and 100 test vector rows. Training pairs occupy A/B, F/G, K/L rows 4–903; test pairs
occupy C/D, H/I, M/N rows 4–103. Order is preserved. The numerical comparison reads
workbook XML through the bounded Phase-1 reader and independently evaluates metrics.

Pooling x/y/z yields 2,700 train or 300 test scalar observations, representing only
900 or 100 vector rows per family. This is not an increased number of independent
conformations. Four target tables do not establish four independent geometry samples
or a common physical geometry join across intrinsic and transition targets.

Fig. 9 has 1,000 calculated/predicted rows for each of J and J*. Phase 1 strongly
supports first-900 then final-100 numerical alignment to the dipole blocks. Any such
coupling split below is an inherited numerical block designation, not a newly
established author coupling-test protocol. No validation set is invented.

## 4. Scalar metric reproduction

**COMPUTED FROM RELEASED DATA:** Fresh calculations agree with all 32 earlier
component/pooled records. This table pools x/y/z but gives vector-row counts:

| Target | Split | Vector rows | Pearson r | Predictive R² | MAE | RMSE | Bias |
|---|---|---|---|---|---|---|---|
| CAT intrinsic | train | 900 | 0.945356 | 0.892176 | 1.427174 | 2.337915 | 0.244696 |
| CAT intrinsic | test | 100 | 0.964168 | 0.928739 | 1.595103 | 2.171721 | 0.086017 |
| PS intrinsic | train | 900 | 0.965032 | 0.931199 | 1.158132 | 1.606455 | 0.030202 |
| PS intrinsic | test | 100 | 0.965538 | 0.931915 | 1.140544 | 1.515579 | 0.004633 |
| CAT transition | train | 900 | 0.844695 | 0.704106 | 0.032910 | 0.055673 | 0.007973 |
| CAT transition | test | 100 | 0.879775 | 0.768187 | 0.031160 | 0.046658 | 0.007391 |
| PS transition | train | 900 | 0.862415 | 0.741005 | 0.191950 | 0.265942 | -0.022062 |
| PS transition | test | 100 | 0.864336 | 0.745103 | 0.199044 | 0.278501 | 0.007470 |

Test-minus-train pooled errors (same source-number units):

| Target | Δ MAE | Δ RMSE | Δ bias |
|---|---|---|---|
| CAT intrinsic | +0.167929 | -0.166194 | -0.158679 |
| PS intrinsic | -0.017587 | -0.090876 | -0.025569 |
| CAT transition | -0.001751 | -0.009015 | -0.000582 |
| PS transition | +0.007095 | +0.012559 | +0.029532 |

Three of four pooled test RMSEs are smaller than their training counterparts;
PS transition is the exception. These numerical gaps do not identify their cause.

The full per-component and pooled metrics are in
[ml_scalar_metrics.csv](../../data/derived/ml_scalar_metrics.csv); generalization
gaps are in [phase2_ml_vectors.json](../outputs/phase2_ml_vectors.json).
Test-minus-train differences describe these supplied blocks. A smaller test error
does not establish leakage, improved transfer or a statistically significant change;
the underlying geometries, sampling dependence and original selection remain unknown.

## 5. Vector-level ML performance

**REIMPLEMENTATION CHOICE:** Direction requires both norms strictly above 1e-3
in source dipole units; relative magnitude error requires only the calculated norm
above that threshold. Absolute summaries keep every row. The simple sensitivity
set is 1e-4, 1e-3 and 1e-2. All 900/100 rows survive the default and lower threshold.

**COMPUTED FROM RELEASED DATA:** Normalized vector error means
`RMS(||mu_hat-mu||) / RMS(||mu||)`, not a mean of unstable rowwise ratios.
Magnitude errors use `||mu_hat||-||mu||`; the last column is the median absolute
relative magnitude error among eligible rows.

| Target | Split | Normalized vector error | Magnitude r | Magnitude MAE | Magnitude RMSE | Median relative magnitude error |
|---|---|---|---|---|---|---|
| CAT intrinsic | train | 0.3275 | 0.9683 | 1.815171 | 2.704548 | 0.3263 |
| CAT intrinsic | test | 0.2665 | 0.9780 | 1.749662 | 2.511048 | 0.2745 |
| PS intrinsic | train | 0.2605 | 0.8811 | 1.212955 | 1.674283 | 0.0946 |
| PS intrinsic | test | 0.2600 | 0.8614 | 1.146482 | 1.421571 | 0.1045 |
| CAT transition | train | 0.5432 | 0.8939 | 0.036717 | 0.054292 | 0.2592 |
| CAT transition | test | 0.4814 | 0.9057 | 0.034542 | 0.049915 | 0.2717 |
| PS transition | train | 0.5081 | 0.5772 | 0.254690 | 0.329111 | 0.2607 |
| PS transition | test | 0.5043 | 0.5912 | 0.257844 | 0.346748 | 0.1913 |

Signed angular fidelity in degrees; fractions use eligible direction rows:

| Target | Split | Mean angle | Median angle | 90th percentile | <5° | <10° | <20° |
|---|---|---|---|---|---|---|---|
| CAT intrinsic | train | 41.23 | 29.56 | 98.77 | 16.9% | 26.1% | 39.2% |
| CAT intrinsic | test | 56.24 | 48.62 | 127.61 | 14.0% | 27.0% | 34.0% |
| PS intrinsic | train | 11.06 | 9.67 | 20.47 | 20.8% | 52.3% | 89.2% |
| PS intrinsic | test | 10.33 | 8.66 | 18.50 | 20.0% | 58.0% | 94.0% |
| CAT transition | train | 38.38 | 24.34 | 96.73 | 6.9% | 21.4% | 43.6% |
| CAT transition | test | 38.78 | 27.63 | 84.74 | 3.0% | 14.0% | 36.0% |
| PS transition | train | 23.15 | 14.61 | 52.41 | 13.7% | 35.0% | 63.0% |
| PS transition | test | 24.47 | 15.48 | 52.72 | 9.0% | 36.0% | 58.0% |

At 1e-2, CAT transition loses 51 training and eight test angular comparisons;
its medians change from 24.34°/27.63° to 22.73°/26.19°. PS transition loses one
test comparison; other groups are unchanged. Thus weak vectors affect some tails,
but removing these few test directions does not remove the PS transition deficit.
Test PS transition magnitude R² is **−0.1890** despite positive r=0.5912: its norm
predictions have greater squared error than a constant calculated-mean benchmark.
The test mean norm bias is −0.18635 in source units, consistent with attenuation.
The complete 24 threshold-specific summaries are in
[ml_vector_metrics.csv](../../data/derived/ml_vector_metrics.csv).

Magnitude and angular statistics are descriptive of the released Cartesian frame
and sign convention. Transition-state phase choices are not recoverable; the primary
angles preserve source signs. A secondary phase-insensitive angle, where reported,
does not replace those source vectors or modify coupling reconstruction.

## 6. Residual analysis

**COMPUTED FROM RELEASED DATA:** Test-component errors and magnitude-stratified
absolute error ratios are:

| Target | Bias (x, y, z) | RMSE (x, y, z) | Q4/Q1 vector-error RMS |
|---|---|---|---|
| CAT intrinsic | +0.335855, -0.337619, +0.259817 | 2.242831, 2.611431, 1.516327 | 2.084 |
| PS intrinsic | +0.151168, -0.039956, -0.097312 | 1.847303, 1.297991, 1.339264 | 1.513 |
| CAT transition | -0.001341, +0.005669, +0.017845 | 0.040654, 0.056433, 0.041153 | 3.456 |
| PS transition | +0.059537, +0.042442, -0.079570 | 0.355369, 0.153717, 0.287702 | 1.330 |

The empirical 3×3 residual covariance matrices (sample divisor n−1) and full
correlations for all eight target/split groups are in
[phase2_ml_vectors.json](../outputs/phase2_ml_vectors.json). PS transition shows
substantial x/y residual correlation: 0.6441 train and 0.6563 test. CAT intrinsic
x/y correlations are −0.3550 and −0.2499. These errors are not independent by axis.

Larger-norm quartiles have higher absolute error RMS in these test blocks, especially
CAT transition (3.456×). Relative error need not increase with magnitude: for CAT
intrinsic, test median angle is 69.13° in the lowest-norm
quartile and 5.04° in the highest. Large vectors can
dominate pooled correlation while weak vectors retain poor direction fidelity.

Residual covariance and cross-component correlations are empirical summaries, not
independent error-component assumptions. Magnitude-stratified summaries use a bounded
set of quantile bins; they are descriptive heteroscedasticity diagnostics, not fitted
variance models or hypothesis tests. A few largest-error row locators identify
auditable failures without publishing their original dipole vectors. Full residual
arrays are not tracked.

## 7. Coupling reconstruction

**STRONG INFERENCE FROM PHASE 1:** In released component labels, the fixed tensor is
`T = diag(-2,+1,+1)` with `s = 5.034063649307054`. Phase 2 reads this frozen value
from [the Phase-1 summary](../outputs/phase1_coupling.json); it does not refit it.
The near-10 Å interpretation under Debye/cm⁻¹ and vacuum screening remains conditional
and nonunique. Physical API constants are not calibrated to the source scalar.

**COMPUTED FROM RELEASED DATA:** All-1,000 comparisons against Fig. 9:

| Channel | R² | RMSE | MAE | Maximum absolute residual |
|---|---|---|---|---|
| J calculated | 0.999999999999602 | 0.000342697861516 | 0.000266792956952 | 0.00211157864487 |
| J predicted | 0.999999991169988 | 0.0435288529357 | 0.00687981272305 | 0.666477879087 |
| J* calculated | 0.999999145488319 | 0.000687582343526 | 0.000252412994321 | 0.00976290553745 |
| J* predicted | 0.999999247022084 | 0.000463991356988 | 0.000196701158902 | 0.00583799812371 |

The following algebra is exact for couplings calculated from the released dipoles.
The released Fig. 9 columns differ slightly by residuals compatible with the
Phase-1 precision bounds. Closure to machine precision is not claimed against
those rounded source columns themselves.

## 8. Exact ML-error propagation into J

**COMPUTED FROM RELEASED DATA:** Expand the bilinear form, with `C_hat=C+dC` and
`P_hat=P+dP`:

```text
Delta J = s*((C+dC)^T*T*(P+dP) - C^T*T*P)
        = s*dC^T*T*P + s*C^T*T*dP + s*dC^T*T*dP
        = CAT term   + PS term    + cross term.
```

For each axis k, the contributions are `s*w_k*dC_k*P_k`,
`s*w_k*C_k*dP_k` and `s*w_k*dC_k*dP_k`. Summing the axes and terms is exact.
The first-order approximation omits the cross term. Components may reinforce or
cancel, so RMS terms cannot be treated as independent fractions of total variance.

**COMPUTED FROM RELEASED DATA:** All-1,000-row term summaries; raw entries
retain this family's numerical coupling units. The last column normalizes
by the population SD of calculated coupling reconstructed from dipoles.

| Term | Mean absolute | RMS | Bias | RMS / calculated SD |
|---|---|---|---|---|
| cat | 116.342982 | 179.119317 | 7.49840428 | 0.329870 |
| ps | 68.6347766 | 144.818777 | 2.01134984 | 0.266702 |
| cross | 25.3638557 | 52.5574099 | -0.945588405 | 0.096791 |
| first | 151.24046 | 241.033066 | 9.50975412 | 0.443892 |
| total | 145.671271 | 224.14469 | 8.56416572 | 0.412790 |

Exact expansion closure has maximum absolute error 1.023e-12,
with zero rows outside the stated floating-point bound. The discrepancy between
released Fig. 9 prediction error and reconstructed prediction error has RMSE
0.0435002624; it is a separate source-rounding comparison.

The largest absolute **net** first-order Cartesian contributor is x/y/z in
67.3%/25.8%/6.9% of rows. The alternate
sum-of-absolute-CAT-and-PS definition is recorded separately. Every term's x/y/z
mean absolute contribution, RMS and bias is in
[ml_error_propagation.csv](../../data/derived/ml_error_propagation.csv), including
first-900 and final-100 blocks. No isolated direction is treated as an independent cause.

First-order-versus-exact-error R² is 0.944939, MAE 25.3638557
and RMSE 52.5574099. Cross RMS is 23.448%
of total-error RMS. Yet adding the cross term changes total MSE from
58096.9388 to 50240.842:
the positive cross second moment 2762.28134 is outweighed
by the signed first×cross contribution -10618.3782.
Second order therefore reduces, rather than increases, the MSE for this released block.

## 9. Exact ML-error propagation into J*

The same expansion is evaluated independently for the transition vectors. No
intrinsic/transition geometry correspondence is assumed beyond each supported
within-family coupling join.

**COMPUTED FROM RELEASED DATA:** All-1,000-row term summaries; raw entries
retain this family's numerical coupling units. The last column normalizes
by the population SD of calculated coupling reconstructed from dipoles.

| Term | Mean absolute | RMS | Bias | RMS / calculated SD |
|---|---|---|---|---|
| cat | 0.224830455 | 0.379238561 | 0.015730597 | 0.509887 |
| ps | 0.206944556 | 0.364645417 | -0.00754532122 | 0.490267 |
| cross | 0.0951907019 | 0.178187766 | -0.00788827294 | 0.239574 |
| first | 0.361074194 | 0.596373767 | 0.00818527577 | 0.801826 |
| total | 0.311722531 | 0.4945106 | 0.000297002833 | 0.664871 |

Exact expansion closure has maximum absolute error 1.332e-15,
with zero rows outside the stated floating-point bound. The discrepancy between
released Fig. 9 prediction error and reconstructed prediction error has RMSE
0.000854346317; it is a separate source-rounding comparison.

The largest absolute **net** first-order Cartesian contributor is x/y/z in
65.1%/12.2%/22.7% of rows. The alternate
sum-of-absolute-CAT-and-PS definition is recorded separately. Every term's x/y/z
mean absolute contribution, RMS and bias is in
[ml_error_propagation.csv](../../data/derived/ml_error_propagation.csv), including
first-900 and final-100 blocks. No isolated direction is treated as an independent cause.

First-order-versus-exact-error R² is 0.870161, MAE 0.0951907019
and RMSE 0.178187766. Cross RMS is 36.033%
of total-error RMS. Yet adding the cross term changes total MSE from
0.35566167 to 0.244540733:
the positive cross second moment 0.0317508798 is outweighed
by the signed first×cross contribution -0.142871816.
Second order therefore reduces, rather than increases, the MSE for this released block.

For terms a, b and c, the exact mean-squared error is
`E[(a+b+c)^2] = E[a^2]+E[b^2]+E[c^2]+2E[ab]+2E[ac]+2E[bc]`.
The output records second moments and covariance/bias contributions. Signed cross
terms may reduce total error; percentages based on isolated positive diagonal terms
would be misleading. First-order R² uses the exact coupling error as its response,
not the original calculated coupling.

## 10. Why J* prediction is worse

**COMPUTED FROM RELEASED DATA:** A common dimensionless comparison avoids
confusing the very different J and J* numerical scales:

| Diagnostic, all 1,000 rows | J | J* |
|---|---|---|
| CAT-error RMS / calculated SD | 0.329870 | 0.509887 |
| PS-error RMS / calculated SD | 0.266702 | 0.490267 |
| Cross RMS / calculated SD | 0.096791 | 0.239574 |
| Total-error RMS / calculated SD | 0.412790 | 0.664871 |
| Magnitude-channel RMS / calculated SD | 0.250897 | 0.433583 |
| Direction-channel RMS / calculated SD | 0.323898 | 0.486381 |
| 2 E[CAT×PS] / calculated variance | 0.017096 | 0.142579 |
| x coefficient MSE amplification (-2 versus -1) | 2.349403 | 2.570645 |

The symmetric magnitude/direction diagnostic uses `v=m*u` and the exact identity
`dv = (m_hat-m)*(u_hat+u)/2 + (m_hat+m)*(u_hat-u)/2`. Insert these radial and
directional increments into
`Delta J = s*[dC^T*T*(P_hat+P)/2 + (C_hat+C)^T*T*dP/2]`.
This shares the original cross term equally between CAT and PS and closes exactly.
All 1,000 rows are eligible at its 1e-12 existence guard; this is distinct from
the conservative angular-reporting threshold. Both magnitude and direction channel
RMS/SD increase for J*. Their covariance is retained, so they are not additive
independent percentages.

The x coefficient doubles every x contribution relative to a signed −1 control.
Changing −2 to −1 in **both** calculated and predicted arithmetic reduces total
error MSE by factors 2.3494 (J) and 2.5706 (J*). This quantifies amplification within
these arrays, without suggesting a physically valid alternative tensor or a fitted
accuracy improvement. Partner-vector magnitudes/orientations and cross-axis covariance
also matter; the coefficient alone is not a universal explanation.

The numerical loss combines larger relative dipole errors on both species,
particularly poor PS transition magnitude fidelity, and larger coupling-weighted
directional errors. Positive CAT–PS first-order reinforcement is stronger relative
to J* variance. CAT transition's better median angle does not contradict this:
coupling weights each directional error by its partner vector and tensor. Sign-flip
frequency is almost unchanged, while second-order cancellation partly mitigates
the larger first-order error. None of these diagnostics identifies a physical cause
or assigns unique causal shares to correlated prediction errors.

These are algebraic associations and counterfactual decompositions within fixed
released arrays. They do not identify why a neural network made an error, establish
electronic-state physics, or prove performance on unseen chemical systems. Raw
transition errors are smaller in absolute source units; that alone does not mean
better prediction. The relevant degradation concerns errors relative to signal,
orientation and the bilinear combination.

## 11. Sign and ranking fidelity

**COMPUTED FROM RELEASED DATA:** Source Fig. 9 comparisons over all 1,000 rows:

| Metric | J | J* |
|---|---|---|
| Pearson r | 0.912925953 | 0.747549173 |
| Predictive R² | 0.829605104 | 0.558007372 |
| RMSE | 224.144248 | 0.494507892 |
| MAE | 145.672023 | 0.311711337 |
| Bias | 8.56696908 | 0.000292192257 |
| Signed Spearman rho | 0.77778271 | 0.692212727 |
| Signed Kendall tau-b | 0.612444444 | 0.529767476 |
| Magnitude Spearman rho | 0.6643354 | 0.673865326 |
| Magnitude Kendall tau-b | 0.48806006 | 0.484735946 |
| Sign agreement | 747/1000 (74.7%) | 743/1000 (74.3%) |
| Sign flips | 253 | 257 |

Overlap counts, with the selected-row denominator k:

| Ranking | k | J overlap | J* overlap |
|---|---|---|---|
| signed top | 10 | 8/10 | 4/10 |
| signed top | 25 | 19/25 | 14/25 |
| signed top | 50 | 42/50 | 27/50 |
| signed top | 100 | 80/100 | 65/100 |
| absolute top | 10 | 8/10 | 4/10 |
| absolute top | 25 | 16/25 | 11/25 |
| absolute top | 50 | 35/50 | 27/50 |
| absolute top | 100 | 78/100 | 53/100 |
| signed bottom | 10 | 6/10 | 4/10 |
| signed bottom | 25 | 17/25 | 11/25 |
| signed bottom | 50 | 38/50 | 24/50 |
| signed bottom | 100 | 74/100 | 52/100 |

Neither source channel contains exact zeros. The functions nevertheless distinguish
zero/nonzero mismatches from strict nonzero sign flips. Spearman uses average ranks;
Kendall uses tau-b with joint/marginal ties. Top-k uses stable original-row ordering
at exact ties and reports cutoff multiplicities. No significance or independence
claim accompanies these statistics.

J* signed ranking and top-tail overlap are worse, but magnitude Spearman is slightly
higher (0.6739 versus 0.6643). “All ranking measures worsen” would therefore be false.
The full six numerical-block summaries are in
[coupling_rank_metrics.csv](../../data/derived/coupling_rank_metrics.csv).

Rank correlations and top-k overlaps use the 1,000 validation rows, not 180 identified
photocatalytic systems. Signed ranking and absolute-value ranking answer different
questions and are reported separately. Tie handling, exact-zero sign handling and
top-k denominators are recorded with the analytical output. Row ordering supplies
only deterministic tie resolution, not an additional scientific criterion.
For the final-100 diagnostic block, k=100 selects the entire block, so perfect
overlap is a tautology and carries no ranking-performance evidence.

## 12. Screening reconstruction and threshold ambiguity

**COMPUTED FROM RELEASED DATA:** Exactly 34 positive J/J* points are supplied.
The strict `J>50 AND J*>0.01` probe selects seven. The bounded grid below reports
counts only; † marks the same seven-point membership as that probe.

| J threshold \ J* threshold | 0.002 | 0.003 | 0.005 | 0.01 | 0.015 | 0.02 | 0.03 |
|---|---|---|---|---|---|---|---|
| 20 | 20 | 19 | 15 | 11 | 9 | 6 | 3 |
| 30 | 13 | 12 | 10 | 8 | 7 | 6 | 3 |
| 40 | 10 | 9 | 8 | 7† | 6 | 5 | 3 |
| 50 | 9 | 8 | 7† | 7† | 6 | 5 | 3 |
| 60 | 8 | 7 | 6 | 6 | 5 | 4 | 2 |
| 70 | 8 | 7 | 6 | 6 | 5 | 4 | 2 |
| 80 | 6 | 5 | 5 | 5 | 4 | 3 | 1 |

Six of 49 cells select seven points; only three preserve the probe's seven members.
Nine cells select six and five cells select eight. Seven-count matches at
(30,0.015), (60,0.003) and (70,0.003) have different memberships. The grid is a
sampled neighborhood, not an exhaustive map of every continuous threshold region.
The probe was not optimized against experimental measurements.

The exact same-set **conditional** intervals reproduce Phase 0:
`J_threshold in [32.06871,50.81013)` with J*=0.01 held fixed;
`J*_threshold in [0.00342,0.0137)` with J=50 held fixed.
Lower endpoints are inclusive and upper endpoints exclusive under strict `>`.
These one-axis intervals must not be multiplied into an assumed joint rectangle.
Thus 50/0.01 is not uniquely identified. The 49-row
[sensitivity table](../../data/derived/screening_sensitivity.csv) also records
overlap, added/removed counts and Jaccard similarity without exposing source scores.

**STRONG INFERENCE:** The unique star can be mapped to CAT1/PS1 using the published
figure/text anchor. The six other selected numerical-point identities remain
unresolved; the seven selected chemical identities are known only as a set. No
missing 146 scores are invented. A count match alone cannot establish a particular
threshold, a pair-level aggregation rule or the complete author screening classifier.

## 13. Experimental-validation reproduction

**DIRECTLY OBSERVED / COMPUTED FROM RELEASED DATA:** A fresh read of SI Table 3
and Fig. 1e gives 44 listed identities, of which 43 are measured: six filtered and
37 ruled-out. All 43 measured TON/selectivity pairs agree across the two sources.
The selected identity set is CAT1/PS1, CAT37/PS41, CAT49/PS1, CAT49/PS18,
CAT49/PS33, CAT50/PS41 and CAT61/PS4. CAT50/PS41 is the unmeasured selected system;
CAT61/PS33 is the exceptional ruled-out success under the published classification.

Declared measured-set arithmetic is **precision=6/6=100%** and
**recall=6/7=85.7142857%**. The existing conditional joint-good probe gives
TP/FP/FN/TN=6/0/1/36. Its same-classification intervals remain nonunique:
TON threshold `[1155,1404)` at selectivity threshold 72%, and selectivity threshold
`[70.4,73.2)` at TON threshold 1370, each conditional on the other fixed value.

The unsynthesized CAT50/PS41 system has no measured outcome. It therefore does not
belong in measured precision's denominator and is not automatically a false positive.
Dividing measured successes by all seven initial predictions would ask a different
question. The reported recall is restricted to the tested set, not the 180 or 3,444
candidate universe. The joint TON>1370/selectivity>72% probe remains conditional;
it is not silently adopted as a unique author-defined numerical outcome classifier.

## 14. Architecture-level reimplementation

**DIRECTLY OBSERVED:** The article's ML protocol (PDF p. 8) discloses two hidden
ReLU layers, candidate widths 256/512/1024, L1 regularization, three Cartesian
outputs, Adam and learning rate 1e-4, with TensorFlow/Keras named as the original
framework. Input dimension, selected widths, model count, regularization coefficient
and scope, output activation, loss, batch size, epochs, early stopping, preprocessing,
seed and complete optimizer options are not established.

**REIMPLEMENTATION CHOICE:** [ml_architecture.py](../../src/hu2025_repro/ml_architecture.py)
represents the disclosed family without a framework, weights or training operation.
Unresolved fields remain explicit; caller-selected values are independent settings.
It does not import the optional full-computation contract's chosen defaults as author
facts. Synthetic specification/shape validation is not training or model validation.

## 15. Claim-by-claim reproducibility

See [ML_CLAIM_SCORECARD.md](ML_CLAIM_SCORECARD.md) and the
[scope definition](../../docs/ZERO_COMPUTE_ML_REPRODUCTION.md).

- **Exactly reproducible source-data arithmetic:** released scalar/vector metrics,
  numerical split membership, error decomposition, validation-row ranks, descriptor
  screening and declared experimental precision/recall.
- **Algorithmically reimplemented:** the disclosed architecture family and analytic
  coupling/error functions, validated on synthetic inputs.
- **Partially reproducible:** fixed-tensor agreement to source precision, the 34-point
  screening map, conditional thresholds and selected-score identity mapping.
- **Not reproducible from the release:** original X/preprocessing/training/weights,
  full trajectories, physical label regeneration, all 180 scores and aggregation.

The article qualifies trained-model transfer to similar geometries (PDF p. 7).
Released evaluation arrays do not test that transfer. The described 180,000-conformation
workflow and plotted predictions also do not independently establish wall-clock
savings: neither the executable original model nor a matching timing baseline is supplied.

## 16. Remaining irreducible unknowns

The preceding work does not recover geometry/snapshot IDs, atom-selection schema,
frames/origins, state/root/phase conventions, original preprocessing and model
settings, weights, complete coupling units/distance processing, the 180-system score
table or trajectory aggregation. Published sample-accounting, adsorption-sign and
selected-marker/condition-study inconsistencies remain documented. None is silently
resolved by evaluating the released predictions more precisely.

All **28 synthetic tests passed**. The three lightweight analyses reran successfully;
all 231 CSV summary rows agree with their JSON counterparts, including the rank-overlap
columns. Six coupling blocks passed exact term, magnitude/direction, covariance/bias,
second-order and x-weight consistency checks. Independent review checked numerical
definitions, table values and interpretation. The machine-readable
[validation snapshot](../outputs/phase2_validation.json) records these checks.

All 6,901 original files (85,541,434 bytes) retained their path set, hashes, sizes
and mtimes. Source-exclusion/privacy checks covered the existing three-commit history
and proposed files; no sensitive or forbidden source content was found. The same
unchanged guard is used for the final index and new local commit. No source policy
was relaxed, dependencies installed, MD/QM/TDDFT jobs launched, labels/trajectories
generated, model trained or optimizer stepped. This phase makes a local commit only;
no push or public-history rewrite is authorized or performed.

## 17. Whether further scientific compute is necessary for the stated goal

**COMPUTED FROM RELEASED DATA / scope conclusion:** For reproducing and understanding the released ML
evaluation, disclosed architecture family and numerical dipole-to-coupling methodology,
there is **no scientific need to run new MD, DFT or TDDFT**. Those calculations cannot
add evidence about arithmetic already determined by the released arrays. Model training
is likewise unnecessary for this evaluation-reproduction scope.

This conclusion is bounded. Reproducing the original trained mapping from geometry,
testing chemical transfer, independently validating quantum labels or regenerating
the complete screening workflow are different goals. They require missing author
artifacts and/or a separately defined new computational study; new calculations alone
would not recover undisclosed author settings. The preserved
[OPTIONAL FULL COMPUTATIONAL REPRODUCTION plan](../../docs/COMPUTE_PLAN.md) supports
such an extension without making it a current requirement.

The smallest useful next task stays within this scope: independently review the
claim–evidence links, numerical definitions and remaining-data request. An author
data-request draft could target X/split/weights and aggregation/score mapping;
drafting or reviewing it does not require scientific jobs or authorization to send it.
