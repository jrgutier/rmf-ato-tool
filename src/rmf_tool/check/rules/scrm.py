"""System C-SCRM rules SCRM-001 to SCRM-015 (NIST SP 800-161 Rev. 1, SP 800-18 Rev. 2,
DoDI 5000.82, DoDI 5000.83, DoDI 8500.01). They read the system's C-SCRM record: scrm.yaml
(ART-RA), written at P-14 and given its R-3 responses; scrm-acquisition.yaml (ART-REQ), written
at P-17; and scrm-plan.yaml (ART-SSP), written at S-4 with the S-2 control decisions, supplier
monitoring and the supply chain reporting the M-5 posture reports follow. Each part is judged
once its task is in the run's scope, and each rule stays quiet about a file that is unreadable
(RUN-FM-001 reports it).

Table 28 (baseline risk factors), Table 29 (the Supply Chain Risk Severity Schema) and Table 30
(the assessment record) are SP 800-161 Appendix E. Every baseline factor is owed for a critical
source; a non-critical one is assessed at the agency's discretion (p. 247)."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.consistency import INVENTORY_FILE
from rmf_tool.run import scope

SCRM_FILE = "artifacts/data/scrm.yaml"
ACQUISITION_FILE = "artifacts/data/scrm-acquisition.yaml"
PLAN_FILE = "artifacts/data/scrm-plan.yaml"
ORG_FILE = "artifacts/data/scrm-org.yaml"
RA_FILE = "artifacts/data/ra.yaml"
REQUIREMENTS_FILE = "artifacts/data/requirements.yaml"
INFOTYPES_FILE = "artifacts/data/infotypes.yaml"
ASSESS, ALLOCATE, TAILOR, PLAN, MONITOR_DESIGN, RESPOND = (
    "P-14", "P-17", "S-2", "S-4", "S-5", "R-3")

TABLE28 = ("purpose", "criticality", "information-and-data", "reliance",
           "operational-environment", "external-interdependencies", "functionality",
           "company-information", "quality-past-performance", "personnel", "physical",
           "geopolitical", "foci", "compliance-legal", "fraud-corruption-sanctions",
           "cybersecurity", "counterfeit-nonconforming", "supply-chain-relationships")
# Table 28 puts counterfeit products in the baseline "if relevant ...; if in doubt, include".
OPTIONAL_FACTOR = "counterfeit-nonconforming"
SUBSTANTIAL = 3  # SCRSS levels 3 and above are "substantial risk" under the FASC rule (p. 257)
WEIGHED_FIRST = ("law-enforcement", "counter-intelligence", "legal")  # p. 258
THREAT_DATA = ("attacks-observed", "incident-data", "ttps", "disasters")  # p. 290
LIKELIHOOD_INPUTS = ("threat-assumptions", "threat-information", "peer-history",
                     "expert-perspective", "external-exposure")  # p. 292
TSN_FOR_CRITICAL = ("criticality-analysis", "all-source-threat-assessment",
                    "cyber-test-and-evaluation")
# DoDI 5000.83 §3.5.b(7): technical mitigations for mission-critical functions and critical
# components must, at a minimum, include these.
MITIGATIONS = ("software-assurance", "hardware-assurance", "procurement-strategies",
               "anti-counterfeit")
EXCLUSION_APPROVERS = ("contracting-officer", "counsel")
CONTRACT_TERMS = ("qualifying-condition", "flow-down", "revalidation", "reporting",
                  "response-roles", "termination")  # pp. 55-56
PLAN_CONSIDERATIONS = ("vendor-saas", "hybrid-or-cloud", "open-source", "non-taa-ict-ot",
                       "unauthorized-resellers", "emerging-technology")  # SP 800-18r2 p. 47
CONSIDERATION_OF_KIND = {"open-source": "open-source", "cloud-service-provider":
                         "hybrid-or-cloud"}
SECURITY_PERSONNEL = ("PER-CISO", "PER-ISSM", "PER-ISSO", "PER-ISSE")
INCLUDE_SUPPLIERS = ("contingency-planning", "incident-response", "disaster-recovery",
                     "testing")
MONITORED = ("compliance", "effectiveness", "change")  # SP 800-39 via p. 304
OUTSIDE_TOLERANCE = ("requires-mitigation", "share")
REACH = ("system", "mission", "enterprise")
# What a report at each level covers: Level 1 (p. 43) and Level 3 (p. 47).
REPORT_CONTENT = {"level-1": ("extent", "effectiveness", "urgent-conditions", "metrics",
                              "top-risks"),
                  "level-3": ("implementation", "efficiency", "effectiveness", "exposure",
                              "metrics")}
SYSTEM_OWNERS = ("PER-PM",)
URGENT_RECIPIENTS = {"PER-MDA": ("PER-MDA",), "the authorizing official": ("PER-AO", "PER-AODR"),
                     "dod-cio": ("dod-cio",)}


def _list(data: Any, key: str) -> list[dict[str, Any]]:
    value = data.get(key) if isinstance(data, dict) else None
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _refs(item: Any, key: str) -> list[str]:
    value = item.get(key) if isinstance(item, dict) else None
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _id(item: Any, key: str = "id") -> str | None:
    value = item.get(key) if isinstance(item, dict) else None
    return value if isinstance(value, str) else None


def _key(item: Any, key: str) -> str | None:
    """A field usable as a set member or lookup key; malformed input reads as missing."""
    value = item.get(key) if isinstance(item, dict) else None
    return value if isinstance(value, str) else None


def _ids(items: list[dict[str, Any]], key: str = "id") -> set[str]:
    return {i for i in (_id(item, key) for item in items) if i}


def _obj(data: Any, key: str) -> dict[str, Any]:
    value = data.get(key) if isinstance(data, dict) else None
    return value if isinstance(value, dict) else {}


def _active(ctx: Context, task: str) -> bool:
    return task in set(scope.active_tasks(ctx.run))


def _doc(ctx: Context, path: str) -> dict[str, Any] | None:
    data = ctx.data(path)
    return data if isinstance(data, dict) else None


def _missing(ctx: Context, task: str, path: str) -> bool:
    return _active(ctx, task) and not ctx.run.path(path).is_file()


def _critical(scrm: dict[str, Any]) -> list[str]:
    return sorted(i for s in _list(scrm, "suppliers") if s.get("criticality") == "critical"
                  for i in [_id(s)] if i)


def _level(item: dict[str, Any]) -> int:
    value = _obj(item, "severity").get("level")
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


# --- SCRM-001 ----------------------------------------------------------------------------
def suppliers(ctx: Context) -> list[RunFinding]:
    """P-14: every supplied item has a supplier, every ra.yaml supply chain record its
    suppliers, the criticality of a supplier follows the items it supplies, and every critical
    supplier has an assessment, prioritized ahead of the non-critical ones."""
    if _missing(ctx, ASSESS, SCRM_FILE):
        return [make("SCRM-001", "ART-RA has no artifacts/data/scrm.yaml, the system's C-SCRM "
                     "record of suppliers and their assessments", SCRM_FILE, None, {ASSESS})]
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-001", message, SCRM_FILE, None, {ASSESS}))

    sups = _list(scrm, "suppliers")
    listed = _doc(ctx, INVENTORY_FILE) is not None  # its own rules report a missing inventory
    inventory = _ids(_list(ctx.data(INVENTORY_FILE), "items"))
    chains = _ids(_list(_obj(ctx.data(RA_FILE), "external"), "supply_chain"))
    functions = {_id(f): set(_refs(f, "items")) for f in
                 _list(_obj(scrm, "criticality"), "functions")}
    supplied: set[str] = set()
    for sup in sups:
        sid = _id(sup)
        chain = _key(sup, "supply_chain")
        if chains and chain not in chains:
            err(f"{sid} names supply chain record {chain}, which ra.yaml does not hold")
        for item in _refs(sup, "items"):
            supplied.add(item)
            if listed and item not in inventory:
                err(f"{sid} provides {item}, which is no inventory item")
            for fid, items in sorted(functions.items(), key=lambda kv: str(kv[0])):
                if item in items and sup.get("criticality") != "critical":
                    err(f"{sid} supplies {item}, which performs mission-critical function "
                        f"{fid}, yet is rated non-critical")
        for fid in _refs(sup, "functions"):
            if fid not in functions:
                err(f"{sid} names mission-critical function {fid}, which the criticality "
                    "analysis does not hold")
    for item in sorted(inventory - supplied):
        err(f"inventory item {item} has no supplier in scrm.yaml, so the supplier and "
            "component inventory is incomplete")
    named = {_id(s, "supply_chain") for s in sups}
    for chain in sorted(chains - named):
        err(f"ra.yaml supply chain record {chain} has no supplier in scrm.yaml")
    assessed = _ids(_list(scrm, "assessments"), "supplier")
    for sid in _critical(scrm):
        if sid not in assessed:
            err(f"critical supplier {sid} has no supply chain risk assessment")
    # p. 247: externally driven priorities (policy direction, a regulatory requirement) may
    # rank a non-critical source ahead; the record names the driver.
    ranks = [(s.get("priority"), _id(s), s.get("criticality"), s.get("priority_driver"))
             for s in sups if isinstance(s.get("priority"), int)]
    for p_crit, crit, kind, _ in ranks:
        for p_other, other, other_kind, driver in ranks:
            if kind == "critical" and other_kind == "non-critical" and p_crit > p_other \
                    and not driver:
                err(f"{crit} is critical yet its assessment priority {p_crit} ranks below "
                    f"non-critical {other} at {p_other}")
    return out


# --- SCRM-002 ----------------------------------------------------------------------------
def trusted_systems(ctx: Context) -> list[RunFinding]:
    """P-14: the criticality analysis names inventory items, and a system with mission-critical
    functions applies the DoDI 5200.44 practices DoDI 8500.01, 5000.82 and 5000.83 name, the
    minimum technical mitigations of DoDI 5000.83 among them, with threat analysis of its
    critical suppliers sought through the TSN focal point."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-002", message, SCRM_FILE, None, {ASSESS}))

    analysis = _obj(scrm, "criticality")
    inventory = {_id(i): i for i in _list(ctx.data(INVENTORY_FILE), "items")}
    functions = _list(analysis, "functions")
    for f in functions if _doc(ctx, INVENTORY_FILE) is not None else ():
        for item in _refs(f, "items"):
            if item not in inventory:
                err(f"{_id(f)} names {item}, which is no inventory item")
    if not functions:
        return out
    practices = set(_refs(analysis, "tsn"))
    for practice in TSN_FOR_CRITICAL:
        if practice not in practices:
            err(f"the system has mission-critical functions but applies no TSN practice "
                f"{practice}")
    if "assured-suppliers" not in practices and "scrm-countermeasures" not in practices:
        err("mission-critical function items use neither assured suppliers nor SCRM "
            "countermeasures")
    for mitigation in MITIGATIONS:
        if mitigation not in practices:
            err(f"technical mitigations for mission-critical functions and critical components "
                f"do not include {mitigation}")
    if _obj(analysis, "focal_point").get("threat_analysis") == "not-required":
        err("threat analysis of suppliers of critical components is marked not required, yet "
            "the system has mission-critical functions")
    return out


