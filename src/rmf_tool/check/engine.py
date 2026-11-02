"""`rmf check`: evaluate the run rules once, derive task status, then select findings.

Every rule runs over the whole run; selection then applies the plan §7.3 semantics:

- ``--final``: every finding (scope-awareness lives in the rules).
- ``--task T``: rules whose ``applies_after`` is at or before T, findings owned by T or
  run-wide. T's own missing CHECKPOINT is not demanded: the journal entry follows the pass.
- no option: rules whose ``applies_after`` lies before the next action, findings owned by
  tasks before it or run-wide; once the run is done this equals ``--final``.

DEGRADED-001 is non-suppressible (plan §7.6): every selection keeps it.
"""

from __future__ import annotations

from dataclasses import dataclass

from rmf_tool.check import rules_by_id
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules import IMPLEMENTED, JOURNAL_RULE, RULES, UNFILTERED
from rmf_tool.check.rules.journal import journal
from rmf_tool.findings import Finding
from rmf_tool.run import status as status_mod
from rmf_tool.run.model import INTERVIEWS_DIR, Run


@dataclass
class Evaluation:
    findings: list[RunFinding]
    status: status_mod.Status


def _owned(ctx: Context, f: RunFinding) -> RunFinding:
    if f.owners or f.run_wide or not f.finding.path:
        return f
    path = f.finding.path
    if path.startswith(f"{INTERVIEWS_DIR}/"):
        task = ctx.interview_task(path)
        owners = {task} if task else set()
    else:
        artifact = ctx.run.owner_artifact(path)
        owners = set(ctx.run.writers(artifact)) if artifact else set()
    return RunFinding(f.finding, frozenset(owners), f.family, f.run_wide)


def evaluate(run: Run) -> Evaluation:
    ctx = Context(run)
    registry = rules_by_id()
    if unlisted := sorted(set(RULES) - set(registry)):
        raise ValueError(f"rule(s) with no entry in registry.yaml: {', '.join(unlisted)}")
    findings = [_owned(ctx, f) for rid, rule in RULES.items() if run.holds(registry[rid].since)
                for f in rule(ctx)]
    st = status_mod.derive(run, findings)
    findings += journal(ctx, st.done_tasks)
    findings.sort(key=lambda f: (f.finding.path or "", f.finding.line or 0, f.rule,
                                 f.finding.message))
    return Evaluation(findings, st)


def select(run: Run, ev: Evaluation, task: str | None = None, family: str | None = None,
           rules: list[str] | None = None, final: bool = False) -> list[Finding]:
    pos = run.position
    chosen: list[RunFinding] = []
    for f in ev.findings:
        if final or (task is None and ev.status.next is None):
            keep = True
        elif task is not None:
            keep = status_mod.gate_open(run, f.rule, pos[task]) and (
                not f.owners or (task in f.owners and f.rule != JOURNAL_RULE))
        else:
            limit = pos[ev.status.next] - 1 if ev.status.next else len(pos)
            keep = status_mod.gate_open(run, f.rule, limit) and (
                not f.owners or any(pos.get(o, len(pos)) <= limit for o in f.owners))
        if keep and family is not None:
            keep = f.family == family
        if keep and rules:
            keep = f.rule in rules
        if keep or f.rule in UNFILTERED:
            chosen.append(f)
    return [f.finding for f in chosen]


def rules_run(rules: list[str] | None = None) -> list[str]:
    return [r for r in IMPLEMENTED if not rules or r in rules or r in UNFILTERED]
