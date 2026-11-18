"""`rmf new` -> `rmf run init --mode hybrid` -> `rmf status` names P-1 next (plan §4.2)."""

import json

import pytest
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.cli import app
from rmf_tool.run.model import open_run, read_yaml
from rmf_tool.workspace import init_run

runner = CliRunner()


def test_new_then_run_init_then_status(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    ws = tmp_path / "demo"
    result = runner.invoke(app, ["new", "demo", "--dir", str(ws), "--run-id", "first-run"])
    assert result.exit_code == 0, result.output
    (ws / "framework").symlink_to(REPO_ROOT / "framework")  # ws stands in for a fork
    monkeypatch.chdir(ws)
    result = runner.invoke(app, ["run", "init", "--mode", "hybrid", "--run-id", "hybrid-run"])
    assert result.exit_code == 0, result.output
    result = runner.invoke(app, ["status", "runs/hybrid-run"])
    assert result.exit_code == 0, result.output
    assert "next: Prepare 1: Risk Management Roles (P-1)" in result.stdout
    assert result.stdout.startswith("now: 20")
    data = json.loads(runner.invoke(app, ["status", "runs/hybrid-run", "--format", "json"]).stdout)
    assert data["mode"] == "hybrid" and data["next"]["task"] == "P-1" and not data["done"]
    assert runner.invoke(app, ["new", "demo", "--dir", str(ws)]).exit_code == 2
    assert runner.invoke(app, ["run", "init", "--mode", "manual"]).exit_code == 2


@pytest.mark.parametrize(("scenario", "first"), [("skeleton", "P-10"),
                                                 ("c1-s4-one-family", "C-1")])
def test_a_run_entering_past_p1_checks_clean_at_its_first_task(tmp_path, scenario, first):
    """A scenario entering past P-1 scaffolds its entry determination and the seeds the tasks
    before it hand on (ART-BIA, ART-REG), so after `rmf build` the first task reports only
    what it writes itself."""
    run_dir = init_run(tmp_path, REPO_ROOT, run_id="entry-run",
                       scenario_path=REPO_ROOT / f"tests/agent/scenarios/{scenario}.yaml")
    config = read_yaml(run_dir / "run.yaml")
    assert config["entry"]["task"] == first
    assert {"date", "deficiencies"} <= set(config["entry"])
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    ev = engine.evaluate(run)
    assert ev.status.next == first
    errors = [f for f in engine.select(run, ev, task=first) if f.severity == "E"]
    own = {(f.rule, f.finding.message) for f in ev.findings if first in f.owners}
    assert [f.message for f in errors if (f.rule, f.message) not in own] == []
