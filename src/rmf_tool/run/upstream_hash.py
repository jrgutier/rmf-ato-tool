"""``upstream_hash`` (plan §4.4): which upstream files a run or an agent-lane result was
produced against.

sha256 over ``p.encode() + b"\\0" + bytes(p) + b"\\0"`` for each POSIX path ``p`` in
``sorted(set(expand(globs)))``. A glob ending in ``**`` matches every file below it;
dotfiles (``.DS_Store``, editor droppings) are ignored.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

# The tool itself. Not a bare ``src/**``: expand() skips only dot-prefixed parts, so that
# would hash __pycache__ and call every run stale after a Python upgrade or a test run.
SRC_GLOBS = ("src/**/*.py", "src/**/*.yaml", "src/**/*.json", "src/**/*.j2")
# run.yaml:upstream_hash for runs not created from a scenario (RUN-STALE-001).
UNION_GLOBS = ("AGENTS.md", "framework/**", "playbooks/**", "personas/**", "templates/**",
               *SRC_GLOBS)


def expand(root: Path, globs: Iterable[str]) -> list[str]:
    paths: set[str] = set()
    for pattern in globs:
        for match in root.glob(pattern):
            files = match.rglob("*") if match.is_dir() and pattern.endswith("**") else [match]
            for f in files:
                rel = f.relative_to(root)
                if f.is_file() and not any(part.startswith(".") for part in rel.parts):
                    paths.add(rel.as_posix())
    return sorted(paths)


def compute(root: Path, globs: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for rel in expand(root, globs):
        digest.update(rel.encode() + b"\0" + (root / rel).read_bytes() + b"\0")
    return digest.hexdigest()
