"""The authorization ledger (ART-AUTHREC): every decision of a run as a record.

A later decision is a new record, so a cATO, a continuation or a rescission never overwrites
the authorization beneath it. ``in_force`` replays the records to say what stands on a date.
A run on the contract before the ledger keeps ``decision.yaml``: ``load`` lifts it with the
conversion ``rmf run migrate`` writes, so rules read one shape.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

from rmf_tool.run.model import Run, YamlError

LEDGER_FILE = "artifacts/data/authorizations.yaml"
LEGACY_FILE = "artifacts/data/decision.yaml"
LEDGER_ARTIFACT = "ART-AUTHREC"
LEGACY_ARTIFACT = "ART-AODM"
LEGACY_TASKS = ("R-4", "M-6")  # the tasks that could write decision.yaml
LIFTED_ID = "AUTH-001"
SURVIVORS = ("decision", "decided_by", "date", "authorization_termination_date", "conditions",
             "risk_level", "rar_ref", "degraded_disclosure", "rationale", "sources")


@dataclass(frozen=True)
class Standing:
    """An authorization in force, with what is attached to it."""
    record: dict[str, Any]
    continuous: dict[str, Any] | None = None  # the AD-CATO record, while it holds
    ongoing: dict[str, Any] | None = None  # the latest AD-CONT record

    @property
    def expires(self) -> dt.date | None:
        """No date under a cATO or ongoing authorization, which lift the termination date."""
        if self.continuous or self.ongoing:
            return None
        return parse_date(self.record.get("authorization_termination_date"))


def parse_date(value: Any) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def lift(decision: dict[str, Any], kinds: dict[str, Any]) -> dict[str, Any]:
    """A decision.yaml as one ledger record. ``task`` comes from the decision type; a legacy
    AD-IATT lands on R-4, the only place decision.yaml could be written, so AODM-001 reports
    it as it always did."""
    decided_in = (kinds.get(decision.get("decision")) or {}).get("decided_in") or []
    task = next((t for t in decided_in if t in LEGACY_TASKS), LEGACY_TASKS[0])
    record: dict[str, Any] = {"id": LIFTED_ID, "subject": "system", "task": task,
                              "basis": "initial" if task == LEGACY_TASKS[0] else "time-driven",
                              "conveyed_to": ["PER-PM"]}
    record.update({k: decision[k] for k in SURVIVORS if k in decision})
    if "rationale" in decision:  # the old contract's only statement of why the risk was accepted
        record["risk_acceptance"] = decision["rationale"]
    return record


def file_of(run: Run) -> str:
    return LEDGER_FILE if LEDGER_ARTIFACT in run.artifacts else LEGACY_FILE


def artifact_of(run: Run) -> str:
    return LEDGER_ARTIFACT if LEDGER_ARTIFACT in run.artifacts else LEGACY_ARTIFACT


def load(run: Run) -> list[dict[str, Any]] | None:
    """The records, oldest first, or None when the file is missing or unreadable."""
    rel = file_of(run)
    if not run.path(rel).is_file():
        return None
    try:
        data = run.data(rel)
    except YamlError:
        return None
    if not isinstance(data, dict):
        return None
    if rel == LEGACY_FILE:
        kinds = {e.id: e.data for e in run.framework.index("decisions").values()}
        return [lift(data, kinds)]
    return [r for r in data.get("records") or [] if isinstance(r, dict)]


def effects(run: Run) -> dict[str, str]:
    return {e.id: e.data["effect"] for e in run.framework.index("decisions").values()}


def _order(record: dict[str, Any]) -> tuple[dt.date, str]:
    return parse_date(record.get("date")) or dt.date.max, str(record.get("id"))


def in_force(records: list[dict[str, Any]], effect_of: dict[str, str],
             on: dt.date | None = None) -> dict[str, Standing]:
    """Authorizations standing on a date (default: after the last record), keyed by record ID.
    A record that names a missing authorization changes nothing; AODM-005 reports it."""
    stands: dict[str, Standing] = {}
    for r in sorted(records, key=_order):
        date, ident = parse_date(r.get("date")), str(r.get("id"))
        if date is None or (on is not None and date > on):
            continue
        base, effect = r.get("underlying"), effect_of.get(r.get("decision"))
        if r.get("supersedes"):
            stands.pop(r["supersedes"], None)
        if effect in ("test", "authorize"):
            stands[ident] = Standing(r)
        elif effect in ("deny", "rescind"):
            stands.pop(base, None)
        elif base in stands:
            held = stands[base]
            if effect == "continuous":
                stands[base] = Standing(held.record, r, held.ongoing)
            elif effect == "continue":
                stands[base] = Standing(held.record, held.continuous, r)
            elif effect == "revoke-continuous":
                stands[base] = Standing(held.record, None, held.ongoing)
    if on is None:
        return stands
    return {k: s for k, s in stands.items() if s.expires is None or s.expires >= on}
