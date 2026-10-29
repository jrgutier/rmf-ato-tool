"""The `rmf` command line.

Each phase registers its own subcommands here: top-level commands with
``@app.command()`` and command families as sub-apps via ``app.add_typer``
(as ``lessons`` does). Exit codes: 0 OK, 1 violations, 2 usage or I/O error.
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from rmf_tool import __version__, refs
from rmf_tool import ci as ci_mod
from rmf_tool import doctor as doctor_mod
from rmf_tool import lessons as lessons_mod
from rmf_tool.findings import Finding, report
from rmf_tool.framework import validate as validate_mod
from rmf_tool.framework.model import FRAMEWORK_DIR
from rmf_tool.gitutil import repo_root
from rmf_tool.profiles import PROFILES, ProfileError, resolve
from rmf_tool.refs import fetch as fetch_mod
from rmf_tool.refs import importer, index_render, show, sync, verify

EXIT_OK, EXIT_VIOLATIONS, EXIT_USAGE = 0, 1, 2

app = typer.Typer(
    name="rmf",
    help="Deterministic tooling for the DoD RMF manual and agent simulation template.",
    no_args_is_help=True,
    add_completion=False,
)
lessons_app = typer.Typer(help="Check docs/LESSONS.md.", no_args_is_help=True)
app.add_typer(lessons_app, name="lessons")
refs_app = typer.Typer(
    help="Fetch, import, verify, extract and index the reference library.", no_args_is_help=True
)
app.add_typer(refs_app, name="refs")

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


@app.command()
def validate(
    profile: Annotated[
        str | None,
        typer.Option(help=f"Validation profile: {', '.join(PROFILES)}. "
                          "Default: the closed phases (.phases/*.closed)."),
    ] = None,
    stats: Annotated[
        bool, typer.Option("--stats", help="Also report entity and citation counts.")
    ] = False,
    root: Annotated[
        Path | None,
        typer.Option("--root", help=f"Framework directory (default: {FRAMEWORK_DIR}/).",
                     file_okay=False),
    ] = None,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Validate the framework YAML: every FW-* rule whose phase is in the profile.

    FW-SCHEMA-001, FW-ID-*, FW-REF-001, FW-ART-001, FW-ORD-001, FW-IO-001, FW-RACI-001,
    FW-DAG-001, FW-CITE-001/002, FW-TASK-001. Citations to pending-acquisition references
    are counted as deferred until p2x.
    """
    repo = repo_root()
    try:
        active = resolve(repo, profile)
    except ProfileError as exc:
        raise _usage_error(str(exc)) from exc
    fw_root = root if root is not None else repo / FRAMEWORK_DIR
    if not fw_root.is_dir():
        raise _usage_error(f"framework directory not found: {fw_root}")
    try:
        result = validate_mod.validate(fw_root, repo, active)
    except validate_mod.UnimplementedRules as exc:
        raise _usage_error(f"profile {active.name}: {exc}") from exc
    except refs.IndexFileError as exc:
        raise _usage_error(str(exc)) from exc
    out = report(result.findings, result.rules_run)
    out["summary"]["deferred_citations"] = result.stats["deferred_citations"]
    if fmt is OutputFormat.json:
        payload = {"profile": active.name, **(result.stats if stats else {}), **out}
        typer.echo(json.dumps(payload, indent=2))
    else:
        for f in result.findings:
            err_console.print(f.render(), markup=False)
        if stats:
            console.print(", ".join(f"{k}: {v}" for k, v in result.stats.items()), markup=False)
        if result.rules_run:
            summary = out["summary"]
            console.print(f"rmf validate ({active.name}): {len(result.rules_run)} rule(s), "
                          f"{summary['errors']} error(s), {summary['warnings']} warning(s), "
                          f"{summary['deferred_citations']} deferred citation(s)", markup=False)
        else:
            console.print(f"rmf validate ({active.name}): no framework rules are active in "
                          f"phases {', '.join(sorted(active.phases)) or 'none'}", markup=False)
    raise typer.Exit(EXIT_OK if result.ok else EXIT_VIOLATIONS)


@lessons_app.command("check")
def lessons_check(fmt: FormatOption = OutputFormat.text) -> None:
    """LES-002 (format, append-only vs the merge-base) and LES-003 (no pending promotion)."""
    findings = lessons_mod.check(repo_root())
    _emit_findings(findings, ["LES-002", "LES-003"], fmt)
    failed = any(f.severity == "E" for f in findings)
    raise typer.Exit(EXIT_VIOLATIONS if failed else EXIT_OK)


