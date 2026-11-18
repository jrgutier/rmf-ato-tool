"""Regenerate ``framework/baselines/cnssi-1253-parameters.yaml`` from the Parameter Value
column of CNSSI 1253 Appendix D (Tables D-1..D-20): the minimum values CNSSI 1253 specifies
for NSS for SP 800-53r5 organization-defined parameters (page 22).

Each row's column text is read from the PDF's word geometry: the column lies between the
drawn rules either side of its "Parameter Value" header, and a row is the band between the
horizontal rules around its printed ID (text in the column above a page's first band
continues the previous page's last row). The text, normalized for whitespace, must occur in
that row's lines of ``references/text/CNSSI1253.md``. Each row is split into assignments at
item labels ("h.1.", "c.1., c.2.") and ordinals ("2nd PV:"), each mapped to the catalog
parameters it assigns, and each value gets a ``bound``: ``max`` when a smaller amount is
stricter, ``min`` when a larger one is, ``none`` when it is no comparable amount.

    uv run python -m rmf_tool.cnssi1253_params           # rewrite the YAML, print a summary
    uv run python -m rmf_tool.cnssi1253_params --check   # exit 1 when the YAML is stale
"""

from __future__ import annotations

import argparse
import re
import sys
from bisect import bisect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rmf_tool import catalog
from rmf_tool.cnssi1253 import (
    _ID,
    _ID_MAX_X,
    _PAGE,
    _TEXT_ID,
    FIRST_TABLE_PAGE,
    PDF_PATH,
    REF,
    TEXT_PATH,
    ExtractError,
    _q,
    oscal_id,
)
from rmf_tool.overlay_specs import aggregated
from rmf_tool.run.model import schema_errors
from rmf_tool.yamlload import safe_load

YAML_PATH = "framework/baselines/cnssi-1253-parameters.yaml"
SCHEMA_PATH = "framework/schema/cnssi-1253-parameters.schema.json"
_DEFINITION = "Contains minimum values specified for NSS"  # page 22, the column's definition

# (control, printed label) -> the catalog label it stands for, with the reason.
LABEL_ALIASES = {
    ("cm-5.5", "5.b."): ("(b)", "the row prefixes the enhancement number to item (b)"),
}
# (control, label or "" for a whole-row value) -> (bound, reason), where the classifier
# cannot settle it.
BOUNDS = {
    ("cm-3.7", "1st PV:"): ("none", "one frequency per integrity impact level"),
}
# (page, printed ID) -> reason, for a row whose column text is not in its text lines.
TEXT_DIFFERS: dict[tuple[int, str], str] = {}


# --- amounts -----------------------------------------------------------------------------

_DAYS = {"minute": 1 / 1440, "hour": 1 / 24, "day": 1, "week": 7, "month": 31, "quarter": 92,
         "year": 366}
_EVERY = {"daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92, "annually": 366,
          "annual": 366, "continuously": 0, "semi-annually": 183, "semiannually": 183,
          "semi-annual": 183, "bi-weekly": 14, "biweekly": 14, "hourly": 1 / 24,
          "immediately": 0, "real time": 0, "real-time": 0, "same day": 1, "same-day": 1}
# Longest first, and never inside a longer word: "semi-annually" is no "annually", and "near
# real time" is no amount.
_EVERY_RE = "|".join(re.escape(k).replace(r"\ ", r"\s+")
                     for k in sorted(_EVERY, key=len, reverse=True))
_NUMBERS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12}
_NUM = rf"\d+(?:\.\d+)?|{'|'.join(_NUMBERS)}"
_AMOUNT = re.compile(
    rf"\b(?P<nt>{_NUM})\s+times?\s+(?:per|a|each)\s+(?P<tunit>{'|'.join(_DAYS)})\b"
    rf"|\b(?P<n1>{_NUM})\s*(?:\(\d+\)\s*)?-?\s*(?:(?:working|business)\s+)?"
    rf"(?P<unit>{'|'.join(_DAYS)})s?\b"
    rf"|(?<![-\w])(?<!near )(?P<every>{_EVERY_RE})\b"
    rf"|\b(?P<n2>{_NUM})\s*-?\s*(?:characters?|attempts?|sessions?|versions?)\b"
    rf"|(?P<pct>\d+(?:\.\d+)?)\s*%"
    rf"|\b(?:at least|maximum of|minimum of|no more than)\s+(?P<n3>{_NUM})\b(?!\s*[(%\w-])",
    re.IGNORECASE)
