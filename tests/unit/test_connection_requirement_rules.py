"""CONN-001 to CONN-004 and REQS-001 to REQS-004 report malformed run data as findings (or
leave it to RUN-FM-001); they never raise on it."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

OURS = ("CONN-001", "CONN-002", "CONN-003", "CONN-004", "REQS-005",
        "REQS-001", "REQS-002", "REQS-003", "REQS-004")
JUNK = [{"x": 1}]  # a list of mappings where a string is expected


def _boundary(data):
    conn = data["connections"][0]
    conn.update(component=JUNK, network="mission-partner", cross_domain=True,
                approvals=[{"authority": JUNK}, 7],
                cross_domain_solution={"provider": "other", "considered": 5, "component": JUNK},
                mission_partner={"requirement_approved_by": [JUNK], "partner_package": JUNK})
    data["components"][0]["id"] = JUNK
    data["dodin"] = {"position": "outside", "waiver": {"reviewed": JUNK, "granted": 3}}


def _requirements(data):
    req = data["requirements"][0]
    req.update(id=JUNK, needs=[JUNK], derived_from=5, allocated_to=[JUNK, "CMP-NONE"])
    data["needs"][0]["stakeholder"] = JUNK
    data["design_policy"][0].update(statement=JUNK, requirements=9)
    data["design_policy"][1]["statement"] = ["DP-SCAP"]
    data["agreement"]["agreed"] = [{"stakeholder": JUNK}, "x"]
    data["workforce"] = {"contracted_work_roles": ["Cyber Defense Analyst"],
                         "qualification_requirement": JUNK, "dfars_239_71": 1}


@pytest.mark.parametrize("rule", OURS)
def test_malformed_data_is_reported_not_raised(rule, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/boundary.yaml", _boundary)
    edit_yaml(run_dir / "artifacts/data/requirements.yaml", _requirements)
    findings = RULES[rule](Context(open_run(run_dir, REPO_ROOT)))
    assert all(f.rule == rule for f in findings)
    if rule in ("CONN-001", "CONN-003", "CONN-004", "REQS-001", "REQS-002", "REQS-003"):
        assert findings, rule


def test_allocation_is_judged_at_p17_when_p15_is_out_of_scope(tmp_path, monkeypatch):
    """A run that seeds ART-REQ and allocates at P-17 is still held to the allocation clause."""
    from rmf_tool.run import scope

    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/requirements.yaml",
              lambda d: d["requirements"][1].update(allocated_to=["CMP-GONE"]))
    run = open_run(run_dir, REPO_ROOT)
    monkeypatch.setattr(scope, "active_tasks", lambda _run: ["P-16", "P-17"])
    messages = [f.finding.message for f in RULES["REQS-001"](Context(run))]
    assert messages == ["REQ-02 is allocated to CMP-GONE, which is not a boundary component"]
