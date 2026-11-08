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
from rmf_tool.run.authorization import parse_date as ledger_day
from rmf_tool.run.model import FACTS_FILE

INFOTYPES_FILE = "artifacts/data/infotypes.yaml"
C2, P12, P13 = "C-2", "P-12", "P-13"
LEVELS = ("low", "moderate", "high")
# FIPS 199 and SP 800-60: not applicable is a value for the confidentiality of an information
# type only, never for a system, whose floor is low.
NOT_APPLICABLE = "not-applicable"
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
    """low, moderate and high in order, not applicable below low, anything malformed below that."""
    if value in LEVELS:
        return LEVELS.index(value)
    return -1 if value == NOT_APPLICABLE else -2


def _system_mark(levels: Iterator[str | None]) -> str | None:
    """The high-water mark the system's value is judged against: not applicable on every
    information type leaves the system at low."""
    mark = max(levels, key=_rank, default=None)
    return LEVELS[0] if mark == NOT_APPLICABLE else mark


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
    """CATG-001: the system is not below the high-water mark of its information types. An
    adjustment above it and the review of the factors are CADJ-001."""
    cat = _categorization(ctx)
    types = _types(ctx)
    if cat is None or not types:
        return []
    out: list[RunFinding] = []
    for key, name in OBJECTIVES.items():
        mark = _system_mark(_level(t, key) for t in types)
        value = cat.get(key)
        if _rank(value) < _rank(mark):
            out.append(make("CATG-001", f"{name} is {value}, below the high-water mark {mark} "
                            "of the information types", FACTS_FILE, None, {C2}))
    return out


def adjustments(ctx: Context) -> list[RunFinding]:
    """CADJ-001, split from CATG-001: each objective raised above the high-water mark has its
    adjustment recorded, and the provisional levels are reviewed against the SP 800-60 Step 3
    and FIPS 199 factors."""
    cat = _categorization(ctx)
    types = _types(ctx)
    if cat is None or not types:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("CADJ-001", message, FACTS_FILE, None, {C2}))

    adjusted = {(_key(a.get("objective")), _key(a.get("to")))
                for a in _dicts(cat.get("adjustments"))}
    for key, name in OBJECTIVES.items():
        mark = _system_mark(_level(t, key) for t in types)
        value = cat.get(key)
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
        if not isinstance(info.get("privacy"), bool):
            err(f"{ident} does not identify whether the information type is personally "
                "identifiable information")
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


SAOP, C3 = "PER-PRIV", "C-3"
REVIEWERS = ("PER-AO", "PER-AODR")
PRIVACY_OVERLAY = "CNSSI1253F-ATT6-PRIVACY"
PRIVACY_LEVELS = tuple(f"{PRIVACY_OVERLAY}-{x}" for x in ("LOW", "MODERATE", "HIGH"))
ACCT = f"{PRIVACY_OVERLAY}-ACCT"


def privacy_approval(ctx: Context) -> list[RunFinding]:
    """PIIC-001: the SAOP or designee approves the determination whether the system processes
    PII and the Privacy Overlays selected, a system processing PII applies a Privacy Overlay (and
    the ACCT Overlay when its logs include PII), and the SAOP approves its categorization before
    the authorizing official or designated representative reviews it."""
    if C3 not in scope.active_tasks(ctx.run):
        return []
    cat = facts_mod.get(ctx.facts, "categorization")
    approved = cat.get("approved") if isinstance(cat, dict) else None
    if not isinstance(approved, dict) or approved.get("value") is not True:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("PIIC-001", message, FACTS_FILE, None, {C3}))

    reviewer = approved.get("approved_by")
    if reviewer not in REVIEWERS:
        err("the security categorization is reviewed by the authorizing official or designated "
            f"representative, not {reviewer}")
    privacy = approved.get("privacy")
    if not isinstance(privacy, dict):
        err("the determination whether the system processes PII and whether the Privacy Overlay "
            "applies is not approved by the SAOP or designee")
        return out
    by = privacy.get("by")
    if SAOP not in (by, privacy.get("designee_of")):
        err(f"the PII determination is approved by {by}, not the SAOP or designee")
    pii = ctx.processes_pii
    if privacy.get("pii") is not pii:
        err(f"the approved PII determination is {privacy.get('pii')}, and the information types "
            f"{'hold' if pii else 'hold no'} PII")
    overlays = {o for o in _list(cat.get("overlays")) if isinstance(o, str)}
    if pii and not overlays & set(PRIVACY_LEVELS):
        err("the system processes PII and applies no Privacy Overlay (low, moderate or high)")
    logs = privacy.get("logs_pii")
    if pii and not isinstance(logs, bool):
        err("the system processes PII and the SAOP or designee has not confirmed whether its "
            "logs include PII")
    if logs is True and ACCT not in overlays:
        err("the system has logs that include PII, and the ACCT Overlay is not applied")
    agreed = {o for o in _list(privacy.get("overlays")) if isinstance(o, str)}
    for overlay in sorted(o for o in overlays - agreed if o.startswith(PRIVACY_OVERLAY)):
        err(f"the Privacy Overlay {overlay} is selected without the approval of the SAOP or "
            "designee")
    if pii:
        signed, reviewed = (ledger_day(privacy.get("date")), ledger_day(approved.get("date")))
        if reviewed is None:
            err("the categorization of a system processing PII records no date of the "
                "authorizing official's review, so the SAOP approval cannot be shown before it")
        elif signed is not None and signed > reviewed:
            err(f"the SAOP approved the categorization of a system processing PII on {signed}, "
                f"after the authorizing official's review of {reviewed}")
    return out