_MAX_WORDS = re.compile(r"\b(?:maximum|not to exceed|no more than|within|up to)\b", re.I)
_MIN_WORDS = re.compile(r"\b(?:at least|minimum|longer)\b", re.I)


def _number(s: str) -> float:
    return float(s) if s[0].isdigit() else float(_NUMBERS[s.lower()])


def amount(value: str) -> tuple[float, str] | None:
    """The first comparable amount in ``value``: (days, "days") for a duration or frequency,
    (n, "count") for characters, attempts, sessions or a bare "at least two", (n, "percent");
    None when there is none."""
    m = _AMOUNT.search(value)
    if m is None:
        return None
    if m["tunit"]:
        return _DAYS[m["tunit"].lower()] / _number(m["nt"]), "days"
    if m["unit"]:
        return _number(m["n1"]) * _DAYS[m["unit"].lower()], "days"
    if m["every"]:
        return float(_EVERY[" ".join(m["every"].lower().split())]), "days"
    if m["pct"]:
        return float(m["pct"]), "percent"
    return _number(m["n2"] or m["n3"]), "count"


def classify(value: str) -> str:
    """``max`` when a smaller amount is stricter, ``min`` when a larger one is, else none."""
    found = amount(value)
    if found is None:
        return "none"
    m = _AMOUNT.search(value)
    assert m is not None
    if found[1] == "days" and (m["every"] or re.search(r"\bevery\b", value, re.I)):
        return "max"  # a frequency: "at least annually" still means no longer than a year
    before = value[:m.end()]
    if _MAX_WORDS.search(before):
        return "max"
    if _MIN_WORDS.search(value) or found[1] in ("count", "percent"):
        return "min"
    return "max"  # a bare duration is a time limit or an inactivity period


_FOR_TYPE = re.compile(r"\bfor (\w+?)s?\s*$", re.I)


def scoped(run_value: str, nss_value: str) -> str:
    """The part of ``run_value`` the NSS value speaks to. An NSS value for one type ("not to
    exceed 180 days for passwords") is compared with the run's clause for that type, not with
    the first amount of a value that lists one period per authenticator type (F-06-5); clauses
    are split on ";". A per-type value with no clause for that type has nothing to compare
    (PVAL-002 then asks for the amount); a value of one clause stands whole."""
    m = _FOR_TYPE.search(nss_value)
    clauses = [c for c in run_value.split(";") if c.strip()]
    if m is None or len(clauses) < 2:
        return run_value
    stem = re.compile(rf"\b{re.escape(m[1])}", re.I)
    hits = [c for c in clauses if stem.search(c)]
    return "; ".join(hits)


def looser(run_value: str, nss: dict[str, Any]) -> bool | None:
    """Whether ``run_value`` is looser than the NSS value ``nss`` ({value, bound}); None when
    either has no comparable amount, the kinds differ, or the bound is none."""
    cases = _conditions(nss["value"])
    if cases:
        # one bound per condition ("if voluntary, ...; if involuntary, ..."): each is checked
        # against the run's clause for the same condition (F-07-6)
        mine = _conditions(run_value)
        verdicts = [looser(mine[k], {**nss, "value": v}) if k in mine else None
                    for k, v in cases.items()]
        if True in verdicts:
            return True
        return None if None in verdicts else False
    a, b = amount(scoped(run_value, nss["value"])), amount(nss["value"])
    if a is None or b is None or a[1] != b[1] or nss["bound"] == "none":
        return None
    return a[0] > b[0] if nss["bound"] == "max" else a[0] < b[0]


_IF = re.compile(r"^\s*if (\w+)\b", re.I)


def _conditions(value: str) -> dict[str, str]:
    """``{"voluntary": "...", "involuntary": "..."}`` for a value of two or more clauses each
    opening with "if <condition>"; empty otherwise."""
    out: dict[str, str] = {}
    for clause in value.split(";"):
        m = _IF.match(clause)
        if m is None:
            return {}
        out[m[1].lower()] = clause
    return out if len(out) > 1 else {}


# --- PDF geometry ------------------------------------------------------------------------


@dataclass
class Row:
    page: int
    table_id: str
    words: list[tuple[int, float, float, str]] = field(default_factory=list)

    def lines(self) -> list[str]:
        out: dict[tuple[int, float], list[str]] = {}
        for page, y, _, word in sorted(self.words):
            out.setdefault((page, y), []).append(word)
        return [" ".join(ws) for ws in out.values()]

    @property
    def text(self) -> str:
        """The lines joined; a word hyphenated at a line end is joined back ("non-
        privileged" -> "non-privileged")."""
        return re.sub(r"(?<=\w-)\n", "", "\n".join(self.lines())).replace("\n", " ")


