"""Follow-up experiments: bias shrinkage, pathological instances, and scaling
beyond exact-DP reach."""
import math
import sys
import time

sys.path.insert(0, ".")
from exact import bits_to_adj, count_perfect_matchings, cycle_count, ladder_count
from anneal import anneal_count
from bench import graph_cycle, graph_ladder, graph_random


def main():
    print("=== 1. Bias check: ladder 2x8 (exact = 34) ===")
    for samples, burn in ((256, 64), (1024, 256), (4096, 1024)):
        r = anneal_count(graph_ladder(8), 16, eps=0.25, samples=samples,
                         burn=burn, replicas=8, seed=7)
        print(f"  samples={samples:5d} burn={burn:5d} est={r['mean']:8.1f} "
              f"SE={r['se']:6.1f} rel.err={abs(r['mean']-34)/34:6.3f}")

    print("\n=== 2. Chordless cycles (Z=2, irreducibility stress) ===")
    for n in (18, 20):
        t0 = time.time()
        r = anneal_count(graph_cycle(n), n, eps=0.25, samples=1024,
                         burn=256, replicas=8, seed=11)
        print(f"  C_{n}: est={r['mean']:6.2f} SE={r['se']:5.2f} "
              f"(exact=2) t={time.time()-t0:5.1f}s")

    print("\n=== 3. Sparse random graphs (rare matchings) ===")
    for (n, p) in ((20, 0.25), (20, 0.3)):
        edges = graph_random(n, p, 777)
        exact = count_perfect_matchings(bits_to_adj(edges, n), n)
        while exact == 0:
            edges = graph_random(n, p, 778)
            exact = count_perfect_matchings(bits_to_adj(edges, n), n)
        t0 = time.time()
        r = anneal_count(edges, n, eps=0.25, samples=1024, burn=256,
                         replicas=8, seed=13)
        print(f"  G({n},{p}): exact={exact:6d} est={r['mean']:8.1f} SE={r['se']:6.1f} "
              f"rel.err={abs(r['mean']-exact)/exact:6.3f} t={time.time()-t0:5.1f}s")

    print("\n=== 4. Beyond exact DP: n = 24, 28, 32 (G(n,0.5)) ===")
    for n in (24, 28, 32):
        t0 = time.time()
        r1 = anneal_count(graph_random(n, 0.5, 999), n, eps=0.25, samples=1024,
                          burn=256, replicas=8, seed=21)
        r2 = anneal_count(graph_random(n, 0.5, 999), n, eps=0.25, samples=1024,
                          burn=256, replicas=8, seed=22)
        spread = abs(r1["mean"] - r2["mean"]) / r1["mean"]
        print(f"  G({n},0.5): run1={r1['mean']:10.0f} (SE {r1['se']:8.0f})  "
              f"run2={r2['mean']:10.0f} (SE {r2['se']:8.0f})  "
              f"rel.spread={spread:5.3f} t={time.time()-t0:5.1f}s")


if __name__ == "__main__":
    main()
