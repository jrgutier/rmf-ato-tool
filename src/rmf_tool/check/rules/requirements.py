"""Requirement rules of P-15 and P-17: REQS-001 to REQS-004. They read
artifacts/data/requirements.yaml (ART-REQ) once its task is in the run's scope, and stay quiet
about a file that is unreadable (RUN-FM-001 reports it).

The design policy statements are the DoDI 8500.01 and DoDI 5000.82 statements on system design
that no control of the baseline carries (triage, WI-209), and the DoWI 8430.01 policy, tenet and
common security and resilience requirements for covered software (WI-99). Each key names one
sentence of the source; a conditional one may be marked not applicable with a reason, an
unconditional one binds every system those instructions cover."""

from __future__ import annotations

from typing import Any

from rmf_tool.check import providers
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.software import has_covered_software
from rmf_tool.run import scope

REQUIREMENTS_FILE = "artifacts/data/requirements.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
ORG_CONTEXT_FILE = "artifacts/data/org-context.yaml"
DEFINE, ALLOCATE = "P-15", "P-17"
SOFTWARE_DP = "DP-SW-"  # DoWI 8430.01: conditional on covered software, and only on that
# key: (register entry and gist, conditional). Conditional statements hold only where their own
# words say: "whenever possible", "used in support of", "where required by DISA STIGs", "as
# appropriate", "to the extent practical", or where the system has what they speak of
# (interoperable communications, a BIOS, a procured computer asset). The rest state no condition.
DESIGN_POLICY: dict[str, tuple[str, bool]] = {
    "DP-RESILIENCE-AUDIT": ("REQ-DODI8500.01-0018: self-defense attempts leave an incident "
                            "audit trail", True),
    "DP-ARCH-PRINCIPLES": ("REQ-DODI8500.01-0020: interoperability through DoD architecture "
                           "principles and a standards-based approach", False),
    "DP-BIOMETRICS": ("REQ-DODI8500.01-0030: biometrics managed under DoDD 8521.01", True),
    "DP-ASSISTIVE-TECH": ("REQ-DODI8500.01-0166: no unnecessary restriction of assistive "
                          "technology (29 U.S.C. 791, 794, 794d)", False),
    "DP-CRYPTO-INTEROP": ("REQ-DODI8500.01-0249: interoperable communications consistent "
                          "with approved cryptographic design", True),
    "DP-CYBER-ARCH": ("REQ-DODI8500.01-0251: adherence to DoD cybersecurity architectures "
                      "as issued", False),
    "DP-MARKING-METADATA": ("REQ-DODI8500.01-0275: marking and metadata on all DoD "
                            "information", False),
    "DP-IDENTITY-ASSURANCE": ("REQ-DODI8500.01-0286: identity assurance procedures aligned "
                              "with the DoD Identity Management Strategic Plan", True),
    "DP-ENTERPRISE-ARCH": ("REQ-DODI8500.01-0341: consistent with the DoD Architecture "
                           "Framework and DoD CIO cybersecurity architectures", False),
    "DP-BIOS-MANAGE": ("REQ-DODI8500.01-0348: BIOS managed under SP 800-147 §3.2", True),
    "DP-BIOS-SPEC": ("REQ-DODI8500.01-0348: PC client specifications require BIOS "
                     "protections of SP 800-147 §3.1", True),
    "DP-TPM": ("REQ-DODI8500.01-0349: new computer assets include TPM 1.2 or higher where "
               "DISA STIGs require it", True),
    "DP-TPM-TCG": ("REQ-DODI8500.01-0350: vendor TPMs conform to Trusted Computing "
                   "Group standards and are Component-approved", True),
    "DP-TPM-ON": ("REQ-DODI8500.01-0350: the TPM is on and ready for provisioning "
                  "on receipt", True),
    "DP-TPM-JUSTIFY": ("REQ-DODI8500.01-0350: written justification to the AO for "
                       "assets procured without an available TPM", True),
    "DP-SCAP": ("REQ-DODI8500.01-0352: DoD IT complies with SCAP standards", False),
    "DP-STANDARDS-REGISTRY": ("REQ-DODI5000.82-0090: IT standards selected from the DoD IT "
                              "Standards Registry", False),
    "DP-STANDARDS-SUFFICIENT": ("REQ-DODI5000.82-0090: the standards suffice for the "
                                "interoperability and cybersecurity joint operations need",
                                False),
    "DP-DATA-PROTECTION": ("REQ-DODI5000.82-0169: industry practice for authentication, "
                           "access, encryption, monitoring and data protection", True),
    # DoWI 8430.01 binds DoW software development and deployment efforts and covered software,
    # so each holds where the system includes software the DoW develops or deploys.
    "DP-SW-PRACTICES": ("REQ-DOWI8430.01-0006: modern, secure, human-centric practices such "
                        "as Agile and DevSecOps", True),
    "DP-SW-TRACEABLE": ("REQ-DOWI8430.01-0007: measurable, testable requirements traceable to "
                        "mission critical functions, with cybersecurity, cyber resilience and "
                        "zero trust suitability", True),
    "DP-SW-SECURITY-QUALITY": ("REQ-DOWI8430.01-0090: security and quality integrated into "
                               "every step of the lifecycle", True),
    "DP-SW-COMMON-REQUIREMENTS": ("REQ-DOWI8430.01-0175: covered software developed, tested "
                                  "and validated against a common set of verifiable security "
                                  "and resilience requirements", True),
    "DP-SW-SECURE-ARCH": ("REQ-DOWI8430.01-0176: secure architecture and design: least "
                          "privilege, defense-in-depth, modularization", True),
    "DP-SW-INPUT-VALIDATION": ("REQ-DOWI8430.01-0178: input validation, output encoding and "
                               "injection prevention", True),
    "DP-SW-SAFETY": ("REQ-DOWI8430.01-0181: software safety, especially for operational "
                     "technology and mission-critical systems", True),
    "DP-SW-RESILIENCE": ("REQ-DOWI8430.01-0182: operational resilience: runtime protection, "
                         "fault tolerance, rollback and recovery", True),
}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    """A value usable as a set member or lookup key; malformed input reads as missing."""
    return value if isinstance(value, str) else None


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [r for r in _list(data.get(key)) if isinstance(r, dict)]


