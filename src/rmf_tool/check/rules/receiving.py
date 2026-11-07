"""The receiving side of an authorization done elsewhere: RECIP-001 on the customer's review of a
provider's authorization package (SP 800-37r2 Appendix F, DoD CIO reciprocity 4.5), RECIP-002 on
the controls the customer adds, RECIP-003 on a system its Granting organization stops supporting,
and RECIP-004 on a system another organization authorized and this one now owns (CNSSI 1254
Annex D 3.c and 3.e, DoD CIO reciprocity 3.3).

The Granting and Receiving records of a reciprocity agreement are judged elsewhere; these rules
read leveraged-authorizations.yaml and system-description.yaml only."""

from __future__ import annotations

import datetime as dt
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.check.rules.coverage import CORE_DOCUMENTS
from rmf_tool.run import authorization as ledger
from rmf_tool.run import scope

LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
SYSTEM_FILE = "artifacts/data/system-description.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
COMMON = "common-control-provider"  # inheritance inside the organization: no package to review
IMPLEMENTED = ("implemented", "alternative")
RELINQUISHED = frozenset({"configuration", "maintenance"})  # CNSSI 1254 Annex D 3.c

Record = dict[str, Any]


def _items(record: Any, key: str) -> list[Record]:
    value = record.get(key) if isinstance(record, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _block(record: Any, key: str) -> Record:
    value = record.get(key) if isinstance(record, dict) else None
    return value if isinstance(value, dict) else {}


def _strings(record: Any, key: str) -> list[str]:
    value = record.get(key) if isinstance(record, dict) else None
    return [str(v) for v in value] if isinstance(value, list) else []


def _leveraged(ctx: Context) -> list[Record]:
    if not scope.produced_or_seeded(ctx.run, "ART-SD"):
        return []
    return _items(ctx.data(LEVERAGED_FILE), "leveraged_authorizations")


def _first_authorization(ctx: Context) -> dt.date | None:
    effect_of = ledger.effects(ctx.run)
    dates = [ledger.parse_date(r.get("date")) for r in ctx.ledger or ()
             if isinstance(r, dict) and effect_of.get(r.get("decision")) == "authorize"]
    return min((d for d in dates if d), default=None)


def _collector(rule: str, path: str) -> tuple[list[RunFinding], Any]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, path, None, {"C-1"}))

    return out, err


# --- RECIP-001: the customer's review of the provider's authorization package ----------------

def package_review(ctx: Context) -> list[RunFinding]:
    out, err = _collector("RECIP-001", LEVERAGED_FILE)
    decided = _first_authorization(ctx)
    components = _items(ctx.data(BOUNDARY_FILE), "components")
    categorization = ctx.facts.get("categorization") if isinstance(ctx.facts, dict) else None
    overlays = _strings(categorization, "overlays")
    for r in _leveraged(ctx):
        lid = r.get("id")
        if r.get("arrangement") == COMMON or "enterprise" in r:
            continue
        review = _block(r, "package_review")
        if not review:
            err(f"{lid}: the customer organization does not review the provider's authorization "
                "package")
            continue
        reviewed = ledger.parse_date(review.get("date"))
        if reviewed is not None and decided is not None and reviewed > decided:
            err(f"{lid}: the provider's authorization package is reviewed on {reviewed}, after "
                f"the authorization decision of {decided} that relies on it")
        if not _items(review, "factors"):
            err(f"{lid}: the review of the provider's authorization package considers no risk "
                "factor")
        considered = {i.get("component") for i in _items(review, "integration")}
        for c in components:
            if c.get("leveraged_authorization") == lid and c.get("id") not in considered:
                err(f"{lid}: the risk of integrating {c.get('id')} with the system is not "
                    "considered in the review")
        given = {i.get("overlay") for i in _items(review, "overlays")}
        for overlay in overlays:
            if overlay not in given:
                err(f"{lid}: no consideration is given to the security control overlay "
                    f"{overlay} in the review")
    return out


# --- RECIP-002: the controls the customer adds ------------------------------------------------
# In the baseline, a control is documented (SSP-COV-001), assessed (SAR-COV-001) and monitored
# (CONMON-001); this rule puts it there and holds it implemented.

def additional_controls(ctx: Context) -> list[RunFinding]:
    out, err = _collector("RECIP-002", LEVERAGED_FILE)
    run = ctx.run
    baseline = ctx.data("baseline.json")
    selected = {c.get("control_id") for c in _items(baseline, "controls")}
    ssp = {i.get("control_id"): i.get("status")
           for _, i in family_records(ctx, SSP_DIR, "controls")}
    for r in _leveraged(ctx):
        lid = r.get("id")
        for control in _strings(r, "additional_controls"):
            if isinstance(baseline, dict) and control not in selected:
                err(f"{lid}: additional control {control} is not in the baseline the "
                    "authorization covers")
            if scope.produced_or_seeded(run, "ART-SSP") and ssp.get(control) not in IMPLEMENTED:
                err(f"{lid}: additional control {control} is not documented as implemented in "
                    "the SSP")
    return out


# --- RECIP-003: a system its Granting organization no longer supports -------------------------

def support_ended(ctx: Context) -> list[RunFinding]:
    out, err = _collector("RECIP-003", LEVERAGED_FILE)
    effect_of = ledger.effects(ctx.run)
    records = {r.get("id"): r for r in ctx.ledger or () if isinstance(r, dict)}
    for r in _leveraged(ctx):
        support = _block(r, "granting_support")
        if support.get("continued") is not True:
            continue
        held = records.get(support.get("authorization"))
        if held is None or effect_of.get(held.get("decision")) != "authorize":
            err(f"{r.get('id')}: the Granting organization stopped supporting it on "
                f"{support.get('ended')} and this organization continues using it without "
                "a full authorization of its own")
    return out


# --- RECIP-004: a system authorized by another organization and now owned by this one ---------

def origin(ctx: Context) -> list[RunFinding]:
    out, err = _collector("RECIP-004", SYSTEM_FILE)
    if not scope.produced_or_seeded(ctx.run, "ART-SD"):
        return out
    came = _block(ctx.data(SYSTEM_FILE), "origin")
    if not came:
        return out
    kind, provider = came.get("kind"), came.get("organization")
    owner = _block(ctx.facts, "owning_organization").get("value")
    if provider is not None and provider == owner:
        err(f"the providing organization {provider} is this system's own organization, so no "
            f"receiving organization took over ownership of the {kind}")
    relinquished = set(_strings(came, "relinquished"))
    operating = ledger.parse_date(came.get("operating"))
    own = kind == "separate-instance" or RELINQUISHED <= relinquished
    if own and operating is not None:
        effect_of = ledger.effects(ctx.run)
        standing = ledger.in_force([r for r in ctx.ledger or () if isinstance(r, dict)],
                                   effect_of, operating)
        effects = {effect_of.get(s.record.get("decision")) for s in standing.values()}
        if "authorize" not in effects:
            err(f"the {kind} operated before its receiving AO authorized it, on {operating}")
    listed = {i.get("document"): i for i in _items(came, "reuse")}
    for document in CORE_DOCUMENTS:
        item = listed.get(document)
        if item is None:
            err(f"the providing organization's {document} is neither reused nor explained")
        elif item.get("reused") is False and not item.get("reason"):
            err(f"the providing organization's {document} is not reused and no reason is given")
    return out
