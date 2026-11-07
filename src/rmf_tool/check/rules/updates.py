"""Updated outputs and the inputs a task incorporates.

UPD-001 holds the system registration record: reported in eMASS or ERS (DoDI 8500.01 3.t and
encl. 3 9.b), and updated by each task SP 800-37r2 has update it (characterization at C-1,
categorization at C-3, the authorization at R-5, removal at M-7). UPD-002 holds that a
significant change, once implemented, reaches the system plan (SP 800-18r1 3.1). TIN-001 holds
that categorization and control selection rest on the decisions of the Prepare step (CNSSI 1253
1.2.2).
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope

Record = dict[str, Any]

REGISTRATION_FILE = "artifacts/data/registration.yaml"
CHANGES_FILE = "artifacts/data/changes.yaml"
PLAN_REVIEWS_FILE = "artifacts/data/plan-reviews.yaml"
REPORTED_IN = ("eMASS", "ERS")
ALTERNATE = "alternate"
# The task that updates the registry, what it adds, and the artifact that shows it did its work.
REGISTRY_UPDATES = (
    ("C-1", "characterization", "ART-SD"),
    ("C-3", "categorization", "ART-CAT"),
    ("R-5", "authorization", "ART-AUTHRPT"),
    ("M-7", "disposal", "ART-DISP"),
)
PREPARE_DECISIONS = "ART-ORG-CONTEXT"
INFORMATION_TYPES = "ART-INFOTYPES"
# The artifact that records the decision, the task whose decision it is, and what it decides.
INCORPORATES = (
    ("ART-CAT", "C-2", "security categorization", (PREPARE_DECISIONS, INFORMATION_TYPES)),
    ("ART-BASELINE", "S-1", "control selection", (PREPARE_DECISIONS,)),
)


def _block(record: Any, key: str) -> Record:
    value = record.get(key) if isinstance(record, dict) else None
    return value if isinstance(value, dict) else {}


def _items(record: Any, key: str) -> list[Record]:
    value = record.get(key) if isinstance(record, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _front(ctx: Context, artifact: str) -> Record | None:
    doc = ctx.docs.get(f"artifacts/{artifact}.md")
    return doc.data if doc is not None and isinstance(doc.data, dict) else None


def _touched(ctx: Context, artifact: str, task: str) -> bool:
    return task in _strings((_front(ctx, artifact) or {}).get("touched_by"))


# --- UPD-001: the registration record, reported and kept up to date -------------------------

def registration(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-REG"):
        return []
    data = ctx.data(REGISTRATION_FILE)
    if not isinstance(data, dict):
        return []
    out: list[RunFinding] = []

    def err(message: str, task: str) -> None:
        out.append(make("UPD-001", message, REGISTRATION_FILE, None, {task}))

    registry = _block(data, "registry")
    if registry.get("reported_in") not in REPORTED_IN:
        err(f"the system is not reported in either eMASS or ERS (reported_in is "
            f"{registry.get('reported_in')!r})", "P-18")
    tool = registry.get("tool")
    if tool == ALTERNATE and not str(registry.get("ers_import") or "").strip():
        err("the Component uses an alternate tool for system data but records no way, worked "
            "out with the DoD CIO, to import it into ERS (ers_import)", "P-18")
    registered = _day(registry.get("date"))
    updates = _items(data, "updates")
    active = set(scope.active_tasks(ctx.run))
    for task, content, evidence in REGISTRY_UPDATES:
        if task not in active or not _touched(ctx, evidence, task):
            continue
        mine = [u for u in updates if u.get("task") == task]
        if content not in {u.get("content") for u in mine}:
            err(f"{task} completed the {content} of the system, but the registration "
                f"information is not updated with it (no {content} update by {task})", task)
        for u in (u for u in mine if u.get("content") == content):
            day = _day(u.get("date"))
            if day is None:
                err(f"the {content} update of the registration information has no date", task)
            elif registered is not None and day < registered:
                err(f"the {content} update of the registration information is dated {day}, "
                    f"before the system was registered on {registered}", task)
    return out


# --- UPD-002: a significant change reaches the system plan -----------------------------------

def plan_updates(ctx: Context) -> list[RunFinding]:
    if not (scope.produced_or_seeded(ctx.run, "ART-CHG")
            and scope.produced_or_seeded(ctx.run, "ART-SSP")):
        return []
    plan = ctx.data(PLAN_REVIEWS_FILE)
    changes = ctx.data(CHANGES_FILE)
    if not isinstance(plan, dict) or not isinstance(changes, dict):
        return []
    referenced = {c.get("change_ref") for c in _items(plan, "changes")}
    out = []
    for change in _items(changes, "changes"):
        if _block(change, "security_impact").get("result") != "significant":
            continue
        if _day(_block(change, "implementation").get("date")) is None:
            continue
        if change.get("id") not in referenced:
            out.append(make("UPD-002", f"{change.get('id')}: a significant change was implemented "
                            "but the system security plan was not updated for it (no plan "
                            "change references it)", PLAN_REVIEWS_FILE, None, {"M-1"}))
    return out


# --- TIN-001: categorization and selection rest on the Prepare decisions ---------------------

def prepare_decisions(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, PREPARE_DECISIONS):
        return []
    out = []
    active = set(scope.active_tasks(ctx.run))
    for artifact, task, what, wanted in INCORPORATES:
        front = _front(ctx, artifact)
        if task not in active or front is None:
            continue
        sources = set(_strings(front.get("sources")))
        for needed in wanted:
            if needed in sources or not scope.produced_or_seeded(ctx.run, needed):
                continue
            where = f"artifacts/{artifact}.md"
            if needed == PREPARE_DECISIONS:
                out.append(make("TIN-001", f"the {what} does not incorporate the decisions made "
                                f"during the Prepare step: {needed} is not among the sources of "
                                f"{artifact}", where, None, {task}))
            else:
                out.append(make("TIN-001", f"the {what} does not incorporate the information "
                                f"types identified at P-12: {needed} is not among the sources of "
                                f"{artifact}", where, None, {task}))
    return out


RULES: dict[str, Callable[[Context], list[RunFinding]]] = {
    "UPD-001": registration,
    "UPD-002": plan_updates,
    "TIN-001": prepare_decisions,
}