def cnssi_method(ctx: Context) -> list[RunFinding]:
    """CATG-004: DoDI 8500.01 Encl 3.g(1) categorizes every DoD IS and PIT system under CNSSI
    1253, NSS or not. The high-water mark stands in only under the degraded policy (plan 7.6),
    while CNSSI 1253 is a degraded reference the run cites."""
    cat = _categorization(ctx)
    if cat is None or "method" not in cat or cat.get("method") == "cnssi1253":
        return []
    if "CNSSI1253" in ctx.degraded_refs:
        return []
    return [make("CATG-004", f"the system is categorized by {cat.get('method')}, not in "
                 "accordance with CNSSI 1253, which DoDI 8500.01 requires of every DoD IS and PIT "
                 "system", FACTS_FILE, None, {C2})]


def information_owners(ctx: Context) -> list[RunFinding]:
    """CATG-005: every information type has an identified information owner, and each type's
    impact levels trace to that owner's input: a token the owner record itself cites (an
    interview answer at any task, or a product file a real owner supplied), or an answer the
    owner gave in any interview (CNSSI 1253 3.1: all information owners are identified to
    provide inputs, and each sets the impact level for their information type; DoDI 8500.01
    Encl 3.18.b)."""
    data = ctx.data(INFOTYPES_FILE)
    if P12 not in scope.active_tasks(ctx.run) or not isinstance(data, dict):
        return []
    types = _dicts(data.get("information_types"))
    if not types:
        return []

    def err(message: str) -> RunFinding:
        return make("CATG-005", message, INFOTYPES_FILE, None, {P12})

    owners = _dicts(data.get("information_owners"))
    if not owners:
        return [err("infotypes.yaml identifies no information owners of its information types")]
    answered_by: dict[str, str] = {}
    for i in ctx.interviews:
        if i.front:
            for a in i.answers:
                answered_by[a.id] = str(i.front.get("persona"))
    owned_by: dict[str, set[str]] = {}
    inputs: dict[str, set[str]] = {}
    for owner in owners:
        who = str(owner.get("persona"))
        cited = {str(s) for s in _list(owner.get("sources"))}
        for tid in _list(owner.get("types")):
            owned_by.setdefault(str(tid), set()).add(who)
            inputs.setdefault(str(tid), set()).update(cited)
    out = []
    for info in types:
        tid = str(info.get("id"))
        mine = owned_by.get(tid, set())
        if not mine:
            out.append(err(f"{tid} has no information owner identified"))
            continue
        traced = {str(s) for s in _list(info.get("sources"))}
        if traced.isdisjoint(inputs.get(tid, set())) \
                and all(answered_by.get(s) not in mine for s in traced):
            out.append(err(f"the impact levels of {tid} trace to no input of its information "
                           f"owner ({', '.join(sorted(mine))})"))
    return out


# SP 800-37r2 Task P-13: information enters a system by creation or collection; a stage the
# system stores it in ends in disposition (OMB A-130 ties disposition to retention). A system
# that only transmits a type keeps no copy to dispose of.
LIFE_CYCLE_START = ("creation", "collection")
LIFE_CYCLE_STORED, LIFE_CYCLE_END = "storage", "disposition"


def life_cycle(ctx: Context) -> list[RunFinding]:
    """INFL-001: P-13 identifies how each information type enters the system (creation or
    collection) and, for one the system stores, its disposition (SP 800-37r2 Task P-13)."""
    if P13 not in scope.active_tasks(ctx.run):
        return []
    out: list[RunFinding] = []
    for info in _types(ctx):
        stages = {s.get("stage") for s in _dicts(info.get("life_cycle"))}
        if not stages & set(LIFE_CYCLE_START):
            out.append(make("INFL-001", f"{info.get('id')}: the information life cycle "
                            "identifies no creation or collection stage", INFOTYPES_FILE,
                            None, {P13}))
        if LIFE_CYCLE_STORED in stages and LIFE_CYCLE_END not in stages:
            out.append(make("INFL-001", f"{info.get('id')}: the information life cycle stores "
                            "the information and identifies no disposition stage",
                            INFOTYPES_FILE, None, {P13}))
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CATG-001", high_water), ("CADJ-001", adjustments),
                ("CATG-002", handling_floors),
                ("CATG-003", information_types), ("PIIC-001", privacy_approval),
                ("INFL-001", life_cycle), ("CATG-004", cnssi_method),
                ("CATG-005", information_owners))
