"""`rmf ci`: the fast lane plus the checks of every phase in the active profile (§5.0)."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from rmf_tool import agents_md, doc_counts, lessons, playbooks_sync, refs
from rmf_tool.check import agent_lane, load_registry
from rmf_tool.findings import Finding
from rmf_tool.framework import validate as framework_validate
from rmf_tool.framework.model import FRAMEWORK_DIR, META_FILE
from rmf_tool.profiles import PHASES, Profile, rule_active
from rmf_tool.refs import currency, index_render, verify
from rmf_tool.render import manual
from rmf_tool.run.model import RUN_FILE, read_yaml

COVERAGE_MIN = 85
MIN_WORKER_CPUS = 4
VALID_MINIMAL = "tests/fixtures/runs/valid_minimal"
HYBRID_MINIMAL = "tests/fixtures/runs/hybrid_minimal"
EXAMPLE_RUN = "examples/uas-gcs/runs/example-synthetic-01"
GOLDEN_OSCAL = "tests/golden/oscal"


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
    tests: bool = True  # False: every check but pytest (`rmf ci --no-tests`)


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
    if ctx.profile is None or ctx.profile.name != "release":
        marker += " and not release"
    # Workers repeat module fixtures, so below MIN_WORKER_CPUS they cost more than they save: a
    # 2-core runner took 65 minutes with them and 49 in series. An environment synced without
    # xdist, a dev dependency, also runs in series.
    parallel = importlib.util.find_spec("xdist") and (os.cpu_count() or 1) >= MIN_WORKER_CPUS
    workers = ["-n", "auto"] if parallel else []
    argv = [sys.executable, "-m", "pytest", "-q", *workers, "-m", marker,
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


def _valid_minimal(rules: tuple[str, ...] | None = None,
                   fixture: str = VALID_MINIMAL) -> Callable[[Context], Any]:
    """`rmf check --final` on a fixture run, optionally limited to some rules."""
    def run(ctx: Context) -> tuple[bool, list[Finding], str]:
        from rmf_tool.check import engine
        from rmf_tool.run.model import RunError, open_run

        try:
            r = open_run(ctx.root / fixture, ctx.root)
        except RunError as exc:
            return _findings_step([Finding("RUN-CFG-001", "E", str(exc), fixture)])
        found = engine.select(r, engine.evaluate(r), rules=list(rules) if rules else None,
                              final=True)
        return _findings_step([replace(f, path=f"{fixture}/{f.path}" if f.path
                                       else fixture) for f in found])
    return run


def _contracts(ctx: Context) -> tuple[bool, list[Finding], str]:
    """The fixtures live on the current contract, and at release so does the example, so the
    p14 re-run cannot be skipped behind a warning."""
    assert ctx.profile is not None
    current = str(read_yaml(ctx.root / FRAMEWORK_DIR / META_FILE)["framework_version"])
    runs = [VALID_MINIMAL, HYBRID_MINIMAL]
    if ctx.profile.name == "release":
        runs.append(EXAMPLE_RUN)
    stale = [(r, read_yaml(ctx.root / r / RUN_FILE).get("framework_version")) for r in runs]
    return _findings_step([Finding("RUN-VER-001", "E", f"on contract {v}, not {current}", r)
                           for r, v in stale if str(v) != current])


def _example(ctx: Context) -> tuple[bool, list[Finding], str]:
    """The example fork run (p7); a fork's own profile does not evaluate examples/."""
    assert ctx.profile is not None
    if not ctx.profile.examples:
        return True, [], f"{EXAMPLE_RUN} skipped ({ctx.profile.name} profile)"
    if not (ctx.root / EXAMPLE_RUN / "run.yaml").is_file():
        return _findings_step([Finding("RUN-CFG-001", "E", "the example run is missing",
                                       EXAMPLE_RUN)])
    return _valid_minimal(fixture=EXAMPLE_RUN)(ctx)


def _golden_oscal(ctx: Context) -> tuple[bool, list[Finding], str]:
    from rmf_tool.oscal import validate as oscal_validate

    base = ctx.root / GOLDEN_OSCAL
    paths = sorted(base.glob("*.json"))
    found = [Finding("OSCAL-001", "E", m, f"{GOLDEN_OSCAL}/{rel}")
             for rel, m in oscal_validate.schema_problems_in(ctx.root, base, paths)]
    found += [Finding("OSCAL-002", "E", m, f"{GOLDEN_OSCAL}/{rel}")
              for rel, m in oscal_validate.trestle_problems_in(base, paths)]
    if not paths:
        found.append(Finding("OSCAL-001", "E", "no golden OSCAL documents", GOLDEN_OSCAL))
    return _findings_step(found)


