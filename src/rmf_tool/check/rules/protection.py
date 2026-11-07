"""The program protection records, PPROT-001 to PPROT-006, and the pathway release gates,
GATE-001 (DoDI 5000.83, DoDI 8500.01, DoDI 8510.01, CNSSP 12). P-14 writes protection.yaml beside
ART-RA and, for a technology that transitions from S&T, st-protection.yaml; P-15 and P-17 write
protection-requirements.yaml beside ART-REQ; P-16 writes nss-assessments.yaml beside ART-BND.

A rule judges its record while the task that writes it is in scope, and says so when the record
is missing then; with the task out of scope it judges the record only if the run holds it, so a
run that seeds the artifact without the record is not refused. A rule that reads a second record
reads it only when the run holds it.

Acquisition decision points come from framework/milestones.yaml on the spine pathway and from
`decision_points` in framework/pathways.yaml on the others; the dates a program passed them are
in protection.yaml `program.decision_points`.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.plans import _space
from rmf_tool.run import authorization as ledger
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

PROT_FILE = "artifacts/data/protection.yaml"
ST_FILE = "artifacts/data/st-protection.yaml"
PREQ_FILE = "artifacts/data/protection-requirements.yaml"
NSS_FILE = "artifacts/data/nss-assessments.yaml"

USD_RE = "USD(R&E)"
DELEGATED = ("CAE", "CAE-designee")  # DoDI 5000.83 2.2.e: the CAE or a designee
DELEGATED_PATHWAYS = ("PW-UCA", "PW-MTA", "PW-SWP")  # 2.2.e.(2): urgent, middle tier, software
MCA = "PW-MCA"
PPP_PATHWAYS = (MCA, "PW-UCA", "PW-MTA", "PW-SWP")  # DoDI 5000.83 3.5
# milestones.yaml kinds: decision points and milestones, not life-cycle events (IOC, FOC).
MCA_KINDS = ("milestone", "decision-point")
MILESTONES = ("milestone",)  # CNSSP 12 and DoDI 8510.01: before all (major) acquisition milestones
DELEGATED_ACAT = ("IB", "IC", "II", "III")  # 2.2.e.(1), on major capability programs
MDAP_ACAT = ("ID", "IB", "IC")
# The MDD is the entry into the pathway, before a program exists to protect (DoDI 5000.85 3.5).
ENTRY = "MS-MDD"
PREPARERS = ("PER-LSE", "PER-PM")  # DoDI 5000.83 5.3.c; DoDI 5000.88 3.4.c has the PM prepare it
CRE = "cyber-resilient-engineering"
RISK_SOURCES = ("design-vulnerability", "supply-chain-exploit-insertion", "battlefield-loss")
# Full-rate production or full-deployment decision (DoDI 5000.83 5.3.c.(3)).
FULL_RATE = ("MS-FRP", "DP-DBS-FULL")
# Decision points after which the system is fielded.
FIELDED = ("MS-IOC", "MS-FOC", "DP-UCA-PRODUCTION", "DP-DBS-LIMITED", "DP-DBS-FULL",
           "DP-SWP-MVCR")
# DoDI 5000.88 3.5.b.(1)(b): before Milestones A and B and the LRIP and FRP decisions.
ITRA_POINTS = ("MS-A", "MS-B", "MS-C", "MS-FRP")
SPONSOR = "PER-SPONSOR"
PLAN_TOPICS = ("scrm", "export-control", "anti-tamper")  # DoDI 5000.83 2.8.a
CI_SUPPORT = "counterintelligence-security-support"  # 2.8.b
THREAT_INFO = "threat-information"  # 2.8.c
ASSURANCE = ("software-assurance", "hardware-assurance")
NSA = "NSA"
AO_ROLES = ("PER-AO", "PER-AODR")  # the cognizant AO; the AODR acts for the AO but in the decision
NSS_COVERS = ("cybersecurity-requirements", "security-architecture")
Check = Callable[[str], None]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


def _ids(items: Any) -> set[str]:
    """A list field as a set of strings; anything else, which the schema refuses, as empty."""
    return {str(i) for i in items if not isinstance(i, dict | list)} if isinstance(items, list) \
        else set()


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _record(ctx: Context, rule: str, rel: str, task: str,
            owed: bool = True) -> tuple[dict[str, Any] | None, list[RunFinding], Check]:
    """The record a task writes, the findings so far and an error helper. A missing record is a
    finding while its task is in scope and the run owes it; an unreadable one is RUN-FM-001's."""
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, rel, None, {task}))

    if not owed:
        return None, out, err
    if not ctx.run.path(rel).is_file():
        if task in scope.active_tasks(ctx.run):
            err(f"{rel} is missing; {task} writes it")
        return None, out, err
    data = ctx.data(rel)
    return (data if isinstance(data, dict) else None), out, err


