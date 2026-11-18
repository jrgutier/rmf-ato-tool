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
from rmf_tool import labels
from rmf_tool.catalog import family
from rmf_tool.check import rules_by_id
from rmf_tool.check.findings import RunFinding
from rmf_tool.run import clock, frontmatter, interviews, scope
from rmf_tool.run import facts as facts_mod
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
        shown = labels.named(aid, art.get("name", ""))
        if art.get("generated"):
            # the CLI's own output (schema null), not data an agent writes beside it
            made = [d for d in art.get("data") or [] if d.get("schema") is None]
            if not any(run.path(d["path"]).is_file() for d in made):
                problems.append(f"{shown} not generated")
            continue
        md = run.artifact_md(aid)
        if not md.is_file():
            problems.append(f"{shown} missing ({run.rel(md)})")
            continue
        data: Any = frontmatter.parse(md.read_text(encoding="utf-8")).data or {}
        if task not in (data.get("touched_by") or []):
            problems.append(f"{aid} touched_by does not list {task}")
        if art.get("producer") == task and data.get("produced_by_task") != task:
            problems.append(f"{aid} produced_by_task is not {task}")
    return problems


# Rules that stay quiet until the task touches its output, so the status line would not show
# them before the task starts (F-14-2): (task, rule, data file, key, what is owed).
QUIET_OWED = (("A-4", "PASM-002", "artifacts/data/sar-report.yaml", "privacy",
               "the privacy assessment results for the AO (sar-report.yaml privacy)"),)


def _processes_pii(run: Run) -> bool:
    try:
        data = run.data("artifacts/data/infotypes.yaml")
    except (YamlError, OSError):
        return False
    items = data.get("information_types") if isinstance(data, dict) else None
    return any(isinstance(i, dict) and i.get("privacy") is True for i in items or ())


def _quiet_owed(run: Run, task: str) -> list[tuple[str, str]]:
    out = []
    for t, rule, rel, key, what in QUIET_OWED:
        if t != task or not run.holds("0.2.0") or not _processes_pii(run):
            continue
        try:
            data = run.data(rel) if run.path(rel).is_file() else None
        except YamlError:
            data = None
        if not (isinstance(data, dict) and data.get(key)):
            out.append((rule, f"{rule}: owes {what}"))
    return out


def reached(run: Run, task: str) -> bool:
    """Progress, not scope: every active task before ``task`` has written its outputs, so a
    decision recorded at ``task`` cannot precede the work it rests on."""
    active = set(scope.active_tasks(run))
    return not any(_artifact_problems(run, t)
                   for t in run.ancestors.get(task, frozenset()) if t in active)


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
            missing += [f"fact {f} not set_by {t}" for f in run.writes_facts(t)
                        if facts_mod.set_by(facts, f) != t]
            need = int(task.get("min_interviews") or 0)
            if counts.get(t, 0) < need:
                missing.append(f"{counts.get(t, 0)}/{need} interview(s)")
            errors: dict[str, int] = {}
            for f in findings:
                if f.error and t in f.owners and gate_open(run, f.rule, run.position[t]):
                    errors[f.rule] = errors.get(f.rule, 0) + 1
            missing += [f"{rule}: {n} error(s)" for rule, n in sorted(errors.items())]
            missing += [m for rule, m in _quiet_owed(run, t) if rule not in errors]
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


DECISION_TASK = "R-4"


def decision_floor(run: Run) -> tuple[dt.date | None, list[str]]:
    """The earliest date an authorization decision may carry, by the run's own records, and
    why (F-15-1): the run's date, the PIA approval (PRIV-003) and the latest scheduled
    completion of a POA&M item recommended before authorization (MPOA-001)."""

    def day(value: Any) -> dt.date | None:
        try:
            return dt.date.fromisoformat(str(value))
        except ValueError:
            return None

    def read(rel: str) -> Any:
        try:
            return run.data(rel) if run.path(rel).is_file() else None
        except YamlError:
            return None

    found: list[tuple[dt.date, str]] = []
    if (now := clock.today(run.config)) is not None:
        found.append((now, "the run's date"))
    pia = read("artifacts/data/pia.yaml")
    if isinstance(pia, dict) and pia.get("status", "approved") == "approved":
        approved = day((pia.get("approval") or {}).get("date"))
        if approved:
            found.append((approved, "the PIA approval (PRIV-003)"))
    poam = read("artifacts/poam/items.yaml")
    for item in (poam.get("items") or []) if isinstance(poam, dict) else []:
        if isinstance(item, dict) and item.get("recommended_completion") == "before-authorization":
            when = day(item.get("scheduled_completion"))
            if when:
                found.append((when, f"{item.get('id')} (MPOA-001)"))
    if not found:
        return None, []
    floor = max(d for d, _ in found)
    return floor, [why for d, why in found if d == floor]


def _floor(run: Run, task: str) -> dict[str, Any]:
    if task != DECISION_TASK:
        return {}
    floor, why = decision_floor(run)
    return {"not_before": {"date": floor.isoformat(), "because": why}} if floor else {}


def to_json(run: Run, st: Status, gaps: bool = False) -> dict[str, Any]:
    active = [s for s in st.tasks.values() if s.state == scope.ACTIVE]
    out: dict[str, Any] = {
        "now": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%MZ"),  # for journal entries
        "run_id": st.run_id,
        "mode": st.mode,
        "done": st.done,
        "next": None if st.next is None else {
            "task": st.next, "name": st.tasks[st.next].name,
            "label": labels.task_label(st.next, st.tasks[st.next].name, run.repo),
            "step": st.next.split("-")[0],
            "playbook": run.tasks[st.next].get("playbook"),
            **({"family": st.family} if st.family else {}),
            **_floor(run, st.next),
        },
        "counts": {"active": len(active), "done": sum(s.done for s in active),
                   "deferred": len(st.tasks) - len(active)},
        "ssp": {"baseline": st.baseline, "statements": st.statements},
        "sar": {"baseline": st.baseline, "determinations": st.determinations},
        "tasks": [{"id": s.id, "name": s.name,
                   "label": labels.task_label(s.id, s.name, run.repo),
                   "state": s.state, "done": s.done,
                   "missing": s.missing, **({"rationale": s.rationale} if s.rationale else {})}
                  for s in st.tasks.values()],
    }
    if gaps:
        out["family_gaps"] = {f: g for f, g in family_gaps(run).items() if g["ssp"] or g["sar"]}
    return out


def compute(run: Run) -> Status:
    from rmf_tool.check import engine

    return engine.evaluate(run).status
