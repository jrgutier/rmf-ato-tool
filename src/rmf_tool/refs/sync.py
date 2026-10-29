"""Index-side orchestration of text extraction (`rmf refs extract`) and `rmf refs sync`.

``extract.py`` writes ``references/text/``; only this module writes the ``text`` block
of index.yaml, from the returned ``ExtractResult``.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rmf_tool.findings import Finding
from rmf_tool.refs import TEXT_DIR, load_index, save_index


@dataclass(frozen=True)
class Extracted:
    id: str
    status: str  # extracted | current
    pages: int


def _pdf_entries(index: Any, ids: list[str] | None) -> list[Any]:
    selected = [e for e in index["references"] if e["kind"] == "pdf" and e["status"] == "ok"
                and (not ids or e["id"] in ids)]
    unknown = sorted(set(ids or ()) - {e["id"] for e in index["references"]})
    if unknown:
        raise KeyError(f"unknown reference id(s): {', '.join(unknown)}")
    return selected


def text_block(root: Path, result: Any, source_sha256: str) -> dict[str, Any]:
    return {
        "path": result.text_path.resolve().relative_to(root.resolve()).as_posix(),
        "source_sha256": source_sha256,
        "extractor": result.extractor,
        "extractor_version": result.extractor_version,
        "rmf_extract_version": result.rmf_extract_version,
        "pages": result.pages,
        "sha256": result.sha256,
        "ocr": result.ocr,
        "ocr_pages": list(result.ocr_pages),
    }


def extract_all(root: Path, ids: list[str] | None = None, *, extractor: str = "pymupdf",
                ocr: bool = False, full: bool = False) -> list[Extracted]:
    """Extract every ok PDF whose recorded tuple is not current (all of them with
    ``full``), and record the text blocks in index.yaml."""
    from rmf_tool.refs import extract

    index = load_index(root)
    out: list[Extracted] = []
    try:
        for entry in _pdf_entries(index, ids):
            text = entry.get("text")
            if not full and not ocr and extract.is_current(text, entry["sha256"], extractor):
                out.append(Extracted(entry["id"], "current", text["pages"]))
                continue
            result = extract.extract(entry["id"], root / entry["local_path"], root / TEXT_DIR,
                                     source_sha256=entry["sha256"], extractor=extractor, ocr=ocr)
            entry["text"] = text_block(root, result, entry["sha256"])
            out.append(Extracted(entry["id"], "extracted", result.pages))
    finally:
        save_index(root, index)  # keep the blocks of documents extracted before a failure
    return out


def full_check(root: Path, index: Any, ids: list[str] | None = None) -> list[Finding]:
    """REF-003 by re-extraction: a fresh extraction into a temp dir must be byte-identical
    to the committed ``.md`` and ``.toc.yaml``."""
    from rmf_tool.refs import extract

    findings: list[Finding] = []
    for entry in _pdf_entries(index, ids):
        text = entry.get("text")
        if not text:
            continue  # reported by verify.check_texts
        committed = root / text["path"]
        with tempfile.TemporaryDirectory(prefix="rmf-extract-") as tmp:
            result = extract.extract(entry["id"], root / entry["local_path"], Path(tmp),
                                     source_sha256=entry["sha256"],
                                     extractor=text["extractor"], ocr=text["ocr"])
            pairs = ((result.text_path, committed),
                     (result.toc_path, committed.with_name(result.toc_path.name)))
            for fresh, old in pairs:
                if not old.is_file() or fresh.read_bytes() != old.read_bytes():
                    findings.append(Finding("REF-003", "E",
                                            f"{entry['id']}: re-extraction differs from "
                                            f"{old.name}", old.relative_to(root).as_posix()))
    return findings
