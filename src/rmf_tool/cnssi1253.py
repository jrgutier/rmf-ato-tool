"""Regenerate ``framework/baselines/cnssi-1253.yaml`` from CNSSI 1253 Appendix D (Tables
D-1..D-20): the NSS privacy control baseline and the per-objective (C/I/A) Low/Moderate/High
security control baselines.

The committed text extraction loses empty table cells, so the column a symbol sits in cannot
be read from it. Cell values therefore come from the PDF's word geometry (each symbol is
placed under the nearest L/M/H header of the page) and are then checked cell for cell
against ``references/text/CNSSI1253.md``: per row, the ordered sequence of ``X``/``+``/``--``
cells must match. A row that cannot be read or disagrees with the text needs an entry in
``framework/baselines/cnssi-1253.overrides.yaml``; an override that changes nothing fails.

    uv run python -m rmf_tool.cnssi1253           # rewrite the YAML, print a summary
    uv run python -m rmf_tool.cnssi1253 --check   # exit 1 when the YAML is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from rmf_tool import catalog

REF = "CNSSI1253"
PDF_PATH = "references/pdf/CNSSI1253.pdf"
TEXT_PATH = "references/text/CNSSI1253.md"
YAML_PATH = "framework/baselines/cnssi-1253.yaml"
OVERRIDES_PATH = "framework/baselines/cnssi-1253.overrides.yaml"
PROFILE_PATHS = {
    level: f"references/oscal/profiles/NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json"
    for level in ("low", "moderate", "high")
}
FIRST_TABLE_PAGE = 25  # Table D-1 (printed page D-4)

OBJECTIVES = ("c", "i", "a")
LEVELS = ("L", "M", "H")
COLUMNS = tuple(f"{o}{lv}" for o in OBJECTIVES for lv in LEVELS)
SYMBOLS = {"X": "X", "+": "+", "--": "-"}  # table symbol -> YAML cell character
BLANK = "."
_ID = re.compile(r"^([A-Z]{2})-(\d+)(?:\((\d+)\))?$")
_TEXT_ID = re.compile(r"^([A-Z]{2}-\d+(?:\(\d+\))?)(?:\s|$)")
_TABLE = re.compile(r"^Table (D-\d+): (.+)$")
_PAGE = re.compile(r"^<!-- page (\d+)(?: [^>]*)? -->$")
_TOLERANCE = 6.0  # points between a symbol's centre and its column centre
_ID_MAX_X = 90.0  # the ID column's right edge


# CNSSI 1253 Appendix E overlays the references hold, by reference ID (the form C-2 records in
# facts.yaml categorization.overlays). The Classified System Overlay's Table 1 is a plain
# add-list. The Privacy Overlay selects one of four control sets (its §4.1 two questions), so
# it is transcribed as one overlay per set, `<ref>-<SET>` (ADR-0003); the bare reference ID
# stays listed untranscribed so an old pick fails with a pointer to the sets. The Space
# Platform Overlay selects per condition and is not machine-readable yet.
OVERLAYS = {
    "CNSSI1253E-ATT5-CLASSIFIED": "Classified System Overlay",
    "CNSSI1253F-ATT2-SPACE": "Space Platform Overlay",
    "CNSSI1253F-ATT6-PRIVACY": "Privacy Overlay",
}
CLASSIFIED = "CNSSI1253E-ATT5-CLASSIFIED"
_CLASSIFIED_TITLE = "Table 1: Classified System Overlay Summary of Control Specifications"
_CLASSIFIED_END = "Table 2: Controls with Implementation Considerations"
_OVERLAY_MARK = re.compile(r"^\+[GRV]*$")
PRIVACY = "CNSSI1253F-ATT6-PRIVACY"
# Table 2 columns 3..6, in order: (overlay ID suffix, title of the control set)
PRIVACY_SETS = (("ACCT", "Accountability (ACCT)"), ("LOW", "Low"), ("MODERATE", "Moderate"),
                ("HIGH", "High"))
_PRIVACY_TITLE = "Table 2: Privacy Overlays Security and Privacy Controls"
_PRIVACY_END = "Detailed Overlays Control Specifications"
# Rows whose printed control name is not the catalog title of their printed ID. The ID wins.
_PRIVACY_ERRATA = {
    "ia-2.6": "the row repeats IA-2(5)'s name (Individual Authentication with Group "
              "Authentication)",
    "pt-8": "the row says 'Requirement'; the catalog title is 'Computer Matching Requirements'",
}


# CNSSI 1253 makes the NSS privacy control baseline apply to every NSS (cited in the YAML).
PRIVACY_BASELINE_QUOTES = (
    (14, "Include the NSS privacy control baseline contained in Appendix D Tables D-1 through "
         "D-20, which is a default for all NSS."),
    (10, "All systems will implement the NSS privacy control baseline to manage organizational "
         "PII risks."),
    (22, 'Controls indicated with an "X" or a "+" in this column are required for all NSS.'),
)


class ExtractError(Exception):
    """Appendix D cannot be regenerated without a new override or a code fix."""


def oscal_id(table_id: str) -> str:
    m = _ID.match(table_id)
    if not m:
        raise ExtractError(f"not a control id: {table_id!r}")
    fam, num, enh = m.groups()
    return f"{fam.lower()}-{int(num)}" + (f".{int(enh)}" if enh else "")


@dataclass
class Row:
    page: int
    table_id: str  # as printed: AC-2(4)
    privacy: str = BLANK
    cells: dict[str, str] = field(default_factory=lambda: dict.fromkeys(COLUMNS, BLANK))
    withdrawn: bool = False
    y: float = 0.0

    @property
    def id(self) -> str:
        return oscal_id(self.table_id)

    def sequence(self) -> list[str]:
        """Symbols in reading order (privacy column first), as the text extraction has them."""
        return [s for s in (self.privacy, *(self.cells[c] for c in COLUMNS)) if s != BLANK]

    def objective(self, obj: str) -> str:
        return "".join(self.cells[f"{obj}{lv}"] for lv in LEVELS)


# --- PDF geometry ------------------------------------------------------------------------


def _centre(w: Any) -> tuple[float, float]:
    return (w[0] + w[2]) / 2, (w[1] + w[3]) / 2


def _header(words: list[Any]) -> list[float] | None:
    """Centres of the nine L/M/H column headers (C, I, A), or None on a page without one."""
    lines: dict[int, list[Any]] = defaultdict(list)
    for w in words:
        if w[4] in LEVELS:
            lines[round(w[1])].append(w)
    for line in lines.values():
        if len(line) == 9:
            line.sort(key=lambda w: w[0])
            if "".join(w[4] for w in line) == "LMH" * 3:
                return [_centre(w)[0] for w in line]
    return None


def _privacy_column(words: list[Any]) -> float | None:
    """The rotated "Privacy Control Baseline" header is the leftmost rotated "Privacy"."""
    rotated = [w for w in words if w[4] == "Privacy" and (w[3] - w[1]) > (w[2] - w[0])]
    return min(_centre(w)[0] for w in rotated) if rotated else None


def pdf_rows(pdf: Path) -> list[Row]:
    import pymupdf

    rows: list[Row] = []
    centres: list[float] | None = None
    privacy_x: float | None = None
    with pymupdf.open(pdf) as doc:
        for pno in range(FIRST_TABLE_PAGE, doc.page_count + 1):
            words: Any = doc[pno - 1].get_text("words")
            centres = _header(words) or centres  # a continuation page repeats no header
            privacy_x = _privacy_column(words) or privacy_x
            ids = sorted((w for w in words if _ID.match(w[4]) and w[2] < _ID_MAX_X),
                         key=lambda w: w[1])
            if not ids:
                continue
            if centres is None or privacy_x is None:
                raise ExtractError(f"page {pno}: no L/M/H column header found")
            page_rows = [Row(pno, w[4], y=_centre(w)[1]) for w in ids]
            top = min(r.y for r in page_rows) - 15
            for w in words:
                x, y = _centre(w)
                if y < top or w[2] < _ID_MAX_X:
                    continue
                row = min(page_rows, key=lambda r: abs(r.y - y))
                if w[4] == "Withdrawn":
                    row.withdrawn = True
                if w[4] not in SYMBOLS:
                    continue
                dist = [abs(x - c) for c in centres]
                k = min(range(9), key=dist.__getitem__)
                if dist[k] < _TOLERANCE:
                    if row.cells[COLUMNS[k]] != BLANK:
                        raise ExtractError(f"page {pno} {row.table_id}: two symbols in "
                                           f"column {COLUMNS[k]}")
                    row.cells[COLUMNS[k]] = SYMBOLS[w[4]]
                elif abs(x - privacy_x) < _TOLERANCE:
                    row.privacy = SYMBOLS[w[4]]
                elif x < centres[-1] + 2 * _TOLERANCE:
                    raise ExtractError(f"page {pno} {row.table_id}: symbol {w[4]!r} at "
                                       f"x={x:.1f} is under no column")
            rows += page_rows
    return rows


# --- text extraction ---------------------------------------------------------------------


@dataclass
class TextTables:
    sequences: dict[tuple[int, str], list[str]]  # (page, table id) -> symbols in order
    titles: dict[str, tuple[int, str]]  # family (AC) -> (page, "Table D-1: ... Family")


def text_tables(md: Path) -> TextTables:
    sequences: dict[tuple[int, str], list[str]] = {}
    titles: dict[str, tuple[int, str]] = {}
    page = 0
    current: tuple[int, str] | None = None
    for line in md.read_text(encoding="utf-8").splitlines():
        m = _PAGE.match(line)
        if m:
            page, current = int(m.group(1)), None
            continue
        if page < FIRST_TABLE_PAGE:
            continue
        t = _TABLE.match(line.strip())
        if t:
            fam = re.search(r"\(([A-Z]{2})\) Family$", t.group(2))
            if fam:
                titles[fam.group(1)] = (page, line.strip())
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        ident = next((m.group(1) for c in cells[:3] if (m := _TEXT_ID.match(c))), None)
        if ident:
            current = (page, ident)
            sequences.setdefault(current, [])
        if current is not None:
            sequences[current] += [SYMBOLS[c] for c in cells if c in SYMBOLS]
    return TextTables(sequences, titles)


def classified_overlay(md: Path) -> dict[int, list[str]]:
    """Table 1 of the Classified System Overlay: page -> controls marked ``+`` (select)."""
    pages: dict[int, list[str]] = defaultdict(list)
    page, inside = 0, False
    for line in md.read_text(encoding="utf-8").splitlines():
        m = _PAGE.match(line)
        if m:
            page = int(m.group(1))
            continue
        if line.strip() == _CLASSIFIED_TITLE:
            inside = True
        elif line.strip() == _CLASSIFIED_END:
            break
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        ident = next((m.group(1) for c in cells[:2] if (m := _TEXT_ID.match(c))), None)
        if ident is None:
            continue
        if not any(_OVERLAY_MARK.match(c) for c in cells):
            raise ExtractError(f"{CLASSIFIED} page {page} {ident}: no '+' specification cell")
        pages[page].append(ident)
    if not pages:
        raise ExtractError(f"{CLASSIFIED}: {_CLASSIFIED_TITLE!r} not found")
    return dict(pages)


def _name_key(s: str) -> str:
    # "(MAINTENANCE) POLICY AND PROCEDURES": Table 2 prefixes the family to each -1 control.
    s = re.sub(r"^\s*[(\[][^)\]]*[)\]]\s*(?=POLICIES AND PROCEDURES|POLICY AND PROCEDURES)", "",
               s)
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _catalog_name(controls: dict[str, dict[str, Any]], cid: str) -> str:
    """The name Table 2 prints: the title, prefixed by the parent's title for an enhancement."""
    title = controls[cid]["title"]
    return f"{controls[cid.split('.')[0]]['title']} {title}" if "." in cid else title


