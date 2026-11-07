"""Assessment rules ASMT-001 to ASMT-012: what the plan prepares, selects, reuses and brings in
from external providers (A-1, A-2), what each determination statement found (A-3), how findings
are triaged (A-5) and how the POA&M records and ranks them (A-6, M-3). Each stays quiet about an
artifact not in play; RUN-ART-001 reports a missing file."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Iterable
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.consistency import BOUNDARY_FILE, RAR_FILE
from rmf_tool.check.rules.content import POAM_FILE, SAR_DIR, family_records
from rmf_tool.run import authorization as ledger
from rmf_tool.run import poam_dates, scope

SAP_FILE = "artifacts/data/sap.yaml"
REPORT_FILE = "artifacts/data/sar-report.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
SAR_DOC = "artifacts/ART-SAR.md"
USERS_FILE = "artifacts/data/users.yaml"
NO_LOGICAL_ACCESS, GENERAL_PUBLIC = "no-logical-access", "general-public"
INFORMATION_OWNER = "PER-IO"
SYSTEM_OWNER, CCP, AO, AODR, SCA, CISO = ("PER-PM", "PER-CCP", "PER-AO", "PER-AODR", "PER-SCA",
                                          "PER-CISO")
RISK_ASSESSMENT, ORG_CONTEXT, CATEGORIZATION = "ART-RA", "ART-ORG-CONTEXT", "ART-CAT"
ACCESS = ("system", "environment", "documentation", "records", "artifacts", "test-results")
# SP 800-53A section 2.4: what each assessment method applies to.
METHOD_OBJECTS = {"examine": {"specifications", "mechanisms", "activities"},
                  "interview": {"individuals"}, "test": {"mechanisms", "activities"}}
INDEPENDENCE = ("self-assessment", "internal", "independent")
REUSE_CHECKS = ("credibility", "appropriateness", "applicability", "currency", "relevance")
PRODUCT_CHECKS = ("controls_implemented", "meets_requirements", "configuration_consistent",
                  "assurance_satisfied")
COMPONENT_PRODUCT = "component-product"
SATISFIED, OTHER, NOT_APPLICABLE = "satisfied", "other-than-satisfied", "not-applicable"
INCONSEQUENTIAL, FALSE_POSITIVE = "inconsequential", "false-positive"
SIGNIFICANT = ("high", "very-high")
LEVELS = ("very-low", "low", "moderate", "high", "very-high")
STATUS_TERMS = ("planned", "ongoing", "delayed", "completed", "risk-accepted")
CLOSED_ITEMS = ("completed", "risk-accepted")
UNRESOLVED = ("open", "risk-accepted")  # a SAR or STIG finding's status
ASSESSMENT_EVENT = "security-control-assessment"

Err = Callable[[str], None]


def _day(value: Any) -> dt.date | None:
    return ledger.parse_date(value)


def _mapping(ctx: Context, rel: str) -> dict[str, Any]:
    data = ctx.data(rel)
    return data if isinstance(data, dict) else {}


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [r for r in data.get(key) or () if isinstance(r, dict)]


def _block(data: dict[str, Any], key: str) -> dict[str, Any]:
    found = data.get(key)
    return found if isinstance(found, dict) else {}


def _at(out: list[RunFinding], rule: str, rel: str) -> Err:
    def err(message: str) -> None:
        out.append(make(rule, message, rel))
    return err


def _reporter(rule: str, rel: str) -> tuple[list[RunFinding], Err]:
    out: list[RunFinding] = []
    return out, _at(out, rule, rel)


def _sap(ctx: Context) -> dict[str, Any] | None:
    """The plan's data, once the plan is in play."""
    if not scope.produced_or_seeded(ctx.run, "ART-SAP"):
        return None
    return ctx.data(SAP_FILE) if isinstance(ctx.data(SAP_FILE), dict) else None


def _start(sap: dict[str, Any]) -> dt.date | None:
    return _day(_block(sap, "schedule").get("start"))


def _team(sap: dict[str, Any]) -> set[Any]:
    return {m.get("persona") for m in _records(sap, "team")}


def _late(when: Any, limit: dt.date | None) -> bool:
    day = _day(when)
    return day is not None and limit is not None and day > limit


# --- ASMT-001: the plan is prepared, reviewed and approved ------------------------------------

def _approval(sap: dict[str, Any], err: Err) -> None:
    found = _block(sap, "approval")
    if not found:
        err("no approval: assessment plans are reviewed and approved")
        return
    if found.get("reviewed_by") != SCA:
        err("the assessment plan is reviewed by the security control assessor, not "
            f"{found.get('reviewed_by')}")
    if found.get("approved_by") not in (AO, AODR):
        err("assessment plans are approved by the authorizing official or designated "
            f"representative, not {found.get('approved_by')}")
    if _late(found.get("date"), _start(sap)):
        err(f"the assessment plan was approved on {found.get('date')}, after the control "
            f"assessments start on {_start(sap)}")


