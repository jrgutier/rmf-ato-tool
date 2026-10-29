"""JOURNAL-001 (plan §8): ``journal.md`` is well formed and every done task has a CHECKPOINT.

    # Journal — <run-id>
    ## 2026-11-05T14:02Z · CHECKPOINT · task C-2
    ## 2026-11-05T15:40Z · RETRY · task S-4 · lesson: L-0012
"""

from __future__ import annotations

import re

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run.model import JOURNAL_FILE

RULE = "JOURNAL-001"
TITLE = re.compile(r"^# Journal — (\S+)\s*$")
ENTRY = re.compile(
    r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z) · "
    r"(?P<type>CHECKPOINT|DECISION|RETRY|CORRECTION|NOTE) · "
    r"(?P<subject>task [PCSIARM]-\d{1,2}|artifact ART-[A-Z]+(?:-[A-Z]+)*|run)"
    r"(?P<extra>(?: · [a-z][a-z_ ]*: \S.*?)*)\s*$"
)


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
            out.append(make(RULE, "malformed entry; expected '## <YYYY-MM-DDTHH:MMZ> · "
                            "<CHECKPOINT|DECISION|RETRY|CORRECTION|NOTE> · task <T>|artifact "
                            "<ART>|run[ · key: value]'", JOURNAL_FILE, lineno))
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
