"""`rmf baseline resolve`: ``baseline.json`` (ART-BASELINE data) from ``facts.yaml`` only.

The categorization must be approved (C-3). Selection (CNSSI 1253 §3.2.1, Task S-1) is the
union of the Appendix D security control baselines for each objective at its own impact
level (C, I and A columns of ``framework/baselines/cnssi-1253.yaml``, origin ``baseline``)
and the NSS privacy control baseline, "a default for all NSS" (origin ``privacy-baseline``
for controls no security column selects). The overlays in
``categorization.overlays`` are added next, then ``tailoring.yaml`` (add/remove) and
``run.yaml:control_subset`` apply. ``method: high-water-mark`` (the SP 800-53B profile at the
highest of C/I/A, read as raw OSCAL JSON) is the plan §7.6 fallback, allowed only while the
CNSSI1253 reference is degraded. ``product/profile.yaml`` (proposed values) is never read.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from rmf_tool import catalog, refs
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import BASELINE_FILE, Run, YamlError
from rmf_tool.yamlload import safe_load

PROFILE_PATHS = {
    level: f"references/oscal/profiles/NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json"
    for level in ("low", "moderate", "high")
}
TABLES_PATH = "framework/baselines/cnssi-1253.yaml"
TAILORING_FILE = "artifacts/data/tailoring.yaml"
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


def overlay_problem(tables: dict[str, Any], name: str) -> str | None:
    """Why ``name`` cannot be applied from ``categorization.overlays``, or None."""
    known = {o["id"]: o for o in tables["overlays"]}
    overlay = known.get(name)
    if overlay is None:
        return (f"unknown overlay {name!r} in categorization.overlays; {TABLES_PATH} lists "
                f"{', '.join(known)}")
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


def overlay_ids(tables: dict[str, Any], overlays: list[str]) -> list[str]:
    known = {o["id"]: o for o in tables["overlays"]}
    ids: list[str] = []
    for name in overlays:
        problem = overlay_problem(tables, name)
        if problem:
            raise BaselineError(problem)
        ids += [cid for block in known[name]["blocks"] for cid in block["add"]]
    return ids


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

    for cid in overlay_ids(tables, overlays):
        origin.setdefault(cid, "overlay")
    tailoring = run.path(TAILORING_FILE)
    if tailoring.is_file():
        try:
            data = run.data(TAILORING_FILE)
        except YamlError as exc:
            raise BaselineError(f"{TAILORING_FILE}: {exc}") from exc
        errors = run.schema_errors("tailoring", data)
        if errors:
            raise BaselineError(f"{TAILORING_FILE}: {errors[0]}")
        for action in data["actions"]:
            cid = action["control_id"]
            if action["action"] == "add":
                origin.setdefault(cid, "tailored-in")
            elif action["action"] == "remove":
                origin.pop(cid, None)
    unknown = sorted(c for c in origin if c not in known)
    if unknown:
        raise BaselineError(f"controls not in the catalog: {', '.join(unknown)}")
    subset = run.config.get("control_subset")
    selected = [c for c in origin if not subset or c in subset]
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
