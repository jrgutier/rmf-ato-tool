"""SRA-001 to SRA-004 beyond their negative fixtures: the template a run copies, malformed
input, and the cases the sources permit."""

import json
from pathlib import Path

import jsonschema
from conftest import REPO_ROOT, edit_yaml
from ruamel.yaml import YAML

from rmf_tool.check import engine
from rmf_tool.check.context import Context
from rmf_tool.check.rules import risk_assessment
from rmf_tool.run.model import open_run

RA = "artifacts/data/ra.yaml"
SPACE = "CNSSI1253F-ATT2-SPACE"


def _schema():
    return json.loads((REPO_ROOT / "framework/schema/ra.schema.json").read_text())


def _messages(run_dir: Path, rule) -> list[str]:
    return [f.finding.message for f in rule(Context(open_run(run_dir, REPO_ROOT)))]


def _non_nss(run_dir: Path, **fields) -> None:
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["categorization"].__setitem__("overlays", [SPACE]))
    connection = {"component": "CMP-IDP", "information_exchange": "Sign-in assertions.",
                  "nss": False, "introduces": ["PC-01"], "risk": "low",
                  "end_to_end_impact": "A forged assertion reaches the relay.",
                  "sources": ["INT-003.A1"]}
    analysis = {"considered_by": ["PER-SPONSOR", "PER-AODR"], "coordinated_with": ["nsa"],
                "sources": ["INT-003.A1"], **fields}

    def edit(d):
        d["external"]["connections"][0] = connection
        d["external"]["end_to_end_analysis"] = analysis
    edit_yaml(run_dir / RA, edit)


def test_the_data_template_is_valid_yaml_of_the_schema():
    data = YAML(typ="safe").load((REPO_ROOT / "templates/data/ra.yaml").read_text())
    jsonschema.Draft202012Validator(_schema()).validate(data)


def test_the_example_shape_needs_every_section():
    """Each top-level section is required, so a run cannot leave one out silently. The sections
    added after the contract opened stay optional; SWA-002 (since 0.2.0) asks for components,
    PRIV-007 asks `privacy` of a system processing PII, and RARC-001 (since 0.2.0) asks
    `date`, `team`, `tailoring` and `rationales`."""
    schema = _schema()
    optional = {"ai_capabilities", "components", "privacy", "date", "team", "tailoring",
                "rationales"}
    assert set(schema["required"]) | optional == set(schema["properties"])


def test_malformed_lists_are_reported_not_raised(minimal_run):
    def mangle(d):
        d["threat_sources"][0]["id"] = ["TS-01"]
        d["threat_events"][0]["threat_sources"] = [{"id": "TS-01"}]
        d["external"]["connections"][0]["component"] = {"id": "CMP-IDP"}
        d["external"]["end_to_end_analysis"] = {"coordinated_with": 3, "considered_by": [{}]}
        d["prioritization"]["order"] = "TE-01"
    edit_yaml(minimal_run / RA, mangle)
    edit_yaml(minimal_run / "facts.yaml",
              lambda d: d["categorization"].__setitem__("overlays", [SPACE]))
    found = engine.evaluate(open_run(minimal_run, REPO_ROOT)).findings
    assert any(f.rule == "RUN-FM-001" and f.finding.path == RA for f in found)


def test_the_aodr_and_the_sponsor_may_consider_a_non_nss_connection(minimal_run):
    """CNSSP 12: the mission owner (PM or sponsor) and the AO, for whom the AODR may act."""
    _non_nss(minimal_run)
    assert _messages(minimal_run, risk_assessment.external_risk) == []


def test_non_nss_connections_need_nsa_coordination_only_under_the_space_overlay(minimal_run):
    _non_nss(minimal_run, coordinated_with=[], considered_by=[])
    assert len(_messages(minimal_run, risk_assessment.external_risk)) == 2
    edit_yaml(minimal_run / "facts.yaml",
              lambda d: d["categorization"].__setitem__("overlays", []))
    assert _messages(minimal_run, risk_assessment.external_risk) == []


def test_a_response_other_than_none_answers_insufficient_trust(minimal_run):
    """SP 800-37 Appendix G: compensating controls, greater risk, another provider or not
    obtaining the service each answer insufficient trust."""
    for response in ("accept-greater-risk", "more-trustworthy-provider", "not-obtained"):
        edit_yaml(minimal_run / RA, lambda d, r=response: d["external"]["providers"][0].update(
            trust="insufficient", response=r))
        assert _messages(minimal_run, risk_assessment.external_risk) == [], response


def test_equal_risks_may_be_ordered_either_way(minimal_run):
    """Refining risks of the same level is the organization's method, not a rule's."""
    edit_yaml(minimal_run / RA, lambda d: d["threat_events"][1].__setitem__("risk", "moderate"))
    edit_yaml(minimal_run / RA,
              lambda d: d["prioritization"].__setitem__("order", ["TE-02", "TE-01"]))
    assert _messages(minimal_run, risk_assessment.prioritization) == []


def test_a_run_without_the_file_in_its_contract_is_not_asked_for_it(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("framework_version", "0.1.0"))
    (minimal_run / RA).unlink()
    run = open_run(minimal_run, REPO_ROOT)
    assert not any(d["path"] == RA for d in run.artifacts["ART-RA"]["data"])
    assert _messages(minimal_run, risk_assessment.threat_model) == []


def test_migrate_leaves_the_risk_assessment_data_for_the_run_to_write(minimal_run):
    """`rmf run migrate` invents nothing: on the new contract SRA-001 asks for ra.yaml."""
    from rmf_tool.run import migrate

    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("framework_version", "0.1.0"))
    (minimal_run / RA).unlink()
    migrate.migrate(open_run(minimal_run, REPO_ROOT))
    assert not (minimal_run / RA).exists()
    assert any("has no artifacts/data/ra.yaml" in m
               for m in _messages(minimal_run, risk_assessment.threat_model))


def test_an_event_dropped_from_consideration_may_stay_out_of_the_order(minimal_run):
    """SP 800-30 pp. 40 and 42: an event that is not relevant, or that no vulnerability or
    predisposing condition bears on, drops from further consideration."""
    edit_yaml(minimal_run / RA, lambda d: d["prioritization"].__setitem__("order", ["TE-01"]))
    edit_yaml(minimal_run / RA, lambda d: d["prioritization"].__setitem__("couplings", []))
    edit_yaml(minimal_run / RA,
              lambda d: d["threat_events"][1].__setitem__("relevance", "not-applicable"))
    assert _messages(minimal_run, risk_assessment.prioritization) == []
    edit_yaml(minimal_run / RA, lambda d: d["threat_events"][1].update(
        relevance="possible", vulnerabilities=[], conditions=[]))
    assert _messages(minimal_run, risk_assessment.prioritization) == []


def test_an_environment_is_no_external_service(minimal_run):
    """A third-party environment is a provider record, not an external security service."""
    edit_yaml(minimal_run / RA, lambda d: d["external"].__setitem__("services_provided", False))
    edit_yaml(minimal_run / RA,
              lambda d: d["external"]["providers"][0].__setitem__("kind", "environment"))
    assert not [m for m in _messages(minimal_run, risk_assessment.external_risk)
                if "services_provided" in m]


def test_an_irrelevant_event_may_rest_on_an_out_of_scope_source(minimal_run):
    edit_yaml(minimal_run / RA, lambda d: d["threat_sources"][0].__setitem__("in_scope", False))
    edit_yaml(minimal_run / RA,
              lambda d: d["threat_events"][0].__setitem__("relevance", "not-applicable"))
    assert _messages(minimal_run, risk_assessment.threat_model) == []
