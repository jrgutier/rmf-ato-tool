"""A CSO-hosted system (CLOUD-*) and where any system is hosted (HOST-001).

A system is CSO-hosted when service-agreements.yaml names the cloud among its environments or a
cloud service provider among its agreements, or P-16's hosting record says cloud. Its
artifacts/data/cloud.yaml then records, at S-4, the offerings and their FedRAMP or DoD
provisional authorization (DoD CIO reciprocity guide 1.1, 4.1; CNSSI 1254 scenario d), the
mission impact level the mission AO sets, the DTM 24-001 Table 1 activity tracking checklist,
the contract clauses, the CSSP's part, external assessments and their events, the reports
performers owe, user activity monitoring and the incident response split. HOST-001 judges the
hosting record P-16 adds to boundary.yaml (DoDI 8500.01 Encl 3).
Rules are quiet until their task is in scope; a run older than 0.2.0 is not held to them.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

CLOUD_FILE = "artifacts/data/cloud.yaml"
AGREEMENTS_FILE = "artifacts/data/service-agreements.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
S4, P16 = "S-4", "P-16"
AO_ROLES = ("PER-AO", "PER-AODR")  # the AODR acts for the AO except the decision itself
MISSION_OWNER = "PER-SPONSOR"
PM = "PER-PM"
CSSP_ROLE = "PER-CSSP"
LEVELS = ("IL2", "IL4", "IL5", "IL6")
# FedRAMP baselines eligible for DoD reciprocity for public data (DoD CIO reciprocity 4.1).
RECIPROCAL_BASELINES = ("moderate", "high")
STIG_GUIDES = ("cc-srg", "srg", "stig")
REVIEW_COVERS = ("data-types", "impact-level", "conditions")
# Mission data and the lowest impact level that accommodates it (DoD CIO reciprocity guide 1.1).
# Classified above SECRET is permitted at no impact level.
DATA_FLOOR = {"cui": "IL4", "mission-operations": "IL4", "cui-above-il4": "IL5",
              "unclassified-nss": "IL5", "classified-secret": "IL6"}
ABOVE_SECRET = "classified-above-secret"

# DTM 24-001 Table 1 (pp. 8-9, read from the page images: the extraction drops the CSSP star,
# L-0076), the same for IaaS, PaaS and SaaS: the key of each activity.
ANY, DOW, CSSP, DCRT = "any", "dow", "cssp", "dcrt"
TABLE_1 = {
    "external-vulnerability-scans": ANY, "web-vulnerability-scans": ANY,
    "dcrt-operations": DCRT, "dcat-operations": ANY, "penetration-testing": ANY,
    "intrusion-assessment": ANY, "awareness-and-training": ANY, "endpoint-security": ANY,
    "apply-security-configurations": ANY, "mitigate-vulnerabilities": ANY,
    "monitor-vulnerability-compliance": ANY, "malware-protection": ANY,
    "asw-boundary": DOW, "asw-application": ANY, "warning-intelligence": DOW,
    "endpoint-visibility": ANY, "correlate-threat-data": CSSP, "malware-notification": CSSP,
    "nsm-boundary": CSSP, "enclave-monitoring": ANY, "uam-detect": ANY, "uam-audit-data": ANY,
    "uam-correlate": DOW, "cpcon-implementation": ANY, "cpcon-notification": CSSP,
    "incident-categorization": CSSP, "incident-reporting": CSSP, "incident-handling": ANY,
    "incident-law-enforcement": CSSP, "incident-counterintelligence": CSSP,
    "incident-analysis": CSSP,
}
IL6_DOW = ("uam-detect",)  # the IL 6 column marks DoW only
IL2_NOT_APPLICABLE = ("asw-boundary", "nsm-boundary")  # BCP: IL2 traffic needs no CAP
DOW_ENTITIES = ("cssp", "dcrt", "dow-entity")
PERFORMERS = (*DOW_ENTITIES, "commercial")
DOW_RETAINS = ("training-requirement", "compliance-oversight", "effectiveness-criteria")
NSS_POLICIES = ("CNSSP 32", "NSD 42", "EO 14028", "NSM-08")
CONTRACT_CLAUSES = ("accreditation-boundary", "licensing", "cssp-incident-notification",
                    "threat-representative-testing", "csp-dco-data",
                    "corrective-action-process", "inspection-access", "report-delivery")
DCO_PARTIES = ("cssp", "authorizing-official")
CSSP_DUTIES = ("correlate-threat-data", "aggregate-csp-information", "dodin-status",
               "incident-handling-support", "community-awareness", "risk-decision-support",
               "malware-notification", "anti-malware-vendor-contact", "detection-processes",
               "cpcon-compliance-monitoring", "incident-analysis", "adequacy-determination")
VISIBILITY = ("endpoint-devices", "audit-logs", "csp-supporting-information", "csp-findings")
EXTERNAL_ACTIVITIES = ("dcrt-operations", "dcat-operations", "penetration-testing",
                       "intrusion-assessment")
RELEASE_DAYS = 30  # DTM 24-001 Att 3, 3.a.(2)(b)4
DCRT_COVERS = ("all-findings", "significant-vulnerabilities", "exploited-vulnerability-analysis")
OWNER_CSSP = ("mission-owner", "cssp")
CONSTRAINTS = ("safety", "real-world-mission-execution", "operational-security")
# What a performer of each activity owes, and to whom (DTM 24-001 Att 3, 3.a to 3.c).
DELIVERABLES: dict[str, dict[str, tuple[str, ...]]] = {
    "external-vulnerability-scans": {"scan-notification": OWNER_CSSP,
                                     "scan-executive-summary": OWNER_CSSP,
                                     "situational-awareness": (*OWNER_CSSP,
                                                               "authorizing-official")},
    "web-vulnerability-scans": {"scan-executive-summary": OWNER_CSSP,
                                "situational-awareness": OWNER_CSSP},
    "endpoint-security": {"endpoint-alerts": ("authorizing-official", "cssp")},
    "mitigate-vulnerabilities": {"correlation-analysis": OWNER_CSSP},
    "monitor-vulnerability-compliance": {"compliance-statistics": ("mission-owner",)},
    "malware-protection": {"malware-procedures": ("mission-owner",),
                           "malware-incident-report": ("mission-owner",),
                           "malware-trend-report": ("mission-owner", "authorizing-official"),
                           "corrective-action-report": OWNER_CSSP},
    "asw-application": {"violation-report": ("mission-owner",),
                        "action-report": OWNER_CSSP},
    "endpoint-visibility": {"control-state-change": OWNER_CSSP, "threat-report": OWNER_CSSP},
    "enclave-monitoring": {"anomalous-event-report": OWNER_CSSP, "action-report": OWNER_CSSP},
}
ANNUAL = ("malware-trend-report",)
EITHER = (("endpoint-security", "endpoint-alerts"),)  # to the AO or the CSSP
UAM_ACTIVITIES = ("uam-detect", "uam-audit-data")
UAM_PROCEDURES = ("uam-procedures", "anomalous-activity-response", "chain-of-custody",
                  "audit-data-preservation")
UAM_PARTNERS = ("component-insider-threat-program", "law-enforcement", "counterintelligence")
# Who may hold each shared incident response duty (DTM 24-001 Att 3, 3.d).
IR_DUTIES = {
    "support-cssp-incident-handling": ("mission-owner",),
    "report-events-and-incidents": ("mission-owner",),
    "provide-incident-artifacts": ("mission-owner",),
    "safeguard-incident-information": ("mission-owner",),
    "report-csp-findings": ("csp",),
    "damage-assessment": ("incident-handler",),
    "post-incident-feedback": ("incident-handler",),
    "countermeasures": ("incident-handler",),
    "corrective-actions": ("incident-handler",),
    "deliver-ir-artifacts": ("mission-owner",),
    "operational-impact": ("mission-owner",),
    "passive-countermeasures": ("mission-owner",),
    "retain-incident-artifacts": ("mission-owner",),
    "make-data-available": ("csp",),
}
CPT_TO = "cssp"
# DoDI 8500.01 Encl 3: a new major application is hosted in a DECC when operationally feasible.
MAJOR_APPLICATION = "major-application"
NEW_STATES = ("under-development",)
DEVELOPED_STATES = ("under-development", "under-major-modification")
DECC = "decc"
CLOUD_ASSESSMENTS = ("cloud-hosted", "can-be-cloud-hosted", "cannot-be-cloud-hosted")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


def _text(value: Any) -> str | None:
    """A scalar key as read, or None when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, str) else None


