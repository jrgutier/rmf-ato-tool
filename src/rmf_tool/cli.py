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

console = Console(soft_wrap=True)  # never wrap lines agents parse (L-0022)
err_console = Console(stderr=True, soft_wrap=True)


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


# --- workspaces and runs ---------------------------------------------------------------

run_app = typer.Typer(help="Start runs.", no_args_is_help=True)
app.add_typer(run_app, name="run")
baseline_app = typer.Typer(help="Resolve the run's control baseline.", no_args_is_help=True)
app.add_typer(baseline_app, name="baseline")
catalog_app = typer.Typer(help="Read the NIST SP 800-53r5 catalog.", no_args_is_help=True)
app.add_typer(catalog_app, name="catalog")
oscal_app = typer.Typer(help="Build and validate a run's OSCAL documents.", no_args_is_help=True)
app.add_typer(oscal_app, name="oscal")
playbooks_app = typer.Typer(help="Keep playbook headers in sync with framework/.",
                            no_args_is_help=True)
app.add_typer(playbooks_app, name="playbooks")

RunArg = Annotated[
    Path | None,
    typer.Argument(metavar="[RUN]", help="Run directory (default: the cwd if it holds run.yaml, "
                                         "else the newest runs/*/).", show_default=False),
]
ModeOption = Annotated[str, typer.Option(help="synthetic or hybrid.")]
RunIdOption = Annotated[
    str | None, typer.Option("--run-id", help="Run ID (default YYYYMMDD-<mode>-NN).")
]


def _open(run: Path | None) -> Any:
    from rmf_tool.run.model import RunError, open_run

    try:
        return open_run(run)
    except RunError as exc:
        raise _usage_error(str(exc)) from exc


@app.command("new")
def new(
    slug: Annotated[str, typer.Argument(help="Short product name (lowercase, digits, -).")],
    directory: Annotated[
        Path | None, typer.Option("--dir", help="Workspace directory (default: ./<slug>).",
                                  file_okay=False, show_default=False)
    ] = None,
    mode: ModeOption = "synthetic",
    run_id: RunIdOption = None,
    force: Annotated[
        bool, typer.Option("--force", help="Reuse a non-empty product/ or runs/.")
    ] = False,
) -> None:
    """Scaffold a workspace (product/ from templates, runs/) and start its first run."""
    from rmf_tool.workspace import WorkspaceError, new_workspace

    target = directory if directory is not None else Path(slug)
    try:
        run_dir = new_workspace(target, slug, repo_root(), mode, run_id, force)
    except WorkspaceError as exc:
        raise _usage_error(str(exc)) from exc
    typer.echo(f"created {target / 'product'} and run {run_dir}\n"
                  f"next: fill in product/, then uv run rmf status {run_dir}")


@run_app.command("init")
def run_init(
    mode: ModeOption = "synthetic",
    run_id: RunIdOption = None,
    scenario: Annotated[
        Path | None, typer.Option(help="Agent-lane scenario (tests/agent/scenarios/<s>.yaml): "
                                       "product, scope, seeds, control subset.", dir_okay=False)
    ] = None,
) -> None:
    """Start a run in ./runs/<run-id>/ and stamp run.yaml (upstream_hash, versions)."""
    from rmf_tool.workspace import WorkspaceError, init_run

    try:
        run_dir = init_run(Path.cwd(), repo_root(), mode, run_id, scenario)
    except WorkspaceError as exc:
        raise _usage_error(str(exc)) from exc
    typer.echo(f"created {run_dir}\nnext: uv run rmf status {run_dir}")


