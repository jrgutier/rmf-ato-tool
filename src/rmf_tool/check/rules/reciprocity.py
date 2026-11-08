"""Reciprocity in a run (DoD CIO reciprocity playbook, CNSSI 1254 Annex D, DoDI 8500.01, DoDI
8510.01): RCP-001 on what the Granting side gives each Receiving organization, RCP-002 on how it
coordinates with them and tells them of changes, RCP-003 on the patches and the CSSP it keeps for
them, RCP-004 on what this organization does before it uses a system it receives, RCP-005 on the
authorization to use, RCP-009 on what this organization keeps up after it, RCP-006 on the
agreement between the two sides, RCP-007 on the body of evidence a Receiving AO weighs and on a
refusal and its escalation, and RCP-008 on the registry record.

All of them read ``artifacts/data/reciprocity.yaml`` of ART-SD once ART-SD is produced or seeded.
``receiving_organizations`` lists the organizations this system is deployed into, so the run is
their Granting side; ``received_systems`` lists systems deployed into this one, so the run is
their Receiving side. An empty list means the run has no such relationship, but an authorization
deploying the system at enterprise scope needs a Receiving organization, and an Enterprise system
received in leveraged-authorizations.yaml needs a received-system record. Each rule stays quiet
about a missing or unreadable file (RUN-ART-001 and RUN-FM-001 report those).

Who acts follows the sources: the authorization to use and a refusal are the Receiving AO's
decisions; reviewing the package and passing documents on can go to the AODR. No window is set
where the source states none."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.authorization import business_days_between
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope

FILE = "artifacts/data/reciprocity.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
CHANGES_FILE = "artifacts/data/changes.yaml"
POAM_FILE = "artifacts/poam/items.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
REGISTRATION_FILE = "artifacts/data/registration.yaml"
DISPOSAL_FILE = "artifacts/data/disposal.yaml"
SAR_RESULTS = "artifacts/sar/results"
ARTIFACT = "ART-SD"

Record = dict[str, Any]
Err = Callable[[str], None]

AO = "PER-AO"
AO_OR_DR = frozenset({"PER-AO", "PER-AODR"})
ISO = "PER-PM"  # the information system owner is the PM persona
CISO = "PER-CISO"
EQUIVALENT = "equivalent"
# CNSSI 1254 Annex D 4.a: the documents the deploying organization submits.
PACKAGE = {"ssp": "system security plan", "sar": "security assessment report",
           "rar": "risk assessment report", "poam": "POA&M",
           "authorization-decision": "authorization decision document",
           "deployment-sites": "list of deployment sites and projected deployment dates"}
EVIDENCE = "body-of-evidence"
INSTALLATION = "installation-configuration"
INSTRUCTIONS = "deployment-instructions"
VISIBILITY = ("emass", "other-tool", "manual-inheritance")
AUTOMATED = frozenset({"emass", "other-tool"})
AWARENESS = AUTOMATED | {"manual-inheritance"}  # DoD CIO reciprocity 4.2.1.b.(2).a
RECORD_KEEPING = ("compatible", "incompatible")
OUTCOMES = ("pending", "accepted", "refused")
ORIGINS = ("built-in", "deployment-configured", "inherited", "hybrid")
MANUAL = "manual-inheritance"
REAUTHORIZATION = "reauthorization"
PLAN = "plan"
NOTICE_MONTHS = 6  # DoD CIO reciprocity 4.4.1: at least six months before a reauthorization
STATUS_LEAD_WORKING_DAYS = 60  # CNSSI 1254 Annex D 4.d
REFUSAL_REPORT_BUSINESS_DAYS = 10  # DoD CIO reciprocity section 9
# DoD CIO reciprocity 4.4.1: what the JFHQ-DODIN accredited CSSP maintains.
CSSP_SERVICES = {"continuous-monitoring": "continuous monitoring",
                 "patch-management": "patch management", "iavm": "the IAVM Program",
                 "ess": "End Point Security Services monitoring", "siem": "SIEM monitoring",
                 "operational-orders": "operational orders", "poams": "POA&Ms",
                 "annual-reviews": "annual reviews",
                 "periodic-reviews": "quarterly or monthly reviews"}
ACCREDITOR = "JFHQ-DODIN"
BUILT_IN, CONFIGURED, INHERITED = "built-in", "deployment-configured", "inherited"
RECEIVING = "receiving"
ACCEPTED, REFUSED = "accepted", "refused"
ACCEPTABLE = "acceptable"
AUTHORIZED_CONFIGURATION = "authorized-configuration"
DSAWG = "dsawg"
# DoD CIO reciprocity 4.2.3.f: what the agreement addresses at a minimum.
TOPICS = {"operating-constraints": "operating constraints",
          "operating-environment": "operation environment",
          "monitoring-requirements": "monitoring requirements",
          "security-maintenance": "security maintenance",
          "vulnerability-scanning": "vulnerability scanning",
          "iavm-compliance": "IAVM compliance",
          "lifecycle-replacement": "lifecycle replacement of software and components",
          "roles-responsibilities": "roles and responsibilities"}
# DoD CIO reciprocity 4.3: what an AO Committee's interconnection service agreement defines.
ISA_TOPICS = {"relationships": "the relationships",
              "roles-responsibilities": "roles and responsibilities",
              "boundary-gaps": "steps to address gaps between authorization boundaries",
              "ppsm-coordination": "PPSM coordination",
              "cssp-identification": "CSSP identification",
              "incident-response": "incident response",
              "agreement-review": "agreement review requirements"}
ISA = "isa"
MOU_MOA = frozenset({"mou", "moa"})
PARTIES = frozenset({"granting", "receiving"})
SOFTWARE_DELIVERY = "software-delivery"
SHARING = "package-sharing"
NOTIFY_TO = {"pm": "the PM", "original-ao": "the original AO"}
# DoD CIO reciprocity section 5: what a Receiving AO weighs when the documents DoDI 8510.01
# requires are not available.
BOE_ITEMS = {"poam": "the Enterprise Capability POA&M",
             "residual-risk": "the residual risk assessment of each High or Very High risk "
                              "vulnerability",
             "boundary-diagram": "the authorization boundary diagram",
             "data-flows": "the data-flow, interface and cross-domain diagrams",
             "high-risk-justification": "the impact and technical justification of remaining "
                                        "High or Very High risk vulnerabilities",
             "plans": "the IAVM plan, COOP, Disaster Recovery Plan and incident management plans",
             "hardware-software": "the hardware and software lists with their STIG checklists",
             "test-results": "the validation or verification test results"}
REQUIRED_DOCS = ("ssp", "sar", "rar", "poam", "authorization-decision")
GROUNDS = ("insufficient-content", "excessive-risk")
# DoD CIO reciprocity section 9: the resolution process, in order.
LEVELS = ("ao", "rmf-tag-chair", "ao-council")
UNRESOLVED = "unresolved"
TAG_SECRETARIAT = "rmf-tag-secretariat"
COUNCIL_CHAIR = "DoD CISO"


def _block(record: Any, key: str) -> Record:
    value = record.get(key) if isinstance(record, dict) else None
    return value if isinstance(value, dict) else {}


def _items(record: Any, key: str) -> list[Record]:
    value = record.get(key) if isinstance(record, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _strings(record: Any, key: str) -> list[str]:
    value = record.get(key) if isinstance(record, dict) else None
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _key(value: Any) -> str | None:
    """A value usable as a lookup key; malformed input reads as missing."""
    return value if isinstance(value, str) else None


def _collector(rule: str, task: str) -> tuple[list[RunFinding], Err]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, FILE, None, {task}))

    return out, err


def _data(ctx: Context) -> Record | None:
    """reciprocity.yaml once ART-SD is in play; it is kept up from C-1 onward."""
    if not scope.produced_or_seeded(ctx.run, ARTIFACT):
        return None
    data = ctx.data(FILE)
    return data if isinstance(data, dict) else None


def _months_before(day: dt.date, months: int) -> dt.date:
    """The same day ``months`` earlier, or the month's last day when it has no such day."""
    month = day.month - months
    year = day.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    for back in range(4):
        try:
            return dt.date(year, month, day.day - back)
        except ValueError:
            continue
    return dt.date(year, month, 28)


