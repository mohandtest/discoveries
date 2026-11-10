import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from network_null import adjacency, attempt, read_graph, run_chain, triangle_count
from random import Random


class NetworkNullTests(unittest.TestCase):
    def test_karate_fixture(self):
        path = Path(__file__).parent / 'data' / 'karate.edgelist'
        labels, edges = read_graph(path)
        self.assertEqual((len(labels), len(edges)), (34, 78))
        self.assertEqual(triangle_count(adjacency(len(labels), edges)), 45)

    def test_preserves_simple_graph_and_degrees(self):
        labels, edges = read_graph(Path(__file__).parent / 'data' / 'karate.edgelist')
        adj = adjacency(len(labels), edges)
        degrees = [len(a) for a in adj]
        rng = Random(6)
        for _ in range(10000):
            attempt(edges, adj, rng)
        self.assertEqual([len(a) for a in adj], degrees)
        self.assertEqual(len(set(edges)), len(edges))
        self.assertEqual(adj, adjacency(len(labels), edges))

    def test_known_triangle_tail(self):
        # Six degree-2 vertices: exactly 10/70 realizations have 2 triangles.
        edges = [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)]
        chains = [run_chain(6, edges, 1000, 3000, 10, seed)[0] for seed in range(4)]
        fraction = sum(x == 2 for chain in chains for x in chain) / 12000
        self.assertAlmostEqual(fraction, 1 / 7, delta=0.02)

    def test_rejects_malformed_and_keeps_isolates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'graph'
            path.write_text('a b\nb a\n')
            with self.assertRaises(ValueError):
                read_graph(path)
            path.write_text('a a\n')
            with self.assertRaises(ValueError):
                read_graph(path)
            path.write_text('a b\nc d\ne\n')
            labels, edges = read_graph(path)
            self.assertEqual((len(labels), len(edges)), (5, 2))


if __name__ == '__main__':
    unittest.main()
