"""What the plan rules allow: each case below is one the source permits, so a rule that starts
refusing it fails here. The clauses that refuse have their negative fixtures."""

from __future__ import annotations

import pytest
from _mutations import apply
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

SSP = "artifacts/data/ssp-records.yaml"
CP = "artifacts/data/contingency.yaml"
IR = "artifacts/data/incident-response.yaml"
SVC = "artifacts/data/service-agreements.yaml"
LEDGER = "artifacts/data/authorizations.yaml"
NEGATIVE = REPO_ROOT / "tests/fixtures/negative"


def _rule_errors(run_dir, rule):
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule == rule]


def _contractor_waived(d):
    path = d["reporting_paths"][4]
    path.update(applies=False, not_applicable_rationale="No cleared contractor touches it.",
                recipients=["PER-AO"], reference="Not applicable")


def _standalone(d):
    d["dodin_connected"] = False
    d["agreements"][0]["role"] = "other"


def _functional_on_low(d):
    d["exercises"][0]["type"] = "functional"


def _gap_with_poam(d):
    d["bia"]["processes"][0]["rto_hours"] = 30
    d["strategy"]["rto_gaps"] = [{"process": "BP-01", "poam_item": "POAM-001"}]


def _unfunded_with_poam(d):
    d["funding"][2].update(status="unfunded", poam_item="POAM-001")


def _not_nsa_on_unclassified(d):
    d["cryptography"].update(nsa_approved=False, key_management_process="Enterprise PKI.")


def _space_exception(d):
    d["space_nss"] = True
    d["cryptography"]["space"]["command_protection"] = "cnssi-1200-exception"


def _gfe_only(d):
    d["telework"] = {"non_gfe_remote_access": False}


def _isso_owns_a_path(d):
    d["reporting_paths"][0]["owner"] = "PER-ISSO"


def _two_sustainment_lines(d):
    sustained = next(line for line in d["funding"] if line["purpose"] == "sustainment")
    d["funding"].append({**sustained, "phases": ["PH-PD"]})  # a later line, operations left out


def _scheme_by_reference(d):
    d["agreements"][0]["evaluation"]["scheme"] = "DoD O-8530.01-M"


def _encrypted_link_needs_no_nsa_approval(d):
    d["space_nss"] = True
    d["cryptography"]["space"]["emergency_links"][0].update(unencrypted=False, approved_by="PER-AO")


@pytest.mark.parametrize(("rule", "file", "edit"), [
    ("IRPT-001", IR, _contractor_waived),
    ("SVCA-001", SVC, _standalone),
    ("CPLAN-002", CP, _functional_on_low),
    ("CPLAN-001", CP, _gap_with_poam),
    ("FUND-001", SSP, _unfunded_with_poam),
    ("CRYP-001", SSP, _not_nsa_on_unclassified),
    ("CRYP-002", SSP, _space_exception),
    ("CRYP-002", SSP, _encrypted_link_needs_no_nsa_approval),
    ("TELE-001", SSP, _gfe_only),
    ("IRPT-001", IR, _isso_owns_a_path),
    ("FUND-001", SSP, _two_sustainment_lines),
    ("SVCA-001", SVC, _scheme_by_reference),
], ids=lambda v: v.__name__ if callable(v) else v)
def test_a_permitted_case_is_not_refused(rule, file, edit, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / file, edit)
    assert _rule_errors(run_dir, rule) == []


def test_an_old_contract_run_is_not_held_to_the_records(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / CP).unlink()
    assert any("is missing; S-4 writes it" in m for m in _rule_errors(run_dir, "CPLAN-001"))
    edit_yaml(run_dir / "run.yaml", lambda d: d.update(framework_version="0.1.0"))
    assert _rule_errors(run_dir, "CPLAN-001") == []


def _cato_run(tmp_path, fixture="SVCA-001.scope.yaml"):
    """valid_minimal under a cATO, the system on premises and in the cloud, one CSSP on premises."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    spec = YAML(typ="safe").load((NEGATIVE / fixture).read_text(encoding="utf-8"))
    for mutation in spec["mutations"]:
        apply(run_dir, mutation)
    assert _rule_errors(run_dir, "SVCA-001")
    return run_dir


def test_two_cssps_together_cover_the_cato_criteria(tmp_path):
    run_dir = _cato_run(tmp_path)

    def cloud_cssp(d):
        on_prem = d["agreements"][0]
        cloud = {**on_prem, "id": "SVA-003", "provider": "Cloud CSSP", "environments": ["cloud"],
                 "services": [{**on_prem["services"][1], "id": "SRV-04"}],
                 "effectiveness": [{**on_prem["effectiveness"][0], "service": "SRV-04"}]}
        d["agreements"].append(cloud)

    edit_yaml(run_dir / SVC, cloud_cssp)
    assert _rule_errors(run_dir, "SVCA-001") == []


def test_a_revoked_cato_lifts_the_cato_criteria(tmp_path):
    run_dir = _cato_run(tmp_path)
    with (run_dir / LEDGER).open("a", encoding="utf-8") as fh:
        fh.write("- id: AUTH-004\n  decision: AD-RCATO\n  subject: system\n  basis: revocation\n"
                 "  decided_by: PER-AO\n  task: M-6\n  date: '2026-12-20'\n"
                 "  underlying: AUTH-002\n  revocation_reason: Posture fell.\n"
                 "  rationale: Posture fell.\n  sources: [INT-012.A1]\n")
    assert _rule_errors(run_dir, "SVCA-001") == []


def test_no_baseline_is_no_alignment_finding(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / "baseline.json").unlink()
    assert not any("outside the baseline" in m for m in _rule_errors(run_dir, "SVCA-001"))


def test_a_documentation_weakness_on_sc_13_needs_no_vep_referral(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/poam/items.yaml",
              lambda d: d["items"][0].update(control_id="sc-13"))
    assert _rule_errors(run_dir, "CRYP-003") == []
