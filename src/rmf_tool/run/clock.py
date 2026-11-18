"""The run's clock (dry-run finding F-17-5).

A synthetic run simulates months of work in an afternoon: the assessment, the decision and
monitoring all carry dates after the run started. ``run.yaml as_of`` stays the start (it is
OSCAL's last-modified stamp); ``clock`` is the simulated date the run has reached, set with
``rmf run clock set DATE`` and only ever moved forward. Rules that compare a record's date with
"today" read :func:`today`, so a simulated decision on 2027-01-25 is not "in the future".
"""

from __future__ import annotations

import datetime as dt
import io
from typing import Any

from ruamel.yaml import YAML

from rmf_tool.run.model import RUN_FILE, Run

FIELD = "clock"


class ClockError(ValueError):
    pass


def _day(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def today(config: dict[str, Any]) -> dt.date | None:
    """The run's date: its simulated clock when set, else the day it started."""
    return _day(config.get(FIELD)) or _day(config.get("as_of"))


def set_clock(run: Run, value: str) -> tuple[dt.date | None, dt.date]:
    """Move the clock forward to ``value``; returns (old, new). Rewrites run.yaml whole,
    keeping its comments and order."""
    new = _day(value)
    if new is None or len(value) != 10:
        raise ClockError(f"{value!r} is no date (YYYY-MM-DD)")
    old = today(run.config)
    if old is not None and new < old:
        raise ClockError(f"the clock runs forward only: {new} is before {old}")
    yaml = YAML()
    yaml.preserve_quotes = True
    path = run.dir / RUN_FILE
    data = yaml.load(path.read_text(encoding="utf-8"))
    data[FIELD] = new.isoformat()
    buf = io.StringIO()
    yaml.dump(data, buf)
    path.write_text(buf.getvalue(), encoding="utf-8")
    return old, new
