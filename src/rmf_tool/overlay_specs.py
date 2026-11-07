"""Regenerate ``framework/baselines/overlay-specs.yaml`` from Section 6 of the Classified System
Overlay and the Privacy Overlays: per control, the justification to select (or not select, or
recommend), the guidance, the control extension, the parameter values and the
regulatory/statutory references, each tied to the control sets it applies to.

The summary tables mark which of these each control has (``+GRV`` in the Classified Table 1;
``+GVR`` and ``E`` per control set in the Privacy Table 2), so every specification is checked
against its table row: a control in Section 6 must be in the table, a mark must have its
subheading and a subheading its mark. A mismatch fails the generator unless it is listed in
``ERRATA`` with what the document prints.

    uv run python -m rmf_tool.overlay_specs           # rewrite the YAML, print a summary
    uv run python -m rmf_tool.overlay_specs --check   # exit 1 when the YAML is stale
"""

from __future__ import annotations

import argparse
import functools
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rmf_tool import catalog
from rmf_tool.cnssi1253 import CLASSIFIED, PRIVACY, ExtractError, oscal_id
from rmf_tool.yamlload import safe_load

YAML_PATH = "framework/baselines/overlay-specs.yaml"
_PAGE = re.compile(r"^<!-- page (\d+)(?: [^>]*)? -->$")
_HEADING = re.compile(r"^([A-Z]{2}-\d+(?:\(\d+\))?),?\s+(\S.*)$")
_FOOTNOTE = re.compile(r"^\d{1,2} [A-Z]")
_BASELINE_NOTE = re.compile(r"\b(?:Included )?In (?:the )?Privacy Control Baseline", re.I)
# Section 6 of each overlay: the line that opens it and the one that closes it.
SECTIONS = {
    CLASSIFIED: ("# 6. Detailed Overlay Control Specifications",
                 "# 7. Implementation Considerations"),
    PRIVACY: ("Detailed Overlays Control Specifications", "Implementation Considerations"),
}
# Privacy control sets in Table 2 column order, and the words Section 6 names them by.
SETS = ("ACCT", "LOW", "MODERATE", "HIGH", "ENHANCING")
_SET_WORDS = {"acct": "ACCT", "low": "LOW", "moderate": "MODERATE", "mod": "MODERATE",
              "high": "HIGH", "privacy enhancing": "ENHANCING"}
KINDS = ("justification", "extension", "guidance", "parameter")
MARKS = {"guidance": "G", "parameter": "V", "extension": "E"}
_LABEL = re.compile(
    r"^(?:(?P<jus>Justification to (?P<disp>Select|Not Select|Recommend))(?: for (?P<jsets>[^:]+))?"
    r"|(?P<pre>[A-Za-z, ]+? )?"
    r"(?P<kind>Guidance|Discussion|Parameter Values?(?:\(s\))?|Control Extension|Extension)"
    r"(?: for (?P<ksets>[^:]+))?"
    r"|(?P<ref>Regulatory/Statutory Reference\(s\)|Reference\(s\)|References))"
    r":\s*(?P<rest>.*)$")
