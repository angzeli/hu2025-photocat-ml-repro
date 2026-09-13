# Article and Supplementary Information methods audit

This report separates published statements, independently checked table correspondence, and unresolved interpretation. It does not implement the neural network or simulate new structures. Original PDFs, extracted text, and rendered source figures remain local-only; no full text or source-figure copies are included in this report.

## Sources and page convention

- **Article:** `orginal/s41929-025-01291-z.pdf`, 15 PDF pages. PDF pages 1-11 correspond to printed pages 126-136; pages 12-15 contain Extended Data Figs. 1-4.
- **SI:** `orginal/41929_2025_1291_MOESM1_ESM.pdf`, 99 PDF pages. Printed SI page numbers are one less than the PDF page numbers.
- **Supplementary figure workbook:** `orginal/41929_2025_1291_MOESM2_ESM.xlsx`.
- **Main Fig. 1 workbook:** `orginal/41929_2025_1291_MOESM11_ESM.xlsx`.
- Publisher record: [Hu et al., Nature Catalysis (2025)](https://www.nature.com/articles/s41929-025-01291-z), DOI 10.1038/s41929-025-01291-z.

Page references below always identify the PDF page and, where useful, its printed number. Text extraction used `pypdf` across both PDFs. Visual inspection covered article Fig. 1, Methods, Extended Data Figs. 3-4, SI Figs. 1-9, and SI Tables 1-3. Intermediate source renderings/text were written only to temporary local storage outside Git.

## Directly disclosed pipeline

**DIRECTLY OBSERVED:** The article defines 41 Cu(I) photosensitizers and 84 macrocyclic metal-complex catalysts, yielding 3,444 combinations; adsorption energy and lifetime reduce this to 180 combinations. Its text then describes 1,000 MD conformations per retained combination, 180,000 total conformations, first-principles labels on selected conformations, prediction of intrinsic/transition dipoles, calculation of coupling, and experimental selection. [Article PDF p. 3 / printed p. 128; PDF pp. 7-8 / printed pp. 132-133.]

**DIRECTLY OBSERVED:** MD is described as canonical-ensemble classical MD with a Nosé-Hoover thermostat, 298 K, 1 fs timestep, a periodic 5 × 5 × 5 nm box, one CAT, one PS and counterions, universal forcefield parameters, and a 12.5 Å Lennard-Jones/Coulomb cutoff. Total duration is 110 ps: 10 ps equilibration and 100 ps sampled every 0.1 ps. The Methods describe randomly choosing 1,000 catalyst conformations and 1,000 photosensitizer conformations **separately**. [Article PDF p. 7 / printed p. 132.]

**UNRESOLVED:** Extended Data Fig. 3 calls the DFT-labelled subset 2,000 conformations with dipole couplings, subtracts it from 180,000 to obtain 178,000, and schematically describes ML prediction of couplings. The detailed Methods instead describe separate CAT/PS samples and dipole-vector prediction before coupling calculation. The schematic does not establish that 2,000 *paired* snapshots were labelled or that the CAT/PS training rows were paired. Treating these descriptions as one exact sample-index scheme would add an undocumented assumption. [Article PDF p. 14, Extended Data Fig. 3; compare PDF pp. 7-8.]

## Descriptor identity and threshold corroboration

**DIRECTLY OBSERVED:** SI Fig. 1 explicitly defines adsorption-energy screening as strictly below −0.20 eV; SI Fig. 2 defines lifetime screening as strictly above 90 ns. These are documented thresholds, rather than boundaries estimated from plotted marks. [SI PDF pp. 9-10 / printed pp. 8-9.]

**COMPUTED FROM RELEASED DATA:** `forensics/scripts/audit_paper_evidence.py` parses all 84 explicitly indexed catalyst values in SI Table 1 and all 41 indexed lifetimes in SI Table 2. Each matches the corresponding workbook row order at SI display precision: no catalyst deviations above 0.00005001 eV and no lifetime deviations above 0.500001 ns. Thus using workbook numeric row `i` as CAT `i` or PS `i` is corroborated by the independently indexed SI tables. This is stronger than assuming that row number itself is an identifier. [SI PDF pp. 73-76 / printed pp. 72-75; MOESM2, `Supplementary Fig. 1` and `Supplementary Fig. 2`; derived checks in `forensics/outputs/paper_table_checks.json`.]

The explicitly indexed retained set is CAT 1, 2, 3, 13, 14, 15, 25, 26, 27, 37, 38, 39, 49, 50, 51, 61, 62, 63; and PS 1, 4, 12, 17, 18, 20, 28, 33, 36, 41. The resulting Cartesian product contains 180 identities. Full-precision threshold reconstruction belongs to the prescreen outputs; the PDF provides the identity cross-check.

**SOURCE INCONSISTENCY:** Article equation (1) visibly prints `E_ad = E_complex + E_cat − E_CO2`, with a plus sign before the catalyst energy. That expression must not be silently corrected when describing the paper. Reusing released adsorption values is possible without resolving it; a fresh energy reproduction requires clarification of the intended energy reference and sign convention. [Article PDF p. 7 / printed p. 132, equation (1), visually checked.]

## Dipole labels, targets, and units

| SI figure | Meaning of panels a/b/c | Horizontal axis | Vertical axis | Unit disclosed in figure/caption? | Source |
|---|---|---|---|---|---|
| 5 | CAT intrinsic dipole x/y/z | Calculated component | Predicted component | No | SI PDF p. 13 / printed p. 12 |
| 6 | PS intrinsic dipole x/y/z | Calculated component | Predicted component | No | SI PDF p. 14 / printed p. 13 |
| 7 | CAT transition dipole x/y/z | Calculated component | Predicted component | No | SI PDF p. 15 / printed p. 14 |
| 8 | PS transition dipole x/y/z | Calculated component | Predicted component | No | SI PDF p. 16 / printed p. 15 |
| 9a | Intrinsic coupling J | Calculated J | Predicted J | No | SI PDF p. 17 / printed p. 16 |
| 9b | Transition coupling J* | Calculated J* | Predicted J* | No | SI PDF p. 17 / printed p. 16 |

**DIRECTLY OBSERVED:** All the dipole/coupling validation plots include signed values. Fig. 1d uses logarithmic positive J/J* axes without units. The detailed Methods identify PS dipoles as those of the **reduced** photosensitizer; shortened SI figure captions say photosensitizer. [Article PDF pp. 2-3, 8; SI PDF pp. 13-17.]

**UNRESOLVED:** No dipole-unit or coupling-unit specification was located in the article or SI text/captions or the visually checked axes. eV, meV, cm⁻¹, Debye, atomic units, and arbitrary units cannot be assigned simply from value magnitudes. Descriptor eV and ns labels do not transfer to J/J*. The formula has the dimensions of an interaction energy under a consistent physical unit system, but this does not reveal the numerical convention used to generate the workbook values.

Published plot annotations are reference claims only; numerical `r`, prediction `R²`, MAE, and RMSE must come from the independent workbook analysis. In particular, a label `R` in the figure is not automatically a prediction coefficient of determination.

## Coupling expression and aggregation

**DIRECTLY OBSERVED:** Article equations (3)-(4) specify the dipole approximation:

```text
J = (1 / (4π ε0)) [ (μC · μP) / r³ − 3 (μC · r)(μP · r) / r⁵ ]
J* = the same expression with both μ vectors replaced by transition dipoles μ*.
```

Here `r` is the vector connecting the **centres of mass** of the catalyst and photosensitizer, not explicitly the metal-metal vector. The prose calls ε0 the dielectric constant. It does not provide a numerical dielectric factor, unit conversion, choice of solvent screening, coordinate wrapping rule, or minimum-image implementation. [Article PDF pp. 7-8 / printed pp. 132-133.]

**DIRECTLY OBSERVED:** Methods Step 4 and Extended Data Fig. 3 prescribe a statistical average across the MD conformations. Neither identifies a signed mean, mean magnitude, magnitude of the signed mean, or RMS; neither gives explicit weighting. [Article PDF p. 8 / printed p. 133; PDF p. 14.]

| Candidate aggregation | Compatibility with documentation | What would distinguish it |
|---|---|---|
| `mean(J)` | Not excluded; the literal averaging language permits it | Signed, pair-indexed 1,000-snapshot values and reported pair value |
| `mean(abs(J))` | Not excluded; positive plotted values alone do not prove it | Same inputs, including the negative tail |
| `abs(mean(J))` | Not excluded; differs from mean magnitude when signs cancel | Same inputs and sign handling |
| `sqrt(mean(J²))` | Not excluded; statistical averaging language is insufficient | Same inputs and high-magnitude tail |

The same uncertainty applies to J*. Positive Fig. 1d points are not evidence that every conformation was made positive before averaging. Signed Fig. 9 values are not a labelled 1,000-point distribution for a particular Fig. 1d pair. Cross-figure scales cannot identify an aggregation algorithm without that correspondence. There is insufficient evidence to rank the four rules reliably or choose one as the author implementation.

## Neural-network disclosure and missing input contract

All directly disclosed NN entries below are from article PDF p. 8 / printed p. 133, `ML protocol`.

| Object | Directly disclosed | Remaining gap |
|---|---|---|
| Software | TensorFlow and Keras | Package versions and environment absent from PDF disclosure; reference publication dates are not versions |
| Topology | Input layer, two hidden layers, output layer | Complete fitted architecture and input dimension unresolved |
| Hidden widths | Candidate widths 256, 512, 1,024 | Chosen width for each layer/model and selection criterion absent |
| Activation | ReLU for each hidden layer | Output activation unspecified |
| Regularization | L1 | Coefficient and affected parameters/layers unspecified |
| Optimization | Supervised backpropagation, Adam, learning rate 0.0001 | Adam options and any learning-rate schedule unspecified |
| Split counts | 900 train / 100 test from 1,000 samples, for CAT and PS respectively | Structure identifiers, indices, sampling seed, and common split across targets unspecified |
| Input feature family | Coordinates of metal atoms and atoms around the metal | Exact atom lists, selection radius/bond rule, coordinate units, order, variable-composition encoding, padding absent |
| Vector targets | Three Cartesian components of intrinsic and transition dipoles | Exact grouping into fitted models is internally ambiguous |
| Other training settings | None additionally located in the PDFs | Loss, batch size, epochs, early stopping, initialization, seed, normalization, centering, rotation/frame handling, target scaling, validation design absent |
| Reusable implementation | No implementation supplied by these PDF descriptions | Model weights, checkpoints, train/test index files, feature arrays, scripts and notebooks require separate package evidence; the PDFs do not provide them |

**SOURCE AMBIGUITY:** The Methods say two models predict transition dipoles for CAT and PS, then describe three output neurons for directions of intrinsic dipole and transition dipole. Four plotted target families do not by themselves establish whether four separately fitted vector models, repeated use of two model templates, or another arrangement generated the results. Do not present a conventionally reasonable four-model design as a disclosed author setting.

**DIRECTLY OBSERVED:** The article specifies Gaussian 16, ωB97XD, LANL2DZ for transition metals, 6-31G(d) for other elements, and PCM treatment of water/acetonitrile in its quantum-chemistry Methods. This is useful method-level information. It does not supply the selected 2,000 geometry records, their labels/indices, detailed TDDFT root selection for every dipole, or executable calculation inputs. [Article PDF p. 7 / printed p. 132.]

| Required part of X | PDF recoverability | Reason |
|---|---|---|
| General feature concept | Directly recoverable | Metal/local-atom coordinates explicitly named |
| Exact metal-centred atom selection | Absent | No atom list or selection algorithm |
| Atom ordering | Absent | No input-vector schema |
| Units and coordinate origin/frame | Absent | No explicit input representation or transform |
| Centering/normalization/scaling | Absent | Not specified; must not assume none |
| Molecule identity universe | Directly recoverable | CAT/PS definitions and indexed descriptor tables |
| Label-row to molecule/snapshot identity | Absent | No PDF index key linking structures to ML rows |
| Train/test row identities | Absent | Counts disclosed, structure-index split not given |

Coordinate archives may establish additional geometry provenance, but a released structure with a familiar CAT/PS name is not automatically an ML feature row. Coordinate-file absence/presence conclusions belong to the recursive archive audit. Matching 1,000-row lengths is insufficient to prove alignment among Figs. 5-8 or with Fig. 9, especially given separately sampled CAT and PS conformations.

## Selected identities and experimental validation

**DIRECTLY OBSERVED:** Article PDF p. 3 / printed p. 128 reports seven selected systems, an unsynthesizable CAT-50-containing system, six validated predictions, and 37 ruled-out systems tested. SI Table 3 identifies the unsynthesized system as **CAT 50 / PS 41** and explicitly divides seven filtered rows from 37 ruled-out rows. The six measured filtered identities are CAT 1 / PS 1, CAT 37 / PS 41, CAT 49 / PS 1, CAT 61 / PS 4, CAT 49 / PS 18, and CAT 49 / PS 33. The exceptional ruled-out system is CAT 61 / PS 33. [SI PDF pp. 77-78 / printed pp. 76-77.]

**COMPUTED FROM RELEASED DATA:** Table 3 has 44 identity rows, one wholly unmeasured row, and 43 measured rows. A deterministic identity-based comparison of all 43 measured TON/selectivity pairs against MOESM11 `Fig.1e` gives zero discrepancies. The first seven measured worksheet rows must not all be labelled predicted: that block includes the ruled-out exception. [Script/output referenced above.]

**DIRECTLY OBSERVED:** Fig. 1 identifies the red star as the best system; the main text identifies that best system as CAT 1 / PS 1. This directly establishes the star's identity. Assigning a particular unlabelled Fig. 1d workbook row to it additionally requires matching the unique plotted coordinate; such a row assignment is a high-confidence cross-source inference, not a direct spreadsheet label. [Article PDF p. 2 / printed p. 127, caption; PDF p. 4 / printed p. 129.]

The six measured filtered identities and the seventh unmeasured identity are directly available as a **set**. Their assignment to every individual unlabelled J/J* point is not furnished by Table 3. A visual point order is not an identity key.

### Meaning and limitation of precision/recall

The article defines precision using experimentally successful predicted combinations and recall using experimentally successful combinations across the tested set. On its declared classification, the arithmetic is `6/6 = 100%` precision and `6/(6+1) = 85.714...%` recall. The unsynthesized seventh prediction is unvalidated, not a measured false positive; treating all seven initial predictions as the precision denominator would answer a different question. These estimates apply to the tested subset and do not establish recall across all 180 or all 3,444 candidates. [Article PDF p. 3 / printed p. 128.]

**COMPUTED FROM RELEASED DATA, CONDITIONAL ON AN INFERRED RULE:** Using the illustrative joint rule `TON_CO > 1370 AND CO selectivity > 72%` yields TP=6, FP=0, FN=1, TN=36 and reproduces that arithmetic. This rule is suggested by the discussion and optimal-region plot but is not uniquely specified as an author classifier; many nearby boundaries can yield the same labels. The report must distinguish reconstruction of the authors' outcome classes from independent validation of a prespecified numerical definition of good performance.

**SOURCE INCONSISTENCY:** The prose describes ruled-out results, aside from the exception, as below both TON 1,370 and selectivity 72%. Among the remaining 36 ruled-out rows, five have TON at least 1,370 and nine have selectivity at least 72%. They can still be outside a joint high-TON/high-selectivity region, but the literal individual-bound wording does not match the table. [Article PDF p. 3; SI Table 3; independent counts in `paper_table_checks.json`.]

**SOURCE INCONSISTENCY:** SI PDF p. 18 / printed p. 17 describes a four-system condition check using CAT 1 / PS 1, CAT 49 / PS 34, CAT 4 / PS 1, and CAT 37 / PS 17, and calls two filtered and two ruled-out. Table 3 marks only CAT 1 / PS 1 as filtered among those four. CAT 49 / PS 34 is explicitly ruled out, while CAT 49 / PS 33 is filtered; PS 34 also has a lifetime below the 90 ns prescreen. These are distinct released identities and must not be silently merged or corrected.

**SOURCE INCONSISTENCY:** Fig. 1d visually appears to contain six blue markers plus the red star, consistent with seven initial selections, while its caption describes five blue promising systems; Fig. 1e has the five blue measured predictions plus the red star. Preserve the distinction between the initial seven and measured six; do not use the caption alone to infer that the map contains only six selected coordinates. [Article PDF p. 2 / printed p. 127, visually checked.]

## Package interpretation and follow-up priority

The article's Data availability statement describes separately released optimized computational coordinates and **initial and final** MD configurations. It does not claim that full trajectories or all labelled ML geometries are released. [Article PDF p. 9 / printed p. 134.] The supplement workbook supplies plotted values, rather than an implementation package. MOESM14's worksheet is named `Extended Data Fig. 3`, whereas the actual article's Extended Data Fig. 3 is a workflow diagram and Fig. 4 is kinetic decay. The worksheet's name must not make it an ML-training-data package; the workbook-content and publisher-link audits resolve that labelling discrepancy.

The most valuable next evidence is the missing row/structure/split key and exact input-feature contract, followed by coupling units and aggregation code. Those determine whether released labels can support an exact ML reconstruction at all. A later independently designed model may be scientifically useful, but it must state its new choices explicitly and cannot certify the undisclosed author settings.
