# Hu et al. 2025 photocatalysis ML reproduction

Independent reproduction and forensic reimplementation project for Hu et al.,
“Identifying a highly efficient molecular photocatalytic CO₂ reduction system via
descriptor-based high-throughput screening”, *Nature Catalysis* **8**, 126–136
(2025). [Original article and DOI](https://doi.org/10.1038/s41929-025-01291-z).

**Phase 0 is complete; Phase 1 reconstructs and freezes the algorithm.** The
descriptor screen, released prediction statistics and validation coupling tensor
have been reconstructed. No production MD, DFT/QM calculation or neural-network
training has run. Exact author-model reproduction remains impossible because the
original inputs, weights and complete settings are unavailable; independent
scientific algorithm reproduction is the project target.

## Local evidence and redistribution boundary

`orginal/` is the existing, deliberately preserved spelling. Its contents are
immutable, local-only publisher/author evidence. Original supplementary and source
files remain copyrighted by their respective rights holders and are retained only
insofar as appropriate for this research workflow. They are not distributed in
this Git repository, regardless of size or potential licence permissions.

Do not force-add, use Git LFS, relocate or convert source files to bypass exclusion.
Full numeric extractions also remain local in ignored `forensics/local_only/`.
Tracked material is limited to metadata, hashes, scripts, reconstructed candidate
IDs, computed metrics and forensic reports. A clone alone does not include inputs.

## Contents

- `orginal/`: immutable downloaded evidence, ignored.
- `data/manifests/`: file hashes, package roles and publisher links.
- `data/derived/`: reconstructed IDs, numerical metrics and classification audits.
- `forensics/scripts/`: bounded deterministic forensic analyses.
- `forensics/outputs/`: metadata and computed audit summaries.
- `forensics/reports/`: evidence reports and reproducibility matrix.
- `forensics/local_only/`: complete numeric extractions, ignored and never distributable.
- `docs/`: algorithm specification, independent contract, compute plan and provenance.
- `configs/`: explicit future-compute settings and unresolved inputs; no launch authority.
- `src/hu2025_repro/`: physical dipole-coupling and aggregation functions.
- `tests/`: entirely synthetic coupling checks.

Start with [Phase-0 data forensics](forensics/reports/PHASE0_DATA_FORENSICS.md),
the [reproducibility matrix](forensics/reports/REPRODUCIBILITY_MATRIX.md), and
[rerun instructions](docs/PHASE0_REPRODUCTION.md).

Phase 1: [coupling reconstruction](forensics/reports/PHASE1_COUPLING_RECONSTRUCTION.md),
[algorithm specification](docs/ALGORITHM_SPEC.md),
[authoritative reimplementation contract](docs/REIMPLEMENTATION_CONTRACT.md),
[configuration](configs/reimplementation_v1.yaml), and [future compute plan](docs/COMPUTE_PLAN.md).
The near-10 Å Debye/cm⁻¹ interpretation is conditional and not uniquely identified.
The next task is pilot input preparation and dry-run validation; chemistry, state,
parameter and launch gates remain. Neither phase establishes end-to-end reproduction
or scientific validation of the paper's model.
