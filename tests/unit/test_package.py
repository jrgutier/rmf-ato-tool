"""`rmf package`: the eMASS-shaped manifest (plan §6.4, DoDI 8510.01 p. 19, §7.6)."""

from conftest import REPO_ROOT, VALID_MINIMAL

from rmf_tool import package
from rmf_tool.run.model import open_run


def manifest(run_dir):
    return package.manifest(open_run(run_dir, REPO_ROOT))["package"]


def test_committed_manifest_is_fresh():
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    assert package.render(run) == (VALID_MINIMAL / "package/manifest.yaml").read_text()


def test_authorization_package_elements():
    pkg = manifest(VALID_MINIMAL)
    assert pkg["authorization_package"] == [
        {"element": "security-plan", "artifact_id": "ART-SSP", "status": "present",
         "oscal": ["oscal/ssp.json"]},
        {"element": "security-assessment-report", "artifact_id": "ART-SAR", "status": "present",
         "oscal": ["oscal/assessment-results.json"]},
        {"element": "poams", "artifact_id": "ART-POAM", "status": "present",
         "oscal": ["oscal/poam.json"]},
        {"element": "authorization-decision", "artifact_id": "ART-AODM", "status": "present",
         "oscal": []},
    ]


def test_every_core_artifact_and_oscal_document_listed():
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    pkg = package.manifest(run)["package"]
    listed = {a["artifact_id"]: a for a in pkg["artifacts"]}
    core = {aid for aid, art in run.artifacts.items() if art.get("package") == "core"}
    assert core <= set(listed) and "ART-PKG" not in listed
    assert listed["ART-RAR"]["oscal"] == ["oscal/assessment-results.json"]
    assert listed["ART-BND"]["oscal"] == ["oscal/ssp.json"]
    assert {(o["model"], o["artifact_id"]) for o in pkg["oscal"]} == {
        ("profile", "ART-BASELINE"), ("ssp", "ART-SSP"), ("assessment-plan", "ART-SAP"),
        ("assessment-results", "ART-SAR"), ("poam", "ART-POAM")}
    assert pkg["degraded_references"] == []


def test_missing_oscal_and_degraded_reference(minimal_run, monkeypatch):
    (minimal_run / "oscal/poam.json").unlink()
    monkeypatch.setattr(package, "read_yaml", lambda path: {"references": [
        {"id": "CNSSI1253", "status": "degraded", "degraded": {"reason": "unobtainable"}},
        {"id": "SP800-37R2", "status": "ok"}]})
    pkg = manifest(minimal_run)
    assert pkg["authorization_package"][2]["oscal"] == []
    assert "poam" not in {o["model"] for o in pkg["oscal"]}
    assert pkg["degraded_references"] == [{"ref": "CNSSI1253", "reason": "unobtainable"}]