# --- SCRM-003 ----------------------------------------------------------------------------
def baseline_factors(ctx: Context) -> list[RunFinding]:
    """P-14: an assessment of a critical supplier covers every baseline risk factor of
    Table 28, leaving out only counterfeit and non-conforming products when they are not
    relevant."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    out: list[RunFinding] = []
    critical = set(_critical(scrm))
    for a in _list(scrm, "assessments"):
        aid, sid = _id(a), _id(a, "supplier")
        factors = _list(a, "factors")
        if sid not in critical:  # p. 247: factors of a non-critical source are discretionary
            continue
        for f in factors:
            if f.get("status") == "not-relevant" and f.get("factor") != OPTIONAL_FACTOR:
                out.append(make("SCRM-003", f"{aid} marks {f.get('factor')} not relevant; only "
                                "counterfeit and non-conforming products may be left out of "
                                "the baseline", SCRM_FILE, None, {ASSESS}))
        held = {_key(f, "factor") for f in factors}
        for factor in TABLE28:
            if factor not in held:
                out.append(make("SCRM-003", f"{aid} assesses critical supplier {sid} without "
                                f"baseline risk factor {factor} of Table 28", SCRM_FILE, None,
                                {ASSESS}))
    return out


# --- SCRM-004 ----------------------------------------------------------------------------
def assessment_record(ctx: Context) -> list[RunFinding]:
    """P-14: an assessment record names a supplier of the record and articles that supplier
    provides, identifies mitigation options for a risk that requires mitigation, names the
    agreement under which non-federal support was obtained, and a substantial risk is cleared by
    senior leadership and legal counsel."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-004", message, SCRM_FILE, None, {ASSESS}))

    sups = {_id(s): set(_refs(s, "items")) for s in _list(scrm, "suppliers")}
    for a in _list(scrm, "assessments"):
        aid, sid = _id(a), _id(a, "supplier")
        if sid not in sups:
            err(f"{aid} assesses {sid}, which is no supplier in scrm.yaml")
            continue
        for article in _list(a, "covered_articles"):
            if _key(article, "item") not in sups[sid]:
                err(f"{aid} covers an article its supplier does not provide: "
                    f"{article.get('item')} is not among the items of {sid}")
        if a.get("tolerance") == "requires-mitigation" and not _refs(a, "mitigation"):
            err(f"{aid} requires mitigation but identifies no viable mitigation option for "
                "the unresolved or unacceptable risk")
        if _refs(_obj(a, "conducted_by"), "non_federal_support") and \
                not a.get("services_agreement"):
            err(f"{aid} drew on non-federal support but names no agreement limiting scope, "
                "data use, access, disposal and retention")
        if _level(a) >= SUBSTANTIAL:
            review = _obj(a, "review")
            if review.get("senior_leadership") is not True:
                err(f"{aid} assesses a substantial risk but senior leadership did not clear "
                    "the assessment record")
            if review.get("legal_counsel") is not True:
                err(f"{aid} assesses a substantial risk but legal counsel did not clear the "
                    "assessment record")
    return out


