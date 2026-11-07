"""MSN-001 (SP 800-37r2 Task P-8, DoDI 8510.01 Table 1, cATO IC01): the missions, business
functions and mission/business processes the system supports are identified by the mission or
business owner, and each mission essential function names the assets and data that support it
once the boundary and the information types are on record. Quiet when P-8 is not in scope."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.assessment import _records
from rmf_tool.check.rules.categorize import INFOTYPES_FILE
from rmf_tool.check.rules.consistency import BOUNDARY_FILE
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import FACTS_FILE

P8 = "P-8"
# DoDI 8510.01 Table 1 names the Mission or Business Owner: the sponsor whose missions the
# system supports, or the representative of its user community.
MISSION_OWNERS = ("PER-SPONSOR", "PER-UR")
BOUNDARY, INFOTYPES = "ART-BND", "ART-INFOTYPES"


def _ids(ctx: Context, artifact: str, rel: str, key: str) -> set[Any] | None:
    """The ids an artifact declares, or None while the artifact is not in play."""
    if not scope.produced_or_seeded(ctx.run, artifact):
        return None
    data = ctx.data(rel)
    if not isinstance(data, dict):
        return set()
    return {r["id"] for r in _records(data, key) if isinstance(r.get("id"), str)}


def _listed(item: dict[str, Any], key: str) -> list[Any]:
    return item.get(key) if isinstance(item.get(key), list) else []


def _assets(item: dict[str, Any], components: set[Any] | None, err: Any) -> None:
    if components is None:
        return
    listed = _listed(item, "supported_by")
    if item.get("essential") is True and not listed:
        err(f"{item.get('id')} is a mission essential function with no supporting assets "
            "captured, though the boundary's components are on record")
    for ref in listed:
        if not isinstance(ref, str) or ref not in components:
            err(f"{item.get('id')} is supported by {ref}, which the assets on record do not "
                "declare")


def _data(item: dict[str, Any], infotypes: set[Any] | None, err: Any) -> None:
    if infotypes is None:
        return
    listed = _listed(item, "data")
    if item.get("essential") is True and not listed:
        err(f"{item.get('id')} is a mission essential function with no supporting information "
            "types captured, though the information types are on record")
    for ref in listed:
        if not isinstance(ref, str) or ref not in infotypes:
            err(f"{item.get('id')} is supported by {ref}, which the information types on record "
                "do not declare")


def missions(ctx: Context) -> list[RunFinding]:
    if P8 not in scope.active_tasks(ctx.run):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("MSN-001", message, FACTS_FILE, None, {P8}))

    node = facts_mod.get(ctx.facts, "missions")
    found = node if isinstance(node, dict) else {}
    items = _records(found, "items")
    if not items:
        err("P-8 identifies no mission, business function or mission/business process the "
            "system is intended to support")
        return out
    if found.get("identified_by") not in MISSION_OWNERS:
        err("the mission or business owner identifies the missions the system supports, "
            f"not {found.get('identified_by')}")
    components = _ids(ctx, BOUNDARY, BOUNDARY_FILE, "components")
    infotypes = _ids(ctx, INFOTYPES, INFOTYPES_FILE, "information_types")
    for item in items:
        _assets(item, components, err)
        _data(item, infotypes, err)
    return out
