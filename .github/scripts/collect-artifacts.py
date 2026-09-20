"""Collect only the supported ARM64 installer into a fresh release artifact."""
import hashlib
from pathlib import Path
import shutil


def collect(root: Path, output: Path) -> None:
    installers = sorted(p for p in root.rglob('*') if p.suffix in {'.dmg', '.exe', '.msi', '.deb', '.rpm', '.AppImage'})
    if (len(installers) != 1 or installers[0].parent != root / 'dmg'
            or not installers[0].name.endswith('_aarch64.dmg')
            or installers[0].is_symlink()):
        raise RuntimeError('Expected exactly one macOS ARM64 DMG and no other installers')
    if output.exists() and any(output.iterdir()):
        raise RuntimeError('Artifact output directory must be empty')
    output.mkdir(exist_ok=True)
    target = output / installers[0].name
    shutil.copy2(installers[0], target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (output / 'SHA256SUMS-macos-arm64.txt').write_text(f'{digest}  {target.name}\n')


if __name__ == '__main__':
    collect(Path('frontend/src-tauri/target/release/bundle'), Path('dist'))
