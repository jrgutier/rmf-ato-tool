"""Apply the I-8 overlay marks held back by the fan-out cap, once the user approves the two
exceptions drafted in ovs-fanout-exceptions.draft.yaml (copied into conformance/policy.yaml).

    uv run python docs/audits/2026-11-triage/ovs-fanout-marks.py

Refuses to run until each rule the marks cite has an approved exception whose limit holds all
its items, and until each such rule is in the registry. Then marks each entry of
ovs-fanout-marks.yaml with rmf's own mark_many, adds the entries to the rule's enforces list,
and lists the open work items that rmf validate would accept as closed-partial, judged by the
closure rule FW-REQ-004 itself applies. Safe to rerun."""

import re
import sys
from collections import Counter
from pathlib import Path

from ruamel.yaml import YAML

from rmf_tool import refs
from rmf_tool.conformance import evidence, register, rules
from rmf_tool.conformance.cli_support import mark_many
from rmf_tool.framework.load import load

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REGISTRY = REPO / "src/rmf_tool/check/registry.yaml"
yaml = YAML(typ="safe")


def rule_block(text: str, rule: str) -> re.Match[str] | None:
    return re.search(rf"  - id: {rule}\n(?:    .*\n)+", text)


def closable(work_items: set[str]) -> list[str]:
    """The open work items among these that FW-REQ-004 accepts as closed-partial."""
    reg = register.load(REPO)
    probe = evidence.probe(REPO, load(REPO / "framework", REPO).framework)
    index = refs.load_index(REPO)
    out = []
    for ident in sorted(work_items):
        item = reg.work_items.get(ident)
        bound = reg.bound(ident)
        if item is None or item["status"] != "open" or not bound:
            continue
        if not rules._closure_problems(ident, {**item, "status": "closed-partial"}, bound,
                                       probe, index):
            out.append(ident)
    return out


def main() -> int:
    entries = yaml.load((HERE / "ovs-fanout-marks.yaml").read_text("utf-8"))["entries"]
    deferred = {e["id"] for e in entries}
    items = Counter(i["target"] for e in entries for i in e["evidence"] if i["kind"] == "rule")
    held = Counter(i["target"] for f in sorted((REPO / "conformance/requirements").glob("*.yaml"))
                   for e in yaml.load(f.read_text("utf-8"))["requirements"]
                   if e["id"] not in deferred for i in e.get("evidence") or []
                   if i["kind"] == "rule")
    policy = yaml.load((REPO / "conformance/policy.yaml").read_text("utf-8"))
    approved = {x["target"]: x["limit"] for x in policy.get("fan_out_exceptions") or []
                if x.get("kind") == "rule" and x.get("approved_by") == "user"}
    text = REGISTRY.read_text("utf-8")
    problems = [f"{rule}: needs an approved exception with limit >= {count + held[rule]}"
                for rule, count in sorted(items.items())
                if approved.get(rule, 0) < count + held[rule]]
    problems += [f"{rule} is not in {REGISTRY.relative_to(REPO)}" for rule in sorted(items)
                 if rule_block(text, rule) is None]
    if problems:
        print("not applied; " + "; ".join(problems), file=sys.stderr)
        return 1
    mark_many(REPO, {e["id"]: {k: e.get(k) for k in ("status", "reason", "evidence",
                                                       "ruling_sought")} for e in entries})
    for rule in items:
        block = rule_block(text, rule)
        assert block is not None  # checked above, before any mark was written
        body = block.group(0)
        ids = set(re.findall(r"      - (REQ-\S+)", body))
        ids |= {e["id"] for e in entries for i in e["evidence"] if i.get("target") == rule}
        body = re.sub(r"    enforces:\n(?:      - .*\n)*", "", body)
        body += "    enforces:\n" + "".join(f"      - {i}\n" for i in sorted(ids))
        text = text[:block.start()] + body + text[block.end():]
    REGISTRY.write_text(text, "utf-8")
    print(f"marked {len(entries)} entries; "
          + ", ".join(f"{r} +{n}" for r, n in sorted(items.items())))
    ready = closable({e["work_item"] for e in entries if e.get("work_item")})
    print("closed-partial now valid for (set status and closed_by, then rmf validate):",
          ", ".join(ready) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
