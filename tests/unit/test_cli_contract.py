import json
import shutil

import pytest
from conftest import REPO_ROOT, doc, entry
from typer.testing import CliRunner

from rmf_tool import __version__, ci, doctor
from rmf_tool.cli import app

runner = CliRunner()


def invoke(*args):
    return runner.invoke(app, list(args))


def test_version():
    result = invoke("--version")
    assert result.exit_code == 0
    assert result.stdout.strip() == f"rmf {__version__}"


@pytest.mark.parametrize("cmd", [
    [], ["doctor"], ["ci"], ["lessons"], ["lessons", "check"], ["refs"],
    *(["refs", c] for c in ("fetch", "import", "verify", "extract", "index", "sync", "show")),
])
def test_help(cmd):
    result = invoke(*cmd, "--help")
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_usage_errors_exit_2():
    assert invoke("no-such-command").exit_code == 2
    assert invoke("doctor", "--format", "yaml").exit_code == 2


def test_bare_rmf_shows_help():
    result = invoke()
    assert result.exit_code == 2
    assert "Usage" in result.output


def test_doctor_json(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    real_which = shutil.which
    monkeypatch.setattr(doctor.shutil, "which", lambda n: real_which(n) if n != "qpdf" else None)

    result = invoke("doctor", "--format", "json")
    data = json.loads(result.stdout)

    assert result.exit_code == 1
    assert data["ok"] is False
    qpdf = next(c for c in data["checks"] if c["name"] == "qpdf")
    assert (qpdf["ok"], qpdf["required"]) == (False, True)


def test_doctor_text_ok(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    monkeypatch.setattr(doctor, "run_checks", lambda root: [
        doctor.Check("python", True, True, "3.12"),
        doctor.Check("pymupdf", False, False, "not installed"),
    ])

    result = invoke("doctor")

    assert result.exit_code == 0
    assert "absent (optional)" in result.stdout


def test_lessons_check_json(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.root)
    git_repo.write("docs/LESSONS.md", doc(entry(1)))

    result = invoke("lessons", "check", "--format", "json")
    data = json.loads(result.stdout)

    assert result.exit_code == 0
    assert data["summary"] == {"errors": 0, "warnings": 1, "rules_run": ["LES-002", "LES-003"]}


def test_lessons_check_pending_exits_1(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.root)
    git_repo.write("docs/LESSONS.md", doc(entry(1, promotion="pending")))

    result = invoke("lessons", "check")

    assert result.exit_code == 1
    assert "LES-003" in result.output


@pytest.fixture
def repo_with_p1(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.root)
    git_repo.write("docs/LESSONS.md", doc(entry(1)))
    git_repo.write("AGENTS.md", (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    calls = []

    def fake_subprocess(argv, ctx):
        calls.append(argv)
        return True, [], "ok output" if ctx.capture else ""

    monkeypatch.setattr(ci, "run_subprocess", fake_subprocess)
    git_repo.calls = calls
    return git_repo


def test_ci_profile_p1_json(repo_with_p1):
    result = invoke("ci", "--profile", "p1", "--format", "json")
    data = json.loads(result.stdout)

    assert result.exit_code == 0
    assert (data["profile"], data["phases"], data["ok"]) == ("p1", ["p1"], True)
    assert [s["name"] for s in data["steps"]] == ["lessons check", "AGENTS.md", "ruff", "pytest"]
    assert data["steps"][0]["rules"] == ["LES-002", "LES-003"]
    pytest_argv = repo_with_p1.calls[1]
    assert "not slow and not network and not agent" in pytest_argv
    assert f"--cov-fail-under={ci.COVERAGE_MIN}" in pytest_argv


def test_ci_bare_runs_fast_lane_only_without_closed_phases(repo_with_p1):
    result = invoke("ci", "--slow")

    assert result.exit_code == 0
    assert "phases: none closed" in result.stdout
    assert "lessons check" not in result.stdout
    assert "not network and not agent" in repo_with_p1.calls[1]


def test_ci_reports_failures_exit_1(repo_with_p1):
    repo_with_p1.write("docs/LESSONS.md", doc(entry(2)))
    (repo_with_p1.root / ".phases").mkdir()
    (repo_with_p1.root / ".phases" / "p1.closed").write_text("closed\n")

    result = invoke("ci")

    assert result.exit_code == 1
    assert "FAIL  lessons check (LES-002, LES-003)" in result.stdout
    assert "PASS  AGENTS.md (DOC-001)" in result.stdout


@pytest.mark.parametrize("args", [
    ["--profile", "bogus"],
    ["--profile", "p3a"],  # phase checks not implemented yet
    ["--release"],
    ["--release", "--profile", "p1"],
])
def test_ci_usage_errors(repo_with_p1, args):
    result = invoke("ci", *args)
    assert result.exit_code == 2
    assert repo_with_p1.calls == []
