"""Rigor and scope rules RIGR-001 to RIGR-003 (SP 800-53A section 2.4, 3.2 and appendix C):
the assessment plan grounds its depth and coverage in the factors the organization names, the
organization directs the sampling of each method, and the assessment report records the
attribute values the assessors applied, not below the plan's. Both stay quiet about an
artifact not in play; RUN-ART-001 reports a missing file."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules.assessment import (
    METHOD_OBJECTS,
    SAP_FILE,
    Err,
    _block,
    _records,
    _reporter,
    _sap,
    _team,
)
from rmf_tool.check.rules.content import SAR_DIR, family_records
from rmf_tool.run import scope

CATEGORIZATION, PRIVACY_RISK_ASSESSMENT, SECURITY_PLAN = "ART-CAT", "ART-RA", "ART-SSP"
LEVELS = ("basic", "focused", "comprehensive")  # the hierarchical attribute values
SPECIFIC_OBJECTS = ("focused", "comprehensive")  # a representative sample plus specific objects
RANDOM = "random"
MECHANISMS = "mechanisms"
INTERVIEW = "interview"


def _rank(value: Any) -> int:
    return LEVELS.index(value) if value in LEVELS else -1


def _list(value: Any) -> list[Any]:
    """A list field as written, or nothing when it is not a list (RUN-FM-001 reports that)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> Any:
    """An identifier usable as a key: a malformed one (a list or a mapping) matches nothing."""
    return value if isinstance(value, (str, int)) else None


