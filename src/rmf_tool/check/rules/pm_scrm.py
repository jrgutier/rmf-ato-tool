"""The program manager's SCRM actions P-14 writes beside ART-RA: PMSCRM-001 and PMSCRM-002
(DoDI 5000.90 3.4, DoDI 5000.82 3.5.c, DoDI 5000.83 3.3.c, CNSSP 12). pm-scrm.yaml holds the
market research, the illumination decision, the risk tolerance level with the Table 1 due
diligence it calls for, DIA SCRM TAC requests and their reports, the assured supplier or
countermeasure of each mission-critical item, validated products, and the supply chain
mitigations with the threat information behind them.

Table 1 rows say should, so an action the level calls for is taken or carries a reason. The
risk tolerance level is the run's own: the source gives examples, not classes. Critical items
come from protection.yaml and IA products from inventory.yaml, read only when the run holds them.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules.plans import _space
from rmf_tool.check.rules.protection import _day, _dict, _dicts, _ids, _protection, _record

SCRM_FILE = "artifacts/data/pm-scrm.yaml"
INV_FILE = "artifacts/data/inventory.yaml"
# DoDI 5000.90 Table 1: each level implements all previous strategies and its own.
TABLE_1 = {
    "high": ("foci-caution", "approved-products-lists", "industry-standards",
             "balance-risk-mission"),
    "moderate": ("verifiable-vendor-processes", "vendor-limitations-awareness",
                 "countermeasures-critical-risks"),
    "low": ("assess-critical-components", "implement-countermeasures", "assessment-vendors"),
    "very-low": ("follow-dodi5200.44-sp800-161", "criticality-analysis", "ppp-documentation",
                 "tac-requests", "flag-reports"),
}
LEVELS = tuple(TABLE_1)
# Table 1: the kind of procurement each level applies to.
PROCUREMENT = {"simplified": "high", "structured": "moderate", "engineered": "low",
               "assured": "very-low"}
FLAG_ALWAYS = ("critical", "high")  # "select medium" is the PM's choice
MISSION_ITEMS = ("critical-function", "critical-component")
MITIGATION_KINDS = ("acquisition", "engineering")  # CNSSP 12 3.e


def _owed(level: Any) -> list[str]:
    if level not in LEVELS:
        return []
    return [a for lvl in LEVELS[:LEVELS.index(level) + 1] for a in TABLE_1[lvl]]


def _scrm(ctx: Context, rule: str) -> tuple[dict[str, Any] | None, list[RunFinding],
                                            Callable[[str], None]]:
    return _record(ctx, rule, SCRM_FILE, "P-14")


# --- PMSCRM-001: due diligence by risk tolerance -----------------------------------------

def due_diligence(ctx: Context) -> list[RunFinding]:
    data, out, err = _scrm(ctx, "PMSCRM-001")
    if data is None:
        return out
    tolerance = _dict(data.get("risk_tolerance"))
    level, procurement = tolerance.get("level"), tolerance.get("procurement")
    expected = PROCUREMENT.get(str(procurement))
    if expected and level in LEVELS and LEVELS.index(level) < LEVELS.index(expected):
        err(f"Table 1 applies {expected} risk tolerance to {procurement} procurements; "
            f"{level} tolerates more risk than that")
    taken = _ids(data.get("actions"))
    explained = {str(n.get("action")) for n in _dicts(data.get("not_taken")) if n.get("reason")}
    for action in _owed(level):
        if action not in taken and action not in explained:
            err(f"Table 1 asks a system of {level} risk tolerance for {action}; it is neither "
                "taken nor explained")
    if "tac-requests" in taken and not _dicts(data.get("tac_requests")):
        err("no request on critical components or suppliers is sent to the DIA SCRM TAC or "
            "other CI sources")
    ppp = _dict(_protection(ctx).get("ppp"))
    if ppp and "ppp-documentation" in taken and "scrm" not in _ids(ppp.get("sse_activities")):
        err("SCRM is documented in the program protection plan, whose activities leave it out")
    requests = {str(r.get("id")) for r in _dicts(data.get("tac_requests"))}
    for report in _dicts(data.get("reports")):
        ident = report.get("id")
        if str(report.get("request")) not in requests:
            err(f"report {ident} answers {report.get('request')}, which is no TAC request")
        if report.get("rating") in FLAG_ALWAYS and report.get("flagged") is not True:
            err(f"report {ident} came back {report.get('rating')} and is not flagged")
        if report.get("flagged") is True and not report.get("mitigation"):
            err(f"flagged report {ident} has no mitigation decision commensurate with risk")
    started = _day(data.get("started"))
    awards = [d for d in (_day(a.get("date")) for a in _dicts(_protection(ctx).get(
        "contract_awards"))) if d]
    if started is not None and awards and started > min(awards):
        err("supply chain risk management practices begin before the acquisition; the first "
            f"contract award ({min(awards)}) precedes them")
    return out


# --- PMSCRM-002: mission-critical items, validated products, space mitigations ------------

def protections(ctx: Context) -> list[RunFinding]:
    data, out, err = _scrm(ctx, "PMSCRM-002")
    if data is None:
        return out
    covered = {str(m.get("item")) for m in _dicts(data.get("mission_critical"))}
    items = _dicts(_dict(_protection(ctx).get("ppp")).get("critical_items"))
    for item in items:
        if item.get("kind") in MISSION_ITEMS and str(item.get("id")) not in covered:
            err(f"{item.get('id')} performs a mission-critical function with neither an assured "
                "supplier nor an SCRM countermeasure")
    inventory = ctx.data(INV_FILE) if ctx.run.path(INV_FILE).is_file() else None
    explained = {str(u.get("item")) for u in _dicts(data.get("unvalidated_products"))}
    for item in _dicts(_dict(inventory).get("items")):
        if item.get("cnssp11") == "not-compliant" and str(item.get("id")) not in explained:
            err(f"IA product {item.get('id')} is not validated and the record gives no reason "
                "that a validated one is not available or not cost effective")
    if _space(ctx):
        mitigations = _dicts(data.get("mitigations"))
        kinds = {m.get("kind") for m in mitigations}
        for kind in MITIGATION_KINDS:
            if kind not in kinds:
                err(f"a space NSS manages supply chain risk through {kind} mitigations, and "
                    "the record has none")
        all_source = {str(t.get("id")) for t in _dicts(data.get("threat_information"))
                      if t.get("kind") == "all-source"}
        for m in mitigations:
            if not _ids(m.get("informed_by")) & all_source:
                err(f"mitigation {m.get('id')} of a space NSS is not informed by all-source "
                    "supply chain threat information")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("PMSCRM-001", due_diligence), ("PMSCRM-002", protections))
