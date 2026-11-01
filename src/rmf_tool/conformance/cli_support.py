"""The `rmf conformance` commands, apart from their argument parsing."""

from __future__ import annotations

import random
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rmf_tool import refs
from rmf_tool.conformance import extract as extraction
from rmf_tool.conformance import nist_pin, register, report, rules
from rmf_tool.findings import Finding


class UsageError(Exception):
    """Unreadable conformance data or an unknown reference (exit code 2)."""


def _load(root: Path) -> tuple[register.Register, dict[str, Any]]:
    try:
        index = register.index_entries(root)
    except refs.IndexFileError as exc:
        raise UsageError(str(exc)) from exc
    reg = register.load(root)
    if reg.problems:
        path, message = reg.problems[0]
        raise UsageError(f"{path}: {message}")
    return reg, index


def _summary(ref: str, built: register.Built) -> str:
    changes = built.changes
    parts = [f"{ref}: {len(built.document['requirements'])}"]
    if "count" in built.document:
        parts[0] += f" ({built.document['count']} IDs)"
    parts += [f"{len(ids)} {label}" for label, ids in (
        ("new", changes.added), ("changed", changes.changed), ("removed", changes.removed),
        ("ambiguous", changes.ambiguous)) if ids]
    return ", ".join(parts)


def _extractable(reg: register.Register, index: dict[str, Any], only: str | None):
    for ref, source in sorted(reg.sources.items()):
        if only in (None, ref) and source["mode"] != "excluded":
            yield ref, source, index.get(ref)


def extract(root: Path, only: str | None, *, check: bool) -> tuple[list[str], list[Finding]]:
    reg, index = _load(root)
    if only is not None and only not in reg.sources:
        raise UsageError(f"unknown source {only!r}; see {register.SOURCES}")
    if check:
        findings = rules.sync(root, reg, index, only)
        return ([] if findings else ["conformance register is current"]), findings
    lines = []
    for ref, source, entry in _extractable(reg, index, only):
        if entry is None or entry["status"] != "ok":
            lines.append(f"{ref}: {entry['status'] if entry else 'not indexed'}, unassessed")
            continue
        try:
            built = register.build(reg, source, register.text_of(root, entry))
        except (OSError, extraction.SourceError) as exc:
            raise UsageError(f"{ref}: {exc}") from exc
        register.write_requirements(root, built.document)
        lines.append(_summary(ref, built))
        lines += [f"  {ident}: gone from the source; kept as removed, ID retired"
                  for ident in built.changes.removed]
        lines += [f"  {ident}: paired by position in a group that changed; marked needs_review"
                  for ident in built.changes.ambiguous]
        lines += [f"  {m}" for m in rules._yield_problems(ref, built)]
    if only in (None, nist_pin.REF):
        try:
            pin = register.pin_document(root)
        except (OSError, nist_pin.PinError) as exc:
            raise UsageError(str(exc)) from exc
        register.write_if_changed(root / register.NIST_TASKS, register.render_pin(pin))
        lines.append(f"{register.NIST_TASKS}: {len(pin['tasks'])} tasks")
    return lines, []


def accept_text(root: Path, only: str | None) -> list[str]:
    """Record the hash of each imported source text as reviewed."""
    reg, index = _load(root)
    if only is not None and only not in reg.sources:
        raise UsageError(f"unknown source {only!r}; see {register.SOURCES}")
    hashes = dict(reg.text_hashes)
    lines = []
    for ref, _, entry in _extractable(reg, index, only):
        if entry is None or entry["status"] != "ok":
            continue
        try:
            digest = register.text_hash(register.text_of(root, entry))
        except OSError as exc:
            raise UsageError(f"{ref}: {exc}") from exc
        if hashes.get(ref) != digest:
            lines.append(f"{ref}: {'updated' if ref in hashes else 'recorded'}")
            hashes[ref] = digest
    register.write_if_changed(root / register.TEXT_HASHES, register.render_text_hashes(hashes))
    return lines or ["every text hash is current"]


def mark(root: Path, ident: str, **fields: Any) -> str:
    """Set reviewed fields on one entry and rewrite its file."""
    return mark_many(root, {ident: fields})[0]


