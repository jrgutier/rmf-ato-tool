"""PVAL-001: the CNSSI 1253 Parameter Value column, the minimum values specified for NSS
(``framework/baselines/cnssi-1253-parameters.yaml``), reaches the run. A baseline control the
column gives a value for records a value for each parameter it assigns, in its SSP control
statement or by a tailoring parameter action, and a value organizational policy sets "meets or
exceeds the NSS-defined parameter value" (CNSSI 1253 page 24): where both are amounts of one
kind, it is no looser."""

from __future__ import annotations

from typing import Any

from rmf_tool import cnssi1253_params
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.check.rules.overlays import NO_OWN_VALUES, _mapping, _tailored_values
from rmf_tool.check.rules.tailoring import _tailoring

COMPARED = ("max", "min")


def nss_values(ctx: Context) -> list[RunFinding]:
    table = cnssi1253_params.load(ctx.run.repo)
    tailored = _tailored_values(_tailoring(ctx) or {})
    out: list[RunFinding] = []
    # A control's values are judged over all its statements; a duplicate is SSP-DUP-001's.
    statements: dict[str, tuple[str, dict[str, Any]]] = {}
    for rel, item in family_records(ctx, SSP_DIR, "controls"):
        cid = item.get("control_id")
        if not isinstance(cid, str) or cid not in table or item.get("status") in NO_OWN_VALUES:
            continue
        first, values = statements.get(cid, (rel, dict(tailored.get(cid, {}))))
        statements[cid] = (first, {**values, **_mapping(item.get("parameters"))})
    for cid, (rel, recorded) in statements.items():

        def err(message: str, rel: str = rel) -> None:
            out.append(make("PVAL-001", message, rel, None, {"S-4"}))

        for nss in table[cid]:
            unset = [p for p in nss["params"] if not recorded.get(p)]
            if unset:
                err(f"{cid} records no value for {', '.join(unset)}; CNSSI 1253 sets the NSS "
                    f"value {nss['value']!r}")
            if nss["bound"] not in COMPARED:
                continue
            for pid in nss["params"]:
                value = recorded.get(pid)
                if not isinstance(value, str) or not value:
                    continue
                verdict = cnssi1253_params.looser(value, nss)
                if verdict is True:
                    err(f"{cid} {pid}: {value!r} is looser than the NSS minimum "
                        f"{nss['value']!r} (CNSSI 1253 Parameter Value)")
                elif verdict is None:
                    err(f"{cid} {pid}: {value!r} states no amount to compare with the NSS "
                        f"minimum {nss['value']!r}")
    return out
