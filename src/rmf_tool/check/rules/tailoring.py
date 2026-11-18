"""Selection, tailoring and allocation rules, TLR-001 to TLR-010 (Tasks S-1 to S-3).

Each reads ``artifacts/data/tailoring.yaml``, ``allocation.yaml``, ``capabilities.yaml`` or the
generated ``baseline.json`` while its task is active, and stays quiet about a file that is
missing or unreadable (RUN-ART-001 and RUN-FM-001 report those). The assumptions and overlay
conditions come from ``framework/baselines/tailoring-inputs.yaml``.
"""

from __future__ import annotations

import json
import re
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

TAILORING = baseline_mod.TAILORING_FILE
ALLOCATION_FILE = "artifacts/data/allocation.yaml"
CAPABILITIES_FILE = "artifacts/data/capabilities.yaml"
REQ_FILE = "artifacts/ART-REQ.md"
REQS_DATA_FILE = "artifacts/data/requirements.yaml"
RISK_ASSESSMENT = "ART-RA"
# Who accepts the risk of a compensating control: the AO or a designee. Only the authorization
# decision itself is non-delegable (DoDI 8510.01 p. 28); CNSSI 1253 p. 15 says "AO (or designee)".
RISK_ACCEPTORS = ("PER-AO", "PER-AODR")
# The system owner and the authorizing official determine inherited protection (SP 800-53B 2.4).
SYSTEM_OWNER = "PER-PM"
AUTHORIZING = ("PER-AO", "PER-AODR")  # the AO, or the AO's designated representative
LAW_POLICY = ("legislation", "regulation", "policy", "omb-policy")
# An SSP status that says the control is in place, so nothing compensates for it.
IN_PLACE = "implemented"
BASE_NOT_IN_PLACE = ("planned", "not-applicable")
ENHANCEMENT_IN_PLACE = ("implemented", "inherited")
_REQ_ROW = re.compile(r"^\|\s*(REQ-\d{2,3})\s*\|", re.M)


def _active(ctx: Context, *tasks: str) -> bool:
    active = scope.active_tasks(ctx.run)
    return any(t in active for t in tasks)


def _tailoring(ctx: Context) -> dict[str, Any] | None:
    data = ctx.data(TAILORING)
    return data if isinstance(data, dict) else None


def _actions(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in data.get("actions") or [] if isinstance(a, dict)]


def _selected(ctx: Context) -> set[str]:
    return set(baseline_mod.control_ids(ctx.run))


def _ssp_status(ctx: Context) -> dict[str, str]:
    return {str(r.get("control_id")): str(r.get("status"))
            for _, r in family_records(ctx, SSP_DIR, "controls")}


def _categorization(ctx: Context) -> dict[str, Any]:
    cat = facts_mod.get(ctx.facts, "categorization")
    return cat if isinstance(cat, dict) else {}


def _applied(overlay: str, overlays: list[str]) -> bool:
    """Whether an overlay applies, directly or through one of its control sets."""
    return any(o == overlay or o.startswith(f"{overlay}-") for o in overlays)


# --- TLR-001: compensating controls ----------------------------------------------------

