"""The boundary of a complex system and the diagrams P-11 records: SUBS-*. A complex system names
its subsystems with their categorization; the system is categorized no lower than their
high-water mark, and every pair whose categorizations differ has its interface examined, with
controls selected for an interconnection. The network architecture and data flows carry
diagrams that exist and together show what SP 800-18r2 lists for what the run records: the
subsystems and internal boundaries of a complex system, third-party services and external
flows where a component is external, and data stores where the inventory holds a database.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from itertools import combinations
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

BOUNDARY_FILE = "artifacts/data/boundary.yaml"
P11, C2 = "P-11", "C-2"
LEVELS = ("low", "moderate", "high")
OBJECTIVES = {"c": "confidentiality", "i": "integrity", "a": "availability"}
# SP 800-18r2 3.2 (Environment of Operation Diagrams, Network Architecture, Data Flows): what
# every system's diagrams show, and what they show once the run records it.
DIAGRAM_CONTENT = ("components", "data-types", "data-direction")
INVENTORY_FILE = "artifacts/data/inventory.yaml"
DATA_STORE_KINDS = ("database",)


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def _rank(value: Any) -> int:
    return LEVELS.index(value) if value in LEVELS else -1


def _boundary(ctx: Context) -> dict[str, Any] | None:
    if P11 not in scope.active_tasks(ctx.run):
        return None
    data = ctx.data(BOUNDARY_FILE)
    return data if isinstance(data, dict) else None


def subsystems(ctx: Context) -> list[RunFinding]:
    """SUBS-001."""
    data = _boundary(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str, owner: str = P11) -> None:
        out.append(make("SUBS-001", message, BOUNDARY_FILE, None, {owner}))

    subs = _dicts(data.get("subsystems"))
    known = {_key(c.get("id")) for c in _dicts(data.get("components"))}
    for sub in subs:
        stray = [str(c) for c in _list(sub.get("components")) if _key(c) not in known]
        if stray:
            err(f"{sub.get('id')} names {', '.join(stray)}, no boundary component")
    cat = facts_mod.get(ctx.facts, "categorization")
    if isinstance(cat, dict) and C2 in scope.active_tasks(ctx.run):
        for key, name in OBJECTIVES.items():
            mark = max((s.get(key) for s in subs), key=_rank, default=None)
            if _rank(cat.get(key)) < _rank(mark):
                err(f"the system's {name} is {cat.get(key)}, below the high-water mark {mark} of "
                    "its designated subsystems", C2)
    interfaces = {frozenset(map(str, _list(i.get("between")))): i for i in _dicts(
        data.get("subsystem_interfaces"))}
    selected = set(baseline_mod.control_ids(ctx.run))
    for one, other in combinations(subs, 2):
        if all(one.get(k) == other.get(k) for k in OBJECTIVES):
            continue
        pair = frozenset((str(one.get("id")), str(other.get("id"))))
        record = interfaces.get(pair)
        if record is None:
            err(f"{one.get('id')} and {other.get('id')} differ in categorization and no "
                "interface record examines their interfaces, flows and dependencies")
            continue
        controls = [str(c) for c in _list(record.get("controls"))]
        if record.get("connected") is True and not controls:
            err(f"no control is selected for the interconnection of {one.get('id')} and "
                f"{other.get('id')}, whose categorizations differ")
        outside = [c for c in controls if selected and c not in selected]
        if outside:
            err(f"the interconnection of {one.get('id')} and {other.get('id')} selects "
                f"{', '.join(outside)}, outside the baseline")
    return out


def diagrams(ctx: Context) -> list[RunFinding]:
    """SUBS-002."""
    data = _boundary(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SUBS-002", message, BOUNDARY_FILE, None, {P11}))

    shown: set[str] = set()
    for section in ("authorization_boundary", "network_architecture", "data_flow"):
        node = data.get(section) if isinstance(data.get(section), dict) else {}
        drawn = _dicts(node.get("diagrams"))
        if section != "authorization_boundary" and not drawn:
            err(f"{section} carries no diagram")
        for diagram in drawn:
            path = diagram.get("path")
            if not isinstance(path, str) or not ctx.run.resolve(path).is_file():
                err(f"the {section} diagram {path} is not a file in the run directory")
            shown.update(str(s) for s in _list(diagram.get("shows")))
    components = _dicts(data.get("components"))
    inventory = ctx.data(INVENTORY_FILE)
    items = _dicts(inventory.get("items")) if isinstance(inventory, dict) else []
    wanted = list(DIAGRAM_CONTENT)
    if data.get("subsystems"):
        wanted += ["subsystems", "internal-boundaries"]
    if any(c.get("external") is True for c in components):
        wanted += ["third-party-services", "external-flows"]
    if any(i.get("kind") in DATA_STORE_KINDS for i in items):
        wanted.append("data-stores")
    undrawn = [w for w in wanted if w not in shown]
    if undrawn:
        err(f"no diagram shows {', '.join(undrawn)}")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("SUBS-001", subsystems), ("SUBS-002", diagrams))
