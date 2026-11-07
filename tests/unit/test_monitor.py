"""What the Monitor rules must let through: the cases the sources permit, which a negative fixture
cannot show, and the states a run reaches only part way through a cycle."""

from pathlib import Path

import pytest
from conftest import REPO_ROOT, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import authorization, monitor
from rmf_tool.run.model import open_run

CHANGES = "artifacts/data/changes.yaml"
REPORTS = "artifacts/data/posture-reports.yaml"
POAM = "artifacts/poam/items.yaml"
CONMON = "artifacts/data/conmon.yaml"
LEVERAGED = "artifacts/data/leveraged-authorizations.yaml"
LEDGER = "artifacts/data/authorizations.yaml"
PLAN = "artifacts/data/plan-reviews.yaml"
TRANSFER = {"outgoing": "Col A", "incoming": "Col B", "reviewed": ["ART-AODM", "ART-PKG"],
            "accepts_risk_to": []}


def messages(run_dir: Path, rule) -> list[str]:
    return [f.finding.message for f in rule(Context(open_run(run_dir, REPO_ROOT)))]


@pytest.mark.parametrize("rule", [monitor.change_lifecycle, monitor.unauthorized_changes,
                                  monitor.le_ci, monitor.connections, monitor.poam_sources,
                                  monitor.posture_reports, monitor.organization_tier,
                                  monitor.iscm_assessments, monitor.measurement,
                                  monitor.plan_reviews, monitor.inheritance])
def test_the_base_run_holds_every_record(minimal_run, rule):
    assert messages(minimal_run, rule) == []


def test_an_out_of_play_artifact_keeps_its_rules_quiet(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("seeded", []))
    (minimal_run / CHANGES).unlink()
    (minimal_run / REPORTS).unlink()
    assert messages(minimal_run, monitor.change_lifecycle) == []
    assert messages(minimal_run, monitor.posture_reports) == []


def test_an_exempt_change_closes_with_no_test_board_or_verification(minimal_run):
    edit_yaml(minimal_run / CHANGES, lambda d: d["changes"][2].update(closed="2027-01-06",
                                                                      control="pre-approved"))
    assert messages(minimal_run, monitor.change_lifecycle) == []


def test_a_disapproved_change_closes_with_nothing_to_verify(minimal_run):
    def edit(d):
        change = d["changes"][0]
        change["decision"]["outcome"] = "disapproved"
        del change["implementation"], change["verification"]
    edit_yaml(minimal_run / CHANGES, edit)
    assert messages(minimal_run, monitor.change_lifecycle) == []


def test_a_change_already_made_or_ordered_owes_no_test_first(minimal_run):
    edit_yaml(minimal_run / CHANGES, lambda d: d["changes"][1].pop("test"))
    assert messages(minimal_run, monitor.change_lifecycle) == []


def test_an_open_change_may_stay_under_analysis_if_a_poam_item_tracks_it(minimal_run):
    edit_yaml(minimal_run / CHANGES,
              lambda d: d["changes"][1]["root_cause"].update(cause="under-analysis"))
    assert messages(minimal_run, monitor.unauthorized_changes) == []


def test_a_privacy_impact_needs_a_response_on_an_authorized_change(minimal_run):
    edit_yaml(minimal_run / CHANGES, lambda d: d["changes"][0].update(privacy_impact=True))
    assert "the response to the root cause" in messages(minimal_run,
                                                        monitor.unauthorized_changes)[0]


def test_an_unlawful_le_ci_request_may_be_refused_and_an_attempt_is_enough(minimal_run):
    def edit(d):
        change = d["changes"][3]
        change["decision"]["outcome"] = "disapproved"
        change["le_ci"].update(lawful=False, outcome="attempted")
    edit_yaml(minimal_run / CHANGES, edit)
    assert messages(minimal_run, monitor.le_ci) == []


def test_a_denied_connection_that_stands_disconnected_passes(minimal_run):
    edit_yaml(minimal_run / CHANGES, lambda d: d.__setitem__("connections", [
        {"id": "CON-001", "system": "Enclave", "relationship": "hosted", "decision": "AD-DATO",
         "action": "disconnected", "sources": ["INT-030.A1"]}]))
    assert messages(minimal_run, monitor.connections) == []


