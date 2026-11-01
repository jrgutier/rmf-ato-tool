"""The NIST task pin: the Chapter 3 task blocks of SP 800-37r2 as data.

``parse`` reads the 47 ``TASK`` sections of the committed text extraction into
``conformance/nist-tasks.yaml``: Potential Inputs, Expected Outputs, Primary Responsibility,
Supporting Roles and the SDLC phase line. The text is what the document says, so a phrase is
kept as printed apart from the repairs below.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rmf_tool.framework.model import TASKS_80037

REF = "SP800-37R2"
TEXT_PATH = "references/text/SP800-37R2.md"
FIELDS = ("inputs", "outputs", "primary", "supporting")

_PAGE = re.compile(r"^<!-- page (\d+)(?: [^>]*)? -->$")
_TASK = re.compile(r"^#+ TASK ([PCSIARM]-\d{1,2})$")
_LABELS = {
    "Potential Inputs": "inputs",
    "Expected Outputs": "outputs",
    "Primary Responsibility": "primary",
    "Supporting Roles": "supporting",
    "Supporting Role": "supporting",
    "System Development Life Cycle Phase": "sdlc",
    "Discussion": None,
    "References": None,
}
_LABEL = re.compile(r"^(" + "|".join(_LABELS) + r"):\s*(.*)$")
_FOOTNOTE = re.compile(r"^\d{2,3} [A-Z\[]")
_NOTE_MARK = re.compile(r"(?<=[a-z.,;)])\d{2,3}(?=[\s;.,]|$)")
_SDLC = re.compile(r"(New|Existing)\s*[–—-]\s*(.*?)(?:[.;]?\s*(?=Existing)|\.?$)")


class PinError(Exception):
    """The Chapter 3 task blocks cannot be read."""


@dataclass
class TaskBlock:
    id: str
    page: int
    fields: dict[str, list[str]] = field(default_factory=dict)


def _clean(value: str) -> str:
    return _NOTE_MARK.sub("", " ".join(value.split()))


def phrases(value: str) -> list[str]:
    """The semicolon-separated phrases of a field, without the closing period."""
    return [p.strip().removesuffix(".").strip() for p in _clean(value).split(";") if p.strip()]


def sdlc(value: str) -> dict[str, list[str]]:
    """``New – A, B. Existing – C.`` as ``{new: [A, B], existing: [C]}``; the citation notes
    of framework/tasks use the same form with a semicolon."""
    parsed: dict[str, list[str]] = {}
    for kind, stages in _SDLC.findall(_clean(value)):
        parsed[kind.casefold()] = [s.strip() for s in re.split(r"[,;]", stages) if s.strip()]
    return parsed


def _blocks(text: str) -> list[tuple[str, int, list[str]]]:
    """(task, page, body lines) of each ``### TASK`` heading from Chapter 3 on. A heading
    can repeat in a figure (P-3, section ``TASK P-3``); the last occurrence is the task."""
    found: dict[str, tuple[int, list[str]]] = {}
    current: list[str] | None = None
    page = 0
    for line in text.splitlines():
        m = _PAGE.match(line)
        if m:
            page = int(m.group(1))
        task = _TASK.match(line)
        if task:
            current = []
            found[task.group(1)] = (page, current)
        elif current is not None:
            if line.startswith("#"):
                current = None
            else:
                current.append(line)
    return [(task, page, lines) for task, (page, lines) in found.items()]


def _fields(lines: list[str]) -> dict[str, str]:
    """Field label -> value. A value runs over page breaks and stops at the next label; a
    footnote at the foot of a page is skipped until the blank line that ends it."""
    values: dict[str, list[str]] = {}
    label: str | None = None
    in_footnote = False
    for raw in lines:
        line = raw.strip()
        if _PAGE.match(line):
            in_footnote = False
            continue
        if not line:
            in_footnote = False
            continue
        if in_footnote:
            continue
        m = _LABEL.match(line)
        if m:
            label = _LABELS[m.group(1)]
            if label is None:
                continue
            values.setdefault(label, []).append(m.group(2))
            continue
        if _FOOTNOTE.match(line):
            in_footnote = True
            continue
        if label is not None:
            values[label].append(line)
    return {k: " ".join(v) for k, v in values.items()}


def parse(text: str) -> list[dict[str, Any]]:
    """Every task of TASKS_80037 in order. Raises PinError on a missing task or field."""
    blocks = {task: (page, _fields(lines)) for task, page, lines in _blocks(text)}
    missing = [t for t in TASKS_80037 if t not in blocks]
    if missing:
        raise PinError(f"{REF}: no task block for {', '.join(missing)}")
    out = []
    for task in TASKS_80037:
        page, values = blocks[task]
        lacking = [k for k in ("inputs", "outputs", "primary") if not values.get(k)]
        if lacking:
            raise PinError(f"{REF}: TASK {task} has no {', '.join(lacking)}")
        item: dict[str, Any] = {
            "id": task,
            "page": page,
            "inputs": phrases(values["inputs"]),
            "outputs": phrases(values["outputs"]),
            "primary": phrases(values["primary"]),
            "supporting": phrases(values.get("supporting", "")),
        }
        if "sdlc" in values:
            item["sdlc"] = sdlc(values["sdlc"])
        out.append(item)
    return out


def parse_repo(repo: Path) -> list[dict[str, Any]]:
    return parse((repo / TEXT_PATH).read_text(encoding="utf-8"))
