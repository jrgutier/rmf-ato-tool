"""`rmf conformance report`: where the register stands, per document and in total."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rmf_tool.conformance import register, rules
from rmf_tool.conformance.register import STATUSES, Register

# `partial` caps what evidence can prove, so a register resting on it must stay visible.
PARTIAL_WARNING_SHARE = 0.5
TIER_1 = 1
# Kinds that state an obligation; `should` and `table` are advisory outside tier 1.
OBLIGATION_KINDS = frozenset({"lettered", "modal", "indicative", "imperative",
                              register.PROMOTED_KIND})


def blocks_freeze(kind: str, tier: int | None) -> bool:
    """FW-REQ-002 at p13 (ADR-0005): a candidate blocks the freeze when its document is tier 1
    or its kind states an obligation; a should or table candidate elsewhere only warns."""
    return tier == TIER_1 or kind in OBLIGATION_KINDS


def freeze_split(reg: Register, index: Mapping[str, Any]) -> dict[str, int]:
    """Live candidates by what they will mean at p13, and the entries set aside without proof
    (deferred, partial on evidence that cannot fail) that the sign-off at p13 reads, so a
    scripted loop of `mark --status deferred` is as visible as a loop of `not-applicable`
    (FW-REQ-004)."""
    out = {"tier_1": 0, "obligations_elsewhere": 0, "advisory_elsewhere": 0, "deferred": 0,
           "partial_on_weak_evidence": 0}
    for ref, entry in reg.live():
        if entry["status"] == "deferred":
            out["deferred"] += 1
        elif entry["status"] == "partial" and rules.retired(entry):
            out["partial_on_weak_evidence"] += 1
        if entry["status"] != "candidate":
            continue
        tier = (index.get(ref) or {}).get("tier")
        if tier == TIER_1:
            out["tier_1"] += 1
        elif blocks_freeze(entry["kind"], tier):
            out["obligations_elsewhere"] += 1
        else:
            out["advisory_elsewhere"] += 1
    return out


def build(reg: Register, index: Mapping[str, Any], *,
          waivers: list[dict[str, Any]] | None = None) -> dict[str, Any]:
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
    summary = {
        "total": live_total,
        **{s: total[s] for s in STATUSES},
        "removed": len(removed),
        "work_items": len(open_items),
        "unassessed": len(unassessed),
        "waivers": len(waivers or []),
        "reviewed": reviewed,
        "partial_share": round(total["partial"] / assessed, 3) if assessed else 0.0,
        "kinds": dict(sorted(kinds.items())),
        "promoted": promoted,
        "freeze": freeze_split(reg, index),
        "rejected": sum(rejected_by_reason.values()),
        "rejected_by_reason": dict(sorted(rejected_by_reason.items())),
    }
    return {
        "summary": summary,
        "documents": documents,
        "unassessed": unassessed,
        "work_items": open_items,
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
    freeze = s["freeze"]
    lines.append(f"candidates at the p13 freeze: {freeze['tier_1']} in tier 1 documents and "
                 f"{freeze['obligations_elsewhere']} obligations elsewhere block it; "
                 f"{freeze['advisory_elsewhere']} should or table entries elsewhere warn")
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
