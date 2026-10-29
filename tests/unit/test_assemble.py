"""`rmf assemble`: marker blocks, idempotence, unknown marker."""

import pytest
from conftest import REPO_ROOT

from rmf_tool import assemble
from rmf_tool.run.model import open_run

BLOCKS = {"facts": lambda: "| Fact | Value | Set by |\n"}


def test_marker_block_filled_and_idempotent():
    text = "# T\n\n<!-- BEGIN rmf:facts -->\nold\n<!-- END rmf:facts -->\nafter\n"
    once = assemble.assemble_text(text, BLOCKS, "x.md")
    assert once == "# T\n\n<!-- BEGIN rmf:facts -->\n| Fact | Value | Set by |\n" \
                   "<!-- END rmf:facts -->\nafter\n"
    assert assemble.assemble_text(once, BLOCKS, "x.md") == once


@pytest.mark.parametrize("text, message", [
    ("<!-- BEGIN rmf:nope -->\n<!-- END rmf:nope -->\n", "unknown marker rmf:nope"),
    ("<!-- BEGIN rmf:facts -->\nno end\n", "unbalanced"),
])
def test_bad_markers(text, message):
    with pytest.raises(assemble.AssembleError, match=message):
        assemble.assemble_text(text, BLOCKS, "x.md")


def test_write_reports_changed_files(minimal_run):
    md = minimal_run / "artifacts/ART-CAT.md"
    md.write_text(md.read_text().replace("| Control baseline", "| Edited"))
    run = open_run(minimal_run, REPO_ROOT)
    assert assemble.write(run) == ["artifacts/ART-CAT.md"]
    assert assemble.write(run) == []
