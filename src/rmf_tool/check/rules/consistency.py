"""Cross-artifact consistency rules: INV-BND-001/002, STIG-001/002, POAM-CTL-001,
POAM-FLD-001, RAR-001 to RAR-003, DIAS-001 and TASK-DEF-001. Each reads the run-data files it links
and stays quiet about a file that is missing or unreadable (RUN-ART-001 and RUN-FM-001
report those)."""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool import catalog
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import (
    POAM_FILE,
    SAR_DIR,
    SSP_DIR,
    family_records,
    inconsequential,
    monitor_owner,
)
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import RUN_FILE

INVENTORY_FILE = "artifacts/data/inventory.yaml"
BOUNDARY_FILE = "artifacts/data/boundary.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
RAR_FILE = "artifacts/data/rar.yaml"
DIAS_FILE = "artifacts/data/dias.yaml"
# Inventory kinds that a STIG or SRG covers (STIG-001).
STIG_KINDS = ("software", "operating-system", "database", "firmware", "virtual-machine")
# DoDI 8500.01 Encl 3 7.u holds all DoD IT to the STIGs and SRGs, hardware and network devices
# too: from contract 0.2.0 they need a benchmark or a not_applicable rationale as well.
DEVICE_KINDS, DEVICES_SINCE = ("hardware", "network-device"), "0.2.0"
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
    kinds = STIG_KINDS + (DEVICE_KINDS if ctx.run.holds(DEVICES_SINCE) else ())
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
            for i in inventory if i.get("kind") in kinds and i.get("id") not in mapped]
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


# --- DIAS -------------------------------------------------------------------------------

def dias_controls(ctx: Context) -> list[RunFinding]:
    data = ctx.data(DIAS_FILE)
    if not scope.produced_or_seeded(ctx.run, "ART-DIAS") or not isinstance(data, dict):
        return []
    planned = {c.get("control_id") for _, c in family_records(ctx, SSP_DIR, "controls")}
    return [make("DIAS-001", f"the DIAS assurance levels rest on {c}, which the security plan does "
                 "not hold", DIAS_FILE, None, {"R-1"})
            for c in data.get("controls") or () if c not in planned]


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
        if f.get("status") != "closed" and f.get("id") not in covered \
                and not inconsequential(f):
            out.append(make("RAR-001", f"open SAR finding {f.get('id')} "
                            f"({f.get('control_id')}) maps to no risk", RAR_FILE,
                            owners=monitor_owner(f)))
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


def rar_determination(ctx: Context) -> list[RunFinding]:
    data = ctx.data(RAR_FILE)
    if not scope.produced_or_seeded(ctx.run, "ART-RAR") or not isinstance(data, dict):
        return []
    found = data.get("determination")
    if not isinstance(found, dict):
        return [make("RAR-002", "rar.yaml records no determination of risk", RAR_FILE)]
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RAR-002", message, RAR_FILE, None, {"R-2"}))

    collaborators = found.get("collaborated_with") or ()
    advisers = {(i.front or {}).get("persona") for i in ctx.interviews if i.task == "R-2"}
    if found.get("by") not in ("PER-AO", "PER-AODR"):
        err("the authorizing official or designated representative finalizes the determination "
            f"of risk, not {found.get('by')}")
    if "PER-CISO" not in collaborators:
        err("the determination of risk is made in collaboration with the senior agency "
            "information security officer")
    if ctx.processes_pii and "PER-PRIV" not in collaborators:
        err("a system processing PII makes the determination of risk in collaboration with the "
            "senior agency official for privacy")
    if found.get("technical_advisor") != "PER-ISSM":
        err("the ISSM is the primary cybersecurity technical advisor to the AO, not "
            f"{found.get('technical_advisor')}")
    elif "PER-ISSM" not in advisers:
        err("the ISSM gave no R-2 interview, so nothing shows the technical advice reached the AO")
    if "ART-RA" not in (found.get("rests_on") or ()):
        err("risk assessments provide the information for the risk determination, and ART-RA is "
            "not among them")
    return out


def rar_courses(ctx: Context) -> list[RunFinding]:
    """R-3 weighs courses of action and commits to one. A single course stands when it is
    evaluated as adequate (SP 800-39 p. 52). Deferring R-3 defers this."""
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-RAR") or "R-3" not in scope.active_tasks(run):
        return []
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("RAR-003", message, RAR_FILE, None, {"R-3"}))

    for r in _items(ctx, RAR_FILE, "risks") or []:
        courses = r.get("courses_of_action") or []
        chosen = [c for c in courses if c.get("selected") is True]
        if len(courses) == 0:
            err(f"{r.get('id')} weighs no course of action; risk response identifies courses of "
                "action")
            continue
        adequacy = courses[0].get("adequacy")
        if len(courses) == 1 and adequacy is None:
            err(f"{r.get('id')} has a single course of action and no evaluation of whether it is "
                "adequate")
        elif len(courses) == 1 and adequacy != "adequate":
            err(f"{r.get('id')} has a single course of action found inadequate; refine it or "
                "develop alternatives")
        if len(chosen) != 1:
            err(f"{r.get('id')} selects {len(chosen)} courses of action, not one")
        elif chosen[0].get("response") != r.get("response"):
            err(f"{r.get('id')} responds {r.get('response')}, but the selected course of action "
                f"is {chosen[0].get('response')}")
        if not isinstance(r.get("selected_response"), dict):
            err(f"{r.get('id')} has no selected_response stating who is responsible and how "
                "effectiveness is judged")
    return out


