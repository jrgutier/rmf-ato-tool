"""`rmf conformance report`: where the register stands, per document and in total."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rmf_tool.conformance import evidence, register, rules
from rmf_tool.conformance.register import STATUSES, Register

# `partial` caps what evidence can prove, so a register resting on it must stay visible.
PARTIAL_WARNING_SHARE = 0.5
TIER_1 = 1


def freeze_split(reg: Register, index: Mapping[str, Any],
                 probe: evidence.Probe | None = None) -> dict[str, int]:
    """What FW-REQ-002 at p13 reads (ADR-0005, 2026-11-08): the tier 1 candidates and the tier 1
    partials with no strong item, which block the freeze (the second judged only with a probe);
    the candidates outside tier 1, which are advisory; and the entries set aside without proof
    (deferred, partial on evidence that cannot fail) that the sign-off at p13 reads, so a
    scripted loop of `mark --status deferred` is as visible as a loop of `not-applicable`
    (FW-REQ-004)."""
    out = {"tier_1": 0, "tier_1_partial_without_strong": 0, "advisory_elsewhere": 0,
           "deferred": 0, "partial_on_weak_evidence": 0}
    for ref, entry in reg.live():
        if entry["status"] == "deferred":
            out["deferred"] += 1
        elif entry["status"] == "partial" and rules.retired(entry):
            out["partial_on_weak_evidence"] += 1
        tier = (index.get(ref) or {}).get("tier")
        blocker = rules.blocks_freeze(probe, entry, tier)
        if blocker == rules.FREEZE_CANDIDATE:
            out["tier_1"] += 1
        elif blocker == rules.FREEZE_NO_STRONG:
            out["tier_1_partial_without_strong"] += 1
        elif entry["status"] == "candidate":
            out["advisory_elsewhere"] += 1
    return out


def evidence_state(reg: Register, index: Mapping[str, Any],
                   probe: evidence.Probe) -> dict[str, Any]:
    """What ``covered`` rests on and what ``partial`` still owes: covered entries that hold only
    under a precondition, each partial entry's sentences with no strong item, and the sentences
    that wait on the user's ruling. Tier 1 owes full proof, so its unresolved sentences are the
    debt the freeze reads; a sentence that can never fail is no debt, and waits apart. A tier 1
    partial whose every sentence a strong item holds still owes what its reason names: it is
    counted apart (``tier1_partial_by_reason``), since no sentence of it is unresolved."""
    unresolved = []
    awaiting = []
    conditional = debt = partial_1 = by_reason = 0
    for ref, entry in reg.live():
        if sentences := evidence.pending_rulings(entry):
            awaiting.append({"id": entry["id"], "tier": (index.get(ref) or {}).get("tier"),
                             "sentences": sentences})
        tier = (index.get(ref) or {}).get("tier")
        if entry["status"] == "covered":
            conditional += any(i.get("holds_when") for i in entry.get("evidence") or ())
            continue
        sentences = rules.unresolved_sentences(probe, entry)
        if entry["status"] == "partial" and tier == TIER_1:
            partial_1 += 1
            by_reason += not sentences and not evidence.pending_rulings(entry)
        if sentences:
            debt += len(sentences) if tier == TIER_1 else 0
            unresolved.append({"id": entry["id"], "tier": tier, "sentences": sentences})
    return {"conditional": conditional, "tier1_debt": debt, "unresolved": unresolved,
            "awaiting_ruling": awaiting, "tier1_partial_entries": partial_1,
            "tier1_partial_by_reason": by_reason}


def build(reg: Register, index: Mapping[str, Any], *,
          waivers: list[dict[str, Any]] | None = None,
          probe: evidence.Probe | None = None) -> dict[str, Any]:
    documents = []
    total: Counter[str] = Counter()
    rejected_by_reason: Counter[str] = Counter()
    removed = []
    for ref, source in sorted(reg.sources.items()):
        entry = index.get(ref) or {}
        if entry.get("status") != "ok" or source["mode"] == "excluded":
            continue
        doc = reg.files.get(ref, {"requirements": []})
        live = [e for e in doc["requirements"] if not e.get("removed")]
        removed += [e["id"] for e in doc["requirements"] if e.get("removed")]
        counts = Counter(e["status"] for e in live)
        total.update(counts)
        real = rules.retired_share(doc)[1]
        row = {"ref": ref, "mode": source["mode"], "tier": entry.get("tier"), "total": len(live),
               **{s: counts[s] for s in STATUSES},
               # However the statuses were set; over rules.TRIAGE_DOC_SHARE, or over
               # rules.NOISE_DOC_SHARE of live entries, needs a reviewed record in policy.yaml
               # (FW-REQ-004)
               "noise_share": round(rules.noise_share(doc)[0] / len(live), 3) if live else 0.0,
               "retired_share": round(rules.retired_share(doc)[0] / real, 3) if real else 0.0,
               "rejected": len(doc.get("rejected", []))}
        rejected_by_reason.update(r["reason"] for r in doc.get("rejected", []))
        if source["mode"] == "catalog":
            row["ids"] = doc.get("count", 0)
        documents.append(row)
    open_items = [{"id": w["id"], "title": w["title"], "findings": w["findings"],
                   "phase": w.get("phase")}
                  for w in reg.work_items.values() if w["status"] == "open"]
    unassessed = [{"ref": ref, "tier": (index.get(ref) or {}).get("tier"),
                   "status": (index.get(ref) or {}).get("status", "unknown")}
                  for ref in sorted(reg.sources)
                  if (index.get(ref) or {}).get("status") != "ok"]
    kinds = Counter(e["kind"] for _, e in reg.live())
    promoted = sum(1 for _, e in reg.live() if e.get("promoted"))
    live_total = sum(total.values())
    reviewed = live_total - total["candidate"]
    assessed = total["covered"] + total["partial"]
    state = evidence_state(reg, index, probe) if probe else {
        "conditional": 0, "tier1_debt": 0, "unresolved": [], "awaiting_ruling": [],
        "tier1_partial_entries": 0, "tier1_partial_by_reason": 0}
    closure = Counter(w["status"] for w in reg.work_items.values())
    summary = {
        "total": live_total,
        **{s: total[s] for s in STATUSES},
        "removed": len(removed),
        "work_items": len(open_items),
        "closed_items": closure["closed"],
        "closed_partial_items": closure["closed-partial"],
        "conditional": state["conditional"],
        "tier1_debt": state["tier1_debt"],
        "tier1_partial_entries": state["tier1_partial_entries"],
        "tier1_partial_by_reason": state["tier1_partial_by_reason"],
        "awaiting_ruling": sum(len(a["sentences"]) for a in state["awaiting_ruling"]),
        "unassessed": len(unassessed),
        "waivers": len(waivers or []),
        "reviewed": reviewed,
        "partial_share": round(total["partial"] / assessed, 3) if assessed else 0.0,
        "kinds": dict(sorted(kinds.items())),
        "promoted": promoted,
        "freeze": freeze_split(reg, index, probe),
        "rejected": sum(rejected_by_reason.values()),
        "rejected_by_reason": dict(sorted(rejected_by_reason.items())),
    }
    return {
        "summary": summary,
        "documents": documents,
        "unassessed": unassessed,
        "work_items": open_items,
        "unresolved": state["unresolved"],
        "awaiting_ruling": state["awaiting_ruling"],
        "removed": removed,
        "excluded": [{"document": i["document"], "reason": i["reason"]}
                     for i in reg.reference_list if i["disposition"] == "excluded"],
    }


def render(report: Mapping[str, Any]) -> list[str]:
    s = report["summary"]
    columns = ("total", *STATUSES, "rejected")
    width = max((len(d["ref"]) for d in report["documents"]), default=3)
    lines = [f"{'document':<{width}}  {'mode':<9}  " + "  ".join(f"{c:>9}" for c in columns)
             + f"  {'noise':>9}  {'retired':>9}"]
    for d in report["documents"]:
        cells = "  ".join(f"{d[c]:>9}" for c in columns)
        note = f"  ({d['ids']} IDs)" if "ids" in d else ""
        lines.append(f"{d['ref']:<{width}}  {d['mode']:<9}  {cells}  "
                     f"{d['noise_share']:>9.0%}  {d['retired_share']:>9.0%}{note}")
    lines.append(f"{'total':<{width}}  {'':<9}  " + "  ".join(f"{s[c]:>9}" for c in columns))
    lines.append("entries by kind: " + ", ".join(f"{k} {n}" for k, n in s["kinds"].items()))
    lines.append(f"promoted by a reviewer from the rejected set or a missed passage: "
                 f"{s['promoted']} (rmf conformance promote)")
    lines.append(f"rejected in-scope paragraphs and rows: {s['rejected']} ("
                 + ", ".join(f"{k} {n}" for k, n in s["rejected_by_reason"].items())
                 + "); sample them with rmf conformance sample --rejected --seed N")
    lines.append(f"partial is {s['partial_share']:.0%} of covered plus partial; "
                 f"{s['reviewed']} of {s['total']} entries reviewed")
    if s["partial_share"] > PARTIAL_WARNING_SHARE:
        lines.append("WARNING: the register is mostly partial: most assessed requirements rest on "
                     "citations or prose that cannot fail")
    lines.append(f"{s['conditional']} of {s['covered']} covered entries hold under a precondition "
                 f"(holds_when); tier 1 debt: {s['tier1_debt']} unresolved sentences in "
                 f"{sum(u['tier'] == TIER_1 for u in report['unresolved'])} partial entries")
    lines.append(f"tier 1 partial entries: {s['tier1_partial_entries']}, of which "
                 f"{s['tier1_partial_by_reason']} hold every sentence and owe only what their "
                 "reason names")
    lines.append(f"awaiting the user's ruling: {s['awaiting_ruling']} sentences in "
                 f"{len(report['awaiting_ruling'])} entries")
    for a in report["awaiting_ruling"]:
        lines.append(f"  {a['id']}: {len(a['sentences'])} sentence(s)")
    lines.append(f"work items closed {s['closed_items']}, closed-partial "
                 f"{s['closed_partial_items']}, open {s['work_items']}")
    freeze = s["freeze"]
    lines.append(f"blocking the p13 freeze (FW-REQ-002): {freeze['tier_1']} tier 1 candidates and "
                 f"{freeze['tier_1_partial_without_strong']} tier 1 partials with no strong item; "
                 f"{freeze['advisory_elsewhere']} candidates outside tier 1 are advisory")
    lines.append(f"set aside without proof, for the p13 sign-off: {freeze['deferred']} deferred, "
                 f"{freeze['partial_on_weak_evidence']} partial on evidence that cannot fail "
                 "(FW-REQ-004)")
    lines.append(f"open work items: {s['work_items']}; FW-TASK-002 waivers: {s['waivers']}; "
                 f"entries removed from their source: {s['removed']}")
    for w in report["work_items"]:
        lines.append(f"  {w['id']} [{', '.join(w['findings'])}] {w['title']}")
    lines.append(f"unassessed documents (never reported as covered): {s['unassessed']}")
    for u in report["unassessed"]:
        tier = f"tier {u['tier']}" if u["tier"] else "no tier"
        lines.append(f"  {u['ref']} ({tier}, {u['status']})")
    return lines


def waivers(repo: Path) -> list[dict[str, Any]]:
    problems: list[tuple[str, str]] = []
    data = register.read(repo, register.NIST_WAIVERS, "nist-waivers", problems)
    return data["waivers"] if data else []
