#!/usr/bin/env python3
"""Experimental fixed-degree triangle null model for simple undirected graphs.

One edge per line: two whitespace-separated node labels. A single label on a
line declares an isolated vertex. Blank lines and # comments are ignored.
Rejected proposals count as steps. Supports multiple independently seeded
chains; convergence is not guaranteed. Standard library only.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path


def read_graph(path):
    nodes, edges = set(), set()
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        if len(fields) not in (1, 2):
            raise ValueError(f'line {number}: expected one node or two node labels')
        nodes.update(fields)
        if len(fields) == 2:
            u, v = fields
            if u == v:
                raise ValueError(f'line {number}: self-loop')
            edge = tuple(sorted((u, v)))
            if edge in edges:
                raise ValueError(f'line {number}: duplicate undirected edge')
            edges.add(edge)
    if len(nodes) < 4 or len(edges) < 2:
        raise ValueError('need at least four nodes and two edges')
    labels = sorted(nodes)
    ids = {name: i for i, name in enumerate(labels)}
    return labels, sorted((ids[u], ids[v]) for u, v in edges)


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def triangle_count(adj):
    return sum(len(adj[u] & adj[v]) for u in range(len(adj)) for v in adj[u] if u < v) // 3


def attempt(edges, adj, rng):
    # Uniform unordered edge pair and one of two rewirings. Every transition
    # has the same probability as its inverse, because edge count is fixed.
    i, j = rng.sample(range(len(edges)), 2)
    a, b = edges[i]
    c, d = edges[j]
    if len({a, b, c, d}) < 4:
        return False
    if rng.randrange(2):
        c, d = d, c
    if c in adj[a] or d in adj[b]:
        return False
    adj[a].remove(b); adj[b].remove(a)
    adj[c].remove(d); adj[d].remove(c)
    adj[a].add(c); adj[c].add(a)
    adj[b].add(d); adj[d].add(b)
    edges[i] = tuple(sorted((a, c)))
    edges[j] = tuple(sorted((b, d)))
    return True


def run_chain(n, initial_edges, burn, samples, thin, seed):
    edges = list(initial_edges)
    adj = adjacency(n, edges)
    expected = [len(x) for x in adj]
    rng = random.Random(seed)
    accepted = 0
    for _ in range(burn):
        accepted += attempt(edges, adj, rng)
    result = []
    for _ in range(samples):
        for _ in range(thin):
            accepted += attempt(edges, adj, rng)
        result.append(triangle_count(adj))
    assert [len(x) for x in adj] == expected
    return result, accepted


def rhat(chains):
    # Basic between/within-chain R-hat is a warning indicator, not proof.
    m, n = len(chains), len(chains[0])
    means = [statistics.mean(c) for c in chains]
    within = statistics.mean(statistics.variance(c) for c in chains)
    between = n * statistics.variance(means)
    if within == 0:
        return None
    return math.sqrt(((n - 1) * within / n + between / n) / within)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('edge_list')
    p.add_argument('--chains', type=int, default=8)
    p.add_argument('--burn', type=int, default=20000, help='attempted proposals per chain')
    p.add_argument('--samples', type=int, default=200, help='samples per chain')
    p.add_argument('--thin', type=int, default=200, help='attempted proposals between samples')
    p.add_argument('--seed', type=int, default=20261110)
    p.add_argument('--csv', help='write sampled triangle counts to this new file')
    a = p.parse_args()
    if a.chains < 2 or a.samples < 2 or a.burn < 0 or a.thin < 1:
        p.error('require at least 2 chains and samples, burn >= 0 and thin >= 1')
    if a.csv and Path(a.csv).exists():
        p.error('CSV output already exists; choose a new path')
    try:
        labels, edges = read_graph(a.edge_list)
    except (OSError, ValueError) as e:
        p.error(str(e))
    observed = triangle_count(adjacency(len(labels), edges))
    chains, accepted = [], []
    for c in range(a.chains):
        values, moves = run_chain(len(labels), edges, a.burn, a.samples, a.thin, a.seed + c)
        chains.append(values); accepted.append(moves)
    chain_means = [statistics.mean(c) for c in chains]
    chain_tails = [sum(v >= observed for v in c) / len(c) for c in chains]
    se = statistics.stdev(chain_means) / math.sqrt(a.chains)
    tail_se = statistics.stdev(chain_tails) / math.sqrt(a.chains)
    report = {
        'input': a.edge_list,
        'input_sha256': hashlib.sha256(Path(a.edge_list).read_bytes()).hexdigest(),
        'nodes': len(labels), 'edges': len(edges), 'observed_triangles': observed,
        'chains': a.chains, 'burn_attempts': a.burn, 'samples_per_chain': a.samples,
        'spacing_attempts': a.thin, 'seeds': [a.seed + c for c in range(a.chains)],
        'acceptance_fraction_per_chain': [x / (a.burn + a.samples * a.thin) for x in accepted],
        'mean_null_triangles': statistics.mean(chain_means),
        'between_chain_mc_se_mean': se,
        'observed_or_higher_tail_fraction': statistics.mean(chain_tails),
        'between_chain_mc_se_tail': tail_se,
        'triangle_rhat_warning_indicator': rhat(chains),
        'null_range': [min(map(min, chains)), max(map(max, chains))],
        'warning': 'Exploratory MCMC estimates; common starting graph, no proven burn-in or mixing. SE excludes bias. Zero tail hits is not zero probability. Connectivity is not preserved.'
    }
    if a.csv:
        with open(a.csv, 'x', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['chain', 'seed', 'sample', 'triangles'])
            for i, chain in enumerate(chains):
                for j, value in enumerate(chain):
                    writer.writerow([i, a.seed+i, j, value])
    json.dump(report, sys.stdout, indent=2, allow_nan=False)
    print()


if __name__ == '__main__':
    main()
