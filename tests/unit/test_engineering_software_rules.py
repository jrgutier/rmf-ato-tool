"""SSE-001 to SSE-003 and SWA-001 and SWA-002 report malformed run data as findings (or leave it
to RUN-FM-001); they never raise on it."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check.context import Context
from rmf_tool.check.rules import RULES
from rmf_tool.run.model import open_run

OURS = ("SSE-001", "SSE-002", "SSE-003", "SWA-001", "SWA-002")
JUNK = [{"x": 1}]  # a list of mappings where a string is expected


def _requirements(data):
    data["requirements"][0].update(included_in=JUNK, kind=JUNK)
    data["derivation"] = {"informed_by": [JUNK, 3], "methods": [{"addresses": 5,
                                                                 "requirements": [JUNK]}],
                          "key_performance": [{"establishes": JUNK, "based_on": 7}],
                          "exportability": "REQ-01"}
    data["engineering"] = {"practices": [{"area": JUNK, "stages": "design", "principles": [JUNK]},
                                         "x"],
                           "assurance": {"requirements": [JUNK]}}


def _software(data):
    data.update(pipeline=JUNK, ai_development={"used": True, "tools": [JUNK, {"name": JUNK}]},
                evidence={"sbom": "x"}, test_and_evaluation={"cyber_dte": "x"})


def _ra(data):
    data["components"] = [{"name": JUNK, "kind": "open-source", "open_source": "x"},
                          {"kind": "cots", "validation": JUNK}, 4]


def _ssp(data):
    data["controls"][0].update(control_id=JUNK, assurance="x")


@pytest.mark.parametrize("rule", OURS)
def test_malformed_data_is_reported_not_raised(rule, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    data = run_dir / "artifacts/data"
    edit_yaml(data / "requirements.yaml", _requirements)
    edit_yaml(data / "software.yaml", _software)
    edit_yaml(data / "ra.yaml", _ra)
    edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml", _ssp)
    findings = RULES[rule](Context(open_run(run_dir, REPO_ROOT)))
    assert all(f.rule == rule for f in findings)
    if rule != "SSE-003":
        assert findings, rule


@pytest.mark.parametrize("rule", OURS)
def test_the_base_run_holds(rule, tmp_path):
    run = open_run(copy_run(VALID_MINIMAL, tmp_path / "run"), REPO_ROOT)
    assert RULES[rule](Context(run)) == []