@dataclass(frozen=True)
class PrivacyRow:
    page: int
    id: str  # OSCAL control ID
    anchor: str | None  # the printed ID when one cell holds all of it (a usable page anchor)
    marks: tuple[str, ...]  # the ACCT, Low, Mod and High cells


def _privacy_rows(md: Path) -> list[tuple[int, list[str]]]:
    rows, page, inside = [], 0, False
    for line in md.read_text(encoding="utf-8").splitlines():
        m = _PAGE.match(line)
        if m:
            page = int(m.group(1))
            continue
        if line.strip() == _PRIVACY_TITLE:
            inside = True
        elif line.strip() == _PRIVACY_END:
            break
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if len(cells) != 7:
            raise ExtractError(f"{PRIVACY} page {page}: Table 2 row with {len(cells)} cells")
        if cells[1] in ("---", "Control Name") or cells[2] == "ACCT" or cells[0] == "Control":
            continue  # the header repeated on every page
        rows.append((page, cells))
    if not rows:
        raise ExtractError(f"{PRIVACY}: {_PRIVACY_TITLE!r} not found")
    return rows


def privacy_overlay(md: Path, controls: dict[str, dict[str, Any]]) -> list[PrivacyRow]:
    """Table 2 of the Privacy Overlays: the rows that select a control in some control set.

    The extraction sometimes prints an ID on the row after its name, or splits it over two
    rows (``AC-`` then ``3(11)``); both are joined back. A row without an ID is identified by
    its name. A row with an ID must carry that control's catalog name, or be listed in
    ``_PRIVACY_ERRATA``."""
    raw = _privacy_rows(md)
    by_name: dict[str, list[str]] = defaultdict(list)
    for cid in controls:
        by_name[_name_key(_catalog_name(controls, cid))].append(cid)
    out: list[PrivacyRow] = []
    used_errata: set[str] = set()
    problems: list[str] = []
    i = 0
    while i < len(raw):
        page, cells = raw[i]
        i += 1
        if not cells[1]:
            if any(cells[2:]) or not _ID.match(re.sub(r"\s", "", cells[0])):
                problems.append(f"page {page}: stray row {cells!r}")
            continue  # an ID printed below a row that already had one: checked by name
        printed = re.sub(r"\s", "", cells[0])
        pieces = [cells[0]] if cells[0] else []
        while (not printed or printed.endswith("-")) and i < len(raw) \
                and not raw[i][1][1] and not any(raw[i][1][2:]):
            printed += re.sub(r"\s", "", raw[i][1][0])
            pieces.append(raw[i][1][0])
            i += 1
        marks = tuple(cells[2:6])
        if not any(c.startswith("+") for c in marks):
            continue
        name = cells[1].replace("\\|", " ")
        if printed:
            if not _ID.match(printed):
                problems.append(f"page {page}: unreadable ID {printed!r} ({name})")
                continue
            cid = oscal_id(printed)
            if cid not in controls:
                problems.append(f"page {page}: {printed} is not in the SP 800-53r5 catalog")
                continue
            if _name_key(_catalog_name(controls, cid)) != _name_key(name):
                if cid not in _PRIVACY_ERRATA:
                    problems.append(f"page {page}: {printed} is named {name!r}")
                    continue
                used_errata.add(cid)
        else:
            found = by_name.get(_name_key(name), [])
            if len(found) != 1:
                problems.append(f"page {page}: no single catalog control named {name!r}")
                continue
            cid = found[0]
        anchor = pieces[0] if len(pieces) == 1 and _ID.match(pieces[0]) else None
        out.append(PrivacyRow(page, cid, anchor, marks))
    problems += [f"erratum for {cid} matched no row" for cid in _PRIVACY_ERRATA
                 if cid not in used_errata]
    seen = [r.id for r in out]
    problems += [f"{cid} appears twice" for cid in sorted({c for c in seen if seen.count(c) > 1})]
    if problems:
        raise ExtractError(f"{PRIVACY} Table 2: " + "; ".join(problems))
    return out


