"""The risk executive function P-2 describes, where a run enters the RMF, and how detection uses
threat intelligence and covers the assets: RISKX-001, ENTRY-001 and DETC-001.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope
from rmf_tool.run.model import RUN_FILE

ORG_FILE = "artifacts/data/org-context.yaml"
IR_FILE = "artifacts/data/incident-response.yaml"
CONMON_FILE = "artifacts/data/conmon.yaml"
P2, S4, S5 = "P-2", "S-4", "S-5"
RISK_ACTIVITIES = ("frame", "assess", "respond", "monitor")  # SP 800-39 2.1
FORUM_SCOPE = ("all-types-and-sources", "aggregated-risk")
AUDIENCES = ("internal-stakeholders", "external-stakeholders")
APPROVERS = ("PER-AO", "PER-AODR")
CTI_USES = ("log-analysis", "correlation", "adverse-event-analysis")  # SP 800-61r3 DE.AE
MONITORED = ("networks", "physical-environment", "personnel-activity", "external-providers",
             "computing")  # SP 800-61r3 DE.CM


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def risk_executive(ctx: Context) -> list[RunFinding]:
    """RISKX-001: the function's forums, communication vehicles and subordinate autonomy."""
    if P2 not in scope.active_tasks(ctx.run):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RISKX-001", message, ORG_FILE, None, {P2}))

    if not ctx.run.path(ORG_FILE).is_file():
        err(f"{ORG_FILE} is missing; P-2 describes the risk executive function there")
        return out
    function = _mapping(_mapping(ctx.data(ORG_FILE)).get("risk_executive"))
    considered = {str(c) for f in _dicts(function.get("forums")) for c in _list(f.get("considers"))}
    unconsidered = [c for c in FORUM_SCOPE if c not in considered]
    if unconsidered:
        err(f"no organization-wide forum considers {', '.join(unconsidered)} risk")
    reached = {str(a) for c in _dicts(function.get("communication"))
               for a in _list(c.get("audience"))}
    unreached = [a for a in AUDIENCES if a not in reached]
    if unreached:
        err(f"no vehicle shares risk information with {', '.join(unreached)}")
    granted = {_key(a.get("activity")) for a in _dicts(function.get("subordinate_autonomy"))}
    unspecified = [a for a in RISK_ACTIVITIES if a not in granted]
    if unspecified:
        err("the degree of autonomy for subordinate organizations is not specified for "
            f"{', '.join(unspecified)}")
    return out


def entry_point(ctx: Context) -> list[RunFinding]:
    """ENTRY-001: a run entering past P-1 records the determination, and it is consistent."""
    entry = ctx.run.config.get("entry")
    order = list(ctx.run.order)
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("ENTRY-001", message, RUN_FILE, None, run_wide=True))

    active = scope.active_tasks(ctx.run)
    if not isinstance(entry, dict):
        if active and order and active[0] != order[0]:
            err(f"the run enters the RMF at {active[0]} and records no entry determination")
        return out
    task = entry.get("task")
    if task not in order or ctx.run.tasks[task].get("step") != entry.get("step"):
        err(f"the entry task {task} is no task of step {entry.get('step')}")
        return out
    if active and task != active[0]:
        err(f"the entry determination enters at {task}, but the run's first task in scope is "
            f"{active[0]}")
    # A run may re-enter an earlier step (SP 800-37r2 2.4), so a completed task may follow the
    # entry task; it must be a task of the framework.
    unknown = [str(t) for t in _list(entry.get("completed")) if t not in order]
    if unknown:
        err(f"the entry determination counts {', '.join(unknown)} as completed, which is no "
            "RMF task")
    pending = [str(t) for t in _list(entry.get("completed")) if t in active]
    if pending:
        err(f"the entry determination counts {', '.join(pending)} as completed, though the run "
            "still has it in scope")
    if entry.get("approved_by") not in APPROVERS:
        err("the entry determination is approved by the AO or AODR, not "
            f"{entry.get('approved_by')}")
    return out


def detection(ctx: Context) -> list[RunFinding]:
    """DETC-001: CTI in detection and analysis, and the asset classes monitoring covers."""
    out: list[RunFinding] = []
    active = scope.active_tasks(ctx.run)
    if S4 in active and ctx.run.path(IR_FILE).is_file():
        found = _mapping(_mapping(ctx.data(IR_FILE)).get("detection"))
        unused = [u for u in CTI_USES if u not in _list(found.get("cti_used_in"))]
        if unused:
            out.append(make("DETC-001", "up-to-date cyber threat intelligence is not used in "
                            f"{', '.join(unused)}", IR_FILE, None, {S4}))
    if S5 in active and ctx.run.path(CONMON_FILE).is_file():
        data = _mapping(ctx.data(CONMON_FILE))
        covered = {_key(c.get("asset_class")) for c in _dicts(data.get("detection_coverage"))}
        unmonitored = [m for m in MONITORED if m not in covered]
        if unmonitored:
            out.append(make("DETC-001", "continuous monitoring does not cover "
                            f"{', '.join(unmonitored)} at all times", CONMON_FILE, None, {S5}))
        if not data.get("tuning"):
            out.append(make("DETC-001", "nothing says how monitoring is tuned against false "
                            "positives and false negatives", CONMON_FILE, None, {S5}))
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("RISKX-001", risk_executive), ("ENTRY-001", entry_point),
                ("DETC-001", detection))