def _first_deployment(org: Record) -> dt.date | None:
    return min((d for s in _items(org, "sites") if (d := _day(s.get("projected")))),
               default=None)


def _delivered(org: Record) -> dict[str, dt.date | None]:
    """The earliest delivery of each document to a Receiving organization."""
    out: dict[str, dt.date | None] = {}
    for d in _items(org, "deliveries"):
        doc, day = _key(d.get("document")), _day(d.get("date"))
        if doc is None:
            continue
        held = out.get(doc)
        out[doc] = day if held is None or (day is not None and day < held) else held
    return out


def _latest(org: Record, document: str) -> dt.date | None:
    """The latest delivery of one document to a Receiving organization."""
    return max((d for x in _items(org, "deliveries") if x.get("document") == document
                if (d := _day(x.get("date")))), default=None)


def _first_delivery(org: Record) -> dt.date | None:
    return min((d for d in _delivered(org).values() if d is not None), default=None)


def _poam_items(ctx: Context) -> dict[str, Record]:
    return {k: i for i in _items(ctx.data(POAM_FILE), "items") if (k := _key(i.get("id")))}


def _assessed(ctx: Context) -> set[str]:
    """Controls with a determination in the security assessment results."""
    folder = ctx.run.path(SAR_RESULTS)
    out: set[str] = set()
    for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else ():
        for det in _items(ctx.data(f"{SAR_RESULTS}/{path.name}"), "determinations"):
            if control := _key(det.get("control_id")):
                out.add(control)
    return out


def _released(ctx: Context) -> dt.date | None:
    version = ctx.facts.get("system_version") if isinstance(ctx.facts, dict) else None
    return _day(version.get("release_date")) if isinstance(version, dict) else None


# --- RCP-001: what the Granting side gives each Receiving organization -----------------------

