"""`rmf oscal validate`: OSCAL-001 (NIST v1.2.1 schema, regex engine + FormatChecker) and
OSCAL-002 (compliance-trestle 5.2.0 model load) over a run's ``oscal/*.json``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rmf_tool.oscal import schema_validate
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


def schema_problems(run: Run) -> list[tuple[str, str]]:
    """OSCAL-001: (run-relative path, message) per schema error."""
    out = []
    for path in files(run):
        rel = run.rel(path)
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            model = schema_validate.model_of(doc)
        except (ValueError, KeyError) as exc:
            out.append((rel, str(exc)))
            continue
        out += [(rel, schema_validate.describe(e))
                for e in schema_validate.validate(run.repo, doc, model)]
    return out


def trestle_problems(run: Run) -> list[tuple[str, str]]:
    """OSCAL-002: (run-relative path, message) per file trestle cannot load."""
    out = []
    for path in files(run):
        rel = run.rel(path)
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            model = schema_validate.model_of(doc)
            trestle_class(model).oscal_read(path)
        except Exception as exc:  # trestle and pydantic raise many error types
            out.append((rel, f"trestle cannot load: {str(exc).splitlines()[0][:300]}"))
    return out