def _access(prep: dict[str, Any], start: dt.date | None, err: Err) -> None:
    access = _records(prep, "access")
    missing = [kind for kind in ACCESS if kind not in {a.get("to") for a in access}]
    if missing:
        err(f"assessors have no access to {', '.join(missing)}")
    for a in access:
        if a.get("provided_by") != SYSTEM_OWNER:
            err(f"the system owner provides the required access to control assessors, not "
                f"{a.get('provided_by')}")
        if _late(a.get("provided"), start):
            err(f"assessors have access to {a.get('to')} only from {a.get('provided')}, after "
                "the assessment starts")
    documents = prep.get("documentation_provided") or ()
    if "ART-SSP" not in documents:
        err("the documentation provided to the assessor omits the security plan ART-SSP")


def _notified(prep: dict[str, Any], start: dt.date | None, err: Err) -> None:
    if prep.get("informed_by") != SYSTEM_OWNER:
        err("the system owner informs organizational officials of the need to conduct the "
            f"assessment, not {prep.get('informed_by')}")
    notified = _records(prep, "officials_notified")
    if AO not in {n.get("persona") for n in notified}:
        err("the authorizing official is not among the key organizational officials notified "
            "of the impending assessments")
    for n in notified:
        if _late(n.get("date"), start):
            err(f"{n.get('persona')} was notified of the impending assessments on "
                f"{n.get('date')}, after they start")
    resources = _block(prep, "resources")
    if resources.get("allocated_by") != SYSTEM_OWNER:
        err("the system owner ensures that resources are available for the assessment, not "
            f"{resources.get('allocated_by')}")
    if _late(resources.get("allocated"), start):
        err(f"necessary resources were allocated on {resources.get('allocated')}, after the "
            "assessment starts")


def _organization_side(ctx: Context, sap: dict[str, Any], prep: dict[str, Any], err: Err) -> None:
    team, personas = _team(sap), ctx.run.personas
    notified = {n.get("persona") for n in _records(prep, "officials_notified")}
    for channel in _records(prep, "channels"):
        for persona in channel.get("among") or ():
            if persona not in notified:
                err(f"the communication channel names {persona}, who is not among the "
                    "organizational officials notified")
    for poc in _records(prep, "points_of_contact"):
        if poc.get("persona") in team or poc.get("persona") not in personas:
            err(f"{poc.get('persona')} is no organizational point of contact: it must be a "
                "framework persona outside the assessment team")
    for element in _records(prep, "elements"):
        if element.get("persona") in team or element.get("persona") not in personas:
            err(f"{element.get('persona')} is no element of the organization to arrange access "
                "to: it must be a framework persona outside the assessment team")
    between = set(_block(prep, "ambiguity_mechanism").get("between") or ())
    if between.isdisjoint(team) or between <= team:
        err("the mechanism to minimize ambiguities must stand between the organization and the "
            "assessors")
    if ORG_CONTEXT not in (_block(prep, "understanding").get("sources") or ()):
        err("the assessors' understanding of the organization's operations does not rest on "
            f"{ORG_CONTEXT}")


