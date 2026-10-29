"""The `rmf` command line.

Each phase registers its own subcommands here: top-level commands with
``@app.command()`` and command families as sub-apps via ``app.add_typer``
(as ``lessons`` does). Exit codes: 0 OK, 1 violations, 2 usage or I/O error.
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rmf_tool import __version__
from rmf_tool import ci as ci_mod
from rmf_tool import doctor as doctor_mod
from rmf_tool import lessons as lessons_mod
from rmf_tool.findings import Finding, report
from rmf_tool.gitutil import repo_root
from rmf_tool.profiles import PROFILES, ProfileError, resolve

EXIT_OK, EXIT_VIOLATIONS, EXIT_USAGE = 0, 1, 2

app = typer.Typer(
    name="rmf",
    help="Deterministic tooling for the DoD RMF manual and agent simulation template.",
    no_args_is_help=True,
    add_completion=False,
)
lessons_app = typer.Typer(help="Check docs/LESSONS.md.", no_args_is_help=True)
app.add_typer(lessons_app, name="lessons")

console = Console()
err_console = Console(stderr=True)


class OutputFormat(StrEnum):
    text = "text"
    json = "json"


FormatOption = Annotated[
    OutputFormat, typer.Option("--format", help="Output format.", case_sensitive=False)
]


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"rmf {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the version and exit.",
                     callback=_version_callback, is_eager=True),
    ] = False,
) -> None:
    """Deterministic tooling for the DoD RMF manual and agent simulation template."""


def _emit_findings(findings: list[Finding], rules: list[str], fmt: OutputFormat) -> None:
    if fmt is OutputFormat.json:
        typer.echo(json.dumps(report(findings, rules), indent=2))
        return
    for f in findings:
        (err_console if f.severity == "E" else console).print(f.render(), markup=False)
    errors = sum(f.severity == "E" for f in findings)
    warnings = len(findings) - errors
    console.print(f"{', '.join(rules)}: {errors} error(s), {warnings} warning(s)", markup=False)


@app.command()
def doctor(fmt: FormatOption = OutputFormat.text) -> None:
    """Check that required tools are installed (optional extras are reported only)."""
    checks = doctor_mod.run_checks(repo_root())
    failed = any(c.required and not c.ok for c in checks)
    if fmt is OutputFormat.json:
        typer.echo(json.dumps(
            {"ok": not failed, "checks": [c.__dict__ for c in checks]}, indent=2
        ))
    else:
        table = Table(title="rmf doctor")
        for col in ("check", "status", "detail"):
            table.add_column(col)
        for c in checks:
            status = "ok" if c.ok else ("MISSING" if c.required else "absent (optional)")
            table.add_row(c.name, status, c.detail)
        console.print(table)
    raise typer.Exit(EXIT_VIOLATIONS if failed else EXIT_OK)


@app.command()
def ci(
    profile: Annotated[
        str | None,
        typer.Option(help=f"Validation profile: {', '.join(PROFILES)}. "
                          "Default: the closed phases (.phases/*.closed)."),
    ] = None,
    slow: Annotated[bool, typer.Option("--slow", help="Also run slow tests.")] = False,
    release: Annotated[
        bool, typer.Option("--release", help="Same as --profile release --slow.")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Run the fast lane (ruff, pytest) plus every check of the active profile."""
    if release:
        if profile not in (None, "release"):
            err_console.print("--release cannot be combined with --profile", markup=False)
            raise typer.Exit(EXIT_USAGE)
        profile, slow = "release", True
    root = repo_root()
    try:
        active = resolve(root, profile)
    except ProfileError as exc:
        err_console.print(str(exc), markup=False)
        raise typer.Exit(EXIT_USAGE) from exc
    missing = ci_mod.unimplemented_phases(active)
    if missing:
        err_console.print(
            f"profile {active.name} includes phase(s) with no checks in rmf {__version__}: "
            f"{', '.join(missing)}",
            markup=False,
        )
        raise typer.Exit(EXIT_USAGE)

    capture = fmt is OutputFormat.json
    ctx = ci_mod.Context(root, typer.main.get_command(app), slow, capture)
    if not capture:
        phases = ", ".join(sorted(active.phases)) or "none closed"
        console.print(f"rmf ci: profile {active.name} (phases: {phases})", markup=False)
    results = ci_mod.run(active, ctx)
    ok = all(r.ok for r in results)
    if capture:
        typer.echo(json.dumps({
            "profile": active.name,
            "phases": sorted(active.phases),
            "ok": ok,
            "steps": [
                {"name": r.name, "rules": list(r.rules), "ok": r.ok,
                 "findings": report(r.findings, list(r.rules))["findings"], "output": r.output}
                for r in results
            ],
        }, indent=2))
    else:
        for r in results:
            for f in r.findings:
                console.print(f.render(), markup=False)
        for r in results:
            label = f"{r.name} ({', '.join(r.rules)})" if r.rules else r.name
            console.print(f"{'PASS' if r.ok else 'FAIL'}  {label}", markup=False)
    raise typer.Exit(EXIT_OK if ok else EXIT_VIOLATIONS)


@lessons_app.command("check")
def lessons_check(fmt: FormatOption = OutputFormat.text) -> None:
    """LES-002 (format, append-only vs the merge-base) and LES-003 (no pending promotion)."""
    findings = lessons_mod.check(repo_root())
    _emit_findings(findings, ["LES-002", "LES-003"], fmt)
    failed = any(f.severity == "E" for f in findings)
    raise typer.Exit(EXIT_VIOLATIONS if failed else EXIT_OK)