# --- SCRM-005 ----------------------------------------------------------------------------
def severity(ctx: Context) -> list[RunFinding]:
    """P-14: the SCRSS level of Table 29 fits the assessment's threat type and the supplier's
    criticality, and the level sets the escalation and FASC sharing."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-005", message, SCRM_FILE, None, {ASSESS}))

    critical = set(_critical(scrm))
    for a in _list(scrm, "assessments"):
        aid, level = _id(a), _level(a)
        threat = _obj(a, "findings").get("threat_type")
        escalation = _obj(a, "escalation")
        if level >= SUBSTANTIAL and threat != "adversarial":
            err(f"{aid} has SCRSS level {level}, which Table 29 gives only to adversarial-"
                "related risk")
        if level == 2 and threat == "adversarial":
            err(f"{aid} has SCRSS level 2, which Table 29 gives only to non-adversarial risk")
        if level == 2 and _id(a, "supplier") not in critical:
            err(f"{aid} has SCRSS level 2, which Table 29 gives only to risk of a critical "
                "supplier, system, component or high value asset")
        if level >= SUBSTANTIAL and escalation.get("fasc") != "mandatory":
            err(f"{aid} has a substantial risk at SCRSS level {level}, yet it is not shared "
                "with the FASC through the Information Sharing Agency as mandatory")
        if level < SUBSTANTIAL and escalation.get("fasc") == "mandatory":
            err(f"{aid} marks FASC sharing mandatory at SCRSS level {level}; sharing is "
                "mandatory only at levels 3 and above, voluntary below")
        if level >= SUBSTANTIAL and (escalation.get("legal_counsel") is not True
                                     or not _refs(escalation, "officials")):
            err(f"{aid} has a substantial risk not escalated to senior agency officials "
                "and legal counsel")
        if level >= SUBSTANTIAL:
            weighed = set(_refs(escalation, "considered"))
            for equity in WEIGHED_FIRST:
                if equity not in weighed:
                    err(f"{aid} responds to a substantial risk without weighing {equity} "
                        "equities before engaging the source")
    return out


# --- SCRM-006 ----------------------------------------------------------------------------
def threat_analysis(ctx: Context) -> list[RunFinding]:
    """P-14: the supply chain threat analysis captures the four kinds of data of p. 290 and
    the likelihood determination considers what p. 292 lists."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, ASSESS):
        return []
    analysis = _obj(scrm, "threat_analysis")
    out = [make("SCRM-006", f"the supply chain threat analysis captures no {kind} data",
                SCRM_FILE, None, {ASSESS})
           for kind in THREAT_DATA if kind not in _refs(analysis, "data")]
    out += [make("SCRM-006", f"the likelihood determination does not consider {need}",
                 SCRM_FILE, None, {ASSESS})
            for need in LIKELIHOOD_INPUTS if need not in _refs(analysis, "likelihood_inputs")]
    return out


