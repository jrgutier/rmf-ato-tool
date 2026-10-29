"""Running header/footer detection for PDF text extraction (plan PM-5).

A margin line is a horizontal line inside the top or bottom band of the page, or a
non-horizontal line inside a side band (e.g. the rotated "This publication is available
free of charge" notice NIST prints down the left edge). Margin lines are keyed by `pattern_key`
(digits become ``#``, so "PAGE 28" and "PAGE 29" share a key). A key seen on enough
distinct pages is a running header/footer and is stripped from every page. Bare page
numbers in a band are always stripped, and so is a band line that sits on the same row
as a stripped line on at least two pages (a footer such as "APPENDIX C ... PAGE 113" is
one row, even when the appendix spans too few pages to reach the repeat threshold).
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass

TOP_BAND = 0.10
BOTTOM_BAND = 0.075
SIDE_BAND = 0.10
ROW_TOLERANCE = 3.0  # points between baselines of lines on one row
PAGE_NUMBER_KEY = "<page-number>"

_PAGE_NUMBER = re.compile(
    r"^[-–—\s]*(?:page\s+)?(?:(?:[A-Z](?:\.\d{1,2})?-)?\d{1,4}|[ivxlcdm]{1,8})"
    r"(?:\s+of\s+\d{1,4})?[-–—\s]*$",
    re.IGNORECASE,
)
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f\u2028\u2029]")
_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """NFKC, control characters removed, whitespace collapsed and trimmed."""
    text = unicodedata.normalize("NFKC", text.replace("\u00ad", ""))
    text = _CONTROL.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def pattern_key(text: str) -> str:
    """The key that identifies a running header/footer line across pages."""
    text = normalize(text)
    if _PAGE_NUMBER.match(text):
        return PAGE_NUMBER_KEY
    return re.sub(r"\d+", "#", text)


def in_band(baseline: float, height: float) -> bool:
    return baseline <= height * TOP_BAND or baseline >= height * (1 - BOTTOM_BAND)


def in_side_band(x0: float, x1: float, width: float) -> bool:
    return x1 <= width * SIDE_BAND or x0 >= width * (1 - SIDE_BAND)


def min_repeats(pages: int) -> int:
    """How many distinct pages a margin key must appear on to count as running: 5% of
    the pages, at least 3. Lower and a document whose body starts high on the page
    (SP 800-60 Vol. 2) loses its first lines; shorter runs such as a two-page
    appendix footer are caught as row mates of the page number instead."""
    return 2 if pages <= 4 else max(3, math.ceil(pages * 0.05))


@dataclass(frozen=True)
class MarginLine:
    key: str
    y: float  # baseline
    band: bool  # a horizontal line inside the top or bottom band


def detect(page_lines: list[list[MarginLine]], pages: int) -> set[str]:
    """Return the margin keys to strip, given the margin lines found on each page."""
    seen: dict[str, int] = defaultdict(int)
    for lines in page_lines:
        for key in {ln.key for ln in lines}:
            seen[key] += 1
    threshold = min_repeats(pages)
    strip = {key for key, n in seen.items() if key == PAGE_NUMBER_KEY or n >= threshold}
    # A row mate must recur (on 2+ pages): a body line that happens to share the row
    # with a page number once is content, not a footer.
    row_mates: dict[str, int] = defaultdict(int)
    for lines in page_lines:
        rows = [ln.y for ln in lines if ln.band and ln.key in strip]
        mates = {
            ln.key for ln in lines if ln.band and any(abs(ln.y - y) <= ROW_TOLERANCE for y in rows)
        }
        for key in mates - strip:
            row_mates[key] += 1
    return strip | {key for key, n in row_mates.items() if n >= 2}
