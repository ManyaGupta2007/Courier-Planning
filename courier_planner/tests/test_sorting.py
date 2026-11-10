import random
import unittest

from courier.models import Parcel
from courier.sorting import insertion_sort, merge_sort, parcel_sort_key, quick_sort, sort_parcels


class SortingTests(unittest.TestCase):
    def test_all_algorithms_match_builtin(self):
        rng = random.Random(7)
        for size in (0, 1, 2, 10, 200):
            data = [rng.randint(-50, 50) for _ in range(size)]
            expected = sorted(data)
            self.assertEqual(merge_sort(data), expected)
            self.assertEqual(quick_sort(data), expected)
            self.assertEqual(insertion_sort(data), expected)

    def test_merge_sort_is_stable(self):
        pairs = [(1, "a"), (0, "b"), (1, "c"), (0, "d")]
        self.assertEqual(merge_sort(pairs, key=lambda p: p[0]),
                         [(0, "b"), (0, "d"), (1, "a"), (1, "c")])

    def test_parcels_sorted_by_deadline_then_priority(self):
        parcels = [
            Parcel("A", "X", 5, 10, deadline=3.0, priority=1),
            Parcel("B", "X", 5, 10, deadline=2.0, priority=1),
            Parcel("C", "X", 5, 10, deadline=2.0, priority=3),
        ]
        self.assertEqual([p.parcel_id for p in sort_parcels(parcels)], ["C", "B", "A"])
        self.assertEqual(sorted(parcels, key=parcel_sort_key), sort_parcels(parcels))


if __name__ == "__main__":
    unittest.main()
