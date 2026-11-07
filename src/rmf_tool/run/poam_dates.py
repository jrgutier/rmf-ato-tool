"""The POA&M's original dates. CNSSI 1254 keeps a scheduled completion date and initial milestones
unchanged, and items.yaml is rewritten whole, so `rmf build` freezes each item's dates the first
time it sees the item after A-6's CHECKPOINT. Generated, and only ever added to (INV-2)."""

from __future__ import annotations

import io
from typing import Any

from ruamel.yaml import YAML

from rmf_tool.run.model import Run, YamlError, read_yaml

ORIGINAL_FILE = "artifacts/poam/original-dates.yaml"
POAM_FILE = "artifacts/poam/items.yaml"
SINCE = "0.2.0"
A6_CHECKPOINT = "CHECKPOINT · task A-6"


def load(run: Run) -> dict[str, Any]:
    path = run.path(ORIGINAL_FILE)
    try:
        data = read_yaml(path) if path.is_file() else None
    except YamlError:
        return {}
    return data.get("items") or {} if isinstance(data, dict) else {}


def _dates(item: dict[str, Any]) -> dict[str, Any]:
    return {"scheduled_completion": item.get("scheduled_completion"),
            "milestones": {m.get("description"): m.get("due")
                           for m in item.get("milestones") or () if isinstance(m, dict)}}


def freeze(run: Run) -> str | None:
    """The file with any new item added, or None when nothing is to be frozen yet."""
    journal = run.path("journal.md")
    if not run.holds(SINCE) or not run.path(POAM_FILE).is_file() or not journal.is_file():
        return None
    if A6_CHECKPOINT not in journal.read_text(encoding="utf-8"):
        return None
    data = run.data(POAM_FILE)
    items = data.get("items") if isinstance(data, dict) else None
    frozen = dict(load(run))
    for item in items or ():
        if isinstance(item, dict) and item.get("id") not in frozen:
            frozen[item.get("id")] = _dates(item)
    yaml = YAML()
    yaml.default_flow_style = False
    buf = io.StringIO()
    yaml.dump({"items": frozen}, buf)
    return buf.getvalue()
