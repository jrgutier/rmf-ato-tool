"""Organizational risk context rules (OCTX-*): what artifacts/data/org-context.yaml records for
ART-ORG-CONTEXT beyond its Markdown. P-1 writes the role assignments and each later Prepare task
adds its section, so a section is demanded only once its task is in scope, and its finding is
charged to that task. Every rule is quiet until ART-ORG-CONTEXT is produced or seeded, and a run
older than framework_version 0.2.0 is not held to them (``since``).

The rules that read the record from later tasks (A-3, S-5, M-6) judge only what the record
holds: an organization that has not written a section is not judged on it there."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SAR_DIR, SSP_DIR, family_records
from rmf_tool.run import authorization as ledger
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

ORG_FILE = "artifacts/data/org-context.yaml"
CONMON_FILE = "artifacts/data/conmon.yaml"
SAR_REPORT_FILE = "artifacts/data/sar-report.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
ARTIFACT = "ART-ORG-CONTEXT"
# The task whose section each key is, in the order the tasks write them.
SECTIONS = {
    "roles": "P-1", "manpower_structure": "P-1", "open_functions": "P-1", "code_signing": "P-1",
    "program": "P-2", "policies": "P-2", "resources": "P-2", "risk_frame": "P-2",
    "governance": "P-2", "risk_assessment_guidance": "P-2", "risk_response": "P-2",
    "external_entities": "P-2", "common_controls": "P-5", "iscm": "P-7",
}
POSTURE_TASK = "P-3"
OPERATIONS_TASKS = ("M-1", "M-2", "M-3", "M-4", "M-5", "M-6")
# SP 800-37r2 Appendix D: the roles that are an inherent U.S. Government function.
INHERENTLY_GOVERNMENTAL = {
    "PER-AO": "the authorizing official", "PER-CIO": "the chief information officer",
    "PER-RE": "the risk executive (function)",
    "saorm": "the senior accountable official for risk management",
    "PER-CISO": "the senior agency information security officer",
    "PER-PRIV": "the senior agency official for privacy",
}
# DoDI 8510.01 Table 8 (the DoD MA owner appoints the PAO) with DoDI 8500.01 Encl 2, which names
# each mission area's owner.
PAO_APPOINTERS = {"eiema": "dod-cio", "dima": "usd-i", "bma": "dod-cmo", "wma": "cjcs"}
GOVERNMENT = ("dod-civilian", "military", "other-government")
DOD = ("dod-civilian", "military")
# DoDI 8500.01 Encl 3.e: positions a non-U.S. citizen may not hold.
CITIZEN_ONLY_ROLES = ("PER-ISSM", "PER-ISSO", "supervisory-cybersecurity",
                      "pki-registration-authority")
SUPERVISED_POSITIONS = ("system-administrator", "maintainer")
# What makes an appointee one whose function the organization must have identified as open
# (DoDI 8500.01 Encl 3.d). Citizenship is one axis; the affiliations are exclusive, so a
# contractor is counted as a contractor, not also as non-DoD personnel.
OPEN_TO = {"non-us-citizen": lambda r: r.get("citizenship") == "non-us",
           "contractor": lambda r: r.get("affiliation") == "contractor",
           "non-us-provider": lambda r: r.get("affiliation") == "non-us-provider",
           "non-dod": lambda r: r.get("affiliation") == "other-government"}
ISSM_GRANTS = ("support", "authority", "resources")
# DoDI 8510.01 Table 8: who appoints each RMF role. PER-PM holds both the PM (appointed by the
# Component Acquisition Executive) and the SO (by the Component head). The PAO appoints the AO of
# an MA-managed system, so it counts only where the roles hold a PAO. The CISO is the Component
# SCA and may formally delegate the role: an SCA record held by someone else is the CISO's
# delegate. The CISO's own appointer is OCTX-001's.
TABLE_8 = {
    "PER-CIO": ("dod-component-head",),
    "PER-AO": ("dod-component-head", "PER-PAO"),
    "PER-AODR": ("PER-AO",),
    "PER-SCA": ("PER-CISO",),
    "PER-PM": ("component-acquisition-executive", "dod-component-head"),
    "PER-ISSM": ("PER-PM",),
    "PER-ISSO": ("PER-PM",),
}
# The cybersecurity-related positions among the roles; the program manager, user representative
# and a provider organization hold no such position as such.
CYBER_POSITIONS = ("PER-AO", "PER-AODR", "PER-CISO", "PER-ISSM", "PER-ISSO", "PER-SCA",
                   "PER-ISSE", *CITIZEN_ONLY_ROLES[2:], *SUPERVISED_POSITIONS)
CNSSP_22, ANNEX_A = "CNSSP 22", "CNSSP 22 Annex A"
RISK_STEPS = ("frame", "assess", "respond", "monitor")
MISSION_RISK = "mission-business-risk-management"
DOD_STRATEGY = "dod-siso-strategy"
ENTERPRISE_GOVERNANCE = "dod-enterprise-governance"
SENIOR = ("PER-RE", "PER-CIO", "PER-CISO", "PER-AO", "head-of-agency", "dod-component-head",
          "saorm")
SAORM = "saorm"
AUTHORIZED = ("AD-ATO", "AD-ATOC")
DOC_APPROVERS = ("PER-AO", "PER-AODR")
SYSTEM_OWNER = "PER-PM"
LEADERSHIP = ("PER-CIO", "PER-CISO", "PER-RE", "head-of-agency", "dod-component-head", "saorm")
# SP 800-137 3.1 and CNSSP 22 Section IV.f: the ISCM strategy and program provide awareness of
# threats and vulnerabilities, visibility into organizational assets and control effectiveness.
# The last two (CNSSP 22 IV.f) hold from contract 0.2.0, as DEVICES_SINCE does in consistency.py;
# a 0.1.0 run is not held to them.
MONITORED = ("control-effectiveness", "changes", "organizational-state")
MONITORED_SINCE = {"threat-and-vulnerability-awareness": "0.2.0", "asset-visibility": "0.2.0"}
OA_CONDITIONS = ("initial-authorization", "iscm-program")
POSTURE_FACTORS = ("threats", "vulnerabilities", "technologies", "mission")
# Calendar months the organization's stated review cycle allows between two program reviews.
REVIEW_MONTHS = {"monthly": 1, "quarterly": 3, "semi-annually": 6, "annually": 12}
# Periodic frequencies, most frequent first; an event-driven frequency is no period to compare.
RANK = {f: n for n, f in enumerate(("continuous", "daily", "weekly", "monthly", "quarterly",
                                    "semi-annually", "annually"))}

# CNSSP 12 Section IV.b: at a minimum, a space NSS has a formally designated AO, ISSO and SCA.
SPACE_DESIGNATED = {"PER-AO": "AO", "PER-ISSO": "ISSO", "PER-SCA": "SCA"}
SPACE_OVERLAY = "CNSSI1253F-ATT2-SPACE"
SSP_RECORDS_FILE = "artifacts/data/ssp-records.yaml"

Check = Callable[..., None]


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


def _list(value: Any) -> list[str | int | bool]:
    """A list field's scalar items. A list, a mapping or anything else where the schema wants a
    scalar is dropped here and reported by RUN-FM-001, so no rule raises on it."""
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, str | int | bool)]


def _key(value: Any) -> str | None:
    """A field used as a key or looked up: a string, or None (the schema reports the rest)."""
    return value if isinstance(value, str) else None


def _section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def _date(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _record(ctx: Context, rule: str, owner: str
            ) -> tuple[dict[str, Any] | None, list[RunFinding], Check]:
    """The record, the findings so far and an error helper charged to ``owner`` unless a call
    names another task. Quiet until ART-ORG-CONTEXT is in play; a missing record is P-1's
    finding while P-1 is in scope, and an unreadable one is RUN-FM-001's."""
    out: list[RunFinding] = []

    def err(message: str, task: str | None = None) -> None:
        out.append(make(rule, message, ORG_FILE, None, {task or owner}))

    if not scope.produced_or_seeded(ctx.run, ARTIFACT):
        return None, out, err
    if not ctx.run.path(ORG_FILE).is_file():
        if rule == "OCTX-001" and "P-1" in scope.active_tasks(ctx.run):
            err(f"{ORG_FILE} is missing; P-1 writes it", "P-1")
        return None, out, err
    data = ctx.data(ORG_FILE)
    return (data if isinstance(data, dict) else None), out, err


