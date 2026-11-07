"""AONLY-001: the Assess Only process. Technologies below the system level (PIT, IT services
and IT products) "do not require an ATO" but "must still complete specific RMF assessment
procedures under the 'Assess Only' process" (DoDI 8510.01 p. 13), and are "security configured
and reviewed by the cognizant ISSM (under the direction of the AO) for acceptance and connection
into an authorized computing environment (i.e., an IS enclave with an ATO)" (DoDI 8500.01 p. 41,
the ISSM's side p. 49). The AODR may give the direction for the AO; only the decision itself is
non-delegable."""

from __future__ import annotations

from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import authorization as ledger
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope

BELOW_SYSTEM = ("pit", "it-service", "it-product")
ARTIFACT = "ART-AUTHREC"
ASSESSMENT_TASK = "A-3"
ISSM = "PER-ISSM"
DIRECTORS = ("PER-AO", "PER-AODR")
AUTHORIZED = ("AD-ATO", "AD-ATOC", "AD-CATO")


def _below_system(ctx: Context) -> str | None:
    node = facts_mod.get(ctx.facts, "system_type")
    value = node.get("value") if isinstance(node, dict) else None
    return value if value in BELOW_SYSTEM else None


def assess_only(ctx: Context) -> list[RunFinding]:
    kind = _below_system(ctx)
    if kind is None:
        return []
    out: list[RunFinding] = []

    def err(message: str, task: str = "R-4") -> None:
        out.append(make("AONLY-001", message, ledger.LEDGER_FILE, None, {task}))

    if ASSESSMENT_TASK not in scope.active_tasks(ctx.run):
        err(f"the {kind} is below the system level and completes the Assess Only assessment "
            f"procedures, and {ASSESSMENT_TASK} is out of the run's scope", "A-3")
    if not scope.produced_or_seeded(ctx.run, ARTIFACT):
        return out
    book = ctx.data(ledger.LEDGER_FILE)
    records = book.get("acceptances") if isinstance(book, dict) else None
    acceptances = [a for a in records if isinstance(a, dict)] if isinstance(records, list) else []
    if not acceptances:
        err(f"the {kind} is below the system level and is accepted into an authorized computing "
            "environment through the ISSM's review; authorizations.yaml records no acceptance")
    for a in acceptances:
        aid = a.get("id")
        env: Any = a.get("environment") if isinstance(a.get("environment"), dict) else {}
        auth: Any = env.get("authorization") if isinstance(env.get("authorization"), dict) else {}
        if a.get("reviewed_by") != ISSM:
            err(f"{aid}: the security configuration is reviewed by {a.get('reviewed_by')}, not "
                "the cognizant ISSM")
        if a.get("directed_by") not in DIRECTORS:
            err(f"{aid}: the ISSM reviews under the direction of the AO, not "
                f"{a.get('directed_by')}")
        if a.get("secure_configuration") != "approved":
            err(f"{aid}: the {kind} is accepted, and its security configuration is "
                f"{a.get('secure_configuration')}, not approved")
        if auth.get("decision") not in AUTHORIZED:
            err(f"{aid}: {env.get('name')} is no authorized computing environment: its "
                f"authorization is {auth.get('decision')}, not an ATO")
    return out
