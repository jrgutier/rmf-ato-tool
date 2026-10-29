"""Helpers shared by the OSCAL builders (plan Decision B1, §6.6 ``mapping.yaml``).

Every builder maps run YAML to OSCAL JSON, loads it through the compliance-trestle 5.2.0
pydantic models and serializes it with them. UUIDs are uuid5 and the only time stamps come
from run data (``run.yaml:as_of``, SAP dates), so a rebuild is byte-identical (GEN-STALE-001).
"""

from __future__ import annotations

from typing import Any

from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.oscal.version import OSCAL_VERSION
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import Run, YamlError

RMF_NS = "urn:rmf-tool:oscal"


class NotBuildable(Exception):
    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def prop(name: str, value: str, ns: str | None = RMF_NS) -> dict[str, str]:
    return {"name": name, "value": value, **({"ns": ns} if ns else {})}


def trace_props(sources: list[str] | None) -> list[dict[str, str]]:
    return [prop("trace", src) for src in sources or []]


def serialize(model_cls: Any, body: dict[str, Any]) -> str:
    """The trestle-serialized document; a body trestle rejects (schema-valid run data that
    maps to an empty required OSCAL list, say) is NotBuildable rather than a crash."""
    from pydantic import ValidationError

    try:
        model = model_cls.model_validate(body)
    except ValidationError as exc:
        where, why = (str(exc).splitlines() + ["", ""])[1:3]
        raise NotBuildable([f"trestle rejects the {model_cls.__name__}: {where.strip()}: "
                            f"{why.strip()}"]) from exc
    return model.oscal_serialize_json(pretty=True) + "\n"


def system_id(run: Run, facts: dict[str, Any]) -> str:
    return facts_mod.value(facts, "system_id") or run.run_id


def doc_metadata(run: Run, title: str) -> dict[str, Any]:
    return {"title": title, "last-modified": run.config["as_of"], "version": run.run_id,
            "oscal-version": OSCAL_VERSION}


def day(date: Any, end: bool = False) -> str:
    """An RFC 3339 date-time for a run-data date: its first second, or its last with ``end``."""
    return f"{date}T23:59:59Z" if end else f"{date}T00:00:00Z"


def load_data(run: Run, rel: str, schema: str, reasons: list[str], required: bool = True) -> Any:
    """A run-data file validated against its schema; None (and a reason) when unusable."""
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


def party_uuid(sid: str, persona: str) -> str:
    """Parties are defined by the SSP; every document reuses its persona party UUIDs."""
    return uuid_for(sid, "ssp", f"party/{persona}")


def persona_parties(run: Run, sid: str, personas: Any) -> tuple[list, list, list]:
    """(roles, parties, responsible-parties): one role and one party per persona; a party is
    the named human from ``run.yaml:humans`` or the simulated persona (prop ``simulated``)."""
    humans = run.config.get("humans") or {}
    roles, parties, responsible = [], [], []
    for pid in sorted(set(personas)):
        persona = run.personas.get(pid, {})
        human = humans.get(pid)
        roles.append({"id": pid, "title": persona.get("name", pid)})
        parties.append({"uuid": party_uuid(sid, pid), "type": "person",
                        "name": human or f"{persona.get('name', pid)} (simulated)",
                        "props": [prop("simulated", "false" if human else "true")]})
        responsible.append({"role-id": pid, "party-uuids": [party_uuid(sid, pid)]})
    return roles, parties, responsible


def role_ids(node: Any) -> set[str]:
    """Every ``role-id`` value in a document tree (responsible roles, origin actors)."""
    if isinstance(node, dict):
        found = {node["role-id"]} if isinstance(node.get("role-id"), str) else set()
        return found.union(*(role_ids(v) for v in node.values()))
    if isinstance(node, list):
        return set().union(*(role_ids(v) for v in node))
    return set()


def with_personas(run: Run, sid: str, metadata: dict[str, Any], body: Any,
                  extra: set[str] | frozenset[str] = frozenset()) -> dict[str, Any]:
    """``metadata`` plus the roles and parties of every persona the document body names as a
    ``role-id``, and of the ``extra`` personas."""
    roles, parties, responsible = persona_parties(run, sid, role_ids(body) | extra)
    if roles:
        metadata.update({"roles": roles, "parties": parties, "responsible-parties": responsible})
    return metadata
