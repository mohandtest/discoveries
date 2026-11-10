"""Unit tests for the chain and counter machinery."""
import math
import random
import sys

sys.path.insert(0, ".")
from chain import PairedChain
from exact import count_perfect_matchings, double_factorial, ladder_count, bits_to_adj


def test_dp_closed_forms():
    for n in (4, 6, 8, 10):
        adj = [(1 << n) - 1 - (1 << i) for i in range(n)]
        assert count_perfect_matchings(adj, n) == double_factorial(n), n
    for m in (2, 3, 4, 5, 6, 7):
        edges = []
        for i in range(m):
            edges.append((2 * i, 2 * i + 1))
            if i + 1 < m:
                edges.append((2 * i, 2 * i + 2))
                edges.append((2 * i + 1, 2 * i + 3))
        adj = bits_to_adj(edges, 2 * m)
        assert count_perfect_matchings(adj, 2 * m) == ladder_count(m), m
    print("DP matches closed forms (K_n, ladders)")


def test_stationarity_tiny():
    """On K_4 with asymmetric-ish weights, empirical law of M1 should match pi."""
    n = 4
    rng = random.Random(7)
    W = [[1.0] * n for _ in range(n)]
    W[0][1] = W[1][0] = 2.0
    W[2][3] = W[3][2] = 0.5
    W[0][2] = W[2][0] = 1.5
    W[1][3] = W[3][1] = 0.8
    # exact pi over 3 matchings of K_4
    matchings = {(1, 0, 3, 2): W[0][1] * W[2][3],
                 (2, 3, 0, 1): W[0][2] * W[1][3],
                 (3, 2, 1, 0): W[0][3] * W[1][2]}
    Z = sum(matchings.values())
    # canonical key: sorted edge list
    def key(M):
        return tuple(sorted((min(i, M[i]), max(i, M[i])) for i in range(n) if M[i] > i))
    exact = {key(k): v / Z for k, v in matchings.items()}
    ch = PairedChain(n, W, random.Random(1))
    counts = {k: 0 for k in exact}
    N = 200000
    for t in range(N):
        ch.step()
        if t > 20000:
            counts[key(ch.M1)] += 1
    tv = 0.5 * sum(abs(counts[k] / (N - 20000) - exact[k]) for k in exact)
    assert tv < 0.02, tv
    print(f"stationarity on weighted K_4: TV = {tv:.4f} (< 0.02)")


def test_cycle_exchange_C6():
    """Chordless 6-cycle: two-edge switches alone cannot leave matching {01,23,45};
    the cycle-exchange branch must reach {12,34,50} in one step."""
    n = 6
    W = [[0.01] * n for _ in range(n)]     # noncycle edges tiny
    for i in range(6):
        W[i][(i + 1) % 6] = W[(i + 1) % 6][i] = 1.0
    rng = random.Random(3)
    ch = PairedChain(n, W, rng)
    ch.M1 = [1, 0, 3, 2, 5, 4]             # {01,23,45}
    ch.M2 = [5, 2, 1, 4, 3, 0]             # {12,34,50}
    cycs = ch.discrepancy_cycles()
    assert len(cycs) == 1 and len(cycs[0]) == 6, cycs
    ch._cycle_exchange(cycs[0])
    # M1 must now carry M2's old pattern {12,34,50}; M2 must carry {01,23,45}
    assert ch.M1 == [5, 2, 1, 4, 3, 0], ch.M1
    assert ch.M2 == [1, 0, 3, 2, 5, 4], ch.M2
    print("cycle exchange on C_6 works and is a pattern swap")


def test_exchange_preserves_product():
    n = 8
    rng = random.Random(11)
    W = [[rng.uniform(0.1, 5.0) if i < j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i):
            W[i][j] = W[j][i]
    ch = PairedChain(n, W, rng)
    for _ in range(200):
        before = ch.weight(ch.M1) * ch.weight(ch.M2)
        ex_before = ch.exchanges
        ch.step()
        after = ch.weight(ch.M1) * ch.weight(ch.M2)
        if ch.exchanges > ex_before:   # a cycle exchange happened this step
            assert math.isclose(before, after, rel_tol=1e-9), (before, after)
    print("cycle exchanges preserve w(M1)*w(M2) exactly over 200 steps")


if __name__ == "__main__":
    test_dp_closed_forms()
    test_stationarity_tiny()
    test_cycle_exchange_C6()
    test_exchange_preserves_product()
    print("ALL TESTS PASSED")
