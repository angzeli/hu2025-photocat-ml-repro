# OPTIONAL FULL COMPUTATIONAL REPRODUCTION

Status: optional design only; outside the current zero-new-scientific-compute scope.
No plan in this file has been executed. Phase 2 reproduces released ML metrics,
vector errors, coupling-error propagation and screening arithmetic without MD/QM,
TDDFT or training; see [the current scope](ZERO_COMPUTE_ML_REPRODUCTION.md).
This retained extension would independently regenerate physical inputs and models,
not recover the undisclosed author training run. Settings and stop conditions remain
in [the contract](REIMPLEMENTATION_CONTRACT.md) and
[configuration](../configs/reimplementation_v1.yaml). It is not the default next task.

## Pilot before either full path

**REIMPLEMENTATION CHOICE:** Use CAT1/PS1 (known selected anchor) and CAT61/PS33
(known ruled-out experimental success). Both are in the retained 180. These are
deliberately contrasting provenance checks, not an unbiased benchmark. They are
candidates pending verified structures, atom identities, charge/spin and parameters;
do not silently substitute a different pair if either cannot be admitted.

1. Implement local-only run manifests and dry-run MD/QM input generation. Reconcile
   molecular boundaries, atom IDs, coordinate units, bonds, counterions, charge/spin,
   UFF metal parameters, solvent treatment and candidate TD-root policy. Record the
   source of each decision and validate frames/translation laws with synthetic cases.
2. After explicit launch authorization, run at most two independent short trajectories:
   each 10 ps equilibration plus 0.4 ps sampled at 10.1, 10.2, 10.3 and 10.4 ps.
   Use the published 298 K, 1 fs and 50 Å periodic cube where the input gates permit.
   Four adjacent snapshots test data plumbing and state stability; they are not a
   decorrelated label set or a replacement for the 110 ps full trajectory.
3. Extract eight paired snapshots, yielding at most 16 molecule-geometry records.
   Plan one intrinsic-dipole SCF job and one transition calculation per record:
   at most 32 QM job attempts, including retries and any pilot sensitivity jobs.
   If one program job supplies both outputs, the count may be lower. Root requests
   within one TD job do not create additional geometry records. Exhausting the cap
   stops the pilot; no automatic resubmission or root/spin/solvent grid expansion.
4. Initially allow one job at a time, at most 4 CPU cores and 8 GiB memory per job,
   30 minutes per MD attempt and 4 hours per QM attempt. These are proposed ceilings,
   not measured costs or a reservation. Confirm available resources before launch;
   a resource cap is never an instruction to converge by weakening physical settings.
5. Validate dynamics completion, finite energies, whole-molecule integrity and
   intended coordination; separately validate normal QM termination, SCF state,
   root tracking, charge/spin, dipole origin/frame, and geometry identity. Preserve
   failed attempts and distinguish technical termination from scientific acceptance.
6. Fix transition phases against reference vectors in aligned molecular feature
   frames, then restore dipoles to one common pair frame. Recombine using the actual
   minimum-image COM displacement. For the standardized branch, apply one common
   proper rotation to both dipoles and the displacement to align it to +x, then
   replace only its magnitude by 10 Å. Check that the standardized coupling equals
   the actual coupling times `(|r| / 10 Å)^3`; common transverse rotations must not
   change it. Report all four aggregation operations descriptively. Do not
   train a neural network, rank the 180 systems, or claim screening quality from this
   small, temporally correlated plumbing pilot.

Pilot acceptance is a reviewable end-to-end lineage from original identity through
new snapshot, feature frame, electronic state and physical coupling, within the caps.
A blocked parameter, ambiguous state/root, invalid geometry or cap overrun stops the
affected path. Only after review should a separate task authorize extended sampling,
label counts, training and sensitivity costs.

## Minimal algorithm reproduction

**REIMPLEMENTATION CHOICE:** Reuse the released first-screen descriptor values
locally and start with the 180 identities already reconstructed. Preserve the source
descriptor provenance; do not call those descriptors independently recalculated.

After an accepted pilot and a separately approved compute budget:

1. Generate independent 110 ps trajectories for the 180 retained pairs and retain
   exactly 1,000 post-equilibration snapshots per pair with identity/time lineage.
   Stage pair batches; failed pairs remain explicitly incomplete.
2. Grow a bounded labelled set toward 1,000 CAT and 1,000 PS molecular records with
   reviewed chemistry coverage. Keep each selected geometry, electronic state, vector
   origin/frame and split key. Separate molecular selection does not imply original
   author pair joins. Pilot labels may be retained as identified records only if the
   final sampling design admits their selection without leakage.
3. Train four independent vector regressors under the frozen default and bounded
   validation sensitivities. Preserve outer 900/100 and inner 810/90 membership;
   split by temporal groups to reduce within-block mixing across splits. Boundary
   dependence remains; evaluate identity and independent-trajectory holdouts separately.
4. Predict both dipole families, invert preprocessing and molecular rotations, and
   calculate signed J/J* with physical constants. Keep actual COM and the common-
   rotation x/10 Å standardization separate; the latter changes distance after
   preserving dipole orientation relative to the pair vector. It is an independent
   choice, not a recovered author geometry operation.
5. Evaluate all four conformation-to-pair aggregations and their ranking/Pareto
   sensitivity. Compare enrichment of the seven known selected identities and the
   known experimental exception. Treat `50/0.01` as a compatibility probe only.
6. Report coverage, uncertainty and failed/untested identities. The source's 34
   largely unlabelled scores cannot validate a complete numerical 180-system ranking.
   Experimental agreement on the tested subset is not evidence of universal recall.

A timing/accuracy review after the pilot sets batch size and the maximum next-stage
label budget. The 180-system target is not a standing authorization to launch it.

## Full end-to-end reproduction

This path additionally recomputes all 84 catalyst CO₂ adsorption descriptors and
all 41 photosensitizer lifetime descriptors before performing the downstream stages.

**DIRECTLY OBSERVED, UNRESOLVED:** The printed adsorption expression contains
`+ E_cat`. Before energy calculations, establish the intended equation, optimized
fragments/complex reference states, spin/charge, solvation, basis/ECP treatment and
whether corrections belong to the reported descriptor. A conventional subtraction
may be evaluated only as an explicitly independent alternate definition; it must
not be presented as a correction proven from the paper.

For lifetimes, first extract and freeze the stated state/rate expression, emissive
state, energy/oscillator or transition inputs, radiative/nonradiative assumptions,
solvent and units from the primary Methods/SI. Method-level ωB97XD/PCM disclosure
alone is insufficient to implement a defensible lifetime calculation. Missing rate
and state conventions remain blockers, not implicit software defaults.

Start descriptor validation with the two pilot CAT identities and two pilot PS
identities, after the definition gates are resolved and a separate budget is approved.
Compare against released values locally, keeping energy-reference and unit changes
explicit. Only then scale to 84 + 41 descriptors. Apply the strict published cutoffs
to the new values and report changed retained membership; do not force agreement
with the original 18 × 10 set. A changed retained universe creates a separately
identified downstream study.

## Smallest next task

Implement only the pilot identity/state manifest, local-only run layout, synthetic
geometry/frame checks and dry-run MD/QM input generation for the two named pairs.
Produce a blocker list and a concrete 32-attempt-or-smaller job plan. Require verified
charge/spin, topology/UFF parameters and solvent/root assignments in each generated
input. Do not launch MD/QM, train models, or generate production trajectories in that task.
