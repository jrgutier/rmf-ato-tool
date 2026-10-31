"""REF-007 and REF-008: reference currency, checked offline against the committed text.

REF-007 (error): a pinned PDF's ``revision`` is vague or has no month-and-year or ISO date,
its ``revision_stamp`` is missing (unless ``revision_source`` exempts it, with a reason), does
not resolve in the text extraction through ``refs.show.page``, or does not show the year the
revision states.
REF-008 (warning): a control in the pinned OSCAL catalog is absent from the text of a PDF that
describes the same catalog and the entry's ``oscal_only_controls`` does not declare it.
"""

from __future__ import annotations

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
_CONTROL = re.compile(r"\b([A-Z]{2})-(\d{1,2})(?:\((\d{1,2})\))?(?!\d)")
_OSCAL_ID = re.compile(r"([a-z]{2})-(\d+)(?:\.(\d+))?")


def _control(family: str, number: str, enhancement: str | None) -> str:
    """``AC-02(01)`` and ``ac-2.1`` both become ``AC-2(1)``."""
    suffix = f"({int(enhancement)})" if enhancement else ""
    return f"{family.upper()}-{int(number)}{suffix}"


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
    elif not DATED.search(revision):
        fail(f"revision {revision!r} is vague (no month and year or ISO date); state the "
             "edition, date and change number the text shows")
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
    years = _YEAR.findall(revision)
    if years and max(years) not in stamp["anchor"]:
        fail(f"revision_stamp anchor {stamp['anchor']!r} does not show {max(years)}, the latest "
             f"year of revision {revision!r}")
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
