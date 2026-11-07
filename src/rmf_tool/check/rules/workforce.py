"""Workforce qualification and primary roles, WFQ-001 and WFQ-002.

WFQ-001 (P-1): each RMF appointee in ART-ORG-CONTEXT is trained, with the training verified
by someone other than the appointee (DoDI 8510.01 2.7.s, CNSSP 12), and an appointee in a
cyberspace work role is identified by its DCWF code and meets the qualification standard of the
DoD cyberspace workforce policy (DoDD 8140.01 1.2.c). That policy, DoDM 8140.03, sets the period
in which a newly assigned person qualifies and is not in the library, so a pending
qualification is judged only on naming the date it is due.

WFQ-002: the ISSO, a primary role of P-14, P-17 and S-3 in DoDI 8510.01 Tables 1 and 3 (the
RACI's R), takes part, shown by an interview, at each such task in scope that has written its
outputs.
"""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.org_context import CYBER_POSITIONS, _record, _roles, _sub
from rmf_tool.check.rules.privacy import _dict, _list, _strings, _written
from rmf_tool.run import scope

# Roles that are cyberspace work roles whatever the record says; any other appointee is one
# when its position names a DCWF code. Developers are the acquisition personnel with IT
# development responsibilities of DoDI 8500.01 2.4.j.
WORK_ROLES = (*CYBER_POSITIONS, "PER-DEV")
ISSO = "PER-ISSO"


def _work_role(record: dict[str, Any]) -> bool:
    return record.get("role") in WORK_ROLES or bool(_sub(record, "position").get("dcwf_code"))


def qualification(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "WFQ-001", "P-1")
    if data is None:
        return out
    personas = ctx.run.framework.ids("personas")
    for r in _roles(data):
        rid, role = r.get("id"), r.get("role")
        q = r.get("qualification")
        if not isinstance(q, dict):
            err(f"{rid}: {role} has no qualification record; personnel engaged in the RMF are "
                "trained, and those in a cyberspace work role qualified")
            continue
        if not any(isinstance(t, dict) for t in _list(q.get("training"))):
            err(f"{rid}: {role} completed no training the qualification record lists")
        verifier = q.get("verified_by")
        if not isinstance(verifier, str) or verifier == role:
            err(f"{rid}: the training and qualification of {role} are not verified by another "
                "official")
        elif verifier.startswith("PER-") and verifier not in personas:
            err(f"{rid}: the training and qualification of {role} are verified by {verifier}, "
                "which is no official of the framework")
        if not _work_role(r):
            continue
        if not _sub(r, "position").get("dcwf_code"):
            err(f"{rid}: {role} performs a cyberspace work role its position does not identify "
                "by a DCWF code")
        status = q.get("status")
        if status == "not-met":
            err(f"{rid}: {role} performs a cyberspace work role and does not meet the "
                "qualification standard of the DoD cyberspace workforce policy")
        elif status == "pending" and not q.get("due"):
            err(f"{rid}: {role} is pending qualification with no date by which the DoD "
                "cyberspace workforce policy requires it")
        elif status not in ("met", "pending"):
            err(f"{rid}: {role} performs a cyberspace work role and records no qualification "
                "status against the DoD cyberspace workforce policy")
    return out


def isso_primary(ctx: Context) -> list[RunFinding]:
    out = []
    active = set(scope.active_tasks(ctx.run))
    heard: dict[str, set[str]] = {}
    for i in ctx.interviews:
        heard.setdefault(i.task, set()).update(_strings([(i.front or {}).get("persona")]))
    for task, data in ctx.run.tasks.items():
        if ISSO not in _list(_dict(data.get("raci")).get("R")):
            continue
        if task in active and _written(ctx, task) and ISSO not in heard.get(task, set()):
            out.append(make("WFQ-002", f"{ISSO} is a primary role at {task}, and the ISSO gave no "
                            f"{task} interview", None, None, {task}))
    return out
