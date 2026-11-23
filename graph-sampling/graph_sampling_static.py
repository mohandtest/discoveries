"""Static graph-sampling bounds and tight-cut factorization.

No Monte Carlo, graph enumeration, sampler execution or benchmarks.
Conditional on Short (2026), Sharp spectral gaps for the switch and
Curveball chains on every graphical degree sequence (Zenodo 23295359).
See STATIC_GUARANTEES.md for derivations, kernel conventions and caveats.
"""
from fractions import Fraction
from math import comb, isqrt, prod, log, ceil
import argparse
import json


def C(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def read_degrees(path):
    degrees, edges = {}, set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = line.split("#", 1)[0].split()
            if not row:
                continue
            if len(row) not in (1, 2):
                raise ValueError("expected one vertex or two endpoints")
            for u in row:
                degrees.setdefault(u, 0)
            if len(row) == 2:
                e = tuple(sorted(row))
                if e[0] == e[1] or e in edges:
                    raise ValueError("input must be a simple graph")
                edges.add(e)
                for u in e:
                    degrees[u] += 1
    return list(degrees), list(degrees.values())


def graphical(d):
    a = sorted(d, reverse=True)
    n = len(a)
    return (
        all(isinstance(x, int) and 0 <= x < n for x in a)
        and sum(a) % 2 == 0
        and all(
            sum(a[:k]) <= k * (k - 1) + sum(min(k, x) for x in a[k:])
            for k in range(1, n + 1)
        )
    )


def tight_cuts(d):
    a = sorted(d, reverse=True)
    return [
        k for k in range(1, len(a))
        if sum(a[:k]) == k * (k - 1) + sum(min(k, x) for x in a[k:])
    ]


def state_upper(d):
    n = len(d)
    m = sum(d) // 2
    if n == 0:
        return 1
    # Shearer's inequality and the bound from choosing m edges.
    return min(C(C(n, 2), m), isqrt(prod(C(n - 1, x) for x in d)))


def certificate(relax, states, eps):
    # sqrt(states)*exp(-t/relax)/2 <= eps. Use exp(-k) <= 2**(-k).
    if states <= 1:
        return 0
    p, q = eps.numerator, eps.denominator
    target, scale = states * q * q, 4 * p * p
    k = max(0, (target.bit_length() - scale.bit_length()) // 2)
    while (scale << (2 * k)) < target:
        k += 1
    while k and (scale << (2 * (k - 1))) >= target:
        k -= 1
    return ceil(Fraction(relax) * k)


def summarize(relax, states, eps):
    if states <= 1:
        return {
            "relaxation_upper": 0,
            "integer_certificate": 0,
            "log_bound_estimate": 0,
        }
    estimate = max(0, ceil(float(relax) * (log(states) / 2 - log(2 * float(eps)))))
    return {
        "relaxation_upper": str(relax),
        "integer_certificate": certificate(relax, states, eps),
        "log_bound_estimate": estimate,
    }


def analysis(d, eps=Fraction(1, 4)):
    if not graphical(d):
        raise ValueError("nongraphical degree vector")
    if not 0 < eps < 1:
        raise ValueError("epsilon must be in (0,1)")
    n, m = len(d), sum(d) // 2
    S = state_upper(d)
    comp = [n - 1 - x for x in d]
    mc = C(n, 2) - m
    D = C(m, 2) - sum(C(x, 2) for x in d)
    Dc = C(mc, 2) - sum(C(x, 2) for x in comp)
    # Necessary conditions for two nonempty exclusive neighborhoods.
    A = sum(
        1 for i in range(n) for j in range(i + 1, n)
        if 0 < d[i] < n - 1 and 0 < d[j] < n - 1
        and abs(d[i] - d[j]) <= n - 4
    )
    if D == 0 or Dc == 0 or A == 0:
        S = 1  # No possible switch; connectivity implies a unique realization.
    return {
        "n": n,
        "m": m,
        "epsilon": str(eps),
        "disjoint_pairs": D,
        "complement_disjoint_pairs": Dc,
        "disjoint_representation": "graph" if D <= Dc else "complement",
        "active_pair_upper": A,
        "tight_cuts": tight_cuts(d),
        "log_state_upper": log(S),
        "published_2n8_at_tv_quarter": 2 * n**8,
        "quadruple": summarize(6 * C(n, 4), S, eps),
        "lazy_edge": summarize(m * (m - 1), S, eps),
        "lazy_disjoint": summarize(2 * min(D, Dc), S, eps),
        "pruned_curveball": summarize(Fraction(A, 2), S, eps),
        "quadruple_to_lazy_disjoint_clock_factor": (
            str(Fraction(3 * C(n, 4), min(D, Dc)))
            if min(D, Dc) > 0 else None
        ),
    }


def split_factors(d):
    """Describe tight Erdős–Gallai splits without enumerating realizations.

    Labels are original zero-based indices. Every split specifies the
    forced clique and joins, an independent low-degree set, bipartite
    row/column margins, and a recursively factorable residual graph.
    """
    if not graphical(d):
        raise ValueError("nongraphical degree vector")

    def rec(items):
        items = sorted(items, key=lambda p: (-p[1], p[0]))
        a = [v for _, v in items]
        cuts = tight_cuts(a)
        if not cuts:
            return {"kind": "simple", "labels": [u for u, _ in items], "degrees": a}
        k = cuts[0]
        left = items[:k]
        high = [p for p in items[k:] if p[1] >= k]
        low = [p for p in items[k:] if p[1] < k]
        return {
            "kind": "split",
            "clique": [u for u, _ in left],
            "joined_to_clique": [u for u, _ in high],
            "independent": [u for u, _ in low],
            "bipartite_rows": [v - (k - 1) - len(high) for _, v in left],
            "bipartite_cols": [v for _, v in low],
            "residual": rec([(u, v - k) for u, v in high]),
        }

    return rec(list(enumerate(d)))


DATA = {
    "dolphins": {1: 9, 2: 6, 3: 6, 4: 5, 5: 8, 6: 8, 7: 7, 8: 4, 9: 4, 10: 2, 11: 2, 12: 1},
    "karate": {1: 1, 2: 11, 3: 6, 4: 6, 5: 3, 6: 2, 9: 1, 10: 1, 12: 1, 16: 1, 17: 1},
    "florentine": {1: 4, 2: 2, 3: 6, 4: 2, 6: 1},
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group()
    source.add_argument("--edges")
    source.add_argument("--degrees", type=int, nargs="+")
    p.add_argument("--epsilon", default="1/4")
    a = p.parse_args()
    eps = Fraction(a.epsilon)
    if a.edges or a.degrees:
        labels, d = read_degrees(a.edges) if a.edges else (list(range(len(a.degrees))), a.degrees)
        print(json.dumps({
            "labels_by_index": labels,
            "bounds": analysis(d, eps),
            "factorization": split_factors(d),
        }, indent=2))
    else:
        for name, counts in DATA.items():
            d = [k for k, v in counts.items() for _ in range(v)]
            print(name, json.dumps(analysis(d, eps), indent=2))


if __name__ == "__main__":
    main()
