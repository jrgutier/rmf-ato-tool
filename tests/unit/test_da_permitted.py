"""DASH-001 allows what the source allows: a periodic dashboard is "as near real time as
feasible" when the run records why nearer is not feasible (DoD CIO cATO evaluation p. 11)."""

from conftest import REPO_ROOT
from test_check_rules import apply, base_copy

from rmf_tool.check import engine
from rmf_tool.run.model import open_run


def _dash(tmp_path, mutations):
    run_dir = base_copy("minimal", tmp_path / "minimal")
    for m in mutations:
        apply(run_dir, m)
    run = open_run(run_dir, REPO_ROOT)
    found = engine.select(run, engine.evaluate(run), final=True)
    return [f for f in found if f.rule == "DASH-001"]


def test_periodic_with_a_feasibility_limit_passes(tmp_path):
    file = "artifacts/data/cato.yaml"
    assert _dash(tmp_path, [
        {"op": "set_field", "file": file, "path": "dashboard.refresh", "value": "periodic"},
        {"op": "set_field", "file": file, "path": "dashboard.feasibility_limit",
         "value": {"reason": "The enclave's scanner can export results only once a day.",
                   "sources": ["INT-028.A2"]}},
    ]) == []


def test_periodic_without_one_fails(tmp_path):
    file = "artifacts/data/cato.yaml"
    assert _dash(tmp_path, [
        {"op": "set_field", "file": file, "path": "dashboard.refresh", "value": "periodic"}])


def test_space_assumption_considered_and_kept_out_passes(tmp_path):
    """Fable F2: a failed Space vulnerability assumption whose controls were "revisited and
    considered for inclusion" and kept out (outcome revisited-no-change) is no TLR-003 error."""
    from ruamel.yaml import YAML

    spec = YAML(typ="safe").load(
        (REPO_ROOT / "tests/fixtures/negative/TLR-003.space.yaml").read_text(encoding="utf-8"))
    for m in spec["mutations"]:
        if m.get("path") == "assumptions":
            for a in m["value"]:
                if a["id"] == "AS-SPC-3":
                    a["outcome"] = "revisited-no-change"
    run_dir = base_copy("minimal", tmp_path / "minimal")
    for m in spec["mutations"]:
        apply(run_dir, m)
    run = open_run(run_dir, REPO_ROOT)
    found = engine.select(run, engine.evaluate(run), final=True)
    assert not [f for f in found if f.rule == "TLR-003"]


def test_space_on_hhh_has_no_baseline_warning(tmp_path):
    """SPCOV-003 is quiet when the system is categorized at the H/H/H baseline it tailors."""
    run_dir = base_copy("minimal", tmp_path / "minimal")
    for path, value in (("categorization.overlays", ["CNSSI1253F-ATT2-SPACE"]),
                        ("categorization.c", "high"), ("categorization.i", "high"),
                        ("categorization.a", "high")):
        apply(run_dir, {"op": "set_field", "file": "facts.yaml", "path": path, "value": value})
    run = open_run(run_dir, REPO_ROOT)
    found = engine.select(run, engine.evaluate(run), final=True)
    assert not [f for f in found if f.rule == "SPCOV-003"]
