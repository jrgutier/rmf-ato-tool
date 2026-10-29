"""`rmf baseline resolve`: raw OSCAL profiles, tailoring, control subset, determinism."""

import json

import pytest
from conftest import REPO_ROOT, edit_yaml

from rmf_tool import baseline
from rmf_tool.run.model import open_run, schema_errors


def test_resolve_from_raw_json_without_subset(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.pop("control_subset"))
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    profile = json.loads((REPO_ROOT / baseline.PROFILE_PATHS["moderate"]).read_text())
    assert [c["control_id"] for c in data["controls"]][:3] == ["ac-1", "ac-2", "ac-2.1"]
    assert len(data["controls"]) == len(baseline.profile_ids(profile))
    assert data["baseline_id"] == "SP800-53B-MODERATE"
    assert schema_errors(REPO_ROOT, "baseline", data) == []


def test_tailoring_add_and_remove(minimal_run):
    (minimal_run / "artifacts/data/tailoring.yaml").write_text(
        "actions:\n"
        "  - {control_id: ac-2, action: remove, rationale: test, sources: [product/README.md]}\n"
        "  - {control_id: pm-1, action: add, rationale: test, sources: [product/README.md]}\n")
    edit_yaml(minimal_run / "run.yaml", lambda d: d["control_subset"].append("pm-1"))
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    origins = {c["control_id"]: c["origin"] for c in data["controls"]}
    assert "ac-2" not in origins and origins["pm-1"] == "tailored-in"
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
    assert baseline.control_ids(run) == ["ac-2", "au-2", "cm-6", "ia-2", "sc-7", "si-2"]
