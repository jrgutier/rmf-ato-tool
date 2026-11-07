"""``conformance/``: the requirements register, read and regenerated.

Generated fields of an entry come from the source text; reviewed fields survive every
re-extraction. A statement is matched to its entry by locator and statement, then by locator
and anchor, then by a statement or anchor that is unique in the document. A match that is not
one-to-one, or whose statement changed, carries ``needs_review`` until a reviewer clears it. A
statement that disappears stays in the file as ``removed: true``, so its ID is never reused
(INV-3).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema

from rmf_tool import refs
from rmf_tool.conformance import extract, nist_pin
from rmf_tool.refs.currency import text_controls
from rmf_tool.refs.toc import compact
from rmf_tool.yamlload import safe_load

DIRECTORY = "conformance"
SCHEMA_DIR = f"{DIRECTORY}/schema"
SOURCES = f"{DIRECTORY}/sources.yaml"
WORK_ITEMS = f"{DIRECTORY}/work-items.yaml"
TRIAGE = f"{DIRECTORY}/triage.yaml"
POLICY = f"{DIRECTORY}/policy.yaml"
TEXT_HASHES = f"{DIRECTORY}/text-hashes.yaml"
BINDINGS = f"{DIRECTORY}/bindings.yaml"
REQUIREMENTS_DIR = f"{DIRECTORY}/requirements"
NIST_TASKS = f"{DIRECTORY}/nist-tasks.yaml"
NIST_VOCABULARY = f"{DIRECTORY}/nist-vocabulary.yaml"
NIST_WAIVERS = f"{DIRECTORY}/nist-waivers.yaml"

# not-a-requirement: extraction noise, such as a heading or a noun list; it holds no duty.
# not-applicable: a real requirement the tool has nothing to hold it with.
NOT_A_REQUIREMENT = "not-a-requirement"
STATUSES = ("candidate", "covered", "partial", "deferred", "not-applicable", NOT_A_REQUIREMENT)
REVIEWED_STATUSES = ("covered", "partial", "deferred")
REVIEWED = ("status", "reason", "evidence", "work_item", "approved_by", "triaged_by",
            "needs_review", "removal_reason", "promoted", "ruling_sought")
# The kind of an entry a reviewer promoted from the rejected set or from a passage the
# extractor read as context (`rmf conformance promote`); it states an obligation.
PROMOTED_KIND = "promoted"
# Index kinds that enter the register. OSCAL files are pinned by REF-005 instead.
SOURCE_KINDS = ("pdf", "web")

_ORDER = ("id", "citation", "kind", "locator", "context", "statement", "occurrence", *REVIEWED,
          "removed")
_INFORMATION_TYPE = re.compile(r"^(?:#+ )?([CD](?:\.\d+){2,3})\s.*Information Type", re.M)
_REFERENCE = re.compile(
    r"^(Committee on National Security Systems (?:Instruction|Policy Number) \d+"
    r"|DoD (?:Directive|Instruction) [\d.]*\d"
    r"|Executive Order \d+"
    r"|National Institute of Standards and Technology Special Publication [\dA-Z-]+"
    r"|Office of Management and Budget Memorandum [\dA-Z-]+"
    r"|United States Code, Title \d+, (?:Section|Chapter) \d+)", re.M)
REFERENCE_LIST_DOCUMENT = "DODI8510.01"
PIN_SKIP_LABELS = frozenset(k for k, v in nist_pin._LABELS.items() if v is not None)
PIN_STRIP_LABELS = frozenset({"Discussion"})


@dataclass
class Register:
    """Everything under ``conformance/``. ``problems`` are (path, message): unreadable or
    schema-invalid files, reported by FW-REQ-001."""
    sources: dict[str, dict[str, Any]] = field(default_factory=dict)
    reference_list: list[dict[str, Any]] = field(default_factory=list)
    files: dict[str, dict[str, Any]] = field(default_factory=dict)
    work_items: dict[str, dict[str, Any]] = field(default_factory=dict)
    patterns: list[dict[str, Any]] = field(default_factory=list)
    fan_out_exceptions: list[dict[str, Any]] = field(default_factory=list)
    retirements: list[dict[str, Any]] = field(default_factory=list)  # policy.yaml, per document
    noise: list[dict[str, Any]] = field(default_factory=list)  # policy.yaml, per document
    text_hashes: dict[str, str] = field(default_factory=dict)
    waivers: list[dict[str, Any]] = field(default_factory=list)
    omissions: list[dict[str, Any]] = field(default_factory=list)  # vocabulary `omit` phrases
    bindings: list[dict[str, Any]] = field(default_factory=list)
    problems: list[tuple[str, str]] = field(default_factory=list)

    def entries(self) -> Iterable[tuple[str, dict[str, Any]]]:
        for ref, doc in sorted(self.files.items()):
            for entry in doc["requirements"]:
                yield ref, entry

    def live(self) -> Iterable[tuple[str, dict[str, Any]]]:
        return ((ref, e) for ref, e in self.entries() if not e.get("removed"))

    def entry(self, ident: str) -> dict[str, Any] | None:
        return next((e for _, e in self.entries() if e["id"] == ident), None)

    def bound(self, work_item: str) -> list[dict[str, Any]]:
        return [e for _, e in self.live() if e.get("work_item") == work_item]

    def waived(self, work_item: str) -> list[dict[str, Any]]:
        """FW-TASK-002 waivers and vocabulary omissions that name the work item: a pin field
        is not a register entry, so a work item on the task contract binds through them."""
        return [w for w in [*self.waivers, *self.omissions] if w.get("work_item") == work_item]


def requirements_path(ref: str) -> str:
    return f"{REQUIREMENTS_DIR}/{ref}.yaml"


def _validator(repo: Path, name: str) -> Any:
    schema = json.loads((repo / SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


_GENERATED_LINE = re.compile(r"^(  - |    |  |)([a-z_]+):(?: (.*))?$")
_KEY = re.compile(r"^[a-z_]+: ")
_PLAIN = re.compile(r"^[A-Za-z][A-Za-z0-9.-]*$")


def read_generated(text: str) -> Any | None:
    """The document of a file exactly as ``render_requirements`` writes it, parsed a hundred
    times faster than the YAML loader reads it (every value is a JSON scalar on its own
    line). None when any line does not fit, so a hand-edited file goes to the YAML loader
    and is judged as YAML."""
    document: dict[str, Any] = {}
    items: list[Any] | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        if raw.startswith("  - ") and items is not None and not _KEY.match(raw[4:]):
            try:
                items.append(json.loads(raw[4:]))
            except ValueError:
                return None
            continue
        m = _GENERATED_LINE.match(raw)
        if m is None:
            return None
        indent, key, value = m.group(1), m.group(2), m.group(3) or ""
        try:
            parsed = json.loads(value) if value else None
        except ValueError:
            if not _PLAIN.match(value):
                return None
            parsed = value  # ref, mode and catalog are written bare
        if indent == "":
            if value == "":
                items = document[key] = []
            else:
                document[key] = parsed
                items = None
        elif indent == "  - " and items is not None:
            items.append({key: parsed})
        elif indent == "    " and items and isinstance(items[-1], dict):
            items[-1][key] = parsed
        else:
            return None
    return document


def read(repo: Path, rel: str, schema: str, problems: list[tuple[str, str]]) -> Any | None:
    """A YAML file validated against its schema, or None with the problems recorded."""
    try:
        text = (repo / rel).read_text(encoding="utf-8")
        data = read_generated(text) if schema == "requirements" else None
        if data is None:
            data = safe_load(text)
    except OSError as exc:
        problems.append((rel, f"cannot read: {exc.strerror or exc}"))
        return None
    except Exception as exc:  # ruamel raises several unrelated parser error types
        problems.append((rel, f"not valid YAML: {exc}"))
        return None
    errors = sorted(_validator(repo, schema).iter_errors(data),
                    key=lambda e: [str(p) for p in e.absolute_path])
    for error in errors[:5]:
        where = "/".join(map(str, error.absolute_path)) or "(root)"
        problems.append((rel, f"{where}: {error.message[:200]}"))
    return None if errors else data


def load(repo: Path) -> Register:
    reg = Register()
    sources = read(repo, SOURCES, "sources", reg.problems)
    if sources is not None:
        reg.sources = {s["ref"]: s for s in sources["documents"]}
        reg.reference_list = sources["reference_list"]
    work_items = read(repo, WORK_ITEMS, "work-items", reg.problems)
    if work_items is not None:
        reg.work_items = {w["id"]: w for w in work_items["work_items"]}
    triage = read(repo, TRIAGE, "triage", reg.problems)
    if triage is not None:
        reg.patterns = triage["patterns"]
    policy = read(repo, POLICY, "policy", reg.problems)
    if policy is not None:
        reg.fan_out_exceptions = policy["fan_out_exceptions"]
        reg.retirements = policy.get("retirements", [])
        reg.noise = policy.get("noise", [])
    hashes = read(repo, TEXT_HASHES, "text-hashes", reg.problems)
    if hashes is not None:
        reg.text_hashes = hashes["hashes"]
    # The task-contract files and the bindings are optional: a register without a NIST pin
    # (a test fixture) has none, and a work item then binds through entries alone.
    if (repo / NIST_WAIVERS).is_file():
        waivers = read(repo, NIST_WAIVERS, "nist-waivers", reg.problems)
        if waivers is not None:
            reg.waivers = waivers["waivers"]
    if (repo / NIST_VOCABULARY).is_file():
        words = read(repo, NIST_VOCABULARY, "nist-vocabulary", reg.problems)
        if words is not None:
            reg.omissions = [p for p in words["phrases"] if "omit" in p]
    if (repo / BINDINGS).is_file():
        bindings = read(repo, BINDINGS, "bindings", reg.problems)
        if bindings is not None:
            reg.bindings = bindings["bindings"]
    for path in sorted((repo / REQUIREMENTS_DIR).glob("*.yaml")):
        doc = read(repo, f"{REQUIREMENTS_DIR}/{path.name}", "requirements", reg.problems)
        if doc is not None:
            reg.files[path.stem] = doc
    return reg


# --- re-extraction -----------------------------------------------------------------------


@dataclass
class Changes:
    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    ambiguous: list[str] = field(default_factory=list)


@dataclass
class Built:
    document: dict[str, Any]
    changes: Changes
    scope_yields: list[tuple[dict[str, Any], int]] = field(default_factory=list)


def _generated(ref: str, item: extract.Item) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "citation": {"ref": ref, "page": item.page, "anchor": item.anchor},
        "kind": item.kind,
        "locator": item.locator,
        "context": item.context,
        "statement": item.statement,
    }
    if item.occurrence > 1:
        entry["occurrence"] = item.occurrence
    return entry


def _matches(pattern: Mapping[str, Any], ref: str, entry: Mapping[str, Any]) -> bool:
    if pattern["ref"] != ref:
        return False
    if "pages" in pattern:
        first, last = pattern["pages"]
        if not first <= entry["citation"]["page"] <= last:
            return False
    statement = pattern.get("statement")
    context = pattern.get("context")
    return (statement is None or re.search(statement, entry["statement"]) is not None) and \
        (context is None or re.search(context, entry["context"]) is not None)


def _triage(ref: str, entry: dict[str, Any], patterns: list[dict[str, Any]]) -> None:
    """Bulk ``not-applicable`` from reviewed patterns. A reviewer who sets another status
    removes ``triaged_by``; a pattern that stops matching returns its entries to candidate."""
    if entry["status"] != "candidate" and "triaged_by" not in entry:
        return
    pattern = next((p for p in patterns if _matches(p, ref, entry)), None)
    if pattern is not None:
        entry.update(status="not-applicable", reason=pattern["reason"], triaged_by=pattern["id"])
    elif "triaged_by" in entry:
        entry["status"] = "candidate"
        del entry["triaged_by"], entry["reason"]


def _pair(old_entries: list[dict[str, Any]], items: list[extract.Item],
          changes: Changes) -> dict[int, dict[str, Any]]:
    """New item position -> old entry. Groups keyed on (locator, statement) pair in document
    order; a group whose size changed marks every reviewed member for review, because the
    pairing inside it is a guess. Leftovers pair on (locator, anchor), then on a statement or
    anchor unique among the leftovers."""
    matched: dict[int, dict[str, Any]] = {}
    used: set[str] = set()
    old_groups: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in old_entries:
        old_groups[(entry["locator"], entry["statement"])].append(entry)
    new_groups: defaultdict[tuple[str, str], list[int]] = defaultdict(list)
    for pos, item in enumerate(items):
        new_groups[(item.locator, item.statement)].append(pos)
    for key, positions in new_groups.items():
        olds = old_groups.get(key, [])
        for pos, old in zip(positions, olds, strict=False):
            matched[pos] = old
            used.add(old["id"])
        if olds and len(olds) != len(positions):
            changes.ambiguous += [o["id"] for o in olds if o["status"] != "candidate"]

    def leftovers() -> list[dict[str, Any]]:
        return [e for e in old_entries if e["id"] not in used]

    by_anchor: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in leftovers():
        by_anchor[(entry["locator"], entry["citation"]["anchor"])].append(entry)
    for pos, item in enumerate(items):
        olds = [o for o in by_anchor.get((item.locator, item.anchor), []) if o["id"] not in used]
        if pos not in matched and len(olds) == 1:
            matched[pos] = olds[0]
            used.add(olds[0]["id"])
    for old_key, new_key in ((lambda e: e["statement"], lambda i: i.statement),
                             (lambda e: e["citation"]["anchor"], lambda i: i.anchor),
                             (lambda e: _stem(e["locator"], e["citation"]["anchor"]),
                              lambda i: _stem(i.locator, i.anchor))):
        counts: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in leftovers():
            counts[old_key(entry)].append(entry)
        unique = {key: olds[0] for key, olds in counts.items() if len(olds) == 1}
        for pos, item in enumerate(items):
            old = unique.get(new_key(item))
            if pos not in matched and old is not None and old["id"] not in used:
                matched[pos] = old
                used.add(old["id"])
    for pos, item in enumerate(items):  # a footer dropped from the edge of a statement
        wanted = compact(item.statement)
        olds = [o for o in leftovers() if _lost_an_edge(o, item, wanted)]
        if pos not in matched and len(olds) == 1:
            matched[pos] = olds[0]
            used.add(olds[0]["id"])
    return matched


def _lost_an_edge(old: Mapping[str, Any], item: extract.Item, wanted: str) -> bool:
    """``old`` is live and the new statement is most of it, nearby. A short sentence inside a
    long or a dead paragraph is another statement, and must not take its ID or its review."""
    held = compact(old["statement"])
    return not old.get("removed") and wanted in held and 2 * len(wanted) >= len(held) \
        and abs(item.page - old["citation"]["page"]) <= 1


def _stem(locator: str, anchor: str) -> str:
    """The locator and the anchor's first six words: an anchor that grew or shrank at its end
    (a sentence edited after its opening) still pairs when nothing else in the section opens
    the same way."""
    return locator + "|" + " ".join(anchor.split()[:6])


def reconcile(ref: str, entries: list[dict[str, Any]], items: list[extract.Item],
              patterns: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Changes]:
    """The register of ``ref`` for freshly extracted ``items``, keeping IDs and reviewed fields."""
    changes = Changes()
    matched = _pair(entries, items, changes)
    used = {old["id"] for old in matched.values()}
    next_number = max((int(e["id"].rsplit("-", 1)[1]) for e in entries), default=0) + 1
    out: list[dict[str, Any]] = []
    for pos, item in enumerate(items):
        old = matched.get(pos)
        entry = _generated(ref, item)
        if old is None:
            entry["id"] = f"REQ-{ref}-{next_number:04d}"
            entry["status"] = "candidate"
            next_number += 1
            changes.added.append(entry["id"])
        else:
            entry["id"] = old["id"]
            entry.update({k: old[k] for k in REVIEWED if k in old})
            entry.pop("removal_reason", None)
            if old["statement"] != item.statement:
                changes.changed.append(entry["id"])
                if old["status"] != "candidate":
                    entry["needs_review"] = True  # a candidate has no review to redo
            if old["id"] in changes.ambiguous:
                entry["needs_review"] = True
        _triage(ref, entry, patterns)
        out.append(entry)
    for old in entries:
        if old["id"] in used:
            continue
        if old.get("promoted") and not old.get("removed"):
            out.append(dict(old))  # a reviewer's entry; the extractor does not produce it
        else:
            if not old.get("removed"):
                changes.removed.append(old["id"])
            out.append({**old, "removed": True})
    out.sort(key=lambda e: int(e["id"].rsplit("-", 1)[1]))
    return [{k: e[k] for k in _ORDER if k in e} for e in out], changes


def _check_promoted(entries: list[dict[str, Any]], passages: Mapping[int, str]) -> None:
    """A promoted entry whose statement is no longer in the passage it cites is flagged for
    review, never dropped: the reviewer who promoted it decides what the change means."""
    for entry in entries:
        if entry.get("promoted") and not entry.get("removed") and \
                compact(entry["statement"]) not in passages.get(entry["citation"]["page"], ""):
            entry["needs_review"] = True


def _not_promoted(rejected: list[extract.Rejected],
                  entries: list[dict[str, Any]]) -> list[extract.Rejected]:
    """The rejections minus those a live promoted entry now states."""
    stated = {(e["citation"]["page"], compact(e["statement"])) for e in entries
              if e.get("promoted") and not e.get("removed")}
    return [r for r in rejected if (r.page, compact(r.text)) not in stated]


def catalog_ids(source: Mapping[str, Any], text: str) -> list[str]:
    if source["catalog"] == "controls":
        return sorted(text_controls(text))
    return sorted(set(_INFORMATION_TYPE.findall(text)))


def text_of(repo: Path, entry: Mapping[str, Any]) -> str:
    return (repo / entry["text"]["path"]).read_text(encoding="utf-8")


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def block_options(source: Mapping[str, Any]) -> dict[str, Any]:
    """How a source's text splits into blocks: the footer and running-header patterns it
    declares that compile (FW-REQ-001 reports the others) and whether it declares
    ``cut_items``."""
    def patterns(key: str) -> tuple[str, ...]:
        return tuple(f["pattern"] for f in source.get(key, []) if extract.is_regex(f["pattern"]))

    return {"footers": patterns("footers"), "headers": patterns("headers"),
            "cut_items": "cut_items" in source}


def reading_options(source: Mapping[str, Any]) -> dict[str, Any]:
    """``block_options`` plus how the walk reads headings (``run_in_headings``)."""
    return {**block_options(source), "run_in_headings": "run_in_headings" in source}


def labels_for(source: Mapping[str, Any]) -> tuple[frozenset[str], frozenset[str]]:
    if source["mode"] == "pin":
        return PIN_SKIP_LABELS, PIN_STRIP_LABELS
    return frozenset(), frozenset()


def build(reg: Register, source: Mapping[str, Any], text: str) -> Built:
    """The requirements document of one source, regenerated from its text."""
    ref = source["ref"]
    current = reg.files.get(ref, {})
    document: dict[str, Any] = {"schema_version": 1, "ref": ref, "mode": source["mode"]}
    if source["mode"] == "catalog":
        ids = catalog_ids(source, text)
        document.update(catalog=source["catalog"], count=len(ids), ids=ids)
    skip, strip = labels_for(source)
    scopes = source.get("scopes", [])
    found = extract.extract(text, scopes, skip_labels=skip, strip_labels=strip,
                            **reading_options(source)) if scopes else extract.Extraction()
    entries, changes = reconcile(ref, current.get("requirements", []), found.items, reg.patterns)
    _check_promoted(entries, extract.passages(extract.blocks(text, **block_options(source))))
    document["requirements"] = [{k: e[k] for k in _ORDER if k in e} for e in entries]
    document["rejected"] = [{"page": r.page, "locator": r.locator, "reason": r.reason,
                             "text": r.text} for r in _not_promoted(found.rejected, entries)]
    yields = [(scope, sum(1 for i in found.items
                          if scope["pages"][0] <= i.page <= scope["pages"][1]))
              for scope in scopes]
    return Built(document, changes, yields)


def reference_list_keys(text: str) -> list[str]:
    """Documents in the REFERENCES section of DoDI 8510.01, in order."""
    return _REFERENCE.findall(text.rsplit("## REFERENCES", 1)[-1])


def pin_document(repo: Path) -> dict[str, Any]:
    return {"schema_version": 1, "ref": nist_pin.REF, "tasks": nist_pin.parse_repo(repo)}


# --- reviewed fields ---------------------------------------------------------------------


def binding_hits(reg: Register, binding: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The live entries of the binding's document whose statement contains its phrase."""
    wanted = compact(binding["phrase"])
    return [e for ref, e in reg.live()
            if ref == binding["ref"] and wanted in compact(e["statement"])]


