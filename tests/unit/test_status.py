"""Task completion, scope and deferral precedence (plan §7.3)."""

from conftest import REPO_ROOT, edit_yaml

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.run import scope
from rmf_tool.run.model import open_run
from rmf_tool.run.status import compute, family_gaps


def status_of(run_dir):
    return compute(open_run(run_dir, REPO_ROOT))


def test_fixture_done():
    from conftest import VALID_MINIMAL

    st = status_of(VALID_MINIMAL)
    n = len(open_run(VALID_MINIMAL, REPO_ROOT).config["control_subset"])
    assert st.done and st.next is None
    assert (st.baseline, st.statements, st.determinations) == (n, n, n)


def test_task_done_requires_outputs_touched_and_task_rules_pass(minimal_run):
    (minimal_run / "artifacts/ART-CP.md").unlink()
    st = status_of(minimal_run)
    assert not st.tasks["S-4"].done
    assert "Contingency plan (ART-CP) missing (artifacts/ART-CP.md)" in st.tasks["S-4"].missing
    assert st.next == "S-4"

    (minimal_run / "artifacts/ssp/controls/si.yaml").unlink()
    st = status_of(minimal_run)
    assert "SSP-COV-001: 1 error(s)" in st.tasks["S-4"].missing


def test_updater_task_requires_touched_by(minimal_run):
    md = minimal_run / "artifacts/ART-BND.md"
    md.write_text(md.read_text().replace("touched_by: [P-11, P-16, C-1]",
                                         "touched_by: [P-11, P-16]"))
    st = status_of(minimal_run)
    assert st.tasks["P-11"].done
    assert "ART-BND touched_by does not list C-1" in st.tasks["C-1"].missing


def test_facts_and_interviews_required(minimal_run):
    edit_yaml(minimal_run / "facts.yaml", lambda d: d.pop("boundary_id"))
    (minimal_run / "interviews/INT-001-P-10-PER-PM.md").unlink()
    st = status_of(minimal_run)
    assert "fact boundary_id not set_by P-11" in st.tasks["P-11"].missing
    assert "0/1 interview(s)" in st.tasks["P-10"].missing
    assert st.next == "P-10"


def test_next_action_topological(minimal_run):
    for rel in ("artifacts/ART-AODM.md", "artifacts/ART-SAP.md"):
        (minimal_run / rel).unlink()
    st = status_of(minimal_run)
    assert st.next == "A-2"


def test_family_refinement_for_s4(minimal_run):
    (minimal_run / "artifacts/ssp/controls/cm.yaml").unlink()
    run = open_run(minimal_run, REPO_ROOT)
    assert family_gaps(run)["cm"] == {"ssp": ["cm-6"], "sar": []}
    st = compute(run)
    assert (st.next, st.family) == ("S-4", "cm")


def test_applies_after_gates_rules(minimal_run):
    """FACTS-001 (applies_after C-3) does not block C-2; SSP-COV-001 (S-4) not S-1."""
    edit_yaml(minimal_run / "facts.yaml",
              lambda d: d["categorization"]["approved"].__setitem__("value", False))
    (minimal_run / "artifacts/ssp/controls/si.yaml").unlink()
    run = open_run(minimal_run, REPO_ROOT)
    build.build(run)
    ev = engine.evaluate(run)
    rules_c2 = {f.rule for f in engine.select(run, ev, task="C-2")}
    rules_s1 = {f.rule for f in engine.select(run, ev, task="S-1")}
    rules_s4 = {f.rule for f in engine.select(run, ev, task="S-4")}
    assert "FACTS-001" not in rules_c2 and "FACTS-001" in rules_s1
    assert "SSP-COV-001" not in rules_s1 and "SSP-COV-001" in rules_s4
    assert not ev.status.tasks["C-3"].done and ev.status.tasks["C-2"].done


def test_scope_out_of_scope_tasks_deferred():
    from conftest import HYBRID_MINIMAL, VALID_MINIMAL

    st = status_of(HYBRID_MINIMAL)
    assert st.tasks["P-1"].state == scope.OUT_OF_SCOPE and not st.tasks["P-1"].done
    assert st.tasks["P-10"].state == scope.ACTIVE
    st = status_of(VALID_MINIMAL)  # scope all, explicit P-6 deferral, lifecycle stop at R-5
    assert st.tasks["P-6"].state == scope.DEFERRED and st.tasks["M-1"].state == scope.LIFECYCLE
    assert st.done and len(st.done_tasks) == 39


def test_lifecycle_stop_vs_deferred_precedence(hybrid_run):
    def edit(d):
        d["lifecycle_stop"] = "S-4"
        d["lifecycle_stop_rationale"] = "Skeleton stops after planning."
        d["deferred"] = {"A-2": {"kind": "later-cycle", "rationale": "Assessment next cycle."}}
    edit_yaml(hybrid_run / "run.yaml", edit)
    scopes = scope.task_scopes(open_run(hybrid_run, REPO_ROOT))
    assert scopes["P-1"].state == scope.OUT_OF_SCOPE  # scope beats everything
    assert scopes["A-2"].state == scope.DEFERRED  # explicit beats lifecycle
    assert scopes["A-3"].state == scope.LIFECYCLE
    assert scopes["A-3"].rationale == "Skeleton stops after planning."
    assert scopes["S-4"].state == scope.ACTIVE


def test_include_after_stop(minimal_run):
    def edit(d):
        d["lifecycle_stop"] = "S-4"
        d["lifecycle_stop_rationale"] = "Stop after planning."
        d["include_after_stop"] = ["A-3"]
    edit_yaml(minimal_run / "run.yaml", edit)
    scopes = scope.task_scopes(open_run(minimal_run, REPO_ROOT))
    assert scopes["A-3"].state == scope.ACTIVE and scopes["A-6"].state == scope.LIFECYCLE


def test_check_without_options_follows_progress(minimal_run):
    """Before S-4 is done, the progress-gated check shows the next task's findings (S-4 is
    being worked, F-05-3) and counts the later ones it hides."""
    (minimal_run / "artifacts/ssp/controls/si.yaml").unlink()
    run = open_run(minimal_run, REPO_ROOT)
    ev = engine.evaluate(run)
    assert ev.status.next == "S-4"
    shown = engine.select(run, ev)
    assert "SSP-COV-001" in {f.rule for f in shown}
    final = engine.select(run, ev, final=True)
    assert "SSP-COV-001" in {f.rule for f in final}
    assert engine.hidden_errors(run, ev, shown) == (
        sum(f.severity == "E" for f in final) - sum(f.severity == "E" for f in shown))
    assert {f.rule for f in engine.select(run, ev, family="si", final=True)} == {"SSP-COV-001"}
    assert engine.select(run, ev, rules=["TRACE-001"], final=True) == []
