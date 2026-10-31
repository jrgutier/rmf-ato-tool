"""Cross-artifact consistency rules: INV-BND-001/002, STIG-001/002, POAM-CTL-001,
POAM-FLD-001, RAR-001, AODM-001 and TASK-DEF-001. Each reads the run-data files it links
and stays quiet about a file that is missing or unreadable (RUN-ART-001 and RUN-FM-001
report those)."""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import POAM_FILE, SAR_DIR, family_records
from rmf_tool.run import scope
from rmf_tool.run.model import RUN_FILE

INVENTORY_FILE = "artifacts/data/inventory.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
RAR_FILE = "artifacts/data/rar.yaml"
DECISION_FILE = "artifacts/data/decision.yaml"
# Inventory kinds that a STIG or SRG covers (STIG-001); hardware is covered through its OS.
STIG_KINDS = ("software", "operating-system", "database", "firmware", "virtual-machine")
# Boundary components that carry no inventory items of their own (INV-BND-002).
NO_INVENTORY_TYPES = ("this-system", "interconnection")
POAM_REQUIRED = ("severity", "point_of_contact", "resources_required", "scheduled_completion",
                 "milestones")


def _items(ctx: Context, rel: str, key: str) -> list[dict[str, Any]] | None:
    data = ctx.data(rel)
    if not isinstance(data, dict):
        return None
    return [i for i in data.get(key) or [] if isinstance(i, dict)]


# --- inventory / boundary ---------------------------------------------------------------

def inventory_in_boundary(ctx: Context) -> list[RunFinding]:
    inventory = _items(ctx, INVENTORY_FILE, "items")
    components = _items(ctx, BOUNDARY_FILE, "components")
    if inventory is None or components is None:
        return []
    known = {c.get("id") for c in components}
    return [make("INV-BND-001", f"{i.get('id')} names component {i.get('component')}, which "
                 "is not a boundary component", INVENTORY_FILE)
            for i in inventory if i.get("component") not in known]


def boundary_in_inventory(ctx: Context) -> list[RunFinding]:
    inventory = _items(ctx, INVENTORY_FILE, "items")
    components = _items(ctx, BOUNDARY_FILE, "components")
    if inventory is None or components is None:
        return []
    used = {i.get("component") for i in inventory}
    return [make("INV-BND-002", f"boundary component {c.get('id')} has no inventory item",
                 BOUNDARY_FILE)
            for c in components
            if c.get("type") not in NO_INVENTORY_TYPES and not c.get("external")
            and c.get("id") not in used]


# --- STIG -------------------------------------------------------------------------------

