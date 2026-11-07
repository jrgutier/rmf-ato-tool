"""Cases the I-18 rules must allow: a run the source permits passes (Fable review, p11)."""

from conftest import HYBRID_MINIMAL, REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run.model import open_run


def _messages(run_dir, rule):
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule == rule]


def test_a_run_may_reenter_with_later_tasks_completed(tmp_path):
    """SP 800-37r2 2.4: a run may enter or re-enter a step, so tasks after it can be done
    (S-2 and I-1 are seeded, outside the run's scope)."""
    run_dir = copy_run(HYBRID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "run.yaml",
              lambda d: d["entry"].__setitem__("completed", ["P-1", "P-9", "S-2", "I-1"]))
    assert _messages(run_dir, "ENTRY-001") == []


def test_partner_terms_are_not_asked_of_a_system_off_the_dodin(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["system_type"].__setitem__("dodin_connection", "none"))
    edit_yaml(run_dir / "artifacts/data/system-description.yaml", lambda d: d.__setitem__(
        "interconnections", [{
            "id": "ICX-01", "component": "CMP-IDP", "system": "Partner records",
            "organization": "Partner agency", "partner": "foreign-mission-partner",
            "interface": {"kind": "TLS", "ports_protocols_services": "443/TCP",
                          "provider": "Enclave", "boundaries_crossed": "enclave"},
            "agreement": {"instrument": "moa", "reference": "MOA-1", "date": "2026-05-01",
                          "signed_by": ["CIO"]},
            "authorization": {"status": "ATO", "authorizing_official": "Partner AO"},
            "sources": ["product/architecture.md#components"]}]))
    assert _messages(run_dir, "SYSD-003") == []


def test_a_classified_system_may_mark_its_documents_as_its_guidance_says(tmp_path):
    """DoDI 8530.01 Encl 3 p.(1) sets CUI as the floor; the classified level is guidance's."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["classification"].__setitem__("value", "secret"))
    assert _messages(run_dir, "SYSD-006") == []


def test_diagrams_need_not_show_what_the_run_does_not_record(tmp_path):
    """No external component and no database: third-party services, external flows and data
    stores are not asked of the diagrams."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")

    def drop_external(d):
        d["components"] = [c for c in d["components"] if not c.get("external")]
        d["authorization_boundary"]["diagrams"][0]["shows"] = ["components"]
        d["network_architecture"]["diagrams"][0]["shows"] = ["components"]
        d["data_flow"]["diagrams"][0]["shows"] = ["data-types", "data-direction"]
    edit_yaml(run_dir / "artifacts/data/boundary.yaml", drop_external)
    edit_yaml(run_dir / "artifacts/data/inventory.yaml", lambda d: d.__setitem__(
        "items", [i for i in d["items"] if i["kind"] != "database"]))
    assert _messages(run_dir, "SUBS-002") == []