# --- SCRM-007 ----------------------------------------------------------------------------
def contract_terms(ctx: Context) -> list[RunFinding]:
    """P-17: the C-SCRM requirements contracts carry are requirements of requirements.yaml
    allocated to the contract, and a contract term carries only those requirements."""
    if _missing(ctx, ALLOCATE, ACQUISITION_FILE):
        return [make("SCRM-007", "ART-REQ has no artifacts/data/scrm-acquisition.yaml, the "
                     "C-SCRM terms of the system's contracts", ACQUISITION_FILE, None,
                     {ALLOCATE})]
    acq = _doc(ctx, ACQUISITION_FILE)
    if acq is None or not _active(ctx, ALLOCATE):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-007", message, ACQUISITION_FILE, None, {ALLOCATE}))

    matrix = _doc(ctx, REQUIREMENTS_FILE)  # REQS-001 reports a missing matrix
    reqs = {_id(r): r for r in _list(matrix, "requirements")}
    carried = _refs(acq, "requirements")
    for rid in carried if matrix is not None else ():
        if rid not in reqs:
            err(f"C-SCRM requirement {rid} is no requirement in requirements.yaml")
        elif "contract" not in _refs(reqs[rid], "allocated_to"):
            err(f"C-SCRM requirement {rid} is not allocated to the contract in "
                "requirements.yaml")
    terms = _list(acq, "terms")
    for t in terms:
        for rid in _refs(t, "requirements"):
            if rid not in carried:
                err(f"the {t.get('term')} term carries {rid}, which is not a C-SCRM "
                    "requirement of the contract")
    return out