def binding_marks(reg: Register) -> dict[str, dict[str, Any]]:
    """The work_item marks that bring the entries in line with the bindings; only for
    bindings that name exactly one entry (rules.binding_problems reports the rest)."""
    marks: dict[str, dict[str, Any]] = {}
    for binding in reg.bindings:
        hits = binding_hits(reg, binding)
        if len(hits) == 1 and hits[0].get("work_item") != binding["work_item"]:
            marks[hits[0]["id"]] = {"work_item": binding["work_item"]}
    return marks


class MarkError(Exception):
    """A review that the register cannot record."""


def mark(reg: Register, ident: str, **fields: Any) -> dict[str, Any]:
    """Set reviewed fields on a live entry. ``None`` deletes a field. A removed entry takes
    ``removal_reason`` alone, the review FW-REQ-004 asks of a reviewed entry that left its
    source. The caller writes the file; the rules say whether the result is acceptable."""
    entry = reg.entry(ident)
    if entry is None or (entry.get("removed") and set(fields) != {"removal_reason"}):
        raise MarkError(f"no live entry {ident}" + (
            "; a removed entry takes --removal-reason alone" if entry else ""))
    for key, value in fields.items():
        if key not in REVIEWED:
            raise MarkError(f"{key} is not a reviewed field; reviewed fields are "
                            f"{', '.join(REVIEWED)}")
        if value is None:
            entry.pop(key, None)
        else:
            entry[key] = value
    if "status" in fields:
        entry.pop("triaged_by", None)  # a status set by hand is no longer the pattern's
    return entry


