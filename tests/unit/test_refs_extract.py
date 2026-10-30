"""Unit tests for rmf_tool.refs.extract on small PDFs generated with PyMuPDF."""

from __future__ import annotations

import builtins
import importlib.metadata
import re
from collections import Counter
from pathlib import Path

import pytest

from rmf_tool.refs import extract as ex
from rmf_tool.refs.toc import load_toc

# PyMuPDF is the optional AGPL [extract] extra (make bootstrap EXTRACT=1); without it these
# tests are skipped, so a default bootstrap still passes `rmf ci`.
pymupdf = pytest.importorskip("pymupdf")

HEADER = "ACME SPEC 100-1, REV. 2 SAMPLE SPECIFICATION FOR TESTS"
NOTICE = "This publication is available free of charge from: https://example.invalid/100-1"
SHA = "0" * 64


def _chrome(page: pymupdf.Page, n: int) -> None:
    """Running header, footer row and rotated side notice, as NIST prints them."""
    page.insert_text((72, 40), HEADER, fontsize=9)
    page.insert_text((72, 765), "CHAPTER ONE", fontsize=8)
    page.insert_text((500, 765), f"PAGE {n}", fontsize=8)
    page.insert_text((30, 600), NOTICE, fontsize=8, rotate=90)


def _para(page: pymupdf.Page, y: float, lines: list[str], *, x: float = 72) -> float:
    for line in lines:
        page.insert_text((x, y), line, fontsize=10)
        y += 12
    return y + 12


def _heading(page: pymupdf.Page, y: float, text: str) -> float:
    page.insert_text((72, y), text, fontsize=12, fontname="hebo")
    return y + 24


def make_spec(path: Path, *, outline: bool = True) -> Path:
    """Five pages: two of text, a blank page, a figure-only page, and a last text page."""
    doc = pymupdf.open()
    p1 = doc.new_page(width=612, height=792)
    _chrome(p1, 1)
    y = _heading(p1, 110, "1 INTRODUCTION")
    y = _para(
        p1,
        y,
        [
            "The quick brown fox jumps over the lazy dog in an organization-",
            "wide exercise that tests hyphenation joins across lines.",
        ],
    )
    y = _para(p1, y, ["2 Organizations should not treat this sentence as a heading."])
    y = _heading(p1, y, "TASK C-2 Categorize the system and document the results.")
    _para(p1, y, ["Potential Inputs: none at all."])
    p2 = doc.new_page(width=612, height=792)
    _chrome(p2, 2)
    y = _heading(p2, 110, "1.1 BACKGROUND")
    _para(p2, y, ["Background text sits on the second page and mentions PAGE 2 in its body."])
    doc.new_page(width=612, height=792)  # blank
    p4 = doc.new_page(width=612, height=792)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8), False)
    pix.clear_with(128)
    p4.insert_image(pymupdf.Rect(150, 200, 450, 500), pixmap=pix)
    p5 = doc.new_page(width=612, height=792)
    _chrome(p5, 5)
    y = _heading(p5, 110, "APPENDIX A GLOSSARY")
    _para(p5, y, ["Terms are defined here."])
    if outline:
        doc.set_toc(
            [
                [1, "1 INTRODUCTION", 1],
                [2, "1.1 BACKGROUND", 2],
                [
                    1,
                    "This bookmark is a whole paragraph that no heading should ever "
                    "become, because it is far too long to be one.",
                    2,
                ],
                [1, "APPENDIX A GLOSSARY", 5],
            ]
        )
    doc.save(path)
    return path


@pytest.fixture
def spec(tmp_path: Path) -> Path:
    return make_spec(tmp_path / "spec.pdf")


def run(pdf: Path, out: Path, **kw) -> ex.ExtractResult:
    return ex.extract("DOC", pdf, out, source_sha256=SHA, **kw)


def preamble(path: Path) -> dict:
    meta = ex.read_preamble(path)
    assert meta is not None
    return meta


