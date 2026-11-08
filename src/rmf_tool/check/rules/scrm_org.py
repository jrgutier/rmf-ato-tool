"""Organization C-SCRM rules SCRM-020 to SCRM-027 (NIST SP 800-161 Rev. 1 Chapter 2, Section
3.4 and Appendix C). They read artifacts/data/scrm-org.yaml, the C-SCRM part of ART-ORG-CONTEXT:
governance once P-1 is in the run's scope; the frame, policy, levels and process, and maturity
once P-2 is; information sharing at P-3; the Risk Response Framework at P-4; measures at P-7.
Each stays quiet about a file that is unreadable (RUN-FM-001 reports it).

SP 800-161 speaks of the enterprise; a run's organization is the DoD Component, whose head
delegates ownership of supply chain risk to its authorizing officials (p. 41)."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.scrm import ORG_FILE, _active, _doc, _key, _list, _obj, _refs
from rmf_tool.run import scope

ROLES, FRAME, ORG_RISK, BASELINES, ORG_MONITOR = "P-1", "P-2", "P-3", "P-4", "P-7"
LEVELS = ("level-1", "level-2", "level-3")
ASSUMPTION_KINDS = ("threat", "vulnerability", "impact", "likelihood")  # Task 1-1, p. 268
THREAT_SOURCE_KINDS = ("adversarial", "accidental", "structural", "environmental")  # p. 271
APPETITE_INPUTS = ("threats", "vulnerabilities", "constraints", "criticality")  # p. 284
PRIORITY_INPUTS = ("appetite", "tolerance", "threats", "vulnerabilities", "constraints",
                   "criticality")  # pp. 284-285
FRAME_OUTPUTS = ("policy", "criticality", "assessment-methodology", "response-guidance",
                 "monitoring-guidance", "mission-requirements", "revised-processes",
                 "operational-requirements", "acquisition-guidance")  # p. 285
ASSESS_STEP = "P-14"  # the Assess step refines every frame assumption (pp. 290-293)
# Table 1 Level 1 executive leadership ("CEO, CIO, ..., CRO, etc.") with a persona of this
# framework: the organization-level officials, the AO and the acquisition executives.
EXECUTIVES = ("PER-CIO", "PER-CISO", "PER-RE", "PER-PRIV", "PER-IO", "PER-AO", "PER-MDA",
              "PER-SPONSOR")
SENIOR_OFFICIALS = (*EXECUTIVES, "PER-AO")  # p. 257: a senior agency official as FASC liaison
# Section 2.1.4: system owners and project managers (PER-PM), engineering (PER-LSE or
# PER-ISSE), software developers (PER-DEV); senior leaders, p. 41.
DUTY_HOLDERS = {"PER-PM": ("PER-PM",), "PER-DEV": ("PER-DEV",),
                "engineering": ("PER-LSE", "PER-ISSE"), "PER-CIO": ("PER-CIO",),
                "PER-CISO": ("PER-CISO",), "PER-RE": ("PER-RE",)}
# pp. 37, 41-47, 210 and 217: the strategy, policy and implementation plan at Level 1 and/or
# Level 2 (one document may hold several), the C-SCRM plan at Level 3.
ORG_DELIVERABLES = ("strategy", "policy", "implementation-plan")
SYSTEM_DELIVERABLES = ("c-scrm-plan",)
# Fig. 7 and pp. 44-47: Level 1 informs Level 2, Level 2 informs Levels 1 and 3, and Level 3
# informs Levels 1 and 2.
INFORMS = {"level-1": ("level-2",), "level-2": ("level-1", "level-3"),
           "level-3": ("level-1", "level-2")}
PROCESS_STEPS = ("frame", "assess", "respond", "monitor")  # p. 32
SHARING_REACHES = ("P-3", "P-14")
TIER_BELOW = {"sustaining": "foundational", "enhancing": "sustaining"}  # pp. 62-63
UNDER_WAY = ("implemented", "in-progress")
MEASURE_KINDS = ("implementation", "efficiency-effectiveness", "mission-impact")  # Fig. 8
MEASURED_AGAINST = ("appetite", "tolerance")  # p. 284
FRAMEWORK_LEVELS = ("level-1", "level-2")  # p. 298


def _org(ctx: Context, task: str) -> dict[str, Any] | None:
    return _doc(ctx, ORG_FILE) if _active(ctx, task) else None


def _run_personas(ctx: Context) -> set[str]:
    """The personas the run interviewed: the roles the system has."""
    out = set()
    for interview in ctx.interviews:
        persona = (interview.front or {}).get("persona")
        if isinstance(persona, str):
            out.add(persona)
    return out


def _finding(rule: str, message: str, task: str) -> RunFinding:
    return make(rule, message, ORG_FILE, None, {task})


# --- SCRM-020 ----------------------------------------------------------------------------
def frame(ctx: Context) -> list[RunFinding]:
    """P-2: the C-SCRM frame of Tasks 1-1 and 1-2 takes OT-related suppliers into its scope,
    states each kind of assumption and has the Assess step refine it, and says which kinds of
    threat source it addresses."""
    active = set(scope.active_tasks(ctx.run))
    if (ROLES in active or FRAME in active) and not ctx.run.path(ORG_FILE).is_file():
        return [_finding("SCRM-020", "ART-ORG-CONTEXT has no artifacts/data/scrm-org.yaml, the "
                         "organization's C-SCRM context", ROLES if ROLES in active else FRAME)]
    org = _org(ctx, FRAME)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-020", message, FRAME))

    f = _obj(org, "frame")
    if _obj(f, "supply_chain").get("ot_suppliers") is not True:
        err("OT-related suppliers are left out of the scope of the organization's C-SCRM")
    stated: dict[str, set[str]] = {}
    for a in _list(f, "assumptions"):
        stated.setdefault(str(a.get("kind")), set()).update(_refs(a, "refined_at"))
    for kind in ASSUMPTION_KINDS:
        if kind not in stated:
            err(f"the C-SCRM frame states no {kind} assumption")
        elif ASSESS_STEP not in stated[kind]:
            err(f"the {kind} assumption is not refined at P-14, where the Assess step updates "
                "it")
    sources = _obj(f, "threat_sources")
    addressed, left = set(_refs(sources, "addressed")), set(_refs(sources, "not_addressed"))
    for kind in THREAT_SOURCE_KINDS:
        if kind not in addressed | left:
            err(f"the frame does not say whether {kind} threat sources are addressed")
        elif kind in addressed & left:
            err(f"the frame lists {kind} threat sources as both addressed and not addressed")
    return out


# --- SCRM-027 ----------------------------------------------------------------------------
def appetite_tolerance(ctx: Context) -> list[RunFinding]:
    """P-2: Tasks 1-3 and 1-4. Level 1 sets risk appetite and Levels 2 and 3 tolerance with
    thresholds, appetite and tolerance weigh what p. 284 names, and the priorities and
    trade-offs, taken together, weigh what pp. 284-285 name."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err27(message: str) -> None:
        out.append(_finding("SCRM-027", message, FRAME))

    f = _obj(org, "frame")
    appetite = _obj(f, "appetite")
    if appetite.get("set_at") != "level-1":
        err27(f"risk appetite is set at {appetite.get('set_at')}; Level 1 stakeholders set it")
    tolerated = {_key(t, "level") for t in _list(f, "tolerance")}
    for level in ("level-2", "level-3"):
        if level not in tolerated:
            err27(f"no risk tolerance with thresholds is stated at {level}")
    for need in APPETITE_INPUTS:
        if need not in _refs(appetite, "considered"):
            err27(f"risk appetite and tolerance do not consider supply chain {need}")
    weighed = {x for p in _list(f, "priorities") for x in _refs(p, "considered")}
    for need in PRIORITY_INPUTS:
        if need not in weighed:
            err27(f"the priorities and trade-offs do not consider {need}")
    return out


