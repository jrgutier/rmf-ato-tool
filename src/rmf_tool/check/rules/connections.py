"""External connection rules of P-16: CONN-001 to CONN-004. They read the ``connections`` and
``dodin`` of boundary.yaml once P-16 is in the run's scope, and stay quiet about a file that is
missing or unreadable (RUN-ART-001 and RUN-FM-001 report those).

Who approves what follows the sources, not practice: DISA maintains the DISN connection
approval process (REQ-DODI8500.01-0083, -0342); the DoD ISRMC, supported by the DSAWG,
authorizes cross security domain and mission partner connections (REQ-DODI8510.01-0159,
-0166); the DoD CIO approves mission partner interconnections and their validated requirements
(REQ-DODI8530.01-0048, -0301), which follow the DISA Connection Process Guide
(REQ-DODI8530.01-0289)."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope

BOUNDARY_FILE = "artifacts/data/boundary.yaml"
TASK = "P-16"
# Component types through which the system exchanges information with something outside it.
CONNECTION_TYPES = ("interconnection", "system", "service")
RISK_EXECUTIVE = frozenset({"ISRMC", "DSAWG"})
INTERCONNECTION_POINTS = ("dmz", "point-to-point")
CD_PROVIDERS = ("disa-enterprise", "other")
PARTNER_PACKAGE = ("sponsor", "partner-assisted")
HOLDING = ("requested", "approved")  # a planned or disapproved approval holds nothing
LATEST = "9999-12-31"  # a missing review date sorts after any waiver


def _boundary(ctx: Context) -> dict[str, Any] | None:
    if TASK not in scope.active_tasks(ctx.run):
        return None
    data = ctx.data(BOUNDARY_FILE)
    return data if isinstance(data, dict) else None


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _key(value: Any) -> str | None:
    """A value usable as a set member or lookup key; malformed input reads as missing."""
    return value if isinstance(value, str) else None


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [r for r in _list(data.get(key)) if isinstance(r, dict)]


def _authorities(conn: dict[str, Any]) -> set[str | None]:
    """The bodies whose approval of the connection is requested or granted."""
    return {_key(a.get("authority")) for a in _records(conn, "approvals")
            if a.get("status") in HOLDING}


def _finding(rule: str, message: str) -> RunFinding:
    return make(rule, message, BOUNDARY_FILE, None, {TASK})


def approvals(ctx: Context) -> list[RunFinding]:
    """CONN-001: every external connection is recorded with its detail, and carries the
    approvals its network and domain need."""
    data = _boundary(ctx)
    if data is None:
        return []
    out = []
    recorded = {_key(c.get("component")) for c in _records(data, "connections")}
    for comp in _records(data, "components"):
        if comp.get("external") is True and comp.get("type") in CONNECTION_TYPES \
                and _key(comp.get("id")) not in recorded:
            out.append(_finding("CONN-001", f"external connection {comp.get('id')} has no "
                                "connection record with its ports, protocols, data and "
                                "direction"))
    for conn in _records(data, "connections"):
        ident, network, held = conn.get("id"), conn.get("network"), _authorities(conn)
        for approval in _records(conn, "approvals"):
            if approval.get("status") not in HOLDING:
                out.append(_finding("CONN-001", f"{ident}: the {approval.get('authority')} "
                                    f"approval is {approval.get('status')}, so it does not "
                                    "count as requested or granted"))
        if network == "disn" and "DISA" not in held:
            out.append(_finding("CONN-001", f"{ident} connects to the DISN without going "
                                "through the DISA connection approval process"))
        if network == "mission-partner" and "DISA" not in held:
            out.append(_finding("CONN-001", f"{ident}: the mission partner interconnection "
                                "does not follow the DISN connection process"))
        if network == "mission-partner" and "DOD-CIO" not in held:
            out.append(_finding("CONN-001", f"{ident}: the mission partner interconnection "
                                "request has no DoD CIO approval"))
        if (conn.get("cross_domain") is True or network == "mission-partner") \
                and not held & RISK_EXECUTIVE:
            out.append(_finding("CONN-001", f"{ident}: a cross security domain or mission "
                                "partner connection needs authorization by the DoD ISRMC or "
                                "the DSAWG in its support"))
    return out


def cross_domain(ctx: Context) -> list[RunFinding]:
    """CONN-002: a cross-domain connection names its solution, prefers the DISA-provided
    enterprise CD service, and that service is outside the boundary."""
    data = _boundary(ctx)
    if data is None:
        return []
    components = {_key(c.get("id")): c for c in _records(data, "components")}
    out = []
    for conn in _records(data, "connections"):
        if conn.get("cross_domain") is not True:
            continue
        ident = conn.get("id")
        cds = conn.get("cross_domain_solution")
        cds = cds if isinstance(cds, dict) else {}
        provider = cds.get("provider")
        if provider not in CD_PROVIDERS:
            out.append(_finding("CONN-002", f"{ident} crosses security domains but names no "
                                "cross-domain solution"))
        elif provider == "other" and "disa-enterprise" not in _list(cds.get("considered")):
            out.append(_finding("CONN-002", f"{ident} uses a cross-domain solution other than "
                                "the DISA-provided CD service without having considered it"))
        service = components.get(_key(cds.get("component")))
        if provider == "disa-enterprise" and (service or {}).get("external") is not True:
            out.append(_finding("CONN-002", f"{ident}: the DISA-provided enterprise CD service "
                                "is not an external boundary component"))
    return out


def mission_partner(ctx: Context) -> list[RunFinding]:
    """CONN-003: a mission partner interconnection uses an authorized interconnection point,
    rests on a requirement both its sponsor and the DoD CIO approved, and its partner's
    authorization package is the sponsor's work or done with the sponsor's help."""
    data = _boundary(ctx)
    if data is None:
        return []
    out = []
    for conn in _records(data, "connections"):
        if conn.get("network") != "mission-partner":
            continue
        ident = conn.get("id")
        partner = conn.get("mission_partner")
        partner = partner if isinstance(partner, dict) else {}
        if partner.get("interconnection") not in INTERCONNECTION_POINTS:
            out.append(_finding("CONN-003", f"{ident}: a mission partner interconnection uses "
                                "neither a mission partner DMZ nor a point-to-point "
                                "interconnection"))
        approvers = {_key(a) for a in _list(partner.get("requirement_approved_by"))}
        if not {"sponsor", "DOD-CIO"} <= approvers:
            out.append(_finding("CONN-003", f"{ident}: the validated requirement is not "
                                "approved by both the sponsoring DoD Component and the DoD CIO"))
        if partner.get("partner_package") not in PARTNER_PACKAGE:
            out.append(_finding("CONN-003", f"{ident}: the sponsor neither completed nor "
                                "assisted the mission partner's authorization package"))
    return out


def dodin(ctx: Context) -> list[RunFinding]:
    """CONN-004: the boundary says whether the system is on the DODIN; one outside it holds a
    waiver granted after the DoD CIO reviewed its cybersecurity posture."""
    data = _boundary(ctx)
    if data is None:
        return []
    position = data.get("dodin")
    if not isinstance(position, dict):
        return [_finding("CONN-004", "boundary.yaml does not say whether the system operates "
                         "on the DODIN or outside it")]
    if position.get("position") != "outside":
        return []
    waiver = position.get("waiver")
    waiver = waiver if isinstance(waiver, dict) else {}
    out = []
    if waiver.get("reviewed_by") != "DOD-CIO":
        out.append(_finding("CONN-004", "the DODIN waiver names no DoD CIO as having reviewed "
                            "the system's cybersecurity posture"))
    reviewed, granted = str(waiver.get("reviewed") or LATEST), str(waiver.get("granted") or "")
    if reviewed > granted:
        out.append(_finding("CONN-004", f"the cybersecurity posture was reviewed on {reviewed}, "
                            "which does not precede the DODIN waiver granted "
                            f"{granted or 'on no date'}"))
    return out
