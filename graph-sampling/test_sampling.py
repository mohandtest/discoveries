"""Regression tests for the small-graph degree-switch sampler."""
import random
import unittest
from collections import deque

from degree_switch_probe import (degree_sequence, enumerate_regular, make_index,
                                 neighbors, sample_step)
from exact_mixing import exact_tv_curve


class DegreeSwitchTests(unittest.TestCase):
    def test_small_known_counts(self):
        self.assertEqual(len(enumerate_regular(4, 1, make_index(4))), 3)
        self.assertEqual(len(enumerate_regular(6, 2, make_index(6))), 70)
        self.assertEqual(len(enumerate_regular(8, 2, make_index(8))), 3507)

    def test_reversible_and_connected_small(self):
        n, d = 6, 2
        index = make_index(n)
        states = enumerate_regular(n, d, index)
        valid = set(states)
        links = {s: neighbors(s, n, index) for s in states}
        for state, adj in links.items():
            self.assertTrue(adj <= valid)
            for other in adj:
                self.assertIn(state, links[other])
        reached = {states[0]}
        queue = deque([states[0]])
        while queue:
            for nxt in links[queue.popleft()]:
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)
        self.assertEqual(reached, valid)

    def test_degree_invariant(self):
        n, d = 8, 2
        index = make_index(n)
        state = enumerate_regular(n, d, index)[0]
        rng = random.Random(42)
        for _ in range(20000):
            state = sample_step(state, n, index, rng)
            self.assertEqual(degree_sequence(state, n, index), [d] * n)

    def test_exact_tv_decreases(self):
        size, tv = exact_tv_curve(6, 2, (0, 100, 1000))
        self.assertEqual(size, 70)
        self.assertAlmostEqual(tv[0], 69 / 70)
        self.assertGreater(tv[0], tv[100])
        self.assertGreater(tv[100], tv[1000])


if __name__ == '__main__':
    unittest.main()
