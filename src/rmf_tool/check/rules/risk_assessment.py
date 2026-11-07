"""System risk assessment rules SRA-001 to SRA-004 (SP 800-30 Rev. 1, SP 800-37 Rev. 2 Task
P-14, CNSSI 1254 Annex C). SRA-001 to SRA-003 read artifacts/data/ra.yaml, which P-14 writes;
SRA-004 reads the residual levels and control counts of rar.yaml, which R-2 writes. Each stays
quiet about a file that is unreadable (RUN-FM-001 reports it)."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.consistency import BOUNDARY_FILE, INVENTORY_FILE, RAR_FILE, STIG_FILE
from rmf_tool.check.rules.content import SAR_DIR, family_records
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

RA_FILE = "artifacts/data/ra.yaml"
LEVELS = ("very-low", "low", "moderate", "high", "very-high")
SPACE_OVERLAY = "CNSSI1253F-ATT2-SPACE"
MISSION_OWNERS = ("PER-PM", "PER-SPONSOR")
AUTHORIZING = ("PER-AO", "PER-AODR")  # the AODR may act for the AO in everything but the decision


def _in_play(ctx: Context) -> bool:
    """ART-RA is produced or seeded and the run's contract has ra.yaml."""
    return scope.produced_or_seeded(ctx.run, "ART-RA") and any(
        d["path"] == RA_FILE for d in ctx.run.artifacts["ART-RA"].get("data") or ())


def _ra(ctx: Context) -> dict[str, Any] | None:
    data = ctx.data(RA_FILE) if _in_play(ctx) else None
    return data if isinstance(data, dict) else None


