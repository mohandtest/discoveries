#!/usr/bin/env python3
"""Local audit for a lazy degree-preserving switch chain, motivated by
OpenAI/math result family 131. Python 3 standard library only.

Enumerate ALL labeled simple d-regular graphs on n vertices (small n),
verify switch-chain connectivity and transition symmetry, and measure the
empirical distance of the sampler from the exact uniform distribution.

Use only n=4..8 for exhaustive enumeration; n>=9 may become expensive.
"""
import argparse
import itertools
import random
import time
from collections import Counter, deque


def make_index(n):
    return {(u, v): k for k, (u, v) in enumerate(itertools.combinations(range(n), 2))}


def bit(index, u, v):
    if u > v:
        u, v = v, u
    return 1 << index[u, v]


def enumerate_regular(n, d, index):
    """Each labeled simple graph is produced once, using forward edges only."""
    remaining = [d] * n
    result = []

    def rec(i, mask):
        if i == n:
            if not any(remaining):
                result.append(mask)
            return
        k = remaining[i]
        if k < 0:
            return
        candidates = [j for j in range(i + 1, n) if remaining[j] > 0]
        if k > len(candidates):
            return
        remaining[i] = 0
        for partners in itertools.combinations(candidates, k):
            for j in partners:
                remaining[j] -= 1
            if all(remaining[j] >= 0 for j in partners):
                added = 0
                for j in partners:
                    added |= bit(index, i, j)
                rec(i + 1, mask | added)
            for j in partners:
                remaining[j] += 1
        remaining[i] = k

    rec(0, 0)
    return result


def pairings(index, a, b, c, d):
    return (
        bit(index, a, b) | bit(index, c, d),
        bit(index, a, c) | bit(index, b, d),
        bit(index, a, d) | bit(index, b, c),
    )


def neighbors(mask, n, index):
    """All possible distinct non-hold moves of this lazy switch kernel."""
    out = set()
    for a, b, c, d in itertools.combinations(range(n), 4):
        pp = pairings(index, a, b, c, d)
        for src in range(3):
            if mask & pp[src] != pp[src]:
                continue
            for dst in range(3):
                if src != dst and mask & pp[dst] == 0:
                    out.add(mask ^ pp[src] ^ pp[dst])
    return out


def sample_step(mask, n, index, rng):
    # A 1/2 holding probability makes the chain aperiodic.
    if rng.randrange(2) == 0:
        return mask
    a, b, c, d = sorted(rng.sample(range(n), 4))
    pp = pairings(index, a, b, c, d)
    src = rng.randrange(3)
    dst = (src + 1 + rng.randrange(2)) % 3
    if mask & pp[src] == pp[src] and mask & pp[dst] == 0:
        return mask ^ pp[src] ^ pp[dst]
    return mask


def degree_sequence(mask, n, index):
    deg = [0] * n
    for (u, v), k in index.items():
        if mask >> k & 1:
            deg[u] += 1
            deg[v] += 1
    return deg


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n', type=int, default=6, choices=[4, 5, 6, 7, 8])
    p.add_argument('--degree', '-d', type=int, default=2)
    p.add_argument('--samples', type=int, default=30000)
    p.add_argument('--burn', type=int, default=10000)
    p.add_argument('--thin', type=int, default=10)
    p.add_argument('--seed', type=int, default=42)
    a = p.parse_args()
    if not 0 <= a.degree < a.n or a.n * a.degree % 2:
        p.error('degree sequence is not feasible: require 0 <= d < n, n*d even')
    if a.samples <= 0 or a.thin <= 0 or a.burn < 0:
        p.error('samples/thin must be positive and burn nonnegative')
    tic = time.perf_counter()
    index = make_index(a.n)
    states = enumerate_regular(a.n, a.degree, index)
    if not states:
        p.error('no graphs realize this degree sequence')
    state_set = set(states)
    # Check every possible switch: it remains valid and is reversible.
    adj = {}
    for s in states:
        ns = neighbors(s, a.n, index)
        assert ns <= state_set, 'transition breaks degree/graph invariants'
        adj[s] = ns
    for s, ns in adj.items():
        for t in ns:
            assert s in adj[t], 'non-reversible proposal'
    visited = {states[0]}
    q = deque([states[0]])
    while q:
        for t in adj[q.popleft()]:
            if t not in visited:
                visited.add(t)
                q.append(t)
    rng = random.Random(a.seed)
    state = states[0]
    counts = Counter()
    move_count = 0
    for step in range(a.burn + a.samples * a.thin):
        next_state = sample_step(state, a.n, index, rng)
        move_count += next_state != state
        state = next_state
        if step >= a.burn and (step - a.burn) % a.thin == 0:
            assert state in state_set and degree_sequence(state, a.n, index) == [a.degree] * a.n
            counts[state] += 1
    uniform = 1.0 / len(states)
    tv = 0.5 * sum(abs(counts[s] / a.samples - uniform) for s in states)
    print('OpenAI/math #131 local switch-chain probe')
    print(f'n={a.n} degree={a.degree} exact labeled graphs={len(states):,}')
    print(f'connected={len(visited) == len(states)} reversible=True')
    print(f'visited in samples={len(counts):,}/{len(states):,}')
    print(f'samples={a.samples:,} burn={a.burn:,} thinning={a.thin}')
    print(f'acceptance incl. holds={move_count/(a.burn+a.samples*a.thin):.4f}')
    print(f'empirical TV distance to uniform={tv:.5f}')
    print(f'wall seconds={time.perf_counter()-tic:.2f}')
    print('Note: empirical TV includes finite-sample noise and is NOT a mixing-time estimate.')


if __name__ == '__main__':
    main()