@app.command()
def status(
    run: RunArg = None,
    family_gaps: Annotated[
        bool, typer.Option("--family-gaps", help="List baseline controls without SSP "
                                                 "statements or SAR determinations, per family.")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Task completion derived from disk and the next action (plan §7.3)."""
    from rmf_tool.run import status as status_mod

    r = _open(run)
    st = status_mod.compute(r)
    data = status_mod.to_json(r, st, family_gaps)
    if fmt is OutputFormat.json:
        typer.echo(json.dumps(data, indent=2))
        raise typer.Exit(EXIT_OK)
    c = data["counts"]
    typer.echo(f"now: {data['now']}")
    typer.echo(f"run {st.run_id} ({st.mode}): {c['done']}/{c['active']} active task(s) done, "
               f"{c['deferred']} deferred; SSP {st.statements}/{st.baseline} statements")
    for t in data["tasks"]:
        if t["state"] != "active":
            continue
        mark = "done" if t["done"] else "todo"
        detail = "" if t["done"] else "  (" + "; ".join(t["missing"]) + ")"
        typer.echo(f"  {mark:<5}{t['id']:<6}{t['name']}{detail}")
    for fam, gaps in (data.get("family_gaps") or {}).items():
        typer.echo(f"  gaps {fam}: ssp {', '.join(gaps['ssp']) or '-'}; "
                      f"sar {', '.join(gaps['sar']) or '-'}")
    if st.next is None:
        typer.echo("next: none, every active task is done (rmf check --final)")
    else:
        nxt = data["next"]
        fam = f" family {nxt['family']}" if nxt.get("family") else ""
        typer.echo(f"next: {st.next} {nxt['name']}{fam} ({nxt['playbook']})")
    raise typer.Exit(EXIT_OK)


@baseline_app.command("resolve")
def baseline_resolve(run: RunArg = None) -> None:
    """Write baseline.json from facts.yaml (approved categorization), tailoring and subset."""
    from rmf_tool import baseline as baseline_mod

    r = _open(run)
    try:
        data = baseline_mod.resolve(r)
    except baseline_mod.BaselineError as exc:
        typer.echo(f"cannot resolve: {exc}", err=True)
        raise typer.Exit(EXIT_VIOLATIONS) from exc
    r.path("baseline.json").write_text(baseline_mod.render(data), encoding="utf-8")
    typer.echo(f"baseline.json: {data['baseline_id']}, {len(data['controls'])} control(s); "
               f"set facts.yaml baseline_id to {data['baseline_id']!r}")
    typer.echo("note: selection is the SP 800-53B high-water mark (method: high-water-mark); "
               "CNSSI 1253 per-objective selection is pending (Phase 6). Do not call this "
               "the CNSSI 1253 baseline.")


@catalog_app.command("show")
def catalog_show(
    family: Annotated[str | None, typer.Option(help="Control family (ac, AU, ...).")] = None,
    control: Annotated[
        list[str] | None, typer.Option(help="Control ID (ac-2, ac-2.1); repeatable.")
    ] = None,
    run: Annotated[
        Path | None, typer.Option(help="Limit to the run's baseline.json controls.")
    ] = None,
    missing: Annotated[
        bool, typer.Option("--missing", help="With --run: only controls without an SSP "
                                             "statement.")
    ] = False,
    fields: Annotated[
        str, typer.Option(help="Comma list of title, statement, guidance, objectives, params.")
    ] = "title,statement",
    chunk: Annotated[str | None, typer.Option(help="i/n: the i-th of n slices.")] = None,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Compact control text from the catalog (raw OSCAL JSON), for family-sized batches."""
    from rmf_tool import catalog as catalog_mod
    from rmf_tool.run import status as status_mod

    chosen = tuple(f.strip() for f in fields.split(",") if f.strip())
    bad = [f for f in chosen if f not in catalog_mod.FIELDS]
    if bad:
        raise _usage_error(f"unknown field(s) {', '.join(bad)}; "
                           f"expected {', '.join(catalog_mod.FIELDS)}")
    if missing and run is None:
        raise _usage_error("--missing needs --run")
    cat = catalog_mod.load(repo_root())
    if run is not None:
        from rmf_tool import baseline as baseline_mod

        r = _open(run)
        ids = baseline_mod.control_ids(r)
        if missing:
            gaps = status_mod.family_gaps(r)
            ids = [c for c in ids if c in gaps.get(catalog_mod.family(c), {}).get("ssp", [])]
    elif family is None and not control:
        raise _usage_error("give --family, --control or --run")
    else:
        ids = list(cat.order)
    if family is not None:
        ids = [c for c in ids if catalog_mod.family(c) == family.lower()]
    if control:
        wanted = {c.lower() for c in control}
        unknown = sorted(wanted - set(cat.controls))
        if unknown:
            raise _usage_error(f"unknown control(s) {', '.join(unknown)}")
        ids = [c for c in ids if c in wanted]
    if chunk is not None:
        try:
            ids = catalog_mod.chunk(ids, chunk)
        except ValueError as exc:
            raise _usage_error(str(exc)) from exc
    views = [catalog_mod.view(cat, c, chosen) for c in ids]
    if fmt is OutputFormat.json:
        typer.echo(json.dumps({"controls": views}, indent=2))
    else:
        for v in views:
            typer.echo(catalog_mod.render_text(v))
        typer.echo(f"{len(views)} control(s)")


def _changed(paths: list[str], verb: str) -> None:
    for p in paths:
        typer.echo(f"{verb} {p}")


@app.command()
def assemble(
    run: RunArg = None,
    check: Annotated[
        bool, typer.Option("--check", help="Fail if any marker block is stale; write nothing.")
    ] = False,
) -> None:
    """Fill the CLI-owned marker blocks (rmf:facts) in the run's artifact Markdown."""
    from rmf_tool import assemble as assemble_mod

    r = _open(run)
    try:
        if check:
            stale = [rel for rel, (old, new) in assemble_mod.assembled(r).items() if old != new]
            _changed(stale, "stale")
            raise typer.Exit(EXIT_VIOLATIONS if stale else EXIT_OK)
        _changed(assemble_mod.write(r), "assembled")
    except assemble_mod.AssembleError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(EXIT_VIOLATIONS) from exc


@oscal_app.command("build")
def oscal_build(
    run: RunArg = None,
    check: Annotated[
        bool, typer.Option("--check", help="Fail if oscal/ differs from a fresh build.")
    ] = False,
) -> None:
    """Build oscal/profile.json and oscal/ssp.json (trestle models, uuid5, OSCAL 1.2.1)."""
    from rmf_tool import build as build_mod

    r = _open(run)
    out = build_mod.oscal_outputs(r)
    stale = []
    for rel, text in out.files.items():
        path = r.path(rel)
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != text:
            stale.append(rel)
            if not check:
                build_mod.write_output(r, rel, text)
        if rel in out.notes:
            typer.echo(f"not built {rel}: {out.notes[rel]}")
    _changed(stale, "stale" if check else "wrote")
    raise typer.Exit(EXIT_VIOLATIONS if check and stale else EXIT_OK)


@oscal_app.command("validate")
def oscal_validate(run: RunArg = None, fmt: FormatOption = OutputFormat.text) -> None:
    """OSCAL-001 (NIST v1.2.1 schema, regex + FormatChecker) and OSCAL-002 (trestle load)."""
    from rmf_tool.oscal import validate as validate_oscal

    r = _open(run)
    findings = [Finding("OSCAL-001", "E", m, rel) for rel, m in validate_oscal.schema_problems(r)]
    findings += [Finding("OSCAL-002", "E", m, rel)
                 for rel, m in validate_oscal.trestle_problems(r)]
    if not validate_oscal.files(r):
        typer.echo("no oscal/*.json yet (rmf build)")
    _exit_findings(findings, ["OSCAL-001", "OSCAL-002"], fmt)


@app.command()
def build(run: RunArg = None) -> None:
    """Assemble artifact Markdown, build OSCAL, render reports/assumptions.md and refresh
    package/manifest.yaml when present. Run it before every `rmf check` (INV-6)."""
    from rmf_tool import assemble as assemble_mod
    from rmf_tool import build as build_mod

    r = _open(run)
    try:
        changed, notes = build_mod.build(r)
    except assemble_mod.AssembleError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(EXIT_VIOLATIONS) from exc
    _changed(changed, "wrote")
    for rel, why in notes.items():
        typer.echo(f"not built {rel}: {why}")
    typer.echo(f"rmf build: {len(changed)} file(s) changed")


@app.command()
def package(run: RunArg = None) -> None:
    """Write package/manifest.yaml (ART-PKG): artifacts, OSCAL and reports with SHA-256."""
    from rmf_tool import package as package_mod

    r = _open(run)
    wrote = package_mod.write(r)
    typer.echo(f"package/manifest.yaml {'written' if wrote else 'unchanged'}")


@app.command()
def check(
    run: RunArg = None,
    task: Annotated[
        str | None, typer.Option(help="Only rules applying at this task and its findings.")
    ] = None,
    family: Annotated[str | None, typer.Option(help="Only findings of this family.")] = None,
    rules: Annotated[str | None, typer.Option(help="Comma list of rule IDs.")] = None,
    final: Annotated[
        bool, typer.Option("--final", help="Every rule, regardless of progress (scope-aware).")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Run-scope rules (RUN-*, FACTS, GEN-STALE, SSP-COV, SAR-POAM, TRACE, HYB, OSCAL,
    JOURNAL) on a run."""
    from rmf_tool.check import engine

    r = _open(run)
    wanted = [x.strip() for x in rules.split(",") if x.strip()] if rules else None
    unknown = [x for x in wanted or [] if x not in engine.IMPLEMENTED]
    if unknown:
        raise _usage_error(f"unknown or unimplemented rule(s): {', '.join(unknown)}")
    if task is not None and task not in r.tasks:
        raise _usage_error(f"unknown task {task!r}")
    if final and task is not None:
        raise _usage_error("--final cannot be combined with --task")
    ev = engine.evaluate(r)
    findings = engine.select(r, ev, task, family.lower() if family else None, wanted, final)
    if task is not None and fmt is OutputFormat.text and not ev.status.tasks[task].done:
        missing = "; ".join(ev.status.tasks[task].missing) or ev.status.tasks[task].state
        typer.echo(f"note: {task} is not done yet: {missing}", err=True)
    _exit_findings(findings, engine.rules_run(wanted), fmt)


@playbooks_app.command("sync")
def playbooks_sync(
    check: Annotated[
        bool, typer.Option("--check", help="FW-PB-002: fail on a stale header; write nothing.")
    ] = False,
    fmt: FormatOption = OutputFormat.text,
) -> None:
    """Regenerate the header block of each authored playbook from framework/ YAML."""
    from rmf_tool import playbooks_sync as sync_mod

    root = repo_root()
    if check:
        _exit_findings(sync_mod.check(root), ["FW-PB-002"], fmt)
    _changed(sync_mod.sync(root), "synced")