def privacy_sets(rows: list[PrivacyRow]) -> dict[str, dict[int, list[PrivacyRow]]]:
    """Control set suffix -> page -> the rows that set selects (a cell starting with "+")."""
    sets: dict[str, dict[int, list[PrivacyRow]]] = {}
    for k, (suffix, _) in enumerate(PRIVACY_SETS):
        pages: dict[int, list[PrivacyRow]] = defaultdict(list)
        for r in rows:
            if r.marks[k].startswith("+"):
                pages[r.page].append(r)
        sets[suffix] = dict(pages)
    return sets


# --- overrides, cross-checks, output -----------------------------------------------------


def _read_yaml(path: Path) -> Any:
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


_OVERRIDE_KEYS = {"page", "table_id", "reason", "privacy", "c", "i", "a", "withdrawn",
                  "text_differs"}


def _override_problem(o: Any) -> str | None:
    if not isinstance(o, dict):
        return "an override must be a mapping"
    if set(o) - _OVERRIDE_KEYS:
        return f"unknown key(s) {sorted(set(o) - _OVERRIDE_KEYS)}"
    if not (isinstance(o.get("page"), int) and isinstance(o.get("table_id"), str)
            and isinstance(o.get("reason"), str) and o["reason"].strip()):
        return "page, table_id and reason are required"
    if "privacy" in o and not re.fullmatch(r"[.X+-]", str(o["privacy"])):
        return "privacy must be one of . X + -"
    if any(obj in o and not re.fullmatch(r"[.X+-]{3}", str(o[obj])) for obj in OBJECTIVES):
        return "c, i and a must be three of . X + - (low, moderate, high)"
    return None


