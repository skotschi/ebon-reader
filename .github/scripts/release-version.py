"""Apply an already validated SemVer tag only to the disposable build workspace."""
import json
import os
from pathlib import Path
import re

tag = os.environ['RELEASE_TAG']
if not re.fullmatch(r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?', tag):
    raise ValueError('Expected a v-prefixed version tag')
version = tag[1:]
p = Path('frontend/src-tauri/tauri.conf.json')
data = json.loads(p.read_text())
data['version'] = version
p.write_text(json.dumps(data, indent=2) + '\n')
p = Path('frontend/src-tauri/Cargo.toml')
s = p.read_text()
s, count = re.subn(r'(?m)^version\s*=\s*"[^"]+"', f'version = "{version}"', s, count=1)
if count != 1:
    raise ValueError('Package version missing')
p.write_text(s)
with open(os.environ['GITHUB_ENV'], 'a') as env:
    env.write(f'VITE_APP_VERSION={version}\nAPP_VERSION={version}\n')
