"""Dataset loading, saving, validation and random generation."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from .graph import Graph
from .models import Dataset, Parcel


def build_graph(dataset: Dataset) -> Graph:
    """Create the undirected road graph described by a dataset."""
    graph = Graph()
    for node in dataset.coordinates:
        graph.add_node(node)
    for u, v, weight in dataset.edges:
        graph.add_edge(u, v, weight)
    return graph


def validate(dataset: Dataset) -> None:
    """Raise ``ValueError`` if the dataset is internally inconsistent."""
    nodes = set(dataset.coordinates)
    if dataset.depot not in nodes:
        raise ValueError(f"Depot {dataset.depot!r} is not a node of the graph")
    for u, v, _ in dataset.edges:
        if u not in nodes or v not in nodes:
            raise ValueError(f"Edge ({u}, {v}) references an unknown node")
    ids = [p.parcel_id for p in dataset.parcels]
    if len(ids) != len(set(ids)):
        raise ValueError("Parcel ids must be unique")
    for parcel in dataset.parcels:
        if parcel.destination not in nodes:
            raise ValueError(f"{parcel.parcel_id}: unknown destination {parcel.destination!r}")
    if dataset.vehicle_capacity <= 0:
        raise ValueError("vehicle_capacity must be positive")


def load_dataset(path: str | Path) -> Dataset:
    """Read a dataset from a JSON file and validate it."""
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    dataset = Dataset(
        name=raw["name"],
        depot=raw["depot"],
        vehicle_capacity=raw["vehicle_capacity"],
        coordinates={k: (v[0], v[1]) for k, v in raw["nodes"].items()},
        edges=[(u, v, float(w)) for u, v, w in raw["edges"]],
        parcels=[Parcel(**p) for p in raw["parcels"]],
    )
    validate(dataset)
    return dataset


def save_dataset(dataset: Dataset, path: str | Path) -> None:
    """Write a dataset to a JSON file."""
    raw = {
        "name": dataset.name,
        "depot": dataset.depot,
        "vehicle_capacity": dataset.vehicle_capacity,
        "nodes": {k: list(v) for k, v in dataset.coordinates.items()},
        "edges": [list(e) for e in dataset.edges],
        "parcels": [vars(p) for p in dataset.parcels],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(raw, handle, indent=2)


def generate_dataset(
    name: str,
    num_nodes: int,
    num_parcels: int,
    vehicle_capacity: int,
    seed: int = 42,
) -> Dataset:
    """Generate a random, connected road network with random parcels."""
    if num_nodes < 2:
        raise ValueError("need at least two nodes")
    rng = random.Random(seed)

    names = ["Depot"] + [f"N{i:03d}" for i in range(1, num_nodes)]
    coords = {n: (round(rng.uniform(0, 100), 1), round(rng.uniform(0, 100), 1)) for n in names}

    def dist(a: str, b: str) -> float:
        return max(0.1, round(math.dist(coords[a], coords[b]), 1))

    edge_set: dict[frozenset[str], float] = {}
    for i in range(1, num_nodes):  # connect to nearest earlier node -> connected graph
        nearest = min(names[:i], key=lambda other: dist(names[i], other))
        edge_set[frozenset((names[i], nearest))] = dist(names[i], nearest)
    for a in names:  # add extra roads to the 2 nearest neighbours
        for b in sorted((n for n in names if n != a), key=lambda n: dist(a, n))[:2]:
            edge_set[frozenset((a, b))] = dist(a, b)
    edges = [(*sorted(pair), w) for pair, w in edge_set.items()]

    parcels = [
        Parcel(
            parcel_id=f"P{i:04d}",
            destination=rng.choice(names[1:]),
            weight=rng.randint(1, 15),
            value=rng.randint(10, 100),
            deadline=round(rng.uniform(1.0, 12.0), 1),
            priority=rng.randint(1, 3),
        )
        for i in range(1, num_parcels + 1)
    ]
    dataset = Dataset(name, "Depot", vehicle_capacity, coords, edges, parcels)
    validate(dataset)
    return dataset
