"""The NIST SP 800-53r5 catalog, read as raw JSON (L-0004), and `rmf catalog show`: a
compact per-control view sized for agent context (PM-4)."""

from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CATALOG_PATH = "references/oscal/catalog/NIST_SP-800-53_rev5_catalog.json"
FIELDS = ("title", "statement", "guidance", "objectives", "params")
DEFAULT_FIELDS = ("title", "statement")
_INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([^\s}]+)\s*\}\}")
_CONTROL_NUM = re.compile(r"^([a-z]{2})-(\d+)(?:\.(\d+))?$")


@dataclass(frozen=True)
class Catalog:
    controls: dict[str, dict[str, Any]]  # id -> control (enhancements included)
    order: tuple[str, ...]  # catalog order
    families: dict[str, str]  # family id -> title
    params: dict[str, dict[str, Any]]


@functools.cache
def _load(path: Path) -> Catalog:
    doc = json.loads(path.read_text(encoding="utf-8"))["catalog"]
    controls: dict[str, dict[str, Any]] = {}
    params: dict[str, dict[str, Any]] = {}
    families: dict[str, str] = {}

    def walk(items: list[dict[str, Any]]) -> None:
        for c in items:
            controls[c["id"]] = c
            for p in c.get("params") or []:
                params[p["id"]] = p
            walk(c.get("controls") or [])

    for group in doc.get("groups") or []:
        families[group["id"]] = group["title"]
        walk(group.get("controls") or [])
    return Catalog(controls, tuple(controls), families, params)


def load(repo: Path) -> Catalog:
    return _load((repo / CATALOG_PATH).resolve())


def sort_key(control_id: str) -> tuple[str, int, int]:
    m = _CONTROL_NUM.match(control_id)
    if not m:
        return (control_id, 0, 0)
    return (m.group(1), int(m.group(2)), int(m.group(3) or 0))


def family(control_id: str) -> str:
    return control_id.split("-", 1)[0]


def _param_text(cat: Catalog, param_id: str) -> str:
    p = cat.params.get(param_id)
    if p is None:
        return f"[{param_id}]"
    if "select" in p:
        how = p["select"].get("how-many", "one")
        choices = "; ".join(_INSERT.sub(lambda m: _param_text(cat, m.group(1)), c)
                            for c in p["select"].get("choice") or [])
        return f"[Selection ({how.replace('-', ' ')}): {choices}]"
    return f"[Assignment: organization-defined {p.get('label', param_id)}]"


def _prose(cat: Catalog, text: str) -> str:
    return _INSERT.sub(lambda m: _param_text(cat, m.group(1)), text)


def _label(part: dict[str, Any]) -> str:
    return next((p["value"] for p in part.get("props") or [] if p.get("name") == "label"), "")


def _part_lines(cat: Catalog, part: dict[str, Any], depth: int) -> list[str]:
    label = _label(part)
    prose = _prose(cat, part.get("prose", "")).strip()
    text = " ".join(x for x in (label, prose) if x)
    lines = [("  " * depth) + text] if text else []
    for child in part.get("parts") or []:
        lines += _part_lines(cat, child, depth + (1 if text else 0))
    return lines


def _part(control: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((p for p in control.get("parts") or [] if p.get("name") == name), None)


def view(cat: Catalog, control_id: str, fields: tuple[str, ...]) -> dict[str, Any]:
    c = cat.controls[control_id]
    out: dict[str, Any] = {"id": control_id}
    if "title" in fields:
        out["title"] = c.get("title", "")
    for name, key in (("statement", "statement"), ("guidance", "guidance"),
                      ("objectives", "assessment-objective")):
        if name in fields:
            part = _part(c, key)
            out[name] = "\n".join(_part_lines(cat, part, 0)) if part else ""
    if "params" in fields:
        out["params"] = {p["id"]: _param_text(cat, p["id"]) for p in c.get("params") or []}
    return out


def render_text(v: dict[str, Any]) -> str:
    lines = [f"{v['id']}" + (f" {v['title']}" if v.get("title") else "")]
    for name in ("statement", "guidance", "objectives"):
        if v.get(name):
            lines.append(f"  {name}:")
            lines += [f"    {ln}" for ln in v[name].splitlines()]
    for pid, text in (v.get("params") or {}).items():
        lines.append(f"  param {pid}: {text}")
    return "\n".join(lines)


def chunk(items: list[str], spec: str) -> list[str]:
    """``i/n``: the i-th (1-based) of n nearly equal consecutive slices."""
    m = re.fullmatch(r"(\d+)/(\d+)", spec)
    if not m or not 1 <= int(m.group(1)) <= int(m.group(2)):
        raise ValueError(f"--chunk must be i/n with 1 <= i <= n, got {spec!r}")
    i, n = int(m.group(1)), int(m.group(2))
    size, extra = divmod(len(items), n)
    start = (i - 1) * size + min(i - 1, extra)
    return items[start:start + size + (1 if i <= extra else 0)]
