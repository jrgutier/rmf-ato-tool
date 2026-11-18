"""Human-readable labels for framework IDs.

People read "Prepare 1: Risk Management Roles (P-1)" more easily than "P-1". The codes stay the
stable identifiers in files and data (INV-3); every report, status line and generated document
a person reads shows the name first and the code in brackets.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path

from rmf_tool.yamlload import safe_load

STEPS_FILE = "framework/rmf-steps.yaml"
# SP 800-37r2 step names, used only when framework/rmf-steps.yaml cannot be read.
_DEFAULT_STEPS = {"P": "Prepare", "C": "Categorize", "S": "Select", "I": "Implement",
                  "A": "Assess", "R": "Authorize", "M": "Monitor"}


@lru_cache(maxsize=8)
def step_names(repo: Path | None = None) -> dict[str, str]:
    """Step ID -> step name, from framework/rmf-steps.yaml (INV-1)."""
    if repo is not None:
        try:
            data = safe_load((repo / STEPS_FILE).read_text(encoding="utf-8"))
            names = {str(s["id"]): str(s["name"]) for s in data.get("steps") or []}
            if names:
                return names
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            pass
    return dict(_DEFAULT_STEPS)


def task_label(task_id: str, name: str = "",
               repo: Path | Mapping[str, str] | None = None) -> str:
    """'Prepare 1: Risk Management Roles (P-1)'; the bare code when it is not a task code.
    ``repo`` is the repository (step names read from framework/) or a step-name mapping."""
    step, _, number = task_id.partition("-")
    steps = repo if isinstance(repo, Mapping) else step_names(repo)
    if step not in steps or not number.isdigit():
        return f"{name} ({task_id})" if name else task_id
    head = f"{steps[step]} {number}"
    return f"{head}: {name} ({task_id})" if name else f"{head} ({task_id})"


def named(ident: str, name: str = "") -> str:
    """'System Security Plan (ART-SSP)': any other framework entity, name first."""
    return f"{name} ({ident})" if name else ident
