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


def read(run: Run) -> tuple[dict[str, Any], str | None]:
    """(the frozen dates, why the file cannot be read). A file that exists but does not hold
    ``items`` as a mapping is a problem, never an empty record: reading it as empty would let
    the next build freeze today's dates over the original ones."""
    path = run.path(ORIGINAL_FILE)
    if not path.is_file():
        return {}, None
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return {}, str(exc)
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, dict):
        return {}, "expected a mapping `items` of POA&M item IDs"
    return items, None


def load(run: Run) -> dict[str, Any]:
    return read(run)[0]


def _dates(item: dict[str, Any]) -> dict[str, Any]:
    return {"scheduled_completion": item.get("scheduled_completion"),
            "milestones": {m.get("description"): m.get("due")
                           for m in item.get("milestones") or () if isinstance(m, dict)}}


def freeze(run: Run) -> str | None:
    """The file with any new item added, or None when nothing is to be frozen yet or the
    record or the POA&M cannot be read: an unreadable record is left as it is for the person to
    restore (ASMT-010 reports it), not rewritten from the current dates."""
    journal = run.path("journal.md")
    if not run.holds(SINCE) or not run.path(POAM_FILE).is_file() or not journal.is_file():
        return None
    if A6_CHECKPOINT not in journal.read_text(encoding="utf-8", errors="replace"):
        return None
    known, problem = read(run)
    if problem is not None:
        return None
    try:
        data = run.data(POAM_FILE)
    except YamlError:
        return None
    items = data.get("items") if isinstance(data, dict) else None
    frozen = dict(known)
    for item in items if isinstance(items, list) else ():
        if isinstance(item, dict) and isinstance(item.get("id"), str) \
                and item["id"] not in frozen:
            frozen[item["id"]] = _dates(item)
    yaml = YAML()
    yaml.default_flow_style = False
    buf = io.StringIO()
    yaml.dump({"items": frozen}, buf)
    return buf.getvalue()