def apply_overrides(rows: list[Row], overrides: list[dict[str, Any]]) -> set[tuple[int, str]]:
    """Apply hand corrections; returns the (page, table id) rows they cover."""
    index = {(r.page, r.table_id): r for r in rows}
    covered: set[tuple[int, str]] = set()
    for o in overrides:
        problem = _override_problem(o)
        if problem:
            raise ExtractError(f"{OVERRIDES_PATH}: {problem}: {o!r}")
        key = (o["page"], o["table_id"])
        row = index.get(key)
        if row is None:
            raise ExtractError(f"override for {key[1]} on page {key[0]}: no such row")
        before = (row.privacy, dict(row.cells), row.withdrawn)
        row.withdrawn = bool(o.get("withdrawn", row.withdrawn))
        row.privacy = o.get("privacy", row.privacy)
        for obj in OBJECTIVES:
            if obj in o:
                for lv, ch in zip(LEVELS, o[obj], strict=True):
                    row.cells[f"{obj}{lv}"] = ch
        if (row.privacy, row.cells, row.withdrawn) == before and not o.get("text_differs"):
            raise ExtractError(f"override for {key[1]} on page {key[0]} changes nothing; "
                               "remove it")
        covered.add(key)
    return covered


def cross_check_text(rows: list[Row], text: TextTables, covered: set[tuple[int, str]]
                     ) -> list[str]:
    problems = []
    for r in rows:
        key = (r.page, r.table_id)
        if key in covered:
            continue
        if key not in text.sequences:
            problems.append(f"page {r.page} {r.table_id}: row not found in {TEXT_PATH}")
        elif text.sequences[key] != r.sequence():
            problems.append(f"page {r.page} {r.table_id}: text has {text.sequences[key]}, "
                            f"PDF geometry gives {r.sequence()}")
    return problems


