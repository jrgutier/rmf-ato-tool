"""What a cATO application shows, judged from artifacts/data/cato.yaml: CATO-*.

The DoD CIO cATO Implementation Guide (IG) and Evaluation Criteria (EVAL) set what the DoD CISO
considers when a Component presents a system for a cATO. M-6 records it in one file: the
assessment (team, plan, scoring against Table 2 of the IG, recommendation), the platform, its
monitoring, the strategy's triggers, metrics, people, training, process, risk tolerances, the
activities mapping and the SBOM. The rules judge the file whenever it exists, and require it once
the ledger holds an AD-CATO record, so a cATO is never decided without it and a run that seeks
none is not asked for one.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger

CATO_FILE = "artifacts/data/cato.yaml"
POAM_FILE = "artifacts/poam/items.yaml"
INVENTORY_FILE = "artifacts/data/inventory.yaml"
M6 = "M-6"
CATO = "AD-CATO"
APPROVERS = ("PER-AO", "PER-AODR")  # the AODR acts for the AO except the decision itself
# Table 2 of the IG: each cATO requirement and its level, threshold (T) or objective (O).
TABLE_2 = {
    "IC01": "T", "IC02": "T", "IC03": "T", "IC04": "T", "RA01": "T", "RA02": "T",
    "SA01": "T", "SA02": "T", "SA03": "O", "SA04": "T", "SA05": "T", "SA06": "T", "SA07": "T",
    "SA08": "T", "SA09": "T", "SA10": "T", "CM01": "O", "CM02": "T", "CM03": "T", "CM04": "O",
    "CM05": "T", "CM06": "T", "CM07": "T", "RM01": "T", "RM02": "T", "RM03": "T", "RM04": "T",
    "RM05": "T", "RM06": "O", "PP01": "O", "PP02": "T", "PP03": "O", "PP04": "T", "PP05": "T",
    "PP06": "T", "PP07": "T", "PP08": "T", "PP09": "O", "PP10": "T", "TP01": "T", "TP02": "O",
    "TP03": "T", "TP04": "O", "TP05": "T", "TP06": "T", "TP07": "T", "TP08": "O",
}
USE_CASES = ("production-in-factory", "production-outside-factory")  # IG Appendix A
STEPS = ("identify-assessors", "develop-plan", "assess-platform", "assess-teams",
         "assess-processes", "develop-recommendation", "authorize", "monitor")  # EVAL Figure 4
AREAS = ("platform", "process", "people")
CRITERIA = ("defined-documented", "evidence-of-use", "workforce-knowledge",
            "implementation-level")  # IG p. 10, high level evaluation criteria
EVIDENCE = ("documentation", "demonstration")
BRIEFED = ("critical-practices", "assessment-process", "evaluation-criteria")
MET, UNMET = "met", ("not-met", "partially-met")
RESULTS = (MET, *UNMET, "not-applicable")
ANALYSIS = ("existing-authorization", "conmon-strategy", "active-cyber-defense",
            "devsecops-processes", "supply-chain-processes", "scrm-guidance")  # EVAL p. 8
COMPETENCIES = ("conmon", "active-cyber-defense", "secure-supply-chain")
READINESS = ("very-low", "low", "moderate", "high", "very-high")
UNMITIGATED = ("high", "very-high")
FACTORY_ENVIRONMENTS = ("development", "test", "staging")
MONITORED_ENVIRONMENTS = ("development", "test", "production")
HOSTING = ("hyperscale-cloud", "dod-approved")
CNAPP = ("software-composition-analysis", "application-security-testing", "cspm", "ciem",
         "iac-scanning", "cwpp", "cdr")  # EVAL p. 15
ZERO_TRUST = ("ingress-egress", "east-west")
ACCESS_POINTS = ("cnap", "bcap")
SCANNING = ("dependency-analysis", "static-analysis", "dynamic-analysis", "prioritization",
            "adjudication")  # IG SA04
THRESHOLDS = ("guardrail", "control-gate", "notification")  # IG SA02
PIPELINE_FINDINGS = ("capture", "visualize", "feedback")  # IG SA10
AS_CODE = ("infrastructure", "configuration")
CSSP_WATCH = ("non-approved-actions", "malicious-actions")  # IG PP04
COUPLING = ("audit", "incident-response")
TRACKED_IN = ("deficiency-reports", "poam")
TRIGGER_ON = ("findings", "risk-tolerance", "threat-change", "mitigation-effectiveness")
THREATS = ("insider", "external")
METRIC_KINDS = ("hygiene", "trend", "feedback-frequency", "mitigation-effectiveness",
                "posture-dashboard")  # IG p. 14
GROUP = ("application-development-team", "ao-risk-assessment-team", "dsop-security-team",
         "mission-owner")  # IG p. 13 and RM01
FACTORY_GROUP = ("platform-team", "application-development-team", "ao-risk-assessment-team",
                 "mission-owner")  # IG p. 8, use case 1
EXERCISE_SUBJECTS = ("incident-response", "control-gate-trigger", "security-alert",
                     "elevated-privileges")  # EVAL p. 16
EXPERIENCE = ("secure-applications", "devsecops-culture", "security-automation-tools",
              "authorizations", "assessing-security-practices")
CULTURE_MEANS = ("training", "forums", "senior-leadership")
METHOD_SUBJECTS = ("reference-design", "security-automation-tools", "gates-and-tolerances",
                   "finding-adjudication", "root-cause-analysis", "feedback-loops",
                   "poam-and-dashboard")  # EVAL p. 16, IG p. 14
DSO_TEAMS = ("product", "dsop", "security")
TP08_SUBJECTS = ("threat-actor-analysis", "mitigation", "secure-code", "security-automation-tools",
                 "mitigation-effectiveness", "software-factory", "continuous-monitoring",
                 "risk-management")
EFFECTIVENESS_MEANS = ("dynamic-vulnerability-tools", "threat-actor-emulation",
                       "penetration-testing", "operations-analysis")  # IG p. 13
PEN_TESTING = ("threat-modeling", "methods", "assets")  # IG SA05
FEEDBACK_FROM = ("configuration-changes", "incident-analysis", "mitigation-effectiveness",
                 "threat-change", "non-approved-behavior")  # IG p. 9 b
FEEDBACK_ENVIRONMENTS = ("internal", "external")
CSSP_USE = ("non-approved-behavior", "incident-forensics", "threat-landscape")
TOLERANCE_AUTHORS = ("PER-PM", "mission-owner", "PER-SCA", "PER-AO")  # IG p. 9
CRITICALITY = ("mission", "system", "parameter")  # IG IC02
SBOM_FORMATS = ("spdx", "swid", "cyclonedx")
REFERENCE_DESIGN = "DoD Enterprise DevSecOps Reference Design"
ASSESSMENT_COVERS = ("threat-modeling", "vulnerability-analysis", "independent-verification",
                     "penetration-testing", "attack-surface-reviews", "manual-code-reviews",
                     "te-scope", "sast", "dast", "iast")  # EVAL pp. 11-12
IR_PROGRAM = ("policies", "plans", "procedures", "defined-roles", "training",
              "communication")  # EVAL p. 12


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    """A list field as read, or [] when it is malformed (RUN-FM-001 reports the schema)."""
    return value if isinstance(value, list) else []


def _dicts(items: Any) -> list[dict[str, Any]]:
    return [i for i in _list(items) if isinstance(i, dict)]


def _strs(value: Any) -> list[str]:
    """A list field's items as strings, so a malformed item is a finding, never a crash."""
    return [str(v) for v in _list(value)]


