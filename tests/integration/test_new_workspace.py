"""`rmf new` -> `rmf run init --mode hybrid` -> `rmf status` names P-1 next (plan §4.2)."""

import json

from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool.cli import app

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
    assert "next: P-1 Risk Management Roles" in result.stdout
    assert result.stdout.startswith("now: 20")
    data = json.loads(runner.invoke(app, ["status", "runs/hybrid-run", "--format", "json"]).stdout)
    assert data["mode"] == "hybrid" and data["next"]["task"] == "P-1" and not data["done"]
    assert runner.invoke(app, ["new", "demo", "--dir", str(ws)]).exit_code == 2
    assert runner.invoke(app, ["run", "init", "--mode", "manual"]).exit_code == 2
