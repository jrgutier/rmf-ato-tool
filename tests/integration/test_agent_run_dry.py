"""`scripts/agent-run.sh --dry-run skeleton` (plan §4.2, marker `agent`: the dry run makes one
isolation-probe model call under the user's Claude Code login)."""

import subprocess

import pytest
from conftest import REPO_ROOT

pytestmark = pytest.mark.agent

FORBIDDEN = ("--permission-mode", "--max-turns", "bypassPermissions",
             "--dangerously-skip-permissions", "--no-sync")


def test_agent_run_dry():
    proc = subprocess.run([str(REPO_ROOT / "scripts/agent-run.sh"), "--dry-run", "skeleton"],
                          cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    argv = next(line for line in proc.stdout.splitlines() if line.startswith("claude argv:"))
    for needed in ("--setting-sources project", "--strict-mcp-config",
                   "--no-session-persistence", "--disable-slash-commands", "--max-budget-usd",
                   "--allowedTools Bash\\(uv\\ run\\ rmf:\\*\\) Read Edit Write Glob Grep"):
        assert needed in argv, needed
    for bad in FORBIDDEN:
        assert bad not in argv, bad
    assert "UV_NO_SYNC=1" in proc.stdout
    assert "isolation probe: ok" in proc.stdout
