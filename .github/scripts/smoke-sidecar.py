"""Exercise the packaged backend with disposable data and graceful stdin shutdown."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

root = Path(__file__).resolve().parents[2]
binaries = [p for p in (root / 'frontend/src-tauri/binaries').glob('ebon_backend-*') if p.is_file()]
if len(binaries) != 1:
    raise RuntimeError(f'Expected one bundled backend, found {len(binaries)}')
with tempfile.TemporaryDirectory(prefix='ebon-smoke-') as directory:
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    env = {**os.environ, 'EBON_DB_PATH': str(Path(directory) / 'test.db'), 'EBON_UPLOAD_DIR': str(Path(directory) / 'uploads')}
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen([str(binaries[0]), '--port', str(port)], cwd=directory, env=env, stdin=subprocess.PIPE, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('Sidecar exited before becoming healthy')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=2) as response:
                        if json.load(response).get('status') == 'ok':
                            break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.25)
            else:
                raise RuntimeError('Sidecar did not become healthy')
            process.communicate(b'exit\n', timeout=20)
            if process.returncode != 0:
                raise RuntimeError(f'Shutdown failed: {process.returncode}')
            print('Packaged sidecar HTTP startup and stdin shutdown passed with temporary data')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            log.seek(0)
            print(log.read().decode(errors='replace'))