def lacks(value: Any, required: tuple[str, ...]) -> list[str]:
    """The required values a list field leaves out."""
    present = {str(v) for v in _list(value)}
    return [r for r in required if r not in present]


def _day(value: Any) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def _sought(ctx: Context) -> list[dict[str, Any]]:
    """The ledger's AD-CATO records: a cATO sought or decided."""
    return [r for r in _dicts(ctx.ledger) if r.get("decision") == CATO]


def _record(ctx: Context, rule: str) -> tuple[dict[str, Any] | None, list[RunFinding],
                                               Callable[[str], None]]:
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make(rule, message, CATO_FILE, None, {M6}))

    if not ctx.run.path(CATO_FILE).is_file():
        return None, out, err
    return _mapping(ctx.data(CATO_FILE)), out, err


# --- CATO-001: the assessment ------------------------------------------------------------------

def assessment(ctx: Context) -> list[RunFinding]:
    """CATO-001: the team, plan, criteria, evidence, scoring and recommendation (IG pp. 9-10,
    19; EVAL Figure 4)."""
    data, out, err = _record(ctx, "CATO-001")
    if data is None:
        if _sought(ctx):
            err(f"a cATO is sought and {CATO_FILE} is missing; M-6 records the cATO assessment "
                "there")
        return out
    if data.get("use_case") not in USE_CASES:
        err(f"a program applying for a cATO is already in one of the use case categories, not "
            f"{data.get('use_case')}")
    a = _mapping(data.get("assessment"))
    if gaps := lacks(a.get("steps"), STEPS):
        err(f"the cATO assessment leaves out the step {', '.join(gaps)}")
    team = _mapping(a.get("team"))
    if team.get("approved_by") not in APPROVERS:
        err(f"the AO approves the assessment team and their capabilities, not "
            f"{team.get('approved_by')}")
    if gaps := lacks(team.get("skills"), AREAS):
        err(f"the assessment team has no skills to assess the DevSecOps {', '.join(gaps)}")
    for m in _dicts(team.get("members")):
        if m.get("trained_on_method") is not True:
            err(f"{m.get('name')} is not trained on the cATO assessment process")
    plan = _mapping(a.get("plan"))
    unknown = [p for p in _strs(plan.get("key_practices")) if p not in TABLE_2]
    if unknown or not plan.get("key_practices"):
        err(f"the assessment plan identifies key practices that are no cATO requirement of "
            f"Table 2: {', '.join(map(str, unknown)) or 'none named'}")
    if plan.get("criteria_basis") != "DODCIO-CATO-EVAL":
        err(f"the evaluation criteria are based on the DevSecOps cATO Evaluation Criteria, not "
            f"{plan.get('criteria_basis')}")
    weights = _mapping(plan.get("weighting"))
    if not weights or any(str(k) not in AREAS and str(k) not in TABLE_2 for k in weights):
        err(f"the weighting criteria weigh {', '.join(map(str, weights)) or 'nothing'}, not the "
            "key areas or practices of Table 2")
    coordinated = _strs(plan.get("coordinated_with"))
    if "PER-PM" not in coordinated:
        err("the assessment plan is not coordinated with the program office (PER-PM)")
    if not set(APPROVERS) & set(coordinated):
        err("the assessment plan is not coordinated with the AO")
    if not set(APPROVERS) & set(_strs(plan.get("reviewed_with"))):
        err("the assessment plan is not reviewed with the AO for key practices and concerns")
    if gaps := lacks(plan.get("briefed_on"), BRIEFED):
        err(f"the assessed organization is not briefed on: {', '.join(gaps)}")
    criteria = _dicts(a.get("criteria"))
    for gap in lacks([c.get("criterion") for c in criteria], CRITERIA):
        err(f"the assessment does not judge the high level criterion {gap}")
    recommend = _mapping(a.get("recommendation")).get("recommend")
    for c in criteria:
        if c.get("result") != MET and (recommend == "authorize" or _sought(ctx)):
            err(f"the high level criterion {c.get('criterion')} is {c.get('result')}, and a "
                "cATO is recommended or decided")
    kinds = [e.get("kind") for e in _dicts(a.get("evidence"))]
    for gap in lacks(kinds, EVIDENCE):
        err(f"the evidence gathered on the practices includes no {gap}")
    roles = [o.get("role") for o in _dicts(_mapping(data.get("people")).get("org_chart"))]
    for i in _dicts(a.get("interviews")):
        if i.get("role") not in roles:
            err(f"the interview of {i.get('role')} represents no key role of the DSO team")
    return out


# --- CATO-012: the recommendation --------------------------------------------------------------

def recommendation(ctx: Context) -> list[RunFinding]:
    """CATO-012: the findings and recommendation reviewed with the PMO, AO and CISO, and the
    readiness determination briefed to the AO with the authorization's conditions (IG p. 10;
    EVAL Figure 4)."""
    data, out, err = _record(ctx, "CATO-012")
    if data is None:
        return out
    a = _mapping(data.get("assessment"))
    rec = _mapping(a.get("recommendation"))
    reviewers = _strs(rec.get("reviewed_with"))
    if "PER-PM" not in reviewers:
        err("the findings and recommendation are not reviewed with the program office (PER-PM)")
    if not set(APPROVERS) & set(reviewers):
        err("the findings and recommendation are not reviewed with the AO")
    if "PER-CISO" not in reviewers:
        err("the findings and recommendation are not reviewed with the CISO")
    if rec.get("readiness") not in READINESS:
        err(f"the final organizational readiness risk determination is {rec.get('readiness')}, "
            "not a risk level")
    if rec.get("briefing") != "ao-cato-decision-briefing":
        err(f"the recommendation reaches the AO in an AO cATO decision briefing, not "
            f"{rec.get('briefing')}")
    standing = ledger.in_force(_dicts(ctx.ledger), ledger.effects(ctx.run))
    conditions = {str(c.get("description")) for held in standing.values() if held.continuous
                  for c in _dicts(held.continuous.get("conditions"))}
    if left := sorted(conditions - set(map(str, _list(rec.get("conditions"))))):
        err(f"the decision briefing leaves out conditions of the authorization: {'; '.join(left)}")
    return out


