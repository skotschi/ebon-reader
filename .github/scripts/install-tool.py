"""Install pinned official scanner archives after SHA256 verification."""
import hashlib
import io
from pathlib import Path
import platform
import sys
import tarfile
import urllib.request

TOOLS = {'actionlint': ('rhysd/actionlint', '1.7.12'), 'gitleaks': ('gitleaks/gitleaks', '8.30.1')}
name = sys.argv[1]
repo, version = TOOLS[name]
system = platform.system().lower()
arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64' if name == 'gitleaks' else 'amd64'}[platform.machine().lower()]
archive = f'{name}_{version}_{system}_{arch}.tar.gz'
base = f'https://github.com/{repo}/releases/download/v{version}/'
def download(filename):
    with urllib.request.urlopen(base + filename, timeout=60) as response:
        return response.read()
checksums = download(f'{name}_{version}_checksums.txt').decode()
expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1].lstrip('*') == archive)
data = download(archive)
if hashlib.sha256(data).hexdigest() != expected:
    raise RuntimeError('Scanner archive checksum mismatch')
output = Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as bundle:
    member = bundle.extractfile(name)
    if member is None:
        raise RuntimeError('Scanner binary missing')
    binary = output / name
    binary.write_bytes(member.read())
    binary.chmod(0o755)
print(binary)
