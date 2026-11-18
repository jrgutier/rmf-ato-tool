"""Generated-output rules: GEN-STALE-001, BSEL-001, BSEL-002, HYB-002, OSCAL-001, OSCAL-002,
OSCAL-003."""

from __future__ import annotations

import json
import os
from typing import Any

from rmf_tool import assemble, build, package
from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.oscal import oscal_cli
from rmf_tool.oscal import validate as oscal_validate
from rmf_tool.run.assumptions import REPORT_FILE
from rmf_tool.run.model import BASELINE_FILE, MANIFEST_FILE

STALE = "GEN-STALE-001"  # run-wide: `rmf build` fixes it, whichever task's files it touches
SELECTED, CONTROLS = "BSEL-001", "BSEL-002"  # split from GEN-STALE-001: the baseline itself
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
    out += _baseline_stale(ctx)
    if run.path(MANIFEST_FILE).is_file() and \
            run.path(MANIFEST_FILE).read_text(encoding="utf-8") != package.render(run):
        out.append(_stale(f"differs from a fresh `rmf package`; {HINT}", MANIFEST_FILE))
    return out


def _loaded(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _controls(data: dict[str, Any]) -> dict[str, Any]:
    return {c.get("control_id"): c.get("origin") for c in data.get("controls") or ()
            if isinstance(c, dict)}


def _baseline(ctx: Context) -> list[RunFinding]:
    """The baseline against a fresh `rmf baseline resolve`: BSEL-001 when it is not selected
    for the approved categorization (method, impact values, overlays) or cannot be resolved,
    BSEL-002 when its controls differ, GEN-STALE-001 for any other difference."""
    run = ctx.run
    if not run.path(BASELINE_FILE).is_file():
        return []
    try:
        fresh = baseline_mod.render(baseline_mod.resolve(run))
    except baseline_mod.BaselineError as exc:
        return [make(SELECTED, f"the baseline exists but `rmf baseline resolve` fails: {exc}",
                     BASELINE_FILE, run_wide=True)]
    text = run.path(BASELINE_FILE).read_text(encoding="utf-8")
    if text == fresh:
        return []
    have, want = _loaded(text), _loaded(fresh)
    moved = []
    if have.get("method") != want.get("method"):
        moved.append(f"the baseline is selected by the {have.get('method')} method, not the "
                     f"{want.get('method')} method the categorization calls for")
    if have.get("categorization") != want.get("categorization"):
        moved.append(f"the baseline is selected for impact values {have.get('categorization')}, "
                     f"not the approved categorization {want.get('categorization')}")
    if have.get("overlays") != want.get("overlays"):
        moved.append(f"the baseline applies overlays {have.get('overlays')}, not the overlays "
                     f"of the approved categorization {want.get('overlays')}")
    if moved:
        return [make(SELECTED, message, BASELINE_FILE, run_wide=True) for message in moved]
    held, due = _controls(have), _controls(want)
    if held != due:
        absent = sorted(f"{c} ({o})" for c, o in due.items() if held.get(c) != o)
        extra = sorted(c for c in held if c not in due)
        parts = ([f"leaves out {', '.join(absent)}"] if absent else []) + (
            [f"adds {', '.join(extra)}"] if extra else [])
        return [make(CONTROLS, "the baseline's controls differ from those a fresh `rmf "
                     f"baseline resolve` selects: it {' and '.join(parts)}", BASELINE_FILE,
                     run_wide=True)]
    return [_stale("differs from a fresh `rmf baseline resolve`", BASELINE_FILE)]


def selection(ctx: Context) -> list[RunFinding]:
    """BSEL-001: the baseline is selected for the approved categorization."""
    return [f for f in _baseline(ctx) if f.finding.rule == SELECTED]


def baseline_controls(ctx: Context) -> list[RunFinding]:
    """BSEL-002: the baseline holds the controls a fresh resolve selects."""
    return [f for f in _baseline(ctx) if f.finding.rule == CONTROLS]


def _baseline_stale(ctx: Context) -> list[RunFinding]:
    return [f for f in _baseline(ctx) if f.finding.rule == STALE]


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


def oscal_cli_constraints(ctx: Context) -> list[RunFinding]:
    """OSCAL-003 runs only when ``RMF_OSCAL_CLI`` opts in (``oscal.oscal_cli``); an opt-in that
    names no executable is reported rather than passed over."""
    if not os.environ.get(oscal_cli.ENV, "").strip():
        return []
    found = oscal_cli.locate(path_lookup=False)
    if found.path is None:
        return [] if os.environ[oscal_cli.ENV].strip().lower() == oscal_cli.OFF else [
            make("OSCAL-003", found.note, run_wide=True)]
    return [make("OSCAL-003", msg, rel)
            for rel, msg in oscal_validate.oscal_cli_problems(found.path, ctx.run)]
