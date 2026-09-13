# What source-data ML reproduction means

The current target is to reproduce and understand the released prediction evidence
and analytic ML workflow of [Hu et al. (2025)](https://doi.org/10.1038/s41929-025-01291-z),
without regenerating the authors' geometries, quantum-chemical labels or trained
models. No new MD, QM, TDDFT, or ML training is required for this source-data scope.
Deterministic array statistics and algebra are analysis, not new scientific data
generation. They cannot replace missing evidence about training or physical validity.

## Exactly reproducible from released source data

**DIRECTLY OBSERVED / COMPUTED FROM RELEASED DATA:** The first descriptor screen,
released train/test calculated-versus-predicted dipole arrays, component metrics,
vector magnitude/direction errors, residual summaries, Fig. 9 prediction statistics,
validation-row sign/rank comparisons, and measured-set experimental arithmetic can
be evaluated independently from the released tables.

The recovered validation tensor also permits exact algebraic decomposition of
coupling prediction error into CAT-error, PS-error and bilinear cross terms, and
their Cartesian contributions. "Exact" here describes the algebra on released
vectors: reconstructing separately rounded Fig. 9 columns retains the small
Phase-1 residuals. The physical units and hidden geometry conventions remain
inferred. A final-100 coupling block is a row-order diagnostic linked to dipole
test membership; Fig. 9 does not itself label a new train/test split.

These are evaluations of supplied predictions. They do not independently regenerate
those predictions or establish that the reported test data represent unseen chemical
identities. The article itself limits model transfer to similar geometries
(article PDF p. 7); broader applicability of a protocol is a separate claim from
demonstrated model transfer. Pooling three Cartesian components does not multiply the number of
molecular conformations. Validation-row rankings are not rankings of the 180 systems.

## Algorithmically reimplemented

**DIRECTLY OBSERVED / REIMPLEMENTATION CHOICE:** The dependency-free
[architecture specification](../src/hu2025_repro/ml_architecture.py) represents the
disclosed family: configurable/unknown input dimension, two hidden ReLU layers,
candidate widths 256/512/1024, L1, three Cartesian outputs and Adam at `1e-4`.
It constructs no model, tensor, weights or optimizer. Exact selected widths, model
count, L1 coefficient/scope, output activation, loss, batch size, epochs, early
stopping, seed and preprocessing remain explicitly unknown. Caller-provided values
are recorded separately as reimplementation choices, never author facts.

The [coupling API](../src/hu2025_repro/coupling.py) implements the analytic tensor,
declared physical-unit conversions and explicit aggregation candidates. The
error-propagation analysis evaluates the bilinear identity on supplied vectors;
no model fitting or hyperparameter search is involved. Synthetic tests establish
these mathematical contracts, not the performance of an independently trained model.

Phase-1 proposed independent training defaults remain available for an optional
future study. They are not silently imported into the paper-defined architecture
family and are not necessary for the current analysis.

## Partially reproducible

**COMPUTED FROM RELEASED DATA / STRONG INFERENCE:** Fig. 1d's supplied positive
points permit a threshold-sensitivity audit and the seven-point compatibility
probe. The known selected identity set is direct evidence, while the CAT1/PS1
star's numeric-row association is a strong cross-source inference. The remaining
selected row-to-identity associations and missing retained-system scores stay
unresolved. Matching seven points is different from establishing the same seven
point members; the sensitivity output reports both.

Measured validation groups permit the authors' declared precision/recall arithmetic.
The unmeasured, unsynthesized CAT50/PS41 prediction is outside measured precision
because no observed outcome assigns it a true/false-positive status. A compatible
joint TON/selectivity probe is not a uniquely disclosed experimental-good rule.
Performance on tested identities does not establish recall over the candidate universe.

## Not reproducible from the released evidence

The original geometry matrix X and sample joins, exact feature selection/order,
preprocessing, complete hyperparameters, trained weights, exact NN training and
full prediction campaign cannot be regenerated. Neither can the full 180-system
score table or the trajectory-to-pair aggregation rule. The released endpoints do
not restore full trajectories or authenticated label inputs. Released predictions
do not independently establish wall-clock acceleration or its hardware dependence.

Generating new trajectories, labels and models would create an independent dataset
and modeling study. It would not reveal the missing author settings or prove that
the authors' weights reproduce their published outputs. Those exact-reproduction
gaps require additional author data/code or documentation, not an assumption that
more computation will reconstruct the missing provenance.

## Completion boundary

The [Phase-2 report](../forensics/reports/PHASE2_ZERO_COMPUTE_ML_REPRODUCTION.md)
and [claim scorecard](../forensics/reports/ML_CLAIM_SCORECARD.md) state computed
findings and their limits. The [screening summary](../forensics/outputs/phase2_screening.json)
and [threshold grid](../data/derived/screening_sensitivity.csv) contain compact
analysis, with no full source coordinates or measurement columns.

Completion means the released ML results and algebra are independently checked,
error channels and screening ambiguity are quantified, and irreducible unknowns
remain explicit. This goal has no scientific need for new MD/DFT/TDDFT or training.
Testing physical generalization, independently regenerating labels, or measuring
end-to-end computational cost would be different questions. The preserved
[compute plan](COMPUTE_PLAN.md) is optional full computational reproduction,
not an unmet requirement of this source-data ML study.

Source files remain immutable under `orginal/`; complete extractions remain ignored
and local-only. Tracked outputs are code, formulas, aggregate metrics, limited identity
metadata and derived analysis. No source redistribution is authorized.

## Rerun this phase

From the repository root, use Python with NumPy, openpyxl and pypdf. The existing
bundled runtime used for earlier phases is sufficient; SciPy, TensorFlow and plotting
frameworks are not required. Full workbook/PDF inputs must already be present under
the ignored source root. The scripts read them without saving source changes and
write only the named compact CSV/JSON summaries.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 forensics/scripts/analyze_ml_vectors.py
PYTHONDONTWRITEBYTECODE=1 python3 forensics/scripts/analyze_error_propagation.py
PYTHONDONTWRITEBYTECODE=1 python3 forensics/scripts/analyze_screening_sensitivity.py
```

The first script independently compares scalar metrics with Phase 0. The second
uses the frozen Phase-1 scalar without refitting and checks exact error closure.
The third verifies screening intervals and SI/workbook experimental correspondence.
Synthetic tests require only NumPy and the standard library. No training command,
model builder or compute-submission entry point is provided. Curated reports require
review if source inputs or numerical definitions change; rerunning summaries alone
does not automatically update their scientific interpretation.
