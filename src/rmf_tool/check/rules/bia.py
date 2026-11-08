"""Business impact and criticality analysis rules: BIA-001 to BIA-003 on artifacts/data/bia.yaml
(ART-BIA, P-8). Each stays quiet about a file that is missing or unreadable, which RUN-ART-001
and the schema report.

CNSSI 1254 element 12 asks whether mission critical functions are present and, if so, which
(REQ-CNSSI1254-0050). SP 800-60 Vol. 1 §4.6 has conflicting categorization and BIA information,
such as a low availability impact beside a short recovery time, trigger a reevaluation by the
mission and data owners (REQ-SP800-60V1R1-0193). The source sets no recovery-time threshold, so
BIA-002 compares the BIA's own impact level with the availability impact of the categorization
in the same FIPS 199 levels; PER-SPONSOR is the mission owner and PER-IO the data owner.

SP 800-161 Appendix G makes the criticality analysis iterative: a high-level determination in
Frame (P-8), updated in Assess (Task 2-0; C-2, where the FIPS 199 categorization is set), and
iterated in Monitor when a change warrants it (M-1), reviewed at least annually, ending in a
narrowed, prioritized list of critical processes, systems and components (REQ-SP800-161R1-1091,
-1098, -1225, -1234, -1549). The source does not say which change warrants an iteration;
BIA-003 takes a change whose security impact analysis is significant."""

from __future__ import annotations

import datetime as dt
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make

BIA = "artifacts/data/bia.yaml"
LEVELS = {"low": 0, "moderate": 1, "high": 2}
OWNERS = ("PER-SPONSOR", "PER-IO")
CHANGES = "artifacts/data/changes.yaml"
BOUNDARY = "artifacts/data/boundary.yaml"
YEAR_DAYS = 366


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def _record(ctx: Context) -> dict[str, Any] | None:
    data = ctx.data(BIA)
    return data if isinstance(data, dict) else None


def criticality(ctx: Context) -> list[RunFinding]:
    """BIA-001: the record answers whether mission critical functions are present and, when
    they are, identifies them, each carried by a process the analysis lists."""
    bia = _record(ctx)
    if bia is None or not isinstance(bia.get("mission_critical"), bool):
        return []
    functions = _dicts(bia.get("functions"))
    out = []
    if bia["mission_critical"] and not functions:
        out.append("says mission critical functions are present but identifies none")
    if not bia["mission_critical"] and functions:
        out.append(f"says no mission critical functions are present but lists {len(functions)}")
    known = {str(p.get("id")) for p in _dicts(bia.get("processes"))}
    for fn in functions:
        named = fn.get("processes")
        for pid in named if isinstance(named, list) else ():
            if str(pid) not in known:
                out.append(f"mission critical function {fn.get('id')} names process {pid}, "
                           "which the analysis does not list")
    return [make("BIA-001", f"the business impact and criticality analysis {m}", BIA, None,
                 {"P-8"}) for m in out]


def reevaluation(ctx: Context) -> list[RunFinding]:
    """BIA-002: a process whose disruption impact exceeds the availability impact of the
    categorization is reevaluated by the mission owner and the data owner."""
    bia = _record(ctx)
    categorization = ctx.facts.get("categorization") if isinstance(ctx.facts, dict) else None
    availability = categorization.get("a") if isinstance(categorization, dict) else None
    if bia is None or availability not in LEVELS:
        return []
    done: dict[str, set[str]] = {}
    for item in _dicts(bia.get("reevaluations")):
        by = item.get("by") if isinstance(item.get("by"), list) else []
        done.setdefault(str(item.get("process")), set()).update(str(b) for b in by)
    out = []
    for proc in _dicts(bia.get("processes")):
        impact, pid = proc.get("disruption_impact"), str(proc.get("id"))
        if impact not in LEVELS or LEVELS[impact] <= LEVELS[availability]:
            continue
        if pid not in done:
            out.append(make("BIA-002", f"process {pid} has a {impact} disruption impact but the "
                            f"availability impact is {availability}, and no reevaluation records "
                            "the conflict", BIA, None, {"C-2"}))
            continue
        missing = [o for o in OWNERS if o not in done[pid]]
        if missing:
            out.append(make("BIA-002", f"the reevaluation of process {pid} is not by the mission "
                            f"and data owners: {', '.join(missing)} missing", BIA, None, {"C-2"}))
    return out


