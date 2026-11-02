"""Run-scope rule implementations (plan §6.5). Each takes a ``Context`` and returns
``RunFinding``s; JOURNAL-001 also needs the derived task status, so the engine runs it last.
"""

from __future__ import annotations

from collections.abc import Callable

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules import (
    artifacts,
    authorization,
    config,
    consistency,
    content,
    coverage,
    generated,
    hybrid,
    journal,
)

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
    # Phase 6
    "RUN-PH-001": artifacts.placeholders,
    "RUN-STALE-001": config.stale_upstream,
    "SSP-COV-002": coverage.ssp_outside,
    "SSP-DUP-001": coverage.ssp_duplicates,
    "SSP-STAT-001": coverage.ssp_status,
    "SAP-COV-001": coverage.sap_coverage,
    "SAR-COV-001": coverage.sar_coverage,
    "POAM-CTL-001": consistency.poam_controls,
    "POAM-FLD-001": consistency.poam_fields,
    "RAR-001": consistency.rar_links,
    "AODM-001": authorization.records_valid,
    "AODM-002": authorization.termination_valid,
    "AODM-003": authorization.cio_concurrence,
    "AODM-004": authorization.threat_assessment,
    "AODM-005": authorization.chain,
    "AODM-006": authorization.live_events,
    "AODM-007": authorization.cato_eligible,
    "AODM-009": authorization.parties_valid,
    "AODM-010": authorization.risk_executive,
    "AODM-011": authorization.issues,
    "ENT-001": authorization.enterprise_boarding,
    "ENT-002": authorization.enterprise_received,
    "AUTHRPT-001": authorization.report_valid,
    "RAR-002": consistency.rar_determination,
    "RAR-003": consistency.rar_courses,
    "DIAS-001": consistency.dias_controls,
    "PKG-003": coverage.data_elements,
    "RUN-VER-001": config.old_contract,
    "INV-BND-001": consistency.inventory_in_boundary,
    "INV-BND-002": consistency.boundary_in_inventory,
    "STIG-001": consistency.stig_mapped,
    "STIG-002": consistency.stig_cat1_poam,
    "CONMON-001": coverage.conmon_frequencies,
    "INT-001": hybrid.interviews_wellformed,
    "HYB-003": hybrid.humans_crosscheck,
    "LES-001": journal.lesson_refs,
    "PKG-001": coverage.package_complete,
    "DEGRADED-001": config.degraded,
    "TASK-DEF-001": consistency.deferrals,
}
JOURNAL_RULE = "JOURNAL-001"
UNFILTERED = frozenset({"DEGRADED-001"})  # non-suppressible (plan §7.6): every selection keeps it
IMPLEMENTED = (*RULES, JOURNAL_RULE)
