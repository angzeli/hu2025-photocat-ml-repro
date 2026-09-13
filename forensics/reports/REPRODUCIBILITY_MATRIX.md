# Phase-0/1 reproducibility matrix

Scope: supplied local evidence under `orginal/`, checked 2026-09-13. `EXACT` means
recoverable as released, not independently regenerated from physics or training.
`INFERABLE` requires a stated inference; `PARTIAL` has material missing components;
`ABSENT` means not found in the audited files; `UNKNOWN` means the files cannot
decide the original convention. None of these labels confers scientific approval.

Source shorthand: **M** = article PDF; **S** = SI PDF; **D** = MOESM2 workbook;
**F** = MOESM11 workbook. PDF pages are one-based; S printed pages are PDF page−1.
All refer to filenames in [the manifest](../../data/manifests/original-files.csv).
Detailed evidence: [main report](PHASE0_DATA_FORENSICS.md),
[workbook audit](WORKBOOK_ML_AUDIT.md), [methods audit](PAPER_METHODS_AUDIT.md),
[structure audit](STRUCTURE_INVENTORY.md),
[Phase-1 coupling reconstruction](PHASE1_COUPLING_RECONSTRUCTION.md).

| Pipeline object | Needed for reproduction | Released? | Exact source | Recoverability | Confidence | Notes |
|---|---|---|---|---|---|---|
| 84 catalyst descriptor values | First screen | Yes | D Fig.1 A2:A85; S Table1 PDF73–75 | EXACT | High | Full values local-only; explicit IDs corroborated at SI rounding |
| 41 PS lifetime values | First screen | Yes | D Fig.2 A2:A42; S Table2 PDF76 | EXACT | High | Full values local-only; units ns |
| 18 retained CAT IDs | Candidate identity set | By thresholding | D Fig.1; S Fig.1 PDF9 | EXACT | High | Strict Ead<−0.20 eV; IDs in derived CSV |
| 10 retained PS IDs | Candidate identity set | By thresholding | D Fig.2; S Fig.2 PDF10 | EXACT | High | Strict lifetime>90 ns |
| 180 candidate identities | Pair universe | By Cartesian product | Prior two rows | EXACT | High | No new physical calculation |
| MD initial structures | Start geometry | Yes | MD_configurations/*_initial.txt | EXACT | High within local files | 3,444 whole-system endpoints; publisher ZIP association inferred |
| MD final structures | End geometry | Yes | MD_configurations/*_final.txt | EXACT | High within local files | 3,444 endpoints; no time/cell metadata in files |
| All 180k sampled snapshots | Exact per-pair screening | No | Full coordinate and package content audit | ABSENT | High for audited files | Endpoint blocks do not reconstruct trajectories |
| 1,000 CAT ML geometries | Exact X and recalculated labels | Not identifiable | D Figs.5/7 have numeric outputs only | ABSENT | High for identifiable dataset | Some endpoint might coincide, but no provenance link establishes this |
| 1,000 PS ML geometries | Exact X and recalculated labels | Not identifiable | D Figs.6/8 have numeric outputs only | ABSENT | High for identifiable dataset | Separate sampling stated; no geometry/sample join |
| DFT intrinsic dipole labels | Target Y | Yes, plotted values | D Figs.5/6 train A/F/K, test C/H/M | EXACT | High for arrays | 1,000×3 per species; geometry/unit linkage missing |
| DFT transition dipole labels | Target Y* | Yes, plotted values | D Figs.7/8 same layout | EXACT | High for arrays | 1,000×3 per species; root/state details incomplete |
| ML dipole predictions | Prediction-statistic reproduction | Yes | D Figs.5–8 train B/G/L, test D/I/N | EXACT | High for arrays | Predictions available without model weights |
| Train/test split | Refit exact author model | Plotted membership only | D Figs.5–8 rows4:903/4:103 | PARTIAL | High | Exactly900/100; no original sample-index file or seed |
| Numerical row alignment | Recombine released dipoles | Algebraic evidence | D Figs.5–9; ml_analysis.json | INFERABLE | Strong blockwise | Intrinsic pair→J and transition pair→J* strongly supported; common physical geometry only plausible |
| Calculated coupling | Validate recombination | Yes | D Fig.9 A3:A1002,D3:D1002 | EXACT | High for arrays | 1,000 values per coupling, signed, units unknown |
| Predicted coupling | Validate recombination | Yes | D Fig.9 B3:B1002,E3:E1002 | EXACT | High for arrays | 1,000 per coupling; correlations independently recomputed |
| Final pair-level J/J* values | Reproduce all 180 screening scores | Partially | F Fig.1d A2:B35 | PARTIAL | High for 34 points | Only34 numeric pairs; identities largely missing |
| Fig.1d candidate IDs | Score-to-identity ranking | Selected set only | S Table3 PDF77–78; M Fig.1 PDF2 | PARTIAL | Mixed | Seven identities exact as a set; one row mapping high-confidence; six unresolved |
| Screening thresholds | Selection rule | First stage explicit; coupling unclear | S Figs.1/2; F Fig.1d | PARTIAL | High/conditional | 50 and 0.01 yield7 points but are not uniquely identifiable settings |
| Experimental validation table | Outcome audit | Yes | F Fig.1e A2:D44; S Table3 PDF77–78 | EXACT | High | Six filtered+37 ruled-out; one additional unsynthesized selected identity |
| Numerical definition of experimentally good | Independent precision/recall | Not unique | M PDF3; F Fig.1e; S Table3 | UNKNOWN | High uncertainty | Joint1370/72 rule is compatible, not uniquely recovered |
| Aggregation rule | Conformation→pair score | Described only as statistical average | M PDF8 and ED Fig.3 PDF14 | UNKNOWN | High uncertainty | Signed mean, mean magnitude, absolute signed mean, RMS unranked |
| Released coupling tensor and scalar | Recombine validation arrays | Numerically reconstructable | D Figs.5–9; phase1_coupling.json | INFERABLE | Overwhelming numerical support | First900 calculated intrinsic fit gives s=5.034063649307054; x tensor held fixed across all four channels; rounding-compatible, not bitwise identity |
| Separation axis in released component labels | Interpret tensor | Not explicitly documented | Phase-1 x/y/z and 48 sign/permutation probes | INFERABLE | Strong | x overwhelmingly favored; ±x, common transverse rotations and equivalent axis relabellings unidentifiable |
| Likely dipole/coupling units | Physically meaningful errors and scores | Not explicitly located | M equations3/4; D/F labels; independent constants | INFERABLE | Conditional | Debye/cm−1 with near10Å is a natural hypothesis; Debye/meV near5Å and atomic-unit alternatives also plausible; exact author units remain UNKNOWN |
| Effective fixed separation in validation transform | Interpret common scalar | Numerically conditional | Phase-1 physical/rounding analysis | INFERABLE | Strong under stated units | Debye/cm−1 and vacuum give10.00003503953813Å; exactly10Å with modern constants falls outside conditional5dp bounds |
| Actual MD separation/standardization | Connect trajectories to tensor | No per-row geometry link | Released endpoints and validation arrays | UNKNOWN | High uncertainty | Fixed-axis tensor does not distinguish fixed geometry, standardized frame/distance or an equivalent convention |
| Exact model architecture | Exact retraining | Partial description | M ML protocol PDF8 | PARTIAL | High for disclosures | Two hidden ReLU layers and 3-output description; model count/input dimension ambiguous |
| Exact selected width | Exact retraining | No | M PDF8 gives256/512/1024 choices | ABSENT | High for audited files | Chosen layers/model widths and criterion missing |
| Training hyperparameters | Exact retraining | Partial | M PDF8 | PARTIAL | High | Adam lr1e−4 and L1 named; loss/coefficient/batch/epochs/seed missing |
| Exact atom-selection schema | Reconstruct X | General concept only | M PDF8 | PARTIAL | High | Metal and surrounding atoms; no indices/radius/order/padding |
| Preprocessing | Reconstruct X | No exact convention | M/D and coordinates | ABSENT | High for audited files | No centering/rotation/normalization/unit schema; do not assume none |
| Model weights/checkpoints/code | Run author model | No | Entire supplied file/content inventory | ABSENT | High for audited files | No Python/notebook/feature/model files or workbook embeddings |
| CAT1 crystal CIF | Supplemental structural evidence | Publisher-listed, locally missing | Publisher MOESM10 | ABSENT | Exact local absence | Published availability is distinct from local inventory |

The recoverable fractions have meaningful denominators for individual objects:
125/125 first-stage descriptors, 180/180 reconstructed candidate identities,
all released dipole/coupling validation arrays, and 43/43 measured validation rows.
Only34 plotted pair-score rows are supplied against180 retained systems; treating
that as coverage assumes distinct system-level points, whose IDs are unavailable.
There is no defensible single percentage for end-to-end reproduction: the missing
X/trajectory/aggregation contracts prevent exact retraining and full screening.
