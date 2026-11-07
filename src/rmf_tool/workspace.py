"""`rmf new` and `rmf run init` (plan §7.1, §4.4): scaffold a fork workspace and start runs.

A workspace holds ``product/`` (from ``templates/workspace/product/``) and ``runs/``. A run
is ``runs/<run-id>/`` with run.yaml (stamped: mode, run_id, product, as_of,
framework_version, git_sha, upstream_hash, upstream_hash_basis, oscal_version), facts.yaml,
assumptions.yaml, journal.md and empty artifact and interview directories. A scenario
(``tests/agent/scenarios/<s>.yaml``) supplies the product, scope, seeds, lifecycle, entry and
control subset, and its ``hash_globs`` scope the upstream hash (``upstream_hash_basis``
records which variant a run carries, ADR-0001). A scenario with ``base_run`` starts from a
copy of that run instead, minus its ``remove`` paths (ADR-0004).
"""

from __future__ import annotations

import datetime as dt
import io
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import jinja2
from ruamel.yaml import YAML

from rmf_tool.framework.model import FRAMEWORK_DIR, META_FILE
from rmf_tool.oscal.version import OSCAL_VERSION
from rmf_tool.run import frontmatter, upstream_hash
from rmf_tool.run.model import (
    ARTIFACTS_DIR,
    ASSUMPTIONS_FILE,
    FACTS_FILE,
    INTERVIEWS_DIR,
    JOURNAL_FILE,
    RUN_FILE,
    RUNS_DIR,
    read_yaml,
    schema_errors,
)

MODES = ("synthetic", "hybrid")
RUN_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,40}$")
TEMPLATES = "templates"
PRODUCT_TEMPLATE = f"{TEMPLATES}/workspace/product"
STAMPED = ("mode", "run_id", "product", "as_of", "framework_version", "git_sha",
           "upstream_hash", "upstream_hash_basis", "oscal_version")
DEFAULTS: dict[str, Any] = {
    "humans": {}, "scope": {"tasks": "all"}, "seeded": [], "lifecycle_stop": None,
    "include_after_stop": [], "lifecycle_stop_rationale": None, "deferred": {},
}
KEY_ORDER = (*STAMPED, "humans", "scope", "seeded", "lifecycle_stop", "include_after_stop",
             "lifecycle_stop_rationale", "deferred", "entry", "control_subset")


class WorkspaceError(Exception):
    """Refused or invalid input (exit code 2)."""


def _yaml() -> YAML:
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_run_id(runs_dir: Path, mode: str, day: dt.date | None = None) -> str:
    stem = f"{(day or dt.datetime.now(dt.UTC).date()):%Y%m%d}-{mode}"
    n = 1
    while (runs_dir / f"{stem}-{n:02d}").exists():
        n += 1
    return f"{stem}-{n:02d}"


def _git_sha(repo: Path) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=12", "HEAD"],
                          capture_output=True, text=True, check=False)
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else None


def _render(template: str, **variables: Any) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, keep_trailing_newline=True,
                             autoescape=False)
    try:
        return env.from_string(template).render(**variables)
    except jinja2.TemplateError as exc:
        raise WorkspaceError(f"template error: {exc}") from exc


def load_scenario(repo: Path, path: Path) -> dict[str, Any]:
    try:
        data = read_yaml(path)
    except ValueError as exc:
        raise WorkspaceError(f"{path}: {exc}") from exc
    errors = schema_errors(repo, "scenario", data)
    if errors:
        raise WorkspaceError(f"{path}: scenario invalid: {errors[0]}")
    return data


def scenario_hash(repo: Path, scenario: dict[str, Any]) -> str:
    return upstream_hash.compute(repo, scenario["hash_globs"])