def compensating(ctx: Context) -> list[RunFinding]:
    """A compensating control stands in for a baseline control the system cannot implement,
    comes from the catalog unless the catalog has none suitable, and carries the assessment
    and the AO's acceptance of its risk (CNSSI 1253 3.2.2 3.c, SP 800-53B 2.4)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []
    selected = _selected(ctx)
    status = _ssp_status(ctx)
    known = catalog.load(ctx.run.repo).controls

    def err(message: str) -> None:
        out.append(make("TLR-001", message, TAILORING, None, {"S-2"}))

    for a in _actions(data):
        if a.get("action") != "compensating":
            continue
        name = a.get("control_id") or (a.get("other_control") or {}).get("id")
        target = a.get("compensating_for")
        if target not in selected:
            err(f"{name} compensates for {target}, which is not a baseline control; a "
                "compensating control replaces a baseline control")
        elif status.get(target) == IN_PLACE:
            err(f"{name} compensates for {target}, which the SSP records as implemented; "
                "compensating controls are selected only where baseline controls cannot be "
                "implemented")
        if not a.get("cannot_implement"):
            err(f"{name} does not state why the baseline control {target} cannot be "
                "implemented")
        if not a.get("equivalence"):
            err(f"{name} does not state how it provides equivalent or comparable protection "
                f"for {target}")
        source = a.get("source")
        if source not in ("catalog", "other"):
            err(f"{name} does not say whether the compensating control comes from the "
                "control catalog or another source")
        search = a.get("catalog_search") or {}
        considered = search.get("considered") or []
        foreign = sorted(c for c in considered if c not in known)
        if source == "other" and search.get("finding") != "no-suitable-control":
            err(f"{name} adopts a compensating control from another source without the "
                "determination that the control catalog contains no suitable compensating "
                "control")
        if source == "other" and foreign:
            err(f"{name} names {', '.join(foreign)} among the catalog controls considered, "
                "which the control catalog does not contain")
        risk = a.get("risk") or {}
        if not risk.get("assessment"):
            err(f"{name} does not assess the risk associated with implementing the "
                "compensating control")
        elif RISK_ASSESSMENT not in (risk.get("sources") or []):
            err(f"{name}: the assessment of the risk of the compensating control does not "
                "rest on the risk assessment ART-RA")
        if risk.get("accepted_by") not in RISK_ACCEPTORS:
            err(f"{name}: the risk of the compensating control is accepted by "
                f"{risk.get('accepted_by')}, not the authorizing official or designated "
                f"representative ({', '.join(RISK_ACCEPTORS)})")
    return out


# --- TLR-002: removal, scoping and the law and policy test -----------------------------

def _column_selects(tables: dict[str, Any], cid: str, objective: str, level: str) -> bool:
    for table in tables["tables"]:
        for block in table["blocks"]:
            for row in block["controls"]:
                if row["id"] == cid and not row.get("withdrawn"):
                    cell = row[objective][baseline_mod.LEVELS.index(level)]
                    return cell in baseline_mod.SELECTED
    return False


def _profile_selects(ctx: Context, cid: str, level: str) -> bool:
    path = ctx.run.repo / baseline_mod.PROFILE_PATHS[level]
    return cid in baseline_mod.profile_ids(json.loads(path.read_text(encoding="utf-8")))


def _downgrade_problem(ctx: Context, cid: str, objectives: list[str]) -> str | None:
    """Why the downgrade of ``cid`` does not reflect the FIPS 199 category of the objectives
    it supports, or None: the baseline for those objectives' own levels still selects it."""
    cat = _categorization(ctx)
    levels = [cat.get(o) for o in objectives]
    if any(lv not in baseline_mod.LEVELS for lv in levels):
        return None  # FACTS-001 and C-2 own a malformed categorization
    if cat.get("method", baseline_mod.CNSSI) == baseline_mod.CNSSI:
        tables = baseline_mod.load_tables(ctx.run)
        for o, lv in zip(objectives, levels, strict=True):
            if _column_selects(tables, cid, o, lv):
                return f"the {o.upper()} column at {lv} selects it"
        return None
    top = max(levels, key=baseline_mod.LEVELS.index)
    if _profile_selects(ctx, cid, top):
        return f"the SP 800-53B {top} baseline selects it"
    return None


