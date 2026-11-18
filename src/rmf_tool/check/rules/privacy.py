"""Privacy rules of a system processing PII: PRIV-001 to PRIV-012, PASM-001 and PASM-002. Each stays
quiet for a system that processes no PII (``Context.processes_pii``), for a task outside the run's
scope, and about a file that is missing or unreadable where another rule reports it (RUN-ART-001,
RUN-FM-001).

Who does what follows the sources. DoDI 5400.16 makes the PIA, on DD Form 2930 (2930A when
adapted), coordinated by the PM through the ISSM, the privacy representative and the records
office, reviewed by the Component senior information security officer and privacy officer, and
approved by the Component CIO or the reviewing official (REQ-DODI5400.16-0056 to -0060). It
excludes NSS from the PIA requirement while asking that privacy implications be considered
(REQ-DODI5400.16-0051); the Privacy Overlay that replaces the PCIL analysis on an NSS
(REQ-CNSSI1253F-ATT6-PRIVACY-0044) can select RA-8, and a selected RA-8 makes the PIA a control
the system implements, so this framework reads the exclusion as void once ra-8 is in the
baseline (ADR-0003, 2026-11-07). SP 800-37r2 Task S-5 assigns each privacy control an
organization-defined frequency in the privacy continuous monitoring strategy and has the senior
agency official for privacy consulted on a privacy control the strategy lacks
(REQ-SP800-37R2-0320); PER-PRIV stands for that official, as in RAR-002 and AODM-010."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope

INFOTYPES = "artifacts/data/infotypes.yaml"
PIA = "artifacts/data/pia.yaml"
CONMON = "artifacts/data/conmon.yaml"
RA = "artifacts/data/ra.yaml"
REQUIREMENTS = "artifacts/data/requirements.yaml"
SSP_RECORDS = "artifacts/data/ssp-records.yaml"
PLAN_REVIEWS = "artifacts/data/plan-reviews.yaml"
CHANGES = "artifacts/data/changes.yaml"
BASELINE = "baseline.json"
SSP_DOC = "artifacts/ART-SSP.md"
PRIVACY = "PER-PRIV"
PII = "processes-pii"
PRIVACY_OVERLAY = "CNSSI1253F-ATT6-PRIVACY"
# DoDI 8500.01 Enclosure 3 i: DoD IT processing PII complies with DoD 5400.11-R and DoDI 5400.16,
# and IT processing PHI with DoD 8580.02-R as well.
PII_ISSUANCES = ("DOD5400.11-R", "DODI5400.16")
PHI_ISSUANCE = "DOD8580.02"
# DoDI 8500.01 Enclosure 3 j, after DoDI 5400.16 1b: whom the PII is about makes the PIA required.
PIA_SUBJECTS = frozenset({"public", "federal-personnel", "contractors",
                          "foreign-nationals-us-facilities-abroad"})
# DoDI 5400.16 1c and 1d: the bases on which no PIA is required, "no-pii" aside.
EXCLUSIONS = frozenset({"nss", "internal-government-operations", "previously-assessed",
                        "unchanged", "feedback-website", "matching-agreement",
                        "statistical-agreement"})
ADAPTED_BASIS = "third-party-website"
FORMS = {"required": "DD-2930", "adapted": "DD-2930A"}
# DoDI 5400.16 Enclosure 3 2b to 2e: the parties a PIA is coordinated through and its reviewers.
COORDINATION = {"issm": "the information system security manager",
                "privacy-representative": "the privacy representative",
                "records-management": "the records management office"}
REVIEWERS = {"PER-CISO": "cybersecurity-policy", PRIVACY: "privacy-policy"}
APPROVERS = {"cio": "PER-CIO"}
PREPARER = "PER-PM"  # E3 2b: the PM or designee completes and coordinates the PIA
OMB_A130 = "OMB-A-130"
FIPPS = "FIPPS"  # DoDI 5400.11 5.2: systems are evaluated against the FIPPs
# Tasks that update the plans with what they learned.
PLAN_TASKS = ("I-2", "A-5", "M-1", "M-4", "M-7")
SAP = "artifacts/data/sap.yaml"
SAR_REPORT = "artifacts/data/sar-report.yaml"
AUTHORIZERS = ("PER-AO", "PER-AODR")  # SP 800-37r2 S-6: the AO or designated representative


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [v for v in _list(value) if isinstance(v, dict)]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _str(value: Any) -> str | None:
    """A value usable as a set member or lookup key; malformed input reads as absent."""
    return value if isinstance(value, str) else None


def _strings(values: Any) -> set[str]:
    """The string members of a list; malformed members read as absent."""
    return {v for v in (values if isinstance(values, list) else ()) if isinstance(v, str)}


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _active(ctx: Context, task: str) -> bool:
    return ctx.processes_pii and task in scope.active_tasks(ctx.run)


def _record(ctx: Context, rel: str) -> dict[str, Any] | None:
    data = ctx.data(rel)
    return data if isinstance(data, dict) else None


def _finding(rule: str, message: str, rel: str, task: str) -> RunFinding:
    return make(rule, message, rel, None, {task})


def _types(ctx: Context) -> list[dict[str, Any]]:
    return [t for t in _dicts(_dict(ctx.data(INFOTYPES)).get("information_types"))
            if t.get("privacy") is True]


def _privacy(ctx: Context) -> dict[str, Any] | None:
    found = _dict(ctx.data(INFOTYPES)).get("privacy")
    return found if isinstance(found, dict) else None


def _determination(ctx: Context) -> str | None:
    return _str(_dict((_privacy(ctx) or {}).get("pia")).get("determination"))


def _baseline_ids(ctx: Context) -> set[str]:
    data = _dict(ctx.data(BASELINE))
    return _strings([c.get("control_id") for c in _dicts(data.get("controls"))])


def _overlays(ctx: Context) -> list[str]:
    categorization = _dict(_dict(ctx.facts).get("categorization"))
    return [o for o in _list(categorization.get("overlays")) if isinstance(o, str)]


# --- PRIV-001: P-12 records the privacy compliance and decides the PIA ------------------------

def determination(ctx: Context) -> list[RunFinding]:
    """PRIV-001: a system processing PII records the issuances it complies with, its SORN,
    SSN justification and records coordination, and whether a PIA is required, adapted or not
    required on a basis DoDI 5400.16 gives."""
    if not _active(ctx, "P-12") or _record(ctx, INFOTYPES) is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("PRIV-001", message, INFOTYPES, "P-12"))

    found = _privacy(ctx)
    if found is None:
        err("the system processes PII and records no privacy compliance or PIA determination")
        return out
    types = _types(ctx)
    details = [_dict(t.get("pii")) for t in types]
    for t, pii in zip(types, details, strict=True):
        if not pii:
            err(f"{t.get('id')} contains PII and does not say whom it is about or whether it "
                "holds PHI or SSNs")
    held = _strings(found.get("compliance"))
    for issuance in PII_ISSUANCES:
        if issuance not in held:
            err(f"DoD IT that processes PII complies with DoD 5400.11-R and DoDI 5400.16, and "
                f"{issuance} is not among the issuances it complies with")
    if any(p.get("phi") is True for p in details) and PHI_ISSUANCE not in held:
        err("DoD IT that processes protected health information complies with DoD 8580.02-R, "
            "and it is not among the issuances it complies with")
    if any(p.get("ssn") is True for p in details) and not isinstance(
            found.get("ssn_justification"), dict):
        err("the system holds SSNs and records no SSN use and justification memorandum")
    sorn = _dict(found.get("sorn"))
    if sorn.get("status") == "not-required" and not sorn.get("reason"):
        err("no SORN is required, and the record does not say why")
    _pia_basis(ctx, found, details, err)
    return out


def _pia_basis(ctx: Context, found: dict[str, Any], details: list[dict[str, Any]],
               err: Any) -> None:
    pia = _dict(found.get("pia"))
    decided, basis = _str(pia.get("determination")), _str(pia.get("basis"))
    subjects = {s for p in details for s in _strings(p.get("subjects"))}
    if decided == "not-required":
        if basis == "no-pii":
            err("the PIA is not required because no PII is collected, yet the system "
                "processes PII")
        elif basis not in EXCLUSIONS and subjects & PIA_SUBJECTS:
            err("a PIA is required for a DoD IS that collects PII about members of the public, "
                "federal personnel, contractors or foreign nationals employed at U.S. military "
                f"facilities internationally, and {basis} is no basis for excluding it")
        if basis == "nss":
            if "ra-8" in _baseline_ids(ctx):
                err("ra-8 is in the baseline, so the PIA is required even though the system is "
                    "an NSS")
            if not any(o.startswith(PRIVACY_OVERLAY) for o in _overlays(ctx)):
                err("the NSS exclusion from the PIA rests on no Privacy Overlay control set in "
                    "the categorization overlays")
            if not pia.get("privacy_implications"):
                err("the NSS is excluded from the PIA requirement, and the record does not say "
                    "how its privacy implications were considered")
    if decided == "adapted" and basis != ADAPTED_BASIS:
        err("an adapted PIA (DD Form 2930A) is for a third-party website or application that "
            f"may make PII available, not {basis}")
    if basis == ADAPTED_BASIS and decided != "adapted":
        err("a third-party website or application that may make PII available takes an "
            f"adapted PIA, not {decided}")
    if decided in FORMS and not pia.get("due"):
        err("the PIA is required, and the record does not say when it is due")


# --- PRIV-002 to PRIV-004: the PIA itself ------------------------------------------------------

def _pia(ctx: Context, task: str) -> tuple[dict[str, Any] | None, bool]:
    """The PIA record and whether the run needs one: PII, P-14 in scope, and a determination
    of required or adapted."""
    if not _active(ctx, task) or _determination(ctx) not in FORMS:
        return None, False
    return _record(ctx, PIA), True


def _unapproved(data: dict[str, Any]) -> bool:
    return data.get("status") in ("draft", "in-review")


def pia_form(ctx: Context) -> list[RunFinding]:
    """PRIV-002: a required or adapted PIA exists, prepared on its DoD form."""
    _, needed = _pia(ctx, "P-14")
    if not needed:
        return []
    decided, pia = _determination(ctx), ctx.data(PIA)
    if not isinstance(pia, dict):
        return [_finding("PRIV-002", f"the PIA is {decided}, and artifacts/data/pia.yaml holds "
                         "no PIA", PIA, "P-14")]
    if pia.get("form") != FORMS[str(decided)]:
        return [_finding("PRIV-002", f"a {decided} PIA is prepared on its DoD form "
                         f"{FORMS[str(decided)]}, not {pia.get('form')}", PIA, "P-14")]
    return []


def pia_approval(ctx: Context) -> list[RunFinding]:
    """PRIV-003: the PIA is coordinated, reviewed and approved by the officials DoDI 5400.16
    names, in that order, and approved before an authorization decision takes it."""
    data, _ = _pia(ctx, "P-14")
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("PRIV-003", message, PIA, "P-14"))

    if _unapproved(data):
        # a draft PIA is coordinated, not yet reviewed or approved (F-02-9); no authorization
        # decision may take it
        for c in _dicts(data.get("coordination")):
            if c.get("party") == "issm" and c.get("by") != "PER-ISSM":
                err(f"the PIA is coordinated through the ISSM, not {c.get('by')}")
        for record in ctx.ledger or ():
            if _str(record.get("decision")) in _authorizing(ctx):
                err(f"the PIA is still {data.get('status')}, so it was not approved for the "
                    f"authorization decision {record.get('id')}")
        return out
    approval = _dict(data.get("approval"))
    approved = _day(approval.get("date"))
    coordination = _dicts(data.get("coordination"))
    parties = _strings([c.get("party") for c in coordination])
    for party, words in COORDINATION.items():
        if party not in parties:
            err(f"the PM does not coordinate the PIA through {words}")
    for c in coordination:
        if c.get("party") == "issm" and c.get("by") != "PER-ISSM":
            err(f"the PIA is coordinated through the ISSM, not {c.get('by')}")
    reviews = _dicts(data.get("reviews"))
    for reviewer, confirms in REVIEWERS.items():
        if not any(reviewer in (r.get("by"), r.get("designee_of")) and r.get("confirms") == confirms
                   for r in reviews):
            err(f"{reviewer} does not review the completed PIA and confirm its compliance with "
                f"{confirms.replace('-', ' ')}")
    role, approver = _str(approval.get("role")), _str(approval.get("by"))
    if role in APPROVERS and approver != APPROVERS[role]:
        err(f"the Component CIO approves the PIA as final review and approval official, not "
            f"{approver}")
    preparers = {PREPARER} | _strings([c.get("by") for c in coordination])
    if approver in preparers:
        err(f"{approver} prepared or coordinated the PIA and cannot also give it final review "
            "and approval")
    for step in [*coordination, *reviews]:
        day = _day(step.get("date"))
        if approved is not None and day is not None and day > approved:
            err(f"a coordination or review of {day} follows the PIA approval of {approved}")
    for record in ctx.ledger or ():
        decided = _day(record.get("date"))
        if _str(record.get("decision")) in _authorizing(ctx) and approved is not None \
                and decided is not None and approved > decided:
            err(f"the PIA approved on {approved} was not in the package for the authorization "
                f"decision {record.get('id')} of {decided}")
    return out


def _authorizing(ctx: Context) -> set[str]:
    return {e.id for e in ctx.run.framework.index("decisions").values()
            if e.data.get("effect") == "authorize"}


def pia_distribution(ctx: Context) -> list[RunFinding]:
    """PRIV-004: after approval the PIA goes to the DoD CIO, and section 1 is published in the
    Component repository, or publication restricted for a stated reason."""
    data, _ = _pia(ctx, "P-14")
    if data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("PRIV-004", message, PIA, "P-14"))

    if _unapproved(data):
        return out  # distribution follows approval
    approved = _day(_dict(data.get("approval")).get("date"))
    submission = data.get("submission")
    if not isinstance(submission, dict):
        err("the approved PIA is not submitted to the DoD CIO")
    else:
        sent = _day(submission.get("date"))
        if approved is not None and sent is not None and sent < approved:
            err(f"the PIA was submitted to the DoD CIO on {sent}, before the PIA approval date "
                f"{approved}")
    publication = data.get("publication")
    if not isinstance(publication, dict):
        err("section 1 of the PIA is neither published in the Component repository nor "
            "restricted")
    elif publication.get("status") == "restricted" and not publication.get("reason"):
        err("publication of the PIA is restricted without the security concern or the "
            "classified or sensitive information that restricts it")
    return out


# --- PRIV-005: M-1 tests each change for new privacy risk -------------------------------------

def change_privacy(ctx: Context) -> list[RunFinding]:
    """PRIV-005: each change to a system processing PII states whether it changes the privacy
    posture, and a change that does leads to a review of the PIA."""
    data = _record(ctx, CHANGES)
    if not ctx.processes_pii or not scope.produced_or_seeded(ctx.run, "ART-CHG") or data is None:
        return []
    out = []
    updates = _strings([u.get("change") for u in _dicts(_dict(ctx.data(PIA)).get("updates"))])
    needs_pia = _determination(ctx) in FORMS
    for change in _dicts(data.get("changes")):
        ident, impact = _str(change.get("id")), change.get("privacy_impact")
        if not isinstance(impact, bool):
            out.append(_finding("PRIV-005", f"{ident} is not tested for new privacy risk: "
                                "privacy_impact is not stated", CHANGES, "M-1"))
        elif impact and needs_pia and ident not in updates:
            out.append(_finding("PRIV-005", f"{ident} changes the privacy posture, and no PIA "
                                "review in artifacts/data/pia.yaml follows it", CHANGES, "M-1"))
        elif impact and _determination(ctx) == "not-required" \
                and ident not in _strings(_dict(_privacy(ctx)).get("redetermined_after")):
            out.append(_finding("PRIV-005", f"{ident} creates new privacy risk on a system with "
                                "no PIA, so the PIA determination is due again at P-12",
                                CHANGES, "M-1"))
    return out


# --- PRIV-006: the privacy continuous monitoring strategy -------------------------------------

def _privacy_controls(ctx: Context) -> set[str]:
    """Baseline controls the NSS privacy control baseline or an applied Privacy Overlay control
    set selects."""
    try:
        tables = baseline_mod.load_tables(ctx.run)
    except baseline_mod.BaselineError:
        return set()
    selected = set()
    for table in _dicts(tables.get("tables")):
        for block in _dicts(table.get("blocks")):
            selected |= {r.get("id") for r in _dicts(block.get("controls"))
                         if r.get("privacy") in tuple(baseline_mod.SELECTED)
                         and not r.get("withdrawn")}
    applied = {o for o in _overlays(ctx) if o.startswith(PRIVACY_OVERLAY)}
    for overlay in _dicts(tables.get("overlays")):
        if _str(overlay.get("id")) in applied:
            selected |= {c for b in _dicts(overlay.get("blocks")) for c in _strings(b.get("add"))}
    return selected & _baseline_ids(ctx)


def privacy_monitoring(ctx: Context) -> list[RunFinding]:
    """PRIV-006: the PCM strategy holds every privacy control of the baseline with an assessment
    frequency, on the guidance of the SAOP, who is consulted on a control it lacked."""
    data = _record(ctx, CONMON)
    if not _active(ctx, "S-5") or data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("PRIV-006", message, CONMON, "S-5"))

    found = data.get("privacy")
    if not isinstance(found, dict):
        err("the system processes PII and has no privacy continuous monitoring strategy")
        return out
    if found.get("guidance_by") != PRIVACY:
        err("the senior agency official for privacy gives guidance on the ongoing monitoring of "
            f"privacy controls, not {found.get('guidance_by')}")
    entries = _dicts(found.get("controls"))
    held = _strings([c.get("control") for c in entries])
    for control in sorted(_privacy_controls(ctx) - held):
        err(f"privacy control {control} has no assessment frequency in the privacy continuous "
            "monitoring strategy")
    for entry in entries:
        if entry.get("origin") != "added":
            continue
        consulted = _dict(entry.get("consultation"))
        if consulted.get("by") != PRIVACY:
            err(f"{entry.get('control')} is added to the PCM strategy without consulting the "
                "senior agency official for privacy")
        elif consulted.get("appropriate") is False:
            err(f"the senior agency official for privacy found {entry.get('control')} not "
                "appropriate for the use case, and the strategy monitors it")
    return out


# --- PRIV-007: the privacy risk assessment's legal basis, carried into ART-REQ -----------------

def legal_basis(ctx: Context) -> list[RunFinding]:
    """PRIV-007: the privacy risk assessment evaluates the legal and policy requirements,
    OMB A-130 among them with what the privacy baseline leaves unmet, and each applicable one,
    and each Privacy Act rule of a system of records, is carried by an ART-REQ requirement."""
    data = _record(ctx, RA)
    if not _active(ctx, "P-14") or data is None:
        return []
    out: list[RunFinding] = []

    def err(message: str, rel: str = RA, task: str = "P-14") -> None:
        out.append(_finding("PRIV-007", message, rel, task))

    found = data.get("privacy")
    if not isinstance(found, dict):
        err("the system processes PII and the risk assessment has no privacy risk assessment")
        return out
    legal = _dicts(found.get("legal_requirements"))
    a130 = next((r for r in legal if r.get("authority") == OMB_A130), None)
    if a130 is None:
        err("the privacy risk assessment does not evaluate the applicability of OMB A-130")
    elif a130.get("applies") is not True:
        err("OMB A-130 applies to a federal information system, and the privacy risk "
            "assessment finds it does not")
    elif not _list(a130.get("beyond_baseline")) and not a130.get("baseline_sufficient"):
        err("the privacy risk assessment does not evaluate which OMB A-130 obligations the "
            "privacy control baseline leaves unmet: beyond_baseline names none and "
            "baseline_sufficient gives no reason")
    if FIPPS not in _strings([r.get("authority") for r in legal]):
        err("the privacy risk assessment does not consider the Fair Information Practice "
            "Principles in evaluating the system")
    reqs = _record(ctx, REQUIREMENTS)
    if reqs is None or "P-15" not in scope.active_tasks(ctx.run):
        return out
    known = _strings([r.get("id") for r in _dicts(reqs.get("requirements"))])
    for item in legal:
        carried = _strings(item.get("requirements"))
        if item.get("applies") is True and not carried & known:
            err(f"the applicable privacy requirement {item.get('authority')} is carried by no "
                "requirement of ART-REQ", REQUIREMENTS, "P-15")
    sorn = _dict(_dict(_privacy(ctx)).get("sorn"))
    if sorn.get("status") in ("published", "pending"):
        rules = {r["rule"]: r for r in _dicts(reqs.get("privacy_act"))
                 if isinstance(r.get("rule"), str)}
        wanted = ["direct-collection", "disclosure-bar", "first-amendment", "access-appeals",
                  "rules-of-conduct"]
        if sorn.get("contractor_operated") is True:
            wanted.append("contract-provisions")
        for rule in wanted:
            entry = rules.get(rule)
            if entry is None:
                err(f"the system keeps a system of records, and ART-REQ does not address the "
                    f"Privacy Act rule {rule}", REQUIREMENTS, "P-15")
            elif entry.get("applies") is True and not _strings(entry.get("requirements")) & known:
                err(f"the Privacy Act rule {rule} applies and is carried by no requirement",
                    REQUIREMENTS, "P-15")
    return out


# --- PRIV-008: the privacy plan, held in ART-SSP ----------------------------------------------

def privacy_plan(ctx: Context) -> list[RunFinding]:
    """PRIV-008: a system processing PII holds its privacy plan in ART-SSP, the one plan
    artifact this framework has, with the privacy requirements and the methods and metrics that
    assess the privacy controls."""
    data = _record(ctx, SSP_RECORDS)
    if not _active(ctx, "S-4") or data is None:
        return []
    out = []
    if not isinstance(data.get("privacy_plan"), dict):
        out.append(_finding("PRIV-008", "the system processes PII and ART-SSP holds no privacy "
                            "plan", SSP_RECORDS, "S-4"))
    return out


# --- PRIV-010: the plans are updated by the tasks that learn something --------------------------

def plan_updates(ctx: Context) -> list[RunFinding]:
    """PRIV-010: once I-2, A-5, M-1, M-4 or M-7 has written ART-SSP, the plan change log holds
    its update, and for a system processing PII that update covers the privacy plan."""
    data = _record(ctx, PLAN_REVIEWS)
    doc = ctx.docs.get(SSP_DOC)
    if data is None or doc is None or "S-4" not in scope.active_tasks(ctx.run):
        return []
    touched = _strings(_dict(doc.data).get("touched_by"))
    changes = _dicts(data.get("changes"))
    out = []
    for task in PLAN_TASKS:
        if task not in touched:
            continue
        mine = [c for c in changes if c.get("task") == task]
        plans = {p for c in mine for p in _strings(c.get("plans"))}
        if not mine:
            out.append(_finding("PRIV-010", f"{task} wrote ART-SSP, and the plan change log "
                                f"records no update of the plans by {task}", PLAN_REVIEWS, task))
        elif ctx.processes_pii and "privacy" not in plans:
            out.append(_finding("PRIV-010", f"the {task} update of the plans leaves out the "
                                "privacy plan of a system processing PII", PLAN_REVIEWS, task))
    return out


# --- PRIV-009: the privacy role takes part where it is primary ----------------------------------

def privacy_role(ctx: Context) -> list[RunFinding]:
    """PRIV-009: a role the RACI makes primary only when the system processes PII takes part,
    shown by an interview, at each task in scope that has written its outputs."""
    if not ctx.processes_pii:
        return []
    out = []
    active = set(scope.active_tasks(ctx.run))
    for task, data in ctx.run.tasks.items():
        raci = _dict(data.get("raci"))
        conditional = {p for p, c in _dict(raci.get("when")).items() if c == PII}
        for persona in sorted(conditional & set(_list(raci.get("R")))):
            if task not in active or not _written(ctx, task):
                continue
            heard = _strings([(i.front or {}).get("persona") for i in ctx.interviews
                          if i.task == task])
            if persona not in heard:
                out.append(make("PRIV-009", f"{persona} is a primary role at {task} for a "
                                f"system processing PII, and gave no {task} interview",
                                None, None, {task}))
    return out


def _written(ctx: Context, task: str) -> bool:
    """Whether the task has written its outputs: each lists it in touched_by."""
    for aid in _list(ctx.run.tasks[task].get("outputs")):
        doc = ctx.docs.get(f"artifacts/{aid}.md")
        if doc is not None and task in _list(_dict(doc.data).get("touched_by")):
            return True
    return False


# --- PRIV-011: the Component privacy program, appended at P-2 -----------------------------------

ORG_CONTEXT = "artifacts/ART-ORG-CONTEXT.md"
PROGRAM_HEADING = re.compile(r"^## Privacy program\s*$", re.M)


def privacy_program(ctx: Context) -> list[RunFinding]:
    """PRIV-011: once P-2 has written ART-ORG-CONTEXT, it describes the Component privacy
    program in its own section, whether or not this system processes PII."""
    doc = ctx.docs.get(ORG_CONTEXT)
    if doc is None or "P-2" not in scope.active_tasks(ctx.run) \
            or "P-2" not in _list(_dict(doc.data).get("touched_by")):
        return []
    heading = PROGRAM_HEADING.search(doc.body or "")
    if not heading:
        return [_finding("PRIV-011", "P-2 wrote ART-ORG-CONTEXT without its Privacy program "
                         "section on the Component privacy and civil liberties program",
                         ORG_CONTEXT, "P-2")]
    return []


# --- PRIV-012: the SAOP approves the privacy plan before the AO -------------------------------

def _touched(ctx: Context, aid: str, task: str) -> bool:
    doc = ctx.docs.get(f"artifacts/{aid}.md")
    return doc is not None and task in _list(_dict(doc.data).get("touched_by"))


def _first_authorization(ctx: Context) -> dt.date | None:
    """The date of the first decision that authorizes the system and that no later record
    supersedes: the authorization these plans feed. The old ATO a reauthorization replaces is
    not that decision."""
    effect = ledger.effects(ctx.run)
    records = ledger.load(ctx.run) or ()
    replaced = {str(r.get("supersedes")) for r in records if r.get("supersedes")}
    dates = [_day(r.get("date")) for r in records
             if effect.get(str(r.get("decision"))) == "authorize"
             and str(r.get("id")) not in replaced]
    return min((d for d in dates if d is not None), default=None)


def saop_approval(ctx: Context) -> list[RunFinding]:
    """PRIV-012: for a system processing PII, once S-6 has written ART-SSP, the AO or AODR has
    approved the plans, and the senior agency official for privacy (PER-PRIV, the role a designee
    acts in) reviewed and approved the privacy plan first: the first such approval precedes the
    AO's or AODR's approval of the plans and the first authorization decision (SP 800-37r2 S-4
    and S-6, DoDI 5400.11 3.1.b.(4), CNSSI 1253 3.2.2.f.7)."""
    data = _record(ctx, SSP_RECORDS)
    if not ctx.processes_pii or data is None or "S-6" not in scope.active_tasks(ctx.run) \
            or not _touched(ctx, "ART-SSP", "S-6"):
        return []
    by_ao = [_day(a.get("date")) for a in _dicts(data.get("approvals"))
             if a.get("system_role") in AUTHORIZERS]
    ao = min((d for d in by_ao if d is not None), default=None)
    if ao is None:
        return [_finding("PRIV-012", "S-6 wrote ART-SSP, and no approval of the security and "
                         "privacy plans by the authorizing official or designated representative "
                         "is on record", SSP_RECORDS, "S-6")]
    plan = _dict(data.get("privacy_plan"))
    approvals = _dicts(plan.get("approvals"))
    if not approvals:
        return [_finding("PRIV-012", "the privacy plan of a system processing PII went to the "
                         "authorizing official without the review and approval of the senior "
                         "agency official for privacy", SSP_RECORDS, "S-6")]
    saop = [a for a in approvals if a.get("by") == PRIVACY]
    if not saop:
        others = ", ".join(sorted(_strings([a.get("by") for a in approvals])))
        return [_finding("PRIV-012", f"the privacy plan is reviewed and approved by {others}, "
                         "not the senior agency official for privacy (PER-PRIV)", SSP_RECORDS,
                         "S-6")]
    first = min((d for d in (_day(a.get("date")) for a in saop) if d is not None), default=None)
    if first is None:
        return []
    out = []
    if first > ao:
        out.append(_finding("PRIV-012", f"the senior agency official for privacy approved the "
                            f"privacy plan on {first}, after the authorizing official's approval "
                            f"of the plans on {ao}", SSP_RECORDS, "S-6"))
    decided = _first_authorization(ctx)
    if decided is not None and first > decided:
        out.append(_finding("PRIV-012", f"the senior agency official for privacy approved the "
                            f"privacy plan on {first}, after the authorization decision of "
                            f"{decided}", SSP_RECORDS, "S-6"))
    return out


# --- PIIF-001: the data flows say they carry PII ------------------------------------------------

BOUNDARY = "artifacts/data/boundary.yaml"


def pii_flows(ctx: Context) -> list[RunFinding]:
    """PIIF-001: for a system processing PII, boundary.yaml data_flow says the flows carry PII
    and names the information types they carry (DoD CIO cATO evaluation criteria 1.0.o: data
    flows include PII), each one ART-INFOTYPES marks as PII."""
    data = _record(ctx, BOUNDARY)
    if data is None or not _active(ctx, "P-11"):
        return []
    flow = _dict(data.get("data_flow"))
    out = []
    if flow.get("carries_pii") is not True:
        out.append(_finding("PIIF-001", "the system processes PII and its data flows do not say "
                            "they carry PII", BOUNDARY, "P-11"))
    pii = {str(i.get("id")) for i in _types(ctx) if i.get("privacy") is True}
    named = _strings(flow.get("pii_types"))
    for tid in sorted(pii - named):
        # P-12 writes the information types after P-11 drew the flows (F-02-3)
        out.append(_finding("PIIF-001", f"the data flows do not name {tid}, an information type "
                            "of PII", BOUNDARY, "P-12"))
    return out


# --- PASM-001: the privacy scope and assessors of the assessment plan ---------------------------

def _privacy_assessment(ctx: Context, rel: str, aid: str, task: str) -> dict[str, Any] | None:
    data = _record(ctx, rel)
    if not _active(ctx, task) or data is None or not _touched(ctx, aid, task):
        return None
    return data


def privacy_assessment_plan(ctx: Context) -> list[RunFinding]:
    """PASM-001: the assessment plan of a system processing PII scopes every privacy control of
    the baseline, and its privacy assessors are on the team and are the senior agency official
    for privacy or an independent assessor (SP 800-37r2 A-1 to A-3); the senior agency official
    for privacy identifies its methodologies and metrics (Appendix D)."""
    data = _privacy_assessment(ctx, SAP, "ART-SAP", "A-2")
    if data is None:
        return []
    privacy = data.get("privacy")
    if not isinstance(privacy, dict):
        return [_finding("PASM-001", "the assessment plan of a system processing PII has no "
                         "privacy assessment scope", SAP, "A-2")]
    team = {str(m.get("persona")): m for m in _dicts(data.get("team"))}
    out = []
    for persona in sorted(_strings(privacy.get("assessors"))):
        member = team.get(persona)
        if member is None:
            out.append(_finding("PASM-001", f"privacy assessor {persona} is not on the "
                                "assessment team of the plan", SAP, "A-2"))
        elif persona != PRIVACY and member.get("independent") is not True:
            out.append(_finding("PASM-001", "privacy controls are assessed by the senior agency "
                                f"official for privacy or an independent assessor, not {persona}",
                                SAP, "A-2"))
    method = _dict(privacy.get("methodology"))
    if method and method.get("identified_by") != PRIVACY:
        out.append(_finding("PASM-001", "the privacy assessment methodologies and metrics are "
                            f"identified by {method.get('identified_by')}, not the senior agency "
                            "official for privacy", SAP, "A-2"))
    scoped = _strings(privacy.get("controls"))
    for control in sorted(_privacy_controls(ctx) - scoped):
        out.append(_finding("PASM-001", f"privacy control {control} of the baseline is outside "
                            "the privacy scope of the assessment plan", SAP, "A-2"))
    return out


# --- PASM-002: the privacy assessment report ----------------------------------------------------

def privacy_assessment_report(ctx: Context) -> list[RunFinding]:
    """PASM-002: the assessment report of a system processing PII documents the privacy control
    assessment, by a privacy assessor of the plan, and the senior agency official for privacy
    provides it to the AO or AODR (SP 800-37r2 A-3, A-4)."""
    data = _privacy_assessment(ctx, SAR_REPORT, "ART-SAR", "A-4")
    if data is None:
        return []
    privacy = data.get("privacy")
    if not isinstance(privacy, dict):
        return [_finding("PASM-002", "the assessment report of a system processing PII has no "
                         "privacy assessment results", SAR_REPORT, "A-4")]
    out = []
    planned = _strings(_dict(_dict(ctx.data(SAP)).get("privacy")).get("assessors"))
    for persona in sorted(_strings(privacy.get("assessed_by")) - planned):
        if not planned:
            break  # PASM-001 reports a plan with no privacy assessors
        out.append(_finding("PASM-002", f"the privacy assessment results are documented by "
                            f"{persona}, not a privacy assessor of the assessment plan",
                            SAR_REPORT, "A-4"))
    provided = _dict(privacy.get("provided"))
    if provided.get("by") != PRIVACY:
        out.append(_finding("PASM-002", "privacy information goes to the authorizing official "
                            "from the senior agency official for privacy, not "
                            f"{provided.get('by')}",
                            SAR_REPORT, "A-4"))
    if provided.get("to") not in AUTHORIZERS:
        out.append(_finding("PASM-002", f"the privacy assessment results are provided to "
                            f"{provided.get('to')}, not the authorizing official or designated "
                            "representative", SAR_REPORT, "A-4"))
    return out
