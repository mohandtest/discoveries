"""Fair head-to-head: FPRAS vs exact (reachable-state DP) on identical graphs.

Motivated by external review: the original benchmark overstated exact-DP
infeasibility (full-table DP visits 2^n subsets; the memoized recursion visits
only reachable states — 61k at n=24). This script saves each graph to an edge
list, runs both counters on the SAME graph, and reports the FPRAS's true
relative error where truth is available.

Cross-validation: G(24,0.5) seed 42 must give 77,137,026 (reviewer's value).
"""
import csv
import os
import random
import sys
import time

sys.path.insert(0, ".")
from exact2 import exact_count_reachable
from anneal import anneal_count


def graph_gnp(n, p, seed):
    rng = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]


def save_edges(edges, n, path):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")


def load_edges(path):
    with open(path) as f:
        records = [line.split("#", 1)[0].strip() for line in f]
    records = [line for line in records if line]
    n, m = map(int, records[0].split())
    assert len(records) - 1 == m
    nbr = [0] * n
    edges = []
    for line in records[1:]:
        u, v = map(int, line.split())
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u
        edges.append((u, v))
    return nbr, edges, m


def main():
    os.makedirs("graphs", exist_ok=True)
    cases = [(24, 0.5, 42), (28, 0.5, 42), (30, 0.5, 42), (32, 0.5, 42)]
    rows = []
    print(f"{'graph':16s} {'exact':>16s} {'exact_t':>8s} {'states':>12s} "
          f"{'fpras':>16s} {'SE':>12s} {'rel.err':>8s} {'fpras_t':>8s}")
    for (n, p, seed) in cases:
        path = f"graphs/g{n}_p{int(p*100)}_s{seed}.edges"
        if not os.path.exists(path):
            save_edges(graph_gnp(n, p, seed), n, path)
        nbr, edges, m = load_edges(path)
        t0 = time.perf_counter()
        exact, states = exact_count_reachable(nbr)
        ex_t = time.perf_counter() - t0
        if n == 24 and seed == 42:
            assert exact == 77_137_026, exact
            print("  [cross-validation vs reviewer: PASS]")
        t0 = time.perf_counter()
        r = anneal_count(edges, n, eps=0.25, samples=1024, burn=1024,
                         replicas=8, seed=909)
        fp_t = time.perf_counter() - t0
        rel = abs(r["mean"] - exact) / exact
        z = (r["mean"] - exact) / r["se"] if r["se"] else float("inf")
        print(f"G({n},{p})        {exact:16,} {ex_t:8.2f} {states:12,} "
              f"{r['mean']:16,.0f} {r['se']:12,.0f} {rel:8.3f} {fp_t:8.1f}  z={z:+.1f}")
        rows.append({"graph": f"G({n},{p},s{seed})", "edges": m, "exact": exact,
                     "exact_states": states, "exact_s": round(ex_t, 3),
                     "fpras": round(r["mean"]), "fpras_se": round(r["se"]),
                     "rel_err": round(rel, 4), "z": round(z, 2),
                     "fpras_s": round(fp_t, 1)})

    with open("results_head_to_head.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\nresults_head_to_head.csv written")


if __name__ == "__main__":
    main()
