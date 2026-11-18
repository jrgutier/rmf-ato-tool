"""The run's simulated clock (F-17-5): set forward only, valid in run.yaml, read by rules."""

import datetime as dt

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run

from rmf_tool.check import engine
from rmf_tool.run import clock
from rmf_tool.run.model import open_run


def test_clock_moves_forward_and_keeps_run_yaml_valid(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    run = open_run(run_dir, REPO_ROOT)
    start = clock.today(run.config)
    old, new = clock.set_clock(run, "2030-01-01")
    assert (old, new) == (start, dt.date(2030, 1, 1))
    run = open_run(run_dir, REPO_ROOT)
    assert clock.today(run.config) == dt.date(2030, 1, 1)
    found = engine.select(run, engine.evaluate(run), final=True)
    assert not [f for f in found if f.rule in ("RUN-CFG-001", "RUN-FM-001")]
    with pytest.raises(clock.ClockError):
        clock.set_clock(run, "2029-12-31")
    with pytest.raises(clock.ClockError):
        clock.set_clock(run, "soon")
