"""DOC-001: AGENTS.md has the fixed sections, fits in 250 lines, and its CLI section
lists exactly the registered commands (plan §8)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from rmf_tool.findings import Finding

AGENTS_PATH = "AGENTS.md"
MAX_LINES = 250
SECTIONS = (
    "Purpose",
    "Repo layout",
    "Invariants",
    "CLI commands",
    "Fork workflow",
    "Run protocol pointer",
    "Learned rules",
    "Bumping OSCAL / references",
)
INVARIANT_COUNT = 8

_CODE = re.compile(r"`rmf ([^`]*)`")
_WORD = re.compile(r"^[a-z][a-z0-9-]*$")
_LR = re.compile(r"^- LR-\d{2,}: \S.* \(from L-\d{4}\)$")


def command_paths(command: Any, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    """Every visible group and leaf command path below ``command``, the object returned
    by ``typer.main.get_command(app)``. Typer >= 0.26 vendors Click, so groups are
    recognised by their ``commands`` mapping rather than by a Click class (L-0009)."""
    paths: set[tuple[str, ...]] = set()
    for name, sub in getattr(command, "commands", {}).items():
        if getattr(sub, "hidden", False):
            continue
        paths.add((*prefix, name))
        paths |= command_paths(sub, (*prefix, name))
    return paths


def leaf_paths(command: Any) -> set[tuple[str, ...]]:
    paths = command_paths(command)
    return {p for p in paths if not any(q[: len(p)] == p and q != p for q in paths)}


def _sections(lines: list[str]) -> dict[str, tuple[int, list[str]]]:
    sections: dict[str, tuple[int, list[str]]] = {}
    name = None
    for lineno, line in enumerate(lines, start=1):
        if line.startswith("## "):
            name = line[3:].strip()
            sections[name] = (lineno, [])
        elif name is not None:
            sections[name][1].append(line)
    return sections


def documented_paths(section_lines: list[str]) -> set[tuple[str, ...]]:
    paths = set()
    for line in section_lines:
        for match in _CODE.finditer(line):
            words = []
            for token in match.group(1).split():
                if not _WORD.match(token):
                    break
                words.append(token)
            if words:
                paths.add(tuple(words))
    return paths


def check_text(text: str, cli: Any, path: str = AGENTS_PATH) -> list[Finding]:
    findings: list[Finding] = []

    def err(msg: str, line: int | None = None) -> None:
        findings.append(Finding("DOC-001", "E", msg, path, line))

    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        err(f"{len(lines)} lines; the limit is {MAX_LINES}")
    sections = _sections(lines)
    if tuple(sections) != SECTIONS:
        err(f"H2 sections must be exactly, in order: {' | '.join(SECTIONS)}")

    _, invariants = sections.get("Invariants", (0, []))
    ids = re.findall(r"\bINV-(\d+)\b", "\n".join(invariants))
    missing = [n for n in range(1, INVARIANT_COUNT + 1) if str(n) not in ids]
    if missing:
        err("Invariants section is missing " + ", ".join(f"INV-{n}" for n in missing))

    start, learned = sections.get("Learned rules", (0, []))
    for offset, line in enumerate(learned, start=1):
        if line.startswith("- LR-") and not _LR.match(line):
            err(f"learned rule must read '- LR-nn: <rule> (from L-NNNN)': {line!r}", start + offset)

    _, cli_lines = sections.get("CLI commands", (0, []))
    documented = documented_paths(cli_lines)
    registered = command_paths(cli)
    for p in sorted(documented - registered):
        err(f"CLI section documents unregistered command: rmf {' '.join(p)}")
    for p in sorted(leaf_paths(cli) - documented):
        err(f"registered command not documented in CLI section: rmf {' '.join(p)}")
    return findings


def check(root: Path, cli: Any) -> list[Finding]:
    file = root / AGENTS_PATH
    if not file.is_file():
        return [Finding("DOC-001", "E", "file not found", AGENTS_PATH)]
    return check_text(file.read_text(encoding="utf-8"), cli)
