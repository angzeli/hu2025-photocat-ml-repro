# Independent reimplementation contract v1

This is the authoritative contract for future Phase 2+ implementation. It freezes
evidence, explicit independent defaults, bounded sensitivities, and stop conditions;
it does not authorize calculation launch. The [configuration](../configs/reimplementation_v1.yaml)
mirrors the numerical defaults. The [algorithm specification](ALGORITHM_SPEC.md)
preserves source inconsistencies; the [compute plan](COMPUTE_PLAN.md) defines staged scope.

All publisher/source files, full extracts and source-derived coordinates remain
local-only under `orginal/` or `forensics/local_only/`. Future raw scientific inputs,
trajectories, labels and outputs must use a separately designated ignored run root
before generation. Tracked outputs contain code, contracts and compact summaries.

## A. Paper-defined — DIRECTLY OBSERVED

Source anchors are in the [methods audit](../forensics/reports/PAPER_METHODS_AUDIT.md).

| Setting | Published constraint | Boundaries of disclosure |
|---|---|---|
| Universe | 84 CAT × 41 PS | Identities require reviewed chemistry metadata before new inputs |
| Pre-screen | `E_ad < -0.20 eV`; lifetime `> 90 ns` | Adsorption equation prints a catalyst-energy plus sign; unresolved |
| Retained combinations | 18 CAT × 10 PS = 180 | Reusing descriptors is the minimal path |
| MD ensemble/thermostat | NVT; Nosé–Hoover | Relaxation time/chain and engine absent |
| MD temperature/timestep | 298 K; 1 fs | Integrator and constraints absent |
| MD cell | Cubic 5 nm, periodic | One CAT, one PS, counterions; topology/charges absent |
| Force field/cutoff | UFF family; 12.5 Å LJ and Coulomb cutoff | Typing, parameters and boundary treatments incomplete |
| MD duration | 110 ps total, first 10 ps equilibration | Snapshot endpoints and original seeds absent |
| Sampling | 0.1 ps interval; 1,000 per retained pair | Frame/sample IDs absent |
| Label selection | 1,000 CAT + 1,000 PS sampled separately | Schematic's paired-conformation accounting differs |
| QM software/method | Gaussian 16; ωB97XD | Revision and executable input options absent |
| Basis/ECP | LANL2DZ for transition metals; 6-31G(d) for other atoms | Exact atom-to-basis/ECP map must be explicit |
| Solvation | PCM; water/acetonitrile described | Per-stage solvent assignment and PCM options incomplete |
| PS label species | Reduced PS | Parent charge, multiplicity and root mapping absent |
| NN implementation | TensorFlow/Keras | Versions unavailable |
| Hidden structure | Two hidden ReLU layers; widths 256/512/1024 considered | Final per-layer widths and model count ambiguous |
| Training | L1; Adam; learning rate `1e-4` | Penalty, loss and other optimizer/training options absent |
| Split/output | 900/100; Cartesian dipoles | Original geometry/split key and grouping absent |
| Coupling/aggregation | Dipole tensor using COM displacement; statistical average | Units, scalar convention and averaging operation unspecified |

## B. Forensically reconstructed

**COMPUTED FROM RELEASED DATA:** The first-screen identities and 900/100 dipole
blocks are recoverable. One scalar applied to `(-2,+1,+1)` component products
nearly recovers calculated/predicted intrinsic/transition couplings in released
row order. The scalar is fit only on the first 900 calculated intrinsic rows;
the final 100 and other channels are evaluation data, not refitting opportunities.

The [Phase-1 reconstruction report](../forensics/reports/PHASE1_COUPLING_RECONSTRUCTION.md)
and [compact analytical output](../forensics/outputs/phase1_coupling.json)
are authoritative for the independently estimated scalar, orientation tests,
conversion constants, effective-distance inference, and rounding limitations.
The fitted scalar is a forensic statistic; physical production code must compute
its prefactor from constants and declared units, never calibrate it to source labels.

