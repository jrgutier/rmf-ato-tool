"""The NIST task pin: the 47 Chapter 3 blocks of SP 800-37r2, parsed into data."""

import pytest
from conftest import REPO_ROOT

from rmf_tool.conformance import nist_pin
from rmf_tool.framework.model import TASKS_80037


@pytest.fixture(scope="module")
def pin():
    return {t["id"]: t for t in nist_pin.parse_repo(REPO_ROOT)}


def test_every_task_is_parsed_with_its_fields(pin):
    assert list(pin) == list(TASKS_80037)
    assert all(t["inputs"] and t["outputs"] and t["primary"] for t in pin.values())
    assert sum(len(t["supporting"]) > 0 for t in pin.values()) == 47


def test_phrases_are_whole_clean_and_split_at_semicolons(pin):
    """Each field is the block's semicolon list, one phrase per item: no empty phrase, no
    trailing punctuation, no unsplit list, and no field repeats a phrase."""
    for task in pin.values():
        for field in nist_pin.FIELDS:
            phrases = task[field]
            assert phrases == [p.strip() for p in phrases if p.strip()], (task["id"], field)
            assert not any(p.endswith((".", ";")) or ";" in p for p in phrases), (task["id"], field)
            assert len(set(phrases)) == len(phrases), (task["id"], field)
    assert pin["P-18"]["inputs"] == [
        "Organizational policy on system registration", "system information"]
    assert pin["P-18"]["outputs"] == ["Registered system in accordance with organizational policy"]
    assert pin["R-4"]["primary"] == ["Authorizing Official"]


def test_tasks_p1_to_p7_have_no_sdlc_line_and_the_rest_do(pin):
    assert [t for t in pin if "sdlc" not in pin[t]] == [f"P-{n}" for n in range(1, 8)]


def test_singular_supporting_role_is_read(pin):
    assert pin["P-12"]["supporting"] == [
        "Mission or Business Owner", "System Security Officer", "System Privacy Officer"]
    assert "Chief Information Officer" in pin["P-18"]["supporting"]


def test_a_value_runs_over_a_page_break(pin):
    assert pin["M-1"]["inputs"][-1] == "information from automated and manual monitoring tools"
    assert len(pin["M-1"]["inputs"]) == 9


def test_footnote_marks_do_not_bleed_into_values(pin):
    text = " ".join(p for t in pin.values() for f in nist_pin.FIELDS for p in t[f])

    assert "108" not in text and "tool94" not in text
    assert pin["R-1"]["primary"][-1] == "Senior Agency Official for Privacy"
    assert "updated plans of action and milestones" in pin["M-4"]["outputs"]


def test_a_footnote_body_at_the_foot_of_a_page_is_skipped(pin):
    assert not any("independent evaluation" in p for t in pin.values()
                   for f in nist_pin.FIELDS for p in t[f])


@pytest.mark.parametrize("value, expected", [
    ("New – Development/Acquisition; Implementation/Assessment. Existing – Operations/Maintenance.",
     {"new": ["Development/Acquisition", "Implementation/Assessment"],
      "existing": ["Operations/Maintenance"]}),
    ("SDLC phase: New – Implementation/Assessment; Existing – Operations/Maintenance.",
     {"new": ["Implementation/Assessment"], "existing": ["Operations/Maintenance"]}),
    ("New – Not Applicable. Existing – Disposal.",
     {"new": ["Not Applicable"], "existing": ["Disposal"]}),
])
def test_the_document_and_the_citation_notes_parse_alike(value, expected):
    assert nist_pin.sdlc(value) == expected


def test_a_missing_block_is_an_error_not_a_short_pin():
    with pytest.raises(nist_pin.PinError, match="no task block"):
        nist_pin.parse("### TASK P-1\n\nPotential Inputs: x.\n")


def test_a_block_without_a_required_field_is_an_error():
    text = "\n".join(f"### TASK {t}\n\nPotential Inputs: x.\n\nExpected Outputs: y.\n\n"
                     "Primary Responsibility: z.\n" for t in TASKS_80037 if t != "M-7")
    text += "\n### TASK M-7\n\nPotential Inputs: x.\n"

    with pytest.raises(nist_pin.PinError, match="TASK M-7 has no outputs, primary"):
        nist_pin.parse(text)
