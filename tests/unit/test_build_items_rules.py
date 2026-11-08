"""Cases the sources of the tier 1 build items permit, which their rules must let pass. The
negative fixtures (tests/fixtures/negative/) prove each clause fails; these prove the rules
stay quiet where the source allows the case."""

from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.run.model import open_run

BIA = "artifacts/data/bia.yaml"
CHANGES = "artifacts/data/changes.yaml"


def _messages(run_dir, prefix):
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule.startswith(prefix)]


def _run(tmp_path):
    return copy_run(VALID_MINIMAL, tmp_path / "run")


def test_criticality_needs_no_assess_iteration_before_categorization(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / "facts.yaml", lambda d: d.pop("categorization"))
    edit_yaml(run_dir / BIA, lambda d: d["criticality"]["iterations"].pop(1))
    assert not [m for m in _messages(run_dir, "BIA-003") if "Assess" in m]


def test_criticality_monitor_iteration_on_or_after_a_significant_change_passes(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / CHANGES,
              lambda d: d["changes"][0]["security_impact"].update(result="significant"))
    edit_yaml(run_dir / BIA, lambda d: d["criticality"]["iterations"].append(
        {"step": "monitor", "date": "2026-12-01", "change": "CHG-001",
         "summary": "The relay update leaves the critical items unchanged.",
         "sources": ["INT-019.A1"]}))
    assert _messages(run_dir, "BIA-003") == []


def test_criticality_monitor_iteration_dated_before_the_change_fails(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / CHANGES,
              lambda d: d["changes"][0]["security_impact"].update(result="significant"))
    edit_yaml(run_dir / BIA, lambda d: d["criticality"]["iterations"].append(
        {"step": "monitor", "date": "2026-11-01", "change": "CHG-001",
         "summary": "Reviewed.", "sources": ["INT-019.A1"]}))
    assert _messages(run_dir, "BIA-003") == [
        "the criticality analysis has its Monitor iteration for CHG-001 dated before the change"]


def test_criticality_without_mission_critical_functions_needs_no_defensive_item(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / BIA, lambda d: d["criticality"]["critical_items"].pop(1))
    assert _messages(run_dir, "BIA-003") == []


def test_criticality_system_item_is_not_read_against_the_boundary(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / BIA, lambda d: d["criticality"]["critical_items"].append(
        {"rank": 3, "kind": "system", "item": "Analysis enclave", "role": "infrastructure",
         "processes": ["BP-01"], "sources": ["INT-019.A1"]}))
    assert _messages(run_dir, "BIA-003") == []


ORG = "artifacts/data/org-context.yaml"


def _later(run_dir, index, later):
    edit_yaml(run_dir / ORG, lambda d: d["reference_currency"]["references"][index].update(
        later_edition=later))


def test_reference_currency_later_cnss_edition_adopted_passes(tmp_path):
    run_dir = _run(tmp_path)
    _later(run_dir, 0, {"edition": "November 2026", "published": "2026-10-01", "adopted": True})
    assert _messages(run_dir, "RCUR-001") == []


def test_reference_currency_sp800_53_release_within_a_year_may_wait(tmp_path):
    run_dir = _run(tmp_path)
    _later(run_dir, 3, {"edition": "Release 5.3.0", "published": "2026-01-15",
                        "adopted": False})
    assert _messages(run_dir, "RCUR-001") == []


def test_posture_report_listing_the_plan_change_passes(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / "artifacts/data/plan-reviews.yaml",
              lambda d: d["changes"][0].update(date="2026-12-20"))
    edit_yaml(run_dir / "artifacts/data/posture-reports.yaml",
              lambda d: d["reports"][0].update(plan_changes=["1.1"]))
    assert _messages(run_dir, "MRPT-003") == []