# --- CATO-015: Table 2 scoring -----------------------------------------------------------------

def scoring(ctx: Context) -> list[RunFinding]:
    """CATO-015: the assessment scores Table 2 of the IG (p. 19) as _scoring says."""
    data, out, err = _record(ctx, "CATO-015")
    if data is None:
        return out
    a = _mapping(data.get("assessment"))
    _scoring(_dicts(a.get("scores")), _mapping(a.get("recommendation")),
             _strs(_mapping(a.get("plan")).get("key_practices")), bool(_sought(ctx)), err)
    return out


def _scoring(scores: list[dict[str, Any]], rec: dict[str, Any], selected: list[str],
             decided: bool, err: Callable[[str], None]) -> None:
    """Table 2 (IG p. 19): it is no conformance checklist, so the organization chooses its
    practices. Every threshold row is scored, and an objective row the plan selects; any row
    may be not-applicable with a reason. A threshold requirement must be met before a cATO is
    recommended or decided; an objective one may not be fully met initially."""
    for s in scores:
        ident = str(s.get("requirement"))
        if ident not in TABLE_2:
            err(f"{ident} is no cATO requirement of Table 2")
        if s.get("result") not in RESULTS:
            err(f"{ident} is scored {s.get('result')}, not met, partially-met, not-met or "
                "not-applicable")
        elif s.get("result") == "not-applicable" and not s.get("reason"):
            err(f"{ident} is scored not-applicable with no reason")
    scored = {str(s.get("requirement")) for s in scores}
    unscored = [r for r, level in TABLE_2.items()
                if (level == "T" or r in selected) and r not in scored]
    if unscored:
        err(f"threshold requirements and the objective ones the plan selects are not scored: "
            f"{', '.join(unscored)}")
    unmet = [str(s.get("requirement")) for s in scores
             if TABLE_2.get(str(s.get("requirement"))) == "T" and s.get("result") in UNMET]
    if unmet and (rec.get("recommend") == "authorize" or decided):
        err(f"a threshold requirement must be met: {', '.join(unmet)} unmet and a cATO is "
            "recommended or decided")
    for gap in lacks([s.get("area") for s in scores], AREAS):
        err(f"the assessment scores no {gap} against the evaluation and weighting criteria")


def met(data: dict[str, Any], row: str) -> bool:
    """Whether the assessment scores a Table 2 row met: an objective row is held to its
    practice only then, since it may not be fully met initially (IG p. 19)."""
    return any(str(s.get("requirement")) == row and s.get("result") == MET
               for s in _dicts(_mapping(data.get("assessment")).get("scores")))


# --- CATO-002: entry conditions ----------------------------------------------------------------

def entry(ctx: Context) -> list[RunFinding]:
    """CATO-002: a current ATO, no High or Very High unmitigated finding, the analysis and the
    three competencies (EVAL p. 8, IG p. 6, cATO memo)."""
    data, out, err = _record(ctx, "CATO-002")
    if data is None:
        return out
    a = _mapping(data.get("assessment"))
    day = _day(a.get("date"))
    effects = ledger.effects(ctx.run)
    standing = ledger.in_force(_dicts(ctx.ledger), effects, day) if day is not None else {}
    held = standing.get(str(data.get("underlying")))
    if held is None or effects.get(str(held.record.get("decision"))) != "authorize":
        err(f"the cATO assessment rests on {data.get('underlying')}, no current ATO in force on "
            f"{a.get('date')}")
    items = _dicts(_mapping(ctx.data(POAM_FILE)).get("items")) \
        if ctx.run.path(POAM_FILE).is_file() else []
    # The pursuit this assessment serves: its AD-CATO decision, the first on or after the
    # assessment. Before it, today's POA&M is the state the cATO is sought on; after it, only
    # findings identified by the decision date count, as later ones are a revocation matter.
    decision = min((d for r in _sought(ctx) if (d := _day(r.get("date"))) is not None
                    and day is not None and d >= day), default=None)
    open_high = [str(i.get("id")) for i in items
                 if i.get("residual_risk") in UNMITIGATED and i.get("status") != "completed"
                 and (decision is None
                      or (_day(_mapping(i.get("identified")).get("date")) or decision)
                      <= decision)]
    if open_high:
        err(f"{', '.join(open_high)}: a cATO needs a current ATO with no High or Very High "
            "unmitigated findings")
    if gaps := lacks(a.get("analysis"), ANALYSIS):
        err(f"the cATO analysis does not review the {', '.join(gaps)}")
    if gaps := lacks(a.get("competencies"), COMPETENCIES):
        err(f"the cATO evidence has not demonstrated the {', '.join(gaps)} competency")
    s = _mapping(data.get("strategy"))
    triggers = _dicts(s.get("triggers"))
    for t in triggers:
        if t.get("approved_by") not in APPROVERS:
            err(f"{t.get('id')}: an automated trigger rests on a threshold the AO approved, not "
                f"{t.get('approved_by')}")
        if t.get("plan") not in COUPLING:
            err(f"{t.get('id')}: automated triggers sit within the auditing and incident "
                f"response plans, not {t.get('plan')}")
    for gap in lacks([t.get("threat") for t in triggers], THREATS):
        err(f"the automated triggers and approved thresholds include no {gap} threats")
    if gaps := lacks(s.get("issue_investigation"), ("PER-CSSP", "PER-SCA")):
        err(f"an issue or anomaly is investigated and mitigated by the CSSP along with the SCA; "
            f"{', '.join(gaps)} is missing")
    return out


# --- CATO-003: the platform --------------------------------------------------------------------