def removal(ctx: Context) -> list[RunFinding]:
    """TLR-002: a remove action rests on a scoping consideration, the absence of risk, or a legal
    or policy requirement whose circumstances do not apply (a downgrade's conditions are
    TLRB-001); and every remove and compensating action is tested against the laws,
    regulations and policies that carry the control (CNSSI 1253 2.6, SP 800-53B 2.4)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-002", message, TAILORING, None, {"S-2"}))

    for a in _actions(data):
        kind = a.get("action")
        if kind not in ("remove", "compensating"):
            continue
        cid = a.get("control_id") or a.get("compensating_for")
        if kind == "remove":
            basis = a.get("basis")
            consideration = (a.get("scoping") or {}).get("consideration")
            if basis is None:
                err(f"{cid} is removed with no basis; a control is tailored out only on a "
                    "scoping consideration, the absence of risk, or a requirement whose "
                    "circumstances do not apply")
            elif basis == "scoping" and consideration is None:
                err(f"{cid} is removed by scoping and names no scoping consideration")
        law = a.get("law_policy")
        if not isinstance(law, dict):
            err(f"{cid}: the {kind} action records no test against the laws, regulations and "
                "policies that carry the control")
            continue
        missed = [k for k in LAW_POLICY if k not in (law.get("reviewed") or [])]
        if missed:
            err(f"{cid}: the {kind} action is not tested against {', '.join(missed)}; "
                "tailoring is conducted in accordance with OMB policy and the laws, "
                "regulations and policies the control carries")
        # A requirement that applies only in circumstances this system lacks does not require
        # the control here (SP 800-53B 2.4); the action names the authority instead.
        excused = a.get("basis") == "circumstance-not-applicable"
        if excused and not law.get("authorities"):
            err(f"{cid} is removed because a requirement's circumstances do not apply, and "
                "law_policy names no authority whose circumstances were tested")
        held_in = kind == "remove" and law.get("requires_control") is True
        if held_in and basis_applies(a):
            err(f"{cid} is required to meet a legislative, regulatory or policy requirement, "
                "so it is not tailored out of the baseline")
        if kind == "compensating" and law.get("requires_control") is True:
            err(f"{cid}: compensating controls are not used to avoid the need to comply with "
                "a legislative, regulatory or policy requirement that requires the control")
    return out


def downgrade(ctx: Context) -> list[RunFinding]:
    """TLRB-001, split from TLR-002: a removal under the security objective consideration names
    the objectives it supports, reflects their FIPS 199 category, rests on the organizational
    assessment of risk and leaves the security-relevant information protected (CNSSI 1253
    2.6)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLRB-001", message, TAILORING, None, {"S-2"}))

    for a in _actions(data):
        if a.get("action") != "remove":
            continue
        cid = a.get("control_id")
        consideration = (a.get("scoping") or {}).get("consideration")
        down = a.get("downgrade") or {}
        objectives = list(down.get("objectives") or [])
        if consideration == "security-objective" and not objectives:
            err(f"{cid} is downgraded under the security objective consideration and names no "
                "security objective it supports")
        problem = _downgrade_problem(ctx, cid, objectives) if objectives else None
        if problem:
            err(f"{cid}: the downgrade does not reflect the FIPS 199 security category of the "
                f"security objectives it supports; {problem}")
        if objectives and RISK_ASSESSMENT not in (down.get("sources") or []):
            err(f"{cid}: the downgrade is not supported by the organizational assessment of risk "
                "ART-RA")
        if objectives and down.get("security_relevant_unaffected") is not True:
            err(f"{cid}: the downgrade affects the protection of the security-relevant "
                "information within the system")
    return out


def basis_applies(action: dict[str, Any]) -> bool:
    """Whether a removal's requirement test binds: not for a requirement whose circumstances
    do not apply to the system, which names its authority instead."""
    return action.get("basis") in ("scoping", "no-risk")


# --- DPOL-001 to DPOL-003, CFLR-001 to CFLR-003: control floors --------------------------

STAND_ALONE = "stand-alone"
NOT_APPLICABLE = "not-applicable"
CATO_FILE = "artifacts/data/cato.yaml"
CATO = "AD-CATO"


def _approvals(data: dict[str, Any], kind: str, key: str) -> dict[Any, Any]:
    """Each control a ``kind`` action names under ``key``, with who approved the action."""
    return {a.get(key): a.get("approved_by") for a in _actions(data) if a.get("action") == kind}


def _binds(ctx: Context, record: dict[str, Any], system_type: dict[str, Any]) -> bool:
    """Whether a floor record's duty binds this system: its ``applies_to`` system types, and
    ``applies_when: cato`` while a cATO is sought (an AD-CATO record or the cATO record)."""
    kinds = record.get("applies_to")
    if kinds and system_type.get("value") not in kinds:
        return False
    if record.get("applies_when") == "cato":
        ledger = ctx.ledger if isinstance(ctx.ledger, list) else []
        return ctx.run.path(CATO_FILE).is_file() or any(
            isinstance(r, dict) and r.get("decision") == CATO for r in ledger)
    return True


