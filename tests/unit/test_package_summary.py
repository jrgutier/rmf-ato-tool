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
