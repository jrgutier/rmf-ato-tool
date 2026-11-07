"""inputs_since and outputs_since: a run is held to an input or output from the contract that
added it, so a task done under an older contract stays done (L-0065)."""

from __future__ import annotations

import shutil
from pathlib import Path

from rmf_tool.run import status
from rmf_tool.run.model import open_run

REPO = Path(__file__).resolve().parents[2]
MINIMAL = REPO / "tests/fixtures/runs/valid_minimal"


def _at(tmp_path: Path, contract: str) -> Path:
    run = tmp_path / "run"
    shutil.copytree(MINIMAL, run)
    config = run / "run.yaml"
    text = config.read_text(encoding="utf-8")
    config.write_text(text.replace("framework_version: 0.2.0", f"framework_version: {contract}"),
                      encoding="utf-8")
    return run


def test_current_contract_holds_the_added_outputs_and_inputs():
    run = open_run(MINIMAL, REPO)
    assert "ART-REG" in run.tasks["R-5"]["outputs"]
    assert "ART-SSP" in run.tasks["M-1"]["outputs"]
    assert "ART-ORG-CONTEXT" in run.tasks["C-2"]["inputs"]


def test_older_contract_reads_tasks_without_them(tmp_path):
    run = open_run(_at(tmp_path, "0.1.0"), REPO)
    assert "ART-REG" not in run.tasks["R-5"]["outputs"]
    assert "ART-AUTHRPT" in run.tasks["R-5"]["outputs"]
    assert "ART-SSP" not in run.tasks["M-1"]["outputs"]
    assert "ART-ORG-CONTEXT" not in run.tasks["C-2"]["inputs"]


def test_an_added_output_does_not_reopen_a_task_of_an_older_run(tmp_path):
    path = _at(tmp_path, "0.1.0")
    reg = path / "artifacts/ART-REG.md"
    reg.write_text(reg.read_text(encoding="utf-8").replace(
        "touched_by: [P-18, C-1, C-3, R-5]", "touched_by: [P-18]"), encoding="utf-8")
    run = open_run(path, REPO)
    assert not any("ART-REG" in p for p in status._artifact_problems(run, "R-5"))


def test_an_added_output_reopens_the_task_of_a_current_run(tmp_path):
    path = tmp_path / "run"
    shutil.copytree(MINIMAL, path)
    reg = path / "artifacts/ART-REG.md"
    reg.write_text(reg.read_text(encoding="utf-8").replace(
        "touched_by: [P-18, C-1, C-3, R-5]", "touched_by: [P-18, C-1, C-3]"), encoding="utf-8")
    run = open_run(path, REPO)
    assert "ART-REG touched_by does not list R-5" in status._artifact_problems(run, "R-5")
