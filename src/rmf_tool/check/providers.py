"""Provider IDs (dry-run finding F-04-1).

A provider (a common control provider, a leveraged service, a CSSP) used to be matched by its
name, as free text, across five files written by five tasks: P-2's external entities, P-5's
common controls, C-1's leveraged authorizations, S-3's allocation and S-4's SSP and service
agreements. One different word broke an earlier task. P-2 now registers each provider once in
``org-context.yaml providers`` as ``PRV-##``, and every other record names it by that ID.

A name that equals a registered provider's name still resolves to its ID, so a run written
before the registry existed keeps working; ``rmf run migrate`` rewrites names to IDs.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context

ORG_CONTEXT_FILE = "artifacts/data/org-context.yaml"
PROVIDER_ID = re.compile(r"^PRV-\d{2,3}$")


def registry(ctx: Context) -> dict[str, str]:
    """PRV-## -> provider name, from org-context.yaml providers."""
    data = ctx.data(ORG_CONTEXT_FILE)
    items = data.get("providers") if isinstance(data, dict) else None
    return {str(p["id"]): str(p.get("name") or p["id"]) for p in items or []
            if isinstance(p, dict) and isinstance(p.get("id"), str)}


def _norm(name: str) -> str:
    return " ".join(name.lower().split())


def keyer(ctx: Context) -> Callable[[Any], str | None]:
    """A function giving each provider reference its comparison key: the PRV-## ID when the
    value is one or names a registered provider, else the value itself."""
    known = registry(ctx)
    by_name = {_norm(name): pid for pid, name in known.items()}

    def key(value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        if value in known:
            return value
        return by_name.get(_norm(value), value)

    return key


def shown(ctx: Context) -> Callable[[Any], str]:
    """A function rendering a provider reference for a message or a document: its name, with
    the ID in brackets."""
    known = registry(ctx)

    def show(value: Any) -> str:
        return f"{known[value]} ({value})" if isinstance(value, str) and value in known \
            else str(value)

    return show


# Every field that names a provider: (file or directory, list key, field).
FIELDS = (
    (ORG_CONTEXT_FILE, "common_controls", "provided_by"),
    (ORG_CONTEXT_FILE, "external_entities", "provider"),
    ("artifacts/data/leveraged-authorizations.yaml", "leveraged_authorizations", "provider"),
    ("artifacts/data/allocation.yaml", "allocations", "provider"),
    ("artifacts/data/allocation.yaml", "allocations", "also_provided_by"),
    ("artifacts/data/allocation.yaml", "providers", "provider"),
    ("artifacts/data/service-agreements.yaml", "agreements", "provider"),
    ("artifacts/data/requirements.yaml", "requirements", "allocated_to"),
    ("artifacts/ssp/controls", "controls", "inherited_from"),
)


def references(ctx: Context) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """(file, field, record) for every provider reference in the run."""
    for rel, key, field in FIELDS:
        paths = sorted(ctx.run.path(rel).glob("*.yaml")) if not rel.endswith(".yaml") \
            else [ctx.run.path(rel)]
        for path in paths:
            data = ctx.data(ctx.run.rel(path)) if path.is_file() else None
            for item in (data.get(key) or [] if isinstance(data, dict) else []):
                if isinstance(item, dict) and field in item:
                    yield ctx.run.rel(path), field, item


def of_allocation(record: dict[str, Any]) -> list[str]:
    """Every provider of an allocation: `provider` and any `also_provided_by` (F-05-8)."""
    names = [record.get("provider"), *(record.get("also_provided_by") or [])]
    return [n for n in names if isinstance(n, str) and n.strip()]
