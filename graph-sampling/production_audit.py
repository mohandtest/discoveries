#!/usr/bin/env python3
"""Exact transition matrices of the actual production attempt function."""
import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from degree_switch_probe import make_index
from heterogeneous_audit import enumerate_degrees
from network_null import adjacency, attempt
from observables import measure


class Proposal:
    def __init__(self, i, j, coin):
        self.pair, self.coin = [i, j], coin

    def sample(self, population, k):
        assert k == 2
        return self.pair

    def randrange(self, n):
        assert n == 2
        return self.coin


def state_edges(mask, index):
    return [edge for edge, k in index.items() if mask >> k & 1]


def matrix(degrees):
    n = len(degrees)
    index = make_index(n)
    states = enumerate_degrees(degrees, index)
    lookup = {s:i for i,s in enumerate(states)}
    m = sum(degrees)//2
    rows = []
    for state in states:
        original = state_edges(state, index)
        counts = Counter()
        if m < 2:
            counts[lookup[state]] = 1
            denominator = 1
        else:
            denominator = 2*m*(m-1)
            for i, j in itertools.permutations(range(m), 2):
                for coin in range(2):
                    edges = list(original)
                    adj = adjacency(n, edges)
                    attempt(edges, adj, Proposal(i, j, coin))
                    assert [len(a) for a in adj] == list(degrees)
                    assert adj == adjacency(n, edges) and len(set(edges)) == m
                    target = sum(1 << index[e] for e in edges)
                    counts[lookup[target]] += 1
        rows.append({j: Fraction(c, denominator) for j,c in counts.items()})
    assert all(sum(row.values()) == 1 for row in rows)
    assert all(p == rows[j].get(i, 0) for i,row in enumerate(rows) for j,p in row.items())
    if rows:
        seen, todo = {0}, [0]
        while todo:
            for j in rows[todo.pop()]:
                if j not in seen:
                    seen.add(j); todo.append(j)
        assert len(seen) == len(rows)
    return states, rows, index


def propagate(prob, rows):
    out = [0.0]*len(rows)
    for i, row in enumerate(rows):
        for j, p in row.items():
            out[j] += prob[i]*float(p)
    return out


def study():
    report = []
    for degrees in ([2]*6, [3,3,2,2,1,1], [4,3,3,2,2,2], [3,2,2,1,1,1], [3]*4, [1]*4):
        states, rows, index = matrix(degrees)
        n = len(degrees)
        reference = state_edges(states[0], index)
        metrics = [measure(adjacency(n, state_edges(s,index)),reference) for s in states]
        records = []
        budgets = [0,1,5,10,50,100]
        for start in range(len(states)):
            prob = [float(i==start) for i in range(len(states))]
            for step in range(max(budgets)+1):
                if step in budgets:
                    tv = sum(abs(p-1/len(states)) for p in prob)/2
                    errors = {key: abs(sum(p*(v[key]>=metrics[start][key]) for p,v in zip(prob,metrics)) -
                                       sum(v[key]>=metrics[start][key] for v in metrics)/len(states)) for key in metrics[0]}
                    records.append(dict(start=start, attempts=step, tv=tv, tail_errors=errors))
                prob = propagate(prob,rows)
        report.append(dict(degrees=degrees, states=len(states),
                           triangle_histogram=dict(Counter(v['triangles'] for v in metrics)),
                           transition_rows=[{str(j):str(p) for j,p in row.items()} for row in rows],
                           state_masks=states, records=records))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path, default=Path('results/production_exact.json'))
    path = parser.parse_args().output
    with path.open('x') as f:
        json.dump(study(),f,indent=2)
        f.write('\n')
