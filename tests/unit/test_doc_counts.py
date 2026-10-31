import re
import shutil

import pytest
from conftest import REPO_ROOT

from rmf_tool import doc_counts


@pytest.fixture
def tree(tmp_path):
    """A repo whose framework and references are the real ones and whose three documents
    are copies the test may change."""
    for name in ("framework", "references"):
        (tmp_path / name).symlink_to(REPO_ROOT / name, target_is_directory=True)
    for rel in ("README.md", "AGENTS.md", doc_counts.REGISTRY_REL):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((REPO_ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def edit(root, rel, pattern, repl):
    path = root / rel
    text, n = re.subn(pattern, repl, path.read_text(encoding="utf-8"), count=1)
    assert n == 1, pattern
    path.write_text(text, encoding="utf-8")


def test_the_repository_states_each_count_and_they_are_right():
    """README.md is the fork's to rewrite, so only upstream-owned files must state counts."""
    for statement in doc_counts.STATEMENTS:
        if statement.file == "README.md":
            continue
        text = (REPO_ROOT / statement.file).read_text(encoding="utf-8")
        assert statement.pattern.search(text), f"{statement.file}: {statement.pattern.pattern}"
    assert doc_counts.check(REPO_ROOT) == []


@pytest.mark.parametrize(("rel", "pattern", "repl", "expected"), [
    (doc_counts.REGISTRY_REL, r"(\d+) rules,", "999 rules,", "states 999 rules; computed"),
    (doc_counts.REGISTRY_REL, r"(\d+) repo-scope", "1 repo-scope", "states 1 repo rules"),
    (doc_counts.REGISTRY_REL, r"(\d+) run-scope", "2 run-scope", "states 2 run rules"),
    ("AGENTS.md", r"\d+ tasks", "46 tasks", "states 46 tasks; computed 47"),
    ("AGENTS.md", r"\d+ personas", "5 personas", "states 5 personas"),
    ("README.md", r"[Tt]he \d+ reference PDFs", "The 31 reference PDFs", "states 31 PDFs"),
    ("README.md", r"\d+ NIST documents", "3 NIST documents", "states 3 NIST PDFs"),
    ("README.md", r"\d+ DoD and\s+CNSS documents", "9 DoD and CNSS documents",
     "states 9 DoD and CNSS PDFs"),
])
def test_stale_counts_are_reported(tree, rel, pattern, repl, expected):
    assert doc_counts.check(tree) == []
    edit(tree, rel, pattern, repl)

    found = doc_counts.check(tree)

    assert [f.rule for f in found] == ["DOC-002"]
    assert expected in found[0].message and found[0].path == rel and found[0].line


def test_an_absent_statement_or_file_is_not_a_finding(tree):
    (tree / "README.md").unlink()
    edit(tree, "AGENTS.md", r"\d+ tasks", "all tasks")

    assert doc_counts.check(tree) == []


def test_a_pending_acquisition_reference_is_not_a_committed_pdf(tree):
    (tree / "references").unlink()
    shutil.copytree(REPO_ROOT / "references", tree / "references",
                    ignore=shutil.ignore_patterns("pdf", "text", "_inbox"))
    index = tree / "references/index.yaml"
    text = index.read_text(encoding="utf-8")
    index.write_text(re.sub(r"(?m)^(    status: )ok$", r"\1pending-acquisition", text, count=1),
                     encoding="utf-8")

    found = doc_counts.check(tree)

    assert [f.message for f in found if "PDFs" in f.message]
    assert any("states 32 PDFs; computed 31" in f.message for f in found)


def test_an_unreadable_index_is_a_finding_not_a_traceback(tree):
    (tree / "references").unlink()
    (tree / "references").mkdir()

    found = doc_counts.check(tree)

    assert found and {f.rule for f in found} == {"DOC-002"}
    assert all("cannot compute" in f.message and "index" in f.message for f in found)


def test_an_unreadable_framework_is_a_finding_not_zero(tree):
    (tree / "framework").unlink()
    (tree / "framework").mkdir()

    found = doc_counts.check(tree)

    assert {f.message.split(" to check")[0] for f in found} == {
        "cannot compute tasks", "cannot compute personas"}
    assert not any("computed 0" in f.message for f in found)
