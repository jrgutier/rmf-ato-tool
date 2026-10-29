"""Trace tokens (INV-5): parsing, anchors and resolution; interview and journal parsing."""

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL

from rmf_tool.check.context import Context
from rmf_tool.check.rules.journal import ENTRY, journal
from rmf_tool.run import frontmatter, interviews, trace
from rmf_tool.run.model import open_run


def test_prose_tokens_and_generated_blocks():
    text = ("a [[INT-001.A1]] b\n<!-- BEGIN rmf:facts -->\n[[X]]\n<!-- END rmf:facts -->\n"
            "[[ART-SSP]]")
    assert list(trace.prose_tokens(trace.strip_generated(text))) == [
        ("INT-001.A1", 1), ("ART-SSP", 5)]


def test_anchors():
    md = "# Top\n## Data flow {#flows}\n## Data flow\n```\n## not a heading\n```\n"
    assert trace.markdown_anchors(md) == {"top", "flows", "data-flow", "data-flow-1"}
    assert trace.slug("Boundary protection (BP)") == "boundary-protection-bp"
    assert trace.yaml_anchors({"items": [{"id": "INV-001"}]}) == {"items", "id", "INV-001"}


@pytest.mark.parametrize("token, problem", [
    ("INT-001.A1", None), ("INT-001.A9", "no interview answer"),
    ("ASM-001", None), ("ASM-BASELINE-001", "no assumption"),
    ("ART-SSP", None), ("ART-CONMON", "not in the run"), ("ART-NOPE", "unknown artifact"),
    ("product/security.md#audit", None), ("product/security.md#nope", "no heading or key"),
    ("product/missing.md", "not found"), ("product/../run.yaml", "outside the product"),
    ("product/README.md", None), ("int-1", "malformed"),
])
def test_resolver(token, problem):
    ctx = Context(open_run(VALID_MINIMAL, REPO_ROOT))
    found = ctx.resolver.problem(token)
    assert (found is None) if problem is None else (problem in found)


def test_interview_parse():
    text = (VALID_MINIMAL / "interviews/INT-001-P-10-PER-PM.md").read_text()
    parsed = interviews.parse("interviews/x.md", text)
    assert parsed.task == "P-10" and parsed.error is None
    (answer,) = parsed.answers
    assert (answer.id, answer.question_id, answer.asked_of) == ("INT-001.A1", "INT-001.Q1",
                                                                  "PER-PM")
    assert answer.fields == {"respondent": "simulated", "tag": "SIMULATED", "basis": ""}
    assert answer.basis == ["product/inventory.md#items"]


def test_frontmatter_errors():
    assert frontmatter.parse("# no fm").error.startswith("no front-matter")
    assert "not closed" in frontmatter.parse("---\na: 1\n").error
    assert "mapping" in frontmatter.parse("---\n- a\n---\nbody").error
    assert frontmatter.set_key("---\nrun_id: a\n---\nrun_id: keep\n", "run_id", "b") == \
        "---\nrun_id: b\n---\nrun_id: keep\n"


def test_journal_format(minimal_run):
    assert ENTRY.match("## 2026-11-05T15:40Z · RETRY · task S-4 · lesson: L-0012")
    assert not ENTRY.match("## 2026-11-05 · CHECKPOINT · task S-4")
    (minimal_run / "journal.md").write_text(
        "# Journal — other\n## 2026-11-05T14:02Z · CHECKPOINT · artifact ART-SSP\n## bad\n")
    messages = [f.finding.message for f in journal(Context(open_run(minimal_run, REPO_ROOT)),
                                                     {"P-10"})]
    assert any("not valid-minimal" in m for m in messages)
    assert any("a CHECKPOINT names a task" in m for m in messages)
    assert any("malformed entry" in m for m in messages)
    assert any("P-10 is done but has no CHECKPOINT" in m for m in messages)
    (minimal_run / "journal.md").unlink()
    assert "missing" in journal(Context(open_run(minimal_run, REPO_ROOT)), set())[0].finding.message
