import math
import unittest

from courier.graph import Graph, dijkstra, shortest_path


def sample_graph() -> Graph:
    g = Graph()
    for u, v, w in [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5), ("C", "D", 8)]:
        g.add_edge(u, v, w)
    g.add_node("Z")  # isolated
    return g


class DijkstraTests(unittest.TestCase):
    def test_distances(self):
        dist, _ = dijkstra(sample_graph(), "A")
        self.assertEqual(dist["B"], 3)  # A-C-B beats A-B
        self.assertEqual(dist["D"], 8)

    def test_path_reconstruction(self):
        path, distance = shortest_path(sample_graph(), "A", "D")
        self.assertEqual(path, ["A", "C", "B", "D"])
        self.assertEqual(distance, 8)

    def test_unreachable_node(self):
        path, distance = shortest_path(sample_graph(), "A", "Z")
        self.assertEqual(path, [])
        self.assertTrue(math.isinf(distance))

    def test_unknown_node(self):
        with self.assertRaises(KeyError):
            dijkstra(sample_graph(), "nope")

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            Graph().add_edge("A", "B", -1)


if __name__ == "__main__":
    unittest.main()
