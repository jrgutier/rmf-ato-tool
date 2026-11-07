"""Software rules of DoWI 8430.01, SWA-001 and SWA-002 (Tasks S-4 and P-14).

SWA-001 reads artifacts/data/software.yaml (with ART-CMP) while S-4 is in the run's scope: the
CI/CD pipeline and build, AI used in development, the SBOM and integrated cyber test of covered
software. SWA-002 reads the third-party components of artifacts/data/ra.yaml (ART-RA) while
P-14 is. Each stays quiet about a file that is missing or unreadable (RUN-ART-001 and RUN-FM-001
report those) and reports malformed records as findings."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

SOFTWARE_FILE = "artifacts/data/software.yaml"
RA_FILE = "artifacts/data/ra.yaml"
PLAN, ASSESS_RISK = "S-4", "P-14"
# Product kinds that are or carry covered software: DoWI 8430.01's glossary counts any software,
# firmware, operating system, application or cloud-based service developed, acquired, integrated
# or operated for the DoW. A hardware product may still hold firmware, so it must say why not.
SOFTWARE_KINDS = ("software", "software-enabled-hardware", "service")
HARDWARE = "hardware"
SECTIONS = ("pipeline", "ai_development", "evidence", "test_and_evaluation")


def product_kind(ctx: Context) -> Any:
    acquisition = facts_mod.get(ctx.facts, "acquisition")
    return acquisition.get("product_kind") if isinstance(acquisition, dict) else None


def has_covered_software(ctx: Context) -> bool:
    """Whether DoWI 8430.01 binds the system: its software record says so, or its product kind
    is or carries software."""
    data = ctx.data(SOFTWARE_FILE)
    declared = isinstance(data, dict) and data.get("covered_software") is True
    return declared or product_kind(ctx) in SOFTWARE_KINDS

def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [r for r in _list(value) if isinstance(r, dict)]


def _finding(rule: str, message: str, task: str, path: str) -> RunFinding:
    return make(rule, message, path, None, {task})


def software(ctx: Context) -> list[RunFinding]:
    """SWA-001: covered software is produced by a secure, automated CI/CD pipeline with signed
    provenance, carries an SBOM that holds its custom, COTS, third-party and transitive
    components, uses only approved AI applications that meet 3.6.d, and plans independent
    government cyber DT&E (DoWI 8430.01 2.8.b, 2.8.k, 3.5, 3.6)."""
    if PLAN not in scope.active_tasks(ctx.run):
        return []
    data = ctx.data(SOFTWARE_FILE)
    if not isinstance(data, dict):
        return []
    kind = product_kind(ctx)
    if data.get("covered_software") is not True:
        if kind in SOFTWARE_KINDS:
            return [_finding("SWA-001", f"the system's product kind is {kind}, and software.yaml "
                             "says it includes no covered software", PLAN, SOFTWARE_FILE)]
        if kind == HARDWARE and not data.get("covered_software_reason"):
            return [_finding("SWA-001", "the hardware product says it includes no covered "
                             "software and does not say why it holds no firmware or other "
                             "software", PLAN, SOFTWARE_FILE)]
        return []

    def err(message: str) -> RunFinding:
        return _finding("SWA-001", message, PLAN, SOFTWARE_FILE)

    out = [err(f"the system includes covered software and software.yaml has no {key}")
           for key in SECTIONS if not isinstance(data.get(key), dict)]
    pipeline = _dict(data.get("pipeline"))
    produced = pipeline.get("produced") is not False  # 3.5.c.(1) binds producing software
    if "pipeline" in data and produced and pipeline.get("automated") is not True:
        out.append(err("the covered software is not produced by a secure, automated CI/CD "
                       "pipeline"))
    if "pipeline" in data and produced \
            and _dict(pipeline.get("provenance")).get("signed") is not True:
        out.append(err("the build provenance attestations are not cryptographically signed, so "
                       "they give no verifiable chain of custody"))
    sbom = _dict(_dict(data.get("evidence")).get("sbom"))
    if "evidence" in data:  # 2.8.k, 3.5.b and 3.5.i.(4): what the SBOM holds
        if produced and sbom.get("custom_generated") is not True:
            out.append(err("an SBOM is not generated and maintained for the custom software"))
        if sbom.get("cots_captured") is not True:
            out.append(err("SBOMs are not captured for the COTS software"))
        if sbom.get("third_party_included") is not True:
            out.append(err("the SBOM leaves out third-party components"))
        if sbom.get("transitive_included") is not True:
            out.append(err("the SBOM leaves out transitive dependencies"))
    ai = _dict(data.get("ai_development"))
    tools = _records(ai.get("tools"))
    if ai.get("used") is True and len(tools) == 0:
        out.append(err("AI generates or modifies the software and no AI application or service "
                       "is named"))
    for tool in tools if ai.get("used") is True else ():  # 3.6.b.(1), 3.6.d.(1)-(2)
        name = tool.get("name")
        if tool.get("on_dow_system") is not True:
            out.append(err(f"AI application {name} does not reside on a DoW information system"))
        if tool.get("no_training_on_data") is not True:
            out.append(err(f"AI application {name} has no contractual guarantee that government "
                           "data and prompts are not used to train external models"))
        if tool.get("auditable") is not True:
            out.append(err(f"AI application {name} cannot be audited and monitored by "
                           "designated authorities"))
    events = _records(_dict(data.get("test_and_evaluation")).get("cyber_dte"))
    independent = [e for e in events if e.get("independent") is True]
    if "test_and_evaluation" in data and len(independent) == 0:
        out.append(err("no periodic, independent government cyber DT&E event is planned"))
    return out


def components(ctx: Context) -> list[RunFinding]:
    """SWA-002: a non-trivial open-source component has its governance, community and license
    reviewed beyond the six risk factors, and a COTS product that does not use an available
    validated product says why (DoWI 8430.01 3.5.i; SP 800-37r2 Task I-1)."""
    if ASSESS_RISK not in scope.active_tasks(ctx.run):
        return []
    data = ctx.data(RA_FILE)
    if not isinstance(data, dict):
        return []
    out = []
    for component in _records(data.get("components")):
        name, kind = component.get("name"), component.get("kind")
        review = _dict(component.get("open_source"))
        missing = [k for k in ("governance", "community", "license") if not review.get(k)]
        if kind == "open-source" and missing:
            out.append(_finding("SWA-002", f"open-source component {name} is not reviewed for "
                                f"its {', '.join(missing)}", ASSESS_RISK, RA_FILE))
        validation = _dict(component.get("validation"))
        if kind == "cots" and validation.get("outcome") == "not-selected" \
                and not validation.get("reason"):
            out.append(_finding("SWA-002", f"COTS component {name} does not use an available "
                                "validated product and does not say why", ASSESS_RISK, RA_FILE))
    return out
