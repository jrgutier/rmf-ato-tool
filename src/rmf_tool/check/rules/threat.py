"""The system's risk designation, THREAT-001 (Task P-14).

DoDI 8510.01 3.3.a(3): risks to systems are designated consistent with the most severe threat to
any individual component or subcomponent, for consideration of requirements, acquisition and
T&E. ra.yaml records system_risk. Every risk ra.yaml rates against a part of the system is such
a threat: each threat event (against the assets it harms), each external connection (against
its component) and each supply chain risk (against its items), so the designation is judged
against the union of them. A designation above the worst threat is the organization's to make
and is not refused.
"""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.risk_assessment import LEVELS, RA_FILE, _id, _list, _ra


def _threats(data: dict[str, Any]) -> list[tuple[str, str, list[str]]]:
    """(record ID, risk level, the parts of the system it is a threat to) for each rated risk."""
    external = data.get("external") if isinstance(data.get("external"), dict) else {}
    out = []
    for e in _list(data, "threat_events"):
        out.append((_id(e), e.get("risk"), [i.get("asset") for i in _list(e, "impacts")]))
    for c in _list(external, "connections"):
        out.append((_id(c, "component"), c.get("risk"), [c.get("component")]))
    for s in _list(external, "supply_chain"):
        items = s.get("items") if isinstance(s.get("items"), list) else []
        out.append((_id(s), s.get("risk"), items))
    return [(i, r, [p for p in parts if isinstance(p, str)]) for i, r, parts in out
            if i and r in LEVELS]


def designation(ctx: Context) -> list[RunFinding]:
    data = _ra(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("THREAT-001", message, RA_FILE, None, {"P-14"}))

    designated = data.get("system_risk")
    if not isinstance(designated, dict) or designated.get("level") not in LEVELS:
        err("ra.yaml designates no risk for the system (system_risk) consistent with the most "
            "severe threat to any individual component or subcomponent")
        return out
    threats = _threats(data)
    if not threats:
        return out
    worst, risk, parts = max(threats, key=lambda t: LEVELS.index(t[1]))
    level = designated["level"]
    if LEVELS.index(level) < LEVELS.index(risk):
        err(f"the system's risk is designated {level}, below the {risk} risk of {worst} to "
            f"{', '.join(sorted(set(parts))) or 'a component'}, the most severe threat to any "
            "individual component")
    set_by = designated.get("set_by")
    if not isinstance(set_by, str) or set_by not in {t[0] for t in threats}:
        err(f"system_risk is set by {set_by}, which is not a threat ra.yaml "
            "rates against a component")
    return out
