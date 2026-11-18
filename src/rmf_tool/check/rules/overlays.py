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


# --- SPCOV-001: the Space Platform Overlay's scope -----------------------------------------

SPACE = "CNSSI1253F-ATT2-SPACE"
SPACE_SCOPE = ("space-platform", "link")
SSP_RECORDS = "artifacts/data/ssp-records.yaml"


def space_segments(ctx: Context) -> list[str] | None:
    """The segments of a space NSS the system is part of (categorization.space_segments), or
    None when it names none. SPCOV-001 and RAPT-001 read them here."""
    segments = _categorization(ctx).get("space_segments")
    return [s for s in segments if isinstance(s, str)] if isinstance(segments, list) else None


def space_scope(ctx: Context) -> list[RunFinding]:
    """The overlay's scope is the space platform and the link segment interfacing with it, not
    the ground or user segment (its Section 1), and it applies to every space NSS in that scope
    (Section 4). A system declared a space NSS elsewhere names its segments, so leaving them out
    is no way past the second test."""
    cat = _categorization(ctx)
    overlays = [o for o in cat.get("overlays") or () if isinstance(o, str)] \
        if isinstance(cat.get("overlays"), list) else []
    segments = space_segments(ctx)
    records = ctx.data(SSP_RECORDS)
    declared = isinstance(records, dict) and records.get("space_nss") is True
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SPCOV-001", message, "facts.yaml", None, {"C-2"}))

    if (SPACE in overlays or declared) and segments is None:
        err("a space NSS names its segments in categorization.space_segments (space-platform, "
            "link, ground, user)")
    if SPACE in overlays and segments and set(segments).isdisjoint(SPACE_SCOPE):
        err("the Space Platform Overlay's scope is the space platform and the link segment "
            f"interfacing with it, and the system is the {', '.join(segments)} segment")
    if segments and set(segments) & set(SPACE_SCOPE) and SPACE not in overlays:
        err("the system is a space platform or its link segment, and categorization.overlays "
            f"does not apply the Space Platform Overlay ({SPACE})")
    return out


# --- SPCOV-002: controls CNSSP 12 requires of a space NSS stay selected ---------------------

def space_policy_controls(ctx: Context) -> list[RunFinding]:
    """CNSSP 12 says what space NSS "must implement"; the Space Platform Overlay's controls
    whose guidance carries each duty stay in the baseline (framework/baselines/
    tailoring-inputs.yaml policy_controls), whatever S-2 tailors."""
    overlays = _categorization(ctx).get("overlays")
    applied = [o for o in overlays if isinstance(o, str)] if isinstance(overlays, list) else []
    required = [p for p in baseline_mod.load_inputs(ctx.run.repo).get("policy_controls") or []
                if p["overlay"] in applied]
    base = baseline_mod.load(ctx.run)
    if not required or base is None:
        return []
    selected = set(baseline_mod.control_ids(ctx.run))
    subset = ctx.run.config.get("control_subset")
    out = []
    for policy in required:
        absent = [c for c in policy["controls"] if c not in selected
                  and (not isinstance(subset, list) or c in subset)]
        if absent:
            duty = policy["text"][len("Space NSS "):].rstrip(".")
            out.append(make("SPCOV-002", f"{policy['id']}: {policy['authority']} requires of a "
                            f"space NSS that it {duty}, and "
                            f"{', '.join(absent)} is tailored out of the baseline",
                            "baseline.json", None, {"S-2"}))
    return out


# --- OVLX-001: overlays obtained from their owner -------------------------------------------

CLASSIFIED = "CNSSI1253E-ATT5-CLASSIFIED"
# Kinds whose overlay is no authority's own specification set, so a removal there is tailoring.
UNOWNED_KINDS = ("other", "dod-ks")
SAP_ASSUMPTION = "AS-CLS-1"  # holds: no SAP or SCI
DOMAINS_ASSUMPTION = "AS-ADD-3"  # holds: communicates across security domains

