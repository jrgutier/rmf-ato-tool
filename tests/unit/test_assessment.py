"""The assessment rules allow what their sources allow, and the POA&M's dates freeze once."""

from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

from rmf_tool import build, catalog
from rmf_tool.check import engine
from rmf_tool.run import poam_dates
from rmf_tool.run.model import open_run

SAP = "artifacts/data/sap.yaml"
POAM = "artifacts/poam/items.yaml"
AC = "artifacts/sar/results/ac.yaml"
USERS = "artifacts/data/users.yaml"
ORIGINAL = poam_dates.ORIGINAL_FILE


def errors(run_dir):
    run = open_run(run_dir, REPO_ROOT)
    return [f for f in engine.select(run, engine.evaluate(run), final=True) if f.severity == "E"]


def built(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    return errors(run_dir)


def test_determination_statements_are_the_leaf_objectives():
    cat = catalog.load(REPO_ROOT)
    labels = catalog.determination_statements(cat, "ac-2")
    assert {"AC-02a.[01]", "AC-02b.", "AC-02d.03[02]", "AC-02j."} <= set(labels)
    assert "AC-02a." not in labels and "AC-02" not in labels


def test_a_control_stays_satisfied_with_a_statement_that_does_not_apply(tmp_path):
    """SP 800-53A: assessors can disregard a non-applicable requirement and still find the
    control satisfied."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/sar/results/si.yaml", lambda d: d["determinations"][0][
        "statements"][0].update(result="not-applicable", reason="No PII in the flaw reports."))
    assert built(run_dir) == []


def test_methods_are_not_limited_to_all_three(tmp_path):
    """Organizations are not expected to employ every method: the plan and the result may use
    one."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / SAP, lambda d: d["procedures"][1].update(
        methods=["examine"], objects=["specifications"],
        sampling=[s for s in d["procedures"][1]["sampling"] if s["method"] == "examine"]))
    edit_yaml(run_dir / SAP, lambda d: d["procedures"][1]["sampling"][0].update(
        types=[t for t in d["procedures"][1]["sampling"][0]["types"]
               if t["type"] == "specifications"]))
    edit_yaml(run_dir / "artifacts/sar/results/cm.yaml",
              lambda d: d["determinations"][0].update(methods=["examine"]))
    assert built(run_dir) == []


def test_an_inconsequential_finding_needs_no_poam_item_or_risk(tmp_path):
    """SP 800-37r2: the system owner may decide a finding is inconsequential; it stays in the
    report. Neither SAR-POAM-001 nor RAR-001 asks for more."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / AC, lambda d: d["findings"][0]["triage"].update(action="inconsequential"))
    def drop(poam):
        poam["items"] = [i for i in poam["items"] if i["finding_ref"] != "FND-001"]
        for n, item in enumerate(sorted(poam["items"], key=lambda i: i["priority"]), 1):
            item["priority"] = n
    edit_yaml(run_dir / POAM, drop)
    edit_yaml(run_dir / "artifacts/data/rar.yaml",
              lambda d: d.update(risks=[r for r in d["risks"] if r["id"] != "RSK-001"]))
    edit_yaml(run_dir / "artifacts/data/rar.yaml", lambda d: d["risks"][0].update(priority=1))
    assert [f for f in built(run_dir) if f.rule in ("SAR-POAM-001", "RAR-001", "ASMT-006")] == []


def test_a_user_group_with_no_logical_access_needs_no_access_decision(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    def strip(users):
        users["users"][0]["privilege_level"] = "no-logical-access"
        del users["users"][0]["access_decision"]
    edit_yaml(run_dir / USERS, strip)
    assert [f for f in errors(run_dir) if f.rule == "ASMT-013"] == []


def test_a_late_milestone_with_a_recorded_change_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / POAM, lambda d: d["items"][0].update(
        milestone_changes=[{"milestone": "Run and record the first account review",
                            "new_date": "2027-02-10", "reason": "The reviewer moved."}],
        status="delayed", obstacles=["personnel"], comments="The reviewer moved."))
    assert built(run_dir) == []


def test_dates_freeze_only_after_the_a6_checkpoint(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / ORIGINAL).unlink()
    journal = run_dir / "journal.md"
    journal.write_text(journal.read_text().replace("CHECKPOINT · task A-6", "NOTE · task A-6"))
    edit_yaml(run_dir / POAM, lambda d: d["items"][0].update(scheduled_completion="2027-03-01"))
    assert poam_dates.freeze(open_run(run_dir, REPO_ROOT)) is None


def test_the_first_frozen_date_stays(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    first = (run_dir / ORIGINAL).read_text()
    edit_yaml(run_dir / POAM, lambda d: d["items"][0].update(scheduled_completion="2027-03-01"))
    build.build(open_run(run_dir, REPO_ROOT))
    assert (run_dir / ORIGINAL).read_text() == first


def test_a_new_item_joins_the_frozen_dates(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / POAM, lambda d: d["items"].append(
        {**d["items"][0], "id": "POAM-005", "priority": 5}))
    build.build(open_run(run_dir, REPO_ROOT))
    frozen = YAML(typ="safe").load((run_dir / ORIGINAL).read_text())["items"]
    assert frozen["POAM-005"]["scheduled_completion"] == "2027-01-29"


def test_an_older_contract_writes_no_frozen_dates(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / ORIGINAL).unlink()
    edit_yaml(run_dir / "run.yaml", lambda d: d.update(framework_version="0.1.0"))
    assert poam_dates.freeze(open_run(run_dir, REPO_ROOT)) is None


def test_procedures_run_together_may_share_a_sequence(tmp_path):
    """SP 800-53A names sequencing as one way to optimize, not a total order."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / SAP, lambda d: d["procedures"][1].update(
        sequence=d["procedures"][0]["sequence"]))
    assert [f for f in errors(run_dir) if f.rule == "ASMT-002"] == []