**COMPUTED FROM RELEASED DATA:** The independent scalar is `5.034063649307054`.
The physical prefactor for Debye dipoles and Å displacement is
`5034.116566872031 cm⁻¹` at a unit component product and 1 Å separation. Under that
unit convention and vacuum screening, the fitted scalar implies
`r_eff = 10.00003503953813 Å`, an excess of `0.00003503953813 Å` over 10 Å
(relative `0.000003503953813`). The near-10 Å value is a **STRONG INFERENCE** about
the validation transform, not a directly documented author geometry. Exact 10 Å
with modern constants lies outside the conditional uniform-five-decimal rounding
interval reported in Phase 1; it must not be described as exact physical recovery.
The empirical scalar and the physical 10.0 Å implementation are distinct objects.

Other unit/distance combinations remain possible: for example, meV coupling with
Debye dipoles gives a separation near 5 Å. The Debye/cm⁻¹/near-10 Å interpretation
is a particularly natural candidate, not uniquely identifiable from one scalar.
The favored separation axis is unique among x/y/z under fixed column meanings;
its sign, transverse-axis relabellings and equivalent common frame rotations are
not identifiable from the diagonal tensor.

**STRONG INFERENCE:** Numerical row correspondence is strong within the intrinsic
pair and within the transition pair. Shared physical geometry across all four
targets remains unproven. The validation-array transform does not identify an MD
distance distribution, pair-level aggregation, or the authors' exact input frame.

## C. Reimplementation choices

Every setting below is a **REIMPLEMENTATION CHOICE**, never an author setting.
`unresolved` means a required manifest or bounded comparison must resolve the value
before the affected calculation is runnable. A bounded set is not permission to
launch its Cartesian product. Sensitivities are sequential, one factor at a time,
and subject to an explicit compute budget.

### Identity, states and MD

| Missing setting | v1 default or bounded resolution | Planned sensitivity / decision test |
|---|---|---|
| Molecular identity, bonds, atom IDs | Source-backed reviewed manifest; persist source atom indices; no geometry-only charge/spin inference | Check metal coordination, valence, counterion identity, atom counts and identical-ID endpoint correspondence |
| Coordinate units / PBC | Convert verified length units to Å; reconstruct whole molecules by reviewed bonds; minimum-image COM displacement in 50 Å cube | Test wrapping invariance and absence of broken molecules before dynamics |
| MD engine | LAMMPS candidate; exact installed version and compatible UFF implementation must be recorded before execution | OpenMM is an alternative only after identical parameter/energy conventions are established; no automatic fallback |
| UFF parameters / charges | `unresolved`; explicit atom/bond/angle/torsion/nonbonded records and source provenance required, including metal typing | Reject unsupported parameters; compare small distorted-geometry energies/forces with parameterization reference |
| Contents / solvent | One CAT + one PS + identified counterions, no explicit solvent as independent baseline | If source clarification requires solvent, revise topology and budget before adding it |
| Thermostat / integration | Nosé–Hoover chain length 3, damping 0.1 ps, velocity Verlet, no bond constraints | Damping 1.0 ps and timestep 0.5 fs after baseline numerical stability is established |
| Initial velocities | Maxwell–Boltzmann at 298 K; remove total COM momentum; seed 2025 | Seeds 2026 and 2027 on the same admitted pilot only |
| Cutoff treatment | Energy-shifted LJ and truncated Coulomb at 12.5 Å; no undocumented dielectric multiplier | Compare a declared long-range-electrostatics variant later; it changes the independent model and is not an author setting |
| Full-run snapshots | `10.1 + 0.1*k ps`, `k=0..999`; retain all complete frames | Temporal block/autocorrelation checks; no independence claim from interval alone |
| Failed trajectories | Stop the affected pair; preserve attempt and failure; no silent replacement or dropped-frame mean | A revised input/attempt gets a new identity and consumes the same authorized budget |

### QM labels and molecular frames

