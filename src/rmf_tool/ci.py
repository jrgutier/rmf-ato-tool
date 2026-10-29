"""`rmf ci`: the fast lane plus the checks of every phase in the active profile (§5.0)."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rmf_tool import agents_md, lessons
from rmf_tool.findings import Finding
from rmf_tool.profiles import PHASES, Profile, rule_active

COVERAGE_MIN = 85


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


@dataclass(frozen=True)
class Step:
    name: str
    phase: str | None  # None: fast lane, always run
    rules: tuple[str, ...]
    run: Callable[[Context], tuple[bool, list[Finding], str]]


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


STEPS: tuple[Step, ...] = (
    Step("lessons check", "p1", ("LES-002", "LES-003"),
         lambda ctx: _findings_step(lessons.check(ctx.root))),
    Step("AGENTS.md", "p1", ("DOC-001",),
         lambda ctx: _findings_step(agents_md.check(ctx.root, ctx.cli))),
    Step("ruff", None, (), _ruff),
    Step("pytest", None, (), _pytest),
)


def unimplemented_phases(profile: Profile, steps: tuple[Step, ...] = STEPS) -> list[str]:
    """Phases in the profile that have no checks in this version of the tool."""
    implemented = {s.phase for s in steps if s.phase}
    return [p for p in PHASES if profile.includes(p) and p not in implemented]


def run(profile: Profile, ctx: Context, steps: tuple[Step, ...] = STEPS) -> list[StepResult]:
    results = []
    for step in steps:
        if step.phase is not None and not rule_active(step.phase, profile):
            continue
        ok, findings, output = step.run(ctx)
        results.append(StepResult(step.name, step.rules, ok, findings, output))
    return results
