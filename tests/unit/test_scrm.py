"""The cases SP 800-161 Rev. 1 and SP 800-18 Rev. 2 permit pass the C-SCRM rules (Fable's I-14
review): each test mutates valid_minimal into a permitted case and asserts the rule is silent,
and the paired negative fixture under tests/fixtures/negative/ shows the refused case fails."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

D = "artifacts/data/"


def messages(run_dir, rule):
    return [f.finding.message for f in RULES[rule](Context(open_run(run_dir, REPO_ROOT)))]


@pytest.fixture
def run(tmp_path):
    return copy_run(VALID_MINIMAL, tmp_path / "run")


def test_lead_may_be_a_group_or_any_executive(run):
    edit_yaml(run / D / "scrm-org.yaml", lambda d: d["governance"].__setitem__(
        "lead", {"office": "Risk board", "group": "Component risk board"}))
    assert not [m for m in messages(run, "SCRM-021") if "lead" in m]
    edit_yaml(run / D / "scrm-org.yaml", lambda d: d["governance"].__setitem__(
        "lead", {"persona": "PER-AO", "office": "AO office"}))
    assert not [m for m in messages(run, "SCRM-021") if "lead" in m]


def test_duty_is_owed_only_by_roles_the_run_has(run):
    edit_yaml(run / D / "scrm-org.yaml", lambda d: d["governance"].__setitem__(
        "roles", [r for r in d["governance"]["roles"] if r["persona"] != "PER-DEV"]))
    assert "no C-SCRM duty is defined for PER-DEV" in messages(run, "SCRM-021")
    for path in (run / "interviews").glob("*-PER-DEV.md"):
        path.unlink()
    assert "no C-SCRM duty is defined for PER-DEV" not in messages(run, "SCRM-021")


def test_strategy_at_one_level_suffices(run):
    edit_yaml(run / D / "scrm-org.yaml", lambda d: d["levels"][1].__setitem__(
        "deliverables", ["policy"]))
    assert messages(run, "SCRM-022") == []


def test_sharing_needs_a_process_not_every_practice_and_may_cite_the_dod_liaison(run):
    def edit(d):
        d["sharing"]["practices"] = d["sharing"]["practices"][:1]
        d["sharing"]["fasc"]["liaison"] = "The DoD senior official designated to the FASC"
    edit_yaml(run / D / "scrm-org.yaml", edit)
    assert messages(run, "SCRM-023") == []


def test_one_lower_tier_practice_not_started_does_not_block(run):
    edit_yaml(run / D / "scrm-org.yaml", lambda d: d["maturity"]["practices"].append(
        {"practice": "Supplier risk assessments", "tier": "foundational",
         "status": "not-started"}))
    assert messages(run, "SCRM-024") == []


def test_non_critical_source_factors_are_discretionary(run):
    def edit(d):
        other = {**d["assessments"][0], "id": "SA-02", "supplier": "SUP-01",
                 "covered_articles": [{"item": "INV-001", "name": "n", "identifier": "i",
                                       "description": "d"}],
                 "factors": [{"factor": "purpose", "status": "not-relevant", "finding": "f",
                              "agency_factor": "a", "sources": ["INT-023.A1"]}]}
        d["assessments"].append(other)
    edit_yaml(run / D / "scrm.yaml", edit)
    assert messages(run, "SCRM-003") == []


def test_screening_holds_the_lists_that_apply(run):
    edit_yaml(run / D / "scrm-acquisition.yaml", lambda d: [
        r.__setitem__("screening", r["screening"][:2]) for r in d["selection"]])
    assert messages(run, "SCRM-008") == []


def test_low_impact_system_may_state_inheritance_instead_of_a_plan(run):
    edit_yaml(run / "facts.yaml", lambda d: d["categorization"].update(
        {"c": "low", "i": "low", "a": "low"}))
    edit_yaml(run / D / "scrm-plan.yaml", lambda d: d.pop("plan"))
    assert any("states no inheritance" in m for m in messages(run, "SCRM-009"))
    edit_yaml(run / D / "scrm-plan.yaml", lambda d: d.__setitem__("inheritance", {
        "controls": "c", "tolerances": "t", "acceptance": "a", "sources": ["INT-007.A1"]}))
    assert messages(run, "SCRM-009") == []


def test_supplier_continuity_waits_for_a_sustaining_practice(run):
    def org(d):
        for p in d["maturity"]["practices"]:
            if p["tier"] == "sustaining":
                p["status"] = "in-progress"
    edit_yaml(run / D / "scrm-org.yaml", org)
    edit_yaml(run / D / "scrm-plan.yaml", lambda d: d["contingency"]["activities"][0]
              .__setitem__("suppliers", ["SUP-01"]))
    assert messages(run, "SCRM-011") == []


def test_a_delegated_decision_may_sit_below_the_reach(run):
    def edit(d):
        d["response"][0]["reach"] = "mission"
        d["response"][0]["decision"]["delegated_by"] = "PER-RE"
    edit_yaml(run / D / "scrm.yaml", edit)
    assert messages(run, "SCRM-013") == []


def test_a_system_without_a_level_1_report_owes_none_to_the_risk_executive(run):
    edit_yaml(run / D / "scrm-plan.yaml", lambda d: d.__setitem__(
        "reporting", [r for r in d["reporting"] if r["level"] != "level-1"]))
    assert messages(run, "SCRM-014") == []


def test_no_flow_down_without_subcontractors(run):
    def edit(d):
        d["subcontractors"] = False
        d["terms"] = [t for t in d["terms"] if t["term"] != "flow-down"]
    edit_yaml(run / D / "scrm-acquisition.yaml", edit)
    assert messages(run, "SCRM-015") == []


def test_an_external_driver_may_rank_a_non_critical_source_first(run):
    def edit(d):
        d["suppliers"][2]["priority"] = 3
        for s in d["suppliers"]:
            if s["criticality"] == "non-critical":
                s["priority_driver"] = "NDAA Section 889 review of every supplier"
    edit_yaml(run / D / "scrm.yaml", edit)
    assert messages(run, "SCRM-001") == []


def test_a_phase_may_repeat_for_spiral_or_agile_cycles(run):
    edit_yaml(run / D / "scrm-plan.yaml", lambda d: d["plan"]["lifecycle"].append(
        {"phase": "integration", "activities": "Each sprint reruns the supplier checks."}))
    assert messages(run, "SCRM-030") == []


def test_a_low_impact_system_that_inherits_needs_no_sdlc_map(run):
    def edit(d):
        d.pop("plan")
        d["inheritance"] = {"controls": "Inherited from the enclave", "tolerances": "Enclave's",
                            "acceptance": "Enclave AO", "sources": ["INT-007.A1"]}
    edit_yaml(run / D / "scrm-plan.yaml", edit)
    assert messages(run, "SCRM-030") == []
