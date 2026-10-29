import pytest
from _refs_fixtures import SHA_A, entry, make_root
from typer.testing import CliRunner

from rmf_tool.cli import app
from rmf_tool.refs import show, toc

runner = CliRunner()

MD = """\
<!--
preamble
-->

<!-- page 1 -->

# 1 INTRODUCTION

Intro text.

## 1.1 Purpose and Applicability

The purpose of this
publication is clear.

<!-- page 2 label="ii" -->

\\# not a heading

## 1.2 Target Audience

Audience text.

# 2 THE FUNDAMENTALS

Fundamentals text.
"""

ENTRIES = [
    toc.TocEntry(1, "1 INTRODUCTION", 1, "1-introduction", "1", "outline"),
    toc.TocEntry(2, "1.1 Purpose and Applicability", 1, "11-purpose-and-applicability", "1.1",
                 "outline"),
    toc.TocEntry(2, "1.2 Target Audience", 2, "12-target-audience", "1.2", "regex"),
    toc.TocEntry(1, "2 THE FUNDAMENTALS", 2, "2-the-fundamentals", "2", "outline"),
]


@pytest.fixture
def rr(tmp_path):
    text = {"path": "references/text/DOC-A.md", "source_sha256": SHA_A, "extractor": "pymupdf",
            "extractor_version": "2.0", "rmf_extract_version": "1", "pages": 2,
            "sha256": SHA_A, "ocr": False, "ocr_pages": []}
    rr = make_root(tmp_path, [entry(status="ok", sha256=SHA_A, size_bytes=1,
                                    downloaded="2026-10-29", text=text),
                              entry("DOC-B")])
    rr.write("references/text/DOC-A.md", MD)
    rr.write("references/text/DOC-A.toc.yaml", toc.render_toc("DOC-A", ENTRIES))
    return rr


def test_section_by_number_runs_to_next_sibling(rr):
    out = show.section(rr.root, rr.entry("DOC-A"), "1")
    assert out.startswith("# 1 INTRODUCTION\n")
    assert "## 1.2 Target Audience" in out and "<!-- page 2" in out
    assert "THE FUNDAMENTALS" not in out


def test_section_by_title_or_anchor(rr):
    by_title = show.section(rr.root, rr.entry("DOC-A"), "1.1 purpose and applicability")
    by_anchor = show.section(rr.root, rr.entry("DOC-A"), "12-target-audience")
    assert by_title.splitlines()[-1] == "\\# not a heading"
    assert "publication is clear." in by_title and "1.2 Target" not in by_title
    assert "Audience text." in by_anchor and "FUNDAMENTALS" not in by_anchor


def test_repeated_heading_resolves_to_last_occurrence(rr):
    md = MD.replace("Intro text.", "# 2 THE FUNDAMENTALS\n\nFigure copy.")
    rr.write("references/text/DOC-A.md", md)
    rr.write("references/text/DOC-A.toc.yaml", toc.render_toc(
        "DOC-A", [ENTRIES[0], toc.TocEntry(1, "2 THE FUNDAMENTALS", 1, "2-the-fundamentals",
                                            "2", "regex"), *ENTRIES[1:]]))
    assert show.section(rr.root, rr.entry("DOC-A"), "2") == \
        "# 2 THE FUNDAMENTALS\n\nFundamentals text.\n"


def test_last_section_runs_to_end(rr):
    assert show.section(rr.root, rr.entry("DOC-A"), "2").endswith("Fundamentals text.\n")


def test_page_with_anchor_is_line_break_insensitive(rr):
    out = show.page(rr.root, rr.entry("DOC-A"), 1, "purpose of this publication")
    assert out.startswith("<!-- page 1 -->") and "page 2" not in out


def test_page_with_heading_anchor(rr):
    out = show.page(rr.root, rr.entry("DOC-A"), 2, "12-target-audience")
    assert out.startswith('<!-- page 2 label="ii" -->')


@pytest.mark.parametrize("call,match", [
    (lambda rr: show.section(rr.root, rr.entry("DOC-A"), "9.9"), "no section"),
    (lambda rr: show.page(rr.root, rr.entry("DOC-A"), 7, "x"), "no page 7"),
    (lambda rr: show.page(rr.root, rr.entry("DOC-A"), 1, "Audience text"), "not found"),
    (lambda rr: show.page(rr.root, rr.entry("DOC-A"), 1, " - "), "not found"),
    (lambda rr: show.section(rr.root, rr.entry("DOC-B"), "1"), "no text extraction"),
])
def test_not_found(rr, call, match):
    with pytest.raises(show.NotFound, match=match):
        call(rr)


def test_toc_text_mismatch_detected(rr):
    rr.write("references/text/DOC-A.toc.yaml", toc.render_toc("DOC-A", ENTRIES[:2]))
    with pytest.raises(show.NotFound, match="re-extract"):
        show.section(rr.root, rr.entry("DOC-A"), "1")


@pytest.mark.parametrize("args,code,needle", [
    (["DOC-A", "--section", "1.2"], 0, "Audience text."),
    (["DOC-A", "--page", "1", "--anchor", "Intro text"], 0, "<!-- page 1 -->"),
    (["DOC-A", "--section", "7"], 1, "no section"),
    (["DOC-A"], 2, "either"),
    (["DOC-A", "--page", "1"], 2, "either"),
    (["DOC-A", "--section", "1", "--page", "1", "--anchor", "x"], 2, "either"),
    (["NOPE", "--section", "1"], 2, "unknown reference"),
])
def test_cli_show(rr, monkeypatch, args, code, needle):
    monkeypatch.chdir(rr.root)
    result = runner.invoke(app, ["refs", "show", *args])
    assert result.exit_code == code
    assert needle in result.output