def package(ctx: Context) -> list[RunFinding]:
    """RCP-001: each Receiving organization gets the package documents CNSSI 1254 Annex D 4.a
    names, the body of evidence, the installation and configuration requirements with every
    applicable STIG before deployment, the deployment instructions and a current POA&M, and
    continuing visibility through a tool, or manual inheritance where the tools do not match.
    The package also reaches the information owners and the ISO of every interconnected
    system."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-001", "R-1")
    stigs = {k for b in _items(ctx.data(STIG_FILE), "benchmarks") if (k := _key(b.get("id")))}
    # A current POA&M is one delivered on or after its newest item was identified.
    newest = max((d for i in _poam_items(ctx).values()
                  if (d := _day(_block(i, "identified").get("date")))), default=None)
    enterprise = [r.get("id") for r in ctx.ledger or () if isinstance(r, dict)
                  and _block(r, "deployment").get("scope") == "enterprise"]
    co_use = _block(data, "co_use").get("notification_processes")
    if enterprise and not _items(data, "receiving_organizations") and not co_use:
        err(f"{enterprise[0]} deploys the system at enterprise scope, but reciprocity.yaml "
            "names no Receiving organization and no co-use notification processes")
    for org in _items(data, "receiving_organizations"):
        rid = org.get("id")
        delivered = _delivered(org)
        for doc, name in PACKAGE.items():
            if doc not in delivered:
                err(f"{rid}: the {name} is not delivered to the receiving organization")
        if EVIDENCE not in delivered:
            err(f"{rid}: the body of evidence behind the package is not shared with the "
                "receiving organization")
        if INSTRUCTIONS not in delivered:
            err(f"{rid}: the deployment instructions are not provided to the receiving "
                "organization")
        poam = _latest(org, "poam")
        if poam is not None and newest is not None and poam < newest:
            err(f"{rid}: the latest POA&M delivered predates its newest item, so the receiving "
                "organization does not hold a current POA&M")
        first, setup = _first_deployment(org), delivered.get(INSTALLATION)
        if setup is None or (first is not None and setup >= first):
            err(f"{rid}: installation and configuration requirements do not reach the receiving "
                "organization before the system is deployed")
        missing = sorted(stigs - set(_strings(org, "installation_stigs")))
        if missing:
            err(f"{rid}: the installation and configuration requirements leave out the "
                f"applicable STIGs {', '.join(missing)}")
        tool = _block(org, "visibility")
        via = _key(tool.get("via"))
        if via not in VISIBILITY:
            err(f"{rid}: the receiving organization has no continuing visibility of the "
                "security authorization package through eMASS, another tool or manual "
                "inheritance")
        elif tool.get("record_keeping") not in RECORD_KEEPING:
            err(f"{rid}: the receiving organization's record keeping is neither compatible nor "
                "incompatible with this organization's RMF tool")
        elif tool.get("record_keeping") == "incompatible" and via != MANUAL:
            err(f"{rid}: the manual inheritance capability is not used for a receiving "
                "organization whose record keeping system is incompatible")
    sharing = set(_strings(_block(data, "package_sharing"), "shared_with"))
    if "PER-IO" not in sharing:
        err("the security authorization package is not shared with the affected information "
            "owners or stewards")
    for conn in _items(ctx.data(BOUNDARY_FILE), "connections"):
        cid = _key(conn.get("id"))
        if cid and cid not in sharing:
            err(f"the security authorization package is not shared with the ISO of the "
                f"interconnected system behind {cid}")
    return out


# --- RCP-002: coordination with and notices to each Receiving organization -------------------

def coordination(ctx: Context) -> list[RunFinding]:
    """RCP-002: the Granting side gathers requirements from each Receiving organization it knew
    before the system was released, and coordinates them during development; has every
    additional control they ask for assessed; resolves the issues they raised before it deploys
    to them; updates them on its RMF activities and no later than 60 working days before
    deployment; and tells them of every change and new finding after the first delivery, of a
    decommissioning plan, and of each reauthorization at least six months ahead, the in-force
    ATO's termination being the next one, with receipt acknowledged. An organization that joins
    after release, or after a reauthorization's notice was due, is not held to what came before
    it (CNSSI 1254 Annex D 3.b)."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-002", "M-5")
    released = _released(ctx)
    assessed = _assessed(ctx)
    changes = [c for c in _items(ctx.data(CHANGES_FILE), "changes") if _key(c.get("id"))]
    poam = _poam_items(ctx)
    records = [r for r in ctx.ledger or () if isinstance(r, dict)]
    reauthorizations = [r for r in records if r.get("basis") == REAUTHORIZATION]
    effect_of = ledger.effects(ctx.run)
    terminations = sorted({d for s in ledger.in_force(records, effect_of).values()
                           if effect_of.get(s.record.get("decision")) == "authorize"
                           and (d := s.expires) is not None})
    as_of = _day(str(ctx.run.config.get("as_of"))[:10])
    disposal = ctx.data(DISPOSAL_FILE) if scope.produced_or_seeded(ctx.run, "ART-DISP") else None
    for org in _items(data, "receiving_organizations"):
        rid = org.get("id")
        joined = _day(org.get("joined"))
        reqs = _block(org, "requirements")
        known = released is not None and joined is not None and joined < released
        gathered = _day(reqs.get("gathered"))
        if known and (gathered is None or gathered >= released):
            err(f"{rid}: requirements are not gathered from the receiving organization before "
                "the system is released")
        early = min((d for v in _strings(reqs, "coordinated") if (d := _day(v))), default=None)
        if known and (early is None or early >= released):
            err(f"{rid}: security requirements are not coordinated with the receiving "
                "organization during system development")
        for control in _strings(reqs, "additional_controls"):
            if control not in assessed:
                err(f"{rid}: the additional control {control} requested by the receiving "
                    "organization is not addressed by the security control assessment")
        first = _first_deployment(org)
        for issue in _items(org, "issues"):
            raised, resolved = _day(issue.get("raised")), _day(issue.get("resolved"))
            due = first is not None and raised is not None and raised < first
            if (resolved is not None and raised is not None and resolved < raised) or \
                    (due and (resolved is None or resolved > first)):
                err(f"{rid}: the security issue {issue.get('id')} raised by the receiving "
                    "organization is not resolved before the system is deployed to it")
        updates = _items(org, "status_updates")
        if "rmf-activities" not in {_key(u.get("covers")) for u in updates}:
            err(f"{rid}: the receiving organization gets no status update of the RMF "
                "activities")
        earliest = min((d for u in updates if (d := _day(u.get("date")))), default=None)
        if first is not None and (earliest is None or business_days_between(
                earliest, first) < STATUS_LEAD_WORKING_DAYS):
            err(f"{rid}: no status update reaches the receiving organization "
                f"{STATUS_LEAD_WORKING_DAYS} working days before the planned deployment")
        notices = _items(org, "notices")
        _changes_and_findings(org, notices, changes, poam, err)
        _acknowledged(rid, notices, err)
        _reauthorizations(rid, joined, notices, reauthorizations, terminations, as_of, err)
        if isinstance(disposal, dict) and disposal and "decommissioning" not in {
                _key(n.get("plan")) for n in notices if n.get("kind") == PLAN}:
            err(f"{rid}: the plan to decommission the system is not notified to the receiving "
                "organization")
    return out


