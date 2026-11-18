"""The test strategy record A-2 writes beside the assessment plan: TSTRAT-001 to TSTRAT-004
(DoDI 5000.89, the pathway instructions, DoDI 8500.01, DoDI 8510.01). test-strategy.yaml holds
the TEMP or other test planning document the pathway calls for, its approvals, its cybersecurity
test objectives and events, and the conditions under which each event's data was obtained.

The rules judge the record while A-2 is in scope and say so when it is missing then. The ACAT and
the decision points passed are read from protection.yaml when the run holds it; without it the
clauses that need them stay quiet.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules.protection import (
    _day,
    _dict,
    _dicts,
    _ids,
    _passed,
    _pathway,
    _protection,
    _record,
    decision_points,
)

TS_FILE = "artifacts/data/test-strategy.yaml"
DOTE = ("DOT&E", "DOT&E-designee")  # DoDI 5000.89 3.6.k: the DOT&E or a designee
USDRE = ("USD(R&E)", "USD(R&E)-designee")  # 2.2.e: the USD(R&E) delegates as appropriate
OSD_DAYS = 45  # DoDI 5000.89 3.7.a.(2): oversight TEMPs reach the OSD 45 days before the decision
# The test planning document each pathway calls for (DoDI 5000.89 3.7.a.(3), Sections 4 and 5).
DOCUMENTS = {
    "PW-MCA": ("temp",),
    "PW-MTA": ("test-strategy",),
    "PW-SWP": ("test-strategy",),
    "PW-UCA": ("abbreviated-test-plan", "test-strategy", "temp"),
    "PW-DBS": ("implementation-plan", "temp"),
    "PW-AOS": ("temp", "test-strategy", "abbreviated-test-plan", "implementation-plan"),
}
DBS_OVERSIGHT_DOCUMENT = "temp"  # DoDI 5000.75 4B.3.c.(2)(e)
PEN_TEST = "penetration-exploitation"
OT_ASSESSMENTS = ("cvpa", "adversarial-assessment")  # DoDI 5000.89 4.5.d.(1)
CEVA = "cyber-economic-vulnerability-analysis"
DCO = "dco-evaluation"
CVI = "cooperative-vulnerability-identification"
PRODUCTION = "production-representative"
REPRESENTATIVE = "operationally-representative"


def _strategy(ctx: Context, rule: str) -> tuple[dict[str, Any] | None, list[RunFinding],
                                                 Callable[[str], None]]:
    return _record(ctx, rule, TS_FILE, "A-2")


def _phase(events: list[dict[str, Any]], *phases: str) -> list[dict[str, Any]]:
    return [e for e in events if e.get("phase") in phases]


# --- TSTRAT-001: the planning document and its approvals -----------------------------------

def approvals(ctx: Context) -> list[RunFinding]:
    data, out, err = _strategy(ctx, "TSTRAT-001")
    if data is None:
        return out
    document, oversight = _dict(data.get("document")), _dict(data.get("oversight"))
    pathway = _pathway(ctx)
    kind = document.get("kind")
    allowed = DOCUMENTS.get(pathway or "", ())
    if pathway and kind not in allowed:
        err(f"T&E planning, resourcing and documentation follow the {pathway} pathway policy, "
            f"which calls for a {' or '.join(allowed)}, not a {kind}")
    if pathway == "PW-DBS" and oversight.get("dote") is True and kind != DBS_OVERSIGHT_DOCUMENT:
        err("a business system on the DOT&E oversight list documents its T&E management content "
            "in a test and evaluation master plan")
    if pathway and document.get("pathway") != pathway:
        err(f"the test planning document is written for {document.get('pathway')}, and the "
            f"program is on {pathway}")
    parts = {a.get("part"): a for a in _dicts(data.get("approvals"))}
    live_fire = oversight.get("lfte") is True or any(
        e.get("kind") == "lft" for e in _dicts(data.get("events")))
    if oversight.get("dote") is True:
        for part in ("ot-e", "lft-e") if live_fire else ("ot-e",):
            if _dict(parts.get(part)).get("by") not in DOTE:
                err(f"the DOT&E is the approval authority for the {part} planned activities of a "
                    f"program on T&E oversight, not {_dict(parts.get(part)).get('by')}")
    acat = _dict(_protection(ctx).get("program")).get("acat")
    if acat == "ID" and _dict(parts.get("dt-e")).get("by") not in USDRE:
        err("the USD(R&E) is the approval authority for the DT&E plan of an ACAT ID program, not "
            f"{_dict(parts.get('dt-e')).get('by')}")
    document_approval = parts.get("document")
    if document_approval is None:
        err("the test strategy documentation requires DoD Component approval, and none is "
            "recorded")
    passed = _passed(_dict(_protection(ctx).get("program")))
    if oversight.get("dote") is True or oversight.get("usdre") is True:
        approval = _dict(document_approval)
        point, sent = approval.get("decision_point"), _day(approval.get("submitted_to_osd"))
        if not point or sent is None:
            err("the TEMP of an oversight program is submitted to the OSD before the decision "
                "point it supports; the document approval names no decision point or no "
                "submission date")
        due = passed.get(str(point))
        if due and sent and (due - sent).days < OSD_DAYS:
            err(f"the TEMP of an oversight program is submitted to the OSD for approval 45 "
                f"calendar days before {point}, not on {sent}")
    return out


# --- TSTRAT-002: cybersecurity test events -------------------------------------------------

def cyber_events(ctx: Context) -> list[RunFinding]:
    data, out, err = _strategy(ctx, "TSTRAT-002")
    if data is None:
        return out
    events = _dicts(data.get("events"))
    kinds = {e.get("kind") for e in events}
    pathway = _pathway(ctx)
    valid = decision_points(ctx, pathway, ("milestone", "decision-point", "event"))
    for e in events:
        if valid and e.get("decision_point") not in valid:
            err(f"{e.get('id')} supports {e.get('decision_point')}, which is no decision point "
                "of the program's pathway")
    developmental = _phase(events, "dt", "integrated")
    operational = _phase(events, "ot", "integrated")
    if not any("cybersecurity" in _ids(e.get("evaluates")) for e in developmental):
        err("the test strategy describes no DT event designed to evaluate cybersecurity")
    if operational and not any("cybersecurity" in _ids(e.get("evaluates"))
                               for e in operational):
        err("the test strategy describes no OT event designed to evaluate cybersecurity")
    frameworks = _ids(data.get("evaluation_frameworks"))
    if developmental and "def" not in frameworks:
        err("the test strategy includes a developmental evaluation framework for its DT events")
    if operational and not frameworks & {"oef", "ot-concept"}:
        err("the test strategy includes an OT concept or an operational evaluation framework")
    if operational:
        for kind in sorted(set(OT_ASSESSMENTS) - kinds):
            err(f"OT&E evaluates cybersecurity through a CVPA and an adversarial assessment, and "
                f"the test strategy plans no {kind}")
        if DCO not in kinds:
            err("cybersecurity testing includes evaluating defensive cyberspace operations")
        if data.get("financial_functions") is True and CEVA not in kinds:
            err("cybersecurity OT&E of a system with financial or fiscal/business functions "
                "includes a cyber economic vulnerability analysis")
    if developmental and CVI not in kinds:
        err("the test strategy plans no cooperative vulnerability identification to find "
            "vulnerabilities and plan their mitigation")
    return out


# --- TSTRAT-004 (split from TSTRAT-002): penetration and exploitation testing ---------------

def penetration_tests(ctx: Context) -> list[RunFinding]:
    """TSTRAT-004: the test strategy plans penetration and exploitation testing that is
    independent, threat representative and evaluates the complete system with its CSSP, in both
    the DT&E and the OT&E (DoDI 5000.89, DoDI 8500.01). TSTRAT-002 asks the other events and the
    evaluation frameworks, and reports a missing record."""
    data, out, err = _strategy(ctx, "TSTRAT-004")
    if data is None:
        return []  # TSTRAT-002 reports the missing test strategy
    pens = [e for e in _dicts(data.get("events")) if e.get("kind") == PEN_TEST]
    if not pens:
        err("cybersecurity evaluation in acquisition T&E includes penetration and exploitation "
            "testing, and the test strategy plans none")
    for e in pens:
        if e.get("independent") is not True or e.get("threat_representative") is not True:
            err(f"{e.get('id')}: penetration and exploitation testing is independent and threat "
                "representative")
    # narrower penetration tests may stand beside them; the DT&E and the OT&E each hold one of
    # the complete system defenses with the CSSP, or one integrated test does (F-11-6)
    whole = [e for e in pens
             if e.get("scope") == "complete-system" and e.get("includes_cssp") is True]
    if pens and not whole:
        err(f"{pens[0].get('id')}: penetration and exploitation testing evaluates the complete "
            "system cyberspace defenses, including the controls and protection provided by "
            "cybersecurity service providers")
    phases = {e.get("phase") for e in whole}
    if whole and (not phases & {"dt", "integrated"} or not phases & {"ot", "integrated"}):
        err("penetration and exploitation testing is planned and resourced as part of both the "
            "DT&E and the OT&E")
    return out


# --- TSTRAT-003: what was tested, how and by whom ------------------------------------------

def test_provenance(ctx: Context) -> list[RunFinding]:
    data, out, err = _strategy(ctx, "TSTRAT-003")
    if data is None:
        return out
    for e in _dicts(data.get("events")):
        ident = e.get("id")
        if e.get("kind") == "adversarial-assessment" and e.get("system") != PRODUCTION:
            err(f"{ident}: the system under test is mature enough to represent the production "
                f"version, not a {e.get('system')}")
        if e.get("results_reused") is not True:
            continue
        if e.get("system") != PRODUCTION:
            err(f"{ident}: results reused as assessment evidence come from a system that "
                f"represents the production version, not a {e.get('system')}")
        if e.get("environment") != REPRESENTATIVE:
            err(f"{ident}: results reused as assessment evidence come from an operationally "
                f"representative environment, not a {e.get('environment')}")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("TSTRAT-001", approvals), ("TSTRAT-002", cyber_events),
                ("TSTRAT-003", test_provenance), ("TSTRAT-004", penetration_tests))
