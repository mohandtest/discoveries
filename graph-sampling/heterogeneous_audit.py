#!/usr/bin/env python3
"""Enumerate and audit small, heterogeneous labeled degree sequences.

Uses forward-edge backtracking, checked against an independent exhaustive
enumeration of all edge subsets. Restricted to n <= 6 for the brute-force
check. No external dependencies. Run: python3 heterogeneous_audit.py
"""
import itertools
import math
from collections import deque

from degree_switch_probe import bit, degree_sequence, make_index, neighbors
from triangle_null_study import triangles


def enumerate_degrees(degrees, index):
    n = len(degrees)
    if any(not isinstance(d, int) or d < 0 or d >= n for d in degrees):
        raise ValueError('degrees must be integers between 0 and n-1')
    remaining = list(degrees)
    states = []

    def visit(i, mask):
        if i == n:
            if not any(remaining):
                states.append(mask)
            return
        wanted = remaining[i]
        candidates = [j for j in range(i + 1, n) if remaining[j] > 0]
        if wanted < 0 or wanted > len(candidates):
            return
        remaining[i] = 0
        for chosen in itertools.combinations(candidates, wanted):
            added = 0
            for j in chosen:
                remaining[j] -= 1
                added |= bit(index, i, j)
            visit(i + 1, mask | added)
            for j in chosen:
                remaining[j] += 1
        remaining[i] = wanted

    visit(0, 0)
    return states


def audit(degrees):
    n = len(degrees)
    if not 4 <= n <= 6:
        raise ValueError('audit requires 4 <= n <= 6')
    index = make_index(n)
    states = enumerate_degrees(degrees, index)
    brute = {s for s in range(1 << len(index)) if degree_sequence(s, n, index) == list(degrees)}
    assert len(states) == len(set(states)) and set(states) == brute
    if not states:
        return None
    where = {s: i for i, s in enumerate(states)}
    adjacency = [set(where[t] for t in neighbors(s, n, index)) for s in states]
    assert all(i in adjacency[j] for i, links in enumerate(adjacency) for j in links)
    seen = {0}
    queue = deque([0])
    while queue:
        for j in adjacency[queue.popleft()]:
            if j not in seen:
                seen.add(j)
                queue.append(j)
    assert len(seen) == len(states)
    p = 1 / (12 * math.comb(n, 4))
    assert all(len(links) * p <= 1 for links in adjacency)
    stats = [triangles(s, n, index) for s in states]
    return len(states), {t: stats.count(t) for t in sorted(set(stats))}


if __name__ == '__main__':
    for degrees in ([3, 3, 2, 2, 1, 1], [4, 3, 3, 2, 2, 2], [3, 2, 2, 1, 1, 1]):
        result = audit(degrees)
        print(f'degrees={degrees} states={result[0]} triangle_histogram={result[1]}')
    print('Backtracking matches exhaustive edge subsets; each audited switch graph is symmetric and connected.')
