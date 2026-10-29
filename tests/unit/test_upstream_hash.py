"""upstream_hash (plan §4.4): sha256 over sorted POSIX paths, each `path\\0bytes\\0`."""

import hashlib

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