| Missing setting | v1 default or bounded resolution | Planned sensitivity / decision test |
|---|---|---|
| Geometry used for labels | Single points on extracted whole-molecule snapshots; do not optimize away the sampled conformation | Two explicitly tagged relaxed-geometry comparisons only after a later budget is approved |
| Charge and spin | Required per-species/state manifest. Reduced PS has one additional electron relative to its verified parent; actual integer charge and multiplicity remain `unresolved` | Compare only chemically justified source-backed spin candidates; never assign singlet/doublet from geometry or naming alone |
| PCM solvent | Bounded candidates water/acetonitrile; per-stage assignment unresolved | Compare the two only for the same validated geometry/state; do not assume a mixed-solvent dielectric |
| Transition target/root | Root identity unresolved; request lowest 5 admissible roots for the verified spin/reference treatment; track state character across frames | Compare lowest-energy admissible state and lowest bright state (oscillator strength `>= 1e-3`); crossings/no qualifying root stop automatic selection |
| Transition sign/phase | Evaluate overlaps with a fixed reference transition vector in aligned molecular feature frames within a tracked state; fix phase there before restoring the common pair frame; flag near-zero overlap | Check overlap continuity; signed mean and absolute signed mean can change under local sign flips; mean absolute and RMS cannot |
| SCF/grid details | Candidate tight SCF and ultrafine integration grid; record resolved program settings | Tighter thresholds/finer grid on one admitted geometry; normal termination alone does not validate state or root |
| Quantum program | Gaussian 16 baseline from paper; availability/licence/revision unresolved | ORCA would be an explicitly versioned method translation with independent basis/ECP/PCM checks, never assumed equivalent |
| Intrinsic dipole origin | Molecular COM origin for every state, including charged CAT/reduced PS; store original program origin and net charge | Verify translation law and identical physical coupling after consistent frame operations; charged dipoles are origin-dependent |
| Coordinate frame | Right-handed molecular frame fixed by metal plus two manifest-selected, non-collinear ligand anchors; store forward/inverse rotations per snapshot | Compare a whole-molecule rigid-fit frame. Reject collinear anchors; never rotate features without rotating target vectors |

For a translation of origin by `a` and active frame rotation `R`, transform a
charged intrinsic dipole as `mu_new = R (mu_old - Q*a)`, with `Q*a` converted to
the same dipole units. Transition dipoles between orthogonal states do not acquire
the `Q*a` origin term. The physical pair calculation uses COM-origin dipoles in one
common pair frame: undo each molecule's feature-frame rotation before evaluating
the tensor, and rotate the displacement consistently. Coordinate transforms,
charges, centres, units and rotations belong to the geometry–label lineage.
For charged species, this API evaluates the defined dipole–dipole term; it is not
the complete electrostatic interaction including monopole and other multipole terms.

### Features, splits and training

| Missing setting | v1 default or bounded resolution | Planned sensitivity / decision test |
|---|---|---|
| Atom selection | Metal + first bonded coordination shell from reviewed topology, fixed over each trajectory | Include a second bonded shell; exact maximum slot count is frozen from admitted identities before training |
| Atom ordering / species encoding | Metal first, other selected atoms by immutable manifest index; pad to species-family maximum with mask; add element one-hot channels | Compare topology-canonical ordering; never reorder independently per snapshot by fluctuating distance |
| Centering / frame | Feature coordinates metal-centred in the molecular frame above; labels COM-origin and rotated into that frame | Compare COM-centred features using identical target origins and recorded transforms |
| Normalization | Fit per-feature mean/std on training rows only; zero-variance scale = 1; padded coordinates remain zero and mask is unscaled | Unscaled coordinates as one-factor control; categorical channels stay unscaled |
| Target scaling | Per-component mean/std from training only; invert before physical coupling; zero-variance scale = 1 | No target scaling as one-factor control |
| Model count / grouping | Four independent three-output regressors: CAT/PS × intrinsic/transition; linear output | Two species models with six outputs each |
| Widths | Two layers `(256,256)` | `(512,512)` and `(1024,1024)`; select on validation only |
| L1 | `1e-6 * sum(abs(hidden kernels))`; exclude biases/output layer | Coefficients `0`, `1e-7`, `1e-5` |
| Loss | Mean squared error averaged over samples and three standardized components, plus the declared L1 term | Mean absolute error with otherwise identical scaling |
| Adam / learning rate | `1e-4`, beta1 0.9, beta2 0.999, epsilon `1e-7`, AMSGrad false; constant rate | No schedule search in v1 |
| Initialization / precision | He-normal hidden kernels, Glorot-uniform output kernel, zero biases; float32 NN, float64 coupling | Float64 training on a small fixed subset only if numerical instability is observed |
| Batch / epochs | Batch 32, shuffled training batches; maximum 2,000 epochs | Batch 16/64; epoch ceiling is a cap, not a target |
| Early stopping | Validation total objective, patience 100 epochs, minimum improvement `1e-6`, restore best weights | Patience 50/200 |
| Seed / versions | Seed 2025 for sampling, split and training with separate recorded streams; record exact TensorFlow/Keras and environment versions before launch | Seeds 2026/2027; report determinism limitations on selected hardware |
| Label sample count | Full-stage target 1,000 CAT + 1,000 PS records, independently selected but explicitly linked when paired | Balanced identity coverage versus proportional sampling; pilot is not this training dataset |
| Split | Outer 900 development / 100 untouched test per species; development 810 fit / 90 validation; common membership for that species' intrinsic/transition labels | Allocate whole fixed-size temporal blocks to reduce within-block mixing across splits; boundary dependence remains; identity and independent-trajectory holdouts are separately reported tests |

