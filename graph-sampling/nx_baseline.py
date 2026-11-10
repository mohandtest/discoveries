"""Run actual NetworkX 3.5 swap code for a fixed number of loop iterations.

The public API stops on successes, which samples a different (jump-chain)
distribution. A line tracer stops BEFORE the next proposal loop iteration.
Includes early-continue rejections that NetworkX's max_tries does not count.
Instrumentation overhead makes these timings unsuitable for speed claims.
"""
import inspect
import random
import sys


class _BudgetComplete(Exception):
    pass


class NetworkXChain:
    def __init__(self, n, edges, seed):
        import networkx as nx
        if nx.__version__ != '3.5':
            raise RuntimeError('baseline is audited for networkx==3.5 only')
        self.nx = nx
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(n))
        self.graph.add_edges_from(edges)
        self.rng = random.Random(seed)
        self.function = inspect.unwrap(nx.double_edge_swap)
        lines, start = inspect.getsourcelines(self.function)
        matches = [start+i for i, line in enumerate(lines) if line.strip() == 'while swapcount < nswap:']
        if len(matches) != 1:
            raise RuntimeError('unrecognized NetworkX source')
        self.loop_line = matches[0]

    def advance(self, budget):
        if budget == 0:
            return 0
        if sys.gettrace() is not None:
            raise RuntimeError('baseline requires no existing Python tracer')
        attempts, accepted = 0, 0

        def trace(frame, event, arg):
            nonlocal attempts, accepted
            if frame.f_code is self.function.__code__:
                if event == 'line' and frame.f_lineno == self.loop_line:
                    accepted = frame.f_locals['swapcount']
                    if attempts == budget:
                        raise _BudgetComplete
                    attempts += 1
                return trace
            return None

        try:
            sys.settrace(trace)
            self.nx.double_edge_swap(self.graph, nswap=budget+1, max_tries=budget+1, seed=self.rng)
        except _BudgetComplete:
            pass
        finally:
            sys.settrace(None)
        assert attempts == budget
        return accepted

    def adjacency(self):
        return [set(self.graph[u]) for u in range(len(self.graph))]