DISPOSITIONS = {"Select": "select", "Not Select": "not-select", "Recommend": "recommend"}
# Authorities a reference names, in the form a run's law_policy.authorities names them.
AUTHORITIES = (
    (re.compile(r"\bE\.?\s?O\.?\s?(\d{5})"), "EO {0}"),
    (re.compile(r"\bExecutive Order\s+(\d{5})"), "EO {0}"),
    (re.compile(r"\bCNSS([DIP])\s*(?:No\.?)?\s*(\d+)"), "CNSS{0} No. {1}"),
    (re.compile(r"\b5\s*U\.?\s?S\.?\s?C\.?\s*§?\s*552a"), "5 U.S.C. 552a"),
    (re.compile(r"\bPrivacy Act\b"), "5 U.S.C. 552a"),
    (re.compile(r"\bOMB Circular\s*(?:No\.\s*)?(A-\d+)"), "OMB Circular {0}"),
    (re.compile(r"\bOMB\s+(?:Memorandum\s+)?(M-\d{2}-\d{2})"), "OMB {0}"),
    (re.compile(r"\bFISA\b"), "FISA"),
    (re.compile(r"\bE-Government Act\b"), "E-Government Act of 2002"),
    (re.compile(r"\bDoD[DIM]?\s*(\d{4}\.\d{2})"), "DoD {0}"),
    (re.compile(r"\bICD\s*(\d{3})"), "ICD {0}"),
    (re.compile(r"\bNIST SP\s*(800-\d+[A-Z]?)"), "NIST SP {0}"),
    (re.compile(r"\bFIPS\s*(?:PUB\s*)?(\d{3})"), "FIPS {0}"),
    (re.compile(r"\b(\d+)\s*C\.?F\.?R\.?"), "{0} CFR"),
    (re.compile(r"\b(\d+)\s*U\.?\s?S\.?\s?C\.?\s*§*\s*(\d+[a-z]?)(?!\d)"), "{0} U.S.C. {1}"),
    (re.compile(r"\bP(?:ub(?:lic)?)?\.?\s*L(?:aw)?\.?\s*(?:No\.\s*)?(\d+-\d+)"), "Pub. L. {0}"),
    (re.compile(r"\bFISMA\b"), "FISMA"),
    (re.compile(r"\bFAR Parts?\b"), "FAR"),
    (re.compile(r"\bNARA GRS\b"), "NARA GRS"),
    (re.compile(r"\bNISTIR[- ](\d+)"), "NISTIR {0}"),
    (re.compile(r"\bNational Insider Threat Policy\b"), "National Insider Threat Policy"),
    (re.compile(r"\bMinimum Standards for Executive Branch Insider Threat Programs\b"),
     "Minimum Standards for Executive Branch Insider Threat Programs"),
    (re.compile(r"\bPrivacy and Civil Liberties Implementation Guide\b"),
     "Privacy and Civil Liberties Implementation Guide for the ISE"),
    (re.compile(r"\bNSM[- ](\d+)"), "NSM-{0}"),
    (re.compile(r"\bNSPM[- ](\d+)"), "NSPM-{0}"),
)


@dataclass
class Statement:
    kind: str
    text: str
    sets: tuple[str, ...] = ()
    disposition: str | None = None


@dataclass
class Spec:
    control: str
    heading: str
    page: int
    anchor: str
    statements: list[Statement] = field(default_factory=list)
    references: str = ""
    in_privacy_baseline: bool = False


def _sets(words: str | None) -> tuple[str, ...]:
    """The control sets a label names ("ACCT, Low, and Moderate"), in Table 2 order."""
    if not words:
        return ()
    found = set()
    for part in re.split(r",|\band\b|\bor\b", words):
        key = re.sub(r"\s+", " ", part).strip().lower()
        if not key:
            continue
        if key not in _SET_WORDS:
            for word in key.split():  # "Low Moderate" with its comma lost
                if word not in _SET_WORDS:
                    raise ExtractError(f"unknown control set {part.strip()!r} in {words!r}")
                found.add(_SET_WORDS[word])
            continue
        found.add(_SET_WORDS[key])
    return tuple(s for s in SETS if s in found)


def _join(lines: list[str]) -> str:
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if out.endswith("-") and out[-2:-1].isalnum() and (line[:1].islower()
                                                           or line[:1].isdigit()):
            out += line  # a word or compound broken at the line end
        else:
            out = f"{out} {line}" if out else line
    return re.sub(r"\s+", " ", out).strip()


def _table_line(line: str) -> str | None:
    """A table the extraction made of a wrapped paragraph: its cells in reading order."""
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
    if all(re.fullmatch(r"-*", c) for c in cells):
        return None
    return " ".join(c.replace("\\|", "|") for c in cells if c)


