"""System security engineering rules, SSE-001 to SSE-003 and SSEP-001 (Tasks P-15 and S-4).

SSE-001 and SSE-002 read the ``derivation`` and ``engineering`` sections of
artifacts/data/requirements.yaml (ART-REQ) while P-15 is in the run's scope: how the lead
systems engineer derived the security requirements (DoDI 5000.83 3.3.c.(1)), and the system
security engineering practices and assurance level the program employs (DoDI 5000.83 1.2.c);
SSEP-001, split from SSE-002, reads the same section for privacy engineering and the design
principles.
SSE-003 reads the SSP statements of the baseline controls the SP 800-53r5 catalog marks as
contributing to assurance (FIPS 200 Section 4, SP 800-37r2 Task I-1). Each stays quiet about a
file that is missing or unreadable (RUN-ART-001 and RUN-FM-001 report those) and reports
malformed records as findings."""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.check.rules.software import product_kind
from rmf_tool.run import scope

REQUIREMENTS_FILE = "artifacts/data/requirements.yaml"
DEFINE, PLAN = "P-15", "S-4"
# DoDI 5000.83 3.3.c.(1).(a): the four documents that inform requirements derivation; the
# first may be a draft or validated CDD "or equivalent capability requirements document".
INFORMING = {"capability-requirements": "capability requirements document",
             "concept-of-operations": "concept of operations",
             "operational-mode-summary": "operational mode summary",
             "mission-profiles": "mission profiles"}
# 3.3.c.(1).(d): where the vulnerabilities the derived requirements minimize are introduced.
VULNERABILITY_SOURCES = ("design", "implementation", "interfaces", "access-points")
# 3.3.c.(1).(c): what the key performance parameters and attributes establish.
ESTABLISHED = ("survivability", "sustainment", "security")
CIA = ("confidentiality", "integrity", "availability")
# 3.3.c.(1): where the cybersecurity, security and other system requirements are included.
INCLUSION = {"performance-specification": "system performance specification",
             "product-support": "product support needs"}
# DoDI 5000.83 1.2.c: the practices, and the life cycle activities they are employed in.
SSE_AREAS = ("cybersecurity", "cyber-resilience", "cyber-survivability")
SSE_STAGES = ("design", "test", "manufacture", "sustainment")
PROGRAM_PROTECTION = "program-protection"  # DoDI 5000.83 3.2.a
PRIVACY_ENGINEERING = "privacy-engineering"  # SP 800-53r5 1.3, for a system with PII
# SP 800-160v1r1 Appendix E, the principles for trustworthy secure design (E.1 to E.30).
PRINCIPLES = frozenset({
    "anomaly-detection", "clear-abstractions", "commensurate-protection",
    "commensurate-response", "commensurate-rigor", "commensurate-trustworthiness",
    "compositional-trustworthiness", "continuous-protection", "defense-in-depth",
    "distributed-privilege", "diversity", "domain-separation", "hierarchical-protection",
    "least-functionality", "least-persistence", "least-privilege", "least-sharing",
    "loss-margins", "mediated-access", "minimal-trusted-elements", "minimize-detectability",
    "protective-defaults", "protective-failure", "protective-recovery", "reduced-complexity",
    "redundancy", "self-reliant-trustworthiness", "structured-decomposition-and-composition",
    "substantiated-trustworthiness", "trustworthy-system-control",
})
# An SSP status that says the system implements the control, so its assurance must be satisfied.
# An inherited control's provider addresses its assurance, so the system authors none for it.
IN_PLACE = ("implemented",)
INHERITED = "inherited"
# A software-only product or service has no manufacture activity of its own.
UNMANUFACTURED = ("software", "service")


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    """A value usable as a set member or lookup key; malformed input reads as missing."""
    return value if isinstance(value, str) else None