def _strings(items: Any) -> list[str]:
    return [str(i) for i in items] if isinstance(items, list) else []


def _day(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def _rank(level: Any) -> int:
    return LEVELS.index(level) if level in LEVELS else -1


def _cloud_hosted(ctx: Context) -> bool:
    """What service-agreements.yaml and the P-16 hosting record say, so leaving cloud.yaml out is
    no way around a rule: the agreements, the hosting environment and the cloud assessment."""
    data = _mapping(ctx.data(AGREEMENTS_FILE))
    roles = [a.get("role") for a in _dicts(data.get("agreements"))]
    hosting = _mapping(_mapping(ctx.data(BOUNDARY_FILE)).get("hosting"))
    hosted = hosting.get("environment")
    assessed = _mapping(hosting.get("cloud")).get("assessment")
    return "cloud" in _strings(data.get("system_environments")) \
        or "cloud-service-provider" in roles or hosted == "cloud" or assessed == "cloud-hosted"


def _record(ctx: Context, rule: str, section: str | None = None
            ) -> tuple[dict[str, Any] | None, list[RunFinding], Callable[[str], None]]:
    """The cloud record of a CSO-hosted system at S-4, or None when the rule is not in play. A
    missing required section returns None too: the schema requires it, so RUN-FM-001 reports it."""
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, CLOUD_FILE, None, {S4}))

    if S4 not in scope.active_tasks(ctx.run) or not _cloud_hosted(ctx):
        return None, out, err
    data = ctx.data(CLOUD_FILE)
    if not isinstance(data, dict):
        if rule == "CLOUD-001":
            err("the system is hosted in the cloud and artifacts/data/cloud.yaml is missing")
        return None, out, err
    if section is not None and not isinstance(data.get(section), dict):
        return None, out, err
    return data, out, err


