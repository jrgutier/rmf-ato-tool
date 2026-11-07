"""AC-5/AC-6: the framework schema accepts the real and mini frameworks, the run-side data
contracts are valid Draft 2020-12 schemas that accept a minimal example and reject a
broken one, and unreadable framework files are FW-SCHEMA-001 findings."""

import json
import shutil

import jsonschema
import pytest
from _framework_fixtures import MINI, P3A, REAL
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.framework.load import load
from rmf_tool.framework.model import SCHEMA_DIR
from rmf_tool.framework.validate import fact_paths, schema_findings, validate

SCHEMAS = REPO_ROOT / SCHEMA_DIR
PLAN_RUN_SCHEMAS = {
    "artifact-frontmatter", "run-config", "scenario", "product-profile", "facts", "interview",
    "assumptions", "infotypes", "users", "boundary", "leveraged-authorizations", "inventory",
    "ssp-controls", "sap", "sar-results", "poam-items", "stig-summary", "baseline", "decision",
    "authorizations",
}
# data named in plan §6.4, then the ones p11 added
EXTRA_RUN_SCHEMAS = {"tailoring", "allocation", "conmon", "rar", "authorization-report",
                     "dias", "cm-plan", "contingency", "incident-response",
                     "service-agreements", "ssp-records",
                     "changes", "posture-reports", "plan-reviews", "capabilities",
                     "sar-report", "ra",
                     "requirements", "software", "system-description", "sar-summary",
                     "org-context", "disposal",
                     "protection", "st-protection", "protection-requirements", "nss-assessments",
                     "test-strategy", "registration", "pia", "cato", "cloud"}
# framework/baselines/*.yaml (ADR-0002)
FRAMEWORK_DATA_SCHEMAS = {"baselines", "tailoring-inputs", "overlay-specs"}


def schema(name):
    return json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))


def errors(name, instance):
    validator = jsonschema.Draft202012Validator(schema(name),
                                                format_checker=jsonschema.FormatChecker())
    return [e.message for e in validator.iter_errors(instance)]


def test_real_framework_valid():
    loaded = load(REAL, REPO_ROOT)
    assert loaded.findings == []
    assert schema_findings(loaded, REPO_ROOT) == []
    result = validate(REAL, REPO_ROOT, P3A)
    assert result.ok, [f.render() for f in result.findings]
    assert result.stats["tasks"] == 47 and result.stats["deferred_citations"] == 0


def test_real_framework_task_set_is_exact():
    assert load(REAL, REPO_ROOT).framework.meta["task_set"]["mode"] == "exact"


def test_mini_framework_valid():
    result = validate(MINI, REPO_ROOT, P3A)
    assert result.ok, [f.render() for f in result.findings]
    assert result.stats["tasks"] == 5


def test_schema_files_are_the_planned_set():
    names = {p.name.removesuffix(".schema.json") for p in SCHEMAS.glob("*.schema.json")}
    assert names == {"framework"} | PLAN_RUN_SCHEMAS | EXTRA_RUN_SCHEMAS | FRAMEWORK_DATA_SCHEMAS