# --- SCRM-028 ----------------------------------------------------------------------------
def frame_outputs(ctx: Context) -> list[RunFinding]:
    """P-2: the risk framing step provides every output p. 285 lists, or says where it is
    held."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err28(message: str) -> None:
        out.append(_finding("SCRM-028", message, FRAME))

    f = _obj(org, "frame")
    provided = {_key(o, "output") for o in _list(f, "outputs")}
    for output in FRAME_OUTPUTS:
        if output not in provided:
            err28(f"the risk framing step provides no output {output}")
    return out


# --- SCRM-021 ----------------------------------------------------------------------------
def governance(ctx: Context) -> list[RunFinding]:
    """P-1: an executive-level official, office or group leads C-SCRM, a PMO or other
    dedicated function drives it, ownership is delegated to the authorizing officials, and each
    role SP 800-161 gives a C-SCRM duty has one, among the roles the run has."""
    org = _org(ctx, ROLES)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-021", message, ROLES))

    gov = _obj(org, "governance")
    lead = _obj(gov, "lead")
    # p. 41: an executive-level individual, office or group; a group is named, not a persona.
    if lead.get("persona") not in EXECUTIVES and not lead.get("group"):
        err(f"the C-SCRM lead {lead.get('persona')} is not an executive-level official, office "
            "or group")
    if gov.get("pmo") == "none":
        err("the organization has no C-SCRM PMO or other dedicated C-SCRM function")
    if "PER-AO" not in _refs(gov, "owners"):
        err("ownership of supply chain risk is delegated to no authorizing official")
    holders = {_key(r, "persona") for r in _list(gov, "roles")}
    present = _run_personas(ctx)
    for name, personas in DUTY_HOLDERS.items():
        # pp. 58-59 give these roles as examples; a duty is owed only by a role the run has.
        if present & set(personas) and not holders & set(personas):
            err(f"no C-SCRM duty is defined for {name}")
    return out


# --- SCRM-022 ----------------------------------------------------------------------------
def levels(ctx: Context) -> list[RunFinding]:
    """P-2: Level 1 or Level 2 provides the C-SCRM strategy, policy and implementation plan,
    Level 3 the C-SCRM plan, and each level informs the levels SP 800-161 says it informs."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-022", message, FRAME))

    held = {_key(lv, "level"): lv for lv in _list(org, "levels")}
    upper = {d for level in ("level-1", "level-2") for d in _refs(held.get(level), "deliverables")}
    for deliverable in ORG_DELIVERABLES:
        if deliverable not in upper:
            err(f"neither level-1 nor level-2 provides a C-SCRM {deliverable}")
    for deliverable in SYSTEM_DELIVERABLES:
        if deliverable not in _refs(held.get("level-3"), "deliverables"):
            err(f"level-3 provides no C-SCRM {deliverable}")
    for level in LEVELS:
        if level not in held:
            err(f"the C-SCRM record says nothing of what {level} holds and passes on")
    return out


