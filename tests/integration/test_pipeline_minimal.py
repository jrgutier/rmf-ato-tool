"""On a copy of valid_minimal: baseline resolve -> build -> oscal validate -> package ->
check --final exits 0, and a second pass changes no file (plan §4.2)."""

import json

from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool.cli import app

runner = CliRunner()
PIPELINE = (["baseline", "resolve"], ["build"], ["oscal", "build", "--check"],
            ["oscal", "validate"], ["assemble", "--check"], ["package"],
            ["check", "--final"])


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def run_pipeline(run_dir):
    for cmd in PIPELINE:
        result = runner.invoke(app, [*cmd[:2], str(run_dir), *cmd[2:]] if cmd[0] in (
            "baseline", "oscal") else [cmd[0], str(run_dir), *cmd[1:]])
        assert result.exit_code == 0, (cmd, result.output)


def test_pipeline_minimal_and_idempotent(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    run_pipeline(minimal_run)
    state = snapshot(minimal_run)
    run_pipeline(minimal_run)
    assert snapshot(minimal_run) == state


def test_baseline_resolve_states_its_method(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    result = runner.invoke(app, ["baseline", "resolve", str(minimal_run)])
    assert result.exit_code == 0
    assert "CNSSI 1253 per-objective selection (method: cnssi1253)" in result.stdout
    assert "C=moderate, I=moderate, A=low" in result.stdout and "pending" not in result.stdout
    refused = runner.invoke(app, ["baseline", "resolve", str(minimal_run),
                                  "--method", "high-water-mark"])
    assert refused.exit_code == 1 and "categorization.method" in refused.output


def test_check_json_and_task_mode(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    (minimal_run / "artifacts/ART-CP.md").unlink()
    result = runner.invoke(app, ["check", str(minimal_run), "--final", "--format", "json"])
    data = json.loads(result.stdout)
    assert result.exit_code == 1 and data["summary"]["errors"] >= 1
    assert {f["rule"] for f in data["findings"] if f["severity"] == "E"} == {
        "GEN-STALE-001", "RUN-ART-001", "AODM-001"}
    task = runner.invoke(app, ["check", str(minimal_run), "--task", "S-4"])
    assert task.exit_code == 1 and "error RUN-ART-001" not in task.output  # gated at R-1
    assert "note: S-4 is not done yet: ART-CP missing" in task.output
    assert runner.invoke(app, ["check", str(minimal_run), "--task", "Q-1"]).exit_code == 2
    assert runner.invoke(app, ["check", str(minimal_run), "--rules", "NOPE-001"]).exit_code == 2
    assert runner.invoke(app, ["check", str(minimal_run), "--final", "--task", "S-4"]
                         ).exit_code == 2
    assert runner.invoke(app, ["oscal", "build", str(minimal_run)]).exit_code == 0
    assert runner.invoke(app, ["check", "/nonexistent-run"]).exit_code == 2


def test_resolve_refusal_and_assemble_errors(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    md = minimal_run / "artifacts/ART-SD.md"
    md.write_text(md.read_text() + "\n<!-- BEGIN rmf:bogus -->\n<!-- END rmf:bogus -->\n")
    assert runner.invoke(app, ["assemble", str(minimal_run)]).exit_code == 1
    assert runner.invoke(app, ["build", str(minimal_run)]).exit_code == 1
    facts = minimal_run / "facts.yaml"
    facts.write_text(facts.read_text().replace("value: true", "value: false"))
    result = runner.invoke(app, ["baseline", "resolve", str(minimal_run)])
    assert result.exit_code == 1 and "not approved" in result.output
