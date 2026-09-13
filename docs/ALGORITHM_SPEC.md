# Algorithm specification: published workflow and recoverability

Status: Phase 1. This specification describes Hu et al., *Nature Catalysis* **8**,
126–136 (2025), [DOI 10.1038/s41929-025-01291-z](https://doi.org/10.1038/s41929-025-01291-z).
It does not claim recovery of the authors' executable workflow. No production MD,
quantum-chemistry calculation, or neural-network training has been performed here.

Evidence labels are **DIRECTLY OBSERVED**, **COMPUTED FROM RELEASED DATA**,
**STRONG INFERENCE**, **SPECULATION**, and **REIMPLEMENTATION CHOICE**. A published
statement is directly observed as a statement, not independently verified physics.
Future choices are defined in [the computation contract](REIMPLEMENTATION_CONTRACT.md).

Sources: M = `orginal/s41929-025-01291-z.pdf`; S =
`orginal/41929_2025_1291_MOESM1_ESM.pdf`; D = MOESM2 workbook; F = MOESM11 workbook.
PDF pages are one-based. The authoritative starting audits are [Phase 0](../forensics/reports/PHASE0_DATA_FORENSICS.md),
[matrix](../forensics/reports/REPRODUCIBILITY_MATRIX.md), [methods](../forensics/reports/PAPER_METHODS_AUDIT.md),
[workbooks](../forensics/reports/WORKBOOK_ML_AUDIT.md), and [structures](../forensics/reports/STRUCTURE_INVENTORY.md).
Phase-1 physical reconstruction is documented [separately](../forensics/reports/PHASE1_COUPLING_RECONSTRUCTION.md).

## 1. Chemical universe: 41 PS × 84 CAT

- **Published / DIRECTLY OBSERVED:** 41 Cu(I) photosensitizers and 84 macrocyclic
  metal-complex catalysts define 3,444 pairs. [M pp. 3, 7; S Tables 1–2, pp. 73–76.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Indexed descriptor identities and
  3,444 initial/final endpoint pairs cover that complete grid.
- **Unresolved:** Endpoints omit bonds, molecule boundaries, explicit charges,
  multiplicities, counterion assignments, cell metadata, and coordinate units.
- **Consequence:** Preserve author IDs; require a chemically reviewed identity and
  state manifest before generating independent inputs. Geometry alone cannot assign charge/spin.

## 2. Descriptor pre-screen

- **Published / DIRECTLY OBSERVED:** Retain CAT with `E_ad < -0.20 eV` and PS with
  lifetime `> 90 ns`, both strict inequalities. [S Figs. 1–2, pp. 9–10.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** All 84 energies and 41 lifetimes;
  workbook row identities agree with independently indexed SI tables at printed precision.
- **Unresolved:** M equation (1), p. 7, prints `E_ad = E_complex + E_cat - E_CO2`.
  Its catalyst-energy plus sign must not silently become a conventional subtraction.
  Complete descriptor input/state and PS lifetime-rate conventions remain incomplete.
- **Consequence:** The minimal path applies the published inequalities to released
  values. The full path must resolve energy references and lifetime methodology first.

## 3. Retained universe: 18 × 10 = 180

- **Published / DIRECTLY OBSERVED:** First screening retains 180 systems. [M p. 3.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Exactly 18 CAT IDs and 10 PS IDs
  yield 180 unique identities in [candidate_180.csv](../data/derived/candidate_180.csv).
  No descriptor equals its cutoff.
- **Unresolved:** An endpoint is not a geometry authenticated as an ML label input.
- **Consequence:** Freeze this identity set for the minimal path; do not infer labels
  or sampling histories from its complete endpoint coverage.

## 4. Classical MD

- **Published / DIRECTLY OBSERVED:** NVT, Nosé–Hoover, 298 K, 1 fs, periodic cubic
  5 nm box, one CAT and one PS plus counterions, UFF family, 12.5 Å Lennard-Jones
  and Coulomb cutoff; total 110 ps including 10 ps equilibration. [M p. 7.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** 6,888 endpoint geometries, two per
  universe pair; no full trajectory, topologies, parameter files, or run inputs.
- **Unresolved:** Engine/version, UFF typing and metal coordination, charges,
  counterions, thermostat relaxation, solvent representation, cutoff treatment,
  boundary unwrapping, initial velocities, and seeds.
- **Consequence:** New trajectories are an independent realization. Published
  settings constrain, but do not complete, a runnable dynamics specification.

## 5. 1,000 conformations per retained pair

- **Published / DIRECTLY OBSERVED:** Sample every 0.1 ps across 100 ps after
  equilibration, producing 1,000 per pair and 180,000 overall. [M pp. 3, 7.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Only the initial/final endpoints
  are available for all 180 retained pairs (360 files).
- **Unresolved:** Original snapshot times, trajectory seeds, sampling endpoint
  inclusion, decorrelation, failed snapshots, and trajectory identities.
- **Consequence / REIMPLEMENTATION CHOICE:** Future full-run times are 10.1 through
  110.0 ps inclusive, spaced by 0.1 ps. Preserve time and parent-run IDs; the count
  is not a claim of 1,000 statistically independent observations.

## 6. Selection and first-principles labelling

- **Published / DIRECTLY OBSERVED:** Methods describes separate random selections
  of 1,000 CAT and 1,000 PS conformations. Gaussian 16, ωB97XD, LANL2DZ for transition
  metals, 6-31G(d) for other atoms, and PCM water/acetonitrile are method disclosures.
  PS dipoles refer to the reduced photosensitizer. [M pp. 7–8.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Four target tables each contain
  1,000 three-component calculated dipoles, with 900 training and 100 test rows.
- **Unresolved:** Exact geometries, sample join, charge/spin, solvent per calculation,
  TD roots, and state/phase/origin conventions. Extended Data Fig. 3 (M p. 14)
  subtracts 2,000 coupling-labelled conformations from 180,000; this differs from the
  separate-molecule selection described in Methods.
- **Consequence:** Do not equate 2,000 molecular records with 2,000 paired snapshots.
  Independent labelling must record separate molecule IDs and any explicit pair join.

## 7. Intrinsic and transition dipole prediction

- **Published / DIRECTLY OBSERVED:** Metal/local-atom coordinates; TensorFlow/Keras;
  two hidden ReLU layers; candidate widths 256/512/1024; L1; Adam at `1e-4`;
  three-component outputs and 900/100 split counts. [M p. 8.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Calculated/predicted vectors and
  prediction metrics for CAT intrinsic, PS intrinsic, CAT transition, PS transition.
- **Unresolved:** Feature schema, frames, original split indices, preprocessing,
  widths, fitted model count, loss, L1 coefficient, batch/epoch/seed settings and weights.
  The text's two-model language does not uniquely determine four-target model grouping.
- **Consequence / REIMPLEMENTATION CHOICE:** Four vector regressors are a baseline
  design, not recovered author models. New training requires newly linked geometry–label data.

## 8. Coupling construction

- **Published / DIRECTLY OBSERVED:** M equations (3)–(4), pp. 7–8, use the full dipole
  tensor with the CAT-to-PS centre-of-mass vector, separately for intrinsic and
  transition dipoles. A numerical dielectric/unit convention is not disclosed.
- **Recoverable / COMPUTED FROM RELEASED DATA:** Concatenating each 900-row train
  block then 100-row test block supports
  `q = -2*mu_CAT_x*mu_PS_x + mu_CAT_y*mu_PS_y + mu_CAT_z*mu_PS_z` and one common
  scalar across all four Fig. 9 channels. Phase-1 fitted values, axis controls,
  physical constants, and rounding bounds are in the [reconstruction report](../forensics/reports/PHASE1_COUPLING_RECONSTRUCTION.md).
- **STRONG INFERENCE:** Debye dipoles, cm⁻¹ coupling and an effective separation
  very near 10 Å provide a natural interpretation of the overwhelmingly favored
  x-axis tensor. This is conditional on vacuum screening; unit/distance combinations
  remain degenerate, and +x versus −x cannot be distinguished by this tensor.
- **Unresolved:** Common physical geometry across intrinsic/transition tables,
  origins for charged species, actual MD separations, standardization operations,
  solvent screening, and transition phase conventions.
- **Consequence:** Keep a released-table reconstruction route distinct from a
  physical MD-separation route. A successful fixed tensor cannot establish how
  the authors transformed geometries before evaluation.
- **REIMPLEMENTATION CHOICE:** The future standardized-distance branch applies one
  common proper rotation to both dipoles and the actual minimum-image COM vector,
  aligns that vector to +x, then replaces only its magnitude by 10 Å. This is not
  a recovered author operation or merely substituting laboratory +x for the vector.

## 9. Conformation-to-pair aggregation

- **Published / DIRECTLY OBSERVED:** Statistical averaging over MD conformations.
  [M p. 8; Extended Data Fig. 3, p. 14.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** Fig. 9 has 1,000 validation rows per
  coupling; Fig. 1d supplies 34 positive, largely unlabelled pair-score points.
  Neither gives a pair-indexed 1,000-snapshot-to-score join.
- **Unresolved:** Signed mean, mean absolute value, absolute signed mean, RMS,
  weights, missing-frame policy, and the remaining pair scores.
- **Consequence / REIMPLEMENTATION CHOICE:** Report all four equally weighted
  candidate summaries and their ranking sensitivity. Do not designate an author rule.

## 10. Coupling screening

- **Published / DIRECTLY OBSERVED:** Seven selected identities are in S Table 3
  (pp. 77–78); CAT50/PS41 was not synthesized. M Fig. 1d uses positive logarithmic axes.
- **Recoverable / COMPUTED FROM RELEASED DATA:** The probe `J > 50 AND J* > 0.01`
  selects seven of the 34 points, but nearby conditional threshold intervals yield
  the same count. Six selected numerical-row identities remain unresolved.
- **Unresolved:** Exact author thresholds, full 180 score/rank table, and mapping
  beyond the strongly inferred CAT1/PS1 star. Initial-seven versus measured-six
  marker/caption discrepancies remain documented in the methods audit.
- **Consequence / REIMPLEMENTATION CHOICE:** Compare known identity-set enrichment
  and ranking sensitivity; a seven-point count match does not recover the author classifier.

## 11. Experimental validation

- **Published / DIRECTLY OBSERVED:** Six measured filtered systems and 37 ruled-out
  systems; reported precision 100% and recall about 86%. [M p. 3; S Table 3.]
- **Recoverable / COMPUTED FROM RELEASED DATA:** All 43 measured identities agree
  between Table 3 and Fig. 1e. Conditional on `TON_CO > 1370 AND selectivity > 72%`,
  TP/FP/FN/TN = 6/0/1/36. The rule is compatible and non-unique.
- **Unresolved:** Prespecified experimental-good rule, untested-system outcomes,
  and the SI PS33/PS34 condition-study classification inconsistency.
- **Consequence:** Preserve measured versus unsynthesized membership. These tested-set
  statistics do not establish recall across all 180 or 3,444 systems and do not
  scientifically validate a newly generated ranking.