def _floor(ctx: Context, rule: str, records: list[dict[str, Any]]) -> list[RunFinding]:
    """A control a floor record of framework/baselines/tailoring-inputs.yaml maps to a duty its
    source places on the system, its users or its program stays in the baseline and in effect,
    whatever law_policy says: it is not removed, not recorded not-applicable in the SSP, and
    not stood in for by a compensating control whose risk the AO or AODR did not accept
    (risk.accepted_by, as TLR-001 reads it; a lead default, for the user's ruling). A
    stand-alone system with no DODIN connection may tailor its control set as appropriate with
    the approval of the AO (DoDI 8500.01 p. 38 1.e.(1).(c), p. 39 1.e.(2).(d).5, which governs
    every DoD IS); that permission is exercised by a remove action, which records the approver
    in approved_by. Inheriting a control is no removal. A record binds only the system types it
    names in applies_to, and under its applies_when condition."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    system_type = facts_mod.get(ctx.facts, "system_type")
    system_type = system_type if isinstance(system_type, dict) else {}
    stand_alone = system_type.get("connectivity") == STAND_ALONE \
        and system_type.get("dodin_connection") == "none"
    removed = _approvals(data, "remove", "control_id")
    compensated = {a.get("compensating_for"): (a.get("risk") or {}).get("accepted_by")
                   for a in _actions(data) if a.get("action") == "compensating"}
    status = _ssp_status(ctx)
    out: list[RunFinding] = []

    def err(policy: dict[str, Any], what: str) -> None:
        out.append(make(rule, f"{policy['id']}: {policy['authority']} requires that "
                        f"{policy['text']}, and {what}", TAILORING, None, {"S-2"}))

    for policy in records:
        if not _binds(ctx, policy, system_type):
            continue
        controls = policy["controls"]
        cut = [c for c in controls if c in removed and not stand_alone]
        unapproved = [c for c in controls if c in removed and stand_alone
                      and removed[c] not in AUTHORIZING]
        waived = [c for c in controls if status.get(c) == NOT_APPLICABLE]
        stood_in = [c for c in controls if c in compensated
                    and compensated[c] not in AUTHORIZING]
        if cut:
            err(policy, f"{', '.join(cut)} is tailored out of the baseline")
        if unapproved:
            err(policy, f"{', '.join(unapproved)} is tailored out of a stand-alone system's "
                "baseline without the approval of the AO or AODR")
        if waived:
            err(policy, f"{', '.join(waived)} is recorded not-applicable in the SSP")
        if stood_in:
            err(policy, f"a compensating control stands for {', '.join(stood_in)} without its "
                "risk accepted by the AO or AODR")
    return out


def _dod_policy(ctx: Context, rule: str, subject: str) -> list[RunFinding]:
    """The dod_policy_controls records of one subject: DoDI 8500.01's duties."""
    records = baseline_mod.load_inputs(ctx.run.repo).get("dod_policy_controls") or []
    return _floor(ctx, rule, [p for p in records if p["subject"] == subject])


def _control_floor(ctx: Context, rule: str) -> list[RunFinding]:
    """The control_floors records one rule judges, one source family each."""
    records = baseline_mod.load_inputs(ctx.run.repo).get("control_floors") or []
    return _floor(ctx, rule, [p for p in records if p["rule"] == rule])


def dod_system_controls(ctx: Context) -> list[RunFinding]:
    """DPOL-001: the controls that carry DoDI 8500.01's duties on the system."""
    return _dod_policy(ctx, "DPOL-001", "system")


def dod_user_controls(ctx: Context) -> list[RunFinding]:
    """DPOL-002: the controls that carry DoDI 8500.01's duties on the ISSO, privileged users and
    authorized users."""
    return _dod_policy(ctx, "DPOL-002", "users")


def dod_program_controls(ctx: Context) -> list[RunFinding]:
    """DPOL-003: the controls that carry DoDI 8500.01's duties on DoD IT through the DoD
    Component's cybersecurity program."""
    return _dod_policy(ctx, "DPOL-003", "program")


def nist_floor(ctx: Context) -> list[RunFinding]:
    """CFLR-001: the controls that carry FIPS 200's minimum security requirements and the SP
    800-53A assessment policy. The stand-alone permission _floor allows is DoDI 8500.01's
    (pp. 38-39), which governs every DoD IS, FIPS 200 floors included; FIPS 200 itself allows
    no waiver (p. 5). A lead default, for the user's ruling."""
    return _control_floor(ctx, "CFLR-001")


def dodin_floor(ctx: Context) -> list[RunFinding]:
    """CFLR-002: the controls that carry DoDI 8530.01's DODIN protection duties."""
    return _control_floor(ctx, "CFLR-002")


def dod_acquisition_floor(ctx: Context) -> list[RunFinding]:
    """CFLR-003: the controls that carry the duties of DoDI 5000.83, DoDI 8531.01 and the DoD
    CIO cATO evaluation criteria."""
    return _control_floor(ctx, "CFLR-003")


