"""Recall of the extractor against hand-read pages, and the audit probes against the register.

The labels in tests/fixtures/conformance/recall/ were written by reading the pages before the
extractor was changed. A label is never edited to fit the extractor: a miss below the
threshold is a defect in extract.py or in the scope declarations, not in the label.

Each label is matched to one item: the item on its page whose statement contains it, the
shortest when several do. Recall is reported by unit (lettered, table, prose) and by source
mode. Lettered items, table rows, the pin and the catalogs keep the 95% floor. Prose does not:
after three held-out reviews the remaining prose misses are semantic (`was established`,
`contingency planning begins`, `emphasizes the need`), and the regexes written to hit two of
them matched 23 noise sentences for 3 hits, so they were removed and the labels count as
misses. Extraction is a first pass (plan, Nov 1): triage reads the pages and promotes what it
missed with `rmf conformance promote`. The prose floor is the level measured on the labelled
pages, so a regression fails while a 95% guarantee is not claimed. Noise is the share of
items on the labelled pages that no label matched.
"""

import re
from collections import Counter, defaultdict

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.conformance import extract, register
from rmf_tool.refs.toc import compact

FIXTURES = REPO_ROOT / "tests/fixtures/conformance/recall"
RECALL_FLOOR = 0.95
# Measured 91/94 on 2026-11-01 with the three semantic misses named in the module docstring.
PROSE_FLOOR = 0.968
PROBE_FLOOR = 1.0
# Unlabelled items on the labelled pages. Measured, reported, and bounded so a change that
# doubles the triage load is noticed; it is not a target.
NOISE_CEILING = 0.35
MIN_PAGES = 20
UNITS = ("lettered", "table", "prose")


