"""Persona cards (AC-14): FW-PER-001 and FW-PER-002.

Every persona in ``framework/personas.yaml`` has its own card, ``personas/<PER-ID>.md``
(FW-PER-001). Each card has the required H2 sections, none empty, and its ``## Citations``
section holds at least one ``uv run rmf refs show ...`` command, each of which resolves
the way FW-CITE-002 resolves a framework citation (FW-PER-002).
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path

from rmf_tool.findings import Finding
from rmf_tool.framework.citations import ERROR, Resolver, describe
from rmf_tool.framework.model import Entity, Framework

REQUIRED_SECTIONS = (
    "Responsibilities",
    "Decision authority",
    "Typical concerns",
    "What they know and don't know",
    "Question bank by step",
    "Artifacts owned-approved",
    "Role-play guidance",
    "Red lines",
    "Citations",
)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)
REFS_SHOW = re.compile(r"`uv run rmf refs show ([^`]+)`")


def card_path(persona: Entity) -> str:
    return f"personas/{persona.id}.md"


def _err(rule: str, persona: Entity, message: str, path: str | None,
         line: int | None) -> Finding:
    return Finding(rule, "E", f"{persona.id}: {message}", path, line)


def missing_cards(fw: Framework, root: Path) -> list[Finding]:
    """FW-PER-001: the persona names no card of its own, or the card file is missing."""
    out = []
    for p in fw.of("personas"):
        expected = card_path(p)
        card = p.data.get("card")
        loc = p.location
        if card != expected:
            out.append(_err("FW-PER-001", p, f"card is {card!r}; a persona's card is "
                            f"{expected}", loc.file, loc.line))
        elif not (root / expected).is_file():
            out.append(_err("FW-PER-001", p, f"no persona card at {expected}", loc.file,
                            loc.line))
    return out


def _sections(text: str) -> dict[str, tuple[int, str]]:
    """H2 title -> (line, body up to the next heading of any level)."""
    heads = list(HEADING.finditer(text))
    found: dict[str, tuple[int, str]] = {}
    for i, m in enumerate(heads):
        if len(m.group(1)) != 2:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        found.setdefault(m.group(2), (text.count("\n", 0, m.start()) + 1,
                                      text[m.end():end]))
    return found


def _citation(command: str) -> dict[str, object]:
    """``ID --section S`` or ``ID --page N --anchor A`` as a framework citation mapping."""
    args = shlex.split(" ".join(command.split()))
    if not args or args[0].startswith("-"):
        raise ValueError("no reference ID")
    citation: dict[str, object] = {"ref": args[0]}
    rest = iter(args[1:])
    for flag in rest:
        value = next(rest, None)
        if value is None or flag not in ("--section", "--page", "--anchor"):
            raise ValueError(f"unexpected argument {flag!r}")
        citation[flag[2:]] = int(value) if flag == "--page" else value
    return citation


def card_problems(fw: Framework, root: Path, resolver: Resolver) -> list[Finding]:
    """FW-PER-002: a missing or empty required section, or a citation that does not
    resolve. Personas without a card file are FW-PER-001's."""
    out = []
    for p in fw.of("personas"):
        rel = card_path(p)
        path = root / rel
        if p.data.get("card") != rel or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        sections = _sections(text)
        for name in REQUIRED_SECTIONS:
            if name not in sections:
                out.append(_err("FW-PER-002", p, f"missing section '## {name}'", rel, None))
            elif not sections[name][1].strip():
                out.append(_err("FW-PER-002", p, f"section '## {name}' is empty", rel,
                                sections[name][0]))
        if "Citations" not in sections:
            continue
        line, body = sections["Citations"]
        commands = list(REFS_SHOW.finditer(body))
        if not commands:
            out.append(_err("FW-PER-002", p, "'## Citations' has no `uv run rmf refs show "
                            "...` command", rel, line))
        for m in commands:
            where = line + body.count("\n", 0, m.start())
            try:
                citation = _citation(m.group(1))
            except ValueError as exc:
                out.append(_err("FW-PER-002", p, f"cannot parse `rmf refs show "
                                f"{m.group(1)}`: {exc}", rel, where))
                continue
            result = resolver.resolve(citation)
            if result.status == ERROR:
                out.append(_err("FW-PER-002", p, f"{describe(citation)}: {result.message}",
                                rel, where))
    return out


def optional_pdf_citations(fw: Framework, root: Path, resolver: Resolver) -> list[Finding]:
    """FW-CITE-003 for persona cards: a ``refs show`` command in ``## Citations`` that names
    a PDF marked ``required: false``."""
    out = []
    for p in fw.of("personas"):
        rel = card_path(p)
        path = root / rel
        if p.data.get("card") != rel or not path.is_file():
            continue
        section = _sections(path.read_text(encoding="utf-8")).get("Citations")
        if section is None:
            continue
        line, body = section
        for m in REFS_SHOW.finditer(body):
            try:
                ref = str(_citation(m.group(1))["ref"])
            except ValueError:
                continue
            entry = resolver.entry(ref)
            if entry is not None and entry["kind"] == "pdf" and not entry["required"]:
                out.append(_err("FW-CITE-003", p, f"cites {ref}, a PDF marked required: "
                                "false; mark it required (after import) or drop the citation",
                                rel, line + body.count("\n", 0, m.start())))
    return out
