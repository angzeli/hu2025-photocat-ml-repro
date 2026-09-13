# ML claim scorecard: released-data reproduction

Evidence basis: Hu et al., *Nature Catalysis* **8**, 126–136 (2025),
[DOI](https://doi.org/10.1038/s41929-025-01291-z); article PDF pages are one-based.
Methods/SI anchors are in the [methods audit](PAPER_METHODS_AUDIT.md).
The [Phase-2 report](PHASE2_ZERO_COMPUTE_ML_REPRODUCTION.md) gives independently
computed results and numerical limitations. No new model or scientific job ran.

| Claim | Released evidence | Independently reproducible? | Result | Limitation |
|---|---|---|---|---|
| Dipole ML predictive accuracy | MOESM2 Figs. 5–8 calculated/predicted x/y/z values; SI PDF pp. 13–16 | **COMPUTED FROM RELEASED DATA:** evaluation arithmetic, yes | Per-component/pooled train/test r, predictive R², MAE, RMSE and bias; new vector-angle/magnitude/residual summaries | Prediction arrays do not provide original geometry X, training process or evidence of chemical transfer |
| Intrinsic coupling prediction | MOESM2 Fig. 9 A/B; SI PDF p. 17 | **COMPUTED FROM RELEASED DATA:** yes for released rows | Pearson r = 0.9129259525; predictive R² = 0.8296051039 | Validation-row metrics, not the complete 180-system screening ranking; unit convention remains conditional |
| Transition coupling prediction | MOESM2 Fig. 9 D/E; SI PDF p. 17 | **COMPUTED FROM RELEASED DATA:** yes for released rows | Pearson r = 0.7475491726; predictive R² = 0.5580073723 | Correlation alone conceals vector-scale, angular, nonlinear and covariance effects; see exact error decomposition |
| 900/100 split exists | Distinct train/test blocks in all four vector figures; article PDF p. 8 | **DIRECTLY OBSERVED / COMPUTED FROM RELEASED DATA:** yes for plotted membership | 900 training and 100 test vector rows per target | Geometry/split keys and temporal or identity independence remain unavailable; no additional validation set is supplied |
| Coupling construction from dipoles | Article equations 3–4, PDF pp. 7–8; aligned vector/coupling tables | **COMPUTED FROM RELEASED DATA:** numerical relation; **STRONG INFERENCE:** physical convention | Frozen s and x tensor reproduce all four coupling channels to source-precision residuals; analytical prediction-error decomposition closes numerically | Not bitwise equality to Fig. 9; exact author unit, frame, distance and aggregation pipeline remain unidentified |
| Seven screening candidates | SI Table 3; 34 unlabelled Fig. 1d points | **PARTIAL:** selected identity set and conditional point count | Seven points pass the 50/0.01 probe; threshold sensitivity establishes nonuniqueness | Six selected point-to-identity assignments and the complete 180-score table remain unavailable; no invented missing scores |
| 100% precision | Article PDF p. 3; Fig. 1e; SI Table 3 | **COMPUTED FROM RELEASED DATA:** declared measured-set arithmetic | 6/6 = 100% | CAT50/PS41 is unmeasured, so it is neither a measured success nor false positive; all-seven precision is unestablished |
| 85.7% recall | Same measured evidence; ruled-out CAT61/PS33 exception | **COMPUTED FROM RELEASED DATA:** declared measured-set arithmetic | 6/(6+1) = 85.7142857% | Applies to the tested subset and stated outcome classes; a unique numerical experimental-good classifier is not recoverable |
| Trained-model transfer is limited to similar geometries | Article discussion, PDF p. 7 | **DIRECTLY OBSERVED:** qualification in the paper; independent transfer test, no | The claimed limitation is preserved | Missing X/identity keys/weights prevent testing transferability; plotted train/test membership is not a chemical holdout study |
| ML accelerates the 180,000-conformation workflow | Article PDF pp. 3, 7–8; Extended Data Fig. 3 | **DIRECTLY OBSERVED:** described strategy; runtime benefit, no | Released predictions and downstream algebra are verifiable without new training | No original timing baseline, executable model, full 180,000 predictions or authenticated trajectory join is released; speedup cannot be independently quantified |
| A disclosed MLP architecture can be represented | Article ML protocol, PDF p. 8 | **REIMPLEMENTATION CHOICE:** a dependency-light representation of directly disclosed constraints | Two hidden ReLU layers, candidate widths 256/512/1024, L1, three outputs, Adam at 1e-4 | Selected widths, model count, input dimension, output activation and missing training/preprocessing settings remain explicit unknowns |

`PARTIAL` describes recoverability, not an additional evidence category. A directly
observed paper claim is not independently verified physics. Computed statistics
reproduce released outcomes; architecture representation does not recreate trained
weights. No overall percentage of “ML reproduced” is assigned because these objects
have different denominators and missing dependencies.
