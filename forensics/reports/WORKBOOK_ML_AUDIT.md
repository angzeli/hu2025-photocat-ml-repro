# Workbook and ML source-data audit

All workbooks were read without saving or modifying the source. The OOXML pass parsed every XML/relationship part and checked ZIP CRC integrity. The full metadata output is `forensics/outputs/workbook_audit.json`.

## Workbook coverage

| Workbook package | Sheets | Nonempty cells | Formula cells |
| --- | ---: | ---: | ---: |
| 41929_2025_1291_MOESM11_ESM.xlsx | 2 | 246 | 0 |
| 41929_2025_1291_MOESM12_ESM.xlsx | 3 | 200 | 0 |
| 41929_2025_1291_MOESM13_ESM.xlsx | 6 | 5818 | 0 |
| 41929_2025_1291_MOESM14_ESM.xlsx | 1 | 62847 | 0 |
| 41929_2025_1291_MOESM2_ESM.xlsx | 53 | 1046179 | 0 |

All 65 sheets are visible. No hidden rows/columns, defined names, comments, external relationships, chart objects/caches, embedded data, drawings, macros, or formulas were found. There are ordinary merged headings and formatting. The source arrays are stored numeric values; there are no missing formula caches to recover. All packages pass CRC and XML parsing.

Fig.1d illustrates a formatting trap: stored OOXML dimension A1:B172 and parsed cell extent A1:B141, but only 70 nonempty cells (two headings and 34 numerical pairs). The audit records stored dimension, parsed extent and actual nonempty bounds separately. Metadata does not supply missing candidate IDs or extra screening points.

**Local-copy provenance caveat:** MOESM11 and MOESM2 have `lastModifiedBy=Li, Angze`, Macintosh Excel application metadata, and recorded modification times 2026-09-13T11:03:52Z and 2026-09-13T11:04:07Z. These are observations about files supplied before this audit, not changes made by the audit. Their current hashes identify the supplied local copies; metadata alone cannot prove byte identity with the publisher download. Metadata contains no useful hidden sample mapping.

## Dipole arrays and independently computed metrics

SI PDF pp13–16 establishes Fig.5 catalyst intrinsic, Fig.6 photosensitizer intrinsic, Fig.7 catalyst transition and Fig.8 photosensitizer transition. Panels a/b/c are Cartesian x/y/z. Plot horizontal values are calculated and vertical values are predicted; workbook column labels `x` and `y` denote plot axes, not the Cartesian target. No dipole unit is given in these axes/captions or worksheet labels.

Every figure contains exactly 900 training and 100 test samples for every component, with no missing/nonfinite numerical values. Training ranges are A4:B903, F4:G903, K4:L903; test ranges are C4:D103, H4:I103, M4:N103. Source order is preserved. All underlying values are recoverable, but sample geometries and IDs are not encoded in these blocks.

The table below pools x/y/z (2700 train or 300 test scalar values); these are 900/100 conformations per target, not 2700/300 independent conformations. `data/derived/ml_metrics.csv` also reports each component separately. R² is predictive coefficient of determination, not Pearson r squared.

| Target | Split | Samples | Pearson r | R² | MAE | RMSE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| catalyst_intrinsic | train | 900 | 0.945356 | 0.892176 | 1.427174 | 2.337915 |
| catalyst_intrinsic | test | 100 | 0.964168 | 0.928739 | 1.595103 | 2.171721 |
| photosensitizer_intrinsic | train | 900 | 0.965032 | 0.931199 | 1.158132 | 1.606455 |
| photosensitizer_intrinsic | test | 100 | 0.965538 | 0.931915 | 1.140544 | 1.515579 |
| catalyst_transition | train | 900 | 0.844695 | 0.704106 | 0.032910 | 0.055673 |
| catalyst_transition | test | 100 | 0.879775 | 0.768187 | 0.031160 | 0.046658 |
| photosensitizer_transition | train | 900 | 0.862415 | 0.741005 | 0.191950 | 0.265942 |
| photosensitizer_transition | test | 100 | 0.864336 | 0.745103 | 0.199044 | 0.278501 |

## Coupling arrays

Supplementary Fig.9 contains 1000 paired values for each coupling: J in A3:B1002 and J* in D3:E1002. The calculated/predicted axis direction comes from SI PDF p17. Units are unspecified in the released worksheet and figure axes/caption, so reported errors retain the source numerical scale.