def _changes_and_findings(org: Record, notices: list[Record], changes: list[Record],
                          poam: dict[str, Record], err: Err) -> None:
    rid, since = org.get("id"), _first_delivery(org)
    told = {(_key(n.get("kind")), _key(n.get("change") or n.get("poam_item"))) for n in notices}
    for change in changes:
        day = _day(change.get("date"))
        if since is not None and day is not None and day >= since \
                and ("change", change["id"]) not in told:
            err(f"{rid}: the change {change['id']} to the system is not communicated to the "
                "receiving organization")
    for pid, item in poam.items():
        day = _day(_block(item, "identified").get("date"))
        if since is not None and day is not None and day >= since and ("finding", pid) not in told:
            err(f"{rid}: the new finding {pid} is not notified to the receiving organization")


def _acknowledged(rid: Any, notices: list[Record], err: Err) -> None:
    for notice in notices:
        kind, day = notice.get("kind"), _day(notice.get("date"))
        if kind in (REAUTHORIZATION, PLAN):
            ack = _day(notice.get("acknowledged"))
            if ack is None or (day is not None and ack < day):
                err(f"{rid}: receipt of the {kind} notice is not acknowledged by the receiving "
                    "organization")


def _reauthorizations(rid: Any, joined: dt.date | None, notices: list[Record],
                      reauthorizations: list[Record], terminations: list[dt.date],
                      as_of: dt.date | None, err: Err) -> None:
    """Each reauthorization the run records, and the in-force ATO's termination once its
    notice is due by the run's as_of date, has a notice at least six months ahead, for an
    organization that was a Receiving organization when the notice fell due."""
    sent = {}
    for n in notices:
        event, day = _day(n.get("event")), _day(n.get("date"))
        if n.get("kind") == REAUTHORIZATION and event is not None and day is not None:
            sent[event] = min(day, sent.get(event, day))
    events = [(d, f"the reauthorization {r.get('id')}") for r in reauthorizations
              if (d := _day(r.get("date")))]
    events += [(d, f"the reauthorization due when the ATO terminates on {d}")
               for d in terminations if as_of is not None and _months_before(d, NOTICE_MONTHS)
               <= as_of]
    for event, what in events:
        due = _months_before(event, NOTICE_MONTHS)
        if joined is not None and joined > due:
            continue
        day = sent.get(event)
        if day is None or day > due:
            err(f"{rid}: {what} is not notified to the receiving organization at least "
                f"{NOTICE_MONTHS} months before the reauthorization event")
    for event, day in sent.items():
        due = _months_before(event, NOTICE_MONTHS)
        if day > due and (joined is None or joined <= due):
            err(f"{rid}: the receiving organization is notified less than "
                f"{NOTICE_MONTHS} months before the reauthorization event")


# --- RCP-003: patches and the CSSP the Granting side keeps for its Receiving organizations ---

def sustainment(ctx: Context) -> list[RunFinding]:
    """RCP-003: with a Receiving organization, the Granting side provides each patch or update
    within the DoD and USCYBERCOM timeline that directs it and communicates it to every
    Receiving organization, and assigns a JFHQ-DODIN accredited CSSP that maintains the
    services the playbook names."""
    data = _data(ctx)
    if data is None:
        return []
    orgs = {k for o in _items(data, "receiving_organizations") if (k := _key(o.get("id")))}
    if not orgs:
        return []
    out, err = _collector("RCP-003", "S-5")
    granting = _block(data, "granting")
    patches = _items(granting, "patches")
    for patch in patches:
        pid = patch.get("id")
        due, provided = _day(patch.get("required_by")), _day(patch.get("provided"))
        if provided is None or (due is not None and provided > due):
            err(f"{pid}: the patch is not provided within the DoD and USCYBERCOM timeline")
        for org in sorted(orgs - set(_strings(patch, "communicated_to"))):
            err(f"{pid}: the patch is not communicated to the receiving organization {org}")
    directed = {_key(p.get("directed_action")) for p in patches}
    since = min((d for o in _items(data, "receiving_organizations")
                 if (d := _first_delivery(o))), default=None)
    for action in _items(ctx.data(POAM_FILE), "directed_actions"):
        received = _day(action.get("received"))
        if action.get("response") == "implemented" and _key(action.get("id")) not in directed \
                and since is not None and received is not None and received >= since:
            err(f"the patch or update for {action.get('id')} is not provided to the receiving "
                "organizations")
    cssp = _block(granting, "cssp")
    if cssp.get("accredited_by") != ACCREDITOR:
        err("the CSSP assigned to the system is not JFHQ-DODIN accredited")
    for key, name in CSSP_SERVICES.items():
        if key not in _strings(cssp, "services"):
            err(f"the CSSP assigned does not maintain {name}")
    return out


# --- RCP-004: what this organization does before it uses a system it receives ---------------

