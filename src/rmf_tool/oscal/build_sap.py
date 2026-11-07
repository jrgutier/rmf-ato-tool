"""OSCAL assessment plan builder (ART-SAP; plan §6.6 ``mapping.yaml``).

``artifacts/data/sap.yaml`` holds what the agent decides at A-2 (scope exclusions, subjects,
team, schedule, rules of engagement, procedures). The reviewed controls come from
``baseline.json``, and the activities from ``procedures`` or, on an older run with none, the
catalog's SP 800-53A assessment-method parts.
Subjects reuse the SSP's uuid5 IDs for components, inventory items, users and parties.
"""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.oscal.common import (
    NotBuildable,
    day,
    doc_metadata,
    load_data,
    party_uuid,
    prop,
    serialize,
    trace_props,
    with_personas,
)
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import OSCAL_DIR, Run

SAP_FILE = f"{OSCAL_DIR}/assessment-plan.json"
SAP_DATA = "artifacts/data/sap.yaml"
MODEL = "assessment-plan"
METHODS = ("EXAMINE", "INTERVIEW", "TEST")
SUBJECT_KEYS = {"component": "component", "inventory-item": "inventory", "user": "user",
                "location": "location"}


def load_sap(run: Run, reasons: list[str]) -> dict[str, Any] | None:
    """sap.yaml plus the inputs every assessment document needs (system_id, baseline.json)."""
    facts = facts_mod.load(run)
    if facts_mod.value(facts, "system_id") is None:
        reasons.append("facts.yaml system_id not set")
    if baseline_mod.load(run) is None:
        reasons.append("baseline.json missing (rmf baseline resolve)")
    sap = load_data(run, SAP_DATA, "sap", reasons)
    if sap is not None and baseline_mod.load(run) is not None and not scoped_controls(run, sap):
        reasons.append(f"{SAP_DATA} excludes every baseline control (see SAP-COV-001)")
    return sap


def excluded(sap: dict[str, Any]) -> dict[str, str]:
    return {e["control_id"]: e["rationale"] for e in sap["scope"]["excluded_controls"]}


def scoped_controls(run: Run, sap: dict[str, Any]) -> list[str]:
    """The baseline controls minus the SAP's exclusions, in baseline order."""
    out = excluded(sap)
    return [c for c in baseline_mod.control_ids(run) if c not in out]


def reviewed_controls(run: Run, sap: dict[str, Any]) -> dict[str, Any]:
    base = baseline_mod.load(run) or {}
    selection: dict[str, Any] = {}
    scoped = scoped_controls(run, sap)
    if scoped:
        selection["include-controls"] = [{"control-id": c} for c in scoped]
    out = excluded(sap)
    if out:
        selection["exclude-controls"] = [{"control-id": c} for c in out]
        selection["remarks"] = " ".join(f"{c}: {why}" for c, why in out.items())
    return {"description": f"The controls of baseline {base.get('baseline_id')} in the "
                           "assessment scope.",
            "control-selections": [selection]}


def subject_uuid(sid: str, kind: str, ident: str) -> str:
    if kind == "party":
        return party_uuid(sid, ident)
    return uuid_for(sid, "ssp", f"{SUBJECT_KEYS[kind]}/{ident}")


