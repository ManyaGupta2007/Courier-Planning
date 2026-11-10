"""Phase 3 (part 1): weighted graph and Dijkstra's shortest-path algorithm."""

from __future__ import annotations

import heapq
import math
from collections import defaultdict


class Graph:
    """Undirected (or directed) weighted graph stored as an adjacency dict."""

    def __init__(self) -> None:
        self._adj: dict[str, dict[str, float]] = defaultdict(dict)

    def add_node(self, node: str) -> None:
        self._adj[node]  # touching a defaultdict creates the entry

    def add_edge(self, u: str, v: str, weight: float, directed: bool = False) -> None:
        if weight < 0:
            raise ValueError("Dijkstra requires non-negative edge weights")
        self._adj[u][v] = weight
        self._adj[v]  # make sure v exists as a node
        if not directed:
            self._adj[v][u] = weight

    @property
    def nodes(self) -> list[str]:
        return list(self._adj)

    def neighbours(self, node: str) -> dict[str, float]:
        return self._adj[node]

    def __contains__(self, node: str) -> bool:
        return node in self._adj

    def __len__(self) -> int:
        return len(self._adj)


def dijkstra(graph: Graph, source: str) -> tuple[dict[str, float], dict[str, str | None]]:
    """Single-source shortest paths using a binary heap.

    Time O((V + E) log V).  Returns ``(distance, previous)`` dictionaries;
    unreachable nodes have distance ``math.inf``.
    """
    if source not in graph:
        raise KeyError(f"Unknown node: {source!r}")

    distance = {node: math.inf for node in graph.nodes}
    previous: dict[str, str | None] = {node: None for node in graph.nodes}
    distance[source] = 0.0
    heap: list[tuple[float, str]] = [(0.0, source)]

    while heap:
        dist_u, u = heapq.heappop(heap)
        if dist_u > distance[u]:
            continue  # stale heap entry
        for v, weight in graph.neighbours(u).items():
            candidate = dist_u + weight
            if candidate < distance[v]:
                distance[v] = candidate
                previous[v] = u
                heapq.heappush(heap, (candidate, v))

    return distance, previous


def reconstruct_path(previous: dict[str, str | None], source: str, target: str) -> list[str]:
    """Walk the ``previous`` map backwards. Returns ``[]`` if unreachable."""
    path: list[str] = []
    node: str | None = target
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path if path and path[0] == source else []


def shortest_path(graph: Graph, source: str, target: str) -> tuple[list[str], float]:
    """Convenience wrapper: return ``(path, distance)`` between two nodes."""
    if target not in graph:
        raise KeyError(f"Unknown node: {target!r}")
    distance, previous = dijkstra(graph, source)
    return reconstruct_path(previous, source, target), distance[target]
