"""Scope, deferral precedence and seeding (plan §7.3).

Deferral precedence, highest first: out of scope; explicit ``deferred[T]``; implicit
lifecycle (after ``lifecycle_stop``, not in ``include_after_stop``); otherwise active.
For every active task, each input or updated output whose producers (the producer plus
updaters that are ancestors of the task) are all inactive must be seeded. Generated
artifacts (ART-PKG) are produced by the CLI and never need a seed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rmf_tool.run.model import Run

ACTIVE = "active"
OUT_OF_SCOPE = "out-of-scope"
DEFERRED = "deferred"
LIFECYCLE = "lifecycle"


@dataclass(frozen=True)
class TaskScope:
    state: str  # active | out-of-scope | deferred | lifecycle
    rationale: str | None = None


@dataclass(frozen=True)
class SeedNeed:
    task: str
    artifact: str
    kind: str  # "input" | "updated output"
    producers: tuple[str, ...]


def scope_tasks(run: Run) -> set[str]:
    """run.yaml of the wrong shape (RUN-CFG-001 reports it) reads as what it does say: a scope
    that is no mapping is the default, a task list that is no list names no task."""
    scope = run.config.get("scope")
    tasks = scope.get("tasks", "all") if isinstance(scope, dict) else "all"
    if tasks == "all":
        return set(run.tasks)
    return {t for t in (tasks if isinstance(tasks, list) else [])
            if isinstance(t, str) and t in run.tasks}


def task_scopes(run: Run) -> dict[str, TaskScope]:
    in_scope = scope_tasks(run)
    deferred, after = run.config.get("deferred"), run.config.get("include_after_stop")
    explicit: dict[str, Any] = deferred if isinstance(deferred, dict) else {}
    stop = run.config.get("lifecycle_stop")
    include = {t for t in (after if isinstance(after, list) else []) if isinstance(t, str)}
    stop_at = run.position.get(stop) if isinstance(stop, str) else None
    out: dict[str, TaskScope] = {}
    for t in run.order:
        if t not in in_scope:
            out[t] = TaskScope(OUT_OF_SCOPE, "not in run.yaml scope")
        elif t in explicit and isinstance(explicit[t], dict):
            d = explicit[t]
            out[t] = TaskScope(DEFERRED, f"{d.get('kind')}: {d.get('rationale')}")
        elif stop_at is not None and run.position[t] > stop_at and t not in include:
            out[t] = TaskScope(LIFECYCLE, run.config.get("lifecycle_stop_rationale"))
        else:
            out[t] = TaskScope(ACTIVE)
    return out


def active_tasks(run: Run) -> list[str]:
    scopes = task_scopes(run)
    return [t for t in run.order if scopes[t].state == ACTIVE]


def seeded(run: Run) -> list[dict[str, Any]]:
    listed = run.config.get("seeded")
    return [s for s in (listed if isinstance(listed, list) else []) if isinstance(s, dict)]


def seed_needs(run: Run) -> list[SeedNeed]:
    active = set(active_tasks(run))
    needs: list[SeedNeed] = []
    for t in run.order:
        if t not in active:
            continue
        task = run.tasks[t]
        produced = {a for a in task.get("outputs") or []
                    if run.artifacts.get(a, {}).get("producer") == t}
        wanted = [(a, "input") for a in task.get("inputs") or []]
        wanted += [(a, "updated output") for a in task.get("outputs") or [] if a not in produced]
        for artifact, kind in wanted:
            art = run.artifacts.get(artifact)
            if art is None or art.get("generated"):
                continue  # EXT-* inputs; CLI-generated artifacts
            writers = run.writers(artifact)
            producers = tuple(w for i, w in enumerate(writers)
                              if i == 0 or w in run.ancestors.get(t, frozenset()))
            if not any(p in active for p in producers):
                needs.append(SeedNeed(t, artifact, kind, producers))
    return needs


def produced_or_seeded(run: Run, artifact: str) -> bool:
    """RUN-ART-001 and coverage scope: the producer is active or the artifact is seeded."""
    producer = run.artifacts.get(artifact, {}).get("producer")
    return producer in set(active_tasks(run)) or any(
        s.get("artifact") == artifact for s in seeded(run))