def subjects(sid: str, sap: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for s in sap["assessment_subjects"]:
        if s["include"] == "all":
            out.append({"type": s["type"], "include-all": {}})
        else:
            out.append({"type": s["type"], "include-subjects": [
                {"subject-uuid": subject_uuid(sid, s["type"], i), "type": s["type"]}
                for i in s["include"]]})
    return out


def method_controls(run: Run, controls: list[str]) -> dict[str, list[str]]:
    """Method (EXAMINE, INTERVIEW, TEST) -> the controls whose catalog entry defines it."""
    cat = catalog.load(run.repo)
    out: dict[str, list[str]] = {m: [] for m in METHODS}
    for cid in controls:
        for part in cat.controls.get(cid, {}).get("parts") or []:
            if part.get("name") != "assessment-method":
                continue
            method = next((p["value"] for p in part.get("props") or []
                           if p.get("name") == "method"), None)
            if method in out and cid not in out[method]:
                out[method].append(cid)
    return out


def planned_methods(sap: dict[str, Any], controls: list[str]) -> dict[str, list[str]]:
    """Method -> the scoped controls whose selected procedures use it, in scope order."""
    out: dict[str, list[str]] = {m: [] for m in METHODS}
    chosen = {(m.upper(), c) for p in sap["procedures"] for c in p["controls"]
              for m in p["methods"]}
    for method, listed in out.items():
        listed.extend(c for c in controls if (method, c) in chosen)
    return out


def activity_uuid(sid: str, method: str) -> str:
    return uuid_for(sid, MODEL, f"activity/{method.lower()}")


def build_sap(run: Run) -> str:
    """oscal/assessment-plan.json; raises NotBuildable while inputs are missing or invalid."""
    from trestle.oscal.assessment_plan import AssessmentPlan

    reasons: list[str] = []
    sap = load_sap(run, reasons)
    if reasons:
        raise NotBuildable(reasons)

    facts = facts_mod.load(run)
    sid = facts_mod.value(facts, "system_id")
    name = facts_mod.value(facts, "system_name") or sid
    team = [m["persona"] for m in sap["team"]]
    subject_list = subjects(sid, sap)
    scoped = scoped_controls(run, sap)
    by_method = planned_methods(sap, scoped) if sap.get("procedures") \
        else method_controls(run, scoped)
    activities = [
        {"uuid": activity_uuid(sid, m), "title": f"{m.capitalize()} (SP 800-53A)",
         "description": f"Apply the SP 800-53A {m.lower()} method to the assessment objects "
                        f"that each control's {m.lower()} procedure names.",
         "props": [prop("method", m, None)],
         "related-controls": {"control-selections": [
             {"include-controls": [{"control-id": c} for c in controls]}]}}
        for m, controls in by_method.items() if controls]

    schedule = sap["schedule"]
    milestones = [
        {"uuid": uuid_for(sid, MODEL, f"task/event/{i}"), "type": "milestone",
         "title": e["description"],
         **({"props": [prop("event-kind", e["kind"])]} if e.get("kind") else {}),
         "timing": {"on-date": {"date": day(e["date"])}}}
        for i, e in enumerate(schedule.get("events") or [], start=1)]
    task: dict[str, Any] = {
        "uuid": uuid_for(sid, MODEL, "task/assessment"), "type": "action",
        "title": "Control assessment",
        "description": f"Assess the controls in scope from {schedule['start']} to "
                       f"{schedule['end']}.",
        "timing": {"within-date-range": {"start": day(schedule["start"]),
                                         "end": day(schedule["end"], end=True)}},
        "responsible-roles": [{"role-id": p} for p in sorted(set(team))],
    }
    if activities:
        task["associated-activities"] = [{"activity-uuid": a["uuid"], "subjects": subject_list}
                                         for a in activities]
    if milestones:
        task["tasks"] = milestones

    team_text = "; ".join(
        f"{m['persona']} ({m['role']}"
        + (", independent" if m.get("independent") else "") + ")" for m in sap["team"])
    terms = [{"name": "rules-of-engagement", "title": "Rules of engagement",
              "prose": sap["rules_of_engagement"].strip()},
             {"name": "assessment-team", "title": "Assessment team", "prose": team_text}]
    body: dict[str, Any] = {
        "uuid": uuid_for(sid, MODEL, "assessment-plan"),
        "import-ssp": {"href": "ssp.json"},
        "reviewed-controls": reviewed_controls(run, sap),
        "assessment-subjects": subject_list,
        "assessment-assets": {"assessment-platforms": [
            {"uuid": uuid_for(sid, MODEL, "platform/team"), "title": "Assessment team",
             "props": [prop("assessor", m["persona"]) for m in sap["team"]]}]},
        "tasks": [task],
        "terms-and-conditions": {"parts": terms},
    }
    if activities:
        body["local-definitions"] = {"activities": activities}
    metadata = doc_metadata(run, f"{name} Security Assessment Plan (draft)")
    metadata["props"] = trace_props(sap["sources"])
    body = {"uuid": body.pop("uuid"),
            "metadata": with_personas(run, sid, metadata, body), **body}
    return serialize(AssessmentPlan, body)
