"""``rmf run migrate``: move a run up to the current framework contract.

The move is deterministic and safe to repeat. ``decision.yaml`` becomes one ledger record and a
new ``ART-AUTHREC.md``. A run on the current contract is left alone. What the old contract never
recorded (a threat assessment, the ATO beneath a cATO) is not invented: ``rmf check`` reports it.
"""

from __future__ import annotations

import io
import json
import re

from ruamel.yaml import YAML

from rmf_tool.framework.model import FRAMEWORK_DIR, META_FILE
from rmf_tool.run import authorization as ledger
from rmf_tool.run.model import ARTIFACTS_DIR, RUN_FILE, Run, read_yaml, version_key

STUB = """---
artifact_id: {artifact}
run_id: {run_id}
produced_by_task: A-2
touched_by: {touched}
sources: {sources}
---
# Authorization ledger

The decisions of this run, one record each, are in `artifacts/data/authorizations.yaml`
[[{token}]].
"""


def _dump(data: object) -> str:
    yaml = YAML()
    yaml.width = 4096
    buf = io.StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()


def _bump(run: Run, version: str) -> None:
    path = run.path(RUN_FILE)
    text = path.read_text(encoding="utf-8")
    line = f"framework_version: {version}"
    bumped, found = re.subn(r"^framework_version: .*$", line, text, count=1, flags=re.M)
    path.write_text(bumped if found else f"{text.rstrip()}\n{line}\n", encoding="utf-8")


# Provider references (F-04-1): org-context.yaml providers registers each one as PRV-##.
ORG_CONTEXT = "artifacts/data/org-context.yaml"
PROVIDER_FIELDS = (
    (ORG_CONTEXT, "common_controls", "provided_by"),
    ("artifacts/data/leveraged-authorizations.yaml", "leveraged_authorizations", "provider"),
    ("artifacts/data/allocation.yaml", "allocations", "provider"),
    ("artifacts/data/allocation.yaml", "providers", "provider"),
    ("artifacts/data/service-agreements.yaml", "agreements", "provider"),
    ("artifacts/ssp/controls", "controls", "inherited_from"),
)
_AN_ID = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")  # LA-01, PRV-03: already an identifier


def migrate_providers(run: Run) -> list[str]:
    """Register every provider named as free text in org-context.yaml providers (PRV-##) and
    rewrite the references to the ID, in place, so each file keeps its layout. Names that
    differ by a word get different IDs: the lines returned list them so the person can merge
    them. Safe to repeat."""
    org_path = run.path(ORG_CONTEXT)
    if not org_path.is_file():
        return []
    org = read_yaml(org_path)
    if not isinstance(org, dict):
        return []
    registry = [p for p in org.get("providers") or [] if isinstance(p, dict) and "id" in p]
    by_name = {" ".join(str(p.get("name", "")).lower().split()): str(p["id"]) for p in registry}
    numbers = [int(str(p["id"]).split("-")[1]) for p in registry
               if str(p["id"]).startswith("PRV-")]
    added: list[tuple[str, str]] = []

    def ident(name: str) -> str:
        norm = " ".join(name.lower().split())
        if norm not in by_name:
            numbers.append(max(numbers, default=0) + 1)
            by_name[norm] = f"PRV-{numbers[-1]:02d}"
            added.append((by_name[norm], name))
        return by_name[norm]

    texts: dict[str, str] = {}
    for rel, key, field in PROVIDER_FIELDS:
        paths = [run.path(rel)] if rel.endswith(".yaml") else sorted(run.path(rel).glob("*.yaml"))
        for path in paths:
            if not path.is_file():
                continue
            name = run.rel(path)
            data = read_yaml(path)
            for item in (data.get(key) or [] if isinstance(data, dict) else []):
                value = item.get(field) if isinstance(item, dict) else None
                if not isinstance(value, str) or not value.strip() or _AN_ID.match(value):
                    continue
                text = texts.get(name, path.read_text(encoding="utf-8"))
                pattern = re.compile(rf"(\b{field}:[ \t]*)([\"']?){re.escape(value)}\2"
                                     r"(?=[ \t]*(?:[,}\]\n#]|$))")
                pid = ident(value)
                texts[name] = pattern.sub(lambda m, i=pid: m.group(1) + i, text)
    if added:
        text = texts.get(ORG_CONTEXT, org_path.read_text(encoding="utf-8"))
        rows = "".join(f"  - {{id: {pid}, name: {json.dumps(n)}}}\n" for pid, n in added)
        if registry:
            text = re.sub(r"^providers:[^\n]*\n((?:[ \t-].*\n)*)",
                          lambda m: m.group(0) + rows, text, count=1, flags=re.M)
        else:
            text = text.rstrip("\n") + "\nproviders:\n" + rows
        texts[ORG_CONTEXT] = text
    for name, text in sorted(texts.items()):
        run.path(name).write_text(text, encoding="utf-8")
    lines = [f"registered provider {pid} {n}" for pid, n in added]
    lines += [f"rewrote provider names to IDs in {name}" for name in sorted(texts)]
    if len(added) > 1:
        lines.append("check the registered names: two that mean one provider should share one "
                     "PRV ID")
    return lines


def migrate(run: Run) -> list[str]:
    """Convert the run; return one line per change."""
    version = str(read_yaml(run.repo / FRAMEWORK_DIR / META_FILE)["framework_version"])
    providers = migrate_providers(run) if version_key(run.contract) >= version_key("0.2.0") \
        else []
    if version_key(run.contract) >= version_key(version):
        return [*providers, f"{run.dir.name}: already on contract {run.contract}"]
    lines = list(providers)
    records = []
    legacy, target = run.path(ledger.LEGACY_FILE), run.path(ledger.LEDGER_FILE)
    if legacy.is_file():
        kinds = {e.id: e.data for e in run.framework.index("decisions").values()}
        records = [ledger.lift(run.data(ledger.LEGACY_FILE), kinds)]
    if records or not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_dump({"records": records}), encoding="utf-8")
        lines.append(f"wrote {ledger.LEDGER_FILE} with {len(records)} record(s)")
    memo = run.path(f"{ARTIFACTS_DIR}/{ledger.LEDGER_ARTIFACT}.md")
    if not memo.is_file():
        tasks = list(dict.fromkeys(["A-2", *(r["task"] for r in records)]))
        sources = (records[0].get("sources") if records else None) or ["ART-SAP"]
        memo.write_text(STUB.format(artifact=ledger.LEDGER_ARTIFACT, run_id=run.run_id,
                                    touched=f"[{', '.join(tasks)}]",
                                    sources=f"[{', '.join(sources)}]", token=sources[0]),
                        encoding="utf-8")
        lines.append(f"wrote {ARTIFACTS_DIR}/{ledger.LEDGER_ARTIFACT}.md")
    required = run.schema_required("authorizations", "record")
    for r in records:
        if r.get("decision") == "AD-CATO":
            lines.append(f"{r['id']}: decision.yaml held the cATO over its ATO, which is lost; "
                         "add the ATO record and set underlying")
        if missing := [f for f in required if f not in r]:
            lines.append(f"{r['id']}: the old contract never recorded {', '.join(missing)}; "
                         "add it, since the schema requires it")
    if legacy.is_file():
        legacy.unlink()
        lines.append(f"removed {ledger.LEGACY_FILE}")
    _bump(run, version)
    lines.append(f"run.yaml: framework_version {run.contract} -> {version}")
    lines.append("next: uv run rmf build, then uv run rmf check, and fill what it reports")
    return lines
