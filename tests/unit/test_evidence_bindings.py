"""The judge's reading of a rule's source (evidence.rule_claim and its helpers): which names
read a field, which clauses test absence, and which fixture mutations only set the scene."""

import ast

from rmf_tool.conformance import evidence


def _plain(src: str) -> frozenset[str]:
    return evidence._plain_reads(src)


def test_a_name_also_bound_elsewhere_reads_no_field():
    src = '''
def rule(ctx, given):
    a = r.get("a")
    b = r.get("b")
    for b in items:
        pass
    c = r.get("c")
    c += 1
    d: str = r.get("d")
    e: str = compute()
    e = r.get("e")
    f, g = load()
    f = r.get("f")
    given = r.get("given")
    if (h := r.get("h")):
        pass
    k = r.get("k")
    ks = [k for k in keys]
'''
    assert _plain(src) == {"a", "d", "h"}


def test_absence_through_a_list_of_silences():
    src = '''
def rule(ctx):
    if missing := [k for k in KEYS if not r.get("x")]:
        err("missing")
    gaps = [k for k in KEYS if r.get("y") is None]
    if gaps:
        err("gaps")
'''
    plain = _plain(src)
    lists = evidence._absence_lists(src, plain)
    assert lists == {"gaps", "missing"}
    tests = [t for c in evidence.failing_clauses(src, "missing") for t in c]
    assert any(evidence._tests_absence(t, plain, lists=lists) for t in tests)
    tests = [t for c in evidence.failing_clauses(src, "gaps") for t in c]
    assert any(evidence._tests_absence(t, plain, lists=lists) for t in tests)


def _absent(expr: str, plain=frozenset({"x"})) -> bool:
    return evidence._tests_absence(ast.parse(expr, mode="eval").body, plain)


def test_false_and_zero_are_values_but_an_empty_count_is_absence():
    assert not _absent("x is False")
    assert not _absent('r.get("score") == 0')
    assert _absent('len(r.get("items")) == 0')
    assert _absent('len(r.get("items")) < 1')
    assert _absent("x is None")


def test_only_the_task_list_of_run_yaml_is_scaffolding():
    run = {"op": "set_field", "file": "run.yaml"}
    assert evidence._scaffolding({**run, "path": "include_after_stop"})
    assert evidence._scaffolding({**run, "path": "scope.tasks"})
    assert not evidence._scaffolding({**run, "path": "clock"})
    assert not evidence._scaffolding({**run, "path": "entry"})
    assert evidence._scaffolding({"op": "append_text", "file": "artifacts/data/x.yaml"})
