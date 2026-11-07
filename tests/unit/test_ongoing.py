"""OAUTH-001, OMP-001 and OMP-002 on what the sources permit, beside what the negative fixtures
refuse: the AO's own call for a review, an existing system entering at monitoring under a
current authorization, and a reauthorization with every input on or before it."""
from pathlib import Path

from conftest import REPO_ROOT, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import ongoing
from rmf_tool.run.model import open_run

FILE = "artifacts/data/authorizations.yaml"


def _check(run_dir: Path, rule) -> str:
    return " | ".join(f.finding.message for f in rule(Context(open_run(run_dir, REPO_ROOT))))


def _review(**fields) -> dict:
    return {"id": "AUTH-003", "decision": "AD-CONT", "subject": "system", "basis": "time-driven",
            "decided_by": "PER-AO", "task": "M-6", "date": "2026-12-15",
            "risk_level": "moderate", "risk_acceptance": "I accept the residual risk.",
            "signature": "pki", "conveyed_to": ["PER-PM"], "underlying": "AUTH-002",
            "review": {"frequency_days": 30, "events": ["significant change"]},
            "ongoing_acknowledgment": "I accept the ongoing process.",
            "rationale": "Monitoring supports it.", "sources": ["INT-012.A1"], **fields}


def _add(run_dir: Path, *records: dict) -> None:
    edit_yaml(run_dir / FILE, lambda d: d["records"].extend(records))


def test_the_ao_may_call_a_review_on_an_event_no_one_defined(minimal_run):
    trigger = {"event": "press report of a breach", "raised_by": "PER-AO", "date": "2027-01-04"}
    _add(minimal_run, _review(),
         _review(id="AUTH-004", basis="event-driven", date="2027-01-05", trigger=trigger))
    assert _check(minimal_run, ongoing.review_events) == ""
    trigger["raised_by"] = "automated-tool"
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].update(trigger=trigger))
    assert "is not one of the defined trigger events" in _check(minimal_run,
                                                                ongoing.review_events)


def test_time_driven_reviews_on_their_frequency_pass_beside_event_reviews(minimal_run):
    trigger = {"event": "significant change", "raised_by": "PER-ISSM", "date": "2027-01-09"}
    _add(minimal_run, _review(),
         _review(id="AUTH-004", basis="event-driven", date="2027-01-10", trigger=trigger),
         _review(id="AUTH-005", date="2027-01-14"))
    assert _check(minimal_run, ongoing.review_events) == ""


def _enter_at_monitoring(run_dir: Path, **entry) -> None:
    def edit(d):
        d["scope"] = {"tasks": ["M-1", "M-2", "M-6"]}
        d["seeded"] = [*d.get("seeded", []),
                       {"artifact": "ART-AUTHREC", "from_task": "A-2", "path": FILE}]
        d["entry"] = {"step": "M", "task": "M-1", "current_state": "In operation.",
                      "completed": [*(f"P-{i}" for i in range(1, 19)),
                                    "C-2", "S-1", "S-2", "I-1", "A-2", "R-4"],
                      "gaps": "None found.", "decision": "Enter at M-1.",
                      "notified": ["PER-ISSM"], "approved_by": "PER-AO", **entry}
    edit_yaml(run_dir / "run.yaml", edit)


def test_an_existing_system_under_a_current_authorization_enters_at_monitoring(minimal_run):
    _enter_at_monitoring(minimal_run, deficiencies=[])
    assert _check(minimal_run, ongoing.existing_entry) == ""
    edit_yaml(minimal_run / FILE, lambda d: d["records"].append(
        {**_review(), "id": "AUTH-003", "decision": "AD-RESC", "task": "R-4",
         "revocation_reason": "incident"}))
    assert "needs a current authorization in effect" in _check(minimal_run,
                                                               ongoing.existing_entry)


def test_an_entry_before_assessment_is_not_an_existing_system_entry(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("entry", {
        "step": "S", "task": "S-1", "completed": []}))
    assert _check(minimal_run, ongoing.existing_entry) == ""


def test_a_reauthorization_with_every_input_on_or_before_it_passes(minimal_run):
    inputs = [{"by": p, "date": "2026-11-20"} for p in ("PER-CISO", "PER-PRIV", "PER-RE")]
    edit_yaml(minimal_run / FILE, lambda d: d["records"][1].update(
        basis="reauthorization", supersedes="AUTH-001", initiation_inputs=inputs))
    assert _check(minimal_run, ongoing.reauthorization_inputs) == ""
