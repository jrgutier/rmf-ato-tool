"""GATE-001's clause reads "no ATO or ATO with conditions of the system stands" as an empty list
of authorizing records, not ``not any(...)``. The two readings agree on every input case."""

from __future__ import annotations

import itertools
from types import SimpleNamespace

from rmf_tool.check.rules.protection import AUTHORIZING

DECISIONS = (*AUTHORIZING, "AD-CATO", "AD-IATT", "AD-DATO", "AD-RESC", None, 7)
SUBJECTS = ("system", "common-controls", None, ["system"])
RECORDS = [{"decision": d, "subject": s} for d, s in itertools.product(DECISIONS, SUBJECTS)]


def _old(standing):
    return not any(s.record.get("decision") in AUTHORIZING
                   and s.record.get("subject") == "system" for s in standing)


def _new(standing):
    authorizing = [s for s in standing if s.record.get("decision") in AUTHORIZING
                   and s.record.get("subject") == "system"]
    return len(authorizing) == 0


def test_the_rewritten_clause_fires_exactly_when_the_old_one_did():
    cases = [()] + [(r,) for r in RECORDS] + list(itertools.combinations(RECORDS, 2))
    for case in cases:
        standing = [SimpleNamespace(record=r) for r in case]
        assert _old(standing) == _new(standing), case


def test_the_rule_source_holds_the_rewritten_clause():
    import inspect

    from rmf_tool.check.rules import protection

    source = inspect.getsource(protection.authorization_gates)
    assert "authorizing = [s for s in standing" in source and "if len(authorizing) == 0:" in source
    assert "not any(" not in source
