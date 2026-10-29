"""Interview rules: INT-001 (transcript structure, plan §7.4) and HYB-003 (human answers
against ``run.yaml:humans``). Respondent and tag values themselves are HYB-001.

INT-001 reads an unquoted YAML date (``date: 2026-10-29``) as the ISO string it denotes, and
leaves the free-text ``Control focus:`` alone (nothing consumes it).
"""

from __future__ import annotations

import datetime as dt
import re

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run.interviews import Interview

FILE_NAME = re.compile(r"^(INT-\d{3})-([PCSIARM]-\d{1,2})-(PER-[A-Z0-9]+)\.md$")


def _persona(interview: Interview, asked_of: str | None) -> str | None:
    return asked_of or (interview.front or {}).get("persona")


def interviews_wellformed(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out: list[RunFinding] = []
    seen_ids: dict[str, str] = {}
    seen_answers: dict[str, str] = {}
    for interview in ctx.interviews:
        rel = interview.rel
        owners = {interview.task} if interview.task in run.tasks else None

        def err(message: str, line: int | None = None, rel: str = rel,
                owners: set[str] | None = owners) -> None:
            out.append(make("INT-001", message, rel, line, owners))

        front = interview.front
        if front is None:
            err(interview.error or "no front-matter", 1)
            continue
        front = {k: v.isoformat() if isinstance(v, dt.date) else v for k, v in front.items()}
        for e in run.schema_errors("interview", front):
            err(f"front-matter {e}", 1)
        iid, task, persona = front.get("interview_id"), front.get("task"), front.get("persona")
        if task not in run.tasks:
            err(f"unknown task {task!r}", 1)
        if persona not in run.personas:
            err(f"unknown persona {persona!r}", 1)
        if front.get("run_id") != run.run_id:
            err(f"run_id {front.get('run_id')!r} is not this run ({run.run_id})", 1)
        name = FILE_NAME.match(rel.rsplit("/", 1)[-1])
        if name is None:
            err("file name must be INT-###-<task>-<persona>.md", 1)
        elif name.groups() != (iid, task, persona):
            err(f"file name says {'-'.join(name.groups())}; front-matter says "
                f"{iid}-{task}-{persona}", 1)
        if iid in seen_ids:
            err(f"interview_id {iid} also used by {seen_ids[iid]}", 1)
        elif iid:
            seen_ids[iid] = rel
        if not interview.answers:
            err("no answers (### Qn {#INT-###.Qn} then **An {#INT-###.An}** ...)")
        for a in interview.answers:
            prefix, _, num = a.id.partition(".A")
            if prefix != iid:
                err(f"answer {a.id} does not belong to {iid}", a.line)
            if a.id in seen_answers:
                err(f"answer {a.id} also in {seen_answers[a.id]}", a.line)
            seen_answers.setdefault(a.id, rel)
            if a.question_id is None:
                err(f"answer {a.id} has no question heading above it", a.line)
            elif a.question_id != f"{prefix}.Q{num}":
                err(f"answer {a.id} sits under question {a.question_id}", a.line)
            if a.asked_of is None:
                err(f"question for {a.id} has no 'Asked of:' line", a.line)
            elif a.asked_of not in run.personas:
                err(f"question for {a.id} is asked of unknown persona {a.asked_of}", a.line)
            if a.task is not None and a.task != task:
                err(f"question for {a.id} names task {a.task}; the interview is for {task}",
                    a.line)
    return out


def humans_crosscheck(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    humans = run.config.get("humans") or {}
    out: list[RunFinding] = []
    for interview in ctx.interviews:
        owners = {interview.task} if interview.task in run.tasks else None
        for a in interview.answers:
            persona = _persona(interview, a.asked_of)
            respondent, fallback = a.fields.get("respondent"), a.fields.get("fallback")
            listed = humans.get(persona) if isinstance(humans, dict) else None
            if respondent == "human" and run.mode != "hybrid":
                problem = f"answer {a.id} is from a human, but the run is {run.mode}"
            elif respondent == "human" and not listed:
                problem = (f"answer {a.id} is from a human, but {persona} has no named person "
                           "in run.yaml humans")
            elif fallback is not None and not listed:
                problem = (f"answer {a.id} has fallback {fallback}, but {persona} has no named "
                           "person in run.yaml humans")
            elif respondent == "simulated" and listed and fallback != "human-unavailable":
                problem = (f"answer {a.id} simulates {persona}, who is a listed human "
                           f"({listed}); ask them, or mark fallback: human-unavailable")
            else:
                continue
            out.append(make("HYB-003", problem, interview.rel, a.line, owners))
    return out
