"""Run-scope rule implementations (plan §6.5). Each takes a ``Context`` and returns
``RunFinding``s; JOURNAL-001 also needs the derived task status, so the engine runs it last.
"""

from __future__ import annotations

from collections.abc import Callable

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules import artifacts, config, content, generated

Rule = Callable[[Context], list[RunFinding]]

RULES: dict[str, Rule] = {
    "RUN-CFG-001": config.run_cfg,
    "RUN-FM-001": artifacts.front_matter,
    "RUN-ART-001": artifacts.core_present,
    "FACTS-001": content.facts_complete,
    "GEN-STALE-001": generated.stale,
    "SSP-COV-001": content.ssp_coverage,
    "SAR-POAM-001": content.sar_poam,
    "TRACE-001": content.trace_present,
    "TRACE-002": content.trace_resolves,
    "HYB-001": content.tagged,
    "HYB-002": generated.assumptions_report,
    "OSCAL-001": generated.oscal_schema,
    "OSCAL-002": generated.oscal_trestle,
}
JOURNAL_RULE = "JOURNAL-001"
IMPLEMENTED = (*RULES, JOURNAL_RULE)
