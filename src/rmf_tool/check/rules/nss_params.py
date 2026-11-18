"""PVAL-001: the CNSSI 1253 Parameter Value column, the minimum values specified for NSS
(``framework/baselines/cnssi-1253-parameters.yaml``), reaches the run. A baseline control the
column gives a value for records a value for each parameter it assigns, in its SSP control
statement or by a tailoring parameter action, and a value organizational policy sets "meets or
exceeds the NSS-defined parameter value" (CNSSI 1253 page 24): where both are amounts of one
kind, it is no looser."""

from __future__ import annotations

import re
from typing import Any

from rmf_tool import cnssi1253_params
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SSP_DIR, family_records
from rmf_tool.check.rules.overlays import NO_OWN_VALUES, _mapping, _tailored_values
from rmf_tool.check.rules.tailoring import _tailoring

COMPARED = ("max", "min")


def _findings(ctx: Context) -> list[RunFinding]:
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
                # a short scoping value no amount orders ("all information"): a recorded
                # value that leaves out its words is a warning for a person to judge that it
                # meets or exceeds it (F-08-6); longer guidance prose is not compared
                words = _words(nss["value"])
                for pid in nss["params"] if 0 < len(words) <= SHORT else ():
                    value = recorded.get(pid)
                    if isinstance(value, str) and value and not words <= _words(value):
                        out.append(make("PVAL-002", f"{cid} {pid}: {value!r} differs from the "
                                        f"NSS value {nss['value']!r}; record why it meets or "
                                        "exceeds it", rel, None, {"S-4"}))
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
                    # A stricter value may be one no parser reads ("on every change"), so an
                    # unreadable value is a warning to state the amount, never an error.
                    out.append(make("PVAL-002", f"{cid} {pid}: {value!r} states no amount to "
                                    f"compare with the NSS minimum {nss['value']!r}", rel, None,
                                    {"S-4"}))
    return out


SHORT = 5  # words: a scoping value, not guidance prose
_STOP = {"and", "or", "the", "a", "an", "of"}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP}


def nss_values(ctx: Context) -> list[RunFinding]:
    return [f for f in _findings(ctx) if f.rule == "PVAL-001"]


def unstated_amounts(ctx: Context) -> list[RunFinding]:
    return [f for f in _findings(ctx) if f.rule == "PVAL-002"]
