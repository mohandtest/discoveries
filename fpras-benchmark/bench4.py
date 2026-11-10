"""Head-to-head: single-pair annealing vs windowed cross-level chain."""
import sys
import time

sys.path.insert(0, ".")
from exact import count_perfect_matchings, bits_to_adj, ladder_count
from anneal import anneal_count
from awindow import anneal_windowed
from bench import graph_cycle, graph_ladder, graph_random


def main():
    cases = [
        ("C_18", graph_cycle(18), 18, 2),
        ("C_20", graph_cycle(20), 20, 2),
        ("Ladder_2x8", graph_ladder(8), 16, ladder_count(8)),
    ]
    edges = graph_random(16, 0.3, 555)
    ex = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    while ex == 0:
        edges = graph_random(16, 0.3, 556)
        ex = count_perfect_matchings(bits_to_adj(edges, 16), 16)
    cases.append(("G(16,0.3)", edges, 16, ex))

    print(f"{'case':12s} {'method':10s} {'est':>10s} {'SE':>8s} {'exact':>8s} "
          f"{'rel.err':>8s} {'t':>7s}")
    for name, edges, n, exact in cases:
        t0 = time.time()
        r = anneal_count(edges, n, eps=0.25, samples=1024, burn=128,
                         replicas=6, seed=41)
        print(f"{name:12s} {'single':10s} {r['mean']:10.2f} {r['se']:8.2f} "
              f"{exact:8d} {abs(r['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}")
        for W_levels in (4, 8):
            t0 = time.time()
            r = anneal_windowed(edges, n, W_levels=W_levels, q=2, eps=0.25,
                                samples=1024, burn=128, replicas=6, seed=41)
            print(f"{name:12s} {'win W='+str(W_levels):10s} {r['mean']:10.2f} "
                  f"{r['se']:8.2f} {exact:8d} {abs(r['mean']-exact)/exact:8.3f} "
                  f"{time.time()-t0:7.1f}")


if __name__ == "__main__":
    main()
