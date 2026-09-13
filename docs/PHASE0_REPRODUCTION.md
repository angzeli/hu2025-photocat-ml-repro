# Rerunning the Phase-0 audit

Run from the repository root with the supplied files at the exact path `orginal/`.
A Git clone does not include them. Never copy inputs into tracked directories.
Python 3.12.14, NumPy 2.3.5, openpyxl 3.1.5 and pypdf 6.10.0 were used from the
existing Codex bundled runtime. No dependencies were installed or changed. The
scripts use standard-library facilities in addition to those three libraries;
there is no ML framework requirement.

Validation used the existing bundled Python interpreter with the versions above.
The commands below use `python3` as shorthand for an interpreter with those libraries.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 forensics/scripts/inventory_original_files.py
python3 forensics/scripts/inspect_coordinates.py
python3 forensics/scripts/inspect_workbooks.py
python3 forensics/scripts/analyze_ml.py
python3 forensics/scripts/audit_paper_evidence.py
python3 forensics/scripts/analyze_screening.py
python3 forensics/scripts/analyze_aggregation.py
python3 forensics/scripts/validate_phase0.py
```

The ordering matters: `analyze_ml.py` reads workbook metadata when writing its
report; validation reads manifests and screening outputs. Every numerical result
and source summary is regenerated from local inputs. The main report, matrix,
structure report and methods report are curated interpretations; a future changed
input requires re-reviewing them rather than treating prose as automatically updated.
The publisher-package map is curated metadata captured from the linked publisher page.

The manifest records each source's path, size, hash, type and role. The coordinate
script validates every atom record and endpoint grid. The workbook script inspects
all XML/relationships, shared strings and worksheet metadata. ML analysis emits
per-component/pooled metrics and algebraic ordering tests. The PDF script independently
checks indexed SI descriptor/experimental tables. Screening and aggregation scripts
produce classifications and explicitly conditional numerical probes.

## Output boundary and provenance

| Output | Provenance and interpretation |
|---|---|
| `data/manifests/original-files.csv` | Every file under `orginal/`; metadata and SHA-256 only |
| `data/manifests/original-summary.json` | Counts/types/parseability/duplicate summary |
| `data/manifests/publisher-packages.csv` | Publisher page links, labels and local package presence, captured 2026-09-13 |
| `forensics/outputs/structure_metadata.csv` | Per-file counts/composition/order hashes and computed summaries; no coordinates |
| `forensics/outputs/structure_summary.json` | Endpoint/grid/schema aggregate audit |
| `forensics/outputs/workbook_audit.json` | All65 sheets and package metadata; no numeric table dumps |
| `data/derived/retained_*.csv`, `candidate_180.csv` | Decisions/ID Cartesian product from D Figs.1/2; SI IDs corroborated |
| `data/derived/ml_metrics.csv` |32 independent per-component/pooled metric records from D Figs.5–8 |
| `data/derived/supfig9_coupling_metrics.csv` | Two independent metric/sign/range summaries from D Fig.9 |
| `forensics/outputs/ml_analysis.json` | Metric definitions, ranges, tensor scale, residual/control summaries |
| `data/derived/fig1d_classification.csv` | F Fig.1d ranks and hypothetical50/0.01 cutoff decisions; no original score table |
| `data/derived/selected_systems.csv` | Seven selected identities from SI Table3; exact set membership, not point order |
| `data/derived/fig1d_identity_mapping.csv` | One high-confidence star mapping plus six unresolved points |
| `data/derived/fig1e_validation.csv` |43 identity/group/conditional-outcome classifications; no source TON/selectivity columns |
| `data/derived/validation_sensitivity.csv` | Confusion counts under three assumed definitions of good performance |
| `data/derived/aggregation_probes.csv` | Four operations on validation arrays; not pair-level MD averages |
| `forensics/outputs/screening_analysis.json` | Descriptor/count/range/threshold-identifiability summaries |
| `forensics/outputs/paper_table_checks.json` | Independent PDF/workbook concordance and outcome counts |
| `forensics/outputs/publisher_comparison.json` | Optional local/publisher all-cell comparison, hashes and metadata |
| `forensics/outputs/final_validation.json` | Source immutability and staged/history exclusion evidence from final preparation |

**D** is `41929_2025_1291_MOESM2_ESM.xlsx`; **F** is
`41929_2025_1291_MOESM11_ESM.xlsx`. Exact sheets/cell ranges are in the main and
workbook reports. The full numerical extractions written by ML/screening scripts
live exclusively under ignored `forensics/local_only/`. They remain source-derived
evidence and must never be staged or distributed.

## Optional publisher-copy comparison

Two temporary publisher workbooks were retrieved because local pre-task re-save
metadata was detected. Their URLs and hashes are preserved in the comparison output.
The originals under `orginal/` were not replaced. To repeat the comparison after
obtaining those downloads in temporary or ignored storage:

```sh
python3 forensics/scripts/compare_publisher_workbooks.py \
  --pair orginal/41929_2025_1291_MOESM2_ESM.xlsx forensics/local_only/publisher-MOESM2.xlsx \
  --pair orginal/41929_2025_1291_MOESM11_ESM.xlsx forensics/local_only/publisher-MOESM11.xlsx
```

No script fetches data, trains a model, simulates structures or changes Git state.
The optional comparison requires those extra local files; temporary storage is not
a persistent dataset dependency for the core audit. It compares cell content and
the documented structural fields, not every formatting attribute or binary print setting.

## Integrity and commit verification

The task's initial baseline was captured in temporary local storage before analysis.
It contains metadata/hashes only. To check both initial timestamps and content,
place a local copy at the ignored example path used below:

```sh
python3 forensics/scripts/validate_phase0.py \
  --baseline forensics/local_only/phase0-before.json
```

Without that option, validation compares the current source set/sizes/hashes with
the committed manifest. It checks the index and reachable historical blobs, not
just the current working tree. Run it before committing and after any new commit.
Review staged contents manually as well: source data converted to another text
format will not have the same hash as the original workbook.

Expected numerical controls include18/10/180 retained counts,34 plotted pairs,
7 hypothetical coupling passes,43 measured systems, and one conditional false
negative. SI/table checks independently corroborate identity order and all measured
validation rows. Negative ordering controls support the algebraic alignment result.
No new neural-network generalization test or physical calculation is claimed.