def receiving_review(ctx: Context) -> list[RunFinding]:
    """RCP-004: for each system it receives, this organization keeps aware of the Granting
    system's assessment through a tool, requests the package, deployment instructions and a
    current POA&M, makes its own package available, reviews the Granting AO's decision and the
    deployment guide, determines the impact of connecting it (through its DSAWG representative
    for an Enterprise system) and implements augmenting controls before it decides, and tests
    by origin: built-in controls not re-tested, controls configured at deployment tested by the
    receiving side, inherited controls validated by the receiving ISO with evidence."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-004", "A-2")
    received = _items(data, "received_systems")
    links = _enterprise_links(ctx)
    linked = {_key(r.get("leveraged")) for r in received}
    for la in sorted(links - linked):
        err(f"{la}: the Enterprise system received has no received-system record in "
            "reciprocity.yaml")
    for system in received:
        sid = system.get("id")
        outcome = system.get("outcome")
        if outcome not in OUTCOMES:
            err(f"{sid}: the outcome of the received system is not pending, accepted or "
                "refused")
            continue
        if _key(system.get("leveraged")) in links and system.get("enterprise") is not True:
            err(f"{sid}: the received system links an Enterprise system in "
                "leveraged-authorizations.yaml but is not recorded as one")
        _tests(sid, system, err)
        if outcome == "pending":
            continue
        decided = _decided(system)
        review = _block(system, "review")
        reviewed = _day(review.get("date"))
        if _key(review.get("by")) not in AO_OR_DR or reviewed is None \
                or (decided is not None and reviewed > decided):
            err(f"{sid}: the Granting AO's authorization decision and package are not reviewed "
                "by the Receiving AO before the decision")
        vias = {_key(a.get("via")) for a in _items(system, "awareness")}
        if AWARENESS.isdisjoint(vias):
            err(f"{sid}: situational awareness of the Granting system's assessment activities "
                "is not kept through eMASS, another automated tool or manual inheritance")
        pkg = _block(system, "package")
        asked = set(_strings(pkg, "requested_documents"))
        for doc in sorted({*REQUIRED_DOCS, INSTRUCTIONS} - asked):
            err(f"{sid}: the Granting organization is not asked for the {doc}")
        if outcome == REFUSED:
            continue
        shared = _day(system.get("own_package_shared"))
        if shared is None or (decided is not None and shared > decided):
            err(f"{sid}: the receiving system's security authorization package is not made "
                "available to the Granting organization")
        guide = _day(system.get("guide_reviewed"))
        if guide is None or (decided is not None and guide > decided):
            err(f"{sid}: the controls and the deployment guide are not reviewed against the "
                "local security posture before the system is deployed")
        impact = _block(system, "impact")
        determined = _day(impact.get("determined"))
        if determined is None or (decided is not None and determined > decided):
            err(f"{sid}: the security impact of connecting the Granting system is not "
                "determined before the decision")
        if _is_enterprise(system, links) and impact.get("via") != DSAWG:
            err(f"{sid}: issues that may preclude connecting the Enterprise system are not "
                "identified through the DSAWG representative")
        deployed = _deployed(system)
        for aug in _items(impact, "augmenting_controls"):
            done = _day(aug.get("implemented"))
            if done is None or (deployed is not None and done > deployed):
                err(f"{sid}: the augmenting control {aug.get('control')} required to deploy "
                    "the system is not implemented by the time it is deployed")
    return out


def _enterprise_links(ctx: Context) -> set[str]:
    """Leveraged authorizations that record an Enterprise system this organization receives."""
    return {k for la in _items(ctx.data(LEVERAGED_FILE), "leveraged_authorizations")
            if la.get("enterprise") and (k := _key(la.get("id")))}


def _is_enterprise(system: Record, links: set[str]) -> bool:
    return system.get("enterprise") is True or _key(system.get("leveraged")) in links


def _deployed(system: Record) -> dt.date | None:
    """The day the received system was installed in this one."""
    return _day(_block(system, "installation").get("implemented"))


def _decided(system: Record) -> dt.date | None:
    """The day the Receiving AO decided: the authorization to use, or the refusal."""
    return _day(_block(system, "atu").get("issued")) or \
        _day(_block(system, "refusal").get("documented"))


def _tests(sid: Any, system: Record, err: Err) -> None:
    for control in _items(system, "controls"):
        cid, origin = control.get("control"), control.get("origin")
        if origin == BUILT_IN and control.get("retested") is True:
            err(f"{sid}: the built-in control {cid} is re-tested though it does not change "
                "when the system is deployed")
        elif origin == CONFIGURED and control.get("tested_by") != RECEIVING:
            err(f"{sid}: the control {cid} configured at deployment is not tested by the "
                "receiving system owner")
        elif origin not in ORIGINS:
            err(f"{sid}: the control {cid} is neither built in, configured at deployment, "
                "inherited nor hybrid")
        tested, deployed = _day(control.get("tested")), _deployed(system)
        if origin == CONFIGURED and (tested is None or (deployed is not None
                                                         and tested < deployed)):
            err(f"{sid}: the control {cid} configured at deployment is not tested once it is "
                "configured on deployment")
        elif origin == INHERITED and control.get("validated_by") != ISO:
            err(f"{sid}: the inherited control {cid} is not validated by the receiving system "
                "ISO")
        evidence = control.get("evidence")
        if origin == INHERITED and not evidence:
            err(f"{sid}: no supporting documentation or artifact is developed for the inherited "
                f"control {cid}")
        if origin == "hybrid" and control.get("established_by") != RECEIVING:
            err(f"{sid}: inheritance for the hybrid control {cid} is not established by the "
                f"receiving organization, but {control.get('established_by')}")
        elif origin == "hybrid" and not evidence:
            err(f"{sid}: no supporting evidence supports the implementation of the hybrid control "
                f"{cid} within the receiving system")


# --- RCP-005: the authorization to use and what follows it ----------------------------------

def authorization_to_use(ctx: Context) -> list[RunFinding]:
    """RCP-005: a system this organization accepts gets an authorization to use issued by the
    Receiving AO on an acceptable risk, a copy to the Granting AO, notice to subordinate sites
    limited to the authorized configuration, an update of the hosting system's authorization
    documentation in the change log with the added controls and the installation documents
    and difference tests, the installation guide implemented after it is received, and the
    inherited controls provided."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-005", "I-2")
    changes = {k for c in _items(ctx.data(CHANGES_FILE), "changes") if (k := _key(c.get("id")))}
    links = _enterprise_links(ctx)
    for system in _items(data, "received_systems"):
        sid = system.get("id")
        if _is_enterprise(system, links) and system.get("coordination_point") != CISO:
            err(f"{sid}: the Component CISO is not the single cybersecurity coordination point "
                "for the DoD-wide program deploying the system")
        if system.get("outcome") != ACCEPTED:
            continue
        atu = _block(system, "atu")
        issued = _day(atu.get("issued"))
        if atu.get("by") != AO or issued is None:
            err(f"{sid}: no authorization to use or connect is issued by the Receiving AO")
        if atu.get("risk") != ACCEPTABLE:
            err(f"{sid}: the authorization to use does not rest on a determination that the "
                "risk to the receiving system is acceptable")
        copy = _day(atu.get("copy_to_granting_ao"))
        if copy is None or (issued is not None and copy < issued):
            err(f"{sid}: a copy of the authorization to use is not provided to the Granting AO")
        sites = _block(atu, "sites_notified")
        notified = _day(sites.get("date"))
        if sites.get("scope") != AUTHORIZED_CONFIGURATION or notified is None \
                or (issued is not None and notified < issued):
            err(f"{sid}: subordinate sites are not notified that the system may operate only in "
                "the authorized configuration")
        _hosting(sid, system, changes, err)
    return out


