"""Coverage rules: SSP-COV-002, SSP-DUP-001, SSP-STAT-001, SAP-COV-001, SAR-COV-001,
CONMON-001, PKG-001 and PKG-003. Like SSP-COV-001 they are scope-aware: an artifact whose producer
is out of scope and that is not seeded is never demanded (plan §7.3 ``--final``)."""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.catalog import family
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.check.rules.content import SAR_DIR, SSP_DIR, family_records, sections
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import MANIFEST_FILE

SAP_FILE = "artifacts/data/sap.yaml"
CONMON_FILE = "artifacts/data/conmon.yaml"
# CNSSI 1254 Section IV: the RMF core documents.
CORE_DOCUMENTS = {"ART-SSP": "SSP", "ART-SAR": "SAR", "ART-RAR": "RAR", "ART-POAM": "POA&M",
                  "ART-AODM": "Authorization Decision Document"}
PLACEHOLDER = "<<FILL"
UNREAD_HOMES = {"pending", "rule"}  # not built yet, or a rule already holds the element
SSP_STATUSES = ("implemented", "partial", "planned", "alternative", "not-applicable",
                "inherited")


def _mapping(ctx: Context, rel: str) -> dict[str, Any] | None:
    data = ctx.data(rel)
    return data if isinstance(data, dict) else None


# --- SSP --------------------------------------------------------------------------------

def ssp_outside(ctx: Context) -> list[RunFinding]:
    if baseline_mod.load(ctx.run) is None:
        return []
    baseline = set(baseline_mod.control_ids(ctx.run))
    return [make("SSP-COV-002", f"statement for {item.get('control_id')}, which is not in the "
                 "baseline", rel)
            for rel, item in family_records(ctx, SSP_DIR, "controls")
            if item.get("control_id") not in baseline]


def ssp_duplicates(ctx: Context) -> list[RunFinding]:
    first: dict[str, str] = {}
    out = []
    for rel, item in family_records(ctx, SSP_DIR, "controls"):
        cid = str(item.get("control_id"))
        if cid in first:
            out.append(make("SSP-DUP-001", f"second statement for {cid} (first in "
                            f"{first[cid]})", rel))
        else:
            first[cid] = rel
    return out


def ssp_status(ctx: Context) -> list[RunFinding]:
    out = []
    for rel, item in family_records(ctx, SSP_DIR, "controls"):
        cid, status = item.get("control_id"), item.get("status")
        if status not in SSP_STATUSES:
            problem = f"{cid}: status {status!r} is not one of {', '.join(SSP_STATUSES)}"
        elif status == "not-applicable" and not str(item.get("rationale") or "").strip():
            problem = f"{cid} is not-applicable without a rationale"
        elif status == "inherited" and not str(item.get("inherited_from") or "").strip():
            problem = f"{cid} is inherited without inherited_from (the providing system)"
        else:
            continue
        out.append(make("SSP-STAT-001", problem, rel))
    return out


# --- SAP / SAR --------------------------------------------------------------------------

def _sap_scope(ctx: Context) -> dict[str, Any]:
    sap_scope = (_mapping(ctx, SAP_FILE) or {}).get("scope")
    return sap_scope if isinstance(sap_scope, dict) else {}


def _excluded(ctx: Context) -> set[str]:
    return {str(e.get("control_id")) for e in _sap_scope(ctx).get("excluded_controls") or []
            if isinstance(e, dict)}