| Coupling | Calculated range | Predicted range | Pearson r | R² | MAE | RMSE |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| J | -2001.9466 to 4820.3512 | -1869.4985 to 4539.516 | 0.912925953 | 0.829605104 | 145.672023 | 224.144248 |
| Jstar | -3.25842 to 3.43637 | -2.57829 to 2.8211 | 0.747549173 | 0.558007372 | 0.311711337 | 0.494507892 |

The recomputed correlations round to the published 0.913 (J) and 0.748 (J*). Both couplings have both signs. Sign counts and disagreements are in `data/derived/supfig9_coupling_metrics.csv`. Signed values are preserved; no absolute-value transformation was applied.

## Numerical ordering evidence

Concatenating the 900 training rows followed by the 100 test rows reveals a strong algebraic correspondence. A single common scale in the expression below nearly reconstructs all four calculated/predicted J/J* columns:

`coupling = s × (−2 CAT_x PS_x + CAT_y PS_y + CAT_z PS_z)`

The scale is `5.03406364931`, estimated solely from the first 900 calculated intrinsic-coupling rows. It is then fixed for the remaining 100 rows, both predicted channels, and both transition channels. This is an algebraic provenance test; no neural network or predictive ML model was trained.

| Coupling channel | All-row R² | Last-100 R² | RMSE | Largest absolute residual |
| --- | ---: | ---: | ---: | ---: |
| J calculated | 0.999999999999602 | 0.999999999999688 | 0.00034269786 | 0.0021115786 |
| J predicted | 0.999999991169988 | 0.999999919269161 | 0.043528853 | 0.66647788 |
| Jstar calculated | 0.999999145488319 | 0.999998987986675 | 0.00068758234 | 0.0097629055 |
| Jstar predicted | 0.999999247022084 | 0.999999189343878 | 0.00046399136 | 0.0058379981 |

Negative controls reorder the reconstructed coupling by test-first order, a one-row cyclic shift, and 100 fixed-seed permutations. The full metrics and residual summaries are in `forensics/outputs/ml_analysis.json`. These controls distinguish specific numerical ordering from merely equal sample counts.

**Classification:** the numeric row pairing Fig.5+Fig.6→Fig.9a is **strongly supported**, and Fig.7+Fig.8→Fig.9b is **strongly supported**. The expression is consistent with a dipole tensor with fixed separation axis along x. It does not establish the original physical distance, unit conversion, dielectric factor, or coordinate convention. Residuals are nonzero; the stored values do not establish their cause.

A common physical conformation pair across all four targets remains **plausible**, not proven. The two coupling identities separately connect intrinsic and transition blocks to adjacent Fig.9 columns; they do not independently establish that those columns use the same underlying geometries. There are no molecule/snapshot IDs, structure-file joins, or original split indices in these blocks, hidden workbook structures or metadata. The missing coordinate mapping prevents recovery of input X from these tables alone.

## Reproduction and redistribution boundary

Run `forensics/scripts/inspect_workbooks.py`, then `forensics/scripts/analyze_ml.py` with Python containing numpy and openpyxl. Both read source workbooks only. The first emits metadata; the second emits computed metrics and this report. Complete numerical extracts are written exclusively under ignored `forensics/local_only/supfig5_dipoles.csv` through `supfig8_dipoles.csv` and `supfig9_couplings.csv`. These source-derived extracts must never be staged, committed, or uploaded. The tracked metrics/reports are compact analytical summaries and do not substitute for the source tables.

## Publisher-copy comparison

A separately downloaded publisher copy of each locally re-saved workbook (MOESM2 and MOESM11) was compared against the supplied local evidence. Both ZIP byte sequences differ, but **every nonempty cell agrees exactly**: numerical XML values were compared as exact decimal values, text was resolved through shared strings, and formulas/cached values were included. Sheet order/state, nonempty bounds, merged ranges, hidden rows/columns, defined names, comments, links and object counts also agree. Thus the audit found no local cell-content alteration.

Both publisher packages were separately CRC-checked and all XML parts inspected. They contain no additional hidden sample identifiers, orphan shared strings, chart caches, or embedded datasets. Custom properties record office-software build/version identifiers, not conformation IDs. Hashes and a per-sheet comparison are in `forensics/outputs/publisher_comparison.json`. Publisher downloads remain temporary local-only evidence. This comparison strengthens the workbook-specific absence findings; it does not establish absence from unreleased author materials.