@pytest.mark.parametrize("path", sorted(SCHEMAS.glob("*.schema.json")), ids=lambda p: p.name)
def test_schema_is_valid_draft_2020_12(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(doc)
    assert doc["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert doc["$id"] == f"urn:rmf-tool:schema:{path.name.removesuffix('.schema.json')}"


FRONTMATTER = {"artifact_id": "ART-SSP", "run_id": "example-synthetic-01",
               "produced_by_task": "S-4", "touched_by": ["S-4", "I-2"],
               "sources": ["INT-007.A3", "product/architecture.md#identity", "ASM-001"]}


def test_frontmatter_schema_rejects_fact_fields():
    assert errors("artifact-frontmatter", FRONTMATTER) == []
    for fact in ("system_name", "categorization", "baseline_id", "boundary_id"):
        assert errors("artifact-frontmatter", {**FRONTMATTER, fact: "x"}), fact
    assert errors("artifact-frontmatter", {k: v for k, v in FRONTMATTER.items()
                                           if k != "sources"})


SRC = ["INT-001.A1"]
_RA = YAML(typ="safe").load((REPO_ROOT / "templates/data/ra.yaml").read_text(encoding="utf-8"))
NEED = {"id": "NEED-01", "stakeholder": "PER-IO", "kind": "loss-concern", "concern": "c",
        "assets": ["a"], "success_criteria": "s", "priority": 1, "rationale": "r", "sources": SRC}
REQUIREMENT = {"id": "REQ-01", "statement": "s", "kind": "security", "needs": ["NEED-01"],
               "priority": 1, "criticality": 1, "measure": {"kind": "assurance", "statement": "m"},
               "verification": {"method": "test", "description": "d"}, "sources": SRC}
AGREEMENT = {"analysis": "a", "feedback": "f",
             "agreed": [{"stakeholder": "PER-IO", "date": "2026-01-02", "decisions": "d"}],
             "sources": SRC}
DERIVATION = {
    "informed_by": [{"kind": "concept-of-operations", "document": "CONOPS"}],
    "methods": [{"method": "misuse cases", "addresses": ["design"], "requirements": ["REQ-01"]}],
    "key_performance": [{"name": "Survivability KPP", "establishes": ["survivability"]}],
    "exportability": ["REQ-01"], "sources": SRC}
ENGINEERING = {
    "practices": [{"area": "cybersecurity", "stages": ["design"], "practice": "p"}],
    "assurance": {"level": "l", "requirements": ["REQ-01"], "commensurate_with": {
        "technology": "t", "program": "p", "system": "s", "mission": "m"}},
    "sources": SRC}
RUN_EXAMPLES = {
    "capabilities": (
        {"capabilities": [{"id": "CAP-01", "name": "Secure remote authentication",
                           "controls": ["ia-2.1", "ia-2.2", "sc-8.1"], "sources": SRC}]},
        {"capabilities": [{"id": "CAP-01", "name": "x", "controls": [], "sources": SRC}]}),
    "run-config": (
        {"mode": "hybrid", "run_id": "example-synthetic-01", "product": "../../product",
         "as_of": "2026-10-29T12:00:00Z", "framework_version": "0.1.0", "git_sha": "abc1234",
         "upstream_hash": "a" * 64, "oscal_version": "1.2.1", "humans": {"PER-AO": None},
         "scope": {"tasks": ["P-10", "C-1"]},
         "seeded": [{"artifact": "ART-RA", "from_task": "P-14", "path": "artifacts/ART-RA.md"}],
         "lifecycle_stop": "R-5", "include_after_stop": ["M-1"],
         "lifecycle_stop_rationale": "in EMD", "deferred": {
             "P-4": {"kind": "not-applicable", "rationale": "no tailored org baseline"}}},
        {"mode": "auto"}),
    "scenario": (
        {"name": "skeleton", "description": "12-task slice", "product": "tests/agent/products/esg",
         "scope": {"tasks": "all"}, "seeded": [], "hash_globs": ["AGENTS.md"],
         "control_subset": ["ac-2", "sc-7"]},
        {"name": "skeleton", "description": "x", "product": "p", "scope": {"tasks": []},
         "seeded": [], "hash_globs": []}),
    "product-profile": (
        {"name": "Example Sensor Gateway", "acronym": "ESG", "pathway": "PW-MCA",
         "current_phase": "PH-EMD", "pii": False, "nss": True,
         "proposed_categorization": {"c": "moderate", "i": "moderate", "a": "low"}},
        {"name": "x", "acronym": "ESG", "pathway": "PW-MCA", "current_phase": "PH-EMD",
         "pii": False, "nss": True, "proposed_categorization": {"c": "medium", "i": "low",
                                                                "a": "low"}}),
    "facts": (
        {"system_id": {"value": "ESG-001", "set_by_task": "C-1", "sources": SRC},
         "lifecycle_state": {"value": "under-development", "set_by_task": "C-1"},
         "categorization": {"c": "moderate", "i": "moderate", "a": "low", "overlays": [],
                            "set_by_task": "C-2",
                            "approved": {"value": True, "approved_by": "PER-AO",
                                         "set_by_task": "C-3"}},
         "baseline_id": {"value": "cnssi1253-m-m-l", "set_by_task": "S-1"}},
        {"system_id": {"value": "ESG-001"}}),
    "interview": (
        {"interview_id": "INT-007", "run_id": "example-synthetic-01", "task": "S-4",
         "persona": "PER-ISSO", "date": "2026-10-29"},
        {"interview_id": "INT-7", "run_id": "r", "task": "S-4", "persona": "ISSO",
         "date": "yesterday"}),
    "assumptions": (
        {"assumptions": [{"id": "ASM-BASELINE-001", "statement": "s", "rationale": "r",
                          "task": "S-1", "persona": "PER-AO", "tag": "ASSUMPTION"}]},
        {"assumptions": [{"id": "ASM-001", "statement": "s", "rationale": "r", "task": "S-1",
                          "tag": "SIMULATED"}]}),
    "infotypes": (
        {"information_types": [{"id": "INF-01", "title": "Mission data", "description": "d",
                                "sp800_60_ids": ["C.3.5.1"],
                                "confidentiality": {"base": "moderate"},
                                "integrity": {"base": "moderate"},
                                "availability": {"base": "low", "selected": "moderate",
                                                 "adjustment_justification": "mission"},
                                "life_cycle": [{"stage": "collection", "description": "d"}],
                                "sources": SRC}]},
        {"information_types": []}),
    "users": (
        {"users": [{"id": "USR-OPERATOR", "title": "Operator", "type": "internal",
                    "privilege_level": "non-privileged",
                    "authorized_privileges": [{"title": "operate",
                                               "functions_performed": ["fly"]}],
                    "sources": SRC}]},
        {"users": [{"id": "USR-OPERATOR", "title": "Operator", "type": "contractor",
                    "privilege_level": "non-privileged", "authorized_privileges": [],
                    "sources": SRC}]}),
    "boundary": (
        {"authorization_boundary": {"description": "d", "sources": SRC},
         "network_architecture": {"description": "d", "sources": SRC,
                                  "diagrams": [{"path": "artifacts/net.svg", "caption": "c"}]},
         "data_flow": {"description": "d", "sources": SRC},
         "components": [{"id": "CMP-GCS", "title": "GCS", "type": "this-system",
                         "description": "d", "status": "under-development", "sources": SRC}]},
        {"authorization_boundary": {"description": "d", "sources": SRC},
         "network_architecture": {"description": "d", "sources": SRC},
         "data_flow": {"description": "d", "sources": []}, "components": []}),
    "leveraged-authorizations": (
        {"leveraged_authorizations": [{"id": "LA-01", "title": "Enclave", "provider": "DISA",
                                       "date_authorized": "2026-01-15", "sources": SRC}]},
        {"leveraged_authorizations": [{"id": "LA-1", "title": "Enclave", "provider": "DISA",
                                       "date_authorized": "2026-01-15", "sources": SRC}]}),
    "inventory": (
        {"items": [{"id": "INV-001", "description": "Laptop", "kind": "hardware",
                    "component": "CMP-GCS", "sources": SRC}]},
        {"items": [{"id": "INV-001", "description": "Laptop", "kind": "hardware",
                    "component": "this-system", "sources": SRC}]}),
    "ssp-controls": (
        {"family": "ac", "controls": [{"control_id": "ac-2.1", "status": "inherited",
                                       "statement": "s", "responsible_roles": ["PER-CCP"],
                                       "components": ["this-system"], "inherited_from": "LA-01",
                                       "sources": SRC}]},
        {"family": "ac", "controls": [{"control_id": "AC-2", "status": "implemented",
                                       "statement": "s", "responsible_roles": ["PER-ISSO"],
                                       "components": ["this-system"], "sources": SRC}]}),
    "sap": (
        {"scope": {"include": "baseline", "excluded_controls": []},
         "assessment_subjects": [{"type": "component", "include": "all"}],
         "team": [{"persona": "PER-SCA", "role": "lead", "independent": True}],
         "schedule": {"start": "2026-11-01", "end": "2026-11-20",
                      "events": [{"date": "2026-11-05", "description": "scan", "kind": "scan"}]},
         "rules_of_engagement": "r", "sources": SRC},
        {"scope": {"include": "everything", "excluded_controls": []},
         "assessment_subjects": [], "team": [], "schedule": {"start": "2026-11-01"},
         "rules_of_engagement": "r", "sources": SRC}),
    "sar-results": (
        {"family": "ac",
         "determinations": [{"control_id": "ac-2", "result": "other-than-satisfied",
                             "methods": ["examine", "test"], "summary": "s",
                             "finding_refs": ["FND-001"], "sources": SRC}],
         "findings": [{"id": "FND-001", "control_id": "ac-2", "title": "t", "description": "d",
                       "status": "open", "severity": "moderate", "sources": SRC}]},
        {"family": "ac", "determinations": [{"control_id": "ac-2", "result": "passed",
                                             "methods": [], "summary": "s", "sources": SRC}],
         "findings": []}),
    "poam-items": (
        {"items": [{"id": "POAM-001", "finding_ref": "STG-003", "control_id": "cm-6",
                    "weakness": "w", "status": "open", "point_of_contact": "PER-ISSM",
                    "scheduled_completion": "2027-01-31",
                    "milestones": [{"description": "patch", "due": "2026-12-15"}]}]},
        {"items": [{"id": "POAM-001", "finding_ref": "F-1", "control_id": "cm-6",
                    "weakness": "w", "status": "open"}]}),
    "stig-summary": (
        {"benchmarks": [{"id": "BM-01", "title": "Windows 11 STIG", "version": "V2R1",
                         "applies_to": ["INV-002"]}],
         "not_applicable": [{"inventory_item": "INV-003", "rationale": "firmware only"}],
         "findings": [{"id": "STG-001", "benchmark": "BM-01", "rule_id": "V-253256",
                       "category": "CAT I", "inventory_item": "INV-002", "title": "t",
                       "status": "open"}]},
        {"benchmarks": [], "not_applicable": [],
         "findings": [{"id": "STG-001", "benchmark": "BM-01", "rule_id": "V-1",
                       "category": "CAT 1", "inventory_item": "INV-002", "title": "t",
                       "status": "open"}]}),
    "baseline": (
        {"baseline_id": "cnssi1253-m-m-l", "method": "cnssi1253",
         "categorization": {"c": "moderate", "i": "moderate", "a": "low"}, "overlays": [],
         "sources": [{"path": "references/oscal/catalog/x.json", "sha256": "b" * 64}],
         "controls": [{"control_id": "ac-2", "origin": "baseline"}]},
        {"baseline_id": "x", "method": "cnssi1253", "categorization": {"c": "moderate",
                                                                       "i": "moderate"},
         "overlays": [], "sources": [], "controls": []}),
    "decision": (
        {"decision": "AD-ATOC", "decided_by": "PER-AO", "date": "2026-12-01",
         "authorization_termination_date": "2029-12-01",
         "conditions": [{"id": "COND-01", "description": "patch planner", "due": "2027-03-01"}],
         "risk_level": "moderate", "rar_ref": "ART-RAR", "rationale": "r", "sources": SRC},
        {"decision": "ATO", "decided_by": "PER-AO", "date": "2026-12-01", "rationale": "r",
         "sources": SRC}),
    "authorizations": (
        {"records": [{"id": "AUTH-001", "decision": "AD-ATOC", "subject": "system",
                      "basis": "initial", "decided_by": "PER-AO", "task": "R-4",
                      "date": "2026-12-01", "risk_level": "moderate",
                      "risk_acceptance": "I accept the risk.", "signature": "pki",
                      "conveyed_to": ["PER-PM"], "rationale": "r", "sources": SRC}]},
        {"records": [{"id": "AUTH-1", "decision": "ATO", "decided_by": "PER-AO",
                      "date": "2026-12-01", "rationale": "r", "sources": SRC}]}),
    "tailoring": (
        {"actions": [{"control_id": "ac-17", "action": "remove", "rationale": "no remote access",
                      "sources": SRC}]},
        {"actions": [{"control_id": "ac-17", "action": "drop", "rationale": "r",
                      "sources": SRC}]}),
    "allocation": (
        {"allocations": [{"control_id": "pe-3", "type": "common", "components": ["this-system"],
                          "provider": "Base facility", "sources": SRC}]},
        {"allocations": [{"control_id": "pe-3", "type": "shared", "components": [],
                          "sources": SRC}]}),
    "conmon": (
        {"frequencies": [{"family": "ac", "frequency": "monthly", "method": "automated scan",
                          "responsible": "PER-ISSO"}],
         "ongoing_authorization": {"time_trigger_days": 365, "event_triggers": ["new CAT I"]},
         "reporting": {"recipients": ["PER-AO"], "frequency": "quarterly"}, "sources": SRC},
        {"frequencies": [], "ongoing_authorization": {"time_trigger_days": 0,
                                                      "event_triggers": []},
         "reporting": {"recipients": [], "frequency": "quarterly"}, "sources": SRC}),
    "rar": (
        {"risks": [{"id": "RSK-001", "title": "t", "description": "d", "likelihood": "moderate",
                    "impact": "high", "level": "moderate", "finding_refs": ["FND-001"],
                    "poam_refs": ["POAM-001"], "response": "mitigate", "sources": SRC}],
         "overall_risk": "moderate", "sources": SRC},
        {"risks": [{"id": "RSK-001", "title": "t", "description": "d", "likelihood": "medium",
                    "impact": "high", "level": "moderate", "finding_refs": [],
                    "poam_refs": [], "response": "ignore", "sources": SRC}],
         "overall_risk": "moderate", "sources": SRC}),
    "authorization-report": (
        {"decision_ref": "AUTH-001",
         "receipt": {"received_by": "PER-PM", "received": "2026-01-02",
                     "terms_acknowledged": True},
         "retention": {"retained_by": "PER-PM", "policy": "p", "retain_until": "2030-01-01"},
         "available_to": ["PER-PM"], "marking": "CUI",
         "terms_verification": {"verified_by": "PER-AO", "frequency_days": 90},
         "assessment_records": ["artifacts/data/sap.yaml"], "sources": SRC},
        {"decision_ref": "AUTH-001",
         "receipt": {"received_by": "PER-PM", "received": "2026-01-02",
                     "terms_acknowledged": False},
         "retention": {"retained_by": "PER-PM", "policy": "p", "retain_until": "2030-01-01"},
         "available_to": ["PER-PM"], "marking": "unmarked",
         "terms_verification": {"verified_by": "PER-AO", "frequency_days": 90},
         "assessment_records": ["artifacts/data/sap.yaml"], "sources": SRC}),
    "changes": (
        {"monitoring": {"unauthorized_changes": {
            "from": "2026-01-01", "to": "2026-02-01", "method": "drift scan",
            "reconciled_against": ["baseline"]}},
         "changes": [{"id": "CHG-001", "origin": "requested", "date": "2026-01-02",
                      "summary": "s", "requested_by": "PER-ISSO", "control": "exempt",
                      "security_impact": {"result": "none", "analysis": "a"}, "sources": SRC}],
         "sources": SRC},
        {"monitoring": {"unauthorized_changes": {
            "from": "2026-01-01", "to": "2026-02-01", "method": "drift scan",
            "reconciled_against": []}},
         "changes": [{"id": "CHG-001", "origin": "walk-in", "date": "2026-01-02",
                      "summary": "s", "requested_by": "PER-ISSO", "control": "exempt",
                      "security_impact": {"result": "none", "analysis": "a"}, "sources": SRC}],
         "sources": SRC}),
    "posture-reports": (
        {"reports": [{"id": "SPR-001", "period": {"from": "2026-01-01", "to": "2026-02-01"},
                      "issued": "2026-02-02", "marking": "CUI",
                      "deliveries": [{"recipient": "DISA", "date": "2026-02-02",
                                      "content": ["poam"]}],
                      "scorecard": {"reported": "2026-02-01"}, "sources": SRC}],
         "organization_tier": {"reviews": [], "open_poam_items": 0, "feeds": "P-7"},
         "sources": SRC},
        {"reports": [{"id": "SPR-001", "period": {"from": "2026-01-01", "to": "2026-02-01"},
                      "issued": "2026-02-02", "marking": "SECRET//NOFORN",
                      "deliveries": [{"recipient": "NSA", "date": "2026-02-02",
                                      "content": ["poam"]}],
                      "scorecard": {"reported": "2026-02-01"}, "sources": SRC}],
         "organization_tier": {"reviews": [], "open_poam_items": 0, "feeds": "P-1"},
         "sources": SRC}),
    "registration": (
        {"ppsm": {"registered": "2026-01-02", "registry_id": "PPSM-1",
                  "connections": ["CONN-01"]}, "sources": SRC},
        {"ppsm": {"registered": "2026-01-02", "registry_id": "PPSM-1",
                  "connections": ["link-1"]}, "sources": SRC}),
    "plan-reviews": (
        {"schedule": {"interval_days": 365, "set_by": "policy"}, "reviews": [], "changes": [],
         "sources": SRC},
        {"schedule": {"interval_days": 0, "set_by": "policy"}, "reviews": [], "changes": [],
         "sources": SRC}),
    "dias": (
        {"assurance": {"identity_proofing": "IAL2", "authentication": "AAL2",
                       "federation": "not-applicable"},
         "controls": ["ia-2"], "processes": "p", "compensating_controls": [], "sources": SRC},
        {"assurance": {"identity_proofing": "IAL9", "authentication": "AAL2",
                       "federation": "not-applicable"},
         "controls": ["ac-2"], "processes": "p", "compensating_controls": [], "sources": SRC}),
    "sar-report": (
        {"methodology": {"standard": "NIST SP 800-53A Rev. 5"},
         "delivered": [{"to": "PER-PM", "date": "2026-02-01"}], "sources": SRC},
        {"methodology": {"standard": ""}, "sources": SRC}),
    "ra": (_RA, {**_RA, "risk_model": {**_RA["risk_model"], "analysis_approach": "guess"}}),
    "requirements": (
        {"needs": [NEED], "requirements": [REQUIREMENT], "constraints": [],
         "design_policy": [{"statement": "DP-SCAP", "applies": True, "requirements": ["REQ-01"],
                            "sources": SRC}],
         "agreement": AGREEMENT, "derivation": DERIVATION, "engineering": ENGINEERING},
        {"needs": [NEED], "requirements": [{**REQUIREMENT, "verification": {
            "method": "guess", "description": "d"}}], "constraints": [], "design_policy": [],
         "agreement": AGREEMENT, "derivation": DERIVATION, "engineering": ENGINEERING}),
    "software": (
        {"covered_software": False, "sources": SRC},
        {"covered_software": True, "pipeline": {"automated": True}, "sources": SRC}),
}

_PIA = YAML(typ="safe").load((REPO_ROOT / "templates/data/pia.yaml").read_text(encoding="utf-8"))
RUN_EXAMPLES["pia"] = (_PIA, {**_PIA, "form": "DD-9999"})

_FIXTURE_RECORDS = REPO_ROOT / "tests/fixtures/runs/valid_minimal/artifacts/data"


def _record(name):
    return YAML(typ="safe").load((_FIXTURE_RECORDS / f"{name}.yaml").read_text(encoding="utf-8"))


RUN_EXAMPLES.update({
    name: (_record(name), {**_record(name), field: value})
    for name, field, value in (
        ("cm-plan", "configuration_items", [{"id": "CI-1"}]),
        ("contingency", "exercises", [{"id": "EX-1", "type": "drill"}]),
        ("incident-response", "reporting_paths", [{"case": "unknown"}]),
        ("service-agreements", "agreements", [{"id": "SVA-1", "role": "vendor"}]),
        ("ssp-records", "space_nss", "maybe"),
        ("system-description", "ownership", "leased"),
        ("sar-summary", "assessment_type", "spot-check"),
        ("org-context", "roles", [{"id": "RA-01", "role": "PER-AO", "citizenship": "dual"}]),
        ("protection", "program", {"acat": "IV", "mda": "DAE"}),
        ("protection-requirements", "read", {"ppp": "PPP-1"}),
        ("nss-assessments", "nss", "perhaps"),
        ("test-strategy", "approvals", []))
})
# cloud.yaml lives in the derived `cloud` base, not valid_minimal; its template is a valid record.
_CLOUD = YAML(typ="safe").load(
    (REPO_ROOT / "templates/data/cloud.yaml").read_text(encoding="utf-8"))
RUN_EXAMPLES["cloud"] = (_CLOUD, {**_CLOUD, "mission_impact_level": {"level": "IL3"}})
_ST = YAML(typ="safe").load(
    (REPO_ROOT / "templates/data/st-protection.yaml").read_text(encoding="utf-8"))
RUN_EXAMPLES["st-protection"] = (_ST, {**_ST, "critical_technology_elements": []})
_CATO = YAML(typ="safe").load((REPO_ROOT / "templates/data/cato.yaml").read_text(encoding="utf-8"))
RUN_EXAMPLES["cato"] = (_CATO, {**_CATO, "metrics": []})
RUN_EXAMPLES["disposal"] = (
    {"end_state": "Sanitized and removed", "environment": {"restored_to": "original"},
     "residual_check": {"date": "2030-01-01", "no_detrimental_factors": True},
     "storage": {"stored": False},
     "supply_chain": {"non_reuse_elements": ["drives"], "prevention": "Shredded on site."},
     "sources": SRC},
    {"end_state": "Sanitized", "environment": {"restored_to": "wherever"}, "sources": SRC})


def test_every_run_schema_has_examples():
    assert set(RUN_EXAMPLES) | {"artifact-frontmatter"} == PLAN_RUN_SCHEMAS | EXTRA_RUN_SCHEMAS


@pytest.mark.parametrize("name", sorted(RUN_EXAMPLES))
def test_run_schema_accepts_valid_and_rejects_broken_example(name):
    good, bad = RUN_EXAMPLES[name]
    assert errors(name, good) == []
    assert errors(name, bad)


def test_interview_answer_definition():
    answer = {"$defs": schema("interview")["$defs"], "$ref": "#/$defs/answer"}
    validator = jsonschema.Draft202012Validator(answer)
    ok = {"id": "INT-007.A3", "question_id": "INT-007.Q3", "asked_of": "PER-ISSO", "task": "S-4",
          "respondent": "simulated", "tag": "SIMULATED", "basis": ["product/arch.md#identity"]}
    assert list(validator.iter_errors(ok)) == []
    assert list(validator.iter_errors({**ok, "tag": "ASSUMPTION"}))


def test_fact_paths_come_from_the_facts_schema():
    assert fact_paths(REPO_ROOT) == {
        "system_id", "system_name", "acronym", "aliases", "boundary_id", "lifecycle_state",
        "categorization", "categorization.approved", "baseline_id", "acquisition",
        "classification", "system_type", "owning_organization", "system_version",
        "operational_environment", "lifecycle_phase"}


def test_real_framework_writes_each_fact_once():
    writers = {}
    for task in load(REAL, REPO_ROOT).framework.of("tasks"):
        for fact in task.data["writes_facts"]:
            writers.setdefault(fact, []).append(task.id)
    assert {f: w for f, w in writers.items() if len(w) > 1} == {}
    assert set(writers) == fact_paths(REPO_ROOT)


def test_unreadable_files_are_schema_findings(tmp_path):
    fw = tmp_path / "fw"
    shutil.copytree(MINI, fw)
    (fw / "pathways.yaml").unlink()
    (fw / "reviews.yaml").write_text("reviews: [\n")
    (fw / "milestones.yaml").write_text("- just a list\n")
    (fw / "decisions.yaml").write_text("decisions: {}\n")
    shutil.rmtree(fw / "tasks")

    result = validate(fw, REPO_ROOT, P3A)

    messages = {(f.path.rsplit("/", 1)[-1], f.message.split(":")[0]) for f in result.findings}
    assert {f.rule for f in result.findings} == {"FW-SCHEMA-001"}
    assert ("pathways.yaml", "file not found") in messages
    assert ("reviews.yaml", "not valid YAML") in messages
    assert ("milestones.yaml", "expected a mapping with key 'milestones'") in messages
    assert ("decisions.yaml", "'decisions' must be a list") in messages
    assert ("tasks", "no task files") in messages


def test_schema_error_names_entity_and_field(tmp_path):
    fw = tmp_path / "fw"
    shutil.copytree(MINI, fw)
    meta = fw / "meta.yaml"
    meta.write_text(meta.read_text().replace("mode: subset", "mode: some"))
    c = fw / "tasks" / "C.yaml"
    c.write_text(c.read_text().replace("min_interviews: 1", "min_interviews: -1", 1))

    findings = validate(fw, REPO_ROOT, P3A).findings

    rendered = sorted(f.render() for f in findings)
    assert any("tasks/C.yaml:2: C-1: min_interviews: -1 is less than the minimum" in r
               for r in rendered), rendered
    assert any("meta.yaml:1: meta/task_set/mode: 'some' is not one of" in r for r in rendered)


def _sources_properties(node, pointer=""):
    if isinstance(node, dict):
        for key, child in (node.get("properties") or {}).items():
            if key == "sources":
                yield f"{pointer}/properties/sources", child
        for key, child in node.items():
            yield from _sources_properties(child, f"{pointer}/{key}")
    elif isinstance(node, list):
        for n, child in enumerate(node):
            yield from _sources_properties(child, f"{pointer}/{n}")


# baseline.json is written by `rmf baseline resolve`; its sources are the files it read.
TRACED = sorted(p for p in SCHEMAS.glob("*.schema.json") if p.name != "baseline.schema.json")


@pytest.mark.parametrize("path", TRACED, ids=lambda p: p.name)
def test_sources_properties_hold_trace_tokens(path):
    """L-0073: TRACE-002 reads every `sources` key of run data as trace tokens, so a list of
    origin kinds named `sources` fails every run that fills it."""
    root = json.loads(path.read_text(encoding="utf-8"))

    def resolve(node):
        while isinstance(node, dict) and "$ref" in node:
            node = root["$defs"][node["$ref"].rpartition("/")[2]]
        return node

    for pointer, node in _sources_properties(root):
        token = resolve(resolve(node).get("items"))
        assert str((token or {}).get("pattern", "")).startswith("^(INT-"), pointer
