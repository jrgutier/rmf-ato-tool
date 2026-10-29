"""RUN-CFG-001: run.yaml valid; scope, deferrals and seeds name real tasks and artifacts;
every artifact an active task needs from an inactive producer is seeded with a file."""

from __future__ import annotations

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope
from rmf_tool.run.model import RUN_FILE

RULE = "RUN-CFG-001"


def run_cfg(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out = [make(RULE, f"schema: {e}", RUN_FILE) for e in run.schema_errors("run-config",
                                                                          run.config)]

    def err(message: str) -> None:
        out.append(make(RULE, message, RUN_FILE))

    tasks = (run.config.get("scope") or {}).get("tasks")
    named = [*(tasks if isinstance(tasks, list) else []),
             *(run.config.get("include_after_stop") or []),
             *(run.config.get("deferred") or {})]
    if run.config.get("lifecycle_stop"):
        named.append(run.config["lifecycle_stop"])
    for t in sorted({str(t) for t in named} - set(run.tasks)):
        err(f"unknown task {t}")
    if not run.product_dir.is_dir():
        err(f"product directory {run.config.get('product')!r} not found")

    active = set(scope.active_tasks(run))
    seeded = scope.seeded(run)
    for s in seeded:
        artifact, origin, path = s.get("artifact"), s.get("from_task"), str(s.get("path"))
        if artifact not in run.artifacts:
            err(f"seeded artifact {artifact} is not a framework artifact")
            continue
        if origin not in run.writers(artifact):
            err(f"seeded {artifact} from {origin}, which neither produces nor updates it")
        elif origin in active:
            err(f"seeded {artifact} from {origin}, which is in scope; let the task produce it")
        if not run.path(path).is_file():
            err(f"seed file {path} ({artifact}) not found")
    have = {s.get("artifact") for s in seeded}
    for need in scope.seed_needs(run):
        if need.artifact not in have:
            err(f"{need.task} needs {need.artifact} ({need.kind}), whose producer(s) "
                f"{', '.join(need.producers)} are not in scope; add it to seeded with a file")
    return out