def selected(rows: list[Row], obj: str, level: str) -> set[str]:
    """Controls with X or + in the objective's column for ``level`` (L/M/H)."""
    return {r.id for r in rows if r.cells[f"{obj}{level}"] in "X+"}


def nist_marked(rows: list[Row], level: str) -> set[str]:
    """Controls the table marks as in the SP 800-53B baseline at ``level`` (X or --)."""
    return {r.id for r in rows for o in OBJECTIVES if r.cells[f"{o}{level}"] in "X-"}


def profile_ids(repo: Path, level: str) -> set[str]:
    doc = json.loads((repo / PROFILE_PATHS[level]).read_text(encoding="utf-8"))
    return {cid for imp in doc["profile"].get("imports") or []
            for inc in imp.get("include-controls") or [] for cid in inc.get("with-ids") or []}


def nist_differences(repo: Path, rows: list[Row]) -> dict[str, dict[str, list[str]]]:
    """Per level: 800-53B profile controls the table does not mark, and the reverse."""
    out = {}
    for name, level in (("low", "L"), ("moderate", "M"), ("high", "H")):
        marked, profile = nist_marked(rows, level), profile_ids(repo, name)
        out[name] = {"profile_only": sorted(profile - marked, key=catalog.sort_key),
                     "table_only": sorted(marked - profile, key=catalog.sort_key)}
    return out


