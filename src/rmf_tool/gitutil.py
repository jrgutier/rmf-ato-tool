"""Git helpers shared by every command that diffs against a base revision."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Base:
    """The revision to diff against. ``ref`` is None when no base exists (skip)."""

    ref: str | None
    how: str  # "merge-base" | "HEAD~1" | "skip"
    warning: str | None = None


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def repo_root(start: Path | None = None) -> Path:
    """The git top-level containing ``start`` (default cwd), else ``start`` itself."""
    start = (start or Path.cwd()).resolve()
    proc = _git(start, "rev-parse", "--show-toplevel")
    return Path(proc.stdout.strip()) if proc.returncode == 0 else start


def resolve_base(root: Path, upstream: str = "origin/main") -> Base:
    """Merge-base with ``upstream``, else ``HEAD~1``, else a skip with a warning."""
    proc = _git(root, "merge-base", "HEAD", upstream)
    if proc.returncode == 0 and proc.stdout.strip():
        return Base(proc.stdout.strip(), "merge-base")
    proc = _git(root, "rev-parse", "--verify", "--quiet", "HEAD~1^{commit}")
    if proc.returncode == 0 and proc.stdout.strip():
        return Base(proc.stdout.strip(), "HEAD~1")
    return Base(
        None,
        "skip",
        f"no merge-base with {upstream} and no HEAD~1; diff-against-base checks skipped",
    )


def show_file(root: Path, ref: str, path: str) -> str | None:
    """Contents of ``path`` (repo-relative, POSIX) at ``ref``, or None if absent there."""
    proc = _git(root, "show", f"{ref}:{path}")
    return proc.stdout if proc.returncode == 0 else None