def _offerings(data: dict[str, Any]) -> list[dict[str, Any]]:
    return _dicts(data.get("offerings"))


def _rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    return _dicts(_mapping(data.get("checklist")).get("activities"))


def _entity(row: dict[str, Any]) -> Any:
    return _mapping(row.get("performer")).get("entity")


# --- CLOUD-001: the offerings and their authorizations -------------------------------------

def offerings(ctx: Context) -> list[RunFinding]:
    """CLOUD-001: each offering leverages a FedRAMP or DoD provisional authorization fit for the
    mission's impact level, reviewed and inherited as the reciprocity guide says."""
    data, out, err = _record(ctx, "CLOUD-001")
    if data is None:
        return out
    leveraged = {_text(la.get("id")): la for la in _dicts(_mapping(
        ctx.data(LEVERAGED_FILE)).get("leveraged_authorizations"))}
    mission = _mapping(data.get("mission_impact_level")).get("level")
    owner = MISSION_OWNER
    for o in _offerings(data):
        oid = o.get("id")
        auth = _mapping(o.get("authorization"))
        basis, level = auth.get("basis"), auth.get("impact_level")
        la = leveraged.get(_text(o.get("leveraged_authorization")))
        if la is None:
            err(f"{oid}: leverages no authorization in leveraged-authorizations.yaml, so the "
                "existing authorization and its documentation are not reused")
        elif la.get("arrangement") != "external-service":
            err(f"{oid}: {la.get('id')} is not an IT service authorized by another "
                f"organization (arrangement {la.get('arrangement')})")
        elif la.get("decision") != "AD-ATO":
            err(f"{oid}: a FedRAMP or DoD provisional authorization is considered a valid "
                f"authorization to operate; {la.get('id')} records {la.get('decision')}")
        if _rank(level) < _rank(mission):
            err(f"{oid}: authorized at {level}, below the impact level {mission} of the mission "
                "data it processes or stores")
        if basis == "fedramp" and auth.get("fedramp_baseline") not in RECIPROCAL_BASELINES:
            err(f"{oid}: a FedRAMP authorization at the {auth.get('fedramp_baseline')} baseline "
                "is not eligible for use under reciprocity; it needs the moderate baseline")
        request = _mapping(auth.get("package_access_request"))
        if basis == "fedramp" and request.get("submitted_by") != owner:
            err(f"{oid}: the FedRAMP Package Access Request for the body of evidence is "
                f"submitted by the mission owner, not {request.get('submitted_by')}")
        if basis == "fedramp" and _rank(mission) > _rank("IL2"):
            err(f"{oid}: data categorized at {mission} is hosted under a DoD provisional "
                "authorization, not a FedRAMP authorization")
        if basis == "dod-pa" and auth.get("package_location") != "emass":
            err(f"{oid}: the package and inheritance of a DoD provisional authorization are "
                f"leveraged from eMASS, not {auth.get('package_location')}")
        uplift = _mapping(auth.get("uplift_request"))
        if basis == "dod-pa" and auth.get("path") == "uplift" and (
                uplift.get("requested_by") != MISSION_OWNER or uplift.get("via") != "dcas"):
            err(f"{oid}: uplifting an IL2 offering to IL4/5 needs a DoD Sponsor's request to "
                "DISA through the DoD Cloud Authorization Services")
        documents = _strings(_mapping(o.get("inheritance")).get("documents"))
        if mission in ("IL4", "IL5") and not {"ssp", "srtm"} <= set(documents):
            err(f"{oid}: at {mission} the mission owner uses the CSO's SSP and SRTM to "
                f"understand control implementation guidance, not {', '.join(documents)}")
        guides = _strings(o.get("configuration_guidance"))
        if not set(STIG_GUIDES) & set(guides):
            err(f"{oid}: CSP systems comply with configuration guidance by using STIGs or "
                f"SRGs, not {', '.join(guides)}")
        review = _mapping(o.get("package_review"))
        missed = [c for c in REVIEW_COVERS if c not in _strings(review.get("covers"))]
        if missed:
            err(f"{oid}: the mission owner has not come to understand {', '.join(missed)}: "
                "the type of data, the authorized impact level and the conditions of the "
                "provisional authorization")
        reviewers = _strings(review.get("reviewed_by"))
        if owner not in reviewers or not set(AO_ROLES) & set(reviewers):
            err(f"{oid}: the provisional authorization artifacts are reviewed by the mission "
                f"owner and the authorizing official, not {', '.join(reviewers)}")
        if PM not in reviewers or review.get("accepted_by") not in AO_ROLES:
            err(f"{oid}: the selected CSP cybersecurity services are reviewed by the PM and "
                "accepted by the authorizing official")
        for m in _dicts(o.get("additional_measures")):
            if m.get("in_contract") is not True:
                err(f"{oid}: the additional security measure {m.get('measure')} is not "
                    "documented in the contract agreement with the IT service provider")
            if m.get("assessed") is not True or m.get("approved_by") not in AO_ROLES:
                err(f"{oid}: the newly included security-related information on "
                    f"{m.get('measure')} is not assessed and approved")
    return out


