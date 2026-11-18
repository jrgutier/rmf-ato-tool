"""``facts.yaml``, the only home of system facts (INV-4, plan §7.2).

Each fact is ``{value, set_by_task, sources?}``; ``categorization`` holds c/i/a/overlays
directly and its approval under ``approved``. Framework tasks name facts by dotted path.
"""

from __future__ import annotations

from typing import Any

from rmf_tool.run.model import FACTS_FILE, Run, YamlError

# Fact label for the injected facts block, in display order.
LABELS = {
    "system_name": "System name",
    "acronym": "Acronym",
    "system_id": "System ID",
    "aliases": "Aliases",
    "boundary_id": "Authorization boundary",
    "lifecycle_state": "Life-cycle state",
    "categorization": "Security categorization",
    "categorization.approved": "Categorization approved",
    "baseline_id": "Control baseline",
    "classification": "Classification and handling markings",
    "system_type": "IT type",
    "owning_organization": "Owning organization",
    "system_version": "System version",
    "operational_environment": "Operational environment",
    "lifecycle_phase": "Life-cycle phase",
}


def load(run: Run) -> dict[str, Any]:
    """facts.yaml as a mapping; a missing, empty or unreadable file reads as {} (RUN-FM-001
    reports schema problems)."""
    path = run.path(FACTS_FILE)
    if not path.is_file():
        return {}
    try:
        data = run.data(FACTS_FILE)
    except YamlError:
        return {}
    return data if isinstance(data, dict) else {}


def get(facts: dict[str, Any], dotted: str) -> Any:
    """The fact node at a dotted path (``categorization.approved``), or None."""
    node: Any = facts
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def nss(facts: dict[str, Any], fallback: Any = None) -> bool | None:
    """The run's NSS status: the `nss` fact once C-1 sets it, else the fallback record value
    (P-16's nss-assessments.yaml) until then."""
    node = get(facts, "nss")
    if isinstance(node, dict) and isinstance(node.get("value"), bool):
        return node["value"]
    return fallback if isinstance(fallback, bool) else None


def set_by(facts: dict[str, Any], dotted: str) -> str | None:
    node = get(facts, dotted)
    return node.get("set_by_task") if isinstance(node, dict) else None


def value(facts: dict[str, Any], dotted: str) -> Any:
    node = get(facts, dotted)
    return node.get("value") if isinstance(node, dict) else None


def display(facts: dict[str, Any], dotted: str) -> str | None:
    """A fact's value as one line of text, or None when unset."""
    node = get(facts, dotted)
    if not isinstance(node, dict):
        return None
    if dotted == "categorization":
        cia = "/".join(str(node.get(k, "?")).upper() for k in ("c", "i", "a"))
        overlays = ", ".join(node.get("overlays") or []) or "none"
        return f"C/I/A {cia}; overlays: {overlays}"
    val = node.get("value")
    if dotted == "classification" and val is not None:
        marks = [*(node.get("compartments") or ()), *(node.get("handling_markings") or ())]
        return f"{val}; markings: {', '.join(map(str, marks)) or 'none'}"
    if dotted == "system_type" and val is not None:
        return f"{val}, {node.get('connectivity')}"
    if dotted == "system_version" and val is not None and node.get("release_date"):
        return f"{val} (released {node['release_date']})"
    if isinstance(val, bool):
        by = node.get("approved_by")
        return ("yes" if val else "no") + (f" ({by})" if by else "")
    if isinstance(val, list):
        return ", ".join(map(str, val)) or "none"
    return None if val is None else str(val)


def high_water(facts: dict[str, Any]) -> str | None:
    cat = get(facts, "categorization")
    if not isinstance(cat, dict):
        return None
    levels = ("low", "moderate", "high")
    values = [cat.get(k) for k in ("c", "i", "a")]
    if any(v not in levels for v in values):
        return None
    return max(values, key=levels.index)


def approved(facts: dict[str, Any]) -> bool:
    return value(facts, "categorization.approved") is True
