"""The cybersecurity strategy record P-14 writes beside ART-RA: CSSTRAT-001 to CSSTRAT-003
(DoDI 5000.82 3.5.b and Table 2, DoDI 5000.75, DoDI 5000.87, DoDI 5000.89, DoDI 5000.90,
DoDI 8500.01). cybersecurity-strategy.yaml holds the program's category, the CSS the run read,
its approvals and its reviews.

Every pathway owes a CSS, so the record is asked for while P-14 is in scope. Where the run holds
protection.yaml, the ACAT, decision points and contract awards are read from it; otherwise from
the CSS record. Who approves follows Table 2 only: the Component CIO and the DoD CIO for an
ACAT ID or BCAT I program, the DoD CIO for a mission-critical or mission-essential business
system (DoDI 5000.75 2.3.c.(1)), and the respective CIO, either one, for every other program.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules.protection import (
    ENTRY,
    _day,
    _dict,
    _dicts,
    _ids,
    _passed,
    _pathway,
    _ppp_owed,
    _protection,
    _record,
    decision_points,
)
from rmf_tool.run import authorization as ledger

CSS_FILE = "artifacts/data/cybersecurity-strategy.yaml"
DOD_CIO, COMPONENT_CIO = "DoD-CIO", "Component-CIO"
DBS, SWP = "PW-DBS", "PW-SWP"
# Table 2 row 1 and DoDI 5000.90 2.3.c: ACAT ID; row 3: DBS BCAT I.
BOTH_CIOS = "Component CIO and DoD CIO"
MISSION_IT = ("mission-critical", "mission-essential")  # DoDI 5000.75 2.3.c.(1)
# Table 2 rows 2, 4 and 5: the CSS is part of the documentation resulting in an acquisition
# strategy on these programs.
ACQ_STRATEGY_PATHWAYS = ("PW-MCA", "PW-UCA", "PW-MTA", "PW-SWP")
AOS = "PW-AOS"
ACAT_I = ("ID", "IB", "IC")  # Table 2 names only the services ACAT I programs of PW-AOS
BASED_ON = ("cssr-requirements", "threats", "derived-requirements", "performance-specifications",
            "operational-use")  # DoDI 5000.89 3.5.b.(1)
SWP_ASSESSMENTS = ("supply-chain", "development-environment", "processes-and-tools",
                   "continuous-automated-testing")  # DoDI 5000.87 3.2.d.(3)(i)
AO_ROLES = ("PER-AO", "PER-AODR")
PROGRAM_OFFICE = "PER-PM"  # holds the program office and the system owner
REVISIT = ("threat-assessment", "continuous-monitoring")  # DoDI 5000.90 3.3.b.(5)


def _css(ctx: Context, rule: str) -> tuple[dict[str, Any] | None, list[RunFinding],
                                           Callable[[str], None]]:
    return _record(ctx, rule, CSS_FILE, "P-14")


def _points(ctx: Context, program: dict[str, Any]) -> dict[str, Any]:
    """The decision points passed that a CSS review or approval must precede: on a business
    system every ATP decision point (DoDI 5000.75), elsewhere the milestone decisions, never the
    entry into the pathway."""
    pathway = _pathway(ctx)
    kinds = ("milestone", "decision-point") if pathway == DBS else ("milestone",)
    valid = decision_points(ctx, pathway, kinds)
    return {p: d for p, d in _passed(program).items() if p != ENTRY and p in valid}


def _program(ctx: Context, data: dict[str, Any]) -> dict[str, Any]:
    """The program as the CSS rules read it. protection.yaml, when the run holds it, is the one
    home of the ACAT, the decision points passed and the contract awards; the CSS record adds the
    BCAT, the mission criticality and which milestone decision authorized an award."""
    own = _dict(data.get("program"))
    prot = _dict(_protection(ctx).get("program"))
    if not prot:
        return own
    authorized = {str(a.get("id")): a.get("authorized_at")
                  for a in _dicts(own.get("contract_awards"))}
    awards = [{**a, "authorized_at": authorized.get(str(a.get("id")))}
              for a in _dicts(_protection(ctx).get("contract_awards"))]
    return {**own, "acat": prot.get("acat"), "decision_points": prot.get("decision_points"),
            "contract_awards": awards}


def _preceded(items: list[dict[str, Any]], point: str, date: Any) -> list[dict[str, Any]]:
    day = _day(date)
    return [i for i in items if i.get("before") == point and day is not None
            and (_day(i.get("date")) or day) <= day]


# --- CSSTRAT-001: who approves the CSS, per Table 2 ----------------------------------------

def approvals(ctx: Context) -> list[RunFinding]:
    data, out, err = _css(ctx, "CSSTRAT-001")
    if data is None:
        return out
    program = _program(ctx, data)
    pathway = _pathway(ctx)
    approved = _dicts(data.get("approvals"))
    acat, bcat, mission = program.get("acat"), program.get("bcat"), program.get("mission")
    if acat is None:
        err("the CSS record gives no ACAT and the run holds no protection.yaml that does")
    points = _points(ctx, program)
    if acat == "ID" or (pathway == DBS and bcat == "I"):
        owed: tuple[str, ...] = (COMPONENT_CIO, DOD_CIO)
        label = "an ACAT ID" if acat == "ID" else "a BCAT I business"
        for point, date in sorted(points.items()):
            have = {a.get("authority") for a in _preceded(approved, point, date)}
            for who in owed:
                if who not in have:
                    err(f"{label} program obtains {BOTH_CIOS} approval of the CSS before "
                        f"{point}; no {who} approval precedes it")
    elif pathway == DBS and mission in MISSION_IT:
        for point, date in sorted(points.items()):
            if DOD_CIO not in {a.get("authority") for a in _preceded(approved, point, date)}:
                err(f"the DoD CIO approves the CSS of {mission} IT before ATP decision point "
                    f"{point}")
    elif points and (pathway != AOS or acat in ACAT_I):
        dated = sorted((d, p) for p, d in points.items() if d is not None)
        first, day = (dated[0][1], dated[0][0]) if dated else (min(points), None)
        cios = {a.get("authority") for a in approved
                if day is None or (_day(a.get("date")) or day) <= day}
        if not cios & {DOD_CIO, COMPONENT_CIO}:
            err(f"the CSS gains approval from the respective CIO; no CIO approval precedes {first}")
    if pathway == SWP:
        strategy = _dict(data.get("acquisition_strategy"))
        authority = _dict(strategy.get("approval")).get("authority")
        if authority != "DA" or strategy.get("includes_css") is not True:
            err("on the software pathway the DA approves the acquisition strategy that includes "
                f"the CSS; the record gives {authority}")
        entered = _passed(program).get("DP-SWP-EXECUTION")
        when = _day(_dict(strategy.get("approval")).get("date"))
        if entered is not None and when is not None and when > entered:
            err("the DA approves the acquisition strategy before the execution phase is entered")
    return out


# --- CSSTRAT-002: reviews before milestone decisions and contract awards -------------------

def reviews(ctx: Context) -> list[RunFinding]:
    data, out, err = _css(ctx, "CSSTRAT-002")
    if data is None:
        return out
    program = _program(ctx, data)
    seen = _dicts(data.get("reviews")) + _dicts(data.get("approvals"))
    passed = _passed(program)
    for point, date in sorted(_points(ctx, program).items()):
        if not _preceded(seen, point, date):
            err(f"the CSS is reviewed prior to acquisition milestone decision {point}")
    for award in _dicts(program.get("contract_awards")):
        at = award.get("authorized_at")
        if at:
            when, day = passed.get(str(at)), _day(award.get("date"))
            if when is None or day is None or when > day:
                err(f"contract award {award.get('id')} is authorized at {at}, which is no "
                    "milestone decision the program passed before the award")
            continue
        if not _preceded(seen, str(award.get("id")), award.get("date")):
            err(f"the CSS is reviewed prior to contract award {award.get('id')}")
    for r in _dicts(data.get("reviews")):
        if PROGRAM_OFFICE not in _ids(r.get("by")):
            err(f"review {r.get('id')}: the program office and the system owner review and "
                "maintain the CSS")
        if set(_ids(r.get("prompted_by"))) & set(REVISIT):
            if not _ids(r.get("coordinated_with")) & set(AO_ROLES):
                err(f"review {r.get('id')}: the PM revisits the cybersecurity posture in "
                    "coordination with the AO")
            if _dict(r.get("ao_validation")).get("by") not in AO_ROLES \
                    and not r.get("no_validation_reason"):
                err(f"review {r.get('id')}: the iteration concludes with the AO validating the "
                    "CSS and updated POA&M, or the record says why not")
    return out


# --- CSSTRAT-003: what the CSS holds and where -------------------------------------------

def content(ctx: Context) -> list[RunFinding]:
    data, out, err = _css(ctx, "CSSTRAT-003")
    if data is None:
        return out
    strategy = _dict(data.get("strategy"))
    pathway = _pathway(ctx)
    entity = ctx.run.framework.index("pathways").get(pathway or "")
    phases = set(entity.data.get("phases") or ()) if entity else set()
    planned = {a.get("phase") for a in _dicts(strategy.get("activities"))}
    for phase in sorted(phases - planned):
        err(f"the CSS outlines cybersecurity activities across all phases; none is planned for "
            f"{phase}")
    sources = {t.get("from") for t in _dicts(strategy.get("threat_information"))}
    if "intelligence-community" not in sources:
        err("the PM uses cyber threat information produced by the Intelligence Community in "
            "developing the CSS")
    missing = set(BASED_ON) - _ids(strategy.get("based_on"))
    if missing:
        err(f"the CSS is based on requirements, threats, derived requirements, performance "
            f"specifications and intended use; it leaves out {', '.join(sorted(missing))}")
    if _dict(strategy.get("rmf")).get("incorporated") is not True:
        err("the CSS incorporates the RMF process that supports obtaining an ATO")
    places = _ids(strategy.get("documented_in"))
    if not _ppp_owed(ctx) and "stand-alone" not in places:
        err("without a program protection plan the CSS is a stand-alone required document")
    acat = _program(ctx, data).get("acat")
    in_table = pathway in ACQ_STRATEGY_PATHWAYS or (pathway == AOS and acat in ACAT_I)
    if in_table and acat != "ID" and "acquisition-strategy" not in places:
        err("the CSS is developed as part of the documentation that results in the acquisition "
            "strategy")
    if pathway == SWP:
        left = set(SWP_ASSESSMENTS) - _ids(strategy.get("recurring_assessments"))
        if left:
            err("a software pathway CSS includes recurring assessment of the supply chain, the "
                "development environment, processes and tools, and continuous automated testing; "
                f"it leaves out {', '.join(sorted(left))}")
    first = min((d for d in (_day(r.get("date")) for r in ledger.load(ctx.run) or ()) if d),
                default=None)
    written = _day(strategy.get("date"))
    if first is not None and written is not None and written > first:
        err("the PM's cybersecurity activities start with the CSS and continue through the RMF "
            f"to an ATO; the CSS is dated after the first authorization decision ({first})")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CSSTRAT-001", approvals), ("CSSTRAT-002", reviews), ("CSSTRAT-003", content))
