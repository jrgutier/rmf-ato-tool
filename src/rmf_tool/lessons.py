"""docs/LESSONS.md checks: LES-002 (format, append-only) and LES-003 (no pending promotion).

Entry format (plan §8)::

    ## L-0012 · 2026-11-05 · run: uas-gcs/example-synthetic-01 · tags: ssp, trace
    - Symptom: ...
    - Root cause: ...
    - Fix: ...
    - Rule: ...
    - Promotion: AGENTS.md INV-8 | check: SSP-DUP-001 | LR-03 | none — <reason>

Text before the first entry is a free-form preamble. Headings inside fenced code
blocks are not entries.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

from rmf_tool.findings import Finding
from rmf_tool.gitutil import resolve_base, show_file

LESSONS_PATH = "docs/LESSONS.md"
FIELDS = ("Symptom", "Root cause", "Fix", "Rule", "Promotion")

_HEADER = re.compile(
    r"^## (?P<id>L-(?P<num>\d{4})) · (?P<date>\d{4}-\d{2}-\d{2}) · run: (?P<run>\S+)"
    r" · tags: (?P<tags>[a-z0-9-]+(?:, [a-z0-9-]+)*)$"
)
_FIELD = re.compile(r"^- (?P<key>[A-Za-z ]+): (?P<value>\S.*)$")
_PROMOTION = re.compile(
    r"^(?:AGENTS\.md (?:INV-\d+|LR-\d{2,})|LR-\d{2,}|check: \S.*|none — \S.*)$"
)


@dataclass
class Entry:
    id: str
    num: int
    date: dt.date | None
    line: int
    lines: list[str] = field(default_factory=list)
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return "\n".join(line.rstrip() for line in self.lines).rstrip()


def parse(text: str, path: str = LESSONS_PATH) -> tuple[list[Entry], list[Finding]]:
    """Split LESSONS.md into entries and report LES-002 format errors."""
    entries: list[Entry] = []
    findings: list[Finding] = []

    def err(msg: str, line: int) -> None:
        findings.append(Finding("LES-002", "E", msg, path, line))

    in_fence = False
    current: Entry | None = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        if current is None and line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            m = _HEADER.match(line)
            if not m:
                err(f"malformed entry header: {line!r}", lineno)
                current = None
                continue
            try:
                date = dt.date.fromisoformat(m["date"])
            except ValueError:
                err(f"invalid date {m['date']}", lineno)
                date = None
            current = Entry(m["id"], int(m["num"]), date, lineno, [line])
            entries.append(current)
            continue
        if current is None:
            continue  # preamble
        current.lines.append(line)
        if not line.strip():
            continue
        if line.startswith("  ") and current.fields:
            last = list(current.fields)[-1]
            current.fields[last] += " " + line.strip()
            continue
        m = _FIELD.match(line)
        if not m:
            err(f"{current.id}: unexpected line {line!r}", lineno)
            continue
        key = m["key"]
        if key not in FIELDS:
            err(f"{current.id}: unknown field {key!r}", lineno)
        elif key in current.fields:
            err(f"{current.id}: duplicate field {key!r}", lineno)
        else:
            current.fields[key] = m["value"]

    for entry in entries:
        if tuple(entry.fields) != FIELDS:
            err(
                f"{entry.id}: fields must be exactly {', '.join(FIELDS)} in that order "
                f"(found {', '.join(entry.fields) or 'none'})",
                entry.line,
            )
    return entries, findings


def check_format(text: str, path: str = LESSONS_PATH) -> list[Finding]:
    """LES-002 format, monotonic IDs and dates; LES-003 pending promotions."""
    entries, findings = parse(text, path)
    if not entries:
        findings.append(Finding("LES-002", "E", "no lesson entries found", path, None))
    prev: Entry | None = None
    for entry in entries:
        expected = 1 if prev is None else prev.num + 1
        if entry.num != expected:
            findings.append(
                Finding("LES-002", "E", f"{entry.id}: expected L-{expected:04d}", path, entry.line)
            )
        if prev and prev.date and entry.date and entry.date < prev.date:
            findings.append(
                Finding(
                    "LES-002", "E", f"{entry.id}: date precedes {prev.id}", path, entry.line
                )
            )
        promotion = entry.fields.get("Promotion")
        if promotion is not None:
            for part in (p.strip() for p in promotion.split("|")):
                if part.lower().startswith("pending"):
                    findings.append(
                        Finding(
                            "LES-003",
                            "E",
                            f"{entry.id}: 'Promotion: pending' must be triaged before merge",
                            path,
                            entry.line,
                        )
                    )
                elif not _PROMOTION.match(part):
                    findings.append(
                        Finding(
                            "LES-002",
                            "E",
                            f"{entry.id}: invalid promotion {part!r} (use AGENTS.md INV-n, "
                            "LR-nn, check: <rule|test>, or none — <reason>)",
                            path,
                            entry.line,
                        )
                    )
        prev = entry
    return findings


def check_append_only(current: str, base: str, path: str = LESSONS_PATH) -> list[Finding]:
    """LES-002: every entry present at the base must be unchanged and in place."""
    old, _ = parse(base, path)
    new, _ = parse(current, path)
    findings = []
    for i, entry in enumerate(old):
        if i >= len(new):
            findings.append(
                Finding("LES-002", "E", f"{entry.id} was removed (append-only)", path, None)
            )
        elif new[i].text != entry.text:
            findings.append(
                Finding(
                    "LES-002", "E", f"{entry.id} was modified (append-only)", path, new[i].line
                )
            )
    return findings


def check(root: Path) -> list[Finding]:
    """Run LES-002 and LES-003 on ``root/docs/LESSONS.md`` against ``resolve_base()``."""
    file = root / LESSONS_PATH
    if not file.is_file():
        return [Finding("LES-002", "E", "file not found", LESSONS_PATH, None)]
    current = file.read_text(encoding="utf-8")
    findings = check_format(current)
    base = resolve_base(root)
    if base.ref is None:
        findings.append(Finding("LES-002", "W", base.warning or "append check skipped"))
        return findings
    base_text = show_file(root, base.ref, LESSONS_PATH)
    if base_text is not None:
        findings += check_append_only(current, base_text)
    return findings