def _yaml(name):
    return YAML(typ="safe").load((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sources():
    return register.load(REPO_ROOT).sources


@pytest.fixture(scope="module")
def labelled(sources):
    """(page label, mode, extracted items on that page)."""
    out = []
    texts = {}
    for page in _yaml("pages.yaml")["pages"]:
        ref, number = page["ref"], page["page"]
        source = sources[ref]
        if ref not in texts:
            texts[ref] = (REPO_ROOT / f"references/text/{ref}.md").read_text(encoding="utf-8")
        skip, strip = register.labels_for(source)
        scopes = [s for s in source["scopes"] if s["pages"][0] <= number <= s["pages"][1]]
        assert scopes, f"{ref} page {number} is in no scope of conformance/sources.yaml"
        items = [i for i in extract.extract(texts[ref], scopes, skip_labels=skip,
                                            strip_labels=strip).items if i.spans(number)]
        out.append((page, source["mode"], items))
    return out


def _unit(label, item):
    """Which unit a label belongs to: the matched item's, or the label's own shape when it
    was missed, so a missed prose sentence counts against prose."""
    if item is not None:
        return item.kind if item.kind in ("lettered", "table") else "prose"
    if extract._LABEL.match(label):
        return "lettered"
    return "table" if " | " in label else "prose"


def _matches(page, items):
    """label -> the one item whose statement contains it (the shortest), or None."""
    found = {}
    for label in page["requirements"]:
        wanted = compact(label)
        hits = [i for i in items if wanted in compact(i.statement)]
        found[label] = min(hits, key=lambda i: len(i.statement)) if hits else None
    return found


def test_the_labelled_set_is_large_enough():
    pages = _yaml("pages.yaml")["pages"]

    assert len(pages) >= MIN_PAGES
    assert len({p["ref"] for p in pages}) >= 10
    assert sum(len(p["requirements"]) for p in pages) >= 180
    prose = sum(1 for p in pages for label in p["requirements"]
                if _unit(label, None) == "prose")
    assert prose >= 60, f"only {prose} prose labels; prose needs its own measurement"


def test_recall_by_unit_and_by_mode_holds_its_floor(labelled):
    """95% on lettered, table, pin and catalog; prose at the level measured on the labelled
    pages (module docstring), reported so it is tracked and not claimed."""
    hits: Counter[str] = Counter()
    totals: Counter[str] = Counter()
    misses = defaultdict(list)
    for page, mode, items in labelled:
        for label, item in _matches(page, items).items():
            for key in (mode, _unit(label, item)):
                totals[key] += 1
                if item is not None:
                    hits[key] += 1
                else:
                    misses[key].append(f"{page['ref']} p{page['page']}: {label}")
    recall = {key: hits[key] / totals[key] for key in totals}
    units = {u: f"{hits[u]}/{totals[u]} = {recall.get(u, 0):.3f}" for u in UNITS}
    modes = {m: f"{hits[m]}/{totals[m]} = {recall[m]:.3f}"
             for m in ("statement", "pin", "catalog")}
    overall = sum(hits[u] for u in UNITS) / sum(totals[u] for u in UNITS)
    print(f"\nrecall by unit: {units}; by mode: {modes}; overall {overall:.3f}")

    assert set(recall) >= {"statement", "pin", "catalog", *UNITS}
    for key, value in sorted(recall.items()):
        # the statement mode is prose plus lettered items, so prose's misses are its misses
        floor = PROSE_FLOOR if key in ("prose", "statement") else RECALL_FLOOR
        assert value >= floor, f"{key} recall {value:.3f}: " + "; ".join(misses[key])


def test_noise_on_the_labelled_pages_is_reported_and_bounded(labelled):
    noise = total = 0
    by_kind: Counter[str] = Counter()
    for page, _, items in labelled:
        matched = {id(i) for i in _matches(page, items).values() if i is not None}
        on_page = [i for i in items if i.page == page["page"]]  # a spanning item counts once
        total += len(on_page)
        for item in on_page:
            if id(item) not in matched:
                noise += 1
                by_kind[item.kind] += 1
    share = noise / total
    print(f"\nnoise: {noise}/{total} = {share:.3f} ({dict(sorted(by_kind.items()))})")

    assert share <= NOISE_CEILING


def test_every_probe_is_in_the_register_or_the_pin():
    reg = register.load(REPO_ROOT)
    pin = {t["id"]: t for t in register.read(REPO_ROOT, register.NIST_TASKS, "nist-tasks",
                                             [])["tasks"]}
    probes = _yaml("probes.yaml")["probes"]
    findings = set()
    misses = []
    checked = 0
    for probe in probes:
        findings.add(probe["finding"])
        if probe.get("source") == "none":
            assert probe["reason"]
            continue
        checked += 1
        wanted = compact(probe["phrase"])
        if probe.get("in") == "pin":
            hit = any(wanted in compact(p) for p in pin[probe["task"]][probe["field"]])
        else:
            hit = any(wanted in compact(e["statement"])
                      for ref, e in reg.live() if ref == probe["ref"])
        if not hit:
            misses.append(f"{probe['finding']} {probe['ref']}: {probe['phrase']}")
    print(f"\nprobes: {checked - len(misses)}/{checked}")

    assert findings >= {f"N-{n}" for n in range(1, 20)} | {f"D-{n}" for n in range(1, 19)}
    assert (checked - len(misses)) / checked >= PROBE_FLOOR, misses


def test_headline_phrases_the_first_extractor_missed_are_present():
    """The review that forced this rework counted these at zero."""
    reg = register.load(REPO_ROOT)
    statements = defaultdict(list)
    for ref, entry in reg.live():
        statements[ref].append(compact(entry["statement"]))
    wanted = [("SP800-37R2", "authorizationtouse", 10), ("SP800-37R2", "denialofauthorization", 3),
              ("FIPS199", "cannotbeassigned", 1), ("DODCIO-CATO", "softwarebillofmaterials", 1),
              ("SP800-137", "metrics", 30)]
    for ref, phrase, floor in wanted:
        if ref not in reg.files:  # a fork may drop a reference
            continue
        count = sum(phrase in s for s in statements[ref])
        assert count >= floor, (ref, phrase, count)


# The raw-line reader below shares nothing with extract.py: a line the extractor misreads
# (joined onto a caption, started on an excluded page) must still be found or reported.
_RAW_PAGE = re.compile(r"^<!-- page (\d+)")
_RAW_LIST = re.compile(r"^(?:\([a-z0-9]{1,2}\)|[a-z]{1,2}\.|\d{1,2}\.|[•●▪–-]|o)\s")
_RAW_CAPTION = re.compile(r"^(?:FIGURE|TABLE|Figure|Table) \S+[.:]\s")
_RAW_FOOTNOTE = re.compile(r"^\d{1,3} (?=\S)")
_RAW_FIELD = re.compile(r"^([A-Z][A-Za-z ]{3,40}):\s*")


def _mostly_caps(line):
    letters = [c for c in line if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) >= 0.7 * len(letters)


def _raw_lines(source, text):
    """(page, line) for every line of every in-scope page that must be in an entry or a
    rejection. Stated exclusions: page markers, blank lines, markdown headings unless they
    carry a list label, table rows, lines in mostly capitals (headings and figure text), a
    figure or table caption with the wrapped lines under it that open in lowercase, and in a
    pin-mode source the paragraph under a task field label that conformance/nist-tasks.yaml
    holds. A skipped paragraph runs to the next blank line, or over a page break when the next
    page opens in lowercase (its continuation). A footnote number opening a line and a
    stripped field label (`Discussion:`) are removed from the line."""
    skip, strip = register.labels_for(source)
    in_scope = {p for s in source["scopes"] for p in range(s["pages"][0], s["pages"][1] + 1)}
    out = []
    page = 0
    skipping = None  # "field" or "caption" while inside one
    blank = broke = False  # a blank line, a page break, since the last line of text
    for raw in text.splitlines():
        line = raw.strip()
        m = _RAW_PAGE.match(line)
        if m:
            page = int(m.group(1))
            broke = True
            continue
        if not line:
            blank = True
            continue
        lower = line[0].islower()
        if skipping == "field" and (not blank or (broke and lower)) \
                or skipping == "caption" and not blank and lower:
            blank = broke = False
            continue
        skipping = None
        blank = broke = False
        if page not in in_scope or line.startswith("|"):
            continue
        if line.startswith("#"):
            line = line.lstrip("# ")
            if not _RAW_LIST.match(line):
                continue
        field = _RAW_FIELD.match(line)
        if field and field.group(1) in skip:
            skipping = "field"
            continue
        if field and field.group(1) in strip:
            line = line[field.end():]
        if _RAW_CAPTION.match(line):
            skipping = "caption"
            continue
        if _mostly_caps(line):
            continue
        out.append((page, _RAW_FOOTNOTE.sub("", line)))
    return out


def _accounted(line, held):
    """The line is in one held text, or (a long paragraph split at a sentence boundary inside
    the line) ends one held text and starts the next."""
    wanted = compact(line)
    if not wanted or wanted in held:
        return True
    return any(f"{wanted[:k]}\n" in held and f"\n{wanted[k:]}" in held
               for k in range(1, len(wanted)))


def test_no_raw_line_in_scope_is_dropped_silently():
    """Every line of every in-scope page of every source, read from references/text with the
    reader above and never through extract.blocks(), is contained in an entry or in a recorded
    rejection with a known reason. The fakes this has caught: short labels `continue`d with no
    record (485 blocks), and a reader built on the extractor's own blocks that inherited its
    joins, so a paragraph absorbed by a caption or started on an excluded page (L-0053) was
    invisible to it."""
    reg = register.load(REPO_ROOT)
    index = register.index_entries(REPO_ROOT)
    lost = []
    checked = 0
    for ref, source in sorted(reg.sources.items()):
        entry = index.get(ref)
        if source["mode"] == "excluded" or entry is None or entry["status"] != "ok":
            continue
        text = register.text_of(REPO_ROOT, entry)
        doc = reg.files[ref]
        assert all(r["reason"] in extract.REJECT_REASONS for r in doc["rejected"]), ref
        held = "\n" + "\n".join(
            [compact(e["statement"]) for e in doc["requirements"] if not e.get("removed")]
            + [compact(r["text"]) for r in doc["rejected"]]) + "\n"
        for page, line in _raw_lines(source, text):
            checked += 1
            if not _accounted(line, held):
                lost.append(f"{ref} p{page}: {line[:80]}")
    print(f"\nin-scope raw lines accounted for: {checked - len(lost)}/{checked}")

    assert checked > 0
    assert lost == [], f"{len(lost)} in-scope lines are in no entry and no rejection:\n" \
        + "\n".join(lost[:40])


_RAW_MASK = re.compile(r"\d+")
_FOOTER_SHARE = 0.10  # a footnote that recurs, or a line of a table, stays well under this
_FOOTER_LENGTH = 6  # "Page 3" and a phone number count; a bare page number has its own check


def _footer_lines(text):
    """(page -> packed text, packed page-closing lines that recur as a footer), read from the
    text and not through extract: a line with a digit among the last two of a page that closes
    at least two pages and a tenth of the document."""
    pages = {}
    page = 0
    for raw in text.splitlines():
        m = _RAW_PAGE.match(raw.strip())
        if m:
            page = int(m.group(1))
            pages[page] = []
        elif page and raw.strip():
            pages[page].append(raw.strip())
    closing = {line for lines in pages.values() for line in lines[-2:]
               if re.search(r"\d", line) and len(compact(line)) >= _FOOTER_LENGTH
               and not line.startswith("|")}
    seen = {key: 0 for key in {_RAW_MASK.sub("#", line) for line in closing}}
    for lines in pages.values():
        for key in {_RAW_MASK.sub("#", line) for line in lines[-2:]} & seen.keys():
            seen[key] += 1
    least = max(2, _FOOTER_SHARE * len(pages))
    footers = {compact(line) for line in closing if seen[_RAW_MASK.sub("#", line)] >= least}
    return {n: compact(" ".join(lines)) for n, lines in pages.items()}, footers


def test_no_statement_starts_on_a_page_number_or_holds_a_footer():
    """An entry whose statement opens with a bare number and whose words sit on the next page
    is a page number joined to the page after it: `rmf refs show` cannot find it at its cited
    page, though FW-REQ-001 passes. The statement of any entry holding a recurring page-closing
    line has absorbed a footer. The cure is `footers` in conformance/sources.yaml."""
    reg = register.load(REPO_ROOT)
    index = register.index_entries(REPO_ROOT)
    bad = []
    for ref, doc in sorted(reg.files.items()):
        entry = index.get(ref)
        if entry is None or not entry.get("text"):
            continue
        pages, footers = _footer_lines(register.text_of(REPO_ROOT, entry))
        for e in doc["requirements"]:
            if e.get("removed"):
                continue
            page, statement = e["citation"]["page"], compact(e["statement"])
            numbered = re.match(r"\d{1,3} ((?:\S+ ){5}\S+)", e["statement"])
            if numbered:
                opening = compact(numbered.group(1))
                if opening not in pages.get(page, "") and opening in pages.get(page + 1, ""):
                    bad.append(f"{e['id']} p{page}: starts on a page number")
            if any(f in statement for f in footers):
                bad.append(f"{e['id']} p{page}: holds a footer")

    assert bad == [], "\n".join(bad[:40])
