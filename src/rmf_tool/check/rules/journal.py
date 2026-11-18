"""JOURNAL-001 (plan §8): ``journal.md`` is well formed and every done task has a CHECKPOINT.
LES-001: every RETRY and CORRECTION cites a lesson that exists in docs/LESSONS.md, or says
``lesson: none — <reason>``.

    # Journal — <run-id>
    ## 2026-11-05T14:02Z · CHECKPOINT · task C-2
    ## 2026-11-05T15:40Z · RETRY · task S-4 · lesson: L-0012
    ## 2026-11-05T16:30Z · CORRECTION · artifact ART-SAR · lesson: none — typo only
"""

from __future__ import annotations

import re

from rmf_tool import lessons
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run.model import JOURNAL_FILE

RULE = "JOURNAL-001"
LESSON = re.compile(r"(?:^| · )lesson: (?:(?P<id>L-\d{4})|none — \S.*?)(?= · |$)")
TITLE = re.compile(r"^# Journal — (\S+)\s*$")
ENTRY = re.compile(
    r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z) · "
    r"(?P<type>CHECKPOINT|DECISION|RETRY|CORRECTION|NOTE) · "
    r"(?P<subject>task [PCSIARM]-\d{1,2}|artifact ART-[A-Z]+(?:-[A-Z]+)*|run)"
    r"(?P<extra>(?: · [a-z][a-z_ ]*: \S.*?)*)\s*$"
)


def _diagnose(line: str) -> str:
    """The first part of an entry header that does not match (F-09-8)."""
    parts = line[3:].split(" · ")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z", parts[0].strip()):
        return f"the time {parts[0].strip()!r} is not YYYY-MM-DDTHH:MMZ"
    if len(parts) < 2 or parts[1].strip() not in ("CHECKPOINT", "DECISION", "RETRY",
                                                     "CORRECTION", "NOTE"):
        return f"the type {parts[1].strip() if len(parts) > 1 else ''!r} is unknown"
    if len(parts) < 3 or not re.fullmatch(
            r"task [PCSIARM]-\d{1,2}|artifact ART-[A-Z]+(?:-[A-Z]+)*|run", parts[2].strip()):
        return (f"the scope {parts[2].strip() if len(parts) > 2 else ''!r} is not 'task T', "
                "'artifact ART-X' or 'run'")
    return "a trailing part is not 'key: value'"


def journal(ctx: Context, done: set[str]) -> list[RunFinding]:
    run = ctx.run
    path = run.path(JOURNAL_FILE)
    if not path.is_file():
        return [make(RULE, "journal.md missing (rmf run init creates it)", JOURNAL_FILE)]
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[RunFinding] = []
    title = TITLE.match(lines[0]) if lines else None
    if title is None:
        out.append(make(RULE, f"line 1 must be '# Journal — {run.run_id}'", JOURNAL_FILE, 1))
    elif title.group(1) != run.run_id:
        out.append(make(RULE, f"journal is for run {title.group(1)}, not {run.run_id}",
                        JOURNAL_FILE, 1))
    checkpoints: set[str] = set()
    for lineno, line in enumerate(lines, start=1):
        if not line.startswith("## "):
            continue
        m = ENTRY.match(line)
        if m is None:
            out.append(make(RULE, f"malformed entry ({_diagnose(line)}); expected '## "
                            "<YYYY-MM-DDTHH:MMZ> · <CHECKPOINT|DECISION|RETRY|CORRECTION|NOTE> · "
                            "task <T>|artifact <ART>|run[ · key: value]'", JOURNAL_FILE, lineno))
            continue
        if m.group("type") == "CHECKPOINT":
            if not m.group("subject").startswith("task "):
                out.append(make(RULE, "a CHECKPOINT names a task", JOURNAL_FILE, lineno))
            else:
                checkpoints.add(m.group("subject")[5:])
    for task in run.order:
        if task in done and task not in checkpoints:
            out.append(make(RULE, f"{task} is done but has no CHECKPOINT entry", JOURNAL_FILE,
                            None, {task}))
    return out


def lesson_refs(ctx: Context) -> list[RunFinding]:
    path = ctx.run.path(JOURNAL_FILE)
    if not path.is_file():
        return []  # JOURNAL-001
    try:
        known = {e.id for e in lessons.parse(
            (ctx.run.repo / lessons.LESSONS_PATH).read_text(encoding="utf-8"))[0]}
    except OSError:
        known = None
    out: list[RunFinding] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = ENTRY.match(line)
        if m is None or m.group("type") not in ("RETRY", "CORRECTION"):
            continue
        ref = LESSON.search(m.group("extra"))
        if ref is None:
            problem = (f"{m.group('type')} without 'lesson: L-NNNN' or "
                       "'lesson: none — <reason>'")
        elif ref.group("id") and known is not None and ref.group("id") not in known:
            problem = f"{m.group('type')} cites {ref.group('id')}, which is not in docs/LESSONS.md"
        else:
            continue
        out.append(make("LES-001", problem, JOURNAL_FILE, lineno))
    return out