# --- rmf refs ------------------------------------------------------------------------


class Extractor(StrEnum):
    pymupdf = "pymupdf"
    pdfplumber = "pdfplumber"


IdsOption = Annotated[
    list[str] | None, typer.Option("--id", help="Limit to this reference ID (repeatable).")
]


def _usage_error(message: str) -> typer.Exit:
    err_console.print(message, markup=False)
    return typer.Exit(EXIT_USAGE)


def _index(root: Path) -> Any:
    try:
        return refs.load_index(root)
    except refs.IndexFileError as exc:
        raise _usage_error(str(exc)) from exc


def _exit_findings(findings: list[Finding], rules: list[str], fmt: OutputFormat) -> None:
    _emit_findings(findings, rules, fmt)
    raise typer.Exit(EXIT_VIOLATIONS if any(f.severity == "E" for f in findings) else EXIT_OK)


def _emit_fetch(results: list[fetch_mod.Result], fmt: OutputFormat) -> None:
    if fmt is OutputFormat.json:
        typer.echo(json.dumps({
            "ok": not any(r.failed for r in results),
            "results": [{"id": r.id, "status": r.status, "message": r.message} for r in results],
        }, indent=2))
        return
    for r in results:
        line = f"{r.status:<16} {r.id}" + (f"  {r.message}" if r.message else "")
        (err_console if r.failed else console).print(line, markup=False)