def _hosting(sid: Any, system: Record, changes: set[str], err: Err) -> None:
    update = _block(system, "hosting_update")
    if _key(update.get("change")) not in changes:
        err(f"{sid}: the hosting system's authorization and connection documentation is not "
            "updated through the change log to incorporate the system")
    augmenting = _items(_block(system, "impact"), "augmenting_controls")
    added = {_key(a.get("control")) for a in augmenting}
    for control in sorted(c for c in added - set(_strings(update, "controls")) if c):
        err(f"{sid}: the hosting system's authorization does not include the added control "
            f"{control}")
    install = _block(system, "installation")
    # Difference tests are needed only where the receiving environment differs.
    needed = {INSTALLATION} | ({"difference-tests"} if _items(install, "differences") else set())
    for doc in sorted(needed - set(_strings(update, "documents"))):
        err(f"{sid}: the updated authorization documentation leaves out the {doc} documents")
    implemented = _day(install.get("implemented"))
    received = _day(_block(system, "package").get("received"))
    if implemented is None or (received is not None and implemented < received):
        err(f"{sid}: the installation guide and security configuration requirements are not "
            "implemented after they are received")
    for diff in _items(install, "differences"):
        tested = diff.get("tested")
        if not tested:
            err(f"{sid}: the configuration difference {diff.get('item')} is not tested")
    inherited = {_key(c.get("control")) for c in _items(system, "controls")
                 if c.get("origin") == INHERITED}
    for control in sorted(c for c in inherited - set(_strings(system, "provided_controls")) if c):
        err(f"{sid}: the inherited control {control} required by the reciprocity authorization "
            "is not provided by the receiving organization")


# --- RCP-009: what this organization keeps up for a system it accepted --------------------