# --- TLR-003: baseline and overlay assumptions -----------------------------------------

def assumptions(ctx: Context) -> list[RunFinding]:
    """S-2 tests each assumption under the baselines and the applied overlays. One that fails
    revisits the selection; one the baselines do not address that holds supplements it
    (SP 800-53B 2.3, CNSSI 1253 2.4)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-003", message, TAILORING, None, {"S-2"}))

    overlays = list(_categorization(ctx).get("overlays") or [])
    framework = baseline_mod.load_inputs(ctx.run.repo)["assumptions"]
    applicable = {a["id"]: a for a in framework
                  if "overlay" not in a or _applied(a["overlay"], overlays)}
    records = {str(r.get("id")): r for r in data.get("assumptions") or []
               if isinstance(r, dict)}
    actions = _actions(data)
    acted = {a.get("control_id") for a in actions} | {a.get("compensating_for")
                                                       for a in actions}
    added = {a.get("control_id") for a in actions if a.get("action") == "add"}
    selected = _selected(ctx)
    for aid in applicable:
        if aid not in records:
            err(f"tailoring.yaml does not test the assumption {aid} "
                f"({applicable[aid]['text']})")
    for aid, record in records.items():
        spec = applicable.get(aid)
        if spec is None:
            err(f"{aid} is not an assumption of the baselines or of an applied overlay "
                f"({baseline_mod.INPUTS_PATH})")
            continue
        controls = list(record.get("controls") or [])
        named = list(record.get("overlays") or [])
        unapplied = [o for o in named if not _applied(o, overlays)]
        if unapplied:
            err(f"{aid} names the overlay {', '.join(unapplied)}, which "
                "categorization.overlays does not apply")
        # A baseline assumption that fails, or one the baselines leave out that holds.
        diverges = spec["when"] == "holds-false" and record.get("holds") is False
        applies = spec["when"] == "holds-true" and record.get("holds") is True
        untouched = sorted(c for c in controls if c not in acted)
        unmet = sorted(c for c in controls if c not in added and c not in selected)
        no_change = record.get("outcome") == "revisited-no-change"
        if diverges and not controls and not named and not spec.get("controls"):
            err(f"the assumption {aid} does not hold, and the control selection is not "
                "revisited by an overlay or by tailoring")
        if diverges and untouched:
            err(f"the assumption {aid} does not hold, and no tailoring action revisits "
                f"{', '.join(untouched)}")
        # The Space Platform Overlay tailors out Table 1's Associated Controls on each of its
        # assumptions: where one fails, they "should be revisited and considered for inclusion".
        # Considered and kept out is a revisit too: the record says so with its rationale.
        tailored_out = sorted(c for c in spec.get("controls") or () if c not in acted)
        if diverges and tailored_out and record.get("outcome") != "revisited-no-change":
            err(f"the assumption {aid} does not hold, and the controls the overlay tailors out "
                f"on it are not revisited: {', '.join(tailored_out)}")
        if applies and not controls and not named and not no_change:
            err(f"the assumption {aid} applies, so additional controls are likely needed, and "
                "no control, overlay or revisited-no-change outcome is named")
        if applies and unmet:
            err(f"the assumption {aid} applies, and {', '.join(unmet)} is neither in the "
                "baseline nor supplemented by an add action")
    return out


# --- TLR-004: assurance ----------------------------------------------------------------

def assurance(ctx: Context) -> list[RunFinding]:
    """S-2 determines whether additional assurance-related controls are needed, and if so
    adds controls the catalog marks as contributing to assurance (CNSSI 1253 3.2.2 3.f.5)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-004", message, TAILORING, None, {"S-2"}))

    cat = catalog.load(ctx.run.repo)
    added = [a for a in _actions(data) if a.get("action") == "add"]
    assured = [a.get("control_id") for a in added
               if catalog.contributes_to_assurance(cat, str(a.get("control_id")))]
    record = data.get("assurance")
    if not isinstance(record, dict):
        err("tailoring.yaml does not determine whether additional assurance-related controls "
            "are needed to increase the trustworthiness of the system")
    elif record.get("additional_needed") is True and len(assured) == 0:
        err("additional assurance-related controls are needed, and no add action tailors in a "
            "control the catalog marks as contributing to assurance")
    for a in added:
        cid = str(a.get("control_id"))
        if a.get("assurance") is True and not catalog.contributes_to_assurance(cat, cid):
            err(f"{cid} is added as an assurance-related control, and the catalog does not "
                "mark it as contributing to assurance")
    return out


