import hashlib
import os
from pathlib import Path
import shutil

root = Path('frontend/src-tauri/target/release/bundle')
files = list(root.glob('nsis/*.exe')) + list(root.glob('dmg/*.dmg'))
if not files:
    raise RuntimeError('No desktop installers were produced')
output = Path('dist')
output.mkdir(exist_ok=True)
checksums = []
for source in files:
    target = output / source.name
    shutil.copy2(source, target)
    checksums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}')
(output / f'SHA256SUMS-{os.environ["ARTIFACT_LABEL"]}.txt').write_text('\n'.join(checksums) + '\n')
