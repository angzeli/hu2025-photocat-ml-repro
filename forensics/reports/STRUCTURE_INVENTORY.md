# Original-material and coordinate inventory

The immutable source root is `orginal/` (the existing spelling is intentional). This audit read all 6,901 files, detected their contents, and parsed every coordinate row. No source file was rewritten, renamed or extracted in place. The original-data manifest contains file metadata and hashes; the coordinate outputs contain counts, compositions and element-order metadata, never complete coordinates.

## Complete local inventory

**DIRECTLY OBSERVED / COMPUTED FROM RELEASED DATA:** there are 6,901 files totaling **85,541,434 bytes**.

| Content class | Files | Validation |
|---|---:|---|
| Article PDF | 1 | PDF header and full document structure parsed; 15 pages |
| Supplementary Information PDF | 1 | PDF header and full document structure parsed; 99 pages |
| XLSX workbooks | 5 | Recognized as OOXML by internal content types and workbook XML; all ZIP member CRC checks pass |
| Root computational coordinate texts | 6 | Every line parsed as element and three finite numeric coordinates |
| MD coordinate texts | 6,888 | Every line parsed as element and three finite numeric coordinates |
| Standalone ZIP/TAR archives | 0 | Content-based detection, not a filename-only search |

All original bytes have SHA-256 records in `data/manifests/original-files.csv`. There are **no byte-identical duplicate groups**. The largest file is the SI PDF, 11,898,869 bytes; no file exceeds 100 MiB. Size does not alter the task's local-only provenance rule.

The five Excel files are ZIP containers internally. Their XML, sheets, relationships, hidden content and embedded objects are audited separately by the workbook audit. They are not counted as independent downloadable coordinate archives. No standalone archive exists locally, so no `archive-contents.csv` is generated; inventing an archive-member list for the already expanded directory would overstate provenance.

## Nature/Springer package correspondence

The publisher's [article and supplementary-material listing](https://www.nature.com/articles/s41929-025-01291-z) supplies the package descriptions below. The `MOESM` number is a publisher storage identifier; it is not the displayed Supplementary Data number.

| Local item / published identifier | Publisher description | Local status |
|---|---|---|
| `41929_2025_1291_MOESM1_ESM.pdf` | Supplementary Information | Present |
| `41929_2025_1291_MOESM2_ESM.xlsx` | Supplementary Data 1; supplementary figure source data | Present |
| `MOESM3`–`MOESM8` TXT files | Supplementary Data 2–7; GS, TI1, MS, TI2, TI3, TI4, respectively | Present; six parsed structures |
| `41929_2025_1291_MOESM9_ESM.zip` | Supplementary Data 8; initial and final MD configurations of all combinations | Archive absent; `MD_configurations/` has matching content roles |
| `41929_2025_1291_MOESM10_ESM.cif` | Supplementary Data 9; CAT1 CIF | Absent locally |
| `MOESM11`, `MOESM12`, `MOESM13` XLSX files | Source Data for Figs. 1, 2, 3 | Present |
| `41929_2025_1291_MOESM14_ESM.xlsx` | Source Data Extended Data Fig. 4, according to publisher | Present; workbook sheet labels Extended Data Fig. 3, a mapping discrepancy |

The association of the expanded MD folder with Supplementary Data 8 is **STRONG INFERENCE** from its contents and the publisher's description. The missing ZIP cannot be checksum-compared, so exact archive-to-directory identity, original archive ordering, and complete extraction provenance are not proven. The local audit establishes what is present; it does not claim that every publisher release has been downloaded.

## MD coverage and content-level findings

**DIRECTLY OBSERVED:** all 6,888 MD files match `cat-{CAT}_pho-{PS}_{initial|final}.txt`. Their identities form the complete Cartesian product **CAT 1–84 × PS 1–41 = 3,444 pairs**, with exactly one initial and one final file per pair. No identities or endpoints are missing from this grid. The filename coverage encompasses the entire pre-screen universe, rather than only 180 retained pairs.

**COMPUTED FROM RELEASED DATA:**

- Every MD file contains 118–221 atoms in one headerless element–x–y–z block.
- No coordinate file contains a blank line, comment, title, atom-count header, second block delimiter, time stamp, snapshot index, train/test label, dipole value or other metadata record.
- For all 3,444 pairs, the initial and final element sequences match exactly; none has numerically identical initial and final coordinates.
- There are 3,444 distinct MD element-order sequences, each shared by its initial/final pair. Row ordering is directly recoverable, and element-sequence consistency is established between endpoints. Persistent atom identity is not independently proven for indistinguishable atoms of the same element, because explicit atom IDs are absent.
- Across all 6,894 coordinate files, no complete numeric coordinate list is duplicated.
- The arithmetic centroid is nonzero (tolerance 10⁻⁸ in the unlabelled coordinate units) in every MD file. These supplied whole-system coordinates are not centered on their arithmetic centroid. This observation does not identify the preprocessing applied to the unpublished neural-network inputs.