The split builder must construct compatible equal-size groups, preserve exactly
900/100 membership when claimed, and reject incompatible counts instead of breaking
groups silently. Fit scalers on the 810 fitting rows during model selection. After
selection, either retain the selected model or refit on 900 using its frozen epoch
count and recomputed development-only scalers; declare the choice before touching
the 100 test rows. v1 retains the selected model. Do not choose hyperparameters,
aggregation or thresholds to improve those test results. Report temporal dependence
and distinguish interpolation from chemistry-transfer validation.

### Coupling, aggregation and screening

| Missing setting | v1 default or bounded resolution | Planned sensitivity / decision test |
|---|---|---|
| Physical dipole/coupling units | Store own labels in Debye, coordinates/displacement in Å, coupling in cm⁻¹; preserve any program-native originals locally | Check independent conversion to J/eV/meV; this is a reimplementation representation |
| Pair displacement | Evaluate the actual minimum-image COM vector; separately rotate both dipoles and that vector by one common proper rotation aligning it to +x, then replace only its magnitude by 10 Å | Standardized distance 8/12 Å; covariance check below; no claim that this is the authors' trajectory treatment |
| Dielectric factor | Vacuum prefactor (`epsilon_r=1`); PCM-labelled dipoles do not silently add a second solvent factor | A screened model requires a separate justified dielectric choice and versioned comparison |
| Aggregation | Emit all: signed mean, mean absolute, absolute signed mean, RMS; equal snapshot weights; no single selected rule | Compare pair rank stability across all four and both distance conventions; do not infer rules from global Fig. 9 validation rows |
| Missing/nonfinite coupling | Fail that pair summary; no automatic skip, clipping or replacement | Diagnose failed frames explicitly before revised aggregation |
| Screening | Report ranks/Pareto status and known selected identity-set enrichment; `J>50 AND J*>0.01` only as a labelled compatibility probe | Explore thresholds only as descriptive sensitivity, never an identified author boundary |
| Experimental-good rule | Preserve published membership; joint `TON_CO>1370 AND selectivity>72%` is a conditional audit probe | Keep unmeasured CAT50/PS41 separate; no recall claim beyond tested identities |

For the standardized branch choose a proper orthogonal rotation `R` with
`R*r = (|r|, 0, 0)`, transform both COM-origin dipoles by that same `R`, and evaluate
the tensor at `(10 Å, 0, 0)`. Any common rotation around the resulting x-axis is
equivalent by transverse tensor invariance. Replacing only the displacement by
laboratory +x while leaving dipoles unchanged is a different operation and is not
the v1 standardization. With identical units and dielectric conventions, the planned
covariance check is `J_standardized = J_actual * (|r| / 10 Å)^3`, separately for J
and J*. This chosen geometry operation is not inferred from the released-table
tensor; released-table reconstruction continues to use the stored component frame.

## Admission and change control

Phase 2 can implement manifests, parsers, synthetic checks and dry-run input generation.
Actual pilot execution remains blocked until chemical identity/state, topology/UFF,
software availability, solvent/root choices and explicit resource/launch approval are
recorded. A contract revision is required for a scientific choice outside the bounded
sets above. Operational software versions and resolved input options must be captured
in the run manifest without credentials, host details or identifying local paths.

Scientific acceptance requires correct geometry/method/state lineage, program normal
termination, SCF convergence, intended stable electronic state and tracked transition
root, finite correctly transformed dipoles, and explicit units. Process activity or
an output file alone satisfies none of these gates. The Phase-1 synthetic coupling
checks validate the analytic implementation, not the future MD/QM/ML workflow.