def _day(value: Any) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def _criticality_iterations(crit: dict[str, Any], ctx: Context) -> list[tuple[str, set[str]]]:
    """Frame, then Assess once the categorization is set, Monitor for each significant change,
    and no gap of more than a year."""
    iterations = _dicts(crit.get("iterations"))
    steps = {}
    for it in iterations:
        steps.setdefault(str(it.get("step")), []).append(_day(it.get("date")))
    out: list[tuple[str, set[str]]] = []
    frame = [d for d in steps.get("frame", ()) if d]
    if not frame:
        out.append(("has no Frame iteration (P-8)", {"P-8"}))
    categorized = isinstance(ctx.facts, dict) and isinstance(ctx.facts.get("categorization"), dict)
    assess = [d for d in steps.get("assess", ()) if d]
    if categorized and not assess:
        out.append(("has no Assess iteration updating the Frame one, though the categorization "
                    "is set (SP 800-161 Task 2-0, C-2)", {"C-2"}))
    elif frame and assess and max(assess) < min(frame):
        out.append(("has its Assess iteration dated before the Frame iteration it updates",
                    {"C-2"}))
    changes = ctx.data(CHANGES)
    named = {str(it.get("change")): _day(it.get("date")) for it in iterations
             if it.get("step") == "monitor"}
    for chg in _dicts(changes.get("changes")) if isinstance(changes, dict) else ():
        impact = chg.get("security_impact")
        if not isinstance(impact, dict) or impact.get("result") != "significant":
            continue
        cid, when = str(chg.get("id")), _day(chg.get("date"))
        done = named.get(cid)
        if cid not in named:
            out.append((f"has no Monitor iteration for {cid}, a change with a significant "
                        "security impact", {"M-1"}))
        elif when and done and done < when:
            out.append((f"has its Monitor iteration for {cid} dated before the change", {"M-1"}))
    dates = sorted(d for ds in steps.values() for d in ds if d)
    for before, after in zip(dates, dates[1:], strict=False):
        if (after - before).days > YEAR_DAYS:
            out.append((f"went unreviewed from {before} to {after}; SP 800-161 asks for a review "
                        "and update annually at minimum", {"M-1"}))
    return out


def _criticality_items(crit: dict[str, Any], bia: dict[str, Any], ctx: Context) -> list[str]:
    """A prioritized list: ranks 1 to n; each item underpins processes the analysis lists, a
    component is one the boundary lists, and each mission critical process is underpinned."""
    items = _dicts(crit.get("critical_items"))
    out = []
    ranks = sorted(i.get("rank") for i in items if isinstance(i.get("rank"), int))
    if ranks != list(range(1, len(items) + 1)):
        out.append(f"is not a prioritized list: ranks {ranks} are not 1 to {len(items)}")
    known = {str(p.get("id")) for p in _dicts(bia.get("processes"))}
    boundary = ctx.data(BOUNDARY)
    components = {str(c.get("id")) for c in _dicts(boundary.get("components"))} \
        if isinstance(boundary, dict) else None
    covered: set[str] = set()
    for item in items:
        procs = item.get("processes") if isinstance(item.get("processes"), list) else []
        covered.update(str(p) for p in procs)
        for pid in procs:
            if str(pid) not in known:
                out.append(f"names critical item {item.get('item')} underpinning process {pid}, "
                           "which the analysis does not list")
        if item.get("kind") == "component" and components is not None \
                and str(item.get("item")) not in components:
            out.append(f"names critical component {item.get('item')}, which is not a component "
                       "of the authorization boundary")
        if item.get("kind") == "process" and str(item.get("item")) not in known:
            out.append(f"names critical process {item.get('item')}, which the analysis does not "
                       "list")
    if bia.get("mission_critical") is True:
        mission = {str(p) for fn in _dicts(bia.get("functions"))
                   for p in (fn.get("processes") if isinstance(fn.get("processes"), list) else ())}
        for pid in sorted(mission - covered):
            out.append(f"leaves mission critical process {pid} underpinned by no critical item")
        if mission and not any(i.get("role") == "defensive" for i in items):
            out.append("names no component delivering a defensive, commonly shared process "
                       "(access control, identity management, crypto) as critical")
    return out


def criticality_analysis(ctx: Context) -> list[RunFinding]:
    """BIA-003: the SP 800-161 criticality analysis is iterated in Frame, Assess and Monitor,
    at least annually, and narrows to a prioritized list of critical items."""
    bia = _record(ctx)
    crit = bia.get("criticality") if bia else None
    if not isinstance(crit, dict):
        return []
    found = _criticality_iterations(crit, ctx)
    found += [(m, {"P-8", "C-2"}) for m in _criticality_items(crit, bia, ctx)]
    return [make("BIA-003", f"the criticality analysis {m}", BIA, None, tasks)
            for m, tasks in found]