def platform(ctx: Context) -> list[RunFinding]:
    """CATO-003: the DevSecOps platform on an approved reference design, its hosting and what its
    automation enables (EVAL pp. 9, 14; IG pp. 8, 11)."""
    data, out, err = _record(ctx, "CATO-003")
    if data is None:
        return out
    p = _mapping(data.get("platform"))
    design = _mapping(p.get("reference_design"))
    if design.get("approved") is not True:
        err(f"the DSOP implements an approved DevSecOps Reference Design, and "
            f"{design.get('name')} is not one")
    if not str(design.get("name") or "").startswith(REFERENCE_DESIGN):
        err(f"the DSOP adheres to {design.get('name')}, which is not identified as a DoD "
            "Enterprise DevSecOps Reference Design")
    auth = _mapping(p.get("authorization"))
    if auth.get("status") != "authorized" or auth.get("continuous_monitoring") is not True:
        err("the DevSecOps platform is not already authorized to operate and in a state of "
            "continuous monitoring")
    if "continuous-monitoring" not in _strs(auth.get("inherited")):
        err("the cATO does not inherit the DSOP's applicable continuous monitoring practices")
    if p.get("delivery") != "own-system-as-a-service":
        err(f"the DSOP is delivered and operated as its own system and provided as a service, "
            f"not {p.get('delivery')}")
    hosting = _mapping(p.get("hosting"))
    if hosting.get("kind") not in HOSTING:
        err(f"the application hosting environment is a hyperscale cloud or another DoD approved "
            f"environment, not {hosting.get('kind')}")
    if gaps := lacks(hosting.get("environments"), FACTORY_ENVIRONMENTS):
        err(f"the hosting environment provides no {', '.join(gaps)} environment")
    if gaps := lacks(p.get("enables"), COMPETENCIES):
        err(f"the DSOP automation does not enable {', '.join(gaps)}")
    gates = {str(g.get("id")) for g in _dicts(p.get("control_gates"))}
    rails = {str(g.get("id")) for g in _dicts(p.get("guardrails"))}
    if all(x.get("collects_evidence") is not True
           or not set(_strs(x.get("guardrails"))) & rails
           or not set(_strs(x.get("control_gates"))) & gates
           for x in _dicts(p.get("pipelines"))):
        err("no DevSecOps pipeline has automated guardrails and control gates that collect "
            "evidence for continuous risk determinations")
    return out


# --- CATO-004: monitoring, active cyber defense and vulnerability management ------------------

def monitoring(ctx: Context) -> list[RunFinding]:
    """CATO-004: what production monitoring and the CSSP watch, the SOC, and how vulnerabilities
    are tracked and fixed (IG pp. 11-12, 16, PP04, PP05; EVAL pp. 12-13)."""
    data, out, err = _record(ctx, "CATO-004")
    if data is None:
        return out
    m = _mapping(data.get("monitoring"))
    siem = _mapping(m.get("siem_analytics"))
    if siem.get("developed_by") != "application-manager" or siem.get("provided_to") != "PER-CSSP":
        err("the application manager develops SIEM monitoring analytics for unique application "
            "events and provides them to the CSSP")
    if m.get("traffic_inspection") != "unique-application":
        err(f"production monitoring is configured for unique application traffic inspection, "
            f"not {m.get('traffic_inspection')}")
    sidecar = _mapping(m.get("sidecar"))
    if sidecar.get("used") is True and sidecar.get("configured_for") != "unique-application":
        err("the security sidecar is not configured for unique application traffic inspection "
            "and handling of events")
    if gaps := lacks(m.get("cssp_application_monitoring"), CSSP_WATCH):
        err(f"CSSP application monitoring does not watch for {', '.join(gaps)}")
    if m.get("soc") != "local" or m.get("cssp") != "external":
        err("active cyber defense needs a local SOC and an external CSSP")
    if m.get("acd_methodology") != "documented":
        err("the methodology supporting active cyber defense is not documented")
    v = _mapping(m.get("vulnerability_management"))
    if v.get("expectations_published") is not True or v.get(
            "remediation_timelines_published") is not True:
        err("expectations and timelines for corrective action plans and remediation are not "
            "published")
    if v.get("staffing_plan_published") is not True:
        err("no published plan ensures the availability of staff and resources")
    if gaps := lacks(v.get("tracked_in"), TRACKED_IN):
        err(f"findings are not tracked using {', '.join(gaps)}")
    if v.get("documented_on") != "discovery":
        err(f"critical and moderate vulnerabilities are documented upon discovery, not "
            f"{v.get('documented_on')}")
    if v.get("timeframe_accepted_by") not in APPROVERS:
        err(f"critical and moderate vulnerabilities are mitigated within a timeframe acceptable "
            f"to the AO, not {v.get('timeframe_accepted_by')}")
    if m.get("assessment_scope") != "full-lifecycle":
        err("the security assessment does not cover the DSOP full lifecycle and the delivery "
            "pipeline")
    if gaps := lacks(m.get("assessment_covers"), ASSESSMENT_COVERS):
        err(f"the security assessment of the DSOP does not address {', '.join(gaps)}")
    return out


# --- CATO-005: control gates and guardrails ----------------------------------------------------

def gates(ctx: Context) -> list[RunFinding]:
    """CATO-005: each control gate and guardrail described, tied to a risk tolerance and to
    incident response, demonstrated, and the thresholds set (EVAL pp. 15-16; IG pp. 12-13,
    SA02, SA10, PP08)."""
    data, out, err = _record(ctx, "CATO-005")
    if data is None:
        return out
    p = _mapping(data.get("platform"))
    tolerances = {str(t.get("id")): t for t in _dicts(data.get("tolerances"))}
    irp = ctx.run.artifact_md("ART-IRP").is_file()
    for g in _dicts(p.get("control_gates")):
        ident = g.get("id")
        for name, what in (("opens_on", "opens"), ("closes_on", "closes")):
            if not str(g.get(name) or "").strip():
                err(f"{ident}: the description does not say what triggers cause the gate to "
                    f"{what}")
        if not str(g.get("alert_trigger") or "").strip():
            err(f"{ident}: the description does not say what triggers an alert")
        if not str(g.get("alert_responder") or "").startswith("PER-"):
            err(f"{ident}: the description of how to respond to the gate's alert names no role "
                f"that responds: {g.get('alert_responder')}")
        if g.get("demonstrated") not in ("demonstration", "screenshot"):
            err(f"{ident}: each control gate is demonstrated in action or shown in dashboard "
                f"screen shots, not {g.get('demonstrated')}")
        if str(g.get("tolerance")) not in tolerances:
            err(f"{ident}: agreed-to risk tolerances are implemented in the pipeline control "
                f"gates, and {g.get('tolerance')} is no tolerance")
        if not str(g.get("trigger_routing") or "").startswith("PER-"):
            err(f"{ident}: the control gate routes its event triggers to no role for escalating "
                f"resolution: {g.get('trigger_routing')}")
        if g.get("described_in") != "ART-IRP":
            err(f"{ident}: control gate processes are described in the incident response "
                f"management material, not {g.get('described_in')}")
        elif not irp:
            err(f"{ident}: control gate processes are described in the incident response plan, "
                "and the run has no ART-IRP")
    for g in _dicts(p.get("guardrails")):
        ident = g.get("id")
        if not str(g.get("out_of_tolerance") or "").strip():
            err(f"{ident}: no process says what occurs when something is out of the guardrail's "
                "risk tolerance")
        if str(g.get("tolerance")) not in tolerances:
            err(f"{ident}: guardrail promotion rules rest on an agreed risk tolerance, and "
                f"{g.get('tolerance')} is no tolerance")
        if g.get("described_in") != "ART-IRP":
            err(f"{ident}: guardrail processes are described in the incident response management "
                f"material, not {g.get('described_in')}")
        elif not irp:
            err(f"{ident}: guardrail processes are described in the incident response plan, and "
                "the run has no ART-IRP")
    if data.get("use_case") == "production-in-factory" and all(
            t.get("applies_to") != "dsop" for t in tolerances.values()):
        err("the DSOP's single authorization boundary has no risk tolerance to set the "
            "guardrail and control gate promotion rules")
    for t in tolerances.values():
        if t.get("applies_to") == "application" and t.get("set_by") != "dsop-team":
            err(f"{t.get('id')}: the DSOP team establishes the risk tolerances required for "
                f"applications traversing the pipeline, not {t.get('set_by')}")
    if gaps := lacks(p.get("thresholds"), THRESHOLDS):
        err(f"the platform does not set {', '.join(gaps)} thresholds")
    if gaps := lacks(p.get("pipeline_findings"), PIPELINE_FINDINGS):
        err(f"security findings during pipeline runs are not {', '.join(gaps)}d")
    return out


