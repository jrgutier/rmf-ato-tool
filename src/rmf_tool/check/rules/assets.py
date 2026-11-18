"""The assets P-10 identifies: ASSET-*. The inventory names each component individually with
what CNSSI 1254 Annex C asks of it, a unique item identifier and the asset management system
that holds it; the organization's asset scope considers every asset class of SP 800-37 Task
P-10; the run says whether the system is a high-value asset. Judged once P-10 is in scope.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

INVENTORY_FILE = "artifacts/data/inventory.yaml"
WRITER = "P-10"
# SP 800-37r2 Task P-10 discussion: tangible and intangible assets.
ASSET_CLASSES = ("physical-environmental", "human", "technology", "mission-business-processes",
                 "information-data", "firmware", "software", "services", "reputation",
                 "privacy-interests")
SOFTWARE_KINDS = ("software", "operating-system", "database", "firmware")
IDENTIFIED_KINDS = ("hardware", "network-device", *SOFTWARE_KINDS)
HARDWARE_KINDS = ("hardware", "network-device")
# Replicas of a virtual machine or a cloud service are one configuration item; IUID (DoDI
# 8320.04) covers tangible items, so software may carry a configuration-item ID instead of a
# UII (dry-run finding F-02-5).
COUNTED_KINDS = ("virtual-machine", "service")


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def _inventory(ctx: Context) -> dict[str, Any] | None:
    if WRITER not in scope.active_tasks(ctx.run):
        return None
    data = ctx.data(INVENTORY_FILE)
    return data if isinstance(data, dict) else None


def asset_scope(ctx: Context) -> list[RunFinding]:
    """ASSET-001: the organization defines the scope of assets considered, across every class."""
    data = _inventory(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("ASSET-001", message, INVENTORY_FILE, None, {WRITER}))

    considered = {_key(r.get("class")) for r in _dicts(data.get("asset_scope"))}
    unscoped = [c for c in ASSET_CLASSES if c not in considered]
    if unscoped:
        err(f"the organization's asset scope does not consider {', '.join(unscoped)}")
    excluded = {_key(r.get("class")) for r in _dicts(data.get("asset_scope"))
                if r.get("considered") is False}
    for asset in _dicts(data.get("assets")):
        if _key(asset.get("class")) in excluded:
            err(f"{asset.get('id')} is a {asset.get('class')} asset, a class the asset scope "
                "leaves out")
    return out


def inventory_items(ctx: Context) -> list[RunFinding]:
    """ASSET-002: each component named individually, with the CNSSI 1254 fields, a unique item
    identifier, and the asset management system that holds the inventory."""
    data = _inventory(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("ASSET-002", message, INVENTORY_FILE, None, {WRITER}))

    items = _dicts(data.get("items"))
    system_type = facts_mod.get(ctx.facts, "system_type")
    networked = isinstance(system_type, dict) and system_type.get("connectivity") == "networked"
    if not isinstance(data.get("asset_management_system"), dict):
        err("the inventory names no DoD IT asset management system that holds it")
    shared = sorted(u for u, n in Counter(_key(i.get("uii")) for i in items
                                            if _key(i.get("uii"))).items() if n > 1)
    for uii in shared:
        err(f"the unique item identifier {uii} is shared by more than one item")
    for item in items:
        ident, kind = item.get("id"), item.get("kind")
        if isinstance(item.get("quantity"), int) and item["quantity"] > 1 \
                and kind not in COUNTED_KINDS:
            err(f"{ident} stands for {item.get('quantity')} units; each component is "
                "individually identified")
        if kind in IDENTIFIED_KINDS and not item.get("uii") \
                and not (kind in SOFTWARE_KINDS and item.get("ci_id")):
            err(f"{ident} has no unique item identifier")
        if not item.get("owner"):
            err(f"{ident} names no system or component owner")
        if kind in HARDWARE_KINDS and networked and not item.get("hostname"):
            err(f"{ident} is a networked device with no hostname")
        if kind in HARDWARE_KINDS and not item.get("serial_number"):
            err(f"{ident} is hardware with no serial number")
        if kind in SOFTWARE_KINDS and not item.get("version"):
            err(f"{ident} is software with no version number")
        uc = item.get("unified_capability")
        if isinstance(uc, dict) and uc.get("certification") != "certified":
            err(f"{ident} is a unified capability product without unified capability "
                f"certification for cybersecurity ({uc.get('certification')})")
        if kind in SOFTWARE_KINDS and item.get("software_category") not in ("cots", "gots",
                                                                           "oss"):
            err(f"{ident} has no software category (COTS, GOTS or OSS)")
    return out


def high_value_asset(ctx: Context) -> list[RunFinding]:
    """ASSET-003: whether the system is an HVA, and its place on the Component HVA inventory."""
    data = _inventory(ctx)
    if data is None:
        return []
    hva = data.get("hva")
    if not isinstance(hva, dict):
        return [make("ASSET-003", "the inventory does not say whether the system is a "
                     "high-value asset", INVENTORY_FILE, None, {WRITER})]
    if hva.get("designated") is True and not hva.get("inventory_entry"):
        return [make("ASSET-003", "a high-value asset has no entry on the Component HVA "
                     "inventory", INVENTORY_FILE, None, {WRITER})]
    return []


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("ASSET-001", asset_scope), ("ASSET-002", inventory_items),
                ("ASSET-003", high_value_asset))
