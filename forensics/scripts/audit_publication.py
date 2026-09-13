#!/usr/bin/env python3
"""Read-only source/privacy audit of reachable history, index and proposed files.

Explicit public-email exceptions must be independently verified public metadata.
Reports contain locations and categories, never matched credential values. This
bounded pattern/content scan complements manual review; it cannot prove absence
of every possible secret or detect every transformation of a source dataset.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
TEXT_TYPES = {'.py', '.md', '.csv', '.json', '.yaml', '.yml'}
EMAIL = re.compile(r'(?<![\w.+-])[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PATTERNS = {
    'local_filesystem_path': re.compile(r'/(?:Users|home|private/(?:tmp|var)|tmp|var/folders)/[^\s`"<>]+'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'credential_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9_-]{25,}|AKIA[0-9A-Z]{16})\b'),
    'assigned_secret': re.compile(r'(?i)\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)[\x22\x27]?\s*[=:]\s*[\x22\x27]?[A-Za-z0-9+/_.=-]{16,}'),
    'authorization_or_cookie': re.compile(r'(?i)\b(?:Authorization[\x22\x27]?\s*:\s*[\x22\x27]?(?:Bearer|Basic)\s+[A-Za-z0-9+/_.=-]{8,}|(?:Set-Cookie|Cookie)[\x22\x27]?\s*:\s*[\x22\x27]?[^\s]+=[^\s;]{8,})'),
    'credential_url': re.compile(r'\b[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@', re.I),
    'private_ipv4': re.compile(r'\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b'),
    'local_hostname': re.compile(r'\b[A-Za-z0-9_-]+\.(?:local|lan|internal)\b', re.I),
    'session_identifier': re.compile(r'(?i)(?:session[_-]?id|oauth[_-]?(?:token|code))\s*[=:]\s*[\x22\x27]?[A-Za-z0-9_-]{16,}'),
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-email', action='append', default=[])
    parser.add_argument('--private-token', action='append', default=[])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output:
        destination = args.output.resolve()
        if any(destination == p or p in destination.parents
               for p in ((ROOT / 'orginal').resolve(), (ROOT / '.git').resolve())):
            parser.error('Report destination must be outside source evidence and Git internals')
    with (ROOT / 'data/manifests/original-files.csv').open() as stream:
        original_hashes = {row['sha256'] for row in csv.DictReader(stream)}
    public_emails = set(args.public_email)
    findings = []
    public_email_occurrences = 0

    def scan_identifiers(text, name, location, line=None):
        nonlocal public_email_occurrences
        position = dict(location=location, path=name)
        if line is not None:
            position['line'] = line
        for category, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(dict(position, category=category))
        if any(token and token.casefold() in text.casefold() for token in args.private_token):
            findings.append(dict(position, category='explicit_private_identifier'))
        for match in EMAIL.finditer(text):
            if match.group() not in public_emails:
                findings.append(dict(position, category='email_not_verified_public'))
            else:
                public_email_occurrences += 1

    def scan_path(name, location):
        scan_identifiers(name, name, location)
        if (name.startswith(('orginal/', 'original/', 'forensics/local_only/', 'data/local_only/'))
                or not (name == '.gitignore' or Path(name).suffix in TEXT_TYPES)):
            findings.append(dict(location=location, path=name, category='unapproved_path_or_type'))
        if Path(name).name.startswith('.env') or any(part in ('.ssh', '.aws', '.azure') for part in Path(name).parts):
            findings.append(dict(location=location, path=name, category='credential_file'))

    def scan(name, data, location, is_commit=False, check_path=True):
        if not is_commit:
            if check_path:
                scan_path(name, location)
            if hashlib.sha256(data).hexdigest() in original_hashes:
                findings.append(dict(location=location, path=name, category='exact_original_copy'))
            if data.startswith((b'%PDF-', b'PK\x03\x04', b'\x1f\x8b', b'version https://git-lfs.github.com/spec/v1')):
                findings.append(dict(location=location, path=name, category='source_archive_or_lfs_signature'))
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            findings.append(dict(location=location, path=name, category='binary_not_reviewable_text'))
            return
        for number, line in enumerate(text.splitlines(), 1):
            scan_identifiers(line, name, location, line=number)
        if not is_commit and name.endswith('.csv'):
            rows = list(csv.reader(io.StringIO(text)))
            if rows:
                headers = {item.lower() for item in rows[0]}
                raw_components = {'calculated_x', 'predicted_x', 'calculated_y', 'predicted_y'}
                raw_pairs = {'j_calculated', 'j_predicted'}
                raw_experiment = {'ton_co', 'co_selectivity_percent'}
                if len(rows) > 20 and (headers >= raw_components or headers >= raw_pairs or headers >= raw_experiment):
                    findings.append(dict(location=location, path=name, category='full_source_style_numeric_table'))
        atom_line = re.compile(r'^\s*[A-Z][a-z]?\s+[-+]?\d+\.\d+\s+[-+]?\d+\.\d+\s+[-+]?\d+\.\d+\s*$', re.M)
        if len(atom_line.findall(text)) > 10:
            findings.append(dict(location=location, path=name, category='coordinate_dump'))

    commits = git('rev-list', '--all').decode().splitlines()
    commit_objects = {entry.partition(' ')[0] for entry in git('rev-list', '--objects', *commits).decode().splitlines()}
    historical_paths = 0
    for commit in commits:
        scan('commit metadata', git('cat-file', 'commit', commit), commit, is_commit=True)
        # A blob can occur at multiple paths, including a forbidden historical
        # path. rev-list --objects supplies only one name per object, so inspect
        # every commit tree separately while keeping content scans deduplicated.
        for entry in git('ls-tree', '-r', '-z', commit).split(b'\0'):
            if entry:
                _, name = entry.split(b'\t', 1)
                scan_path(name.decode(), commit)
                historical_paths += 1
    historical_blobs = 0
    auxiliary_blobs = 0
    auxiliary_findings = []
    for entry in git('rev-list', '--objects', '--all').decode().splitlines():
        oid, _, name = entry.partition(' ')
        if git('cat-file', '-t', oid).strip() == b'blob':
            before = len(findings)
            scan(name, git('cat-file', 'blob', oid), oid, check_path=oid not in commit_objects)
            if oid in commit_objects:
                historical_blobs += 1
            else:
                # Codex may retain non-commit local tree snapshots after an
                # authorized amend. Inspect them, but distinguish them from
                # commit history; a normal explicit main push excludes these refs.
                auxiliary_blobs += 1
                auxiliary_findings.extend(findings[before:])
                del findings[before:]
    tracked = git('ls-files', '-z').decode().split('\0')[:-1]
    for name in tracked:
        scan(name, git('show', ':' + name), 'index')
    proposed = sorted(set(tracked + git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')[:-1]))
    for name in proposed:
        path = ROOT / name
        if path.is_file():
            scan(name, path.read_bytes(), 'working_tree')
    for path in (ROOT / '.gitattributes', ROOT / '.git/info/attributes'):
        if path.exists() and 'filter=lfs' in path.read_text():
            findings.append(dict(path=path.relative_to(ROOT).as_posix(), category='lfs_attribute_rule'))
    ignored = []
    for name in ('orginal/', 'forensics/local_only/'):
        result = subprocess.run(['git', 'check-ignore', name], cwd=ROOT, capture_output=True)
        if result.returncode != 0:
            findings.append(dict(path=name, category='required_ignore_missing'))
        else:
            ignored.append(name)
    report = dict(audited_head=git('rev-parse', 'HEAD').decode().strip(),
                  reachable_commits=commits, reachable_blob_count=historical_blobs,
                  commit_file_paths_checked=historical_paths,
                  auxiliary_local_noncommit_blobs_checked=auxiliary_blobs,
                  auxiliary_local_noncommit_findings=auxiliary_findings,
                  auxiliary_scope='Local non-commit tree refs are not reachable from the audited commit history and are not part of a normal main push.',
                  index_file_count=len(tracked), proposed_file_count=len(proposed),
                  ignored_source_roots=ignored, verified_public_email_allowlist_size=len(public_emails),
                  public_email_occurrences=public_email_occurrences, findings=findings,
                  limitation='Pattern/type/hash/schema checks plus manual review; no universal secret or transformed-source detection guarantee.',
                  network_actions='none; remote identity and ref checks occur separately')
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