def _data(ctx: Context, task: str) -> dict[str, Any] | None:
    if task not in scope.active_tasks(ctx.run):
        return None
    data = ctx.data(REQUIREMENTS_FILE)
    return data if isinstance(data, dict) else None


def _finding(rule: str, message: str, task: str = DEFINE) -> RunFinding:
    return make(rule, message, REQUIREMENTS_FILE, None, {task})


def matrix(ctx: Context) -> list[RunFinding]:
    """REQS-001: the requirement matrix exists, traces each requirement upward to a need,
    policy statement or parent, keeps derived requirements in the matrix, and at P-17
    allocates each requirement to something the boundary holds."""
    active = set(scope.active_tasks(ctx.run))
    if DEFINE in active and not ctx.run.path(REQUIREMENTS_FILE).is_file():
        return [_finding("REQS-001", "ART-REQ has no artifacts/data/requirements.yaml, the "
                         "requirements traceability verification matrix")]
    data = ctx.data(REQUIREMENTS_FILE)
    if not isinstance(data, dict):
        return []
    requirements = _records(data, "requirements")
    out = _upward(data, requirements) if DEFINE in active else []
    if ALLOCATE in active:
        out += _allocation(ctx, requirements)
    return out


def _upward(data: dict[str, Any], requirements: list[dict[str, Any]]) -> list[RunFinding]:
    held = {_key(r.get("id")) for r in requirements}
    needs = {_key(n.get("id")) for n in _records(data, "needs")}
    out = []
    for req in requirements:
        ident = req.get("id")
        if not req.get("needs") and not req.get("policy") and not req.get("derived_from"):
            out.append(_finding("REQS-001", f"{ident} traces to no protection need, design "
                                "policy statement or parent requirement"))
        for need in _list(req.get("needs")):
            if _key(need) not in needs:
                out.append(_finding("REQS-001", f"{ident} traces to protection need {need}, "
                                    "which the requirements do not record"))
        for parent in _list(req.get("derived_from")):
            if _key(parent) not in held:
                out.append(_finding("REQS-001", f"derived requirement {ident} is derived from "
                                    f"{parent}, which the traceability matrix does not hold"))
            elif parent == ident:
                out.append(_finding("REQS-001", f"{ident} is derived from itself, which traces "
                                    "it to no parent"))
    return out


