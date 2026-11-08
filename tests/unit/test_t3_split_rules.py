"""Cases the sources permit that the rules split from capped rules, and the T3 rule clauses, must
not refuse: CADJ-001 a raise above the high-water mark that records its adjustment, BSEL-001 and
BSEL-002 a baseline resolved again after the categorization changes, SSPI-001 a hybrid control
the plan does not record as inherited, and INFL-001 a life cycle that starts at creation, or a run
whose scope leaves out P-13."""

from __future__ import annotations

from _mutations import apply
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.run.model import open_run

INFOTYPES = "artifacts/data/infotypes.yaml"


def _errors(run_dir, *rules: str) -> list[str]:
    run = open_run(run_dir, REPO_ROOT)
    return [f"{f.rule}: {f.finding.message}" for f in engine.evaluate(run).findings
            if f.rule in rules]


def test_a_raise_with_its_adjustment_recorded_is_not_refused(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def raise_availability(data):
        cat = data["categorization"]
        cat["a"] = "moderate"
        cat["adjustments"] = [{"objective": "a", "from": "low", "to": "moderate",
                               "factor": "critical functionality",
                               "rationale": "The relay is the only path for field reports."}]
    edit_yaml(run_dir / "facts.yaml", raise_availability)
    assert _errors(run_dir, "CADJ-001", "CATG-001") == []


def test_a_baseline_resolved_again_after_the_categorization_changes_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / INFOTYPES,
              lambda d: d["information_types"][0]["availability"].update(base="moderate"))
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["categorization"].update(a="moderate"))
    apply(run_dir, {"op": "resolve_baseline", "file": "baseline.json"})
    build.build(open_run(run_dir, REPO_ROOT))
    assert _errors(run_dir, "BSEL-001", "BSEL-002") == []


def test_a_hybrid_control_need_not_be_recorded_inherited(tmp_path):
    """SP 800-37r2 2.4: a hybrid control is partly provided at the system level, so its plan
    statement may record it implemented; only a common control is referenced as inherited."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    allocation = run_dir / "artifacts/data/allocation.yaml"
    edit_yaml(allocation, lambda d: d["allocations"][0].update(provider="Analysis enclave"))
    assert _errors(run_dir, "SSPI-001") == []


def test_a_life_cycle_that_starts_at_creation_passes(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / INFOTYPES, lambda d: d["information_types"][0].update(life_cycle=[
        {"stage": "creation", "description": "Field units create the reports."},
        {"stage": "disposition", "description": "The relay keeps no report once forwarded."}]))
    assert _errors(run_dir, "INFL-001") == []


def test_the_life_cycle_is_not_demanded_without_p13_in_scope(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / INFOTYPES, lambda d: d["information_types"][0].pop("life_cycle"))
    assert _errors(run_dir, "INFL-001")
    edit_yaml(run_dir / "run.yaml", lambda d: d["scope"].update(
        tasks=["P-1", "P-10", "P-11", "P-12", "C-1", "C-2", "C-3", "S-1", "S-4"]))
    assert _errors(run_dir, "INFL-001") == []
