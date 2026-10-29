"""`rmf refs show <id> --section S | --page N --anchor A`: print a cited passage from the
committed text extraction (AC-4a). Sections resolve through ``<ID>.toc.yaml``; a page
citation needs an anchor that occurs on that page (line-break-insensitive) or is the
anchor of a heading on it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from rmf_tool.refs import toc

_HEADING = re.compile(r"^(#{1,6}) \S")
_PAGE = re.compile(r"^<!-- page (\d+)(?: [^>]*)? -->$")


class NotFound(LookupError):
    """The section, page or anchor does not resolve (exit code 1)."""


def _paths(root: Path, entry: Any) -> tuple[Path, Path]:
    text = entry.get("text")
    if not text:
        raise NotFound(f"{entry['id']}: no text extraction (rmf refs extract --id {entry['id']})")
    md = root / text["path"]
    return md, md.with_name(f"{entry['id']}.toc.yaml")


def section(root: Path, entry: Any, wanted: str) -> str:
    """The text from the heading matching ``wanted`` (its number, title or anchor) up to
    the next heading at the same or a higher level."""
    md, toc_path = _paths(root, entry)
    entries = toc.load_toc(toc_path)
    key = wanted.strip().casefold()
    # A heading can repeat (800-37r2 shows TASK P-3 in a figure on p31 and as the task
    # section on p49); the last occurrence is the section itself.
    matches = [i for i, e in enumerate(entries) if e.num.casefold() == key] or \
        [i for i, e in enumerate(entries) if key in (e.title.casefold(), e.anchor.casefold())]
    match = matches[-1] if matches else None
    if match is None:
        raise NotFound(f"{entry['id']}: no section {wanted!r} in {toc_path.name}")
    lines = md.read_text(encoding="utf-8").splitlines()
    heading_lines = [n for n, line in enumerate(lines) if _HEADING.match(line)]
    if len(heading_lines) != len(entries):
        raise NotFound(f"{entry['id']}: {toc_path.name} lists {len(entries)} headings but the "
                       f"text has {len(heading_lines)}; re-extract")
    start, level = heading_lines[match], entries[match].level
    end = next((heading_lines[k] for k in range(match + 1, len(entries))
                if entries[k].level <= level), len(lines))
    return "\n".join(lines[start:end]).rstrip() + "\n"


def page(root: Path, entry: Any, number: int, anchor: str) -> str:
    """Page ``number`` of the extraction, if ``anchor`` resolves on it."""
    md, toc_path = _paths(root, entry)
    out: list[str] = []
    inside = False
    for line in md.read_text(encoding="utf-8").splitlines():
        m = _PAGE.match(line)
        if m:
            if inside:
                break
            inside = int(m.group(1)) == number
        if inside:
            out.append(line)
    if not out:
        raise NotFound(f"{entry['id']}: no page {number}")
    body = "\n".join(out)
    anchors = {e.anchor for e in toc.load_toc(toc_path) if e.page == number} \
        if toc_path.is_file() else set()
    wanted = toc.compact(anchor)
    if anchor not in anchors and (not wanted or wanted not in toc.compact(body)):
        raise NotFound(f"{entry['id']}: anchor {anchor!r} not found on page {number}")
    return body.rstrip() + "\n"
