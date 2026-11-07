"""ISCM rules: the runs SP 800-37 and SP 800-137 allow pass (the negative fixtures hold the
runs they refuse)."""

from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

CONMON = "artifacts/data/conmon.yaml"


def _found(run_dir, rule, task=None):
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), task=task,
                                             final=task is None) if f.rule == rule]


def test_s5_closes_before_the_ao_approves_at_s6(tmp_path):
    """The approval can come with the plan approval at S-6 (SP 800-37r2 Task S-5), so a strategy
    not yet approved holds S-6, never S-5."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / CONMON, lambda d: d.pop("approval"))
    assert _found(run_dir, "ISCM-004", task="S-5") == []
    assert any("records no approval" in m for m in _found(run_dir, "ISCM-004", task="S-6"))


def _sc_continuous(overrides):
    def edit(d):
        sc = next(r for r in d["frequencies"] if r["family"] == "sc")
        sc["frequency"] = "continuous"
        sc["overrides"] = [{"control": c, "frequency": "monthly", "reason": "Manual review."}
                           for c in overrides]
    return edit


def test_an_override_takes_a_control_out_of_a_continuous_family(tmp_path):
    """A continuous family whose untooled controls are overridden to a manual frequency is
    covered; the control left continuous with no tool is not."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / CONMON, _sc_continuous(["sc-7", "sc-15"]))
    assert _found(run_dir, "ISCM-002") == []
    edit_yaml(run_dir / CONMON, _sc_continuous(["sc-7"]))
    assert _found(run_dir, "ISCM-002") == [
        "no automated tool assesses sc-15, so it needs a manual assessment frequency, "
        "not continuous"]


def test_a_slower_tool_beside_a_manual_method_is_allowed(tmp_path):
    """A tool assessing ac-2 annually supplements the monthly manual review; only a continuous
    minimum binds a tool's own frequency."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    tool = {"id": "TOOL-02", "name": "Directory audit", "strategy": "other", "assesses": ["ac-2"],
            "method": "test", "frequency": "annually", "analysis": "ISSO review.",
            "reporting": "Annual report to the ISSM.", "selection": "Reads the directory.",
            "upkeep": "Checked each release.", "responsible": "PER-ISSO"}
    edit_yaml(run_dir / CONMON, lambda d: d["tools"].append(tool))
    assert _found(run_dir, "ISCM-002") == []


def test_inheriting_from_a_leveraged_authorization_needs_no_delegation(tmp_path):
    """Inheriting common controls is not a delegation to an external partner."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / CONMON, lambda d: d.__setitem__(
        "delegations", [x for x in d["delegations"] if x["partner"] != "LA-01"]))
    assert _found(run_dir, "ISCM-006") == []
