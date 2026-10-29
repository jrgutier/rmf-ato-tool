"""`rmf baseline resolve`: ``baseline.json`` (ART-BASELINE data) from ``facts.yaml`` only.

The categorization must be approved (C-3). Selection takes the SP 800-53B profile at the
high-water mark of C/I/A, read as raw OSCAL JSON, then applies ``tailoring.yaml``
(add/remove) and ``run.yaml:control_subset``. CNSSI 1253 per-objective selection is not
machine-readable from the references yet, so ``method`` is recorded as high-water-mark.
``product/profile.yaml`` (proposed values) is never read.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from rmf_tool import catalog
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import BASELINE_FILE, Run, YamlError

PROFILE_PATHS = {
    level: f"references/oscal/profiles/NIST_SP-800-53_rev5_{level.upper()}-baseline_profile.json"
    for level in ("low", "moderate", "high")
}
TAILORING_FILE = "artifacts/data/tailoring.yaml"


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


def resolve(run: Run) -> dict[str, Any]:
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
    profile_rel = PROFILE_PATHS[level]
    profile_path = run.repo / profile_rel
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    known = catalog.load(run.repo).controls
    order = {cid: i for i, cid in enumerate(catalog.load(run.repo).order)}

    origin = {cid: "baseline" for cid in profile_ids(profile)}
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
    baseline_id = f"SP800-53B-{level.upper()}" + (f"-SUBSET-{len(selected)}" if subset else "")
    return {
        "baseline_id": baseline_id,
        "method": "high-water-mark",
        "categorization": {k: cat[k] for k in ("c", "i", "a")},
        "overlays": list(cat.get("overlays") or []),
        "sources": [
            {"path": profile_rel, "sha256": _sha256(profile_path)},
            {"path": catalog.CATALOG_PATH, "sha256": _sha256(run.repo / catalog.CATALOG_PATH)},
        ],
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