# --- SCRM-015 ----------------------------------------------------------------------------
def terms(ctx: Context) -> list[RunFinding]:
    """P-17: the contract carries each C-SCRM term of pp. 55-56, with grounds for termination
    when a change to supply chain risk cannot be mitigated (p. 55)."""
    acq = _doc(ctx, ACQUISITION_FILE)
    if acq is None or not _active(ctx, ALLOCATE):
        return []
    kinds = {_key(t, "term") for t in _list(acq, "terms")}
    # p. 56: flow-down "if and when applicable"; a contract recorded with no subcontractors
    # needs none.
    owed = [t for t in CONTRACT_TERMS
            if t != "flow-down" or acq.get("subcontractors") is not False]
    return [make("SCRM-015", f"the contract carries no {term} term for C-SCRM",
                 ACQUISITION_FILE, None, {ALLOCATE})
            for term in owed if term not in kinds]

# --- SCRMLC-001: C-SCRM in each step of the procurement life cycle -------------------------

PROCUREMENT_STEPS = ("plan-procurement", "define-requirements", "market-analysis",
                     "complete-procurement", "ensure-compliance", "monitor-performance")


def procurement_steps(ctx: Context) -> list[RunFinding]:
    """SCRMLC-001: P-17 records how C-SCRM considerations enter each step of the procurement and
    contract management life cycle SP 800-161 3.1.2 names from NISTIR 7622, and charge card
    purchases of ICT/OT when the program makes them."""
    acq = _doc(ctx, ACQUISITION_FILE)
    if acq is None or not _active(ctx, ALLOCATE):
        return []
    covered = {_key(s, "step") for s in _list(acq, "procurement_steps")}
    out = [make("SCRMLC-001", f"C-SCRM considerations are not incorporated into the {step} step "
                "of the procurement and contract management life cycle", ACQUISITION_FILE, None,
                {ALLOCATE}) for step in PROCUREMENT_STEPS if step not in covered]
    if acq.get("charge_card_purchases") is True and "charge-card-purchases" not in covered:
        out.append(make("SCRMLC-001", "the program makes ICT/OT charge card purchases and records "
                        "no C-SCRM considerations for them", ACQUISITION_FILE, None, {ALLOCATE}))
    return out


# --- SCRM-008 ----------------------------------------------------------------------------
def selection(ctx: Context) -> list[RunFinding]:
    """P-17: each supplier has a selection record with the prohibited supplier lists screened
    (pp. 254-255 are not inclusive); a listed supplier is not selected; an excluded source is
    excluded under legal authority with the contracting officer's and counsel's approval
    (DoDI 5000.83); open source software comes from a vetted and approved library."""
    acq, scrm = _doc(ctx, ACQUISITION_FILE), _doc(ctx, SCRM_FILE)
    if acq is None or scrm is None or not _active(ctx, ALLOCATE):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-008", message, ACQUISITION_FILE, None, {ALLOCATE}))

    sups = {_id(s): s for s in _list(scrm, "suppliers")}
    records = {_id(r, "supplier"): r for r in _list(acq, "selection")}
    for sid in sorted(i for i in records if i and i not in sups):
        err(f"selection record {sid} names no supplier of scrm.yaml")
    for sid in sorted(i for i in sups if i):
        record = records.get(sid)
        if record is None:
            err(f"{sid} has no selection record with due diligence and screening")
            continue
        # p. 254: the lists are "not inclusive"; the record holds the screenings done.
        screening = _list(record, "screening")
        if not screening:
            err(f"{sid} was screened against no prohibited supplier list")
        for entry in screening:
            if entry.get("result") == "listed" and record.get("selected") is True:
                err(f"{sid} is on the {entry.get('list')} list yet selected; a prohibited "
                    "supplier is excluded from procurement")
        exclusion = _obj(record, "exclusion")
        if record.get("selected") is False and not exclusion.get("authority"):
            err(f"{sid} is excluded on SCRM grounds without the legal authority exercised")
        if record.get("selected") is False and \
                not set(EXCLUSION_APPROVERS) <= set(_refs(exclusion, "approved_by")):
            err(f"the exclusion of {sid} is not approved by both the contracting officer and "
                "counsel")
        if sups[sid].get("kind") == "open-source" and \
                record.get("approved_source") != "vetted-library":
            err(f"{sid} supplies open source software from no vetted and approved library")
    return out


