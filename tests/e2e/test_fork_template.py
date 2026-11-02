"""The template forks cleanly (plan §4.3): a local clone without examples/ and with its own
README.md, a new workspace, and `rmf ci --profile fork` exits 0."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT

pytestmark = pytest.mark.slow


def _fork_ci(tmp_path: Path, *flags: str) -> None:
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    fork = tmp_path / "fork"
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}
    subprocess.run(["git", "clone", "--quiet", "--local", str(REPO_ROOT), str(fork)],
                   check=True, env=env)
    # The clone holds the committed tree; LFS PDFs are not needed by the fork profile's
    # offline checks beyond what the clone's pointers and texts provide, so reuse the files.
    pdf = REPO_ROOT / "references/pdf"
    if pdf.is_dir():
        shutil.rmtree(fork / "references/pdf", ignore_errors=True)
        shutil.copytree(pdf, fork / "references/pdf")
    shutil.rmtree(fork / "examples")
    (fork / "README.md").write_text("# Acme\n", encoding="utf-8")
    uv = ["uv", "run", "--project", str(fork)]
    run = subprocess.run([*uv, "rmf", "new", "acme", "--dir", "."], cwd=fork,
                         capture_output=True, text=True, env=env)
    assert run.returncode == 0, run.stdout + run.stderr
    ci = subprocess.run([*uv, "rmf", "ci", "--profile", "fork", *flags], cwd=fork,
                        capture_output=True, text=True, env=env)
    failed = "\n".join(line for line in ci.stdout.splitlines() if line.startswith("FAILED"))
    assert ci.returncode == 0, failed + "\n" + ci.stdout[-4000:] + ci.stderr[-2000:]


def test_fork_without_examples_passes_fork_checks(tmp_path):
    _fork_ci(tmp_path, "--no-tests")


@pytest.mark.release
def test_fork_without_examples_passes_its_test_suite(tmp_path):
    """The whole suite again, in the clone: half of a CI run, so only `rmf ci --release`."""
    _fork_ci(tmp_path)