# --- TLR-005: overlay conditions -------------------------------------------------------

def overlay_conditions(ctx: Context) -> list[RunFinding]:
    """An applied overlay's conditions are each answered, and a condition that applies
    selects its controls (CNSSI 1253E Attachment 5, Table 2 and Section 7)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-005", message, TAILORING, None, {"S-2"}))

    overlays = list(_categorization(ctx).get("overlays") or [])
    conditions = [c for c in baseline_mod.load_inputs(ctx.run.repo)["overlay_conditions"]
                  if _applied(c["overlay"], overlays)]
    answers = {(str(r.get("overlay")), str(r.get("condition"))): r
               for r in data.get("overlay_conditions") or [] if isinstance(r, dict)}
    selected = _selected(ctx)
    for c in conditions:
        answer = answers.get((c["overlay"], c["id"]))
        if answer is None:
            err(f"the {c['overlay']} condition {c['id']} is not answered by tailoring.yaml "
                f"overlay_conditions: {c['question']}")
            continue
        missing = sorted(x for x in c["controls"] if x not in selected)
        if answer.get("applies") is True and missing:
            err(f"the {c['overlay']} condition {c['id']} applies, so {', '.join(missing)} "
                "must be selected, and the baseline does not select it")
    return out


# --- TLR-006: specification information ------------------------------------------------

def specification(ctx: Context) -> list[RunFinding]:
    """Control specification information is provided for a selected control
    (CNSSI 1253 3.2.2 3.f, SP 800-53B 2.4)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []
    selected = _selected(ctx)
    for a in _actions(data):
        if a.get("action") != "specification":
            continue
        cid = a.get("control_id")
        spec = a.get("specification") or {}
        if not spec.get("text"):
            out.append(make("TLR-006", f"{cid}: the specification action provides no control "
                            "specification information", TAILORING, None, {"S-2"}))
        if cid not in selected:
            out.append(make("TLR-006", f"{cid}: specification information is provided for a "
                            "control the baseline does not select", TAILORING, None, {"S-2"}))
    return out


# --- TLR-007: enhancements and their base control --------------------------------------

def enhancements(ctx: Context) -> list[RunFinding]:
    """A selected control enhancement needs its base control selected and implemented
    (SP 800-53 2.2, SP 800-53B 2.2)."""
    if not _active(ctx, "S-1", "S-2"):
        return []
    out: list[RunFinding] = []
    selected = _selected(ctx)
    status = _ssp_status(ctx)
    for cid in sorted(selected):
        base, dot, _ = cid.partition(".")
        if not dot:
            continue
        if base not in selected:
            out.append(make("TLR-007", f"the control enhancement {cid} is selected without "
                            f"the selection of its base control {base}",
                            baseline_mod.BASELINE_FILE, None, {"S-1", "S-2"}))
        elif status.get(cid) in ENHANCEMENT_IN_PLACE and status.get(base) in BASE_NOT_IN_PLACE:
            out.append(make("TLR-007", f"the control enhancement {cid} is {status[cid]}, and "
                            f"the implementation of its base control {base} is "
                            f"{status[base]}", SSP_DIR, None, {"S-4"}))
    return out


# --- TLR-008 and TLR-011: capabilities -----------------------------------------------

def _capabilities(ctx: Context) -> list[dict[str, Any]] | None:
    data = ctx.data(CAPABILITIES_FILE)
    if not isinstance(data, dict) or not _active(ctx, "S-1"):
        return None
    return [c for c in data.get("capabilities") or [] if isinstance(c, dict)]


def capabilities(ctx: Context) -> list[RunFinding]:
    """A defined capability documents the mapping of the catalog controls that support it
    (SP 800-53A 3.5, SP 800-53B 2.5)."""
    caps = _capabilities(ctx)
    if not caps:  # read the catalog only when there is a mapping to judge
        return []
    known = catalog.load(ctx.run.repo).controls
    out: list[RunFinding] = []
    for cap in caps:
        foreign = sorted(c for c in cap.get("controls") or [] if c not in known)
        if foreign:
            out.append(make("TLR-008", f"the capability {cap.get('id')} maps "
                            f"{', '.join(foreign)}, which the control catalog does not contain, "
                            "so the mapping of the controls that support it is not documented",
                            CAPABILITIES_FILE, None, {"S-1"}))
    return out


