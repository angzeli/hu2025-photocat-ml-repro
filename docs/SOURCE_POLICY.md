# Source handling and Git boundary

All publisher/author original files, their copies and lossless extractions are
local-only evidence. The exclusion applies independent of file size and licence.
`orginal/` is immutable and must retain its spelling. Nothing in this Phase-0 task
authorizes a push, tag, release, LFS migration or history rewrite.

Tracked candidates are independently reconstructed ID combinations. Tracked
classification tables contain row locators, ranks and decisions; they omit the
complete original Fig. 1 coordinates and experimental measurements. Complete
descriptor, dipole, coupling and Fig. 1 extracts belong only in ignored
`forensics/local_only/`. A converted CSV is still source evidence when it reproduces
the source table. Hashes, sheet names, file sizes, structural counts and genuinely
computed statistics are permitted metadata or analysis.

Every local source was hashed and its size and modification time recorded before
analysis. Final validation compares these against both the file manifest and the
initial snapshot. The initial snapshot is temporary; the committed validation
record reports the result without embedding original content. Publisher comparison
copies and HTML obtained to resolve provenance questions remain in temporary local
storage and are never added to Git.

Before committing, inspect the exact staged paths, sizes, content and existing
history. The source guard checks tracked and staged paths, all reachable historical
blobs, excluded file types, exact matches to original file hashes, and LFS rules.
Manual content review is also required because a hash comparison alone cannot detect
a renamed table that has been reformatted. If original files are already committed,
stop and report the affected history; do not silently rewrite it.

Initial repository state on 2026-09-13: no `.git/`, no local history or index, and no
remote refs returned by read-only inspection of the requested GitHub URL. Therefore
there was no pre-existing tracked or committed source exposure. The largest original
is 11,898,869 bytes; none exceed 100 MiB. All remain excluded under the stricter user
policy. File size is not permission to redistribute them.
