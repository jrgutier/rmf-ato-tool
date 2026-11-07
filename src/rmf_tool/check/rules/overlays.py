"""Overlay control specifications, OVS-001 to OVS-003 (Tasks S-2 and S-4).

Section 6 of each transcribed overlay (``framework/baselines/overlay-specs.yaml``) gives a
control its justification, guidance, parameter values and regulatory/statutory references.
These rules read it only for the overlays the run applies (``categorization.overlays``),
and only for the control sets the run names.
"""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog, overlay_specs
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.check.rules.tailoring import TAILORING, _actions, _active, _categorization, _tailoring

# Who coordinates a control the Privacy Overlays say not to select: the SAOP, whom PER-PRIV
# plays, or a designee, who records designee_of: PER-PRIV (CNSSI 1253F Att. 6, AC-2(8)).
SAOP = "PER-PRIV"
# An SSP status under which the system sets no parameter of its own: the provider does, or the
# control does not apply.
NO_OWN_VALUES = ("inherited", "not-applicable")


def _applied(ctx: Context) -> dict[str, list[overlay_specs.Applied]]:
    overlays = _categorization(ctx).get("overlays")
    if not isinstance(overlays, list) or not overlays:
        return {}
    return overlay_specs.applied(ctx.run.repo, overlays)


# --- OVS-001: removing an overlay control is tested against the authorities it cites -----

def removal_authorities(ctx: Context) -> list[RunFinding]:
    """A control an applied overlay selects is tailored out only after the laws, regulations
    and policies the overlay cites for it are tested: each names in law_policy.authorities
    (CNSSI 1253E Att. 5 and 1253F Att. 6, Section 6 Reference(s))."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    specs = _applied(ctx)
    out: list[RunFinding] = []
    for a in _actions(data):
        cid = a.get("control_id")
        law = a.get("law_policy")
        if a.get("action") != "remove" or not isinstance(law, dict) or not isinstance(cid, str):
            continue  # TLR-002 reports a removal with no law and policy test
        recorded = law.get("authorities") if isinstance(law.get("authorities"), list) else []
        for spec in specs.get(cid, []):
            if spec.disposition != "select":
                continue  # a recommended control is optional, and may be left out
            unnamed = [n for n in spec.authorities if not overlay_specs.named(n, recorded)]
            if unnamed:
                out.append(make("OVS-001", f"{cid} is removed, and law_policy.authorities does "
                                f"not name {', '.join(unnamed)}, which the {spec.title} "
                                "references cite for it", TAILORING, None, {"S-2"}))
    return out


# --- OVS-002: a control the Privacy Overlays say not to select ---------------------------

def not_selected(ctx: Context) -> list[RunFinding]:
    """A control the applied Privacy Overlays control set justifies not selecting is selected
    only after coordinating with the SAOP or designee: the tailoring action that keeps or adds
    it records privacy_coordination by PER-PRIV or a designee of PER-PRIV (CNSSI 1253F Att. 6,
    AC-2(8))."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    selected = set(baseline_mod.control_ids(ctx.run))
    coordinated: dict[str, Any] = {}
    for a in _actions(data):
        if a.get("action") != "remove" and isinstance(a.get("privacy_coordination"), dict) \
                and isinstance(a.get("control_id"), str):
            coordinated[a.get("control_id")] = a["privacy_coordination"]
    out: list[RunFinding] = []
    for cid, specs in _applied(ctx).items():
        if cid not in selected or not any(s.disposition == "not-select" for s in specs):
            continue
        record = coordinated.get(cid)
        if record is None:
            out.append(make("OVS-002", f"{cid} is selected, and no tailoring action records "
                            "the coordination with the SAOP or designee that the Privacy "
                            "Overlays require before it is selected", TAILORING, None, {"S-2"}))
        elif SAOP not in (record.get("by"), record.get("designee_of")):
            out.append(make("OVS-002", f"{cid}: the coordination before selecting it is with "
                            f"{record.get('by')}, not the SAOP or designee ({SAOP})", TAILORING,
                            None, {"S-2"}))
    return out


# --- OVS-003: parameter values the overlay assigns reach the SSP ---------------------------

def _recorded(cat: catalog.Catalog, params: Any) -> set[str]:
    if not isinstance(params, dict):
        return set()
    out = set()
    for pid in params:
        if not isinstance(pid, str):
            continue
        out.add(pid)
        out.update(overlay_specs.aggregated(cat, pid))
    return out


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _tailored_values(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """control -> the parameter values S-2 assigned by a tailoring parameter action."""
    out: dict[str, dict[str, Any]] = {}
    for a in _actions(data):
        param = _mapping(a.get("parameter"))
        cid, pid = a.get("control_id"), param.get("param_id")
        if a.get("action") == "parameter" and isinstance(cid, str) and isinstance(pid, str) \
                and param.get("value"):
            out.setdefault(cid, {})[pid] = param["value"]
    return out


def parameter_values(ctx: Context) -> list[RunFinding]:
    """A value is recorded, in the SSP control statement or by a tailoring parameter action,
    for each organization-defined parameter an applied overlay assigns a value to (Section 6
    Parameter Value(s)), unless the control is inherited or not applicable."""
    specs = _applied(ctx)
    if not specs:
        return []
    cat = catalog.load(ctx.run.repo)
    tailored = _tailored_values(_tailoring(ctx) or {})
    out: list[RunFinding] = []
    for rel, item in family_records(ctx, SSP_DIR, "controls"):
        cid = item.get("control_id")
        if not isinstance(cid, str) or item.get("status") in NO_OWN_VALUES or cid not in specs:
            continue
        recorded = _recorded(cat, {**tailored.get(cid, {}), **_mapping(item.get("parameters"))})
        for spec in specs[cid]:
            if spec.disposition == "not-select":
                continue
            for statement in spec.statements:
                if statement["kind"] != "parameter":
                    continue
                wanted = overlay_specs.assigned_params(cat, cid, statement["text"])
                unset = [p for p in wanted if p not in recorded]
                if unset:
                    out.append(make("OVS-003", f"{cid} records no value for {', '.join(unset)}; "
                                    f"the {spec.title} assigns a parameter value for it",
                                    rel, None, {"S-4"}))
    return out