def stig_mapped(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-STIG"):
        return []
    inventory = _items(ctx, INVENTORY_FILE, "items")
    stig = ctx.data(STIG_FILE)
    if inventory is None or not isinstance(stig, dict):
        return []
    known = {i.get("id") for i in inventory}
    mapped: set[str] = set()
    referenced: list[tuple[str, str]] = []
    for b in stig.get("benchmarks") or []:
        for inv in b.get("applies_to") or [] if isinstance(b, dict) else []:
            mapped.add(inv)
            referenced.append((inv, f"benchmark {b.get('id')}"))
    for n in stig.get("not_applicable") or []:
        if isinstance(n, dict):
            mapped.add(n.get("inventory_item"))
            referenced.append((n.get("inventory_item"), "not_applicable"))
    for f in stig.get("findings") or []:
        if isinstance(f, dict):
            referenced.append((f.get("inventory_item"), f"finding {f.get('id')}"))
    out = [make("STIG-001", f"{where} names {inv}, which is not in the inventory", STIG_FILE)
           for inv, where in referenced if inv not in known]
    out += [make("STIG-001", f"{i.get('id')} ({i.get('kind')}) has no STIG/SRG benchmark and "
                 "no not_applicable rationale", STIG_FILE)
            for i in inventory if i.get("kind") in STIG_KINDS and i.get("id") not in mapped]
    return out


def _poam_items(ctx: Context) -> list[dict[str, Any]] | None:
    if not scope.produced_or_seeded(ctx.run, "ART-POAM"):
        return None
    return _items(ctx, POAM_FILE, "items")


def stig_cat1_poam(ctx: Context) -> list[RunFinding]:
    items = _poam_items(ctx)
    findings = _items(ctx, STIG_FILE, "findings")
    if items is None or findings is None:
        return []
    linked = {i.get("finding_ref") for i in items}
    return [make("STIG-002", f"open CAT I STIG finding {f.get('id')} ({f.get('rule_id')}) has "
                 "no POA&M item", POAM_FILE)
            for f in findings
            if f.get("category") == "CAT I" and f.get("status") == "open"
            and f.get("id") not in linked]


# --- POA&M ------------------------------------------------------------------------------

def poam_controls(ctx: Context) -> list[RunFinding]:
    items = _poam_items(ctx)
    if items is None:
        return []
    known = catalog.load(ctx.run.repo).controls
    baseline = set(baseline_mod.control_ids(ctx.run))
    out = []
    for i in items:
        cid = i.get("control_id")
        if cid not in known:
            out.append(make("POAM-CTL-001", f"{i.get('id')}: {cid} is not an SP 800-53r5 "
                            "control", POAM_FILE))
        elif cid not in baseline:
            out.append(make("POAM-CTL-001", f"{i.get('id')}: {cid} is not in the baseline",
                            POAM_FILE))
    return out


def poam_fields(ctx: Context) -> list[RunFinding]:
    items = _poam_items(ctx)
    if items is None:
        return []
    out = []
    for i in items:
        missing = [k for k in POAM_REQUIRED if not i.get(k)]
        if missing:
            out.append(make("POAM-FLD-001", f"{i.get('id')} lacks {', '.join(missing)}",
                            POAM_FILE))
        poc = i.get("point_of_contact")
        if poc and poc not in ctx.run.personas:
            out.append(make("POAM-FLD-001", f"{i.get('id')}: point_of_contact {poc} is not a "
                            "framework persona", POAM_FILE))
    return out


# --- RAR --------------------------------------------------------------------------------

def rar_links(ctx: Context) -> list[RunFinding]:
    if not scope.produced_or_seeded(ctx.run, "ART-RAR"):
        return []
    risks = _items(ctx, RAR_FILE, "risks")
    if risks is None:
        return []
    sar = [f for _, f in family_records(ctx, SAR_DIR, "findings")]
    findings = {f.get("id") for f in sar} | {
        f.get("id") for f in _items(ctx, STIG_FILE, "findings") or []}
    poam = {i.get("id"): i for i in _items(ctx, POAM_FILE, "items") or []}
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RAR-001", message, RAR_FILE))

    covered: set[str] = set()
    for r in risks:
        refs = set(r.get("finding_refs") or [])
        covered |= refs
        for ref in sorted(refs - findings):
            err(f"{r.get('id')} links finding {ref}, which does not exist")
        for ref in r.get("poam_refs") or []:
            item = poam.get(ref)
            if item is None:
                err(f"{r.get('id')} links POA&M item {ref}, which does not exist")
            elif item.get("finding_ref") not in refs:
                err(f"{r.get('id')} links {ref}, whose finding {item.get('finding_ref')} is "
                    "not among the risk's finding_refs")
    for f in sar:
        if f.get("status") != "closed" and f.get("id") not in covered:
            err(f"open SAR finding {f.get('id')} ({f.get('control_id')}) maps to no risk")
    return out


# --- AO decision ------------------------------------------------------------------------

def decision_valid(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-AODM"):
        return []
    decision = ctx.data(DECISION_FILE)
    if not isinstance(decision, dict):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("AODM-001", message, DECISION_FILE))

    kinds = {e.id: e.data for e in run.framework.index("decisions").values()}
    kind = kinds.get(decision.get("decision"))
    if kind is None:
        err(f"decision {decision.get('decision')!r} is not one of {', '.join(kinds)}")
    else:
        decided_in = kind.get("decided_in") or []
        writers = run.writers("ART-AODM")
        if not any(s.get("artifact") == "ART-AODM" for s in scope.seeded(run)):
            active = set(scope.active_tasks(run))
            writers = [t for t in writers if t in active]
        if not set(decided_in) & set(writers):
            err(f"{decision.get('decision')} is decided in {', '.join(decided_in)}, not in "
                f"{' or '.join(writers) or 'any task of this run'}, the tasks of this run that "
                f"can write {DECISION_FILE}")
        if decision.get("decided_by") != kind.get("decided_by"):
            err(f"{decision.get('decision')} is decided by {kind.get('decided_by')}, not "
                f"{decision.get('decided_by')}")
        if kind.get("atd_required") and not decision.get("authorization_termination_date"):
            err(f"{decision.get('decision')} needs an authorization_termination_date")
        if kind.get("conditions_required") and not decision.get("conditions"):
            err(f"{decision.get('decision')} needs conditions")
    if decision.get("rar_ref") != "ART-RAR":
        err("no rar_ref: ART-RAR (the decision must rest on the risk assessment report)")
    degraded = ctx.degraded_refs
    if degraded and not str(decision.get("degraded_disclosure") or "").strip():
        err(f"the run depends on degraded reference(s) {', '.join(degraded)}; add a "
            "degraded_disclosure (plan §7.6)")
    return out


# --- deferrals --------------------------------------------------------------------------

def deferrals(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("TASK-DEF-001", message, RUN_FILE))

    for task, entry in (run.config.get("deferred") or {}).items():
        if isinstance(entry, dict) and not str(entry.get("rationale") or "").strip():
            err(f"deferral of {task} has no rationale")
    scopes = scope.task_scopes(run)
    if any(s.state == scope.LIFECYCLE for s in scopes.values()) and not str(
            run.config.get("lifecycle_stop_rationale") or "").strip():
        err(f"tasks after lifecycle_stop {run.config.get('lifecycle_stop')} are deferred "
            "without a lifecycle_stop_rationale")
    for aid, art in run.artifacts.items():
        producer = art.get("producer")
        state = scopes.get(producer)
        if art.get("package") == "core" and state and state.state in (scope.DEFERRED,
                                                                       scope.LIFECYCLE):
            err(f"{producer} produces core artifact {aid} and is in scope, so it cannot be "
                f"deferred ({state.state})")
    return out
