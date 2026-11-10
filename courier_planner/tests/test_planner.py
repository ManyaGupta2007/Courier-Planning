import unittest
from pathlib import Path

from courier.dataset import build_graph, generate_dataset, load_dataset
from courier.planner import plan_trips
from courier.routing import nearest_neighbour_route

DATA = Path(__file__).resolve().parent.parent / "data"


class RoutingTests(unittest.TestCase):
    def test_route_visits_every_stop_and_returns(self):
        ds = load_dataset(DATA / "small.json")
        route = nearest_neighbour_route(build_graph(ds), ds.depot, {"A", "B", "F"})
        self.assertEqual(sorted(route.stops), ["A", "B", "F"])
        self.assertEqual(route.full_path[0], ds.depot)
        self.assertEqual(route.full_path[-1], ds.depot)

    def test_no_stops_gives_empty_route(self):
        ds = load_dataset(DATA / "small.json")
        route = nearest_neighbour_route(build_graph(ds), ds.depot, [])
        self.assertEqual(route.total_distance, 0)


class PlannerTests(unittest.TestCase):
    def test_small_dataset_known_result(self):
        trip = plan_trips(load_dataset(DATA / "small.json"))[0]
        self.assertEqual([p.parcel_id for p in trip.selected], ["P001", "P003", "P004"])
        self.assertEqual(trip.knapsack.total_value, 120)
        self.assertEqual(trip.route.stops, ["A", "C", "D"])
        self.assertAlmostEqual(trip.route.total_distance, 24.0)
        self.assertTrue(all(d.on_time for d in trip.deliveries))

    def test_capacity_never_exceeded(self):
        ds = generate_dataset("t", 20, 60, 50, seed=5)
        for trip in plan_trips(ds, max_trips=5):
            self.assertLessEqual(trip.knapsack.total_weight, 50)

    def test_multiple_trips_never_repeat_parcels(self):
        ds = generate_dataset("t", 20, 40, 40, seed=9)
        loaded = [p.parcel_id for trip in plan_trips(ds, max_trips=10) for p in trip.selected]
        self.assertEqual(len(loaded), len(set(loaded)))

    def test_generated_dataset_is_connected(self):
        ds = generate_dataset("t", 40, 5, 30, seed=1)
        trip = plan_trips(ds)[0]  # would raise if a stop were unreachable
        self.assertGreater(len(trip.selected), 0)


if __name__ == "__main__":
    unittest.main()