# --- CLOUD-002: the mission impact level ---------------------------------------------------

def impact_level(ctx: Context) -> list[RunFinding]:
    """CLOUD-002: the mission AO sets the impact level, and it accommodates the mission data."""
    data, out, err = _record(ctx, "CLOUD-002", "mission_impact_level")
    if data is None:
        return out
    mission = data["mission_impact_level"]
    level = mission.get("level")
    if mission.get("determined_by") not in AO_ROLES:
        err("the impact level for the mission and mission data is the responsibility of the "
            f"mission AO, not {mission.get('determined_by')}")
    kinds = _strings(mission.get("data"))
    if level == "IL2" and mission.get("disclosure_effect") == "serious":
        err("IL2 accommodates data whose unauthorized disclosure could be expected to have a "
            "limited adverse effect, not a serious one")
    for kind in kinds:
        floor = DATA_FLOOR.get(kind)
        if floor is None or _rank(level) >= _rank(floor):
            continue
        if kind == "cui":
            err(f"IL2 accommodates no Controlled Unclassified Information; {level} is too low")
        elif kind == "mission-operations":
            err("IL2 accommodates no military or contingency operations mission data")
        elif kind == "cui-above-il4":
            err("CUI the information owner deems to need more protection than Impact Level 4 "
                f"is hosted at Impact Level 5, not {level}")
        elif kind == "unclassified-nss":
            err("nonpublic, unclassified National Security Systems data is hosted at Impact "
                f"Level 5 or above, not {level}")
        else:
            err(f"classified National Security Information is hosted at Impact Level 6, not "
                f"{level}")
    if ABOVE_SECRET in kinds:
        err("only information classified as SECRET or below is permitted to be hosted at "
            "Impact Level 6")
    return out


# --- CLOUD-003: the cybersecurity activity tracking checklist --------------------------------

