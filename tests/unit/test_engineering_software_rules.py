"""SSE-001 to SSE-003 and SWA-001 and SWA-002 report malformed run data as findings (or leave it
to RUN-FM-001); they never raise on it."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

OURS = ("SSE-001", "SSE-002", "SSE-003", "SWA-001", "SWA-002")
JUNK = [{"x": 1}]  # a list of mappings where a string is expected


def _requirements(data):
    data["requirements"][0].update(included_in=JUNK, kind=JUNK)
    data["derivation"] = {"informed_by": [JUNK, 3], "methods": [{"addresses": 5,
                                                                 "requirements": [JUNK]}],
                          "key_performance": [{"establishes": JUNK, "based_on": 7}],
                          "exportability": "REQ-01"}
    data["engineering"] = {"practices": [{"area": JUNK, "stages": "design", "principles": [JUNK]},
                                         "x"],
                           "assurance": {"requirements": [JUNK]}}


def _software(data):
    data.update(pipeline=JUNK, ai_development={"used": True, "tools": [JUNK, {"name": JUNK}]},
                evidence={"sbom": "x"}, test_and_evaluation={"cyber_dte": "x"})


def _ra(data):
    data["components"] = [{"name": JUNK, "kind": "open-source", "open_source": "x"},
                          {"kind": "cots", "validation": JUNK}, 4]


def _ssp(data):
    data["controls"][0].update(control_id=JUNK, assurance="x")


@pytest.mark.parametrize("rule", OURS)
def test_malformed_data_is_reported_not_raised(rule, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    data = run_dir / "artifacts/data"
    edit_yaml(data / "requirements.yaml", _requirements)
    edit_yaml(data / "software.yaml", _software)
    edit_yaml(data / "ra.yaml", _ra)
    edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml", _ssp)
    findings = RULES[rule](Context(open_run(run_dir, REPO_ROOT)))
    assert all(f.rule == rule for f in findings)
    if rule != "SSE-003":
        assert findings, rule


@pytest.mark.parametrize("rule", OURS)
def test_the_base_run_holds(rule, tmp_path):
    run = open_run(copy_run(VALID_MINIMAL, tmp_path / "run"), REPO_ROOT)
    assert RULES[rule](Context(run)) == []


def _messages(run_dir, rule):
    return [f.finding.message for f in RULES[rule](Context(open_run(run_dir, REPO_ROOT)))]


def test_a_hardware_product_with_a_reason_holds_no_covered_software(tmp_path):
    """A hardware product may hold no firmware or software; said so with a reason, DoWI 8430.01
    does not bind it, and its DP-SW-* statements may then be marked not applicable."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["acquisition"].update(product_kind="hardware"))
    edit_yaml(run_dir / "artifacts/data/software.yaml", lambda d: d.update(
        covered_software=False, covered_software_reason="A passive patch panel: no firmware."))

    def not_applicable(data):
        for record in data["design_policy"]:
            if record["statement"].startswith("DP-SW-"):
                record.update(applies=False, reason="No covered software.", requirements=[])
        data["requirements"][5]["policy"] = []
        data["requirements"][5]["needs"] = ["NEED-01"]
    edit_yaml(run_dir / "artifacts/data/requirements.yaml", not_applicable)
    assert _messages(run_dir, "SWA-001") == []
    assert _messages(run_dir, "REQS-002") == []


def test_wholly_acquired_software_needs_no_pipeline_but_still_an_sbom(tmp_path):
    """3.5.c.(1) binds producing software; 3.5.b's SBOM binds all covered software."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def acquired(data):
        data["pipeline"] = {"produced": False, "reason": "A COTS relay bought as a service."}
        data["evidence"]["sbom"]["custom_generated"] = False
    edit_yaml(run_dir / "artifacts/data/software.yaml", acquired)
    assert _messages(run_dir, "SWA-001") == []
    edit_yaml(run_dir / "artifacts/data/software.yaml",
              lambda d: d["evidence"]["sbom"].update(third_party_included=False))
    assert _messages(run_dir, "SWA-001") == ["the SBOM leaves out third-party components"]


def test_a_trivial_open_source_component_needs_no_project_review(tmp_path):
    """3.5.i.(3) asks the further review of a non-trivial open-source component only."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def trivial(data):
        component = dict(data["components"][0], name="left-pad", trivial="Eleven lines.")
        del component["open_source"]
        data["components"].append(component)
    edit_yaml(run_dir / "artifacts/data/ra.yaml", trivial)
    assert _messages(run_dir, "SWA-002") == []


def test_a_derivation_may_yield_no_exportability_requirement_with_a_reason(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/requirements.yaml", lambda d: d["derivation"].update(
        exportability=[], exportability_none="Nothing is planned for foreign release."))
    assert _messages(run_dir, "SSE-001") == []
    edit_yaml(run_dir / "artifacts/data/requirements.yaml",
              lambda d: d["derivation"].pop("exportability_none"))
    assert _messages(run_dir, "SSE-001") == [
        "the derivation names no exportability requirement and does not say why none is derived"]


def test_a_software_product_needs_no_manufacture_practice(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def no_manufacture(data):
        for practice in data["engineering"]["practices"]:
            practice["stages"] = [s for s in practice["stages"] if s != "manufacture"]
    edit_yaml(run_dir / "artifacts/data/requirements.yaml", no_manufacture)
    assert _messages(run_dir, "SSE-002") == []


def test_an_inherited_assurance_control_needs_no_assurance_record(tmp_path):
    """The provider addresses an inherited control's assurance; the system authors none."""
    import yaml as pyyaml

    spec = pyyaml.safe_load((REPO_ROOT / "tests/fixtures/negative/SSE-003.yaml").read_text())
    from _mutations import apply

    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    for mutation in spec["mutations"]:
        if mutation["file"] == "artifacts/ssp/controls/sa.yaml":
            mutation = {**mutation, "content": mutation["content"].replace(
                "status: implemented", "status: inherited\n    inherited_from: Enterprise")}
        apply(run_dir, mutation)
    assert _messages(run_dir, "SSE-003") == []
