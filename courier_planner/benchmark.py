"""Phase 4: runtime measurements and charts.

Usage:  python benchmark.py
Outputs: results/benchmark.csv and four PNG charts in results/.
"""

from __future__ import annotations

import csv
import random
import time
from pathlib import Path
from typing import Callable

from courier.dataset import build_graph, generate_dataset, load_dataset
from courier.graph import dijkstra
from courier.knapsack import solve_knapsack
from courier.models import Parcel
from courier.planner import plan_trip
from courier.sorting import insertion_sort, merge_sort, parcel_sort_key, quick_sort

RESULTS = Path("results")
REPEATS = 3


def best_of(func: Callable[[], object], repeats: int = REPEATS) -> float:
    """Return the fastest of several runs, in seconds (reduces timing noise)."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        func()
        best = min(best, time.perf_counter() - start)
    return best


def random_parcels(n: int, seed: int = 0) -> list[Parcel]:
    rng = random.Random(seed)
    return [Parcel(f"P{i}", "X", rng.randint(1, 15), rng.randint(10, 100),
                   round(rng.uniform(1, 12), 1), rng.randint(1, 3)) for i in range(n)]


def benchmark_sorting() -> list[dict]:
    rows = []
    algorithms = {"merge sort": merge_sort, "quick sort": quick_sort,
                  "insertion sort": insertion_sort,
                  "built-in (Timsort)": lambda data, key: sorted(data, key=key)}
    for n in (100, 500, 1000, 2000, 4000):
        parcels = random_parcels(n)
        for name, func in algorithms.items():
            if name == "insertion sort" and n > 2000:
                continue  # O(n^2) gets too slow to be useful
            rows.append({"experiment": "sorting", "algorithm": name, "size": n,
                         "seconds": best_of(lambda f=func: f(parcels, key=parcel_sort_key))})
    return rows


def benchmark_knapsack() -> list[dict]:
    rows = []
    for n in (50, 100, 200, 400, 800):
        parcels = random_parcels(n)
        rows.append({"experiment": "knapsack", "algorithm": "DP (capacity 200)", "size": n,
                     "seconds": best_of(lambda: solve_knapsack(parcels, 200))})
    return rows


def benchmark_dijkstra() -> list[dict]:
    rows = []
    for nodes in (50, 100, 200, 400, 800):
        graph = build_graph(generate_dataset("b", nodes, 1, 10, seed=nodes))
        rows.append({"experiment": "dijkstra", "algorithm": "Dijkstra (heap)", "size": nodes,
                     "seconds": best_of(lambda: dijkstra(graph, "Depot"))})
    return rows


def benchmark_pipeline() -> list[dict]:
    rows = []
    for name in ("small", "medium", "large"):
        dataset = load_dataset(f"data/{name}.json")
        graph = build_graph(dataset)
        trips = [plan_trip(graph, dataset.depot, dataset.parcels, dataset.vehicle_capacity)
                 for _ in range(REPEATS)]
        for stage in ("sorting", "knapsack", "routing"):
            rows.append({"experiment": "pipeline", "algorithm": stage,
                         "size": f"{name} ({len(dataset.parcels)} parcels)",
                         "seconds": min(t.timings[stage] for t in trips)})
    return rows


def plot_line(rows: list[dict], title: str, xlabel: str, path: Path, logy: bool = True) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in dict.fromkeys(r["algorithm"] for r in rows):
        points = [(r["size"], r["seconds"] * 1000) for r in rows if r["algorithm"] == name]
        ax.plot(*zip(*points), marker="o", label=name)
    ax.set(title=title, xlabel=xlabel, ylabel="runtime (ms)")
    if logy:
        ax.set_yscale("log")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_pipeline(rows: list[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    datasets = list(dict.fromkeys(r["size"] for r in rows))
    stages = list(dict.fromkeys(r["algorithm"] for r in rows))
    width = 0.8 / len(stages)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, stage in enumerate(stages):
        values = [next(r["seconds"] for r in rows if r["size"] == d and r["algorithm"] == stage) * 1000
                  for d in datasets]
        ax.bar([x + i * width for x in range(len(datasets))], values, width, label=stage)
    ax.set_xticks([x + width for x in range(len(datasets))], datasets)
    ax.set(title="Runtime of each pipeline stage by dataset", ylabel="runtime (ms, log scale)")
    ax.set_yscale("log")
    ax.grid(alpha=0.3, axis="y")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    sorting, knap = benchmark_sorting(), benchmark_knapsack()
    dijk, pipe = benchmark_dijkstra(), benchmark_pipeline()

    with open(RESULTS / "benchmark.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, ["experiment", "algorithm", "size", "seconds"])
        writer.writeheader()
        writer.writerows(sorting + knap + dijk + pipe)

    plot_line(sorting, "Sorting algorithms: runtime vs. number of parcels", "parcels", RESULTS / "chart_sorting.png")
    plot_line(knap, "0/1 knapsack DP: runtime vs. number of parcels", "parcels", RESULTS / "chart_knapsack.png", logy=False)
    plot_line(dijk, "Dijkstra: runtime vs. number of nodes", "graph nodes", RESULTS / "chart_dijkstra.png", logy=False)
    plot_pipeline(pipe, RESULTS / "chart_pipeline.png")

    print(f"{'experiment':<12}{'algorithm':<22}{'size':<24}{'runtime (ms)':>14}")
    for r in sorting + knap + dijk + pipe:
        print(f"{r['experiment']:<12}{r['algorithm']:<22}{str(r['size']):<24}{r['seconds'] * 1000:>14.3f}")
    print(f"\nSaved {RESULTS / 'benchmark.csv'} and 4 charts in {RESULTS}/")


if __name__ == "__main__":
    main()