def _key(activity: str, level: Any) -> str:
    """The Table 1 key in the column of the mission impact level: the mission's data picks the
    column, so an IL6 offering carrying IL4 data is judged at IL 4/5."""
    if level == "IL6" and activity in IL6_DOW:
        return DOW
    return TABLE_1[activity]


def checklist(ctx: Context) -> list[RunFinding]:
    """CLOUD-003: every Table 1 activity of every offering has a performer the key allows, or a
    gap the authorizing official accepts."""
    data, out, err = _record(ctx, "CLOUD-003", "checklist")
    if data is None:
        return out
    sheet = data["checklist"]
    owner = MISSION_OWNER
    level = _mapping(data.get("mission_impact_level")).get("level")
    generated = _strings(sheet.get("generated_by"))
    if owner not in generated or PM not in generated:
        err(f"the activity tracking checklist is generated by the mission owner and PM, not "
            f"{', '.join(generated)}")
    partners = _strings(sheet.get("coordinated_with"))
    if CSSP_ROLE not in partners or not set(AO_ROLES) & set(partners):
        err("the activity tracking checklist is not developed in coordination with the CSSP and "
            "the authorizing official")
    if sheet.get("validated_by") not in AO_ROLES:
        err("who will be responsible for providing each cybersecurity activity is validated by "
            f"the authorizing official, not {sheet.get('validated_by')}")
    rows = _rows(data)
    for o in _offerings(data):
        listed = {_text(r.get("activity")) for r in rows if r.get("offering") == o.get("id")}
        for activity in TABLE_1:
            if activity not in listed:
                err(f"{o.get('id')}: the mission owner does not address the Table 1 activity "
                    f"{activity}")
    for r in rows:
        activity, entity = _text(r.get("activity")), _entity(r)
        where = f"{activity} on {r.get('offering')}"
        if activity not in TABLE_1:
            continue
        key = _key(activity, level)
        if entity == "none":
            if _mapping(r.get("gap")).get("accepted_by") not in AO_ROLES:
                err(f"{where} has no provider, and the authorizing official does not accept "
                    "the risk of the gap")
            continue
        if entity == "not-applicable":
            if not (level == "IL2" and activity in IL2_NOT_APPLICABLE):
                err(f"{where} is applicable at {level}; only boundary cyberspace protection is "
                    "not applicable, at IL2")
            continue
        if key == CSSP and entity != "cssp":
            err(f"{where}: a CSSP must perform this cybersecurity activity, not {entity}")
        elif key == DCRT and entity != "dcrt":
            err(f"{where}: a DoD certified and accredited DCRT must perform such operations, "
                f"not {entity}")
        elif key == DOW and entity not in DOW_ENTITIES:
            err(f"{where}: a DoW entity must perform this cybersecurity activity; a commercial "
                "entity cannot")
        if activity == "awareness-and-training" and entity == "commercial":
            kept = _strings(r.get("dow_retains"))
            missed = [k for k in DOW_RETAINS if k not in kept]
            if missed:
                err(f"{where}: outsourced training leaves DoW without {', '.join(missed)}")
        if activity == "endpoint-security" and r.get("approved_by") not in AO_ROLES:
            err(f"{where}: endpoint configurations and compliance policies are distributed with "
                "the authorizing official's approval")
    return out


# --- CLOUD-004: the CSO contract -----------------------------------------------------------

def contracts(ctx: Context) -> list[RunFinding]:
    """CLOUD-004: each CSO contract carries the cybersecurity clauses DTM 24-001 lists."""
    data, out, err = _record(ctx, "CLOUD-004")
    if data is None:
        return out
    for o in _offerings(data):
        contract = _mapping(o.get("contract"))
        clauses = _strings(contract.get("clauses"))
        missed = [c for c in CONTRACT_CLAUSES if c not in clauses]
        if missed:
            err(f"{o.get('id')}: the CSO contract does not include {', '.join(missed)}")
        if contract.get("dfars_239_76") is not True:
            err(f"{o.get('id')}: the cloud services contract does not follow DFARS Subpart "
                "239.76")
        shared = _strings(contract.get("dco_data_shared_with"))
        if not set(DCO_PARTIES) <= set(shared):
            err(f"{o.get('id')}: the CSP does not share data for CSSP DCO with the designated "
                "CSSP and the authorizing official")
    return out


# --- CLOUD-005: the CSSP's part --------------------------------------------------------------

