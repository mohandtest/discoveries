"""Benchmark: paired-chain annealing counter vs exact subset DP.

Graph families: chordless cycles, ladders, complete graphs, random G(n,p),
and a barbell (two cliques + one bridge edge) as a mixing bottleneck test.
"""
import math
import random
import sys
import time

sys.path.insert(0, ".")
from exact import (bits_to_adj, count_perfect_matchings, cycle_count,
                   double_factorial, ladder_count)
from anneal import anneal_count


def graph_cycle(n):
    return [(i, (i + 1) % n) for i in range(n)]


def graph_ladder(m):
    edges = []
    for i in range(m):
        edges.append((2 * i, 2 * i + 1))
        if i + 1 < m:
            edges.append((2 * i, 2 * i + 2))
            edges.append((2 * i + 1, 2 * i + 3))
    return edges


def graph_barbell(half):
    """Two K_half cliques joined by one bridge edge, n = 2*half."""
    edges = []
    L = list(range(half))
    R = list(range(half, 2 * half))
    for s in (L, R):
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                edges.append((s[i], s[j]))
    edges.append((L[0], R[0]))
    return edges


def graph_random(n, p, seed):
    rng = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]


def run_case(name, edges, n, exact, **kw):
    t0 = time.time()
    res = anneal_count(edges, n, **kw)
    dt = time.time() - t0
    mean, se = res["mean"], res["se"]
    rel = abs(mean - exact) / exact if exact else float("nan")
    relse = se / mean if mean else float("nan")
    print(f"{name:28s} n={n:3d} exact={exact:>12.0f} est={mean:>14.0f} "
          f"rel.err={rel:8.3f} (SE={relse:6.3f}) stages={res['diag']['stages']:5d} "
          f"steps/rep={res['diag']['steps_per_replica']:8d} t={dt:6.1f}s")
    return {"name": name, "n": n, "exact": exact, "est": mean, "se": se,
            "rel_err": rel, "rel_se": relse, "time": dt, **res["diag"]}


def main():
    eps = 0.25
    cases = []
    cases.append(("K_8", graph_random(8, 1.0, 0), 8, double_factorial(8)))
    cases.append(("K_12", graph_random(12, 1.0, 0), 12, double_factorial(12)))
    cases.append(("C_6", graph_cycle(6), 6, cycle_count(6)))
    cases.append(("C_10", graph_cycle(10), 10, cycle_count(10)))
    cases.append(("C_14", graph_cycle(14), 14, cycle_count(14)))
    for m in (4, 6, 8):
        cases.append((f"Ladder_2x{m}", graph_ladder(m), 2 * m, ladder_count(m)))
    cases.append(("Barbell_K6+K6", graph_barbell(6), 12,
                  double_factorial(6) ** 2 + 1))
    for (n, p) in ((8, 0.3), (12, 0.3), (12, 0.5), (16, 0.3), (16, 0.5), (20, 0.5)):
        seed = 100 * n + int(100 * p)
        edges = graph_random(n, p, seed)
        exact = count_perfect_matchings(bits_to_adj(edges, n), n)
        while exact == 0:                     # ensure existence
            seed += 1
            edges = graph_random(n, p, seed)
            exact = count_perfect_matchings(bits_to_adj(edges, n), n)
        cases.append((f"G({n},{p})", edges, n, exact))

    rows = []
    print(f"{'case':28s}        exact           est   rel.err           "
          f"params                        time")
    for name, edges, n, exact in cases:
        rows.append(run_case(name, edges, n, exact, eps=eps, samples=256,
                             burn=64, replicas=8, seed=42))

    import csv
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\nresults.csv written")


if __name__ == "__main__":
    main()
