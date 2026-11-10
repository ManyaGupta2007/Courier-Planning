"""Matplotlib helpers (imported lazily so the core package has no hard dependency)."""

from __future__ import annotations

from pathlib import Path

from .models import Dataset
from .planner import TripPlan


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_route(dataset: Dataset, trip: TripPlan, output: str | Path) -> None:
    """Draw the road network and highlight the trip's route and stop order."""
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(8, 7))
    xy = dataset.coordinates

    for u, v, w in dataset.edges:
        ax.plot(*zip(xy[u], xy[v]), color="#c8c8c8", linewidth=1, zorder=1)
        if len(dataset.edges) <= 30:
            mid = ((xy[u][0] + xy[v][0]) / 2, (xy[u][1] + xy[v][1]) / 2)
            ax.text(*mid, f"{w:g}", fontsize=7, color="#888888", ha="center")

    path = trip.route.full_path
    for a, b in zip(path, path[1:]):
        ax.annotate("", xy=xy[b], xytext=xy[a], zorder=3,
                    arrowprops=dict(arrowstyle="->", color="#d62728", lw=2))

    ax.scatter(*zip(*xy.values()), s=60, color="#1f77b4", zorder=2)
    ax.scatter(*xy[dataset.depot], s=220, marker="s", color="#2ca02c", zorder=4)
    for number, stop in enumerate(trip.route.stops, start=1):
        ax.scatter(*xy[stop], s=170, color="#ff7f0e", zorder=4)
        ax.text(xy[stop][0], xy[stop][1], str(number), ha="center", va="center",
                fontsize=8, fontweight="bold", zorder=5)
    if len(xy) <= 30:
        for node, (x, y) in xy.items():
            ax.text(x + 1.5, y + 1.5, node, fontsize=8)

    ax.set_title(f"{dataset.name} - trip {trip.trip_number}: {trip.route.total_distance:.1f} km "
                 f"(green = depot, orange = numbered stops)")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
