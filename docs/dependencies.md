# Dependency maintenance

## Reproducing installs

Use Node 24 LTS and Python 3.11, matching the release workflow. Run `npm ci`
in `frontend`; commit both npm and Cargo lockfiles when changing dependencies.
The Python `.in` files are editable inputs; `.txt` files are generated,
fully pinned, hashed locks with platform markers for Windows, macOS and Linux.

For runtime only, install `backend/requirements.txt`. For tests and sidecar
builds, install `backend/requirements-dev.txt` instead:

```sh
python -m pip install --require-hashes -r backend/requirements-dev.txt
python -m pytest backend/tests -q
```

Regenerate from the repository root using uv 0.12.17 (an isolated maintenance
tool, not a runtime dependency):

```sh
uv pip compile backend/requirements.in --python-version 3.11 --universal --generate-hashes -o backend/requirements.txt
uv pip compile backend/requirements-dev.in --constraint backend/requirements.txt --python-version 3.11 --universal --generate-hashes -o backend/requirements-dev.txt
```

Add `--upgrade` when intentionally refreshing existing pins. Runtime constraints
keep direct dependencies within their current major versions, with pdfplumber
restricted to 0.11. The development lock constrains shared packages to the runtime
lock and includes pytest, HTTPX and PyInstaller. Desktop packaging is supported
only on macOS ARM64. Portable lock markers do not
imply desktop support for other platforms. These locks make Python
package selection reproducible; they do not promise byte-identical executables
or pin OS toolchains and CI audit tools.

## Issue #1 audit — 2026-09-19

Registry and advisory data were queried again; the earlier issue inventory was
not used as evidence of current fixes. All direct frontend updates stay within
the existing package.json ranges. Selected locked versions:

| Package | Before | After |
| --- | --- | --- |
| SvelteKit | 2.53.4 | 2.70.3 |
| Svelte | 5.53.6 | 5.57.1 |
| Vite | 7.3.1 | 7.3.6 |
| Svelte Vite plugin | 6.2.4 | 6.2.4 |
| Tailwind CSS / Vite integration | 4.2.1 | 4.3.3 |
| Tauri CLI | 2.10.0 | 2.11.4 |
| Tauri Rust runtime | 2.10.2 | 2.11.5 |
| Tauri build | 2.5.5 | 2.6.3 |
| Tauri shell plugin | 2.3.5 | 2.3.6 |
| TypeScript | 5.9.3 | 5.9.3 |
| ESLint | 9.39.3 | 9.39.5 |

Python previously had minimum-only requirements, so there is no previous
reproducible environment to compare. The tested lock selects FastAPI 0.141.1,
Uvicorn 0.53.0, SQLModel 0.0.42, pdfplumber 0.11.10, python-multipart 0.0.32,
Pydantic 2.13.5 and pydantic-settings 2.15.0. All transitive pins and hashes are
in the generated locks.

### Security results and applicability

