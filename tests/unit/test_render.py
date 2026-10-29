"""`rmf render [--check]` (AC-9..AC-11): MANUAL.md and docs/manual/PH-*.md are a
deterministic render of framework/, and FW-MAN-001 fails on any drift.

Regenerate the mini golden after an intended template change with
``RMF_UPDATE_GOLDEN=1 uv run pytest tests/unit/test_render.py``.
"""

import os
import posixpath
import re
import shutil

import pytest
from _framework_fixtures import MINI, REAL
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import ci
from rmf_tool.cli import app
from rmf_tool.framework.load import load
from rmf_tool.profiles import Profile
from rmf_tool.render import manual

GOLDEN = REPO_ROOT / "tests" / "golden"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "repo_neg" / "FW-MAN-001"
TASK_PARTS = ("**Purpose.**", "**Stakeholders (RACI)**", "**Inputs**", "**Outputs**",
              "**Entry criteria**", "**Exit criteria**", "**Alignment**", "**Citations**",
              "**Playbook:**", "**Cross-references:**")
LINK = re.compile(r"\]\(([^)\s]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
runner = CliRunner()


def golden_path(rel: str):
    return GOLDEN / ("MANUAL.mini.md" if rel == manual.MANUAL_MD
                     else f"manual-mini/{rel.removeprefix(manual.PHASE_DIR + '/')}")


def mini_repo(tmp_path, *, with_manual: bool = False):
    """A repository root whose framework/ is the mini framework."""
    root = tmp_path / "repo"
    if with_manual:
        shutil.copytree(FIXTURE, root)
    shutil.copytree(MINI, root / "framework")
    shutil.copytree(REAL / "schema", root / "framework" / "schema")
    (root / "references").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_ROOT / "references" / "index.yaml", root / "references")
    shutil.copytree(REPO_ROOT / "references" / "schema", root / "references" / "schema")
    (root / ".git").mkdir()
    return root


def section(text: str, anchor: str) -> str:
    """The text from an anchored heading to the next heading of the same or higher level."""
    start = text.index(f'<a id="{anchor}"></a>')
    line_start = text.rindex("\n", 0, start) + 1
    level = len(text[line_start:start]) - len(text[line_start:start].lstrip("#"))
    end = re.search(rf"^#{{1,{level}}} ", text[start:], re.M)
    return text[start:start + end.start()] if end else text[start:]


def test_render_mini_golden():
    out = manual.render(MINI, REPO_ROOT)
    if os.environ.get("RMF_UPDATE_GOLDEN"):
        shutil.rmtree(GOLDEN / "manual-mini", ignore_errors=True)
        for rel, text in out.items():
            golden_path(rel).parent.mkdir(parents=True, exist_ok=True)
            golden_path(rel).write_bytes(text.encode("utf-8"))
    assert sorted(out) == ["MANUAL.md", "docs/manual/PH-EMD.md", "docs/manual/PH-MSA.md"]
    for rel, text in out.items():
        assert golden_path(rel).read_bytes() == text.encode("utf-8"), rel
    assert sorted(p.name for p in (GOLDEN / "manual-mini").iterdir()) == [
        "PH-EMD.md", "PH-MSA.md"]


def test_render_real_twice_identical():
    first = manual.render(REAL, REPO_ROOT)
    assert first == manual.render(REAL, REPO_ROOT)
    phases = load(REAL, REPO_ROOT).framework.of("phases")
    assert set(first) == {"MANUAL.md", *(f"docs/manual/{p.id}.md" for p in phases)}
    for text in first.values():
        assert text.endswith("\n") and not text.endswith("\n\n")
        assert "\r" not in text and not re.search(r"[ \t]+$", text, re.M)


def test_manual_task_sections_complete():
    """AC-10: every phase and task section shows purpose, RACI, inputs, outputs, entry and
    exit criteria, alignment, citations and its playbook, in MANUAL.md and its phase file."""
    fw = load(REAL, REPO_ROOT).framework
    out = manual.render(REAL, REPO_ROOT)
    text = out[manual.MANUAL_MD]
    for p in fw.of("phases"):
        for doc in (text, out[f"docs/manual/{p.id}.md"]):
            body = section(doc, manual.anchor("phases", p.id))
            assert manual.text(p.data["purpose"]) in body, p.id
            assert "**Entry criteria**" in body and "**Exit criteria**" in body, p.id
            for c in [*p.data["entry_criteria"], *p.data["exit_criteria"]]:
                assert manual.text(c) in body, p.id
    for e in fw.of("tasks"):
        t = e.data
        for doc in (text, out[f"docs/manual/{t['primary_phase']}.md"]):
            body = section(doc, manual.anchor("tasks", e.id))
            for part in TASK_PARTS:
                assert part in body, (e.id, part)
            assert manual.text(t["purpose"]) in body, e.id
            raci = t["raci"]
            for pid in [*raci["R"], raci["A"], *raci.get("C", []), *raci.get("I", [])]:
                assert f"{pid}.md" in body, (e.id, pid)
            for ident in [*t["inputs"], *t["outputs"]]:
                assert f"[{ident}](" in body, (e.id, ident)
            for c in [*t["entry_criteria"], *t["exit_criteria"]]:
                assert manual.text(c) in body, e.id
            for ident in [*t["aligned_with"]["milestones"], *t["aligned_with"]["reviews"],
                          *t["aligned_with"]["decisions"]]:
                assert manual.anchor("x", ident) in body, (e.id, ident)
            for c in t["citations"]:
                assert manual.anchor("refs", c["ref"]) in body, (e.id, c["ref"])
            assert t["playbook"].split("#")[0].split("/")[-1] in body, e.id


