"""Final validation sweep of the practical winner: single-pair annealing with
the paper's kernel (burn=1024, samples=1024, 8 replicas)."""
import sys
import time

sys.path.insert(0, ".")
from exact import bits_to_adj, count_perfect_matchings, ladder_count
from anneal import anneal_count
from bench import graph_cycle, graph_ladder, graph_random


def main():
    cases = [("C_24", graph_cycle(24), 24, 2)]
    edges = graph_ladder(12)
    cases.append(("Ladder_2x12", edges, 24, ladder_count(12)))
    edges = graph_random(20, 0.25, 31337)
    ex = count_perfect_matchings(bits_to_adj(edges, 20), 20)
    while ex == 0:
        edges = graph_random(20, 0.25, 31338)
        ex = count_perfect_matchings(bits_to_adj(edges, 20), 20)
    cases.append(("G(20,0.25)", edges, 20, ex))
    edges = graph_random(24, 0.5, 4711)
    cases.append(("G(24,0.5)", edges, 24, None))   # beyond cheap DP check here
    # C_30, C_40: internal consistency (two independent runs)
    cases.append(("C_30", graph_cycle(30), 30, 2))
    cases.append(("C_40", graph_cycle(40), 40, 2))

    print(f"{'case':12s} {'est':>12s} {'SE':>10s} {'exact':>10s} {'rel.err':>8s} {'t':>7s}")
    for name, edges, n, exact in cases:
        t0 = time.time()
        r1 = anneal_count(edges, n, eps=0.25, samples=1024, burn=1024,
                          replicas=8, seed=101)
        if exact is None:
            r2 = anneal_count(edges, n, eps=0.25, samples=1024, burn=1024,
                              replicas=8, seed=202)
            spread = abs(r1["mean"] - r2["mean"]) / r1["mean"]
            print(f"{name:12s} {r1['mean']:12.0f} {r1['se']:10.0f} {'n/a':>10s} "
                  f"{'-':>8s} {time.time()-t0:7.1f}s   run2={r2['mean']:.0f} "
                  f"(SE {r2['se']:.0f}) spread={spread:.3f}")
        else:
            print(f"{name:12s} {r1['mean']:12.2f} {r1['se']:10.2f} {exact:10d} "
                  f"{abs(r1['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}s")


if __name__ == "__main__":
    main()
