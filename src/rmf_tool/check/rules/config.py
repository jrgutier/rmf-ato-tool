"""Run-configuration rules.

- RUN-CFG-001: run.yaml valid; scope, deferrals and seeds name real tasks and artifacts;
  every artifact an active task needs from an inactive producer is seeded with a file.
- RUN-STALE-001 (W): ``upstream_hash`` differs from a fresh hash of the same variant
  (``upstream_hash_basis``, ADR-0001; absent means union).
- DEGRADED-001 (W, never filtered out): the run depends on a degraded reference.
"""

from __future__ import annotations

from pathlib import Path

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope, upstream_hash
from rmf_tool.run.model import RUN_FILE, YamlError, read_yaml

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


def stale_upstream(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    stamped = run.config.get("upstream_hash_basis")
    basis = stamped or {"variant": "union"}
    if not isinstance(basis, dict):
        return []  # RUN-CFG-001 reports the schema violation
    if basis.get("variant") == "scenario":
        path = run.repo / str(basis.get("scenario"))
        try:
            globs = read_yaml(path)["hash_globs"]
        except (YamlError, TypeError, KeyError):
            return [make("RUN-STALE-001", f"cannot recompute upstream_hash: scenario "
                         f"{basis.get('scenario')} unreadable or without hash_globs", RUN_FILE)]
        variant = f"scenario {Path(str(basis.get('scenario'))).stem}"
    else:
        globs = list(upstream_hash.UNION_GLOBS)
        variant = "union" if stamped else "union (assumed: run.yaml has no upstream_hash_basis)"
    if run.config.get("upstream_hash") == upstream_hash.compute(run.repo, globs):
        return []
    return [make("RUN-STALE-001", f"upstream files changed since the run started: the {variant} "
                 "hash differs; re-check the affected tasks against the current playbooks",
                 RUN_FILE)]


def degraded(ctx: Context) -> list[RunFinding]:
    return [make("DEGRADED-001", f"the run depends on degraded reference {ref}; the AO memo "
                 "must disclose it (plan §7.6)", RUN_FILE) for ref in ctx.degraded_refs]
