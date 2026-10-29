"""OSCAL POA&M builder (Decision B1): trestle models, uuid5, OSCAL 1.2.1."""

import json

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, edit_yaml

from rmf_tool.oscal import build_poam, build_sar, schema_validate
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run.model import open_run

GOLDEN = REPO_ROOT / "tests/golden/oscal/poam.json"


def built(run_dir):
    doc = json.loads(build_poam.build_poam(open_run(run_dir, REPO_ROOT)))
    return doc["plan-of-action-and-milestones"]


def test_minimal_golden():
    """tests/golden/oscal and the fixture's oscal/ both equal a fresh build (GEN-STALE-001)."""
    text = build_poam.build_poam(open_run(VALID_MINIMAL, REPO_ROOT))
    assert text == GOLDEN.read_text()
    assert text == (VALID_MINIMAL / build_poam.POAM_FILE).read_text()
    assert build_poam.build_poam(open_run(VALID_MINIMAL, REPO_ROOT)) == text


def test_uuid5_stable():
    poam = built(VALID_MINIMAL)
    assert poam["uuid"] == uuid_for("FDR-0001", "poam", "poam")
    assert poam["poam-items"][0]["uuid"] == uuid_for("FDR-0001", "poam", "item/POAM-001")


def test_schema_valid_regex_and_formats():
    doc = json.loads(build_poam.build_poam(open_run(VALID_MINIMAL, REPO_ROOT)))
    assert schema_validate.validate(REPO_ROOT, doc) == []


def test_trestle_model_roundtrip():
    from trestle.oscal.poam import PlanOfActionAndMilestones

    poam = built(VALID_MINIMAL)
    model = PlanOfActionAndMilestones.model_validate(poam)
    assert json.loads(model.oscal_serialize_json()) == {"plan-of-action-and-milestones": poam}


def test_version_stamp_1_2_1():
    meta = built(VALID_MINIMAL)["metadata"]
    assert meta["oscal-version"] == "1.2.1"
    assert meta["last-modified"] == "2026-10-29T12:00:00+00:00"


def test_links_reuse_sar_objects():
    """Linked findings, observations and risks are the SAR's own objects (same uuid5)."""
    poam = built(VALID_MINIMAL)
    sar = json.loads((VALID_MINIMAL / build_sar.SAR_FILE).read_text())
    result = sar["assessment-results"]["results"][0]
    sar_objects = {o["uuid"]: o for key in ("observations", "findings", "risks")
                   for o in result[key]}
    for key in ("observations", "findings", "risks"):
        for obj in poam[key]:
            assert sar_objects[obj["uuid"]] == obj
    item = poam["poam-items"][0]
    assert item["related-findings"] == [{"finding-uuid": poam["findings"][0]["uuid"]}]
    assert item["related-risks"] == [{"risk-uuid": poam["risks"][0]["uuid"]}]
    props = {p["name"]: p["value"] for p in item["props"]}
    assert props["point-of-contact"] == "PER-ISSO"
    assert props["milestone"] == "2027-01-29: Run and record the first account review"
    assert "PER-ISSO" in [r["id"] for r in poam["metadata"]["roles"]]


def test_stig_item_links_observation(minimal_run):
    def add(d):
        d["items"].append({"id": "POAM-099", "finding_ref": "STG-001", "control_id": "ac-11",
                           "weakness": "Session lock not configured.", "status": "open",
                           "comments": "Fix in the next image."})
    edit_yaml(minimal_run / build_sar.POAM_DATA, add)
    poam = built(minimal_run)
    item = poam["poam-items"][-1]
    stig_uuid = uuid_for("FDR-0001", "assessment-results", "observation/STG-001")
    assert item["related-observations"] == [{"observation-uuid": stig_uuid}]
    assert "related-findings" not in item and item["remarks"] == "Fix in the next image."
    assert stig_uuid in [o["uuid"] for o in poam["observations"]]


def test_buildable_without_assessment_data(minimal_run):
    for rel in ("artifacts/data/sap.yaml", build_sar.RAR_DATA, build_sar.STIG_DATA):
        (minimal_run / rel).unlink()
    for path in (minimal_run / build_sar.SAR_RESULTS_DIR).glob("*.yaml"):
        path.unlink()
    poam = built(minimal_run)
    item = poam["poam-items"][0]
    assert not {"related-findings", "related-observations", "related-risks"} & set(item)
    assert not {"findings", "observations", "risks"} & set(poam)


def test_not_buildable_lists_reasons(minimal_run):
    (minimal_run / build_sar.POAM_DATA).unlink()
    edit_yaml(minimal_run / "facts.yaml", lambda d: d.pop("system_id"))
    with pytest.raises(build_poam.NotBuildable) as exc:
        build_poam.build_poam(open_run(minimal_run, REPO_ROOT))
    assert "facts.yaml system_id not set" in str(exc.value)
    assert "artifacts/poam/items.yaml missing" in str(exc.value)


def test_empty_poam_is_not_buildable(minimal_run):
    (minimal_run / build_sar.POAM_DATA).write_text("items: []\n")
    with pytest.raises(build_poam.NotBuildable, match="items.yaml has no items"):
        build_poam.build_poam(open_run(minimal_run, REPO_ROOT))


def test_trestle_rejection_is_not_buildable():
    from trestle.oscal.poam import PlanOfActionAndMilestones

    from rmf_tool.oscal.common import serialize

    with pytest.raises(build_poam.NotBuildable, match="trestle rejects the "
                       "PlanOfActionAndMilestones: uuid: "):
        serialize(PlanOfActionAndMilestones, {"uuid": "not-a-uuid"})