def _org_records(ctx: Context) -> list[dict[str, Any]]:
    data = ctx.data(baseline_mod.ORG_FILE)
    records = data.get("obtained_overlays") if isinstance(data, dict) else None
    return [r for r in records if isinstance(r, dict)] if isinstance(records, list) else []


def _assumption(data: dict[str, Any], aid: str) -> Any:
    return next((r.get("holds") for r in data.get("assumptions") or ()
                 if isinstance(r, dict) and r.get("id") == aid), None)


def obtained(ctx: Context) -> list[RunFinding]:
    """An overlay the library does not hold reaches a run through its owner (CNSSI 1253 page
    161): the CDS overlay and the Intelligence Overlay the Classified System Overlay leaves to
    them (its pages 2 and 4), a SAP authority's specifications, DoD-specific overlays on the RMF
    KS. One applied is applied on its applicability questions (CNSSI 1253 page 10)."""
    overlays = _categorization(ctx).get("overlays")
    applied = {o for o in overlays if isinstance(o, str)} if isinstance(overlays, list) else set()
    records = _org_records(ctx)
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("OVLX-001", message, "facts.yaml", None, {"C-2"}))

    kinds = {str(r.get("kind")) for r in records if r.get("id") in applied}
    for r in records:
        controls = r.get("controls") if isinstance(r.get("controls"), dict) else {}
        if controls.get("remove") and r.get("kind") in UNOWNED_KINDS:
            err(f"{r.get('id')} ({r.get('kind')}) tailors out "
                f"{', '.join(map(str, controls['remove']))}; a removal outside an overlay "
                "authority's own specifications is S-2 tailoring, tested by TLR-002")
        answers = [a.get("answer") for a in r.get("applicability") or () if isinstance(a, dict)]
        if r.get("id") in applied and True not in answers:
            err(f"{r.get('id')} is applied, and none of its applicability questions is answered "
                "yes for the system")
    if CLASSIFIED in applied:
        data = _tailoring(ctx) or {}
        if _assumption(data, SAP_ASSUMPTION) is False and kinds.isdisjoint(("intelligence", "sap")):
            err("the system holds classified information within a SAP or SCI, and applies "
                "neither the Intelligence Overlay nor the SAP authority's specifications "
                f"({baseline_mod.ORG_FILE} obtained_overlays, kind intelligence or sap)")
        if _assumption(data, DOMAINS_ASSUMPTION) is True and "cds" not in kinds:
            err("the classified system communicates across security domains, and applies no "
                f"cross domain solution overlay ({baseline_mod.ORG_FILE} obtained_overlays, "
                "kind cds)")
    return out


# --- SPCOV-003: a baseline-dependent overlay applied to another baseline --------------------

def tailored_baseline(ctx: Context) -> list[RunFinding]:
    """The Space Platform Overlay "is not baseline independent" and "tailors the CNSSI No. 1253
    (H/H/H) control baseline": applied to a system categorized otherwise, its removals and
    additions were not written for the baseline they change. A warning: the source does not
    forbid it, and S-2 tailoring can answer it."""
    cat = _categorization(ctx)
    overlays = cat.get("overlays")
    if not isinstance(overlays, list):
        return []
    try:
        tables = baseline_mod.load_tables(ctx.run)
    except baseline_mod.BaselineError:
        return []
    out = []
    for o in tables["overlays"]:
        tailors = o.get("tailors")
        if o["id"] not in overlays or not tailors:
            continue
        actual = {k: cat.get(k) for k in ("c", "i", "a")}
        if actual != tailors:
            out.append(make("SPCOV-003", f"{o['id']} tailors the "
                            f"{'/'.join(tailors[k][0].upper() for k in 'cia')} baseline, and the "
                            f"system is categorized {'/'.join(str(actual[k]) for k in 'cia')}",
                            "facts.yaml", None, {"S-2"}))
    return out
