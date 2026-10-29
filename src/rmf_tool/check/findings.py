"""Run-scope findings: a ``Finding`` plus the tasks that own it and its control family.

Ownership drives ``rmf check --task T`` and task completion (plan §7.3): a finding on an
artifact's files belongs to every task that writes the artifact, a fact to its writer, an
interview to its task. Findings with no owner (run.yaml, OSCAL, journal, generated
files) are run-wide.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from rmf_tool.check import rules_by_id
from rmf_tool.findings import Finding

_FAMILY_FILE = re.compile(r"^artifacts/(?:ssp/controls|sar/results)/([a-z]{2})(?:\.\d+)?\.yaml$")


@dataclass(frozen=True)
class RunFinding:
    finding: Finding
    owners: frozenset[str] = field(default_factory=frozenset)
    family: str | None = None
    run_wide: bool = False  # never owned by a task, whatever its path

    @property
    def rule(self) -> str:
        return self.finding.rule

    @property
    def error(self) -> bool:
        return self.finding.severity == "E"


def make(rule: str, message: str, path: str | None = None, line: int | None = None,
         owners: set[str] | frozenset[str] | None = None,
         family: str | None = None, run_wide: bool = False) -> RunFinding:
    severity = rules_by_id()[rule].severity
    if family is None and path:
        m = _FAMILY_FILE.match(path)
        family = m.group(1) if m else None
    return RunFinding(Finding(rule, severity, message, path, line),
                      frozenset(owners or ()), family, run_wide)