def cssp_part(ctx: Context) -> list[RunFinding]:
    """CLOUD-005: the CSSP agreement covers the cloud, the CSSP holds its duties for the CSO,
    and the mission owner gives it visibility."""
    data, out, err = _record(ctx, "CLOUD-005", "cssp")
    if data is None:
        return out
    part = data["cssp"]
    agreements = {_text(a.get("id")): a for a in _dicts(_mapping(
        ctx.data(AGREEMENTS_FILE)).get("agreements"))}
    agreement = _mapping(agreements.get(_text(part.get("agreement"))))
    if agreement.get("role") != "cssp" or "cloud" not in _strings(agreement.get("environments")):
        err(f"{part.get('agreement')} is no CSSP agreement covering the cloud environment")
    missed = [d for d in CSSP_DUTIES if d not in _strings(part.get("duties"))]
    if missed:
        err(f"the CSSP does not hold {', '.join(missed)} for the CSO")
    unseen = [v for v in VISIBILITY if v not in _strings(part.get("visibility"))]
    if unseen:
        err(f"the mission owner does not give the CSSP visibility into {', '.join(unseen)}")
    return out


# --- CLOUD-006: shared incident response ---------------------------------------------------

def incident_response(ctx: Context) -> list[RunFinding]:
    """CLOUD-006: the CSSP is the cybersecurity POC and each shared duty has its holder."""
    data, out, err = _record(ctx, "CLOUD-006", "incident_response")
    if data is None:
        return out
    split = data["incident_response"]
    if split.get("cssp_poc") != _mapping(data.get("cssp")).get("agreement"):
        err("the CSSP is not specified as the cybersecurity POC in all documentation and "
            "coordination with the CSP")
    if split.get("cpt_reports_to") != CPT_TO:
        err("the assigned cyber protection team does not report to the CSSP")
    held = {}
    for r in _dicts(split.get("responsibilities")):
        held.setdefault(_text(r.get("duty")), []).append(r.get("party"))
    for duty, parties in IR_DUTIES.items():
        holders = held.get(duty, [])
        if not set(parties) & set(holders):
            err(f"the incident response duty {duty} is held by {', '.join(map(str, holders))}, "
                f"not {', '.join(parties)}")
    return out


# --- CLOUD-007: external assessments -------------------------------------------------------

def external_assessments(ctx: Context) -> list[RunFinding]:
    """CLOUD-007: the mission owner's external assessment process and the DCRT reports."""
    data, out, err = _record(ctx, "CLOUD-007")
    if data is None:
        return out
    performed = {_text(r.get("activity")) for r in _rows(data) if _entity(r) in PERFORMERS}
    found = data.get("external_assessments")
    if not isinstance(found, dict):
        if performed & set(EXTERNAL_ACTIVITIES):
            err("external assessments are performed and the record holds no process to request "
                "and allow them")
        return out
    partners = _strings(found.get("identified_with"))
    if PM not in partners or not set(AO_ROLES) & set(partners):
        err("the need, type and sources of external assessments are identified in coordination "
            "with the PM and authorizing official")
    shared = _strings(found.get("results_shared_with"))
    if not {"mission-owner", "authorizing-official", "cssp"} <= set(shared):
        err("external assessment results are shared with the mission owner, the DoW Component "
            "authorizing official and the CSSP")
    for report in _dicts(found.get("dcrt_reports")):
        briefed = _day(report.get("briefed"))
        released = _day(report.get("released_to_jfhq_dodin"))
        if briefed is not None and released is not None \
                and (released - briefed).days > RELEASE_DAYS:
            err(f"{report.get('id')}: the DCRT report is released to JFHQ-DODIN within 30 "
                "calendar days of the briefing")
        missed = [c for c in DCRT_COVERS if c not in _strings(report.get("covers"))]
        if missed:
            err(f"{report.get('id')}: the DCRT report does not include {', '.join(missed)}")
    return out


# --- CLOUD-008: DCAT, penetration test and intrusion assessment events -------------------------

