"""OSCAL POA&M builder (ART-POAM; plan §6.6 ``mapping.yaml``).

Each item of ``artifacts/poam/items.yaml`` becomes a poam-item. Its finding_ref links the SAR
finding (FND-###) or the STIG observation (STG-###), and every RAR risk that lists the item
in ``poam_refs`` is a related risk. The linked findings, observations and risks are repeated
in the POA&M with the same uuid5 IDs the assessment results use, so links resolve in both
documents. DoD fields without an OSCAL home (severity, point of contact, milestones,
scheduled completion) are ``urn:rmf-tool:oscal`` props.
"""

from __future__ import annotations

from typing import Any

from rmf_tool.oscal.build_sap import SAP_DATA
from rmf_tool.oscal.build_sar import (
    POAM_DATA,
    RAR_DATA,
    STIG_DATA,
    assessment_entities,
    load_results,
)
from rmf_tool.oscal.common import (
    NotBuildable,
    day,
    doc_metadata,
    load_data,
    prop,
    serialize,
    trace_props,
    with_personas,
)
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import OSCAL_DIR, Run

POAM_FILE = f"{OSCAL_DIR}/poam.json"
MODEL = "poam"
ITEM_PROPS = (("source_of_weakness", "source-of-weakness"), ("severity", "severity"),
              ("residual_risk", "residual-risk"), ("point_of_contact", "point-of-contact"),
              ("resources_required", "resources-required"),
              ("scheduled_completion", "scheduled-completion"))


def build_poam(run: Run) -> str:
    """oscal/poam.json; raises NotBuildable while inputs are missing or invalid."""
    from trestle.oscal.poam import PlanOfActionAndMilestones

    reasons: list[str] = []
    facts = facts_mod.load(run)
    if facts_mod.value(facts, "system_id") is None:
        reasons.append("facts.yaml system_id not set")
    poam = load_data(run, POAM_DATA, "poam-items", reasons)
    if poam is not None and not poam["items"]:  # OSCAL requires at least one poam-item
        reasons.append(f"{POAM_DATA} has no items")
    sap = load_data(run, SAP_DATA, "sap", reasons, required=False)
    results = load_results(run, reasons, required=False)
    stig = load_data(run, STIG_DATA, "stig-summary", reasons, required=False)
    rar = load_data(run, RAR_DATA, "rar", reasons, required=False)
    if reasons:
        raise NotBuildable(reasons)

    sid = facts_mod.value(facts, "system_id")
    name = facts_mod.value(facts, "system_name") or sid
    collected = day(sap["schedule"]["end"], end=True) if sap else run.config["as_of"]
    entities = assessment_entities(run, sid, results, stig, rar, poam,
                                   [m["persona"] for m in (sap or {}).get("team") or []],
                                   collected)
    controls = {f["id"]: f["control_id"] for family in results for f in family["findings"]}
    risks = (rar or {}).get("risks") or []
    used: dict[str, set[str]] = {"observations": set(), "findings": set(), "risks": set()}

    def item(i: dict[str, Any]) -> dict[str, Any]:
        ref = i["finding_ref"]
        props = [prop("poam-id", i["id"]), prop("finding-ref", ref),
                 prop("control-id", i["control_id"]), prop("status", i["status"])]
        props += [prop(name, str(i[key])) for key, name in ITEM_PROPS if i.get(key)]
        props += [prop("milestone", f"{m['due']}: {m['description']}")
                  for m in i.get("milestones") or []]
        out: dict[str, Any] = {
            "uuid": uuid_for(sid, MODEL, f"item/{i['id']}"), "title": i["weakness"].strip(),
            "description": (i.get("description") or i["weakness"]).strip(),
            "props": props + trace_props(i.get("sources")),
        }
        if ref in entities.findings:
            used["findings"].add(ref)
            out["related-findings"] = [{"finding-uuid": entities.findings[ref]["uuid"]}]
        evidence = [k for k in (controls.get(ref), ref) if k in entities.observations]
        if evidence:
            used["observations"].update(evidence)
            out["related-observations"] = [
                {"observation-uuid": entities.observations[k]["uuid"]} for k in evidence]
        linked = [r["id"] for r in risks if i["id"] in r["poam_refs"]]
        if linked:
            used["risks"].update(linked)
            out["related-risks"] = [{"risk-uuid": entities.risks[r]["uuid"]} for r in linked]
        if i.get("comments"):
            out["remarks"] = i["comments"].strip()
        return out

    body: dict[str, Any] = {
        "import-ssp": {"href": "ssp.json"},
        "system-id": {"id": sid},
        "poam-items": [item(i) for i in poam["items"]],
    }
    # objects a linked finding or risk points at are repeated too, so every link resolves
    for f in used["findings"]:
        used["risks"].update(r["id"] for r in risks if f in r["finding_refs"])
        if controls[f] in entities.observations:
            used["observations"].add(controls[f])
    for r in risks:
        if r["id"] in used["risks"]:
            used["observations"].update(k for ref in r["finding_refs"]
                                        for k in (controls.get(ref), ref)
                                        if k in entities.observations)
    for key in ("observations", "risks", "findings"):
        objects = getattr(entities, key)
        kept = [obj for k, obj in objects.items() if k in used[key]]
        if kept:
            body[key] = kept
    metadata = with_personas(run, sid, doc_metadata(
        run, f"{name} Plan of Action and Milestones (draft)"), body,
        extra={i["point_of_contact"] for i in poam["items"] if i.get("point_of_contact")})
    return serialize(PlanOfActionAndMilestones, {"uuid": uuid_for(sid, MODEL, "poam"),
                                                 "metadata": metadata, **body})