def _allocation(ctx: Context, requirements: list[dict[str, Any]]) -> list[RunFinding]:
    out = []
    boundary = ctx.data(BOUNDARY_FILE)
    components = {_key(c.get("id")) for c in _records(boundary, "components")} \
        if isinstance(boundary, dict) else set()
    # a provider a requirement is allocated to offers common controls (P-5; F-05-12)
    org = ctx.data(ORG_CONTEXT_FILE)
    pk = providers.keyer(ctx)
    offering = {pk(c.get("provided_by")) for c in _records(org, "common_controls")} \
        if isinstance(org, dict) else set()
    for req in requirements:
        allocated = _list(req.get("allocated_to"))
        if not allocated:
            out.append(_finding("REQS-001", f"{req.get('id')} is allocated to nothing",
                                ALLOCATE))
        for target in allocated:
            if str(target).startswith("CMP-") and _key(target) not in components:
                out.append(_finding("REQS-001", f"{req.get('id')} is allocated to {target}, "
                                    "which is not a boundary component", ALLOCATE))
            if str(target).startswith("PRV-") and target not in offering:
                out.append(_finding("REQS-001", f"{req.get('id')} is allocated to provider "
                                    f"{target}, which offers no common controls in "
                                    "org-context.yaml common_controls", ALLOCATE))
    return out


def design_policy(ctx: Context) -> list[RunFinding]:
    """REQS-002: every design policy statement is addressed once, an unconditional one
    applies, and a DoWI 8430.01 one applies wherever the system has covered software (SWA-001's
    reading of software.yaml and the product kind). REQS-005 judges what carries one."""
    data = _data(ctx, DEFINE)
    if data is None:
        return []
    software = has_covered_software(ctx)
    records = _records(data, "design_policy")
    addressed = {_key(r.get("statement")) for r in records}
    out = []
    seen: set[str] = set()
    for key in DESIGN_POLICY:
        if key not in addressed:
            out.append(_finding("REQS-002", f"{key} is not addressed: the requirements record no "
                                "decision on this design policy statement"))
    for record in records:
        key = _key(record.get("statement"))
        if key not in DESIGN_POLICY:
            out.append(_finding("REQS-002", f"{key} is no design policy statement REQS-002 "
                                "knows"))
            continue
        if key in seen:
            out.append(_finding("REQS-002", f"{key} is addressed by more than one record"))
        seen.add(key)
        if record.get("applies") is not True and not DESIGN_POLICY[key][1]:
            out.append(_finding("REQS-002", f"{key} binds every system, so it cannot be "
                                "marked not applicable"))
        elif record.get("applies") is not True and software and key.startswith(SOFTWARE_DP):
            out.append(_finding("REQS-002", f"{key} binds a system with covered software, so it "
                                "cannot be marked not applicable"))
        elif record.get("applies") is not True and not record.get("reason"):
            out.append(_finding("REQS-002", f"{key} is marked not applicable without saying why "
                                "its condition does not hold"))
    return out