# --- XCON-001 and XCON-002: the SSP, the STIG results and the SAR agree ---------------------

GAP_STATUSES = ("partial", "planned")
CLEAN_STATUSES = ("implemented", "inherited")


def _ssp_controls(ctx: Context) -> dict[str, dict[str, Any]]:
    return {str(c.get("control_id")): c for _, c in family_records(ctx, SSP_DIR, "controls")}


def ssp_sar_agree(ctx: Context) -> list[RunFinding]:
    """XCON-001 (F-12-1): a control the SSP records as partial or planned, or with an open STIG
    finding, is determined satisfied only with a `gap_closed` note saying what closed the gap."""
    if not scope.produced_or_seeded(ctx.run, "ART-SAR"):
        return []
    ssp = _ssp_controls(ctx)
    stig_open = {str(f.get("control_id")) for f in _items(ctx, STIG_FILE, "findings") or []
                 if f.get("status") == "open" and f.get("control_id")}
    out: list[RunFinding] = []
    for rel, d in family_records(ctx, SAR_DIR, "determinations"):
        cid = str(d.get("control_id"))
        if d.get("result") != "satisfied" or str(d.get("gap_closed") or "").strip():
            continue
        status = (ssp.get(cid) or {}).get("status")
        if status in GAP_STATUSES:
            why = f"the SSP records it as {status}"
        elif cid in stig_open:
            why = "stig-summary.yaml has an open finding on it"
        else:
            continue
        out.append(make("XCON-001", f"{cid} is determined satisfied, but {why}; say in "
                        "gap_closed what closed the gap, or determine it other than satisfied",
                        rel, None, {"A-3"}))
    return out


def stig_ssp_agree(ctx: Context) -> list[RunFinding]:
    """XCON-002 (F-10-7): an open STIG finding mapped to a control the SSP calls implemented
    or inherited is named in that control's statement, so the two records do not contradict
    each other silently."""
    findings = _items(ctx, STIG_FILE, "findings")
    if not findings:
        return []
    ssp = _ssp_controls(ctx)
    out: list[RunFinding] = []
    for f in findings:
        cid, fid = str(f.get("control_id") or ""), str(f.get("id"))
        control = ssp.get(cid)
        if f.get("status") != "open" or control is None:
            continue
        if control.get("status") in CLEAN_STATUSES and fid not in str(control.get("statement")):
            out.append(make("XCON-002", f"{fid} is open on {cid}, which the SSP records as "
                            f"{control.get('status')} without naming {fid}", STIG_FILE, None,
                            {"I-1"}))
    return out


# --- NSS-001: one answer to "is this a national security system?" (F-03-4, F-04-5) ---------

NSS_FILE = "artifacts/data/nss-assessments.yaml"
PIA_FILE = "artifacts/data/pia.yaml"
FACTS_FILE = "facts.yaml"


def nss_agrees(ctx: Context) -> list[RunFinding]:
    """NSS-001: the `nss` fact is the run's one answer; P-16's nss-assessments.yaml and the PIA's
    NSS exclusion agree with it."""
    node = facts_mod.get(ctx.facts, "nss")
    if not isinstance(node, dict) or not isinstance(node.get("value"), bool):
        return []
    value = node["value"]
    out: list[RunFinding] = []
    record = ctx.data(NSS_FILE)
    if isinstance(record, dict) and isinstance(record.get("nss"), bool) \
            and record["nss"] is not value:
        out.append(make("NSS-001", f"facts.yaml records nss {str(value).lower()}, and "
                        f"nss-assessments.yaml records nss {str(record['nss']).lower()}",
                        FACTS_FILE, None, {"C-1"}))
    pia = ctx.data(PIA_FILE)
    if isinstance(pia, dict) and pia.get("basis") == "nss" and not value:
        out.append(make("NSS-001", "the PIA is excluded as an NSS, and facts.yaml records the "
                        "system is no NSS", PIA_FILE, None, {"P-14"}))
    return out


# --- PRV-001: provider IDs resolve (F-04-1) -------------------------------------------------

def provider_ids(ctx: Context) -> list[RunFinding]:
    """PRV-001: each provider is registered once in org-context.yaml providers, and every
    PRV-## a record names is registered."""
    from rmf_tool.check import providers

    data = ctx.data(providers.ORG_CONTEXT_FILE)
    if not isinstance(data, dict):
        return []  # no org context yet: OCTX-001 reports it
    items = [p for p in (data.get("providers") or [])
             if isinstance(p, dict)]
    out: list[RunFinding] = []
    seen: set[str] = set()
    for p in items:
        pid = str(p.get("id"))
        if pid in seen:
            out.append(make("PRV-001", f"{pid} is registered twice in providers",
                            providers.ORG_CONTEXT_FILE))
        seen.add(pid)
    known = providers.registry(ctx)
    for rel, field, item in providers.references(ctx):
        values = item.get(field)
        for value in values if isinstance(values, list) else [values]:
            if isinstance(value, str) and providers.PROVIDER_ID.match(value) \
                    and value not in known:
                out.append(make("PRV-001", f"{field} names {value}, which org-context.yaml "
                                "providers does not register", rel))
    return out