def preparation(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("ASMT-001", SAP_FILE)
    _approval(sap, err)
    if not str(sap.get("objectives") or "").strip():
        err("the assessment plan states no objective for the control assessments")
    if not str(sap.get("level_of_effort") or "").strip():
        err("the assessment plan states no level of effort for the control assessments")
    prep = _block(sap, "preparation")
    if not prep:
        err("no preparation: organizational officials, resources and assessor access are "
            "prepared before the assessment")
        return out
    start = _start(sap)
    _notified(prep, start, err)
    _access(prep, start, err)
    _organization_side(ctx, sap, prep, err)
    return out


# --- ASMT-002: assessment procedures are selected and tailored --------------------------------

def _methods_fit(ident: Any, record: dict[str, Any], err: Err) -> None:
    objects = set(record.get("objects") or ())
    methods = record.get("methods") or ()
    fits = {o for m in methods for o in METHOD_OBJECTS.get(m, ())}
    for leftover in sorted(objects - fits):
        err(f"{ident}: no selected assessment method applies to the assessment object "
            f"{leftover}")
    idle = [m for m in methods if METHOD_OBJECTS.get(m, set()).isdisjoint(objects)]
    if idle:
        err(f"{ident}: the assessment method {', '.join(idle)} has no selected assessment object")


def _procedure(ctx: Context, p: dict[str, Any], seen: dict[Any, Any], err: Err) -> None:
    pid = p.get("id")
    baseline = set(baseline_mod.control_ids(ctx.run))
    for cid in p.get("controls") or ():
        if cid not in baseline:
            err(f"{pid} selects assessment procedures for {cid}, which is not in the security "
                "plan after tailoring")
        for method in p.get("methods") or ():
            if (cid, method) in seen:
                err(f"{cid} is in both {seen[cid, method]} and {pid} by {method}: consolidating "
                    "assessment procedures applies each method to a control once")
            seen[cid, method] = pid
    _methods_fit(pid, p, err)
    if RISK_ASSESSMENT not in (p.get("risk_results") or ()):
        err(f"{pid} applies no results of risk assessments: risk_results omits {RISK_ASSESSMENT}")
    if p.get("adaptation", "none") != "none" and not str(p.get("adaptation_note") or "").strip():
        err(f"{pid} is adapted as {p.get('adaptation')} but does not say how the assessment "
            "procedures were adapted")


def procedures(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None or baseline_mod.load(ctx.run) is None:
        return []
    out, err = _reporter("ASMT-002", SAP_FILE)
    records = _records(sap, "procedures")
    seen: dict[Any, Any] = {}
    for p in records:
        _procedure(ctx, p, seen, err)
    excluded = {e.get("control_id") for e in _records(_block(sap, "scope"), "excluded_controls")}
    selected = {cid for cid, _ in seen}
    for cid in baseline_mod.control_ids(ctx.run):
        if cid not in excluded and cid not in selected:
            err(f"scoped control {cid} has no assessment methods and objects selected")
    for extra in _records(sap, "additional_procedures"):
        _methods_fit(extra.get("id"), extra, err)
    reviewer = _block(sap, "optimization").get("reviewed_by")
    if reviewer not in _team(sap):
        err("assessors review the selected assessment procedures to combine or consolidate "
            f"them, not {reviewer}")
    return out


# --- ASMT-003: reused results ------------------------------------------------------------------

def _rank(value: Any) -> int:
    return INDEPENDENCE.index(value) if value in INDEPENDENCE else -1


def _reused(r: dict[str, Any], sap: dict[str, Any], err: Err) -> None:
    rid, start = r.get("id"), _start(sap)
    assessed = _day(r.get("assessed"))
    if _late(assessed, start):
        err(f"{rid}: the original assessment of {assessed} follows the current assessment")
    limit = _block(sap, "reuse_policy").get("max_age_days")
    if assessed and start and limit and (start - assessed).days > limit:
        err(f"{rid}: {(start - assessed).days} days since the previous assessment, beyond the "
            f"{limit} the organization's reuse policy allows")
    required = _block(sap, "assessor_independence").get("required")
    if _rank(r.get("independence")) < _rank(required):
        err(f"{rid}: a previous assessment of independence {r.get('independence')} cannot be "
            f"reused when the current assessment requires {required}")
    if r.get("approved_by") not in (AO, AODR):
        err(f"{rid}: reusing assessment results is approved by the users of the assessment "
            f"results, not {r.get('approved_by')}")
    together = set(r.get("coordinated_with") or ())
    if together.isdisjoint((SYSTEM_OWNER, CCP)) or together.isdisjoint((AO, AODR)):
        err(f"{rid}: system owners or common control providers collaborate with authorizing "
            "officials on the acceptability of previous assessment results")
    if r.get("determined_by") not in _team(sap):
        err(f"{rid}: assessors determine the credibility of the assessment evidence, not "
            f"{r.get('determined_by')}")
    for check in REUSE_CHECKS:
        if _block(r, check).get("verdict") == "not-acceptable":
            err(f"{rid} is reused though its {check} was found not acceptable")
    if r.get("type") == COMPONENT_PRODUCT:
        review = _block(r, "product_review")
        failed = [check for check in PRODUCT_CHECKS if review.get(check) is not True]
        if failed:
            err(f"{rid}: the component product checks do not show {', '.join(failed)}")


def reuse(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("ASMT-003", SAP_FILE)
    records = _records(sap, "reused_results")
    source = _block(sap, "reuse_policy").get("source")
    if records and source != ORG_CONTEXT:
        err(f"the reuse requirements are established by the organization ({ORG_CONTEXT}), not "
            f"{source}")
    for r in records:
        _reused(r, sap, err)
    return out


# --- ASMT-004: external providers --------------------------------------------------------------

def _external_ids(ctx: Context) -> list[str]:
    """What the run itself says is external, so leaving a provider out is no way around this."""
    components = _records(_mapping(ctx, BOUNDARY_FILE), "components")
    return [*(str(c.get("id")) for c in components if c.get("external") is True),
            *(str(a.get("id")) for a in
              _records(_mapping(ctx, LEVERAGED_FILE), "leveraged_authorizations"))]


def _provider(p: dict[str, Any], sap: dict[str, Any], packaged: bool, err: Err) -> None:
    pid = p.get("id")
    review = _block(p, "agreement_review")
    if review.get("by") not in _team(sap):
        err(f"{pid}: the contracts or agreements are reviewed by assessors, not "
            f"{review.get('by')}")
    if _late(review.get("date"), _day(_block(sap, "approval").get("date"))):
        err(f"{pid}: the contract or agreement was reviewed on {review.get('date')}, after the "
            "assessment plan was approved")
    found = _block(p, "provider_assessment")
    # Evidence may still be on request while the plan is made; the package needs it (A-4, R-2).
    evidence = found.get("evidence")
    if evidence == "refused" or (packaged and evidence != "received"):
        err(f"{pid}: the information needed to make risk-based decisions is not made available "
            f"(evidence is {found.get('evidence')})")
    required = _block(sap, "assessor_independence").get("required")
    if _rank(found.get("independence")) < _rank(required):
        err(f"{pid}: the independence of the assessors it used, "
            f"{found.get('independence')}, is below the required {required}")
    if found.get("procedures_reviewed_by") not in _team(sap):
        err(f"{pid}: the assessment procedures it employed are reviewed by assessors, "
            f"not {found.get('procedures_reviewed_by')}")
    if found.get("meets_protection_needs") is not True:
        err(f"{pid}: the externally provided controls do not meet the protection needs of the "
            "organization, so they cannot be leveraged")
    if p.get("kind") != "usg" and p.get("under_usg_authority") is not True \
            and _block(p, "third_party").get("accepted_by") not in (AO, AODR):
        err(f"{pid}: a {p.get('kind')} system outside USG authorities must use a third party "
            "assessment organization acceptable to the cognizant AO")


def external(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("ASMT-004", SAP_FILE)
    records = _records(sap, "external_providers")
    covered = {c for p in records for c in p.get("covers") or ()}
    for ident in _external_ids(ctx):
        if ident not in covered:
            err(f"external {ident} has no external_providers record, so the assessment "
                "procedures are not adjusted for it")
    packaged = not {"A-4", "R-2"}.isdisjoint(scope.active_tasks(ctx.run))
    for p in records:
        _provider(p, sap, packaged, err)
    return out


# --- ASMT-005: each determination statement produces a finding ---------------------------------

def _statements(cat: catalog.Catalog, d: dict[str, Any], err: Err) -> dict[Any, Any]:
    cid, result = d.get("control_id"), d.get("result")
    records = _records(d, "statements")
    found = {s.get("id"): s.get("result") for s in records}
    wanted = catalog.determination_statements(cat, str(cid))
    missing = [s for s in wanted if s not in found]
    if missing:
        err(f"{cid}: no finding for the determination statement {', '.join(missing)}")
    for label in found:
        if label not in wanted:
            err(f"{cid}: {label} is not a determination statement of the control")
    for s in records:
        if s.get("result") == NOT_APPLICABLE and not str(s.get("reason") or "").strip():
            err(f"{cid}: {s.get('id')} is not applicable without a reason")
    against = [label for label, r in found.items() if r in (OTHER, "not-evaluated")]
    if result == SATISFIED and against:
        err(f"{cid} is satisfied, yet the determination statement {', '.join(against)} is not")
    if result == OTHER and OTHER not in found.values():
        err(f"{cid} is other than satisfied, yet no determination statement is")
    if result == NOT_APPLICABLE and set(found.values()) - {NOT_APPLICABLE}:
        err(f"{cid} is not applicable, yet a determination statement applies")
    return found


def _planned(sap: dict[str, Any]) -> dict[Any, set[Any]]:
    planned: dict[Any, set[Any]] = {}
    for p in _records(sap, "procedures"):
        for cid in p.get("controls") or ():
            planned.setdefault(cid, set()).update(p.get("methods") or ())
    return planned


def _used(d: dict[str, Any], sap: dict[str, Any], err: Err) -> None:
    """The determination against the plan: its methods and the reused results it rests on."""
    cid = d.get("control_id")
    planned = _planned(sap).get(cid)
    if planned is not None:
        for method in sorted(set(d.get("methods") or ()) - planned):
            err(f"{cid}: the assessment method {method} was not selected in the assessment plan")
    results = {r.get("id"): r for r in _records(sap, "reused_results")}
    for rid in d.get("reused") or ():
        if rid not in results:
            err(f"{cid}: {rid} is not a reused result of the assessment plan")
        elif cid not in (results[rid].get("controls") or ()):
            err(f"{cid}: the assessment plan does not reuse {rid} for this control")


def _named_in_report(ctx: Context, sap: dict[str, Any], err: Err) -> None:
    doc = ctx.docs.get(SAR_DOC)
    if doc is None:
        return
    for key, what in (("reused_results", "reused result"),
                      ("external_providers", "external assessment")):
        for record in _records(sap, key):
            if str(record.get("id")) not in doc.body:
                err(f"the assessment report does not document the {what} {record.get('id')}")


def _finding(f: dict[str, Any], found: dict[Any, dict[Any, Any]], err: Err) -> None:
    fid, cid = f.get("id"), f.get("control_id")
    statements = found.get(cid, {})
    affected = f.get("affected_statements") or ()
    if not affected:
        err(f"{fid} does not indicate which parts of the control are affected by the finding")
    for label in affected:
        if statements.get(label) not in (OTHER, "not-evaluated"):
            err(f"{fid} names {label} as affected by the finding, but that statement is "
                f"{statements.get(label)}")
    if not str(f.get("state_difference") or "").strip():
        err(f"{fid} does not describe how the actual state differs from the expected state")
    if not f.get("potential_compromise"):
        err(f"{fid} notes no potential compromise to confidentiality, integrity or availability")


def determinations(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-SAR"):
        return []
    out: list[RunFinding] = []
    sap = _sap(ctx) or {}
    found: dict[Any, dict[Any, Any]] = {}
    every = list(family_records(ctx, SAR_DIR, "findings"))
    # A closed finding still names what it found: remediation does not change initial findings.
    named = {label for _, f in every for label in f.get("affected_statements") or ()}
    findings = [(rel, f) for rel, f in every if f.get("status") != "closed"]
    judged = list(family_records(ctx, SAR_DIR, "determinations"))
    # The catalog is read only for a determination to judge: a fresh fork may not hold it yet.
    cat = catalog.load(ctx.run.repo) if judged else None
    for rel, d in judged:
        assert cat is not None
        err = _at(out, "ASMT-005", rel)
        cid = d.get("control_id")
        found[cid] = _statements(cat, d, err)
        _used(d, sap, err)
        unnamed = [s for s, r in found[cid].items() if r == OTHER and s not in named]
        if unnamed:
            err(f"{cid}: no finding names the other than satisfied statement "
                f"{', '.join(unnamed)}")
    for rel, f in findings:
        _finding(f, found, _at(out, "ASMT-005", rel))
    _named_in_report(ctx, sap, _at(out, "ASMT-005", SAR_DOC))
    return out


# --- ASMT-006: findings are triaged ------------------------------------------------------------

def _triage(f: dict[str, Any], triage: dict[str, Any], err: Err) -> None:
    fid, action, by = f.get("id"), triage.get("action"), triage.get("decided_by")
    if RISK_ASSESSMENT not in (triage.get("risk_basis") or ()):
        err(f"{fid}: the initial remediation actions are determined from the updated risk "
            f"assessment, and risk_basis omits {RISK_ASSESSMENT}")
    if action == "immediate-remediation" and by not in (AO, AODR):
        err(f"{fid}: the authorizing official or designated representative decides that a "
            f"finding requires immediate remediation actions, not {by}")
    if action == INCONSEQUENTIAL and by not in (SYSTEM_OWNER, CCP):
        err(f"{fid}: system owners and common control providers decide that a finding is "
            f"inconsequential, not {by}")
    if action == INCONSEQUENTIAL and f.get("severity") in SIGNIFICANT:
        err(f"{fid} of {f.get('severity')} severity is called inconsequential, which means it "
            "presents no significant security or privacy risk")
    if action in ("remediated", FALSE_POSITIVE) and f.get("status") != "closed":
        err(f"{fid} is triaged {action} but its status is {f.get('status')}")


def triage(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []
    if not scope.produced_or_seeded(ctx.run, "ART-SAR"):
        return out
    decided = "A-5" in scope.active_tasks(ctx.run)
    items = _records(_mapping(ctx, POAM_FILE), "items")
    linked = {i.get("finding_ref"): i.get("id") for i in items}
    for rel, f in family_records(ctx, SAR_DIR, "findings"):
        err = _at(out, "ASMT-006", rel)
        found = _block(f, "triage")
        if decided and not found:
            err(f"{f.get('id')} has no triage: organizations review assessor findings to "
                "determine their significance")
        if found:
            _triage(f, found, err)
        if found.get("action") in (INCONSEQUENTIAL, FALSE_POSITIVE) and f.get("id") in linked:
            err(f"{linked[f.get('id')]} transfers {f.get('id')}, triaged {found.get('action')}: "
                "only substantive items go to the plan of action and milestones")
    return out


# --- ASMT-007: the assessment team --------------------------------------------------------------

def team(ctx: Context) -> list[RunFinding]:
    sap = _sap(ctx)
    if sap is None:
        return []
    out, err = _reporter("ASMT-007", SAP_FILE)
    start = _start(sap)
    for member in _records(sap, "team"):
        persona = member.get("persona")
        found = _block(member, "qualification")
        if not found:
            err(f"{persona} has no qualification on record: the CISO establishes a team of "
                "qualified cybersecurity professionals")
            continue
        if found.get("verified_by") != CISO:
            err(f"the CISO establishes the team of qualified assessors; {persona} was verified "
                f"by {found.get('verified_by')}")
        if _late(found.get("verified"), start):
            err(f"{persona} was verified as a qualified assessor on {found.get('verified')}, "
                "after the assessment starts")
    _selection(ctx, sap, start, err)
    independence = _block(sap, "assessor_independence")
    if independence.get("determined_by") not in (AO, AODR):
        err("the authorizing official or designated representative determines the required "
            f"degree of assessor independence, not {independence.get('determined_by')}")
    basis = independence.get("basis") if isinstance(independence.get("basis"), list) else []
    if CATEGORIZATION not in basis:
        err("the required level of independence rests on the results of the security "
            "categorization; basis omits ART-CAT")
    if RISK_ASSESSMENT not in basis:
        err("the required level of independence rests on the risk to organizational operations, "
            "assets, individuals, other organizations and the Nation; basis omits ART-RA")
    _sufficiency(_block(independence, "sufficiency"), err)
    reviewed = _independent_review(independence, _team(sap), ctx, err)
    for member in _records(sap, "team"):
        contract = _block(member, "contract")
        if (member.get("independent") is True and contract.get("owner_involved") is True
                and contract.get("owner_can_influence") is True):
            err(f"{member.get('persona')} is contracted with the system owner directly involved "
                "in the contracting process and able to unduly influence the assessor, so the "
                "member is not independent")
    if independence.get("required") == "independent" and not reviewed:
        for member in _records(sap, "team"):
            if member.get("independent") is not True:
                err(f"{member.get('persona')} lacks the required degree of independence the "
                    "authorizing official determined")
    return out


def _selection(ctx: Context, sap: dict[str, Any], start: dt.date | None, err: Err) -> None:
    """A-1: the AO or designated representative selects the team for the type of assessment,
    weighing the technical expertise required (SP 800-53A 3.2, SP 800-37r2 Task A-1)."""
    selection = _block(sap, "selection")
    if not selection:
        err("no assessor selection is recorded: the authorizing official or designated "
            "representative selects the assessor or assessment team for the type of control "
            "assessment to be conducted")
        return
    if selection.get("selected_by") not in (AO, AODR):
        err("the authorizing official or designated representative selects the assessor or "
            f"assessment team, not {selection.get('selected_by')}")
    if _late(selection.get("date"), start):
        err(f"the assessment team was selected on {selection.get('date')}, after the assessment "
            "starts")
    if ctx.processes_pii and selection.get("assessment_type") == "security":
        err("the system processes PII, so the type of control assessment to be conducted covers "
            "the privacy controls; the assessor was selected for a security assessment only")
    if not selection.get("expertise"):
        err("the selection records no technical expertise the assessors possess to carry out "
            "the assessments")


def _sufficiency(found: dict[str, Any], err: Err) -> None:
    if not found:
        err("the authorizing official has not determined whether the level of assessor "
            "independence is sufficient to provide confidence in the assessment results")
        return
    if found.get("determined_by") not in (AO, AODR):
        err("the authorizing official or designated representative determines whether the "
            f"level of assessor independence is sufficient, not {found.get('determined_by')}")
    if found.get("sufficient") is not True:
        err("the authorizing official determined the level of assessor independence "
            "insufficient to provide confidence that the assessment results are sound")


def _independent_review(independence: dict[str, Any], team: set[Any], ctx: Context,
                        err: Err) -> bool:
    """Whether an independent team of experts reviewing the results stands in for the
    assessors' own independence (SP 800-53A 3.2, special situations)."""
    if independence.get("achieved_by") != "independent-review":
        return False
    review = _block(independence, "review")
    reviewers = review.get("by") if isinstance(review.get("by"), list) else []
    if not reviewers:
        err("independence achieved by an independent review of the assessment results names "
            "no reviewing team of experts")
        return False
    sound = True
    for who in reviewers:
        if not isinstance(who, str) or who in team or who not in ctx.run.personas:
            err(f"the independent team of experts that reviews the assessment results includes "
                f"{who}, who is on the assessment team or no framework persona")
            sound = False
    return sound


# --- ASMT-008: the report as a whole ------------------------------------------------------------

def report(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-SAR"):
        return []
    data = ctx.data(REPORT_FILE)
    if not isinstance(data, dict):
        return []
    out, err = _reporter("ASMT-008", REPORT_FILE)
    methodology = _block(data, "methodology")
    if "800-53A" not in str(methodology.get("standard")) \
            and not str(methodology.get("deviation_rationale") or "").strip():
        err("the methodology is not SP 800-53A and gives no rationale for deviation from "
            "standard assessment resources")
    if "A-4" not in scope.active_tasks(ctx.run):
        return out
    receivers = {d.get("to") for d in _records(data, "delivered")}
    if SYSTEM_OWNER not in receivers:
        err("the system owner receives the assessment results from the control assessors, and "
            "delivered omits PER-PM")
    review = _block(data, "quality_review")
    if not review:
        err("no quality_review: the CISO is responsible for assessing security control "
            "assessments")
        return out
    if review.get("by") != CISO:
        err("the CISO is responsible for assessing the quality of security control assessments, "
            f"not {review.get('by')}")
    end = _day(_block(_mapping(ctx, SAP_FILE), "schedule").get("end"))
    if _late(end, _day(review.get("date"))):
        err(f"the CISO assessed the security control assessments on {review.get('date')}, "
            f"before they ended on {end}")
    return out


# --- ASMT-013: who may use the system ----------------------------------------------------------

def users(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-SD"):
        return []
    out, err = _reporter("ASMT-013", USERS_FILE)
    for u in _records(_mapping(ctx, USERS_FILE), "users"):
        uid = u.get("id")
        if u.get("privilege_level") != NO_LOGICAL_ACCESS:
            access = _block(u, "access_decision")
            if access.get("decided_by") != SYSTEM_OWNER:
                err(f"{uid}: the system owner decides who has access to the system, not "
                    f"{access.get('decided_by')}")
            if access.get("coordinated_with") != INFORMATION_OWNER:
                err(f"{uid}: the system owner decides access in coordination with the "
                    f"information owner, not {access.get('coordinated_with')}")
        if u.get("type") != GENERAL_PUBLIC:
            found = _block(u, "training")
            if found.get("ensured_by") != SYSTEM_OWNER:
                err(f"{uid}: the system owner ensures that system users receive the requisite "
                    f"training, not {found.get('ensured_by')}")
    return out


# --- ASMT-009 to ASMT-012: the POA&M -------------------------------------------------------------

def _items(ctx: Context) -> list[dict[str, Any]] | None:
    if not scope.produced_or_seeded(ctx.run, "ART-POAM"):
        return None
    data = ctx.data(POAM_FILE)
    return _records(data, "items") if isinstance(data, dict) else None


def _latest(ctx: Context) -> dt.date | None:
    """The latest date the run vouches for: its start or its newest authorization record. A
    simulated run has no today."""
    dates = [_day(str(ctx.run.config.get("as_of"))[:10]),
             *(_day(r.get("date")) for r in ctx.ledger or ())]
    return max((d for d in dates if d), default=None)


def _risk_levels(ctx: Context) -> dict[Any, Any]:
    """The RAR level of each POA&M item a risk links, once the RAR exists."""
    return {ref: r.get("level") for r in _records(_mapping(ctx, RAR_FILE), "risks")
            for ref in r.get("poam_refs") or ()}


def poam_record(ctx: Context) -> list[RunFinding]:
    items = _items(ctx)
    if items is None:
        return []
    out, err = _reporter("ASMT-009", POAM_FILE)
    levels = _risk_levels(ctx)
    schedule = _block(_mapping(ctx, SAP_FILE), "schedule")
    for i in items:
        iid = i.get("id")
        if not i.get("risk_level"):
            err(f"{iid} lacks the risk assessment level")
        if not i.get("criticality"):
            err(f"{iid} lacks the criticality of the deficiency")
        if not i.get("mitigation_approach"):
            err(f"{iid} lacks the proposed risk mitigation approach")
        if iid in levels and i.get("risk_level") != levels[iid]:
            err(f"{iid}: the risk assessment level is {i.get('risk_level')}, but the RAR says "
                f"{levels[iid]}")
        identified = _block(i, "identified")
        if not identified:
            err(f"{iid} does not include the event that identified the weakness")
        day = _day(identified.get("date"))
        if identified.get("event") == ASSESSMENT_EVENT and day is not None and (
                _late(_day(schedule.get("start")), day) or _late(day, _day(schedule.get("end")))):
            err(f"{iid}: the date the weakness was identified, {day}, falls outside the security "
                "control assessment")
    return out


def _original(i: dict[str, Any], frozen: dict[str, Any], err: Err) -> None:
    iid, first = i.get("id"), frozen.get(i.get("id"))
    if not isinstance(first, dict):
        return
    if i.get("scheduled_completion") != first.get("scheduled_completion"):
        err(f"{iid}: the scheduled completion date should not be changed, from "
            f"{first.get('scheduled_completion')} to {i.get('scheduled_completion')}")
    now = {m.get("description"): m.get("due") for m in _records(i, "milestones")}
    for description, due in (first.get("milestones") or {}).items():
        if now.get(description) != due:
            err(f"{iid}: the initial milestone {description!r} and its completion date {due} "
                "should not be changed; record it in milestone_changes")


def _changes(i: dict[str, Any], latest: dt.date | None, err: Err) -> None:
    iid = i.get("id")
    milestones = {m.get("description"): m for m in _records(i, "milestones")}
    changes = _records(i, "milestone_changes")
    for change in changes:
        milestone = milestones.get(change.get("milestone"))
        if milestone is None:
            err(f"{iid}: the change to milestones names {change.get('milestone')!r}, which is "
                "not an initial milestone")
        elif change.get("new_date") == milestone.get("due"):
            err(f"{iid}: the new date of {change.get('milestone')!r} equals its original date")
    changed = {c.get("milestone") for c in changes}
    for description, m in milestones.items():
        if _late(latest, _day(m.get("due"))) and not m.get("completed") \
                and description not in changed:
            err(f"{iid}: the milestone {description!r} missed {m.get('due')} and no new date "
                "and reason are recorded in the changes to milestones")


def poam_dates_kept(ctx: Context) -> list[RunFinding]:
    items = _items(ctx)
    if items is None:
        return []
    out, err = _reporter("ASMT-010", POAM_FILE)
    frozen, latest = poam_dates.load(ctx.run), _latest(ctx)
    for i in items:
        iid = i.get("id")
        _original(i, frozen, err)
        _changes(i, latest, err)
        scheduled = _day(i.get("scheduled_completion"))
        if _late(_block(i, "identified").get("date"), scheduled):
            err(f"{iid}: a scheduled completion date of {scheduled} before the weakness was "
                "identified is no realistic estimate")
        for m in _records(i, "milestones"):
            if _late(m.get("due"), scheduled):
                err(f"{iid}: the milestone completion date {m.get('due')} falls after the "
                    f"scheduled completion date {scheduled}")
    return out


def _finding_states(ctx: Context) -> dict[Any, Any]:
    states = {f.get("id"): f.get("status") for _, f in family_records(ctx, SAR_DIR, "findings")}
    states.update({f.get("id"): f.get("status")
                   for f in _records(_mapping(ctx, STIG_FILE), "findings")})
    return states


def _completed(i: dict[str, Any], states: dict[Any, Any], err: Err) -> None:
    iid, ref = i.get("id"), i.get("finding_ref")
    if states.get(ref) in UNRESOLVED:
        err(f"{iid} is Completed, but {ref} is {states.get(ref)}: the status is used only when "
            "the weakness has been fully resolved")
    if not i.get("completed_on"):
        err(f"{iid} is Completed without the date of completion")
    test = _block(i, "corrective_action_test")
    if not test:
        err(f"{iid} is Completed, but the corrective action has not been tested")


def poam_status(ctx: Context) -> list[RunFinding]:
    items = _items(ctx)
    if items is None:
        return []
    out, err = _reporter("ASMT-011", POAM_FILE)
    states = _finding_states(ctx)
    for i in items:
        iid, status = i.get("id"), i.get("status")
        if status not in STATUS_TERMS:
            err(f"{iid}: the vulnerability status {status} is not Completed, Ongoing, Delayed or "
                "Planned")
        if status == "completed":
            _completed(i, states, err)
        elif i.get("completed_on"):
            err(f"{iid} has an actual completion date, yet its status is {status}")
        if status == "delayed" and not str(i.get("comments") or "").strip():
            err(f"{iid} is Delayed: comments must be used if there is a delay")
        if status == "delayed" and not i.get("obstacles"):
            err(f"{iid} is Delayed and identifies no obstacles or challenges")
    return out


def _rank_of(level: Any) -> int:
    return LEVELS.index(level) if level in LEVELS else -1


def _ranked(rows: Iterable[tuple[Any, Any, Any, Any]], what: str, err: Err) -> None:
    """Rows of (ID, priority, risk level, criticality): a lower risk goes ahead of a higher one
    only when its deficiency is more critical (SP 800-37r2 Task A-6 weighs both)."""
    seen: dict[Any, Any] = {}
    ordered = []
    for ident, priority, level, critical in rows:
        if priority is None:
            err(f"{ident} has no priority in the prioritized approach to risk mitigation")
            continue
        if priority in seen:
            err(f"{seen[priority]} and {ident} share priority {priority}: a prioritized "
                f"approach ranks {what} one by one")
        seen[priority] = ident
        ordered.append((priority, ident, level, critical))
    ordered.sort(key=lambda row: row[0])
    for (_, first, low, first_critical), (_, second, high, second_critical) in zip(
            ordered, ordered[1:], strict=False):
        if 0 <= _rank_of(low) < _rank_of(high) \
                and _rank_of(first_critical) <= _rank_of(second_critical):
            err(f"{first} of {low} risk is prioritized ahead of {second} of {high} risk: the "
                "most critical go first")


def poam_priority(ctx: Context) -> list[RunFinding]:
    items = _items(ctx)
    if items is None:
        return []
    out, err = _reporter("ASMT-012", POAM_FILE)
    _ranked(((i.get("id"), i.get("priority"), i.get("risk_level"), i.get("criticality"))
             for i in items if i.get("status") not in CLOSED_ITEMS), "POA&M items", err)
    risks, rar_err = _reporter("ASMT-012", RAR_FILE)
    _ranked(((r.get("id"), r.get("priority"), r.get("level"), None)
             for r in _records(_mapping(ctx, RAR_FILE), "risks")), "risk responses", rar_err)
    return out + risks