def _pathway(ctx: Context) -> str | None:
    acquisition = facts_mod.get(ctx.facts, "acquisition")
    return acquisition.get("pathway") if isinstance(acquisition, dict) else None


def decision_points(ctx: Context, pathway: str | None,
                    kinds: tuple[str, ...] = MCA_KINDS) -> set[str]:
    """The decision points of a pathway: the milestones of these kinds on the spine, its own list
    otherwise. Empty for a pathway whose decision points the framework does not list yet, and a
    clause reading it then stays quiet."""
    return {i for i, kind in _points(ctx, pathway).items() if kind in kinds}


def _points(ctx: Context, pathway: str | None) -> dict[str, Any]:
    """Each decision point of a pathway with its kind, from milestones.yaml on the spine and
    from pathways.yaml otherwise."""
    if pathway == ctx.run.framework.meta.get("spine_pathway"):
        return {i: m.data.get("kind") for i, m in ctx.run.framework.index("milestones").items()}
    entity = ctx.run.framework.index("pathways").get(pathway or "")
    return {d.get("id"): d.get("kind")
            for d in _dicts(entity.data.get("decision_points") if entity else None)}


def _ppp_owed(ctx: Context) -> bool:
    """DoDI 5000.83 3.5 tailors program protection for these pathways; DoDI 5000.74 and 5000.75
    never ask a business system or an acquisition of services for a PPP. With no pathway in
    facts.yaml the PPP is asked for."""
    pathway = _pathway(ctx)
    return pathway is None or pathway in PPP_PATHWAYS


def _passed(program: dict[str, Any]) -> dict[str, dt.date | None]:
    return {str(d.get("id")): _day(d.get("date")) for d in _dicts(program.get("decision_points"))}


def _protection(ctx: Context) -> dict[str, Any]:
    data = ctx.data(PROT_FILE) if ctx.run.path(PROT_FILE).is_file() else None
    return data if isinstance(data, dict) else {}


# --- PPROT-001: approval and submission of the PPP ---------------------------------------

