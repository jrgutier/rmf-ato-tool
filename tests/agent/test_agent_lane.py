"""Committed agent-lane results (plan §4.4, marker `agent`): every scenario's check.json
reports 0 errors, matches meta.yaml check_sha256, has a current upstream_hash, and a fresh
`rmf check --final` on the committed run copy agrees."""

import json

import pytest
from conftest import REPO_ROOT

from rmf_tool.check import agent_lane, engine
from rmf_tool.run.model import open_run

pytestmark = pytest.mark.agent
RESULTS = REPO_ROOT / agent_lane.RESULTS_DIR
SCENARIOS = sorted((REPO_ROOT / agent_lane.SCENARIOS_DIR).glob("*.yaml"))


def test_agent_001_clean():
    assert agent_lane.check(REPO_ROOT, "E") == []


@pytest.mark.parametrize("scenario", [p.stem for p in SCENARIOS])
def test_committed_run_rechecks_clean(scenario):
    result = RESULTS / scenario
    assert json.loads((result / "check.json").read_text())["summary"]["errors"] == 0
    run = open_run(result / "run", REPO_ROOT)
    ev = engine.evaluate(run)
    assert [f for f in engine.select(run, ev, final=True) if f.severity == "E"] == []
    assert ev.status.done