def mark_many(root: Path, marks: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Set reviewed fields on several entries, loading and writing the register once."""
    reg, _ = _load(root)
    touched = set()
    lines = []
    for ident, fields in marks.items():
        try:
            entry = register.mark(reg, ident, **fields)
        except register.MarkError as exc:
            raise UsageError(str(exc)) from exc
        touched.add(entry["citation"]["ref"])
        lines.append(f"{ident}: " + ", ".join(f"{k}={v!r}" for k, v in fields.items()))
    for ref in sorted(touched):
        document = reg.files[ref]
        document["requirements"] = [
            {k: e[k] for k in register._ORDER if k in e} for e in document["requirements"]]
        register.write_requirements(root, document)
    return lines


def promote(root: Path, ref: str, page: int, anchor: str, reason: str) -> str:
    """Promote a rejected paragraph, or a passage the extractor read as context, on one page
    of a document into a live candidate entry, and rewrite the file."""
    reg, index = _load(root)
    if ref not in reg.sources:
        raise UsageError(f"unknown source {ref!r}; see {register.SOURCES}")
    entry = index.get(ref)
    if entry is None or entry["status"] != "ok":
        raise UsageError(f"{ref} is {entry['status'] if entry else 'not indexed'}, unassessed")
    try:
        text = register.text_of(root, entry)
        made = register.promote(reg, ref, text, page, anchor, reason)
    except OSError as exc:
        raise UsageError(f"{ref}: {exc}") from exc
    except register.MarkError as exc:
        raise UsageError(str(exc)) from exc
    register.write_requirements(root, reg.files[ref])
    return f"{made['id']} p{page} [{made['kind']}] {made['locator'] or '-'}: {made['statement']}"


def page(root: Path, ref: str, number: int) -> list[str]:
    """Every live entry and every rejection on one page of a document, in file order: what a
    triage agent reads against the source page before promoting."""
    reg, _ = _load(root)
    doc = reg.files.get(ref)
    if doc is None:
        raise UsageError(f"no requirements file for {ref!r}; see {register.SOURCES}")
    entries = [e for e in doc["requirements"] if not e.get("removed")
               and e["citation"]["page"] == number]
    rejected = [r for r in doc.get("rejected", []) if r["page"] == number]
    lines = [f"{ref} page {number}: {len(entries)} entries, {len(rejected)} rejected"]
    lines += [f"{e['id']} [{e['kind']}] {e['status']} {e['locator'] or '-'}: {e['statement']}"
              for e in entries]
    lines += [f"rejected [{r['reason']}] {r['locator'] or '-'}: {r['text']}" for r in rejected]
    return lines


def report_data(root: Path) -> dict[str, Any]:
    reg, index = _load(root)
    return report.build(reg, index, waivers=report.waivers(root))


def bind(root: Path, *, check: bool) -> tuple[list[str], list[Finding]]:
    """Set work_item on the one live entry each binding names. A phrase that matches no
    entry or several is a finding, never a guess. ``check`` writes nothing."""
    reg, _ = _load(root)
    findings = rules.binding_problems(reg, applied=check)
    if check or findings:
        return ([] if findings else ["every binding names one entry that carries its work "
                                     "item"]), findings
    marks = register.binding_marks(reg)
    return mark_many(root, marks) or ["every binding is already applied"], []


SAMPLE_KINDS = {"prose": extraction.PROSE_KINDS, "lettered": ("lettered",), "table": ("table",),
                "promoted": (register.PROMOTED_KIND,),
                "all": (*extraction.KINDS, register.PROMOTED_KIND)}


def sample(root: Path, *, seed: int, count: int, rejected: bool, kind: str,
           only: str | None) -> list[str]:
    """A seeded sample of live entries, or of the rejected set, for a reviewer to read against
    the source. The population is the committed register in file order, so the same seed
    gives the same sample on the same register."""
    reg, _ = _load(root)
    if only is not None and only not in reg.sources:
        raise UsageError(f"unknown source {only!r}; see {register.SOURCES}")
    if kind not in SAMPLE_KINDS:
        raise UsageError(f"unknown kind {kind!r}; one of {', '.join(SAMPLE_KINDS)}")
    population: list[str] = []
    for ref, doc in sorted(reg.files.items()):
        if only not in (None, ref):
            continue
        if rejected:
            population += [f"{ref} p{r['page']} [{r['reason']}] {r['locator'] or '-'}: "
                           f"{r['text']}" for r in doc.get("rejected", [])]
        else:
            population += [f"{e['id']} p{e['citation']['page']} [{e['kind']}] "
                           f"{e['locator'] or '-'}: {e['statement']}"
                           for e in doc["requirements"]
                           if not e.get("removed") and e["kind"] in SAMPLE_KINDS[kind]]
    if not population:
        return ["nothing to sample"]
    chosen = random.Random(seed).sample(population, min(count, len(population)))
    return [f"population {len(population)}, seed {seed}, sample {len(chosen)}", *chosen]
