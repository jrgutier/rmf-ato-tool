"""What the program protection and test strategy rules allow: each case below is one the source
permits, so a rule that starts refusing it fails here. The clauses that refuse have their negative
fixtures (tests/fixtures/negative/PPROT-*.yaml and TSTRAT-*.yaml)."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

PROT = "artifacts/data/protection.yaml"
PREQ = "artifacts/data/protection-requirements.yaml"
NSS = "artifacts/data/nss-assessments.yaml"
TS = "artifacts/data/test-strategy.yaml"
FACTS = "facts.yaml"


def _errors(run_dir):
    run = open_run(run_dir, REPO_ROOT)
    return [(f.rule, f.finding.message) for f in engine.evaluate(run).findings
            if f.rule.startswith(("PPROT", "TSTRAT"))]


def _award_not_updated(d):
    d["contract_awards"] = [{"id": "K-001", "date": "2026-05-01",
                             "no_update_reason": "The award kept the approved technical approach."}]


def _pm_prepares(d):
    d["ppp"]["prepared_by"] = "PER-PM"


def _two_rfps(d):
    d["solicitations"].append({"id": "RFP-SUP-001", "kind": "rfp", "countermeasures": [],
                               "cyber_resilient_requirements": [], "assurance_remediation": []})


def _rfp_deviation(d):
    d["solicitations"][0].update(countermeasures=[], cyber_resilient_requirements=[],
                                 deviation="A sole-source bridge RFP; the PPP countermeasures "
                                           "go in the follow-on.")


def _aodr_assesses(d):
    d["assessments"][0]["assessed_by"] = ["NSA", "PER-AODR"]


def _later_tapp(d):
    d["inputs"]["tapps"] = [{"id": "TAPP-ME", "area": "microelectronics", "title": "TAPP",
                             "date": "2026-06-01"}]
    d["ppp"]["informed_by"] = ["TAPP-ME"]


def _malformed(d):
    d["technical_risks"][0]["drawn_from"] = 7
    d["ppp"]["sse_activities"] = "cyber-resilient-engineering"


@pytest.mark.parametrize(("file", "edit"), [
    pytest.param(PROT, _award_not_updated, id="a-should-answered-with-a-reason"),
    pytest.param(PROT, _pm_prepares, id="the-pm-prepares-the-ppp-under-5000.88"),
    pytest.param(PREQ, _two_rfps, id="rfps-judged-as-a-set"),
    pytest.param(PREQ, _rfp_deviation, id="an-rfp-deviation-answers-a-should"),
    pytest.param(NSS, _aodr_assesses, id="the-aodr-acts-for-the-ao"),
    pytest.param(PROT, _later_tapp, id="a-tapp-read-after-p-15-is-not-asked-of-it"),
])
def test_permitted(file, edit, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / file, edit)
    assert _errors(run_dir) == []


def test_assessment_before_a_decision_point_that_is_no_milestone_is_not_asked(tmp_path):
    """CNSSP 12 and DoDI 8510.01 ask for the NSA assessment before milestones; the development RFP
    release is a decision point, not a milestone."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / PROT, lambda d: (
        d["program"]["decision_points"].append({"id": "MS-DRFPRD", "date": "2026-05-01"}),
        d["ppp"]["submissions"].append({"decision_point": "MS-DRFPRD", "date": "2026-04-20"})))
    assert _errors(run_dir) == []


def test_a_pathway_without_listed_decision_points_is_not_judged(tmp_path):
    """The framework lists no decision points for PW-MTA yet, so none is refused there."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FACTS, lambda d: d["acquisition"].update(pathway="PW-MTA"))
    edit_yaml(run_dir / PROT, lambda d: d["ppp"]["tailoring"].update(pathway="PW-MTA"))
    edit_yaml(run_dir / TS, lambda d: d["document"].update(kind="test-strategy", pathway="PW-MTA"))
    assert _errors(run_dir) == []


def test_malformed_lists_are_findings_not_crashes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / PROT, _malformed)
    rules = {rule for rule, _ in _errors(run_dir)}
    assert rules == {"PPROT-002"}


def _ppp_errors(run_dir):
    return [e for e in _errors(run_dir) if e[0].startswith("PPROT")]


def test_oversight_with_no_live_fire_needs_no_lfte_approval(tmp_path):
    """DOT&E approves the LFT&E planning only where there is live fire testing."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / TS, lambda d: (
        d["oversight"].update(dote=True),
        d["approvals"][0].update(submitted_to_osd="2026-03-01"),
        d["approvals"].append({"part": "ot-e", "by": "DOT&E", "date": "2026-04-15"})))
    assert _errors(run_dir) == []


