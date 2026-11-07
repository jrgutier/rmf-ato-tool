"""Ongoing authorization review events (OAUTH-001), the operations and maintenance entry of an
existing system (OMP-001) and the inputs behind a reauthorization (OMP-002). The ledger rules
read the records through ``rmf_tool.run.authorization`` and stay quiet about a missing or
unreadable file (RUN-ART-001 and RUN-FM-001 report those); OMP-001 reads run.yaml's entry."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope
from rmf_tool.run.model import RUN_FILE

Record = dict[str, Any]

AUTOMATED = "automated-tool"
EXISTING_STEPS = ("A", "R", "M")  # past implementation: the system exists (SP 800-37r2 2.4)
CONFIRMED = ("C-2", "S-1", "S-2", "I-1")  # categorized; controls selected, tailored, implemented
STANDING = ("authorize", "continue", "continuous")
REAUTH_INPUTS = {"PER-CISO": "the senior agency information security officer",
                 "PER-PRIV": "the senior agency official for privacy",
                 "PER-RE": "the risk executive (function)"}


def _records(ctx: Context) -> list[Record]:
    if not scope.produced_or_seeded(ctx.run, ledger.artifact_of(ctx.run)):
        return []
    return ctx.ledger or []


def _ordered(records: list[Record]) -> list[tuple[dt.date, Record]]:
    dated = [(ledger.parse_date(r.get("date")), r) for r in records]
    return sorted(((d, r) for d, r in dated if d is not None),
                  key=lambda x: (x[0], str(x[1].get("id"))))


def _finder(ctx: Context, rule: str) -> tuple[list[RunFinding], Callable[[Record, str], None]]:
    out: list[RunFinding] = []
    rel = ledger.file_of(ctx.run)

    def err(record: Record, message: str) -> None:
        owners = {record["task"]} if record.get("task") in ctx.run.tasks else None
        out.append(make(rule, f"{record.get('id')}: {message}", rel, None, owners))

    return out, err


def _events(record: Record) -> list[str]:
    review = record.get("review")
    events = review.get("events") if isinstance(review, dict) else None
    return [str(e) for e in events] if isinstance(events, list) else []


def _frequency(record: Record) -> int | None:
    review = record.get("review")
    days = review.get("frequency_days") if isinstance(review, dict) else None
    return days if isinstance(days, int) and not isinstance(days, bool) and days > 0 else None


# --- OAUTH-001: event-driven reviews, and the time-driven frequency beside them --------------

def review_events(ctx: Context) -> list[RunFinding]:
    out, err = _finder(ctx, "OAUTH-001")
    ordered = _ordered(_records(ctx))
    for i, (date, r) in enumerate(ordered):
        prior = [p for _, p in ordered[:i] if p.get("underlying") == r.get("underlying")]
        if r.get("basis") == "event-driven":
            _trigger(r, date, prior, err)
    return out


def _trigger(record: Record, date: dt.date, prior: list[Record],
             err: Callable[[Record, str], None]) -> None:
    trigger = record.get("trigger")
    if not isinstance(trigger, dict):
        err(record, "an event-driven review names the trigger event, who raised it and when")
        return
    day = ledger.parse_date(trigger.get("date"))
    if day is not None and day > date:
        err(record, f"the trigger of {day} follows the review it prompted on {date}")
    raised = trigger.get("raised_by")
    if raised == record.get("decided_by"):
        return  # the authorizing official may determine independently that a review is needed
    defined = {e for p in prior for e in _events(p)}
    if defined and str(trigger.get("event")) not in defined:
        err(record, f"trigger {trigger.get('event')!r} raised by {raised} is not one of the "
            f"defined trigger events ({', '.join(sorted(defined))})")


# --- OMP-001: an existing system entering past implementation --------------------------------

def existing_entry(ctx: Context) -> list[RunFinding]:
    entry = ctx.run.config.get("entry")
    out: list[RunFinding] = []
    if not isinstance(entry, dict) or entry.get("step") not in EXISTING_STEPS:
        return out

    def err(message: str) -> None:
        out.append(make("OMP-001", message, RUN_FILE, None, run_wide=True))

    task = entry.get("task")
    completed = entry.get("completed")
    done = {str(t) for t in completed} if isinstance(completed, list) else set()
    active = set(scope.active_tasks(ctx.run))
    # The Prepare tasks include P-14, the security and privacy risk assessment.
    prepare = [t for t in ctx.run.order if ctx.run.tasks[t].get("step") == "P"
               and t not in done and t not in active]
    if prepare:
        err(f"an existing system entering at {task} has not completed the Prepare tasks "
            f"{', '.join(prepare)}")
    missing = [t for t in CONFIRMED if t not in done and t not in active]
    if missing:
        err(f"an existing system entering at {task} has not confirmed {', '.join(missing)} "
            "completed")
    if entry.get("step") != "M":
        return out
    deficiencies = entry.get("deficiencies")
    if not isinstance(deficiencies, list):
        err(f"an entry at {task} lists the deficiencies the gap analysis found, an empty list "
            "when none")
    elif deficiencies:
        listed = "; ".join(map(str, deficiencies))
        err(f"the gap analysis found control deficiencies ({listed}); address them at "
            "implementation, assessment and authorization before entering at monitoring")
    effect_of = ledger.effects(ctx.run)
    earlier = [r for r in _records(ctx) if r.get("task") not in active]
    held = {effect_of.get(s.record.get("decision"))
            for s in ledger.in_force(earlier, effect_of).values()}
    if held.isdisjoint(STANDING):
        err(f"an entry at {task} needs a current authorization in effect; without one the run "
            "continues with assessment and authorization")
    return out


# --- OMP-002: the inputs to a decision to reauthorize -----------------------------------------

def reauthorization_inputs(ctx: Context) -> list[RunFinding]:
    out, err = _finder(ctx, "OMP-002")
    for r in _records(ctx):
        if r.get("basis") != "reauthorization":
            continue
        date = ledger.parse_date(r.get("date"))
        given = r.get("initiation_inputs")
        inputs = [i for i in given if isinstance(i, dict)] if isinstance(given, list) else []
        by = {str(i.get("by")): ledger.parse_date(i.get("date")) for i in inputs}
        lacking = [name for per, name in REAUTH_INPUTS.items() if per not in by]
        if lacking:
            err(r, f"the decision to reauthorize includes no input from {', '.join(lacking)}")
        late = sorted(per for per, day in by.items()
                      if day is not None and date is not None and day > date)
        if late:
            err(r, f"the input from {', '.join(late)} is dated after the reauthorization")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("OAUTH-001", review_events), ("OMP-001", existing_entry),
                ("OMP-002", reauthorization_inputs))