def test_a_real_common_control_provider_passes(minimal_run):
    def edit(d):
        d["leveraged_authorizations"][0].update(arrangement="common-control-provider",
                                                provider="Analysis enclave")
        del d["leveraged_authorizations"][0]["ao_aware"]
    edit_yaml(minimal_run / LEVERAGED, edit)
    assert messages(minimal_run, monitor.inheritance) == []


def test_an_accepted_risk_needs_no_poam_item(minimal_run):
    """SP 800-37r2 Task A-6: no entry is necessary for a deficiency accepted as residual risk."""
    def edit(d):
        finding = d["external_findings"][0]
        del finding["poam_item"]
        finding["accepted_in"] = "AUTH-002"
    edit_yaml(minimal_run / POAM, edit)
    assert messages(minimal_run, monitor.poam_sources) == []


def test_no_poam_review_is_due_before_a_decision(minimal_run):
    edit_yaml(minimal_run / LEDGER, lambda d: d.__setitem__("records", []))
    edit_yaml(minimal_run / POAM, lambda d: d.pop("ao_review"))
    assert messages(minimal_run, monitor.poam_sources) == []


def test_an_se_system_reports_to_dia_alone(minimal_run):
    edit_yaml(minimal_run / CONMON,
              lambda d: d["reporting"]["dodin"].update(designation="SE"))
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0]["deliveries"].append(
        {"recipient": "DIA", "date": "2027-03-02", "content": ["poam"]}))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_a_system_off_the_dodin_owes_no_dodin_status(minimal_run):
    edit_yaml(minimal_run / CONMON, lambda d: d["reporting"].update(
        dodin={"designation": "not-connected"}))
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0].update(
        deliveries=[{"recipient": p, "date": "2027-03-01", "content": ["posture"]}
                    for p in ("PER-AO", "PER-ISSM")]))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_a_report_need_not_resend_what_an_earlier_one_delivered(minimal_run):
    later = {"id": "SPR-002", "period": {"from": "2027-03-01", "to": "2027-03-31"},
             "issued": "2027-03-31", "marking": "CUI", "scorecard": {"reported": "2027-02-15"},
             "deliveries": [{"recipient": p, "date": "2027-03-31", "content": ["posture"]}
                            for p in ("PER-AO", "PER-ISSM")],
             "sharing": {"display": "automated", "audiences": ["superior", "peer"],
                         "qualities": ["visible", "accessible", "understandable", "trusted",
                                       "interoperable"]},
             "sources": ["INT-030.A1"]}
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"].append(later))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_a_board_approves_a_plan_update_under_change_management(minimal_run):
    edit_yaml(minimal_run / PLAN, lambda d: d["changes"][0].update(approved_by="PER-CCB"))
    assert messages(minimal_run, monitor.plan_reviews) == []


def test_a_run_begun_after_the_authorization_monitors_from_its_own_start(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("as_of", "2026-12-15T00:00:00Z"))
    edit_yaml(minimal_run / CHANGES, lambda d: d["monitoring"]["unauthorized_changes"].update(
        {"from": "2026-12-15"}))
    assert messages(minimal_run, monitor.unauthorized_changes) == []


def test_cmrs_is_owed_only_under_a_cato(minimal_run):
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0].pop("cmrs"))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_m2_needs_measurement_and_m4_needs_a_review(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("include_after_stop",
                                                                ["M-2", "M-4"]))
    edit_yaml(minimal_run / CONMON, lambda d: d.pop("measurement"))
    edit_yaml(minimal_run / PLAN, lambda d: d.__setitem__("reviews", []))
    assert "holds no security measurement" in messages(minimal_run, monitor.measurement)[0]
    assert "logs it" in messages(minimal_run, monitor.plan_reviews)[0]


@pytest.mark.parametrize(("response", "extra"), [
    ("new-terms", {}), ("denial", {}),
    ("authorization-action", {"action": "reauthorization"}),
])
def test_a_new_ao_who_finds_the_risk_unacceptable_has_three_answers(minimal_run, response, extra):
    transfer = {**TRANSFER, "risk_finding": "unacceptable", "response": response, **extra}
    edit_yaml(minimal_run / LEDGER, lambda d: d["records"][1].update(basis="ao-change",
                                                                     ao_transfer=transfer))
    assert messages(minimal_run, authorization.ao_change) == []


def _aodr_change(d):
    d["changes"][0]["test"]["presented_to"] = ["PER-CCB", "PER-AODR"]


def _aodr_le_ci(d):
    next(c for c in d["changes"] if c.get("origin") == "le-ci")["le_ci"]["coordinated_with"] = \
        "PER-AODR"