def _plan_owed(ctx: Context) -> bool:
    """SP 800-18r2 p. 47: the C-SCRM plan is developed for moderate- and high-impact systems; a
    low-impact system's security plan may identify inherited C-SCRM controls instead."""
    cat = ctx.facts.get("categorization") if isinstance(ctx.facts, dict) else None
    values = [cat.get(k) for k in ("c", "i", "a")] if isinstance(cat, dict) else []
    return not values or any(v in ("moderate", "high") for v in values)


# --- SCRM-009 ----------------------------------------------------------------------------
def plan_content(ctx: Context) -> list[RunFinding]:
    """S-4: the system C-SCRM plan describes the C-SCRM requirements the contracts carry,
    holds the supplier inventory with the criticality scrm.yaml gives, a relationship for each
    critical supplier, each consideration of SP 800-18r2, the system's information types, and
    is approved in coordination with the organization's C-SCRM PMO."""
    if _missing(ctx, PLAN, PLAN_FILE):
        return [make("SCRM-009", "ART-SSP has no artifacts/data/scrm-plan.yaml, the system "
                     "C-SCRM plan", PLAN_FILE, None, {PLAN})]
    doc = _doc(ctx, PLAN_FILE)
    if doc is None or not _active(ctx, PLAN):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-009", message, PLAN_FILE, None, {PLAN}))

    plan = _obj(doc, "plan")
    if not plan:
        if _plan_owed(ctx):
            err("a moderate- or high-impact system has no C-SCRM plan in scrm-plan.yaml")
        elif not _obj(doc, "inheritance"):
            err("a low-impact system without a C-SCRM plan states no inheritance of C-SCRM "
                "controls, tolerances and risk acceptance in scrm-plan.yaml")
        return out
    scrm = _doc(ctx, SCRM_FILE) or {}
    described = set(_refs(plan, "requirements"))
    for rid in _refs(_doc(ctx, ACQUISITION_FILE), "requirements"):
        if rid not in described:
            err(f"the C-SCRM plan does not describe C-SCRM requirement {rid} the contracts "
                "carry")
    rated = {_id(s, "supplier"): s.get("criticality") for s in _list(plan, "suppliers")}
    for sup in _list(scrm, "suppliers"):
        sid = _id(sup)
        if sid not in rated:
            err(f"{sid} is missing from the plan's supplier and component inventory")
        elif rated[sid] != sup.get("criticality"):
            err(f"the plan rates {sid} {rated[sid]} but scrm.yaml rates it "
                f"{sup.get('criticality')}")
    related = _ids(_list(plan, "relationships"), "supplier")
    for sid in _critical(scrm):
        if sid not in related:
            err(f"the plan defines no relationship between critical supplier {sid} and the "
                "system owner")
    held = _ids(_list(ctx.data(INFOTYPES_FILE), "information_types"))
    named = set(_refs(plan, "information_types"))
    for inf in sorted(held - named):
        err(f"the C-SCRM plan does not specify information type {inf}")
    for inf in sorted(named - held) if _doc(ctx, INFOTYPES_FILE) is not None else ():
        err(f"the C-SCRM plan names {inf}, which infotypes.yaml does not hold")
    pmo = _obj(_doc(ctx, ORG_FILE), "governance").get("pmo")
    if pmo in ("dedicated", "matrixed") and _obj(plan, "approval").get("pmo") != "coordinated":
        err("the plan's approval was not coordinated with the C-SCRM PMO the organization "
            "has")
    return out