def _records(data: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    return [r for r in _list(data.get(key)) if isinstance(r, dict)]


def _keys(record: dict[str, Any], key: str) -> set[str]:
    return {k for k in map(_key, _list(record.get(key))) if k}


def _section(ctx: Context, key: str) -> tuple[dict[str, Any] | None, Any]:
    """The requirements and one of its sections, while P-15 is in the run's scope."""
    if DEFINE not in scope.active_tasks(ctx.run):
        return None, None
    data = ctx.data(REQUIREMENTS_FILE)
    if not isinstance(data, dict):
        return None, None
    return data, data.get(key)


def _finding(rule: str, message: str, task: str = DEFINE,
             path: str = REQUIREMENTS_FILE) -> RunFinding:
    return make(rule, message, path, None, {task})


def derivation(ctx: Context) -> list[RunFinding]:
    """SSE-001: the security requirements are derived from the capability requirements
    document, CONOPS, operational mode summary and mission profiles by derivation methods that
    cover design, implementation, interfaces and access points; the key performance parameters
    and attributes establish survivability, sustainment and security measures; exportability
    requirements are derived; and the requirements enter the system performance specification
    and the product support needs (DoDI 5000.83 3.3.c.(1))."""
    data, record = _section(ctx, "derivation")
    if data is None:
        return []
    if not isinstance(record, dict):
        return [_finding("SSE-001", "the requirements do not record how the system security "
                         "requirements were derived (derivation)")]
    held = {_key(r.get("id")) for r in _records(data, "requirements")}
    out: list[RunFinding] = []
    out += _informed(record)
    out += _methods(record, held)
    out += _key_performance(record, held)
    exportability = _list(record.get("exportability"))
    for req in exportability:
        if _key(req) not in held:
            out.append(_finding("SSE-001", f"exportability requirement {req} is not a "
                                "requirement of the traceability matrix"))
    if len(exportability) == 0 and not record.get("exportability_none"):
        out.append(_finding("SSE-001", "the derivation names no exportability requirement and "
                            "does not say why none is derived"))
    out += _inclusion(data)
    return out


def _informed(record: dict[str, Any]) -> list[RunFinding]:
    kinds = {_key(r.get("kind")) for r in _records(record, "informed_by")}
    return [_finding("SSE-001", f"requirements derivation is not informed by the {label}")
            for kind, label in INFORMING.items() if kind not in kinds]


def _methods(record: dict[str, Any], held: set[str | None]) -> list[RunFinding]:
    methods = _records(record, "methods")
    out = []
    covered: set[str] = set()
    for method in methods:
        name = method.get("method")
        covered |= _keys(method, "addresses")
        for req in _list(method.get("requirements")):
            if _key(req) not in held:
                out.append(_finding("SSE-001", f"derivation method {name} derives {req}, which "
                                    "the traceability matrix does not hold"))
    for source in VULNERABILITY_SOURCES:
        if source not in covered:
            out.append(_finding("SSE-001", "no derivation method derives requirements that "
                                f"minimize vulnerabilities introduced by {source}"))
    return out


def _key_performance(record: dict[str, Any], held: set[str | None]) -> list[RunFinding]:
    parameters = _records(record, "key_performance")
    out = []
    established: set[str] = set()
    for kpp in parameters:
        name = kpp.get("name")
        kinds = _keys(kpp, "establishes")
        established |= kinds
        if "security" in kinds and not _keys(kpp, "based_on") & set(CIA):
            out.append(_finding("SSE-001", f"{name} establishes information system security "
                                "measures based on no confidentiality, integrity or "
                                "availability need"))
        for req in _list(kpp.get("requirements")):
            if _key(req) not in held:
                out.append(_finding("SSE-001", f"{name} names {req}, which is no "
                                    "requirement of the traceability matrix"))
    for kind in ESTABLISHED:
        if kind not in established:
            out.append(_finding("SSE-001", "no key performance parameter or attribute "
                                f"establishes {kind} measures"))
    return out


def _inclusion(data: dict[str, Any]) -> list[RunFinding]:
    out = []
    included: set[str] = set()
    for req in _records(data, "requirements"):
        places = _keys(req, "included_in") & set(INCLUSION)
        included |= places
        if req.get("kind") == "security" and len(places) == 0:
            out.append(_finding("SSE-001", f"{req.get('id')} is included in neither the system "
                                "performance specification nor the product support needs"))
    for place, label in INCLUSION.items():
        if place not in included:
            out.append(_finding("SSE-001", f"no requirement is included in the {label}"))
    return out


def practices(ctx: Context) -> list[RunFinding]:
    """SSE-002: the program employs system security engineering practices for cybersecurity,
    cyber resilience and cyber survivability in design, test, manufacture (none for a software
    product or service) and sustainment, for
    program protection, and for privacy where the system holds PII; they apply named principles
    of trustworthy secure design; and the assurance level is commensurate with the technology,
    program, system and mission objectives (DoDI 5000.83 1.2.c and 3.2.a)."""
    data, record = _section(ctx, "engineering")
    if data is None:
        return []
    if not isinstance(record, dict):
        return [_finding("SSE-002", "the requirements do not record the system security "
                         "engineering practices the program employs (engineering)")]
    entries = _records(record, "practices")
    pairs = {(_key(p.get("area")), stage) for p in entries for stage in _keys(p, "stages")}
    areas = {_key(p.get("area")) for p in entries}
    stages = [s for s in SSE_STAGES
              if not (s == "manufacture" and product_kind(ctx) in UNMANUFACTURED)]
    out = []
    for area in SSE_AREAS:
        for stage in stages:
            if (area, stage) not in pairs:
                out.append(_finding("SSE-002", f"no system security engineering practice "
                                    f"addresses {area} in {stage}"))
    if PROGRAM_PROTECTION not in areas:
        out.append(_finding("SSE-002", "the program employs no system security engineering "
                            "practice for program protection"))
    out += _assurance_level(record.get("assurance"), {
        _key(r.get("id")): r for r in _records(data, "requirements")})
    return out


# --- SSEP-001 (split from SSE-002) --------------------------------------------------------
def design_practices(ctx: Context) -> list[RunFinding]:
    """SSEP-001: the engineering practices employ privacy engineering where the system holds
    PII, and apply named principles for trustworthy secure design of SP 800-160v1r1 Appendix E
    (DoDI 5000.83 3.2.a). SSE-002 asks the areas, stages, program protection and assurance."""
    _, record = _section(ctx, "engineering")
    if not isinstance(record, dict):
        return []  # SSE-002 reports the missing engineering record
    entries = _records(record, "practices")
    areas = {_key(p.get("area")) for p in entries}
    out = []
    if ctx.processes_pii and PRIVACY_ENGINEERING not in areas:
        out.append(_finding("SSEP-001", "the system processes PII and employs no privacy "
                            "engineering practice"))
    applied: set[str] = set()
    for practice in entries:
        for principle in _keys(practice, "principles"):
            if principle in PRINCIPLES:
                applied.add(principle)
            else:
                out.append(_finding("SSEP-001", f"{principle} is not a principle for "
                                    "trustworthy secure design of SP 800-160v1r1 Appendix E"))
    if len(applied) == 0:
        out.append(_finding("SSEP-001", "no practice applies a principle for trustworthy "
                            "secure design to develop and integrate the system components"))
    return out


def _assurance_level(record: Any, matrix: dict[str | None, dict[str, Any]]) -> list[RunFinding]:
    record = record if isinstance(record, dict) else {}
    out = []
    carried = [r for r in _list(record.get("requirements"))
               if _measure(matrix.get(_key(r))) == "assurance"]
    if len(carried) == 0:
        out.append(_finding("SSE-002", "the level of assurance is carried by no requirement of "
                            "the traceability matrix with an assurance measure"))
    return out


def _measure(requirement: dict[str, Any] | None) -> Any:
    measure = (requirement or {}).get("measure")
    return measure.get("kind") if isinstance(measure, dict) else None


def control_assurance(ctx: Context) -> list[RunFinding]:
    """SSE-003: every baseline control the catalog marks as contributing to assurance says in
    its SSP statement how its assurance requirements are addressed, and once it is in place they
    are satisfied (FIPS 200 Section 4; SP 800-37r2 Task I-1)."""
    if PLAN not in scope.active_tasks(ctx.run):
        return []
    selected = set(baseline_mod.control_ids(ctx.run))
    statements = [(p, r) for p, r in family_records(ctx, SSP_DIR, "controls")
                  if _key(r.get("control_id")) in selected]
    if not statements:  # no plan yet, so no catalog to read
        return []
    cat = catalog.load(ctx.run.repo)
    out = []
    for path, record in statements:
        cid = _key(record.get("control_id"))
        if record.get("status") == INHERITED \
                or not catalog.contributes_to_assurance(cat, str(cid)):
            continue
        assurance = record.get("assurance")
        assurance = assurance if isinstance(assurance, dict) else {}
        if not assurance.get("addressed"):
            out.append(_finding("SSE-003", f"{cid} contributes to assurance, and its SSP "
                                "statement does not say how its assurance requirements are "
                                "addressed", PLAN, path))
        elif record.get("status") in IN_PLACE and assurance.get("status") != "satisfied":
            out.append(_finding("SSE-003", f"{cid} is in place, and the minimum assurance "
                                "requirements it carries for the baseline are not satisfied",
                                PLAN, path))
    return out
