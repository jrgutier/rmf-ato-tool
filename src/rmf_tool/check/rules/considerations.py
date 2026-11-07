"""Privacy Implementation Considerations, PIC-001 (Task S-2).

CNSSI 1253 Appendix D marks controls outside the NSS privacy control baseline that may
introduce privacy risk if selected to meet a security objective; the Classified System Overlay's
Table 1 has the same column. A selected control so marked is implemented only after the system
owner confers with the SAOP or designee (CNSSI 1253 2.3.1 and page 22), which S-2 records in
tailoring.yaml privacy_implementation. Each checkmark carries subscripted implications to
consider; the coordination addresses each one.
"""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.overlays import SAOP
from rmf_tool.check.rules.tailoring import TAILORING, _active, _categorization, _tailoring


def _records(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["control_id"]: r for r in data.get("privacy_implementation") or []
            if isinstance(r, dict) and isinstance(r.get("control_id"), str)}


def coordinated(ctx: Context) -> list[RunFinding]:
    """A selected control with a Privacy Implementation Considerations checkmark has, before
    it is implemented, a privacy_implementation record of the coordination with the SAOP or a
    designee of the SAOP that addresses each implication its checkmark carries."""
    data = _tailoring(ctx)
    if data is None or not _active(ctx, "S-2"):
        return []
    overlays = _categorization(ctx).get("overlays")
    marked = baseline_mod.privacy_considerations(
        ctx.run.repo,
        [o for o in overlays if isinstance(o, str)] if isinstance(overlays, list) else [])
    records = _records(data)
    out: list[RunFinding] = []
    for cid in baseline_mod.control_ids(ctx.run):
        marks = marked.get(cid)
        if not marks:
            continue
        record = records.get(cid)
        if record is None:
            out.append(make("PIC-001", f"{cid} is selected with a Privacy Implementation "
                            "Considerations checkmark, and no privacy_implementation record "
                            "shows the coordination with the SAOP or designee before it is "
                            "implemented", TAILORING, None, {"S-2"}))
            continue
        if SAOP not in (record.get("by"), record.get("designee_of")):
            out.append(make("PIC-001", f"{cid}: the privacy implementation coordination is with "
                            f"{record.get('by')}, not the SAOP or designee ({SAOP})", TAILORING,
                            None, {"S-2"}))
        given = record.get("implications")
        addressed = {n for n in given if isinstance(n, int)} if isinstance(given, list) else set()
        for n in sorted(set(marks) - addressed):
            out.append(make("PIC-001", f"{cid}: the coordination does not address implication "
                            f"{n} of its checkmark ({marks[n]})", TAILORING, None, {"S-2"}))
    return out