def capability_gaps(ctx: Context) -> list[RunFinding]:
    """A capability that leans on an unselected control is a gap S-2 weighs for
    supplementation, not an error: the baseline may legitimately leave it out."""
    selected = _selected(ctx)
    out: list[RunFinding] = []
    for cap in _capabilities(ctx) or []:
        unselected = sorted(c for c in cap.get("controls") or [] if c not in selected)
        if unselected:
            out.append(make("TLR-011", f"the capability {cap.get('id')} maps to "
                            f"{', '.join(unselected)}, which the baseline does not select; "
                            "S-2 weighs supplementing it", CAPABILITIES_FILE, None, {"S-1", "S-2"}))
    return out


# --- TLR-009: requirement traceability -------------------------------------------------

def requirement_trace(ctx: Context) -> list[RunFinding]:
    """Each allocated control records the requirements it satisfies, and every requirement of
    ART-REQ is satisfied by a control (SP 800-37r2 2.1, CNSSI 1254 Table C-1)."""
    data = ctx.data(ALLOCATION_FILE)
    path = ctx.run.path(REQ_FILE)
    if not isinstance(data, dict) or not path.is_file() or not _active(ctx, "S-3"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-009", message, ALLOCATION_FILE, None, {"S-3"}))

    defined = set(_REQ_ROW.findall(path.read_text(encoding="utf-8")))
    traced: dict[str, list[str]] = {}
    for a in data.get("allocations") or []:
        if isinstance(a, dict):
            for req in a.get("requirements") or []:
                traced.setdefault(str(req), []).append(str(a.get("control_id")))
    if len(defined) == 0:
        err("ART-REQ lists no requirement IDs (REQ-##), so no control can be traced to the "
            "security and privacy requirements it satisfies")
    for req in sorted(set(traced) - defined):
        err(f"{', '.join(traced[req])} traces to {req}, which is not a requirement of ART-REQ")
    # a design policy requirement no control carries (Section 508, the IT Standards Registry)
    # may be met by design or verification instead (F-05-2)
    outside = {str(r.get("id")): r for r in (ctx.data(REQS_DATA_FILE) or {}).get("requirements")
               or [] if isinstance(r, dict) and r.get("satisfied_by")}
    for req in sorted(defined - set(traced)):
        r = outside.get(req)
        if r is not None and r.get("policy"):
            continue
        if r is not None:
            err(f"the requirement {req} is marked satisfied_by {r.get('satisfied_by')}, but only "
                "a requirement carrying a design policy statement may be met outside the "
                "control set")
            continue
        err(f"the requirement {req} is satisfied by no control; traceability of controls to "
            "the requirements ensures all requirements are addressed")
    return out


# --- TLR-010: common control inheritance -----------------------------------------------

def referenced(ctx: Context) -> list[RunFinding]:
    """SSPI-001: a control S-3 allocates as a common control is referenced in the inheriting
    system's security plan as inherited, from a named provider (SP 800-37r2 2.4, Task S-4)."""
    data = ctx.data(ALLOCATION_FILE)
    if not isinstance(data, dict) or not (_active(ctx, "S-3") and _active(ctx, "S-4")):
        return []
    common = {str(a.get("control_id")): a.get("provider") for a in data.get("allocations") or []
              if isinstance(a, dict) and a.get("type") == "common"}
    out: list[RunFinding] = []
    for rel, item in family_records(ctx, SSP_DIR, "controls"):
        cid = str(item.get("control_id"))
        if cid in common and item.get("status") != "inherited":
            out.append(make("SSPI-001", f"{cid} is allocated as a common control of "
                            f"{common[cid]}, and the security plan does not reference it as "
                            f"inherited (status {item.get('status')})", rel, None, {"S-4"}))
    return out


def inheritance(ctx: Context) -> list[RunFinding]:
    """The system owner and the AO determine, for each provider, that the common controls on
    offer protect the inheriting system commensurate with risk, having examined their
    parameters (SP 800-53B 2.4, SP 800-53 2.3)."""
    data = ctx.data(ALLOCATION_FILE)
    if not isinstance(data, dict) or not _active(ctx, "S-3"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TLR-010", message, ALLOCATION_FILE, None, {"S-3"}))

    allocations = [a for a in data.get("allocations") or [] if isinstance(a, dict)]
    providers = {str(p.get("provider")): p for p in data.get("providers") or []
                 if isinstance(p, dict)}
    named = sorted({str(a["provider"]) for a in allocations
                    if a.get("type") in ("common", "hybrid") and a.get("provider")})
    for name in named:
        record = providers.get(name)
        if record is None:
            err(f"controls are inherited from {name}, and no determination records that its "
                "common controls protect the system commensurate with risk")
            continue
        det = record.get("determination") or {}
        deciders = set(det.get("by") or [])
        if SYSTEM_OWNER not in deciders or not deciders & set(AUTHORIZING):
            err(f"the determination for {name} is not made by the system owner ({SYSTEM_OWNER}) "
                f"and the authorizing official or designated representative "
                f"({', '.join(AUTHORIZING)}); system owners and authorizing officials "
                "determine if the common controls provide protection commensurate with risk")
        common = sorted(str(a.get("control_id")) for a in allocations
                        if a.get("provider") == name and a.get("type") == "common")
        if det.get("commensurate") is not True and common:
            err(f"{', '.join(common)} is inherited whole from {name}, whose common controls "
                "are not determined to provide protection commensurate with risk")
        if det.get("parameters_examined") is not True:
            err(f"the determination for {name} does not examine the control parameters "
                "when determining if the common control is adequate to mitigate "
                "system-specific risks")
    return out


# --- TRADE-001: cost, schedule and performance weighed in tailoring -------------------------

def trade_offs(ctx: Context) -> list[RunFinding]:
    """TRADE-001: S-2 records the risk-related issues weighed in deciding which controls to
    employ, at least one trade-off of whatever factor applies (SP 800-53B 2.4: risk-related issues
    *such as* cost, schedule and performance, an open list), and a trade-off that removed a control
    matches a remove action of tailoring.yaml, whose basis TLR-002 holds to a risk-based
    determination (CNSSI 1253 3.2.2 3.f.4)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TRADE-001", message, TAILORING, None, {"S-2"}))

    records = [r for r in data.get("trade_offs") or [] if isinstance(r, dict)]
    if not records:
        err("tailoring.yaml records no trade-off of the risk-related issues weighed in deciding "
            "which controls to employ")
        return out
    removed = {a.get("control_id") for a in _actions(data) if a.get("action") == "remove"}
    for r in records:
        if r.get("outcome") != "removed":
            continue
        for cid in r.get("controls") or []:
            if cid not in removed:
                err(f"a {r.get('factor')} trade-off removes {cid}, which no remove action of "
                    "tailoring.yaml removes")
    return out


# --- OVC-001: conflicts between overlays, and who resolves them -----------------------------

CONFLICT_DECIDERS = (("PER-AO", "PER-AODR"), ("PER-PRIV",))
CONFLICT_PARTIES = {"PER-IO": "the information owner", "PER-PM": "the information system owner",
                    "PER-RE": "the risk executive (function)"}


def overlay_conflicts(ctx: Context) -> list[RunFinding]:
    """OVC-001: a conflict between overlays over applying or removing a control is resolved by
    the AO or its designee (PER-AODR) and the SAOP, in coordination with the information owner,
    the system owner and the risk executive (function) (CNSSI 1253 3.2.2.2)."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    out: list[RunFinding] = []
    for c in data.get("overlay_conflicts") or []:
        if not isinstance(c, dict):
            continue
        what = ", ".join(str(x) for x in c.get("controls") or [])
        deciders = set(c.get("resolved_by") or [])
        if not all(deciders & set(group) for group in CONFLICT_DECIDERS):
            out.append(make("OVC-001", f"the overlay conflict over {what} is not resolved by the "
                            "AO (or designee) and the SAOP (or designee)", TAILORING, None,
                            {"S-2"}))
        parties = set(c.get("coordinated_with") or [])
        for persona, name in CONFLICT_PARTIES.items():
            if persona not in parties:
                out.append(make("OVC-001", f"the overlay conflict over {what} is resolved without "
                                f"coordination with {name} ({persona})", TAILORING, None,
                                {"S-2"}))
    return out