def _checks_doc(ctx: Context) -> tuple[bool, list[Finding], str]:
    from rmf_tool import checks_doc

    if checks_doc.stale(ctx.root):
        return False, [], f"{checks_doc.CHECKS_PATH} is stale; run `rmf checks-doc`"
    return True, [], ""


def _agent_lane(ctx: Context) -> tuple[bool, list[Finding], str]:
    assert ctx.profile is not None
    if ctx.profile.agent_severity is None:  # --profile fork
        return True, [], "AGENT-001 skipped (fork profile)"
    return _findings_step(agent_lane.check(ctx.root, ctx.profile.agent_severity))


SKELETON_RULES = ("RUN-CFG-001", "RUN-FM-001", "RUN-ART-001", "FACTS-001", "GEN-STALE-001",
                  "SSP-COV-001", "SAR-POAM-001", "TRACE-001", "TRACE-002", "HYB-001", "HYB-002",
                  "OSCAL-001", "OSCAL-002", "JOURNAL-001")

RUN_RULES = tuple(r.id for r in load_registry() if r.scope == "run")

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
    # From p5 on, `rmf validate` also runs FW-PB-001/002 and FW-PER-001/002, so the p5 step
    # replaces the p3a step and the p35 playbook step (each finding is reported once).
    # p3b (prose enrichment) is verified by the same `rmf validate`, now with p2x closed, so
    # every citation must resolve. Each validate step stands down for the next one.
    Step("rmf validate", "p3a", framework_validate.IMPLEMENTED, _framework, unless="p3b"),
    Step("rmf validate (p3b, all citations resolvable)", "p3b", framework_validate.IMPLEMENTED,
         _framework, unless="p5"),
    Step("rmf check --final valid_minimal", "p35", SKELETON_RULES,
         _valid_minimal(SKELETON_RULES), unless="p6"),
    Step("rmf oscal validate valid_minimal", "p35", ("OSCAL-001", "OSCAL-002"),
         _valid_minimal(("OSCAL-001", "OSCAL-002"))),
    Step("rmf playbooks sync --check", "p35", ("FW-PB-002",),
         lambda ctx: _findings_step(playbooks_sync.check(ctx.root)), unless="p5"),
    Step("agent lane", "p35", ("AGENT-001",), _agent_lane),
    Step("rmf render --check", "p4", (manual.RULE,),
         lambda ctx: _findings_step(manual.check(ctx.root))),
    Step("rmf validate (playbooks, persona cards)", "p5", framework_validate.IMPLEMENTED,
         _framework, unless="p10"),
    # p6: every run rule on both fixture runs (the p35 step above then stands down).
    Step("rmf check --final valid_minimal (all run rules)", "p6", RUN_RULES, _valid_minimal()),
    Step("rmf check --final hybrid_minimal", "p6", RUN_RULES,
         _valid_minimal(fixture=HYBRID_MINIMAL)),
    Step("rmf checks-doc --check", "p6", (), _checks_doc),
    Step("rmf oscal validate tests/golden/oscal", "p6", ("OSCAL-001", "OSCAL-002"),
         _golden_oscal),
    # p7: the example fork's synthetic run, every run rule (OSCAL and staleness included).
    Step(f"rmf check --final {EXAMPLE_RUN}", "p7", RUN_RULES, _example),
    # p8: documented counts equal computed values.
    Step("documented counts", "p8", (doc_counts.RULE,),
         lambda ctx: _findings_step(doc_counts.check(ctx.root))),
    # p9: reference currency (FW-CITE-003 runs in the rmf validate steps above).
    Step("refs currency", "p9", currency.RULES, _refs_step(currency.check)),
    # p10: the register and the NIST task pin, FW-REQ-* and FW-TASK-002 in `rmf validate`, so
    # this step replaces the p5 one.
    Step("rmf validate (requirements register, NIST task pin)", "p10",
         framework_validate.IMPLEMENTED, _framework),
    # p11: run contracts; a run is held to the contract it was created under.
    Step("run contracts", "p11", ("RUN-VER-001",), _contracts),
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
        if step.run is _pytest and not ctx.tests:
            continue
        ok, findings, output = step.run(ctx)
        results.append(StepResult(step.name, step.rules, ok, findings, output))
    return results
