"""AGENT-001 (plan §4.4): committed agent-lane results are present, clean, self-consistent
and current."""

import functools
import hashlib
import json
import shutil

from conftest import REPO_ROOT

from rmf_tool import ci
from rmf_tool.check import agent_lane
from rmf_tool.profiles import resolve

FIXTURE = REPO_ROOT / "tests/fixtures/repo_neg/AGENT-001"


def test_fixture_reports_every_failure():
    messages = [f.message for f in agent_lane.check(FIXTURE, "E", REPO_ROOT)]
    assert any("no agent-lane result for scenario missing" in m for m in messages)
    assert any("check_sha256" in m for m in messages)
    assert any("reports 1 error(s)" in m for m in messages)
    assert any("stale" in m for m in messages)
    assert all(f.severity == "E" for f in agent_lane.check(FIXTURE, "E", REPO_ROOT))


def test_current_clean_result_passes(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(FIXTURE, root)
    shutil.rmtree(root / "tests/agent/scenarios")
    (root / "tests/agent/scenarios").mkdir()
    shutil.copy(FIXTURE / "tests/agent/scenarios/stale.yaml", root / "tests/agent/scenarios")
    raw = json.dumps({"summary": {"errors": 0, "warnings": 0, "rules_run": []},
                      "findings": []}).encode()
    (root / "tests/agent/results/stale/check.json").write_bytes(raw)
    from rmf_tool.workspace import load_scenario, scenario_hash

    scenario = load_scenario(REPO_ROOT, root / "tests/agent/scenarios/stale.yaml")
    (root / "tests/agent/results/stale/meta.yaml").write_text(
        f"check_sha256: {hashlib.sha256(raw).hexdigest()}\n"
        f"upstream_hash: {scenario_hash(root, scenario)}\n")
    assert agent_lane.check(root, "E", REPO_ROOT) == []


def test_ci_step_severity_follows_profile(tmp_path, monkeypatch):
    real = agent_lane.check
    monkeypatch.setattr(ci.agent_lane, "check", functools.partial(real, schemas=REPO_ROOT))
    step = next(s for s in ci.STEPS if s.rules == ("AGENT-001",))
    for name, expected in (("p35", "W"), ("release", "E")):
        ctx = ci.Context(FIXTURE, None, False, True, resolve(tmp_path, name))
        ok, findings, _ = step.run(ctx)
        assert {f.severity for f in findings} == {expected}
        assert ok is (expected == "W")
    fork = ci.Context(FIXTURE, None, False, True, resolve(tmp_path, "fork"))
    assert step.run(fork) == (True, [], "AGENT-001 skipped (fork profile)")