def test_manual_banner():
    text = manual.render(REAL, REPO_ROOT)[manual.MANUAL_MD]
    head = text[:1500]
    assert head.startswith("# DoD Risk Management Framework")
    assert "**Generated file. Do not edit.**" in head and "`uv run rmf render`" in head
    assert "FW-MAN-001" in head and "Draft guidance, not policy." in head
    assert "Warning: CUI and LLM endpoints." in section(text, "how-to-read")
    titles = re.findall(r'^## <a id="[^"]+"></a>(\d+)\. ', text, re.M)
    assert titles == [str(n) for n in range(1, 10)]  # parts 2-10 of the plan's outline
    for doc, body in manual.render(REAL, REPO_ROOT).items():
        if doc != manual.MANUAL_MD:
            assert body.startswith("<!-- Generated by `uv run rmf render`"), doc


@pytest.mark.parametrize("fw", [MINI, REAL], ids=["mini", "real"])
def test_internal_links_resolve(fw):
    """Every link between the generated documents lands on an anchor that exists."""
    out = manual.render(fw, REPO_ROOT)
    anchors = {doc: set(ANCHOR.findall(text)) | {"how-to-read"} for doc, text in out.items()}
    checked = 0
    for doc, text in out.items():
        for target in LINK.findall(text):
            path, _, frag = target.partition("#")
            if "://" in target or not frag:
                continue
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(doc), path)) if path \
                else doc
            if dest.startswith(("playbooks/", "personas/")):
                continue  # into a playbook or persona card, outside the manual
            assert frag in anchors[dest], (doc, target)
            checked += 1
    assert checked > 50


def test_mermaid_flowchart_chains_phases():
    text = manual.render(MINI, REPO_ROOT)[manual.MANUAL_MD]
    chart = text.split("```mermaid\n", 1)[1].split("```", 1)[0]
    assert chart.splitlines()[0] == "flowchart LR"
    assert "PH_MSA --> MS_A" in chart and "MS_A --> PH_EMD" in chart
    assert 'R_4{"R-4 Authorization Decision"}' in chart and "R_4 --> AD_DATO" in chart


def test_render_check_detects_stale(tmp_path):
    root = mini_repo(tmp_path, with_manual=True)
    findings = manual.check(root)
    by_path = {f.path: f.message for f in findings}
    assert all(f.rule == "FW-MAN-001" and f.severity == "E" for f in findings)
    assert by_path.keys() == {"MANUAL.md", "docs/manual/PH-MSA.md", "docs/manual/PH-EMD.md",
                              "docs/manual/PH-OLD.md"}
    assert by_path["MANUAL.md"].startswith("stale")
    assert by_path["docs/manual/PH-EMD.md"].startswith("missing")
    assert by_path["docs/manual/PH-OLD.md"].startswith("no such phase")


def test_write_fixes_everything_and_is_idempotent(tmp_path):
    root = mini_repo(tmp_path, with_manual=True)
    written, removed = manual.write(root)
    assert written == ["MANUAL.md", "docs/manual/PH-MSA.md", "docs/manual/PH-EMD.md"]
    assert removed == ["docs/manual/PH-OLD.md"]
    assert manual.check(root) == []
    assert manual.write(root) == ([], [])
    (root / "MANUAL.md").write_bytes((root / "MANUAL.md").read_bytes() + b"\n")
    assert [f.path for f in manual.check(root)] == ["MANUAL.md"]  # byte-identical, not trimmed


def test_unrenderable_framework(tmp_path):
    root = mini_repo(tmp_path)
    (root / "framework" / "phases.yaml").write_text("phases: [{id: PH-MSA}]\n")
    with pytest.raises(manual.RenderError) as exc:
        manual.render(root / "framework", root)
    assert all(f.rule == "FW-SCHEMA-001" for f in exc.value.findings)
    [finding] = manual.check(root)
    assert finding.rule == "FW-MAN-001" and finding.message.startswith("cannot render")


def test_cli_render_and_check(tmp_path, monkeypatch):
    root = mini_repo(tmp_path, with_manual=True)
    monkeypatch.chdir(root)

    stale = runner.invoke(app, ["render", "--check", "--format", "json"])
    assert stale.exit_code == 1 and '"rule": "FW-MAN-001"' in stale.stdout
    wrote = runner.invoke(app, ["render"])
    assert wrote.exit_code == 0
    assert "removed docs/manual/PH-OLD.md" in wrote.stdout
    assert "rmf render: 4 file(s) changed" in wrote.stdout
    clean = runner.invoke(app, ["render", "--check"])
    assert clean.exit_code == 0 and "FW-MAN-001: 0 error(s)" in clean.stdout
    assert "rmf render: 0 file(s) changed" in runner.invoke(app, ["render"]).stdout

    (root / "references" / "index.yaml").write_text("references: [\n")
    assert runner.invoke(app, ["render"]).exit_code == 2
    (root / "references" / "index.yaml").unlink()
    (root / "framework" / "phases.yaml").write_text("phases: [{id: PH-MSA}]\n")
    assert runner.invoke(app, ["render"]).exit_code == 1


def test_ci_p4_step(tmp_path):
    step = next(s for s in ci.STEPS if s.phase == "p4")
    assert step.rules == ("FW-MAN-001",)
    p4 = Profile("p4", frozenset({"p1", "p4"}))
    root = mini_repo(tmp_path, with_manual=True)

    [result] = ci.run(p4, ci.Context(root, None, slow=False, capture=True), (step,))
    assert not result.ok and len(result.findings) == 4

    manual.write(root)
    [result] = ci.run(p4, ci.Context(root, None, slow=False, capture=True), (step,))
    assert result.ok and result.findings == []
    assert ci.run(Profile("p3a", frozenset({"p1", "p3a"})), ci.Context(
        root, None, slow=False, capture=True), (step,)) == []