def after_fielding(ctx: Context) -> list[RunFinding]:
    """RCP-009: once a received system is accepted, this organization implements each
    mitigation of the Granting POA&M, applies patches by the PM's date, applies each IAVA and
    STIG released or tracks it in a POA&M item, and reports each new finding back to the
    Granting organization once it is identified."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-009", "M-3")
    poam = _poam_items(ctx)
    for system in _items(data, "received_systems"):
        if system.get("outcome") == ACCEPTED:
            _after_fielding(system.get("id"), system, poam, err)
    return out


def _after_fielding(sid: Any, system: Record, poam: dict[str, Record], err: Err) -> None:
    mitigated = {_key(m.get("poam_item")): _day(m.get("implemented"))
                 for m in _items(system, "mitigations")}
    for item in _strings(_block(system, "package"), "poam_items"):
        if mitigated.get(item) is None:
            err(f"{sid}: the mitigation in the Granting POA&M item {item} is not implemented")
    for patch in _items(system, "patches"):
        due, applied = _day(patch.get("pm_due")), _day(patch.get("applied"))
        if applied is None or (due is not None and applied > due):
            err(f"{sid}: the patch {patch.get('id')} is not implemented in accordance with PM "
                "guidance")
    for update in _items(system, "configuration_updates"):
        outcome = update.get("outcome")
        if outcome == "poam" and _key(update.get("poam_item")) not in poam:
            err(f"{sid}: the {update.get('kind')} {update.get('id')} that cannot be applied is "
                "not tracked in the POA&M")
        elif outcome not in ("applied", "poam"):
            err(f"{sid}: the {update.get('kind')} {update.get('id')} is neither applied nor "
                "tracked in the POA&M")
    for finding in _items(system, "findings"):
        pid, day = finding.get("poam_item"), _day(finding.get("reported"))
        item = poam.get(_key(pid) or "")
        found = _day(_block(item, "identified").get("date"))
        if item is None or day is None or (found is not None and day < found):
            err(f"{sid}: the new finding {pid} is not reported to the Granting organization "
                "once it is identified")


# --- RCP-006: the agreement between the Granting and the Receiving organization ------------

def agreements(ctx: Context) -> list[RunFinding]:
    """RCP-006: each relationship rests on an executed MOU, MOA, SLA or ISA that addresses the
    minimum topics (an ISA what an AO Committee defines), covers sharing the package, names a
    point of contact on this side and a technical POC on each side, sets the notification
    processes, timing and requirements to the PM and original AO, identifies termination
    factors of an MOU or MOA, documents each pre-agreement task with its responsible
    organization, resolves deviations to both sides' satisfaction, agrees the core documents,
    and for a software factory passes software across and feedback back."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-006", "C-1")
    agreements_by_id = {k: a for a in _items(data, "agreements") if (k := _key(a.get("id")))}
    core = {aid for aid, a in ctx.run.artifacts.items() if a.get("package") == "core"}
    sides = [(o, "granting") for o in _items(data, "receiving_organizations")] + \
            [(s, "receiving") for s in _items(data, "received_systems")
             if s.get("outcome") == ACCEPTED]
    for party, side in sides:
        pid = party.get("id")
        agreement = agreements_by_id.get(_key(party.get("agreement")) or "")
        if agreement is None or _day(agreement.get("executed")) is None:
            err(f"{pid}: no documented agreement with the other organization is executed")
            continue
        aid = agreement.get("id")
        decided = _decided(party)
        if side == RECEIVING and decided is not None \
                and (_day(agreement.get("executed")) or decided) > decided:
            err(f"{aid}: the agreement is executed after the Receiving AO's decision")
        _terms(aid, agreement, side, ctx, err)
        _content(aid, agreement, core, err)
        if party.get("kind") == SOFTWARE_DELIVERY:
            covers = set(_strings(agreement, "covers"))
            if SOFTWARE_DELIVERY not in covers:
                err(f"{aid}: the agreement does not pass software across the authorization "
                    "boundary")
            if "feedback" not in covers:
                err(f"{aid}: the agreement does not pass results and feedback back to the "
                    "software factory")
    return out


def _terms(aid: Any, agreement: Record, side: str, ctx: Context, err: Err) -> None:
    instrument = agreement.get("instrument")
    topics = set(_strings(agreement, "topics"))
    for key, name in TOPICS.items():
        if key not in topics:
            err(f"{aid}: the agreement does not address {name}")
    if instrument == ISA:
        for key, name in ISA_TOPICS.items():
            if key not in topics:
                err(f"{aid}: the interconnection service agreement does not define {name}")
    if SHARING not in _strings(agreement, "covers"):
        err(f"{aid}: the sharing of the authorization package is not under terms agreed by "
            "both parties")
    pocs = _block(agreement, "pocs")
    own = "granting" if side == "granting" else RECEIVING
    if _key(pocs.get(own)) not in ctx.run.personas:
        err(f"{aid}: the single point of contact this organization provides to the other is "
            "no role of the run")
    technical = {_key(t.get("party")) for t in _items(pocs, "technical")}
    for party in sorted(PARTIES - technical):
        err(f"{aid}: the agreement identifies no technical POC of the {party} organization")
    notification = _block(agreement, "notification")
    for part in ("processes", "timing", "requirements"):
        if not notification.get(part):
            err(f"{aid}: the agreement does not include the notification {part}")
    for who, name in NOTIFY_TO.items():
        if who not in _strings(notification, "recipients"):
            err(f"{aid}: events that may affect the security posture are not communicated to "
                f"{name}")
    factors = agreement.get("termination_factors")
    if _key(instrument) in MOU_MOA and not factors:
        err(f"{aid}: the factors or conditions justifying termination of the MOU/MOA are not "
            "identified")


def _content(aid: Any, agreement: Record, core: set[str], err: Err) -> None:
    executed = _day(agreement.get("executed"))
    tasks = _items(agreement, "pre_agreement_tasks")
    if not tasks:
        err(f"{aid}: no task completed before entering into the agreement is recorded")
    for task in tasks:
        done = _day(task.get("completed"))
        if task.get("responsible") not in (*PARTIES, "both"):
            err(f"{aid}: the pre-agreement task {task.get('task')} has no responsible "
                "organization documented")
        if done is None or (executed is not None and done > executed):
            err(f"{aid}: the pre-agreement task {task.get('task')} is not completed before the "
                "agreement")
    for dev in _items(agreement, "deviations"):
        accepted = set(_strings(dev, "accepted_by"))
        if _day(dev.get("resolved")) is None or PARTIES - accepted:
            err(f"{aid}: the deviation from the data element {dev.get('element')} is not "
                "resolved to both organizations' satisfaction")
    documents = _strings(agreement, "documents")
    for doc in documents:
        if doc not in core:
            err(f"{aid}: {doc}, agreed as required, is not an RMF core document")
    if not documents:
        err(f"{aid}: the organizations do not agree which RMF core documents are required")


# --- RCP-007: the body of evidence a Receiving AO weighs, and a refusal -------------------