def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _privacy_blocks(pages: dict[int, list[PrivacyRow]]) -> list[str]:
    out = []
    for n, (page, rows) in enumerate(pages.items()):
        anchor = _PRIVACY_TITLE if n == 0 else next((r.anchor for r in rows if r.anchor), None)
        if anchor is None:
            raise ExtractError(f"{PRIVACY} page {page}: no printed ID to cite as the anchor")
        out += [f"      - citation: {{ref: {PRIVACY}, page: {page}, anchor: {_q(anchor)}}}",
                f"        add: [{', '.join(r.id for r in rows)}]"]
    return out


def render(rows: list[Row], text: TextTables, classified: dict[int, list[str]],
           privacy: dict[str, dict[int, list[PrivacyRow]]]) -> str:
    out = [
        f"# {YAML_PATH}: GENERATED by `uv run python -m rmf_tool.cnssi1253`; do not edit.",
        "# Cell values come from the PDF's table geometry and are checked cell for cell",
        f"# against {TEXT_PATH}; hand corrections live in {OVERRIDES_PATH}.",
        "# Schema: framework/schema/baselines.schema.json (ADR-0002).",
        "baseline: CNSSI-1253",
        "title: CNSSI No. 1253 Appendix D, NSS Control Baselines (Tables D-1 to D-20)",
        f"ref: {REF}",
        "citations:",
        f"  - {{ref: {REF}, section: \"3.2.1\"}}",
        f"  - {{ref: {REF}, page: 23, anchor: \"Identifies a control needed to protect NSS\"}}",
        "  # The privacy column applies to every NSS; PII-specific controls are in the Privacy",
        "  # Overlay instead, which applies only on an SAOP determination (page 6).",
        *(f"  - {{ref: {REF}, page: {page}, anchor: {_q(quote)}}}"
          for page, quote in PRIVACY_BASELINE_QUOTES),
        "cells:",
        "  order: [low, moderate, high]",
        "  legend:",
        "    X: in the SP 800-53B baseline and the NSS baseline",
        "    \"+\": added to the NSS baseline by CNSSI 1253",
        "    \"-\": in the SP 800-53B baseline but not selected for the NSS baseline",
        "    \".\": not selected",
        "tables:",
    ]
    by_family: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        by_family[r.table_id[:2]].append(r)
    for n, (fam, fam_rows) in enumerate(by_family.items(), start=1):
        if fam not in text.titles:
            raise ExtractError(f"no 'Table D-n: ... ({fam}) Family' title in {TEXT_PATH}")
        title_page, title = text.titles[fam]
        table_id, table_title = _TABLE.match(title).groups()  # type: ignore[union-attr]
        if table_id != f"D-{n}":
            raise ExtractError(f"{title!r} is table {n} in page order")
        out += [f"  - table: {table_id}", f"    family: {fam.lower()}",
                f"    title: {_q(table_title)}", "    blocks:"]
        pages: dict[int, list[Row]] = defaultdict(list)
        for r in fam_rows:
            pages[r.page].append(r)
        for page, page_rows in pages.items():
            anchor = title if page == title_page else page_rows[0].table_id
            out += [f"      - citation: {{ref: {REF}, page: {page}, anchor: {_q(anchor)}}}",
                    "        controls:"]
            for r in page_rows:
                if r.withdrawn:
                    out.append(f"          - {{id: {r.id}, withdrawn: true}}")
                    continue
                cia = ", ".join(f"{o}: {_q(r.objective(o))}" for o in OBJECTIVES)
                out.append(f"          - {{id: {r.id}, privacy: {_q(r.privacy)}, {cia}}}")
    out.append("overlays:")
    for ref, title in OVERLAYS.items():
        out += [f"  - id: {ref}", f"    title: {title}", f"    ref: {ref}",
                f"    transcribed: {'true' if ref == CLASSIFIED else 'false'}"]
        if ref == CLASSIFIED:
            out.append("    blocks:")
            for n, (page, ids) in enumerate(classified.items()):
                anchor = _CLASSIFIED_TITLE if n == 0 else ids[0]
                out += [f"      - citation: {{ref: {ref}, page: {page}, anchor: {_q(anchor)}}}",
                        f"        add: [{', '.join(oscal_id(i) for i in ids)}]"]
        elif ref == PRIVACY:
            for suffix, set_title in PRIVACY_SETS:
                out += [f"  - id: {ref}-{suffix}", f"    title: {title}, {set_title} control set",
                        f"    ref: {ref}", "    transcribed: true", "    blocks:",
                        *_privacy_blocks(privacy[suffix])]
    return "\n".join(out) + "\n"