def test_a_more_critical_deficiency_may_go_ahead_of_a_higher_risk(tmp_path):
    """SP 800-37r2 Task A-6: the prioritized approach weighs criticality beside risk."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    def rerank(poam):
        for item, priority in zip(poam["items"], (1, 2, 3, 4), strict=True):
            item["priority"] = priority
        poam["items"][0]["criticality"] = "very-high"
    edit_yaml(run_dir / POAM, rerank)
    assert [f for f in errors(run_dir) if f.rule == "ASMT-012"] == []


def test_a_remediated_closed_finding_still_names_its_statement(tmp_path):
    """SP 800-37r2 Task A-5: remediation and the addendum do not change the initial findings, so
    a closed finding keeps naming the other than satisfied statement it found."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / AC, lambda d: d["findings"][0].update(status="closed"))
    edit_yaml(run_dir / POAM, lambda d: d["items"][0].update(
        status="completed", completed_on="2027-01-20",
        corrective_action_test={"by": "PER-SCA", "date": "2027-01-20", "result": "Reviewed."}))
    assert [f for f in errors(run_dir) if f.rule in ("ASMT-005", "ASMT-011")] == []


def test_one_interview_round_beside_a_separate_examine_and_test_record(tmp_path):
    """SP 800-53A consolidation: a control may sit in an interview record shared across
    controls and in its own examine and test record."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    def split(sap):
        first = sap["procedures"][0]
        first.update(methods=["examine", "test"], objects=["specifications", "mechanisms"])
        sap["procedures"].append({**first, "id": "PRC-003", "controls": ["ac-2", "cm-6"],
                                  "methods": ["interview"], "objects": ["individuals"],
                                  "sequence": 3})
    edit_yaml(run_dir / SAP, split)
    assert [f for f in errors(run_dir) if f.rule == "ASMT-002"] == []


def test_provider_evidence_may_still_be_requested_before_the_report(tmp_path):
    """The package needs the provider's evidence (SP 800-37r2 Task A-4, R-2); while the plan is
    made it may still be on request."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / SAP, lambda d: d["external_providers"][0]["provider_assessment"].update(
        evidence="requested"))
    assert [f for f in errors(run_dir) if f.rule == "ASMT-004"]
    edit_yaml(run_dir / "run.yaml", lambda d: d.update(
        lifecycle_stop="A-3", lifecycle_stop_rationale="The report is not written yet."))
    assert [f for f in errors(run_dir) if f.rule == "ASMT-004"] == []


def test_the_designated_representative_may_act_for_the_ao(tmp_path):
    """SP 800-37r2: the AO may delegate everything but the authorization decision."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / SAP, lambda d: d["assessor_independence"].update(
        determined_by="PER-AODR"))
    assert [f for f in errors(run_dir) if f.rule == "ASMT-007"] == []
