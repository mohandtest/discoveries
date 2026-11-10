"""Full-hierarchy chain (paper structure) vs single-pair annealing."""
import sys
import time

sys.path.insert(0, ".")
from exact import ladder_count
from anneal import anneal_count
from hierarchy import anneal_hierarchy
from bench import graph_cycle, graph_ladder, graph_random


def main():
    cases = [
        ("C_18", graph_cycle(18), 18, 2),
        ("C_20", graph_cycle(20), 20, 2),
        ("Ladder_2x8", graph_ladder(8), 16, ladder_count(8)),
    ]
    edges = graph_random(16, 0.3, 555)
    ex = count_perfect_matchings = None
    from exact import count_perfect_matchings, bits_to_adj
    ex = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    while ex == 0:
        edges = graph_random(16, 0.3, 556)
        ex = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    cases.append(("G(16,0.3)", edges, 16, ex))

    print(f"{'case':12s} {'method':14s} {'est':>10s} {'SE':>8s} {'exact':>8s} "
          f"{'rel.err':>8s} {'t':>7s}")
    for name, edges, n, exact in cases:
        t0 = time.time()
        r = anneal_count(edges, n, eps=0.25, samples=1024, burn=1024,
                         replicas=4, seed=41)
        print(f"{name:12s} {'single':14s} {r['mean']:10.2f} {r['se']:8.2f} "
              f"{exact:8d} {abs(r['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}")
        t0 = time.time()
        r = anneal_hierarchy(edges, n, q=2, eps=0.25, steps=1500000,
                             replicas=4, seed=41)
        print(f"{name:12s} {'hierarchy':14s} {r['mean']:10.2f} {r['se']:8.2f} "
              f"{exact:8d} {abs(r['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}"
              f"  (min stage mean {r['diag']['min_stage_mean']:.3f})")


if __name__ == "__main__":
    main()
