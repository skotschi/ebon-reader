from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_BIN_DIR = BACKEND_DIR.parent / "frontend" / "src-tauri" / "binaries"
ENTRYPOINT = BACKEND_DIR / "sidecar_main.py"
PYINSTALLER_NAME = "ebon_backend"

# PyInstaller packages the host interpreter; cross-compiling the Rust app alone
# cannot produce a compatible backend. Require a native Apple Silicon build.
def _resolve_target() -> tuple[str, str]:
    system = platform.system()
    machine = platform.machine()
    if (system, machine) != ("Darwin", "arm64"):
        raise RuntimeError(
            f"Unsupported desktop build platform: {system}/{machine}. "
            "Only macOS ARM64 (Apple Silicon) is supported."
        )
    return "aarch64-apple-darwin", ""


def build_sidecar() -> int:
    target_triple, ext = _resolve_target()
    if not ENTRYPOINT.exists():
        print(f"ERROR: Missing sidecar entrypoint: {ENTRYPOINT}")
        return 1

    for stale_path in (
        BACKEND_DIR / "build",
        BACKEND_DIR / "dist",
        BACKEND_DIR / "sidecar_main.spec",
    ):
        if stale_path.is_dir():
            shutil.rmtree(stale_path)
        elif stale_path.exists():
            stale_path.unlink()

    print(f"Building backend sidecar with PyInstaller for {target_triple}...")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--collect-data",
            "app.assets",
            "--name",
            PYINSTALLER_NAME,
            str(ENTRYPOINT),
        ],
        cwd=BACKEND_DIR,
        check=False,
    )
    if result.returncode != 0:
        print("ERROR: PyInstaller build failed.")
        return result.returncode

    built_binary = BACKEND_DIR / "dist" / f"{PYINSTALLER_NAME}{ext}"
    if not built_binary.exists():
        print(f"ERROR: Built binary not found: {built_binary}")
        return 1

    FRONTEND_BIN_DIR.mkdir(parents=True, exist_ok=True)
    destination = FRONTEND_BIN_DIR / f"{PYINSTALLER_NAME}-{target_triple}{ext}"
    shutil.copy2(built_binary, destination)

    print(f"SUCCESS: Sidecar binary copied to: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build_sidecar())
