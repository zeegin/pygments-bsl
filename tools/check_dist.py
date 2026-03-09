#!/usr/bin/env python3
"""Smoke-check built distribution artifacts."""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
BANNED_PARTS = {"tests", "examplefiles"}
SMOKE_SNIPPET = """
from pygments import lexers

assert lexers.get_lexer_by_name("bsl").name == "1C (BSL) Lexer"
assert lexers.get_lexer_by_name("sdbl").name == "1C (SDBL) Lexer"
"""


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd)


def _artifact_paths() -> list[Path]:
    wheels = sorted(DIST_DIR.glob("*.whl"))
    sdists = sorted(DIST_DIR.glob("*.tar.gz"))
    if not wheels or not sdists:
        raise SystemExit("Expected at least one wheel and one sdist in dist/")
    return [*wheels, *sdists]


def _archive_members(path: Path) -> list[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()

    with tarfile.open(path) as archive:
        return [member.name for member in archive.getmembers()]


def _check_archive_contents(path: Path) -> None:
    banned = [
        member
        for member in _archive_members(path)
        if any(part in BANNED_PARTS for part in PurePosixPath(member).parts)
    ]
    if banned:
        joined = ", ".join(sorted(banned))
        raise SystemExit(f"{path.name} unexpectedly contains test fixtures: {joined}")


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _smoke_install(path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pygments-bsl-dist-") as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = _venv_python(venv_dir)
        _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
        _run([str(python), "-m", "pip", "install", str(path)])
        _run([str(python), "-c", SMOKE_SNIPPET], cwd=tmp_path)


def main() -> None:
    for artifact in _artifact_paths():
        _check_archive_contents(artifact)
        _smoke_install(artifact)


if __name__ == "__main__":
    main()
