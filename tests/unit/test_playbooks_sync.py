"""`rmf playbooks sync`: headers generated from framework/, authored bodies preserved."""

import shutil

from conftest import REPO_ROOT

from rmf_tool import playbooks_sync

BODY = "<!-- rmf:body authored -->\n\n## Steps\n\n1. Do the work.\n"


def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "playbooks/P").mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "framework", root / "framework")
    return root


def test_header_generated_from_yaml(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(f"{playbooks_sync.BEGIN}\n{playbooks_sync.END}\n{BODY}")
    assert playbooks_sync.sync(root) == ["playbooks/P/P-10.md"]
    text = path.read_text()
    assert "# P-10 · Asset Identification" in text
    assert "| Outputs | ART-INV (produces) |" in text
    assert "[PER-PM](../../personas/PER-PM.md)" in text
    assert text.endswith(BODY)


def test_authored_body_preserved_and_sync_idempotent(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-11.md"
    path.write_text(BODY)  # no header yet: sync prepends it
    playbooks_sync.sync(root)
    first = path.read_text()
    assert first.startswith(playbooks_sync.BEGIN) and first.endswith(BODY)
    assert playbooks_sync.sync(root) == [] and path.read_text() == first
    assert playbooks_sync.check(root) == []


def test_check_flags_edit_inside_markers(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(BODY)
    assert [f.message for f in playbooks_sync.check(root)] == [
        "header missing; run `rmf playbooks sync`"]
    playbooks_sync.sync(root)
    path.write_text(path.read_text().replace("| Minimum interviews | 1 |",
                                             "| Minimum interviews | 0 |"))
    findings = playbooks_sync.check(root)
    assert [(f.rule, f.path) for f in findings] == [("FW-PB-002", "playbooks/P/P-10.md")]


def test_generated_or_unmarked_files_are_skipped(tmp_path):
    root = repo(tmp_path)
    (root / "playbooks/P/P-10.md").write_text("# not yet authored\n")
    assert playbooks_sync.sync(root) == [] and playbooks_sync.check(root) == []
