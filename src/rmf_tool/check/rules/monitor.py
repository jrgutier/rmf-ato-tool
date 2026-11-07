"""The Monitor step's records, from the change log to the posture report: MCHG-001 to MCHG-003 on
each change in ART-CHG, MCON-001 on hosted and interconnected systems, MLEV-001 on what a system
inherits, MPOA-001 on the POA&M and the outside findings it takes, MRPT-001 and MRPT-002 on what
M-5 reports and to whom, MISCM-001 on the ISCM program assessment a decision reads, MMEAS-001 on
security measurement and MPLAN-001 on the system plan's review log.

A rule stays quiet while its artifact is out of play. Once it is in play the data file is demanded
here, because ART-CHG and ART-SECRPT are supporting artifacts, which RUN-ART-001 does not cover."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import POAM_FILE, SAR_DIR, family_records
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope

CHANGES_FILE = "artifacts/data/changes.yaml"
REPORTS_FILE = "artifacts/data/posture-reports.yaml"
CONMON_FILE = "artifacts/data/conmon.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
ALLOCATION_FILE = "artifacts/data/allocation.yaml"
RAR_FILE = "artifacts/data/rar.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
PLAN_REVIEWS_FILE = "artifacts/data/plan-reviews.yaml"

UNCONTROLLED = ("exempt", "pre-approved")  # SP 800-128 3.3.2 step iii
TESTED = ("pass", "fail")
AFTER_THE_FACT = ("unscheduled", "unauthorized")  # SP 800-128 3.3.2: controlled after the fact
UNTESTED = (*AFTER_THE_FACT, "dow-order")  # already made, or ordered: no test comes first
ROOT_CAUSES = ("adversary-attack", "process-failure", "inadvertent-error", "other")
UNDER_ANALYSIS = "under-analysis"
RECONCILED = frozenset({"baseline", "inventory", "change-requests"})  # SP 800-128 3.4, 3.4.1
AO_OR_DR = frozenset({"PER-AO", "PER-AODR"})  # DoDI 8510.01: the AODR acts for the AO

STOPPED = ("deny", "rescind")
VALID = ("authorize", "continuous")
ARRANGEMENTS = ("common-control-provider", "organizational-system", "external-service")
ENTERPRISE = "enterprise"  # judged by ENT-002

COMPLETIONS = ("before-authorization", "after-authorization")  # SP 800-37r2 Task A-6
RESOLVED = ("completed", "risk-accepted")

# DoDI 8530.01 Enclosure 4, 3.c.(5): who receives the POA&M, by GENSER or SE designation.
POAM_BODIES = {"GENSER": ("CDRUSSTRATCOM", "DISA"), "SE": ("DIA",)}
NOT_CONNECTED = "not-connected"
AWARENESS = frozenset({"threats", "traffic", "fault", "performance", "bandwidth", "route",
                       "network-management"})  # DoDI 8530.01 Enclosure 3, 5.b
EMPLOYEE_USE = "employee-use"
SHARING = frozenset({"visible", "accessible", "understandable", "trusted", "interoperable"})
AUDIENCES = frozenset({"superior", "peer"})  # vertically and horizontally, DoDI 8530.01 2.i.(2)
CMRS_METHODS = ("automated", "manual")
REVIEWERS = frozenset({"PER-RE", "PER-CISO"})

ISCM_PARTIES = frozenset({"PER-PM", "PER-AO", "PER-CIO", "PER-CISO", "PER-PRIV", "PER-RE"})
ISCM_STAGES = frozenset({"before", "during", "after"})  # SP 800-137A 3.1
OTHER_THAN_SATISFIED = "other-than-satisfied"
PLAN_APPROVERS = ("PER-AO", "PER-AODR", "PER-CCB")  # SP 800-18r2 3.2: through change management
Record = dict[str, Any]
Err = Callable[[str], None]


def _block(record: Any, key: str) -> Record:
    value = record.get(key) if isinstance(record, dict) else None
    return value if isinstance(value, dict) else {}


def _items(record: Any, key: str) -> list[Record]:
    value = record.get(key) if isinstance(record, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _strings(record: Any, key: str) -> set[str]:
    value = record.get(key) if isinstance(record, dict) else None
    return {str(v) for v in value} if isinstance(value, list) else set()


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _as_of(ctx: Context) -> dt.date | None:
    return _day(str(ctx.run.config.get("as_of"))[:10])


def _collector(rule: str, path: str, task: str) -> tuple[list[RunFinding], Err]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, path, None, {task}))

    return out, err


def _in_play(ctx: Context, artifact: str) -> bool:
    return scope.produced_or_seeded(ctx.run, artifact)


def _first_authorization(ctx: Context) -> dt.date | None:
    effect_of = ledger.effects(ctx.run)
    dates = [_day(r.get("date")) for r in ctx.ledger or ()
             if effect_of.get(r.get("decision")) == "authorize"]
    return min((d for d in dates if d), default=None)


# --- MCHG-001: a change through control, from test to close-out -----------------------------

def change_lifecycle(ctx: Context) -> list[RunFinding]:
    if not _in_play(ctx, "ART-CHG"):
        return []
    out, err = _collector("MCHG-001", CHANGES_FILE, "M-1")
    data = ctx.data(CHANGES_FILE)
    if not isinstance(data, dict):
        err("no change log data: M-1 records each change in artifacts/data/changes.yaml")
        return out
    for c in _items(data, "changes"):
        cid, test, decision = c.get("id"), _block(c, "test"), _block(c, "decision")
        implementation, verification = _block(c, "implementation"), _block(c, "verification")
        controlled = c.get("control") not in UNCONTROLLED
        if controlled and c.get("origin") not in UNTESTED:
            if test.get("result") not in TESTED:
                err(f"{cid}: the proposed change is not tested for security and functional "
                    "impacts")
            audience = _strings(test, "presented_to")  # SP 800-128 3.3.2 step v
            missing = [] if "PER-CCB" in audience else ["PER-CCB"]
            missing += [] if audience & AO_OR_DR else ["PER-AO"]
            if missing:
                err(f"{cid}: the impacts of the change are not presented to "
                    f"{', '.join(missing)}")
            tested, implemented = _day(test.get("date")), _day(implementation.get("date"))
            if tested and implemented and tested > implemented:
                err(f"{cid}: the change is made on {implemented}, before it is tested on {tested}")
        if c.get("origin") == "dow-order" and "PER-CSSP" not in _strings(
                decision, "communicated_to"):
            err(f"{cid}: the impacts of the DoW order are not shared with the CSSP")
        requester = c.get("requested_by")
        if decision and requester not in _strings(decision, "communicated_to"):
            err(f"{cid}: the board's decision is not communicated to the requester {requester}")
        if controlled and c.get("closed") and implementation \
                and verification.get("result") != "pass":
            err(f"{cid}: a change request is not closed until the change is confirmed deployed "
                "without issues")
    return out


# --- MCHG-002: unauthorized changes, their root cause and the response ----------------------

def unauthorized_changes(ctx: Context) -> list[RunFinding]:
    data = ctx.data(CHANGES_FILE)
    if not _in_play(ctx, "ART-CHG") or not isinstance(data, dict):
        return []
    out, err = _collector("MCHG-002", CHANGES_FILE, "M-1")
    window = _block(_block(data, "monitoring"), "unauthorized_changes")
    start, end = _day(window.get("from")), _day(window.get("to"))
    # Monitoring is due from the first authorization; a run begun after it (a seeded ledger)
    # answers for its own span, and a run with no authorization yet owes no start date.
    first = _first_authorization(ctx)
    due = max((d for d in (first, _as_of(ctx)) if d), default=None) if first else None
    if due is not None and (start is None or start > due):
        err(f"monitoring for unauthorized changes starts at {start}, after the authorization or "
            f"the run start of {due}")
    if missing := sorted(RECONCILED - _strings(window, "reconciled_against")):
        err(f"changes detected by monitoring are not reconciled with {', '.join(missing)}")
    poam, rar = ctx.data(POAM_FILE), ctx.data(RAR_FILE)
    responses = {i.get("id") for i in _items(poam, "items")} | {
        r.get("id") for r in _items(rar, "risks")}
    for c in _items(data, "changes"):
        cid, origin, root = c.get("id"), c.get("origin"), _block(c, "root_cause")
        day, cause = _day(c.get("date")), root.get("cause")
        if end is not None and day is not None and day > end:
            err(f"{cid} of {day} falls after monitoring for unauthorized changes ends on {end}")
        if origin == "unauthorized" and cause not in (*ROOT_CAUSES, UNDER_ANALYSIS):
            err(f"{cid}: information about the unauthorized change is not analyzed to determine "
                "the root cause")
        if c.get("closed") and cause == UNDER_ANALYSIS:
            err(f"{cid} is closed before the root cause of the unauthorized change is determined")
        answered = origin == "unauthorized" or c.get("privacy_impact") is True
        if answered and root.get("response") not in responses:
            err(f"{cid}: the response to the root cause names {root.get('response')}, which is "
                "no POA&M item or risk (Task M-3)")
        if origin in AFTER_THE_FACT and c.get("control") in UNCONTROLLED:
            err(f"{cid}: a change outside the process goes through configuration change control "
                f"even after the fact, not {c.get('control')}")
    return out


# --- MCHG-003: lawful LE/CI tools, accommodated and coordinated with the AO -----------------

def le_ci(ctx: Context) -> list[RunFinding]:
    data = ctx.data(CHANGES_FILE)
    if not _in_play(ctx, "ART-CHG") or not isinstance(data, dict):
        return []
    out, err = _collector("MCHG-003", CHANGES_FILE, "M-1")
    for c in _items(data, "changes"):
        if c.get("origin") != "le-ci":
            continue
        cid, tool, decision = c.get("id"), _block(c, "le_ci"), _block(c, "decision")
        if tool.get("lawful") is True and decision.get("outcome") == "disapproved":
            err(f"{cid}: network administrators accommodate lawful LE/CI tools and solutions; "
                "the board disapproved this one")
        if tool.get("coordinated_with") not in AO_OR_DR:
            err(f"{cid}: LE/CI organizations coordinate the implementation with their AO, not "
                f"{tool.get('coordinated_with')}")
        attempted = _day(tool.get("attempted"))
        implemented = _day(_block(c, "implementation").get("date"))
        if attempted is None or (implemented is not None and attempted > implemented):
            err(f"{cid}: the attempt to coordinate with the AO of {attempted} follows the "
                f"implementation of {implemented}")
        if c.get("control") in UNCONTROLLED:
            err(f"{cid}: LE/CI solutions are coordinated consistent with change control, not "
                f"{c.get('control')}")
    return out


# --- MCON-001: the AO's decision on a hosted or interconnected system is enforced -----------

def connections(ctx: Context) -> list[RunFinding]:
    data = ctx.data(CHANGES_FILE)
    if not _in_play(ctx, "ART-CHG") or not isinstance(data, dict):
        return []
    out, err = _collector("MCON-001", CHANGES_FILE, "M-1")
    effect_of, today = ledger.effects(ctx.run), _as_of(ctx)
    records = _items(data, "connections")
    for r in records:
        term = _day(r.get("authorization_termination_date"))
        lapsed = term is not None and today is not None and term < today
        stopped = effect_of.get(r.get("decision")) in STOPPED or lapsed
        if stopped and r.get("action") != "disconnected":
            err(f"{r.get('id')}: the AO's authorization decision on {r.get('system')} is not "
                f"enforced; the connection stands at {r.get('action')}")
    named = {r.get("component") for r in records}
    for component in _items(ctx.data(BOUNDARY_FILE), "components"):
        if component.get("type") == "interconnection" and component.get("id") not in named:
            err(f"{component.get('id')}: no AO authorization decision is recorded for the "
                "interconnected system")
    return out


# --- MLEV-001: inheriting from a system that is no approved common control provider ---------

def inheritance(ctx: Context) -> list[RunFinding]:
    data = ctx.data(LEVERAGED_FILE)
    if not _in_play(ctx, "ART-SD") or not isinstance(data, dict):
        return []
    out, err = _collector("MLEV-001", LEVERAGED_FILE, "C-1")
    effect_of, today = ledger.effects(ctx.run), _as_of(ctx)
    allocation = ctx.data(ALLOCATION_FILE)  # S-3 writes it after C-1
    providers = {a.get("provider") for a in _items(allocation, "allocations")
                 if a.get("type") == "common"}
    for r in _items(data, "leveraged_authorizations"):
        lid, arrangement = r.get("id"), r.get("arrangement")
        if ENTERPRISE in r:
            continue
        if arrangement not in ARRANGEMENTS:
            err(f"{lid}: the record names no arrangement of the inheritance: "
                f"{', '.join(ARRANGEMENTS)}")
        if arrangement == "common-control-provider" and allocation is not None \
                and r.get("provider") not in providers:
            err(f"{lid}: {r.get('provider')} provides no common control in allocation.yaml, so "
                "it is no approved common control provider")
        if arrangement != "organizational-system":
            continue
        decision = r.get("decision")
        if effect_of.get(decision) not in VALID:
            err(f"{lid}: the system providing inherited controls holds a valid authorization to "
                f"operate, not {decision}")
        term = _day(r.get("authorization_termination_date"))
        if term is not None and today is not None and term < today:
            err(f"{lid}: the authorization to operate of the system providing inherited controls "
                f"ended on {term}")
        if _block(r, "ao_aware").get("official") not in AO_OR_DR:
            err(f"{lid}: the authorizing official of the system inheriting the controls is not "
                "made aware of the inheritance")
    return out


# --- MPOA-001: the POA&M and the outside findings it takes ----------------------------------

def poam_sources(ctx: Context) -> list[RunFinding]:
    data = ctx.data(POAM_FILE)
    if not _in_play(ctx, "ART-POAM") or not isinstance(data, dict):
        return []
    out, err = _collector("MPOA-001", POAM_FILE, "A-6")
    items, external = _items(data, "items"), _items(data, "external_findings")
    ids = {i.get("id") for i in items}
    documented = {f.get("id") for _, f in family_records(ctx, SAR_DIR, "findings")}
    documented |= {f.get("id") for f in _items(ctx.data(STIG_FILE), "findings")}
    documented |= {f.get("id") for f in external}
    # M-3's own sources of a weakness: an order, a disclosure report, an analyzed vulnerability.
    documented |= {r.get("id") for key in ("directed_actions", "vdp_reports", "vulnerabilities")
                   for r in _items(data, key)}
    first = _first_authorization(ctx)
    for i in items:
        iid, recommended = i.get("id"), i.get("recommended_completion")
        if recommended not in COMPLETIONS:
            err(f"{iid}: the task carries no recommendation for completion before or after "
                "system authorization")
        scheduled = _day(i.get("scheduled_completion"))
        if recommended == COMPLETIONS[0] and first and scheduled and scheduled > first:
            err(f"{iid}: recommended for completion before system authorization of {first}, but "
                f"scheduled for {scheduled}")
        if i.get("finding_ref") not in documented:
            err(f"{iid}: the deficiency {i.get('finding_ref')} is not documented in the "
                "assessment reports")
    if first is not None and _block(data, "ao_review").get("by") not in AO_OR_DR:
        err("the plan of action and milestones is not reviewed by the authorizing official")
    decisions = {r.get("id") for r in ctx.ledger or ()}
    for f in external:
        fid, verified = f.get("id"), _block(f, "verified")
        if f.get("poam_item") not in ids and f.get("accepted_in") not in decisions:
            err(f"{fid}: the {f.get('event')} finding of {f.get('body')} is not leveraged in a "
                "POA&M item or an accepted risk")
        found, checked = _day(f.get("date")), _day(verified.get("date"))
        if found and (checked is None or checked < found):
            err(f"{fid}: the POA&M for the finding of {found} is not verified as maintained")
    return out


# --- MRPT-001: what M-5 reports, and who receives it ----------------------------------------

def _designation(ctx: Context, err: Err) -> str | None:
    """The DODIN designation of the system; a run cannot call itself apart from the DODIN while
    its boundary holds an interconnection."""
    dodin = _block(_block(ctx.data(CONMON_FILE), "reporting"), "dodin")
    designation = dodin.get("designation")
    if designation not in (*POAM_BODIES, NOT_CONNECTED):
        err(f"conmon.yaml reporting.dodin names no GENSER or SE designation: {designation}")
        return None
    linked = [c.get("id") for c in _items(ctx.data(BOUNDARY_FILE), "components")
              if c.get("type") == "interconnection"]
    if designation == NOT_CONNECTED and linked:
        err(f"the system is {NOT_CONNECTED}, but its boundary holds {', '.join(map(str, linked))}")
    return designation


def _cmrs(ctx: Context, report: Record, err: Err) -> None:
    effect_of = ledger.effects(ctx.run)
    standing = ledger.in_force(ctx.ledger or [], effect_of).values()
    cmrs, rid = _block(report, "cmrs"), report.get("id")
    if any(s.continuous for s in standing) and cmrs.get("method") not in CMRS_METHODS:
        err(f"{rid}: compliance reporting statistics do not reach the Continuous Monitoring and "
            "Risk Scoring system of record")
    if cmrs.get("method") == "manual" and cmrs.get("automated_process") == "developed":
        err(f"{rid}: manual reporting goes on after the automated process is developed")


def _sharing(report: Record, err: Err) -> None:
    rid, sharing = report.get("id"), _block(report, "sharing")
    if missing := sorted(AUDIENCES - _strings(sharing, "audiences")):
        err(f"{rid}: cybersecurity status data is not shared across the DoD enterprise with "
            f"{', '.join(missing)} organizations")
    if sharing.get("display") != "automated":
        err(f"{rid}: DODIN operations and cybersecurity data are not displayed by automated "
            "capabilities")
    if missing := sorted(SHARING - _strings(sharing, "qualities")):
        err(f"{rid}: DODIN operations and cybersecurity data are not {', '.join(missing)}")


def _dodin(ctx: Context, reports: list[Record], designation: str, err: Err) -> None:
    """What the reports hand DoD bodies, taken together: an update once sent is not owed again.
    POA&M updates and vulnerability coordination are owed "as required" (DoDI 8530.01 Encl. 4,
    3.c.(5); DoDI 8531.01 2.10.d), so only to a body conmon.yaml records as having required them."""
    required = _block(_block(_block(ctx.data(CONMON_FILE), "reporting"), "dodin"), "required_by")
    received: dict[str, set[str]] = {}
    for r in reports:
        for d in _items(r, "deliveries"):
            received.setdefault(str(d.get("recipient")), set()).update(_strings(d, "content"))
        _sharing(r, err)
    for body in POAM_BODIES.get(designation, ()):
        if body in required and "poam" not in received.get(body, ()):
            err(f"POA&Ms and subsequent updates are not provided to {body} for a {designation} "
                "system")
    shared = {f for r in reports for f in _strings(r, "findings_shared")}
    poam = ctx.data(POAM_FILE)
    for f in _items(poam, "external_findings"):
        if f.get("id") not in shared or "findings" not in received.get("CDRUSSTRATCOM", ()):
            err(f"the CDRUSSTRATCOM has no visibility into the {f.get('event')} finding "
                f"{f.get('id')}")
    items = _items(poam, "items")
    if items and "JFHQ-DODIN" in required \
            and "vulnerability-reports" not in received.get("JFHQ-DODIN", ()):
        err("vulnerability reports and assessments are not coordinated with JFHQ-DODIN")
    posted = {(v.get("poam_item"), v.get("status")) for r in reports
              for v in _items(r, "vulnerability_status")}
    for i in items:
        if i.get("status") in RESOLVED and (i.get("id"), i.get("status")) not in posted:
            err(f"the mitigation or risk acceptance status of {i.get('id')} is not reported to "
                f"JFHQ-DODIN as {i.get('status')}")


def _awareness(ctx: Context, err: Err) -> None:
    areas = _strings(_block(_block(ctx.data(CONMON_FILE), "reporting"), "dodin"), "awareness")
    if missing := sorted(AWARENESS - areas):
        err(f"ISCM gives no ongoing awareness of {', '.join(missing)} to support DODIN operations")
    if EMPLOYEE_USE not in areas:
        err("ISCM does not support monitoring of employee use of the DODIN to detect anomalous "
            "activity")


def posture_reports(ctx: Context) -> list[RunFinding]:
    if not _in_play(ctx, "ART-SECRPT"):
        return []
    out, err = _collector("MRPT-001", REPORTS_FILE, "M-5")
    data = ctx.data(REPORTS_FILE)
    if not isinstance(data, dict):
        err("no posture report data: M-5 records each report in "
            "artifacts/data/posture-reports.yaml")
        return out
    designation = _designation(ctx, err)
    wanted = _strings(_block(ctx.data(CONMON_FILE), "reporting"), "recipients")
    changes = ctx.data(CHANGES_FILE)
    external = {r.get("id") for r in _items(ctx.data(LEVERAGED_FILE), "leveraged_authorizations")
                if r.get("arrangement") == "external-service"}
    reports = _items(data, "reports")
    reported = {s.get("change") for r in reports for s in _items(r, "service_changes")
                if s.get("reported_to") == "USCYBERCOM"}
    for r in reports:
        rid = r.get("id")
        recipients = {d.get("recipient") for d in _items(r, "deliveries")}
        if missing := sorted(wanted - recipients):
            err(f"{rid}: the report does not reach {', '.join(missing)}, its recipients in "
                "conmon.yaml")
        issued = _day(r.get("issued"))
        scored = _day(_block(r, "scorecard").get("reported"))
        if scored is None or (issued and scored > issued):
            err(f"{rid}: cybersecurity scorecard reporting of {scored} is not accomplished by the "
                f"report issued on {issued}")
        _cmrs(ctx, r, err)
    if designation in POAM_BODIES:
        _dodin(ctx, reports, designation, err)
        _awareness(ctx, err)
    for c in _items(changes, "changes"):
        if external and "external_service" not in c:
            err(f"{c.get('id')}: the change does not say which external service it touches, or "
                "null for none, while the system leverages one")
        if c.get("external_service") in external and c.get("id") not in reported:
            err(f"{c.get('id')}: the status change of the external service is not reported "
                "through the network operations chain of command to the Commander, USCYBERCOM")
    return out


# --- MRPT-002: the organization tier reviews what the system reports ------------------------

def organization_tier(ctx: Context) -> list[RunFinding]:
    data = ctx.data(REPORTS_FILE)
    if not _in_play(ctx, "ART-SECRPT") or not isinstance(data, dict):
        return []
    out, err = _collector("MRPT-002", REPORTS_FILE, "M-5")
    tier, reports = _block(data, "organization_tier"), _items(data, "reports")
    reviews = _items(tier, "reviews")
    if missing := sorted(REVIEWERS - {r.get("by") for r in reviews}):
        err(f"the organization tier review of status reports lacks {', '.join(missing)}")
    issued = [d for d in (_day(r.get("issued")) for r in reports) if d]
    for review in reviews:
        day = _day(review.get("reviewed"))
        if issued and day and day < max(issued):
            err(f"{review.get('by')} reviewed on {day}, before the last report of {max(issued)}")
    # POA&M items carry no status date, so the count at a past review cannot be recomputed.
    count = tier.get("open_poam_items")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        err("the organization tier holds no aggregate POA&M information: open_poam_items is "
            f"{count}")
    return out


# --- MISCM-001: the ISCM program assessment a decision reads --------------------------------

def _iscm_report(a: Record, err: Err) -> None:
    aid, draft, final = a.get("id"), _block(a, "draft"), _block(a, "final")
    sponsor = a.get("executive_sponsor")
    if sponsor not in _strings(draft, "reviewed_by"):
        err(f"{aid}: the draft report is not reviewed by the executive sponsor {sponsor}")
    if sponsor not in _strings(final, "presented_to"):
        err(f"{aid}: the final report of findings is not presented to the organization's "
            f"executive sponsor {sponsor}")
    reviewed, presented = _day(draft.get("reviewed")), _day(final.get("presented"))
    if reviewed and (presented is None or presented < reviewed):
        err(f"{aid}: the final report of {presented} does not follow the draft reviewed on "
            f"{reviewed}")
    if unresolved := [d.get("issue") for d in _items(a, "differences")
                      if d.get("status") != "resolved"]:
        err(f"{aid}: the final report leaves differences of opinion open: "
            f"{', '.join(map(str, unresolved))}")


def _iscm_results(a: Record, err: Err) -> None:
    aid, results = a.get("id"), _items(a, "results")
    actions = _items(a, "recommendations")
    known = {r.get("id") for r in actions}
    elements = {r.get("element") for r in results}
    for r in results:
        if r.get("judgment") == OTHER_THAN_SATISFIED and r.get("further_action") not in known:
            err(f"{aid}: the shortfall in {r.get('element')} names {r.get('further_action')}, so "
                "the assessment results do not indicate the further actions required")
    for action in actions:
        if action.get("based_on") not in elements:
            err(f"{aid}: recommendation {action.get('id')} is not based on the data collected: "
                f"no result for {action.get('based_on')}")
    scores = [r.get("score") for r in results if isinstance(r.get("score"), int | float)]
    if scores:
        overall = a.get("overall_score")
        if len(scores) != len(results):
            err(f"{aid}: scoring is performed, but not for each assessment element")
        if not isinstance(overall, int | float):
            err(f"{aid}: scoring is performed, but no single score combines the scoring results")


def iscm_assessments(ctx: Context) -> list[RunFinding]:
    data = ctx.data(ledger.file_of(ctx.run))
    out, err = _collector("MISCM-001", ledger.file_of(ctx.run), "M-6")
    assessments = _items(data, "iscm_assessments")
    for a in assessments:
        aid = a.get("id")
        if missing := sorted(ISCM_PARTIES - _strings(a, "parties_considered")):
            err(f"{aid}: the ISCM program assessment does not consider the needs of "
                f"{', '.join(missing)}")
        stages = {e.get("stage") for e in _items(a, "expectations")}
        if missing := sorted(ISCM_STAGES - stages):
            err(f"{aid}: no expectations are set {' or '.join(missing)} the assessment")
        _iscm_report(a, err)
        _iscm_results(a, err)
    known = {a.get("id"): _day(_block(a, "final").get("presented")) for a in assessments}
    for r in ctx.ledger or ():
        name = r.get("iscm_assessment")
        if name is None:
            continue
        date = _day(r.get("date"))
        if name not in known:
            err(f"{r.get('id')}: the decision reads {name}, which is no ISCM program assessment")
        elif date and known[name] and known[name] > date:
            err(f"{r.get('id')}: the decision of {date} reads the ISCM program assessment "
                f"report of {known[name]}")
    return out


# --- MMEAS-001: security measurement, from information need to reported result --------------

def measurement(ctx: Context) -> list[RunFinding]:
    data = ctx.data(CONMON_FILE)
    out, err = _collector("MMEAS-001", CONMON_FILE, "M-2")
    if not isinstance(data, dict):
        return out
    block = _block(data, "measurement")
    if not block:
        if "M-2" in scope.active_tasks(ctx.run):
            err("conmon.yaml holds no security measurement: M-2 needs its measures")
        return out
    needs = {n.get("id") for n in _items(block, "information_needs")}
    measures = {}
    for m in _items(block, "measures"):
        measures[m.get("id")] = m
        if m.get("need") not in needs:
            err(f"{m.get('id')}: the measure satisfies no security-relevant information need: "
                f"{m.get('need')}")
    for r in _items(block, "results"):
        measure = measures.get(r.get("measure"))
        if measure is None:
            err(f"{r.get('id')}: the measurement result is of {r.get('measure')}, no measure "
                "defined in the strategy")
            continue
        limits = _block(measure, "acceptable")
        low, high, value = limits.get("min"), limits.get("max"), r.get("value")
        if not isinstance(value, int | float) or isinstance(value, bool):
            err(f"{r.get('id')}: the measurement result {value!r} is no number the acceptable "
                "parameters can judge")
            continue
        within = (low is None or value >= low) and (high is None or value <= high)
        if r.get("within_parameters") is not within:
            err(f"{r.get('id')}: performance outside acceptable parameters is not recorded as "
                "such")
        if missing := sorted(_strings(measure, "users") - _strings(r, "informed")):
            err(f"{r.get('id')}: the measurement users {', '.join(missing)} are not informed")
    return out


# --- MPLAN-001: the system plan's review and change records ---------------------------------

def plan_reviews(ctx: Context) -> list[RunFinding]:
    data = ctx.data(PLAN_REVIEWS_FILE)
    if not _in_play(ctx, "ART-SSP") or not isinstance(data, dict):
        return []
    out, err = _collector("MPLAN-001", PLAN_REVIEWS_FILE, "M-4")
    interval = _block(data, "schedule").get("interval_days")
    reviews = _items(data, "reviews")
    if "M-4" in scope.active_tasks(ctx.run) and len(reviews) == 0:
        err("M-4 reviews the system plan on the organization-defined schedule and logs it")
    days = sorted(d for d in (_day(r.get("date")) for r in reviews) if d)
    for earlier, later in zip(days, days[1:], strict=False):
        if isinstance(interval, int) and (later - earlier).days > interval:
            err(f"the system plan went unreviewed from {earlier} to {later}, past the "
                f"organization-defined schedule of {interval} days")
    log = {i.get("id") for i in _items(ctx.data(CHANGES_FILE), "changes")}
    for c in _items(data, "changes"):
        if c.get("change_ref") is not None and log and c.get("change_ref") not in log:
            err(f"{c.get('version')}: the system plan update is not tracked by change "
                f"management: {c.get('change_ref')} is not in the change log")
        if c.get("approved_by") not in PLAN_APPROVERS:
            err(f"{c.get('version')}: the update to the system plan is approved under change "
                f"management, by {' or '.join(PLAN_APPROVERS)}, not {c.get('approved_by')}")
    return out
