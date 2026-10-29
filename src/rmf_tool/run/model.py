"""The run model (plan §7.1): a run directory, its ``run.yaml`` and the framework it executes.

A ``Run`` is short-lived (one command). File contents are read on demand and never
cached, because ``rmf build`` rewrites files between reads.
"""

from __future__ import annotations

import functools
import json
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import FormatChecker
from ruamel.yaml import YAML

from rmf_tool.framework import graph
from rmf_tool.framework.load import load
from rmf_tool.framework.model import FRAMEWORK_DIR, SCHEMA_DIR, Framework, task_sort_key
from rmf_tool.gitutil import repo_root

RUN_FILE = "run.yaml"
FACTS_FILE = "facts.yaml"
ASSUMPTIONS_FILE = "assumptions.yaml"
JOURNAL_FILE = "journal.md"
BASELINE_FILE = "baseline.json"
MANIFEST_FILE = "package/manifest.yaml"
ARTIFACTS_DIR = "artifacts"
INTERVIEWS_DIR = "interviews"
OSCAL_DIR = "oscal"
REPORTS_DIR = "reports"
RUNS_DIR = "runs"
FAMILY_TOKEN = "<fam>"  # artifacts.yaml data paths with one file per control family


class RunError(Exception):
    """No run found, or run.yaml unreadable (exit code 2)."""


class YamlError(ValueError):
    pass


def read_yaml(path: Path) -> Any:
    """Safe-load a YAML file; raises YamlError with a short message."""
    try:
        return YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise YamlError(f"cannot read: {exc.strerror or exc}") from exc
    except Exception as exc:  # ruamel raises several unrelated parser error types
        raise YamlError(f"not valid YAML: {exc}") from exc


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise YamlError(f"cannot read: {exc.strerror or exc}") from exc
    except ValueError as exc:
        raise YamlError(f"not valid JSON: {exc}") from exc


@functools.cache
def _validator(schema_path: Path) -> Any:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema, format_checker=FormatChecker())


def schema_errors(repo: Path, name: str, data: Any) -> list[str]:
    """Errors of ``data`` against ``framework/schema/<name>.schema.json``."""
    validator = _validator((repo / SCHEMA_DIR / f"{name}.schema.json").resolve())
    errors = sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:200]}"
            for e in errors]