def sap_coverage(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-SAP") or baseline_mod.load(run) is None:
        return []
    if _mapping(ctx, SAP_FILE) is None:
        return [make("SAP-COV-001", "no readable SAP data, so no baseline control is in the "
                     "SAP scope", SAP_FILE, None, {run.artifacts["ART-SAP"]["producer"]})]
    out = []
    sap_scope = _sap_scope(ctx)
    if sap_scope.get("include") != "baseline":
        out.append(make("SAP-COV-001", "scope.include must be 'baseline'", SAP_FILE))
    baseline = set(baseline_mod.control_ids(run))
    for e in sap_scope.get("excluded_controls") or []:
        if not isinstance(e, dict):
            continue
        cid = e.get("control_id")
        if cid not in baseline:
            out.append(make("SAP-COV-001", f"excludes {cid}, which is not in the baseline "
                            "(the scope is stale)", SAP_FILE))
        elif not str(e.get("rationale") or "").strip():
            out.append(make("SAP-COV-001", f"excludes baseline control {cid} without a "
                            "rationale", SAP_FILE))
    return out


def sar_coverage(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-SAR") or baseline_mod.load(run) is None:
        return []
    determined = {item.get("control_id")
                  for _, item in family_records(ctx, SAR_DIR, "determinations")}
    excluded = _excluded(ctx)
    return [make("SAR-COV-001", f"scoped control {cid} has no assessment determination",
                 f"{SAR_DIR}/{family(cid)}.yaml")
            for cid in baseline_mod.control_ids(run)
            if cid not in excluded and cid not in determined]


# --- CONMON / package -------------------------------------------------------------------

def conmon_frequencies(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-CONMON") or baseline_mod.load(run) is None:
        return []
    conmon = _mapping(ctx, CONMON_FILE)
    if conmon is None:
        return [make("CONMON-001", "no readable conmon.yaml, so no family has a monitoring "
                     "frequency", CONMON_FILE, None, {run.artifacts["ART-CONMON"]["producer"]})]
    listed = {f.get("family") for f in conmon.get("frequencies") or [] if isinstance(f, dict)}
    families = sorted({family(c) for c in baseline_mod.control_ids(run)})
    return [make("CONMON-001", f"baseline family {fam} has no monitoring frequency",
                 CONMON_FILE, family=fam) for fam in families if fam not in listed]


def package_complete(ctx: Context) -> list[RunFinding]:
    """The manifest exists and lists every core artifact in play that is on disk (a core
    artifact missing from disk is RUN-ART-001). A missing listing is owned by the artifact's
    producer, so artifacts produced after R-1 (RAR, AO memo) never block R-1."""
    run = ctx.run
    if not scope.produced_or_seeded(run, "ART-PKG"):
        return []
    manifest = _mapping(ctx, MANIFEST_FILE)
    if manifest is None:
        return [make("PKG-001", "package manifest missing or unreadable; run `rmf package`",
                     MANIFEST_FILE, None, {run.artifacts["ART-PKG"]["producer"]})]
    package = manifest.get("package") if isinstance(manifest.get("package"), dict) else {}
    listed = {a.get("artifact_id") for a in package.get("artifacts") or []
              if isinstance(a, dict) and a.get("files")}
    out = []
    for aid, art in run.artifacts.items():
        if art.get("package") != "core" or not scope.produced_or_seeded(run, aid):
            continue
        on_disk = run.artifact_md(aid).is_file() or bool(run.data_files(aid))
        if on_disk and aid not in listed:
            out.append(make("PKG-001", f"core artifact {aid} is not in the manifest; run "
                            "`rmf build`", MANIFEST_FILE, None, {art.get("producer")}))
    return out


def _value_at(data: Any, path: list[str]) -> list[Any]:
    """The values at a dotted path; ``*`` walks a list."""
    if not path:
        return [data]
    key, rest = path[0], path[1:]
    if key == "*":
        return [v for item in data or () for v in _value_at(item, rest)] \
            if isinstance(data, list) else []
    return _value_at(data.get(key), rest) if isinstance(data, dict) else []


def _carried(ctx: Context, aid: str, element: dict[str, Any]) -> bool:
    if "fact" in element:
        return facts_mod.get(ctx.facts, element["fact"]) is not None
    if "heading" in element:
        doc = ctx.docs.get(f"artifacts/{element.get('artifact', aid)}.md")
        return doc is not None and any(
            heading == element["heading"]
            and any(line.strip() and PLACEHOLDER not in line for line in lines)
            for heading, _, lines in sections(doc.body, 1))
    files = sorted(ctx.run.dir.glob(element["file"]))
    path = element["path"].split(".")
    values = [v for f in files for v in _value_at(ctx.data(ctx.run.rel(f)), path)]
    if element.get("exists"):
        return any(isinstance(v, str) and ctx.run.resolve(v).is_file() for v in values)
    return any(v not in (None, "", [], {}) for v in values)


def data_elements(ctx: Context) -> list[RunFinding]:
    """Each CNSSI 1254 Annex C element a core document has a home for is in that document."""
    run, out = ctx.run, []
    for aid in CORE_DOCUMENTS:
        if aid not in run.artifacts or not scope.produced_or_seeded(run, aid):
            continue
        art = run.artifacts[aid]
        for element in art.get("data_elements") or ():
            if not element.keys() & UNREAD_HOMES and not _carried(ctx, aid, element):
                out.append(make("PKG-003", f"{aid} does not carry the CNSSI 1254 data element "
                                f"{element['element']}", run.rel(run.artifact_md(aid)), None,
                                {art.get("producer")}))
    return out