def _count(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _organization(who: Any, ctx: Context, team: set[Any]) -> bool:
    """The organization speaks through a framework persona who is not an assessor."""
    return isinstance(who, str) and who in ctx.run.personas and who not in team


def _sources(ctx: Context, rigor: dict[str, Any], err: Err) -> None:
    if rigor.get("categorization") != CATEGORIZATION:
        err("the rigor and scope of the assessment rest on the security categorization "
            f"{CATEGORIZATION}, not {rigor.get('categorization')}")
    privacy = rigor.get("privacy_risk_assessment")
    if ctx.processes_pii and privacy != PRIVACY_RISK_ASSESSMENT:
        err("the system processes PII, so the rigor and scope of the assessment rest on the "
            f"privacy risk assessment {PRIVACY_RISK_ASSESSMENT}, not {privacy}")
    if SECURITY_PLAN not in _list(rigor.get("plans")):
        err("the controls assessed are those of the approved plans: rigor.plans omits the "
            f"security plan {SECURITY_PLAN}")


def _assurance(ctx: Context, rigor: dict[str, Any], team: set[Any], err: Err) -> dict[Any, Any]:
    requirements = {_key(r.get("id")): r for r in _records(rigor, "assurance_requirements")}
    if not requirements:
        err("no assurance requirement the organization intends to meet is specified, so "
            "nothing grounds the depth and coverage of the assessment")
    for ident, r in requirements.items():
        if not _organization(r.get("specified_by"), ctx, team):
            err(f"the assurance requirement {ident} is specified by the organization through a "
                f"persona outside the assessment team, not {r.get('specified_by')}")
    return requirements


def _direction(ctx: Context, rigor: dict[str, Any], team: set[Any], err: Err) -> None:
    direction = _block(rigor, "direction")
    by = direction.get("by")
    if not _organization(by, ctx, team):
        err("the organization provides direction on the type, number and specific objects "
            f"to be assessed through a persona outside the assessment team, not {by}")
    if team.isdisjoint(c for c in _list(direction.get("conferred_with")) if isinstance(c, str)):
        err("the organization confers with the assessors on the sampling direction: "
            "conferred_with names no member of the assessment team")
    if not direction.get("factors"):
        err("the sampling direction considers no factors, such as the available resources "
            "and the importance of the assessment")


def _levels(pid: Any, p: dict[str, Any], requirements: dict[Any, Any], err: Err) -> None:
    ident = _key(p.get("assurance_requirement"))
    requirement = requirements.get(ident)
    if requirement is None:
        err(f"{pid} meets the assurance requirement {ident}, which the organization never "
            "specified among rigor.assurance_requirements")
        return
    if _rank(p.get("depth")) < _rank(requirement.get("depth")):
        err(f"{pid} selects depth {p.get('depth')}, below the depth the assurance requirement "
            f"needs, {requirement.get('depth')} ({ident})")
    if _rank(p.get("coverage")) < _rank(requirement.get("coverage")):
        err(f"{pid} selects coverage {p.get('coverage')}, below the coverage the assurance "
            f"requirement needs, {requirement.get('coverage')} ({ident})")


def _types(pid: Any, method: Any, p: dict[str, Any], sample: dict[str, Any], ctx: Context,
           err: Err) -> set[Any]:
    """The object types the record samples, checked against what the procedure selects for
    the method; an interview samples organizational roles, the framework's personas."""
    types = [t for t in _list(sample.get("types")) if isinstance(t, dict)]
    sampled = {t.get("type") for t in types if isinstance(t.get("type"), str)}
    for t in types:
        if _count(t.get("number")) < 1:
            err(f"{pid} {method}: the number of objects of the type {t.get('type')} to sample "
                f"is {t.get('number')}, not a count of at least one")
    if method == INTERVIEW:
        for role in sorted(sampled - set(ctx.run.personas), key=str):
            err(f"{pid} interview: the individuals to be interviewed are sampled by "
                f"organizational role, and {role} is no persona of the framework")
        return sampled
    selected = {o for o in _list(p.get("objects")) if isinstance(o, str)}
    selected &= METHOD_OBJECTS.get(method, set())
    for foreign in sorted(sampled - selected, key=str):
        err(f"{pid} {method}: the sampled object type {foreign} is not one the procedure "
            f"selects for the {method} method")
    for unsampled in sorted(selected - sampled, key=str):
        err(f"{pid} {method}: the object type {unsampled} the procedure selects is not "
            "sampled, so the sample lacks the diversity of types selected")
    return sampled


def _sample(pid: Any, method: Any, p: dict[str, Any], sample: dict[str, Any], ctx: Context,
            err: Err) -> None:
    sampled = _types(pid, method, p, sample, ctx, err)
    if p.get("coverage") in SPECIFIC_OBJECTS and not sample.get("specific"):
        err(f"{pid} {method}: {p.get('coverage')} coverage samples specific objects deemed "
            "particularly important beside the representative sample, and none is named")
    if sample.get("selection") != RANDOM and not str(sample.get("bias_control") or "").strip():
        err(f"{pid} {method}: a sampling method other than random sampling is used with care "
            "to avoid bias, and no bias control is recorded")
    if method != "test" or MECHANISMS not in sampled:
        return
    extent = [e for e in _list(sample.get("extent")) if isinstance(e, dict)]
    if not extent:
        err(f"{pid} test: mechanism-related testing records the extent of the testing "
            "conducted, and none is recorded")
    for e in extent:
        if _count(e.get("count")) < 1:
            err(f"{pid} test: the extent of the testing counts {e.get('count')} "
                f"{e.get('measure')}, not at least one")


def _sampling(pid: Any, p: dict[str, Any], ctx: Context, err: Err) -> None:
    methods = [m for m in _list(p.get("methods")) if isinstance(m, str)]
    directed: dict[Any, dict[str, Any]] = {}
    for sample in _records(p, "sampling"):
        method = sample.get("method")
        if not isinstance(method, str) or method not in methods:
            err(f"{pid}: a sampling record directs the method {method}, which the procedure "
                "does not select")
        elif method in directed:
            err(f"{pid}: two sampling records direct the method {method}")
        else:
            directed[method] = sample
    for method in methods:
        if method not in directed:
            err(f"{pid} selects the method {method}, and no sampling record directs the "
                "type, number and specific objects it applies to")
    for method, sample in directed.items():
        _sample(pid, method, p, sample, ctx, err)


def rigor(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("RIGR-001", SAP_FILE)
    block = _block(sap, "rigor")
    requirements = _assurance(ctx, block, _team(sap), err)
    _sources(ctx, block, err)
    for p in _records(sap, "procedures"):
        _levels(p.get("id"), p, requirements, err)
    return out


# --- RIGR-003: the organization directs the sampling of each method ---------------------------
def sampling(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("RIGR-003", SAP_FILE)
    _direction(ctx, _block(sap, "rigor"), _team(sap), err)
    for p in _records(sap, "procedures"):
        _sampling(p.get("id"), p, ctx, err)
    return out


# --- RIGR-002: the report records the attribute values applied --------------------------------
def _planned(sap: dict[str, Any]) -> dict[Any, dict[str, int]]:
    """Per control, the highest depth and coverage rank any procedure assessing it selects."""
    planned: dict[Any, dict[str, int]] = {}
    for p in _records(sap, "procedures"):
        for cid in (c for c in _list(p.get("controls")) if isinstance(c, str)):
            levels = planned.setdefault(cid, {"depth": -1, "coverage": -1})
            for attribute in levels:
                levels[attribute] = max(levels[attribute], _rank(p.get(attribute)))
    return planned


def _applied(d: dict[str, Any], planned: dict[str, int], err: Err) -> None:
    cid = d.get("control_id")
    for attribute, plan in planned.items():
        value = d.get(attribute)
        if value not in LEVELS:
            err(f"{cid}: the determination records no {attribute} attribute value the "
                "assessors applied")
        elif _rank(value) < plan:
            err(f"{cid}: the assessors applied {attribute} {value}, below the {attribute} "
                f"{LEVELS[plan]} the assessment plan assigned")


def applied(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-SAR"):
        return []
    planned = _planned(_sap(ctx) or {})
    out: list[RunFinding] = []
    for rel, d in family_records(ctx, SAR_DIR, "determinations"):
        if _key(d.get("control_id")) in planned:
            found, err = _reporter("RIGR-002", rel)
            _applied(d, planned[d["control_id"]], err)
            out.extend(found)
    return out