The atom rows have the form conventionally used for Cartesian coordinates, but the files do not explicitly state coordinate units, cell vectors, periodic boundary conditions, time, charge, multiplicity or molecule boundaries. Such information must be sourced from the paper/SI where available. Periodic wrapping, intermolecular distances, coordination shells or bonds should not be assumed from these files alone without the required conventions.

**Presence conclusion:** the local coordinate release contains **6,888 MD endpoint geometry blocks**, plus six reaction-coordinate geometries. It does **not** contain 180 × 1,000 intermediate snapshots. This conclusion follows from parsing the full contents of every coordinate file, not merely interpreting `initial`/`final` filenames. It remains scoped to the locally supplied material; the original ZIP itself is unavailable for byte-level comparison.

## Six separately released computational geometries

Publisher labels identify these as reaction-pathway structures, not a set of independently optimized versions of all 84 catalysts and all 41 photosensitizers.

| Source | Publisher label | Atoms | Composition (computed) | Co row (1-based) |
|---|---|---:|---|---:|
| `41929_2025_1291_MOESM3_ESM.txt` | GS | 50 | C15 Co1 H27 N5 O2 | 1 |
| `41929_2025_1291_MOESM4_ESM.txt` | TI1 | 47 | C15 Co1 H25 N5 O1 | 1 |
| `41929_2025_1291_MOESM5_ESM.txt` | MS | 50 | C16 Co1 H25 N5 O3 | 1 |
| `41929_2025_1291_MOESM6_ESM.txt` | TI2 | 50 | C16 Co1 H25 N5 O3 | 1 |
| `41929_2025_1291_MOESM7_ESM.txt` | TI3 | 51 | C16 Co1 H26 N5 O3 | 41 |
| `41929_2025_1291_MOESM8_ESM.txt` | TI4 | 49 | C16 Co1 H25 N5 O2 | 1 |

The different Co position in TI3 is a concrete reason not to assume a universal "metal is the first atom" convention. File order is evidence; an atom-selection convention for the neural network is a separate question.

## Recoverability of the labelled neural-network input X

| Object / convention | Assessment from coordinates | Evidence and limit |
|---|---|---|
| Initial/final pair identity | Directly recoverable | Numeric CAT/PS IDs in all filenames; full 84 × 41 grid |
| Endpoint coordinates and atom order | Directly recoverable locally | Complete finite coordinate records, preserved initial/final element ordering |
| Exact 1,000 CAT and 1,000 PS labelled conformations | Absent as an identified dataset | Only pair endpoints and six reaction structures are present; no label-to-geometry mapping |
| Molecule/atom segmentation within pair files | Partially inferable | Elements and ordered rows available; no explicit atom-to-molecule IDs or bonds |
| Snapshot / conformation ID | Absent | No IDs in contents; filenames identify only pair and endpoint |
| Dipole source-data row link | Absent | No row IDs, descriptor IDs or ML labels in coordinate files |
| Train/test index link | Absent | No split indicators or index lists in coordinate files |
| Selected metal-centered environment | Not recoverable from these files alone | Element identities and metal positions exist, but the trained atom selection and label linkage do not |
| Coordinate origin / frame used for labels | Absent | Endpoint axes are retained, but no training-frame transformation is recorded |
| Centering / normalization used for X | Absent | Whole-system endpoint coordinates do not specify NN preprocessing |
| Length units, cell, PBC, time | Absent from the files | Consult paper/SI separately; do not assign units by magnitude alone |

No geometry is authenticated as one of the first-principles-labelled ML samples. It is logically possible that an unlabelled endpoint coincides with an unreported training sample, but the release supplies no way to establish that coincidence. The correct conclusion is that the **exact labelled X and its row mapping are unrecoverable**, rather than an assertion that no endpoint could ever have been used during training.

A complete 180,000-frame trajectory, or a separately indexed 2,000-molecule labelled geometry set, cannot be reconstructed exactly from two endpoints per pair. Simulation of new trajectories would generate new data and lies outside Phase 0.

## Reproducible outputs and validation

- `forensics/scripts/inventory_original_files.py` detects PDF/OOXML/text/archive contents, hashes every original, parses PDF document structures, verifies ZIP CRCs, and inventories any nested non-OOXML archives in memory if present.
- `forensics/scripts/inspect_coordinates.py` requires every coordinate line to contain a valid element and three finite values; it rejects unrecognized or nonfinite records and computes coverage/order metadata.
- `data/manifests/original-files.csv` and `original-summary.json` record complete file-level provenance and inventory counts.
- `forensics/outputs/structure_metadata.csv` records per-file atom counts, compositions, numeric IDs and element-order hashes without coordinates.
- `forensics/outputs/structure_summary.json` records aggregate coverage, initial/final consistency and missing-metadata findings.

Both scripts completed successfully against all local originals. The root Phase-0 validation separately compares original hashes and modification times before and after the complete analysis. The manifest and structure records have one row per corresponding original file, and the reported counts are derived from those outputs.