def section_lines(md: Path, ref: str) -> list[tuple[int, str]]:
    """(page, line) of Section 6, page markers and blank lines dropped."""
    start, end = SECTIONS[ref]
    out: list[tuple[int, str]] = []
    page, inside, footnote, blank = 0, False, False, True
    for line in md.read_text(encoding="utf-8").splitlines():
        if m := _PAGE.match(line):
            page, footnote = int(m.group(1)), False
            continue
        text = line.strip()
        if text == start:
            inside = True
            continue
        if inside and text == end:
            if out and re.fullmatch(r"\d+", out[-1][1]):
                out.pop()  # the section number printed above the next title
            return out
        # A footnote opens after a blank line with its number and runs to the page end.
        if inside and blank and _FOOTNOTE.match(text):
            footnote = True
        blank = not text
        if not inside or not text or footnote:
            continue
        if text.startswith("|"):
            joined = _table_line(text)
            if joined:
                out.append((page, joined))
            continue
        out.append((page, text))
    raise ExtractError(f"{ref}: Section 6 ({start!r} to {end!r}) not found")


def _is_heading(text: str, known: set[str]) -> str | None:
    m = _HEADING.match(text)
    if not m:
        return None
    try:
        cid = oscal_id(m.group(1))
    except ExtractError:
        return None
    rest = m.group(2)
    # A heading names the control: "AC-11, Device Lock" or "AC-3(9) Access Enforcement | ...".
    if cid not in known or not (rest[:1].isupper() or rest[:1] == "("):
        return None
    return cid


def parse(md: Path, ref: str, known: set[str]) -> list[Spec]:
    """Section 6 of an overlay, one Spec per control heading."""
    lines = section_lines(md, ref)
    specs: list[Spec] = []
    current: Spec | None = None
    block: tuple[str, Statement | None] | None = None  # (kind, statement) being read
    buffer: list[str] = []
    in_heading = False

    def flush() -> None:
        nonlocal buffer
        if block is not None and current is not None:
            kind, statement = block
            text = _join(buffer)
            if kind == "references":
                current.references = _join([current.references, text])
            elif statement is not None:
                statement.text = _join([statement.text, text])
        buffer = []

    for page, text in lines:
        cid = _is_heading(text, known)
        if cid is not None:
            flush()
            block = None
            current = Spec(cid, text, page, text)
            specs.append(current)
            in_heading = True
            current.in_privacy_baseline = bool(_BASELINE_NOTE.search(text))
            continue
        if current is None:
            continue  # the section's boilerplate before the first control
        m = _LABEL.match(text)
        if m is None and in_heading and block is None:
            current.heading = _join([current.heading, text])
            current.in_privacy_baseline = bool(_BASELINE_NOTE.search(current.heading))
            continue
        in_heading = False
        if m is None:
            if block is None:
                raise ExtractError(f"{ref} page {page} {current.control}: text before any "
                                   f"subheading: {text[:70]!r}")
            buffer.append(text)
            continue
        flush()
        rest = m.group("rest")
        if m.group("ref"):
            block = ("references", None)
        elif m.group("jus"):
            statement = Statement("justification", "", _sets(m.group("jsets")),
                                  DISPOSITIONS[m.group("disp")])
            current.statements.append(statement)
            block = ("justification", statement)
        else:
            word = m.group("kind")
            kind = ("guidance" if word in ("Guidance", "Discussion") else
                    "extension" if word.endswith("Extension") else "parameter")
            sets = _sets(m.group("ksets")) or _sets(m.group("pre"))
            statement = Statement(kind, "", sets)
            current.statements.append(statement)
            block = (kind, statement)
        buffer = [rest] if rest else []
    flush()
    return specs


def authorities(references: str) -> list[str]:
    """The authorities a reference string names, normalized and in order of first mention."""
    found: list[tuple[int, str]] = []
    for pattern, form in AUTHORITIES:
        for m in pattern.finditer(references):
            name = form.format(*m.groups())
            if name not in (n for _, n in found):
                found.append((m.start(), name))
    return [n for _, n in sorted(found)]


# --- what a run reads ---------------------------------------------------------------------

TITLES = {CLASSIFIED: "Classified System Overlay", PRIVACY: "Privacy Overlay"}
SELECTING = ("select", "recommend")


