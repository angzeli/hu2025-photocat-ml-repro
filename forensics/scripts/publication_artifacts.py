"""Narrow exceptions for reviewed public figures and project metadata.

Figure hashes are recorded only after source, metadata and visual review plus a
repeat build. The builder must never update this allowlist automatically. Retain
older reviewed digests while their figures remain in reachable commit history.
An exact path alone never authorizes binary content or a renamed source file.
"""
import hashlib
import io
from pathlib import PurePosixPath
import struct

TEXT_TYPES = {'.py', '.md', '.csv', '.json', '.yaml', '.yml'}
METADATA_FILES = {'.gitignore', 'LICENSE', 'CITATION.cff', 'requirements.txt'}
FORBIDDEN_ROOTS = ('orginal/', 'original/', 'forensics/local_only/', 'data/local_only/')
REVIEWED_FIGURES = {
    'figures/derived/reproducibility_ladder.png': (
        '0553f423feb2ec7a359fab79f429247e346ff0628225a89468f0f3e30b620c7d',),
    'figures/derived/reproducibility_ladder.pdf': (
        '564adbe27136a709d39cb5cedb4a1ff86eadba809cc122f63331003e7b971bfa',),
    'figures/derived/ml_quality.png': (
        'ab125b72b7e8d1009815198f3d1ef9c92e7c282e3017009b5f6f9e2661ae1661',),
    'figures/derived/ml_quality.pdf': (
        'd370c5f3547b7552c192642721cce9dba238fda6c48b6fd2b023137ef4a6882f',),
    'figures/derived/coupling_error_decomposition.png': (
        '2ae73c5463c782c1070d765da7cfd5e7f05419e1f6076ef5e57c506e827b0a2e',),
    'figures/derived/coupling_error_decomposition.pdf': (
        'e0807622835f9a017413ffb11225cc43b28f6b7d8debdf76eb0a4721a360d7a4',),
    'figures/derived/screening_sensitivity.png': (
        'a60096278dd25a2e965620b59238b235d93a998ca556ef4c39c07a4f4ca71013',),
    'figures/derived/screening_sensitivity.pdf': (
        'bdae0e05c21a421727cf0eb4c25bb412473aa163be28e2336c8c117bd42b2d56',),
}


def allowed_path(name):
    """Check every historical path, including aliases of an already seen blob."""
    return (not name.startswith(FORBIDDEN_ROOTS)
            and (name in METADATA_FILES or name in REVIEWED_FIGURES
                 or PurePosixPath(name).suffix in TEXT_TYPES))


def reviewed_figure_text(name, data):
    """Validate approved bytes and return metadata/text for the privacy scanner.

PNG pixels still require visual review; this is not general image declassification.
Unknown or changed bytes fail closed, including at an otherwise approved path.
"""
    if hashlib.sha256(data).hexdigest() not in REVIEWED_FIGURES.get(name, ()):
        raise ValueError('Unreviewed figure path or bytes')
    if name.endswith('.pdf'):
        if not data.startswith(b'%PDF-'):
            raise ValueError('Expected a PDF figure')
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted or len(reader.pages) != 1:
            raise ValueError('Expected one unencrypted figure page')
        return str(dict(reader.metadata or {})) + '\n' + reader.pages[0].extract_text()
    if not name.endswith('.png') or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Expected a PNG figure')
    texts = []
    offset = 8
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        length, kind = struct.unpack('>I4s', data[offset:offset + 8])
        end = offset + 12 + length
        if end > len(data):
            raise ValueError('Truncated PNG payload')
        payload = data[offset + 8:offset + 8 + length]
        if kind == b'tEXt':
            texts.append(payload.decode('latin-1'))
        elif kind in (b'zTXt', b'iTXt'):
            raise ValueError('Additional PNG metadata requires explicit review support')
        offset = end
        if kind == b'IEND':
            if offset != len(data):
                raise ValueError('Unexpected data after PNG end')
            return '\n'.join(texts)
    raise ValueError('Missing PNG end')
