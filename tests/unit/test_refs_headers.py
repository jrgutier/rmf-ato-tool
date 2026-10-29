"""Unit tests for rmf_tool.refs.headers: running header/footer detection."""

from __future__ import annotations

import pytest

from rmf_tool.refs import headers
from rmf_tool.refs.headers import PAGE_NUMBER_KEY, MarginLine


def test_normalize_nfkc_controls_and_space() -> None:
    assert (
        headers.normalize("  e\ufb03cient\u00a0 con\u00adtrol\u2028x\t ") == "efficient control x"
    )


def test_pattern_key_masks_digits() -> None:
    assert headers.pattern_key("NIST SP 800-53, REV. 5 SECURITY") == "NIST SP #-#, REV. # SECURITY"
    assert headers.pattern_key("CHAPTER THREE") == "CHAPTER THREE"


@pytest.mark.parametrize(
    "line", ["12", "PAGE 29", "Page 3 of 10", "iv", "- 7 -", " xii ", "B-12", "PAGE D-4", "A.1-3"]
)
def test_pattern_key_page_numbers(line: str) -> None:
    assert headers.pattern_key(line) == PAGE_NUMBER_KEY


def test_bands() -> None:
    assert headers.in_band(44, 792) and headers.in_band(754, 792)  # header, footer baselines
    assert not headers.in_band(717, 792)  # footnotes stay
    assert not headers.in_band(83, 792)  # first body line stays
    assert headers.in_side_band(15, 27, 612) and headers.in_side_band(560, 580, 612)
    assert not headers.in_side_band(90, 523, 612)


def lines(*keys: str, y: float = 750.0, band: bool = True) -> list[MarginLine]:
    return [MarginLine(k, y, band) for k in keys]


def test_detect_requires_repeats() -> None:
    pages = [lines("HEADER"), lines("HEADER"), lines("HEADER") + lines("ONE-OFF", y=40), [], []]
    assert headers.detect(pages, 5) == {"HEADER"}
    assert headers.detect(pages[:2], 2) == {"HEADER"}  # short documents: two pages suffice
    assert headers.detect([lines("HEADER"), lines("HEADER"), [], [], []], 5) == set()


def test_min_repeats_scales_with_length() -> None:
    assert [headers.min_repeats(n) for n in (2, 5, 60, 61, 304, 733)] == [2, 3, 3, 4, 16, 37]


def test_detect_always_strips_page_numbers() -> None:
    assert headers.detect([lines(PAGE_NUMBER_KEY), [], [], [], []], 5) == {PAGE_NUMBER_KEY}


def test_detect_strips_row_mates_of_stripped_lines() -> None:
    footer = [MarginLine("APPENDIX C", 751.0, True), MarginLine(PAGE_NUMBER_KEY, 752.5, True)]
    other_row = [MarginLine("FIGURE TITLE", 700.0, True), MarginLine(PAGE_NUMBER_KEY, 752, True)]
    rotated = [MarginLine("SIDE NOTE", 751.0, False), MarginLine(PAGE_NUMBER_KEY, 751, True)]
    assert headers.detect([footer, footer, [], [], []], 5) == {PAGE_NUMBER_KEY, "APPENDIX C"}
    assert headers.detect([footer, [], [], [], []], 5) == {PAGE_NUMBER_KEY}  # once is content
    assert headers.detect([other_row, other_row, [], [], []], 5) == {PAGE_NUMBER_KEY}
    assert headers.detect([rotated, rotated, [], [], []], 5) == {PAGE_NUMBER_KEY}
