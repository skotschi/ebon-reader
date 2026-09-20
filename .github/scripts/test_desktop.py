"""Exercise artifact selection and the exact publication preflight without publishing."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]


def module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


collector = module(REPO / '.github/scripts/collect-artifacts.py')
sidecar = module(REPO / 'backend/build_sidecar.py')


class DesktopTests(unittest.TestCase):
    def test_native_build_only(self):
        for system, machine in [('Darwin', 'arm64'), ('Darwin', 'x86_64'), ('Windows', 'AMD64'), ('Linux', 'aarch64')]:
            with self.subTest(system=system, machine=machine), patch.object(sidecar.platform, 'system', return_value=system), patch.object(sidecar.platform, 'machine', return_value=machine):
                if (system, machine) == ('Darwin', 'arm64'):
                    self.assertEqual(sidecar._resolve_target(), ('aarch64-apple-darwin', ''))
                else:
                    with self.assertRaises(RuntimeError):
                        sidecar._resolve_target()

    def test_collection(self):
        for names in [[], ['dmg/App_x64.dmg'], ['nsis/App.exe'], ['dmg/App_aarch64.dmg', 'nsis/App.exe'], ['dmg/App_aarch64.dmg', 'dmg/Other_aarch64.dmg'], ['dmg/App_aarch64.dmg']]:
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / 'bundle'
                output = Path(directory) / 'dist'
                for name in names:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b'synthetic installer')
                if names == ['dmg/App_aarch64.dmg']:
                    collector.collect(root, output)
                    self.assertEqual(len(list(output.iterdir())), 2)
                    with self.assertRaises(RuntimeError):
                        collector.collect(root, output)
                else:
                    with self.assertRaises(RuntimeError):
                        collector.collect(root, output)

    def test_publication_preflight(self):
        workflow = (REPO / '.github/workflows/release.yml').read_text()
        preflight = workflow.split('          # Fail closed', 1)[1].split('          if gh release view', 1)[0]
        preflight = '\n'.join(line[10:] for line in preflight.splitlines()[2:])
        for scenario in ['valid', 'windows', 'intel', 'extra', 'hidden', 'bad checksum', 'empty manifest', 'extra manifest entry', 'missing dmg']:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                name = 'eBon Reader_0.1.0_aarch64.dmg'
                if scenario == 'windows':
                    name = 'App.exe'
                if scenario == 'intel':
                    name = 'App_x64.dmg'
                (root / name).write_bytes(b'synthetic installer')
                digest = hashlib.sha256(b'synthetic installer').hexdigest()
                manifest = f'{digest}  {name}\n'
                if scenario == 'bad checksum':
                    manifest = '0' * 64 + f'  {name}\n'
                if scenario == 'empty manifest':
                    manifest = ''
                if scenario == 'extra manifest entry':
                    manifest *= 2
                (root / 'SHA256SUMS-macos-arm64.txt').write_text(manifest)
                if scenario in ['extra', 'hidden']:
                    (root / ('.extra' if scenario == 'hidden' else 'extra.exe')).touch()
                if scenario == 'missing dmg':
                    (root / name).unlink()
                with tempfile.TemporaryDirectory() as runner_temp:
                    result = subprocess.run(['bash', '-c', 'set -euo pipefail\n' + preflight], cwd=root, env={**os.environ, 'RUNNER_TEMP': runner_temp}, capture_output=True)
                self.assertEqual(result.returncode == 0, scenario == 'valid', result.stderr.decode())
