"""``rmf run migrate``: move a run up to the current framework contract.

The move is deterministic and safe to repeat. ``decision.yaml`` becomes one ledger record and a
new ``ART-AUTHREC.md``. A run on the current contract is left alone. What the old contract never
recorded (a threat assessment, the ATO beneath a cATO) is not invented: ``rmf check`` reports it.
"""

from __future__ import annotations

import io
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


def migrate(run: Run) -> list[str]:
    """Convert the run; return one line per change."""
    version = str(read_yaml(run.repo / FRAMEWORK_DIR / META_FILE)["framework_version"])
    if version_key(run.contract) >= version_key(version):
        return [f"{run.dir.name}: already on contract {run.contract}"]
    lines = []
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