def _rejection_at(doc: Mapping[str, Any], page: int, wanted: str) -> dict[str, Any] | None:
    return next((r for r in doc.get("rejected", [])
                 if r["page"] == page and wanted in compact(r["text"])), None)


def _block_at(text: str, page: int, wanted: str,
              source: Mapping[str, Any]) -> extract.Block | None:
    for block in extract.blocks(text, **block_options(source)):
        if block.kind in ("heading", "header", "footer"):
            continue
        if block.page <= page <= (block.end_page or block.page) \
                and wanted in compact(block.text):
            return block
    return None


def _sentence_of(paragraph: str, wanted: str, anchor: str) -> str:
    """The one sentence of ``paragraph`` that holds the anchor."""
    hits = [s for s in map(extract.without_trailing_label, extract.sentences(paragraph))
            if wanted in compact(s)]
    if len(hits) != 1:
        raise MarkError(f"{anchor!r} is in {len(hits)} sentences of that paragraph, not one; "
                        "use words of a single sentence")
    return hits[0]


def _promoted_entry(doc: Mapping[str, Any], ident: str) -> dict[str, Any]:
    entry = next((e for e in doc["requirements"] if e["id"] == ident), None)
    if entry is None or entry.get("removed") or not entry.get("promoted"):
        raise MarkError(f"{ident} is no live promoted entry of {doc['ref']}; --replace rebases "
                        "only a reviewer's entry, the extractor re-reads its own")
    return entry