@dataclass
class Run:
    dir: Path
    repo: Path
    config: dict[str, Any]
    framework: Framework

    # --- framework views ------------------------------------------------------------
    @cached_property
    def tasks(self) -> dict[str, Any]:
        return {tid: e.data for tid, e in self.framework.index("tasks").items()}

    @cached_property
    def artifacts(self) -> dict[str, Any]:
        return {aid: e.data for aid, e in self.framework.index("artifacts").items()}

    @cached_property
    def personas(self) -> dict[str, Any]:
        return {pid: e.data for pid, e in self.framework.index("personas").items()}

    @cached_property
    def order(self) -> list[str]:
        """Task IDs in topological order (RMF step, then number, as the tie-break)."""
        return graph.topo_order(graph.dependency_graph(self.framework), key=task_sort_key)

    @cached_property
    def position(self) -> dict[str, int]:
        return {t: i for i, t in enumerate(self.order)}

    @cached_property
    def ancestors(self) -> dict[str, frozenset[str]]:
        return graph.ancestors(graph.dependency_graph(self.framework))

    def writers(self, artifact: str) -> list[str]:
        """The producer first, then every task that updates the artifact (topological)."""
        art = self.artifacts.get(artifact, {})
        producer = art.get("producer")
        updaters = [t for t in self.order
                    if artifact in (self.tasks[t].get("outputs") or []) and t != producer]
        return ([producer] if producer else []) + updaters

    @cached_property
    def fact_writers(self) -> dict[str, str]:
        """Dotted fact path -> the task whose writes_facts names it."""
        return {f: t for t in self.order for f in (self.tasks[t].get("writes_facts") or [])}

    # --- run views ------------------------------------------------------------------
    @property
    def run_id(self) -> str:
        return str(self.config.get("run_id", self.dir.name))

    @property
    def mode(self) -> str:
        return str(self.config.get("mode", ""))

    @property
    def product_dir(self) -> Path:
        return (self.dir / str(self.config.get("product", "product"))).resolve()

    def path(self, rel: str) -> Path:
        return self.dir / rel

    def rel(self, path: Path) -> str:
        return path.relative_to(self.dir).as_posix()

    def data_files(self, artifact: str) -> list[tuple[str, str | None]]:
        """(run-relative path, schema name) of each existing data file of an artifact;
        family paths (``<fam>``) expand to every file present."""
        out = []
        for entry in self.artifacts.get(artifact, {}).get("data") or []:
            path, schema = entry["path"], entry.get("schema")
            if FAMILY_TOKEN in path:
                parent, _, pattern = path.rpartition("/")
                for f in sorted((self.dir / parent).glob(pattern.replace(FAMILY_TOKEN, "*"))):
                    out.append((self.rel(f), schema))
            elif "#" not in path and (self.dir / path).is_file():
                out.append((path, schema))
        return out

    def artifact_md(self, artifact: str) -> Path:
        return self.dir / ARTIFACTS_DIR / f"{artifact}.md"

    def owner_artifact(self, rel: str) -> str | None:
        """The artifact a run-relative file belongs to (its MD or one of its data files)."""
        if rel.startswith(f"{ARTIFACTS_DIR}/") and rel.endswith(".md") and rel.count("/") == 1:
            stem = rel[len(ARTIFACTS_DIR) + 1:-3]
            return stem if stem in self.artifacts else None
        for aid, art in self.artifacts.items():
            for entry in art.get("data") or []:
                path = entry["path"].partition("#")[0]
                if FAMILY_TOKEN in path:
                    parent, _, pattern = path.rpartition("/")
                    prefix, _, suffix = pattern.partition(FAMILY_TOKEN)
                    head, _, name = rel.rpartition("/")
                    if head == parent and name.startswith(prefix) and name.endswith(suffix):
                        return aid
                elif rel == path and path != FACTS_FILE:
                    return aid
        return None

    def data(self, rel: str) -> Any:
        """YAML or JSON content of a run file; raises YamlError."""
        path = self.dir / rel
        return read_json(path) if rel.endswith(".json") else read_yaml(path)

    def schema_errors(self, name: str, data: Any) -> list[str]:
        return schema_errors(self.repo, name, data)


def find_run_dir(arg: Path | None, cwd: Path | None = None) -> Path:
    """The run directory: ``arg`` (a run dir or its run.yaml), else cwd when it holds
    run.yaml, else the only or most recently initialised ``runs/*/run.yaml``."""
    cwd = cwd or Path.cwd()
    if arg is not None:
        path = arg if arg.is_dir() else arg.parent
        if not (path / RUN_FILE).is_file():
            raise RunError(f"{arg}: no {RUN_FILE} found")
        return path
    if (cwd / RUN_FILE).is_file():
        return cwd
    candidates = sorted(cwd.glob(f"{RUNS_DIR}/*/{RUN_FILE}"),
                        key=lambda p: (os.stat(p).st_mtime_ns, p.parent.name))
    if not candidates:
        raise RunError("no run found: pass the run directory, or run `rmf run init` first")
    return candidates[-1].parent


def open_run(arg: Path | None = None, repo: Path | None = None) -> Run:
    """Load a run. The framework comes from the repository containing the cwd."""
    run_dir = find_run_dir(arg)
    repo = repo or repo_root()
    try:
        config = read_yaml(run_dir / RUN_FILE)
    except YamlError as exc:
        raise RunError(f"{run_dir / RUN_FILE}: {exc}") from exc
    if not isinstance(config, dict):
        raise RunError(f"{run_dir / RUN_FILE}: expected a mapping")
    loaded = load(repo / FRAMEWORK_DIR, repo)
    if loaded.findings:
        raise RunError(f"framework unreadable: {loaded.findings[0].render()} "
                       "(run `rmf validate`)")
    return Run(run_dir.resolve(), repo, config, loaded.framework)