# --- CATO-006: attack surface, cloud protection, scanning and the SBOM -------------------------

def supply_chain(ctx: Context) -> list[RunFinding]:
    """CATO-006: zero trust, the access point, CNAPP on a cloud host, IaC and CaC, scanning and
    adjudication (IG Table 2 RA, SA; EVAL pp. 7, 15)."""
    data, out, err = _record(ctx, "CATO-006")
    if data is None:
        return out
    p = _mapping(data.get("platform"))
    if gaps := lacks(p.get("zero_trust"), ZERO_TRUST):
        err(f"DSOP zero trust does not enforce {', '.join(gaps)} traffic")
    if p.get("access_point") not in ACCESS_POINTS:
        err(f"the platform leverages a Cloud Native Access Point or Boundary Cloud Access Point, "
            f"not {p.get('access_point')}")
    hosting = _mapping(p.get("hosting"))
    if hosting.get("kind") == "hyperscale-cloud" and hosting.get("cloud") is not True:
        err("the hosting environment is a hyperscale cloud, so it is hosted on a cloud: "
            f"cloud is {hosting.get('cloud')}")
    cloud = hosting.get("kind") == "hyperscale-cloud" or hosting.get("cloud") is True
    if cloud and (gaps := lacks(p.get("cnapp"), CNAPP)):
        err(f"an environment hosted on a cloud deploys a CNAPP, and it lacks {', '.join(gaps)}")
    if gaps := lacks(p.get("as_code"), AS_CODE):
        err(f"the platform does not rely on {', '.join(gaps)} as code to avoid environment drift")
    if met(data, "SA03") and p.get("configuration_validation") != "automated":
        err("security control configurations and their validation are not automated")
    if gaps := lacks(p.get("scanning"), SCANNING):
        err(f"security scanning leaves out {', '.join(gaps)}")
    if _mapping(p.get("adjudication")).get("false_positives") != "captured-and-analyzed":
        err("findings are adjudicated without capturing and analyzing false positives")
    return out


# --- CATO-014: the SBOM ------------------------------------------------------------------------

def sbom(ctx: Context) -> list[RunFinding]:
    """CATO-014: the SBOM of the DSOP and of the applications passing through it, its format,
    frequency, archive and analysis (EVAL pp. 14-15; IG p. 16)."""
    data, out, err = _record(ctx, "CATO-014")
    if data is None:
        return out
    s = _mapping(data.get("sbom"))
    dsop = _mapping(s.get("dsop"))
    if dsop.get("provided") is not True or not str(dsop.get("statement") or "").strip():
        err("no SBOM for the DSOP with a statement of how it was developed")
    if s.get("applications") != "automated-export":
        err(f"the SBOM of applications passing through the DSOP is an automated export, not "
            f"{s.get('applications')}")
    # The format is not yet mandated (EVAL p. 14): another one stands with a stated reason.
    if s.get("format") not in SBOM_FORMATS and not str(s.get("format_reason") or "").strip():
        err(f"the SBOM is in one of the common formats SPDX, SWID or CycloneDX, not "
            f"{s.get('format')}, or the record states why another format is used")
    if not str(s.get("frequency") or "").strip():
        err("the SBOM format is specified but not how often it is generated")
    if s.get("archive") not in ("with-assessment-evidence", "separate"):
        err(f"no archive of SBOMs is maintained for products passing through pipelines: "
            f"{s.get('archive')}")
    if not str(s.get("analysis") or "").strip() or not str(s.get("new_cve") or "").strip():
        err("the record does not explain how SBOMs are analyzed and how a new CVE is applied "
            "to them")
    if s.get("composition_analysis") != "in-sbom-creation":
        err("software composition analysis is not addressed in the creation of the SBOMs")
    return out


# --- CATO-007: the monitoring strategy and its metrics ----------------------------------------

def strategy(ctx: Context) -> list[RunFinding]:
    """CATO-007: what the system strategy states for a cATO, and its metrics (EVAL pp. 10-13;
    IG pp. 13-16, PP03, CM07, RM06)."""
    data, out, err = _record(ctx, "CATO-007")
    if data is None:
        return out
    m = _mapping(data.get("monitoring"))
    if m.get("vulnerability_tracking") != "all-assets":
        err(f"the strategy plans to assess and track vulnerabilities on all the system assets, "
            f"not {m.get('vulnerability_tracking')}")
    if gaps := lacks(m.get("audit_ir_coupling"), COUPLING):
        err(f"the strategy is not tightly coupled with the {', '.join(gaps)} strategy")
    if m.get("pipeline_monitored") is not True:
        err("the software development pipeline and its environment are not monitored")
    if m.get("attack_events") != "evaluated":
        err("events that could help detect, understand, or recover from an attack are not "
            "evaluated")
    if m.get("artifact_reassessment") != "continuous":
        err("artifacts in the artifact repository are not continuously reassessed for residual "
            "risk")
    if gaps := lacks(m.get("environments"), MONITORED_ENVIRONMENTS):
        err(f"continuous monitoring is not implemented in the {', '.join(gaps)} environment")
    if met(data, "PP03") and m.get("soc_strategy") != "software-factory":
        err("the SOC continuous monitoring strategy does not use the software factory")
    metrics = _dicts(data.get("metrics"))
    for gap in lacks([x.get("kind") for x in metrics], METRIC_KINDS):
        err(f"the strategy determines no {gap} metric")
    for x in metrics:
        if x.get("collection") not in ("automated", "manual"):
            err(f"{x.get('id')}: a metric is collected automatically or manually, not "
                f"{x.get('collection')}")
    if all(x.get("trend_analysis") is not True for x in metrics):
        err("no metric is identified, collected and trend analyzed")
    return out