@dataclass(frozen=True)
class Applied:
    """One overlay's specification of a control, as it applies to a run's control set."""
    overlay: str
    control: str
    disposition: str  # select, not-select or recommend
    statements: tuple[dict, ...]  # guidance, extension and parameter statements that apply
    authorities: tuple[str, ...]
    references: str
    citation: dict

    @property
    def title(self) -> str:
        return TITLES[self.overlay]


@functools.cache
def _load(path: Path) -> dict[str, dict[str, dict]]:
    data = safe_load(path.read_text(encoding="utf-8"))
    return {o["overlay"]: {s["control"]: s for s in o["specs"]} for o in data["overlays"]}


def load(repo: Path) -> dict[str, dict[str, dict]]:
    """overlay reference -> control -> its Section 6 specification."""
    return _load((repo / YAML_PATH).resolve())


def control_sets(overlays: list[str]) -> dict[str, set[str]]:
    """The transcribed overlays a run applies, each with the Privacy Overlays control sets it
    names (empty for an overlay without sets)."""
    out: dict[str, set[str]] = {}
    for name in overlays:
        if not isinstance(name, str):
            continue
        for ref in SECTIONS:
            if name == ref:
                out.setdefault(ref, set())
            elif name.startswith(f"{ref}-") and name[len(ref) + 1:] in SETS:
                out.setdefault(ref, set()).add(name[len(ref) + 1:])
    return out


def _justifies(statement: dict, sets: set[str]) -> bool:
    """Whether a justification speaks to the run: no sets named, one of the run's sets, or a
    Privacy Enhancing recommendation, which any set may tailor in."""
    named = set(statement.get("sets") or ())
    return not named or bool(named & sets) or statement.get("disposition") == "recommend"


def _applies(statement: dict, sets: set[str], selecting: set[str]) -> bool:
    named = set(statement.get("sets") or ())
    return bool(named & sets) if named else not sets or bool(selecting & sets) \
        or "ENHANCING" in selecting


def applied(repo: Path, overlays: list[str]) -> dict[str, list[Applied]]:
    """control -> the specifications of the run's overlays that apply to it. For the Privacy
    Overlays a control is specified for a set its justification names; a Privacy Enhancing
    control is recommended for every set."""
    out: dict[str, list[Applied]] = {}
    specs = load(repo)
    for ref, sets in control_sets(overlays).items():
        for cid, spec in specs.get(ref, {}).items():
            if spec.get("in_privacy_baseline"):
                continue
            justifications = [st for st in spec.get("statements") or ()
                              if st["kind"] == "justification"]
            disposition = None  # a set's own select or not-select outranks a recommendation
            for st in justifications:
                if _justifies(st, sets) and disposition in (None, "recommend"):
                    disposition = st["disposition"]
            if disposition is None:
                continue
            selecting = {x for st in justifications if st["disposition"] in SELECTING
                         for x in st.get("sets") or ()}
            rest = tuple(st for st in spec.get("statements") or ()
                         if (st in justifications and _justifies(st, sets))
                         or (st["kind"] != "justification" and _applies(st, sets, selecting)))
            out.setdefault(cid, []).append(Applied(
                ref, cid, disposition, rest, tuple(spec.get("authorities") or ()),
                spec.get("references") or "", spec["citation"]))
    return out


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def named(authority: str, recorded: list[str]) -> bool:
    """Whether a recorded authority names this one ("EO 13526, Sec. 4.1" names EO 13526)."""
    want = _norm(authority)
    return any(want in _norm(r) for r in recorded if isinstance(r, str))


_ITEM = re.compile(r"(?:^|[.;:]\s+)(\(?[a-z]\)?\.?)\s")


def aggregated(cat: catalog.Catalog, param_id: str) -> list[str]:
    """The parameters an aggregate parameter (``mp-4_prm_1``) stands for, or none."""
    return [p["value"] for p in cat.params.get(param_id, {}).get("props") or []
            if p.get("name") == "aggregates"]