def test_software_pathway_mvcr_is_an_event_not_a_milestone(tmp_path):
    """The MVCR is deployed, not decided (DoDI 5000.87): no PPP submission or NSA assessment is
    asked before it, and the ATO must precede it."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FACTS, lambda d: d["acquisition"].update(pathway="PW-SWP"))
    edit_yaml(run_dir / PROT, lambda d: (
        d["program"].update(decision_points=[
            {"id": "DP-SWP-PATHWAY", "date": "2026-03-15"},
            {"id": "DP-SWP-EXECUTION", "date": "2026-04-15"},
            {"id": "DP-SWP-MVCR", "date": "2026-12-01"}]),
        d["ppp"].update(submissions=[{"decision_point": "DP-SWP-PATHWAY", "date": "2026-03-10"},
                                     {"decision_point": "DP-SWP-EXECUTION", "date": "2026-04-10"}]),
        d["ppp"]["tailoring"].update(pathway="PW-SWP")))
    edit_yaml(run_dir / NSS, lambda d: d["assessments"][0].update(decision_point="DP-SWP-EXECUTION",
                                                                   date="2026-04-01"))
    edit_yaml(run_dir / TS, lambda d: (
        d["document"].update(kind="test-strategy", pathway="PW-SWP"),
        [e.update(decision_point="DP-SWP-EXECUTION") for e in d["events"]],
        d["approvals"][0].update(decision_point="DP-SWP-EXECUTION")))
    assert _errors(run_dir) == []


@pytest.mark.parametrize("pathway", ["PW-DBS", "PW-AOS"])
def test_no_ppp_on_business_systems_or_services(pathway, tmp_path):
    """DoDI 5000.83 3.5 tailors program protection for MCA, UCA, MTA and SWP; DoDI 5000.74 and
    5000.75 ask no PPP of a business system or an acquisition of services."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FACTS, lambda d: d["acquisition"].update(pathway=pathway))
    (run_dir / PROT).unlink()
    assert _ppp_errors(run_dir) == []


def test_critical_technology_without_applicable_horizontal_guidance(tmp_path):
    """'Consistent with all available horizontal protection guidance' allows none."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / PROT, lambda d: (
        d["program"].update(critical_technology={"associated": True, "areas": []}),
        d["inputs"].update(horizontal_protection=[])))
    assert _errors(run_dir) == []


@pytest.mark.parametrize(("pathway", "kind"), [("PW-SWP", "cns"), ("PW-UCA", "juon")])
def test_jcids_content_is_asked_only_of_a_jcids_document(pathway, kind, tmp_path):
    """DoDI 5000.83 2.8 binds JCIDS capability requirements; a CNS or a JUON is no JCIDS
    document, so its missing SCRM, AT or threat content is not refused."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FACTS, lambda d: d["acquisition"].update(pathway=pathway))
    edit_yaml(run_dir / PREQ, lambda d: (
        d["capability_document"].update(kind=kind),
        [c.update(included=False, addressed_by=[])
         for c in d["capability_document"]["protection_content"]]))
    assert [e for e in _errors(run_dir) if e[0] == "PPROT-004"] == []


def test_a_rescinded_authorization_opens_no_gate(tmp_path):
    """GATE-001 reads the ledger in force on the gate's date: an ATO with conditions rescinded
    before the MVCR does not authorize the release."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / FACTS, lambda d: d["acquisition"].update(pathway="PW-SWP"))
    edit_yaml(run_dir / PROT, lambda d: d["program"].update(decision_points=[
        {"id": "DP-SWP-PATHWAY", "date": "2026-03-15"},
        {"id": "DP-SWP-MVCR", "date": "2027-02-01"}]))
    edit_yaml(run_dir / "artifacts/data/authorizations.yaml", lambda d: d["records"].append(
        {"id": "AUTH-003", "subject": "system", "task": "M-6", "decision": "AD-RESC",
         "decided_by": "PER-AO", "date": "2027-01-10", "underlying": "AUTH-002",
         "revocation_reason": "Risk no longer acceptable.", "sources": ["INT-012.A1"]}))
    run = open_run(run_dir, REPO_ROOT)
    gate = [f.finding.message for f in engine.evaluate(run).findings if f.rule == "GATE-001"]
    assert gate == ["the system is fielded at DP-SWP-MVCR, and no ATO or ATO with conditions of "
                    "the system stands on that date"]