@pytest.mark.parametrize(("path", "edit", "rule"), [
    (CHANGES, _aodr_change, monitor.change_lifecycle),
    (CHANGES, _aodr_le_ci, monitor.le_ci),
    (LEVERAGED, lambda d: d["leveraged_authorizations"][0]["ao_aware"].update(
        official="PER-AODR"), monitor.inheritance),
    (POAM, lambda d: d["ao_review"].update(by="PER-AODR"), monitor.poam_sources),
])
def test_the_aodr_acts_for_the_ao(minimal_run, path, edit, rule):
    edit_yaml(minimal_run / path, edit)
    assert messages(minimal_run, rule) == []


def test_no_monitoring_start_is_due_before_any_authorization(minimal_run):
    edit_yaml(minimal_run / LEDGER, lambda d: d.__setitem__("records", []))
    edit_yaml(minimal_run / CHANGES, lambda d: d["monitoring"].pop("unauthorized_changes"))
    assert not [m for m in messages(minimal_run, monitor.unauthorized_changes) if "starts at" in m]


def test_a_completed_item_does_not_falsify_an_earlier_organization_tier_count(minimal_run):
    edit_yaml(minimal_run / POAM, lambda d: d["items"][0].update(status="completed"))
    assert messages(minimal_run, monitor.organization_tier) == []


def test_a_scorecard_on_a_slower_cycle_than_the_report_passes(minimal_run):
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0]["scorecard"].update(
        reported="2025-06-01"))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_dodin_bodies_are_owed_poams_and_coordination_only_as_required(minimal_run):
    edit_yaml(minimal_run / CONMON, lambda d: d["reporting"]["dodin"].pop("required_by"))
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0].update(
        deliveries=[dl for dl in d["reports"][0]["deliveries"]
                    if dl["recipient"] in ("PER-AO", "PER-ISSM", "CDRUSSTRATCOM")]))
    edit_yaml(minimal_run / REPORTS, lambda d: d["reports"][0]["deliveries"][2].update(
        content=["findings"]))
    assert messages(minimal_run, monitor.posture_reports) == []


def test_a_change_names_no_external_service_with_null(minimal_run):
    edit_yaml(minimal_run / LEVERAGED, lambda d: d["leveraged_authorizations"][0].update(
        arrangement="external-service"))
    edit_yaml(minimal_run / CHANGES, lambda d: [c.update(external_service=None)
                                                for c in d["changes"]])
    assert messages(minimal_run, monitor.posture_reports) == []


def test_any_combining_single_score_passes(minimal_run):
    edit_yaml(minimal_run / LEDGER, lambda d: d["iscm_assessments"][0].update(overall_score=9))
    assert messages(minimal_run, monitor.iscm_assessments) == []


ACCEPTED = {**TRANSFER, "risk_finding": "acceptable", "response": "signed-decision",
            "accepts_risk_to": sorted(authorization.AO_ACCEPTS)}


@pytest.mark.parametrize(("decision", "reviewed"), [
    ("AD-ATOC", ["ART-SECRPT"]),
    ("AD-CATO", ["ART-AODM", "ART-PKG"]),
])
def test_a_new_ao_may_read_the_automated_report_alone_and_sign_a_cato(minimal_run, decision,
                                                                       reviewed):
    transfer = {**ACCEPTED, "reviewed": reviewed}
    edit_yaml(minimal_run / LEDGER, lambda d: d["records"][1].update(
        basis="ao-change", decision=decision, ao_transfer=transfer))
    assert messages(minimal_run, authorization.ao_change) == []


@pytest.mark.parametrize(("rel", "edit", "needle"), [
    (CHANGES, lambda d: d["changes"][0].update(id=["CHG-001"]), None),
    (PLAN, lambda d: d["changes"][0].update(change_ref=["CHG-001"], approved_by=["PER-AO"]),
     "by PER-AO or PER-AODR or PER-CCB, not ['PER-AO']"),
    (PLAN, lambda d: d["reviews"][0].update(date=["2026-10-30"]), None),
    (PLAN, lambda d: d.update(schedule={"interval_days": "yearly"}, changes="v1"), None),
])
def test_a_malformed_plan_review_log_is_a_finding_not_a_crash(minimal_run, rel, edit, needle):
    edit_yaml(minimal_run / rel, edit)
    found = messages(minimal_run, monitor.plan_reviews)
    assert needle is None or any(needle in m for m in found)
