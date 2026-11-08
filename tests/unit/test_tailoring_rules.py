"""TLR-001 to TLR-010 on the cases their sources permit, and the resolver and catalog behaviour
they rely on. The negative fixtures (tests/fixtures/negative/TLR-*.yaml) prove each clause
fails; these prove the rules stay quiet where SP 800-53B and CNSSI 1253 allow the case."""

import copy

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool import baseline, build, catalog
from rmf_tool.check import engine
from rmf_tool.run.model import open_run, schema_errors

TAILORING = "artifacts/data/tailoring.yaml"
ALLOCATION = "artifacts/data/allocation.yaml"
LAW = {"reviewed": ["legislation", "regulation", "policy", "omb-policy"],
       "requires_control": False, "sources": ["INT-028.A3"]}
COMPENSATING = {
    "control_id": "si-4", "action": "compensating", "compensating_for": "sc-15",
    "source": "catalog", "cannot_implement": "No collaborative devices to configure.",
    "equivalence": "Monitoring detects device activation.",
    "risk": {"assessment": "Low residual risk.", "accepted_by": "PER-AO",
             "sources": ["ART-RA"]},
    "law_policy": LAW, "rationale": "Monitoring stands in.", "sources": ["INT-028.A3"]}


def _tlr(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule.startswith("TLR-")]


def _add_action(run_dir, action):
    edit_yaml(run_dir / TAILORING, lambda d: d["actions"].append(copy.deepcopy(action)))


def test_other_source_compensating_control_needs_no_catalog_id():
    other = {**{k: v for k, v in COMPENSATING.items() if k != "control_id"}, "source": "other",
             "other_control": {"id": "ORG-MON-1", "title": "Watch", "origin": "Handbook"},
             "catalog_search": {"considered": ["si-4"], "finding": "no-suitable-control"}}
    assert schema_errors(REPO_ROOT, "tailoring", {"actions": [other]}) == []
    without = {k: v for k, v in other.items() if k != "other_control"}
    assert schema_errors(REPO_ROOT, "tailoring", {"actions": [without]})
    catalog_one = {k: v for k, v in COMPENSATING.items() if k != "control_id"}
    assert schema_errors(REPO_ROOT, "tailoring", {"actions": [catalog_one]})


def test_valid_other_source_compensating_control_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**{k: v for k, v in COMPENSATING.items() if k != "control_id"},
                          "source": "other",
                          "other_control": {"id": "ORG-MON-1", "title": "Watch",
                                            "origin": "Enclave handbook"},
                          "catalog_search": {"considered": ["si-4"],
                                             "finding": "no-suitable-control"}})
    assert _tlr(run_dir) == []


@pytest.mark.parametrize("contract, expected", [("0.2.0", "compensating"), ("0.1.0", None)])
def test_catalog_compensating_control_reaches_the_baseline_from_its_contract(
        tmp_path, contract, expected):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "run.yaml", lambda d: (d.update(framework_version=contract),
                                               d["control_subset"].append("si-14")))
    _add_action(run_dir, {**COMPENSATING, "control_id": "si-14"})  # outside M-M-L
    origins = {c["control_id"]: c["origin"]
               for c in baseline.resolve(open_run(run_dir, REPO_ROOT))["controls"]}
    assert origins.get("si-14") == expected


def test_removal_whose_requirement_circumstances_do_not_apply_passes(tmp_path):
    """SP 800-53B 2.4: a requirement that applies only in specified circumstances justifies
    tailoring when they do not apply; requires_control false records that test."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {"control_id": "pt-2", "action": "remove",
                          "basis": "circumstance-not-applicable",
                          "law_policy": {**LAW, "authorities": ["Privacy Act of 1974"]},
                          "rationale": "No system of records.", "sources": ["INT-028.A3"]})
    assert _tlr(run_dir) == []


def test_provider_not_commensurate_may_supply_hybrid_controls(tmp_path):
    """A provider whose offer falls short leaves the system to supplement: hybrid passes,
    only a control inherited whole fails (TLR-010)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        d["providers"][0]["determination"]["commensurate"] = False
        d["allocations"][4]["type"] = "hybrid"
        d["allocations"][4]["components"] = ["CMP-RELAY"]
    edit_yaml(run_dir / ALLOCATION, edit)
    assert _tlr(run_dir) == []


def test_a_control_may_support_several_capabilities(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/capabilities.yaml", lambda d: d["capabilities"].append(
        {"id": "CAP-02", "name": "Account accountability", "controls": ["ac-2", "au-2"],
         "sources": ["product/security.md#accounts"]}))
    assert _tlr(run_dir) == []


def test_a_failed_assumption_answered_by_tailoring_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        record = next(a for a in d["assumptions"] if a["id"] == "AS-BL-2")
        record.update(holds=False, controls=["ac-2"])
    edit_yaml(run_dir / TAILORING, edit)
    assert _tlr(run_dir) == []


