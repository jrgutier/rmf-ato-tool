"""RCP-001 to RCP-009: the cases the sources permit pass, a reauthorization on the ledger needs its
notice, and malformed run data is reported as findings (or left to RUN-FM-001), never raised on."""

from __future__ import annotations

import pytest
from conftest import HYBRID_MINIMAL, REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

OURS = tuple(f"RCP-00{n}" for n in range(1, 10))
FILE = "artifacts/data/reciprocity.yaml"


def _found(run_dir, rule):
    return [f.finding.message for f in RULES[rule](Context(open_run(run_dir, REPO_ROOT)))]


def test_fixtures_hold_no_reciprocity_finding():
    for base in (VALID_MINIMAL, HYBRID_MINIMAL):
        for rule in OURS:
            assert _found(base, rule) == [], (base.name, rule)


def test_permitted_cases_pass(tmp_path):
    """The AODR may review the Granting package; a refused system needs no agreement, impact
    determination, guide review or own package; a pending one is not yet held to an ATU; an
    SLA needs no termination factors; a status update earlier than 60 working days counts."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        d["received_systems"][0]["review"]["by"] = "PER-AODR"
        d["received_systems"][1].pop("agreement", None)
        d["agreements"][1]["termination_factors"] = []
        d["receiving_organizations"][0]["status_updates"][0]["date"] = "2026-06-01"

    edit_yaml(run_dir / FILE, edit)
    for rule in OURS:
        assert _found(run_dir, rule) == [], rule


def test_pending_system_is_not_held_to_an_authorization_to_use(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        d["received_systems"][0]["outcome"] = "pending"
        del d["received_systems"][0]["atu"]

    edit_yaml(run_dir / FILE, edit)
    assert _found(run_dir, "RCP-005") == []
    assert _found(run_dir, "RCP-009") == []


def test_a_reauthorization_on_the_ledger_needs_its_notice(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/authorizations.yaml",
              lambda d: d["records"][1].update(basis="reauthorization"))
    assert any("the reauthorization AUTH-002 is not notified" in m
               for m in _found(run_dir, "RCP-002"))


def test_no_relationship_means_no_finding_but_the_sharing(tmp_path):
    run_dir = copy_run(HYBRID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FILE, lambda d: d.update(package_sharing={"shared_with": []}))
    assert _found(run_dir, "RCP-001") == [
        "the security authorization package is not shared with the affected information owners "
        "or stewards"]


@pytest.mark.parametrize("junk", [[{"x": 1}], [["a"], 3], [{"id": ["x"], "agreement": ["y"],
                                                              "sites": [{"site": ["z"]}]}]])
def test_malformed_records_are_never_raised_on(tmp_path, junk):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def edit(d):
        d["receiving_organizations"] = junk
        d["received_systems"] = junk + [{"outcome": "accepted", "review": {"by": ["PER-AO"]},
                                         "atu": {"by": {"x": 1}}, "awareness": [{"via": []}],
                                         "impact": {"augmenting_controls": [{"control": []}]},
                                         "controls": [{"control": [], "origin": "inherited"}]}]
        d["agreements"] = junk + [{"id": "AGR-09", "instrument": ["mou"], "pocs": {"granting": []}}]
        d["granting"] = {"patches": [{"directed_action": []}], "cssp": []}

    edit_yaml(run_dir / FILE, edit)
    for rule in OURS:
        _found(run_dir, rule)


def _edit(run_dir, edit):
    edit_yaml(run_dir / FILE, edit)


def test_fix_round_permitted_cases(tmp_path):
    """Each case the sources allow passes every RCP rule: an organization that joins after
    release (CNSSI 1254 Annex D 3.b) and after a reauthorization's notice fell due; a POA&M
    resent after its newest item; an issue raised after deployment still open; an augmenting
    control implemented after the authorization to use but by deployment; receiving-side
    manual inheritance (DoD CIO reciprocity 4.2.1.b.(2).a); a request endorsed by a CISO
    equivalent; no difference tests where nothing differs; a pending system not yet judged."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/authorizations.yaml",
              lambda d: d["records"][1].update(basis="reauthorization"))

    def edit(d):
        org = d["receiving_organizations"][0]
        org["joined"] = "2026-11-01"
        org["requirements"] = {"gathered": "2026-11-02", "coordinated": ["2026-11-02"],
                               "additional_controls": ["ia-2"]}
        org["issues"].append({"id": "RI-02", "raised": "2027-02-01"})
        org["notices"] = [n for n in org["notices"] if n["kind"] != "reauthorization"]
        rs1, rs2 = d["received_systems"]
        rs1["impact"]["augmenting_controls"][0]["implemented"] = "2026-12-19"
        rs1["awareness"] = [{"date": "2026-11-25", "via": "manual-inheritance"}]
        rs1["installation"]["differences"] = []
        rs1["hosting_update"]["documents"] = ["installation-configuration"]
        rs2["body_of_evidence"]["requests"][0].update(
            endorsed_by="equivalent", equivalent={"title": "Agency CISO",
                                                  "authority": "Agency delegation 12"})
        d["received_systems"].append({"id": "RS-03", "system": "Pilot sensor",
                                      "granting_organization": "Lab", "granting_ao": "Lab AO",
                                      "outcome": "pending", "sources": ["INT-012.A1"]})

    _edit(run_dir, edit)
    for rule in OURS:
        assert _found(run_dir, rule) == [], (rule, _found(run_dir, rule))


def test_a_co_use_enterprise_system_needs_no_receiving_organization(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _edit(run_dir, lambda d: d.update(receiving_organizations=[], co_use={
        "notification_processes": "Incident and PII breach notices through the eMASS record."}))
    assert _found(run_dir, "RCP-001") == []


def test_an_enterprise_link_is_not_escaped_by_the_flag(tmp_path):
    """A received system linked to an Enterprise leveraged authorization is an Enterprise system
    whatever its own flag says: the mismatch is reported and the DSAWG and CISO clauses apply."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/leveraged-authorizations.yaml",
              lambda d: d["leveraged_authorizations"][0].update(enterprise={
                  "accepted_by": "DoD ISRMC", "accepted": "2026-03-01",
                  "receiving_action": "deploy",
                  "change_request": {"id": "CR-1", "approved_on": "isrmc-risk-acceptance"}}))

    def edit(d):
        rs1 = d["received_systems"][0]
        rs1.update(enterprise=False, leveraged="LA-01", coordination_point="PER-ISSM")
        rs1["impact"]["via"] = "local"

    _edit(run_dir, edit)
    found = _found(run_dir, "RCP-004")
    assert any("is not recorded as one" in m for m in found)
    assert any("through the DSAWG representative" in m for m in found)
    assert any("single cybersecurity coordination point" in m for m in _found(run_dir, "RCP-005"))
