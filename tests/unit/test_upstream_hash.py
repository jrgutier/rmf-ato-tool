"""upstream_hash (plan §4.4): sha256 over sorted POSIX paths, each `path\\0bytes\\0`."""

import hashlib
import subprocess

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.run import upstream_hash


def tree(root):
    (root / "framework/tasks").mkdir(parents=True)
    (root / "framework/meta.yaml").write_text("a: 1\n")
    (root / "framework/tasks/P.yaml").write_text("tasks: []\n")
    (root / "AGENTS.md").write_text("# Agents\n")
    (root / "framework/.DS_Store").write_text("junk")
    (root / "other.txt").write_text("unrelated\n")
    return root


def test_hash_algorithm_sorted_paths_nul_separated(tmp_path):
    root = tree(tmp_path)
    expected = hashlib.sha256(
        b"AGENTS.md\0# Agents\n\0"
        b"framework/meta.yaml\0a: 1\n\0"
        b"framework/tasks/P.yaml\0tasks: []\n\0"
    ).hexdigest()
    assert upstream_hash.compute(root, ["framework/**", "AGENTS.md"]) == expected
    assert upstream_hash.expand(root, ["framework/**", "AGENTS.md", "AGENTS.md"]) == [
        "AGENTS.md", "framework/meta.yaml", "framework/tasks/P.yaml"]


def test_hash_scoped_to_scenario_globs(tmp_path):
    root = tree(tmp_path)
    before = upstream_hash.compute(root, ["framework/tasks/*.yaml"])
    (root / "framework/meta.yaml").write_text("a: 2\n")
    assert upstream_hash.compute(root, ["framework/tasks/*.yaml"]) == before
    (root / "framework/tasks/P.yaml").write_text("tasks: [x]\n")
    assert upstream_hash.compute(root, ["framework/tasks/*.yaml"]) != before


def test_unrelated_file_change_does_not_change_scenario_hash(tmp_path):
    root = tree(tmp_path)
    globs = list(upstream_hash.UNION_GLOBS)
    before = upstream_hash.compute(root, globs)
    (root / "other.txt").write_text("changed\n")
    (root / "framework/.DS_Store").write_text("changed")
    assert upstream_hash.compute(root, globs) == before


def test_python_caches_cannot_enter_the_hash(tmp_path):
    package = tmp_path / "src/pkg"
    (package / "__pycache__").mkdir(parents=True)
    (package / "m.py").write_text("x = 1\n")
    (package / "data.yaml").write_text("a: 1\n")
    (package / "__pycache__/m.cpython-312.pyc").write_bytes(b"\x00one")
    globs = list(upstream_hash.UNION_GLOBS)
    before = upstream_hash.compute(tmp_path, globs)

    assert upstream_hash.expand(tmp_path, globs) == ["src/pkg/data.yaml", "src/pkg/m.py"]
    (package / "__pycache__/m.cpython-312.pyc").write_bytes(b"\x00two")
    assert upstream_hash.compute(tmp_path, globs) == before
    (package / "m.py").write_text("x = 2\n")
    assert upstream_hash.compute(tmp_path, globs) != before
    # why SRC_GLOBS name suffixes: a bare src/** would pick the cache up
    assert "src/pkg/__pycache__/m.cpython-312.pyc" in upstream_hash.expand(tmp_path, ["src/**"])


def test_every_scenario_hashes_the_tool_sources():
    scenarios = sorted((REPO_ROOT / "tests/agent/scenarios").glob("*.yaml"))
    assert scenarios
    for path in scenarios:
        globs = YAML(typ="safe").load(path.read_text(encoding="utf-8"))["hash_globs"]
        assert set(upstream_hash.SRC_GLOBS) <= set(globs), path.name


def test_every_tracked_source_file_is_hashed():
    """A new file suffix under src/ must be added to SRC_GLOBS (or deliberately excluded
    here), or edits to it would not make a run stale."""
    unhashed_on_purpose: set[str] = set()
    listed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-co", "--exclude-standard", "src"],
        capture_output=True, text=True, check=False)
    if listed.returncode != 0:
        pytest.skip("not a git checkout")
    hashed = set(upstream_hash.expand(REPO_ROOT, upstream_hash.SRC_GLOBS))
    files = {f for f in listed.stdout.split() if (REPO_ROOT / f).is_file()}
    missed = files - hashed - unhashed_on_purpose
    assert missed == set()