def events(ctx: Context) -> list[RunFinding]:
    """CLOUD-008: each event's description, written approval, constraints, mission details,
    results and lessons learned."""
    data, out, err = _record(ctx, "CLOUD-008")
    if data is None:
        return out
    owner = MISSION_OWNER
    for e in _dicts(data.get("events")):
        eid, kind, performer = e.get("id"), e.get("kind"), e.get("performer")
        described = _mapping(e.get("description"))
        if described.get("architecture_diagrams") is not True or not set(OWNER_CSSP) <= set(
                _strings(described.get("delivered_to"))):
            err(f"{eid}: a detailed description with architectural diagrams is delivered to "
                "the mission owner and the CSSP")
        if kind == "intrusion-assessment" and "authorizing-official" not in _strings(
                described.get("delivered_to")):
            err(f"{eid}: a detailed description of support is sent to the authorizing official "
                "to facilitate the intrusion assessment")
        approval = _mapping(e.get("approval"))
        approved, held = _day(approval.get("date")), _day(e.get("date"))
        if approval.get("by") != owner or approval.get("written") is not True or (
                approved is not None and held is not None and approved > held):
            err(f"{eid}: the mission owner's written approval precedes the {kind}")
        missed = [c for c in CONSTRAINTS if c not in _strings(e.get("constraints_basis"))]
        if missed:
            err(f"{eid}: the constraints are not based on {', '.join(missed)}")
        details = _mapping(e.get("mission_details"))
        expected = "performer" if performer == "dow-entity" else "mission-owner"
        if kind != "intrusion-assessment" and details.get("submitted_by") != expected:
            err(f"{eid}: mission details from a {performer} reach JFHQ-DODIN through the "
                f"{expected}")
        sent = _day(details.get("date"))
        if kind != "intrusion-assessment" and held is not None and (sent is None
                                                                   or sent > held):
            err(f"{eid}: mission details are provided to JFHQ-DODIN before mission execution")
        results = _mapping(e.get("results"))
        wanted = (*OWNER_CSSP, "jfhq-dodin") if kind == "dcat" else OWNER_CSSP
        if not set(wanted) <= set(_strings(results.get("delivered_to"))) \
                or results.get("remediation_recommendations") is not True:
            err(f"{eid}: results with remediation recommendations go to "
                f"{', '.join(wanted)}")
        if kind == "penetration-test" and not set(OWNER_CSSP) <= set(
                _strings(e.get("lessons_learned_to"))):
            err(f"{eid}: lessons learned are disseminated to the mission owner and the CSSP")
        if performer == "commercial" and kind != "dcat" \
                and e.get("fedramp_demonstrated") is not True:
            err(f"{eid}: a commercial entity demonstrates during its FedRAMP authorization that "
                "it can perform this within DoW standards")
    return out


# --- CLOUD-009: what performers owe ----------------------------------------------------------

def deliverables(ctx: Context) -> list[RunFinding]:
    """CLOUD-009: a performer of a Table 1 activity, CSSP or other DoW or commercial entity, owes
    its reports to their recipients."""
    data, out, err = _record(ctx, "CLOUD-009")
    if data is None:
        return out
    owed = {(_text(d.get("activity")), _text(d.get("kind"))): d
            for d in _dicts(data.get("deliverables"))}
    # A CSSP is a DoW entity, so it owes what any DoW or commercial performer owes.
    performed = {_text(r.get("activity")) for r in _rows(data) if _entity(r) in PERFORMERS}
    for activity in sorted(a for a in performed & set(DELIVERABLES) if a):
        for kind, recipients in DELIVERABLES[activity].items():
            found = owed.get((activity, kind))
            if found is None:
                err(f"the performer of {activity} owes a {kind} and the record holds none")
                continue
            got = _strings(found.get("recipients"))
            if (activity, kind) in EITHER:
                short = [] if set(recipients) & set(got) else [" or ".join(recipients)]
            else:
                short = [r for r in recipients if r not in got]
            if short:
                err(f"the {kind} of {activity} does not reach {', '.join(short)}")
            if kind in ANNUAL and found.get("cadence") != "annually":
                err(f"the {kind} of {activity} is provided annually, not "
                    f"{found.get('cadence')}")
    return out


# --- CLOUD-010: user activity monitoring ---------------------------------------------------

