#!/usr/bin/env python3
"""Quantify the dolphins triangle-null tail (the study's unresolved zero-hit).

Long high-budget runs of the production edge-pair kernel on the dolphins
network (62 nodes, 159 edges, observed 45..95 triangles? -- read from data),
reporting the null triangle distribution: mean, SD, quantiles, empirical
upper-tail counts at the observed value, a distributional summary, and
kernel throughput (attempts/sec). Also runs karate for the contrast row.

Standard library only. Run: python3 dolphins_tail.py [--chains 16]
"""
import argparse
import json
import math
import statistics
import time
from collections import Counter

from network_null import adjacency, read_graph, run_chain, triangle_count


def study(path, label, chains, burn, samples, thin, seed):
    labels_, edges = read_graph(path)
    n, m = len(labels_), len(edges)
    obs = triangle_count(adjacency(n, edges))
    per_chain = []
    t0 = time.perf_counter()
    total_attempts = 0
    for c in range(chains):
        vals, accepted = run_chain(n, edges, burn, samples, thin, seed + c)
        per_chain.append(vals)
        total_attempts += burn + samples * thin
    wall = time.perf_counter() - t0
    draws = [v for chain in per_chain for v in chain]
    mean = statistics.mean(draws)
    sd = statistics.pstdev(draws)
    hits = sum(v >= obs for v in draws)
    quant = statistics.quantiles(draws, n=100)
    lo, hi = min(draws), max(draws)
    z = (obs - mean) / sd if sd else None
    # normal-tail extrapolation, reported with its assumption attached
    if sd:
        from math import erf
        tail_norm = 0.5 * (1 - erf((obs - mean) / (sd * math.sqrt(2))))
    else:
        tail_norm = None
    return {
        'dataset': label, 'input': path, 'nodes': n, 'edges': m,
        'observed_triangles': obs,
        'chains': chains, 'burn_attempts': burn, 'samples_per_chain': samples,
        'thin_attempts': thin, 'seeds': [seed + c for c in range(chains)],
        'draws_total': len(draws),
        'null_mean': round(mean, 4), 'null_sd': round(sd, 4),
        'null_min': lo, 'null_max': hi,
        'null_q50': round(quant[49], 1), 'null_q95': round(quant[94], 1),
        'null_q99': round(quant[98], 1),
        'hits_at_or_above_observed': hits,
        'empirical_tail_bound': round(1.0 / (len(draws) + 1), 8),
        'z_of_observed': round(z, 2) if z is not None else None,
        'normal_tail_extrapolation': tail_norm,
        'normal_tail_note': 'assumes approximate normality of the null '
                            'triangle count; verify against quantiles',
        'attempts_per_second': round(total_attempts / wall, 1),
        'wall_seconds': round(wall, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chains', type=int, default=16)
    ap.add_argument('--burn', type=int, default=500000)
    ap.add_argument('--samples', type=int, default=50000)
    ap.add_argument('--thin', type=int, default=40)
    ap.add_argument('--seed', type=int, default=20261110)
    a = ap.parse_args()
    out = [
        study('data/dolphins.edgelist', 'dolphins', a.chains, a.burn,
              a.samples, a.thin, a.seed),
        study('data/karate.edgelist', 'karate', a.chains, a.burn // 4,
              a.samples // 2, a.thin, a.seed + 1000),
    ]
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
