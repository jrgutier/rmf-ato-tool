"""OSCAL profile and SSP builders (plan Decision B1, §6.6 ``mapping.yaml``).

Source YAML is mapped to OSCAL JSON, loaded through the compliance-trestle 5.2.0 pydantic
models and serialized by them. UUIDs are uuid5 and the only time stamp is
``run.yaml:as_of``, so a build is byte-identical for the same inputs (GEN-STALE-001).
The SSP is built only once all of its inputs exist; until then the reasons are reported.
"""

from __future__ import annotations

import re
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.oscal.version import OSCAL_VERSION
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import frontmatter
from rmf_tool.run.model import OSCAL_DIR, Run, YamlError
from rmf_tool.run.trace import HEADING, PROSE, strip_generated

RMF_NS = "urn:rmf-tool:oscal"
CATALOG_URL = ("https://raw.githubusercontent.com/usnistgov/oscal-content/v1.6.0/nist.gov/"
               "SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json")
SP800_60 = "https://doi.org/10.6028/NIST.SP.800-60v2r1"
PROFILE_FILE = f"{OSCAL_DIR}/profile.json"
SSP_FILE = f"{OSCAL_DIR}/ssp.json"
COMPONENT_STATES = {"operational", "under-development", "disposition", "other"}
IMPLEMENTATION_STATES = {"implemented", "partial", "planned", "alternative", "not-applicable"}
TOKEN_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")

USERS = "artifacts/data/users.yaml"
BOUNDARY = "artifacts/data/boundary.yaml"
INFOTYPES = "artifacts/data/infotypes.yaml"
INVENTORY = "artifacts/data/inventory.yaml"
LEVERAGED = "artifacts/data/leveraged-authorizations.yaml"
SSP_CONTROLS_DIR = "artifacts/ssp/controls"


class NotBuildable(Exception):
    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def _prop(name: str, value: str, ns: str | None = RMF_NS) -> dict[str, str]:
    return {"name": name, "value": value, **({"ns": ns} if ns else {})}


def _plain(text: str) -> str:
    return " ".join(PROSE.sub(lambda m: "", text).split())


def _serialize(model_cls: Any, body: dict[str, Any]) -> str:
    return model_cls.model_validate(body).oscal_serialize_json(pretty=True) + "\n"


def _system_id(run: Run, facts: dict[str, Any]) -> str:
    return facts_mod.value(facts, "system_id") or run.run_id


def _metadata(run: Run, title: str) -> dict[str, Any]:
    return {"title": title, "last-modified": run.config["as_of"], "version": run.run_id,
            "oscal-version": OSCAL_VERSION}


def build_profile(run: Run) -> str | None:
    """oscal/profile.json from baseline.json, or None when there is no baseline yet."""
    from trestle.oscal.profile import Profile

    data = baseline_mod.load(run)
    if data is None:
        return None
    sid = _system_id(run, facts_mod.load(run))
    body = {
        "uuid": uuid_for(sid, "profile", "profile"),
        "metadata": _metadata(run, f"Tailored control baseline {data.get('baseline_id')}"),
        "imports": [{"href": CATALOG_URL,
                     "include-controls": [{"with-ids": baseline_mod.control_ids(run)}]}],
        "merge": {"as-is": True},
    }
    return _serialize(Profile, body)


def _load(run: Run, rel: str, schema: str, reasons: list[str], required: bool = True) -> Any:
    if not run.path(rel).is_file():
        if required:
            reasons.append(f"{rel} missing")
        return None
    try:
        data = run.data(rel)
    except YamlError as exc:
        reasons.append(f"{rel}: {exc}")
        return None
    if run.schema_errors(schema, data):
        reasons.append(f"{rel} violates {schema}.schema.json (see RUN-FM-001)")
        return None
    return data


def _description(run: Run, fallback: str) -> str:
    path = run.artifact_md("ART-SD")
    if path.is_file():
        body = strip_generated(frontmatter.parse(path.read_text(encoding="utf-8")).body)
        paragraph: list[str] = []
        for line in body.splitlines():
            if HEADING.match(line):
                if paragraph:
                    break
                continue
            if line.strip():
                paragraph.append(line)
            elif paragraph:
                break
        text = _plain(" ".join(paragraph))
        if text:
            return text
    return fallback


def _diagrams(sid: str, key: str, block: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"description": block["description"].strip()}
    diagrams = [{"uuid": uuid_for(sid, "ssp", f"diagram/{key}/{i}"), "caption": d["caption"],
                 "links": [{"href": f"product/{d['path']}", "rel": "diagram"}]}
                for i, d in enumerate(block.get("diagrams") or [], start=1)]
    if diagrams:
        out["diagrams"] = diagrams
    return out


def _impact(level: dict[str, Any]) -> dict[str, Any]:
    out = {"base": f"fips-199-{level['base']}"}
    if level.get("selected"):
        out["selected"] = f"fips-199-{level['selected']}"
    if level.get("adjustment_justification"):
        out["adjustment-justification"] = level["adjustment_justification"]
    return out


