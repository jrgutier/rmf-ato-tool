"""docs/CHECKS.md is generated from registry.yaml and kept fresh (`rmf checks-doc --check`)."""

from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import checks_doc
from rmf_tool.check import load_registry
from rmf_tool.cli import app

runner = CliRunner()


def test_committed_checks_md_is_fresh():
    assert not checks_doc.stale(REPO_ROOT)


def test_every_rule_listed_once_and_render_is_deterministic():
    text = checks_doc.render()
    assert text == checks_doc.render()
    for rule in load_registry():
        assert text.count(f"\n| {rule.id} |") == 1, rule.id
    rules = load_registry()
    counts = {scope: sum(r.scope == scope for r in rules) for scope in ("repo", "run")}
    assert (f"{len(rules)} rules: {counts['repo']} repository-scope, "
            f"{counts['run']} run-scope.") in text
    assert "W for pending-acquisition before p2x" in text  # severity notes survive


def test_check_flags_a_stale_file_and_write_fixes_it(tmp_path, monkeypatch):
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: tmp_path)
    result = runner.invoke(app, ["checks-doc", "--check"])
    assert result.exit_code == 1 and "stale" in result.output
    assert "written" in runner.invoke(app, ["checks-doc"]).output
    assert (tmp_path / checks_doc.CHECKS_PATH).read_text() == checks_doc.render()
    assert runner.invoke(app, ["checks-doc", "--check"]).exit_code == 0
    assert "unchanged" in runner.invoke(app, ["checks-doc"]).output
