"""OSCAL profile and SSP builders (Decision B1): trestle models, uuid5, OSCAL 1.2.1."""

import json

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, edit_yaml

from rmf_tool import baseline
from rmf_tool.oscal import build_ssp, schema_validate
from rmf_tool.oscal import validate as oscal_validate
from rmf_tool.oscal.uuids import uuid_for
from rmf_tool.run.model import open_run


def built(run_dir):
    run = open_run(run_dir, REPO_ROOT)
    return json.loads(build_ssp.build_ssp(run)), json.loads(build_ssp.build_profile(run))


def test_minimal_golden():
    """The committed fixture OSCAL is exactly a fresh build (GEN-STALE-001 relies on it)."""
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    assert build_ssp.build_ssp(run) == (VALID_MINIMAL / "oscal/ssp.json").read_text()
    assert build_ssp.build_ssp(run) == (REPO_ROOT / "tests/golden/oscal/ssp.json").read_text()
    assert build_ssp.build_profile(run) == (VALID_MINIMAL / "oscal/profile.json").read_text()


def test_uuid5_stable():
    assert uuid_for("FDR-0001", "ssp", "ssp") == uuid_for("FDR-0001", "ssp", "ssp")
    assert uuid_for("FDR-0001", "ssp", "ssp") != uuid_for("FDR-0002", "ssp", "ssp")
    ssp, _ = built(VALID_MINIMAL)
    assert ssp["system-security-plan"]["uuid"] == uuid_for("FDR-0001", "ssp", "ssp")


def test_schema_valid_regex_and_formats():
    ssp, profile = built(VALID_MINIMAL)
    assert schema_validate.validate(REPO_ROOT, ssp) == []
    assert schema_validate.validate(REPO_ROOT, profile) == []
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    assert oscal_validate.schema_problems(run) == []
    assert oscal_validate.trestle_problems(run) == []


def test_trestle_model_roundtrip():
    from trestle.oscal.ssp import SystemSecurityPlan

    ssp, _ = built(VALID_MINIMAL)
    model = SystemSecurityPlan.model_validate(ssp["system-security-plan"])
    assert json.loads(model.oscal_serialize_json()) == ssp


def test_version_stamp_1_2_1():
    ssp, profile = built(VALID_MINIMAL)
    for doc in (ssp["system-security-plan"], profile["profile"]):
        assert doc["metadata"]["oscal-version"] == "1.2.1"
        assert doc["metadata"]["last-modified"] == "2026-10-29T12:00:00+00:00"


def test_statement_mapping():
    ssp, profile = built(VALID_MINIMAL)
    reqs = {r["control-id"]: r for r in
            ssp["system-security-plan"]["control-implementation"]["implemented-requirements"]}
    assert list(reqs) == baseline.control_ids(open_run(VALID_MINIMAL, REPO_ROOT))
    sc7 = reqs["sc-7"]["by-components"][0]
    assert sc7["implementation-status"] == {"state": "implemented"}
    assert sc7["remarks"].startswith("Inherited from Analysis enclave")
    assert {"name": "trace", "ns": build_ssp.RMF_NS, "value": "ASM-001"} in reqs["ia-2"]["props"]
    assert profile["profile"]["imports"][0]["include-controls"][0]["with-ids"] == list(reqs)


def test_hybrid_human_party(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("humans", {"PER-ISSO": "Pat"}))
    ssp, _ = built(minimal_run)
    parties = {p["name"]: p for p in ssp["system-security-plan"]["metadata"]["parties"]}
    assert parties["Pat"]["props"][0]["value"] == "false"
    assert "Information Systems Security Engineer (simulated)" in parties


def test_not_buildable_lists_reasons(minimal_run):
    for rel in ("baseline.json", "artifacts/data/boundary.yaml"):
        (minimal_run / rel).unlink()
    for path in (minimal_run / "artifacts/ssp/controls").glob("*.yaml"):
        path.unlink()
    edit_yaml(minimal_run / "facts.yaml", lambda d: d.pop("system_id"))
    (minimal_run / "artifacts/data/users.yaml").write_text("users: []\n")
    run = open_run(minimal_run, REPO_ROOT)
    with pytest.raises(build_ssp.NotBuildable) as exc:
        build_ssp.build_ssp(run)
    text = str(exc.value)
    for needle in ("facts.yaml system_id not set", "baseline.json missing",
                   "boundary.yaml missing", "users.yaml violates users.schema.json",
                   "no artifacts/ssp/controls/<fam>.yaml yet"):
        assert needle in text
    assert build_ssp.build_profile(run) is None
