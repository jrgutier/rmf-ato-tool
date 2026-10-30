"""The committed example fork run (plan §4.3, AC-20): final check, OSCAL, generated files,
coverage and journal, on the run as committed."""

import json
import re

import pytest
from conftest import EXAMPLE_RUN, REPO_ROOT
from ruamel.yaml import YAML
from typer.testing import CliRunner

from rmf_tool.cli import app
from rmf_tool.run.model import open_run

pytestmark = pytest.mark.slow
runner = CliRunner()


def rmf(*args):
    result = runner.invoke(app, [*args])
    assert result.exit_code == 0, (args, result.output)
    return result


@pytest.fixture(autouse=True)
def _repo_cwd(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)


def test_final_check_has_no_errors():
    report = json.loads(rmf("check", str(EXAMPLE_RUN), "--final", "--format", "json").stdout)
    assert report["summary"]["errors"] == 0


def test_oscal_valid_and_generated_files_current():
    rmf("oscal", "validate", str(EXAMPLE_RUN))
    rmf("oscal", "build", str(EXAMPLE_RUN), "--check")
    rmf("assemble", str(EXAMPLE_RUN), "--check")
    for model in ("ssp", "assessment-plan", "assessment-results", "poam"):
        assert (EXAMPLE_RUN / "oscal" / f"{model}.json").is_file(), model


def test_every_core_artifact_and_report_present():
    run = open_run(EXAMPLE_RUN, REPO_ROOT)
    status = json.loads(rmf("status", str(EXAMPLE_RUN), "--format", "json").stdout)
    assert status["done"]
    produced = {a for t in status["tasks"] if t["state"] == "active"
                for a in run.tasks[t["id"]].get("outputs") or []}
    present = {p.stem for p in (EXAMPLE_RUN / "artifacts").glob("ART-*.md")}
    assert produced - {"ART-PKG"} <= present
    assert (EXAMPLE_RUN / "package/manifest.yaml").is_file()
    assert (EXAMPLE_RUN / "reports/assumptions.md").is_file()


def test_ssp_statements_cover_the_baseline():
    baseline = json.loads((EXAMPLE_RUN / "baseline.json").read_text())
    status = json.loads(rmf("status", str(EXAMPLE_RUN), "--format", "json").stdout)
    assert status["ssp"]["statements"] == len(baseline["controls"]) > 0
    assert status["sar"]["determinations"] == len(baseline["controls"])


def test_a_checkpoint_for_every_active_step():
    status = json.loads(rmf("status", str(EXAMPLE_RUN), "--format", "json").stdout)
    run = open_run(EXAMPLE_RUN, REPO_ROOT)
    steps = {t["id"][0] for t in status["tasks"] if t["state"] == "active"}
    journal = (EXAMPLE_RUN / "journal.md").read_text(encoding="utf-8")
    seen = {m.group(1)[0] for m in re.finditer(r"^## \S+ · CHECKPOINT · task (\S+)", journal,
                                               flags=re.M)}
    assert steps and steps <= seen, steps - seen
    assert YAML(typ="safe").load((EXAMPLE_RUN / "run.yaml").read_text())["mode"] == run.mode
