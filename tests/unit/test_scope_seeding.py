"""Seeding (plan §7.3): every artifact an active task needs from an inactive producer is
seeded with an existing file (RUN-CFG-001); --final stays scope-aware (RUN-ART-001)."""

from conftest import REPO_ROOT, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run import scope
from rmf_tool.run.model import open_run


def final_findings(run_dir, rule):
    run = open_run(run_dir, REPO_ROOT)
    return [f for f in engine.select(run, engine.evaluate(run), final=True) if f.rule == rule]


def drop_seed(run_dir, artifact):
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__(
        "seeded", [s for s in d["seeded"] if s["artifact"] != artifact]))


def test_unseeded_input_from_out_of_scope_producer_fails_run_cfg(minimal_run):
    drop_seed(minimal_run, "ART-REQ")
    messages = [f.message for f in final_findings(minimal_run, "RUN-CFG-001")]
    assert any(m.startswith("C-1 needs ART-REQ (input)") for m in messages)
    assert any(m.startswith("S-1 needs ART-REQ (input)") for m in messages)


def test_unseeded_updated_output_from_out_of_scope_producer_fails_run_cfg(minimal_run):
    drop_seed(minimal_run, "ART-RA")
    needs = scope.seed_needs(open_run(minimal_run, REPO_ROOT))
    assert any(n.task == "R-2" and n.artifact == "ART-RA" and n.kind == "updated output"
               for n in needs)
    assert any("R-2 needs ART-RA (updated output)" in f.message
               for f in final_findings(minimal_run, "RUN-CFG-001"))


def test_seed_file_missing_fails(minimal_run):
    (minimal_run / "artifacts/data/stig-summary.yaml").unlink()
    assert any("seed file artifacts/data/stig-summary.yaml" in f.message
               for f in final_findings(minimal_run, "RUN-CFG-001"))


def test_seed_from_wrong_or_active_task(minimal_run):
    def edit(d):
        d["seeded"] += [{"artifact": "ART-STAKE", "from_task": "P-1",
                         "path": "artifacts/ART-STAKE.md"},
                        {"artifact": "ART-INV", "from_task": "P-10",
                         "path": "artifacts/ART-INV.md"},
                        {"artifact": "ART-NOPE", "from_task": "P-1", "path": "x.md"}]
    edit_yaml(minimal_run / "run.yaml", edit)
    messages = " | ".join(f.message for f in final_findings(minimal_run, "RUN-CFG-001"))
    assert "neither produces nor updates it" in messages
    assert "which is in scope" in messages
    assert "not a framework artifact" in messages


def test_generated_artifacts_need_no_seed():
    from conftest import VALID_MINIMAL

    needs = scope.seed_needs(open_run(VALID_MINIMAL, REPO_ROOT))
    assert needs and all(n.artifact != "ART-PKG" for n in needs)


def test_final_is_scope_aware(minimal_run):
    """ART-CONMON (core, producer S-5 out of scope, not seeded) is not required."""
    assert final_findings(minimal_run, "RUN-ART-001") == []
    edit_yaml(minimal_run / "run.yaml", lambda d: d["scope"]["tasks"].append("S-5"))
    messages = [f.message for f in final_findings(minimal_run, "RUN-ART-001")]
    assert "core artifact ART-CONMON missing" in messages
