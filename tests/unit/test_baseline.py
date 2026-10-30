"""`rmf baseline resolve`: CNSSI 1253 per-objective selection, overlays, the high-water-mark
fallback, tailoring, control subset, determinism."""

import json

import pytest
from conftest import REPO_ROOT, edit_yaml

from rmf_tool import baseline, catalog
from rmf_tool.run.model import open_run, schema_errors

PRIVACY_ONLY_MML = 35  # controls only the privacy column selects at M/M/L


def _no_subset(run_dir):
    edit_yaml(run_dir / "run.yaml", lambda d: d.pop("control_subset"))


def _categorize(run_dir, c, i, a, **extra):
    def edit(d):
        d["categorization"].update(c=c, i=i, a=a, **extra)
    edit_yaml(run_dir / "facts.yaml", edit)


def _ids(run_dir):
    return [c["control_id"] for c in baseline.resolve(open_run(run_dir, REPO_ROOT))["controls"]]


def test_cnssi_mml_golden(minimal_run):
    _no_subset(minimal_run)
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    ids = [c["control_id"] for c in data["controls"]]
    assert data["method"] == "cnssi1253" and data["baseline_id"] == "CNSSI1253-M-M-L"
    assert len(ids) == 466
    assert ids[:3] == ["ac-1", "ac-2", "ac-2.1"]
    assert "ac-2.12" in ids  # "+" at C/I moderate (Insider Threat)
    assert "cp-7" not in ids  # availability moderate/high only; A is low
    origins = {c["control_id"]: c["origin"] for c in data["controls"]}
    assert origins["at-3.5"] == "privacy-baseline"  # privacy column only (CNSSI 1253 §3.2.1)
    assert origins["au-2"] == "baseline"  # privacy X, but also selected by C and I
    assert sum(o == "privacy-baseline" for o in origins.values()) == PRIVACY_ONLY_MML
    assert set(origins.values()) == {"baseline", "privacy-baseline"}
    assert [s["path"] for s in data["sources"]] == [baseline.TABLES_PATH,
                                                     "references/oscal/catalog/"
                                                     "NIST_SP-800-53_rev5_catalog.json"]
    assert schema_errors(REPO_ROOT, "baseline", data) == []


def test_cnssi_differs_from_the_800_53b_high_water_mark(minimal_run):
    _no_subset(minimal_run)
    ids = set(_ids(minimal_run))
    profile = json.loads((REPO_ROOT / baseline.PROFILE_PATHS["moderate"]).read_text())
    nist = set(baseline.profile_ids(profile))
    assert len(nist) == 287
    assert len(ids - nist) == 200
    assert sorted(nist - ids) == [
        "cp-10.2", "cp-2.1", "cp-2.3", "cp-2.8", "cp-4.1", "cp-6", "cp-6.1", "cp-6.3", "cp-7",
        "cp-7.1", "cp-7.2", "cp-7.3", "cp-8", "cp-8.1", "cp-8.2", "ia-12.5", "ma-6", "pe-10",
        "pe-11", "pe-13.1", "pe-9"]


def test_selection_is_the_union_of_the_objectives(minimal_run):
    _no_subset(minimal_run)
    picked = {}
    for cia in (("moderate", "moderate", "low"), ("moderate", "low", "low"),
                ("low", "moderate", "low"), ("low", "low", "low")):
        _categorize(minimal_run, *cia)
        picked[cia] = set(_ids(minimal_run))
    mml = picked[("moderate", "moderate", "low")]
    assert mml == picked[("moderate", "low", "low")] | picked[("low", "moderate", "low")]
    assert picked[("low", "low", "low")] < picked[("moderate", "low", "low")] < mml


def test_cnssi_ids_per_objective_cells():
    rows = [{"id": "ac-1", "privacy": "X", "c": "...", "i": "...", "a": "..."},
            {"id": "ac-2", "privacy": ".", "c": "..X", "i": "...", "a": "..."},
            {"id": "ac-3", "privacy": ".", "c": "...", "i": "...", "a": ".+X"},
            {"id": "ac-4", "privacy": ".", "c": "--.", "i": "...", "a": "..."},
            {"id": "ac-5", "withdrawn": True}]
    tables = {"tables": [{"blocks": [{"controls": rows}]}]}

    def pick(c, i, a):
        return baseline.cnssi_origins(tables, {"c": c, "i": i, "a": a})

    assert pick("low", "low", "low") == {"ac-1": "privacy-baseline"}
    assert pick("high", "low", "low") == {"ac-1": "privacy-baseline", "ac-2": "baseline"}
    assert pick("low", "high", "moderate") == {"ac-1": "privacy-baseline", "ac-3": "baseline"}
    # "--" never selects
    assert pick("moderate", "moderate", "moderate") == {"ac-1": "privacy-baseline",
                                                        "ac-3": "baseline"}


