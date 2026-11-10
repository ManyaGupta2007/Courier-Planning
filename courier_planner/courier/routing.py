"""Phase 3 (part 2): nearest-neighbour TSP approximation on top of Dijkstra.

The delivery points are not directly connected to each other, so the distance
between two stops is the Dijkstra shortest-path distance over the road graph.
The nearest-neighbour heuristic then repeatedly drives to the closest stop that
has not been visited yet.  It runs in O(k * (V + E) log V) for k stops and is
not optimal, but is usually within 25% of the best tour.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

from .graph import Graph, dijkstra, reconstruct_path


@dataclass
class Leg:
    """One shortest-path segment between two consecutive stops."""

    start: str
    end: str
    distance: float
    path: list[str]


@dataclass
class RoutePlan:
    """Complete delivery route for one trip."""

    depot: str
    stops: list[str] = field(default_factory=list)  # visiting order (no depot)
    legs: list[Leg] = field(default_factory=list)

    @property
    def total_distance(self) -> float:
        return sum(leg.distance for leg in self.legs)

    @property
    def full_path(self) -> list[str]:
        """Node-by-node path including intermediate junctions."""
        path = [self.depot]
        for leg in self.legs:
            path.extend(leg.path[1:])  # skip the repeated start node
        return path

    def arrival_distances(self) -> dict[str, float]:
        """Cumulative distance driven when each stop is first reached."""
        arrivals: dict[str, float] = {}
        travelled = 0.0
        for leg in self.legs:
            travelled += leg.distance
            arrivals.setdefault(leg.end, travelled)
        return arrivals


def nearest_neighbour_route(
    graph: Graph,
    depot: str,
    stops: Iterable[str],
    return_to_depot: bool = True,
) -> RoutePlan:
    """Build a delivery route with the nearest-neighbour heuristic."""
    unvisited = set(stops) - {depot}
    plan = RoutePlan(depot=depot)
    current = depot

    while unvisited:
        distance, previous = dijkstra(graph, current)
        # Tie-break on the name so results are deterministic.
        nearest = min(unvisited, key=lambda s: (distance[s], s))
        if math.isinf(distance[nearest]):
            raise ValueError(f"Delivery point {nearest!r} is unreachable from {current!r}")
        plan.legs.append(
            Leg(current, nearest, distance[nearest], reconstruct_path(previous, current, nearest))
        )
        plan.stops.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    if return_to_depot and plan.stops:
        distance, previous = dijkstra(graph, current)
        plan.legs.append(
            Leg(current, depot, distance[depot], reconstruct_path(previous, current, depot))
        )

    return plan
