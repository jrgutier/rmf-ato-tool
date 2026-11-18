"""What C-1 records about the system beside its identity: SYSD-*. The classification, IT type,
owning organization, version, operational environment and life-cycle phase are facts
(INV-4); ownership, physical environment, NOSC and CSSP alignment and interconnections are
`artifacts/data/system-description.yaml`; user groups and consumed services extend users.yaml
and leveraged-authorizations.yaml. A record is judged once C-1 is in scope; an unreadable file
is RUN-FM-001's.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import FACTS_FILE

SD_FILE = "artifacts/data/system-description.yaml"
USERS_FILE = "artifacts/data/users.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
SVC_FILE = "artifacts/data/service-agreements.yaml"
WRITER = "C-1"
C2 = "C-2"
LEVELS = ("low", "moderate", "high")
UNCLASSIFIED = "unclassified"
CLASSIFIED_OVERLAY = "CNSSI1253E-ATT5-CLASSIFIED"
# DoDI 8530.01 Encl 2 9.a and 11.l: DIA authorizes SE CSSPs, CDRUSSTRATCOM (its cyberspace
# operations role now held by USCYBERCOM) GENSER CSSPs after DISA evaluation.
GENSER_AUTHORITIES = {"CDRUSSTRATCOM", "USCYBERCOM"}
SE_AUTHORITY = "DIA"
# Encl 4 c.(6): changes go to CDRUSSTRATCOM and DISA for GENSER systems, DIA for SE systems.
GENSER_RECIPIENTS = ({"CDRUSSTRATCOM", "USCYBERCOM"}, "DISA")
PARTNER_TERMS = ("dodin-operations-responsibilities", "cybersecurity-requirements",
                 "data-protection-requirements", "incident-reporting-contacts")
PARTNER_BASIS = ("component-risk-assessment", "risk-tolerance-guidance",
                 "interconnection-policy")
DOD_PARTY = "dod-component"
INTERCONNECTION = "interconnection"
FOREIGN_GROUPS = ("foreign-national", "coalition-partner")
EXTERNAL_INSTRUMENTS = ("interagency-agreement", "statement-of-work", "contract")
CUI = "CUI"
MARKINGS = ("unclassified", CUI, "confidential", "secret", "top-secret")
VULNERABILITY_DOCUMENTS = ("ART-SAR", "ART-POAM", "ART-STIG", "ART-CMP")


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _c1_active(ctx: Context) -> bool:
    return WRITER in scope.active_tasks(ctx.run)


def _rank(value: Any) -> int:
    return LEVELS.index(value) if value in LEVELS else -1


# --- SYSD-001: the classification and IT type against the categorization -----------------
# FACTS-001 holds that each fact C-1 writes is set (C-1 facts_since in framework/tasks/C.yaml).

def system_facts(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []

    def err(message: str, owner: str = WRITER) -> None:
        out.append(make("SYSD-001", message, FACTS_FILE, None, {owner}))

    if not _c1_active(ctx):
        return out
    facts = ctx.facts
    level = _mapping(facts_mod.get(facts, "classification")).get("value")
    cat = facts_mod.get(facts, "categorization")
    if level is not None and isinstance(cat, dict):
        overlays = _list(cat.get("overlays"))
        if level != UNCLASSIFIED and CLASSIFIED_OVERLAY not in overlays:
            err(f"the system holds {level} information and the Classified System Overlay is "
                "not applied", C2)
        if level == UNCLASSIFIED and CLASSIFIED_OVERLAY in overlays:
            err("the Classified System Overlay is applied to a system whose classification is "
                "unclassified", C2)
    _system_type(ctx, err)
    return out


def _system_type(ctx: Context, err: Any) -> None:
    node = _mapping(facts_mod.get(ctx.facts, "system_type"))
    kind = node.get("value")
    cat = _mapping(facts_mod.get(ctx.facts, "categorization"))
    if kind == "enclave" and cat:
        for host in _dicts(node.get("hosts")):
            low = [k for k in ("c", "i", "a") if _rank(cat.get(k)) < _rank(host.get(k))]
            if low:
                err(f"the enclave is categorized below {host.get('system')}, a system it hosts "
                    f"({', '.join(low)})", C2)
    if kind == "pit-system":
        if node.get("designated_by") not in ("osd-component-head", "dod-component-head",
                                             "delegate"):
            err("the PIT system is not designated by the responsible OSD or DoD Component "
                "head or a delegate")
        if not node.get("registered_in"):
            err("the PIT system is not centrally registered at the DoD Component level")
        if node.get("pit_ao_appointed") is not True:
            err("the PIT system's AO is not one specifically appointed to authorize PIT "
                "systems")


# --- SYSD-002: ownership, physical environment and service alignment -----------------------

def system_description(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SYSD-002", message, SD_FILE, None, {WRITER}))

    if not _c1_active(ctx):
        return out
    if not ctx.run.path(SD_FILE).is_file():
        err(f"{SD_FILE} is missing; C-1 writes it")
        return out
    data = _mapping(ctx.data(SD_FILE))
    connection = _mapping(facts_mod.get(ctx.facts, "system_type")).get("dodin_connection")
    alignment = data.get("service_alignment")
    if connection in ("direct", "indirect") and not isinstance(alignment, dict):
        err("the system connects to the DODIN and is aligned to no NOSC and CSSP")
    if not isinstance(alignment, dict):
        return out
    designation = alignment.get("designation")
    authorities = {a for a in _list(alignment.get("authorized_by")) if _key(a)}
    if designation in ("genser", "both") and not authorities & GENSER_AUTHORITIES:
        err("a CSSP offers GENSER cybersecurity services as authorized by CDRUSSTRATCOM "
            "(USCYBERCOM)")
    if designation in ("se", "both") and SE_AUTHORITY not in authorities:
        err("a CSSP offers SE cybersecurity services as authorized by the Director, DIA")
    # S-4 writes the agreements; C-1 names the one it will hold. Until S-4 records any, the
    # cross-file match waits, and a mismatch is charged to S-4, the later writer (F-04-2).
    agreements = _dicts(_mapping(ctx.data(SVC_FILE)).get("agreements")) \
        if ctx.run.path(SVC_FILE).is_file() else []
    if agreements:
        cssps = {_key(a.get("id")) for a in agreements if a.get("role") == "cssp"}
        if _key(alignment.get("cssp_agreement")) not in cssps:
            out.append(make("SYSD-002", f"the aligned CSSP {alignment.get('cssp_agreement')} "
                            f"is no CSSP agreement in {SVC_FILE}", SVC_FILE, None, {"S-4"}))
    for change in _dicts(alignment.get("changes")):
        told = {a for a in _list(change.get("reported_to")) if _key(a)}
        genser_told = told & GENSER_RECIPIENTS[0] and GENSER_RECIPIENTS[1] in told
        if designation in ("genser", "both") and not genser_told:
            err(f"the CSSP change of {change.get('date')} on a GENSER system is reported to "
                "CDRUSSTRATCOM and the Director, DISA")
        if designation in ("se", "both") and SE_AUTHORITY not in told:
            err(f"the CSSP change of {change.get('date')} on an SE system is reported to the "
                "Director, DIA")
    return out


# --- SYSD-003: interconnections and their agreements --------------------------------------

def interconnections(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SYSD-003", message, SD_FILE, None, {WRITER}))

    if not _c1_active(ctx) or not ctx.run.path(SD_FILE).is_file():
        return out
    records = _dicts(_mapping(ctx.data(SD_FILE)).get("interconnections"))
    boundary = _dicts(_mapping(ctx.data(BOUNDARY_FILE)).get("components"))
    links = {_key(c.get("id")) for c in boundary if c.get("type") == INTERCONNECTION}
    described = {_key(r.get("component")) for r in records}
    for component in sorted(str(c) for c in links - described if c):
        err(f"the interconnection {component} has no interconnection record")
    known = {_key(c.get("id")) for c in boundary}
    # DoDI 8530.01 Encl 4 4.d and 4.f: mission partner agreements govern connection to the DODIN.
    connection = _mapping(facts_mod.get(ctx.facts, "system_type")).get("dodin_connection")
    dodin = connection in ("direct", "indirect")
    for r in records:
        ident, partner = r.get("id"), r.get("partner")
        agreement = _mapping(r.get("agreement"))
        instrument = agreement.get("instrument")
        if _key(r.get("component")) not in known:
            err(f"{ident}: {r.get('component')} is no boundary component")
        if partner == DOD_PARTY or not dodin:
            continue
        unbased = [b for b in PARTNER_BASIS if b not in _list(r.get("based_on"))]
        if unbased:
            err(f"{ident}: the mission partner agreement is not based on "
                f"{', '.join(unbased)}")
        if partner == "foreign-mission-partner" and instrument != "international-agreement":
            err(f"{ident}: an interconnection with a foreign mission partner is concluded as an "
                f"international agreement, not {instrument}")
        if partner == "defense-contractor" and instrument != "contract":
            err(f"{ident}: a Defense contractor is required by contract to meet cybersecurity "
                f"requirements to connect, not by {instrument}")
        if partner == "federal-mission-partner" and r.get("cybersecurity_services") not in (
                "dod-cssp-subscription", "equivalent-capability-assessed"):
            err(f"{ident}: a federal mission partner subscribes to a DoD CSSP or holds an "
                "equivalent capability the DoD CIO and DISA assessed")
    return out


# --- MPAG-001: what a mission partner agreement states (split from SYSD-003) ---------------

def partner_terms(ctx: Context) -> list[RunFinding]:
    """MPAG-001: each mission partner agreement governing a DODIN connection states the terms
    DoDI 8530.01 Encl 4 names: cybersecurity and data protection requirements, DODIN operations
    responsibilities and incident reporting contacts."""
    out: list[RunFinding] = []
    if not _c1_active(ctx) or not ctx.run.path(SD_FILE).is_file():
        return out
    connection = _mapping(facts_mod.get(ctx.facts, "system_type")).get("dodin_connection")
    if connection not in ("direct", "indirect"):
        return out
    for r in _dicts(_mapping(ctx.data(SD_FILE)).get("interconnections")):
        if r.get("partner") == DOD_PARTY:
            continue
        unstated = [t for t in PARTNER_TERMS if t not in _list(r.get("terms"))]
        if unstated:
            out.append(make("MPAG-001", f"{r.get('id')}: the mission partner agreement does "
                            f"not state {', '.join(unstated)}", SD_FILE, None, {WRITER}))
    return out


# --- SYSD-004: user groups ------------------------------------------------------------------

def user_groups(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SYSD-004", message, USERS_FILE, None, {WRITER}))

    if not _c1_active(ctx):
        return out
    for group in _dicts(_mapping(ctx.data(USERS_FILE)).get("users")):
        ident = group.get("id")
        if not group.get("category"):
            err(f"{ident}: the user category is not described")
        if not group.get("access_requirements") \
                and group.get("privilege_level") != "no-logical-access":
            err(f"{ident}: the user access requirements, restrictions and constraints are not "
                "described")
        if group.get("privilege_level") == "privileged":
            if not group.get("roles"):
                err(f"{ident}: privileged users carry no user ID information (role or "
                    "function)")
            held = _mapping(group.get("privileged_access"))
            if held.get("qualified") is not True:
                err(f"{ident}: personnel filling positions with privileged access are not "
                    "qualified")
            if held.get("statement_signed") is not True:
                err(f"{ident}: personnel with privileged access have not signed a Statement of "
                    "Acceptance of Responsibilities")
        if group.get("category") in FOREIGN_GROUPS:
            foreign = _mapping(group.get("foreign_access"))
            if foreign.get("authorized_by") != "dod-component-head":
                err(f"{ident}: access by foreign personnel to the system is authorized by the "
                    f"DoD Component head, not {foreign.get('authorized_by')}")
            if not foreign.get("release_limits"):
                err(f"{ident}: nothing limits foreign access strictly to information cleared "
                    "for release")
    return out


# --- SYSD-005: the agreement behind a consumed IT service ---------------------------------

def consumed_services(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SYSD-005", message, LEVERAGED_FILE, None, {WRITER}))

    if not _c1_active(ctx):
        return out
    for record in _dicts(_mapping(ctx.data(LEVERAGED_FILE)).get("leveraged_authorizations")):
        ident = record.get("id")
        service = record.get("service")
        if not isinstance(service, dict):
            err(f"{ident}: the leveraged authorization names no service and agreement")
            continue
        agreement = _mapping(service.get("agreement"))
        instrument = agreement.get("instrument")
        if service.get("kind") == "internal" and instrument != "sla":
            err(f"{ident}: a service-level agreement is executed for an internal IT service, "
                f"not {instrument}")
        if service.get("kind") == "external" and instrument not in EXTERNAL_INSTRUMENTS:
            err(f"{ident}: an external IT service is held by an interagency agreement or a "
                f"government statement of work, not {instrument}")
        if service.get("kind") == "external" and agreement.get("security_requirements") \
                is not True:
            err(f"{ident}: the agreement for the external service does not incorporate the "
                "security requirements of DoDI 8500.01")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("SYSD-001", system_facts), ("SYSD-002", system_description),
                ("SYSD-003", interconnections), ("MPAG-001", partner_terms),
                ("SYSD-004", user_groups),
                ("SYSD-005", consumed_services), ("SYSD-006", handling_markings))


# --- SYSD-006: handling of vulnerability and configuration detail -------------------------

def handling_markings(ctx: Context) -> list[RunFinding]:
    """DoDI 8530.01 Encl 3 p.(1): a document holding vulnerability information or configuration
    detail is handled at a minimum as CUI. Whether it is handled at the system's classification
    level is for the applicable classification guidance, so a classified system's documents
    are not held to that level here."""
    out: list[RunFinding] = []
    for aid in VULNERABILITY_DOCUMENTS:
        rel = f"artifacts/{aid}.md"
        doc = ctx.docs.get(rel)
        if not scope.produced_or_seeded(ctx.run, aid) or doc is None \
                or not isinstance(doc.data, dict):
            continue
        owner = {ctx.run.artifacts[aid].get("producer")}
        marking = doc.data.get("handling")
        if marking not in MARKINGS:
            out.append(make("SYSD-006", f"{aid} holds vulnerability or configuration detail and "
                            "carries no handling marking", rel, None, owner))
        elif MARKINGS.index(marking) < MARKINGS.index(CUI):
            out.append(make("SYSD-006", f"{aid} is handled as {marking}; vulnerability and "
                            "configuration detail is handled at a minimum as CUI", rel, None,
                            owner))
    return out