# --- CATO-008: people -------------------------------------------------------------------------

def people(ctx: Context) -> list[RunFinding]:
    """CATO-008: the risk governance group, insider threat, the organization chart, tabletop
    exercises, onboarding, experience and culture change (EVAL pp. 10, 16-17; IG pp. 8, 13-14,
    RM01, RM05, TP02, TP04, TP06)."""
    data, out, err = _record(ctx, "CATO-008")
    if data is None:
        return out
    p = _mapping(data.get("people"))
    group = _mapping(p.get("risk_governance_group"))
    if gaps := lacks(group.get("members"), GROUP):
        err(f"the cybersecurity risk governance group has no member from the {', '.join(gaps)}")
    if data.get("use_case") == "production-in-factory" and (
            gaps := lacks(group.get("members"), FACTORY_GROUP)):
        err(f"with production in the factory the group managing the risk includes the "
            f"{', '.join(gaps)}")
    if not group.get("periodic_review") or not str(group.get("ad_hoc_resolution") or "").strip():
        err("the group sets no periodic review of risk and no approach for ad-hoc resolution of "
            "risks that exceed thresholds")
    if gaps := lacks(p.get("threats_tracked"), THREATS):
        err(f"the risk management strategy does not track {', '.join(gaps)} threats")
    insider = _mapping(p.get("insider_threat"))
    wg = _mapping(insider.get("working_group"))
    if wg.get("established") is not True or wg.get("active") is not True \
            or wg.get("chair") != "senior-leadership":
        err("no insider threat working group is established, active, and chaired by senior "
            "leadership")
    if not insider.get("critical_areas"):
        err("the insider threat working group identifies no critical areas for review")
    triggers = {str(t.get("id")): t
                for t in _dicts(_mapping(data.get("strategy")).get("triggers"))}
    for ident in _strs(insider.get("thresholds")):
        if _mapping(triggers.get(ident)).get("threat") != "insider":
            err(f"{ident}: the insider threat working group's threshold for analysis is no "
                "insider threat trigger of the strategy")
    chart = _dicts(p.get("org_chart"))
    if not chart:
        err("no organization chart shows the roles within the DSO Team")
    for o in chart:
        if o.get("team") not in DSO_TEAMS:
            err(f"{o.get('role')}: the organization chart shows the roles within the DSO Team's "
                f"product, DSOP and security teams, not {o.get('team')}")
    if gaps := lacks(p.get("ir_program"), IR_PROGRAM):
        err(f"the evidence of the incident response program includes no {', '.join(gaps)}")
    exercises = _dicts(p.get("tabletop_exercises"))
    if all(e.get("participants") != "whole-team" or not e.get("after_action_report")
           for e in exercises):
        err("no tabletop exercise with the whole team produced an After Action Report")
    for gap in lacks([s for e in exercises for s in _list(e.get("subjects"))], EXERCISE_SUBJECTS):
        err(f"the tabletop exercises do not include {gap}")
    onboarding = _mapping(p.get("onboarding"))
    if onboarding.get("by_role") is not True or onboarding.get("offboarding") is not True:
        err("no onboarding and offboarding process is defined for team members based on their "
            "role")
    if onboarding.get("completed_by") != "all-personnel":
        err(f"all personnel have gone through onboarding without regard to rank or position, "
            f"not {onboarding.get('completed_by')}")
    if gaps := lacks(p.get("experience"), EXPERIENCE[:-1] + (
            EXPERIENCE[-1:] if met(data, "TP04") else ())):
        err(f"no member of the team has experience in {', '.join(gaps)}")
    culture = _mapping(p.get("culture_change"))
    if not culture.get("challenges") or not str(culture.get("approach") or "").strip():
        err("cultural change challenges and the change management approach are not identified")
    if gaps := lacks(culture.get("means"), CULTURE_MEANS):
        err(f"cultural change challenges are not addressed with {', '.join(gaps)}")
    if met(data, "TP02") and p.get("position_descriptions") != "dcwf":
        err(f"hiring position descriptions and certification requirements follow the DCWF, not "
            f"{p.get('position_descriptions')}")
    return out


# --- CATO-009: training -----------------------------------------------------------------------

def training(ctx: Context) -> list[RunFinding]:
    """CATO-009: the documented training process and who on which team was trained on what
    (EVAL pp. 13, 16-17; IG pp. 13-14, TP01, TP03, TP05, TP07, TP08)."""
    data, out, err = _record(ctx, "CATO-009")
    if data is None:
        return out
    t = _mapping(data.get("training"))
    process = _mapping(t.get("process"))
    if process.get("documented") is not True or process.get("certification") is not True:
        err("the DevSecOps education, certification, and training process is not documented")
    if process.get("validation") is not True:
        err("no training compliance and validation process ensures team members meet their "
            "requirements")
    records = _dicts(t.get("records"))
    members = [r.get("member") for r in records]
    for role in (o.get("role") for o in _dicts(_mapping(data.get("people")).get("org_chart"))):
        if role not in members:
            err(f"{role}: no verification of appropriate training for this member of the team")
    for gap in lacks([r.get("team") for r in records], DSO_TEAMS):
        err(f"no member of the {gap} team has a training record")
    if all(r.get("team") != "cssp" or "devsecops-principles" not in _list(r.get("subjects"))
           for r in records):
        err("no evidence that the CSSP received training on DevSecOps principles")
    if lacks([s for r in records if r.get("team") == "leadership"
              for s in _list(r.get("subjects"))], ("software-modernization", "cato-method")):
        err("leadership training on software modernization and cATO methods is not tracked")
    if met(data, "TP08") and (
            gaps := lacks([s for r in records for s in _list(r.get("subjects"))], TP08_SUBJECTS)):
        err(f"the team is not trained in {', '.join(gaps)}")
    if all(x.get("shadowed") not in members for x in _dicts(t.get("cross_functional"))):
        err("cross-functional team training and shadowing are not documented")
    return out


# --- CATO-013: training in the cATO method ----------------------------------------------------

def method_training(ctx: Context) -> list[RunFinding]:
    """CATO-013: the product, DSOP and security teams trained in the cATO method on each subject
    EVAL p. 16 and IG p. 14 list, judged on the teams together: training is by role."""
    data, out, err = _record(ctx, "CATO-013")
    if data is None:
        return out
    subjects = [s for r in _dicts(_mapping(data.get("training")).get("records"))
                if r.get("team") in DSO_TEAMS for s in _list(r.get("subjects"))]
    if gaps := lacks(subjects, METHOD_SUBJECTS):
        err(f"no member of the product, DSOP or security team is trained in the cATO method on "
            f"{', '.join(gaps)}")
    return out