def _list(data: Any, key: str) -> list[dict[str, Any]]:
    value = data.get(key) if isinstance(data, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _refs(item: dict[str, Any], key: str) -> list[str]:
    """The string IDs a field lists; a malformed field is RUN-FM-001's to report."""
    value = item.get(key)
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _id(item: dict[str, Any], key: str = "id") -> str | None:
    value = item.get(key)
    return value if isinstance(value, str) else None


def _ids(items: list[dict[str, Any]]) -> set[str]:
    return {i for i in map(_id, items) if i}


# --- SRA-001 ----------------------------------------------------------------------------

def threat_model(ctx: Context) -> list[RunFinding]:
    """The threat sources, events, vulnerabilities and information sources hold together."""
    if not _in_play(ctx):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SRA-001", message, RA_FILE))

    if not ctx.run.path(RA_FILE).is_file():
        err("ART-RA has no artifacts/data/ra.yaml, so the risk assessment records no threat "
            "sources, threat events, likelihood or impact")
        return out
    data = _ra(ctx)
    if data is None:
        return out
    sources = {_id(s): s for s in _list(data, "threat_sources") if _id(s)}
    weaknesses = _ids(_list(data, "vulnerabilities")) | _ids(
        _list(data, "predisposing_conditions"))
    events = _list(data, "threat_events")
    for s in sources.values():
        if s.get("type") == "adversarial":
            if s.get("capability") == "not-applicable":
                err(f"{s.get('id')} is an adversarial threat source with no assessed capability "
                    "to initiate a threat event")
            if s.get("intent") == "not-applicable":
                err(f"{s.get('id')} is an adversarial threat source with no assessed intent "
                    "to initiate a threat event")
            if s.get("targeting") == "not-applicable":
                err(f"{s.get('id')} is an adversarial threat source with no assessed targeting "
                    "of the system")
        elif s.get("range_of_effects") == "not-applicable":
            err(f"{s.get('id')} is a non-adversarial threat source with no assessed range of "
                "effects")
    for e in events:
        named = [ref for ref in _refs(e, "threat_sources") if ref in sources]
        for ref in _refs(e, "threat_sources"):
            if ref not in sources:
                err(f"{e.get('id')} names threat source {ref}, which ra.yaml does not list")
        for ref in [*_refs(e, "vulnerabilities"), *_refs(e, "conditions")]:
            if ref not in weaknesses:
                err(f"{e.get('id')} names {ref}, which is no vulnerability or predisposing "
                    "condition in ra.yaml")
        if named and e.get("relevance") != "not-applicable" and all(
                sources[ref].get("in_scope") is False for ref in named):
            err(f"{e.get('id')} is initiated only by threat sources judged not relevant or out "
                "of scope")
    known = _ids(events)
    for scenario in _list(data, "threat_scenarios"):
        for ref in _refs(scenario, "events"):
            if ref not in known:
                err(f"{scenario.get('id')} names threat event {ref}, which ra.yaml does not list")
    kinds = {s.get("kind") for s in _list(data, "information_sources")}
    missing = [k for k in ("threat", "vulnerability", "impact") if k not in kinds]
    if missing:
        err(f"ra.yaml names no source of {', '.join(missing)} information; the sources of "
            "threat, vulnerability and impact information are identified")
    return out


# --- SRA-002 ----------------------------------------------------------------------------

def _space(ctx: Context) -> bool:
    categorization = facts_mod.get(ctx.facts, "categorization")
    overlays = categorization.get("overlays") if isinstance(categorization, dict) else None
    return isinstance(overlays, list) and SPACE_OVERLAY in overlays


def external_risk(ctx: Context) -> list[RunFinding]:
    """Connections, external providers and suppliers each carry the risk they introduce."""
    data = _ra(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SRA-002", message, RA_FILE))

    ext = data.get("external") if isinstance(data.get("external"), dict) else {}
    weaknesses = _ids(_list(data, "vulnerabilities")) | _ids(
        _list(data, "predisposing_conditions"))
    connections = {_id(c, "component"): c for c in _list(ext, "connections")
                   if _id(c, "component")}
    providers = _list(ext, "providers")
    supplied = {_id(p, "component") for p in providers}
    for comp in _list(ctx.data(BOUNDARY_FILE), "components"):
        cid = comp.get("id")
        if comp.get("external") is True or comp.get("type") == "interconnection":
            if cid not in connections:
                err(f"external component {cid} has no connection record in ra.yaml, so the "
                    "risk its connection and information exchange introduce is not considered")
            if comp.get("type") == "service" and cid not in supplied:
                err(f"external service {cid} has no record in external.providers, so who "
                    "supplies it, its services and assurances are not documented")
    for cid, c in connections.items():
        for ref in _refs(c, "introduces"):
            if ref not in weaknesses:
                err(f"connection {cid} introduces {ref}, which is no vulnerability or "
                    "predisposing condition in ra.yaml")
    if ext.get("services_provided") is False and any(
            p.get("kind") == "service-provider" for p in providers):
        err("external.services_provided is false, yet ra.yaml lists external providers of "
            "services")
    for p in providers:
        pid, response = p.get("id"), p.get("response")
        if p.get("trust") == "insufficient" and response == "none":
            err(f"{pid}: trust in it gives insufficient assurance and no response is recorded "
                "(compensating controls, greater risk, a more trustworthy source or not "
                "obtaining the service)")
        if p.get("risk_acceptable") is False and response == "none":
            err(f"{pid}: the risk arising from use of the external services is not acceptable "
                "and no response is recorded")
        if response == "compensating-controls" and not p.get("compensating_controls"):
            err(f"{pid} employs compensating controls but names none")
    inventory = _ids(_list(ctx.data(INVENTORY_FILE), "items"))
    chained: set[Any] = set()
    for record in _list(ext, "supply_chain"):
        for ref in _refs(record, "items"):
            chained.add(ref)
            if ref not in inventory:
                err(f"supply chain record {record.get('id')} names {ref}, which is no "
                    "inventory item")
        for ref in _refs(record, "vulnerabilities"):
            if ref not in weaknesses:
                err(f"supply chain record {record.get('id')} names {ref}, which is no "
                    "vulnerability or predisposing condition in ra.yaml")
    for ref in sorted(inventory):
        if ref not in chained:
            err(f"inventory item {ref} is in no supply chain record, so its supply chain risk "
                "is not considered")
    if _space(ctx):
        out += _space_findings(ext)
    return out


def _space_findings(ext: dict[str, Any]) -> list[RunFinding]:
    """CNSSP 12: a space NSS weighs each non-NSS component in one end-to-end analysis of risks,
    which the mission owner and the AO or AODR make in coordination with the NSA."""
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SRA-002", message, RA_FILE))

    non_nss = [c for c in _list(ext, "connections") if c.get("nss") is False]
    for c in non_nss:
        if not c.get("end_to_end_impact"):
            err(f"connection {c.get('component')} to a non-NSS component states no end-to-end "
                "impact")
    analysis = ext.get("end_to_end_analysis") if isinstance(
        ext.get("end_to_end_analysis"), dict) else {}
    by, names = set(_refs(analysis, "considered_by")), ", ".join(
        str(c.get("component")) for c in non_nss)
    if non_nss and "nsa" not in _refs(analysis, "coordinated_with"):
        err(f"the end-to-end analysis of risks over non-NSS components ({names}) is not "
            "coordinated with the NSA")
    if non_nss and (not by & set(MISSION_OWNERS) or not by & set(AUTHORIZING)):
        err(f"the impact of non-NSS components ({names}) was not considered by both the "
            "mission owner and the AO or AODR")
    for n in _list(ext, "nonconforming"):
        if "nsa" not in _refs(n, "coordinated_with"):
            err(f"{n.get('component')} is not built to fully meet the policy, and its "
                "comparison of alternatives was not coordinated with the NSA")
    return out


# --- SRA-003 ----------------------------------------------------------------------------

def prioritization(ctx: Context) -> list[RunFinding]:
    """The priority order ranks every threat event once and never a lower risk first."""
    data = _ra(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SRA-003", message, RA_FILE))

    plan = data.get("prioritization") if isinstance(data.get("prioritization"), dict) else {}
    order = _refs(plan, "order")
    events = [e for e in _list(data, "threat_events") if _id(e)]
    risk = {_id(e): e.get("risk") for e in events}
    # SP 800-30 pp. 40 and 42: an event that is not relevant, or that no vulnerability or
    # predisposing condition bears on, drops from further consideration.
    considered = {_id(e) for e in events if e.get("relevance") != "not-applicable"
                  and (_refs(e, "vulnerabilities") or _refs(e, "conditions"))}
    for ref in sorted(considered):
        if ref not in order:
            err(f"prioritization.order leaves out threat event {ref}")
    for ref in order:
        if ref not in risk:
            err(f"prioritization.order names {ref}, which ra.yaml does not list")
    ranked = [(ref, risk[ref]) for ref in order if risk.get(ref) in LEVELS]
    for (first, high), (then, low) in zip(ranked, ranked[1:], strict=False):
        if LEVELS.index(high) < LEVELS.index(low):
            err(f"prioritization.order ranks a lower risk above a higher one: {first} ({high}) "
                f"before {then} ({low})")
    for coupling in _list(plan, "couplings"):
        for ref in _refs(coupling, "events"):
            if ref not in risk:
                err(f"a coupling names threat event {ref}, which ra.yaml does not list")
    return out


# --- SRA-004 ----------------------------------------------------------------------------

def rar_residual(ctx: Context) -> list[RunFinding]:
    """Each RAR risk states its residual level, and the RAR counts the controls per level."""
    data = ctx.data(RAR_FILE)
    if not scope.produced_or_seeded(ctx.run, "ART-RAR") or not isinstance(data, dict):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SRA-004", message, RAR_FILE))

    risks = _list(data, "risks")
    for r in risks:
        if r.get("residual_level") is None:
            err(f"{r.get('id')} records no residual risk level expected after the mitigations "
                "in the POA&M are implemented")
    declared = data.get("controls_by_level")
    if not isinstance(declared, dict):
        err("rar.yaml records no number of controls with risks identified at each level of risk")
        return out
    findings = [f for _, f in family_records(ctx, SAR_DIR, "findings")]
    controls = {_id(f): _id(f, "control_id")
                for f in [*findings, *_list(ctx.data(STIG_FILE), "findings")] if _id(f)}
    if any(ref not in controls for r in risks for ref in _refs(r, "finding_refs")):
        return out  # a finding the RAR links that does not exist is RAR-001's to report
    for level in LEVELS:
        found = {controls.get(ref) for r in risks if r.get("level") == level
                 for ref in _refs(r, "finding_refs")} - {None}
        if declared.get(level) != len(found):
            err(f"controls_by_level gives {declared.get(level)} for {level}; the risks identify "
                f"{len(found)} controls at that level")
    return out


# --- RARC-001 ---------------------------------------------------------------------------
RISK_FACTORS = ("threat", "vulnerability", "impact", "likelihood", "predisposing-condition")


def report_content(ctx: Context) -> list[RunFinding]:
    """What a risk assessment report states beyond the threat model (SP 800-30 App. K, DoDI
    8500.01 3.f)."""
    data = _ra(ctx)
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RARC-001", message, RA_FILE))

    if "date" not in data:
        err("ra.yaml has no date: the risk assessment report lists the date of the risk "
            "assessment")
    if "team" not in data:
        err("ra.yaml has no team: the risk assessment report lists the team or individuals "
            "conducting it, with contact information")
    if "rationales" not in data:
        err("ra.yaml has no rationales: the risk assessment report lists the rationale for each "
            "risk-related decision, or an empty list")
    if "tailoring" not in data:
        err("ra.yaml has no tailoring: the risk assessment report lists any tailoring of its "
            "robustness, or an empty list")
    purpose = data.get("purpose") if isinstance(data.get("purpose"), dict) else {}
    update = purpose.get("update") if isinstance(purpose.get("update"), dict) else {}
    if purpose.get("kind") == "subsequent":
        if not update.get("circumstances"):
            err("ra.yaml is a subsequent risk assessment with no update.circumstances: it states "
                "the circumstances that prompted it")
        if not update.get("previous"):
            err("ra.yaml is a subsequent risk assessment with no update.previous: it states a "
                "reference to the previous risk assessment report")
    model = data.get("risk_model") if isinstance(data.get("risk_model"), dict) else {}
    factors = model.get("factors") if isinstance(model.get("factors"), list) else []
    unused = [f for f in RISK_FACTORS if f not in factors]
    if unused:
        err(f"the risk model leaves out {', '.join(unused)}: all of the risk factors of SP "
            "800-30 are used across the DoD, so risk information is reciprocal")
    tailored = _list(data, "tailoring")
    communication = data.get("communication") if isinstance(data.get("communication"),
                                                            dict) else {}
    if tailored and not set(_refs(communication, "recipients")) & set(AUTHORIZING):
        err("ra.yaml tailors the robustness of the assessment but communicates the results to "
            "no AO or AODR: tailoring is explained so AOs understand to what degree they can "
            "rely on the results")
    return out