# --- SCRM-032 (split from SCRM-009) -------------------------------------------------------
def plan_considerations(ctx: Context) -> list[RunFinding]:
    """S-4: the system C-SCRM plan addresses each consideration of SP 800-18r2 and does not
    call one inapplicable while scrm.yaml holds a supplier of that kind. SCRM-009 asks the
    plan itself."""
    doc = _doc(ctx, PLAN_FILE)
    if doc is None or not _active(ctx, PLAN):
        return []
    plan = _obj(doc, "plan")
    if not plan:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-032", message, PLAN_FILE, None, {PLAN}))

    scrm = _doc(ctx, SCRM_FILE) or {}
    considered = {_key(c, "kind"): c for c in _list(plan, "considerations")}
    for kind in PLAN_CONSIDERATIONS:
        if kind not in considered:
            err(f"the C-SCRM plan does not address consideration {kind}")
    for sup in _list(scrm, "suppliers"):
        kind = CONSIDERATION_OF_KIND.get(str(sup.get("kind")))
        if kind and considered.get(kind, {}).get("applies") is False:
            err(f"the plan says {kind} does not apply, yet {_id(sup)} is a supplier of that "
                "kind")
    return out


# --- SCRM-010 ----------------------------------------------------------------------------
def control_decisions(ctx: Context) -> list[RunFinding]:
    """S-2, recorded at S-4: each implemented C-SCRM control has someone responsible for it,
    only the authorizing official accepts the risk of removing one, a cloud service provider
    goes through FedRAMP first, a procurement's control selection consults information security
    personnel and avoids LPTA source selection, and the tailoring is coordinated among
    security, privacy and supply chain officials."""
    doc, scrm = _doc(ctx, PLAN_FILE), _doc(ctx, SCRM_FILE) or {}
    if doc is None or not _active(ctx, PLAN):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-010", message, PLAN_FILE, None, {TAILOR, PLAN}))

    controls = _obj(doc, "controls")
    for d in _list(controls, "decisions"):
        if d.get("decision") in ("selected", "tailored") and not d.get("owner"):
            err(f"{d.get('control')} is implemented with no one responsible for its execution")
        if d.get("decision") == "removed" and d.get("accepted_by") != "PER-AO":
            err(f"{d.get('control')} is removed from the baseline but its risk is accepted by "
                f"{d.get('accepted_by')}; only the authorizing official accepts that risk")
    clouds = _ids(_list(controls, "cloud"), "supplier")
    for sup in _list(scrm, "suppliers"):
        if sup.get("kind") == "cloud-service-provider" and _id(sup) not in clouds:
            err(f"cloud service provider {_id(sup)} has no FedRAMP record; FedRAMP guidelines "
                "apply first")
    for p in _list(controls, "procurement"):
        if not set(_refs(p, "consulted")) & set(SECURITY_PERSONNEL):
            err(f"the control selection for {p.get('supplier')} consulted no information "
                "security personnel")
        if p.get("source_selection") == "lpta":
            err(f"the acquisition from {p.get('supplier')} uses a lowest price, technically "
                "acceptable source selection")
    if controls.get("coordinated") is not True:
        err("security, privacy and supply chain officials did not coordinate the C-SCRM "
            "tailoring decisions")
    return out


def _sustaining(ctx: Context) -> bool:
    practices = _list(_obj(_doc(ctx, ORG_FILE), "maturity"), "practices")
    return any(p.get("tier") == "sustaining" and p.get("status") == "implemented"
               for p in practices)


# --- SCRM-011 ----------------------------------------------------------------------------
def supplier_continuity(ctx: Context) -> list[RunFinding]:
    """S-4: once the organization implements a sustaining practice, every critical supplier
    takes part in contingency planning, incident response, disaster recovery planning and
    their testing."""
    doc, scrm = _doc(ctx, PLAN_FILE), _doc(ctx, SCRM_FILE)
    if doc is None or scrm is None or not _active(ctx, PLAN):
        return []
    out: list[RunFinding] = []
    # p. 62: including critical suppliers in contingency, incident and recovery planning is a
    # sustaining practice, owed once the organization implements one (SCRM-024).
    owed = _sustaining(ctx)
    known = _ids(_list(scrm, "suppliers"))
    included = {_key(a, "activity"): set(_refs(a, "suppliers"))
                for a in _list(_obj(doc, "contingency"), "activities")}
    for activity, sups in sorted(included.items(), key=lambda kv: str(kv[0])):
        for sid in sorted(sups - known):
            out.append(make("SCRM-011", f"{activity} includes {sid}, which is no supplier in "
                            "scrm.yaml", PLAN_FILE, None, {PLAN}))
    for sid in _critical(scrm) if owed else ():
        for activity in INCLUDE_SUPPLIERS:
            if sid not in included.get(activity, set()):
                out.append(make("SCRM-011", f"critical supplier {sid} is not included in "
                                f"{activity}", PLAN_FILE, None, {PLAN}))
    return out


