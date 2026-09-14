"""Regression checks for the narrow public-binary publication boundary."""
import hashlib
import contextlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'forensics/scripts'))
import publication_artifacts as policy  # noqa: E402
import audit_publication  # noqa: E402


def png_fixture(metadata_kind=b'tEXt'):
    """One synthetic pixel; never a publisher/source fixture."""
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload)))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(metadata_kind, b'Software\0synthetic-review-fixture')
            + chunk(b'IDAT', zlib.compress(b'\0\0\0\0'))
            + chunk(b'IEND', b''))


class PublicationArtifactTests(unittest.TestCase):
    figure = 'figures/derived/ml_quality.png'

    def test_paths_default_deny_binary_and_source_roots(self):
        for name in ('LICENSE', 'CITATION.cff', 'requirements.txt', self.figure):
            self.assertTrue(policy.allowed_path(name), name)
        for name in ('arbitrary.pdf', 'figures/derived/other.png', 'copy.cff',
                     'nested/requirements.txt', 'orginal/summary.json',
                     'original/summary.md', 'forensics/local_only/metrics.csv',
                     'data/local_only/metrics.csv'):
            self.assertFalse(policy.allowed_path(name), name)

    def test_reviewed_bytes_expose_metadata_for_privacy_scan(self):
        data = png_fixture()
        digest = hashlib.sha256(data).hexdigest()
        with patch.dict(policy.REVIEWED_FIGURES, {self.figure: (digest,)}):
            self.assertIn('synthetic-review-fixture', policy.reviewed_figure_text(self.figure, data))

    def test_byte_changes_or_source_substitution_are_rejected(self):
        data = png_fixture()
        digest = hashlib.sha256(data).hexdigest()
        with patch.dict(policy.REVIEWED_FIGURES, {self.figure: (digest,)}):
            for changed in (data + b'extra', data.replace(b'Software', b'Changed!'),
                            b'%PDF-1.4\nsynthetic source-substitution sentinel'):
                with self.assertRaises(ValueError):
                    policy.reviewed_figure_text(self.figure, changed)

    def test_approved_bytes_cannot_be_reused_at_an_unreviewed_path(self):
        data = png_fixture()
        digest = hashlib.sha256(data).hexdigest()
        with patch.dict(policy.REVIEWED_FIGURES, {self.figure: (digest,)}):
            for alias in ('figures/derived/alias.png', 'figures/derived/screening_sensitivity.png'):
                with self.assertRaises(ValueError):
                    policy.reviewed_figure_text(alias, data)

    def test_signature_and_unsupported_metadata_fail_closed(self):
        for data in (b'not an image', png_fixture(b'zTXt')):
            digest = hashlib.sha256(data).hexdigest()
            with patch.dict(policy.REVIEWED_FIGURES, {self.figure: (digest,)}):
                with self.assertRaises(ValueError):
                    policy.reviewed_figure_text(self.figure, data)

    def test_deleted_historical_alias_is_still_rejected(self):
        """A valid current tree must not hide an unreviewed historical alias."""
        data = png_fixture()
        digest = hashlib.sha256(data).hexdigest()
        alias = 'figures/derived/screening_sensitivity.png'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            email = 'fixture' + '@' + 'example.org'
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            git('init', '-q')
            git('config', 'user.name', 'Synthetic Audit Fixture')
            git('config', 'user.email', email)
            git('config', 'commit.gpgsign', 'false')
            (root / 'data/manifests').mkdir(parents=True)
            (root / 'data/manifests/original-files.csv').write_text('sha256\n')
            (root / '.gitignore').write_text('orginal/\nforensics/local_only/\n')
            (root / 'orginal').mkdir()
            (root / 'forensics/local_only').mkdir(parents=True)
            (root / self.figure).parent.mkdir(parents=True)
            (root / self.figure).write_bytes(data)
            git('add', '.')
            git('commit', '-qm', 'Valid synthetic figure')
            (root / alias).write_bytes(data)
            git('add', alias)
            git('commit', '-qm', 'Unreviewed historical alias')
            git('rm', alias)
            git('commit', '-qm', 'Remove alias from current tree')
            output = io.StringIO()
            with (patch.dict(policy.REVIEWED_FIGURES, {self.figure: (digest,), alias: ()}),
                  patch.object(audit_publication, 'ROOT', root),
                  patch.object(sys, 'argv', ['audit', '--public-email', email]),
                  contextlib.redirect_stdout(output), self.assertRaises(SystemExit)):
                audit_publication.main()
            findings = json.loads(output.getvalue())['findings']
            self.assertTrue(any(row['path'] == alias
                                and row['category'] == 'unreviewed_or_unreadable_figure'
                                and row['location'] not in ('index', 'working_tree')
                                for row in findings))


if __name__ == '__main__':
    unittest.main()
