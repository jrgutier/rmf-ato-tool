"""The task dependency graph: stable topological order, feedback edges excluded, producers
before updaters, and cycle detection (FW-DAG-001)."""

import pytest
from _framework_fixtures import MINI, REAL
from conftest import REPO_ROOT
from hypothesis import given
from hypothesis import strategies as st

from rmf_tool.framework import graph
from rmf_tool.framework.load import load
from rmf_tool.framework.model import TASKS_80037


def real_framework():
    return load(REAL, REPO_ROOT).framework


def test_topo_order_stable():
    deps = graph.dependency_graph(real_framework())
    order = graph.topo_order(deps)

    assert order == graph.topo_order(dict(reversed(list(deps.items()))))
    assert order == list(TASKS_80037)  # the framework's DAG follows the 800-37r2 sequence


def test_feedback_edges_excluded():
    fw = load(MINI, REPO_ROOT).framework
    r4 = fw.index("tasks")["R-4"]
    assert r4.data["feeds_back_to"] == ["C-2"]  # a loop back would be a cycle in depends_on

    deps = graph.dependency_graph(fw)

    assert deps["R-4"] == ["C-3"]
    assert graph.cycles(deps) == []
    assert "R-4" not in graph.ancestors(deps)["C-2"]


def test_producer_precedes_updaters():
    fw = real_framework()
    position = {t: i for i, t in enumerate(graph.topo_order(graph.dependency_graph(fw)))}
    producers = {a.id: a.data["producer"] for a in fw.of("artifacts")}
    checked = 0
    for task in fw.of("tasks"):
        for art in task.data["outputs"]:
            assert position[producers[art]] <= position[task.id], (art, task.id)
            checked += task.id != producers[art]
    assert checked > 20  # updaters exist, so the property is not vacuous


def test_dependency_graph_drops_dangling_edges():
    fw = load(MINI, REPO_ROOT).framework
    fw.index("tasks")["C-1"].data["depends_on"] = ["P-11", "Z-1"]
    assert graph.dependency_graph(fw)["C-1"] == ["P-11"]


def test_cycle_reported_from_smallest_node():
    deps = {"P-1": ["P-3"], "P-2": ["P-1"], "P-3": ["P-2"], "P-4": ["P-4"], "P-5": []}
    assert graph.cycles(deps) == [["P-1", "P-3", "P-2", "P-1"], ["P-4", "P-4"]]
    with pytest.raises(graph.CycleError, match="P-1 -> P-3 -> P-2 -> P-1"):
        graph.topo_order(deps)


NODES = [f"P-{n}" for n in range(1, 13)]


@st.composite
def dags(draw):
    """Random DAGs: edges only from a higher to a lower index in a shuffled node order."""
    nodes = draw(st.permutations(NODES))
    return {n: sorted({nodes[j] for j in range(i) if draw(st.booleans())})
            for i, n in enumerate(nodes)}


@given(dags())
def test_topo_order_respects_every_edge(deps):
    order = graph.topo_order(deps)
    position = {n: i for i, n in enumerate(order)}
    assert sorted(order) == sorted(deps)
    assert all(position[d] < position[n] for n, ds in deps.items() for d in ds)
    assert graph.cycles(deps) == []
    ancestors = graph.ancestors(deps)
    assert all(n not in ancestors[n] for n in deps)


@given(dags(), st.data())
def test_back_edge_creates_a_detected_cycle(deps, data):
    edges = [(n, d) for n, ds in deps.items() for d in ds]
    if not edges:
        return
    node, dep = data.draw(st.sampled_from(edges))
    deps[dep] = [*deps[dep], node]  # dep now also depends on node: a cycle

    found = graph.cycles(deps)

    assert any(node in c and dep in c for c in found)
    assert all(c[0] == c[-1] for c in found)
    with pytest.raises(graph.CycleError):
        graph.topo_order(deps)
