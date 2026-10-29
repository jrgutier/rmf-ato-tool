"""`rmf doctor`: report whether the local toolchain is ready."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    required: bool
    detail: str


def _first_line(argv: list[str], cwd: Path | None = None) -> str | None:
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, check=False, cwd=cwd)
    except OSError:
        return None
    out = (proc.stdout or proc.stderr).strip().splitlines()
    return out[0] if proc.returncode == 0 and out else None


def _tool(name: str, required: bool, hint: str, version_args: tuple[str, ...]) -> Check:
    path = shutil.which(name)
    if path is None:
        return Check(name, False, required, f"not found on PATH ({hint})")
    version = _first_line([path, *version_args]) or path
    return Check(name, True, required, version)


def _module(name: str, hint: str) -> Check:
    found = importlib.util.find_spec(name) is not None
    return Check(name, found, False, "installed" if found else f"not installed ({hint})")


def run_checks(root: Path) -> list[Check]:
    py = sys.version_info
    checks = [
        Check(
            "python",
            py[:2] >= MIN_PYTHON,
            True,
            f"{py.major}.{py.minor}.{py.micro} (need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]})",
        ),
        _tool("uv", True, "make bootstrap", ("--version",)),
        _tool("git", True, "install git", ("--version",)),
        _tool("git-lfs", True, "make bootstrap", ("version",)),
        _tool("jq", True, "make bootstrap", ("--version",)),
        _tool("qpdf", True, "make bootstrap", ("--version",)),
    ]
    if shutil.which("git") and (root / ".git").exists():
        lfs = _first_line(["git", "config", "--get", "filter.lfs.process"], cwd=root)
        checks.append(
            Check(
                "git-lfs hooks",
                lfs is not None,
                True,
                "installed" if lfs else "run: git lfs install --local",
            )
        )
    checks += [
        _module("pymupdf", "optional; EXTRACT=1 make bootstrap"),
        _module("pdfplumber", "optional; EXTRACT=1 make bootstrap"),
        _tool("ocrmypdf", False, "optional; OCR=1 make bootstrap", ("--version",)),
        _tool("tesseract", False, "optional; OCR=1 make bootstrap", ("--version",)),
    ]
    return checks
