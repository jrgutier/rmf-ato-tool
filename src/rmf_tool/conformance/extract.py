"""Requirement candidates from the committed text of a reference (deterministic, offline).

A document is read as blocks: paragraphs, table rows, headings and footnotes, each on the page
it starts. A paragraph that a page break interrupts is one block. Headings are context, never
candidates. A candidate is a lettered or bulleted item, a table row, or a prose paragraph.

The prose unit is the paragraph, not the sentence. Regexes classify sentences at about half
noise and a third misses (the premise test of the p10 rework), so a paragraph enters the
register whole when any of its sentences reads as a requirement: an obligation (``modal``), a
role doing something, an artifact being handled or an applicability statement
(``indicative``), a verb-first instruction (``imperative``), or a recommendation or permission
(``should``). The paragraph's kind is its strongest sentence's. A reviewer reads the whole
paragraph, so a sentence the regexes miss cannot vanish. A paragraph no sentence of which
reads as a requirement is not dropped: it is recorded as rejected with its reason, so a
reviewer can sample the rejected set and measure false rejects. Recall against hand-read
pages is measured in tests/unit/test_conformance_recall.py.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import Any

from rmf_tool.refs.toc import compact

KINDS = ("lettered", "table", "modal", "should", "indicative", "imperative")
PROSE_KINDS = ("modal", "should", "indicative", "imperative")
# Strongest first: the kind of a paragraph is the first of these any sentence has.
_KIND_RANK = ("modal", "indicative", "imperative", "should")
ANCHOR_WORDS = 12
LEAD_IN_WORDS = 6
TITLE_WORDS = 4
MIN_SENTENCE_WORDS = 4
CONTEXT_CHARS = 200
# A paragraph over this many words is split at sentence boundaries into runs under it, each
# its own candidate (the 860-word privacy overlay paragraph is no unit of review).
MAX_PARAGRAPH_WORDS = 300

# Why a prose paragraph or a table row is not a candidate. Every rejection carries one.
REJECT_REASONS = {
    "short": "fewer than four words: a fragment, a heading or a figure label",
    "lead-in": "a single sentence ending with a colon that states no obligation itself: context "
               "for the items that follow",
    "no-marker": "no sentence states an obligation, recommendation, permission, role action, "
                 "artifact handling, applicability or instruction",
    "not-normative": "the only sentences with a marker describe the document, an example or "
                     "a figure",
    "not-a-statement": "an example, figure or table caption",
    "fragment": "a table row of fewer than three words",
    "leader": "a table-of-contents line with dot leaders",
    "label-only": "a run-in heading or a short list label that names what follows, under no "
                  "lead-in that enumerates it",
    "legend": "a figure legend or key row: abbreviations or scale values and their expansions",
    "footer": "a page footer declared in conformance/sources.yaml",
}

MODAL = re.compile(
    r"\b(?:will|must|shall|required to|is required|are required|cannot|can not|may not|"
    r"prohibited|responsible for|responsibilit(?:y|ies)|accountable for|accountability|"
    r"requires?|needs? to|is mandatory|not authorized|not permitted|not granted|is halted|"
    r"are halted|in accordance with)\b", re.I)
SHOULD = re.compile(r"\b(?:should|recommended|encouraged|expected to|discretion|is critical|"
                    r"are critical|is essential|are essential)\b", re.I)
# "may" and "can" state a permission only when a role or an artifact holds it, as the subject
# right before the verb; elsewhere they describe ("a human may serve as a security mechanism",
# "the use of enterprise architecture can enhance").
PERMISSIVE = re.compile(r"\b(?:may|can)\b", re.I)
MIN_BULLET_WORDS = 3
MIN_ROW_WORDS = 3
APPLICABILITY = re.compile(r"\b(?:applies|apply|applicable) (?:only|to|equally)\b", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are)\s+(?:(?:not|also|then|typically|generally|usually|often|normally|"
    r"formally)\s+)?(?:made available|based on|documented|approved|"
    r"provided|submitted|reviewed|updated|established|determined|assessed|included|recorded|"
    r"maintained|retained|conducted|performed|signed|selected|applied|tailored|used|specified|"
    r"informed|guided|consistent with|developed|reported|identified|designated|"
    r"appointed|registered|authorized|issued|subject to|addressed|accomplished|adopted|"
    r"finalized|coordinated|completed)\b", re.I)
# Sentences about the document, a figure or an argument, not about anyone's obligation.
NOT_NORMATIVE = re.compile(
    r"^(?:for example|for instance|examples? (?:of|include)|in contrast|the benefits? of|"
    r"the objective (?:is|of)|the purpose of this|this (?:publication|document|guideline|"
    r"section|chapter|appendix|instruction|issuance|figure|table) (?:describes|provides|"
    r"establishes|is organized|addresses|defines|contains|presents|introduces|discusses|"
    r"shows|summarizes|lists|illustrates))\b|"
    r"\b(?:is provided in (?:appendix|section|chapter)|(?:is|are) (?:presented|discussed|"
    r"described) (?:in|below|above|here))\b", re.I)
NOT_A_STATEMENT = re.compile(
    r"^(?:EXAMPLE|Examples?(?: \d|\s*\(|:| of\b| from\b)|Figure \d|FIGURE \d|Fig\. \d|Table \d|"
    r"TABLE \d)")
_ROLES = (
    r"organizations?|agenc(?:y|ies)|federal agencies|authorizing officials?(?: or (?:authorizing "
    r"official )?designated representatives?)?|system owners?|common control providers?|"
    r"control assessors?|assessors?|assessment teams?|senior agency official for privacy|"
    r"senior agency information security officer|senior accountable official for risk "
    r"management|risk executive(?: \(function\))?|chief information officer|information "
    r"owners?(?:/stewards?| or stewards?)?|mission or business owners?|head of agency|"
    r"system security officers?|system privacy officers?|system administrators?|systems? "
    r"security engineers?|privacy engineers?|enterprise architects?|security architects?|"
    r"privacy architects?|users?|user representatives?|program managers?|project managers?|"
    r"PMs?|AOs?|AODRs?|SOs?|SCAs?|ISSMs?|ISSOs?|CISOs?|CIOs?|URs?|MDAs?|DAs?|SAOPs?(?: or "
    r"designee)?|DoD Components?|DoD Component heads|DoD Component CIOs?|DoD CIO|DoD CISO|"
    r"RMF TAG|DoD ISRMC|USD\([A-Z&]+\)|tier \d officials|customer organizations?|provider "
    r"organizations?|receiving organizations?|IT and PIT systems|systems|the organization|"
    r"the program|programs|the department|components|leadership|senior leaders|officials|"
    r"stakeholders|developers|system developers|the requirements validation authority|"
    r"milestone decision authorit(?:y|ies)|decision authorit(?:y|ies)|contractors?|"
    r"the government|the Government|the DoD Information Enterprise|the RMF(?: process)?|"
    r"the DoD|DoD|the enterprise|enterprises?")
_VERBS = (
    r"prepares?|reviews?|provides?|determines?|develops?|conducts?|approves?|retains?|makes?|"
    r"documents?|maintains?|ensures?|works?|assess(?:es)?|reports?|updates?|selects?|"
    r"identif(?:y|ies)|establish(?:es)?|defines?|obtains?|monitors?|coordinates?|implements?|"
    r"prioritizes?|designates?|appoints?|accepts?|authorizes?|renders?|issues?|serves?|"
    r"receives?|rel(?:y|ies)|submits?|verif(?:y|ies)|informs?|consults?|collaborates?|"
    r"oversees?|leads?|manages?|supports?|participates?|communicates?|tracks?|analyzes?|"
    r"responds?|plans?|allocates?|considers?|uses?|employs?|appl(?:y|ies)|specif(?:y|ies)|"
    r"tailors?|executes?|performs?|assigns?|registers?|brings?|do not|does not|is responsible|"
    r"are responsible|can recommend|categorizes?|confers?|compl(?:y|ies)|initiates?|"
    r"completes?|promotes?|advises?|directs?|validates?|evaluates?|incorporates?|integrates?|"
    r"address(?:es)?|protects?|shares?|requests?|decides?|chooses?|includes?|recommends?|"
    r"notif(?:y|ies)|limits?|controls?|tests?|describes?|records?|produces?|deliver(?:s|)|"
    r"dedicates?|revisits?|reassess(?:es)?|remains?|halts?|revises?|elevates?|"
    r"adjusts?|aligns?|cross-references?|leverages?|collects?|aggregates?|correlates?|"
    r"grants?|transfers?|withdraws?|rescinds?|terminates?|operates?|consists?|acts?|"
    r"adopts?|finalizes?|follows?|refers?|seeks?|signs?|accounts? for")
# Named decisions and artifacts of the process: a sentence that says what one is, holds or
# does states a requirement on it ("The authorization package includes...").
_ARTIFACTS = (
    r"(?:type|facility|joint|ongoing|common control|initial|single) authorizations?|"
    r"authorizations? to (?:use|operate)|denials? of authorization|authorization "
    r"(?:packages?|decisions?|boundar(?:y|ies)|termination dates?|frequenc(?:y|ies))|"
    r"(?:c?ATOs?|ATUs?|IATTs?)(?: determinations?)?|plans? of action and milestones|POA&Ms?|"
    r"(?:system )?security plans?|privacy plans?|security and privacy plans?|assessment plans?|"
    r"assessment reports?|security and privacy assessment (?:plans?|reports?)|risk assessments?|"
    r"risk assessment reports?|risk management strateg(?:y|ies)|continuous monitoring "
    r"strateg(?:y|ies)|ISCM strateg(?:y|ies)|executive summar(?:y|ies)|security "
    r"categorizations?|control baselines?|baselines?|overlays?|tailoring|system "
    r"registrations?|cybersecurity strateg(?:y|ies)|program protection plans?|PPPs?|TEMPs?|"
    r"SSPs?|SARs?|SAPs?|contingency plans?|incident response plans?|configuration "
    r"management plans?|SCRM plans?|C-SCRM plans?|privacy impact assessments?|interconnection "
    r"security agreements?|memoranda of (?:agreement|understanding)|(?:security |privacy |common |"
    r"compensating )?controls?|control enhancements?")
_ARTIFACT_VERBS = (
    r"is|are|includes?|contains?|identif(?:y|ies)|describes?|addresses?|allows?|documents?|"
    r"provides?|conveys?|specif(?:y|ies)|establish(?:es)?|defines?|supports?|covers?|remains?|"
    r"requires?|does not|do not|leverages?|serves?|begins?|ends?|expires?|takes? effect")
# A footnote number glued to a word or its punctuation ("authorization159 is",
# "controls.60 This"); removed before a sentence is classified, never from the statement.
_FOOTNOTE_MARK = re.compile(r"(?:(?<=[a-z\)”])|(?<=[a-z\)”][.,;:]))\d{1,3}(?=\s|$)")
# Between a subject and its verb: adverbs, and one parenthetical clause set off by commas
# ("the AO, in coordination with the SO, approves").
_BETWEEN = (r"(?:,?\s+(?:also|then|first|jointly|formally|explicitly|typically|only|still|and|"
            r"or))*(?:,\s+[^,.;:]{1,80},)?,?\s+")
ARTIFACT = re.compile(rf"\b(?:{_ARTIFACTS}){_BETWEEN}(?:not\s+)?(?:{_ARTIFACT_VERBS})\b",
                      re.I)
_PERMITTED_SUBJECT = re.compile(
    rf"\b(?:{_ROLES}|{_ARTIFACTS})\d{{0,3}}(?:\s+\S+){{0,3}}\s+(?:may|can)\b|"
    r"\bmay be \w+(?:ed|en)\b", re.I)  # a passive permission: "may be downgraded"
INDICATIVE = re.compile(rf"\b(?:{_ROLES}){_BETWEEN}(?:{_VERBS})\b", re.I)
_IMPERATIVES = (
    "Establish|Develop|Ensure|Identify|Conduct|Review|Maintain|Document|Implement|Provide|"
    "Verify|Monitor|Track|Update|Determine|Appoint|Approve|Apply|Assess|Select|Categorize|"
    "Register|Prepare|Report|Coordinate|Define|Analyze|Make|Take|Support|Obtain|Submit|Use|"
    "Employ|Tailor|Authorize|Assign|Complete|Initiate|Specify|Describe|Record|Integrate|"
    "Incorporate|Address|Evaluate|Validate|Communicate|Share|Include|Allocate|Plan|Manage|"
    "Protect|Respond|Comply|Perform|Execute|Oversee|Advise|Promote|Consult|Collaborate|"
    "Recommend|Designate|Issue|Consider|Decide|Request|Require|Notify|Limit|Control|Test|"
    "Serve|Adhere|Collect|Correlate|Prioritize|Remediate|Reassess|"
    "Reauthorize|Refer|Follow|Produce|Deliver|Accept|Confirm|Compare|Transition|Leverage")
IMPERATIVE = re.compile(rf"^(?:{_IMPERATIVES})\b(?! (?:of|to|for)\b)")

BULLETS = ("•", "●", "▪", "-", "–", "o")
_PAGE = re.compile(r"^<!-- page (\d+)(?: [^>]*)? -->$")
# List labels: DoD a. (1) (a) 1., NIST bullets (SP 800-161 sub-bullets are a lowercase o),
# and SP 800-160 activity tasks (VA-2.2).
_LABEL = re.compile(r"^(\([a-z]{1,2}\)|\(\d{1,2}\)|(?:[a-z]|([a-z])\2)\.|\d{1,2}\.|•|●|▪|-|–|"
                    r"o(?=\s+[A-Z])|[A-Z]{2}-\d{1,2}\.\d{1,2})"
                    r"(?:\s+(?=\S)|(?<=\))(?=[A-Z]))")
_ACTIVITY = re.compile(r"^[A-Z]{2}-\d{1,2}$")
_NUMBERED = re.compile(r"^(?:#+ )?(\d{1,2}(?:\.\d{1,2}){1,3})\.?\s+(\S.*)$")
_CAPS = re.compile(r"^[A-Z][A-Z0-9 ,/&()’'—–-]{7,90}\.?$")
_CAPTION = re.compile(r"^(?:FIGURE|TABLE|Figure|Table) (?:[A-Z]-?)?\d{1,2}(?:[-.]\d{1,2})?[.:]\s")
_LEGEND_CELL = re.compile(r"^[A-Z][A-Za-z&/]{0,7}: ")
_LEADER = re.compile(r"\.{4,}|(?:\. ){3,}|…{2,}")
_FOOTNOTE = re.compile(r"^\d{1,3} [A-Z\[“]")
_SENTENCE_END = re.compile(r"(?:[.?!]|(?<=[a-z\)”])[.?!]\d{1,3})\s+(?=[A-Z(“\"])")
_NO_BREAK = re.compile(
    r"\b(?:e\.g|i\.e|etc|No|Nos|vs|Dr|Mr|Ms|U\.S|Sec|Rev|Vol|Fig|cf|al|App|Sect|Pub|Inc|Jr|L)\.$")
_TRAILING_WORDS = re.compile(r"(?<=[a-z\)”][.?!])\s+[a-z][a-z -]*$")
_TERMINAL = ('.', ':', ';', '?', '!', '.”', '.)', '”', ')')
_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
_TITLE_WORD = re.compile(r"^(?:[A-Z0-9&(]|of$|and$|the$|for$|or$|in$|to$|a$|an$)")
_FIELD_LABEL = re.compile(r"^([A-Z][A-Za-z ]{3,40}):\s+(?=\S)")


class SourceError(Exception):
    """A source declaration cannot be applied to the text of its document."""


@dataclass(frozen=True)
class Block:
    page: int
    text: str
    kind: str  # paragraph | row | header | heading | footnote | footer
    end_page: int = 0


@dataclass(frozen=True)
class Item:
    """One requirement candidate. ``anchor`` and ``occurrence`` identify it in the document."""
    kind: str
    page: int
    statement: str
    locator: str
    context: str
    anchor: str = ""
    occurrence: int = 1
    end_page: int = 0  # the page a block rejoined over a page break ends on

    def spans(self, page: int) -> bool:
        return self.page <= page <= (self.end_page or self.page)


@dataclass(frozen=True)
class Rejected:
    """An in-scope paragraph or row that is not a candidate, and why (REJECT_REASONS)."""
    page: int
    locator: str
    reason: str
    text: str


@dataclass
class Extraction:
    items: list[Item] = field(default_factory=list)
    rejected: list[Rejected] = field(default_factory=list)


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _join_wrapped_rows(rows: list[str]) -> list[str]:
    """A row whose only filled cell continues the row above (a cell wrapped onto new lines by
    the PDF extraction) is folded into it, so the row reads as one statement."""
    out: list[list[str]] = []
    for row in rows:
        if _SEPARATOR.match(row):
            out.append([row])
            continue
        cells = _cells(row)
        filled = [n for n, c in enumerate(cells) if c]
        previous = out[-1] if out else None
        if (len(filled) == 1 and previous is not None and len(previous) == len(cells)
                and not _SEPARATOR.match(previous[0]) and previous[filled[0]]):
            previous[filled[0]] = f"{previous[filled[0]]} {cells[filled[0]]}"
            continue
        out.append(cells)
    return [r[0] if len(r) == 1 and _SEPARATOR.match(r[0]) else "| " + " | ".join(r) + " |"
            for r in out]


def _paragraphs(text: str) -> list[Block]:
    """Paragraphs, rows and headings in document order. Text before the first page marker
    (the extraction's own header comment) is nobody's. A caption line is a paragraph of its
    own: only a wrapped continuation (a line opening in lowercase) joins it, so the body text
    that follows a caption with no blank line between is never swallowed by it."""
    blocks: list[Block] = []
    lines: list[str] = []
    start = page = 0
    caption = False

    def flush() -> None:
        nonlocal caption
        if lines:
            blocks.append(Block(start, " ".join(lines), "paragraph"))
            lines.clear()
        caption = False

    rows: list[str] = []

    def flush_rows() -> None:
        joined = _join_wrapped_rows(rows)
        for n, row in enumerate(joined):
            if _SEPARATOR.match(row):
                continue
            header = n + 1 < len(joined) and bool(_SEPARATOR.match(joined[n + 1]))
            blocks.append(Block(page, row, "header" if header else "row"))
        rows.clear()

    for raw in text.splitlines():
        line = raw.strip()
        m = _PAGE.match(line)
        if m:
            flush()
            flush_rows()
            page = int(m.group(1))
        elif not line or page == 0:
            flush()
            flush_rows()
        elif line.startswith("|"):
            flush()
            rows.append(line)
        else:
            flush_rows()
            if line.startswith("#"):
                flush()
                body = line.lstrip("# ")
                if _LABEL.match(body):
                    lines.append(body)  # a bullet the extraction tagged as a heading
                    start = page
                    flush()
                else:
                    blocks.append(Block(page, line, "heading"))
                continue
            if lines and (_LABEL.match(line) or _FOOTNOTE.match(line) or _CAPTION.match(line)
                          or (caption and not line[0].islower())):
                flush()
            if not lines:
                start = page
            lines.append(line)
            caption = caption or bool(_CAPTION.match(line))
    flush()
    flush_rows()
    return blocks


def is_regex(pattern: str) -> bool:
    try:
        re.compile(pattern)
    except re.error:
        return False
    return True


def _page_footers(paragraphs: list[Block], footers: Sequence[str]) -> set[int]:
    """Positions of the paragraphs that close a page and match a declared footer pattern. A
    page number the extraction left in (it sits above the margin band) is a paragraph like
    any other, so without this the next page joins to it."""
    closing: defaultdict[int, list[int]] = defaultdict(list)
    for n, block in enumerate(paragraphs):
        if block.kind == "paragraph":
            closing[block.page].append(n)
    out: set[int] = set()
    for positions in closing.values():
        for n in reversed(positions):
            if not any(re.search(p, paragraphs[n].text) for p in footers):
                break
            out.add(n)
    return out


def blocks(text: str, footers: Sequence[str] = ()) -> list[Block]:
    """The document's blocks, with footnotes tagged and paragraphs rejoined over page breaks:
    a paragraph with no closing punctuation continues in the next paragraph of a later page
    unless that one opens a list item. Footnotes sit between the two halves and are neither
    joined nor allowed to block the join, and neither are ``footers``, the patterns
    conformance/sources.yaml declares for a footer the extraction left in the text, so a
    sentence crossing a page keeps its first page and never absorbs one. A caption, an
    all-caps line or a contents line with dot leaders never continues onto the next page: it
    has no closing punctuation because it is not a sentence, and joining would hide the
    paragraph that follows it (the 2026-10-31 review found in-scope lines lost this way)."""
    out: list[Block] = []
    last_prose: int | None = None
    paragraphs = _paragraphs(text)
    closing = _page_footers(paragraphs, footers)
    for n, block in enumerate(paragraphs):
        if n in closing:
            out.append(replace(block, kind="footer"))
            continue
        body = block.text.lstrip("# ")
        # A numbered line the extraction tagged as a heading is a footnote only when it reads
        # as a sentence; `# 1 Introduction` is a heading.
        if _FOOTNOTE.match(body) and (block.kind == "paragraph"
                                      or (block.kind == "heading" and body.endswith(_TERMINAL))):
            out.append(Block(block.page, body, "footnote"))
            continue
        last = out[last_prose] if last_prose is not None else None
        if (block.kind == "paragraph" and last is not None
                and block.page > (last.end_page or last.page)
                and not _FOOTNOTE_MARK.sub("", last.text).endswith(_TERMINAL)
                and not _LABEL.match(block.text) and not heading_like(block.text)):
            out[last_prose] = replace(last, text=f"{last.text} {block.text}", end_page=block.page)
            continue
        out.append(block)
        continues = block.kind == "paragraph" and not heading_like(block.text) \
            and not _LEADER.search(block.text)
        last_prose = len(out) - 1 if continues else None
    return out


def sentences(paragraph: str) -> list[str]:
    out = []
    start = 0
    for m in _SENTENCE_END.finditer(paragraph):
        head = paragraph[start:m.start() + 1]
        if _NO_BREAK.search(head):
            continue
        out.append(paragraph[start:m.end()].strip())
        start = m.end()
    out.append(paragraph[start:].strip())
    return [s for s in out if s]


def without_trailing_label(sentence: str) -> str:
    """``sentence`` without lower-case words after its last full stop. A two-column glossary
    read line by line puts the next term's label there, and sentences() never splits before a
    lower-case word. An abbreviation is no sentence end, as in sentences()."""
    m = _TRAILING_WORDS.search(sentence)
    if m is None or _NO_BREAK.search(sentence[:m.start()]):
        return sentence
    return sentence[:m.start()]


def _is_label_only(body: str) -> bool:
    """``c. Decisions.``, ``a. System Threat Analysis.`` or ``c. PMs will:``: a run-in heading
    or a short lead-in, which names what follows and requires nothing itself."""
    words = body.rstrip(".:").split()
    if body.endswith(":"):
        return len(words) <= LEAD_IN_WORDS
    return len(words) <= TITLE_WORDS and all(_TITLE_WORD.match(w) for w in words)


def _marker(sentence: str) -> str | None:
    """The kind a sentence's markers give it, before the not-normative filter."""
    if MODAL.search(sentence):
        return "modal"
    if INDICATIVE.search(sentence) or PASSIVE.search(sentence) or ARTIFACT.search(sentence) \
            or APPLICABILITY.search(sentence):
        return "indicative"
    if SHOULD.search(sentence):
        return "should"
    if PERMISSIVE.search(sentence) and _PERMITTED_SUBJECT.search(sentence):
        return "should"
    if IMPERATIVE.match(sentence):
        return "imperative"
    return None


def classify(sentence: str) -> str | None:
    """The kind of a prose sentence, or None when it states no requirement. A sentence ending
    with a colon is judged like any other: "the PM will also dedicate program resources to
    the following by monitoring:" obliges the PM before its list starts."""
    if len(sentence.split()) < MIN_SENTENCE_WORDS:
        return None
    sentence = _FOOTNOTE_MARK.sub("", sentence)
    if NOT_NORMATIVE.search(sentence):
        return None
    return _marker(sentence)


def marked_sentences(statement: str) -> list[str]:
    """The sentences of a prose statement that read as requirements: each is an obligation
    that evidence must cite before the entry is ``covered`` (FW-REQ-003)."""
    return [s for s in sentences(statement) if classify(s) is not None]


def split_long(text: str) -> list[str]:
    """A paragraph over MAX_PARAGRAPH_WORDS as runs of whole sentences under it, in order;
    a shorter paragraph is returned whole. Deterministic: the same text splits the same way."""
    if len(text.split()) <= MAX_PARAGRAPH_WORDS:
        return [text]
    runs: list[list[str]] = [[]]
    for sentence in sentences(text):
        if runs[-1] and sum(len(s.split()) for s in runs[-1]) + len(sentence.split()) \
                > MAX_PARAGRAPH_WORDS:
            runs.append([])
        runs[-1].append(sentence)
    return [" ".join(run) for run in runs if run]


def paragraph_kind(text: str) -> tuple[str | None, str]:
    """The kind of a prose paragraph (its strongest sentence's) or None with the reason it is
    rejected."""
    parts = sentences(text)
    kinds = {classify(s) for s in parts} - {None}
    for kind in _KIND_RANK:
        if kind in kinds:
            return kind, ""
    if len(parts) == 1 and text.endswith(":"):
        return None, "lead-in"
    if len(text.split()) < MIN_SENTENCE_WORDS:
        return None, "short"
    if any(_marker(_FOOTNOTE_MARK.sub("", s)) for s in parts):
        return None, "not-normative"
    return None, "no-marker"


@dataclass
class _Trail:
    """Where the walk is: the section, and the open list items with their lead-in sentences."""
    section: str = ""
    title: str = ""
    lead_in: str = ""
    path: list[tuple[int, str, str]] = field(default_factory=list)  # depth, label, lead-in
    # a prose lead-in ending with ":" whose body is the next paragraph, not a list
    pending_body: bool = False

    def enter_section(self, number: str, title: str) -> None:
        self.section, self.title, self.lead_in = number, title, ""
        self.path = []
        self.pending_body = False

    def retitle(self, title: str) -> None:
        """An unnumbered all-caps line: a heading or figure text. The section number stays."""
        self.title, self.lead_in = title, ""
        self.path = []
        self.pending_body = False

    def enter_label(self, label: str, lead_in: str = "") -> None:
        self.pending_body = False
        depth = _depth(label)
        self.path = [p for p in self.path if p[0] < depth]
        self.path.append((depth, label.rstrip("."), lead_in))

    def lead(self, text: str) -> None:
        if self.path:
            depth, label, _ = self.path[-1]
            self.path[-1] = (depth, label, text)
        else:
            self.lead_in = text

    @property
    def enumerated(self) -> bool:
        """The innermost open item sits under a lead-in that announces a list ("includes the
        following:"), so a short label under it is one of the enumerated things."""
        above = self.path[-2][2] if len(self.path) > 1 else self.lead_in
        return above.endswith(":")

    @property
    def locator(self) -> str:
        labels = [q[1] for q in self.path]
        section = self.section.rstrip(".")
        if labels and section and labels[0].startswith(f"{section}."):
            section = ""  # an activity task label repeats its activity number
        return ".".join(p for p in [section, *labels] if p)

    def leave_bullets(self) -> None:
        self.path = [p for p in self.path if p[1] not in BULLETS]

    @property
    def context(self) -> str:
        parts = [self.title, self.lead_in, *(q[2] for q in self.path[:-1])]
        return " ".join(p for p in parts if p)[:CONTEXT_CHARS].rstrip()


def _depth(label: str) -> int:
    """DoD issuances nest a. (1) (a) 1.; bullets sit below any of them."""
    if label in BULLETS:
        return 4
    if label[0].isupper():
        return 0  # an activity task, VA-2.2
    if label.endswith("."):
        return 3 if label[0].isdigit() else 0
    return 1 if label[1].isdigit() else 2


def _is_heading_line(title: str) -> bool:
    letters = [c for c in title if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) >= 0.7 * len(letters)


def heading_like(text: str) -> bool:
    """A paragraph the walk reads as a heading or a caption: context, never a candidate and
    never a rejection. Every other in-scope paragraph, footnote and row is one or the other
    (tests/unit/test_conformance_recall.py checks this against the register)."""
    numbered = _NUMBERED.match(text)
    return bool(numbered and _is_heading_line(numbered.group(2))) or bool(_ACTIVITY.match(text)) \
        or bool(_CAPS.match(text)) or bool(_CAPTION.match(text))


def _prose(text: str, block: Block, trail: _Trail, *, skip_labels: frozenset[str],
           strip_labels: frozenset[str]) -> tuple[list[Item], list[Rejected]]:
    """A paragraph or footnote as candidates (one, or one per run of an over-long paragraph)
    and rejections. A trailing lead-in sentence becomes context for what follows; the
    paragraph after it is its body."""
    if NOT_A_STATEMENT.match(text):
        return [], [Rejected(block.page, trail.locator, "not-a-statement", text)]
    label = _FIELD_LABEL.match(text)
    if label:
        if label.group(1) in skip_labels:
            return [], []  # a pin field: conformance/nist-tasks.yaml holds it
        if label.group(1) in strip_labels:
            text = text[label.end():]
    body = trail.pending_body
    trail.pending_body = False
    locator, context = trail.locator, trail.context
    if text.endswith(":"):
        trail.lead(sentences(text)[-1])
        trail.pending_body = True
    else:
        trail.lead("")  # a paragraph ends the list its lead-in announced
    items, rejected = [], []
    for run in split_long(text):
        kind, reason = paragraph_kind(run)
        if kind is None and body and reason != "short":
            kind = "indicative"  # the body of a lead-in states what the lead-in announces
        if kind is None:
            rejected.append(Rejected(block.page, locator, reason, run))
        else:
            items.append(Item(kind, block.page, run, locator, context, end_page=block.end_page))
    return items, rejected


def statement_items(document: list[Block], pages: tuple[int, int], *, tables: bool = True,
                    skip_labels: frozenset[str] = frozenset(),
                    strip_labels: frozenset[str] = frozenset(),
                    claimed: frozenset[int] = frozenset()) -> Extraction:
    """Lettered items, table rows and requirement paragraphs on ``pages`` (inclusive), and
    every in-scope paragraph or row that is not one, with its reason. ``skip_labels`` drop a
    ``Label: value`` block whole (the task fields the NIST pin holds); ``strip_labels`` keep
    the value (``Discussion:``). A block belongs to the scope its first page is in; a block
    that starts on a page no scope claims (``claimed`` is every scope's pages) and ends in
    this one belongs here, so a paragraph rejoined over the edge of an exclusion is read."""
    out = Extraction()
    trail = _Trail()
    heading_open = False  # a numbered heading may wrap onto the next all-caps line

    def in_scope(block: Block) -> bool:
        if pages[0] <= block.page <= pages[1]:
            return True
        return block.page not in claimed and pages[0] <= block.end_page <= pages[1]

    def prose(text: str, block: Block) -> None:
        items, rejected = _prose(text, block, trail, skip_labels=skip_labels,
                                 strip_labels=strip_labels)
        out.items += items
        out.rejected += rejected

    for block in document:
        text = block.text
        if block.kind == "heading":
            body = text.lstrip("# ").rstrip(".")
            numbered = _NUMBERED.match(text)
            if _CAPTION.match(body):
                trail.retitle(body)  # a figure or table title, inside its section
                heading_open = False
                continue
            # An unnumbered heading ("TASK S-2", "GLOSSARY") is the locator of what follows.
            trail.enter_section(*(numbered.groups() if numbered else (body, "")))
            heading_open = bool(numbered)
            continue
        if not in_scope(block):
            continue
        if block.kind == "footer":
            out.rejected.append(Rejected(block.page, trail.locator, "footer", text))
            continue
        if block.kind == "header":
            trail.pending_body = False
            continue
        if _LEADER.search(text):
            trail.pending_body = False
            out.rejected.append(Rejected(block.page, trail.locator, "leader", text))
            continue
        if block.kind == "row":
            trail.pending_body = False
            if tables:
                cells = [c for c in _cells(text) if c]
                row = " | ".join(cells)
                if sum(len(c.split()) for c in cells) < MIN_ROW_WORDS:
                    out.rejected.append(Rejected(block.page, trail.locator, "fragment", row))
                elif sum(bool(_LEGEND_CELL.match(c)) for c in cells) * 2 >= len(cells):
                    out.rejected.append(Rejected(block.page, trail.locator, "legend", row))
                else:
                    out.items.append(Item("table", block.page, row, trail.locator or "table",
                                          trail.context))
            continue
        if block.kind == "footnote":
            pending, trail.pending_body = trail.pending_body, False
            trail.leave_bullets()
            prose(text.split(" ", 1)[1], block)
            trail.pending_body = pending
            continue
        numbered = _NUMBERED.match(text)
        if numbered and _is_heading_line(numbered.group(2)):
            trail.enter_section(numbered.group(1), numbered.group(2).rstrip("."))
            heading_open = True
            continue
        if _ACTIVITY.match(text):
            trail.enter_section(text, "")
            heading_open = True
            continue
        if _CAPS.match(text) or _CAPTION.match(text):
            if heading_open:
                trail.title = f"{trail.title} {text}".strip().rstrip(".")
            else:
                trail.retitle(text)
            continue
        heading_open = False
        label = _LABEL.match(text)
        if label:
            trail.enter_label(label.group(1))
            body = text[label.end():]
            short = _is_label_only(body) or (label.group(1) in BULLETS
                                             and len(body.split()) < MIN_BULLET_WORDS)
            if short and (body.endswith(":") or not trail.enumerated):
                # "c. PMs will:" or "c. Decisions.": context for what follows, not a statement
                reason = "lead-in" if body.endswith(":") else "label-only"
                out.rejected.append(Rejected(block.page, trail.locator, reason, text))
                trail.lead(body.rstrip("."))
                continue
            out.items.append(Item("lettered", block.page, text, trail.locator, trail.context,
                                  end_page=block.end_page))
            if body.endswith(":"):
                trail.lead(body)
            continue
        trail.leave_bullets()
        prose(text, block)
    return out


def _strip_label(statement: str) -> str:
    label = _LABEL.match(statement)
    return statement[label.end():] if label else statement


def _prefix(item: Item, length: int, pages: dict[int, str]) -> str:
    """The first ``length`` words of the statement, cut back to what is on the cited page."""
    words = _strip_label(item.statement).split()[:length]
    page = pages.get(item.page, "")
    while len(words) > 1 and compact(" ".join(words)) not in page:
        words.pop()
    return " ".join(words)


def _on_its_page(item: Item, pages: dict[int, str]) -> Item:
    """A sentence late in a block rejoined over a page break starts on the block's next page."""
    opening = compact(" ".join(_strip_label(item.statement).split()[:3]))
    if opening not in pages.get(item.page, "") and opening in pages.get(item.page + 1, ""):
        return replace(item, page=item.page + 1)
    return item


def identify(items: list[Item], pages: dict[int, str]) -> list[Item]:
    """Anchor every item: a prefix long enough to be unique. Identical statements are told
    apart by ``occurrence`` in document order."""
    seen: Counter[str] = Counter()
    numbered = []
    for item in (_on_its_page(i, pages) for i in items):
        seen[item.statement] += 1
        numbered.append(replace(item, occurrence=seen[item.statement]))
    length = {id(i): ANCHOR_WORDS for i in numbered}
    anchored = {id(i): _prefix(i, ANCHOR_WORDS, pages) for i in numbered}
    while True:
        groups: defaultdict[str, list[Item]] = defaultdict(list)
        for i in numbered:
            groups[anchored[id(i)]].append(i)
        grew = False
        for group in groups.values():
            if len({g.statement for g in group}) < 2:
                continue
            for i in group:
                longer = _prefix(i, length[id(i)] + 4, pages)
                length[id(i)] += 4
                if longer != anchored[id(i)]:
                    anchored[id(i)] = longer
                    grew = True
        if not grew:
            break
    return [replace(i, anchor=anchored[id(i)]) for i in numbered]


def passages(document: list[Block]) -> dict[int, str]:
    """Compact text per page from its blocks. A block rejoined over a page break counts on
    both pages, so a statement that crosses the break matches whole: what FW-REQ-001 checks."""
    parts: defaultdict[int, list[str]] = defaultdict(list)
    for block in document:
        parts[block.page].append(block.text)
        if block.end_page:
            parts[block.end_page].append(block.text)
    return {page: compact(" ".join(texts)) for page, texts in parts.items()}


@lru_cache(maxsize=64)
def raw_pages(text: str) -> dict[int, str]:
    """Compact text per page as ``rmf refs show --page`` sees it. Cached per text: the rules
    extract, count pages and anchor the same document several times in one run."""
    parts: defaultdict[int, list[str]] = defaultdict(list)
    page = 0
    for line in text.splitlines():
        m = _PAGE.match(line.strip())
        if m:
            page = int(m.group(1))
        else:
            parts[page].append(line)
    return {number: compact(" ".join(lines)) for number, lines in parts.items()}


def page_count(text: str) -> int:
    return max(raw_pages(text), default=0)


def extract(text: str, scopes: list[dict[str, Any]], *,
            skip_labels: frozenset[str] = frozenset(),
            strip_labels: frozenset[str] = frozenset(),
            footers: Sequence[str] = ()) -> Extraction:
    """Items and rejections of every scope, in document order."""
    document = blocks(text, footers)
    out = Extraction()
    claimed = frozenset(p for s in scopes for p in range(s["pages"][0], s["pages"][1] + 1))
    for scope in scopes:
        first, last = scope["pages"]
        found = statement_items(document, (first, last), tables=scope.get("tables", True),
                                skip_labels=skip_labels, strip_labels=strip_labels,
                                claimed=claimed)
        out.items += found.items
        out.rejected += found.rejected
    out.items = identify(out.items, raw_pages(text))
    return out
