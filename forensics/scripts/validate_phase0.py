#!/usr/bin/env python3
"""Check Phase-0 counts, immutable evidence and source exclusion from local Git.

Run after staging the intended files and again after committing. --baseline adds
comparison to the pre-analysis JSON snapshot (path,size,mtime_ns,sha256).
No network, staging, commit, source mutation or history rewrite occurs here.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

from publication_artifacts import REVIEWED_FIGURES, allowed_path, reviewed_figure_text

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def read_csv(relative):
    with (ROOT / relative).open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output:
        destination = args.output.resolve()
        forbidden = [(ROOT / 'orginal').resolve(), (ROOT / '.git').resolve()]
        if any(destination == path or path in destination.parents for path in forbidden):
            parser.error('--output must not target immutable sources or Git internals')
        if args.baseline and destination == args.baseline.resolve():
            parser.error('--output must not overwrite the initial baseline')
    manifests = read_csv('data/manifests/original-files.csv')
    manifest = {row['relative_path']: row for row in manifests}
    current = {}
    for path in sorted((ROOT / 'orginal').rglob('*')):
        if path.is_file():
            stat = path.stat()
            current[path.relative_to(ROOT / 'orginal').as_posix()] = dict(
                size=stat.st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                mtime_ns=stat.st_mtime_ns)
    assert current.keys() == manifest.keys(), 'Original path set changed'
    for name, row in current.items():
        assert row['size'] == int(manifest[name]['byte_size']), name
        assert row['sha256'] == manifest[name]['sha256'], name
    baseline_verified = False
    if args.baseline:
        baseline = {row['path'].removeprefix('orginal/'): row
                    for row in json.loads(args.baseline.read_text())}
        assert baseline.keys() == current.keys(), 'Baseline path set changed'
        for name, row in current.items():
            assert all(row[key] == baseline[name][key] for key in ('size', 'sha256', 'mtime_ns')), name
        baseline_verified = True
    assert len(current) == 6901
    assert sum(row['size'] for row in current.values()) == 85541434
    assert len(read_csv('data/derived/retained_catalysts.csv')) == 18
    assert len(read_csv('data/derived/retained_photosensitizers.csv')) == 10
    candidates = read_csv('data/derived/candidate_180.csv')
    assert len(candidates) == len({(row['cat_id'], row['ps_id']) for row in candidates}) == 180
    fig1d = read_csv('data/derived/fig1d_classification.csv')
    fig1e = read_csv('data/derived/fig1e_validation.csv')
    assert len(fig1d) == 34 and sum(row['pass_both'] == 'True' for row in fig1d) == 7
    assert len(fig1e) == 43
    assert sum(row['author_selection_group'] == 'filtered' for row in fig1e) == 6
    assert sum(row['classification'] == 'FN' for row in fig1e) == 1
    ml = read_csv('data/derived/ml_metrics.csv')
    coupling = read_csv('data/derived/supfig9_coupling_metrics.csv')
    assert len(ml) == 32 and len(coupling) == 2
    for row in ml + coupling:
        assert all(math.isfinite(float(row[key])) for key in ('pearson_r', 'r2', 'mae', 'rmse'))
    assert all(int(row['n_samples']) == (900 if row['split'] == 'train' else 100) for row in ml)
    assert all(int(row['n_values']) == 1000 for row in coupling)
    audit = json.loads((ROOT / 'forensics/outputs/workbook_audit.json').read_text())
    assert len(audit['workbooks']) == 5
    assert sum(len(book['sheets']) for book in audit['workbooks']) == 65
    structure = json.loads((ROOT / 'forensics/outputs/structure_summary.json').read_text())
    assert structure['md_file_count'] == 6888 and structure['md_pair_count'] == 3444
    paper = json.loads((ROOT / 'forensics/outputs/paper_table_checks.json').read_text())
    assert not paper['cat_index_order_rounding_mismatches']
    assert not paper['ps_index_order_rounding_mismatches']
    assert not paper['table3']['workbook_si_value_discrepancies']
    publisher = json.loads((ROOT / 'forensics/outputs/publisher_comparison.json').read_text())
    assert all(row['all_nonempty_cell_content_identical'] for row in publisher['comparisons'])

    original_hashes = {row['sha256'] for row in current.values()}
    tracked = git('ls-files', '-z').decode().split('\0')[:-1]
    staged = git('diff', '--cached', '--name-only', '-z').decode().split('\0')[:-1]
    rejected = []
    sizes = {}

    def inspect_blob(name, content):
        if not allowed_path(name):
            rejected.append(f'Unapproved tracked source/type: {name}')
        if hashlib.sha256(content).hexdigest() in original_hashes:
            rejected.append(f'Exact original-file copy: {name}')
        if name in REVIEWED_FIGURES:
            try:
                reviewed_figure_text(name, content)
            except Exception as error:
                rejected.append(f'Unreviewed or unreadable derived figure: {name} ({type(error).__name__})')
            return
        if content.startswith((b'%PDF-', b'PK\x03\x04', b'\x1f\x8b', b'version https://git-lfs.github.com/spec/v1')):
            rejected.append(f'Forbidden source/archive/LFS bytes: {name}')
        if name.endswith('.gitattributes') and b'filter=lfs' in content:
            rejected.append(f'LFS rule: {name}')
        content.decode('utf-8')  # Other permitted artifacts remain inspectable text.

    for name in tracked:
        content = git('show', ':' + name)
        inspect_blob(name, content)
        if name in staged:
            sizes[name] = len(content)
    historical_blobs = 0
    reviewed_pairs = set()
    for commit in git('rev-list', '--all').decode().splitlines():
        for entry in git('ls-tree', '-r', '-z', commit).split(b'\0'):
            if entry:
                info, name_bytes = entry.split(b'\t', 1)
                name = name_bytes.decode()
                oid = info.split()[2].decode()
                if name in REVIEWED_FIGURES and (name, oid) not in reviewed_pairs:
                    inspect_blob(name, git('cat-file', 'blob', oid))
                    reviewed_pairs.add((name, oid))
    objects = git('rev-list', '--objects', '--all').decode().splitlines()
    for line in objects:
        oid, _, name = line.partition(' ')
        if git('cat-file', '-t', oid).strip() == b'blob':
            inspect_blob(name, git('cat-file', 'blob', oid))
            historical_blobs += 1
    ignored = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=ROOT,
                             input=''.join('orginal/' + name + '\n' for name in current).encode(),
                             stdout=subprocess.PIPE, check=True).stdout.decode().splitlines()
    assert len(ignored) == len(current), 'Not all originals ignored'
    for p in (ROOT / '.gitattributes', ROOT / '.git/info/attributes'):
        assert not p.exists() or 'filter=lfs' not in p.read_text(), f'LFS attributes: {p}'
    assert not rejected, '\n'.join(rejected)
    report = dict(
        original_file_count=len(current), original_bytes=sum(row['size'] for row in current.values()),
        manifest_hashes_and_sizes_match=True, pre_analysis_hashes_sizes_mtimes_match=baseline_verified,
        original_subtree_fully_ignored=True, tracked_file_count=len(tracked),
        staged_file_sizes=sizes, reachable_historical_blobs_checked=historical_blobs,
        forbidden_source_path_type_magic_or_exact_copy_findings=rejected,
        lfs_source_rules_found=False, derived_count_checks_passed=True,
        audit_limit='Exact-copy/type/history guard plus manual content review; hashes alone cannot detect reformatted source tables.',
        remote_note='This script is local and makes no push. Remote refs are inspected separately read-only.')
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