def assigned_params(cat: catalog.Catalog, control_id: str, value: str) -> list[str]:
    """The organization-defined parameters an overlay parameter value assigns: those of the
    statement items it names by label ("a.", "(b)"), or of the whole statement when it names
    none."""
    control = cat.controls.get(control_id) or {}
    statement = next((p for p in control.get("parts") or [] if p.get("name") == "statement"),
                     None)
    if statement is None:
        return []
    items = {catalog._label(p): p for p in statement.get("parts") or [] if catalog._label(p)}
    labels = [m.group(1) for m in _ITEM.finditer(value) if m.group(1) in items]
    chosen = [items[label] for label in dict.fromkeys(labels)] or [statement]

    def params(part: dict) -> list[str]:
        found = catalog._INSERT.findall(part.get("prose") or "")
        for child in part.get("parts") or []:
            found += params(child)
        return found

    def expand(pid: str) -> list[str]:
        param = cat.params.get(pid, {})
        parts = aggregated(cat, pid)
        nested = [n for choice in (param.get("select") or {}).get("choice") or []
                  for n in catalog._INSERT.findall(choice)]
        return [*(parts or [pid]), *(x for n in nested for x in expand(n))]

    return list(dict.fromkeys(x for part in chosen for pid in params(part) for x in expand(pid)))


# --- the summary tables ------------------------------------------------------------------

_TEXT_ID = re.compile(r"^([A-Z]{2}-\d+(?:\(\d+\))?)(?:\s|$)")


def classified_marks(md: Path) -> dict[str, str]:
    """Table 1 of the Classified System Overlay: control -> its mark (``+GR``)."""
    marks: dict[str, str] = {}
    inside = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.strip() == "Table 1: Classified System Overlay Summary of Control Specifications":
            inside = True
        elif line.strip() == "Table 2: Controls with Implementation Considerations":
            break
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        ident = next((m.group(1) for c in cells[:2] if (m := _TEXT_ID.match(c))), None)
        mark = next((c for c in cells if re.fullmatch(r"\+[GRV]*", c)), None)
        if ident and mark:
            marks[oscal_id(ident)] = mark
    return marks


def privacy_marks(md: Path, known: dict[str, dict]) -> dict[str, tuple[str, ...]]:
    """Table 2 of the Privacy Overlays: control -> its ACCT, Low, Mod, High and Enhancing
    cells, read through the row joining of rmf_tool.cnssi1253."""
    from rmf_tool import cnssi1253

    out: dict[str, tuple[str, ...]] = {}
    raw = cnssi1253._privacy_rows(md)
    by_name: dict[str, list[str]] = {}
    for cid in known:
        by_name.setdefault(cnssi1253._name_key(cnssi1253._catalog_name(known, cid)), []).append(cid)
    i = 0
    while i < len(raw):
        _, cells = raw[i]
        i += 1
        if not cells[1]:
            continue
        printed = re.sub(r"\s", "", cells[0])
        while (not printed or printed.endswith("-")) and i < len(raw) \
                and not raw[i][1][1] and not any(raw[i][1][2:]):
            printed += re.sub(r"\s", "", raw[i][1][0])
            i += 1
        if printed and cnssi1253._ID.match(printed):
            cid = oscal_id(printed)
        else:
            found = by_name.get(cnssi1253._name_key(cells[1].replace("\\|", " ")), [])
            if len(found) != 1:
                continue
            cid = found[0]
        out[cid] = tuple(re.sub(r"\s", "", c) for c in cells[2:7])
    return out


# The extraction put AC-16's Guidance box (a two-column table on page 39) under the AC-16(3)
# heading and ran the rest of that guidance into AC-16's justification. The PDF prints both
# under AC-16: "Guidance: Use privacy attributes including, as a minimum, ... PII to enable
# cross system functionality ..." (page 39).
_AC16_SPLIT = "to enable cross system functionality"


