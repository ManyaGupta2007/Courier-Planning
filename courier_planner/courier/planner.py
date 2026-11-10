"""Integration layer: sort -> knapsack -> route -> timing, for one or more trips."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .dataset import build_graph
from .graph import Graph
from .knapsack import KnapsackResult, solve_knapsack
from .models import Dataset, Parcel
from .routing import RoutePlan, nearest_neighbour_route
from .sorting import sort_parcels


@dataclass
class Delivery:
    """Expected delivery time of one loaded parcel."""

    parcel: Parcel
    arrival_hours: float

    @property
    def on_time(self) -> bool:
        return self.arrival_hours <= self.parcel.deadline


@dataclass
class TripPlan:
    """Everything produced for a single trip of the vehicle."""

    trip_number: int
    start_time: float
    queue: list[Parcel]  # parcels still waiting, sorted by urgency
    knapsack: KnapsackResult
    route: RoutePlan
    deliveries: list[Delivery]
    duration_hours: float
    timings: dict[str, float] = field(default_factory=dict)  # seconds per stage

    @property
    def selected(self) -> list[Parcel]:
        return self.knapsack.selected


def plan_trip(
    graph: Graph,
    depot: str,
    parcels: list[Parcel],
    capacity: int,
    speed_kmh: float = 20.0,
    service_hours: float = 0.1,
    start_time: float = 0.0,
    trip_number: int = 1,
) -> TripPlan:
    """Plan one trip for the given waiting parcels."""
    timings: dict[str, float] = {}

    t0 = time.perf_counter()
    queue = sort_parcels(parcels)
    timings["sorting"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    knapsack = solve_knapsack(queue, capacity)
    timings["knapsack"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    stops = {p.destination for p in knapsack.selected}
    route = nearest_neighbour_route(graph, depot, stops)
    timings["routing"] = time.perf_counter() - t0

    # Expected arrival time at each stop = driving time + service time so far.
    arrival_km = route.arrival_distances()
    stop_index = {stop: i for i, stop in enumerate(route.stops)}
    deliveries = [
        Delivery(
            parcel=p,
            arrival_hours=start_time
            + arrival_km[p.destination] / speed_kmh
            + service_hours * stop_index[p.destination],
        )
        for p in knapsack.selected
    ]
    duration = route.total_distance / speed_kmh + service_hours * len(route.stops)

    return TripPlan(trip_number, start_time, queue, knapsack, route, deliveries, duration, timings)


def plan_trips(
    dataset: Dataset,
    max_trips: int = 1,
    capacity: int | None = None,
    speed_kmh: float = 20.0,
    service_hours: float = 0.1,
) -> list[TripPlan]:
    """Plan up to ``max_trips`` consecutive trips until no parcel is left."""
    graph = build_graph(dataset)
    capacity = capacity if capacity is not None else dataset.vehicle_capacity
    remaining = list(dataset.parcels)
    clock = 0.0
    trips: list[TripPlan] = []

    for number in range(1, max_trips + 1):
        if not remaining:
            break
        trip = plan_trip(graph, dataset.depot, remaining, capacity,
                         speed_kmh, service_hours, clock, number)
        if not trip.selected:  # nothing fits (e.g. every parcel exceeds capacity)
            break
        trips.append(trip)
        loaded = {p.parcel_id for p in trip.selected}
        remaining = [p for p in remaining if p.parcel_id not in loaded]
        clock += trip.duration_hours

    return trips
