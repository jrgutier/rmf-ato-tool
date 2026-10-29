"""`rmf ci`: the fast lane plus the checks of every phase in the active profile (§5.0)."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from rmf_tool import agents_md, lessons, playbooks_sync, refs
from rmf_tool.check import agent_lane
from rmf_tool.findings import Finding
from rmf_tool.framework import validate as framework_validate
from rmf_tool.framework.model import FRAMEWORK_DIR
from rmf_tool.profiles import PHASES, Profile, rule_active
from rmf_tool.refs import index_render, verify

COVERAGE_MIN = 85
VALID_MINIMAL = "tests/fixtures/runs/valid_minimal"


@dataclass
class StepResult:
    name: str
    rules: tuple[str, ...]
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    output: str = ""


@dataclass(frozen=True)
class Context:
    root: Path
    cli: Any  # typer.main.get_command(app)
    slow: bool
    capture: bool  # capture subprocess output (json) instead of streaming it (text)
    profile: Profile | None = None  # set by run()


@dataclass(frozen=True)
class Step:
    name: str
    phase: str | None  # None: fast lane, always run
    rules: tuple[str, ...]
    run: Callable[[Context], tuple[bool, list[Finding], str]]
    unless: str | None = None  # skipped when the profile includes this phase


def run_subprocess(argv: list[str], ctx: Context) -> tuple[bool, list[Finding], str]:
    if ctx.capture:
        proc = subprocess.run(argv, cwd=ctx.root, capture_output=True, text=True, check=False)
        return proc.returncode == 0, [], proc.stdout + proc.stderr
    proc = subprocess.run(argv, cwd=ctx.root, check=False)
    return proc.returncode == 0, [], ""


def _ruff(ctx: Context) -> tuple[bool, list[Finding], str]:
    return run_subprocess([sys.executable, "-m", "ruff", "check", "."], ctx)


def _pytest(ctx: Context) -> tuple[bool, list[Finding], str]:
    marker = "not network and not agent" if ctx.slow else "not slow and not network and not agent"
    argv = [sys.executable, "-m", "pytest", "-q", "-m", marker,
            "--cov=rmf_tool", f"--cov-fail-under={COVERAGE_MIN}"]
    return run_subprocess(argv, ctx)


def _findings_step(findings: list[Finding]) -> tuple[bool, list[Finding], str]:
    return not any(f.severity == "E" for f in findings), findings, ""


def _refs_step(check: Callable[[Path, Any], list[Finding]]) -> Callable[[Context], Any]:
    """A step over references/index.yaml; an unreadable index is a REF-001 error."""
    def run(ctx: Context) -> tuple[bool, list[Finding], str]:
        try:
            index = refs.load_index(ctx.root)
        except refs.IndexFileError as exc:
            return _findings_step([Finding("REF-001", "E", str(exc), refs.INDEX_PATH)])
        return _findings_step(check(ctx.root, index))
    return run


def _framework(ctx: Context) -> tuple[bool, list[Finding], str]:
    """`rmf validate` on framework/ under the active profile."""
    assert ctx.profile is not None
    try:
        result = framework_validate.validate(ctx.root / FRAMEWORK_DIR, ctx.root, ctx.profile)
    except refs.IndexFileError as exc:
        return _findings_step([Finding("FW-CITE-001", "E", str(exc), refs.INDEX_PATH)])
    return _findings_step(result.findings)


def _valid_minimal(rules: tuple[str, ...] | None = None) -> Callable[[Context], Any]:
    """`rmf check --final` on the skeleton fixture, optionally limited to some rules."""
    def run(ctx: Context) -> tuple[bool, list[Finding], str]:
        from rmf_tool.check import engine
        from rmf_tool.run.model import RunError, open_run

        try:
            r = open_run(ctx.root / VALID_MINIMAL, ctx.root)
        except RunError as exc:
            return _findings_step([Finding("RUN-CFG-001", "E", str(exc), VALID_MINIMAL)])
        found = engine.select(r, engine.evaluate(r), rules=list(rules) if rules else None,
                              final=True)
        return _findings_step([replace(f, path=f"{VALID_MINIMAL}/{f.path}" if f.path
                                       else VALID_MINIMAL) for f in found])
    return run


def _agent_lane(ctx: Context) -> tuple[bool, list[Finding], str]:
    assert ctx.profile is not None
    if ctx.profile.agent_severity is None:  # --profile fork
        return True, [], "AGENT-001 skipped (fork profile)"
    return _findings_step(agent_lane.check(ctx.root, ctx.profile.agent_severity))


SKELETON_RULES = ("RUN-CFG-001", "RUN-FM-001", "RUN-ART-001", "FACTS-001", "GEN-STALE-001",
                  "SSP-COV-001", "SAR-POAM-001", "TRACE-001", "TRACE-002", "HYB-001", "HYB-002",
                  "OSCAL-001", "OSCAL-002", "JOURNAL-001")

STEPS: tuple[Step, ...] = (
    Step("lessons check", "p1", ("LES-002", "LES-003"),
         lambda ctx: _findings_step(lessons.check(ctx.root))),
    Step("AGENTS.md", "p1", ("DOC-001",),
         lambda ctx: _findings_step(agents_md.check(ctx.root, ctx.cli))),
    # p2: REF-001 warns for pending-acquisition; p2x (the exit gate) makes it an error.
    Step("refs verify", "p2", verify.VERIFY_RULES,
         _refs_step(lambda root, index: verify.verify(root, index)), unless="p2x"),
    Step("refs verify (strict)", "p2x", verify.VERIFY_RULES,
         _refs_step(lambda root, index: verify.verify(root, index, strict=True))),
    Step("refs extract --check", "p2", ("REF-003",), _refs_step(verify.check_texts)),
    Step("refs index --check", "p2", ("REF-004",), _refs_step(index_render.check)),
    Step("rmf validate", "p3a", framework_validate.IMPLEMENTED, _framework),
    Step("rmf check --final valid_minimal", "p35", SKELETON_RULES, _valid_minimal()),
    Step("rmf oscal validate valid_minimal", "p35", ("OSCAL-001", "OSCAL-002"),
         _valid_minimal(("OSCAL-001", "OSCAL-002"))),
    Step("rmf playbooks sync --check", "p35", ("FW-PB-002",),
         lambda ctx: _findings_step(playbooks_sync.check(ctx.root))),
    Step("agent lane", "p35", ("AGENT-001",), _agent_lane),
    Step("ruff", None, (), _ruff),
    Step("pytest", None, (), _pytest),
)


def unimplemented_phases(profile: Profile, steps: tuple[Step, ...] = STEPS) -> list[str]:
    """Phases in the profile that have no checks in this version of the tool."""
    implemented = {s.phase for s in steps if s.phase}
    return [p for p in PHASES if profile.includes(p) and p not in implemented]


def run(profile: Profile, ctx: Context, steps: tuple[Step, ...] = STEPS) -> list[StepResult]:
    ctx = replace(ctx, profile=profile)
    results = []
    for step in steps:
        if step.phase is not None and not rule_active(step.phase, profile):
            continue
        if step.unless is not None and profile.includes(step.unless):
            continue
        ok, findings, output = step.run(ctx)
        results.append(StepResult(step.name, step.rules, ok, findings, output))
    return results
