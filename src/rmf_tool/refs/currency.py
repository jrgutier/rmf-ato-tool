"""REF-007 and REF-008: reference currency, checked offline against the committed text.

REF-007 (error): a pinned PDF's ``revision`` is vague or has no month-and-year or ISO date,
its ``revision_stamp`` is missing (unless ``revision_source`` exempts it, with a reason), does
not resolve in the text extraction through ``refs.show.page``, or does not show the revision:
the anchor must contain the revision's latest full date (its latest month and year when it
has none, its year when it has neither). What the
document says about its own revision is read wherever it sits, so moving the stamp cannot hide
it: the highest ``Change N`` on pages 1, 2 or the stamp page with its date, the ``INCLUDES
UPDATES AS OF`` date anywhere, and the latest date of an errata table must all be named.
REF-008 (warning): a control in the pinned OSCAL catalog is absent from the text of a PDF that
describes the same catalog and the entry's ``oscal_only_controls`` does not declare it.
"""

from __future__ import annotations

import datetime
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from rmf_tool.findings import Finding
from rmf_tool.refs import INDEX_PATH, show

RULES = ("REF-007", "REF-008")
CATALOG_ID = "OSCAL-CATALOG-53R5"
# PDFs that describe the SP 800-53 Rev. 5 catalog.
CATALOG_PDFS = ("SP800-53R5", "SP800-53AR5", "SP800-53B")

_MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
          r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
# A revision names a date: month and year ("May 2010", "January 23, 2020") or ISO.
DATED = re.compile(rf"\b{_MONTH}\.?\s+(?:\d{{1,2}},?\s+)?\d{{4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b")
# "Change 1" is exact; a bare "changes", "updates" or "updated" is not.
VAGUE = re.compile(
    r"\bchanges?\b(?!\s+\d)|\bupdates?\b(?!\s+as of)|\bupdated\b|\bas amended\b|\bdraft\b"
    r"|\bcurrent\b|\blatest\b|\bpending\b|\brecord(?:ed)? (?:the |at )|\bTBD\b|\bunknown\b",
    re.IGNORECASE)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_MONTH_YEAR = re.compile(rf"\b({_MONTH})\.?,?\s+(\d{{4}})\b", re.I)
_MONTHS = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
# The number in "Version 2 March 2024" or "Rev. 5 September 2020" is not a day. Words such as
# "Effective" or "dated" may precede a real day, so this stays a list of labels.
_NOT_A_DAY = (r"(?<![.\d])(?<!Rev )(?<!Rev\. )(?<!Revision )(?<!Version )(?<!Vol )(?<!Vol\. )"
              r"(?<!Volume )(?<!Change )(?<!Release )(?<!Attachment )(?<!Section )")
