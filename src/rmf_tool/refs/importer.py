"""`rmf refs import ID PATH`: pin a PDF the user downloaded by hand (browser-assisted).

The file must start with ``%PDF-`` and pass ``qpdf --check``. It is moved to the entry's
``local_path`` (stored in Git LFS), its SHA-256 and size are pinned, and the entry
becomes ``ok``. See ``playbooks/_ops/fetch-blocked-refs.md``.
"""

from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path
from typing import Any

from rmf_tool.refs import find, load_index, save_index, sha256_file
from rmf_tool.refs.domains import disallowed_reason
from rmf_tool.refs.fetch import validate_file


class ImportRejected(ValueError):
    """The id or file cannot be imported (exit code 1)."""


def import_ref(root: Path, ref_id: str, source: Path, *, url: str | None = None,
               today: str | None = None) -> Any:
    """Import ``source`` as reference ``ref_id``; returns the updated entry."""
    data = load_index(root)
    entry = find(data, ref_id)
    if entry is None:
        raise ImportRejected(f"unknown reference id {ref_id!r} (add it to references/index.yaml)")
    if entry["kind"] != "pdf" or not entry["local_path"]:
        raise ImportRejected(f"{ref_id} is a {entry['kind']} entry; only PDFs are imported")
    if not source.is_file():
        raise ImportRejected(f"{source}: no such file")
    if url is not None:
        reason = disallowed_reason(url)
        if reason:
            raise ImportRejected(f"REF-006: --url {url}: {reason}")
    reason = validate_file(source, "pdf")
    if reason:
        raise ImportRejected(f"{source}: {reason}")

    dest = root / entry["local_path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != dest.resolve():
        shutil.move(str(source), dest)
    entry["sha256"] = sha256_file(dest)
    entry["size_bytes"] = dest.stat().st_size
    entry["downloaded"] = today or dt.datetime.now(dt.UTC).date().isoformat()
    entry["resolved_url"] = url
    entry["status"] = "ok"
    save_index(root, data)
    return entry
