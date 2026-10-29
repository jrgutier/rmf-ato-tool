"""AGENT-001 (plan §4.4): every agent-lane scenario has a committed, self-attested result
whose ``check.json`` reports 0 errors, whose ``meta.yaml:check_sha256`` matches it, and
whose ``upstream_hash`` equals the scenario's current hash. W under ``rmf ci``, E under
``--release``, skipped under ``--profile fork``."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rmf_tool.findings import Finding
from rmf_tool.run.model import YamlError, read_yaml

RULE = "AGENT-001"
SCENARIOS_DIR = "tests/agent/scenarios"
RESULTS_DIR = "tests/agent/results"


def check(root: Path, severity: str, schemas: Path | None = None) -> list[Finding]:
    """``root`` holds the scenarios and results; ``schemas`` the framework/schema directory's
    repository (default ``root``)."""
    from rmf_tool.workspace import WorkspaceError, load_scenario, scenario_hash

    findings: list[Finding] = []

    def add(message: str, path: str) -> None:
        findings.append(Finding(RULE, severity, message, path))

    for path in sorted((root / SCENARIOS_DIR).glob("*.yaml")):
        rel = path.relative_to(root).as_posix()
        try:
            scenario = load_scenario(schemas or root, path)
        except WorkspaceError as exc:
            add(str(exc), rel)
            continue
        name = scenario["name"]
        result = root / RESULTS_DIR / name
        check_json, meta_yaml = result / "check.json", result / "meta.yaml"
        shown = f"{RESULTS_DIR}/{name}"
        if not check_json.is_file() or not meta_yaml.is_file():
            add(f"no agent-lane result for scenario {name}; run scripts/agent-run.sh {name}",
                shown)
            continue
        raw = check_json.read_bytes()
        try:
            meta = read_yaml(meta_yaml)
            errors = json.loads(raw)["summary"]["errors"]
        except (YamlError, ValueError, KeyError, TypeError) as exc:
            add(f"unreadable result: {exc}", shown)
            continue
        if not isinstance(meta, dict):
            add("meta.yaml is not a mapping", f"{shown}/meta.yaml")
            continue
        if meta.get("check_sha256") != hashlib.sha256(raw).hexdigest():
            add("check.json does not match meta.yaml check_sha256", f"{shown}/check.json")
        if errors != 0:
            add(f"check.json reports {errors} error(s)", f"{shown}/check.json")
        if meta.get("upstream_hash") != scenario_hash(root, scenario):
            add(f"result is stale: upstream files of scenario {name} changed since the run "
                f"(re-run scripts/agent-run.sh {name})", f"{shown}/meta.yaml")
    return findings
