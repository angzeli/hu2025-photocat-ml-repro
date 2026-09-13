# Hu et al. 2025 photocatalysis ML reproduction

Independent reproduction and forensic reimplementation project for Hu et al.,
“Identifying a highly efficient molecular photocatalytic CO₂ reduction system via
descriptor-based high-throughput screening”, *Nature Catalysis* **8**, 126–136
(2025). [Original article and DOI](https://doi.org/10.1038/s41929-025-01291-z).

Current phase: **Phase 0 — repository initialization and released-data forensics**.
The descriptor screen and released prediction statistics have been reconstructed.
The original neural-network inputs, trained models and full screening calculation
have not been reproduced. No new neural network, DFT or MD calculation has run.

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
- `docs/`: reproduction instructions and source-handling record.

Start with [Phase-0 data forensics](forensics/reports/PHASE0_DATA_FORENSICS.md),
the [reproducibility matrix](forensics/reports/REPRODUCIBILITY_MATRIX.md), and
[rerun instructions](docs/PHASE0_REPRODUCTION.md).

Phase 0 establishes what the released evidence supports; it does not establish
end-to-end reproduction or scientific validation of the paper's model.
