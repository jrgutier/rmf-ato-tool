"""OSCAL assessment results builder (ART-SAR; plan §6.6 ``mapping.yaml``).

One result per run. Each SAR determination (``sar/results/<fam>.yaml``) becomes an
observation, each SAR finding (FND-###) a finding that targets the control's assessment
objective, each STIG finding (``stig-summary.yaml``, STG-###) an observation on its inventory
item, and each RAR risk (``rar.yaml``, RSK-###) a risk. ``assessment_entities`` is shared with
the POA&M builder, so the POA&M repeats these objects under the same uuid5 IDs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.oscal.build_sap import load_sap, reviewed_controls
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

SAR_FILE = f"{OSCAL_DIR}/assessment-results.json"
SAR_RESULTS_DIR = "artifacts/sar/results"
STIG_DATA = "artifacts/data/stig-summary.yaml"
RAR_DATA = "artifacts/data/rar.yaml"
POAM_DATA = "artifacts/poam/items.yaml"
MODEL = "assessment-results"
NIST_NS = "http://csrc.nist.gov/ns/oscal"


@dataclass
class Entities:
    """OSCAL objects keyed by their run-data ID: ``observations`` by control ID (one per
    determination) or STG-###, ``findings`` by FND-###, ``risks`` by RSK-###."""

    observations: dict[str, dict[str, Any]] = field(default_factory=dict)
    findings: dict[str, dict[str, Any]] = field(default_factory=dict)
    risks: dict[str, dict[str, Any]] = field(default_factory=dict)


def load_results(run: Run, reasons: list[str], required: bool = True) -> list[dict[str, Any]]:
    files = sorted(run.path(SAR_RESULTS_DIR).glob("*.yaml"))
    if not files and required:
        reasons.append(f"no {SAR_RESULTS_DIR}/<fam>.yaml yet (A-3)")
    out = []
    for path in files:
        data = load_data(run, run.rel(path), "sar-results", reasons)
        if data:
            out.append(data)
    return out


def observation_uuid(sid: str, key: str) -> str:
    return uuid_for(sid, MODEL, f"observation/{key}")


def _target(run: Run, control_id: str) -> tuple[str, str]:
    """(type, id) of the catalog part a finding targets: the assessment objective if the
    catalog defines one, else the control statement."""
    parts = {p.get("name"): p.get("id")
             for p in catalog.load(run.repo).controls.get(control_id, {}).get("parts") or []}
    if parts.get("assessment-objective"):
        return "objective-id", parts["assessment-objective"]
    return "statement-id", parts.get("statement") or f"{control_id}_smt"


def _risk_status(risk: dict[str, Any], poam_status: dict[str, str]) -> str:
    if risk["response"] == "accept":
        return "deviation-approved"
    states = [poam_status.get(p) for p in risk["poam_refs"]]
    if states and all(s == "completed" for s in states):
        return "closed"
    return "remediating" if states else "open"