def promote(reg: Register, ref: str, text: str, page: int, anchor: str, reason: str | None,
            *, sentence: bool = False, replace: str | None = None) -> dict[str, Any]:
    """A reviewer's entry for a passage the extractor rejected or read as context
    (`rmf conformance promote`): the rejection on ``page`` holding ``anchor``, else the block
    of the text on that page holding it; with ``sentence``, only the sentence of it that holds
    the anchor. The entry gets the next ID of its document, cites the page with the passage's
    opening words, and carries ``promoted: {reason}``. The caller writes the file; FW-REQ-001
    then checks the citation like any other.

    ``replace`` names a live promoted entry whose passage moved (a footer left it, a page
    shifted): it is rebased onto the passage found the same way, keeping its ID, its status,
    its evidence and every other reviewed field, and its reason unless ``reason`` gives a new
    one. Rebasing is the review the move asked for, so ``needs_review`` is cleared."""
    doc = reg.files.get(ref)
    if doc is None or ref not in reg.sources:
        raise MarkError(f"no requirements file for {ref}")
    target = _promoted_entry(doc, replace) if replace else None
    if target is None and not reason:
        raise MarkError("a new promoted entry needs --reason: why the passage is a requirement")
    wanted = compact(anchor)
    if not wanted:
        raise MarkError("the anchor needs a word or two of the passage")
    for entry in doc["requirements"]:
        if entry is not target and not entry.get("removed") \
                and entry["citation"]["page"] == page and wanted in compact(entry["statement"]):
            raise MarkError(f"{entry['id']} already states that passage on page {page}")
    rejection = _rejection_at(doc, page, wanted)
    if rejection is not None:
        statement, locator = rejection["text"], rejection["locator"]
    else:
        block = _block_at(text, page, wanted, reg.sources[ref])
        if block is None:
            raise MarkError(f"{anchor!r} is in no rejection and no paragraph of {ref} page "
                            f"{page}; see rmf conformance page {ref} {page}")
        statement = block.text.split(" ", 1)[1] if block.kind == "footnote" else block.text
        locator = ""
    if sentence:
        statement = _sentence_of(statement, wanted, anchor)
    if rejection is not None and compact(statement) == compact(rejection["text"]):
        doc["rejected"].remove(rejection)  # part of it stays rejected, as re-extraction finds it
    item = extract.Item(PROMOTED_KIND, page, statement, locator, "")
    item = extract.identify([item], extract.raw_pages(text))[0]
    if target is not None:
        target.pop("occurrence", None)
        target.update(_generated(ref, item))
        target.pop("needs_review", None)
        if reason:
            target["promoted"] = {**target["promoted"], "reason": reason}
        rebased = {k: target[k] for k in _ORDER if k in target}
        target.clear()
        target.update(rebased)
        return target
    numbers = [int(e["id"].rsplit("-", 1)[1]) for e in doc["requirements"]]
    entry = {**_generated(ref, item), "id": f"REQ-{ref}-{max(numbers, default=0) + 1:04d}",
             "status": "candidate", "promoted": {"reason": reason}}
    doc["requirements"].append({k: entry[k] for k in _ORDER if k in entry})
    return doc["requirements"][-1]