# --- SCRM-012 ----------------------------------------------------------------------------
def supplier_monitoring(ctx: Context) -> list[RunFinding]:
    """S-4, which S-5 builds on: the plan monitors every critical supplier after award for
    compliance, effectiveness and change."""
    doc, scrm = _doc(ctx, PLAN_FILE), _doc(ctx, SCRM_FILE) or {}
    if doc is None or not _active(ctx, PLAN):
        return []
    out: list[RunFinding] = []
    watched = {_id(m, "supplier"): set(_refs(m, "monitors"))
               for m in _list(_obj(doc, "monitoring"), "suppliers")}
    for sid in _critical(scrm):
        if sid not in watched:
            out.append(make("SCRM-012", f"critical supplier {sid} has no monitoring after "
                            "award", PLAN_FILE, None, {PLAN, MONITOR_DESIGN}))
            continue
        for kind in MONITORED:
            if kind not in watched[sid]:
                out.append(make("SCRM-012", f"monitoring of {sid} does not cover {kind}",
                                PLAN_FILE, None, {PLAN, MONITOR_DESIGN}))
    return out


# --- SCRM-013 ----------------------------------------------------------------------------
def response(ctx: Context) -> list[RunFinding]:
    """R-3: a supply chain risk outside tolerance has alternatives identified and evaluated,
    and the decision is one of them, taken at a level its reach calls for."""
    scrm = _doc(ctx, SCRM_FILE)
    if scrm is None or not _active(ctx, RESPOND):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-013", message, SCRM_FILE, None, {RESPOND}))

    responses = {_id(r, "assessment"): r for r in _list(scrm, "response")}
    assessments = _ids(_list(scrm, "assessments"))
    for aid in sorted(i for i in responses if i and i not in assessments):
        err(f"a response names {aid}, which is no assessment in scrm.yaml")
    for a in _list(scrm, "assessments"):
        aid = _id(a)
        if a.get("tolerance") in OUTSIDE_TOLERANCE and aid not in responses:
            err(f"{aid} is outside tolerance and has no R-3 response record")
    for aid, r in sorted(responses.items(), key=lambda kv: str(kv[0])):
        actions = {_key(o, "action") for o in _list(r, "alternatives")}
        if len(actions) < 2:
            err(f"the response to {aid} evaluates fewer than two distinct courses of action")
        decision = _obj(r, "decision")
        if _key(decision, "action") not in actions:
            err(f"the response to {aid} decides {decision.get('action')}, which is not among "
                "the alternatives evaluated")
        reach, level = r.get("reach"), decision.get("level")
        # p. 298: the risk executive (PER-RE) may delegate a decision; its delegation stands.
        if reach in REACH and level in REACH and REACH.index(level) < REACH.index(reach) \
                and decision.get("delegated_by") != "PER-RE":
            err(f"the response to {aid} is decided at {level} level for an impact that "
                f"reaches the {reach}")
    return out


# --- SCRM-014 ----------------------------------------------------------------------------
def reporting(ctx: Context) -> list[RunFinding]:
    """S-4: the plan sets the supply chain reporting the M-5 posture reports follow. A Level 1
    report, where the system has one, reaches the risk executive function with extent,
    effectiveness, urgent conditions, metrics and top risks (pp. 43, 62); a Level 3 one reaches
    the system owner with implementation, efficiency, effectiveness, exposure and metrics
    (p. 47); urgent threats reach the MDA, the authorizing official and the DoD CIO."""
    doc = _doc(ctx, PLAN_FILE)
    if doc is None or not _active(ctx, PLAN):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SCRM-014", message, PLAN_FILE, None, {PLAN}))

    reports = _list(doc, "reporting")
    if not reports:
        err("the C-SCRM plan sets no supply chain reporting for the M-5 posture reports")
        return out
    for r in reports:
        level = r.get("level")
        for content in REPORT_CONTENT.get(str(level), ()):
            if content not in _refs(r, "content"):
                err(f"the {level} supply chain report leaves out {content}")
        if level == "level-3" and not set(_refs(r, "audience")) & set(SYSTEM_OWNERS):
            err("the level-3 supply chain report does not reach the system owner")
        if level == "level-1" and "PER-RE" not in _refs(r, "audience"):
            err("the level-1 supply chain report does not reach the risk executive function")
    notified = set(_refs(_obj(doc, "urgent"), "notified"))
    for who, accepted in URGENT_RECIPIENTS.items():
        if not notified & set(accepted):
            err(f"mission-critical supply chain threats that cannot be addressed are not "
                f"notified to {who}")
    return out
