"""`rmf validate` and the p3a `rmf ci` step: exit codes, profiles, --stats JSON, --root."""

import json
import re
import shutil

import pytest
from _framework_fixtures import MINI, NEG, P3A, compose
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import ci
from rmf_tool.check import load_registry
from rmf_tool.cli import app
from rmf_tool.framework.validate import CHECKED_ELSEWHERE
from rmf_tool.profiles import Profile

runner = CliRunner()


@pytest.fixture(autouse=True)
def at_repo(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    # `--profile p3a` means closed ∪ {p3a}; pin "closed" to the phases before p3a so these
    # tests check exactly the p3a rules, however many .phases/*.closed markers the repo has.
    monkeypatch.setattr("rmf_tool.profiles.closed_phases",
                        lambda root: frozenset({"p1", "p2", "p2x"}))


def invoke(*args):
    return runner.invoke(app, list(args))


def test_help():
    result = invoke("validate", "--help")
    # Typer forces a terminal under GITHUB_ACTIONS, so CI output carries ANSI codes.
    assert result.exit_code == 0 and "--stats" in re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)


def test_real_framework_stats_json():
    result = invoke("validate", "--profile", "p3a", "--stats", "--format", "json")
    data = json.loads(result.stdout)

    assert result.exit_code == 0
    assert (data["tasks"], data["phases"], data["decisions"]) == (47, 5, 5)
    assert data["personas"] >= 15
    assert data["summary"]["errors"] == 0
    assert data["summary"]["deferred_citations"] == data["deferred_citations"] == 0
    assert data["summary"]["rules_run"][0] == "FW-SCHEMA-001"


def test_text_output_and_stats():
    result = invoke("validate", "--profile", "p3a", "--stats", "--root", str(MINI))
    assert result.exit_code == 0
    assert "tasks: 5" in result.stdout
    assert "12 rule(s), 0 error(s)" in result.stdout


def test_violation_exits_1_and_reports_finding(tmp_path):
    fw = compose(NEG / "FW-DAG-001", tmp_path / "fw")

    text = invoke("validate", "--profile", "p3a", "--root", str(fw))
    as_json = json.loads(invoke("validate", "--profile", "p3a", "--root", str(fw),
                                "--format", "json").stdout)

    assert text.exit_code == 1
    assert "FW-DAG-001" in text.output and "C-1 -> P-11 -> C-3 -> C-2 -> C-1" in text.output
    assert as_json["summary"]["errors"] == 1 and "tasks" not in as_json
    assert as_json["findings"][0]["rule"] == "FW-DAG-001"


def test_closed_profile_without_framework_phase_runs_nothing(tmp_path, monkeypatch):
    shutil.copytree(REPO_ROOT / "framework", tmp_path / "framework")
    shutil.copytree(REPO_ROOT / "references" / "schema", tmp_path / "references" / "schema")
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)

    result = invoke("validate")

    assert result.exit_code == 0
    assert "no framework rules are active" in result.stdout


@pytest.mark.parametrize("args, needle", [
    (["--profile", "p99"], "unknown profile"),
    (["--profile", "p3a", "--root", "no/such/dir"], "framework directory not found"),
])
def test_usage_errors_exit_2(args, needle):
    result = invoke("validate", *args)
    assert result.exit_code == 2
    assert needle in result.output


def test_unimplemented_active_rule_exit_2(monkeypatch):
    """An active FW-* rule this version does not implement stops validate (no vacuous
    pass); simulated by dropping one rule, so it holds whichever phases are finished."""
    from rmf_tool.framework import validate as validate_mod

    monkeypatch.setattr(validate_mod, "IMPLEMENTED",
                        tuple(r for r in validate_mod.IMPLEMENTED if r != "FW-TASK-001"))
    result = invoke("validate", "--profile", "p3a")
    assert result.exit_code == 2
    assert "not implemented in this version: FW-TASK-001" in result.output


def test_bad_index_is_usage_error(tmp_path, monkeypatch):
    shutil.copytree(MINI, tmp_path / "framework")
    shutil.copytree(REPO_ROOT / "framework" / "schema", tmp_path / "framework" / "schema")
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)

    result = invoke("validate", "--profile", "p3a")

    assert result.exit_code == 2 and "references/index.yaml" in result.output


def test_ci_p3a_step_runs_validate():
    step = next(s for s in ci.STEPS if s.phase == "p3a")
    ctx = ci.Context(REPO_ROOT, None, slow=False, capture=True)

    [result] = ci.run(P3A, ctx, (step,))

    assert result.ok and result.name == "rmf validate"
    fw_rules = {r.id for r in load_registry() if r.id.startswith("FW-")}
    assert result.rules[0] == "FW-SCHEMA-001"
    assert set(result.rules) == fw_rules - set(CHECKED_ELSEWHERE)
    assert ci.run(Profile("p2", frozenset({"p1", "p2"})), ctx, (step,)) == []


def test_ci_p3a_step_reports_bad_index(tmp_path):
    shutil.copytree(REPO_ROOT / "framework", tmp_path / "framework")
    step = next(s for s in ci.STEPS if s.phase == "p3a")

    [result] = ci.run(P3A, ci.Context(tmp_path, None, slow=False, capture=True), (step,))

    assert not result.ok and result.findings[0].rule == "FW-CITE-001"
