"""The plan records S-4 writes beside the security, CM, contingency and incident response plans:
CMPL-*, CPLAN-*, IRPT-*, SVCA-*, SSPR-*, FUND-*, CRYP-* and TELE-*. Each record is a data file,
so these rules judge values, not headings. A rule is quiet while its artifact is out of play,
and says so when the artifact is in play and the record is missing.

A classified system is read from the Classified System Overlay in facts.yaml. A space NSS is
`space_nss` in ssp-records.yaml or the Space Platform Overlay, because that overlay is not
transcribed yet and FACTS-001 refuses it, so the field carries a run until it is; a space-system
issue in the ledger says the same whatever the field says.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.check import providers
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.consistency import POAM_FILE
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.run import authorization as ledger
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

CM_FILE = "artifacts/data/cm-plan.yaml"
CP_FILE = "artifacts/data/contingency.yaml"
IR_FILE = "artifacts/data/incident-response.yaml"
SVC_FILE = "artifacts/data/service-agreements.yaml"
SSP_FILE = "artifacts/data/ssp-records.yaml"
INVENTORY_FILE = "artifacts/data/inventory.yaml"

CLASSIFIED_OVERLAY = "CNSSI1253E-ATT5-CLASSIFIED"
SPACE_OVERLAY = "CNSSI1253F-ATT2-SPACE"
NSA = "NSA"
CNSSP_15 = "CNSSP 15"
SP_800_114 = "NIST SP 800-114"
DOD_CIO = "DoD CIO"
ANNUAL_REVIEW_DAYS = 365
ESSENTIAL_MTD_HOURS = 12  # SP 800-34r1 3.2.1 under FCD-1
EXERCISE_RANK = {"tabletop": 1, "functional": 2, "full-scale": 3}
REQUIRED_RANK = {"low": 1, "moderate": 2, "high": 3}  # SP 800-34r1 3.5.4
TOTAL_LOSS = "all-information-resources-and-connectivity"
DOD_FUND_PURPOSES = ("implementation", "assessment", "sustainment", "configuration-management",
                     "vulnerability-management")
SPACE_FUND_PURPOSES = ("acquisition", "implementation", "sustainment", "decommission")
OPERATIONS_PHASE = "PH-OS"
INSTRUMENTS = ("dod-component-policy", "dod-component-issuance", "support-agreement", "moa",
               "contract", "sla")
# DoDI 8530.01 Reference (p), DoD O-8530.01-M, and the Evaluator's Scoring Metrics under it.
CSSP_SCHEMES = ("DoD O-8530.01-M", "evaluator-scoring-metrics")
VALIDATION_COVERS = ("roles", "responsibilities", "scope", "applicability")
SUBSCRIBERS = ("PER-ISSM", "PER-ISSO", "PER-PM", "PER-IO")  # the side that owns the system
STATUS_OF = {"AD-ATO": "ATO", "AD-ATOC": "ATO-with-conditions", "AD-IATT": "IATT"}
NO_DECISION, DENIED = "none", "DATO"
CATO_EFFECT = "continuous"
VOL_3, VOL_4 = "DoDM 5200.01 Volume 3", "DoDM 5200.01 Volume 4"
NISP_MANUAL = "DoD 5220.22-M"
CNSSI_1010 = "CNSSI 1010"
PRIVACY_REG = "DoD 5400.11-R"  # loss or unauthorized disclosure of PII (DoDI 8500.01 p. 22)
Check = Callable[[str], None]


def _in_play(ctx: Context, rule: str, artifact: str, rel: str,
             owner: str = "S-4") -> tuple[dict[str, Any] | None, list[RunFinding], Check]:
    """The record, the findings so far and an error helper. A missing record is a finding once
    its artifact is in play; an unreadable one is RUN-FM-001's."""
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, rel, None, {owner}))

    if not scope.produced_or_seeded(ctx.run, artifact):
        return None, out, err
    if not ctx.run.path(rel).is_file():
        err(f"{rel} is missing; {owner} writes it")
        return None, out, err
    data = ctx.data(rel)
    return (data if isinstance(data, dict) else None), out, err


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def _overlays(ctx: Context) -> list[str]:
    cat = facts_mod.get(ctx.facts, "categorization")
    return list(cat.get("overlays") or ()) if isinstance(cat, dict) else []


