"""PM-6 on the example fork run (plan §3): an honest run of the seeded product is not
vacuously green. The run-rule mutation fixtures are re-applied to it in
tests/unit/test_check_rules.py (base ``example``)."""

import json

import pytest
from conftest import EXAMPLE_RUN
from ruamel.yaml import YAML

pytestmark = pytest.mark.slow
load = YAML(typ="safe").load
LEVELS = ("very low", "low", "moderate", "high", "very high")


def data(rel):
    return load((EXAMPLE_RUN / rel).read_text(encoding="utf-8"))


def records(directory, key):
    return [r for p in sorted((EXAMPLE_RUN / directory).glob("*.yaml"))
            for r in (load(p.read_text(encoding="utf-8")) or {}).get(key) or []]


def test_open_findings_are_carried_by_poam_items():
    findings = records("artifacts/sar/results", "findings")
    poam_refs = {i["finding_ref"] for i in data("artifacts/poam/items.yaml")["items"]}
    open_ids = {f["id"] for f in findings if f["status"] == "open"}
    assert open_ids and open_ids <= poam_refs


def test_ssp_has_inherited_and_not_applicable_controls():
    controls = records("artifacts/ssp/controls", "controls")
    assert any(c["status"] == "inherited" and c.get("inherited_from") for c in controls)
    assert any(c["status"] == "not-applicable" and c.get("rationale") for c in controls)
    assert any(c["status"] == "partial" for c in controls)


def test_open_stig_finding_and_cat_i_in_poam():
    stig = data("artifacts/data/stig-summary.yaml")["findings"]
    poam_refs = {i["finding_ref"] for i in data("artifacts/poam/items.yaml")["items"]}
    assert any(f["category"] in ("CAT I", "CAT II") and f["status"] == "open" for f in stig)
    assert all(f["id"] in poam_refs for f in stig
               if f["category"] == "CAT I" and f["status"] == "open")


def test_assumptions_and_a_moderate_or_higher_risk():
    assert data("assumptions.yaml")["assumptions"]
    risks = data("artifacts/data/rar.yaml")["risks"]
    assert any(LEVELS.index(r["level"]) >= LEVELS.index("moderate") for r in risks)


def test_seeded_weaknesses_reach_the_poam():
    """The product's three disclosed weaknesses each end in a POA&M item."""
    poam = (EXAMPLE_RUN / "artifacts/poam/items.yaml").read_text(encoding="utf-8")
    for weakness in ("gcsmaint", "planner", "5.2.1"):
        assert weakness in poam, weakness


def test_metrics_report_the_status_mix():
    metrics = json.loads((EXAMPLE_RUN / "reports/metrics.json").read_text(encoding="utf-8"))
    assert metrics
