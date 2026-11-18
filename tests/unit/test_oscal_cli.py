"""OSCAL-003: NIST oscal-cli constraint validation, optional. A stand-in ``oscal-cli`` writes the
SARIF log the real one writes, so the tests need neither Java nor the download."""

import json
import os
import stat
import sys
from pathlib import Path

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run
from typer.testing import CliRunner

from rmf_tool.check.context import Context
from rmf_tool.check.rules import generated
from rmf_tool.cli import app
from rmf_tool.oscal import oscal_cli
from rmf_tool.run.model import open_run

runner = CliRunner()
GOLDEN = REPO_ROOT / "tests/golden/oscal"

# Two breaches of one oscal-cli rule and one of another, plus a pass oscal-cli may include.
SARIF = {"runs": [{"results": [
    {"kind": "fail", "level": "error", "ruleId": "oscal-index-metadata-role-id",
     "message": {"text": "Key reference [admin] not found in index 'index-metadata-role-id'"}},
    {"kind": "fail", "level": "error", "ruleId": "oscal-index-metadata-role-id",
     "message": {"text": "Key reference [operator] not found in index 'index-metadata-role-id'"}},
    {"kind": "fail", "level": "error", "ruleId": "oscal-inventory-item-prop-name-values",
     "message": {"text": "Value 'vendor-name' doesn't match one of 'asset-id, asset-tag'"}},
    {"kind": "pass", "ruleId": "oscal-unique-property-in-context-location",
     "message": {"text": "ok"}},
]}]}


def fake_oscal_cli(tmp_path: Path, sarif: dict | None = SARIF, code: int = 1,
                   stderr: str = "") -> Path:
    """An executable that answers ``validate ... -o FILE DOC`` like oscal-cli: it writes
    ``sarif`` to FILE (when given), logs each DOC it was asked about, and exits ``code``."""
    log = tmp_path / "oscal-cli.log"
    script = tmp_path / "oscal-cli"
    script.write_text(
        f"#!{sys.executable}\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        f"open({str(log)!r}, 'a').write(args[-1] + '\\n')\n"
        f"sarif = {None if sarif is None else json.dumps(sarif)!r}\n"
        "if sarif is not None:\n"
        "    open(args[args.index('-o') + 1], 'w').write(sarif)\n"
        f"sys.stderr.write({stderr!r})\n"
        f"sys.exit({code})\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def test_oscal_003_reports_constraint_failures(tmp_path, monkeypatch):
    """`rmf check` with RMF_OSCAL_CLI set: one warning per oscal-cli rule per document, the
    profile left out (validating it would fetch the remote catalog)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    monkeypatch.setenv(oscal_cli.ENV, str(fake_oscal_cli(tmp_path)))
    found = generated.oscal_cli_constraints(Context(open_run(run_dir, REPO_ROOT)))
    docs = sorted(p.name for p in (run_dir / "oscal").glob("*.json") if p.name != "profile.json")
    assert docs and {f.finding.path for f in found} == {f"oscal/{d}" for d in docs}
    assert {f.finding.severity for f in found} == {"W"} and {f.rule for f in found} == {
        "OSCAL-003"}
    ssp = sorted(f.finding.message for f in found if f.finding.path == "oscal/ssp.json")
    assert ssp == [
        "oscal-cli oscal-index-metadata-role-id: Key reference [admin] not found in index "
        "'index-metadata-role-id' (and 1 more like it)",
        "oscal-cli oscal-inventory-item-prop-name-values: Value 'vendor-name' doesn't match "
        "one of 'asset-id, asset-tag'"]
    asked = (tmp_path / "oscal-cli.log").read_text().split()
    assert not any(a.endswith("profile.json") for a in asked)


def test_rmf_check_runs_oscal_003_only_on_opt_in(tmp_path, monkeypatch):
    run = open_run(copy_run(VALID_MINIMAL, tmp_path / "run"), REPO_ROOT)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    fake_oscal_cli(tmp_path)  # on PATH, but rmf check does not look there
    monkeypatch.delenv(oscal_cli.ENV)
    assert generated.oscal_cli_constraints(Context(run)) == []
    monkeypatch.setenv(oscal_cli.ENV, "off")
    assert generated.oscal_cli_constraints(Context(run)) == []
    monkeypatch.setenv(oscal_cli.ENV, str(tmp_path / "missing"))
    [f] = generated.oscal_cli_constraints(Context(run))
    assert f.finding.severity == "W" and "is not an executable" in f.finding.message


def test_rmf_oscal_validate_finds_oscal_cli_on_path(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.delenv(oscal_cli.ENV)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    fake_oscal_cli(tmp_path)
    result = runner.invoke(app, ["oscal", "validate", str(GOLDEN), "--format", "json"])
    assert result.exit_code == 0, result.output  # warnings only
    summary = json.loads(result.output)["summary"]
    assert "OSCAL-003" in summary["rules_run"]
    assert summary["errors"] == 0 and summary["warnings"] == 8
    skipped = runner.invoke(app, ["oscal", "validate", str(GOLDEN), "--no-oscal-cli",
                                  "--format", "json"])
    assert json.loads(skipped.output)["summary"]["warnings"] == 0


def test_rmf_oscal_validate_says_when_oscal_cli_is_skipped(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    result = runner.invoke(app, ["oscal", "validate", str(GOLDEN)])
    assert result.exit_code == 0 and "RMF_OSCAL_CLI=off: OSCAL-003 skipped" in result.output


@pytest.mark.parametrize(("sarif", "code", "stderr", "expected"), [
    ({"runs": [{"results": []}]}, 0, "", []),
    (None, 0, "", []),
    (None, 2, "Picked up JAVA_TOOL_OPTIONS: x\n\x1b[31mjava.lang.Error: boom\x1b[m\n",
     ["oscal-cli exited 2: java.lang.Error: boom"]),
])
def test_oscal_cli_outcomes(tmp_path, sarif, code, stderr, expected):
    exe = fake_oscal_cli(tmp_path, sarif, code, stderr)
    assert oscal_cli.problems(str(exe), GOLDEN / "poam.json") == expected


def test_locate_prefers_env_then_path_then_bootstrapped_copy(tmp_path, monkeypatch):
    monkeypatch.delenv(oscal_cli.ENV)
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    assert oscal_cli.locate(root=tmp_path).path is None
    boot = tmp_path / oscal_cli.BOOTSTRAPPED
    boot.parent.mkdir(parents=True)
    fake_oscal_cli(boot.parent)
    assert oscal_cli.locate(root=tmp_path).path == str(boot)
    assert oscal_cli.locate(path_lookup=False, root=tmp_path).path is None
    monkeypatch.setenv(oscal_cli.ENV, str(boot))
    assert oscal_cli.locate(path_lookup=False).path == str(boot)
