import itertools
import random
import unittest

from courier.knapsack import solve_knapsack
from courier.models import Parcel


def brute_force(parcels, capacity):
    best = 0
    for r in range(len(parcels) + 1):
        for combo in itertools.combinations(parcels, r):
            if sum(p.weight for p in combo) <= capacity:
                best = max(best, sum(p.value for p in combo))
    return best


class KnapsackTests(unittest.TestCase):
    def test_matches_brute_force_on_random_instances(self):
        rng = random.Random(3)
        for _ in range(30):
            parcels = [Parcel(f"P{i}", "X", rng.randint(1, 9), rng.randint(1, 50), 1.0)
                       for i in range(rng.randint(1, 9))]
            capacity = rng.randint(1, 25)
            result = solve_knapsack(parcels, capacity)
            self.assertEqual(result.total_value, brute_force(parcels, capacity))
            self.assertLessEqual(result.total_weight, capacity)
            self.assertEqual(sum(p.value for p in result.selected), result.total_value)

    def test_nothing_fits(self):
        result = solve_knapsack([Parcel("P", "X", 10, 5, 1.0)], 4)
        self.assertEqual(result.selected, [])
        self.assertEqual(result.total_value, 0)

    def test_empty_input(self):
        self.assertEqual(solve_knapsack([], 10).total_value, 0)

    def test_negative_capacity_rejected(self):
        with self.assertRaises(ValueError):
            solve_knapsack([], -1)


if __name__ == "__main__":
    unittest.main()
