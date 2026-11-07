"""Apply the I-8 overlay marks held back by the fan-out cap, once the user approves the two
exceptions drafted in ovs-fanout-exceptions.draft.yaml (copied into conformance/policy.yaml).

    uv run python docs/audits/2026-11-triage/ovs-fanout-marks.py

Refuses to run until each rule the marks cite has an approved exception whose limit holds its
items. Then marks each entry of ovs-fanout-marks.yaml with rmf's own mark_many, adds the
entries to the rule's enforces list in the registry, and lists the work items whose bound
entries all carry rule evidence, for closing as closed-partial. Safe to rerun."""

import re
import sys
from collections import Counter
from pathlib import Path

from ruamel.yaml import YAML

from rmf_tool.conformance.cli_support import mark_many

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REGISTRY = REPO / "src/rmf_tool/check/registry.yaml"
yaml = YAML(typ="safe")
entries = yaml.load((HERE / "ovs-fanout-marks.yaml").read_text("utf-8"))["entries"]
items = Counter(i["target"] for e in entries for i in e["evidence"] if i["kind"] == "rule")
policy = yaml.load((REPO / "conformance/policy.yaml").read_text("utf-8"))
approved = {x["target"]: x["limit"] for x in policy.get("fan_out_exceptions") or []
            if x.get("kind") == "rule" and x.get("approved_by") == "user"}
text = REGISTRY.read_text("utf-8")
deferred = {e["id"] for e in entries}
held = Counter(i["target"] for f in sorted((REPO / "conformance/requirements").glob("*.yaml"))
               for e in yaml.load(f.read_text("utf-8"))["requirements"]
               if e["id"] not in deferred for i in e.get("evidence") or [] if i["kind"] == "rule")
missing = []
for rule, count in sorted(items.items()):
    if approved.get(rule, 0) < count + held[rule]:
        missing.append(f"{rule}: needs an approved exception with limit >= {count + held[rule]}")
if missing:
    sys.exit("not applied; " + "; ".join(missing))
mark_many(REPO, {e["id"]: {k: e.get(k) for k in ("status", "reason", "evidence",
                                                   "ruling_sought")} for e in entries})
for rule in items:
    ids = {e["id"] for e in entries for i in e["evidence"] if i.get("target") == rule}
    block = re.search(rf"  - id: {rule}\n(?:    .*\n)+", text)
    body = block.group(0)
    ids |= set(re.findall(r"      - (REQ-\S+)", body))
    body = re.sub(r"    enforces:\n(?:      - .*\n)*", "", body)
    body += "    enforces:\n" + "".join(f"      - {i}\n" for i in sorted(ids))
    text = text[:block.start()] + body + text[block.end():]
REGISTRY.write_text(text, "utf-8")
print(f"marked {len(entries)} entries; " + ", ".join(f"{r} +{n}" for r, n in sorted(items.items())))
bound: dict[str, list[bool]] = {}
for f in sorted((REPO / "conformance/requirements").glob("*.yaml")):
    for e in yaml.load(f.read_text("utf-8"))["requirements"]:
        wi = e.get("work_item")
        if wi in {x["work_item"] for x in entries}:
            strong = e["status"] == "partial" and not e.get("ruling_sought") and any(
                i["kind"] == "rule" for i in e.get("evidence") or [])
            bound.setdefault(wi, []).append(strong)
ready = sorted(w for w, s in bound.items() if all(s))
print("closed-partial candidates (then run rmf validate):", ", ".join(ready) or "none")
