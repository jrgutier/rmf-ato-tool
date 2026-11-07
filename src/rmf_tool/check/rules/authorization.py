"""The authorization ledger: AODM-001 to AODM-007, AODM-009 to AODM-011 and AOCHG-001, the
Enterprise boarding and receipt of ENT-001 and ENT-002, and AUTHRPT-001 on what follows a decision.
Each reads the records through ``rmf_tool.run.authorization`` and stays quiet about a missing
or unreadable file (RUN-ART-001 and RUN-FM-001 report those), except AUTHRPT-001: ART-AUTHRPT is
not a core artifact, so RUN-ART-001 never demands its data and the rule must. A record's findings
belong to the task that wrote it. These rules test progress, not scope: a decision type has to be
reachable in the run as it stands on disk, so a task merely being in scope never excuses a record
written ahead of it."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope, status
from rmf_tool.run.model import YamlError

ATO_TYPES = ("AD-ATO", "AD-ATOC")
ELEVATED_RISK = ("high", "very-high")  # DoDI 8510.01 4.3.c(7): "Very High" or "High"
RECEIVERS = {"system": "PER-PM", "common-controls": "PER-CCP"}
SAP_FILE = "artifacts/data/sap.yaml"
RAR_EFFECTS = ("authorize", "deny")
COMPLETE_REVIEW = ("initial", "reauthorization")  # SP 800-37r2 p. 168: a zero-based review
ORG_CONTEXT = "artifacts/ART-ORG-CONTEXT.md"  # holds the risk tolerance (P-2)
RAR_FILE = "artifacts/data/rar.yaml"
REPORT_FILE = "artifacts/data/authorization-report.yaml"
OPERATIONAL_COMMANDERS = "PER-OPCDR"
ACQUISITION_REPRESENTATIVES = frozenset({"PER-PM", "PER-MDA"})
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
POAM_FILE = "artifacts/poam/items.yaml"
SAR_DIR = "artifacts/sar/"
# DoD CIO reciprocity memo 4.2.1.b.
DSAWG_DOCUMENTS = ("ART-SSP", "ART-SAR", "ART-RAR", "ART-POAM", "ART-AODM")
BRIEF_LEAD_BUSINESS_DAYS = 60  # DoD CIO reciprocity memo 4.2.1.h
AO_DECISION_DOCUMENTS = frozenset({"ART-AODM", "ART-AUTHREC"})  # SP 800-37r2 p. 172
AO_PACKAGE_OR_REPORT = frozenset({"ART-PKG", "ART-SECRPT"})
AO_AUTOMATED_REPORT = "ART-SECRPT"  # a report from automated security management tools
AO_RESPONSES = {"acceptable": ("signed-decision",),
                "unacceptable": ("authorization-action", "new-terms", "denial")}
AO_ACTIONS = ("ongoing-authorization", "reauthorization")
AO_ACCEPTS = frozenset({"organizational-operations", "organizational-assets", "individuals",
                        "other-organizations", "the-nation"})
Record = dict[str, Any]


def _kinds(ctx: Context) -> dict[str, dict[str, Any]]:
    return {e.id: e.data for e in ctx.run.framework.index("decisions").values()}


def _rule(ctx: Context, rule: str) -> tuple[list[RunFinding], Callable[[Record, str], None]]:
    out: list[RunFinding] = []
    rel = ledger.file_of(ctx.run)

    def err(record: Record, message: str) -> None:
        owners = {record["task"]} if record.get("task") in ctx.run.tasks else None
        out.append(make(rule, f"{record.get('id')}: {message}", rel, None, owners))

    return out, err


def _records(ctx: Context) -> list[Record]:
    if not scope.produced_or_seeded(ctx.run, ledger.artifact_of(ctx.run)):
        return []
    return ctx.ledger or []


def _typed(ctx: Context) -> Iterator[tuple[Record, dict[str, Any]]]:
    kinds = _kinds(ctx)
    for record in _records(ctx):
        kind = kinds.get(record.get("decision"))
        if kind is not None:
            yield record, kind


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _before(records: list[Record], record: Record) -> list[Record]:
    """The records written before this one, by date and then ID."""
    mine = (_day(record.get("date")) or dt.date.max, str(record.get("id")))
    return [r for r in records
            if (_day(r.get("date")) or dt.date.max, str(r.get("id"))) < mine]


def _one_year_before(day: dt.date) -> dt.date:
    try:
        return day.replace(year=day.year - 1)
    except ValueError:  # 29 February
        return day.replace(year=day.year - 1, day=28)


# --- AODM-001: each record, against its decision type and the run's progress ---------------

def records_valid(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-001")
    run, kinds = ctx.run, _kinds(ctx)
    records = _records(ctx)
    # A seeded ledger holds decisions taken outside this run, so a record at a task the run does
    # not carry out is accepted. A task the run does carry out is still judged on its progress.
    is_seeded = any(s.get("artifact") == ledger.artifact_of(run) for s in scope.seeded(run))
    active = set(scope.active_tasks(run))
    seen: set[Any] = set()
    for r in records:
        if r.get("id") in seen:
            err(r, "this record ID is used twice")
        seen.add(r.get("id"))
        kind = kinds.get(r.get("decision"))
        if kind is None:
            err(r, f"{r.get('decision')!r} is not one of the decision types: {', '.join(kinds)}")
            continue
        decided_in, task = kind.get("decided_in") or [], r.get("task")
        if task not in decided_in:
            err(r, f"{r['decision']} is decided in {', '.join(decided_in)}, not in {task}")
        elif task not in active:
            if not is_seeded:
                err(r, f"{task} is not an active task of this run")
        elif not status.reached(run, task):
            err(r, f"{r['decision']} is recorded at {task}, but the tasks before {task} have not "
                "written their outputs")
        if kind.get("atd_required") and not r.get("authorization_termination_date"):
            err(r, f"{r['decision']} needs an authorization_termination_date")
        if kind.get("conditions_required") and not r.get("conditions"):
            err(r, f"{r['decision']} needs conditions")
        if kind.get("effect") in RAR_EFFECTS and r.get("rar_ref") != "ART-RAR":
            err(r, "no rar_ref: ART-RAR (the decision must rest on the risk assessment report)")
        if (ctx.degraded_refs and kind.get("effect") in RAR_EFFECTS
                and not str(r.get("degraded_disclosure") or "").strip()):
            err(r, f"the run depends on degraded reference(s) {', '.join(ctx.degraded_refs)}; "
                "add a degraded_disclosure (plan §7.6)")
    doc = ctx.docs.get(f"artifacts/{ledger.LEDGER_ARTIFACT}.md")
    touched = (doc.data or {}).get("touched_by") or [] if doc else []
    for task in ("R-4", "M-6"):
        if task in touched and task in active and not any(r.get("task") == task for r in records):
            out.append(make("AODM-001", f"{task} touched {ledger.LEDGER_ARTIFACT} but recorded no "
                            "decision", ledger.file_of(run), None, {task}))
    return out


# --- AODM-009: who decides, on what, and who is told ----------------------------------------

def parties_valid(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-009")
    for r, kind in _typed(ctx):
        if r.get("decided_by") != kind.get("decided_by"):
            err(r, f"{r['decision']} is decided by {kind.get('decided_by')}, not "
                f"{r.get('decided_by')}")
        if r.get("subject") not in kind.get("applies_to", ()):
            err(r, f"{r['decision']} decides on {', '.join(kind['applies_to'])}, not "
                f"{r.get('subject')}")
        receivers = r.get("conveyed_to")
        if not isinstance(receivers, list) or RECEIVERS.get(r.get("subject")) not in receivers:
            err(r, f"the decision is not conveyed to {RECEIVERS.get(r.get('subject'))}")
    return out


# --- AODM-002: termination date, review and frequency --------------------------------------

def termination_valid(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-002")
    for r, kind in _typed(ctx):
        date, atd = _day(r.get("date")), _day(r.get("authorization_termination_date"))
        requires = kind.get("requires") or ()
        if atd is not None and kind.get("atd_forbidden"):
            err(r, f"{r['decision']} carries no authorization_termination_date")
        if atd is not None and date is not None:
            if atd <= date:
                err(r, f"the termination date {atd} is not after the decision date {date}")
            limit = kind.get("max_term_days")
            if limit and (atd - date).days > limit:
                err(r, f"the term of {(atd - date).days} days exceeds {r['decision']}'s limit of "
                    f"{limit} days")
        if "review" in requires and not r.get("review"):
            err(r, f"{r['decision']} needs review: a time-driven frequency and event triggers")
        if "ongoing_acknowledgment" in requires and not r.get("ongoing_acknowledgment"):
            err(r, f"{r['decision']} needs ongoing_acknowledgment: the AO accepts the ongoing "
                "process")
        if r.get("basis") in ("time-driven", "event-driven") and not r.get("review"):
            err(r, f"a {r['basis']} decision records the review that triggered it")
        if r.get("basis") == "time-driven" and date is not None:
            _late_review(r, date, _before(_records(ctx), r), err)
    return out


def _late_review(record: Record, date: dt.date, prior: list[Record],
                 err: Callable[[Record, str], None]) -> None:
    """A time-driven review falls within the frequency the last review on this authorization
    set."""
    last = [r for r in prior if isinstance(r.get("review"), dict)
            and r.get("underlying") == record.get("underlying")]
    if not last:
        return
    since, days = _day(last[-1].get("date")), last[-1]["review"].get("frequency_days")
    if since is not None and days and (date - since).days > days:
        err(record, f"this review comes {(date - since).days} days after {last[-1].get('id')}, "
            f"past its {days}-day frequency")


# --- AODM-003: Component CIO position before an ATO at High or Very High --------------------

def cio_concurrence(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-003")
    for r, _ in _typed(ctx):
        if r["decision"] not in ATO_TYPES or r.get("risk_level") not in ELEVATED_RISK:
            continue
        position = r.get("cio_concurrence")
        if not isinstance(position, dict):
            err(r, f"an ATO at {r['risk_level']} risk needs cio_concurrence before it is issued")
            continue
        when, date = _day(position.get("date")), _day(r.get("date"))
        if position.get("by") != "PER-CIO":
            err(r, f"cio_concurrence is by {position.get('by')}, not PER-CIO")
        if when is not None and date is not None and when > date:
            err(r, f"the Component CIO's position, {when}, follows the decision, {date}")
        if position.get("position") == "non-concur" and not position.get("directions"):
            err(r, "a non-concurrence records the CIO's directions")
    return out


# --- AODM-004: Intelligence Community threat assessment within 12 months ---------------------

def threat_assessment(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-004")
    for r, kind in _typed(ctx):
        if "threat_assessment" not in (kind.get("requires") or ()):
            continue
        found = r.get("threat_assessment")
        if not isinstance(found, dict):
            err(r, f"{r['decision']} needs threat_assessment (DoDI 5000.90 p. 11)")
            continue
        date, issued = _day(r.get("date")), _day(found.get("issued"))
        reviewed = _day(found.get("reviewed"))
        if found.get("reviewed_by") != "PER-PM":
            err(r, f"the PM reviews the threat assessment, not {found.get('reviewed_by')}")
        if date is None or issued is None or reviewed is None:
            continue
        if issued > date or issued < _one_year_before(date):
            err(r, f"the threat assessment of {issued} was not issued within the 12 months "
                f"before the decision of {date}")
        if reviewed > date or reviewed < issued:
            err(r, f"the review of {reviewed} does not fall between the assessment and the "
                "decision")
    return out


# --- AODM-005: what a record rests on -------------------------------------------------------

def chain(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-005")
    records = _records(ctx)
    by_id = {r.get("id"): r for r in records}
    effect_of = ledger.effects(ctx.run)
    for r, kind in _typed(ctx):
        effect, requires = kind.get("effect"), kind.get("requires") or ()
        base = r.get("underlying")
        needs_base = "underlying" in requires or (effect == "deny" and r.get("task") == "M-6")
        if needs_base and not base:
            err(r, f"{r['decision']} names the authorization it rests on in underlying")
        date = _day(r.get("date"))
        prior = _before(records, r)
        if base:
            stands = ledger.in_force(prior, effect_of, date)
            if base not in stands:
                err(r, f"underlying {base} is not in force on {date}")
            elif effect == "revoke-continuous" and stands[base].continuous is None:
                err(r, f"underlying {base} has no cATO to revoke")
            elif effect == "continue" and stands[base].record.get("basis") not in COMPLETE_REVIEW:
                err(r, f"ongoing authorization rests on an initial authorization from a complete "
                    f"review; {base} has basis {stands[base].record.get('basis')}")
        if "revocation_reason" in requires and not r.get("revocation_reason"):
            err(r, f"{r['decision']} records its revocation_reason")
        if "provider" in requires:
            provider = r.get("provider")
            if not isinstance(provider, dict):
                err(r, f"{r['decision']} names the provider and its completed ATO")
            elif date is not None and (_day(provider.get("date")) or date) > date:
                err(r, f"the provider's ATO of {provider.get('date')} follows the decision")
        replaced = by_id.get(r.get("supersedes"))
        if effect == "authorize":
            standing = [i for i, held in ledger.in_force(prior, effect_of, date).items()
                        if effect_of.get(held.record.get("decision")) == "authorize"
                        and i != r.get("supersedes")]
            if standing:
                err(r, f"a system has a single authorization, and {standing[0]} is in force; "
                    "name it in supersedes")
        if r.get("supersedes") and replaced not in prior:
            err(r, f"supersedes {r['supersedes']}, which is not an earlier record")
        if r.get("basis") == "reauthorization" and not r.get("supersedes"):
            err(r, "a reauthorization names the record it supersedes")
        if r.get("basis") == "ao-change":
            if not r.get("supersedes") or not r.get("ao_transfer"):
                err(r, "a change of AO names the record it supersedes and the ao_transfer")
            atd, old = (_day(x.get("authorization_termination_date")) if x else None
                        for x in (r, replaced))
            if atd is not None and old is not None and atd > old:
                err(r, f"a new AO's terms cannot extend the termination date {old} to {atd}")
    return out


# --- AOCHG-001: the new authorizing official's review, finding and response -----------------

def ao_change(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AOCHG-001")
    for r, kind in _typed(ctx):
        if r.get("basis") != "ao-change" or not isinstance(r.get("ao_transfer"), dict):
            continue
        transfer = r["ao_transfer"]
        reviewed = set(transfer.get("reviewed") or ())
        # SP 800-37r2 p. 172: the decision document and package, or the automated report alone
        if AO_AUTOMATED_REPORT not in reviewed and (
                not reviewed & AO_DECISION_DOCUMENTS or not reviewed & AO_PACKAGE_OR_REPORT):
            err(r, "the new authorizing official has not reviewed the current authorization "
                f"decision document and the package or a report: {', '.join(sorted(reviewed))}")
        if transfer.get("incoming") == transfer.get("outgoing"):
            err(r, f"responsibility is not transferred: {transfer.get('incoming')} is both "
                "outgoing and incoming")
        finding, response = transfer.get("risk_finding"), transfer.get("response")
        if response not in AO_RESPONSES.get(finding, ()):
            err(r, f"a new authorizing official who finds the current risk {finding} answers "
                f"with {' or '.join(AO_RESPONSES.get(finding, ('a known finding',)))}, not "
                f"{response}")
        if response == "signed-decision" and kind.get("effect") not in ("authorize", "continuous"):
            err(r, "acceptable risk is a new or updated authorization decision document, not "
                f"{r.get('decision')}")
        if response == "authorization-action" and transfer.get("action") not in AO_ACTIONS:
            err(r, f"an authorization action is {' or '.join(AO_ACTIONS)}, not "
                f"{transfer.get('action')}")
        if response == "signed-decision" \
                and (gap := sorted(AO_ACCEPTS - set(transfer.get("accepts_risk_to") or ()))):
            err(r, f"the new authorizing official does not explicitly accept the risk to "
                f"{', '.join(gap)}")
    return out


# --- AODM-006: live test events are authorized ----------------------------------------------

def live_events(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-SAP"):
        return []
    try:
        sap = ctx.data(SAP_FILE) if run.path(SAP_FILE).is_file() else None
    except YamlError:
        return []
    schedule = sap.get("schedule") if isinstance(sap, dict) else None
    events = (schedule.get("events") or []) if isinstance(schedule, dict) else []
    out = []
    effect_of = ledger.effects(run)
    records = _records(ctx)
    for event in events:
        day = _day(event.get("date")) if isinstance(event, dict) and event.get("live") else None
        if day and not ledger.in_force(records, effect_of, day):
            out.append(make("AODM-006", f"live test event {event.get('description')!r} on {day} "
                            "falls under no IATT or authorization in force",
                            ledger.file_of(run), None, {"A-2"}))
    return out


# --- AODM-007: cATO eligibility -------------------------------------------------------------

def cato_eligible(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-007")
    records = {r.get("id"): r for r in _records(ctx)}
    facts = facts_mod.load(ctx.run)
    acquisition = facts.get("acquisition") if isinstance(facts, dict) else None
    for r, kind in _typed(ctx):
        if kind.get("effect") != "continuous":
            continue
        date = _day(r.get("date"))
        approval, notice = r.get("dod_ciso_approval"), r.get("component_ciso_notification")
        requires = kind.get("requires") or ()
        if not isinstance(approval, dict):
            if "dod_ciso_approval" in requires:
                err(r, "a cATO needs a recorded dod_ciso_approval")
        elif date is not None and (_day(approval.get("date")) or date) > date:
            err(r, f"the DoD CISO approval of {approval.get('date')} follows the decision")
        if not isinstance(notice, dict):
            if "component_ciso_notification" in requires:
                err(r, "the AO notifies the Component CISO first: component_ciso_notification")
        elif isinstance(approval, dict) and (
                (_day(notice.get("date")) or dt.date.min)
                > (_day(approval.get("date")) or dt.date.max)):
            err(r, "the Component CISO notice follows the DoD CISO approval")
        base = records.get(r.get("underlying")) or {}
        if base and base.get("decision") not in ATO_TYPES:
            err(r, f"a cATO rests on an ATO, not {base.get('decision')}")
        if not isinstance(acquisition, dict):
            err(r, "a cATO depends on the pathway: set facts.acquisition")
            continue
        if acquisition.get("pathway") not in (kind.get("allowed_pathways") or ()):
            err(r, f"a cATO is limited to {', '.join(kind['allowed_pathways'])}, not "
                f"{acquisition.get('pathway')}")
        if acquisition.get("product_kind") in (kind.get("excluded_product_kinds") or ()):
            err(r, f"{acquisition.get('product_kind')} programs cannot hold a cATO")
    return out


# --- AODM-010: the risk executive before the final decision -----------------------------------

def _unconsidered(ctx: Context, record: Record) -> list[str]:
    """What SP 800-37r2 p. 92 has a decision consider, and the run does not hold."""
    missing = []
    if not record.get("risk_level"):
        missing.append("the current residual risk")
    if not isinstance(ctx.data(POAM_FILE), dict):
        missing.append("the plans of action and milestones")
    if ORG_CONTEXT not in ctx.docs:
        missing.append("the risk tolerance of the organization")
    return missing


def risk_executive(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-010")
    rar = ctx.data(RAR_FILE)
    determination = (rar.get("determination") if isinstance(rar, dict) else None) or {}
    for r, kind in _typed(ctx):
        if "risk_executive" not in (kind.get("requires") or ()):
            continue
        found = r.get("risk_executive")
        if not isinstance(found, dict):
            err(r, f"{r['decision']} needs risk_executive: the authorizing official consults the "
                "risk executive (function) first")
            continue
        date, consulted = _day(r.get("date")), _day(found.get("consulted"))
        if found.get("by") != "PER-RE":
            err(r, f"the risk executive (function) is consulted, not {found.get('by')}")
        if date is not None and consulted is not None and consulted > date:
            err(r, f"the consultation of {consulted} follows the final authorization decision of "
                f"{date}")
        if found.get("analyzed_by") != "PER-AO":
            err(r, "the authorizing official analyzes the risk executive (function) input, not "
                f"{found.get('analyzed_by')}")
        if missing := _unconsidered(ctx, r):
            err(r, f"the authorization decision does not consider {', '.join(missing)}")
        given = determination.get("risk_executive_input")
        if given and found.get("input_relevant", True) and found.get("input") != given:
            err(r, "the risk executive (function) input from R-2 is not documented in the "
                "authorization decision")
        privacy = r.get("privacy_coordination") or {}
        coordinated, reviewed = privacy.get("by"), _day(privacy.get("date"))
        if ctx.processes_pii and kind.get("effect") == "authorize" \
                and coordinated != "PER-PRIV":
            err(r, "a system processing PII coordinates the authorization decision with the "
                f"privacy official, not {coordinated}")
        elif ctx.processes_pii and date is not None and reviewed is not None and reviewed > date:
            err(r, f"the privacy official reviewed the authorization package on {reviewed}, "
                f"after the authorization decision of {date}")
    return out


# --- AODM-011: where an authorization issue goes ----------------------------------------------

def issues(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "AODM-011")
    items = ledger.section(ctx.run, "issues")
    for issue in items:
        kind, forum = issue.get("kind"), issue.get("forum")
        if kind == "mission-area" and forum != "PAO":
            err(issue, f"an authorization issue within a mission area is resolved by its PAO, not "
                f"{forum}")
        if kind == "space-system" and forum != "USSPACECOM":
            err(issue, "an authorization issue for space systems is resolved by USSPACECOM, not "
                f"{forum}")
        if kind == "community-risk" and forum != "DSAWG":
            err(issue, "an authorization issue on sharing community risk goes to the DSAWG forum, "
                f"not {forum}")
        if kind == "process-dispute" and forum != "DOD-CISO":
            err(issue, "a dispute among RMF and other processes follows the escalation procedures "
                f"of the DoD CISO, not {forum}")
        if kind in ("dsawg-appeal", "isrmc-direction") and forum != "ISRMC":
            err(issue, f"a {kind} goes to the DoD ISRMC, not {forum}")
        resolved, raised = _day(issue.get("resolved")), _day(issue.get("raised"))
        if issue.get("status") == "resolved" and (
                resolved is None or not issue.get("resolution")):
            err(issue, "a resolved issue records its date and its resolution")
        elif resolved is not None and raised is not None and resolved < raised:
            err(issue, f"resolved on {resolved}, before it was raised on {raised}")
    effect_of = ledger.effects(ctx.run)
    for r, _ in _typed(ctx):
        date = _day(r.get("date"))
        if date is None or effect_of.get(r.get("decision")) != "authorize":
            continue
        for issue in items:
            raised = _day(issue.get("raised")) or dt.date.max
            complied = _day(issue.get("resolved")) if issue.get("status") == "resolved" else None
            if issue.get("kind") == "isrmc-direction" and raised <= date \
                    and (complied or dt.date.max) > date:
                err(r, f"the AO complies with DoD ISRMC direction {issue.get('id')} before this "
                    "decision")
    return out


# --- ENT-001: Enterprise boarding at the DSAWG and the DoD ISRMC -------------------------------

def _federal_holidays(year: int) -> set[dt.date]:
    """5 U.S.C. 6103: a fixed date falling on a weekend is observed on the nearest weekday."""
    def nth(month: int, weekday: int, n: int) -> dt.date:
        first = dt.date(year, month, 1)
        return first + dt.timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))

    def observed(day: dt.date) -> dt.date:
        return day + dt.timedelta(days={5: -1, 6: 1}.get(day.weekday(), 0))

    fixed = [(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)]
    last_monday = nth(5, 0, 5) if nth(5, 0, 5).month == 5 else nth(5, 0, 4)
    return {*(observed(dt.date(year, m, d)) for m, d in fixed), nth(1, 0, 3), nth(2, 0, 3),
            last_monday, nth(9, 0, 1), nth(10, 0, 2), nth(11, 3, 4)}


def business_days_between(start: dt.date, end: dt.date) -> int:
    """Weekdays after ``start`` up to and including ``end``, federal holidays excepted."""
    days = (start + dt.timedelta(days=n + 1) for n in range((end - start).days))
    return sum(1 for d in days if d.weekday() < 5
               and d not in _federal_holidays(d.year) | _federal_holidays(d.year + 1))


def _enterprise_ato(record: Record, deployment: Record, boardings: dict[Any, Record],
                    err: Callable[[Record, str], None]) -> None:
    boarding = boardings.get(deployment.get("boarding")) or {}
    isrmc = boarding.get("isrmc") or {}
    date, decided = _day(record.get("date")), _day(isrmc.get("decided"))
    if isrmc.get("outcome") == "approved" and decided is None:
        err(record, "the ISRMC approval carries no date, so nothing shows it came first")
    elif isrmc.get("outcome") != "approved" or (decided or dt.date.max) > (date or dt.date.min):
        err(record, "an Enterprise system receives its ATO only after the ISRMC approves it")
    elif deployment.get("version") != boarding.get("version"):
        err(record, f"the ATO is for the version being deployed, {boarding.get('version')}, not "
            f"{deployment.get('version')}")


def _submitted(boarding: Record) -> dt.date:
    return _day((boarding.get("dsawg_submission") or {}).get("date")) or dt.date.min


def _follows_disapproval(boarding: Record, boardings: dict[Any, Record]) -> bool:
    """Whether this is a re-boarding, named or not: the last decided boarding before it was a
    disapproval, so leaving out ``reboarding_of`` escapes nothing."""
    named = boardings.get(boarding.get("reboarding_of")) or {}
    if (named.get("isrmc") or {}).get("outcome") == "disapproved":
        return True
    earlier = sorted((b for b in boardings.values()
                      if _submitted(b) < _submitted(boarding)), key=_submitted)
    outcomes = [o for b in earlier
                if (o := (b.get("isrmc") or {}).get("outcome")) in ("approved", "disapproved")]
    return outcomes[-1:] == ["disapproved"]


def _boarding(boarding: Record, boardings: dict[Any, Record], poam: dict[Any, Record],
              err: Callable[[str], None]) -> None:
    submission, isrmc = boarding.get("dsawg_submission") or {}, boarding.get("isrmc") or {}
    if missing := [d for d in DSAWG_DOCUMENTS if d not in (submission.get("documents") or ())]:
        err(f"the DSAWG submission lacks {', '.join(missing)}")
    if not submission.get("sites"):
        err("the DSAWG submission lists no deployment sites and dates")
    for brief in boarding.get("status_briefs") or ():
        requested, briefed = _day(brief.get("requested")), _day(brief.get("briefed"))
        if briefed is None or (requested is not None and briefed < requested):
            err(f"the DSAWG requested an authorization status brief on {requested}, and none "
                "answered it")
    briefed = _day(isrmc.get("briefed"))
    dates = [isrmc.get("planned_deployment"),
             *(s.get("deployment") for s in submission.get("sites") or ())]
    planned = min((d for d in map(_day, dates) if d is not None), default=None)
    if briefed is not None and planned is not None and (
            briefed >= planned
            or business_days_between(briefed, planned) < BRIEF_LEAD_BUSINESS_DAYS):
        err(f"the ISRMC is briefed no later than {BRIEF_LEAD_BUSINESS_DAYS} business days before "
            f"the planned deployment of {planned}, not on {briefed}")
    outcome = isrmc.get("outcome")
    decided = _day(isrmc.get("decided"))
    recommended = _day((boarding.get("dsawg_recommendation") or {}).get("date"))
    if outcome in ("approved", "disapproved") and (
            recommended is None or (decided is not None and recommended > decided)):
        err("the ISRMC decides on the DSAWG recommendation, which must come first")
    if outcome == "disapproved" and isrmc.get("guidance_via") != "DSAWG":
        err("ISRMC guidance on actions and mitigations reaches the Granting organization through "
            "the DSAWG")
    if _follows_disapproval(boarding, boardings) \
            and (boarding.get("adjustments") or {}).get("worked_with") != "DSAWG":
        err("the Granting AO works with the DSAWG to adjust the Enterprise system")
    if outcome != "approved":
        return
    if unmet := [p for p in isrmc.get("directed_risks") or ()
                 if (poam.get(p) or {}).get("status") != "completed"]:
        err(f"the ISRMC will not grant its approval until {', '.join(unmet)} are mitigated in the "
            "POA&M")
    if isrmc.get("monitored_by") != "ISRMC" or isrmc.get("dodin_connection") != "authorized":
        err("the ISRMC monitors the residual risk and authorizes connection to the DoDIN")
    reboarded = {b.get("reboarding_of") for b in boardings.values()}
    for change in boarding.get("risk_changes") or ():
        if change.get("mitigated") is not True and boarding.get("id") not in reboarded:
            err(f"the change in the acceptability of risk of {change.get('date')} cannot be "
                "mitigated and requires a re-boarding at the ISRMC")


def enterprise_boarding(ctx: Context) -> list[RunFinding]:
    out, err = _rule(ctx, "ENT-001")
    boardings = {b.get("id"): b for b in ledger.section(ctx.run, "boardings")}
    for r, kind in _typed(ctx):
        if "deployment" not in (kind.get("requires") or ()):
            continue
        deployment = r.get("deployment")
        if not isinstance(deployment, dict):
            err(r, f"{r['decision']} needs deployment: whether this is an Enterprise system")
        elif deployment.get("scope") == "enterprise":
            _enterprise_ato(r, deployment, boardings, err)
    data = ctx.data(POAM_FILE)
    items = data.get("items") if isinstance(data, dict) else None
    poam = {i.get("id"): i for i in items or ()}
    for boarding in boardings.values():
        _boarding(boarding, boardings, poam,
                  lambda message, b=boarding: err({**b, "task": "R-4"}, message))
    return out


# --- ENT-002: an Enterprise system this organization receives ---------------------------------

def enterprise_received(ctx: Context) -> list[RunFinding]:
    data = ctx.data(LEVERAGED_FILE)
    items = data.get("leveraged_authorizations") if isinstance(data, dict) else None
    out = []

    def err(item: Record, message: str) -> None:
        out.append(make("ENT-002", f"{item.get('id')}: {message}", LEVERAGED_FILE))

    for item in items or ():
        found = item.get("enterprise")
        if not isinstance(found, dict):
            continue
        if found.get("accepted_by") != "DoD ISRMC":
            err(item, "enterprise level risk acceptance is a determination of the DoD ISRMC, not "
                f"{found.get('accepted_by')}")
        elif found.get("receiving_action") == "refuse":
            err(item, "the receiving organization may not refuse to deploy a system the DoD ISRMC "
                "accepted")
        if (found.get("change_request") or {}).get("approved_on") != "isrmc-risk-acceptance":
            err(item, "the ISRMC risk acceptance is the RMF artifact that approves the change "
                "request")
    return out


# --- AUTHRPT-001: receipt, retention and verification after the decision ----------------------

def report_valid(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-AUTHRPT"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("AUTHRPT-001", message, REPORT_FILE, None, {"R-5"}))

    report = ctx.data(REPORT_FILE)
    if not isinstance(report, dict):
        err("no authorization report data: R-5 records the receipt, retention and marking")
        return out
    records = {r.get("id"): r for r in ctx.ledger or []}
    record = records.get(report.get("decision_ref"))
    if record is None:
        err(f"decision_ref {report.get('decision_ref')} is no record of the ledger")
        return out
    receiver = RECEIVERS.get(record.get("subject"))
    receipt, retention = report.get("receipt") or {}, report.get("retention") or {}
    if receipt.get("received_by") != receiver:
        err(f"the authorization decision and package are received by {receiver}, not "
            f"{receipt.get('received_by')}")
    date, received = _day(record.get("date")), _day(receipt.get("received"))
    if date is not None and received is not None and received < date:
        err(f"the receipt of {received} precedes the authorization decision of {date}")
    if retention.get("retained_by") != receiver:
        err(f"{receiver} retains the authorization decision and package, not "
            f"{retention.get('retained_by')}")
    available = report.get("available_to") or ()
    if missing := [p for p in record.get("conveyed_to") or () if p not in available]:
        err(f"authorization documents are not available to {', '.join(missing)}")
    until = _day(retention.get("retain_until"))
    term = _day(record.get("authorization_termination_date"))
    if until is not None and term is not None and until < term:
        err(f"authorization decision information is retained only to {until}, before the "
            f"termination date {term}")
    verifier = (report.get("terms_verification") or {}).get("verified_by")
    if verifier != "PER-AO":
        err(f"the authorizing official verifies the terms and conditions, not {verifier}")
    kept = report.get("assessment_records") or ()
    if gone := [p for p in kept if not run.path(p).is_file()]:
        err(f"the retained assessment records {', '.join(gone)} do not exist")
    if missing := [d for d in (SAP_FILE, SAR_DIR) if not any(p.startswith(d) for p in kept)]:
        err(f"the assessment records retained for the audit trail lack {', '.join(missing)}")
    _operational_awareness(ctx, report.get("operational_awareness"), err)
    return out


def _items(value: Any) -> list[dict[str, Any]]:
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _persona_ids(value: Any) -> set[str]:
    return {p for p in value if isinstance(p, str)} if isinstance(value, list) else set()


def _operational_awareness(ctx: Context, aware: Any, err: Callable[[str], None]) -> None:
    """DoDI 8510.01 4.4.a(9) and (10): the AO verifies the operational commanders have the
    system's cyber risk information, and facilitates coordination with them and with the
    acquisition or procurement representatives on each risk that affects an operational
    requirement."""
    if not isinstance(aware, dict):
        err("the report records no operational_awareness: the AO verifies the operational "
            "commanders have the cyber risk information on the system")
        return
    if OPERATIONAL_COMMANDERS not in _persona_ids(aware.get("informed")):
        err("the cyberspace and functional operational commanders are not among the officials "
            "verified to have the necessary cyber risk information on the system")
    rar = ctx.data(RAR_FILE)
    risks = {r.get("id") for r in _items(rar.get("risks") if isinstance(rar, dict) else None)}
    for item in _items(aware.get("affected_requirements")):
        risk, parties = item.get("risk"), _persona_ids(item.get("coordinated_with"))
        if risk not in risks:
            err(f"{risk} affects an operational requirement but is no risk of {RAR_FILE}")
        if OPERATIONAL_COMMANDERS not in parties:
            err(f"{risk} affects an operational requirement and its coordination leaves out the "
                "cyberspace and functional operational commanders")
        if ACQUISITION_REPRESENTATIVES.isdisjoint(parties):
            err(f"{risk} affects an operational requirement and its coordination leaves out the "
                "acquisition or procurement representatives")
