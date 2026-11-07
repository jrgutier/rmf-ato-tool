"""Business impact and criticality analysis rules: BIA-001 and BIA-002 on artifacts/data/bia.yaml
(ART-BIA, P-8). Each stays quiet about a file that is missing or unreadable, which RUN-ART-001
and the schema report.

CNSSI 1254 element 12 asks whether mission critical functions are present and, if so, which
(REQ-CNSSI1254-0050). SP 800-60 Vol. 1 §4.6 has conflicting categorization and BIA information,
such as a low availability impact beside a short recovery time, trigger a reevaluation by the
mission and data owners (REQ-SP800-60V1R1-0193). The source sets no recovery-time threshold, so
BIA-002 compares the BIA's own impact level with the availability impact of the categorization
in the same FIPS 199 levels; PER-SPONSOR is the mission owner and PER-IO the data owner."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make

BIA = "artifacts/data/bia.yaml"
LEVELS = {"low": 0, "moderate": 1, "high": 2}
OWNERS = ("PER-SPONSOR", "PER-IO")


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
