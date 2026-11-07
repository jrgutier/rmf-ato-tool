"""The categorization C-2 draws from the information types P-12 records: CATG-*. The system's
impact levels hold against the high-water mark of its information types, an adjustment away
from it is recorded with its factor, the review weighs the factors SP 800-60 Step 3 and FIPS 199
name, and special handling (CUI, CTI, classified information, software artifacts with a
military application, system information) sets its floor. Judged once C-2 or P-12 is in scope.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import FACTS_FILE

INFOTYPES_FILE = "artifacts/data/infotypes.yaml"
C2, P12 = "C-2", "P-12"
LEVELS = ("low", "moderate", "high")
CLASSIFICATIONS = ("unclassified", "confidential", "secret", "top-secret")
OBJECTIVES = {"c": "confidentiality", "i": "integrity", "a": "availability"}
# SP 800-60v1r1 Step 3 and FIPS 199 section 3: organization, environment, mission, use and data
# sharing, within the context of the organization and the overall national interest.
REVIEW_FACTORS = ("organization", "environment", "mission", "use", "data-sharing",
                  "national-interest")
MODERATE = "moderate"
CTI_PROTECTION = ("dfars-252.204-7012", "exempt-dfars-252.204-7000-a-3")


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in items or () if isinstance(i, dict)]


def _rank(value: Any) -> int:
    return LEVELS.index(value) if value in LEVELS else -1


def _types(ctx: Context) -> list[dict[str, Any]]:
    data = ctx.data(INFOTYPES_FILE)
    return _dicts(data.get("information_types")) if isinstance(data, dict) else []


def _level(info: dict[str, Any], key: str) -> str | None:
    node = info.get(OBJECTIVES[key])
    if not isinstance(node, dict):
        return None
    return node.get("selected") or node.get("base")


def _handling(info: dict[str, Any]) -> dict[str, Any]:
    node = info.get("handling")
    return node if isinstance(node, dict) else {}


def _categorization(ctx: Context) -> dict[str, Any] | None:
    if C2 not in scope.active_tasks(ctx.run):
        return None
    cat = facts_mod.get(ctx.facts, "categorization")
    return cat if isinstance(cat, dict) else None


def high_water(ctx: Context) -> list[RunFinding]:
    """CATG-001: the system against the high-water mark of its information types, each
    adjustment recorded, and the review factors weighed."""
    cat = _categorization(ctx)
    types = _types(ctx)
    if cat is None or not types:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("CATG-001", message, FACTS_FILE, None, {C2}))

    adjusted = {(_key(a.get("objective")), _key(a.get("to")))
                for a in _dicts(cat.get("adjustments"))}
    for key, name in OBJECTIVES.items():
        mark = max((_level(t, key) for t in types), key=_rank, default=None)
        value = cat.get(key)
        if _rank(value) < _rank(mark):
            err(f"{name} is {value}, below the high-water mark {mark} of the information types")
        if _rank(value) > _rank(mark) and (key, _key(value)) not in adjusted:
            err(f"{name} is raised to {value} above the high-water mark {mark} of the "
                "information types with no recorded adjustment")
    unweighed = [f for f in REVIEW_FACTORS if f not in _list(cat.get("factors_reviewed"))]
    if unweighed:
        err("the provisional impact levels are not reviewed against "
            f"{', '.join(unweighed)}")
    return out


def handling_floors(ctx: Context) -> list[RunFinding]:
    """CATG-002: CUI and CTI at no less than moderate confidentiality, software artifacts with a
    military application at moderate confidentiality and integrity, system information at the
    level of the user information, and nothing classified above the system's level."""
    cat = _categorization(ctx)
    types = _types(ctx)
    if cat is None or not types:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("CATG-002", message, FACTS_FILE, None, {C2}))

    controlled = [t.get("id") for t in types
                  if _handling(t).get("cui") is True or _handling(t).get("cti") is True]
    if controlled and _rank(cat.get("c")) < _rank(MODERATE):
        err("the system processes controlled unclassified information "
            f"({', '.join(map(str, controlled))}) and its "
            f"confidentiality is {cat.get('c')}, below moderate")
    artifacts = [t.get("id") for t in types if _handling(t).get("software_artifacts") is True]
    for key in ("c", "i"):
        if artifacts and _rank(cat.get(key)) < _rank(MODERATE):
            err(f"software artifacts with a military or space application "
                f"({', '.join(map(str, artifacts))}) are protected at a minimum of moderate "
                f"{OBJECTIVES[key]}, not {cat.get(key)}")
    users = [t for t in types if t.get("system_information") is not True]
    for info in (t for t in types if t.get("system_information") is True):
        for key, name in OBJECTIVES.items():
            mark = max((_level(t, key) for t in users), key=_rank, default=None)
            if _rank(_level(info, key)) < _rank(mark):
                err(f"{info.get('id')} is system information at {name} {_level(info, key)}, "
                    f"below the most sensitive user information ({mark})")
    level = facts_mod.get(ctx.facts, "classification")
    system = level.get("value") if isinstance(level, dict) else None
    for info in types:
        held = _handling(info).get("classification")
        if system in CLASSIFICATIONS and held in CLASSIFICATIONS \
                and CLASSIFICATIONS.index(held) > CLASSIFICATIONS.index(system):
            err(f"{info.get('id')} is {held} information processed on a system approved for "
                f"{system}")
    return out


def information_types(ctx: Context) -> list[RunFinding]:
    """CATG-003: why each type was selected, how PII was identified, its handling, and how CTI is
    protected where it leaves the system."""
    if P12 not in scope.active_tasks(ctx.run) and not scope.produced_or_seeded(
            ctx.run, "ART-INFOTYPES"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("CATG-003", message, INFOTYPES_FILE, None, {P12}))

    types = _types(ctx)
    for info in types:
        ident = info.get("id")
        if not info.get("selection_basis"):
            err(f"{ident} records no basis for selecting the information type")
        if info.get("privacy") is True and not info.get("pii_identification"):
            err(f"{ident} holds PII and does not say how the PII was identified")
        if not _handling(info):
            err(f"{ident} records no handling: classification, CUI and CTI")
    if not any(_handling(t).get("cti") is True for t in types):
        return out
    data = ctx.data(INFOTYPES_FILE)
    cti = data.get("cti") if isinstance(data, dict) else None
    if not isinstance(cti, dict):
        err("the system holds CTI and records no assessment of its exposure and protection")
        return out
    if cti.get("protection") not in CTI_PROTECTION:
        err("protection of CTI is consistent with DFARS 252.204-7012 unless exempted by DFARS "
            f"252.204-7000(a)(3), not {cti.get('protection')}")
    if cti.get("agreements_include_8582") is not True:
        err("the legally binding agreements do not include the DoDI 8582.01 requirements for "
            "CTI")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CATG-001", high_water), ("CATG-002", handling_floors),
                ("CATG-003", information_types))
