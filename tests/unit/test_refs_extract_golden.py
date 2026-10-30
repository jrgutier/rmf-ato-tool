"""Golden checks of the committed reference extractions (slow; needs references/pdf)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from rmf_tool.refs import extract as ex
from rmf_tool.refs.toc import load_toc

pytestmark = pytest.mark.slow

ROOT = Path(__file__).resolve().parents[2]
TEXT = ROOT / "references" / "text"
PDF = ROOT / "references" / "pdf"
GOLDEN = YAML(typ="safe").load(
    (ROOT / "tests" / "fixtures" / "golden" / "excerpts.yaml").read_text(encoding="utf-8")
)
COMMITTED = sorted(p.name.removesuffix(".md") for p in TEXT.glob("*.md"))

TASKS_80037 = (
    [f"P-{i}" for i in range(1, 19)]
    + [f"C-{i}" for i in range(1, 4)]
    + [f"S-{i}" for i in range(1, 7)]
    + [f"I-{i}" for i in range(1, 3)]
    + [f"A-{i}" for i in range(1, 7)]
    + [f"R-{i}" for i in range(1, 6)]
    + [f"M-{i}" for i in range(1, 8)]
)


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _pages(doc: str) -> dict[int, str]:
    pages: dict[int, list[str]] = {}
    current = 0
    for line in (TEXT / f"{doc}.md").read_text(encoding="utf-8").splitlines():
        m = ex.PAGE_MARKER.match(line)
        if m:
            current = int(m.group("num"))
            pages[current] = []
        elif current:
            pages[current].append(line)
    return {n: _flat("\n".join(lines)) for n, lines in pages.items()}


@pytest.mark.parametrize("doc", sorted(GOLDEN))
def test_golden_excerpts(doc: str) -> None:
    pages = _pages(doc)
    spec = GOLDEN[doc]
    for item in spec.get("excerpts", []):
        assert _flat(item["contains"]) in pages[item["page"]], (doc, item)
    for gone in spec.get("absent", []):
        hits = [n for n, text in pages.items() if n >= gone["from_page"] and gone["text"] in text]
        assert hits == [], (doc, gone["text"], hits[:5])


def test_80037_toc_has_all_47_task_headings() -> None:
    entries = load_toc(TEXT / "SP800-37R2.toc.yaml")
    tasks = {e.num for e in entries if e.title.startswith("TASK ")}
    assert len(TASKS_80037) == 47
    assert tasks == set(TASKS_80037)
    for e in entries:
        if e.title.startswith("TASK "):
            assert e.title == f"TASK {e.num}" and e.level == 3


@pytest.mark.parametrize("doc", COMMITTED)
def test_full_reextract_matches_committed(doc: str, tmp_path: Path) -> None:
    meta = ex.read_preamble(TEXT / f"{doc}.md")
    assert meta is not None
    sha, extractor = meta["source_sha256"], meta["extractor"]
    if extractor == "pymupdf":
        pytest.importorskip("pymupdf")  # the optional AGPL [extract] extra (L-0038)
    if meta["ocr"] == "true":  # OCR never runs in tests or CI: verify the recorded tuple only
        assert ex.check(doc, PDF / f"{doc}.pdf", TEXT, source_sha256=sha, extractor=extractor) == []
        return
    res = ex.extract(doc, PDF / f"{doc}.pdf", tmp_path, source_sha256=sha, extractor=extractor)
    assert res.text_path.read_bytes() == (TEXT / f"{doc}.md").read_bytes()
    assert res.toc_path.read_bytes() == (TEXT / f"{doc}.toc.yaml").read_bytes()
