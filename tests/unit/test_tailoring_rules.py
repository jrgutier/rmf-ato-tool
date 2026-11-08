"""TLR-001 to TLR-010 on the cases their sources permit, and the resolver and catalog behaviour
they rely on. The negative fixtures (tests/fixtures/negative/TLR-*.yaml) prove each clause
fails; these prove the rules stay quiet where SP 800-53B and CNSSI 1253 allow the case."""

import copy

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

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
    """A compensating control may stand for a listed control when the AO or AODR accepted its
    risk, as TLR-001 records it (a lead default, for the user's ruling)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**COMPENSATING, "compensating_for": "ia-2"})
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


def _floors(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule.startswith(("DPOL-", "CFLR-"))]


REMOVE_SI3 = {**REMOVE_PL4, "control_id": "si-3", "rationale": "Said to need no malware scan."}


def test_a_stand_alone_system_may_tailor_a_floor_control_with_the_aos_approval(tmp_path):
    """The stand-alone permission of DoDI 8500.01 pages 38 and 39 holds for every floor: si-3
    carries FIPS 200 SI and DoDI 8530.01 malware duties, and a removal the AO approved passes
    on a stand-alone system with no DODIN connection, while one nobody approved fails."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml", lambda d: d["system_type"].update(
        connectivity="stand-alone", dodin_connection="none"))
    _add_action(run_dir, REMOVE_SI3)
    assert any("si-3 is tailored out of a stand-alone system's baseline without the approval"
               in m for m in _floors(run_dir))
    edit_yaml(run_dir / TAILORING, lambda d: d["actions"][-1].update(approved_by="PER-AO"))
    assert _floors(run_dir) == []


def test_a_compensating_control_the_aodr_accepted_passes_a_floor(tmp_path):
    """A compensating control may stand for a floor control when the AO or AODR accepted its
    risk; FIPS 200 allows the SP 800-53 tailoring guidance (p. 10)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    risk = {**COMPENSATING["risk"], "accepted_by": "PER-AODR"}
    _add_action(run_dir, {**COMPENSATING, "compensating_for": "sc-8", "risk": risk})
    assert _floors(run_dir) == []


def test_an_inherited_floor_control_passes(tmp_path):
    """Inheriting a control is no removal: ac-2 carries FIPS 200 AC and DoDI 8500.01 duties."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml", lambda d: d["controls"][0].update(
        status="inherited", inherited_from="Enterprise identity service"))
    assert _floors(run_dir) == []


def test_a_pit_interconnection_floor_binds_only_a_pit_system(tmp_path):
    """DoDI 8500.01 p. 39 item 4 binds interconnections of PIT systems: sc-7 removed from a
    major application is no PC-DOD-42 finding (the FIPS 200 and DoDI 5000.83 floors judge it)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _add_action(run_dir, {**REMOVE_PL4, "control_id": "sc-7"})
    found = _floors(run_dir)
    assert found and not any(m.startswith("PC-DOD-42:") for m in found)


def test_a_cato_floor_binds_only_while_a_cato_is_sought(tmp_path):
    """The cATO evaluation criteria judge a cATO package: with no cATO record and no AD-CATO
    record, ac-5 removed is no CF-CATO-5 finding; an AD-CATO record makes it one."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / "artifacts/data/cato.yaml").unlink()
    _add_action(run_dir, {**REMOVE_PL4, "control_id": "ac-5"})
    assert not any(m.startswith("CF-CATO-5:") for m in _floors(run_dir))
    edit_yaml(run_dir / "artifacts/data/authorizations.yaml",
              lambda d: d["records"][-1].update(decision="AD-CATO"))
    assert any(m.startswith("CF-CATO-5:") for m in _floors(run_dir))


def test_an_entry_resting_on_a_proxy_floor_record_is_not_covered():
    """A proxy record (the source names no control and several could meet the duty), in
    control_floors or dod_policy_controls, cannot carry covered: a covered entry may cite no
    fixture whose declared message is a proxy record's."""
    load = YAML(typ="safe").load
    inputs = baseline.load_inputs(REPO_ROOT)
    records = [*inputs["control_floors"], *inputs["dod_policy_controls"]]
    proxies = {r["id"] for r in records if r.get("mapping") == "proxy"}
    assert {"PC-DOD-38", "PC-DOD-44"} <= proxies
    assert proxies
    leaning = []
    for path in sorted((REPO_ROOT / "conformance/requirements").glob("*.yaml")):
        for entry in load(path.read_text(encoding="utf-8"))["requirements"]:
            if entry.get("status") != "covered":
                continue
            for item in entry.get("evidence") or ():
                fixture = REPO_ROOT / str(item.get("fixture") or "")
                if fixture.suffix != ".yaml" or not fixture.is_file():
                    continue
                messages = load(fixture.read_text(encoding="utf-8"))["expect"].get("messages")
                if any(m.partition(":")[0] in proxies for m in messages or ()):
                    leaning.append(entry["id"])
    assert leaning == []
