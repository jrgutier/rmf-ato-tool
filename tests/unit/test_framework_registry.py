"""The rule registry (plan §6.5): exactly 63 rules (27 repo, 36 run), each with a phase
and a negative fixture or exemption; rules of phases that have checks are implemented and
their fixtures exist."""

from pathlib import Path

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool import ci
from rmf_tool.check import REGISTRY_PATH, load_registry, registry_errors, rules_by_id
from rmf_tool.framework.validate import CHECKED_ELSEWHERE, IMPLEMENTED

REPO_RULES = {
    "FW-SCHEMA-001", "FW-ID-001", "FW-ID-002", "FW-REF-001", "FW-ART-001", "FW-ORD-001",
    "FW-IO-001", "FW-RACI-001", "FW-DAG-001", "FW-CITE-001", "FW-CITE-002", "FW-TASK-001",
    "FW-PB-001", "FW-PB-002", "FW-PER-001", "FW-PER-002", "FW-MAN-001", "REF-001", "REF-002",
    "REF-003", "REF-004", "REF-005", "REF-006", "LES-002", "LES-003", "DOC-001", "AGENT-001",
}
SKELETON_RULES = {
    "RUN-CFG-001", "RUN-FM-001", "RUN-ART-001", "FACTS-001", "GEN-STALE-001", "SSP-COV-001",
    "SAR-POAM-001", "TRACE-001", "TRACE-002", "HYB-001", "HYB-002", "OSCAL-001", "OSCAL-002",
    "JOURNAL-001",
}


def test_registry_rule_count():
    rules = load_registry()
    assert len(rules) == 63
    assert {r.id for r in rules if r.scope == "repo"} == REPO_RULES
    assert sum(r.scope == "run" for r in rules) == 36


def test_phases_follow_the_plan():
    by_id = rules_by_id()
    assert {r for r, rule in by_id.items() if rule.phase == "p35"} == SKELETON_RULES | {
        "AGENT-001"}
    assert {r.id for r in by_id.values() if r.phase == "p3a"} == {
        r for r in IMPLEMENTED if by_id[r].phase == "p3a"}
    assert {r.phase for r in by_id.values() if r.scope == "run"} == {"p35", "p6"}
    assert all(r.applies_after is None for r in by_id.values() if r.scope == "repo")


def phases_with_checks():
    return {s.phase for s in ci.STEPS if s.phase}


def test_every_rule_has_fixture_or_exemption():
    """For rules whose phase already has checks, the named fixture exists: a directory, a
    file, or a test node (path::name) whose test function is defined."""
    active = phases_with_checks()
    checked = 0
    for rule in load_registry():
        assert (rule.fixture is None) != (rule.exempt_reason is None), rule.id
        if rule.phase not in active or rule.fixture is None:
            continue
        path, _, test = rule.fixture.partition("::")
        target = REPO_ROOT / path
        assert target.exists(), f"{rule.id}: {rule.fixture}"
        if test:
            assert f"def {test}(" in target.read_text(encoding="utf-8"), rule.id
        checked += 1
    # every rule of a phase with checks has a fixture (plan §6.5: no exemptions)
    assert checked == sum(r.phase in active for r in load_registry())


def test_framework_rules_are_implemented_by_validate():
    for rule in load_registry():
        if rule.id.startswith("FW-") and rule.phase in phases_with_checks():
            assert rule.id in IMPLEMENTED or rule.id in CHECKED_ELSEWHERE


def test_profile_severity_needs_a_note():
    data = YAML(typ="safe").load(REGISTRY_PATH.read_text(encoding="utf-8"))
    for r in data["rules"]:
        if r["id"] == "REF-001":
            del r["severity_note"]
    assert any("severity_note" in e for e in registry_errors(data))


@pytest.mark.parametrize("change, needle", [
    ({"severity": "X"}, "'X' is not one of"),
    ({"phase": "p9"}, "'p9' is not one of"),
    ({"exempt_reason": "both given"}, "is not valid under any of the given schemas"),
    ({"ac": ["AC-99a", "8"]}, "does not match"),
])
def test_registry_schema_rejects(change, needle):
    data = YAML(typ="safe").load(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["rules"][0].update(change)
    assert any(needle in e for e in registry_errors(data))


def test_duplicate_rule_ids_rejected(tmp_path):
    data = YAML(typ="safe").load(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["rules"].append(dict(data["rules"][0]))
    assert "duplicate rule id FW-SCHEMA-001" in registry_errors(data)
    bad = Path(tmp_path / "registry.yaml")
    YAML().dump(data, bad)
    with pytest.raises(ValueError, match="duplicate rule id"):
        load_registry(bad)
