"""Phase 2 (part 2): 0/1 knapsack by dynamic programming.

Choose the subset of parcels that maximises total value without exceeding the
vehicle's weight capacity.  Each parcel is either loaded or left behind.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import Parcel


@dataclass
class KnapsackResult:
    """Outcome of the DP, including the full table as evidence."""

    selected: list[Parcel]
    total_value: int
    total_weight: int
    capacity: int
    table: list[list[int]]  # table[i][w] = best value using first i parcels, capacity w


def solve_knapsack(parcels: Sequence[Parcel], capacity: int) -> KnapsackResult:
    """Solve 0/1 knapsack. Time O(n * W), space O(n * W).

    ``parcels`` should already be sorted by urgency: on equal value the
    back-tracking step prefers earlier (more urgent) parcels.
    """
    if capacity < 0:
        raise ValueError("capacity must not be negative")

    n = len(parcels)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i, parcel in enumerate(parcels, start=1):
        for w in range(capacity + 1):
            best = table[i - 1][w]  # option 1: leave the parcel
            if parcel.weight <= w:  # option 2: load the parcel
                best = max(best, table[i - 1][w - parcel.weight] + parcel.value)
            table[i][w] = best

    # Back-track through the table to recover which parcels were chosen.
    selected: list[Parcel] = []
    w = capacity
    for i in range(n, 0, -1):
        if table[i][w] != table[i - 1][w]:
            parcel = parcels[i - 1]
            selected.append(parcel)
            w -= parcel.weight
    selected.reverse()

    return KnapsackResult(
        selected=selected,
        total_value=table[n][capacity],
        total_weight=sum(p.weight for p in selected),
        capacity=capacity,
        table=table,
    )


def format_table(parcels: Sequence[Parcel], result: KnapsackResult) -> str:
    """Render the DP table as text (useful for small instances / screenshots)."""
    cap = result.capacity
    header = "Parcel".ljust(10) + " ".join(f"{w:>3}" for w in range(cap + 1))
    lines = [header, "-" * len(header)]
    for i, row in enumerate(result.table):
        label = "(none)" if i == 0 else f"{parcels[i - 1].parcel_id}"
        lines.append(label.ljust(10) + " ".join(f"{v:>3}" for v in row))
    return "\n".join(lines)