# --- CATO-010: process ------------------------------------------------------------------------

def process(ctx: Context) -> list[RunFinding]:
    """CATO-010: active testing, feedback from cyber operations, business rules (EVAL pp. 11,
    14; IG pp. 8-9, 12-13, SA05, CM06, PP09)."""
    data, out, err = _record(ctx, "CATO-010")
    if data is None:
        return out
    p = _mapping(data.get("process"))
    testing = _mapping(p.get("active_testing"))
    if testing.get("basis") != "real-world-adversary-tactics" \
            or testing.get("cadence") != "ongoing":
        err("security testing is not ongoing against adversary tactics and techniques based on "
            "real-world observations")
    if not str(testing.get("strategy") or "").strip() \
            or not str(testing.get("budget") or "").strip():
        err("no strategy and budget for automated cybersecurity testing resources")
    kinds = {i.get("kind") for i in _dicts(testing.get("iterations"))}
    if not {"analysis", "penetration-test"} <= kinds:
        err("the ongoing iterations of cybersecurity analysis and penetration testing are not "
            "documented")
    if gaps := lacks(p.get("control_effectiveness"), EFFECTIVENESS_MEANS):
        err(f"security control effectiveness is not determined with {', '.join(gaps)}")
    if gaps := lacks(p.get("pen_testing"), PEN_TESTING):
        err(f"pen-testing and threat emulation leave out {', '.join(gaps)}")
    f = _mapping(p.get("feedback"))
    if gaps := lacks(f.get("environments"), FEEDBACK_ENVIRONMENTS):
        err(f"no active feedback mechanism for the {', '.join(gaps)} production environment")
    if gaps := lacks(f.get("from_cyber_operations"), FEEDBACK_FROM):
        err(f"feedback from cyber operations on {', '.join(gaps)} is not monitored for the risk "
            "response")
    if f.get("incident_reviews_with") != "devsecops-team":
        err(f"application cybersecurity incidents are reviewed in collaboration with the "
            f"DevSecOps team, not {f.get('incident_reviews_with')}")
    if gaps := lacks(f.get("cssp_monitoring"), CSSP_USE):
        err(f"the DevSecOps team does not leverage CSSP monitoring for {', '.join(gaps)}")
    if p.get("compliance_monitoring") != "changing-threat":
        err("control compliance and continued effectiveness are not monitored against the "
            "changing threat")
    if not p.get("business_rules"):
        err("the system establishes no business rules")
    return out


# --- CATO-011: risk tolerances and the activities mapping -------------------------------------

def tolerances(ctx: Context) -> list[RunFinding]:
    """CATO-011: the cATO risk tolerances, who sets them and on what basis, the event triggers,
    and the DevSecOps activities mapping (EVAL pp. 10, 15; IG pp. 8-9, IC02, CM02, PP01)."""
    data, out, err = _record(ctx, "CATO-011")
    if data is None:
        return out
    tols = _dicts(data.get("tolerances"))
    if not tols:
        err("the cATO risk management strategy establishes no risk tolerances")
    for t in tols:
        ident = t.get("id")
        if t.get("basis") != "component-risk-posture-guidance":
            err(f"{ident}: cATO risk tolerances are based on the Component's risk posture "
                f"guidance, not {t.get('basis')}")
        if t.get("criticality") not in CRITICALITY:
            err(f"{ident}: the tolerance is not set from the criticality of mission, systems, "
                f"or key system parameters, but {t.get('criticality')}")
    authors = [a for t in tols for a in _strs(t.get("developed_by"))]
    authors += ["PER-AO"] if set(APPROVERS) & set(authors) else []
    if gaps := lacks(authors, TOLERANCE_AUTHORS):
        err(f"the risk tolerances are not developed collaboratively with {', '.join(gaps)}")
    if data.get("use_case") == "production-outside-factory" and all(
            "production-ao" not in _strs(t.get("developed_by")) for t in tols):
        err("with production outside the DSOP the risk governance team works with the "
            "production environment's AO on the tolerances")
    triggers = _dicts(_mapping(data.get("strategy")).get("triggers"))
    for gap in lacks([t.get("on") for t in triggers], TRIGGER_ON):
        err(f"no event trigger is established on {gap}")
    mapping = _mapping(data.get("activities_mapping"))
    if mapping.get("guidebook") != "DevSecOps Fundamentals Guidebook Activities and Tools":
        err(f"the activities are mapped from the DevSecOps Activities and Tools Guidebook, not "
            f"{mapping.get('guidebook')}")
    activities = _dicts(mapping.get("activities"))
    for gap in lacks([a.get("kind") for a in activities], ("required", "preferred")):
        err(f"the mapping of DevSecOps activities to the implementation has no {gap} activity")
    roadmap = {str(r.get("id")) for r in _dicts(mapping.get("roadmap"))}
    for a in activities:
        if a.get("implemented") is not True and str(a.get("roadmap")) not in roadmap:
            err(f"{a.get('activity')}: an activity not implemented has no item on the activities "
                "and tools roadmap")
    if all(a.get("demonstrated") is not True for a in activities):
        err("no activity of the Activities and Tools Guidebook is demonstrated")
    if not mapping.get("additional_documentation"):
        err("the additional documentation listed with the mapped activities is not included")
    return out


# --- CATT-001: the Table 2 practices no other rule holds --------------------------------------

THREAT_TARGETS = ("network-data-architecture", "mission-assets",
                  "cybersecurity-architecture")  # IG IC03
RISK_ASSESSMENTS = ("mission-based", "threat-based", "resiliency-survivability-based")  # SA06
CYBER_AREAS = ("cybersecurity", "cyber-resiliency", "cyber-survivability")  # IG SA07, RM02
CONFIGURATIONS = ("system", "control")  # IG SA08
PRIORITIZATION = ("vulnerability-identification", "impact-analysis")  # IG RM03
PROACTIVE = ("preventive", "resiliency")  # IG CM01: "preventive / resiliency", either
VALIDATED = ("secure-configurations", "control-compliance")  # IG p. 13
CHECKS = ("periodic", "continuous")  # IG p. 12: periodic checks of secure configurations
CHANGE_MONITORS = (*CHECKS, "on-change")  # IG CM05: monitor for change, by any method


def owed(ctx: Context, data: dict[str, Any], row: str) -> bool:
    """Whether the practice of a Table 2 row is owed (IG p. 19): an objective row only once it is
    scored met; a threshold row unless it is scored not-applicable, and, while it is not met,
    only once a cATO is recommended or decided, since a threshold row must be met by then."""
    a = _mapping(data.get("assessment"))
    result = next((s.get("result") for s in _dicts(a.get("scores"))
                   if str(s.get("requirement")) == row), None)
    if TABLE_2[row] == "O":
        return result == MET
    if result == "not-applicable":
        return False
    recommended = _mapping(a.get("recommendation")).get("recommend") == "authorize"
    return result == MET or recommended or bool(_sought(ctx))