def _absent(data: dict[str, Any], active: set[str], keys: tuple[str, ...], err: Check) -> None:
    for key in keys:
        task = SECTIONS[key]
        if task in active and key not in data:
            err(f"org-context.yaml has no {key}, which {task} records", task)


def _space_nss(ctx: Context) -> bool:
    """A space NSS: declared in ssp-records.yaml, or applying the Space Platform Overlay."""
    records = ctx.data(SSP_RECORDS_FILE)
    cat = facts_mod.get(ctx.facts, "categorization")
    overlays = cat.get("overlays") if isinstance(cat, dict) else None
    return (isinstance(records, dict) and records.get("space_nss") is True) or \
        (isinstance(overlays, list) and SPACE_OVERLAY in overlays)


def _roles(data: dict[str, Any]) -> list[dict[str, Any]]:
    return _dicts(data.get("roles"))


def _holders(data: dict[str, Any]) -> set[str]:
    return {str(r.get("role")) for r in _roles(data)}


def _sub(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


# --- OCTX-001: role appointments and the people in them (P-1) -------------------------------

def roles(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-001", "P-1")
    if data is None:
        return out
    active = set(scope.active_tasks(ctx.run))
    _absent(data, active, ("roles", "manpower_structure", "open_functions"), err)
    # The appointments are P-1's to make; a context seeded from outside the run is judged on
    # the records it holds, not on the ones it leaves out.
    holders = _holders(data)
    if "P-1" in active and "PER-UR" not in holders:
        err("no user representative is appointed for the system")
    if "P-1" in active and "PER-ISSM" not in holders:
        err("no ISSM is appointed for the system")
    if "P-1" in active and _space_nss(ctx):
        for role, title in SPACE_DESIGNATED.items():
            if role not in _holders(data):
                err(f"a space NSS has no formally designated {title}")
    for r in _roles(data):
        rid, role, held = r.get("id"), _key(r.get("role")), _key(r.get("affiliation"))
        by = r.get("appointed_by")
        if role == "PER-UR" and r.get("appointed_by") != SYSTEM_OWNER:
            err(f"{rid}: the user representative is appointed by {r.get('appointed_by')}, not "
                "the information system owner")
        if role == "PER-PAO" and _key(r.get("mission_area")) not in PAO_APPOINTERS:
            err(f"{rid}: the PAO names no mission_area ({', '.join(PAO_APPOINTERS)}), so whether "
                "its DoD MA owner appointed it cannot be read")
        elif role == "PER-PAO" and by != PAO_APPOINTERS.get(_key(r.get("mission_area"))):
            err(f"{rid}: the PAO for mission area {r.get('mission_area')} is appointed by {by}, "
                "not the DoD MA owner of that mission area")
        if role == "PER-DODCISO" and by != "dod-cio":
            err(f"{rid}: the DoD CISO is appointed by {by}, not the DoD CIO")
        if role == "PER-TAG" and by != "PER-CISO":
            err(f"{rid}: the RMF TAG Representative is appointed by {by}, not the DoD Component "
                "CISO")
        if role in INHERENTLY_GOVERNMENTAL and held not in GOVERNMENT:
            err(f"{rid}: {INHERENTLY_GOVERNMENTAL[role]} is an inherent U.S. Government "
                f"function and is assigned to government personnel only, not {held}")
        if role == "PER-AO" and (r.get("citizenship") != "us" or held not in DOD):
            err(f"{rid}: the AO must be a U.S. citizen and a DoD official, not "
                f"{r.get('citizenship')} {held}")
        if role == "PER-AO" and not _sub(r, "appointment").get("basis"):
            err(f"{rid}: the AO's appointment states no basis")
        if role == "PER-ISSM" and set(ISSM_GRANTS) - set(_list(r.get("granted"))):
            err(f"{rid}: the ISSM is appointed without the support, authority and resources to "
                "satisfy the responsibilities")
        if role != "PER-CISO":
            continue
        # DoDI 8510.01 Table 8: the Component head appoints where no Component CIO exists.
        if by != "PER-CIO" and (by != "dod-component-head" or "PER-CIO" in holders):
            err(f"{rid}: the senior agency information security officer is designated by "
                f"{r.get('appointed_by')}, not the chief information officer")
        if r.get("primary_duty") != "security":
            err(f"{rid}: the senior agency information security officer maintains security "
                f"duties as a primary responsibility, not {r.get('primary_duty')}")
        if r.get("heads_office") is not True:
            err(f"{rid}: the senior agency information security officer heads an office with "
                "the mission and resources for the security program")
        if "PER-PRIV" not in _list(r.get("coordinates_with")):
            err(f"{rid}: the senior agency information security officer coordinates with the "
                "senior agency official for privacy")
    return out


# --- RAPT-001: the appointing authorities of DoDI 8510.01 Table 8 (P-1) ----------------------

def appointments(ctx: Context) -> list[RunFinding]:
    """RAPT-001: each Table 8 role is appointed by the official Table 8 names, an AO and a PM or
    SO are appointed for the system, as is the Component CISO (4.3.c(6)), the PM or SO in
    writing (4.3.c(3)), and the AO role is re-delegated only to government personnel
    (2.7.m(1)). The Component CISO's own appointer is OCTX-001's clause, not restated here. A
    PER-SCA record held by the CISO (same name and email) is the CISO performing as the SCA and
    is judged by the CISO's appointer; only a delegate must be appointed by the CISO. A context
    seeded from outside the run is judged on the records it holds."""
    data, out, err = _record(ctx, "RAPT-001", "P-1")
    if data is None:
        return out
    holders = _holders(data)
    if "P-1" in scope.active_tasks(ctx.run):
        if "PER-AO" not in holders:
            err("no AO is appointed for the system")
        if "PER-PM" not in holders:
            err("no PM or SO is appointed for the system")
        if "PER-CISO" not in holders:
            err("no DoD Component CISO is appointed to direct the Component cybersecurity program")
    cisos = [r for r in _roles(data) if r.get("role") == "PER-CISO"]
    for r in _roles(data):
        rid, role, held = r.get("id"), _key(r.get("role")), _key(r.get("affiliation"))
        by = r.get("appointed_by")
        allowed = [a for a in TABLE_8.get(role or "", ()) if a != "PER-PAO" or a in holders]
        if role == "PER-SCA" and any(_same_holder(r, c) for c in cisos):
            allowed = sorted({_key(c.get("appointed_by")) for c in cisos
                              if _same_holder(r, c)} - {None})
        if allowed and by not in allowed:
            err(f"{rid}: {role} is appointed by {by}, which DoDI 8510.01 Table 8 does not name "
                f"as its appointing authority ({' or '.join(allowed)})")
        instrument = _key(_sub(r, "appointment").get("instrument"))
        if role == "PER-PM" and instrument in (None, "oral"):
            err(f"{rid}: the PM or SO is not appointed in writing")
        if role == "PER-AODR" and held not in GOVERNMENT:
            err(f"{rid}: the AO role cannot be re-delegated to personnel who are not government "
                f"personnel, and the AODR is {held}")
    return out


def _same_holder(one: dict[str, Any], other: dict[str, Any]) -> bool:
    """Whether two role records name the same person: the same name and business email. A
    delegate who uses the office's mailbox is still another person."""
    name, email = _key(one.get("name")), _key(_sub(one, "contact").get("email"))
    return name is not None and email is not None and name == _key(other.get("name")) \
        and email == _key(_sub(other, "contact").get("email"))


# --- OCTX-013: who may hold a cybersecurity position, and on what terms (P-1) ---------------

def positions(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-013", "P-1")
    if data is None:
        return out
    records = _roles(data)
    by_id = {_key(r.get("id")): r for r in records}
    manpower = {_key(p.get("id")) for p in _dicts(data.get("manpower_structure"))}
    opened: dict[Any, set[str]] = {}
    for f in _dicts(data.get("open_functions")):
        opened.setdefault(_key(f.get("function")), set()).update(_list(f.get("open_to")))
    for r in records:
        rid, role, held = r.get("id"), _key(r.get("role")), _key(r.get("affiliation"))
        position = _sub(r, "position")
        barred = role in CITIZEN_ONLY_ROLES or position.get("supervisory") is True \
            or "pki-certificate-issuance" in _list(r.get("duties"))
        if barred and r.get("citizenship") == "non-us":
            err(f"{rid}: a non-U.S. citizen may not serve as ISSM, ISSO, in a supervisory "
                "cybersecurity position or be responsible for PKI certificate issuance")
        if role in SUPERVISED_POSITIONS and r.get("citizenship") == "non-us":
            supervisor = by_id.get(_key(r.get("supervised_by"))) or {}
            if supervisor.get("citizenship") != "us":
                err(f"{rid}: a non-U.S. citizen {role} serves under the immediate supervision of "
                    "a U.S. citizen")
            if _sub(r, "personnel_security").get("status") != "met":
                err(f"{rid}: a non-U.S. citizen {role} meets the investigative requirements of "
                    "DoDM 5200.02")
        if role not in CYBER_POSITIONS:
            continue
        for category, applies in OPEN_TO.items():
            if applies(r) and category not in opened.get(role, set()):
                err(f"{rid}: {role} is held by a {category} appointee, and the organization has "
                    f"not identified it as a cybersecurity function a {category} may perform")
        if position.get("suitability") != "met":
            err(f"{rid}: the position is not designated with its suitability and fitness "
                f"requirements met ({position.get('designation')}, "
                f"{position.get('suitability')})")
        if held == "dod-civilian" and position.get("recorded_in") != "DCPDS":
            err(f"{rid}: the position designation of a civilian is documented in the Defense "
                f"Civilian Personnel Data System, not {position.get('recorded_in')}")
        elsewhere = _key(position.get("manpower_of"))
        if elsewhere is None and _key(position.get("manpower_id")) not in manpower:
            err(f"{rid}: the position {position.get('manpower_id')} is not identified in the "
                "organization's manpower structure")
        if _sub(r, "duties_statement").get("form") != "written":
            err(f"{rid}: the appointee was given no written statement of cybersecurity "
                "responsibilities")
        if role == "PER-ISSM" and _sub(r, "personnel_security").get("status") != "met":
            err(f"{rid}: the ISSM does not meet the requirements of DoDM 5200.02")
    return out


# --- OCTX-002: code-signing certificates (P-1) ----------------------------------------------

def code_signing(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-002", "P-1")
    if data is None:
        return out
    if "P-1" in scope.active_tasks(ctx.run) and "code_signing" not in data:
        err("org-context.yaml has no code_signing, which P-1 records")
        return out
    signing = _section(data, "code_signing")
    if signing.get("used") is not True:
        return out
    if not signing.get("process"):
        err("code-signing certificates are used and no process designates the individuals "
            "authorized to receive them")
    designated = _dicts(signing.get("designated"))
    need = signing.get("operational_need")
    count = need if type(need) is int else None  # a count; true or "2" is none
    if count is None:
        err("code-signing certificates are used and code_signing states no operational_need, "
            "the number of holders operational requirements call for")
    if count is not None and len(designated) > count:
        err(f"{len(designated)} individuals are designated to receive code-signing "
            f"certificates where operational requirements need {need}: designations are kept "
            "to a minimum")
    return out


# --- OCTX-003: program, policies and resources (P-2) ----------------------------------------

def _system_id(ctx: Context) -> Any:
    node = facts_mod.get(ctx.facts, "system_id")
    return node.get("value") if isinstance(node, dict) else node


def program(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-003", "P-2")
    if data is None:
        return out
    active = set(scope.active_tasks(ctx.run))
    _absent(data, active, ("program", "policies", "resources"), err)
    if "program" in data:
        prog = _section(data, "program")
        implements = set(_list(prog.get("implements")))
        if CNSSP_22 not in implements:
            err("the Cybersecurity Risk Management Program does not implement CNSSP 22")
        if ANNEX_A not in implements:
            err("the Cybersecurity Risk Management Program does not support the CNSSP 22 "
                "Annex A issuances")
        if MISSION_RISK not in _list(prog.get("integrated_with")):
            err("the Cybersecurity Risk Management Program is not integrated with mission and "
                "business risk management")
        if {"strategic-planning", "operational-planning"} - set(_list(prog.get(
                "integrated_with"))):
            err("security and privacy risk management is not integrated with the strategic and "
                "operational planning processes")
        if prog.get("scope") != "organization-wide":
            err(f"the Cybersecurity Risk Management Program is {prog.get('scope')}, not an "
                "integrated, organization-wide program")
        missing = [s for s in RISK_STEPS if s not in _list(prog.get("processes"))]
        if missing:
            err(f"the program does not {', '.join(missing)} risk: risk management frames, "
                "assesses, responds to and monitors risk")
        system = _system_id(ctx)
        if system and system not in _list(prog.get("systems")):
            err(f"{system} is not assigned to and governed by the Component cybersecurity "
                "program")
        if DOD_STRATEGY not in _list(prog.get("consistent_with")):
            err("the Component cybersecurity program is not consistent with the strategy and "
                "direction of the DoD SISO")
        integrated = {g for b in _dicts(prog.get("governance_bodies"))
                      for g in _list(b.get("integrates_with"))}
        if ENTERPRISE_GOVERNANCE not in integrated:
            err("no cybersecurity governance body integrates with the DoD enterprise "
                "governance processes")
    return out


# --- OCTX-012: life-cycle policies and the resources for risk management (P-2) -----------

def policies_resources(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-012", "P-2")
    if data is None:
        return out
    holders = _holders(data)
    if "policies" in data:
        policies = _dicts(data.get("policies"))
        covered = {p for pol in policies for p in _list(pol.get("phases"))}
        phases = list(ctx.run.framework.index("phases"))
        for phase in phases:
            if phase not in covered:
                err(f"no organizational policy integrates risk management into {phase}: "
                    "policies carry it throughout the system life cycle")
        if not [p for p in policies if p.get("sse_integrated") is True]:
            err("no organizational policy integrates systems security engineering within "
                "systems engineering")
        if SYSTEM_OWNER not in {who for p in policies for who in _list(p.get("directs"))}:
            err("no organizational policy directs the system owner to maintain the system in "
                "compliance with the RMF")
        for p in policies:
            if _key(p.get("owner")) not in holders:
                err(f"{p.get('id')}: its owner {p.get('owner')} holds no role in roles")
    if "resources" in data:
        res = _section(data, "resources")
        funding = _section(res, "funding")
        if funding.get("process") != "PPBE":
            err(f"resources for the RMF are identified and allocated in {funding.get('process')}, "
                "not the Planning, Programming, Budgeting, and Execution process")
        for key in ("funding", "staffing"):
            line = _section(res, key)
            for official in (_key(line.get("identified_by")), _key(line.get("secured_by"))):
                if official not in holders:
                    err(f"the {key} for the risk management tasks is identified or secured by "
                        f"{official}, who holds no role in roles")
            for official in _list(line.get("made_available_to")):
                if official not in holders:
                    err(f"the {key} for the risk management tasks is made available to "
                        f"{official}, who holds no role in roles")
        allocation = _section(res, "allocation")
        deciders = set(_list(allocation.get("determined_by")))
        if "PER-CIO" not in deciders or not deciders & set(DOC_APPROVERS):
            err("the allocation of resources protecting the systems is not determined by the "
                "chief information officer and the authorizing officials")
        if ctx.processes_pii and "PER-PRIV" not in _list(allocation.get("coordinated_with")):
            err("the system processes PII and the allocation of resources protecting it is not "
                "coordinated with the senior agency official for privacy")
    return out


# --- OCTX-004: the risk management strategy (P-2) -------------------------------------------

def strategy(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-004", "P-2")
    if data is None:
        return out
    active = set(scope.active_tasks(ctx.run))
    _absent(data, active, ("risk_frame", "governance", "risk_assessment_guidance",
                           "risk_response", "external_entities"), err)
    if "governance" in data:
        executive = _sub(_section(data, "governance"), "risk_executive")
        delegate = _key(executive.get("delegated_to"))
        if _key(executive.get("led_by")) not in {SAORM, delegate} - {None}:
            err(f"the risk executive (function) is led by {executive.get('led_by')}, not the "
                "senior accountable official for risk management or the official or group it "
                "delegated the function to")
        if executive.get("structured_by") != SAORM:
            err(f"the structure and responsibilities of the risk executive (function) are "
                f"determined by {executive.get('structured_by')}, not the senior accountable "
                "official for risk management")
    if "external_entities" in data:
        entities = _dicts(data.get("external_entities"))
        for e in entities:
            if e.get("relationship") != "actual":
                continue
            if e.get("risk_acceptable") is not True:
                if not e.get("response"):
                    err(f"{e.get('id')}: the ongoing risk of the relationship with "
                        f"{e.get('name')} is neither determined acceptable nor given a response")
                continue
            if e.get("accepted_by") not in SENIOR:
                err(f"{e.get('id')}: the risk of the relationship with {e.get('name')} is "
                    f"accepted by {e.get('accepted_by')}, not a senior leader")
        named = {_key(e.get("name")) for e in entities}
        leveraged = ctx.data(LEVERAGED_FILE)
        records = leveraged.get("leveraged_authorizations") if isinstance(leveraged, dict) \
            else None
        for la in _dicts(records):
            if _key(la.get("provider")) not in named:
                err(f"{la.get('id')}: the system leverages an authorization from "
                    f"{la.get('provider')}, which external_entities does not list")
    return out


# --- OCTX-005: common control packages (P-5) ------------------------------------------------

def common_controls(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-005", "P-5")
    if data is None:
        return out
    if "P-5" in scope.active_tasks(ctx.run) and "common_controls" not in data:
        err("org-context.yaml has no common_controls, which P-5 records")
    holders = _holders(data)
    for cc in _dicts(data.get("common_controls")):
        provider = cc.get("provided_by")
        if _key(cc.get("persona")) not in holders:
            err(f"{provider}: the common control provider {cc.get('persona')} holds no role in "
                "roles")
        if _sub(cc, "authorization").get("decision") not in AUTHORIZED:
            err(f"{provider}: the common controls hold no authorization from their authorizing "
                f"official ({_sub(cc, 'authorization').get('decision')})")
        assessed = _sub(cc, "assessed_by")
        if assessed.get("qualified") is not True:
            err(f"{provider}: the common controls are assessed by an assessor who is not "
                "qualified")
        if assessed.get("chosen_by") == "system-owner":
            err(f"{provider}: the assessment of the common controls is arranged by the system "
                "owner, not the common control provider or the organization")
        if cc.get("deficiencies") is True and "poam" not in cc:
            err(f"{provider}: the common controls have deficiencies and no plan of action and "
                "milestones")
        for name in ("plan", "sar", "poam"):
            doc = _sub(cc, name)
            if not doc:
                continue
            if doc.get("approved_by") not in DOC_APPROVERS:
                err(f"{provider}: the {name} is approved by {doc.get('approved_by')}, not the "
                    "authorizing official accountable for the common controls")
            if SYSTEM_OWNER not in _list(doc.get("available_to")):
                err(f"{provider}: the {name} is not made available to the system owner of the "
                    "inheriting system")
            approved, shared = _date(doc.get("approved_on")), _date(doc.get("available_on"))
            if approved and shared and shared < approved:
                err(f"{provider}: the {name} is made available before the authorizing official "
                    "reviewed and approved it")
    return out


# --- OCTX-006: inherited controls in the system assessment (A-3) ----------------------------

def inherited_assessment(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-006", "A-3")
    if data is None or "common_controls" not in data:
        return out
    packages = {_key(cc.get("provided_by")): cc for cc in _dicts(data.get("common_controls"))}
    inherited = {_key(c.get("control_id")): _key(c.get("inherited_from"))
                 for _, c in family_records(ctx, SSP_DIR, "controls")
                 if c.get("status") == "inherited" and _key(c.get("inherited_from"))}
    leveraged = {_key(la.get("provider")) for la in _dicts(
        _section_of(ctx, LEVERAGED_FILE).get("leveraged_authorizations"))}
    # Both dates belong to this assessment: when its report was first delivered, and when the
    # provider's results it rests on were made available (recorded on the determination).
    delivered = [_date(d.get("date")) for d in _dicts(_section_of(ctx, SAR_REPORT_FILE)
                                                      .get("delivered"))]
    delivered_on = min((d for d in delivered if d), default=None)
    for _, det in family_records(ctx, SAR_DIR, "determinations"):
        cid = det.get("control_id")
        if _key(cid) not in inherited:
            continue
        basis = _sub(det, "inherited")
        package = packages.get(inherited[cid])
        if package is None and inherited[cid] in leveraged:
            package = {}  # an external provider's authorization package, leveraged (C-1)
        if package is None or basis.get("basis") != "provider-assessment":
            err(f"the system assessment assesses the inherited control {cid}: its determination "
                "rests on the separate assessment of the common controls it inherits")
            continue
        if basis.get("verified") is not True:
            err(f"the assessor does not verify that the system inherits and uses {cid}")
        shared = _date(_sub(basis, "provider_assessment").get("available_on"))
        if delivered_on and (shared is None or shared > delivered_on):
            err(f"the assessment is delivered as complete before the assessment results of the "
                f"common controls behind {cid} are made available to the system owner")
    return out


def _latest(ctx: Context) -> dt.date | None:
    """The latest date the run vouches for: its newest authorization record (L-0067)."""
    days = [_date(r.get("date")) for r in _dicts(ctx.ledger)]
    return max((d for d in days if d), default=None)


def _section_of(ctx: Context, rel: str) -> dict[str, Any]:
    value = ctx.data(rel)
    return value if isinstance(value, dict) else {}


# --- OCTX-007: the organizational ISCM program (P-7) ----------------------------------------

def iscm_program(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-007", "P-7")
    if data is None:
        return out
    if "P-7" in scope.active_tasks(ctx.run) and "iscm" not in data:
        err("org-context.yaml has no iscm, which P-7 records")
    if "iscm" not in data:
        return out
    iscm = _section(data, "iscm")
    for p in _dicts(iscm.get("processes")):
        if p.get("mode") == "manual" and p.get("verified") is not True:
            err(f"the manual ISCM process {p.get('name')} is not verified as repeatable")
    subjects = {_key(p.get("subject")) for p in _dicts(iscm.get("policies"))}
    if "security-status-monitoring" not in subjects:
        err("there is no organization-wide policy for security status monitoring")
    if "results-to-risk-assessment" not in subjects:
        err("there is no organization-wide policy for making ISCM results available to the "
            "risk assessment process")
    objectives = {_key(o.get("id")) for o in _dicts(iscm.get("objectives"))}
    for a in _dicts(iscm.get("activities")):
        if not set(_list(a.get("objectives"))) & objectives:
            err(f"the ISCM activity {a.get('name')} maps to no ISCM strategic objective")
    held = [*MONITORED, *(m for m, since in MONITORED_SINCE.items() if ctx.run.holds(since))]
    for item in held:
        if item not in _list(iscm.get("monitors")):
            err(f"organization-wide continuous monitoring does not determine {item}")
    declared = {_key(n.get("element")) for n in _dicts(iscm.get("not_applicable"))}
    for assessment in _dicts(iscm.get("assessments")):
        for j in _dicts(assessment.get("judgments")):
            element, judgment = _key(j.get("element")), j.get("judgment")
            if judgment == "not-applicable" and element not in declared:
                err(f"{element} is judged not applicable, and the organization-wide ISCM "
                    "strategy does not specify that it is not applicable")
            if element in declared and judgment != "satisfied":
                err(f"{element} is not applicable under the strategy and is judged {judgment}: "
                    "such elements are judged satisfied")
    return out


# --- OCTX-008: reviewing and assessing the ISCM program (P-7) -------------------------------

def _months_after(day: dt.date, months: int) -> dt.date:
    """The same day ``months`` calendar months later, clamped to the end of a shorter month."""
    total = day.month - 1 + months
    year, month = day.year + total // 12, total % 12 + 1
    last = (dt.date(year + month // 12, month % 12 + 1, 1) - dt.timedelta(days=1)).day
    return dt.date(year, month, min(day.day, last))


def iscm_review(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-008", "P-7")
    if data is None or "iscm" not in data:
        return out
    iscm = _section(data, "iscm")
    holders = _holders(data)
    reviews = sorted(_dicts(iscm.get("reviews")), key=lambda r: str(r.get("date")))
    allowed = REVIEW_MONTHS.get(str(_section(iscm, "review_cycle").get("frequency")))
    established, latest = _date(iscm.get("established")), _latest(ctx)
    # A first review, and a first formal assessment, are due one review cycle after the program
    # was established, judged on the latest date the run vouches for (L-0067).
    due = bool(allowed and established and latest
               and latest > _months_after(established, allowed))
    if due and not reviews:
        err("the ISCM program and strategy record no review")
    previous = None
    for r in reviews:
        day = _date(r.get("date"))
        if allowed and previous and day and day > _months_after(previous, allowed):
            err(f"the ISCM program review of {day} follows the previous one by more than its "
                f"{_section(iscm, 'review_cycle').get('frequency')} review frequency")
        previous = day or previous
    considered = {c for r in reviews for c in _list(r.get("considered"))}
    if reviews and "threats" not in considered:
        err("no ISCM strategy review looks for ways to improve the response to known and "
            "emerging threats")
    assessments = _dicts(iscm.get("assessments"))
    if due and not assessments:
        err("the ISCM program has no formal assessment of how well it meets its objectives")
    for a in assessments:
        if not set(_list(a.get("reported_to"))) & set(LEADERSHIP):
            err(f"the ISCM program assessment of {a.get('date')} is not reported to "
                "organizational leadership")
        for f in _dicts(a.get("findings")):
            if _key(f.get("owner")) not in holders:
                err(f"ISCM assessment finding {f.get('id')}: the role responsible for the "
                    f"response, {f.get('owner')}, holds no role in roles")
            due, held = _date(f.get("due")), _date(a.get("date"))
            if due and held and due < held:
                err(f"ISCM assessment finding {f.get('id')}: the time frame for completion "
                    "ends before the assessment")
    return out


# --- OCTX-009: organizational minimum frequencies in the system strategy (S-5) --------------

def minimum_frequencies(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-009", "S-5")
    if data is None or not scope.produced_or_seeded(ctx.run, "ART-CONMON"):
        return out
    minimums = {_key(m.get("family")): _key(m.get("frequency"))
                for m in _dicts(_section(data, "iscm").get("minimum_frequencies"))}
    conmon = _section_of(ctx, CONMON_FILE)
    if not minimums or not conmon:
        return out
    families = {f.split("-")[0] for f in baseline_mod.control_ids(ctx.run)} \
        if baseline_mod.load(ctx.run) else set()
    for record in _dicts(conmon.get("frequencies")):
        fam, freq = _key(record.get("family")), _key(record.get("frequency"))
        floor = minimums.get(fam)
        if floor in RANK and freq in RANK and RANK[freq] > RANK[floor]:
            err(f"the {fam} monitoring frequency {freq} is less frequent than the "
                f"organization's minimum {floor}")
    review = _section(conmon, "minimum_review")
    if set(minimums) & families and review.get("by") != SYSTEM_OWNER:
        err(f"the system owner does not review whether the organization's minimum monitoring "
            f"frequencies suffice for the system (reviewed by {review.get('by')})")
    return out


# --- OCTX-010: the ongoing authorization process (M-6) --------------------------------------

def ongoing_process(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-010", "M-6")
    if data is None:
        return out
    kinds = {e.id: str(e.data.get("effect")) for e in ctx.run.framework.index("decisions")
             .values()}
    if not any(s.ongoing for s in ledger.in_force(_dicts(ctx.ledger), kinds).values()):
        return out
    iscm = _section(data, "iscm")
    process = _sub(iscm, "ongoing_authorization")
    if not process:
        err("the system is under ongoing authorization and the organization records no "
            "organization-wide ongoing authorization process", "P-7")
        return out
    for condition in OA_CONDITIONS:
        if condition not in _list(process.get("conditions")):
            err(f"the ongoing authorization process does not designate that the {condition} "
                "condition is satisfied before a system transitions", "P-7")
    if iscm.get("program_status") != "in-place":
        err("the system is under ongoing authorization and no organizational continuous "
            "monitoring program is in place", "P-7")
    return out


# --- OCTX-011: the organizational risk posture in operations (P-3) --------------------------

def _operating_since(ctx: Context) -> dt.date | None:
    """When the authorization to operate that stands was granted, or None: the system has been
    in operations since then."""
    kinds = {e.id: str(e.data.get("effect")) for e in ctx.run.framework.index("decisions")
             .values()}
    standing = ledger.in_force(_dicts(ctx.ledger), kinds).values()
    days = [_date(s.record.get("date")) for s in standing
            if kinds.get(_key(s.record.get("decision"))) == "authorize"]
    return min((d for d in days if d), default=None)


def posture_reviews(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "OCTX-011", POSTURE_TASK)
    if data is None:
        return out
    active = set(scope.active_tasks(ctx.run))
    reviews = _dicts(data.get("posture_reviews"))
    since = _operating_since(ctx)
    latest = _latest(ctx)
    if POSTURE_TASK in active and set(OPERATIONS_TASKS) & active and since and latest \
            and latest > since and not reviews:
        err("no ongoing review of threat, vulnerability, technology and mission changes "
            "against the organizational risk posture is recorded")
    considered = {c for r in reviews for c in _list(r.get("considered"))}
    missing = [f for f in POSTURE_FACTORS if f not in considered]
    if reviews and missing:
        err(f"the posture reviews do not review {', '.join(missing)} changes against the "
            "organizational risk posture")
    return out


# --- RMR-001: no conflict of interest between roles, and a privacy official designated (P-1) --

def role_conflicts(ctx: Context) -> list[RunFinding]:
    """RMR-001 (SP 800-37r2 Task P-1 and Appendix D): one individual in several roles holds no
    conflict of interest, so the authorizing official is not also the system owner of what it
    authorizes; and P-1 designates a senior agency official for privacy. Individuals are
    compared by name, the field that identifies the appointee. The common control provider half
    of the source's example is not checked: org-context.yaml cannot tell whether this run's AO
    authorizes the provider's common controls, which their own AO may do."""
    data, out, err = _record(ctx, "RMR-001", "P-1")
    if data is None:
        return out
    if "P-1" in scope.active_tasks(ctx.run) and "PER-PRIV" not in _holders(data):
        err("no senior agency official for privacy is designated for the organization")
    named: dict[str, set[str]] = {}
    shown: dict[str, str] = {}
    for r in _roles(data):
        name = r.get("name")
        if isinstance(name, str) and name.strip():
            key = name.strip().casefold()
            shown.setdefault(key, name.strip())
            named.setdefault(key, set()).add(str(r.get("role")))
    for key, held in sorted(named.items()):
        name = shown[key]
        if {"PER-AO", SYSTEM_OWNER} <= held:
            err(f"{name} holds both the authorizing official and the system owner role: an "
                "authorizing official cannot occupy the role of system owner for a system it "
                "authorizes")
    return out
