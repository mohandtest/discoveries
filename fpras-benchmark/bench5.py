"""Windowed chain with a compute budget closer to the theory's prescription
(chain length proportional to J), on the pathological cases."""
import sys
import time

sys.path.insert(0, ".")
from exact import ladder_count
from anneal import anneal_count
from awindow import anneal_windowed
from bench import graph_cycle, graph_ladder


def main():
    cases = [
        ("C_18", graph_cycle(18), 18, 2),
        ("C_20", graph_cycle(20), 20, 2),
        ("Ladder_2x8", graph_ladder(8), 16, ladder_count(8)),
    ]
    print(f"{'case':12s} {'method':16s} {'est':>8s} {'SE':>6s} {'exact':>6s} "
          f"{'rel.err':>8s} {'t':>7s}")
    for name, edges, n, exact in cases:
        t0 = time.time()
        r = anneal_count(edges, n, eps=0.25, samples=1024, burn=1024,
                         replicas=4, seed=41)
        print(f"{name:12s} {'single b=1024':16s} {r['mean']:8.2f} {r['se']:6.2f} "
              f"{exact:6d} {abs(r['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}")
        t0 = time.time()
        r = anneal_windowed(edges, n, W_levels=6, q=2, eps=0.25, samples=1024,
                            burn=4096, replicas=4, seed=41, refresh_every=32)
        print(f"{name:12s} {'win W6 q2 b=4k':16s} {r['mean']:8.2f} {r['se']:6.2f} "
              f"{exact:6d} {abs(r['mean']-exact)/exact:8.3f} {time.time()-t0:7.1f}")


if __name__ == "__main__":
    main()