# --- writing -----------------------------------------------------------------------------


def _scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_requirements(document: Mapping[str, Any]) -> str:
    """Stable bytes: one line per field, JSON-quoted (valid YAML), so a diff shows one fact."""
    lines = [f"# Generated by `rmf conformance extract` from references/text/{document['ref']}.md."
             " Reviewed fields are set",
             "# with `rmf conformance mark`; everything else is regenerated (INV-2).",
             "schema_version: 1", f"ref: {document['ref']}", f"mode: {document['mode']}"]
    if document["mode"] == "catalog":
        lines += [f"catalog: {document['catalog']}", f"count: {document['count']}", "ids:"]
        lines += [f"  - {_scalar(i)}" for i in document["ids"]]
    if not document["requirements"]:
        lines.append("requirements: []")
    else:
        lines.append("requirements:")
    for entry in document["requirements"]:
        first = True
        for key, value in entry.items():
            lines.append(f"  {'- ' if first else '  '}{key}: {_scalar(value)}")
            first = False
    rejected = document.get("rejected", [])
    lines.append("# In-scope paragraphs and rows that are not candidates, each with its reason"
                 " (rmf_tool.conformance.extract.REJECT_REASONS);")
    lines.append("# sample them with `rmf conformance sample --rejected`.")
    lines.append("rejected: []" if not rejected else "rejected:")
    lines += [f"  - {_scalar(r)}" for r in rejected]
    return "\n".join(lines) + "\n"


