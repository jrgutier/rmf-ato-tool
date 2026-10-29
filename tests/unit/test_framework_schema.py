"""AC-5/AC-6: the framework schema accepts the real and mini frameworks, the run-side data
contracts are valid Draft 2020-12 schemas that accept a minimal example and reject a
broken one, and unreadable framework files are FW-SCHEMA-001 findings."""

import json
import shutil

import jsonschema
import pytest
from _framework_fixtures import MINI, P3A, REAL
from conftest import REPO_ROOT

from rmf_tool.framework.load import load
from rmf_tool.framework.model import SCHEMA_DIR
from rmf_tool.framework.validate import fact_paths, schema_findings, validate

SCHEMAS = REPO_ROOT / SCHEMA_DIR
PLAN_RUN_SCHEMAS = {
    "artifact-frontmatter", "run-config", "scenario", "product-profile", "facts", "interview",
    "assumptions", "infotypes", "users", "boundary", "leveraged-authorizations", "inventory",
    "ssp-controls", "sap", "sar-results", "poam-items", "stig-summary", "baseline", "decision",
}
EXTRA_RUN_SCHEMAS = {"tailoring", "allocation", "conmon", "rar"}  # data named in plan §6.4


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
    assert names == {"framework"} | PLAN_RUN_SCHEMAS | EXTRA_RUN_SCHEMAS


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
RUN_EXAMPLES = {
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
}


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
        "categorization", "categorization.approved", "baseline_id"}


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
