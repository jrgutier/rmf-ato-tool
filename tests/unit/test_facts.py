"""facts.yaml, the one home of system facts (plan §7.2)."""

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, edit_yaml

from rmf_tool import assemble, baseline
from rmf_tool.run import facts
from rmf_tool.run.model import open_run


def test_facts_set_by_task_provenance():
    run = open_run(VALID_MINIMAL, REPO_ROOT)
    data = facts.load(run)
    for fact, writer in run.fact_writers.items():
        assert facts.set_by(data, fact) == writer, fact
    assert facts.high_water(data) == "moderate"
    assert facts.display(data, "categorization.approved") == "yes (PER-AO)"


def test_baseline_resolve_reads_facts_not_profile(minimal_run):
    (minimal_run / "product/profile.yaml").write_text(
        "categorization: {c: high, i: high, a: high}\n")
    edit_yaml(minimal_run / "facts.yaml", lambda d: d["categorization"].__setitem__("c", "high"))
    data = baseline.resolve(open_run(minimal_run, REPO_ROOT))
    assert data["baseline_id"] == "SP800-53B-HIGH-SUBSET-6"
    assert data["categorization"] == {"c": "high", "i": "moderate", "a": "low"}


def test_resolve_refuses_unapproved_categorization(minimal_run):
    edit_yaml(minimal_run / "facts.yaml",
              lambda d: d["categorization"]["approved"].__setitem__("value", False))
    with pytest.raises(baseline.BaselineError, match="not approved"):
        baseline.resolve(open_run(minimal_run, REPO_ROOT))
    edit_yaml(minimal_run / "facts.yaml", lambda d: d.pop("categorization"))
    with pytest.raises(baseline.BaselineError, match="no categorization"):
        baseline.resolve(open_run(minimal_run, REPO_ROOT))


def test_build_injects_facts_block(minimal_run):
    edit_yaml(minimal_run / "facts.yaml", lambda d: d["system_name"].__setitem__(
        "value", "Field Data Relay II"))
    run = open_run(minimal_run, REPO_ROOT)
    assemble.write(run)
    for name in ("ART-SD", "ART-CAT", "ART-SSP", "ART-AODM", "ART-BASELINE"):
        assert "| System name | Field Data Relay II | C-1 |" in (
            minimal_run / f"artifacts/{name}.md").read_text()
    assert assemble.facts_block({}) == "_No system facts are set yet (facts.yaml)._\n"
