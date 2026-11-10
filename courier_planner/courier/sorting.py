"""Phase 2 (part 1): sorting algorithms for parcel prioritisation.

Parcels are ordered by *earliest deadline first*, then by *highest priority*,
then by *lightest weight*.  Merge sort is the algorithm used by the planner
because it is stable and guarantees O(n log n) in the worst case.  Quick sort
and insertion sort are included so that Phase 4 can compare them.
"""

from __future__ import annotations

import random
from typing import Callable, Sequence, TypeVar

from .models import Parcel

T = TypeVar("T")
KeyFunc = Callable[[T], object]


def parcel_sort_key(parcel: Parcel) -> tuple[float, int, int]:
    """Earliest deadline first, then highest priority, then lightest."""
    return (parcel.deadline, -parcel.priority, parcel.weight)


def merge_sort(items: Sequence[T], key: KeyFunc = lambda x: x) -> list[T]:
    """Stable top-down merge sort. Time O(n log n), extra space O(n)."""
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)

    merged: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # "<=" keeps equal elements in their original order (stability).
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(items: Sequence[T], key: KeyFunc = lambda x: x, seed: int = 0) -> list[T]:
    """Randomised 3-way quick sort. Average O(n log n), worst case O(n^2)."""
    rng = random.Random(seed)

    def _sort(data: list[T]) -> list[T]:
        if len(data) <= 1:
            return data
        pivot_key = key(data[rng.randrange(len(data))])
        smaller = [x for x in data if key(x) < pivot_key]
        equal = [x for x in data if key(x) == pivot_key]
        larger = [x for x in data if key(x) > pivot_key]
        return _sort(smaller) + equal + _sort(larger)

    return _sort(list(items))


def insertion_sort(items: Sequence[T], key: KeyFunc = lambda x: x) -> list[T]:
    """Stable insertion sort. O(n^2); only competitive on tiny inputs."""
    result = list(items)
    for i in range(1, len(result)):
        current = result[i]
        current_key = key(current)
        j = i - 1
        while j >= 0 and key(result[j]) > current_key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def sort_parcels(parcels: Sequence[Parcel]) -> list[Parcel]:
    """Sort parcels by deadline / priority using merge sort."""
    return merge_sort(parcels, key=parcel_sort_key)