def test_catalog_marks_assurance_controls():
    cat = catalog.load(REPO_ROOT)
    assert catalog.contributes_to_assurance(cat, "sa-11")
    assert not catalog.contributes_to_assurance(cat, "ac-2")
    assert catalog.view(cat, "sa-11", ("title", "assurance"))["assurance"] is True


def test_inputs_cover_both_assumption_lists():
    data = baseline.load_inputs(REPO_ROOT)
    ids = {a["id"] for a in data["assumptions"] if "overlay" not in a}
    assert {f"AS-BL-{n}" for n in range(1, 6)} <= ids  # SP 800-53B 2.3, adopted by CNSSI 1253
    assert {"AS-NSS-1", "AS-NSS-2", "AS-NSS-3", "AS-ADD-1", "AS-ADD-2", "AS-ADD-3"} <= ids


def test_designated_representative_may_accept_compensating_risk(tmp_path):
    """Only the authorization decision is non-delegable (DoDI 8510.01 p. 28); CNSSI 1253
    p. 15 names the AO or designee, so PER-AODR may accept the risk (TLR-001)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**COMPENSATING, "risk": {**COMPENSATING["risk"],
                                                   "accepted_by": "PER-AODR"}})
    assert _tlr(run_dir) == []


def test_inheritance_determined_by_owner_and_designated_representative_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / ALLOCATION,
              lambda d: d["providers"][0]["determination"].update(by=["PER-PM", "PER-AODR"]))
    assert _tlr(run_dir) == []


def test_inheritance_without_the_system_owner_fails(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / ALLOCATION,
              lambda d: d["providers"][0]["determination"].update(by=["PER-AO"]))
    assert any("not made by the system owner" in m for m in _tlr(run_dir))


@pytest.mark.parametrize("answer", [{"controls": ["sc-7"]}, {"outcome": "revisited-no-change"}])
def test_applying_assumption_answered_by_protection_already_selected_passes(tmp_path, answer):
    """A cross-domain link the baseline's boundary protection already addresses needs no add
    action: SP 800-53B 2.3 says additional controls are likely needed, not always."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        next(a for a in d["assumptions"] if a["id"] == "AS-ADD-3").update(holds=True, **answer)
    edit_yaml(run_dir / TAILORING, edit)
    assert _tlr(run_dir) == []


def test_circumstance_not_applicable_is_not_refused_as_required(tmp_path):
    """The requirement exists but does not apply to this system: requires_control is not read,
    the authority is (TLR-002)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {"control_id": "pt-2", "action": "remove",
                          "basis": "circumstance-not-applicable",
                          "law_policy": {**LAW, "requires_control": True,
                                         "authorities": ["Privacy Act of 1974"]},
                          "rationale": "No system of records.", "sources": ["INT-028.A3"]})
    assert _tlr(run_dir) == []


def test_capability_gap_is_a_warning_not_an_error(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/capabilities.yaml",
              lambda d: d["capabilities"][0]["controls"].append("ac-17"))
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    found = engine.select(run, engine.evaluate(run), final=True)
    assert {(f.rule, f.severity) for f in found if f.rule.startswith("TLR-")} == {("TLR-011", "W")}


def _dpol(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule.startswith("DPOL-")]


REMOVE_PL4 = {"control_id": "pl-4", "action": "remove", "basis": "scoping",
              "scoping": {"consideration": "technology"}, "law_policy": LAW,
              "rationale": "Said to need no rules of behavior.", "sources": ["INT-028.A3"]}


def test_a_stand_alone_system_may_tailor_a_dod_policy_control_with_the_aos_approval(tmp_path):
    """DoDI 8500.01 pages 38 and 39: a stand-alone system's control set may be tailored as
    appropriate with the approval of the AO, so a removal the AO or AODR approved passes."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**REMOVE_PL4, "approved_by": "PER-AODR"})
    assert any("pl-4 is tailored out of the baseline" in m for m in _dpol(run_dir))
    edit_yaml(run_dir / "facts.yaml", lambda d: d["system_type"].update(
        connectivity="stand-alone", dodin_connection="none"))
    assert _dpol(run_dir) == []


def test_a_compensating_control_the_ao_approved_passes(tmp_path):
    """A compensating control may stand for a listed control with the AO's or AODR's
    approval (a lead default, for the user's ruling)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**COMPENSATING, "compensating_for": "ia-2", "approved_by": "PER-AO"})
    assert _dpol(run_dir) == []


def test_a_parameter_or_specification_on_a_dod_policy_control_passes(tmp_path):
    """Only a remove action tailors a control out; the minimal run sets an ac-2 parameter and
    specification, which DPOL-002 reads as kept."""
    assert _dpol(copy_run(VALID_MINIMAL, tmp_path / "run")) == []


def test_a_networked_pit_system_is_judged(tmp_path):
    """DoDI 8500.01 page 39 item 5 permits tailoring only for a stand-alone PIT system, with the
    AO's approval; a networked PIT system is judged like an IS."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, REMOVE_PL4)
    edit_yaml(run_dir / "facts.yaml", lambda d: d["system_type"].update(value="pit-system"))
    assert any("pl-4 is tailored out of the baseline" in m for m in _dpol(run_dir))
