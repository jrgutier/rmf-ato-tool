"""`rmf oscal validate`: OSCAL-001 (NIST v1.2.1 schema, regex engine + FormatChecker) and
OSCAL-002 (compliance-trestle 5.2.0 model load) over a run's ``oscal/*.json``, or over the
``*.json`` of any directory (``tests/golden/oscal``), and OSCAL-003 (NIST oscal-cli constraint
validation, optional; see ``oscal.oscal_cli``)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rmf_tool.oscal import oscal_cli, schema_validate
from rmf_tool.run.model import OSCAL_DIR, Run


def trestle_class(model: str) -> Any:
    from trestle.oscal import assessment_plan, assessment_results, catalog, poam, profile, ssp

    return {
        "ssp": ssp.SystemSecurityPlan,
        "profile": profile.Profile,
        "catalog": catalog.Catalog,
        "assessment-plan": assessment_plan.AssessmentPlan,
        "assessment-results": assessment_results.AssessmentResults,
        "poam": poam.PlanOfActionAndMilestones,
    }[model]


def files(run: Run) -> list[Path]:
    return sorted((run.dir / OSCAL_DIR).glob("*.json"))


def schema_problems_in(repo: Path, base: Path, paths: list[Path]) -> list[tuple[str, str]]:
    """OSCAL-001: (path relative to ``base``, message) per schema error."""
    out = []
    for path in paths:
        rel = path.relative_to(base).as_posix()
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            model = schema_validate.model_of(doc)
        except (ValueError, KeyError) as exc:
            out.append((rel, str(exc)))
            continue
        out += [(rel, schema_validate.describe(e))
                for e in schema_validate.validate(repo, doc, model)]
    return out


def trestle_problems_in(base: Path, paths: list[Path]) -> list[tuple[str, str]]:
    """OSCAL-002: (path relative to ``base``, message) per file trestle cannot load."""
    out = []
    for path in paths:
        rel = path.relative_to(base).as_posix()
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            model = schema_validate.model_of(doc)
            trestle_class(model).oscal_read(path)
        except Exception as exc:  # trestle and pydantic raise many error types
            out.append((rel, f"trestle cannot load: {str(exc).splitlines()[0][:300]}"))
    return out


def oscal_cli_problems_in(exe: str, base: Path, paths: list[Path]) -> list[tuple[str, str]]:
    """OSCAL-003: (path relative to ``base``, message) per oscal-cli rule a file breaks. A file
    that is not OSCAL JSON is left to OSCAL-001, and a profile is skipped (``oscal_cli``)."""
    out = []
    for path in paths:
        try:
            model = schema_validate.model_of(json.loads(path.read_text(encoding="utf-8")))
        except (ValueError, KeyError):
            continue
        if model in oscal_cli.SKIPPED_MODELS:
            continue
        rel = path.relative_to(base).as_posix()
        out += [(rel, msg) for msg in oscal_cli.problems(exe, path)]
    return out


def schema_problems(run: Run) -> list[tuple[str, str]]:
    return schema_problems_in(run.repo, run.dir, files(run))


def trestle_problems(run: Run) -> list[tuple[str, str]]:
    return trestle_problems_in(run.dir, files(run))


def oscal_cli_problems(exe: str, run: Run) -> list[tuple[str, str]]:
    return oscal_cli_problems_in(exe, run.dir, files(run))
