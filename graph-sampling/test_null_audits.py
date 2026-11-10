"""Independent small-instance checks for the null-model audits."""
import contextlib
import io
import unittest

from degree_switch_probe import make_index
from heterogeneous_audit import audit, enumerate_degrees
from triangle_null_study import study


class NullAuditTests(unittest.TestCase):
    def test_triangle_null_probabilities(self):
        with contextlib.redirect_stdout(io.StringIO()):
            uniform, jump = study()
        self.assertAlmostEqual(uniform, 1 / 7)
        self.assertAlmostEqual(jump, 1 / 5)

    def test_heterogeneous_exact_graphs(self):
        self.assertEqual(audit([3, 3, 2, 2, 1, 1]), (17, {0: 6, 1: 10, 2: 1}))
        self.assertEqual(audit([3, 2, 2, 1, 1, 1]), (15, {0: 12, 1: 3}))

    def test_empty_and_impossible(self):
        self.assertEqual(enumerate_degrees([0, 0, 0, 0], make_index(4)), [0])
        self.assertEqual(enumerate_degrees([3, 0, 0, 0], make_index(4)), [])
        with self.assertRaises(ValueError):
            enumerate_degrees([4, 0, 0, 0], make_index(4))


if __name__ == '__main__':
    unittest.main()