def user_activity_monitoring(ctx: Context) -> list[RunFinding]:
    """CLOUD-010: outsourced UAM follows a legal review and the AO's risk decision; procedures,
    chain of custody and the DoW entity's correlation are recorded."""
    data, out, err = _record(ctx, "CLOUD-010")
    if data is None:
        return out
    rows = _rows(data)
    outsourced = any(_entity(r) == "commercial" for r in rows
                     if r.get("activity") in UAM_ACTIVITIES)
    uam = data.get("uam")
    if not isinstance(uam, dict):
        if any(_entity(r) in PERFORMERS for r in rows if r.get("activity") in UAM_ACTIVITIES):
            err("user activity monitoring is performed and the record holds no UAM procedures")
        return out
    if outsourced:
        review, decision = _mapping(uam.get("legal_review")), _mapping(uam.get("ao_decision"))
        reviewed, decided = _day(review.get("date")), _day(decision.get("date"))
        if decision.get("by") not in AO_ROLES or reviewed is None or decided is None \
                or reviewed > decided:
            err("before UAM is outsourced, the authorizing official ensures the DoW Component "
                "legal advisor reviews the provider's ability to legally perform UAM")
    missed = [p for p in UAM_PROCEDURES if p not in _strings(uam.get("procedures"))]
    if missed:
        err(f"the UAM procedures shared with the mission owner leave out {', '.join(missed)}")
    if not set(OWNER_CSSP) <= set(_strings(uam.get("data_shared_with"))):
        err("collected UAM data is not shared with the mission owner and the CSSP")
    correlation = _mapping(uam.get("correlation"))
    partners = [p for p in UAM_PARTNERS
                if p not in _strings(correlation.get("coordinates_with"))]
    if partners:
        err(f"the DoW entity correlating insider threat audit data does not coordinate with "
            f"{', '.join(partners)}")
    if correlation.get("analysts_trained") is not True:
        err("analysts are not trained to coordinate with insider threat and law enforcement")
    return out


# --- HOST-001: where the system is hosted ---------------------------------------------------

def hosting(ctx: Context) -> list[RunFinding]:
    """HOST-001: P-16 records where the system is hosted and why."""
    if P16 not in scope.active_tasks(ctx.run):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("HOST-001", message, BOUNDARY_FILE, None, {P16}))

    found = _mapping(ctx.data(BOUNDARY_FILE)).get("hosting")
    if not isinstance(found, dict):
        err("boundary.yaml records no hosting: where the system is hosted and why")
        return out
    kind = facts_mod.value(ctx.facts, "system_type")
    state = facts_mod.value(ctx.facts, "lifecycle_state")
    environment = found.get("environment")
    decc = _mapping(found.get("decc")).get("status")
    designation = _mapping(found.get("enclave_application")).get("status")
    # Encl 3.b holds a new major application to a DECC; an existing authorized enclave (Encl 3.d)
    # meets it too, and DoDI 5000.82 3.7.b puts the cloud first, recorded as decc: cloud.
    if kind == MAJOR_APPLICATION and state in NEW_STATES \
            and environment not in (DECC, "existing-enclave") and decc != "infeasible" \
            and (decc != "cloud" or environment != "cloud"):
        err("a new major application is hosted in a Defense Enterprise Computing Center when "
            "operationally feasible")
    # Encl 3.d is a choice made while the capability is developed or modified, not a judgment of
    # where an operational system now runs.
    if kind == MAJOR_APPLICATION and state in DEVELOPED_STATES and designation != "not-possible":
        err("a capability that can be developed as an application hosted in an existing "
            "authorized enclave is designated a major application requiring a new and separate "
            "authorization")
    if environment == DECC and decc != "hosted":
        err("the system is hosted in a Defense Enterprise Computing Center and decc says "
            f"{decc}")
    cloud = _mapping(found.get("cloud")).get("assessment")
    if state in DEVELOPED_STATES and cloud not in CLOUD_ASSESSMENTS:
        err("no new system or application is approved for development or modernization without "
            "an assessment that it is, or can and would be, cloud-hosted")
    if environment == "cloud" and cloud != "cloud-hosted":
        err(f"the system is hosted in the cloud and its cloud assessment says {cloud}")
    environments = _strings(_mapping(ctx.data(AGREEMENTS_FILE)).get("system_environments"))
    if cloud == "cloud-hosted" and "cloud" not in environments:
        err("the cloud assessment says the system is cloud-hosted and service-agreements.yaml "
            "does not name the cloud among its environments")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CLOUD-001", offerings), ("CLOUD-002", impact_level),
                ("CLOUD-003", checklist), ("CLOUD-004", contracts),
                ("CLOUD-005", cssp_part), ("CLOUD-006", incident_response),
                ("CLOUD-007", external_assessments), ("CLOUD-008", events),
                ("CLOUD-009", deliverables), ("CLOUD-010", user_activity_monitoring),
                ("HOST-001", hosting))