def _availability(ctx: Context) -> str | None:
    cat = facts_mod.get(ctx.facts, "categorization")
    return cat.get("a") if isinstance(cat, dict) else None


def _space(ctx: Context, data: dict[str, Any] | None = None) -> bool:
    records = data if data is not None else ctx.data(SSP_FILE)
    declared = isinstance(records, dict) and records.get("space_nss") is True
    book = ctx.data(ledger.LEDGER_FILE)
    issues = book.get("issues") if isinstance(book, dict) else None
    forum_says = "space-system" in [i.get("kind") for i in _dicts(issues)]
    return declared or forum_says or SPACE_OVERLAY in _overlays(ctx)


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _hours(value: Any) -> float:
    return float(value) if isinstance(value, int | float) else 0.0


def _poam_ids(ctx: Context) -> set[str]:
    data = ctx.data(POAM_FILE)
    items = data.get("items") if isinstance(data, dict) else None
    return {str(i.get("id")) for i in _dicts(items)}


# --- CM plan ----------------------------------------------------------------------------

def ci_register(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CMPL-001", "ART-CMP", CM_FILE)
    if data is None:
        return out
    items = _dicts(data.get("configuration_items"))
    ids = [str(ci.get("id")) for ci in items]
    for ident in sorted({i for i in ids if ids.count(i) > 1}):
        err(f"configuration item identifier {ident} is not unambiguous")
    if "seccm-tools" not in [ci.get("kind") for ci in items]:
        err("no configuration item puts the SecCM tools and testing processes under control")
    inventory = ctx.data(INVENTORY_FILE)
    held = [i for ci in items for i in ci.get("inventory_items") or ()]
    for item in _dicts(inventory.get("items") if isinstance(inventory, dict) else None):
        count = held.count(item.get("id"))
        if count == 0 or count > 1:
            err(f"inventory item {item.get('id')} sits in {count} configuration items, "
                "and belongs to one and only one")
    return out


def cm_tools(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CMPL-002", "ART-CMP", CM_FILE)
    if data is None:
        return out
    for tool in _dicts(data.get("tools")):
        if tool.get("scap") == "not-validated":
            err(f"automated tool {tool.get('name')} is not SCAP-validated although a validated "
                "tool is available")
    inventory = ctx.data(INVENTORY_FILE)
    known = {i.get("id") for i in _dicts(inventory.get("items")
                                         if isinstance(inventory, dict) else None)}
    for entry in _dicts(data.get("manual_monitoring")):
        if entry.get("inventory_item") not in known:
            err(f"manual monitoring names {entry.get('inventory_item')}, which is no inventory "
                "item")
    return out


# --- contingency plan -------------------------------------------------------------------

def bypasses(ctx: Context) -> list[RunFinding]:
    """BYP-001: a cybersecurity mechanism is bypassed only on a procedure coordinated with the
    ISSO and approved in writing by the ISSM (DoDI 8500.01 Encl 3.21.g); cm-plan.yaml bypasses
    records each one, and none is the user's own unilateral act."""
    data, out, err = _in_play(ctx, "BYP-001", "ART-CMP", CM_FILE)
    if data is None:
        return out
    for item in _dicts(data.get("bypasses")):
        bid = item.get("id")
        if "PER-ISSO" not in (item.get("coordinated_with") or []):
            err(f"{bid}: the bypass procedure is not coordinated with the ISSO")
        approval = item.get("approval") if isinstance(item.get("approval"), dict) else {}
        if approval.get("by") != "PER-ISSM" or approval.get("form") != "written":
            err(f"{bid}: the bypass has no written approval from the ISSM (approved by "
                f"{approval.get('by')}, {approval.get('form')})")
    return out


def bia_times(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CPLAN-001", "ART-CP", CP_FILE)
    if data is None:
        return out
    bia = data.get("bia") if isinstance(data.get("bia"), dict) else {}
    strategy = data.get("strategy") if isinstance(data.get("strategy"), dict) else {}
    gaps = {g.get("process"): g.get("poam_item") for g in _dicts(strategy.get("rto_gaps"))}
    # an RTO not yet proven names the exercise that will prove it until A-6 writes the
    # POA&M, and a POA&M item from then on (F-09-5)
    unproven = {g.get("process") for g in _dicts(strategy.get("rto_gaps"))
                if g.get("unproven") is True}
    posted = "A-6" in scope.active_tasks(ctx.run)
    poam = _poam_ids(ctx)
    for process in _dicts(bia.get("processes")):
        ident, mtd = process.get("id"), _hours(process.get("mtd_hours"))
        if process.get("essential_function") in ("MEF", "PMEF", "NEF") \
                and mtd > ESSENTIAL_MTD_HOURS:
            err(f"{ident} supports an essential function, and its maximum tolerable downtime of "
                f"{mtd:g} hours is over 12 hours")
        total = _hours(process.get("rto_hours")) + _hours(process.get("reprocessing_hours"))
        if ident in unproven and posted and gaps.get(ident) not in poam:
            err(f"{ident}: the recovery time objective is not yet proven, and from A-6 a Plan "
                "of Action and Milestone item documents the gap")
        if total > mtd and gaps.get(ident) not in poam and not (ident in unproven
                                                                 and not posted):
            err(f"{ident}: the recovery time objective plus reprocessing time is {total:g} hours, "
                f"over the maximum tolerable downtime of {mtd:g}, and no Plan of Action and "
                "Milestone item documents the gap")
    return out


def exercise_depth(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CPLAN-002", "ART-CP", CP_FILE)
    if data is None:
        return out
    exercises = _dicts(data.get("exercises"))
    ranks = [EXERCISE_RANK.get(str(e.get("type")), 0) for e in exercises]
    availability = _availability(ctx)
    if (max(ranks, default=0)) < REQUIRED_RANK.get(str(availability), 0):
        if availability == "moderate":
            err("a moderate-impact system needs a functional exercise, not a tabletop")
        else:
            err(f"a {availability}-impact system needs an exercise of its depth")
    if availability == "high" and not any(e.get("type") == "full-scale"
                                          and e.get("failover") is True for e in exercises):
        err("a high-impact system exercises a failover to the alternate location")
    return out


def operational_resilience(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CPLAN-003", "ART-CP", CP_FILE)
    if data is None:
        return out
    exercises = _dicts(data.get("exercises"))
    realistic = [e for e in exercises if "realistic-cyber" in (e.get("conditions") or ())]
    if len(realistic) < 1:
        err("no exercise is held under realistic cyber conditions")
    for e in realistic:
        missing = {"work-arounds", "fall-backs"} - set(e.get("tests") or ())
        if missing:
            err(f"{e.get('id')} is held under realistic cyber conditions and does not test "
                "work-arounds and fall-backs")
    if TOTAL_LOSS not in [e.get("loss") for e in exercises]:
        err("no periodic exercise or evaluation tests operating during loss of all information "
            "resources and connectivity")
    strategy = data.get("strategy") if isinstance(data.get("strategy"), dict) else {}
    allocation = strategy.get("dynamic_allocation")
    proved_by = allocation.get("proved_by") if isinstance(allocation, dict) else None
    if proved_by not in [e.get("id") for e in exercises]:
        err(f"allocating information resources dynamically rests on {proved_by}, which is no "
            "exercise of this plan")
    elif "A-3" in scope.active_tasks(ctx.run) and not any(
            e.get("id") == proved_by and e.get("held_on") for e in exercises):
        # a planned exercise proves nothing; by the assessment it has been held (F-09-5)
        err(f"allocating information resources dynamically rests on {proved_by}, which has "
            "not been held (no held_on)")
    return out


# --- incident response plan -------------------------------------------------------------

def _paths(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(p.get("case")): p for p in _dicts(data.get("reporting_paths"))}


def reporting_paths(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "IRPT-001", "ART-IRP", IR_FILE)
    if data is None:
        return out
    paths = _paths(data)
    reference = {case: path.get("reference") for case, path in paths.items()}
    recipients = {case: set(path.get("recipients") or ()) for case, path in paths.items()}
    if reference.get("classified-compromise") != VOL_3:
        err("an actual or potential compromise of classified information is reported under "
            f"{VOL_3}, not {reference.get('classified-compromise')}")
    if reference.get("classified-spillage") != VOL_3:
        err("spillage of classified information is handled under "
            f"{VOL_3}, not {reference.get('classified-spillage')}")
    if reference.get("cui-disclosure") != VOL_4:
        err("an unauthorized disclosure of CUI is reported under "
            f"{VOL_4}, not {reference.get('cui-disclosure')}")
    if reference.get("pii-loss") != PRIVACY_REG:
        err("a loss or unauthorized disclosure of PII or other Privacy Act information is "
            f"reported under {PRIVACY_REG}, not {reference.get('pii-loss')}")
    if reference.get("cnssi-1010") != CNSSI_1010:
        err("cyber incident response and reporting complies with "
            f"{CNSSI_1010}, not {reference.get('cnssi-1010')}")
    contractor = paths.get("cleared-contractor-loss") or {}
    if contractor.get("applies") is not False:
        if contractor.get("reference") != NISP_MANUAL:
            err(f"a loss on a cleared contractor system is reported under {NISP_MANUAL}, not "
                f"{contractor.get('reference')}")
        if "DCSA" not in set(contractor.get("recipients") or ()):
            err("incidents involving cleared defense contractors are reported to DCSA, the "
                "former DSS")
    elif str(contractor.get("not_applicable_rationale") or "") == "":
        err("cleared-contractor-loss is marked not applicable with no rationale")
    if not {"PER-AO", "chain-of-command"} <= recipients.get("incident-to-ao", set()):
        err("incidents are reported to the AO and the appropriate reporting chain")
    if "IG DoD" not in recipients.get("dodin-deficiency", set()):
        err("a cybersecurity deficiency behind a breach goes to the IG DoD")
    return out


def reporting_investigations(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "IRPT-002", "ART-IRP", IR_FILE)
    if data is None:
        return out
    paths = _paths(data)
    compromise = paths.get("classified-compromise") or {}
    if compromise.get("identified_as") != "negligent-discharge":
        err("a disclosure or spillage of classified information is identified as a negligent "
            f"discharge, not {compromise.get('identified_as')}")
    determines = {"willful", "negligent", "inadvertent"} - set(compromise.get("determines") or ())
    if determines:
        err("the investigation determines whether the incident was willful, negligent or "
            "inadvertent")
    lawful = paths.get("federal-law-violation") or {}
    needed = {"DCIO", "law-enforcement", "IG DoD"} - set(lawful.get("recipients") or ())
    if needed:
        err("incidents that appear to violate federal law are reported to the defense criminal "
            "investigative organization, law enforcement and the IG DoD")
    anomalous = paths.get("anomalous-user-activity") or {}
    if "component-investigative-authority" not in (anomalous.get("recipients") or ()):
        err("anomalous user activity contacts the DoD Component investigative authority")
    if anomalous.get("audit_data") != "chain-of-custody":
        err("audit data of anomalous user activity is kept with its chain of custody, not "
            f"{anomalous.get('audit_data')}")
    if _space(ctx):
        space = paths.get("space-events") or {}
        if not {"PER-AO", "operations-organization"} <= set(space.get("recipients") or ()):
            err("space NSS report cybersecurity events to the cognizant AO and operations "
                "organizations")
        threats = paths.get("threats-and-vulnerabilities") or {}
        if "intelligence-authority" not in (threats.get("recipients") or ()):
            err("threats and vulnerabilities are reported to the cognizant intelligence "
                "authority")
    return out


# --- service agreements -----------------------------------------------------------------

def _agreements(data: dict[str, Any]) -> list[dict[str, Any]]:
    return _dicts(data.get("agreements"))


def _services(agreement: dict[str, Any]) -> list[dict[str, Any]]:
    return _dicts(agreement.get("services"))


def _baseline(ctx: Context) -> set[str] | None:
    """The baseline's control IDs, or None when baseline.json is absent or unreadable: the
    alignment clause then has nothing to compare with, and RUN-FM-001 reports the file."""
    return set(baseline_mod.control_ids(ctx.run)) if baseline_mod.load(ctx.run) else None


def _cato_in_force(ctx: Context) -> bool:
    """A cATO holds on a standing authorization; a revocation (AD-RCATO) or a denial ends it."""
    kinds = {e.id: e.data for e in ctx.run.framework.index("decisions").values()}
    effects = {k: str(v.get("effect")) for k, v in kinds.items()}
    return any(s.continuous for s in ledger.in_force(_dicts(ctx.ledger), effects).values())


def service_agreements(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "SVCA-001", "ART-SVCA", SVC_FILE)
    if data is None:
        return out
    baseline = _baseline(ctx)
    documented: dict[str, set[str]] = {}
    pk, show = providers.keyer(ctx), providers.shown(ctx)
    for a in _agreements(data):
        ident, provider = a.get("id"), a.get("provider")
        controls = {c for s in _services(a) for c in s.get("controls") or ()}
        documented.setdefault(str(pk(provider)), set()).update(controls)
        if a.get("instrument") not in INSTRUMENTS:
            err(f"{ident}: cybersecurity services are implemented under policy, an MOA, a contract "
                f"or a support agreement, not {a.get('instrument')}")
        evaluated = a.get("evaluation") if isinstance(a.get("evaluation"), dict) else {}
        if a.get("role") == "cssp" and evaluated.get("scheme") not in CSSP_SCHEMES:
            err(f"{ident}: a CSSP offers services as evaluated under the Evaluator's Scoring "
                f"Metrics of DoD O-8530.01-M, not {evaluated.get('scheme')}")
        validation = a.get("validation") if isinstance(a.get("validation"), dict) else {}
        if validation.get("by") not in SUBSCRIBERS:
            err(f"{ident}: the system's own side validates the support agreement, not "
                f"{validation.get('by')}")
        missing = set(VALIDATION_COVERS) - set(validation.get("covers") or ())
        if missing:
            err(f"{ident}: the validated agreement does not define "
                f"{', '.join(sorted(missing))}")
        for s in _services(a):
            parties = {r.get("party") for r in _dicts(s.get("responsibilities"))}
            if {"service-provider", "subscriber"} - parties:
                err(f"{s.get('id')}: CSSP and subscriber responsibilities are each assigned for "
                    "every service")
            for cid in s.get("controls") or ():
                if baseline is not None and cid not in baseline:
                    err(f"{s.get('id')} aligns with {cid}, a security control outside the "
                        "baseline")
    roles = [a.get("role") for a in _agreements(data)]
    if data.get("dodin_connected") is True and "cssp" not in roles:
        err("no agreement names the system's CSSP")
    for path, control in family_records(ctx, SSP_DIR, "controls"):
        cid, provider = control.get("control_id"), pk(control.get("inherited_from"))
        if provider in documented and cid not in documented[provider]:
            err(f"the implemented security control {cid} ({path}) is not documented in the "
                f"agreement with {show(provider)}")
    if not _cato_in_force(ctx):
        return out
    cssps = [a for a in _agreements(data) if a.get("role") == "cssp"]
    for a in cssps:
        if a.get("integration") == "external" and a.get("instrument") != "sla":
            err(f"{a.get('id')}: an external CSSP on a cATO system is held to a Service Level "
                f"Agreement, not {a.get('instrument')}")
    covered = {env for a in cssps for env in a.get("environments") or ()}
    uncovered = set(data.get("system_environments") or ()) - covered
    if uncovered:
        err(f"the scope and parameters of CSSP support leave out {', '.join(sorted(uncovered))}")
    if "vulnerability-detection" not in [s.get("kind") for a in cssps for s in _services(a)]:
        err("no CSSP sensors and tools detect vulnerabilities")
    named = {pk(a.get("provider")) for a in _agreements(data)}
    inherited = {pk(c.get("inherited_from")) for _, c in family_records(ctx, SSP_DIR, "controls")
                 if c.get("status") == "inherited"}
    for provider in sorted(p for p in inherited if p and p not in named):
        err(f"inherited controls integrate with {show(provider)} and no agreement documents it")
    return out


def service_effectiveness(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "SVCA-002", "ART-SVCA", SVC_FILE, "M-2")
    if data is None:
        return out
    for a in _agreements(data):
        ident = a.get("id")
        services = {s.get("id") for s in _services(a)}
        if "M-2" in scope.active_tasks(ctx.run) and not a.get("effectiveness"):
            err(f"{ident}: M-2 is in scope and measures no service under this agreement")
        for m in _dicts(a.get("effectiveness")):
            issue = m.get("issue") if isinstance(m.get("issue"), dict) else {}
            status = issue.get("status")
            if m.get("measured_by") not in SUBSCRIBERS:
                err(f"{ident}: the effectiveness of a cybersecurity service is monitored by the "
                    f"owner of the system, not {m.get('measured_by')}")
            if m.get("service") not in services:
                err(f"{ident}: effectiveness is measured against {m.get('service')}, which "
                    "is no service provided under the agreement")
            if status == "unresolved" and issue.get("reported_to") != "PER-CIO":
                err(f"{ident}: an issue that cannot be resolved is reported to the DoD "
                    f"Component CIO, not {issue.get('reported_to')}")
            if status == "resolved" and issue.get("reported_to") \
                    and issue.get("resolved_by") != issue.get("reported_to"):
                err(f"{ident}: the DoD Component resolves the issue the parties could not, not "
                    f"{issue.get('resolved_by')}")
            if m.get("rating") == "ineffective" and status == "none":
                err(f"{ident}: a service executed outside the agreement raises an issue")
    return out


# --- security plan records --------------------------------------------------------------

def _system_status(ctx: Context) -> tuple[str, dt.date | None]:
    """What the ledger says of the system: its status and when that status ends."""
    kinds = {e.id: e.data for e in ctx.run.framework.index("decisions").values()}
    records = _dicts(ctx.ledger)
    effects = {k: str(v.get("effect")) for k, v in kinds.items()}
    standing = [s for s in ledger.in_force(records, effects).values()
                if s.record.get("subject") == "system"]
    if standing:
        latest = max(standing, key=lambda s: (str(s.record.get("date")), str(s.record.get("id"))))
        return STATUS_OF.get(str(latest.record.get("decision")), NO_DECISION), latest.expires
    closing = [r for r in records if r.get("subject") == "system"
               and (kinds.get(r.get("decision")) or {}).get("effect") in ("deny", "rescind")]
    if not closing:
        return NO_DECISION, None
    last = max(closing, key=lambda r: (str(r.get("date")), str(r.get("id"))))
    return (DENIED if kinds[last["decision"]].get("effect") == "deny" else NO_DECISION), None


def plan_elements(ctx: Context) -> list[RunFinding]:
    """The ledger holds the decisions, so each task writing it restates the three elements the
    security plan carries (CNSSI 1254 Annex C) in `system_status`."""
    data = ctx.data(ledger.LEDGER_FILE)
    records = _dicts(ctx.ledger)
    if not isinstance(data, dict) or not records:
        return []
    out: list[RunFinding] = []
    last = max(records, key=lambda r: (str(r.get("date")), str(r.get("id"))))

    def err(message: str) -> None:
        out.append(make("SSPR-001", message, ledger.LEDGER_FILE, None, {str(last.get("task"))}))

    block = data.get("system_status") if isinstance(data.get("system_status"), dict) else {}
    held, expires = _system_status(ctx)
    if block.get("status") != held:
        err(f"the security plan states authorization status {block.get('status')}, and the "
            f"ledger holds {held}")
    stated = _day(block.get("termination_date"))
    if stated != expires:
        err(f"the security plan states authorization termination date {stated}, and the ledger "
            f"holds {expires}")
    if held in ("ATO", "ATO-with-conditions"):
        latest = _day(last.get("date"))
        review = _day(block.get("security_review_date"))
        if review is None or latest is None or (latest - review).days > ANNUAL_REVIEW_DAYS:
            err(f"the Security Review Date {review} is not within a year on a system with an ATO")
    return out


def funding(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "FUND-001", "ART-SSP", SSP_FILE)
    if data is None:
        return out
    lines = _dicts(data.get("funding"))
    phases: dict[str, set[str]] = {}
    for line in lines:
        phases.setdefault(str(line.get("purpose")), set()).update(line.get("phases") or ())
    purposes = set(phases)
    for purpose in DOD_FUND_PURPOSES:
        if purpose not in purposes:
            err(f"no budget line for security control {purpose} across the system life cycle")
    if OPERATIONS_PHASE not in phases.get("sustainment", set()):
        err("sustainment funding stops short of operations and support, so the plan and budget "
            "do not run throughout the system life cycle")
    poam = _poam_ids(ctx)
    for line in lines:
        if line.get("status") == "unfunded" and line.get("poam_item") not in poam:
            err(f"unfunded budget line {line.get('purpose')} names no POA&M item")
    if _space(ctx, data):
        for purpose in SPACE_FUND_PURPOSES:
            if purpose not in purposes:
                err(f"no programmed funds to {purpose} what provides the AO approved levels of "
                    "cybersecurity")
    return out


def _uses(data: dict[str, Any]) -> list[dict[str, Any]]:
    crypto = data.get("cryptography")
    return _dicts(crypto.get("uses")) if isinstance(crypto, dict) else []


def cryptography(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CRYP-001", "ART-SSP", SSP_FILE)
    if data is None:
        return out
    crypto = data.get("cryptography") if isinstance(data.get("cryptography"), dict) else {}
    classified = CLASSIFIED_OVERLAY in _overlays(ctx)
    if not str(crypto.get("key_management") or "").strip():
        err("the plan holds no cryptographic key management information")
    if crypto.get("nsa_approved") is False and not crypto.get("key_management_process"):
        err("the solution is not NSA approved and states no key management technology and "
            "processes")
    if classified and crypto.get("nsa_approved") is not True:
        err("a system containing classified information uses NSA-approved encryption "
            "techniques")
    if classified and len(_uses(data)) < 1:
        err("a system containing classified information records no use of cryptography")
    for use in _uses(data):
        ident = use.get("id")
        if use.get("policy_basis") != CNSSP_15:
            err(f"{ident}: cryptography protecting DoD information is implemented under "
                f"{CNSSP_15}, not {use.get('policy_basis')}")
        if use.get("acquisition_basis") != CNSSP_15:
            err(f"{ident}: cryptographic products are acquired under {CNSSP_15}, not "
                f"{use.get('acquisition_basis')}")
        approval = use.get("nsa_approval") if isinstance(use.get("nsa_approval"), dict) else {}
        if classified and approval.get("by") != NSA:
            err(f"{ident}: NSA approves cryptography protecting classified information, not "
                f"{approval.get('by')}")
        if classified and approval.get("algorithm") != use.get("algorithm"):
            err(f"{ident}: the NSA approval covers the application of {approval.get('algorithm')}"
                f", and classified information is protected by {use.get('algorithm')}")
    return out


def space_cryptography(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CRYP-002", "ART-SSP", SSP_FILE)
    if data is None or not _space(ctx, data):
        return out
    crypto = data.get("cryptography") if isinstance(data.get("cryptography"), dict) else {}
    space = crypto.get("space") if isinstance(crypto.get("space"), dict) else {}
    if space.get("command_protection") not in ("authenticated-encrypted-end-to-end",
                                               "cnssi-1200-exception"):
        err("space system commands and data are authenticated and encrypted from end to end, "
            f"not {space.get('command_protection')}")
    if crypto.get("nsa_approved") is not True:
        err("a space NSS uses NSA-approved cryptography")
    documents = [space.get("skmp"), *(space.get("csps") or ())]
    for plan in _dicts(documents):
        if plan.get("approved_by") != NSA:
            err(f"the system key management plan or cryptographic security plan "
                f"{plan.get('name')} is approved by NSA, not {plan.get('approved_by')}")
        submitted, approved = _day(plan.get("submitted")), _day(plan.get("approved"))
        if submitted is None or approved is None or submitted > approved:
            err(f"{plan.get('name')} is submitted to NSA for approval before it is approved")
    for link in _dicts(space.get("emergency_links")):
        if link.get("unencrypted") is True and link.get("approved_by") != NSA:
            err(f"unencrypted emergency backup link {link.get('link')} is approved by NSA, not "
                f"{link.get('approved_by')}")
    for bypass in _dicts(space.get("bypasses")):
        if bypass.get("coordinated_with") != NSA or bypass.get("approved_by") != "PER-AO":
            err(f"cryptographic bypass {bypass.get('capability')} is coordinated with NSA and "
                "approved by the AO")
    for use in _uses(data):
        approval = use.get("nsa_approval") if isinstance(use.get("nsa_approval"), dict) else {}
        if approval.get("by") != NSA:
            err(f"{use.get('id')}: NSA reviews and approves all cryptographies on a space NSS, "
                f"not {approval.get('by')}")
        consulted, started = _day(use.get("nsa_consulted")), _day(use.get("acquisition_started"))
        if consulted is None or started is None or consulted > started:
            err(f"{use.get('id')}: consult with NSA prior to initiating the acquisition")
    return out


def crypto_vulnerabilities(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "CRYP-003", "ART-SSP", SSP_FILE, "M-4")
    if data is None:
        return out
    crypto = data.get("cryptography") if isinstance(data.get("cryptography"), dict) else {}
    poam = _poam_ids(ctx)
    for vulnerability in _dicts(crypto.get("vulnerabilities")):
        ident = vulnerability.get("poam_item")
        if ident not in poam:
            err(f"cryptographic vulnerability {ident} is no POA&M item")
        if vulnerability.get("vep") not in ("submitted", "not-applicable"):
            err(f"{ident}: a cryptographic vulnerability is submitted to the VEP as applicable, "
                f"not {vulnerability.get('vep')}")
    return out


def telework(ctx: Context) -> list[RunFinding]:
    data, out, err = _in_play(ctx, "TELE-001", "ART-SSP", SSP_FILE)
    if data is None:
        return out
    block = data.get("telework") if isinstance(data.get("telework"), dict) else {}
    if block.get("non_gfe_remote_access") is True:
        approval = block.get("approval") if isinstance(block.get("approval"), dict) else {}
        if approval.get("by") != DOD_CIO:
            err("telework on non-government furnished equipment is approved by the DoD CIO, not "
                f"{approval.get('by')}")
        if block.get("basis") != SP_800_114:
            err(f"telework on non-government furnished equipment is developed from {SP_800_114}, "
                f"not {block.get('basis')}")
    return out


# --- PLANREF-001: a plan control is implemented only once its plan is approved -------------

# The controls an SSP statement fulfils by a task-level plan, and the plan's record (F-07-1).
PLAN_CONTROLS = {"cp-2": CP_FILE, "ir-8": IR_FILE, "cm-9": CM_FILE}
IMPLEMENTED = "implemented"


def plan_statements(ctx: Context) -> list[RunFinding]:
    """An SSP statement calls cp-2, ir-8 or cm-9 implemented only when the plan it promises is
    on record and approved (`plan_approval`); until then the control is planned or partial."""
    if not scope.produced_or_seeded(ctx.run, "ART-SSP"):
        return []
    out: list[RunFinding] = []
    for rel, c in family_records(ctx, SSP_DIR, "controls"):
        cid = c.get("control_id")
        plan = PLAN_CONTROLS.get(str(cid))
        if plan is None or c.get("status") != IMPLEMENTED:
            continue
        data = ctx.data(plan) if ctx.run.path(plan).is_file() else None
        approval = data.get("plan_approval") if isinstance(data, dict) else None
        approved = isinstance(approval, dict) and approval.get("date") is not None
        if approved is False:
            out.append(make("PLANREF-001", f"{cid} is implemented, but its plan {plan} is not "
                            "on record with a plan_approval: the control is partial until the "
                            "plan is approved", rel, None, {"S-4"}))
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CMPL-001", ci_register), ("CMPL-002", cm_tools), ("CPLAN-001", bia_times),
                ("CPLAN-002", exercise_depth), ("CPLAN-003", operational_resilience),
                ("IRPT-001", reporting_paths), ("IRPT-002", reporting_investigations),
                ("SVCA-001", service_agreements), ("SVCA-002", service_effectiveness),
                ("SSPR-001", plan_elements), ("FUND-001", funding), ("CRYP-001", cryptography),
                ("CRYP-002", space_cryptography), ("CRYP-003", crypto_vulnerabilities),
                ("TELE-001", telework), ("BYP-001", bypasses),
                ("PLANREF-001", plan_statements))