# --- SCRM-031 (split from SCRM-022) -------------------------------------------------------
def level_flows(ctx: Context) -> list[RunFinding]:
    """P-2: each level the record holds informs the levels SP 800-161 says it informs, down
    and up (pp. 40-47). A level the record leaves out is SCRM-022's."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    held = {_key(lv, "level"): lv for lv in _list(org, "levels")}
    return [_finding("SCRM-031", f"{level} C-SCRM outputs do not inform {other}", FRAME)
            for level in LEVELS if level in held
            for other in INFORMS[level] if other not in _refs(held[level], "informs")]


# --- SCRM-029 ----------------------------------------------------------------------------
def process(ctx: Context) -> list[RunFinding]:
    """P-2: C-SCRM sits in each step of the frame, assess, respond and monitor process."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    steps = {_key(s, "step") for s in _list(_obj(org, "process"), "steps")}
    return [_finding("SCRM-029", f"the C-SCRM process says nothing of the {step} step", FRAME)
            for step in PROCESS_STEPS if step not in steps]


# --- SCRM-023 ----------------------------------------------------------------------------
def sharing(ctx: Context) -> list[RunFinding]:
    """P-3: information-sharing processes are built into the C-SCRM program, a FASC liaison who
    is one of the Component's personas is a senior agency official, and shared information
    reaches P-3 and P-14."""
    org = _org(ctx, ORG_RISK)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-023", message, ORG_RISK))

    s = _obj(org, "sharing")
    if not _list(s, "practices"):
        err("information sharing has no processes built into the C-SCRM program")
    liaison = _obj(s, "fasc").get("liaison")
    # p. 257: the agency designates the liaison; a Component may cite the Department's, by
    # name, instead of one of its own personas.
    if isinstance(liaison, str) and liaison.startswith("PER-") \
            and liaison not in SENIOR_OFFICIALS:
        err(f"the FASC liaison {liaison} is not a senior agency official")
    for task in SHARING_REACHES:
        if task not in _refs(s, "feeds"):
            err(f"shared supply chain risk information does not reach {task} as EXT-THREAT")
    return out


