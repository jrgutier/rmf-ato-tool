"""`rmf build` (plan §7.5): assemble + OSCAL + assumptions report (+ package refresh)."""

import subprocess

from conftest import REPO_ROOT, edit_yaml

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.run.model import open_run


def tree_state(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_build_runs_assemble_oscal_and_assumptions(minimal_run):
    for rel in ("oscal/ssp.json", "oscal/profile.json", "reports/assumptions.md"):
        (minimal_run / rel).unlink()
    md = minimal_run / "artifacts/ART-SD.md"
    md.write_text(md.read_text().replace("| Acronym | FDR | C-1 |\n", ""))
    changed, notes = build.build(open_run(minimal_run, REPO_ROOT))
    assert {"oscal/ssp.json", "oscal/profile.json", "reports/assumptions.md",
            "artifacts/ART-SD.md"} <= set(changed)
    assert notes == {}
    assert "| Acronym | FDR | C-1 |" in md.read_text()


def test_build_then_check_task_has_no_spurious_gen_stale(minimal_run):
    edit_yaml(minimal_run / "facts.yaml", lambda d: d["acronym"].__setitem__("value", "FDRX"))
    run = open_run(minimal_run, REPO_ROOT)
    before = {f.rule for f in engine.select(run, engine.evaluate(run), task="C-1")}
    assert "GEN-STALE-001" in before
    build.build(run)
    after = engine.select(run, engine.evaluate(run), task="C-1")
    assert after == []


def test_build_idempotent(minimal_run):
    run = open_run(minimal_run, REPO_ROOT)
    build.build(run)
    state = tree_state(minimal_run)
    changed, _ = build.build(run)
    assert changed == [] and tree_state(minimal_run) == state


def test_unbuildable_ssp_is_removed_with_reason(minimal_run):
    (minimal_run / "artifacts/data/users.yaml").unlink()
    changed, notes = build.build(open_run(minimal_run, REPO_ROOT))
    assert "oscal/ssp.json" in changed and not (minimal_run / "oscal/ssp.json").exists()
    assert "artifacts/data/users.yaml missing" in notes["oscal/ssp.json"]


def test_cli_build_and_package(minimal_run):
    def rmf(*args):
        return subprocess.run(["uv", "run", "rmf", *args], cwd=REPO_ROOT, capture_output=True,
                              text=True, check=False)
    proc = rmf("build", str(minimal_run))
    assert proc.returncode == 0 and "0 file(s) changed" in proc.stdout
    assert rmf("package", str(minimal_run)).stdout.strip() == "package/manifest.yaml unchanged"