def design_policy_carried(ctx: Context) -> list[RunFinding]:
    """REQS-005 (split from REQS-002): a design policy statement that applies is carried by a
    requirement the matrix holds, and the requirements' policy traces agree with the records
    that list them."""
    data = _data(ctx, DEFINE)
    if data is None:
        return []
    held = {_key(r.get("id")) for r in _records(data, "requirements")}
    records = _records(data, "design_policy")
    traces = {(_key(r.get("id")), _key(k)) for r in _records(data, "requirements")
              for k in _list(r.get("policy"))}
    out = []
    for ident, key in sorted(traces, key=str):
        if key not in DESIGN_POLICY:
            out.append(_finding("REQS-005", f"{ident} traces to {key}, which is no design "
                                "policy statement REQS-002 knows"))
        elif (ident, key) not in {(_key(r), _key(c.get("statement"))) for c in records
                                  if c.get("applies") is True
                                  for r in _list(c.get("requirements"))}:
            out.append(_finding("REQS-005", f"{ident} traces to {key}, but the {key} record "
                                "does not list it as carrying the statement"))
    for record in records:
        key = _key(record.get("statement"))
        if key not in DESIGN_POLICY:
            continue
        carried = [r for r in _list(record.get("requirements")) if _key(r) in held]
        for req in _list(record.get("requirements")):
            if (_key(req), key) not in traces:
                out.append(_finding("REQS-005", f"the {key} record lists {req}, whose policy "
                                    "trace does not name the statement"))
        if record.get("applies") is True and len(carried) == 0:
            out.append(_finding("REQS-005", f"{key} applies but no requirement of the matrix "
                                "carries it"))
    return out


def needs_and_agreement(ctx: Context) -> list[RunFinding]:
    """REQS-003: each protection need is held by a stakeholder persona, traced by a
    requirement, and agreed to by its stakeholder."""
    data = _data(ctx, DEFINE)
    if data is None:
        return []
    needs = _records(data, "needs")
    traced = {_key(n) for r in _records(data, "requirements") for n in _list(r.get("needs"))}
    agreement = data.get("agreement")
    agreed = {_key(a.get("stakeholder")) for a in _records(agreement, "agreed")} \
        if isinstance(agreement, dict) else set()
    out = []
    for need in needs:
        ident, holder = need.get("id"), _key(need.get("stakeholder"))
        if holder not in ctx.run.personas:
            out.append(_finding("REQS-003", f"{ident}: stakeholder {holder} is not a framework "
                                "persona"))
        if need.get("kind") == "loss-concern" and not need.get("assets"):
            out.append(_finding("REQS-003", f"{ident} is a loss concern that names no asset"))
        if ident not in traced:
            out.append(_finding("REQS-003", f"protection need {ident} is traced by no "
                                "requirement"))
    for holder in sorted({_key(n.get("stakeholder")) for n in needs} - agreed, key=str):
        out.append(_finding("REQS-003", f"{holder} holds a protection need but has not agreed "
                            "that the requirements address it"))
    return out


def workforce(ctx: Context) -> list[RunFinding]:
    """REQS-004: at P-17, contracts for cyberspace work roles specify workforce qualification
    requirements, apply DFARS Subpart 239.71, and document contractor qualifications."""
    data = _data(ctx, ALLOCATE)
    if data is None:
        return []
    terms = data.get("workforce")
    if not isinstance(terms, dict):
        return [_finding("REQS-004", "the requirements do not say which cyberspace work roles "
                         "contractor personnel perform", ALLOCATE)]
    if not terms.get("contracted_work_roles"):
        return []
    contract = {_key(r.get("id")) for r in _records(data, "requirements")
                if "contract" in _list(r.get("allocated_to"))}
    out = []
    if _key(terms.get("qualification_requirement")) not in contract:
        out.append(_finding("REQS-004", "no requirement allocated to the contract specifies "
                            "workforce qualifications for the contracted cyberspace work roles",
                            ALLOCATE))
    if terms.get("dfars_239_71") != "applied":
        out.append(_finding("REQS-004", "the contract for cyberspace work roles does not apply "
                            "the DFARS Subpart 239.71 qualification standards", ALLOCATE))
    if terms.get("qualifications_documented") is not True:
        out.append(_finding("REQS-004", "contractor personnel performing cyberspace work roles "
                            "do not have their qualifications documented", ALLOCATE))
    return out
