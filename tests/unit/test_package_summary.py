"""XSUM-001 beyond its negative fixtures: the open POA&M items the executive summary must
highlight are those open when the package was submitted, judged from the POA&M's own dates."""
from conftest import REPO_ROOT, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

POAM = "artifacts/poam/items.yaml"
SUMMARY = "artifacts/data/package-summary.yaml"
UNHIGHLIGHTED = "highlights no risk management issue"


def _messages(run_dir) -> list[str]:
    found = engine.evaluate(open_run(run_dir, REPO_ROOT)).findings
    return [f.finding.message for f in found if f.rule == "XSUM-001"]


def _cite_only_poam_004(d):
    d["issues"] = [{"id": "XS-01", "issue": "The patch item shows the flaw process works.",
                    "poam_items": ["POAM-004"]}]


def test_an_item_identified_after_the_submission_need_not_be_highlighted(minimal_run):
    def later(d):
        for item in d["items"][:3]:
            item["identified"]["date"] = "2026-11-20"  # after the 2026-11-10 submission
    edit_yaml(minimal_run / POAM, later)
    edit_yaml(minimal_run / SUMMARY, _cite_only_poam_004)
    assert not [m for m in _messages(minimal_run) if UNHIGHLIGHTED in m]


def test_an_item_completed_after_the_submission_was_open_when_it_went_in(minimal_run):
    def completed_later(d):
        first = d["items"][0]
        first["status"], first["completed_on"] = "completed", "2026-12-01"
        for item in d["items"][1:3]:
            item["identified"]["date"] = "2026-11-20"
    edit_yaml(minimal_run / POAM, completed_later)
    edit_yaml(minimal_run / SUMMARY, _cite_only_poam_004)
    assert [m for m in _messages(minimal_run) if UNHIGHLIGHTED in m and "POAM-001" in m]


LATE = "after the authorization decision"


def _reauthorized(d):
    first = next(r for r in d["records"] if r["id"] == "AUTH-002")
    d["records"].append({**first, "id": "AUTH-003", "basis": "reauthorization",
                         "supersedes": "AUTH-002", "date": "2027-11-10"})


def test_a_reauthorization_package_is_not_late_against_the_decision_it_renews(minimal_run):
    edit_yaml(minimal_run / "artifacts/data/authorizations.yaml", _reauthorized)
    edit_yaml(minimal_run / SUMMARY, lambda d: d["submission"].update(date="2027-10-15"))
    assert not [m for m in _messages(minimal_run) if LATE in m]


def test_a_package_submitted_after_every_decision_is_late(minimal_run):
    edit_yaml(minimal_run / SUMMARY, lambda d: d["submission"].update(date="2026-11-25"))
    assert [m for m in _messages(minimal_run) if LATE in m and "AUTH-002" in m]


def test_risk_accepted_and_undated_completed_items_are_not_open(minimal_run):
    def closed(d):
        d["items"][0]["status"] = "risk-accepted"
        for item in d["items"][1:3]:
            item["status"] = "completed"
            item.pop("completed_on", None)
    edit_yaml(minimal_run / POAM, closed)
    edit_yaml(minimal_run / SUMMARY, _cite_only_poam_004)
    assert not [m for m in _messages(minimal_run) if UNHIGHLIGHTED in m]
