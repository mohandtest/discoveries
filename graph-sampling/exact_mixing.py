#!/usr/bin/env python3
"""Exact finite-state mixing calculation for the lazy 4-vertex switch kernel.

For *small* d-regular labeled graphs only. This evolves the entire probability
vector and separates genuine mixing from finite-sample histogram noise.
"""
import argparse
import math
from degree_switch_probe import enumerate_regular, make_index, neighbors


def exact_tv_curve(n=6, degree=2, checkpoints=(0, 10, 100, 1000)):
    if not 4 <= n <= 8 or not (0 <= degree < n) or (n * degree) % 2:
        raise ValueError('require 4 <= n <= 8 and a feasible regular degree')
    checkpoints = sorted(set(checkpoints))
    if not checkpoints or checkpoints[0] < 0:
        raise ValueError('checkpoints must be nonnegative')
    index = make_index(n)
    states = enumerate_regular(n, degree, index)
    if not states:
        raise ValueError('no graphs match requested degree sequence')
    where = {s: i for i, s in enumerate(states)}
    adjacency = [tuple(where[t] for t in neighbors(s, n, index)) for s in states]
    # Each non-hold transition selects four vertices, one of 3 source
    # pairings, one of 2 alternatives, and the 1/2 move coin.
    transition_prob = 1.0 / (12 * math.comb(n, 4))
    size = len(states)
    prob = [0.0] * size
    prob[0] = 1.0
    result = {}
    uniform = 1.0 / size
    check = set(checkpoints)
    if 0 in check:
        result[0] = 0.5 * sum(abs(v - uniform) for v in prob)
    for step in range(1, max(checkpoints) + 1):
        nxt = [0.0] * size
        for i, mass in enumerate(prob):
            if mass == 0.0:
                continue
            links = adjacency[i]
            nxt[i] += mass * (1.0 - transition_prob * len(links))
            for j in links:
                nxt[j] += mass * transition_prob
        prob = nxt
        if step in check:
            result[step] = 0.5 * sum(abs(v - uniform) for v in prob)
    return size, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, default=6)
    parser.add_argument('--degree', type=int, default=2)
    parser.add_argument('--steps', type=int, nargs='+', default=[0, 10, 100, 1000])
    args = parser.parse_args()
    size, tv = exact_tv_curve(args.n, args.degree, args.steps)
    print(f'Exact transition-kernel mixing; n={args.n}, degree={args.degree}, states={size:,}')
    for step, dist in tv.items():
        print(f'steps={step:6d} exact_TV={dist:.8f}')
    print('Not an empirical histogram estimate. Enumerates all labeled states.')


if __name__ == '__main__':
    main()
