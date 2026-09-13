# Hu et al. 2025: Phase-0 data forensics

Audit date: 2026-09-13. Target: Hu et al., *Nature Catalysis* **8**, 126–136 (2025),
[DOI 10.1038/s41929-025-01291-z](https://doi.org/10.1038/s41929-025-01291-z).
This is an independent audit of released evidence, not a new simulation, trained
neural network, or claim of end-to-end reproduction.

Evidence labels used throughout: **DIRECTLY OBSERVED** means file contents or an
explicit published statement; **COMPUTED FROM RELEASED DATA** means an independently
executed calculation; **STRONG INFERENCE** means a supported but non-explicit link;
**SPECULATION** means a possible explanation without sufficient evidence to adopt it.
Published claims are not automatically computationally verified results.

Source shorthand: **article**=`orginal/s41929-025-01291-z.pdf`;
**SI**=`orginal/41929_2025_1291_MOESM1_ESM.pdf`; **D**=MOESM2 workbook;
**F**=MOESM11 workbook. All PDF pages are one-based; SI printed pages are PDF page−1.
Other package names resolve through [the source manifest](../../data/manifests/original-files.csv).

## 1. Executive summary

**COMPUTED FROM RELEASED DATA:** The complete first screen is recoverable: 84 CAT
adsorption energies and 41 PS lifetimes give 18 CATs,10 PSs and 180 Cartesian-product
identities. All four dipole targets have900 training and 100 test samples with three
calculated and three predicted components. Both coupling validations contain1,000
calculated/predicted pairs. Recomputed Pearson correlations are **0.912925953 for J**
and **0.747549173 for J***.

**STRONG INFERENCE:** Numeric pairing is substantially better supported than sample
counts alone suggest. With train rows followed by test rows, a fixed dipole tensor
and one scalar reproduce both calculated/predicted coupling channels almost exactly.
This supports Fig.5+6→9a and Fig.7+8→9b numerical order; it does not identify the
physical conformations or prove that all four targets use the same geometry pair.

**DIRECTLY OBSERVED:** Only34 numerical J/J* points occur in the Fig.1d workbook,
not180 labelled system scores. There are6,888 MD endpoint geometries covering all
3,444 combinations, not a released180,000-frame trajectory. Exact ML geometries,
feature definitions, weights, trained widths, several training settings, coupling
units and the averaging implementation are unavailable or unresolved.

**COMPUTED FROM RELEASED DATA:** Seven plotted points satisfy the proposed50/0.01
coupling probe, but those thresholds are not uniquely identified. The measured
experimental table has 6 filtered+37 ruled-out systems. A compatible, non-unique
joint performance criterion gives TP6/FP0/FN1/TN36, precision100%, recall85.714%.
The classification/units/aggregation uncertainties remain explicit.

## 2. Repository and remote state

**DIRECTLY OBSERVED:** The starting folder had `orginal/` and a Finder metadata file,
no `.git/`, no branch/HEAD/index/history, and no remotes. Read-only
`git ls-remote https://github.com/angzeli/hu2025-photocat-ml-repro` succeeded with no
refs, including no branches or tags. An initial sandbox DNS restriction was resolved
by an authorized read-only network call; it was not interpreted as an empty remote.

The repository was initialized on `main`, with `origin` set to that exact URL.
There was no existing local/remote history to overwrite or reconcile. Local commits
contain Phase-0 text, metadata and independently computed outputs. No upstream
branch exists while the remote is empty; ahead/behind is therefore undefined.
A later authorized first push should be straightforward if remote refs remain empty.
No push, tag, release, LFS setup or history rewrite is part of this task.

`orginal/` was ignored before staging or committing. Full source-derived numeric
extracts are additionally ignored under `forensics/local_only/`; they are not
redistributed as converted CSVs. Source/type/hash/history checks and a manual
content review protect the commit boundary. See [source policy](../../docs/SOURCE_POLICY.md)
and [final validation record](../outputs/final_validation.json). Exact final HEAD
and commit IDs are reported at task completion, rather than embedded self-referentially
in a commit. Read-only final remote inspection confirms the unchanged empty remote.

## 3. Original-material inventory

**COMPUTED FROM RELEASED DATA:** 6,901 files total 85,541,434 bytes: two PDFs, five
XLSX workbooks and 6,894 coordinate text files. The article has 15 PDF pages, including
four Extended Data pages; SI has 99. Five XLSX containers pass ZIP CRC/XML parsing.
All6,894 coordinate texts parse as finite element/x/y/z records. No byte duplicates
or standalone ZIP/TAR archives exist in the supplied folder. No file exceeds100MiB;
the largest, SI, is11,898,869 bytes. Size does not relax the exclusion policy.

Every file has relative path, size, SHA-256, content-detected type, package role and
parse status in `data/manifests/original-files.csv`. Hashes, sizes and modification
times were recorded before analysis and compared after analysis. Sources are opened
read-only; no conversion or extraction is written into `orginal/`.

**DIRECTLY OBSERVED:** MOESM2 and 11 contain pre-task local Excel save metadata.
Temporary fresh publisher copies differ in byte hashes but match **every nonempty
cell exactly**, including resolved strings, numeric values, formulas and stored
values. Their inspected structural fields also match; neither publisher copy hides
IDs in unused strings, charts or embedded data. Thus local hashes identify the
supplied files, not pristine publisher bytes, while their tabular content agrees.
See `forensics/outputs/publisher_comparison.json` for hashes, counts and comparison
limits. No publisher comparison copy is committed.

## 4. Nature/Springer data-package mapping

**DIRECTLY OBSERVED:** The publisher page lists14 supplementary/source packages.
The machine-readable [publisher package map](../../data/manifests/publisher-packages.csv)
records links and local presence. Mapping was checked against the actual page,
not inferred solely from numbering.

| Package | Publisher role | Local audit |
|---|---|---|
| MOESM1 | Supplementary Information | Present,99-page PDF |
| MOESM2 | Supplementary Data1, supplementary figure source values | Present,53 sheets |
| MOESM3–8 | Supplementary Data2–7, optimized GS/TI1/MS/TI2/TI3/TI4 | Six single-geometry text files |
| MOESM9 | Supplementary Data8, MD initial/final configurations | ZIP absent;6,888 loose MD files present |
| MOESM10 | Supplementary Data9, CAT1 CIF | Missing locally |
| MOESM11 | Source Data Fig.1 | Present,2 sheets |
| MOESM12 | Source Data Fig.2 | Present,3 sheets |
| MOESM13 | Source Data Fig.3 | Present,6 sheets |
| MOESM14 | Source Data Extended Data Fig.4 | Present; sheet says Extended Data Fig.3, a label discrepancy |

**STRONG INFERENCE:** `MD_configurations/` is the expanded MOESM9 package because
its content and complete endpoint grid match the publisher description. Without
the original archive, its exact byte identity and member manifest cannot be checked.
There are no standalone local archives to extract recursively; every loose file was
inspected by contents. XLSX ZIP internals were independently audited. Missing local
CAT1 CIF is distinguished from publisher non-release. The present task did not add
new files to `orginal/`.

## 5. Descriptor pre-screen reconstruction

**DIRECTLY OBSERVED:** SI Fig.1 PDF9 specifies strict Ead<−0.20eV and SI Fig.2 PDF10
specifies strict τ>90ns. D `Supplementary Fig. 1!A2:A85` contains 84 numeric energies;
`Supplementary Fig. 2!A2:A42` contains 41 lifetimes. SI Tables1–2, PDF73–76, explicitly
index these values. The independent PDF/table cross-check has zero disagreements
at the SI's printed precision, so numeric row order is an evidenced identity mapping.

**COMPUTED FROM RELEASED DATA:** Retained CAT IDs are
**1,2,3,13,14,15,25,26,27,37,38,39,49,50,51,61,62,63**.
Retained PS IDs are **1,4,12,17,18,20,28,33,36,41**. None lies exactly at a cutoff.
The full ranges are−0.35356 to 1.217eV and 13.19672 to 266.15942ns.
The product contains exactly 18×10=180 unique CAT/PS pairs.

`retained_catalysts.csv`, `retained_photosensitizers.csv` and `candidate_180.csv`
store derived identities and provenance. Full descriptor extractions remain in
ignored `forensics/local_only/descriptor_values.csv`. No full source table is tracked.

**DIRECTLY OBSERVED, SOURCE INCONSISTENCY:** Article equation(1), PDF7/printed132,
prints a plus sign before E_cat: Ead=E_complex+E_cat−E_CO2. This audit does not silently
replace it with a conventional formula. Thresholding the released values is exact;
recalculating adsorption energies would require resolving that reference convention.

## 6. ML dataset reconstruction

**DIRECTLY OBSERVED:** The four validation tables recover12,000 calculated scalar
dipole components and 12,000 predicted components: four targets×1,000 rows×three
Cartesian components. They do not supply the structural input matrix X. Article
Methods describes separately sampled 1,000 CAT and 1,000 PS conformations and a
900/100 split for each species. Extended Data Fig.3 instead schematically subtracts
2,000 coupling-labelled conformations from 180,000; this does not establish a common
paired snapshot-index scheme. [Article PDF7–8,14.]

| X-related object | Classification | Evidence/limit |
|---|---|---|
| CAT/PS universe and endpoint identities | Directly recoverable | Explicit descriptor IDs and filenames |
| General input concept | Directly recoverable | Coordinates of metal and surrounding atoms, article PDF8 |
| Exact1,000 CAT and 1,000 PS selected geometries | Absent as identifiable dataset | No sample-to-file key or intermediate frames |
| Metal-centred local environments | Inferable concept; exact selection absent | No atom-index/radius/bond rule |
| Atom order within released endpoint file | Directly recoverable | Line order; input-vector order absent |
| Coordinate convention and input frame | Absent | No model input schema or rigid-frame prescription |
| Normalization/centering/target scaling | Absent | Must not assume no preprocessing |
| Snapshot IDs and pre-split sample indices | Absent | Spreadsheet row numbers identify plotted records only |
| Train/test plotted membership | Directly recoverable | Separate900/100 blocks |

Changing geometries, atom selection, frame or normalization would define an
independent reimplementation; it would not reconstruct the original author X.

## 7. Supplementary Figs.5–8 findings

**DIRECTLY OBSERVED:** Across all five workbooks,65 sheets are visible. No hidden
rows/columns, defined names, comments, formulas, external links, chart caches,
embeddings, drawings or macros were found. Ordinary merged headings, styles and
empty serialized cells are formatting, not hidden ML data. Full sheet order,
dimensions, nonempty counts, relationships and metadata are in `workbook_audit.json`.

Fig.5=CAT intrinsic,6=PS intrinsic,7=CAT transition,8=PS transition. Each contains
900 training samples in A4:B903,F4:G903,K4:L903 and 100 test samples in
C4:D103,H4:I103,M4:N103. Within each pair, first column=calculated and second=predicted;
the three blocks are Cartesian x/y/z. Generic worksheet labels x/y denote plot axes,
not those three target components. SI PDF13–16 supplies the semantic correspondence.

**COMPUTED FROM RELEASED DATA:** All records are finite and complete. The following
statistics pool x/y/z:2,700 scalar training values or 300 test values, still900/100
conformations. `ml_metrics.csv` contains 32 rows: per-component and pooled results.
R²=1−SSE/SST against calculated values; it is not r². MAE andRMSE are in unresolved
source units. These are recalculated prediction statistics, not newly trained results.

| Target | Split | Pearson r | R² | MAE | RMSE |
|---|---|---:|---:|---:|---:|
| CAT intrinsic | Train |0.945356|0.892176|1.427174|2.337915|
| CAT intrinsic | Test |0.964168|0.928739|1.595103|2.171721|
| PS intrinsic | Train |0.965032|0.931199|1.158132|1.606455|
| PS intrinsic | Test |0.965538|0.931915|1.140544|1.515579|
| CAT transition | Train |0.844695|0.704106|0.032910|0.055673|
| CAT transition | Test |0.879775|0.768187|0.031160|0.046658|
| PS transition | Train |0.862415|0.741005|0.191950|0.265942|
| PS transition | Test |0.864336|0.745103|0.199044|0.278501|

## 8. Supplementary Fig.9 findings

**DIRECTLY OBSERVED:** D Fig.9 A3:B1002 andD3:E1002 contain exactly 1,000
calculated/predicted pairs each for J andJ*. There are no explicit train/test labels
on this sheet. Full arrays are recovered only to ignored local storage.

**COMPUTED FROM RELEASED DATA:**

| Coupling | Calculated range | Predicted range | Pearson r | R² | MAE | RMSE |
|---|---|---|---:|---:|---:|---:|
| J |−2001.9466 to 4820.3512|−1869.4985 to 4539.516|0.912925953|0.829605104|145.672023|224.144248|
| J* |−3.25842 to 3.43637|−2.57829 to 2.8211|0.747549173|0.558007372|0.311711337|0.494507892|

Both channels include positive and negative values; exact sign counts and
disagreements are in `supfig9_coupling_metrics.csv`. The correlations independently
round to 0.913 and 0.748. Source numerical units remain unresolved.

## 9. Row-alignment investigation

**COMPUTED FROM RELEASED DATA:** Concatenate each dipole sheet's900 train rows,
then100 test rows. Estimate one zero-intercept scale s from only the first900
calculated-J rows using q=−2μCAT,xμPS,x+μCAT,yμPS,y+μCAT,zμPS,z. The result is
**s=5.03406364931**. Hold it fixed and calculate s×q for the other rows and channels.

| Reconstructed channel | All1,000-row R² | Last100-row R² | RMSE |
|---|---:|---:|---:|
| J calculated |≈0.9999999999996|≈1.000000000000|0.000342698|
| J predicted |0.999999991170|0.999999919269|0.043528853|
| J* calculated |0.999999145488|0.999998987987|0.000687582|
| J* predicted |0.999999247022|0.999999189344|0.000463991|

The last100 rows were not used to infer the scalar. Test-first order, a one-row
shift and 100 deterministic permutations are negative controls; their results are
recorded in `ml_analysis.json`. This is a bounded algebraic provenance test, not
neural-network fitting. Nonzero residuals remain and are not automatically explained
as rounding errors.

**STRONG INFERENCE:** Numeric CAT/PS pairing within intrinsic data and within
transition data, and their corresponding Fig.9 row order, are **strongly supported**.
The tensor form is compatible with a fixed separation direction along x.
The scale does not uniquely identify distance, dielectric factor or unit conversion.

**SPECULATION:** All four targets may share a physical conformation pair, but that
conclusion is only **plausible**. Separate mathematical correspondences to adjacent
coupling columns are not independent proof of shared structural identity. No
geometric identifiers, explicit intrinsic/transition sample join, or pre-split index
file exists in the inspected tables, hidden metadata or coordinate records.

## 10. Coordinate / MD archive findings

**COMPUTED FROM RELEASED DATA:** Every one of 6,894 text files consists only of
finite element/x/y/z lines, with no header, frame delimiter, time, charge/spin,
cell/PBC metadata, or conformation label. MD naming covers CAT1–84×PS1–41 exactly,
with 3,444 initial+3,444 final files. There are118–221 atoms per MD file. Every
initial/final pair has identical element order and changed numeric coordinates.
The atom identity of indistinguishable elements is not proven by element order.

All180 retained pairs have endpoints (360 files), but endpoints do not determine
their1,000 sampled conformations. No additional frames are embedded in the text.
No exact label-to-geometry mapping identifies1,000 CAT or 1,000 PS training inputs.
A coincidental endpoint match cannot be excluded, but it is not a recovered dataset.

The six root text files contain50,47,50,50,51,49 atoms and represent GS/TI1/MS/TI2/TI3/TI4
optimized reaction structures. They are not the claimed2,000 ML inputs. Atom order
also varies across these structures (Co first except MOESM7 at line41), warning
against assuming a universal metal-first schema.

**DIRECTLY OBSERVED:** Methods specifies298K,1fs,5nm cubic periodic box,110ps total,
10ps equilibration and sampling every0.1ps over 100ps. These published settings do not
restore missing trajectories, random selections or forcefield implementation inputs.
The complete [structure audit](STRUCTURE_INVENTORY.md) preserves that distinction.

## 11. Fig.1d screening reconstruction

**DIRECTLY OBSERVED:** F `Fig.1d!A2:B35` has 34 complete numerical pairs and no IDs.
Stored worksheet dimensions and parsed cell extents include empty formatting; the
nonempty numerical extent ends at row35. The publisher comparison confirms the
same34-point content. No additional180-system table occurs in workbook caches.

**COMPUTED FROM RELEASED DATA:** J ranges1.32218–396.24469; J* ranges0.00145–0.16263.
All values are positive. The explicit user-suggested probe J>50 AND J*>0.01 retains
**7 points**, at Excel rows2,21,25,26,27,29,30. Its count matches the stated seven
initial selections **exactly**, but count agreement does not prove point membership,
the author threshold values, or coverage of all 180 systems.

Threshold identifiability is weak: fixing J*>0.01, any strict-J cutoff in
**[32.06871,50.81013)** retains the same seven points. Fixing J>50, any strict-J*
cutoff in **[0.00342,0.0137)** also does so. These are separate conditional intervals,
not a jointly validated threshold rectangle. The plotted region supports an
approximate boundary; the source data do not uniquely identify numerical settings.

The34 rows are at most18.9% of 180 distinct pair scores under the assumption of one
row per system. Since IDs are absent, even that percentage is a point-count comparison,
not verified identity coverage. The other146 retained pair scores cannot be recovered
from this file. `fig1d_classification.csv` stores ranks and decisions, not a duplicate
of the original coordinate table.

## 12. Candidate identity mapping

**DIRECTLY OBSERVED:** SI Table3 supplies the selected set:
CAT1/PS1, CAT37/PS41, CAT49/PS1, CAT61/PS4, CAT49/PS18, CAT49/PS33 andCAT50/PS41.
The last was not experimentally measured because CAT50 was not synthesized.
Set membership is exact/direct; Table3 does not attach the seven J/J* coordinates.

**STRONG INFERENCE:** The Fig.1 star is explicitly the best system; the article
identifies it as CAT1/PS1. Its unique high-J* position matches F row2,
(J,J*)=(77.34961,0.16263). This one row mapping is **high-confidence inference**,
not a spreadsheet label. The other six probe-positive numerical rows remain **unresolved**;
their ordering is not assigned by visual intuition or by sorting Table3.

`selected_systems.csv` records direct set membership; `fig1d_identity_mapping.csv`
records the separate row-mapping confidence. CAT61/PS33 is the ruled-out success,
not a seventh measured prediction. CAT49/PS34 is a distinct ruled-out system and
must not be conflated with selected CAT49/PS33. The SI condition-study paragraph's
classification conflicts with Table3; details are preserved in the methods audit.

## 13. Fig.1e experimental validation reconstruction

**COMPUTED FROM RELEASED DATA:** F `Fig.1e!A2:D44` contains 43 unique CAT/PS rows
with TON_CO and CO selectivity. All43 measured rows agree exactly with SI Table3;
Table3 additionally includes the unmeasured CAT50/PS41 identity, for 44 total rows.
Explicit Table3 grouping gives **6 measured filtered and 37 ruled-out** systems.
The first seven worksheet rows are not all filtered: one is CAT61/PS33, the exception.
No error bars or replicate columns occur in this Fig.1e source table.

SI Table3 additionally supplies TOF_CO (h−1) and irradiation time (h), beyond the
Fig.1e workbook's four columns. Their existence is directly observed; neither
provides the missing prespecified good-system criterion or coupling-point IDs.

**DIRECTLY OBSERVED:** The paper's declared outcome arithmetic is6/6 precision
and 6/7 recall on the tested set. The unsynthesized seventh prediction is excluded
from the measured precision denominator; it is not established as a false positive.

**COMPUTED FROM RELEASED DATA, CONDITIONAL:** TON_CO>1370 AND selectivity>72%
classifies7 systems as good and produces TP6,FP0,FN1,TN36; precision1.0,
recall0.857142857. The FN is CAT61/PS33. This numerical good-system rule is compatible
with the reported outcome, but was not uniquely defined in the publication.
For the same labels, fixing selectivity72 permits TON cutoffs in[1155,1404);
fixing TON1370 permits selectivity cutoffs in[70.4,73.2). These intervals demonstrate
non-uniqueness. Alternative single-outcome definitions change recall, as shown in
`validation_sensitivity.csv`. Recall across all 180 or 3,444 systems is unmeasured.

**DIRECTLY OBSERVED, SOURCE INCONSISTENCY:** Excluding the exceptional ruled-out
success, five other ruled-out rows have TON≥1370 and nine have selectivity≥72%.
They can be outside a joint high-performance region; the prose's literal claim of
both individual values below those limits is nevertheless inconsistent with the table.
The Fig.1d caption's five-blue-point wording also differs from seven initial
selections (six blue plus star); Fig.1e represents the six measured predictions.

Full measurements are in ignored `forensics/local_only/fig1e_source.csv`.
Tracked `fig1e_validation.csv` contains identities, group labels and computed
conditional decisions without reproducing the original measurement columns.

## 14. Coupling aggregation investigation

**DIRECTLY OBSERVED:** Article equations3–4 use the dipole tensor with the
centre-of-mass connecting vector; Methods Step4/ED Fig.3 says statistical average.
It does not specify signed mean, mean magnitude, absolute signed mean orRMS.
No pair-indexed1,000-snapshot coupling series links to Fig.1d.

**COMPUTED FROM RELEASED DATA:** Applying those four operations to the validation
arrays illustrates their non-equivalence. These are **validation-array summaries**,
not reconstructed averages for any particular CAT/PS pair.

| Validation channel | mean(J) | mean(abs(J)) | abs(mean(J)) | RMS |
|---|---:|---:|---:|---:|
| J calculated |21.018031|315.345844|21.018031|543.405970|
| J predicted |29.585000|254.465387|29.585000|464.173678|
| J* calculated |0.001008632|0.489122432|0.001008632|0.743817023|
| J* predicted |0.001300824|0.314403369|0.001300824|0.534712155|

**SPECULATION:** Any of these operations might explain positive map values under
some unknown pair distribution. Positive plotted values do not prove magnitude
averaging; the validation sample is not established as one map pair's ensemble.
Scale and sign therefore cannot rank the candidates reliably. The shared alignment
scalar is evidence about validation-row recombination, not about trajectory averaging.
The aggregation rule remains **UNKNOWN**, with all four candidates unranked.

Unit audit: descriptor energies are explicitlyeV and lifetimesns. Intrinsic and
transition dipole units and J/J* numerical units are not located in the inspected
article, SI, worksheet labels or coordinate metadata. The equations describe an
energy-like interaction but do not identify the workbook's conversion. Do not
assign Debye, atomic units, eV, meV, cm−1 or arbitrary units from magnitude alone.

## 15. Recoverable versus missing neural-network implementation details

**DIRECTLY OBSERVED:** Article PDF8 discloses TensorFlow/Keras, two hidden ReLU
layers, candidate widths 256/512/1024, L1 regularization, Adam learning rate 1e−4,
900/100 samples, local metal-environment coordinates, and Cartesian vector outputs.
It does not disclose software versions, selected widths, L1 coefficient, loss,
batch size, epochs, early stopping, random seed, normalization, initialization,
learning-rate schedule or original split indices. No code, notebook, serialized
features, weights or checkpoints occur in the complete supplied inventory or
workbook embeddings.

The number of fitted models is ambiguous: the text describes two transition models
while also discussing intrinsic and transition three-component outputs. Four plotted
target families do not alone settle fitted-model grouping. The exact input dimension,
atom lists, padding, frame, and output activation remain unavailable. Gaussian16,
ωB97XD, LANL2DZ/6-31G(d) and PCM are method-level disclosures, not an executable
label-generation dataset. See [the methods audit](PAPER_METHODS_AUDIT.md) for exact
page references and every X/hyperparameter gap.

## 16. Reproducibility risk assessment

The [reproducibility matrix](REPRODUCIBILITY_MATRIX.md) distinguishes recoverable
arrays from recoverable scientific processes. Exactly recoverable objects include
125/125 descriptors,180/180 reconstructed identities, all released validation
arrays, and 43/43 measured experimental rows. Numerical row order is inferable
blockwise, and one screening-point identity has a strong cross-source anchor.

Exact retraining is blocked by X and feature/split/model gaps; full screening is
blocked by trajectories, units, aggregation and missing labelled pair scores.
The final publisher comparison shows that missing IDs are not explained by local
workbook re-saving. Endpoint completeness does not cure trajectory incompleteness.
A single overall reproduction percentage would conceal these dependencies and is
not assigned. Phase0 verifies released-data arithmetic, not model generalization,
physical validity or the success of an independent reimplementation.

Validation is bounded: scripts ran on the supplied evidence, the SI independently
corroborates descriptors/experimental rows, alignment includes held-out rows and
ordering controls, and original hashes/sizes/mtimes match the initial baseline.
No dynamics, DFT or neural-network training was launched. Detailed computational
checks do not replace author clarification of unresolved scientific conventions.

## 17. Exact unresolved questions

1. What are the exact1,000 CAT and 1,000 PS geometry records, atom order and source
   snapshot IDs? How do all four target tables join to them and to Fig.9?
2. What atom-selection, centering, rotation, normalization, padding and unit schema
   forms X? How are reduced-PS charge/state and transition roots assigned per row?
3. What model count, widths, output activations, loss, L1 strength, epochs, batch
   size, seeds, package versions and trained weights generated the predictions?
4. What physical separation, coordinate frame, units and dielectric convention
   produce the observed common coupling scalar? Why is its fixed-axis form so exact?
5. Where are the 180 pair-indexed1,000-snapshot coupling ensembles, aggregation code
   and full pair-score table? Why does Fig.1d release only 34 unlabelled pairs?
6. Which numerical rows map to the six selected systems beyond the anchored star?
   What exact J/J* and experimental-good rules were used?
7. How should the printed adsorption-energy sign,2000-label accounting, blue-marker
   count and PS33/PS34 condition-study discrepancy be interpreted?
8. Can the original MD ZIP/member manifest and locally missing CAT1 CIF be supplied
   to close package provenance? They would not alone restore the missing ML inputs.

## 18. Recommended Phase-1 work

Prepare an evidence-specific author data request centred on the **geometry→feature→
label→split key** and the **coupling units/aggregation implementation**, using the
observed row-order/tensor relation as a precise question. Include the missing full
pair-score table, selected-point IDs and training configuration as supporting needs.
Drafting that request is justified; sending it requires explicit user authorization.

Do not start model training until the input contract is obtained or the user
explicitly elects an independently designed approximation. If authors cannot supply
the missing objects, a subsequent project must label its new feature/model/averaging
choices as assumptions and target a bounded sensitivity study, not exact reproduction.