@dataclass
class Result:
    rows: list[Row]
    text: str
    nist: dict[str, dict[str, list[str]]]
    classified: int  # controls the Classified System Overlay adds
    privacy: dict[str, int]  # Privacy Overlay control set suffix -> controls it adds


def generate(repo: Path) -> Result:
    rows = pdf_rows(repo / PDF_PATH)
    seen: dict[str, Row] = {}
    for r in rows:
        if r.id in seen:
            raise ExtractError(f"{r.table_id} appears on pages {seen[r.id].page} and {r.page}")
        seen[r.id] = r
    overrides_path = repo / OVERRIDES_PATH
    overrides = (_read_yaml(overrides_path) or {}).get("overrides") or [] \
        if overrides_path.is_file() else []
    covered = apply_overrides(rows, overrides)
    text = text_tables(repo / TEXT_PATH)
    problems = cross_check_text(rows, text, covered)
    known = catalog.load(repo).controls
    problems += [f"page {r.page} {r.table_id}: {r.id} is not in the SP 800-53r5 catalog"
                 for r in rows if r.id not in known]
    problems += [f"page {r.page} {r.table_id}: withdrawn row has selections"
                 for r in rows if r.withdrawn and r.sequence()]
    classified = classified_overlay(repo / f"references/text/{CLASSIFIED}.md")
    problems += [f"{CLASSIFIED} page {page} {i}: {oscal_id(i)} is not in the catalog"
                 for page, ids in classified.items() for i in ids if oscal_id(i) not in known]
    if problems:
        raise ExtractError(f"{len(problems)} problem(s):\n  " + "\n  ".join(problems))
    privacy = privacy_sets(privacy_overlay(repo / f"references/text/{PRIVACY}.md", known))
    return Result(rows, render(rows, text, classified, privacy), nist_differences(repo, rows),
                  sum(len(ids) for ids in classified.values()),
                  {s: sum(len(rs) for rs in pages.values()) for s, pages in privacy.items()})


def summary(result: Result) -> str:
    rows = [r for r in result.rows if not r.withdrawn]
    lines = [f"{len(result.rows)} rows ({len(result.rows) - len(rows)} withdrawn), "
             f"{len({r.table_id[:2] for r in rows})} families"]
    lines.append(f"privacy baseline: {sum(r.privacy in 'X+' for r in rows)}")
    lines.append(f"{CLASSIFIED}: {result.classified} control(s) added")
    lines.append(f"{PRIVACY}: " + ", ".join(f"{s}={n}" for s, n in result.privacy.items()))
    for obj in OBJECTIVES:
        lines.append(f"{obj}: " + ", ".join(f"{lv}={len(selected(rows, obj, lv))}"
                                             for lv in LEVELS))
    for level, diff in result.nist.items():
        lines.append(f"800-53B {level}: profile-only {diff['profile_only'] or 'none'}; "
                     f"table-only {diff['table_only'] or 'none'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rmf_tool.cnssi1253", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail when the YAML is stale")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        result = generate(args.repo)
    except ExtractError as exc:
        print(f"cnssi1253: {exc}", file=sys.stderr)
        return 2
    target = args.repo / YAML_PATH
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != result.text:
            print(f"{YAML_PATH} is stale; run: uv run python -m rmf_tool.cnssi1253",
                  file=sys.stderr)
            return 1
        print(f"{YAML_PATH} is current")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result.text, encoding="utf-8")
    print(summary(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
