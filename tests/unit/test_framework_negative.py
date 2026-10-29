"""AC-6/AC-7: each framework rule fires on its negative fixture, and only the rules the
fixture declares (``rule`` plus ``also``) fire."""

import pytest
from _framework_fixtures import NEG, P3A, compose, expectation
from conftest import REPO_ROOT

from rmf_tool.check import load_registry
from rmf_tool.framework.validate import IMPLEMENTED, validate

FIXTURE_DIRS = sorted(p for p in NEG.iterdir() if p.is_dir())


@pytest.mark.parametrize("overlay", FIXTURE_DIRS, ids=lambda p: p.name)
def test_negative_fixture_fires_exactly_its_rules(overlay, tmp_path):
    expect = expectation(overlay)
    assert expect["rule"] == overlay.name

    result = validate(compose(overlay, tmp_path / "fw"), REPO_ROOT, P3A)

    fired = {f.rule for f in result.findings if f.severity == "E"}
    assert fired == {expect["rule"], *expect["also"]}, [f.render() for f in result.findings]
    assert not result.ok


def test_every_p3a_framework_rule_has_a_fixture():
    p3a_rules = {r.id for r in load_registry() if r.id.startswith("FW-") and r.phase == "p3a"}
    assert p3a_rules == {p.name for p in FIXTURE_DIRS} <= set(IMPLEMENTED)


def test_registry_points_at_the_fixture_dirs():
    for rule in load_registry():
        if rule.id in IMPLEMENTED and rule.phase == "p3a":
            assert rule.fixture == f"tests/fixtures/framework_neg/{rule.id}/"


def test_fixture_findings_name_file_and_line(tmp_path):
    overlay = NEG / "FW-RACI-001"
    result = validate(compose(overlay, tmp_path / "fw"), REPO_ROOT, P3A)
    [finding] = result.findings
    assert finding.path.endswith("tasks/R.yaml")
    assert finding.line == 2
    assert finding.message.startswith("R-4: raci.A must name exactly one persona (found 2)")