def _repair(ref: str, specs: list[Spec]) -> None:
    if ref != PRIVACY:
        return
    by_id = {s.control: s for s in specs}
    ac16, ac163 = by_id.get("ac-16"), by_id.get("ac-16.3")
    moved = [st for st in (ac163.statements if ac163 else []) if st.kind == "guidance"]
    justification = next((st for st in (ac16.statements if ac16 else [])
                          if st.kind == "justification" and _AC16_SPLIT in st.text), None)
    if ac16 is None or ac163 is None or len(moved) != 1 or justification is None:
        raise ExtractError(f"{PRIVACY}: the AC-16 guidance repair no longer matches the text; "
                           "read page 39 and update _repair")
    head, _, tail = justification.text.partition(_AC16_SPLIT)
    justification.text = head.strip()
    ac163.statements.remove(moved[0])
    moved[0].text = _join([moved[0].text, _AC16_SPLIT + tail])
    ac16.statements.insert(1, moved[0])


# What the document prints that its own table does not mark, or the reverse; each is read
# against the PDF page. Key: (overlay, control, what differs).
ERRATA: dict[tuple[str, str, str], str] = {}


def _cross_check_classified(specs: list[Spec], marks: dict[str, str]) -> list[str]:
    problems = []
    by_id = {s.control: s for s in specs}
    for cid in marks:
        if cid not in by_id and (CLASSIFIED, cid, "missing") not in ERRATA:
            problems.append(f"{cid}: in Table 1 but not in Section 6")
    for s in specs:
        mark = marks.get(s.control)
        if mark is None:
            if (CLASSIFIED, s.control, "unmarked") not in ERRATA:
                problems.append(f"{s.control}: in Section 6 but not in Table 1")
            continue
        has = {k for k in KINDS if any(st.kind == k for st in s.statements)}
        for kind, letter in MARKS.items():
            if (letter in mark) != (kind in has) \
                    and (CLASSIFIED, s.control, kind) not in ERRATA:
                problems.append(f"{s.control}: Table 1 marks {mark!r}, Section 6 "
                                f"{'has no' if kind not in has else 'has a'} {kind}")
        if ("R" in mark) != bool(s.references) \
                and (CLASSIFIED, s.control, "references") not in ERRATA:
            problems.append(f"{s.control}: Table 1 marks {mark!r}, references "
                            f"{'missing' if not s.references else 'present'}")
        if not any(st.kind == "justification" for st in s.statements):
            problems.append(f"{s.control}: no justification to select")
    return problems


def _cross_check_privacy(specs: list[Spec], marks: dict[str, tuple[str, ...]]) -> list[str]:
    problems = []
    by_id = {s.control: s for s in specs}
    for cid, cells in marks.items():
        if any(c.startswith(("+", "*")) for c in cells) and cid not in by_id \
                and (PRIVACY, cid, "missing") not in ERRATA:
            problems.append(f"{cid}: selected in Table 2 but not in Section 6")
    for s in specs:
        if s.in_privacy_baseline:
            continue
        cells = marks.get(s.control)
        if cells is None:
            if (PRIVACY, s.control, "unmarked") not in ERRATA:
                problems.append(f"{s.control}: in Section 6 but not in Table 2")
            continue
        # "*" in the Privacy Enhancing column recommends an optional control.
        selects = {SETS[k] for k, c in enumerate(cells) if c.startswith(("+", "*"))}
        justified = {x for st in s.statements if st.kind == "justification"
                     and st.disposition in ("select", "recommend") for x in st.sets}
        if selects != justified and (PRIVACY, s.control, "sets") not in ERRATA:
            problems.append(f"{s.control}: Table 2 selects {sorted(selects)}, Section 6 "
                            f"justifies {sorted(justified)}")
        letters = "".join(cells)
        for kind, letter in MARKS.items():
            has = any(st.kind == kind for st in s.statements)
            if (letter in letters) != has and (PRIVACY, s.control, kind) not in ERRATA:
                problems.append(f"{s.control}: Table 2 marks {cells}, Section 6 "
                                f"{'has a' if has else 'has no'} {kind}")
    return problems


# --- output ------------------------------------------------------------------------------


