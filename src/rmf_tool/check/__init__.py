"""The rule registry (``registry.yaml``, plan §6.5): the authoritative list of rules with
their scope, severity, acceptance criteria, enforcement phase and negative fixture.
The rule engines (``rmf validate`` now, ``rmf check`` from Phase 3.5) take rule
activation from here, so a rule's phase is recorded in exactly one place.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import jsonschema

from rmf_tool.yamlload import safe_load

REGISTRY_PATH = Path(__file__).with_name("registry.yaml")
REGISTRY_SCHEMA_PATH = Path(__file__).with_name("registry.schema.json")


@dataclass(frozen=True)
class Rule:
    id: str
    scope: str
    severity: str
    ac: tuple[str, ...]
    phase: str
    applies_after: str | None
    summary: str
    hint: str
    fixture: str | None = None
    exempt_reason: str | None = None
    severity_note: str | None = None
    enforces: tuple[str, ...] = ()
    since: str | None = None


def registry_errors(data: Any) -> list[str]:
    schema = json.loads(REGISTRY_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
              for e in jsonschema.Draft202012Validator(schema).iter_errors(data)]
    ids = [r.get("id") for r in data.get("rules", []) if isinstance(r, dict)]
    errors += [f"duplicate rule id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    return errors


@cache
def load_registry(path: Path = REGISTRY_PATH) -> tuple[Rule, ...]:
    data = safe_load(path.read_text(encoding="utf-8"))
    errors = registry_errors(data)
    if errors:
        raise ValueError(f"{path.name}: " + "; ".join(errors[:5]))
    return tuple(Rule(**{**r, "ac": tuple(r["ac"]), "enforces": tuple(r.get("enforces", ()))})
                 for r in data["rules"])


def rules_by_id() -> dict[str, Rule]:
    return {r.id: r for r in load_registry()}
