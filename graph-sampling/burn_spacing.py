#!/usr/bin/env python3
"""Isolate burn-in from thinning on the real networks (dolphins, karate).

The validation study varied burn and spacing together; this grid holds one
fixed while sweeping the other, measuring bias against a long-run reference
mean and Monte Carlo noise across chains. Standard library only.

Run: python3 burn_spacing.py [--chains 8] [--samples 200]
"""
import argparse
import json
import statistics
import time

from network_null import adjacency, read_graph, run_chain, triangle_count

BURNS = [0, 5_000, 25_000, 125_000]
THINS = [1, 25]


def cell(n, edges, burn, thin, samples, chains, seed):
    per_chain_means = []
    for c in range(chains):
        vals, _ = run_chain(n, edges, burn, samples, thin, seed + c)
        per_chain_means.append(statistics.mean(vals))
    mean = statistics.mean(per_chain_means)
    mcse = (statistics.stdev(per_chain_means) / len(per_chain_means)
            if len(per_chain_means) > 1 else 0.0)
    return mean, mcse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chains', type=int, default=8)
    ap.add_argument('--samples', type=int, default=200)
    ap.add_argument('--seed', type=int, default=20261111)
    a = ap.parse_args()
    out = []
    for path, label, ref in (('data/dolphins.edgelist', 'dolphins', 34.0),
                             ('data/karate.edgelist', 'karate', 39.4)):
        labels_, edges = read_graph(path)
        n = len(labels_)
        obs = triangle_count(adjacency(n, edges))
        for burn in BURNS:
            t0 = time.perf_counter()
            mean, mcse = cell(n, edges, burn, THINS[1], a.samples,
                              a.chains, a.seed + burn)
            wall = time.perf_counter() - t0
            out.append({'dataset': label, 'burn_attempts': burn,
                        'thin_attempts': THINS[1], 'mean_null': round(mean, 3),
                        'bias_vs_ref': round(mean - ref, 3),
                        'between_chain_mcse': round(mcse, 3),
                        'wall_s': round(wall, 1)})
        for thin in THINS:
            t0 = time.perf_counter()
            mean, mcse = cell(n, edges, BURNS[-1], thin, a.samples,
                              a.chains, a.seed + 7000 + thin)
            wall = time.perf_counter() - t0
            out.append({'dataset': label, 'burn_attempts': BURNS[-1],
                        'thin_attempts': thin, 'mean_null': round(mean, 3),
                        'bias_vs_ref': round(mean - ref, 3),
                        'between_chain_mcse': round(mcse, 3),
                        'wall_s': round(wall, 1)})
    print(json.dumps({'reference_means': {'dolphins': 34.0, 'karate': 39.4},
                      'note': 'reference means from the long dolphins_tail '
                              'runs; bias = cell mean - reference',
                      'cells': out}, indent=1))


if __name__ == '__main__':
    main()
