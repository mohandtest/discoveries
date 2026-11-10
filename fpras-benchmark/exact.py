"""Exact counting of perfect matchings via subset DP, plus closed forms."""
from math import prod


def count_perfect_matchings(adj, n):
    """adj: list of n bitmask neighbor sets. Returns number of perfect matchings.
    DP over even subsets: f[S] = # perfect matchings of induced subgraph on S."""
    size = 1 << n
    f = [0] * size
    f[0] = 1
    for S in range(2, size):
        if bin(S).count("1") & 1:
            continue
        low = (S & -S).bit_length() - 1
        rest = S ^ (1 << low)
        m = adj[low] & rest
        total = 0
        while m:
            j = m & -m
            total += f[S ^ (1 << low) ^ j]
            m ^= j
        f[S] = total
    return f[size - 1]


def double_factorial(n):
    """(n-1)!! = number of perfect matchings of K_n, n even."""
    return prod(range(1, n, 2))


def ladder_count(m):
    """Perfect matchings of the 2 x m ladder graph = Fibonacci(m+1)."""
    a, b = 1, 1
    for _ in range(m):
        a, b = b, a + b
    return a


def cycle_count(n):
    """Perfect matchings of the chordless cycle C_n, n even: exactly 2."""
    assert n % 2 == 0
    return 2


def bits_to_adj(edges, n):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj
