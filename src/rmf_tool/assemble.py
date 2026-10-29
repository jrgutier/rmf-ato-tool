"""`rmf assemble`: fill the CLI-owned marker blocks in a run's artifact Markdown.

    <!-- BEGIN rmf:facts -->
    ...generated from facts.yaml...
    <!-- END rmf:facts -->

``facts`` is the only marker; any other ``rmf:`` marker is an error. Front-matter and
prose never restate facts (INV-4): the block is the one place they appear in Markdown.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import ARTIFACTS_DIR, Run

BLOCK = re.compile(
    r"(<!-- BEGIN rmf:(?P<name>[a-z-]+) -->\n)(?P<body>.*?)(<!-- END rmf:(?P=name) -->)", re.S)
ANY_MARKER = re.compile(r"<!-- (BEGIN|END) rmf:([a-z-]+)[^>]*-->")


class AssembleError(Exception):
    pass


def facts_block(facts: dict[str, Any]) -> str:
    rows = [(label, facts_mod.display(facts, key), facts_mod.set_by(facts, key))
            for key, label in facts_mod.LABELS.items()]
    rows = [r for r in rows if r[1] is not None]
    if not rows:
        return "_No system facts are set yet (facts.yaml)._\n"
    lines = ["| Fact | Value | Set by |", "|---|---|---|"]
    lines += [f"| {label} | {val} | {by or '?'} |" for label, val, by in rows]
    return "\n".join(lines) + "\n"


def renderers(run: Run) -> dict[str, Callable[[], str]]:
    facts = facts_mod.load(run)
    return {"facts": lambda: facts_block(facts)}


def assemble_text(text: str, blocks: dict[str, Callable[[], str]], where: str) -> str:
    for m in ANY_MARKER.finditer(text):
        if m.group(2) not in blocks:
            raise AssembleError(f"{where}: unknown marker rmf:{m.group(2)}")
    begins = len(re.findall(r"<!-- BEGIN rmf:", text))
    if begins != len(BLOCK.findall(text)) or begins != len(re.findall(r"<!-- END rmf:", text)):
        raise AssembleError(f"{where}: unbalanced rmf marker (each BEGIN line needs its END)")
    return BLOCK.sub(lambda m: m.group(1) + blocks[m.group("name")]() + m.group(4), text)


def assembled(run: Run) -> dict[str, tuple[str, str]]:
    """run-relative path -> (current text, assembled text) for every artifact Markdown."""
    blocks = renderers(run)
    out = {}
    for path in sorted((run.dir / ARTIFACTS_DIR).glob("*.md")):
        rel = run.rel(path)
        text = path.read_text(encoding="utf-8")
        out[rel] = (text, assemble_text(text, blocks, rel))
    return out


def write(run: Run) -> list[str]:
    """Assemble in place; returns the files that changed."""
    changed = []
    for rel, (old, new) in assembled(run).items():
        if old != new:
            run.path(rel).write_text(new, encoding="utf-8")
            changed.append(rel)
    return changed
