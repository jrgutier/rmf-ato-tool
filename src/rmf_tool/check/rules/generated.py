"""Generated-output rules: GEN-STALE-001, HYB-002, OSCAL-001, OSCAL-002."""

from __future__ import annotations

from rmf_tool import assemble, build, package
from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.oscal import validate as oscal_validate
from rmf_tool.run.assumptions import REPORT_FILE
from rmf_tool.run.model import BASELINE_FILE, MANIFEST_FILE

STALE = "GEN-STALE-001"  # run-wide: `rmf build` fixes it, whichever task's files it touches
HINT = "run `rmf build`; never hand-edit generated files (INV-2)"


def _stale(message: str, path: str | None = None) -> RunFinding:
    return make(STALE, message, path, run_wide=True)


def stale(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out: list[RunFinding] = []
    try:
        for rel, (old, new) in assemble.assembled(run).items():
            if old != new:
                out.append(_stale(f"marker block differs from a fresh assemble; {HINT}",
                                rel))
    except assemble.AssembleError as exc:
        out.append(_stale(str(exc)))
    oscal = build.oscal_outputs(run)
    for rel, text in oscal.files.items():
        path = run.path(rel)
        if text is None and path.is_file():
            out.append(_stale(f"exists but cannot be built now ({oscal.notes[rel]}); {HINT}",
                            rel))
        elif text is not None and not path.is_file():
            out.append(_stale(f"missing; {HINT}", rel))
        elif text is not None and path.read_text(encoding="utf-8") != text:
            out.append(_stale(f"differs from a fresh build; {HINT}", rel))
    if run.path(BASELINE_FILE).is_file():
        try:
            fresh = baseline_mod.render(baseline_mod.resolve(run))
        except baseline_mod.BaselineError as exc:
            out.append(_stale(f"exists but `rmf baseline resolve` fails: {exc}",
                            BASELINE_FILE))
        else:
            if run.path(BASELINE_FILE).read_text(encoding="utf-8") != fresh:
                out.append(_stale("differs from a fresh `rmf baseline resolve`",
                                BASELINE_FILE))
    if run.path(MANIFEST_FILE).is_file() and \
            run.path(MANIFEST_FILE).read_text(encoding="utf-8") != package.render(run):
        out.append(_stale(f"differs from a fresh `rmf package`; {HINT}", MANIFEST_FILE))
    return out


def assumptions_report(ctx: Context) -> list[RunFinding]:
    path = ctx.run.path(REPORT_FILE)
    if not path.is_file():
        return [make("HYB-002", f"assumptions report missing; {HINT}", REPORT_FILE)]
    if path.read_text(encoding="utf-8") != build.assumptions_report(ctx.run):
        return [make("HYB-002", "assumptions report incomplete or stale (it must list every "
                     f"assumption and tagged answer); {HINT}", REPORT_FILE)]
    return []


def oscal_schema(ctx: Context) -> list[RunFinding]:
    return [make("OSCAL-001", msg, rel) for rel, msg in oscal_validate.schema_problems(ctx.run)]


def oscal_trestle(ctx: Context) -> list[RunFinding]:
    return [make("OSCAL-002", msg, rel) for rel, msg in oscal_validate.trestle_problems(ctx.run)]
