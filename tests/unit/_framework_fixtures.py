"""Shared helpers for the framework tests: the mini framework, negative-fixture overlays
and the profiles rmf validate runs under."""

from __future__ import annotations

import shutil
from pathlib import Path

from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.profiles import Profile

FIXTURES = REPO_ROOT / "tests" / "fixtures"
MINI = FIXTURES / "framework_mini"
NEG = FIXTURES / "framework_neg"
REAL = REPO_ROOT / "framework"

# p3a after p2x closed: every citation must resolve.
P3A = Profile("p3a", frozenset({"p1", "p2", "p2x", "p3a"}))
# p3a before p2x: citations to pending-acquisition references are deferred.
P3A_BEFORE_P2X = Profile("p3a", frozenset({"p1", "p2", "p3a"}))


def compose(overlay: Path, dest: Path, base: Path = MINI) -> Path:
    """Copy ``base`` to ``dest`` and lay the overlay's files over it (expect.yaml aside)."""
    shutil.copytree(base, dest)
    for src in overlay.rglob("*"):
        if src.is_file() and src.name != "expect.yaml":
            target = dest / src.relative_to(overlay)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, target)
    return dest


def expectation(overlay: Path) -> dict:
    return YAML(typ="safe").load((overlay / "expect.yaml").read_text(encoding="utf-8"))
