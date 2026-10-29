"""The task dependency graph: ``depends_on`` edges only. ``feeds_back_to`` edges
(monitoring results feeding earlier tasks) are documentation and never ordering, so
they cannot create cycles (FW-DAG-001) or ancestry (FW-ORD-001, FW-IO-001).
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from rmf_tool.framework.model import Framework, task_sort_key

Graph = Mapping[str, Sequence[str]]  # node -> the nodes it depends on


class CycleError(ValueError):
    def __init__(self, cycles: list[list[str]]) -> None:
        super().__init__("depends_on cycle: " + "; ".join(" -> ".join(c) for c in cycles))
        self.cycles = cycles


def dependency_graph(fw: Framework) -> dict[str, list[str]]:
    """Task -> its depends_on tasks, keeping only edges to tasks that exist
    (dangling ones are FW-REF-001's)."""
    tasks = fw.index("tasks")
    return {tid: [d for d in (t.data.get("depends_on") or []) if d in tasks]
            for tid, t in tasks.items()}


def cycles(graph: Graph) -> list[list[str]]:
    """One representative cycle per strongly connected component that has one
    (Tarjan), each starting at its smallest node, in node order."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    found: list[list[str]] = []

    def strongconnect(v: str) -> None:
        index[v] = low[v] = len(index)
        stack.append(v)
        on_stack.add(v)
        for w in graph.get(v, ()):
            if w not in graph:
                continue
            if w not in index:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            component = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            if len(component) > 1 or v in graph.get(v, ()):
                found.append(_cycle_path(graph, set(component)))

    for node in sorted(graph, key=str):
        if node not in index:
            strongconnect(node)
    return sorted(found)


def _cycle_path(graph: Graph, component: set[str]) -> list[str]:
    start = min(component)
    path, seen, node = [start], {start}, start
    while True:
        node = min(w for w in graph[node] if w in component)
        if node in seen:
            return path[path.index(node):] + [node]
        path.append(node)
        seen.add(node)


def topo_order(graph: Graph, key: Callable[[str], Any] = task_sort_key) -> list[str]:
    """Dependencies first; among ready nodes the smallest ``key`` first, so the order is
    stable for a given graph. Raises CycleError on a cycle."""
    remaining = {n: sum(1 for d in deps if d in graph) for n, deps in graph.items()}
    dependents: dict[str, list[str]] = {n: [] for n in graph}
    for n, deps in graph.items():
        for d in deps:
            if d in graph:
                dependents[d].append(n)
    ready = [(key(n), n) for n, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        _, n = heapq.heappop(ready)
        order.append(n)
        for m in dependents[n]:
            remaining[m] -= 1
            if remaining[m] == 0:
                heapq.heappush(ready, (key(m), m))
    if len(order) != len(graph):
        raise CycleError(cycles(graph))
    return order


def ancestors(graph: Graph) -> dict[str, frozenset[str]]:
    """Node -> every node it transitively depends on (excluding itself unless it lies
    on a cycle)."""
    result: dict[str, frozenset[str]] = {}
    for node in graph:
        seen: set[str] = set()
        todo = [d for d in graph[node] if d in graph]
        while todo:
            d = todo.pop()
            if d not in seen:
                seen.add(d)
                todo.extend(x for x in graph[d] if x in graph)
        result[node] = frozenset(seen)
    return result

