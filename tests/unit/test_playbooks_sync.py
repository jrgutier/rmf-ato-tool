"""`rmf playbooks sync`: headers and generated bodies from framework/, authored bodies
preserved; FW-PB-001 (coverage) and FW-PB-002 (stale or incomplete playbooks)."""

import shutil

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool import playbooks_sync
from rmf_tool.framework.load import load

SECTIONS = "".join(f"\n## {s}\n\nText.\n" for s in playbooks_sync.SECTIONS)
BODY = f"{playbooks_sync.AUTHORED}\n{SECTIONS}"
NEG = REPO_ROOT / "tests/fixtures/repo_neg"


def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "playbooks/P").mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "framework", root / "framework")
    (root / "templates").mkdir()
    shutil.copy(REPO_ROOT / playbooks_sync.BODY_TEMPLATE, root / playbooks_sync.BODY_TEMPLATE)
    return root


def at(findings, path):
    return [f for f in findings if f.path == path]


def test_header_generated_from_yaml(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(f"{playbooks_sync.BEGIN}\n{playbooks_sync.END}\n{BODY}")
    assert "playbooks/P/P-10.md" in playbooks_sync.sync(root)
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
    assert at(playbooks_sync.check(root), "playbooks/P/P-11.md") == []


def test_check_flags_edit_inside_markers(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(BODY)
    assert [f.message for f in at(playbooks_sync.check(root), "playbooks/P/P-10.md")] == [
        "header missing; run `rmf playbooks sync`"]
    playbooks_sync.sync(root)
    path.write_text(path.read_text().replace("| Minimum interviews | 1 |",
                                             "| Minimum interviews | 0 |"))
    findings = at(playbooks_sync.check(root), "playbooks/P/P-10.md")
    assert [(f.rule, f.path) for f in findings] == [("FW-PB-002", "playbooks/P/P-10.md")]


def test_generated_body_rendered_when_body_generated(tmp_path):
    root = repo(tmp_path)
    rel = "playbooks/S/S-5.md"
    assert [f.rule for f in at(playbooks_sync.check(root), rel)] == ["FW-PB-001"]
    assert rel in playbooks_sync.sync(root)  # a missing playbook is created, generated
    text = (root / rel).read_text()
    head, _, body = text.partition(f"\n{playbooks_sync.GENERATED}\n")
    assert head.startswith(playbooks_sync.BEGIN) and "# S-5 · " in head
    assert playbooks_sync._missing_sections(body, 2) == []
    for needle in ("`artifacts/data/conmon.yaml`", "templates/artifacts/ART-CONMON.md",
                   "uv run rmf check <run> --task S-5", "| PER-ISSM (",
                   'uv run rmf refs show SP800-37R2 --section "TASK S-5"'):
        assert needle in body
    assert at(playbooks_sync.check(root), rel) == []

    (root / rel).write_text(text.replace("## Steps", "## Steps\n\nHand edit."))
    assert [f.message for f in at(playbooks_sync.check(root), rel)] == [
        "generated playbook stale or edited by hand; run `rmf playbooks sync`"]
    assert playbooks_sync.sync(root) == [rel] and (root / rel).read_text() == text


def test_generated_bodies_cover_special_tasks(tmp_path):
    """A generated output (R-1, ART-PKG) and a task without outputs (A-1) still render
    followable bodies."""
    root = repo(tmp_path)
    fw = load(root / "framework", root).framework
    tasks = {e.id: e.data for e in fw.of("tasks")}
    r1 = playbooks_sync.body(fw, tasks["R-1"], root)
    assert "uv run rmf package <run>" in r1 and "No interview is required." in r1
    a1 = playbooks_sync.body(fw, tasks["A-1"], root)
    assert "A-1 has no artifact output" in a1 and "DECISION" in a1


def org_context(tasks):
    sections = SECTIONS.replace("\n## ", "\n### ")
    return ("# Org context\n\n" + playbooks_sync.AUTHORED + "\n"
            + "".join(f"\n## Task {t}\n{sections}" for t in tasks))


def test_org_context_playbook_has_section_per_task(tmp_path):
    root = repo(tmp_path)
    rel = "playbooks/P/P-org-context.md"
    path = root / rel
    path.write_text(org_context([f"P-{n}" for n in range(1, 8)]))
    playbooks_sync.sync(root)
    text = path.read_text()
    for n in range(1, 8):
        begin, end = playbooks_sync._markers(f"P-{n}")
        assert text.index(f"## Task P-{n}\n{begin}\n") < text.index(end)
    assert "**P-3 · Risk Assessment—Organization**" in text
    assert at(playbooks_sync.check(root), rel) == []
    assert playbooks_sync.sync(root) == []

    path.write_text(org_context(["P-1", "P-2", "P-4", "P-5", "P-6", "P-7"]))
    assert [f.message for f in at(playbooks_sync.check(root), rel) if f.rule == "FW-PB-001"
            ] == ["P-3: playbooks/P/P-org-context.md has no section #task-p-3 (## Task P-3)"]


def test_repo_org_context_anchors_resolve():
    text = (REPO_ROOT / "playbooks/P/P-org-context.md").read_text(encoding="utf-8")
    fw = load(REPO_ROOT / "framework", REPO_ROOT).framework
    anchors = [e.data["playbook"].partition("#")[2] for e in fw.of("tasks")
               if e.data["playbook"].startswith("playbooks/P/P-org-context.md#")]
    assert anchors == [f"task-p-{n}" for n in range(1, 8)]
    assert all(playbooks_sync._section(text, a) is not None for a in anchors)


def test_repo_has_a_playbook_for_every_task():
    assert [f for f in playbooks_sync.check(REPO_ROOT) if f.rule == "FW-PB-001"] == []


def test_authored_body_needs_every_section(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(BODY.replace("\n## Done when\n", "\n## Done\n"))
    playbooks_sync.sync(root)
    assert [f.message for f in at(playbooks_sync.check(root), "playbooks/P/P-10.md")] == [
        "P-10: authored body lacks or misorders ## Done when"]


def test_unmarked_file_reported_and_left_alone(tmp_path):
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text("# not yet authored\n")
    playbooks_sync.sync(root)
    assert path.read_text() == "# not yet authored\n"
    [finding] = at(playbooks_sync.check(root), "playbooks/P/P-10.md")
    assert finding.rule == "FW-PB-002" and finding.message.startswith("P-10: no body marker")


def compose(overlay, tmp_path):
    """A synced copy of the repo's playbooks with the fixture overlay applied."""
    root = repo(tmp_path)
    shutil.rmtree(root / "playbooks")
    shutil.copytree(REPO_ROOT / "playbooks", root / "playbooks")
    playbooks_sync.sync(root)
    expect = YAML(typ="safe").load((overlay / "expect.yaml").read_text(encoding="utf-8"))
    for rel in expect["delete"]:
        (root / rel).unlink()
    for src in (overlay / "playbooks").rglob("*.md"):
        shutil.copy(src, root / src.relative_to(overlay))
    return root, expect


@pytest.mark.parametrize("rule", ["FW-PB-001", "FW-PB-002"])
def test_negative_fixture(rule, tmp_path):
    root, expect = compose(NEG / rule, tmp_path)
    findings = playbooks_sync.check(root)
    assert {f.rule for f in findings} == {expect["rule"], *expect["also"]}
    rendered = [f.render() for f in findings if f.rule == rule]
    for message in expect["messages"]:
        assert any(message in r for r in rendered), (message, rendered)


def test_marker_must_stand_on_its_own_line(tmp_path):
    """An authored body that quotes the generated marker is still authored."""
    root = repo(tmp_path)
    path = root / "playbooks/P/P-10.md"
    path.write_text(BODY + f"\nUpgrade by replacing `{playbooks_sync.GENERATED}`.\n")
    playbooks_sync.sync(root)
    assert path.read_text().endswith(f"`{playbooks_sync.GENERATED}`.\n")
    assert at(playbooks_sync.check(root), "playbooks/P/P-10.md") == []