_FULL_DATES = (
    # (regex, groups -> (year, month, day))
    (re.compile(rf"\b({_MONTH})\.?\s+(\d{{1,2}}),?\s+(\d{{4}})\b", re.I),
     lambda m: (m[3], _MONTHS[m[1][:3].lower()], m[2])),
    (re.compile(rf"{_NOT_A_DAY}\b(\d{{1,2}})\s+({_MONTH})\.?,?\s+(\d{{4}})\b", re.I),
     lambda m: (m[3], _MONTHS[m[2][:3].lower()], m[1])),
    (re.compile(r"\b(\d{4})[-.](\d{2})[.-](\d{2})\b"), lambda m: (m[1], m[2], m[3])),
    (re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b"), lambda m: (m[3], m[1], m[2])),
)
# A stamp, not a mention: "Incorporating Change 2", "Change 2 Effective", "Change 2," at line start.
_CHANGE = re.compile(r"\bIncorporating\s+Change\s+(\d+)\b|\bChange\s+(\d+)\s+Effective\b"
                     r"|^\s*Change\s+(\d+),", re.I | re.M)
# Upper case only: the lower-case form is a bibliography citing another document.
_UPDATES_AS_OF = re.compile(r"INCLUDES\s+UPDATES\s+AS\s+OF\s+([^\n]{0,40})")
_ERRATA_HEADING = re.compile(r"#*\s*Errata(?:\s+(?:Sheet|Updates?))?\s*", re.I)
_CONTROL = re.compile(r"\b([A-Z]{2})-(\d{1,2})(?:\((\d{1,2})\))?(?!\d)")
_OSCAL_ID = re.compile(r"([a-z]{2})-(\d+)(?:\.(\d+))?")


def _control(family: str, number: str, enhancement: str | None) -> str:
    """``AC-02(01)`` and ``ac-2.1`` both become ``AC-2(1)``."""
    suffix = f"({int(enhancement)})" if enhancement else ""
    return f"{family.upper()}-{int(number)}{suffix}"


def full_dates(text: str) -> set[tuple[int, int, int]]:
    """Every day-precise date in ``text`` as (year, month, day), in any of four notations."""
    out: set[tuple[int, int, int]] = set()
    for rx, conv in _FULL_DATES:
        for m in rx.finditer(text):
            year, month, day = (int(x) for x in conv(m))
            try:
                datetime.date(year, month, day)
            except ValueError:
                continue
            out.add((year, month, day))
    return out


def month_years(text: str) -> set[tuple[int, int]]:
    """Every (year, month) written as a month and year in ``text``."""
    return {(int(m[2]), _MONTHS[m[1][:3].lower()]) for m in _MONTH_YEAR.finditer(text)}


def _first_line(body: str) -> str:
    """The first line of a page after its ``<!-- page N -->`` marker."""
    return next((line for line in body.splitlines()[1:] if line.strip()), "")


def _errata_dates(pages: dict[int, str]) -> set[tuple[int, int, int]]:
    """Dates in an errata table: the page headed Errata and the pages its table runs onto."""
    out: set[tuple[int, int, int]] = set()
    for number in sorted(pages):
        if _ERRATA_HEADING.fullmatch(_first_line(pages[number])):
            out |= full_dates(pages[number])
            number += 1
            while _first_line(pages.get(number, "")).startswith("|"):
                out |= full_dates(pages[number])
                number += 1
    return out


def _change_number(match: re.Match[str]) -> int:
    return int(next(g for g in match.groups() if g))


def text_controls(text: str) -> set[str]:
    return {_control(*m.groups()) for m in _CONTROL.finditer(text)}


def catalog_controls(catalog: dict[str, Any]) -> set[str]:
    def walk(controls: list[dict[str, Any]]) -> Iterator[str]:
        for c in controls:
            m = _OSCAL_ID.fullmatch(c["id"])
            if m:
                yield _control(*m.groups())
            yield from walk(c.get("controls", []))

    return {c for g in catalog["catalog"]["groups"] for c in walk(g["controls"])}


def _ref007(root: Path, entry: Any) -> list[Finding]:
    ref_id = entry["id"]
    revision = entry["revision"]
    out = []

    def fail(message: str) -> None:
        out.append(Finding("REF-007", "E", f"{ref_id}: {message}", INDEX_PATH))

    if VAGUE.search(revision):
        fail(f"revision {revision!r} is vague; state the edition, date and change number "
             "the text shows")
        return out
    if not DATED.search(revision):
        fail(f"revision {revision!r} is vague (no month and year or ISO date); state the "
             "edition, date and change number the text shows")
        return out
    stamp = entry.get("revision_stamp")
    if stamp is None:
        if "revision_source" not in entry:
            fail("no revision_stamp; point it at the passage that shows the revision, or "
                 "declare revision_source with the reason none exists")
        return out
    if "revision_source" in entry:
        fail("has both revision_stamp and revision_source; drop revision_source")
    try:
        show.page(root, entry, stamp["page"], stamp["anchor"])
    except show.NotFound as exc:
        fail(f"revision_stamp: {exc}")
        return out
    anchor = stamp["anchor"]
    stated = full_dates(revision)
    years = _YEAR.findall(revision)
    if stated:
        if max(stated) not in full_dates(anchor):
            y, m, d = max(stated)
            fail(f"revision_stamp anchor {anchor!r} does not show {y}-{m:02d}-{d:02d}, the "
                 f"latest date of revision {revision!r}")
            return out
    elif month_years(revision):
        if max(month_years(revision)) not in month_years(anchor):
            y, m = max(month_years(revision))
            fail(f"revision_stamp anchor {anchor!r} does not show {y}-{m:02d}, the latest "
                 f"month of revision {revision!r}")
            return out
    elif years and max(years) not in anchor:
        fail(f"revision_stamp anchor {anchor!r} does not show {max(years)}, the latest "
             f"year of revision {revision!r}")
        return out
    pages = show.pages(root, entry)
    front = "\n".join(pages.get(n, "") for n in sorted({1, 2, stamp["page"]}))
    latest = max(_CHANGE.finditer(front), key=_change_number, default=None)
    if latest is not None:
        number = _change_number(latest)
        if not re.search(rf"\bchange\s+{number}\b", revision, re.I):
            fail(f"the text shows Change {number}; revision {revision!r} does not name it")
            return out
        following = [line for line in front[latest.end():].splitlines() if line.strip()][:2]
        effective = next(filter(None, map(full_dates, following)), set())
        if effective and not effective & stated:
            y, mo, d = max(effective)
            fail(f"the text dates Change {number} {y}-{mo:02d}-{d:02d}; revision {revision!r} "
                 "does not name that date")
            return out
    for m in _UPDATES_AS_OF.finditer("\n".join(pages.values())):
        listed = sorted(full_dates(m[1]))
        if listed and listed[-1] not in stated:
            y, mo, d = listed[-1]
            fail(f"the text shows updates as of {y}-{mo:02d}-{d:02d}; revision {revision!r} "
                 "does not name that date")
            return out
    errata = _errata_dates(pages)
    if errata and max(errata) not in stated:
        y, mo, d = max(errata)
        fail(f"the errata table runs to {y}-{mo:02d}-{d:02d}; revision {revision!r} does not "
             "name that date")
    return out


def _ref008(root: Path, index: Any) -> list[Finding]:
    by_id = {e["id"]: e for e in index["references"]}
    catalog_entry = by_id.get(CATALOG_ID)
    if catalog_entry is None or not catalog_entry["local_path"]:
        return []
    path = root / catalog_entry["local_path"]
    if not path.is_file():
        return []
    catalog = catalog_controls(json.loads(path.read_text(encoding="utf-8")))
    out = []
    for ref_id in CATALOG_PDFS:
        entry = by_id.get(ref_id)
        if entry is None or entry["status"] != "ok" or not entry.get("text"):
            continue
        absent = catalog - text_controls((root / entry["text"]["path"]).read_text(encoding="utf-8"))
        declared = set(entry.get("oscal_only_controls") or [])
        for label, controls, hint in (
                ("catalog controls absent from the text and not declared in "
                 "oscal_only_controls", absent - declared, "declare them"),
                ("oscal_only_controls present in the text or not in the catalog",
                 declared - absent, "remove them")):
            if controls:
                out.append(Finding("REF-008", "W", f"{ref_id}: {label}: "
                                   f"{', '.join(sorted(controls))} ({hint})", INDEX_PATH))
    return out


def check(root: Path, index: Any) -> list[Finding]:
    findings: list[Finding] = []
    for entry in index["references"]:
        if entry["kind"] == "pdf" and entry["status"] == "ok":
            findings += _ref007(root, entry)
    return findings + _ref008(root, index)