def test_transcribed_overlay_adds_controls(minimal_run):
    _no_subset(minimal_run)
    _categorize(minimal_run, "moderate", "moderate", "low",
                overlays=["CNSSI1253E-ATT5-CLASSIFIED"])
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    origins = {c["control_id"]: c["origin"] for c in data["controls"]}
    assert data["overlays"] == ["CNSSI1253E-ATT5-CLASSIFIED"]
    assert origins["ac-1"] == "baseline"  # in the NSS baseline and the overlay
    assert origins["mp-8.4"] == origins["sc-7.26"] == "overlay"
    assert sum(o == "overlay" for o in origins.values()) == len(origins) - 466


def test_privacy_overlay_acct_set_adds_controls(minimal_run):
    _no_subset(minimal_run)
    _categorize(minimal_run, "moderate", "moderate", "low",
                overlays=["CNSSI1253F-ATT6-PRIVACY-ACCT"])
    origins = {c["control_id"]: c["origin"]
               for c in baseline.resolve(open_run(minimal_run, REPO_ROOT))["controls"]}
    added = sorted(c for c, o in origins.items() if o == "overlay")
    assert len(added) == 31 and {"ac-3.14", "pt-8", "ra-8", "si-18.5"} <= set(added)
    assert origins["ac-2.9"] == "baseline"  # ACCT, but already in the M/M/L NSS baseline


@pytest.mark.parametrize(("overlay", "message"), [
    ("CNSSI1253F-ATT6-PRIVACY", "selected per control set.*PRIVACY-ACCT"),
    ("CNSSI1253F-ATT2-SPACE", "not transcribed"),
    ("CNSSI1253F-NOPE", "unknown overlay"),
])
def test_overlay_not_available_fails_clearly(minimal_run, overlay, message):
    _categorize(minimal_run, "moderate", "moderate", "low", overlays=[overlay])
    with pytest.raises(baseline.BaselineError, match=message):
        baseline.resolve(open_run(minimal_run, REPO_ROOT))


def test_high_water_mark_only_while_cnssi_is_degraded(minimal_run, monkeypatch):
    _no_subset(minimal_run)
    _categorize(minimal_run, "moderate", "moderate", "low", method="high-water-mark")
    run = open_run(minimal_run, REPO_ROOT)
    with pytest.raises(baseline.BaselineError, match="degraded"):
        baseline.resolve(run)
    monkeypatch.setattr(baseline, "cnssi_degraded", lambda run: True)
    data = baseline.resolve(run)
    profile = json.loads((REPO_ROOT / baseline.PROFILE_PATHS["moderate"]).read_text())
    assert data["method"] == "high-water-mark" and data["baseline_id"] == "SP800-53B-MODERATE"
    assert [c["control_id"] for c in data["controls"]] == baseline.profile_ids(profile)
    assert schema_errors(REPO_ROOT, "baseline", data) == []


def test_method_argument_must_match_facts(minimal_run):
    run = open_run(minimal_run, REPO_ROOT)
    assert baseline.resolve(run, "cnssi1253")["method"] == "cnssi1253"
    with pytest.raises(baseline.BaselineError, match="categorization.method"):
        baseline.resolve(run, "high-water-mark")


def test_tailoring_add_and_remove(minimal_run):
    (minimal_run / "artifacts/data/tailoring.yaml").write_text(
        "actions:\n"
        "  - {control_id: ac-2, action: remove, rationale: test, sources: [product/README.md]}\n"
        "  - {control_id: cp-7, action: add, rationale: test, sources: [product/README.md]}\n")
    edit_yaml(minimal_run / "run.yaml", lambda d: d["control_subset"].append("cp-7"))
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    origins = {c["control_id"]: c["origin"] for c in data["controls"]}
    assert "ac-2" not in origins and origins["cp-7"] == "tailored-in"
    assert origins["au-2"] == "baseline"


def test_invalid_tailoring_refused(minimal_run):
    (minimal_run / "artifacts/data/tailoring.yaml").write_text("actions: [{control_id: x}]\n")
    with pytest.raises(baseline.BaselineError, match="tailoring.yaml"):
        baseline.resolve(open_run(minimal_run, REPO_ROOT))


def test_resolve_deterministic_and_matches_fixture(minimal_run):
    run = open_run(minimal_run, REPO_ROOT)
    first = baseline.render(baseline.resolve(run))
    assert first == baseline.render(baseline.resolve(run))
    assert first == (minimal_run / "baseline.json").read_text()
    subset = run.config["control_subset"]
    assert baseline.control_ids(run) == [c for c in catalog.load(REPO_ROOT).order
                                         if c in subset]