def build_ssp(run: Run) -> str:
    """oscal/ssp.json; raises NotBuildable while inputs are missing or invalid."""
    from trestle.oscal.ssp import SystemSecurityPlan

    reasons: list[str] = []
    facts = facts_mod.load(run)
    for fact in ("system_id", "system_name", "lifecycle_state", "categorization"):
        if facts_mod.get(facts, fact) is None:
            reasons.append(f"facts.yaml {fact} not set")
    base = baseline_mod.load(run)
    if base is None:
        reasons.append("baseline.json missing (rmf baseline resolve)")
    boundary = _load(run, BOUNDARY, "boundary", reasons)
    users = _load(run, USERS, "users", reasons)
    infotypes = _load(run, INFOTYPES, "infotypes", reasons)
    inventory = _load(run, INVENTORY, "inventory", reasons, required=False)
    leveraged = _load(run, LEVERAGED, "leveraged-authorizations", reasons, required=False)
    statements: list[dict[str, Any]] = []
    families = sorted(run.path(SSP_CONTROLS_DIR).glob("*.yaml"))
    if not families:
        reasons.append(f"no {SSP_CONTROLS_DIR}/<fam>.yaml yet (S-4)")
    for path in families:
        data = _load(run, run.rel(path), "ssp-controls", reasons)
        statements += data["controls"] if data else []
    if reasons:
        raise NotBuildable(reasons)

    sid = facts_mod.value(facts, "system_id")
    name = facts_mod.value(facts, "system_name")
    cat = facts_mod.get(facts, "categorization")
    lifecycle = facts_mod.value(facts, "lifecycle_state")
    description = _description(run, f"{name}.")

    # metadata: one role and one party per persona named in a statement
    personas = sorted({p for s in statements for p in s["responsible_roles"]})
    humans = run.config.get("humans") or {}
    roles, parties, responsible = [], [], []
    for pid in personas:
        persona = run.personas.get(pid, {})
        party = uuid_for(sid, "ssp", f"party/{pid}")
        human = humans.get(pid)
        roles.append({"id": pid, "title": persona.get("name", pid)})
        parties.append({"uuid": party, "type": "person",
                        "name": human or f"{persona.get('name', pid)} (simulated)",
                        "props": [_prop("simulated", "false" if human else "true")]})
        responsible.append({"role-id": pid, "party-uuids": [party]})

    # components: this-system plus the boundary components
    this_system = next((c for c in boundary["components"] if c["type"] == "this-system"), None)
    comp_uuid = {c["id"]: uuid_for(sid, "ssp", f"component/{c['id']}")
                 for c in boundary["components"]}
    comp_uuid["this-system"] = (comp_uuid[this_system["id"]] if this_system
                                else uuid_for(sid, "ssp", "component/this-system"))
    la_uuid = {la["id"]: uuid_for(sid, "ssp", f"leveraged/{la['id']}")
               for la in (leveraged or {}).get("leveraged_authorizations", [])}

    def component(c: dict[str, Any]) -> dict[str, Any]:
        state = c["status"] if c["status"] in COMPONENT_STATES else "other"
        out: dict[str, Any] = {
            "uuid": comp_uuid[c["id"]], "type": c["type"], "title": c["title"],
            "description": c["description"].strip(),
            "props": [_prop("asset-id", c["id"], None),
                      _prop("implementation-point",
                            "external" if c.get("external") else "internal", None)],
            "status": {"state": state, **({"remarks": c["status"]} if state != c["status"]
                                          else {})},
        }
        if c.get("leveraged_authorization") in la_uuid:
            out["props"].append(_prop("leveraged-authorization-uuid",
                                      la_uuid[c["leveraged_authorization"]], None))
        return out

    components = [component(c) for c in boundary["components"]]
    if this_system is None:
        state = lifecycle if lifecycle in COMPONENT_STATES else "other"
        components.insert(0, {"uuid": comp_uuid["this-system"], "type": "this-system",
                              "title": name, "description": description,
                              "status": {"state": state}})

    for la in (leveraged or {}).get("leveraged_authorizations", []):
        parties.append({"uuid": uuid_for(sid, "ssp", f"party/{la['id']}"),
                        "type": "organization", "name": la["provider"]})

    def user(u: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {
            "uuid": uuid_for(sid, "ssp", f"user/{u['id']}"), "title": u["title"],
            "short-name": u["id"],
            "props": [_prop("type", u["type"], None),
                      _prop("privilege-level", u["privilege_level"], None)],
        }
        role_ids = [r for r in u.get("roles") or [] if TOKEN_ID.match(r)]
        if role_ids:
            out["role-ids"] = role_ids
        if u.get("authorized_privileges"):
            out["authorized-privileges"] = [
                {"title": p["title"], "functions-performed": p["functions_performed"],
                 **({"description": p["description"]} if p.get("description") else {})}
                for p in u["authorized_privileges"]]
        return out

    def inventory_item(i: dict[str, Any]) -> dict[str, Any]:
        props = [_prop("asset-id", i["id"], None), _prop("asset-type", i["kind"], None)]
        for key, prop in (("vendor", "vendor-name"), ("product", "software-name"),
                          ("version", "version"), ("hostname", "fqdn")):
            if i.get(key):
                props.append(_prop(prop, str(i[key]), None))
        for key in ("virtual", "public"):
            if key in i:
                props.append(_prop(key, "yes" if i[key] else "no", None))
        return {"uuid": uuid_for(sid, "ssp", f"inventory/{i['id']}"),
                "description": i["description"].strip(), "props": props,
                "implemented-components": [{"component-uuid": comp_uuid.get(
                    i["component"], uuid_for(sid, "ssp", f"component/{i['component']}"))}]}

    def info_type(t: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {
            "uuid": uuid_for(sid, "ssp", f"infotype/{t['id']}"), "title": t["title"],
            "description": t["description"].strip(),
            "confidentiality-impact": _impact(t["confidentiality"]),
            "integrity-impact": _impact(t["integrity"]),
            "availability-impact": _impact(t["availability"]),
        }
        if t.get("sp800_60_ids"):
            out["categorizations"] = [{"system": SP800_60,
                                       "information-type-ids": t["sp800_60_ids"]}]
        return out

    order = {cid: i for i, cid in enumerate(catalog.load(run.repo).order)}

    def requirement(s: dict[str, Any]) -> dict[str, Any]:
        ctl = s["control_id"]
        state = s["status"] if s["status"] in IMPLEMENTATION_STATES else "implemented"
        remarks = s.get("rationale")
        if s["status"] == "inherited":
            remarks = f"Inherited from {s.get('inherited_from', 'a common control provider')}." \
                      + (f" {remarks}" if remarks else "")
        out: dict[str, Any] = {
            "uuid": uuid_for(sid, "ssp", f"requirement/{ctl}"), "control-id": ctl,
            "props": [_prop("rmf-status", s["status"])]
            + [_prop("trace", src) for src in s["sources"]],
            "responsible-roles": [{"role-id": r} for r in s["responsible_roles"]],
            "by-components": [],
        }
        if s.get("parameters"):
            out["set-parameters"] = [{"param-id": k, "values": [v]}
                                     for k, v in sorted(s["parameters"].items())]
        for comp in s["components"]:
            by: dict[str, Any] = {
                "component-uuid": comp_uuid.get(comp, uuid_for(sid, "ssp", f"component/{comp}")),
                "uuid": uuid_for(sid, "ssp", f"by-component/{ctl}/{comp}"),
                "description": s["statement"].strip(),
                "implementation-status": {"state": state},
            }
            if remarks:
                by["remarks"] = remarks
            out["by-components"].append(by)
        return out

    statements.sort(key=lambda s: (order.get(s["control_id"], len(order)), s["control_id"]))
    hwm = facts_mod.high_water(facts) or "moderate"
    characteristics: dict[str, Any] = {
        "system-ids": [{"id": sid}],
        "system-name": name,
        **({"system-name-short": facts_mod.value(facts, "acronym")}
           if facts_mod.value(facts, "acronym") else {}),
        "description": description,
        "security-sensitivity-level": f"fips-199-{hwm}",
        "system-information": {"information-types": [info_type(t) for t in
                                                     infotypes["information_types"]]},
        "security-impact-level": {
            "security-objective-confidentiality": f"fips-199-{cat['c']}",
            "security-objective-integrity": f"fips-199-{cat['i']}",
            "security-objective-availability": f"fips-199-{cat['a']}",
        },
        "status": {"state": lifecycle},
        "authorization-boundary": _diagrams(sid, "boundary", boundary["authorization_boundary"]),
        "network-architecture": _diagrams(sid, "network", boundary["network_architecture"]),
        "data-flow": _diagrams(sid, "data-flow", boundary["data_flow"]),
    }
    if facts_mod.value(facts, "boundary_id"):
        characteristics["props"] = [_prop("boundary-id", facts_mod.value(facts, "boundary_id"))]
    implementation: dict[str, Any] = {
        "users": [user(u) for u in users["users"]],
        "components": components,
    }
    if leveraged and leveraged.get("leveraged_authorizations"):
        implementation["leveraged-authorizations"] = [
            {"uuid": la_uuid[la["id"]], "title": la["title"],
             "party-uuid": uuid_for(sid, "ssp", f"party/{la['id']}"),
             "date-authorized": la["date_authorized"]}
            for la in leveraged["leveraged_authorizations"]]
    if inventory and inventory.get("items"):
        implementation["inventory-items"] = [inventory_item(i) for i in inventory["items"]]

    metadata = _metadata(run, f"{name} System Security Plan (draft)")
    if roles:
        metadata.update({"roles": roles, "parties": parties, "responsible-parties": responsible})
    elif parties:
        metadata["parties"] = parties
    body = {
        "uuid": uuid_for(sid, "ssp", "ssp"),
        "metadata": metadata,
        "import-profile": {"href": "profile.json"},
        "system-characteristics": characteristics,
        "system-implementation": implementation,
        "control-implementation": {
            "description": f"Planned and implemented controls for baseline "
                           f"{base.get('baseline_id') if base else '?'}.",
            "implemented-requirements": [requirement(s) for s in statements],
        },
    }
    return _serialize(SystemSecurityPlan, body)