def _copy_base_run(base_run: Path, run_dir: Path, run_id: str, remove: list[str]) -> None:
    """A scenario's ``base_run`` copied into ``run_dir`` (ADR-0004): the ``remove`` paths are
    deleted and every Markdown front-matter ``run_id`` names the new run. run.yaml is
    rewritten by the caller."""
    shutil.copytree(base_run, run_dir)
    for rel in remove:
        target = run_dir / rel
        if not target.resolve().is_relative_to(run_dir.resolve()):
            raise WorkspaceError(f"remove path {rel!r} leaves the run directory")
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        else:
            raise WorkspaceError(f"remove path {rel!r} is not in base_run {base_run}")
    for path in run_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        updated = frontmatter.set_key(text, "run_id", run_id)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def init_run(workspace: Path, repo: Path, mode: str = "synthetic", run_id: str | None = None,
             scenario_path: Path | None = None, as_of: str | None = None) -> Path:
    """Create ``<workspace>/runs/<run-id>/``; returns the run directory."""
    if not (repo / FRAMEWORK_DIR / META_FILE).is_file():
        raise WorkspaceError(f"{repo} is not an rmf repository ({FRAMEWORK_DIR}/ not found); "
                             "run rmf from inside the template or a fork")
    if mode not in MODES:
        raise WorkspaceError(f"--mode must be one of {', '.join(MODES)}")
    runs = workspace / RUNS_DIR
    run_id = run_id or default_run_id(runs, mode)
    if not RUN_ID.match(run_id):
        raise WorkspaceError(f"run id {run_id!r} must match {RUN_ID.pattern}")
    run_dir = runs / run_id
    if run_dir.exists():
        raise WorkspaceError(f"{run_dir} already exists")

    scenario = load_scenario(repo, scenario_path) if scenario_path else None
    if scenario:
        product = repo / scenario["product"]
        globs = scenario["hash_globs"]
        basis = {"variant": "scenario", "scenario": Path(
            os.path.relpath(scenario_path.resolve(), repo.resolve())).as_posix()}
    else:
        product = workspace / "product"
        globs = list(upstream_hash.UNION_GLOBS)
        basis = {"variant": "union"}
    if not product.is_dir():
        raise WorkspaceError(f"product directory {product} not found")

    yaml = _yaml()
    base_run = repo / scenario["base_run"] if scenario and "base_run" in scenario else None
    if base_run is not None and not (base_run / RUN_FILE).is_file():
        raise WorkspaceError(f"base_run {base_run} has no {RUN_FILE}")
    template = base_run / RUN_FILE if base_run else repo / TEMPLATES / RUN_FILE
    base = yaml.load(template.read_text(encoding="utf-8")) if template.is_file() else None
    config: dict[str, Any] = dict(DEFAULTS)
    if isinstance(base, dict):
        config.update({k: v for k, v in base.items() if k not in STAMPED})
    meta = read_yaml(repo / FRAMEWORK_DIR / META_FILE)
    config.update({
        # A resumed run keeps its mode and start time: its journal times must not go back.
        "mode": base["mode"] if base_run and isinstance(base, dict) else mode,
        "run_id": run_id,
        "product": Path(os.path.relpath(product.resolve(), run_dir.resolve())).as_posix(),
        "as_of": (base["as_of"] if base_run and isinstance(base, dict) else None)
                 or as_of or now_utc(),
        "framework_version": str(meta["framework_version"]),
        "git_sha": _git_sha(repo),
        "upstream_hash": upstream_hash.compute(repo, globs),
        "upstream_hash_basis": basis,
        "oscal_version": OSCAL_VERSION,
    })
    seeds: list[tuple[Path, str]] = []
    if scenario:
        config["scope"] = scenario["scope"]
        for key in ("lifecycle_stop", "include_after_stop", "entry", "control_subset"):
            if key in scenario:
                config[key] = scenario[key]
        seeds_dir = base_run or repo / scenario.get("seeds_dir", ".")
        config["seeded"] = [dict(s) for s in scenario["seeded"]]
        for s in scenario["seeded"]:
            src = seeds_dir / s["path"]
            if not src.is_file():
                raise WorkspaceError(f"seed file {src} not found")
            seeds.append((src, s["path"]))
    ordered = {k: config[k] for k in KEY_ORDER if k in config}
    errors = schema_errors(repo, "run-config", ordered)
    if errors:
        raise WorkspaceError(f"run.yaml would be invalid: {errors[0]}")

    if base_run is not None:
        assert scenario is not None
        _copy_base_run(base_run, run_dir, run_id, scenario.get("remove") or [])
        buf = io.StringIO()
        yaml.dump(ordered, buf)
        (run_dir / RUN_FILE).write_text(buf.getvalue(), encoding="utf-8")
        return run_dir

    for sub in (f"{ARTIFACTS_DIR}/data", INTERVIEWS_DIR):
        (run_dir / sub).mkdir(parents=True)
    buf = io.StringIO()
    yaml.dump(ordered, buf)
    (run_dir / RUN_FILE).write_text(buf.getvalue(), encoding="utf-8")
    facts_tpl = repo / TEMPLATES / FACTS_FILE
    (run_dir / FACTS_FILE).write_text(
        facts_tpl.read_text(encoding="utf-8") if facts_tpl.is_file() else "{}\n",
        encoding="utf-8")
    (run_dir / ASSUMPTIONS_FILE).write_text("assumptions: []\n", encoding="utf-8")
    journal_tpl = repo / TEMPLATES / JOURNAL_FILE
    journal = (_render(journal_tpl.read_text(encoding="utf-8"), run_id=run_id, mode=mode,
                       as_of=config["as_of"])
               if journal_tpl.is_file() else f"# Journal — {run_id}\n")
    (run_dir / JOURNAL_FILE).write_text(journal, encoding="utf-8")
    for src, rel in seeds:
        dest = run_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.suffix == ".md":
            text = src.read_text(encoding="utf-8")
            dest.write_text(frontmatter.set_key(text, "run_id", run_id), encoding="utf-8")
        else:
            shutil.copyfile(src, dest)
    return run_dir


def new_workspace(directory: Path, slug: str, repo: Path, mode: str = "synthetic",
                  run_id: str | None = None, force: bool = False,
                  as_of: str | None = None) -> Path:
    """Scaffold ``product/`` and ``runs/`` in ``directory`` and start a first run."""
    if not RUN_ID.match(slug):
        raise WorkspaceError(f"slug {slug!r} must match {RUN_ID.pattern}")
    product, runs = directory / "product", directory / RUNS_DIR
    busy = [p for p in (product, runs) if p.is_dir() and any(p.iterdir())]
    if busy and not force:
        raise WorkspaceError(f"{', '.join(map(str, busy))} not empty; pass --force to reuse")
    if mode not in MODES:
        raise WorkspaceError(f"--mode must be one of {', '.join(MODES)}")
    product.mkdir(parents=True, exist_ok=True)
    runs.mkdir(exist_ok=True)
    source = repo / PRODUCT_TEMPLATE
    for src in sorted(source.rglob("*")) if source.is_dir() else []:
        if not src.is_file() or src.name.startswith("."):
            continue
        dest = product / src.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            dest.write_text(_render(src.read_text(encoding="utf-8"), slug=slug),
                            encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copyfile(src, dest)
    if not any(product.iterdir()):
        (product / "README.md").write_text(
            f"# {slug}\n\nProduct material for the RMF run (see AGENTS.md, INV-7).\n",
            encoding="utf-8")
    return init_run(directory, repo, mode, run_id, as_of=as_of)