def _rules(page: Any) -> tuple[list[float], list[float]]:
    """The y of every horizontal and the x of every vertical table rule on the page."""
    ys, xs = set(), set()
    for d in page.get_drawings():
        for item in d["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) < 1:
                    ys.add(round(a.y, 1))
                elif abs(a.x - b.x) < 1:
                    xs.add(round(a.x, 1))
            elif item[0] == "re":
                r = item[1]
                if r.height < 2:
                    ys.add(round(r.y0, 1))
                elif r.width < 2:
                    xs.add(round(r.x0, 1))
    return sorted(ys), sorted(xs)


def pdf_rows(pdf: Path) -> list[Row]:
    import pymupdf

    rows: list[Row] = []
    column: tuple[float, float] | None = None
    with pymupdf.open(pdf) as doc:
        for pno in range(FIRST_TABLE_PAGE, doc.page_count + 1):
            page = doc[pno - 1]
            words: Any = page.get_text("words")
            ys, xs = _rules(page)
            head = next((w for w in words if w[4] == "Parameter"), None)
            top = ys[0] if ys else 0.0
            if head is not None:
                value = next(w for w in words if w[4] == "Value" and abs(w[1] - head[1]) < 2)
                column = (max(x for x in xs if x < head[0]), min(x for x in xs if x > value[2]))
                top = value[3]
            ids = sorted((w for w in words if _ID.match(w[4]) and w[2] < _ID_MAX_X),
                         key=lambda w: w[1])
            if not ids:
                continue
            if column is None:
                raise ExtractError(f"page {pno}: no Parameter Value header found")
            bands = []
            for w in ids:
                i = bisect(ys, (w[1] + w[3]) / 2)
                if not 0 < i < len(ys):
                    raise ExtractError(f"page {pno} {w[4]}: no rules around the row")
                bands.append((ys[i - 1], ys[i], Row(pno, w[4])))
            for w in words:
                x, y = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
                if not column[0] < x < column[1] or y <= top:
                    continue
                hit = [r for a, b, r in bands if a < y < b]
                if len(hit) == 1:
                    target = hit[0]
                elif y < bands[0][0] and rows:
                    target = rows[-1]  # the previous page's last row continues here
                else:
                    raise ExtractError(f"page {pno}: {w[4]!r} at y={y:.1f} is in no row")
                target.words.append((pno, round(w[1], 1), w[0], w[4]))
            rows += [r for _, _, r in bands]
    return rows


# --- text extraction ---------------------------------------------------------------------


def _norm(s: str) -> str:
    return " ".join(s.split())


def _in_order(lines: list[str], text: str) -> bool:
    """Every PDF line occurs in the text row, in order (a line, not the whole value, since
    the text extraction keeps line-end hyphens and repeats a page's header mid-row)."""
    pos = 0
    for line in lines:
        pos = text.find(line, pos)
        if pos < 0:
            return False
        pos += len(line)
    return True


def text_rows(md: Path) -> dict[tuple[int, str], str]:
    """(page, printed ID) -> the row's table lines, joined; a row runs to the next ID, across
    a page break."""
    lines: dict[tuple[int, str], list[str]] = {}
    page, current = 0, None
    for line in md.read_text(encoding="utf-8").splitlines():
        m = _PAGE.match(line)
        if m:
            page = int(m.group(1))
            continue
        if page < FIRST_TABLE_PAGE or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        ident = next((m.group(1) for c in cells[:3] if (m := _TEXT_ID.match(c))), None)
        if ident:
            current = (page, ident)
            lines[current] = []
        if current is not None:
            lines[current].append(" ".join(cells))
    return {k: _norm(" ".join(v)) for k, v in lines.items()}


# --- assignments -------------------------------------------------------------------------

_ITEM = r"[a-z]\.(?:\d+(?![a-z]))?[.:]?"
_ITEMS = re.compile(rf"(?<!\S)(?:\d+\.)?{_ITEM}(?:(?:,\s*|\s+and\s+){_ITEM})*"
                    r"(?=\s|\d(?:st|nd|rd|th) PV:)")
_ORDINAL = re.compile(r"(\d)(?:st|nd|rd|th) PV:")


def _key(label: str) -> str:
    return re.sub(r"[().:\s]", "", label)


def _statement(cat: catalog.Catalog, cid: str) -> dict[str, Any]:
    return next(p for p in cat.controls[cid].get("parts") or [] if p.get("name") == "statement")


def _item(cat: catalog.Catalog, cid: str, label: str) -> dict[str, Any] | None:
    """The statement part a printed label ("h.1.", "c.2:", "d.") names: h.1 is item h's
    sub-item 1; "d." also names an enhancement's "(d)"."""
    alias = LABEL_ALIASES.get((cid, label))
    path = [_key(alias[0])] if alias else re.findall(r"[a-z]|\d+", label)
    part: dict[str, Any] | None = _statement(cat, cid)
    for k in path:
        part = next((p for p in (part or {}).get("parts") or []
                     if _key(catalog._label(p)) == k), None)
    return part


def _inserts(part: dict[str, Any]) -> list[str]:
    """The parameters a part inserts, in statement order (a selection counts once)."""
    found = catalog._INSERT.findall(part.get("prose") or "")
    for child in part.get("parts") or []:
        found += _inserts(child)
    return found


def _expand(cat: catalog.Catalog, pid: str) -> list[str]:
    """An aggregate stands for its parts; a selection also assigns the parameters its
    choices insert."""
    choices = (cat.params.get(pid, {}).get("select") or {}).get("choice") or []
    nested = [n for c in choices for n in catalog._INSERT.findall(c)]
    return [*(aggregated(cat, pid) or [pid]), *(x for n in nested for x in _expand(cat, n))]


@dataclass
class Assignment:
    label: str  # as printed ("c.1., c.2. 1st PV:"), "" for a whole-row value
    params: list[str]
    value: str
    bound: str = "none"


def _intros(cat: catalog.Catalog, cid: str, text: str) -> list[tuple[int, int, list[str], int]]:
    """(start, end, item labels, ordinal or 0) of each label in the text. A run of item
    labels counts only when the control has every item it names, so "(a)" or "e.g." in a
    value is never one."""
    marks = []
    for m in _ITEMS.finditer(text):
        labels = re.split(r",\s*|\s+and\s+", m.group(0))
        if all(_item(cat, cid, lb) is not None for lb in labels):
            marks.append([m.start(), m.end(), labels, 0])
    for m in _ORDINAL.finditer(text):
        prev = next((k for k in marks if k[1] <= m.start()
                     and not text[k[1]:m.start()].strip() and not k[3]), None)
        if prev is not None:
            prev[1], prev[3] = m.end(), int(m.group(1))
        else:
            marks.append([m.start(), m.end(), [], int(m.group(1))])
    return sorted((s, e, lb, n) for s, e, lb, n in marks)


def assignments(cat: catalog.Catalog, cid: str, text: str) -> list[Assignment]:
    marks = _intros(cat, cid, text)
    if not marks:
        params = [x for pid in _inserts(_statement(cat, cid)) for x in _expand(cat, pid)]
        return [Assignment("", list(dict.fromkeys(params)), text)]
    if text[:marks[0][0]].strip():
        raise ExtractError(f"{cid}: text before the first label: {text[:marks[0][0]]!r}")
    out = []
    for k, (start, end, labels, n) in enumerate(marks):
        stop = marks[k + 1][0] if k + 1 < len(marks) else len(text)
        chosen = []
        for part in [_item(cat, cid, lb) for lb in labels] or [_statement(cat, cid)]:
            inserted = _inserts(part)  # type: ignore[arg-type]
            if n > len(inserted):
                raise ExtractError(f"{cid} {text[start:end]!r}: the part inserts "
                                   f"{len(inserted)} parameter(s)")
            own = catalog._INSERT.findall(part.get("prose") or "")  # type: ignore[union-attr]
            # "a. all personnel" assigns item a's own parameter, not its sub-items' selections
            chosen += [inserted[n - 1]] if n else own or inserted
        params = list(dict.fromkeys(x for pid in chosen for x in _expand(cat, pid)))
        label, value = _norm(text[start:end]), text[end:stop].strip()
        if not params or not value:
            raise ExtractError(f"{cid} {label!r}: assigns no parameter or has no value")
        out.append(Assignment(label, params, value))
    return out


# --- output ------------------------------------------------------------------------------


@dataclass
class Result:
    controls: list[tuple[Row, list[Assignment]]]
    text: str


def _bounds(controls: list[tuple[Row, list[Assignment]]]) -> list[str]:
    problems, used = [], set()
    for row, values in controls:
        cid = oscal_id(row.table_id)
        for a in values:
            auto = classify(a.value)
            a.bound = auto
            if (cid, a.label) in BOUNDS:
                used.add((cid, a.label))
                a.bound = BOUNDS[cid, a.label][0]
                if a.bound == auto:
                    problems.append(f"BOUNDS {cid} {a.label!r}: the classifier already says "
                                    f"{auto}; remove it")
    problems += [f"BOUNDS {k}: matches no value" for k in BOUNDS if k not in used]
    return problems


def render(controls: list[tuple[Row, list[Assignment]]]) -> str:
    out = [
        f"# {YAML_PATH}: GENERATED by `uv run python -m rmf_tool.cnssi1253_params`; do not",
        "# edit. The Parameter Value column of CNSSI 1253 Appendix D, read from the PDF's table",
        f"# geometry and checked against {TEXT_PATH}. bound: max when a smaller amount is",
        "# stricter, min when a larger one is, none when the value is no comparable amount.",
        f"# Schema: {SCHEMA_PATH}.",
        f"ref: {REF}",
        f"citation: {{ref: {REF}, page: 22, anchor: {_q(_DEFINITION)}}}",
        "controls:",
    ]
    for row, values in controls:
        out += [f"  - control: {oscal_id(row.table_id)}",
                f"    citation: {{ref: {REF}, page: {row.page}, anchor: {_q(row.table_id)}}}",
                "    values:"]
        for a in values:
            label = f"label: {_q(a.label)}, " if a.label else ""
            out.append(f"      - {{{label}params: [{', '.join(a.params)}], value: {_q(a.value)}, "
                       f"bound: {a.bound}}}")
    return "\n".join(out) + "\n"


def generate(repo: Path) -> Result:
    cat = catalog.load(repo)
    text = text_rows(repo / TEXT_PATH)
    problems, controls, used = [], [], set()
    for row in pdf_rows(repo / PDF_PATH):
        if not row.words:
            continue
        key, pv = (row.page, row.table_id), _norm(row.text)
        matches = _in_order([_norm(ln) for ln in row.lines()], text.get(key, ""))
        if key in TEXT_DIFFERS:
            used.add(key)
            if matches:
                problems.append(f"TEXT_DIFFERS {key}: the text matches; remove it")
        elif not matches:
            problems.append(f"page {row.page} {row.table_id}: {pv!r} is not in its text row")
        try:
            values = assignments(cat, oscal_id(row.table_id), pv)
        except ExtractError as exc:
            problems.append(f"page {row.page} {row.table_id}: {exc}")
            continue
        labels = [a.label for a in values]
        if len(set(labels)) != len(labels):
            problems.append(f"page {row.page} {row.table_id}: a label repeats: {labels}")
        controls.append((row, values))
    problems += [f"TEXT_DIFFERS {k}: matches no row" for k in TEXT_DIFFERS if k not in used]
    problems += _bounds(controls)
    labels_seen = {(oscal_id(r.table_id), a.label) for r, vs in controls for a in vs}
    problems += [f"LABEL_ALIASES {k}: matches no value" for k in LABEL_ALIASES
                 if k not in labels_seen]
    out = render(controls)
    problems += schema_errors(repo, "cnssi-1253-parameters", safe_load(out))
    if problems:
        raise ExtractError(f"{len(problems)} problem(s):\n  " + "\n  ".join(problems))
    return Result(controls, out)


def load(repo: Path) -> dict[str, list[dict[str, Any]]]:
    """Control ID -> its NSS minimum values ({label?, params, value, bound})."""
    data = safe_load((repo / YAML_PATH).read_text(encoding="utf-8"))
    return {c["control"]: c["values"] for c in data["controls"]}


def summary(result: Result) -> str:
    values = [(oscal_id(r.table_id), a) for r, vs in result.controls for a in vs]
    lines = [f"{len(result.controls)} rows with a parameter value, {len(values)} assignments, "
             f"{sum(len(a.params) for _, a in values)} parameters; "
             f"{len(TEXT_DIFFERS)} text override(s), {len(LABEL_ALIASES)} label alias(es), "
             f"{len(BOUNDS)} bound override(s)"]
    lines += [f"{a.bound:<4} {cid} {a.label or '(whole)'} {a.value[:70]} -> {amount(a.value)}"
              for cid, a in values if a.bound != "none"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rmf_tool.cnssi1253_params",
                                     description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail when the YAML is stale")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        result = generate(args.repo)
    except ExtractError as exc:
        print(f"cnssi1253_params: {exc}", file=sys.stderr)
        return 2
    target = args.repo / YAML_PATH
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != result.text:
            print(f"{YAML_PATH} is stale; run: uv run python -m rmf_tool.cnssi1253_params",
                  file=sys.stderr)
            return 1
        print(f"{YAML_PATH} is current")
        return 0
    target.write_text(result.text, encoding="utf-8")
    print(summary(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
