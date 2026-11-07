"""The acquisition life cycle a run records, ACQLC-001 to ACQLC-005 (DoDI 5000.02, 5000.81,
5000.85, 5000.87, DoDI 8510.01).

facts.yaml `acquisition` holds the system's pathway and, for a program that combines pathways,
every pathway it uses; protection.yaml `program` holds the decision points the program passed
and its transitions between pathways; protection-requirements.yaml holds the capability
document P-15 read. Each rule reads a record only when the run holds it.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.protection import (
    PREQ_FILE,
    PROT_FILE,
    _day,
    _dict,
    _dicts,
    _passed,
    _points,
    program_pathways,
)
from rmf_tool.run import facts as facts_mod

FACTS_FILE = "facts.yaml"
DBS, SWP, MCA = "PW-DBS", "PW-SWP", "PW-MCA"
MDA = "PER-MDA"  # the MDA or, on the software pathway, the DA
PM = "PER-PM"
TAILORS = ("processes", "reviews", "documentation")  # DoDI 5000.87 3.1.d
MS_A, CDD_VALIDATION, DRFPRD = "MS-A", "MS-CDDV", "MS-DRFPRD"
IOC = "MS-IOC"
OS, PD = "PH-OS", "PH-PD"
# The August 20, 2025 Secretary of Defense memorandum disestablished JCIDS (DoDI 5000.02
# Change 2, 1.5.a).
JCIDS_END = dt.date(2025, 8, 20)
# The capability document each pathway validates its need in (EXT-CAPDOC). The middle tier
# names none of its own, so any kind serves it.
CAPABILITY_DOCUMENTS = {
    MCA: ("jcids", "requirements-document"),
    "PW-UCA": ("juon", "jeon", "component-uon", "warfighter-issue", "raa-determination"),
    SWP: ("cns",),
    DBS: ("business-requirements",),
    "PW-AOS": ("services-requirement",),
}


def _held(ctx: Context, rel: str) -> dict[str, Any]:
    data = ctx.data(rel) if ctx.run.path(rel).is_file() else None
    return data if isinstance(data, dict) else {}


def _strs(value: Any) -> list[str]:
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _acquisition(ctx: Context) -> dict[str, Any]:
    return _dict(facts_mod.get(ctx.facts, "acquisition"))


# --- ACQLC-001: combined pathways and their transitions -----------------------------------

def combined_pathways(ctx: Context) -> list[RunFinding]:
    """DoDI 5000.02 4.1.a: a program may combine pathways with MDA or DA approval, and then
    defines each transition point, the information requirements at the new pathway's entry
    point, and a smooth transition; combining pathways leaves the statutory thresholds of the
    program as a whole as they were. DoDI 5000.87 1.2.b and 3.1.d: a covered DBS uses the DBS
    pathway and may add the software pathway; a transition approach to the software pathway is
    identified by the PM and approved by the DA, tailoring processes, reviews and documentation."""
    out: list[RunFinding] = []

    def err(message: str, path: str = FACTS_FILE) -> None:
        out.append(make("ACQLC-001", message, path, None, {"P-14"}))

    acquisition = _acquisition(ctx)
    if not acquisition:
        return out
    known = ctx.run.framework.index("pathways")
    pathway, pathways = acquisition.get("pathway"), program_pathways(ctx)
    for p in pathways:
        if p not in known:
            err(f"{p} is no acquisition pathway of framework/pathways.yaml")
    if isinstance(acquisition.get("pathways"), list) and pathway not in pathways:
        err(f"the system's pathway {pathway} is not among the pathways the program combines")
    if pathway == SWP and not isinstance(acquisition.get("covered_dbs"), bool):
        err("a software pathway program states whether it is a covered defense business "
            "system: acquisition.covered_dbs")
    if acquisition.get("covered_dbs") is True and DBS not in pathways:
        err("a covered defense business system uses the DBS pathway, and may only add the "
            "software pathway to it")
    if len(pathways) < 2:
        return out
    program = _dict(_held(ctx, PROT_FILE).get("program"))
    if not program:
        return out
    if MCA in pathways and program.get("acat") == "none":
        err("the use of multiple pathways does not affect the statutory thresholds applicable "
            "to the program as a whole: a program with a major capability acquisition part keeps "
            "its ACAT", PROT_FILE)
    transitions = _dicts(program.get("transitions"))
    reached = {t.get("to") for t in transitions}
    # DoDI 5000.87 1.2.b: a covered DBS incorporates the software pathway; it moves to no new one.
    incorporated = {SWP} if acquisition.get("covered_dbs") is True else set()
    for p in pathways[1:]:
        if p not in reached and p not in incorporated:
            err(f"no transition point is defined from another pathway to {p}", PROT_FILE)
    artifacts = ctx.run.framework.ids("artifacts", "external_inputs")
    personas = ctx.run.framework.ids("personas")
    for t in transitions:
        _transition(ctx, t, pathways, artifacts, personas, err)
    return out


def _transition(ctx: Context, t: dict[str, Any], pathways: list[str], artifacts: set[str],
                personas: set[str], err: Callable[..., None]) -> None:
    source, target = t.get("from"), t.get("to")
    name = f"{source} to {target}"
    if source not in pathways or target not in pathways or source == target:
        err(f"the transition {name} is not between two pathways the program combines",
            PROT_FILE)
    leave, enter = _points(ctx, source), _points(ctx, target)
    if leave and t.get("at") not in leave:
        err(f"{t.get('at')} is no decision point of {source} at which to define the transition "
            "point", PROT_FILE)
    if enter and t.get("entry") not in enter:
        err(f"{t.get('entry')} is no entry point of the new pathway {target}", PROT_FILE)
    needs = _dicts(t.get("information_requirements"))
    if not needs:
        err(f"no information requirements are developed for the {target} entry point",
            PROT_FILE)
    for need in needs:
        if need.get("id") not in artifacts:
            err(f"{need.get('id')}: an information requirement at the new pathway entry point "
                "names no artifact or external input of the framework", PROT_FILE)
        if not any(p in personas for p in _strs(need.get("coordinated_with"))):
            err(f"{need.get('id')}: the information requirement is coordinated with no persona",
                PROT_FILE)
    approach = _dict(t.get("approach"))
    if approach.get("approved_by") != MDA:
        err(f"the MDA or DA approves the transition approach {name}, not "
            f"{approach.get('approved_by')}", PROT_FILE)
    if target == SWP and PM not in _strs(approach.get("identified_by")):
        err(f"the PM and applicable stakeholders identify the transition approach {name}",
            PROT_FILE)
    gaps = [k for k in TAILORS if k not in _strs(approach.get("tailors"))]
    if target == SWP and gaps:
        err(f"the transition approach {name} does not tailor {', '.join(gaps)}", PROT_FILE)
    approved, moved = _day(approach.get("date")), _day(t.get("date"))
    if approved and moved and approved > moved:
        err(f"the transition approach is approved after the transition it governs: {name}, "
            f"approved {approved}, moved {moved}", PROT_FILE)


# --- ACQLC-002: CDD validation before the Development RFP release -------------------------

def cdd_validation(ctx: Context) -> list[RunFinding]:
    """DoDI 5000.85 3.8.c: during TMRR the requirements validation authority validates the CDD
    (or equivalent requirements document), before the Development RFP release decision point.
    Judged on the dates protection.yaml records for the points passed."""
    out: list[RunFinding] = []
    passed = _passed(_dict(_held(ctx, PROT_FILE).get("program")))

    def err(message: str) -> None:
        out.append(make("ACQLC-002", message, PROT_FILE, None, {"P-14"}))

    validated, release = passed.get(CDD_VALIDATION), passed.get(DRFPRD)
    if DRFPRD in passed and (CDD_VALIDATION not in passed
                             or (validated and release and validated > release)):
        err("the CDD (or equivalent requirements document) validation does not precede the "
            f"Development RFP release decision point: record {CDD_VALIDATION} before {DRFPRD}")
    start = passed.get(MS_A)
    if validated and start and validated < start:
        err(f"the CDD is validated during the TMRR phase, which begins at {MS_A} on {start}, "
            f"not on {validated}")
    return out


# --- ACQLC-003: O&S begins upon first fielding or deployment -------------------------------

def os_entry(ctx: Context, pathway: str | None) -> str | None:
    """Where the pathway enters O&S: the PH-OS entry milestone on the spine, else the pathway
    decision point marked `enters: PH-OS`."""
    framework = ctx.run.framework
    if pathway == framework.meta.get("spine_pathway"):
        phase = framework.index("phases").get(OS)
        return phase.data.get("entry_milestone") if phase else None
    entity = framework.index("pathways").get(pathway or "")
    return next((d.get("id") for d in _dicts(entity.data.get("decision_points") if entity
                                             else None) if d.get("enters") == OS), None)


def operations(ctx: Context) -> list[RunFinding]:
    """DoDI 5000.85 3.15: the O&S phase begins upon fielding of the first system, which may
    precede IOC, and is based on an MDA-approved product support strategy. DoDI 5000.81 3.5.d:
    upon deployment, the capability enters O&S. On the spine, production and deployment
    continue after first fielding (the FRP decision follows), so P&D and O&S overlap there;
    elsewhere the system is in O&S once deployed."""
    out: list[RunFinding] = []
    pathway = _acquisition(ctx).get("pathway")
    entry = os_entry(ctx, pathway)
    passed = _passed(_dict(_held(ctx, PROT_FILE).get("program")))
    if entry is None or not passed:
        return out

    def err(message: str, path: str = PROT_FILE) -> None:
        out.append(make("ACQLC-003", message, path, None, {"P-14"}))

    fielded, ioc = passed.get(entry), passed.get(IOC)
    if entry in passed:
        pss = _dict(_dict(_held(ctx, PROT_FILE).get("program")).get("pss"))
        if not pss:
            err("O&S rests on no product support strategy: program.pss records none")
        elif pss.get("approved_by") != MDA:
            err(f"O&S is based on an MDA-approved product support strategy: program.pss is "
                f"approved by {pss.get('approved_by')}, not the MDA")
    if IOC in passed and (entry not in passed or (fielded and ioc and fielded > ioc)):
        err(f"the O&S phase begins upon fielding of the first system, which may precede IOC: "
            f"{entry} is not passed by {IOC}")
    if entry in passed:
        phase = _dict(facts_mod.get(ctx.facts, "lifecycle_phase")).get("value")
        allowed = (PD, OS) if pathway == ctx.run.framework.meta.get("spine_pathway") else (OS,)
        if phase not in allowed:
            err(f"upon {entry} the capability enters O&S, and facts.yaml lifecycle_phase is "
                f"{phase}", FACTS_FILE)
    return out


# --- ACQLC-004: the capability document after JCIDS ---------------------------------------

def capability_document(ctx: Context) -> list[RunFinding]:
    """DoDI 5000.02 Change 2 disestablished JCIDS on August 20, 2025: a JCIDS document is one
    validated by then, and a program needing one after uses the requirements document that
    replaced it. DoDI 8510.01 3.3.a(1)(a): the categorization goes in the appropriate
    capabilities document, the one the program's pathway validates its need in."""
    out: list[RunFinding] = []
    document = _dict(_held(ctx, PREQ_FILE).get("capability_document"))
    if not document:
        return out

    def err(message: str) -> None:
        out.append(make("ACQLC-004", message, PREQ_FILE, None, {"P-15"}))

    kind, validated = document.get("kind"), _day(document.get("validated"))
    # P-15 may read the draft CDD during TMRR; it is validated by the CDD validation point.
    cdd_passed = CDD_VALIDATION in _passed(_dict(_held(ctx, PROT_FILE).get("program")))
    if kind == "jcids" and validated is None and cdd_passed:
        err("a JCIDS capability document records when it was validated: "
            "capability_document.validated")
    if kind == "jcids" and validated and validated > JCIDS_END:
        err(f"JCIDS was disestablished on {JCIDS_END}; a capability document validated on "
            f"{validated} is no JCIDS document")
    pathways = program_pathways(ctx)
    if any(p not in CAPABILITY_DOCUMENTS for p in pathways):
        return out
    kinds = {k for p in pathways for k in CAPABILITY_DOCUMENTS[p]}
    if pathways and kind not in kinds:
        err(f"a {kind} document is not the capability document of the "
            f"{', '.join(pathways)} pathway")
    return out


# --- ACQLC-005: the categorization documented in the capability document -----------------

def categorization_documented(ctx: Context) -> list[RunFinding]:
    """DoDI 8510.01 2.13.a and 3.3.a(1)(a): the categorization is documented in the program's
    capabilities document (the CDD, or the equivalent requirements document after JCIDS)."""
    out: list[RunFinding] = []
    categorization = _dict(facts_mod.get(ctx.facts, "categorization"))
    document = _dict(_held(ctx, PREQ_FILE).get("capability_document"))
    if not categorization or not document:  # a system with no capability document has none
        return out

    def err(message: str) -> None:
        out.append(make("ACQLC-005", message, FACTS_FILE, None, {"C-2"}))

    where = categorization.get("documented_in")
    if not isinstance(where, str) or not where:
        err("document the categorization in the capability document: "
            "categorization.documented_in")
        return out
    if where != document.get("id"):
        err(f"the categorization is documented in {where}, not in the capability document "
            f"{document.get('id')} the program's requirements rest on")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("ACQLC-001", combined_pathways), ("ACQLC-002", cdd_validation),
                ("ACQLC-003", operations), ("ACQLC-004", capability_document),
                ("ACQLC-005", categorization_documented))
