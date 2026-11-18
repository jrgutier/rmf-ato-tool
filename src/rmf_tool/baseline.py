"""`rmf baseline resolve`: ``baseline.json`` (ART-BASELINE data) from ``facts.yaml`` only.

The categorization must be approved (C-3). Selection (CNSSI 1253 §3.2.1, Task S-1) is the
union of the Appendix D security control baselines for each objective at its own impact
level (C, I and A columns of ``framework/baselines/cnssi-1253.yaml``, origin ``baseline``)
and the NSS privacy control baseline, "a default for all NSS" (origin ``privacy-baseline``
for controls no security column selects). The overlays in ``categorization.overlays`` apply
next, their removals and then their additions; then ``tailoring.yaml`` (add, remove, and from
contract 0.2.0 a compensating control taken from the catalog) and ``run.yaml:control_subset``
apply. ``method: high-water-mark`` (the SP 800-53B profile at the
highest of C/I/A, read as raw OSCAL JSON) is the plan §7.6 fallback, allowed only while the
CNSSI1253 reference is degraded. ``product/profile.yaml`` (proposed values) is never read.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from rmf_tool import catalog, refs
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import BASELINE_FILE, Run, YamlError, schema_errors
from rmf_tool.yamlload import safe_load

PROFILE_PATHS = {
    level: f"references/oscal/profiles/NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json"
    for level in ("low", "moderate", "high")
}
TABLES_PATH = "framework/baselines/cnssi-1253.yaml"
TAILORING_FILE = "artifacts/data/tailoring.yaml"
INPUTS_PATH = "framework/baselines/tailoring-inputs.yaml"
PIC_PATH = "framework/baselines/privacy-considerations.yaml"
# From this contract a compensating control from the catalog is a baseline control, so it needs
# an SSP statement (SSP-COV-001); before it, rmf baseline resolve ignored compensating actions.
COMPENSATING_SINCE = "0.2.0"
CNSSI, HIGH_WATER = "cnssi1253", "high-water-mark"
METHODS = (CNSSI, HIGH_WATER)
LEVELS = ("low", "moderate", "high")
SELECTED = "X+"  # table cells that select a control (X: 800-53B and NSS, +: NSS addition)


class BaselineError(Exception):
    """The baseline cannot be resolved from the run's current facts."""