def page_texts(md: str) -> dict[int, str]:
    parts = re.split(r'^<!-- page (\d+)(?: label="[^"]*")? -->$', md, flags=re.M)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def test_page_markers_present_and_sequential(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out")
    md = res.text_path.read_text(encoding="utf-8")
    nums = [int(m) for m in re.findall(r"^<!-- page (\d+) -->$", md, flags=re.M)]
    assert nums == [1, 2, 3, 4, 5] and res.pages == 5
    assert res.text_path == tmp_path / "out" / "DOC.md"
    assert res.toc_path == tmp_path / "out" / "DOC.toc.yaml"


def test_blank_page_marker_only(spec: Path, tmp_path: Path) -> None:
    pages = page_texts(run(spec, tmp_path / "out").text_path.read_text(encoding="utf-8"))
    assert pages[3].strip() == "" and pages[4].strip() == ""  # blank, figure-only


def test_rerun_byte_identical(spec: Path, tmp_path: Path) -> None:
    a = run(spec, tmp_path / "a")
    b = run(spec, tmp_path / "b")
    assert a.text_path.read_bytes() == b.text_path.read_bytes()
    assert a.toc_path.read_bytes() == b.toc_path.read_bytes()
    assert a.sha256 == b.sha256
    raw = a.text_path.read_bytes()
    assert b"\r" not in raw and raw.endswith(b"\n") and not raw.endswith(b"\n\n")


def test_header_footer_stripped(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out")
    md = res.text_path.read_text(encoding="utf-8")
    body = md.split("-->\n", 1)[1]
    for gone in (HEADER, "CHAPTER ONE", "PAGE 1", "PAGE 5", NOTICE):
        assert gone not in body
    assert "mentions PAGE 2 in its body" in body  # body text is never a margin line
    stripped = preamble(res.text_path)["stripped"]
    assert "ACME SPEC #-#, REV. # SAMPLE SPECIFICATION FOR TESTS" in stripped
    assert "<page-number>" in stripped and "CHAPTER ONE" in stripped
    assert "This publication is available free of charge from: https://example.invalid/#-#" in (
        stripped
    )


def test_preamble_records_tuple(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out")
    meta = preamble(res.text_path)
    assert meta["doc"] == "DOC" and meta["source_sha256"] == SHA
    assert meta["extractor"] == "pymupdf" == res.extractor
    assert meta["extractor_version"] == importlib.metadata.version("pymupdf")
    assert meta["rmf_extract_version"] == ex.RMF_EXTRACT_VERSION == res.rmf_extract_version
    assert meta["pages"] == "5" and meta["ocr"] == "false" and meta["ocr_pages"] == "[]"


def test_outline_headings_inserted(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out")
    md = res.text_path.read_text(encoding="utf-8")
    assert "\n# 1 INTRODUCTION\n" in md and "\n## 1.1 BACKGROUND\n" in md
    assert "\n# APPENDIX A GLOSSARY\n" in md
    toc = load_toc(res.toc_path)
    outline = [(e.title, e.page, e.source) for e in toc if e.source == "outline"]
    assert outline == [
        ("1 INTRODUCTION", 1, "outline"),
        ("1.1 BACKGROUND", 2, "outline"),
        ("APPENDIX A GLOSSARY", 5, "outline"),
    ]
    assert not any("whole paragraph" in e.title for e in toc)
    intro = next(e for e in toc if e.title == "1 INTRODUCTION")
    assert intro.level == 1 and intro.anchor == "1-introduction" and intro.num == "1"


def test_regex_heading_fallback(tmp_path: Path) -> None:
    pdf = make_spec(tmp_path / "plain.pdf", outline=False)
    res = run(pdf, tmp_path / "out")
    md = res.text_path.read_text(encoding="utf-8")
    toc = {e.title: e for e in load_toc(res.toc_path)}
    assert set(toc) == {"1 INTRODUCTION", "TASK C-2", "1.1 BACKGROUND", "APPENDIX A GLOSSARY"}
    assert toc["TASK C-2"].page == 1 and toc["TASK C-2"].level == 3
    assert toc["TASK C-2"].num == "C-2" and toc["TASK C-2"].anchor == "task-c-2"
    assert toc["1.1 BACKGROUND"].level == 2 and toc["1.1 BACKGROUND"].source == "regex"
    # The task statement stays in the body under the heading; a numbered sentence does not
    # become a heading.
    assert "### TASK C-2\n\nCategorize the system and document the results.\n" in md
    assert "\n2 Organizations should not treat this sentence as a heading.\n" in md


def test_hyphenation_join(spec: Path, tmp_path: Path) -> None:
    md = run(spec, tmp_path / "out").text_path.read_text(encoding="utf-8")
    assert "in an organization-wide\nexercise" in md


def make_table(path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 100), "Table 1 lists the baselines.", fontsize=10)
    xs, ys = [72, 200, 330, 460], [120, 150, 180, 210]
    for x in xs:
        page.draw_line((x, ys[0]), (x, ys[-1]))
    for y in ys:
        page.draw_line((xs[0], y), (xs[-1], y))
    cells = [
        ["Control", "Name", "Baseline"],
        ["AC-1", "Policy | Procedures", "LOW"],
        ["AC-2", "Organization-\nwide accounts", "MODERATE"],  # a cell wrapped at a hyphen
    ]
    for r, row in enumerate(cells):
        for c, text in enumerate(row):
            page.insert_text((xs[c] + 4, ys[r] + 13), text, fontsize=10)
    page.insert_text((72, 250), "Text after the table.", fontsize=10)
    doc.save(path)
    return path


def test_table_page_pipe_table(tmp_path: Path) -> None:
    md = run(make_table(tmp_path / "t.pdf"), tmp_path / "out").text_path.read_text("utf-8")
    body = page_texts(md)[1].strip().splitlines()
    assert body == [
        "Table 1 lists the baselines.",
        "",
        "| Control | Name | Baseline |",
        "| --- | --- | --- |",
        "| AC-1 | Policy \\| Procedures | LOW |",
        "| AC-2 | Organization-wide accounts | MODERATE |",
        "",
        "Text after the table.",
    ]


def test_table_failure_falls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self, **kw):
        raise RuntimeError("table finder failed")

    monkeypatch.setattr(pymupdf.Page, "find_tables", boom)
    md = run(make_table(tmp_path / "t.pdf"), tmp_path / "out").text_path.read_text("utf-8")
    body = page_texts(md)[1]
    assert ex.TABLE_FALLBACK in body and "Policy | Procedures" in body


def test_two_column_order(tmp_path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 80), "A TITLE THAT SPANS BOTH COLUMNS OF THE PAGE LAYOUT", fontsize=12)
    right = [f"Right column line {i} continues the second column." for i in range(8)]
    left = [f"Left column line {i} reads first in the flow." for i in range(8)]
    _para(page, 120, right, x=320)  # written first, so stream order is right then left
    _para(page, 120, left, x=72)
    doc.save(tmp_path / "cols.pdf")
    body = page_texts(run(tmp_path / "cols.pdf", tmp_path / "out").text_path.read_text("utf-8"))
    text = body[1]
    assert (
        text.index("A TITLE")
        < text.index("Left column line 0")
        < text.index("Left column line 7")
        < text.index("Right column line 0")
    )


def test_page_label_recorded(tmp_path: Path) -> None:
    doc = pymupdf.open()
    for _ in range(3):
        doc.new_page(width=612, height=792).insert_text((72, 300), "Front matter.", fontsize=10)
    doc.set_page_labels([{"startpage": 0, "prefix": "", "style": "r", "firstpagenum": 1}])
    doc.save(tmp_path / "lab.pdf")
    md = run(tmp_path / "lab.pdf", tmp_path / "out").text_path.read_text("utf-8")
    assert '<!-- page 2 label="ii" -->' in md
    assert ex.check("DOC", tmp_path / "lab.pdf", tmp_path / "out", source_sha256=SHA) == []


def test_ocr_off_by_default(spec: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_ocr(page):
        raise AssertionError("OCR must be opt-in")

    monkeypatch.setattr(ex, "_ocr_textpage", no_ocr)
    res = run(spec, tmp_path / "out")
    assert res.ocr is False and res.ocr_pages == []


def test_ocr_opt_in_recorded(spec: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_ocr(page):  # stands in for Tesseract; never run real OCR in tests
        calls.append(page.number + 1)
        page.insert_text((72, 300), "Recognized figure caption.", fontsize=10)  # in memory
        return page.get_textpage()

    monkeypatch.setattr(ex, "_ocr_textpage", fake_ocr)
    res = run(spec, tmp_path / "out", ocr=True)
    assert calls == [4] and res.ocr is True and res.ocr_pages == [4]
    meta = preamble(res.text_path)
    assert meta["ocr"] == "true" and meta["ocr_pages"] == "[4]"
    assert "Recognized figure caption." in page_texts(res.text_path.read_text("utf-8"))[4]


def test_ocr_requires_pymupdf(spec: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="ocr"):
        run(spec, tmp_path / "out", extractor="pdfplumber", ocr=True)


def test_pdfplumber_fallback_same_interface(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out", extractor="pdfplumber")
    md = res.text_path.read_text(encoding="utf-8")
    assert res.extractor == "pdfplumber" and res.pages == 5
    assert res.extractor_version == importlib.metadata.version("pdfplumber")
    assert [int(n) for n in re.findall(r"^<!-- page (\d+) -->$", md, flags=re.M)] == [1, 2, 3, 4, 5]
    assert HEADER not in md.split("-->\n", 1)[1]
    assert "TASK C-2" in {e.title for e in load_toc(res.toc_path)}
    assert run(spec, tmp_path / "again", extractor="pdfplumber").sha256 == res.sha256


def test_unknown_extractor_rejected(spec: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown extractor"):
        run(spec, tmp_path / "out", extractor="poppler")


def test_check_short_circuits_when_tuple_unchanged(
    spec: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "out"
    res = run(spec, out)

    def no_open(*a, **kw):
        raise AssertionError("check must not open the PDF")

    monkeypatch.setattr(ex, "_open", no_open)
    assert ex.check("DOC", spec, out, source_sha256=SHA) == []
    assert ex.check("DOC", spec, out, source_sha256=SHA, text_sha256=res.sha256) == []


def test_check_detects_stale_tuple(spec: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    run(spec, out)
    problems = ex.check("DOC", spec, out, source_sha256="1" * 64)
    assert len(problems) == 1 and "source_sha256" in problems[0]
    problems = ex.check("DOC", spec, out, source_sha256=SHA, extractor="pdfplumber")
    assert any("extractor" in p for p in problems)


def test_check_detects_text_sha_drift(spec: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    res = run(spec, out)
    res.text_path.write_text(res.text_path.read_text("utf-8") + "hand edit\n", encoding="utf-8")
    problems = ex.check("DOC", spec, out, source_sha256=SHA, text_sha256=res.sha256)
    assert problems == [f"DOC: {res.text_path} does not match the recorded text sha256"]


def test_check_detects_bad_page_markers(spec: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    res = run(spec, out)
    md = res.text_path.read_text("utf-8").replace("<!-- page 3 -->\n", "")
    res.text_path.write_text(md, encoding="utf-8")
    assert any("page markers" in p for p in ex.check("DOC", spec, out, source_sha256=SHA))


def test_check_reports_missing_files(spec: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert "missing" in ex.check("DOC", spec, out, source_sha256=SHA)[0]
    assert "missing" in ex.check("DOC", tmp_path / "nope.pdf", out, source_sha256=SHA)[0]
    run(spec, out)
    (out / "DOC.toc.yaml").unlink()
    assert any("toc.yaml is missing" in p for p in ex.check("DOC", spec, out, source_sha256=SHA))


def test_is_current_requires_full_tuple(spec: Path, tmp_path: Path) -> None:
    res = run(spec, tmp_path / "out")
    entry = {
        "source_sha256": SHA,
        "extractor": res.extractor,
        "extractor_version": res.extractor_version,
        "rmf_extract_version": res.rmf_extract_version,
        "sha256": res.sha256,
    }
    assert ex.is_current(entry, SHA, "pymupdf")
    assert not ex.is_current(None, SHA, "pymupdf")
    assert not ex.is_current(entry, "1" * 64, "pymupdf")
    assert not ex.is_current(entry, SHA, "pdfplumber")
    for key in ("source_sha256", "extractor_version", "rmf_extract_version"):
        assert not ex.is_current({**entry, key: "other"}, SHA, "pymupdf")


def test_extract_without_extra_gives_actionable_error(
    spec: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_dist(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", no_dist)
    with pytest.raises(ex.ExtractorUnavailable, match=r"\[extract\] extra"):
        run(spec, tmp_path / "out")
    monkeypatch.undo()

    real_import = builtins.__import__

    def no_pymupdf(name, *args, **kwargs):
        if name == "pymupdf":
            raise ImportError("No module named 'pymupdf'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pymupdf)
    with pytest.raises(ex.ExtractorUnavailable, match="EXTRACT=1"):
        run(spec, tmp_path / "out")
    assert not (tmp_path / "out" / "DOC.md").exists()


def test_infer_glyphs_resolves_private_use_ligatures_per_font() -> None:
    pua = Counter(
        {
            ("Calibri", "rela\ue000onships"): 3,
            ("Calibri", "se\ue001ngs"): 2,
            ("Calibri-Bold", "a\ue001ributes"): 1,  # same code point, another ligature
            ("Calibri", "x\ue002y"): 1,  # nothing in the vocabulary: stays unresolved
            ("Calibri-Bold", "\ue000"): 4,  # a lone glyph is a symbol
        }
    )
    vocab = {"relationships", "settings", "attributes"}
    glyphs = ex.infer_glyphs(pua, vocab)
    assert glyphs == {
        ("Calibri", "\ue000"): "ti",
        ("", "\ue000"): "ti",
        ("Calibri", "\ue001"): "tti",
        ("Calibri-Bold", "\ue001"): "tt",
        ("", "\ue001"): "tti",  # pooled over fonts: settings (2) outweighs attributes (1)
    }
    assert ex._apply_glyphs("se\ue001ngs", "Calibri", glyphs) == "settings"
    assert ex._apply_glyphs("a\ue001ributes", "Calibri-Bold", glyphs) == "attributes"
    assert ex._apply_glyphs("organiza\ue000on", "Unknown", glyphs) == "organization"
    assert ex._apply_glyphs("\uf0b7 item", "Symbol", glyphs) == "• item"
    assert ex._apply_glyphs("x\ue002y", "Calibri", glyphs) == "x\ue002y"
