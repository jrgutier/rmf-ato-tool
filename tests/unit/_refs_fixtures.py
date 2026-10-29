"""Shared helpers for the reference-library tests: a minimal valid PDF and a tmp repo
root with an index.yaml that passes the real schema."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from conftest import REPO_ROOT

from rmf_tool import refs
from rmf_tool.refs.required import REQUIRED_IDS

SHA_A = "a" * 64
SHA_B = "b" * 64


def make_pdf(text: str = "hello") -> bytes:
    """A one-page PDF with a correct xref table (``qpdf --check`` exits 0)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for num, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % num + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % off for off in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1, xref)
    return out


def entry(ref_id: str = "DOC-A", **overrides: Any) -> dict[str, Any]:
    base = {
        "id": ref_id,
        "title": f"Title of {ref_id}",
        "publisher": "NIST",
        "revision": "Rev. 1",
        "kind": "pdf",
        "required": False,
        "acquisition": "auto",
        "urls": [f"https://nvlpubs.nist.gov/{ref_id}.pdf"],
        "landing_url": None,
        "resolved_url": None,
        "local_path": f"references/pdf/{ref_id}.pdf",
        "sha256": None,
        "size_bytes": None,
        "downloaded": None,
        "revision_note": None,
        "status": "missing",
    }
    base.update(overrides)
    return base


def required_entries() -> list[dict[str, Any]]:
    """Placeholder entries for the pinned required set, so REF-001's set check passes."""
    return [entry(rid, required=True, acquisition="browser-assisted", urls=[],
                  landing_url="https://www.esd.whs.mil/", status="pending-acquisition")
            for rid in REQUIRED_IDS]


class RefsRoot:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_index(self, entries: list[dict[str, Any]]) -> None:
        (self.root / refs.INDEX_PATH).write_text(
            refs.dump_index({"schema_version": 1, "references": entries}), encoding="utf-8")

    def index(self) -> Any:
        return refs.load_index(self.root)

    def entry(self, ref_id: str) -> Any:
        return refs.find(self.index(), ref_id)

    def write(self, rel: str, data: bytes | str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_bytes(data)
        return path


def make_root(tmp_path: Path, entries: list[dict[str, Any]] | None = None) -> RefsRoot:
    root = tmp_path / "repo"
    (root / "references" / "schema").mkdir(parents=True)
    shutil.copy(REPO_ROOT / refs.SCHEMA_PATH, root / refs.SCHEMA_PATH)
    rr = RefsRoot(root)
    rr.write_index(entries if entries is not None else [entry()])
    return rr
