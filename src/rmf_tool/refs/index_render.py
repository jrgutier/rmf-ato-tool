"""`rmf refs index [--check]`: render ``references/INDEX.md`` from index.yaml (AC-3, REF-004)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2

from rmf_tool.findings import Finding

INDEX_MD = "references/INDEX.md"
TEMPLATE = "INDEX.md.j2"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _url(entry: Any) -> str:
    url = (entry["urls"] or [entry["landing_url"]])[0]
    return f"<{url}>" if url else "—"


def _sha(value: str | None) -> str:
    return f"`{value}`" if value else "—"


def _text(entry: Any) -> str:
    text = entry.get("text")
    if not text:
        return "—"
    rel = Path(text["path"]).relative_to("references").as_posix()
    return f"[{Path(rel).name}]({rel}) ({text['pages']} pp.)"


def render(index: Any) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
    )
    env.filters.update(cell=_cell, url=_url, sha=_sha, text=_text)
    refs = list(index["references"])
    return env.get_template(TEMPLATE).render(
        documents=[e for e in refs if e["kind"] == "pdf"],
        oscal=[e for e in refs if e["kind"].startswith("oscal-")],
        web=[e for e in refs if e["kind"] == "web"],
    )


def write(root: Path, index: Any) -> bool:
    """Write INDEX.md if it changed. Returns True when it wrote."""
    path = root / INDEX_MD
    text = render(index)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def check(root: Path, index: Any) -> list[Finding]:
    path = root / INDEX_MD
    if not path.is_file():
        return [Finding("REF-004", "E", "missing; run rmf refs index", INDEX_MD)]
    if path.read_text(encoding="utf-8") != render(index):
        return [Finding("REF-004", "E", "stale; run rmf refs index", INDEX_MD)]
    return []
