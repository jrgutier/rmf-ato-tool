"""OSCAL assessment results builder (Decision B1): trestle models, uuid5, OSCAL 1.2.1."""

import json

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, edit_yaml

from rmf_tool.oscal import build_sar, schema_validate
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run.model import open_run

GOLDEN = REPO_ROOT / "tests/golden/oscal/assessment-results.json"


def built(run_dir):
    doc = json.loads(build_sar.build_sar(open_run(run_dir, REPO_ROOT)))
    return doc["assessment-results"]


def test_minimal_golden():
    """tests/golden/oscal and the fixture's oscal/ both equal a fresh build (GEN-STALE-001)."""
    text = build_sar.build_sar(open_run(VALID_MINIMAL, REPO_ROOT))
    assert text == GOLDEN.read_text()
    assert text == (VALID_MINIMAL / build_sar.SAR_FILE).read_text()
    assert build_sar.build_sar(open_run(VALID_MINIMAL, REPO_ROOT)) == text


def test_uuid5_stable():
    result = built(VALID_MINIMAL)["results"][0]
    assert result["findings"][0]["uuid"] == uuid_for("FDR-0001", "assessment-results",
                                                     "finding/FND-001")
    assert result["risks"][0]["uuid"] == uuid_for("FDR-0001", "assessment-results",
                                                  "risk/RSK-001")


def test_schema_valid_regex_and_formats():
    doc = json.loads(build_sar.build_sar(open_run(VALID_MINIMAL, REPO_ROOT)))
    assert schema_validate.validate(REPO_ROOT, doc) == []


def test_trestle_model_roundtrip():
    from trestle.oscal.assessment_results import AssessmentResults

    ar = built(VALID_MINIMAL)
    model = AssessmentResults.model_validate(ar)
    assert json.loads(model.oscal_serialize_json()) == {"assessment-results": ar}


def test_version_stamp_1_2_1():
    meta = built(VALID_MINIMAL)["metadata"]
    assert meta["oscal-version"] == "1.2.1"
    assert meta["last-modified"] == "2026-10-29T12:00:00+00:00"


def test_observations_findings_risks_link():
    result = built(VALID_MINIMAL)["results"][0]
    obs = {o["props"][0]["value"]: o for o in result["observations"]}  # control or STG id
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    expected = [d["control_id"] for p in sorted((VALID_MINIMAL / build_sar.SAR_RESULTS_DIR)
                                               .glob("*.yaml"))
                for d in run.data(run.rel(p))["determinations"]]
    expected += [s["id"] for s in run.data(build_sar.STIG_DATA)["findings"]]
    assert list(obs) == expected
    stig = obs["STG-001"]
    assert stig["types"] == ["finding"] and stig["methods"] == ["TEST"]
    assert stig["subjects"] == [{"subject-uuid": uuid_for("FDR-0001", "ssp", "inventory/INV-002"),
                                 "type": "inventory-item"}]
    finding = result["findings"][0]
    assert finding["related-observations"] == [{"observation-uuid": obs["ac-2"]["uuid"]}]
    assert finding["related-risks"] == [{"risk-uuid": result["risks"][0]["uuid"]}]
    assert finding["origins"][0]["actors"][0]["role-id"] == "PER-SCA"
    risk = result["risks"][0]
    assert risk["characterizations"][0]["origin"]["actors"][0]["role-id"] == "PER-AODR"
    assert [f["value"] for f in risk["characterizations"][0]["facets"]] == \
        ["low", "moderate", "low"]


@pytest.mark.parametrize(("response", "poam_status", "expected"), [
    ("accept", "open", "deviation-approved"),
    ("mitigate", "completed", "closed"),
    ("mitigate", "ongoing", "remediating"),
])
def test_risk_status(minimal_run, response, poam_status, expected):
    edit_yaml(minimal_run / build_sar.RAR_DATA,
              lambda d: d["risks"][0].__setitem__("response", response))
    edit_yaml(minimal_run / build_sar.POAM_DATA,
              lambda d: d["items"][0].__setitem__("status", poam_status))
    assert built(minimal_run)["results"][0]["risks"][0]["status"] == expected


def test_closed_finding_targets_satisfied(minimal_run):
    edit_yaml(minimal_run / "artifacts/sar/results/ac.yaml",
              lambda d: d["findings"][0].__setitem__("status", "closed"))
    finding = built(minimal_run)["results"][0]["findings"][0]
    assert finding["target"]["status"] == {"state": "satisfied"}


def test_not_buildable_lists_reasons(minimal_run):
    for path in (minimal_run / build_sar.SAR_RESULTS_DIR).glob("*.yaml"):
        path.unlink()
    (minimal_run / build_sar.RAR_DATA).write_text("risks: []\n")
    with pytest.raises(build_sar.NotBuildable) as exc:
        build_sar.build_sar(open_run(minimal_run, REPO_ROOT))
    assert "no artifacts/sar/results/<fam>.yaml yet" in str(exc.value)
    assert "rar.yaml violates rar.schema.json" in str(exc.value)