# --- SCRM-024 ----------------------------------------------------------------------------
def maturity(ctx: Context) -> list[RunFinding]:
    """P-2: a sustaining or enhancing practice is under way only once some practice of the
    tier below is implemented, and what is taken up next is a practice the record holds."""
    org = _org(ctx, FRAME)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-024", message, FRAME))

    m = _obj(org, "maturity")
    practices = _list(m, "practices")
    names = {_key(p, "practice") for p in practices}
    for name in _refs(m, "next"):
        if name not in names:
            err(f"the maturity record takes up {name} next, a practice it does not hold")
    # pp. 62-63 judge the tier below as a whole ("broadly standardized and implemented"): a
    # higher-tier practice waits only while no practice of the tier below is implemented.
    implemented = {_key(q, "tier") for q in practices if q.get("status") == "implemented"}
    for p in practices:
        below = TIER_BELOW.get(str(p.get("tier")))
        if below is None or p.get("status") not in UNDER_WAY:
            continue
        if below not in implemented:
            err(f"a practice is under way before the tier below it is implemented: "
                f"{p.get('tier')} practice {p.get('practice')} while no {below} practice "
                "is implemented")
    return out


# --- SCRM-025 ----------------------------------------------------------------------------
def measures(ctx: Context) -> list[RunFinding]:
    """P-7: the C-SCRM program is measured on implementation, efficiency and effectiveness,
    and mission impact, against appetite and tolerance, with goals validated by its
    stakeholders."""
    org = _org(ctx, ORG_MONITOR)
    if org is None:
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(_finding("SCRM-025", message, ORG_MONITOR))

    m = _obj(org, "measures")
    held = _list(m, "measures")
    for kind in MEASURE_KINDS:
        if kind not in {_key(x, "kind") for x in held}:
            err(f"no C-SCRM measure is of kind {kind}")
    for against in MEASURED_AGAINST:
        if against not in {_key(x, "against") for x in held}:
            err(f"no C-SCRM measure measures performance against risk {against}")
    who = _obj(m, "stakeholders")
    stakeholders = set(_refs(who, "primary")) | set(_refs(who, "secondary"))
    for n, goal in enumerate(_list(m, "goals"), 1):
        for persona in _refs(goal, "validated_with"):
            if persona not in stakeholders:
                err(f"goal {n} is validated with {persona}, who is no C-SCRM stakeholder of "
                    "the measures")
    return out


# --- SCRM-026 ----------------------------------------------------------------------------
def response_framework(ctx: Context) -> list[RunFinding]:
    """P-4: Levels 1 and 2 each keep a C-SCRM Risk Response Framework."""
    org = _org(ctx, BASELINES)
    if org is None:
        return []
    kept = {_key(r, "level") for r in _list(org, "response_framework")}
    return [_finding("SCRM-026", f"no C-SCRM Risk Response Framework is kept at {level}",
                     BASELINES) for level in FRAMEWORK_LEVELS if level not in kept]
