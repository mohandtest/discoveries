#!/usr/bin/env python3
"""Exact triangle null-model audit for labeled 2-regular graphs on six vertices.

Run: python3 triangle_null_study.py
All distributions are calculated by enumeration and probability propagation,
not Monte Carlo. This is a tiny synthetic example, not an application finding.
"""
import itertools
import math

from degree_switch_probe import bit, enumerate_regular, make_index, neighbors


def triangles(mask, n, index):
    return sum(all(mask & bit(index, u, v) for u, v in itertools.combinations(triple, 2))
               for triple in itertools.combinations(range(n), 3))


def study():
    n, degree = 6, 2
    index = make_index(n)
    states = enumerate_regular(n, degree, index)
    pos = {state: i for i, state in enumerate(states)}
    links = [tuple(pos[t] for t in neighbors(s, n, index)) for s in states]
    stats = [triangles(s, n, index) for s in states]
    # A network of two disjoint triangles is the observed graph.
    start = stats.index(2)
    count = len(states)
    assert count == 70 and stats.count(2) == 10 and stats.count(0) == 60
    assert all(i in links[j] for i, ns in enumerate(links) for j in ns)
    probability = 1 / (12 * math.comb(n, 4))
    assert all(len(ns) * probability <= 1 for ns in links)

    # The uniform target includes holds. Recording *only successful moves*
    # yields a different jump chain, whose stationary mass is proportional to
    # the number of valid neighbors (on this symmetric transition graph).
    weights = [len(ns) for ns in links]
    assert min(weights) > 0
    uniform_tail = stats.count(2) / count
    jump_tail = sum(w for w, t in zip(weights, stats) if t >= 2) / sum(weights)
    print('n=6 degree=2; observed graph: two disjoint triangles')
    print(f'labeled graphs={count}; triangle counts: 0={stats.count(0)}, 2={stats.count(2)}')
    print(f'exact uniform P(triangles >= 2)={uniform_tail:.6f}')
    print(f'successful-moves-only stationary tail={jump_tail:.6f}')
    print('These are exact synthetic null tails, not real-world significance results.')
    print('finite attempted steps, triangle tail from observed start, full-state TV:')

    distribution = [0.0] * count
    distribution[start] = 1.0
    checkpoints = {0, 10, 50, 100, 200, 500}
    for step in range(max(checkpoints) + 1):
        if step in checkpoints:
            tail = sum(p for p, t in zip(distribution, stats) if t >= 2)
            tv = sum(abs(p - 1 / count) for p in distribution) / 2
            print(f'{step:4d}  {tail:.6f}  {tv:.6f}')
        if step == max(checkpoints):
            break
        nxt = [0.0] * count
        for i, mass in enumerate(distribution):
            nxt[i] += mass * (1 - probability * len(links[i]))
            for j in links[i]:
                nxt[j] += mass * probability
        distribution = nxt
    assert abs(sum(distribution) - 1) < 1e-10
    return uniform_tail, jump_tail


if __name__ == '__main__':
    study()