def ppp_approval(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-001", PROT_FILE, "P-14", _ppp_owed(ctx))
    if data is None:
        return out
    program, ppp = _dict(data.get("program")), _dict(data.get("ppp"))
    authority = _dict(ppp.get("approval")).get("authority")
    acat, mda, pathway = program.get("acat"), program.get("mda"), _pathway(ctx)
    if acat == "ID" and authority != USD_RE:
        err(f"the USD(R&E) is the PPP approval authority for an ACAT ID program, not {authority}")
    if mda == "DAE" and authority != USD_RE:
        err("where the DAE is the milestone decision authority, the USD(R&E) is the PPP approval "
            f"authority, not {authority}")
    if acat != "ID" and mda != "DAE":
        if pathway == MCA and acat in DELEGATED_ACAT and authority not in DELEGATED:
            err("the Component acquisition executive or a designee approves the PPP of an ACAT "
                f"IB, IC, II or III major capability program, not {authority}")
        if pathway in DELEGATED_PATHWAYS and authority not in DELEGATED:
            err("the Component acquisition executive or a designee approves the PPP of an urgent, "
                f"middle tier or software program, not {authority}")
    valid = decision_points(ctx, pathway)
    every = decision_points(ctx, pathway, ("milestone", "decision-point", "event"))
    passed = _passed(program)
    for point in sorted(p for p in passed if every and p not in every):
        err(f"{point} is no decision point of the {pathway} pathway")
    submitted = {str(s.get("decision_point")): _day(s.get("date"))
                 for s in _dicts(ppp.get("submissions"))}
    for point, date in sorted(passed.items()):
        if point == ENTRY or point not in valid:
            continue
        when = submitted.get(point)
        if when is None or (date is not None and when > date):
            err(f"the PPP is submitted for approval at each acquisition pathway decision point, "
                f"and no submission precedes {point}")
    if ppp.get("cybersecurity_strategy") != "appendix":
        err("the cybersecurity strategy is submitted as an appendix to the PPP, not "
            f"{ppp.get('cybersecurity_strategy')}")
    return out


# --- PPROT-002: content, updates and transition of the PPP --------------------------------

def ppp_content(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-002", PROT_FILE, "P-14", _ppp_owed(ctx))
    if data is None:
        return out
    program, ppp = _dict(data.get("program")), _dict(data.get("ppp"))
    if ppp.get("prepared_by") not in PREPARERS:
        err("the lead systems engineer prepares the PPP (the PM under DoDI 5000.88), not "
            f"{ppp.get('prepared_by')}")
    if CRE not in _ids(ppp.get("sse_activities")):
        err("the PPP guides the systems security engineering activities, to include cyber "
            "resilient engineering")
    items = {i.get("id") for i in _dicts(ppp.get("critical_items"))}
    countered = {c.get("item") for c in _dicts(ppp.get("countermeasures"))}
    for item in sorted(items - countered):
        err(f"critical item {item} has no planned countermeasure to mitigate its risks")
    for item in sorted(str(i) for i in countered - items):
        err(f"a countermeasure protects {item}, which is no critical item of the PPP")
    threatened = {t.get("item") for t in _dicts(ppp.get("threats"))}
    for item in sorted(items - threatened):
        err(f"critical item {item} has no threat and vulnerability recorded in the PPP")
    left_out = set(RISK_SOURCES) - _ids(ppp.get("risk_sources"))
    if left_out:
        err("program protection planning manages the risk of foreign collection due to design "
            "vulnerability, supply chain exploit insertion and battlefield loss; it leaves out "
            f"{', '.join(sorted(left_out))}")
    risks = {r.get("id") for r in _dicts(data.get("technical_risks"))}
    for c in _dicts(ppp.get("countermeasures")):
        for risk in sorted(_ids(c.get("mitigates")) - risks):
            err(f"{c.get('id')} mitigates {risk}, which is no technical risk of the design and "
                "technical risk assessment process")
    _anti_tamper(data, err)
    pathway = _pathway(ctx)
    tailored = _dict(ppp.get("tailoring")).get("pathway")
    if pathway and tailored != pathway:
        err(f"program protection is tailored to the program's pathway {pathway}, not {tailored}")
    _updates(data, err)
    passed = _passed(program)
    transition = _dict(ppp.get("transition"))
    if set(passed) & set(FULL_RATE) and transition.get("to") != "sustainment-pm":
        err("after the full-rate production or full-deployment decision the PPP transitions to "
            "the program manager responsible for system sustainment and disposal")
    return out


def _anti_tamper(data: dict[str, Any], err: Check) -> None:
    at = _dict(_dict(data.get("ppp")).get("anti_tamper"))
    read = {h.get("id") for h in _dicts(_dict(data.get("inputs")).get("horizontal_protection"))}
    guidance = _ids(at.get("guidance"))
    unread = guidance - read
    if at.get("outside_us_control") is True and (unread or not guidance):
        err("AT and exportability requirements for technology outside U.S. control are determined "
            "by applying DoD horizontal protection guidance the run read")
    if at.get("required") is True and not at.get("coordinated_with"):
        err("AT is coordinated with the DoD Component office of primary responsibility for DoD AT")
    fielded = set(_passed(_dict(data.get("program")))) & set(FIELDED)
    if at.get("required") is True and fielded and at.get("monitored") is not True:
        err("AT protections implemented in fielded systems are monitored")


def _updates(data: dict[str, Any], err: Check) -> None:
    updates = _dicts(_dict(data.get("ppp")).get("updates"))

    def updated(kind: str, ref: Any, date: dt.date | None) -> bool:
        return any(u.get("after") == kind and u.get("ref") == ref and date is not None
                   and (_day(u.get("date")) or dt.date.min) >= date for u in updates)

    for award in _dicts(data.get("contract_awards")):
        if award.get("no_update_reason"):
            continue
        if not updated("contract-award", award.get("id"), _day(award.get("date"))):
            err(f"the PPP is not updated after contract award {award.get('id')} to reflect the "
                "contractor's approved technical approach")
    for event in _dicts(data.get("significant_events")):
        if event.get("no_update_reason"):
            continue
        if not updated(str(event.get("kind")), event.get("id"), _day(event.get("date"))):
            err(f"the PPP is not updated after {event.get('id')}, a significant threat activity "
                "or compromise")


# --- PPROT-003: TAPPs, horizontal protection and the S&T protection plan ------------------

def st_protection(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-003", PROT_FILE, "P-14",
                                 _ppp_owed(ctx) or ctx.run.path(PROT_FILE).is_file())
    if data is None:
        return out
    program, inputs = _dict(data.get("program")), _dict(data.get("inputs"))
    informed = _ids(_dict(data.get("ppp")).get("informed_by"))
    tech = _dict(program.get("critical_technology"))
    tapps = _dicts(inputs.get("tapps"))
    if tech.get("associated") is True:
        covered = {t.get("area") for t in tapps}
        for area in sorted(_ids(tech.get("areas")) - covered):
            err(f"{area} is a modernization priority area with no applicable TAPP read")
    for tapp in tapps:
        if tapp.get("id") not in informed:
            err(f"TAPP {tapp.get('id')} is read and does not inform the program protection "
                "activities")
    held = ctx.run.path(ST_FILE).is_file()
    if program.get("origin") != "st-transition":
        if held:
            err("st-protection.yaml holds an S&T protection plan, and program.origin is not "
                "st-transition")
        return out
    plan = ctx.data(ST_FILE) if held else None
    if not isinstance(plan, dict):
        err("the technology transitions from S&T, and st-protection.yaml holds no S&T protection "
            "plan")
        return out
    if plan.get("id") not in informed:
        err(f"the S&T protection plan {plan.get('id')} does not inform the PPP")
    elements = {e.get("id") for e in _dicts(plan.get("critical_technology_elements"))}
    for element in sorted(elements - {t.get("element") for t in _dicts(plan.get("threats"))}):
        err(f"{element} has no threat and vulnerability in the S&T protection plan")
    for element in sorted(elements - {c.get("element")
                                      for c in _dicts(plan.get("countermeasures"))}):
        err(f"{element} has no countermeasure selected in the S&T protection plan")
    approval = _dict(plan.get("approval"))
    submitted, approved = _day(approval.get("submitted")), _day(approval.get("project_approved"))
    if submitted and approved and submitted > approved:
        err(f"the S&T protection plan is submitted for approval before project approval, not on "
            f"{submitted} after {approved}")
    transition = _dict(plan.get("transition"))
    if transition.get("to") != "PER-LSE":
        err("S&T managers transition the S&T protection plan to the lead systems engineer "
            f"responsible for system development, not {transition.get('to')}")
    conditions = _ids(transition.get("conditions"))
    if "technology-transition-decision" not in conditions:
        err("the S&T protection plan transitions once a technology transition decision has been "
            "made")
    if "technology-transfer-requirements-met" not in conditions:
        err("the S&T protection plan transitions once technology transfer requirements have been "
            "met to inform the PPP")
    return out


# --- PPROT-004: protection requirements and solicitations ---------------------------------

def protection_requirements(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-004", PREQ_FILE, "P-15")
    if data is None:
        return out
    prot = _protection(ctx)
    ppp, inputs = _dict(prot.get("ppp")), _dict(prot.get("inputs"))
    read = _dict(data.get("read"))
    if prot and read.get("ppp") != ppp.get("id"):
        err(f"P-15 reads the program's PPP {ppp.get('id')}, not {read.get('ppp')}")  # a stable id
    tapps = {t.get("id") for t in _dicts(inputs.get("tapps"))}
    read_on = _day(read.get("date"))
    before = {t.get("id") for t in _dicts(inputs.get("tapps"))
              if read_on is None or (_day(t.get("date")) or dt.date.min) <= read_on}
    for tapp in sorted(str(t) for t in before - _ids(read.get("tapps"))):
        err(f"protection-requirements.yaml does not name {tapp}, a TAPP the run read")
    content = {c.get("topic"): c for c in
               _dicts(_dict(data.get("capability_document")).get("protection_content"))}
    prq = {r.get("id") for r in _dicts(data.get("requirements"))}
    for topic in PLAN_TOPICS:
        entry = content.get(topic)
        if _unraised(entry):
            err(f"{topic} requirements to achieve technology and program protection are not in "
                "the JCIDS capability requirements, and the gap is not raised to the sponsor")
        elif _dict(entry).get("included") is True:
            if not _ids(_dict(entry).get("addressed_by")) & prq:
                err(f"{topic} is in the capability requirements and addressed by no protection "
                    "requirement during capability development")
    if _unraised(content.get(CI_SUPPORT)):
        err("counterintelligence and security support for technology and program protection is "
            "not identified in the JCIDS processes, and the gap is not raised to the sponsor")
    if _unraised(content.get(THREAT_INFO)):
        err("foreign intelligence entity, cyber and supply chain threat information is not in "
            "the JCIDS capability requirements, and the gap is not raised to the sponsor")
    countermeasures = {c.get("id") for c in _dicts(ppp.get("countermeasures"))}
    known = countermeasures | tapps | _ids(read.get("st_protection_plans")) \
        | {_dict(data.get("capability_document")).get("id")}
    for r in _dicts(data.get("requirements")):
        for origin in sorted(str(o) for o in _ids(r.get("derived_from")) - known):
            err(f"{r.get('id')} is derived from {origin}, which is no countermeasure, TAPP, "
                "protection plan or capability document the run read")
    if "P-17" in scope.active_tasks(ctx.run):
        _solicitations(data, ppp, countermeasures, err)
    return out


def _unraised(entry: Any) -> bool:
    """A protection topic the capability document lacks, with the gap not raised to the sponsor."""
    entry = _dict(entry)
    return entry.get("included") is not True and entry.get("raised_to") != SPONSOR


def _solicitations(data: dict[str, Any], ppp: dict[str, Any], countermeasures: set[Any],
                   err: Check) -> None:
    """The RFPs and contracts as a set: the source asks that they carry the protections, not that
    each one does. An RFP that records a deviation answers the lead systems engineer's should for
    itself, and the RFPs without one are judged."""
    solicitations = _dicts(data.get("solicitations"))
    rfps = [s for s in solicitations if s.get("kind") == "rfp"]
    owed = [s for s in rfps if not s.get("deviation")]
    carried = {c for s in owed for c in _ids(s.get("countermeasures"))}
    if owed and not carried & countermeasures:
        err("no request for proposal carries a PPP countermeasure")
    if owed and not any(s.get("cyber_resilient_requirements") for s in owed):
        err("no request for proposal carries a cyber resilient engineering requirement")
    for s in solicitations:
        for cm in sorted(str(c) for c in _ids(s.get("countermeasures")) - countermeasures):
            err(f"{s.get('id')} carries {cm}, a countermeasure the PPP does not plan")
    contracting = [s for s in solicitations if s.get("kind") in ("rfp", "contract")]
    translated = {a for s in contracting for a in _ids(s.get("assurance_remediation"))}
    missing = _ids(ppp.get("sse_activities")) & set(ASSURANCE) - translated
    if contracting and missing:
        err(f"no RFP or contract translates the {', '.join(sorted(missing))} remediation "
            "strategies of program protection into contract requirements")
    named = {s.get("id") for s in solicitations}
    for r in _dicts(data.get("reassessments")):
        if r.get("mitigations") and not _ids(r.get("incorporated_in")) & named:
            err(f"{r.get('id')}: the technical and process mitigations of the reassessment are "
                "incorporated into no solicitation, contract or agreement")


# --- PPROT-005: security in technical risk management, and ITRAs --------------------------

def technical_risk(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-005", PROT_FILE, "P-14", _ppp_owed(ctx))
    if data is None:
        return out
    program, inputs = _dict(data.get("program")), _dict(data.get("inputs"))
    risks = _dicts(data.get("technical_risks"))
    reviews = set(ctx.run.framework.index("reviews"))
    itras = _dicts(inputs.get("itras"))
    read = {_dict(inputs.get("sep")).get("id")} | {i.get("id") for i in itras} \
        | {a.get("id") for a in _dicts(inputs.get("threat_assessments"))}
    security = [r for r in risks if r.get("security") is True]
    if not security:
        err("no technical risk is a cybersecurity or related system security risk")
    for r in security:
        unread = _ids(r.get("drawn_from")) - read
        if unread:
            err(f"{r.get('id')} is drawn from {', '.join(sorted(map(str, unread)))}, which is no "
                "SEP, ITRA or threat assessment the run read")
        if not _ids(r.get("reviews")) & reviews:
            err(f"{r.get('id')}: a security technical risk is assessed at technical reviews, and "
                "it names none of the framework")
    ids = {r.get("id") for r in risks}
    for itra in itras:
        if not _ids(itra.get("informs")) & ids:
            err(f"the results of {itra.get('id')} inform no technical risk; ITRA results inform "
                "risk management activities")
    acat = program.get("acat")
    for itra in itras:
        if acat == "ID" and itra.get("approved_by") != USD_RE:
            err(f"the USD(R&E) conducts and approves the ITRA of an ACAT ID program, not "
                f"{itra.get('approved_by')}")
        if acat in ("IB", "IC") and itra.get("approved_by") == "component-chain":
            err(f"{itra.get('id')}: the approval authority of an ACAT IB or IC ITRA is independent "
                "of the program's chain of command")
    waiver = _dict(program.get("itra_waiver"))
    if waiver and waiver.get("by") != USD_RE:
        err(f"an ITRA is waived at the discretion of the USD(R&E), not {waiver.get('by')}")
    if acat in MDAP_ACAT and waiver.get("by") != USD_RE:
        assessed = {i.get("decision_point") for i in itras}
        for point in sorted(set(_passed(program)) & set(ITRA_POINTS) - assessed):
            err(f"an ITRA is conducted on an MDAP before {point}, and none is recorded")
    design = _dict(data.get("design_assessment"))
    if design.get("requirements_allocated") is not True:
        err("cybersecurity and related system security requirements are allocated to the system "
            "architecture and design")
    return out


# --- PPROT-006: NSA assessment of a National Security System -------------------------------

def nss_assessment(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "PPROT-006", NSS_FILE, "P-16")
    if data is None:
        return out
    space = _space(ctx)
    if space and data.get("nss") is not True:
        err("a space NSS is a National Security System, and nss-assessments.yaml records nss "
            f"{data.get('nss')}")
    if data.get("nss") is not True and not space:
        return out
    passed = _passed(_dict(_protection(ctx).get("program")))
    milestones = decision_points(ctx, _pathway(ctx), MILESTONES)
    assessments = _dicts(data.get("assessments"))
    for point, date in sorted(passed.items()):
        if point not in milestones:
            continue
        before = [a for a in assessments if a.get("decision_point") == point
                  and (date is None or (_day(a.get("date")) or dt.date.max) <= date)]
        if not before:
            err(f"NSA and the cognizant AO assess the cybersecurity requirements and security "
                f"architecture of a National Security System before {point}, and no assessment "
                "is recorded")
    for a in assessments:
        point, by = a.get("decision_point"), _ids(a.get("assessed_by"))
        if NSA not in by or not by & set(AO_ROLES):
            err(f"the assessment before {point} is made by NSA in coordination with the cognizant "
                f"AO, not {', '.join(sorted(map(str, by)))}")
        left_out = set(NSS_COVERS) - _ids(a.get("covers"))
        if left_out:
            err(f"the assessment before {point} does not cover the "
                f"{', '.join(sorted(left_out))}")
    if not space:
        return out

    def with_both(parties: Any) -> bool:
        named = _ids(parties)
        return NSA in named and bool(named & set(AO_ROLES))

    first = min((d for d in passed.values() if d), default=None)
    if not any(with_both(c.get("with")) and (first is None or (_day(c.get("date"))
                                                                or dt.date.max) <= first)
               for c in _dicts(data.get("architecture_coordination"))):
        err("the space NSS security architecture is coordinated with the cognizant AO and NSA "
            "from program inception")
    for c in _dicts(data.get("preexisting_components")):
        verified, included = _day(c.get("verified")), _day(c.get("included"))
        if not with_both(c.get("verified_with")) or (verified and included and verified > included):
            err(f"{c.get('component')}: a pre-existing component or service is verified with the "
                "cognizant AO and NSA before it is committed to the architecture")
    reports = _dicts(data.get("compliance_reports"))
    if not any(with_both(r.get("to")) for r in reports):
        err("no report of the compliance status of the space NSS reaches the cognizant AO and "
            "NSA")
    return out


# --- GATE-001: an authorization before fielding on a pathway's release gate --------------

AUTHORIZING = ("AD-ATO", "AD-ATOC", "AD-CATO")


def authorization_gates(ctx: Context) -> list[RunFinding]:
    """A pathway's decision point marked authorization_gate fields the system, so an ATO, an ATO
    with conditions or a cATO of the system is dated on or before it. Read only when protection.yaml
    records the decision points the program passed."""
    program = _dict(_protection(ctx).get("program"))
    entity = ctx.run.framework.index("pathways").get(_pathway(ctx) or "")
    gates = {d.get("id") for d in _dicts(entity.data.get("decision_points") if entity else None)
             if d.get("authorization_gate") is True}
    records = [r for r in _dicts(ctx.ledger)
               if r.get("decision") in AUTHORIZING and r.get("subject") == "system"]
    out: list[RunFinding] = []
    for point, date in sorted(_passed(program).items()):
        if point not in gates:
            continue
        if not any(date is None or (_day(r.get("date")) or dt.date.max) <= date for r in records):
            out.append(make("GATE-001", f"the system is fielded at {point}, and no ATO, ATO with "
                            "conditions or cATO of the system precedes it", ledger.LEDGER_FILE,
                            None, {"R-4"}))
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("PPROT-001", ppp_approval), ("PPROT-002", ppp_content),
                ("PPROT-003", st_protection), ("PPROT-004", protection_requirements),
                ("PPROT-005", technical_risk), ("PPROT-006", nss_assessment),
                ("GATE-001", authorization_gates))