def render_pin(document: Mapping[str, Any]) -> str:
    lines = [f"# Generated by `rmf conformance extract` from {nist_pin.TEXT_PATH}, Chapter 3. "
             "Do not edit (INV-2).",
             "schema_version: 1", f"ref: {document['ref']}", "tasks:"]
    for task in document["tasks"]:
        first = True
        for key, value in task.items():
            if isinstance(value, list):
                lines.append(f"    {key}:" if value else f"    {key}: []")
                lines += [f"      - {_scalar(p)}" for p in value]
            else:
                lines.append(f"  {'- ' if first else '  '}{key}: {_scalar(value)}")
            first = False
    return "\n".join(lines) + "\n"


def render_text_hashes(hashes: Mapping[str, str]) -> str:
    lines = ["# SHA-256 of each references/text/<REF>.md the register was reviewed against.",
             "# Written only by `rmf conformance accept-text`; FW-REQ-005 fails while a text",
             "# differs (INV-2).",
             "schema_version: 1", "hashes:"]
    lines += [f"  {ref}: {_scalar(digest)}" for ref, digest in sorted(hashes.items())]
    return "\n".join(lines) + "\n"


def write_if_changed(path: Path, text: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_requirements(repo: Path, document: Mapping[str, Any]) -> bool:
    return write_if_changed(repo / requirements_path(document["ref"]),
                            render_requirements(document))


def index_entries(repo: Path) -> dict[str, Any]:
    return {e["id"]: e for e in refs.entries(refs.load_index(repo))}
