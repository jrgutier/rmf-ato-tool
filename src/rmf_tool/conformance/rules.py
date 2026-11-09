"""FW-REQ-* and FW-TASK-002: the register and the NIST task pin, checked by `rmf validate`."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rmf_tool.conformance import evidence, extract, nist_pin, register
from rmf_tool.conformance.register import Register
from rmf_tool.findings import Finding
from rmf_tool.framework.citations import ERROR, Resolver, describe
from rmf_tool.framework.model import TASK_CITATION_REF, Framework
from rmf_tool.refs.toc import compact

# One target behind this many requirements is more likely a catch-all than this many proofs;
# conformance/policy.yaml records the reviewed exceptions.
FAN_OUT_CAP = 25
# A triage pattern that retires more entries than this was not read entry by entry.
TRIAGE_CAP = 40
# A document more than this share of whose real requirements are retired, however the statuses
# were set (patterns, mark, a scripted loop of marks), needs a reviewed record in
# conformance/policy.yaml.
TRIAGE_DOC_SHARE = 0.25
# Noise leaves that share, so without this a whole document could be marked noise and pass. It
# is not 25%: noise runs to 40% of a document, and that is not worth an approval each.
NOISE_DOC_SHARE = 0.5
TRIAGE_DOC_FLOOR = 10  # a short document may still retire a few entries without a record
# A pattern needs this many literal words of four or more letters: `.` retires nothing.
TRIAGE_MIN_WORDS = 2
# A scope yielding fewer entries than this per page is probably misread (front matter, a
# table the extractor cannot see); the scope says `sparse` with a reason when that is right.
MIN_YIELD_PER_PAGE = 0.25
MAX_LISTED = 8
TIER_1 = 1
# Bulk triage is refused here even without a tier: the instruction the fork follows.
NO_BULK_TRIAGE = frozenset({register.REFERENCE_LIST_DOCUMENT})
_LITERAL_WORD = re.compile(r"[A-Za-z]{4,}")


def _err(rule: str, message: str, path: str | None = None) -> Finding:
    return Finding(rule, "E", message, path)


def _listed(items: list[str]) -> str:
    more = f" and {len(items) - MAX_LISTED} more" if len(items) > MAX_LISTED else ""
    return ", ".join(items[:MAX_LISTED]) + more


def _tier(index: Mapping[str, Any], ref: str) -> int | None:
    return index[ref].get("tier") if ref in index else None


# --- FW-REQ-001 --------------------------------------------------------------------------


def _coverage_problems(ref: str, source: Mapping[str, Any], text: str) -> list[str]:
    """Every page in exactly one scope or exclusion."""
    last = extract.page_count(text)
    owners: defaultdict[int, list[str]] = defaultdict(list)
    for label, ranges in (("scope", source.get("scopes", [])),
                          ("exclusion", source.get("excluded", []))):
        for r in ranges:
            first, end = r["pages"]
            if first > end or end > last:
                return [f"{ref}: {label} pages {first}-{end} are not within 1-{last}"]
            for page in range(first, end + 1):
                owners[page].append(f"{label} {first}-{end}")
    problems = []
    uncovered = [p for p in range(1, last + 1) if p not in owners]
    if uncovered:
        problems.append(f"{ref}: pages {_pages(uncovered)} are in no scope and no exclusion; "
                        "read them or exclude them with a reason")
    doubled = sorted(p for p, who in owners.items() if len(who) > 1)
    if doubled:
        problems.append(f"{ref}: pages {_pages(doubled)} are in more than one range")
    return problems


def _footer_problems(ref: str, source: Mapping[str, Any], text: str) -> list[str]:
    """A declared footer pattern that cannot work would leave the join it was added to fix."""
    out = []
    found = [b.text for b in extract.blocks(text, **register.block_options(source))
             if b.kind == "footer"]
    for key, name, where in (("footers", "footer", "page-closing"),
                             ("headers", "header", "page-opening")):
        for footer in source.get(key, []):
            pattern = footer["pattern"]
            if not extract.is_regex(pattern):
                out.append(f"{ref}: {name} pattern {pattern!r} is not a regex")
                continue
            hits = [line for line in found if re.search(pattern, line)]
            if not hits:
                out.append(f"{ref}: {name} pattern {pattern!r} matches no {where} paragraph")
            if any(extract.MODAL.search(line) or extract.SHOULD.search(line) for line in hits):
                out.append(f"{ref}: {name} pattern {pattern!r} matches a paragraph that states "
                           f"a duty; a {name} never does")
    return out


def _pages(pages: list[int]) -> str:
    runs: list[list[int]] = []
    for page in pages:
        if runs and page == runs[-1][-1] + 1:
            runs[-1].append(page)
        else:
            runs.append([page])
    return ", ".join(f"{r[0]}-{r[-1]}" if len(r) > 1 else str(r[0]) for r in runs[:6]) + (
        " and more" if len(runs) > 6 else "")


def _source_problems(reg: Register, index: Mapping[str, Any], repo: Path) -> list[Finding]:
    out = []
    wanted = {i for i, e in index.items() if e["kind"] in register.SOURCE_KINDS}
    missing = sorted(wanted - set(reg.sources))
    if missing:
        out.append(_err("FW-REQ-001", f"reference(s) with no source entry: {_listed(missing)}",
                        register.SOURCES))
    unknown = sorted(set(reg.sources) - wanted)
    if unknown:
        out.append(_err("FW-REQ-001", f"source entries for unknown references: "
                        f"{_listed(unknown)}", register.SOURCES))
    for ref in sorted(set(reg.files) - set(reg.sources)):
        out.append(_err("FW-REQ-001", f"{ref}: requirements file for a reference with no source "
                        "entry; a dropped reference leaves with its index entry, source entry, "
                        "requirements file and text hash together",
                        register.requirements_path(ref)))
    for ref in sorted(set(reg.text_hashes) - wanted):
        out.append(_err("FW-REQ-001", f"{ref}: text hash for a reference that is not in the "
                        "index; drop it with the reference", register.TEXT_HASHES))
    for ref in sorted(set(reg.sources) & wanted):
        source, entry = reg.sources[ref], index[ref]
        if source["mode"] == "excluded":
            if entry["kind"] == "pdf":
                out.append(_err("FW-REQ-001", f"{ref} is a PDF; it cannot be mode: excluded",
                                register.SOURCES))
            if ref in reg.files:
                out.append(_err("FW-REQ-001", f"{ref} is excluded and has no requirement "
                                "entries", register.requirements_path(ref)))
            continue
        if entry["status"] != "ok":
            if ref in reg.files:
                out.append(_err("FW-REQ-001", f"{ref} is {entry['status']}, so it is "
                                "unassessed and has no requirement entries",
                                register.requirements_path(ref)))
            continue
        if not source.get("scopes"):
            out.append(_err("FW-REQ-001", f"{ref} is imported; declare its scopes",
                            register.SOURCES))
            continue
        try:
            text = register.text_of(repo, entry)
        except OSError as exc:
            out.append(_err("FW-REQ-001", f"{ref}: cannot read its text: {exc.strerror or exc}",
                            entry["text"]["path"]))
            continue
        out += [_err("FW-REQ-001", m, register.SOURCES)
                for m in _coverage_problems(ref, source, text)
                + _footer_problems(ref, source, text)]
    for item in reg.reference_list:
        if item.get("ref") and item["ref"] not in reg.sources:
            out.append(_err("FW-REQ-001", f"reference list: {item['document']} names unknown "
                            f"source {item['ref']}", register.SOURCES))
    return out


def _entry_problems(reg: Register, resolver: Resolver, repo: Path,
                    index: Mapping[str, Any]) -> list[Finding]:
    out = []
    for ref, doc in sorted(reg.files.items()):
        path = register.requirements_path(ref)
        if doc["ref"] != ref:
            out.append(_err("FW-REQ-001", f"file names {ref} but holds {doc['ref']}", path))
            continue
        passages: dict[int, str] | None = {}
        if ref in index and index[ref].get("text") and doc["requirements"]:
            try:
                options = register.block_options(reg.sources.get(ref, {}))
                text = register.text_of(repo, index[ref])
                passages = extract.passages(extract.blocks(text, **options))
            except OSError:
                passages = None  # reported once by _source_problems
        counts = Counter(e["id"] for e in doc["requirements"])
        prefix = f"REQ-{ref}-"
        for entry in doc["requirements"]:
            ident = entry["id"]
            if counts[ident] > 1:
                out.append(_err("FW-REQ-001", f"{ident}: duplicate ID", path))
            if not ident.startswith(prefix):
                out.append(_err("FW-REQ-001", f"{ident}: ID must start with {prefix}", path))
            if entry["citation"]["ref"] != ref:
                out.append(_err("FW-REQ-001", f"{ident}: cites {entry['citation']['ref']}", path))
            work_item = entry.get("work_item")
            if work_item is not None and work_item not in reg.work_items:
                out.append(_err("FW-REQ-001", f"{ident}: unknown work item {work_item}", path))
            if entry.get("removed") or passages is None:
                continue
            result = resolver.resolve(entry["citation"])
            if result.status == ERROR:
                out.append(_err("FW-REQ-001", f"{ident}: {describe(entry['citation'])}: "
                                f"{result.message}", path))
                continue
            page = entry["citation"]["page"]
            if compact(entry["statement"]) not in passages.get(page, ""):
                out.append(_err("FW-REQ-001", f"{ident}: the statement is not in the passage on "
                                f"page {page}", path))
    return out


def shape(reg: Register, resolver: Resolver, repo: Path,
          index: Mapping[str, Any]) -> list[Finding]:
    """FW-REQ-001: register shape, IDs, sources with every page dispositioned, citations and
    statements in their passages."""
    out = [_err("FW-REQ-001", message, path) for path, message in reg.problems]
    if not reg.sources:
        return out
    return out + _source_problems(reg, index, repo) + _entry_problems(reg, resolver, repo, index)


# --- FW-REQ-002 --------------------------------------------------------------------------

FREEZE_CANDIDATE = "candidate"
FREEZE_NO_STRONG = "partial with no strong item"


def blocks_freeze(probe: evidence.Probe | None, entry: Mapping[str, Any],
                  tier: int | None) -> str | None:
    """FW-REQ-002 at p13 (ADR-0005, 2026-11-08): what keeps an entry from the freeze, or None.
    Only tier 1 blocks: a candidate, or a partial no evidence item of which judges strong.
    A partial whose every marked sentence the user ruled out has nothing left to prove, as
    FW-REQ-003 reads it, so it passes; so does a partial carrying ``freeze_debt``, the debt the
    user let pass the freeze (the user's Nov 9 decision), whose shape FW-REQ-004 checks. Without
    a probe the second cannot be judged, so only a candidate is named."""
    if tier != TIER_1:
        return None
    if entry["status"] == "candidate":
        return FREEZE_CANDIDATE
    if entry["status"] == "partial" and probe is not None and needs_item(entry) \
            and not entry.get("freeze_debt") and not any(
            evidence.judge(probe, item, entry).strength == evidence.STRONG
            for item in entry.get("evidence") or ()):
        return FREEZE_NO_STRONG
    return None


def freeze(reg: Register, index: Mapping[str, Any], probe: evidence.Probe) -> list[Finding]:
    """FW-REQ-002: the freeze fails on a tier 1 candidate and on a tier 1 partial with no strong
    item. Open work items are the backlog and do not block; a candidate outside tier 1 warns,
    once per document."""
    out = []
    advisory: Counter[str] = Counter()
    for ref, entry in reg.live():
        path = register.requirements_path(ref)
        tier = _tier(index, ref)
        blocker = blocks_freeze(probe, entry, tier)
        if blocker == FREEZE_CANDIDATE:
            out.append(_err("FW-REQ-002", f"{entry['id']}: a tier 1 entry is still a candidate; "
                            "triage it before the freeze", path))
        elif blocker == FREEZE_NO_STRONG:
            out.append(_err("FW-REQ-002", f"{entry['id']}: a tier 1 partial with no strong "
                            "evidence item; give it one that fails when part of its duty is "
                            "broken", path))
        elif tier != TIER_1 and entry["status"] == "candidate":
            advisory[ref] += 1
    for ref, count in sorted(advisory.items()):
        out.append(Finding("FW-REQ-002", "W", f"{ref}: {count} candidate(s) outside tier 1, "
                           "advisory at the freeze", register.requirements_path(ref)))
    return out


# --- FW-REQ-003 --------------------------------------------------------------------------


def _fan_out_limit(reg: Register, kind: str, target: str) -> int:
    for exception in reg.fan_out_exceptions:
        if exception["kind"] == kind and exception["target"] == target \
                and exception.get("approved_by") == "user":
            return exception["limit"]
    return FAN_OUT_CAP


# Which evidence kinds a reverse link of each origin can be cited by.
_LINK_KINDS = {"rule": ("rule",), "schema": ("schema",), "entity": ("pinned", "template")}


def uncited_sentences(entry: Mapping[str, Any], strong: list[Mapping[str, Any]]) -> list[str]:
    """The marked sentences of an entry with more than one, of any kind (a lettered item can
    run to several sentences), that no strong evidence item of its own cites by ``sentence``.
    One obligation of a paragraph proven says nothing about the rest, and one item cites one
    sentence."""
    marked = extract.marked_sentences(entry["statement"])
    if len(marked) < 2:
        return []
    unused = list(strong)
    uncited = []
    for sentence in (s for s in marked if not evidence.ruled_out(entry, s)):
        item = next((i for i in unused if evidence.cites(i, sentence)), None)
        if item is None:
            uncited.append(sentence)
        else:
            unused.remove(item)
    return uncited


def unresolved_sentences(probe: evidence.Probe, entry: Mapping[str, Any]) -> list[str]:
    """The sentences of a partial entry that no strong item holds and no ruling is sought on.
    Computed, never stored: a stored list would drift from the evidence."""
    if entry["status"] != "partial":
        return []
    items = entry.get("evidence") or ()
    strong = [i for i in items if evidence.judge(probe, i, entry).strength == evidence.STRONG]
    sentences = [s for s in evidence.citable(entry["statement"])
                 if evidence.sought(entry, s) is None]
    if len(evidence.citable(entry["statement"])) == 1:
        return [] if strong else sentences
    return [s for s in sentences if not any(evidence.cites(i, s) for i in strong)]


def needs_item(entry: Mapping[str, Any]) -> bool:
    """Whether a sentence of the entry still needs evidence once the user's rulings are read."""
    return not all(evidence.ruled_out(entry, s) for s in evidence.citable(entry["statement"]))


def ruling_problems(entry: Mapping[str, Any], path: str) -> list[Finding]:
    """A ruling is sought on a whole marked sentence, as evidence is, and while it is pending
    the entry cannot be covered: only the user takes a sentence out of what must be proved."""
    out = []
    marked = evidence.citable(entry["statement"])
    for record in entry.get("ruling_sought") or ():
        if not any(evidence.cites(record, s) for s in marked):
            out.append(_err("FW-REQ-003", f"{entry['id']}: ruling_sought "
                            f"{record['sentence'][:40]!r}... is not a whole marked sentence of the "
                            "statement", path))
    if entry["status"] == "covered" and not needs_item(entry):
        out.append(_err("FW-REQ-003", f"{entry['id']}: covered with every marked sentence ruled "
                        "out; such an entry is not-a-requirement", path))
    if entry["status"] == "covered" and evidence.pending_rulings(entry):
        out.append(_err("FW-REQ-003", f"{entry['id']}: covered with a ruling pending; only "
                        "approved_by: user takes a sentence out of what must be proved; use "
                        "partial", path))
    return out


def _shared_fixtures(entry: Mapping[str, Any], strong: list[Mapping[str, Any]]) -> list[str]:
    """One clause per fixture: two strong items on different sentences may share a fixture only
    with two distinct messages."""
    seen: dict[tuple[str, str], Any] = {}
    shared = []
    for item in strong:
        if item["kind"] != "rule":
            continue
        key = (item["fixture"], item["expect"])
        if seen.setdefault(key, item.get("sentence")) != item.get("sentence"):
            shared.append(item["fixture"])
    return shared


def ladder(reg: Register, probe: evidence.Probe) -> list[Finding]:
    """FW-REQ-003: every evidence entry resolves and is linked both ways, ``covered`` has
    strong evidence on every marked sentence, and no target carries more requirements than
    its cap."""
    out = []
    cited: Counter[tuple[str, str]] = Counter()
    claimed: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for ref, entry in reg.live():
        path = register.requirements_path(ref)
        items = entry.get("evidence") or []
        out += ruling_problems(entry, path)
        verdicts = [evidence.judge(probe, item, entry) for item in items]
        cited.update((item["kind"], item["target"]) for item in items)
        for item in items:
            claimed[(item["kind"], item["target"])].add(entry["id"])
        for verdict in verdicts:
            if verdict.strength in (evidence.DENIED, evidence.UNRESOLVED):
                out.append(_err("FW-REQ-003", f"{entry['id']}: evidence {verdict.strength}: "
                                f"{verdict.message}", path))
        strong = [i for i, v in zip(items, verdicts, strict=True)
                  if v.strength == evidence.STRONG]
        for fixture in _shared_fixtures(entry, strong):
            out.append(_err("FW-REQ-003", f"{entry['id']}: {fixture} backs two sentences with one "
                            "message; one fixture proves one clause", path))
        if entry["status"] == "covered" and not strong:
            why = "; ".join(v.message for v in verdicts) or "no evidence"
            out.append(_err("FW-REQ-003", f"{entry['id']}: covered needs a rule with a negative "
                            "fixture and a declared message, a constraint on a required schema "
                            f"field, or a required template heading ({why}); use partial", path))
        elif entry["status"] == "covered" and (uncited := uncited_sentences(entry, strong)):
            out.append(_err("FW-REQ-003", f"{entry['id']}: covered, but {len(uncited)} of its "
                            f"{len(extract.marked_sentences(entry['statement']))} marked "
                            "sentences are cited by no strong evidence (evidence[].sentence): "
                            f"{_listed([s[:60] for s in uncited])}; use partial", path))
    live_ids = {e["id"] for _, e in reg.live()}
    for origin, target, ident in evidence.reverse_links(probe):
        if ident not in live_ids:
            out.append(_err("FW-REQ-003", f"{target} enforces {ident}, which is not a live "
                            "register entry"))
        elif not any(ident in claimed[(kind, target)] for kind in _LINK_KINDS[origin]):
            out.append(_err("FW-REQ-003", f"{target} enforces {ident}, but that entry does "
                            f"not cite {target} as evidence"))
    for exception in reg.fan_out_exceptions:
        if exception.get("approved_by") != "user":
            out.append(_err("FW-REQ-003", f"fan-out exception for {exception['kind']} "
                            f"{exception['target']} needs approved_by: user", register.POLICY))
    for (kind, target), count in sorted(cited.items()):
        limit = _fan_out_limit(reg, kind, target)
        if count > limit:
            out.append(_err("FW-REQ-003", f"{kind} {target} is evidence for {count} requirements, "
                            f"over its limit of {limit}; split the claims or record a reviewed "
                            f"exception in {register.POLICY}"))
    return out


# --- FW-REQ-004 --------------------------------------------------------------------------


def _pattern_problems(reg: Register, index: Mapping[str, Any]) -> list[Finding]:
    out = []
    regexes: dict[tuple[str | None, str | None], str] = {}
    for pattern in reg.patterns:
        ident, ref = pattern["id"], pattern["ref"]
        where = f"{ident} ({ref})"
        if _tier(index, ref) == TIER_1 or ref in NO_BULK_TRIAGE:
            out.append(_err("FW-REQ-004", f"{where}: bulk not-applicable is refused on a tier 1 "
                            "document; review each entry", register.TRIAGE))
        key = (pattern.get("statement"), pattern.get("context"))
        if key in regexes:
            out.append(_err("FW-REQ-004", f"{where}: the same regexes as {regexes[key]}; one "
                            "pattern per reading, not one per page range", register.TRIAGE))
        regexes.setdefault(key, ident)
        for key in ("statement", "context"):
            regex = pattern.get(key)
            if regex is None:
                continue
            try:
                re.compile(regex)
            except re.error as exc:
                out.append(_err("FW-REQ-004", f"{where}: {key} is not a regex: {exc}",
                                register.TRIAGE))
                continue
            if len(_LITERAL_WORD.findall(regex)) < TRIAGE_MIN_WORDS:
                out.append(_err("FW-REQ-004", f"{where}: {key} regex {regex!r} needs at least "
                                f"{TRIAGE_MIN_WORDS} literal words of four letters",
                                register.TRIAGE))
        matched = [e["id"] for r, e in reg.live() if e.get("triaged_by") == ident]
        if len(matched) > TRIAGE_CAP:
            out.append(_err("FW-REQ-004", f"{where}: retires {len(matched)} entries, over the cap "
                            f"of {TRIAGE_CAP}; narrow it or review the entries one by one",
                            register.TRIAGE))
        for sample in pattern["sample"]:
            entry = reg.entry(sample)
            if entry is None or entry.get("removed"):
                out.append(_err("FW-REQ-004", f"{where}: sample {sample} is not a live entry",
                                register.TRIAGE))
            elif not register._matches(pattern, ref, entry):
                out.append(_err("FW-REQ-004", f"{where}: sample {sample} does not match the "
                                "pattern", register.TRIAGE))
    return out


def retired(entry: Mapping[str, Any]) -> bool:
    """An entry set aside without proof: not-applicable, deferred, or partial on evidence that
    cannot fail. `mark --status deferred --reason x` on a tier 2 document, or partial on one
    citation, retires an entry as surely as not-applicable does."""
    return entry["status"] in ("not-applicable", "deferred") or (
        entry["status"] == "partial"
        and all(e["kind"] in ("citation", "prose") for e in entry.get("evidence") or []))


def retired_share(doc: Mapping[str, Any]) -> tuple[int, int]:
    """(retired, real) requirements of a document, however the statuses were set: by pattern,
    by `rmf conformance mark`, or by a scripted loop of marks. Extraction noise is neither: a
    heading marked not-a-requirement retires nothing, and it would otherwise trip the share
    on nearly every document."""
    real = [e for e in doc["requirements"]
            if not e.get("removed") and e["status"] != register.NOT_A_REQUIREMENT]
    return sum(1 for e in real if retired(e)), len(real)


def noise_share(doc: Mapping[str, Any]) -> tuple[int, int]:
    """(noise, live) entries of a document: the entries retired_share leaves out."""
    live = [e for e in doc["requirements"] if not e.get("removed")]
    return sum(1 for e in live if e["status"] == register.NOT_A_REQUIREMENT), len(live)


RETIRED = "not-applicable, deferred, or partial on evidence that cannot fail"


def freeze_debt_problems(entry: Mapping[str, Any], tier: int | None) -> list[str]:
    """FW-REQ-004 on ``freeze_debt`` (ADR-0005, 2026-11-08, the user's Nov 9 decision): it lets
    a tier 1 partial pass the freeze as named debt, so it sits only on a tier 1 partial bound to
    the work item that keeps the debt on the backlog. Group B is a duty held by a presence-only
    item on a required field, so it needs an item that reads the run (not prose or a citation);
    group C is a duty no run record can fail yet, and rests on what builds it."""
    out = []
    if tier != TIER_1 or entry["status"] != "partial":
        out.append(f"freeze_debt passes only a tier 1 partial at the freeze, not a "
                   f"{entry['status']} entry of a tier {tier} document")
    if not entry.get("work_item"):
        out.append("freeze_debt needs the work_item that keeps the debt on the backlog")
    if entry["freeze_debt"].get("group") == "B" and all(
            item["kind"] in ("citation", "prose") for item in entry.get("evidence") or ()):
        out.append("freeze_debt group B is a presence-only item on a required field; with only "
                   "prose or citation evidence it is group C")
    return out


def _record_problems(reg: Register, name: str, records: list[dict[str, Any]],
                     over: Callable[[str, Mapping[str, Any]], str | None]) -> list[Finding]:
    """A document ``over`` a limit needs a per-document record in conformance/policy.yaml with
    approved_by user; a record no document needs is stale. ``over`` says why, or None."""
    out = []
    approved = {r["ref"]: r for r in records if r.get("approved_by") == "user"}
    for ref, doc in sorted(reg.files.items()):
        message = over(ref, doc)
        if message and ref not in approved:
            out.append(_err("FW-REQ-004", message, register.POLICY))
        elif not message and ref in approved:
            out.append(_err("FW-REQ-004", f"{ref}: {name} record is not needed; drop it",
                            register.POLICY))
    for record in records:
        if record.get("approved_by") != "user":
            out.append(_err("FW-REQ-004", f"{name} record for {record['ref']} needs "
                            "approved_by: user", register.POLICY))
        if record["ref"] not in reg.files:
            out.append(_err("FW-REQ-004", f"{name} record for unknown document "
                            f"{record['ref']}", register.POLICY))
    return out


def _over_retired(ref: str, doc: Mapping[str, Any]) -> str | None:
    count, real = retired_share(doc)
    noise, live = noise_share(doc)
    half = max(TRIAGE_DOC_FLOOR, int(live * NOISE_DOC_SHARE))
    if count > max(TRIAGE_DOC_FLOOR, int(real * TRIAGE_DOC_SHARE)):
        return (f"{ref}: {count} of {real} requirements are retired ({RETIRED}; "
                f"{count / real:.0%}), over {TRIAGE_DOC_SHARE:.0%} of the document; retiring "
                f"that much of a document needs a retirements record with approved_by user in "
                f"{register.POLICY}")
    # Each noise mark shrinks the base above, so the two limits are read together too.
    if count and noise <= half < noise + count:
        return (f"{ref}: {noise} noise and {count} retired entries set aside "
                f"{(noise + count) / live:.0%} of {live} live entries, over "
                f"{NOISE_DOC_SHARE:.0%} of the document; that needs a retirements record with "
                f"approved_by user in {register.POLICY}")
    return None


def _over_noise(ref: str, doc: Mapping[str, Any]) -> str | None:
    count, live = noise_share(doc)
    if count <= max(TRIAGE_DOC_FLOOR, int(live * NOISE_DOC_SHARE)):
        return None
    return (f"{ref}: {count} of {live} live entries are {register.NOT_A_REQUIREMENT} "
            f"({count / live:.0%}), over {NOISE_DOC_SHARE:.0%} of the document; that much noise "
            f"needs a noise record with approved_by user in {register.POLICY}")


def _duty_words(text: str) -> set[str]:
    """The extractor's own obligation and recommendation phrases in ``text``, case-folded."""
    return {m.group(0).casefold() for rx in (extract.MODAL, extract.SHOULD)
            for m in rx.finditer(text)}


def unresolved_at_close(probe: evidence.Probe, entry: Mapping[str, Any]) -> bool:
    """A bound entry a closed work item cannot rest on: nothing was decided (candidate), the
    decision was to not decide (deferred, not-applicable), or it is covered or partial with
    no evidence that judges strong (evidence.judge): a citation, prose, a rule that does not
    list the entry, or a rule without a negative fixture cannot fail when the requirement is
    broken."""
    if entry["status"] in ("candidate", "deferred", "not-applicable",
                           register.NOT_A_REQUIREMENT):
        return True
    return not any(evidence.judge(probe, item, entry).strength == evidence.STRONG
                   for item in entry.get("evidence") or [])


def _closure_problems(ident: str, item: Mapping[str, Any], bound: list[Mapping[str, Any]],
                      probe: evidence.Probe, index: Mapping[str, Any]) -> list[Finding]:
    """``closed``: every bound entry covered. ``closed-partial``: built, the rest honestly
    partial, none of those in a tier 1 document."""
    status = item["status"]
    if waiting := [e["id"] for e in bound if evidence.pending_rulings(e)]:
        return [_err("FW-REQ-004", f"{ident} is {status}, but a ruling is pending on "
                     f"{_listed(waiting)}; it stays open", register.WORK_ITEMS)]
    if status == "closed":
        unresolved = [e["id"] for e in bound
                      if e["status"] != "covered" or unresolved_at_close(probe, e)]
        return [_err("FW-REQ-004", f"{ident} is closed, but bound entries are not covered on "
                     f"evidence that judges strong: {_listed(unresolved)}; closed-partial or "
                     "open", register.WORK_ITEMS)] if unresolved else []
    undecided = [e["id"] for e in bound if e["status"] not in ("covered", "partial")]
    partial = [e for e in bound if e["status"] == "partial"]
    tier_1 = [e["id"] for e in partial if _tier(index, e["citation"]["ref"]) == TIER_1]
    out = []
    if undecided:
        out.append(_err("FW-REQ-004", f"{ident} is closed-partial, but bound entries are neither "
                        f"covered nor partial: {_listed(undecided)}", register.WORK_ITEMS))
    if tier_1:
        out.append(_err("FW-REQ-004", f"{ident} is closed-partial with tier 1 entries partial: "
                        f"{_listed(tier_1)}; it stays open", register.WORK_ITEMS))
    if not partial and not undecided:
        out.append(_err("FW-REQ-004", f"{ident} is closed-partial with every entry covered; use "
                        "closed", register.WORK_ITEMS))
    return out


def _work_item_problems(reg: Register, probe: evidence.Probe,
                        index: Mapping[str, Any]) -> list[Finding]:
    out = []
    for ident, item in sorted(reg.work_items.items()):
        if item.get("scope", "register") != "register":
            continue
        bound = reg.bound(ident)
        if not bound and not reg.waived(ident):
            out.append(_err("FW-REQ-004", f"{ident} ({item['status']}) binds no register entry "
                            "and no FW-TASK-002 waiver; set work_item on the entries it closes, "
                            "or scope: internal with the reason", register.WORK_ITEMS))
            continue
        if item["status"] == "open":
            if bound and all(e["status"] == "covered" for e in bound):
                out.append(_err("FW-REQ-004", f"{ident} is open with every bound entry covered; "
                                "close it", register.WORK_ITEMS))
            continue
        out += _closure_problems(ident, item, bound, probe, index)
    return out


def binding_problems(reg: Register, *, applied: bool = True) -> list[Finding]:
    """Each binding in conformance/bindings.yaml names exactly one live entry, no entry is
    named by two work items, and (``applied``) the entry carries the binding's work item,
    which rmf conformance bind writes."""
    out = []
    named: dict[str, str] = {}
    for binding in reg.bindings:
        hits = register.binding_hits(reg, binding)
        where = f"{binding['work_item']} {binding['ref']} {binding['phrase'][:50]!r}"
        if binding["work_item"] not in reg.work_items:
            out.append(_err("FW-REQ-004", f"binding {where}: unknown work item",
                            register.BINDINGS))
        if len(hits) != 1:
            out.append(_err("FW-REQ-004", f"binding {where} matches {len(hits)} live entries, "
                            "not one; narrow or widen the phrase", register.BINDINGS))
            continue
        entry = hits[0]
        other = named.setdefault(entry["id"], binding["work_item"])
        if other != binding["work_item"]:
            out.append(_err("FW-REQ-004", f"binding {where}: {entry['id']} is already bound to "
                            f"{other}; an entry carries one work item", register.BINDINGS))
        elif applied and entry.get("work_item") != binding["work_item"]:
            out.append(_err("FW-REQ-004", f"binding {where}: {entry['id']} carries work item "
                            f"{entry.get('work_item')}; run rmf conformance bind",
                            register.BINDINGS))
    return out


def reasons(reg: Register, index: Mapping[str, Any], probe: evidence.Probe) -> list[Finding]:
    """FW-REQ-004: ``reason`` where required, approval of tier 1 deferrals, closure that can
    be inspected: removal reasons, bounded triage patterns, a reviewed record behind a mostly
    retired document, work items that bind entries and close on strong evidence."""
    out = []
    for ref, entry in reg.entries():
        path = register.requirements_path(ref)
        status, ident = entry["status"], entry["id"]
        if entry.get("removed"):
            if status in register.REVIEWED_STATUSES and not entry.get("removal_reason"):
                out.append(_err("FW-REQ-004", f"{ident}: a {status} entry left its source; "
                                "record removal_reason or restore the text", path))
            continue
        if status in ("partial", "deferred", "not-applicable",
                      register.NOT_A_REQUIREMENT) and not entry.get("reason"):
            out.append(_err("FW-REQ-004", f"{ident}: {status} needs a reason", path))
        elif status == register.NOT_A_REQUIREMENT:
            words = _duty_words(entry["statement"])
            if words and not words & _duty_words(entry["reason"]):
                out.append(_err("FW-REQ-004", f"{ident}: the statement says "
                                f"{', '.join(sorted(words))}; a not-a-requirement reason must "
                                "use that word and say why it binds no one", path))
        if status == "partial" and not entry.get("evidence"):
            out.append(_err("FW-REQ-004", f"{ident}: partial needs at least one evidence item "
                            "(a citation or prose at least); with none it is deferred or "
                            "not-applicable, say which", path))
        if status == "deferred" and _tier(index, ref) == TIER_1 and \
                entry.get("approved_by") != "user":
            out.append(_err("FW-REQ-004", f"{ident}: deferring a tier 1 document needs "
                            "approved_by: user", path))
        if entry.get("freeze_debt"):
            out += [_err("FW-REQ-004", f"{ident}: {problem}", path)
                    for problem in freeze_debt_problems(entry, _tier(index, ref))]
    return out + _pattern_problems(reg, index) \
        + _record_problems(reg, "retirements", reg.retirements, _over_retired) \
        + _record_problems(reg, "noise", reg.noise, _over_noise) \
        + _work_item_problems(reg, probe, index) + binding_problems(reg)


# --- FW-REQ-005 --------------------------------------------------------------------------


def _describe_drift(built: register.Built, current: Mapping[str, Any]) -> list[str]:
    changes = built.changes
    parts = []
    if changes.added:
        parts.append(f"{len(changes.added)} new")
    if changes.changed:
        parts.append(f"{len(changes.changed)} changed ({_listed(changes.changed)})")
    if changes.removed:
        parts.append(f"{len(changes.removed)} no longer in the source ({_listed(changes.removed)})")
    if built.document.get("ids") != current.get("ids"):
        parts.append("the ID set differs")
    return parts or ["fields differ"]


def _yield_problems(ref: str, built: register.Built) -> list[str]:
    out = []
    for scope, count in built.scope_yields:
        first, last = scope["pages"]
        floor = max(1, round((last - first + 1) * MIN_YIELD_PER_PAGE))
        if count < floor and not scope.get("sparse"):
            out.append(f"{ref}: scope {first}-{last} ({scope['note']}) yields {count} entries, "
                       f"under {floor}; check the pages or say why it is sparse")
    return out


def sync(repo: Path, reg: Register, index: Mapping[str, Any],
         only: str | None = None) -> list[Finding]:
    """FW-REQ-005: each source text is the one reviewed (hash), a fresh extraction equals the
    register, every scope yields, and no entry awaits review."""
    out = []
    for ref, source in sorted(reg.sources.items()):
        entry = index.get(ref)
        if entry is None or entry["status"] != "ok" or only not in (None, ref) \
                or source["mode"] == "excluded":
            continue
        path = register.requirements_path(ref)
        try:
            text = register.text_of(repo, entry)
        except OSError as exc:
            out.append(_err("FW-REQ-005", f"{ref}: cannot read its text: {exc.strerror or exc}",
                            path))
            continue
        digest = register.text_hash(text)
        if reg.text_hashes.get(ref) != digest:
            out.append(_err("FW-REQ-005", f"{ref}: the text differs from the reviewed one "
                            f"({'no hash recorded' if ref not in reg.text_hashes else 'hash'}); "
                            "read the change, re-review, then rmf conformance accept-text",
                            register.TEXT_HASHES))
        try:
            built = register.build(reg, source, text)
        except extract.SourceError as exc:
            out.append(_err("FW-REQ-005", f"{ref}: cannot extract: {exc}", path))
            continue
        current = reg.files.get(ref)
        if current is None:
            out.append(_err("FW-REQ-005", f"{ref}: no register file; run rmf conformance extract",
                            path))
        elif built.document != current:
            out.append(_err("FW-REQ-005", f"{ref}: differs from a fresh extraction: "
                            f"{'; '.join(_describe_drift(built, current))}; run rmf "
                            "conformance extract", path))
        out += [_err("FW-REQ-005", m, register.SOURCES) for m in _yield_problems(ref, built)]
        flagged = [e["id"] for e in (current or {}).get("requirements", [])
                   if e.get("needs_review")]
        if flagged:
            out.append(_err("FW-REQ-005", f"{ref}: re-review entries whose statement or pairing "
                            f"changed, then clear needs_review: {_listed(flagged)}", path))
    if only in (None, nist_pin.REF):
        out += _pin_sync(repo)
    if only in (None, register.REFERENCE_LIST_DOCUMENT):
        out += _reference_list_sync(repo, reg, index)
    return out


def _pin_sync(repo: Path) -> list[Finding]:
    problems: list[tuple[str, str]] = []
    current = register.read(repo, register.NIST_TASKS, "nist-tasks", problems)
    out = [_err("FW-REQ-005", m, p) for p, m in problems]
    try:
        fresh = register.pin_document(repo)
    except (OSError, nist_pin.PinError) as exc:
        return [*out, _err("FW-REQ-005", str(exc), register.NIST_TASKS)]
    if current is not None and current != fresh:
        out.append(_err("FW-REQ-005", f"{register.NIST_TASKS} differs from a fresh parse of "
                        f"{nist_pin.TEXT_PATH}; run rmf conformance extract", register.NIST_TASKS))
    return out


def _reference_list_sync(repo: Path, reg: Register, index: Mapping[str, Any]) -> list[Finding]:
    entry = index.get(register.REFERENCE_LIST_DOCUMENT)
    if entry is None or entry["status"] != "ok":
        return []
    try:
        printed = register.reference_list_keys(register.text_of(repo, entry))
    except OSError:
        return []  # reported by the hash and shape checks
    declared = [item["document"] for item in reg.reference_list]
    if printed == declared:
        return []
    absent = [d for d in printed if d not in declared]
    extra = [d for d in declared if d not in printed]
    return [_err("FW-REQ-005", f"reference list of {register.REFERENCE_LIST_DOCUMENT} differs: "
                 f"no disposition for {_listed(absent) or 'none'}; not printed: "
                 f"{_listed(extra) or 'none'}", register.SOURCES)]


# --- FW-TASK-002 -------------------------------------------------------------------------


@dataclass(frozen=True)
class Gap:
    task: str
    field: str
    entity: str  # alternatives joined by "|"

    def render(self) -> str:
        return f"{self.task} {self.field}: lacks {self.entity}"


def normalize(phrase: str) -> str:
    return " ".join(phrase.split()).casefold()


def _has(task: Mapping[str, Any], field: str) -> set[str]:
    raci = task.get("raci") or {}
    accountable = raci.get("A")
    owners = {*(raci.get("R") or ()), *([accountable] if isinstance(accountable, str)
                                        else accountable or ())}
    if field == "inputs":
        return {*(task.get("inputs") or ()), *(task.get("consults") or ())}
    if field == "outputs":
        return set(task.get("outputs") or ())
    if field == "primary":
        return owners
    return owners | set(raci.get("C") or ()) | set(raci.get("I") or ())


def gaps(pin_tasks: Iterable[Mapping[str, Any]], vocabulary: Mapping[str, Mapping[str, Any]],
         tasks: Mapping[str, Mapping[str, Any]]) -> tuple[set[Gap], set[str]]:
    """Mapped entities each task lacks, and phrases the vocabulary does not know."""
    missing: set[Gap] = set()
    unmapped: set[str] = set()
    for pinned in pin_tasks:
        task = tasks.get(pinned["id"])
        if task is None:
            continue
        for field in nist_pin.FIELDS:
            have = _has(task, field)
            for phrase in pinned[field]:
                entry = vocabulary.get(normalize(phrase))
                if entry is None:
                    unmapped.add(normalize(phrase))
                elif "any_of" in entry:
                    if not have & set(entry["any_of"]):
                        missing.add(Gap(pinned["id"], field, "|".join(entry["any_of"])))
                else:
                    missing |= {Gap(pinned["id"], field, e) for e in entry.get("entities", [])
                                if e not in have}
    return missing, unmapped


def _sdlc_note(task: Any) -> str | None:
    wanted = {"ref": TASK_CITATION_REF, "section": f"TASK {task.id}"}
    for citation in task.data.get("citations") or []:
        if all(citation.get(k) == v for k, v in wanted.items()):
            return citation.get("note")
    return None


def _sdlc_problems(pin_tasks: Iterable[Mapping[str, Any]], fw: Framework) -> list[Finding]:
    tasks = fw.index("tasks")
    out = []
    for pinned in pin_tasks:
        task = tasks.get(pinned["id"])
        if task is None:
            continue
        note = _sdlc_note(task)
        declared = nist_pin.sdlc(note) if note else {}
        if declared != pinned.get("sdlc", {}):
            out.append(_err("FW-TASK-002", f"{task.id}: TASK citation note says SDLC {declared}; "
                            f"SP 800-37r2 says {pinned.get('sdlc', {})}", task.location.file))
    return out


def _entities(fw: Framework) -> set[str]:
    return {e.id for e in fw.entities}


def contract(repo: Path, fw: Framework, reg: Register) -> list[Finding]:
    """FW-TASK-002: each task carries the entities its Chapter 3 block maps to. A waiver names
    an open work item, or a rationale for an omission scoped to that task (an input the task
    itself produces, which FW-IO-001 forbids); a waiver nothing needs is an error, so the rule
    tightens as gaps close."""
    problems: list[tuple[str, str]] = []
    pin = register.read(repo, register.NIST_TASKS, "nist-tasks", problems)
    words = register.read(repo, register.NIST_VOCABULARY, "nist-vocabulary", problems)
    waived = register.read(repo, register.NIST_WAIVERS, "nist-waivers", problems)
    out = [_err("FW-TASK-002", m, p) for p, m in problems]
    if pin is None or words is None or waived is None:
        return out
    vocabulary = {normalize(p["phrase"]): p for p in words["phrases"]}
    tasks = {t.id: t.data for t in fw.of("tasks")}
    known = _entities(fw)
    planned = {p["id"]: p["work_item"] for p in words["planned"]}
    for ident in sorted(set(planned) & known):
        out.append(_err("FW-TASK-002", f"planned entity {ident} now exists; drop it from planned",
                        register.NIST_VOCABULARY))
    for ident, item in sorted(planned.items()):
        if item not in reg.work_items:
            out.append(_err("FW-TASK-002", f"planned {ident}: unknown work item {item}",
                            register.NIST_VOCABULARY))
    for entry in words["phrases"]:
        for ident in [*entry.get("entities", []), *entry.get("any_of", [])]:
            if ident not in known and ident not in planned:
                out.append(_err("FW-TASK-002", f"{entry['phrase']!r} maps to unknown entity "
                                f"{ident}", register.NIST_VOCABULARY))
    missing, unmapped = gaps(pin["tasks"], vocabulary, tasks)
    for phrase in sorted(unmapped):
        out.append(_err("FW-TASK-002", f"no vocabulary entry for {phrase!r}",
                        register.NIST_VOCABULARY))
    waivers: defaultdict[Gap, list[dict[str, Any]]] = defaultdict(list)
    for w in waived["waivers"]:
        waivers[Gap(w["task"], w["field"], w["entity"])].append(w)
    for gap in sorted(missing - set(waivers), key=lambda g: (g.task, g.field, g.entity)):
        out.append(_err("FW-TASK-002", gap.render(), fw.index("tasks")[gap.task].location.file))
    for gap in sorted(set(waivers) - missing, key=lambda g: (g.task, g.field, g.entity)):
        out.append(_err("FW-TASK-002", f"waiver no longer needed: {gap.render()}",
                        register.NIST_WAIVERS))
    for gap, items in sorted(waivers.items(), key=lambda kv: (kv[0].task, kv[0].field,
                                                              kv[0].entity)):
        if len(items) > 1:
            out.append(_err("FW-TASK-002", f"duplicate waiver: {gap.render()}",
                            register.NIST_WAIVERS))
        for w in items:
            item = w.get("work_item")
            if item is not None and reg.work_items.get(item, {}).get("status") != "open":
                out.append(_err("FW-TASK-002", f"waiver {gap.render()}: {item} is not an open "
                                "work item", register.NIST_WAIVERS))
    return out + _sdlc_problems(pin["tasks"], fw)
