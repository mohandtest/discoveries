"""Exact perfect-matching counter via memoized lowest-unmatched-vertex DP.

Key property (credit: external reviewer, 2026): the recursion only visits
*reachable* subsets — those obtainable by repeatedly removing the lowest
remaining vertex and a partner — which is a tiny fraction of the 2^n bound
(e.g. 61,233 states for G(24,0.5), vs 8.4M even subsets). This makes exact
counting feasible far beyond what a full-table DP allows.
"""
import sys


def exact_count_reachable(adj):
    """adj: list of n bitmask neighbor sets. Returns (count, states_visited)."""
    n = len(adj)
    memo = {0: 1}
    states = 0

    def f(S):
        nonlocal states
        v = memo.get(S)
        if v is not None:
            return v
        states += 1
        low = (S & -S).bit_length() - 1
        m = adj[low] & (S ^ (1 << low))
        tot = 0
        while m:
            j = m & -m
            tot += f(S ^ (1 << low) ^ j)
            m ^= j
        memo[S] = tot
        return tot

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, 4 * n + 1000))
    try:
        return f((1 << n) - 1), states
    finally:
        sys.setrecursionlimit(old)
