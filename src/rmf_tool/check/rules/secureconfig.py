"""Secure configuration exceptions: SCFG-001. DoDI 8500.01 Encl 3 7.u: DoD IT complies with the
applicable STIGs, security configuration guides and SRGs, with any exception documented and
approved by the responsible AO. The AODR may approve on the AO's behalf; only the
authorization decision itself is non-delegable (DoDI 8510.01).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope

STIG_FILE = "artifacts/data/stig-summary.yaml"
APPROVERS = ("PER-AO", "PER-AODR")
EXCEPTION = "exception"


def exceptions(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-STIG"):
        return []
    data = ctx.data(STIG_FILE)
    findings = data.get("findings") if isinstance(data, dict) else None
    out: list[RunFinding] = []
    owner = {ctx.run.artifacts["ART-STIG"].get("producer")}
    for f in (f for f in findings or () if isinstance(f, dict)):
        if f.get("status") != EXCEPTION:
            continue
        record: Any = f.get("exception")
        approver = record.get("approved_by") if isinstance(record, dict) else None
        if approver not in APPROVERS:
            out.append(make("SCFG-001", f"{f.get('id')}: an exception to the configuration "
                            f"guidance is approved by the responsible AO, not {approver}",
                            STIG_FILE, None, owner))
    return out


def rules() -> Iterator[tuple[str, Callable[[Context], list[RunFinding]]]]:
    yield from (("SCFG-001", exceptions),)
