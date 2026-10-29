"""Unit tests for rmf_tool.refs.toc: the §6.7 heading regex set, outline titles, anchors."""

from __future__ import annotations

from pathlib import Path

import pytest

from rmf_tool.refs import toc


def test_task_heading_keeps_statement_in_body() -> None:
    h = toc.match_heading("TASK C-2 Categorize the system and document the security results.")
    assert h == toc.Heading(
        3, "TASK C-2", "C-2", "task", "Categorize the system and document the security results."
    )


def test_task_heading_long_statement_and_case() -> None:
    long = (
        "Task M-2 Assess the controls implemented within and inherited by the system in accordance"
    )
    h = toc.match_heading(long)
    assert h is not None and h.text == "TASK M-2" and h.rest.startswith("Assess the controls")
    assert toc.match_heading("TASK P-18") == toc.Heading(3, "TASK P-18", "P-18", "task", "")
    assert toc.match_heading("TASK X-1 Not an RMF step") is None


@pytest.mark.parametrize(
    ("line", "level", "num"),
    [
        ("2.1 ORGANIZATION-WIDE RISK MANAGEMENT", 2, "2.1"),
        ("3 Categorization of Information and Information Systems", 1, "3"),
        ("1. Introduction", 1, "1"),
        ("3.4.1.2 Deeply Nested Section Title", 4, "3.4.1.2"),
    ],
)
def test_numbered_heading_accepts_heading_lines(line: str, level: int, num: str) -> None:
    h = toc.match_heading(line)
    assert h is not None and (h.level, h.num, h.kind, h.text) == (level, num, "numbered", line)


@pytest.mark.parametrize(
    "line",
    [
        "2 Organizations should not treat this sentence as a heading.",  # trailing period
        "1.2 Overview:",  # trailing colon
        "4 Roles, responsibilities,",  # trailing comma
        "3 Group and role membership; and",  # list item
        "| 1 Control | Name |",  # pipe-table row
        "1 Name | Value",  # pipe inside the title
        "1) First item of a list",
        "(a) Second item of a list",
        "• Bulleted item",
        "- Dashed item",
        "SECTION 1 PURPOSE.....................................1",  # TOC dot leader
        "2 " + "Word " * 14,  # more than 14 words
        "2 " + "X" * 99,  # more than 100 characters
        "2 lowercase start is not a heading",
        "References: [2] [21] [40]",  # a citation line under a section
    ],
)
def test_numbered_heading_rejects_sentence_table_and_list_lines(line: str) -> None:
    assert toc.match_heading(line) is None


def test_heading_needs_blank_line_and_no_table() -> None:
    assert toc.match_heading("2.1 BACKGROUND", prev_blank=False) is None
    assert toc.match_heading("2.1 BACKGROUND", in_table=True) is None
    assert toc.match_heading("2.1 BACKGROUND") is not None


@pytest.mark.parametrize(
    ("line", "kind", "num", "level"),
    [
        ("APPENDIX F SYSTEM AND COMMON CONTROL AUTHORIZATIONS", "appendix", "F", 1),
        ("Appendix B: Glossary", "appendix", "B", 1),
        ("SECTION 3: RESPONSIBILITIES", "section", "3", 1),
        ("ENCLOSURE 2 PROCEDURES", "part", "ENCLOSURE 2", 1),
        ("GLOSSARY", "part", "GLOSSARY", 1),
        ("REFERENCES", "part", "REFERENCES", 1),
        ("AC-2 ACCOUNT MANAGEMENT", "control", "AC-2", 2),
        ("AC-2(1) AUTOMATED SYSTEM ACCOUNT MANAGEMENT", "control", "AC-2(1)", 3),
    ],
)
def test_other_patterns(line: str, kind: str, num: str, level: int) -> None:
    h = toc.match_heading(line)
    assert h is not None and (h.kind, h.num, h.level, h.text) == (kind, num, level, line)
    assert kind in toc.NEEDS_EMPHASIS


def test_control_pattern_requires_upper_case_title() -> None:
    assert toc.match_heading("AC-2 Account management is described below") is None


@pytest.mark.parametrize(
    ("raw", "clean"),
    [
        ("1.1   BACKGROUND", "1.1 BACKGROUND"),
        ("3.1   PREPARE 51F", "3.1 PREPARE"),  # Word footnote reference
        ("3.2   CATEGORIZE73F", "3.2 CATEGORIZE"),
        ("APPENDIX F", "APPENDIX F"),
        ("Expected Outputs:  Organization-level risk assessment results.", None),
        (
            "Quick link to summary table for RMF tasks, responsibilities, and supporting roles.",
            None,
        ),
        ("This publication describes the Risk Management Framework (RMF) and provides...", None),
        ("Discussion: " + "word " * 20, None),
        ("Supporting Roles:", None),
    ],
)
def test_outline_title_filter(raw: str, clean: str | None) -> None:
    assert toc.outline_title(raw) == clean


def test_outline_num() -> None:
    assert toc.outline_num("2.1 ORGANIZATION-WIDE RISK MANAGEMENT") == "2.1"
    assert toc.outline_num("1. Purpose") == "1"
    assert toc.outline_num("INTRODUCTION") == ""


def test_compact_ignores_case_space_and_punctuation() -> None:
    assert toc.compact("3.1   PREPARE—Org") == toc.compact("3 1 prepare org") == "31prepareorg"


def test_slugger_github_style_and_unique() -> None:
    slug = toc.Slugger()
    assert (
        slug("TABLE 1: PREPARE TASKS—ORGANIZATION LEVEL")
        == "table-1-prepare-tasksorganization-level"
    )
    assert slug("2.1 ORGANIZATION-WIDE RISK") == "21-organization-wide-risk"
    assert [slug("TASK P-3"), slug("TASK P-3"), slug("TASK P-3")] == [
        "task-p-3",
        "task-p-3-1",
        "task-p-3-2",
    ]
    assert slug("Task P-3 1") == "task-p-3-1-1"  # never collides with a generated suffix


def test_render_and_load_round_trip(tmp_path: Path) -> None:
    entries = [
        toc.TocEntry(1, 'A "quoted" title — with \\ backslash', 3, "a-quoted-title", "", "outline"),
        toc.TocEntry(3, "TASK C-2", 66, "task-c-2", "C-2", "regex"),
    ]
    path = tmp_path / "X.toc.yaml"
    path.write_text(toc.render_toc("X", entries), encoding="utf-8")
    assert toc.load_toc(path) == entries
    path.write_text(toc.render_toc("X", []), encoding="utf-8")
    assert toc.load_toc(path) == []


def test_load_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "bad.toc.yaml"
    path.write_text("a: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="list"):
        toc.load_toc(path)
