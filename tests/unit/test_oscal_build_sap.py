"""OSCAL assessment plan builder (Decision B1): trestle models, uuid5, OSCAL 1.2.1."""

import json

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, edit_yaml

from rmf_tool import baseline as baseline_mod
from rmf_tool.oscal import build_sap, schema_validate
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run.model import open_run

GOLDEN = REPO_ROOT / "tests/golden/oscal/assessment-plan.json"


def built(run_dir):
    return json.loads(build_sap.build_sap(open_run(run_dir, REPO_ROOT)))["assessment-plan"]


def test_minimal_golden():
    """tests/golden/oscal and the fixture's oscal/ both equal a fresh build (GEN-STALE-001)."""
    text = build_sap.build_sap(open_run(VALID_MINIMAL, REPO_ROOT))
    assert text == GOLDEN.read_text()
    assert text == (VALID_MINIMAL / build_sap.SAP_FILE).read_text()
    assert build_sap.build_sap(open_run(VALID_MINIMAL, REPO_ROOT)) == text


def test_uuid5_stable():
    ap = built(VALID_MINIMAL)
    assert ap["uuid"] == uuid_for("FDR-0001", "assessment-plan", "assessment-plan")
    assert ap["tasks"][0]["uuid"] == uuid_for("FDR-0001", "assessment-plan", "task/assessment")


def test_schema_valid_regex_and_formats():
    doc = json.loads(build_sap.build_sap(open_run(VALID_MINIMAL, REPO_ROOT)))
    assert schema_validate.validate(REPO_ROOT, doc) == []


def test_trestle_model_roundtrip():
    from trestle.oscal.assessment_plan import AssessmentPlan

    ap = built(VALID_MINIMAL)
    model = AssessmentPlan.model_validate(ap)
    assert json.loads(model.oscal_serialize_json()) == {"assessment-plan": ap}


def test_version_stamp_1_2_1():
    meta = built(VALID_MINIMAL)["metadata"]
    assert meta["oscal-version"] == "1.2.1"
    assert meta["last-modified"] == "2026-10-29T12:00:00+00:00"


def test_activities_from_catalog_methods():
    ap = built(VALID_MINIMAL)
    activities = ap["local-definitions"]["activities"]
    assert [a["props"][0]["value"] for a in activities] == ["EXAMINE", "INTERVIEW", "TEST"]
    for a in activities:
        ids = [c["control-id"] for c in a["related-controls"]["control-selections"][0]
               ["include-controls"]]
        assert ids == baseline_mod.control_ids(open_run(VALID_MINIMAL, REPO_ROOT))
    assert [x["activity-uuid"] for x in ap["tasks"][0]["associated-activities"]] == \
        [a["uuid"] for a in activities]


def test_exclusions_subjects_and_team(minimal_run):
    def edit(d):
        d["scope"]["excluded_controls"] = [{"control_id": "si-2", "rationale": "No patching."}]
        d["assessment_subjects"] = [{"type": "inventory-item", "include": ["INV-002"]},
                                    {"type": "party", "include": ["PER-ISSO"]}]
        d["team"].append({"persona": "PER-ISSE", "role": "Test lead"})
    edit_yaml(minimal_run / build_sap.SAP_DATA, edit)
    ap = built(minimal_run)
    sel = ap["reviewed-controls"]["control-selections"][0]
    included = [c["control-id"] for c in sel["include-controls"]]
    assert "si-2" not in included and "sc-7" in included
    assert sel["exclude-controls"] == [{"control-id": "si-2"}]
    assert sel["remarks"] == "si-2: No patching."
    assert ap["assessment-subjects"][0]["include-subjects"] == [
        {"subject-uuid": uuid_for("FDR-0001", "ssp", "inventory/INV-002"),
         "type": "inventory-item"}]
    assert ap["assessment-subjects"][1]["include-subjects"][0]["subject-uuid"] == \
        uuid_for("FDR-0001", "ssp", "party/PER-ISSO")
    assert [r["id"] for r in ap["metadata"]["roles"]] == ["PER-ISSE", "PER-SCA"]
    team = ap["terms-and-conditions"]["parts"][1]["prose"]
    assert team == "PER-SCA (Lead assessor, independent); PER-ISSE (Test lead)"


def test_not_buildable_lists_reasons(minimal_run):
    (minimal_run / "baseline.json").unlink()
    (minimal_run / build_sap.SAP_DATA).write_text("scope: {}\n")
    with pytest.raises(build_sap.NotBuildable) as exc:
        build_sap.build_sap(open_run(minimal_run, REPO_ROOT))
    assert "baseline.json missing" in str(exc.value)
    assert "sap.yaml violates sap.schema.json" in str(exc.value)


def test_every_control_excluded_is_not_buildable(minimal_run):
    def edit(d):
        d["scope"]["excluded_controls"] = [{"control_id": c, "rationale": "Out of scope."}
                                           for c in baseline_mod.control_ids(run)]
    run = open_run(minimal_run, REPO_ROOT)
    edit_yaml(minimal_run / build_sap.SAP_DATA, edit)
    with pytest.raises(build_sap.NotBuildable, match="excludes every baseline control"):
        build_sap.build_sap(open_run(minimal_run, REPO_ROOT))
