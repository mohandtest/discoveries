"""Replication study: does practical q close the chordless-cycle gap?"""
import sys
import time

sys.path.insert(0, ".")
from exact import count_perfect_matchings, bits_to_adj, ladder_count
from anneal import anneal_count_replicated
from bench import graph_cycle, graph_ladder, graph_random


def main():
    print("=== q-replication study (all at eps=0.25 schedule, 1024 obs/stage) ===")
    for name, edges, n, exact in (
        ("C_18", graph_cycle(18), 18, 2),
        ("C_20", graph_cycle(20), 20, 2),
        ("Ladder_2x8", graph_ladder(8), 16, ladder_count(8)),
    ):
        for q in (2, 8, 32):
            t0 = time.time()
            r = anneal_count_replicated(edges, n, q=q, samples=1024, burn=128,
                                        replicas=6, seed=31)
            rel = abs(r["mean"] - exact) / exact
            print(f"  {name:12s} q={q:3d} est={r['mean']:8.2f} SE={r['se']:6.2f} "
                  f"(exact={exact}) rel.err={rel:6.3f} steps/rep="
                  f"{r['diag']['steps_per_replica']:8d} t={time.time()-t0:6.1f}s")

    print("\n=== sparse graph sanity with q=8 ===")
    edges = graph_random(16, 0.3, 555)
    exact = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    while exact == 0:
        edges = graph_random(16, 0.3, 556)
        exact = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    r = anneal_count_replicated(edges, 16, q=8, samples=1024, burn=128,
                                replicas=6, seed=33)
    print(f"  G(16,0.3): exact={exact} est={r['mean']:.1f} SE={r['se']:.1f} "
          f"rel.err={abs(r['mean']-exact)/exact:.3f}")


if __name__ == "__main__":
    main()
