"""The cases the sources permit that cluster DB's rules once refused: each passes."""

from __future__ import annotations

from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

DATA = "artifacts/data"


def _found(run_dir, rule):
    return [f.finding.message for f in RULES[rule](Context(open_run(run_dir, REPO_ROOT)))]


def test_a_system_leveraged_at_a_reauthorization_is_reviewed_before_that_decision(tmp_path):
    """SP 800-37r2 Appendix F: the review is the basis of the decision that relies on it, so a
    package reviewed after the first ATO and before the reauthorization that leverages it passes."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def reauthorize(d):
        later = dict(d["records"][1], id="AUTH-003", basis="reauthorization", date="2027-02-01")
        d["records"].append(later)

    edit_yaml(run_dir / f"{DATA}/authorizations.yaml", reauthorize)
    edit_yaml(run_dir / f"{DATA}/leveraged-authorizations.yaml",
              lambda d: d["leveraged_authorizations"][0]["package_review"].update(
                  date="2027-01-10", relied_on_by="AUTH-003"))
    assert _found(run_dir, "RECIP-001") == []


def test_a_cybersecurity_strategy_updated_after_the_first_authorization_passes(tmp_path):
    """DoDI 5000.82 3.5.b.(3): the PM updates and maintains the CSS for the life of the system."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / f"{DATA}/cybersecurity-strategy.yaml",
              lambda d: d["strategy"].update(version="2.0", date="2027-01-15"))
    assert _found(run_dir, "CSSTRAT-003") == []


def test_a_product_support_strategy_approved_after_first_fielding_passes(tmp_path):
    """DoDI 5000.85 3.15.a sets no order between the PSS approval and first fielding."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def field(d):
        d["program"]["decision_points"].append({"id": "MS-FIELD", "date": "2026-09-01"})
        d["program"]["pss"] = {"approved_by": "PER-MDA", "date": "2027-03-01"}

    edit_yaml(run_dir / f"{DATA}/protection.yaml", field)
    edit_yaml(run_dir / "facts.yaml", lambda d: d["lifecycle_phase"].update(value="PH-PD"))
    assert _found(run_dir, "ACQLC-003") == []


def _combine(run_dir, pathway, pathways, **acquisition):
    edit_yaml(run_dir / "facts.yaml", lambda d: d["acquisition"].update(
        pathway=pathway, pathways=pathways, **acquisition))


def test_a_transition_to_a_pathway_other_than_software_needs_no_tailoring(tmp_path):
    """DoDI 5000.02 4.1.a asks of a transition MDA approval, its point, its information
    requirements and a smooth transition; tailoring is DoDI 5000.87 3.1.d, to the software
    pathway only."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _combine(run_dir, "PW-MCA", ["PW-MCA", "PW-MTA"])
    transition = {"from": "PW-MCA", "to": "PW-MTA", "at": "MS-B", "entry": "MS-B",
                  "date": "2026-06-01",
                  "information_requirements": [
                      {"id": "EXT-CAPDOC", "coordinated_with": ["PER-PM", "PER-MDA"]}],
                  "approach": {"approved_by": "PER-MDA", "date": "2026-05-01"}}
    edit_yaml(run_dir / f"{DATA}/protection.yaml",
              lambda d: d["program"].update(transitions=[transition]))
    assert _found(run_dir, "ACQLC-001") == []


def test_a_covered_dbs_incorporating_the_software_pathway_records_no_transition(tmp_path):
    """DoDI 5000.87 1.2.b: a covered DBS uses the DBS pathway and incorporates the software
    pathway for its custom software; it moves to no new pathway."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    _combine(run_dir, "PW-DBS", ["PW-DBS", "PW-SWP"], covered_dbs=True)
    assert [m for m in _found(run_dir, "ACQLC-001") if "transition" in m] == []


def test_a_draft_jcids_document_before_cdd_validation_passes(tmp_path):
    """DoDI 5000.85 3.8.c: the CDD is validated during TMRR; P-15 may read the draft first."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / f"{DATA}/protection-requirements.yaml",
              lambda d: d["capability_document"].pop("validated"))
    assert _found(run_dir, "ACQLC-004") == []


def test_a_system_with_no_capability_document_names_none(tmp_path):
    """DoDI 8510.01 3.3.a(1)(a) asks for the categorization in the appropriate capabilities
    document; a system P-15 read none for has none to name."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / f"{DATA}/protection-requirements.yaml",
              lambda d: d.pop("capability_document"))
    edit_yaml(run_dir / "facts.yaml", lambda d: d["categorization"].pop("documented_in"))
    assert _found(run_dir, "ACQLC-005") == []


def test_a_designation_above_every_threat_needs_only_its_rationale(tmp_path):
    """DoDI 8510.01 3.3.a(3) bounds the designation from below; above the worst threat it is
    the organization's, so it names no threat as its source."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / f"{DATA}/ra.yaml", lambda d: d.update(system_risk={
        "level": "high", "rationale": "Mission policy designates the relay high.",
        "sources": ["INT-023.A1"]}))
    assert _found(run_dir, "THREAT-001") == []


def test_a_risk_tolerance_above_its_procurement_row_with_a_basis_passes(tmp_path):
    """DoDI 5000.90 Table 1 names the procurement each level applies to by example."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / f"{DATA}/scrm.yaml", lambda d: d["pm_actions"]["risk_tolerance"].update(
        procurement="engineered"))
    assert _found(run_dir, "PMSCRM-001") == []
