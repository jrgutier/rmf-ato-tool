from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def entry(num: int, date: str = "2026-10-29", promotion: str = "check: SOME-001") -> str:
    return (
        f"## L-{num:04d} · {date} · run: planning · tags: refs, fetch\n"
        f"- Symptom: symptom {num}.\n"
        f"- Root cause: cause {num}.\n"
        f"- Fix: fix {num}.\n"
        f"- Rule: rule {num}.\n"
        f"- Promotion: {promotion}\n"
    )


def doc(*entries: str) -> str:
    return "# Lessons\n\nPreamble.\n\n" + "\n".join(entries)


class GitRepo:
    def __init__(self, root: Path) -> None:
        self.root = root

    def git(self, *args: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True
        )
        return proc.stdout.strip()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GitRepo:
    """An empty git repo isolated from the user's global/system git config."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for var in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{var}_NAME", "test")
        monkeypatch.setenv(f"GIT_{var}_EMAIL", "test@example.invalid")
    repo = GitRepo(tmp_path / "repo")
    repo.root.mkdir()
    repo.git("init", "-q", "-b", "main")
    return repo


VALID_MINIMAL = REPO_ROOT / "tests/fixtures/runs/valid_minimal"


@pytest.fixture
def minimal_run(tmp_path: Path) -> Path:
    """A writable copy of the skeleton fixture run (tests/fixtures/runs/valid_minimal)."""
    import shutil

    return Path(shutil.copytree(VALID_MINIMAL, tmp_path / "valid_minimal"))


def edit_yaml(path: Path, edit) -> None:
    """Round-trip edit of a YAML file: ``edit(data)`` mutates the loaded mapping."""
    import io

    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.width = 4096
    data = yaml.load(path.read_text(encoding="utf-8"))
    edit(data)
    buf = io.StringIO()
    yaml.dump(data, buf)
    path.write_text(buf.getvalue(), encoding="utf-8")
