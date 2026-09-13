# Phase-1 first-publication audit

Date: 2026-09-13. This record distinguishes the commits proposed for publication
from local application snapshots. The public destination is
[angzeli/hu2025-photocat-ml-repro](https://github.com/angzeli/hu2025-photocat-ml-repro).
The user authorized a normal first push of `main`, conditional on source/privacy checks.

## Authorized sanitization

Initial HEAD was `994778306d61d774ad08137c0bfce87e005e1552`; its unchanged parent
is `accb925f374f31fed6f8c6943933136dbecb684d`. Private filesystem examples in two
Phase-0 documents triggered a stop before publication. The user then explicitly
authorized sanitizing those documents and rewriting only the latest unpushed commit.

The resulting replacement commit is `bf130ce19c68afd4415bd15fce1ebf44d3433a6e`.
Only `docs/PHASE0_REPRODUCTION.md` and `forensics/reports/PAPER_METHODS_AUDIT.md`
differ from the replaced commit. Machine-specific interpreter and temporary-storage
examples became portable descriptions or ignored repo-relative examples. Scientific
results, method disclosures, limitations and the parent commit were preserved.
No older commit, branch, remote or local application snapshot was rewritten.

## Privacy and source scope

[audit_publication.py](../scripts/audit_publication.py) checks every reachable
commit's metadata and complete file tree, deduplicated blob contents, index contents,
and tracked/nonignored proposed working files. Per-tree path checks cover aliases
of the same blob at different historical paths. The index and working copies are
checked separately. Findings use locations/categories without echoing matched values.

The precommit history scan covered two commits, 40 unique commit-reachable blobs
and 43 committed file-path occurrences; it found no sensitive or forbidden source
content. The final publication gate additionally covers this audit record and the
complete staged Phase-1 change, then rechecks the new commit before pushing.

One Git author/committer email was retained as intentionally public project metadata.
It was independently corroborated in the author and committer records of this
[existing public project commit](https://github.com/angzeli/computational-modelling-workflow/commit/8edee088b5f42bb00d9a4104849086011ad6a51f).
No other email exception was granted. Runtime private-identifier scan arguments and
local audit logs are not included in the repository.

Checks combine credential/header/cookie/URL/key patterns, private path/network/identity
patterns, filename and extension rules, original-file hash comparison, archive/PDF/LFS
signatures, full-table/coordinate heuristics, and manual inspection of the intended
diff and historical text. The scan is bounded evidence, not a universal proof against
every possible secret or transformed dataset. No new scanner dependency was installed.
Synthetic temporary-repository tests verified quoted JSON credentials, index-only
content, identifying filenames, historical forbidden paths sharing one blob, and
separate treatment of unchanged auxiliary refs.

## Local auxiliary snapshots are not published history

Codex retained non-commit tree references to the pre-sanitization documents. Their
two extra historical document blobs produced seven redacted private-path/identifier
findings in the local auxiliary scope. These snapshots were inspected and left intact;
they are outside the amended commit ancestry. Thus this audit does **not** claim
that every local Git object has been sanitized.

The publication operation is explicitly `git push -u origin main`, never a mirror,
all-ref or force push. Only objects needed by `main` are part of that publication;
local Codex snapshot refs and the superseded commit are excluded. Any future request
to publish other refs or Git internals requires a fresh audit of that scope.

## Immutable evidence boundary

All 6,901 original files (85,541,434 bytes) remain under the ignored `orginal/` root.
The pre-analysis baseline checks path set, SHA-256, size and mtime; it was verified
at Phase-1 entry and is required again at the final staged gate. Full spreadsheet
extracts and local publisher comparisons remain ignored. The coupling script reads
only the necessary workbook XML and writes aggregate analytical statistics, not
dipole, coupling, experimental-table or coordinate mirrors.

The existing [integrity/source guard](../scripts/validate_phase0.py) was extended
only to admit the requested YAML configuration extension. History/index checks
exclude source paths, exact source copies, publisher PDFs/XLSX/archives, coordinate
dumps, full numerical extracts and source LFS pointers. Ignore coverage is checked
for every original file. No LFS rule, forced add or source relocation is introduced.

## Scientific validation and publication gate

Bounded Phase-0 screening and ML reruns reproduced the 18/10/180 identity counts,
900/100 component blocks, 1,000-row coupling comparisons and prior metrics.
The independent reconstruction matched the scalar and all four channel errors.
All eight deterministic synthetic coupling tests passed. Existing Ruby/Psych parsed
the YAML configuration; scalar/distance, split counts, pilot caps and no-launch
settings agree with the reports. Independent review checked physical conventions,
rounding bounds and report-to-JSON numerical agreement. No MD, QM or NN training ran.

Publication requires a clean staged diff, passing source/privacy checks before and
after the Phase-1 commit, a fresh remote-ref read, local `main`, and an empty or
safely compatible destination. A conflicting remote history would stop the push.
After the normal push, remote `main` must equal the local Phase-1 HEAD and upstream
tracking must be established. The final task response records those observed results;
this precommit record does not predict a successful network operation or its own hash.