def evidence_and_refusal(ctx: Context) -> list[RunFinding]:
    """RCP-007: when the documents DoDI 8510.01 requires are not all received, the Receiving AO
    weighs every item of the body of evidence the playbook names, and requests beyond the
    package are endorsed by the requesting Component CISO before they are forwarded. A refusal
    is the Receiving AO's, on one of the two grounds, documented and reported to the Granting AO
    within 10 business days, given to whoever asks, and escalated from the AO level to the RMF
    TAG Chair through its Secretariat and then to the AO Council chaired by the DoD CISO, a
    level being left only unresolved."""
    data = _data(ctx)
    if data is None:
        return []
    out, err = _collector("RCP-007", "R-4")
    for system in _items(data, "received_systems"):
        sid = system.get("id")
        got = set(_strings(_block(system, "package"), "received_documents"))
        boe = _block(system, "body_of_evidence")
        if system.get("outcome") in (ACCEPTED, REFUSED) and set(REQUIRED_DOCS) - got:
            weighed = {_key(i.get("item")) for i in _items(boe, "considered")
                       if i.get("status") in ("considered", "unavailable")}
            for key, name in BOE_ITEMS.items():
                if key not in weighed:
                    err(f"{sid}: the body of evidence considered leaves out {name}")
        for req in _items(boe, "requests"):
            endorsed, forwarded = _day(req.get("endorsed")), _day(req.get("forwarded"))
            equivalent = _block(req, "equivalent")
            # "the requesting Component CISO, or equivalent": an equivalent names its title
            # and the authority it endorses under.
            endorser = CISO if req.get("endorsed_by") == CISO else (
                EQUIVALENT if req.get("endorsed_by") == EQUIVALENT and equivalent.get("title")
                and equivalent.get("authority") else None)
            if endorser not in (CISO, EQUIVALENT) or endorsed is None \
                    or (forwarded is not None and forwarded < endorsed):
                err(f"{sid}: the request for {req.get('document')} beyond the package is not "
                    "endorsed by the requesting Component CISO before it is forwarded")
        if system.get("outcome") == REFUSED:
            _refusal(sid, _block(system, "refusal"), err)
    return out


def _refusal(sid: Any, refusal: Record, err: Err) -> None:
    documented = _day(refusal.get("documented"))
    if refusal.get("decided_by") != AO or documented is None:
        err(f"{sid}: the refusal to participate in reciprocity is not documented by the "
            "refusing AO")
    if refusal.get("grounds") not in GROUNDS:
        err(f"{sid}: the refusal rests neither on insufficient content nor on excessive risk")
    reported = _day(refusal.get("reported_to_granting_ao"))
    if reported is None or (documented is not None and business_days_between(
            documented, reported) > REFUSAL_REPORT_BUSINESS_DAYS):
        err(f"{sid}: the refusal is not reported to the Granting organization's AO within "
            f"{REFUSAL_REPORT_BUSINESS_DAYS} business days")
    for req in _items(refusal, "requests"):
        asked, given = _day(req.get("requested")), _day(req.get("provided"))
        if given is None or (asked is not None and given < asked):
            err(f"{sid}: the documented refusal is not provided to {req.get('by')} on request")
    steps = _items(refusal, "escalation")
    levels = tuple(s.get("level") for s in steps)
    if levels != LEVELS[:len(levels)]:
        err(f"{sid}: the dispute is not raised from the AO level to the RMF TAG Chair and then "
            "to the AO Council, in that order")
    for step, after in zip(steps, steps[1:], strict=False):
        if step.get("result") != UNRESOLVED:
            err(f"{sid}: the dispute is raised to {after.get('level')} though it was resolved "
                f"at {step.get('level')}")
    for step in steps:
        if step.get("level") == "rmf-tag-chair" and step.get("notified") != TAG_SECRETARIAT:
            err(f"{sid}: the RMF TAG Secretariat is not notified before the RMF TAG Chair "
                "mediates")
        if step.get("level") == "ao-council" and step.get("chair") != COUNCIL_CHAIR:
            err(f"{sid}: the AO Council hearing the dispute is not chaired by the DoD CISO")
    if steps and steps[-1].get("result") == UNRESOLVED and steps[-1].get("level") != LEVELS[-1]:
        err(f"{sid}: the dispute unresolved at {steps[-1].get('level')} is not raised to the "
            "next level")


# --- RCP-008: the registry record ------------------------------------------------------------

def registry(ctx: Context) -> list[RunFinding]:
    """RCP-008: the registry record of a system deployed to Receiving organizations holds every
    deployment location, and is updated after each system this organization accepts; a system
    opted out of reciprocity listing carries its exemption justification."""
    data = _data(ctx)
    if data is None or "P-18" not in scope.active_tasks(ctx.run):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RCP-008", message, REGISTRATION_FILE, None, {"P-18"}))

    record = _block(ctx.data(REGISTRATION_FILE), "registry")
    locations = set(_strings(record, "deployment_locations"))
    for org in _items(data, "receiving_organizations"):
        for site in _items(org, "sites"):
            if _key(site.get("site")) and site["site"] not in locations:
                err(f"the deployment location {site['site']} is not maintained in the "
                    "authorization tracking tool")
    for system in _items(data, "received_systems"):
        issued = _day(_block(system, "atu").get("issued"))
        latest = max((d for u in _items(record, "updates")
                      if u.get("received_system") == system.get("id")
                      and (d := _day(u.get("date")))), default=None)
        if system.get("outcome") == ACCEPTED and issued is not None \
                and (latest is None or latest < issued):
            err(f"{system.get('id')}: the authorization tracking tool is not updated after the "
                "system is accepted")
    listing = _block(record, "reciprocity")
    if listing.get("listed") is False and not listing.get("exemption_justification"):
        err("the system is deselected from reciprocity listing without an exemption "
            "justification")
    return out


RULES = {
    "RCP-001": package,
    "RCP-002": coordination,
    "RCP-003": sustainment,
    "RCP-004": receiving_review,
    "RCP-005": authorization_to_use,
    "RCP-006": agreements,
    "RCP-007": evidence_and_refusal,
    "RCP-008": registry,
    "RCP-009": after_fielding,
}
