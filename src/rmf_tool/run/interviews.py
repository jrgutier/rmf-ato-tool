"""Interview transcripts (plan §7.4): ``interviews/INT-###-<task>-<persona>.md``.

Front-matter follows ``interview.schema.json``; each answer is parsed from

    ### Q3 {#INT-007.Q3}
    Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
    **A3 {#INT-007.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/a.md#b]]
    > Accounts are provisioned via ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from rmf_tool.run import frontmatter
from rmf_tool.run.model import INTERVIEWS_DIR, Run
from rmf_tool.run.trace import PROSE

QUESTION = re.compile(r"^###\s+Q(\d+)\s+\{#(INT-\d{3}\.Q\d+)\}\s*$")
ANSWER = re.compile(r"^\*\*A(\d+)\s+\{#(INT-\d{3}\.A\d+)\}\*\*\s*(.*)$")
SEP = re.compile(r"\s+·\s+")


@dataclass
class Answer:
    id: str
    line: int
    fields: dict[str, str]  # respondent, tag, fallback, ... as written
    basis: list[str]
    question_id: str | None = None
    asked_of: str | None = None
    task: str | None = None
    control_focus: str | None = None


@dataclass
class Interview:
    rel: str
    front: dict[str, Any] | None
    error: str | None
    answers: list[Answer] = field(default_factory=list)

    @property
    def task(self) -> str | None:
        return (self.front or {}).get("task")


def _pairs(text: str) -> dict[str, str]:
    out = {}
    for part in SEP.split(text.strip()):
        key, sep, val = part.partition(":")
        if sep:
            out[key.strip().lower().replace(" ", "_")] = val.strip()
    return out


def parse(rel: str, text: str) -> Interview:
    doc = frontmatter.parse(text)
    interview = Interview(rel, doc.data, doc.error)
    question: dict[str, str | None] = {}
    for lineno, line in enumerate(doc.body.splitlines(), start=doc.body_line):
        if m := QUESTION.match(line):
            question = {"id": m.group(2)}
        elif line.startswith("Asked of:") and question:
            question.update(_pairs(line))
        elif m := ANSWER.match(line):
            rest = m.group(3)
            basis = [t.strip() for t in PROSE.findall(rest)]
            interview.answers.append(Answer(
                id=m.group(2), line=lineno, fields=_pairs(PROSE.sub("", rest)), basis=basis,
                question_id=question.get("id"), asked_of=question.get("asked_of"),
                task=question.get("task"), control_focus=question.get("control_focus"),
            ))
    return interview


def load_all(run: Run) -> list[Interview]:
    out = []
    for path in sorted((run.dir / INTERVIEWS_DIR).glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            out.append(Interview(run.rel(path), None, f"cannot read: {exc}"))
            continue
        out.append(parse(run.rel(path), text))
    return out


def answer_ids(interviews: list[Interview]) -> set[str]:
    return {a.id for i in interviews for a in i.answers}