def assessment_entities(run: Run, sid: str, results: list[dict[str, Any]],
                        stig: dict[str, Any] | None, rar: dict[str, Any] | None,
                        poam: dict[str, Any] | None, assessors: list[str],
                        collected: str) -> Entities:
    out = Entities()
    actors = [{"type": "party", "actor-uuid": party_uuid(sid, p), "role-id": p}
              for p in sorted(set(assessors))]
    origins = {"origins": [{"actors": actors}]} if actors else {}

    for family in results:
        for d in family["determinations"]:
            ctl = d["control_id"]
            out.observations[ctl] = {
                "uuid": observation_uuid(sid, ctl), "title": f"{ctl} determination",
                "description": d["summary"].strip(),
                "props": [prop("control-id", ctl), prop("result", d["result"])]
                + trace_props(d["sources"]),
                "methods": [m.upper() for m in d["methods"]],
                "types": ["control-objective"], **origins, "collected": collected,
            }
    benchmarks = {b["id"]: b for b in (stig or {}).get("benchmarks") or []}
    for s in (stig or {}).get("findings") or []:
        bm = benchmarks.get(s["benchmark"], {})
        props = [prop("stig-finding-id", s["id"]), prop("rule-id", s["rule_id"]),
                 prop("category", s["category"]), prop("result", s["status"])]
        if bm:
            props.append(prop("benchmark", f"{bm['title']} {bm['version']}"))
        if s.get("control_id"):
            props.append(prop("control-id", s["control_id"]))
        out.observations[s["id"]] = {
            "uuid": observation_uuid(sid, s["id"]), "title": s["title"],
            "description": f"{s['rule_id']} ({s['category']}) on {s['inventory_item']}: "
                           f"{s['status']}.",
            "props": props + trace_props((stig or {}).get("sources")),
            "methods": ["TEST"], "types": ["finding" if s["status"] == "open" else "discovery"],
            **origins,
            "subjects": [{"subject-uuid": uuid_for(sid, "ssp", f"inventory/{s['inventory_item']}"),
                          "type": "inventory-item"}],
            "collected": day(bm["scan_date"]) if bm.get("scan_date") else collected,
        }

    risks = (rar or {}).get("risks") or []
    for family in results:
        for f in family["findings"]:
            ctl = f["control_id"]
            kind, target = _target(run, ctl)
            finding: dict[str, Any] = {
                "uuid": uuid_for(sid, MODEL, f"finding/{f['id']}"), "title": f["title"],
                "description": f["description"].strip(),
                "props": [prop("finding-id", f["id"]), prop("control-id", ctl),
                          prop("severity", f["severity"]), prop("result", f["status"])]
                + trace_props(f["sources"]),
                **origins,
                "target": {"type": kind, "target-id": target, "status": {
                    "state": "satisfied" if f["status"] == "closed" else "not-satisfied"}},
            }
            if ctl in out.observations:
                finding["related-observations"] = [
                    {"observation-uuid": out.observations[ctl]["uuid"]}]
            linked = [r for r in risks if f["id"] in r["finding_refs"]]
            if linked:
                finding["related-risks"] = [
                    {"risk-uuid": uuid_for(sid, MODEL, f"risk/{r['id']}")} for r in linked]
            if f.get("recommendation"):
                finding["remarks"] = f["recommendation"].strip()
            out.findings[f["id"]] = finding

    controls = {f["id"]: f["control_id"] for family in results for f in family["findings"]}
    poam_status = {i["id"]: i["status"] for i in (poam or {}).get("items") or []}
    rar_task = run.artifacts.get("ART-RAR", {}).get("producer")
    analysts = (run.tasks.get(rar_task, {}).get("raci") or {}).get("R") or []
    for r in risks:
        risk: dict[str, Any] = {
            "uuid": uuid_for(sid, MODEL, f"risk/{r['id']}"), "title": r["title"],
            "description": r["description"].strip(),
            "statement": f"Likelihood {r['likelihood']} and impact {r['impact']} give a "
                         f"{r['level']} risk level (SP 800-30); response: {r['response']}.",
            "props": [prop("risk-id", r["id"]), prop("response", r["response"])]
            + trace_props(r["sources"]),
            "status": _risk_status(r, poam_status),
        }
        if analysts:  # trestle orders keys by model field, so late insertion is harmless
            risk["characterizations"] = [{
                "origin": {"actors": [{"type": "party", "actor-uuid": party_uuid(sid, p),
                                       "role-id": p} for p in analysts]},
                "facets": [{"name": name, "system": NIST_NS, "value": r[key]}
                           for name, key in (("likelihood", "likelihood"), ("impact", "impact"),
                                             ("risk", "level"))]}]
        evidence = [k for ref in r["finding_refs"]
                    for k in (controls.get(ref), ref) if k in out.observations]
        if evidence:
            risk["related-observations"] = [
                {"observation-uuid": out.observations[k]["uuid"]} for k in dict.fromkeys(evidence)]
        out.risks[r["id"]] = risk
    return out


def build_sar(run: Run) -> str:
    """oscal/assessment-results.json; raises NotBuildable while inputs are missing."""
    from trestle.oscal.assessment_results import AssessmentResults

    reasons: list[str] = []
    sap = load_sap(run, reasons)
    results = load_results(run, reasons)
    stig = load_data(run, STIG_DATA, "stig-summary", reasons, required=False)
    rar = load_data(run, RAR_DATA, "rar", reasons, required=False)
    poam = load_data(run, POAM_DATA, "poam-items", reasons, required=False)
    if reasons:
        raise NotBuildable(reasons)

    facts = facts_mod.load(run)
    sid = facts_mod.value(facts, "system_id")
    name = facts_mod.value(facts, "system_name") or sid
    schedule = sap["schedule"]
    entities = assessment_entities(run, sid, results, stig, rar, poam,
                                   [m["persona"] for m in sap["team"]],
                                   day(schedule["end"], end=True))
    base = baseline_mod.load(run) or {}
    result: dict[str, Any] = {
        "uuid": uuid_for(sid, MODEL, "result"),
        "title": "Control assessment results",
        "description": f"Results of assessing the controls of baseline "
                       f"{base.get('baseline_id')} per the assessment plan.",
        "start": day(schedule["start"]),
        "end": day(schedule["end"], end=True),
        "reviewed-controls": reviewed_controls(run, sap),
    }
    for key, items in (("observations", entities.observations),
                       ("risks", entities.risks), ("findings", entities.findings)):
        if items:
            result[key] = list(items.values())
    body: dict[str, Any] = {"import-ap": {"href": "assessment-plan.json"}, "results": [result]}
    metadata = with_personas(run, sid, doc_metadata(
        run, f"{name} Security Assessment Report (draft)"), body)
    return serialize(AssessmentResults, {"uuid": uuid_for(sid, MODEL, "assessment-results"),
                                         "metadata": metadata, **body})
