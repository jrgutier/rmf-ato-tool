"""Headings and `<ID>.toc.yaml` for extracted reference text (plan §6.7, PM-5).

Headings come from the PDF outline when an outline entry is heading-like and its title
is found on its page, and from the guarded regex set for every other block-initial line.
The toc is the citation-resolution index: `{ref, section}` matches an entry's `num` or
`title`, and `{ref, page, anchor}` matches `page` plus the page text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rmf_tool.refs.headers import normalize
from rmf_tool.yamlload import safe_load

MAX_CHARS = 100
_NOT_ALNUM = re.compile(r"[\W_]+")
MAX_WORDS = 14

_LIST_MARKER = re.compile(r"^(?:[-*•▪◦●]|\([A-Za-z0-9]{1,3}\)|[A-Za-z0-9]{1,3}\))(?:\s|$)")
_TRAILING_PUNCT = re.compile(r"[.:;,]$")
_PART_TITLE = re.compile(r"^(?:[A-Z][^\[\]]*)?$")
_DOT_LEADER = re.compile(r"\.{4,}|(?:\. ){3,}|…{2,}")

# (kind, pattern). Order matters: the first match wins.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("task", re.compile(r"^(?i:TASK)\s+(?P<num>[PCSIARM]-\d{1,2})\b\s*(?P<title>.*)$")),
    (
        "numbered",
        re.compile(
            r"^(?P<num>\d{1,2}(?:\.\d{1,2}){0,4})\.?\s+(?P<title>[A-Z][^\n|]{1,90}[^.\s|:;,])$"
        ),
    ),
    (
        "appendix",
        re.compile(r"^APPENDIX\s+(?P<num>[A-Z](?:\.\d+)*)\b[:.\s-]*(?P<title>.*)$", re.I),
    ),
    ("section", re.compile(r"^SECTION\s+(?P<num>\d{1,2})[:.]?\s+(?P<title>.+)$", re.I)),
    (
        "part",
        re.compile(r"^(?P<num>ENCLOSURE\s+\d+|GLOSSARY|REFERENCES)\b[:.\s-]*(?P<title>.*)$", re.I),
    ),
    (
        "control",
        re.compile(
            r"^(?P<num>[A-Z]{2}-\d{1,2}(?:\(\d{1,2}\))?)\s+(?P<title>[A-Z][A-Z0-9 ,/&\-]+)$"
        ),
    ),
)

# Kinds whose match is only trusted when the line stands alone in its block or is set
# in bold/larger type (a numbered sentence fragment is otherwise too easy to hit).
NEEDS_EMPHASIS = frozenset({"numbered", "appendix", "section", "part", "control"})


@dataclass(frozen=True)
class Heading:
    level: int
    text: str  # the Markdown heading text (no leading #)
    num: str
    kind: str  # outline | task | numbered | appendix | section | part | control
    rest: str = ""  # text after the heading on the same line, kept as body text


@dataclass(frozen=True)
class TocEntry:
    level: int
    title: str
    page: int
    anchor: str
    num: str
    source: str


def heading_like(text: str) -> bool:
    """The §6.7 guards shared by every pattern and by outline titles."""
    return (
        0 < len(text) <= MAX_CHARS
        and len(text.split()) <= MAX_WORDS
        and not _LIST_MARKER.match(text)
        and not _DOT_LEADER.search(text)
        and any(c.isalpha() for c in text)
    )


def match_heading(text: str, *, prev_blank: bool = True, in_table: bool = False) -> Heading | None:
    """Match one line against the §6.7 regex set, applying the shared guards.

    An RMF task line ("TASK C-2   Categorize the system ...") yields the heading
    ``TASK C-2``; the task statement stays in the body as `rest`, so only the
    heading text needs to satisfy the guards.
    """
    if not prev_blank or in_table or text.startswith("|"):
        return None
    for kind, pattern in PATTERNS:
        m = pattern.match(text)
        if not m:
            continue
        num = re.sub(r"\s+", " ", m.group("num"))
        if kind == "task":
            head, rest = f"TASK {num}", m.group("title").strip()
        else:
            head, rest = text, ""
        if not heading_like(head):
            return None
        if kind != "task" and _TRAILING_PUNCT.search(head):
            return None
        if kind == "numbered" and ";" in head:  # a list item, not a heading
            return None
        if kind == "part" and not _PART_TITLE.match(m.group("title")):
            return None  # "References: [2] [21]" is a citation line, not a heading
        return Heading(_level(kind, num), head, num, kind, rest)
    return None


def _level(kind: str, num: str) -> int:
    if kind == "numbered":
        return min(num.count(".") + 1, 6)
    if kind == "task":
        return 3
    if kind == "control":
        return 3 if "(" in num else 2
    return 1


_LEADING_NUM = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){0,4})\.?\s")
_WORD_FOOTNOTE_REF = re.compile(r"(?<=[A-Za-z])\s*\d{1,3}F$")


def outline_title(raw: str) -> str | None:
    """Clean an outline (bookmark) title; None if it is not heading-like.

    Word-generated PDFs bookmark whole paragraphs and render footnote references in
    headings as ``51F``; both are filtered here.
    """
    title = _WORD_FOOTNOTE_REF.sub("", normalize(raw))
    if title.endswith(("...", "…")) or _TRAILING_PUNCT.search(title):
        return None
    return title if heading_like(title) else None


def outline_num(title: str) -> str:
    m = _LEADING_NUM.match(title)
    return m.group(1) if m else ""


@lru_cache(maxsize=1 << 16)
def compact(text: str) -> str:
    """Alphanumerics only, casefolded: for line-break- and punctuation-blind matching.
    Memoized: the register compares the same statements and pages hundreds of thousands of
    times per validate. The pattern drops what ``str.isalnum`` rejects: the re docs define a
    word character as alphanumeric (``str.isalnum``) or the underscore."""
    return _NOT_ALNUM.sub("", text.casefold())


def slugify(text: str) -> str:
    """GitHub-style heading anchor (before de-duplication)."""
    text = re.sub(r"[^\w\- ]", "", text.casefold())
    return text.replace(" ", "-")


class Slugger:
    """Assigns unique GitHub-style anchors in document order (`x`, `x-1`, `x-2`)."""

    def __init__(self) -> None:
        self._seen: dict[str, int] = {}

    def __call__(self, text: str) -> str:
        base = slugify(text)
        n = self._seen.get(base)
        if n is None:
            self._seen[base] = 0
            return base
        while True:
            n += 1
            candidate = f"{base}-{n}"
            if candidate not in self._seen:
                self._seen[base] = n
                self._seen[candidate] = 0
                return candidate


def render_toc(doc_id: str, entries: list[TocEntry]) -> str:
    """Serialize the toc as YAML. Strings are JSON-quoted (valid YAML) for stable bytes."""
    out = [f"# Generated by rmf refs extract from references/pdf/{doc_id}.pdf. Do not edit.\n"]
    if not entries:
        out.append("[]\n")
    for e in entries:
        out.append(
            f"- level: {e.level}\n"
            f"  title: {_q(e.title)}\n"
            f"  page: {e.page}\n"
            f"  anchor: {_q(e.anchor)}\n"
            f"  num: {_q(e.num)}\n"
            f"  source: {e.source}\n"
        )
    return "".join(out)


def _q(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def load_toc(path: Path) -> list[TocEntry]:
    stat = path.stat()
    return list(_load_toc(str(path), stat.st_mtime_ns, stat.st_size))


@lru_cache(maxsize=64)
def _load_toc(path: str, mtime_ns: int, size: int) -> tuple[TocEntry, ...]:
    """Parsed once per file version: citation checks resolve hundreds of sections."""
    data = safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: toc must be a YAML list")
    return tuple(TocEntry(**{k: item[k] for k in TocEntry.__dataclass_fields__}) for item in data)