- Full npm audit: **15 affected packages (9 high, 3 moderate, 3 low) → 6 low**,
  with zero high/moderate findings. CI now explicitly includes development
  dependencies. The six remaining package reports share one underlying
  [cookie advisory](https://github.com/advisories/GHSA-pxg6-pf52-xh8x), propagated
  through SvelteKit, adapter-static, runed, svelte-toolbelt and bits-ui. The
  locked SvelteKit still uses cookie 0.6.0. This app ships static frontend assets
  with a Python backend, not a SvelteKit cookie-setting server. Do not force npm's
  suggested obsolete SvelteKit/adapter downgrades; track an upstream compatible
  fix. No audit suppression or transitive override was added.
- The [Vite WebSocket file-read advisory](https://github.com/advisories/GHSA-p9ff-h696-f583)
  affects exposed development servers; its version-7 fix starts at 7.3.2. The
  selected 7.3.6 also clears the later Vite findings. The packaged static app
  does not run Vite. Build-tool filesystem, glob and parsing advisories remain
  relevant to development/CI, which is why production-only audits are inadequate.
- Svelte/SvelteKit/devalue findings include SSR, remote forms and serialization
  paths; those server features are not the desktop serving architecture. The
  compatible updates nevertheless remove the reported findings, including the
  Svelte DOM-clobbering advisory which is not limited to SSR.
- `pip-audit --require-hashes -r backend/requirements-dev.txt`: **no known
  vulnerabilities** for the dependencies applicable to this macOS audit host.
  A fresh resolution of the original requirements also reported none; locking
  prevents later installs silently selecting a different environment. Python
  processes imported receipt files, so parser dependencies are runtime exposure.
- Cargo audit: **2 vulnerabilities → 0**. The old quick-xml was affected by
  [RUSTSEC-2026-0195](https://rustsec.org/advisories/RUSTSEC-2026-0195.html) and
  [RUSTSEC-2026-0194](https://rustsec.org/advisories/RUSTSEC-2026-0194.html), both
  denial-of-service findings. The updated dependency graph clears them.
  Seven informational warnings remain: unmaintained `proc-macro-error`
  (RUSTSEC-2024-0370), `unic-char-property` (RUSTSEC-2025-0081), `unic-char-range`
  (RUSTSEC-2025-0075), `unic-common` (RUSTSEC-2025-0080), `unic-ucd-ident`
  (RUSTSEC-2025-0100), `unic-ucd-version` (RUSTSEC-2025-0098), and `glib`
  unsoundness (RUSTSEC-2024-0429). The Unicode crates are pulled through
  Tauri's urlpattern dependency. glib is in the Linux GTK dependency graph,
  not the tested macOS build; its upstream fix requires glib >=0.20 and cannot
  be forced into the current 0.18 graph safely. Track Tauri's upstream changes.
  These warnings are recorded, not suppressed or described as fixed.

### Validation

Tested on macOS ARM64 with Node 24.19.0, npm 11.17.0, Python 3.11.16,
Rust 1.98.1, pip-audit 2.10.1 and cargo-audit 0.22.2:

- Clean npm install, `npm run check` and `npm run build` pass. Build emits a
  Svelte warning about the initial locale reference in `index.svelte.ts`.
- `npm run lint` fails on **26 pre-existing formatting failures**. A temporary
  checkout of c2f9ba1 with its original npm lock produces the same list.
  ESLint on source has the same **40 errors** before and after (31 explicit-any,
  5 navigation resolve, 3 reactivity, 1 raw-HTML). Running ESLint after a build
  also scans generated `dist` output because the existing frontend ignore file
  omits it. The final post-build lint run reports 76 formatting failures,
  including generated output. No rules or checks were disabled to obtain a
  passing result.
- `python -m pytest backend/tests -q`: **84 passed**, including a second run
  after synchronizing the final hashed development lock.
- PyInstaller sidecar build and `tauri build --no-bundle --ci`: pass on macOS
  ARM64. No installer, signed package or release was published.
- Packaged sidecar started with a temporary SQLite database; health and UI API
  requests returned 200. Sending `exit` on stdin completed graceful shutdown
  with exit status 0.
- Chromium UI smoke: dashboard empty state, sidebar and Import screen render;
  navigation works, with no browser errors or Vite error overlay. Test storage
  was temporary; no personal receipt database was opened.
- Windows, macOS Intel, Linux runtime, DMG/NSIS packaging and the native Tauri
  window lifecycle were not tested locally. The native app was not launched
  because its existing startup code selects the user's real app database.

### Separate follow-up work

Keep issue #1 open until the validation limitations and remaining work are
reviewed. Do not merge through failing required checks.

- Vite 8.3.0 + Svelte Vite plugin 7.3.0: registry availability confirmed;
  evaluate their peer requirements and Vite migration changes together in a
  separate branch. Vite 7.3.6 resolves the current audit findings without this
  migration.
- TypeScript 7.0.2: registry availability confirmed; separately validate Svelte
  checking, editor tooling and typescript-eslint compatibility before selecting
  a target. Retain 5.9.3 here.
- ESLint 10.11.0: registry availability confirmed; separately review plugin
  compatibility and configuration changes. Registry marks ESLint 9.39.5 as
  unsupported, so this follow-up matters even though its audit is clear.
- Resolve the existing formatting/source lint failures and generated-output
  exclusion in a focused cleanup (subsequently completed in #7). Desktop release
  validation now targets only macOS ARM64 (#14). Monitor cookie and the seven
  Rust warnings for compatible upstream fixes.

CI uses [Node 24 LTS](https://nodejs.org/en/about/previous-releases) instead of
Node 20. The existing workflow only runs for releases/manual dispatch; this
change does not claim that PR checks or branch protections are configured.
