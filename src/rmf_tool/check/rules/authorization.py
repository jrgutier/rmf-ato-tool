"""The authorization ledger: AODM-001 to AODM-007. Each reads the records through
``rmf_tool.run.authorization`` and stays quiet about a missing or unreadable file (RUN-ART-001
and RUN-FM-001 report those). A record's findings belong to the task that wrote it. These rules
test progress, not scope: a decision type has to be reachable in the run as it stands on disk,
so a task merely being in scope never excuses a record written ahead of it."""

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
            err(r, f"decision {r.get('decision')!r} is not one of {', '.join(kinds)}")
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
        if r.get("decided_by") != kind.get("decided_by"):
            err(r, f"{r['decision']} is decided by {kind.get('decided_by')}, not "
                f"{r.get('decided_by')}")
        if r.get("subject") not in kind.get("applies_to", ()):
            err(r, f"{r['decision']} decides on {', '.join(kind['applies_to'])}, not "
                f"{r.get('subject')}")
        receivers = r.get("conveyed_to")
        if not isinstance(receivers, list) or RECEIVERS.get(r.get("subject")) not in receivers:
            err(r, f"the decision is not conveyed to {RECEIVERS.get(r.get('subject'))}")
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
            err(r, f"a cATO is not for {acquisition.get('product_kind')} programs")
    return out