def practices(ctx: Context) -> list[RunFinding]:
    """CATT-001: the Table 2 practices and DSOP key practices the record shows performed (IG
    pp. 11-13, 19-21: IC03, IC04, SA06-SA08, CM01, CM05, CM06, RM02, RM03, PP06, PP07), each
    judged only while owed() says it is owed."""
    data, out, err = _record(ctx, "CATT-001")
    if data is None:
        return out
    p = _mapping(data.get("practices"))
    if owed(ctx, data, "IC03") and (gaps := lacks(p.get("threats_identified_to"),
                                                  THREAT_TARGETS)):
        err(f"cyber threats are not identified to the {', '.join(gaps)}")
    # IC04 names no kind of evidence, so any collected evidence holds it.
    if owed(ctx, data, "IC04") and not _strs(p.get("baseline_posture_evidence")):
        err("no evidence is collected for establishing a baseline risk posture")
    if owed(ctx, data, "SA06") and (gaps := lacks(p.get("risk_assessments"), RISK_ASSESSMENTS)):
        err(f"the risk assessments performed leave out the {', '.join(gaps)} one")
    if owed(ctx, data, "SA07") and (gaps := lacks(p.get("verification_validation"),
                                                  CYBER_AREAS)):
        err(f"verification and validation testing leaves out the {', '.join(gaps)} "
            "requirements")
    if owed(ctx, data, "SA08") and (gaps := lacks(p.get("configuration_management"),
                                                  CONFIGURATIONS)):
        err(f"configuration management leaves out the {', '.join(gaps)} configurations")
    aggregation = _mapping(p.get("posture_aggregation"))
    if owed(ctx, data, "RM02"):
        if not str(aggregation.get("method") or "").strip():
            err("no method is established for aggregating findings into a risk posture")
        if gaps := lacks(aggregation.get("covers"), CYBER_AREAS):
            err(f"the method aggregating findings into a risk posture leaves out "
                f"{', '.join(gaps)}")
    if owed(ctx, data, "RM03") and (gaps := lacks(p.get("risk_prioritization"),
                                                  PRIORITIZATION)):
        err(f"risk prioritization is not established on {', '.join(gaps)}")
    if owed(ctx, data, "CM01"):
        if p.get("behavior_monitoring") != "continuous":
            err(f"behavior is monitored {p.get('behavior_monitoring')}, not continuously")
        if not set(PROACTIVE) & set(_strs(p.get("proactive_capabilities"))):
            err("no proactive preventive or resiliency capability is implemented or improved")
    if owed(ctx, data, "CM05") and p.get("configuration_checks") not in CHANGE_MONITORS:
        err(f"secure configurations are not monitored for change: "
            f"{p.get('configuration_checks')}")
    if owed(ctx, data, "PP07") and p.get("configuration_checks") not in CHECKS:
        err(f"the automation provides no periodic checks of secure configurations: "
            f"{p.get('configuration_checks')}")
    if owed(ctx, data, "PP07") and p.get("posture_monitoring") != "automated":
        err(f"the application security posture is not monitored using security automation, but "
            f"{p.get('posture_monitoring')}")
    # The p. 13 practice belongs to the threshold rows CM05 (secure configurations) and CM06
    # (control compliance), so an objective SA03 left unscored cannot excuse it.
    if (owed(ctx, data, "CM05") or owed(ctx, data, "CM06")) \
            and (gaps := lacks(p.get("continuous_validation"), VALIDATED)):
        err(f"the DevSecOps team does not continuously validate {', '.join(gaps)} using "
            "security automation")
    inheritance = _mapping(p.get("inheritance"))
    if owed(ctx, data, "PP06"):
        if inheritance.get("identified_by") != "dsop-security-team":
            err(f"DSOP control inheritance by the application is identified by the DSOP "
                f"security team, not {inheritance.get('identified_by')}")
        if inheritance.get("model") != "shared-security":
            err(f"application control inheritance from the DSOP is identified using a shared "
                f"security model, not {inheritance.get('model')}")
    return out


# --- SWLC-001: the risk-based lifecycle management approach -----------------------------------

CONMON_FILE = "artifacts/data/conmon.yaml"
FACTS_FILE = "facts.yaml"
LIFECYCLE_ADDRESSES = ("software-vulnerabilities", "supply-chain", "development-environment",
                       "intelligence-threats")  # DoDI 5000.87 3.2.b.(3)(b)
BACKLOG_CAPTURES = ("issues", "errors", "threats", "defects", "supplier-updates")  # 3.3.b.(3)


def lifecycle(ctx: Context) -> list[RunFinding]:
    """SWLC-001: a software pathway program's monitoring strategy states its risk-based lifecycle
    management approach, what the backlogs capture, and when a vulnerability fix is released out
    of the release cycle (DoDI 5000.87 3.2.b.(3)(b), 3.3.b.(3), 3.3.b.(5)(a))."""
    facts = _mapping(ctx.data(FACTS_FILE)) if ctx.run.path(FACTS_FILE).is_file() else {}
    if _mapping(facts.get("acquisition")).get("pathway") != "PW-SWP" \
            or not ctx.run.path(CONMON_FILE).is_file():
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("SWLC-001", message, CONMON_FILE, None, {"S-5"}))

    approach = _mapping(_mapping(ctx.data(CONMON_FILE)).get("lifecycle_approach"))
    if gaps := lacks(approach.get("addresses"), LIFECYCLE_ADDRESSES):
        err(f"the risk-based lifecycle management approach does not address {', '.join(gaps)}")
    if gaps := lacks(approach.get("backlog_captures"), BACKLOG_CAPTURES):
        err(f"the program backlogs do not capture {', '.join(gaps)} found in development and "
            "operations")
    if not str(approach.get("out_of_cycle") or "").strip():
        err("the approach does not say when a vulnerability fix is released out of the release "
            "cycle")
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("CATO-001", assessment), ("CATO-002", entry), ("CATO-003", platform),
                ("CATO-004", monitoring), ("CATO-005", gates), ("CATO-006", supply_chain),
                ("CATO-007", strategy), ("CATO-008", people), ("CATO-009", training),
                ("CATO-010", process), ("CATO-011", tolerances), ("CATO-012", recommendation),
                ("CATO-013", method_training), ("CATO-014", sbom), ("CATO-015", scoring),
                ("CATT-001", practices), ("SWLC-001", lifecycle))