def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def render(parsed: dict[str, list[Spec]]) -> str:
    out = [
        f"# {YAML_PATH}: GENERATED by `uv run python -m rmf_tool.overlay_specs`; do not edit.",
        "# Section 6 of each transcribed overlay, per control, checked against the overlay's",
        "# summary table. Schema: framework/schema/overlay-specs.schema.json.",
        "# sets: the Privacy Overlays control sets a statement applies to (none: every set,",
        "# or an overlay without sets). authorities: what the references name, in the form",
        "# tailoring.yaml law_policy.authorities names them (OVS-001).",
        "overlays:",
    ]
    for ref, specs in parsed.items():
        out += [f"  - overlay: {ref}", "    specs:"]
        for s in specs:
            out += [f"      - control: {s.control}",
                    f"        heading: {_q(s.heading)}",
                    f"        citation: {{ref: {ref}, page: {s.page}, anchor: {_q(s.anchor)}}}"]
            if s.in_privacy_baseline:
                out.append("        in_privacy_baseline: true")
            if s.statements:
                out.append("        statements:")
            for st in s.statements:
                keys = [f"kind: {st.kind}"]
                if st.disposition:
                    keys.append(f"disposition: {st.disposition}")
                if st.sets:
                    keys.append(f"sets: [{', '.join(st.sets)}]")
                keys.append(f"text: {_q(st.text)}")
                out.append(f"          - {{{', '.join(keys)}}}")
            if s.references:
                out.append(f"        references: {_q(s.references)}")
                names = authorities(s.references)
                out.append(f"        authorities: [{', '.join(_q(n) for n in names)}]")
    return "\n".join(out) + "\n"


@dataclass
class Result:
    text: str
    specs: dict[str, list[Spec]]


def generate(repo: Path) -> Result:
    known = catalog.load(repo).controls
    parsed: dict[str, list[Spec]] = {}
    problems: list[str] = []
    for ref in SECTIONS:
        md = repo / f"references/text/{ref}.md"
        specs = parse(md, ref, set(known))
        _repair(ref, specs)
        seen = [s.control for s in specs]
        problems += [f"{ref}: {c} appears twice" for c in sorted({c for c in seen
                                                                   if seen.count(c) > 1})]
        for s in specs:
            for st in s.statements:
                if not st.text:
                    problems.append(f"{ref} {s.control}: empty {st.kind}")
            if s.references and not authorities(s.references):
                problems.append(f"{ref} {s.control}: no authority read from {s.references!r}")
            if not s.in_privacy_baseline and not s.statements:
                problems.append(f"{ref} {s.control}: no specification")
        if ref == CLASSIFIED:
            problems += [f"{ref} {p}" for p in
                         _cross_check_classified(specs, classified_marks(md))]
        else:
            problems += [f"{ref} {p}" for p in _cross_check_privacy(specs,
                                                                     privacy_marks(md, known))]
        parsed[ref] = specs
    if problems:
        raise ExtractError(f"{len(problems)} problem(s):\n  " + "\n  ".join(problems))
    return Result(render(parsed), parsed)


def summary(result: Result) -> str:
    lines = []
    for ref, specs in result.specs.items():
        counts = {k: sum(1 for s in specs for st in s.statements if st.kind == k) for k in KINDS}
        lines.append(f"{ref}: {len(specs)} controls; " +
                     ", ".join(f"{k}={n}" for k, n in counts.items()) +
                     f", references={sum(bool(s.references) for s in specs)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rmf_tool.overlay_specs", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail when the YAML is stale")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        result = generate(args.repo)
    except ExtractError as exc:
        print(f"overlay_specs: {exc}", file=sys.stderr)
        return 2
    target = args.repo / YAML_PATH
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != result.text:
            print(f"{YAML_PATH} is stale; run: uv run python -m rmf_tool.overlay_specs",
                  file=sys.stderr)
            return 1
        print(f"{YAML_PATH} is current")
        return 0
    target.write_text(result.text, encoding="utf-8")
    print(summary(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
