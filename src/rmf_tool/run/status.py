"""`rmf status` (plan §7.3): task completion derived from disk.

T is done iff (1) every output exists and lists T in ``touched_by`` (the producer also as
``produced_by_task``), (2) every ``writes_facts`` field has ``set_by_task: T``, (3) there
are at least ``min_interviews`` interviews for T, and (4) no error-severity finding owned
by T comes from a rule whose ``applies_after`` is at or before T. JOURNAL-001 follows
completion (the CHECKPOINT is written after the task passes), so it is not a criterion.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.catalog import family
from rmf_tool.check import rules_by_id
from rmf_tool.check.findings import RunFinding
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import frontmatter, interviews, scope
from rmf_tool.run.model import Run, YamlError

FAMILY_TASKS = {"S-4": "ssp", "A-3": "sar"}  # next action refined per control family
SSP_DIR = "artifacts/ssp/controls"
SAR_DIR = "artifacts/sar/results"


@dataclass
class TaskStatus:
    id: str
    name: str
    state: str  # scope state: active | out-of-scope | deferred | lifecycle
    rationale: str | None
    done: bool
    missing: list[str] = field(default_factory=list)


@dataclass
class Status:
    run_id: str
    mode: str
    tasks: dict[str, TaskStatus]
    next: str | None
    family: str | None
    baseline: int
    statements: int
    determinations: int

    @property
    def done(self) -> bool:
        return self.next is None

    @property
    def done_tasks(self) -> set[str]:
        return {t for t, s in self.tasks.items() if s.done}


def gate_open(run: Run, rule: str, limit: int) -> bool:
    """A rule applies at topological position ``limit`` once its applies_after is reached."""
    after = rules_by_id()[rule].applies_after
    return after is None or run.position.get(after, len(run.order)) <= limit


def _controls(run: Run, directory: str, key: str) -> set[str]:
    out: set[str] = set()
    for path in sorted(run.path(directory).glob("*.yaml")):
        try:
            data = run.data(run.rel(path))
        except YamlError:
            continue
        for item in (data or {}).get(key) or [] if isinstance(data, dict) else []:
            if isinstance(item, dict) and item.get("control_id"):
                out.add(str(item["control_id"]))
    return out


def family_gaps(run: Run) -> dict[str, dict[str, list[str]]]:
    """Per baseline family: controls without an SSP statement and without a SAR determination."""
    stated = _controls(run, SSP_DIR, "controls")
    determined = _controls(run, SAR_DIR, "determinations")
    gaps: dict[str, dict[str, list[str]]] = {}
    for cid in baseline_mod.control_ids(run):
        entry = gaps.setdefault(family(cid), {"ssp": [], "sar": []})
        if cid not in stated:
            entry["ssp"].append(cid)
        if cid not in determined:
            entry["sar"].append(cid)
    return gaps


def _artifact_problems(run: Run, task: str) -> list[str]:
    problems = []
    for aid in run.tasks[task].get("outputs") or []:
        art = run.artifacts.get(aid, {})
        if art.get("generated"):
            if not any(run.path(d["path"]).is_file() for d in art.get("data") or []):
                problems.append(f"{aid} not generated")
            continue
        md = run.artifact_md(aid)
        if not md.is_file():
            problems.append(f"{aid} missing ({run.rel(md)})")
            continue
        data: Any = frontmatter.parse(md.read_text(encoding="utf-8")).data or {}
        if task not in (data.get("touched_by") or []):
            problems.append(f"{aid} touched_by does not list {task}")
        if art.get("producer") == task and data.get("produced_by_task") != task:
            problems.append(f"{aid} produced_by_task is not {task}")
    return problems


def derive(run: Run, findings: list[RunFinding]) -> Status:
    scopes = scope.task_scopes(run)
    facts = facts_mod.load(run)
    counts: dict[str, int] = {}
    for interview in interviews.load_all(run):
        if interview.task:
            counts[interview.task] = counts.get(interview.task, 0) + 1
    tasks: dict[str, TaskStatus] = {}
    for t in run.order:
        task, sc = run.tasks[t], scopes[t]
        missing: list[str] = []
        if sc.state == scope.ACTIVE:
            missing += _artifact_problems(run, t)
            missing += [f"fact {f} not set_by {t}" for f in task.get("writes_facts") or []
                        if facts_mod.set_by(facts, f) != t]
            need = int(task.get("min_interviews") or 0)
            if counts.get(t, 0) < need:
                missing.append(f"{counts.get(t, 0)}/{need} interview(s)")
            errors: dict[str, int] = {}
            for f in findings:
                if f.error and t in f.owners and gate_open(run, f.rule, run.position[t]):
                    errors[f.rule] = errors.get(f.rule, 0) + 1
            missing += [f"{rule}: {n} error(s)" for rule, n in sorted(errors.items())]
        tasks[t] = TaskStatus(t, task.get("name", ""), sc.state, sc.rationale,
                              sc.state == scope.ACTIVE and not missing, missing)
    nxt = next((t for t in run.order if tasks[t].state == scope.ACTIVE and not tasks[t].done
                and all(tasks[d].done or tasks[d].state != scope.ACTIVE
                        for d in run.tasks[t].get("depends_on") or [] if d in tasks)), None)
    fam = None
    gaps = family_gaps(run)
    if nxt in FAMILY_TASKS:
        kind = FAMILY_TASKS[nxt]
        fam = next((f for f, g in gaps.items() if g[kind]), None)
    controls = baseline_mod.control_ids(run)
    return Status(
        run.run_id, run.mode, tasks, nxt, fam, len(controls),
        statements=len(_controls(run, SSP_DIR, "controls") & set(controls)),
        determinations=len(_controls(run, SAR_DIR, "determinations") & set(controls)),
    )


def to_json(run: Run, st: Status, gaps: bool = False) -> dict[str, Any]:
    active = [s for s in st.tasks.values() if s.state == scope.ACTIVE]
    out: dict[str, Any] = {
        "now": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ"),  # for journal entries
        "run_id": st.run_id,
        "mode": st.mode,
        "done": st.done,
        "next": None if st.next is None else {
            "task": st.next, "name": st.tasks[st.next].name,
            "step": st.next.split("-")[0],
            "playbook": run.tasks[st.next].get("playbook"),
            **({"family": st.family} if st.family else {}),
        },
        "counts": {"active": len(active), "done": sum(s.done for s in active),
                   "deferred": len(st.tasks) - len(active)},
        "ssp": {"baseline": st.baseline, "statements": st.statements},
        "sar": {"baseline": st.baseline, "determinations": st.determinations},
        "tasks": [{"id": s.id, "name": s.name, "state": s.state, "done": s.done,
                   "missing": s.missing, **({"rationale": s.rationale} if s.rationale else {})}
                  for s in st.tasks.values()],
    }
    if gaps:
        out["family_gaps"] = {f: g for f, g in family_gaps(run).items() if g["ssp"] or g["sar"]}
    return out


def compute(run: Run) -> Status:
    from rmf_tool.check import engine

    return engine.evaluate(run).status