@refs_app.command("fetch")
def refs_fetch(
    ids: IdsOption = None,
    accept_new: Annotated[
        bool, typer.Option("--accept-new", help="Replace a pinned file whose upstream changed.")
    ] = False,
    note: Annotated[
        str | None, typer.Option(help="Revision note recorded with --accept-new (required).")
    ] = None,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Download auto references and pin their SHA-256.

    Ranged-GET probe, allowed domains on every redirect hop, %PDF- + qpdf --check.
    Browser-assisted entries are skipped.
    """
    if accept_new and not note:
        raise _usage_error("--accept-new requires --note")
    root = repo_root()
    _index(root)
    try:
        results = fetch_mod.fetch(root, ids, accept_new=accept_new, note=note)
    except KeyError as exc:
        raise _usage_error(str(exc.args[0])) from exc
    _emit_fetch(results, fmt)
    raise typer.Exit(EXIT_VIOLATIONS if any(r.failed for r in results) else EXIT_OK)


@refs_app.command("import")
def refs_import(
    ref_id: Annotated[str, typer.Argument(metavar="ID", help="Reference ID in index.yaml.")],
    path: Annotated[Path, typer.Argument(help="The downloaded PDF (e.g. in references/_inbox/).")],
    url: Annotated[
        str | None, typer.Option(help="The URL the file was downloaded from (recorded).")
    ] = None,
) -> None:
    """Import a PDF downloaded by hand (browser-assisted).

    Checks %PDF- and qpdf, moves it into references/pdf/ (Git LFS), pins its SHA-256
    and marks the entry ok.
    """
    root = repo_root()
    _index(root)
    try:
        entry = importer.import_ref(root, ref_id, path, url=url)
    except importer.ImportRejected as exc:
        err_console.print(f"rejected: {exc}", markup=False)
        raise typer.Exit(EXIT_VIOLATIONS) from exc
    console.print(f"imported {ref_id}: {entry['size_bytes']} bytes, sha256 {entry['sha256']}\n"
                  f"next: uv run rmf refs verify --id {ref_id} && uv run rmf refs sync",
                  markup=False)


@refs_app.command("verify")
def refs_verify(
    required: Annotated[
        bool, typer.Option("--required", help="Only required references; every one must be ok "
                                              "(REF-001 is an error for pending-acquisition).")
    ] = False,
    ids: IdsOption = None,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Verify the reference library offline (REF-001/002/005/006).

    REF-001 status, REF-002 SHA-256 (or LFS pointer oid), REF-005 OSCAL pins,
    REF-006 allowed domains.
    """
    root = repo_root()
    findings = verify.verify(root, _index(root), strict=required, required_only=required,
                             ids=ids)
    _exit_findings(findings, list(verify.VERIFY_RULES), fmt)


@refs_app.command("extract")
def refs_extract(
    ids: IdsOption = None,
    extractor: Annotated[
        Extractor, typer.Option(help="PDF extractor (both need the [extract] extra).")
    ] = Extractor.pymupdf,
    ocr: Annotated[bool, typer.Option("--ocr", help="OCR image-only pages (opt-in).")] = False,
    check: Annotated[
        bool, typer.Option("--check", help="REF-003: verify the committed text; write nothing.")
    ] = False,
    full: Annotated[
        bool, typer.Option("--full", help="Re-extract even when current; with --check, "
                                          "re-extract to a temp dir and compare bytes.")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Extract reference PDFs to references/text/ and record them in index.yaml.

    Writes <ID>.md and <ID>.toc.yaml. PDFs whose extraction is current are skipped.
    """
    from rmf_tool.refs.extract import ExtractorUnavailable

    root = repo_root()
    index = _index(root)
    try:
        if check:
            findings = verify.check_texts(root, index, ids)
            if full:
                findings += sync.full_check(root, index, ids)
            _exit_findings(findings, ["REF-003"], fmt)
        results = sync.extract_all(root, ids, extractor=extractor.value, ocr=ocr, full=full)
    except ExtractorUnavailable as exc:
        raise _usage_error(str(exc)) from exc
    except KeyError as exc:
        raise _usage_error(str(exc.args[0])) from exc
    if fmt is OutputFormat.json:
        typer.echo(json.dumps({"results": [r.__dict__ for r in results]}, indent=2))
    else:
        for r in results:
            console.print(f"{r.status:<10} {r.id} ({r.pages} pages)", markup=False)


@refs_app.command("index")
def refs_index(
    check: Annotated[
        bool, typer.Option("--check", help="REF-004: fail if INDEX.md is stale; write nothing.")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Render references/INDEX.md from references/index.yaml."""
    root = repo_root()
    index = _index(root)
    if check:
        _exit_findings(index_render.check(root, index), ["REF-004"], fmt)
    wrote = index_render.write(root, index)
    console.print(f"{index_render.INDEX_MD} {'written' if wrote else 'unchanged'}", markup=False)


@refs_app.command("sync")
def refs_sync(fmt: FormatOption = OutputFormat.text) -> None:
    """Fetch missing references, extract stale text, render INDEX.md, verify.

    REF-001 is a warning for pending-acquisition entries.
    """
    from rmf_tool.refs.extract import ExtractorUnavailable

    root = repo_root()
    _index(root)
    results = fetch_mod.fetch(root, missing_only=True)
    if fmt is OutputFormat.text:
        _emit_fetch([r for r in results if r.status not in ("unchanged", "skipped")], fmt)
    try:
        extracted = sync.extract_all(root)
    except ExtractorUnavailable as exc:
        raise _usage_error(str(exc)) from exc
    if fmt is OutputFormat.text:
        for r in extracted:
            if r.status == "extracted":
                console.print(f"extracted  {r.id} ({r.pages} pages)", markup=False)
    index = _index(root)
    index_render.write(root, index)
    findings = verify.verify(root, index) + verify.check_texts(root, index) \
        + index_render.check(root, index)
    findings += [Finding("REF-001", "E", f"{r.id}: fetch {r.status}: {r.message}")
                 for r in results if r.failed]
    _exit_findings(findings, [*verify.VERIFY_RULES, "REF-003", "REF-004"], fmt)


@refs_app.command("show")
def refs_show(
    ref_id: Annotated[str, typer.Argument(metavar="ID", help="Reference ID in index.yaml.")],
    section: Annotated[
        str | None, typer.Option(help="Section number, title or heading anchor.")
    ] = None,
    page: Annotated[int | None, typer.Option(help="Physical page number (1-based).")] = None,
    anchor: Annotated[
        str | None, typer.Option(help="Text on the page (or a heading anchor); needs --page.")
    ] = None,
) -> None:
    """Print a cited passage from the committed text extraction."""
    if (section is None) == (page is None) or (page is not None) != (anchor is not None):
        raise _usage_error("give either --section S or --page N --anchor A")
    root = repo_root()
    entry = refs.find(_index(root), ref_id)
    if entry is None:
        raise _usage_error(f"unknown reference id {ref_id!r}")
    try:
        if section is not None:
            text = show.section(root, entry, section)
        else:
            assert page is not None and anchor is not None
            text = show.page(root, entry, page, anchor)
    except show.NotFound as exc:
        err_console.print(str(exc), markup=False)
        raise typer.Exit(EXIT_VIOLATIONS) from exc
    typer.echo(text, nl=False)