def _sha256(path: Any) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile_ids(profile: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for imp in profile["profile"].get("imports") or []:
        for inc in imp.get("include-controls") or []:
            ids += inc.get("with-ids") or []
    return ids


def load_tables(run: Run) -> dict[str, Any]:
    path = run.repo / TABLES_PATH
    try:
        data = safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BaselineError(f"{TABLES_PATH}: {exc.strerror or exc}") from exc
    errors = run.schema_errors("baselines", data)
    if errors:
        raise BaselineError(f"{TABLES_PATH}: {errors[0]}")
    return data


def load_inputs(repo: Any) -> dict[str, Any]:
    """The assumptions and overlay conditions S-2 tests a system against, schema-checked."""
    data = safe_load((repo / INPUTS_PATH).read_text(encoding="utf-8"))
    errors = schema_errors(repo, "tailoring-inputs", data)
    if errors:
        raise BaselineError(f"{INPUTS_PATH}: {errors[0]}")
    return data


def cnssi_origins(tables: dict[str, Any], cat: dict[str, str]) -> dict[str, str]:
    """Controls selected by a security column at its objective's level ("baseline") or only
    by the NSS privacy control baseline ("privacy-baseline"), in table order."""
    origins = {}
    for table in tables["tables"]:
        for block in table["blocks"]:
            for row in block["controls"]:
                if row.get("withdrawn"):
                    continue
                if any(row[o][LEVELS.index(cat[o])] in SELECTED for o in ("c", "i", "a")):
                    origins[row["id"]] = "baseline"
                elif row["privacy"] in SELECTED:
                    origins[row["id"]] = "privacy-baseline"
    return origins


ORG_FILE = "artifacts/data/org-context.yaml"
OBTAINED = "OBT-OVL-"


def obtained_overlays(run: Run) -> dict[str, dict[str, Any]]:
    """Overlays the organization obtained from their owner (org-context.yaml
    obtained_overlays), as table overlays: CDS, Intelligence, a SAP authority's, the RMF KS's."""
    if not run.path(ORG_FILE).is_file():
        return {}
    try:
        data = run.data(ORG_FILE)
    except YamlError:
        return {}
    records = data.get("obtained_overlays") if isinstance(data, dict) else None
    out = {}
    for r in records if isinstance(records, list) else []:
        controls = r.get("controls") if isinstance(r, dict) else None
        if isinstance(r.get("id"), str) and isinstance(controls, dict):
            out[r["id"]] = {"id": r["id"], "title": str(r.get("title")), "transcribed": True,
                            "blocks": [{k: list(controls.get(k) or []) for k in ("add", "remove")}]}
    return out


def overlay_problem(tables: dict[str, Any], name: str,
                    obtained: dict[str, dict[str, Any]] | None = None) -> str | None:
    """Why ``name`` cannot be applied from ``categorization.overlays``, or None."""
    known = {o["id"]: o for o in tables["overlays"]}
    if name in (obtained or {}):
        return None
    overlay = known.get(name)
    if overlay is None:
        hint = (f"; an overlay obtained from its owner is recorded in {ORG_FILE} "
                f"obtained_overlays and applied by its {OBTAINED}* ID"
                if not name.startswith(OBTAINED) else
                f"; {ORG_FILE} obtained_overlays records no {name}")
        return (f"unknown overlay {name!r} in categorization.overlays; {TABLES_PATH} lists "
                f"{', '.join(known)}{hint}")
    if overlay["transcribed"]:
        return None
    # The Privacy Overlay is transcribed per control set under its reference ID (ADR-0003).
    sets = [o["id"] for o in tables["overlays"]
            if o["transcribed"] and o["id"].startswith(f"{name}-")]
    if sets:
        return (f"overlay {name} ({overlay['title']}) is selected per control set; record "
                f"the set(s) that apply instead: {', '.join(sets)}")
    return (f"overlay {name} ({overlay['title']}) is not transcribed in {TABLES_PATH}, so its "
            "control selections cannot be applied")


def overlay_changes(tables: dict[str, Any], overlays: list[str],
                    obtained: dict[str, dict[str, Any]] | None = None
                    ) -> tuple[list[str], list[str]]:
    """What the applied overlays add and what they tailor out (``remove``, the Space Platform
    Overlay's "--" against H/H/H)."""
    known = {o["id"]: o for o in tables["overlays"]} | (obtained or {})
    added: list[str] = []
    removed: list[str] = []
    for name in overlays:
        problem = overlay_problem(tables, name, obtained)
        if problem:
            raise BaselineError(problem)
        for block in known[name]["blocks"]:
            added += block.get("add") or []
            removed += block.get("remove") or []
    return added, removed


def overlay_ids(tables: dict[str, Any], overlays: list[str]) -> list[str]:
    return overlay_changes(tables, overlays)[0]


def privacy_column(tables: dict[str, Any]) -> set[str]:
    """Controls the NSS privacy control baseline selects, "a default for all NSS"."""
    return {row["id"] for table in tables["tables"] for block in table["blocks"]
            for row in block["controls"]
            if not row.get("withdrawn") and row["privacy"] in SELECTED}


def privacy_considerations(repo: Any, overlays: list[str]) -> dict[str, dict[int, str]]:
    """Controls with a Privacy Implementation Considerations checkmark: control -> each
    subscripted implication -> its wording in the document whose column marks it (CNSSI 1253
    Appendix D, and Table 1 of each applied overlay that has the column, whose wording is the
    more specific and is preferred)."""
    data = safe_load((repo / PIC_PATH).read_text(encoding="utf-8"))
    errors = schema_errors(repo, "privacy-considerations", data)
    if errors:
        raise BaselineError(f"{PIC_PATH}: {errors[0]}")
    out: dict[str, dict[int, str]] = {}
    docs = [d for d in data["documents"] if d["ref"] in overlays]
    docs += [d for d in data["documents"] if d["ref"] == "CNSSI1253"]
    for doc in docs:
        for block in doc["blocks"]:
            for cid, marks in block["pic"].items():
                for n in marks:
                    out.setdefault(cid, {}).setdefault(n, doc["implications"][str(n)])
    return out


def cnssi_degraded(run: Run) -> bool:
    entry = next((e for e in refs.entries(refs.load_index(run.repo)) if e["id"] == "CNSSI1253"),
                 None)
    return entry is None or entry.get("status") == "degraded"


def _letters(cat: dict[str, str]) -> str:
    return "-".join(cat[o][0].upper() for o in ("c", "i", "a"))


def resolve(run: Run, method: str | None = None) -> dict[str, Any]:
    """The method is ``categorization.method`` in facts.yaml (default cnssi1253); a
    ``method`` argument must agree with it, so GEN-STALE-001 regenerates the same file."""
    facts = facts_mod.load(run)
    cat = facts_mod.get(facts, "categorization")
    if not isinstance(cat, dict):
        raise BaselineError("facts.yaml has no categorization (C-2 sets it)")
    if not facts_mod.approved(facts):
        raise BaselineError("the categorization is not approved (C-3 sets "
                            "categorization.approved.value: true)")
    level = facts_mod.high_water(facts)
    if level is None:
        raise BaselineError("categorization c/i/a must each be low, moderate or high")
    recorded = cat.get("method") or CNSSI
    if method not in (None, recorded):
        raise BaselineError(f"--method {method} differs from facts.yaml categorization.method "
                            f"({recorded}); C-2 records the method there")
    method = recorded
    if method not in METHODS:
        raise BaselineError(f"method must be one of {', '.join(METHODS)}")
    if method == HIGH_WATER and not cnssi_degraded(run):
        raise BaselineError("high-water-mark is the plan §7.6 fallback, allowed only while "
                            "the CNSSI1253 reference is degraded; use cnssi1253")
    overlays = list(cat.get("overlays") or [])
    known = catalog.load(run.repo).controls
    order = {cid: i for i, cid in enumerate(catalog.load(run.repo).order)}

    sources = []
    tables: dict[str, Any] = {"overlays": []}
    if method == CNSSI or overlays:
        tables = load_tables(run)
        sources.append({"path": TABLES_PATH, "sha256": _sha256(run.repo / TABLES_PATH)})
    if method == CNSSI:
        origin = cnssi_origins(tables, cat)
        baseline_id = f"CNSSI1253-{_letters(cat)}"
    else:
        profile_rel = PROFILE_PATHS[level]
        profile_path = run.repo / profile_rel
        origin = dict.fromkeys(profile_ids(json.loads(profile_path.read_text(encoding="utf-8"))),
                               "baseline")
        sources.append({"path": profile_rel, "sha256": _sha256(profile_path)})
        baseline_id = f"SP800-53B-{level.upper()}"
    sources.append({"path": catalog.CATALOG_PATH,
                    "sha256": _sha256(run.repo / catalog.CATALOG_PATH)})

    # Removals first, so a control one applied overlay removes and another adds is selected:
    # an overlay's tailoring-out rests on its assumptions, an addition on the overlay's need.
    # A removal tailors the security baseline; the NSS privacy control baseline, which every
    # NSS implements, keeps its controls (an S-2 remove can still take one out).
    added, removed = overlay_changes(tables, overlays, obtained_overlays(run))
    if removed and method != CNSSI:
        raise BaselineError("an overlay that tailors controls out is written against a CNSSI 1253 "
                            f"baseline; method {method} cannot apply its removals")
    privacy = privacy_column(tables) if removed and method == CNSSI else set()
    for cid in removed:
        if origin.get(cid) == "baseline" and cid in privacy:
            origin[cid] = "privacy-baseline"
        elif origin.get(cid) == "baseline":
            del origin[cid]
    for cid in added:
        origin.setdefault(cid, "overlay")
    tailored: set[str] = set()
    tailoring = run.path(TAILORING_FILE)
    if tailoring.is_file():
        try:
            data = run.data(TAILORING_FILE)
        except YamlError as exc:
            raise BaselineError(f"{TAILORING_FILE}: {exc}") from exc
        errors = run.schema_errors("tailoring", data)
        if errors:
            raise BaselineError(f"{TAILORING_FILE}: {errors[0]}")
        compensating = run.holds(COMPENSATING_SINCE)
        for action in data["actions"]:
            cid, kind = action.get("control_id"), action["action"]
            if kind == "add":
                origin.setdefault(cid, "tailored-in")
                tailored.add(cid)
            elif kind == "remove":
                origin.pop(cid, None)
            elif kind == "compensating" and compensating and cid:
                origin.setdefault(cid, "compensating")
    unknown = sorted(c for c in origin if c not in known)
    if unknown:
        raise BaselineError(f"controls not in the catalog: {', '.join(unknown)}")
    subset = run.config.get("control_subset")
    # the subset limits the selected baseline, not what tailoring adds to it (F-05-5)
    selected = [c for c in origin if not subset or c in subset or c in tailored
                or origin[c] == "compensating"]
    selected.sort(key=lambda c: order[c])
    if subset:
        # The configured subset size, not the post-tailoring count: S-2/S-3 tailoring must not
        # change S-1's baseline_id fact (FACTS-001).
        baseline_id += f"-SUBSET-{len(subset)}"
    return {
        "baseline_id": baseline_id,
        "method": method,
        "categorization": {k: cat[k] for k in ("c", "i", "a")},
        "overlays": overlays,
        "sources": sources,
        "controls": [{"control_id": c, "origin": origin[c]} for c in selected],
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2) + "\n"


def load(run: Run) -> dict[str, Any] | None:
    """The committed baseline.json, or None when absent or unreadable."""
    path = run.path(BASELINE_FILE)
    if not path.is_file():
        return None
    try:
        data = run.data(BASELINE_FILE)
    except YamlError:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("controls"), list) else None


def control_ids(run: Run) -> list[str]:
    data = load(run)
    return [c["control_id"] for c in data["controls"]
            if isinstance(c, dict) and "control_id" in c] if data else []
