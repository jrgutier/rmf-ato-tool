"""Generated run reports (plan §4.5): check.{json,md}, status.md, metrics.json and the
assumptions report; all deterministic."""

import json

import jsonschema
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import reports
from rmf_tool.cli import app
from rmf_tool.run.model import open_run
from rmf_tool.run.status import compute

runner = CliRunner()


def test_check_writes_reports_with_the_plan_shape(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    result = runner.invoke(app, ["check", str(minimal_run), "--final", "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert set(data["summary"]) == {"errors", "warnings", "rules_run", "degraded",
                                    "deferred_citations"}
    assert data["summary"]["errors"] == 0 and data["summary"]["degraded"] == []
    assert len(data["summary"]["rules_run"]) >= 44
    written = (minimal_run / reports.CHECK_JSON).read_bytes()
    assert json.loads(written) == data
    md = (minimal_run / reports.CHECK_MD).read_text()
    rules_run = len(data["summary"]["rules_run"])
    assert f"Selection: --final. Errors: 0. Warnings: 0. Rules run: {rules_run}." in md
    assert "No findings." in md
    runner.invoke(app, ["check", str(minimal_run), "--final", "--format", "json"])
    assert (minimal_run / reports.CHECK_JSON).read_bytes() == written  # deterministic


def test_check_markdown_lists_findings(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    (minimal_run / "artifacts/data/conmon.yaml").write_text(
        (minimal_run / "artifacts/data/conmon.yaml").read_text().replace(
            "  - {family: si,", "  - {family: xx,"))
    result = runner.invoke(app, ["check", str(minimal_run), "--rules", "CONMON-001",
                                 "--task", "S-5"])
    assert result.exit_code == 1
    md = (minimal_run / reports.CHECK_MD).read_text()
    assert "Selection: --task S-5, --rules CONMON-001." in md
    assert "| E | CONMON-001 | artifacts/data/conmon.yaml | baseline family si has no " in md


def test_status_writes_status_and_metrics(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    assert runner.invoke(app, ["status", str(minimal_run)]).exit_code == 0
    metrics = json.loads((minimal_run / reports.METRICS_JSON).read_text())
    jsonschema.Draft202012Validator(reports.METRICS_SCHEMA).validate(metrics)
    assert metrics["done"] is True
    assert metrics["tasks"] == {"active": 39, "done": 39, "deferred": 1, "lifecycle": 7,
                                "out_of_scope": 0}
    assert metrics["coverage"]["ssp_pct"] == 100.0
    assert metrics["answers"]["simulated_pct"] == 100.0
    assert metrics["journal"]["retries"] == 1
    status = (minimal_run / reports.STATUS_MD).read_text()
    assert "Next: none, every active task is done" in status
    assert "| P-6 | Impact-Level Prioritization | deferred | no | not-applicable:" in status


def test_hybrid_metrics_and_next_action(hybrid_run):
    (hybrid_run / "artifacts/ART-AODM.md").unlink()
    run = open_run(hybrid_run, REPO_ROOT)
    st = compute(run)
    metrics = reports.write_status(run, st)
    jsonschema.Draft202012Validator(reports.METRICS_SCHEMA).validate(metrics)
    assert metrics["mode"] == "hybrid" and metrics["done"] is False
    assert metrics["answers"]["human"] == 4 and metrics["assumptions"] == 2
    assert 0 < metrics["answers"]["simulated_pct"] < 100
    assert metrics["tasks"]["out_of_scope"] == 35
    assert "Next: R-4 Authorization Decision." in (hybrid_run / reports.STATUS_MD).read_text()


def test_report_assumptions_command(hybrid_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    path = hybrid_run / reports.ASSUMPTIONS_REPORT
    path.unlink()
    result = runner.invoke(app, ["report", "assumptions", str(hybrid_run)])
    assert result.exit_code == 0 and "written" in result.output
    text = path.read_text()
    assert "| ASM-002 | P-11 | PER-ISSM |" in text and "PER-ISSM (Dana Reyes (fixture))" in text
    assert "unchanged" in runner.invoke(app, ["report", "assumptions",
                                              str(hybrid_run)]).output


def test_deferred_citations_counts_pending_references(minimal_run, monkeypatch):
    from rmf_tool import refs

    real = refs.load_index

    def pending(root):
        index = real(root)
        for r in index["references"]:
            if r["id"] == "SP800-37R2":
                r["status"] = "pending-acquisition"
        return index

    run = open_run(minimal_run, REPO_ROOT)
    assert reports.deferred_citations(run) == 0
    monkeypatch.setattr(refs, "load_index", pending)
    assert reports.deferred_citations(run) > 47  # at least every TASK citation

    def broken(root):
        raise refs.IndexFileError("unreadable")

    monkeypatch.setattr(refs, "load_index", broken)
    assert reports.deferred_citations(run) == 0
