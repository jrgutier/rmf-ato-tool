"""tests/golden/oscal holds the four OSCAL documents of valid_minimal (plan §5 Phase 6).

Regenerate after a fixture change: ``uv run rmf build tests/fixtures/runs/valid_minimal``, then
copy its ``oscal/{ssp,assessment-plan,assessment-results,poam}.json`` here.
"""

from conftest import REPO_ROOT, VALID_MINIMAL
from typer.testing import CliRunner

from rmf_tool import build
from rmf_tool.cli import app
from rmf_tool.run.model import open_run

GOLDEN = REPO_ROOT / "tests/golden/oscal"
runner = CliRunner()


def test_golden_is_a_fresh_build_of_valid_minimal():
    files = build.oscal_outputs(open_run(VALID_MINIMAL, REPO_ROOT)).files
    golden = sorted(p.name for p in GOLDEN.glob("*.json"))
    assert golden == ["assessment-plan.json", "assessment-results.json", "poam.json", "ssp.json"]
    for name in golden:
        assert files[f"oscal/{name}"] == (GOLDEN / name).read_text(), name


def test_oscal_validate_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(REPO_ROOT)
    result = runner.invoke(app, ["oscal", "validate", str(GOLDEN), "--format", "json"])
    assert result.exit_code == 0, result.output
    assert '"errors": 0' in result.output
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "poam.json").write_text((GOLDEN / "poam.json").read_text().replace(
        '"oscal-version": "1.2.1"', '"oscal-version": 121'))
    result = runner.invoke(app, ["oscal", "validate", str(bad)])
    assert result.exit_code == 1 and "OSCAL-001" in result.output
    assert runner.invoke(app, ["oscal", "validate", str(tmp_path)]).exit_code == 2
