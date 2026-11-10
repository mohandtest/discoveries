import itertools
import random
import unittest
from collections import Counter
from fractions import Fraction
from diagnostics import batch_ess, split_rhat, summarize
from degree_switch_probe import degree_sequence, make_index
from network_null import adjacency
from observables import measure
from production_audit import matrix, state_edges


class ResearchTests(unittest.TestCase):
    def test_production_exact_matches_independent_edge_subsets(self):
        for degrees in ([2]*6,[3,3,2,2,1,1],[4,3,3,2,2,2],[3,2,2,1,1,1],[3]*4,[1]*4):
            states,rows,index = matrix(degrees)
            brute = {s for s in range(1<<len(index)) if degree_sequence(s,len(degrees),index)==degrees}
            self.assertEqual(set(states),brute)
            # Independent switch graph: all destinations differing by four edges.
            for i,s in enumerate(states):
                expected = {j for j,t in enumerate(states) if (s^t).bit_count()==4}
                self.assertEqual({j for j in rows[i] if j!=i},expected)
            self.assertTrue(all(sum(row.values())==1 for row in rows))

    def test_observables_known_graphs(self):
        cycle = [(0,1),(1,2),(2,3),(0,3)]
        values = measure(adjacency(5,cycle),cycle)
        self.assertEqual(values,dict(triangles=0,four_cycles=1,components=2,edge_overlap=4,degree_product=16))
        clique = list(itertools.combinations(range(4),2))
        self.assertEqual(measure(adjacency(4,clique),clique)['four_cycles'],3)

    def test_diagnostics_constants_and_dependence(self):
        self.assertIsNone(split_rhat([[1]*20]*4))
        self.assertIsNone(batch_ess([1]*100))
        summary = summarize([[0]*20]*4,1)
        self.assertIsNone(summary['mcse_tail'])
        self.assertTrue(summary['zero_tail_variation'])
        rng = random.Random(42)
        iid = [rng.gauss(0,1) for _ in range(400)]
        blocked = [x for x in iid[:20] for _ in range(20)]
        self.assertLess(batch_ess(blocked),batch_ess(iid))

    def test_nx_budget_and_exact_histogram(self):
        try:
            import networkx as nx
        except ImportError:
            self.skipTest('optional networkx research dependency')
        if nx.__version__!='3.5':
            self.skipTest('baseline requires pinned NetworkX 3.5')
        from nx_baseline import NetworkXChain
        edges = [(0,1),(0,2),(1,2),(3,4),(3,5),(4,5)]
        chain = NetworkXChain(6,edges,52)
        self.assertEqual(chain.advance(0),0)
        chain.advance(1000)
        hits = 0
        for _ in range(5000):
            moved = chain.advance(10)
            self.assertTrue(0<=moved<=10)
            adj = chain.adjacency()
            self.assertEqual([len(a) for a in adj],[2]*6)
            hits += measure(adj,edges)['triangles']==2
        self.assertAlmostEqual(hits/5000,1/7,delta=0.025)
        # A frozen graph must stop, even though no swap can succeed.
        frozen = NetworkXChain(4,list(itertools.combinations(range(4),2)),1)
        self.assertEqual(frozen.advance(100),0)

    def test_nx_exact_proposal_probabilities(self):
        """Enumerate actual NX proposals, including early-continue holds.

        NX draws two oriented edges with replacement. Production draws distinct
        edges. Their exact relation is Q = (m-1)/m P + I/m, not Q = P.
        """
        try:
            import networkx as nx
        except ImportError:
            self.skipTest('optional networkx research dependency')
        if nx.__version__ != '3.5':
            self.skipTest('baseline requires pinned NetworkX 3.5')
        from nx_baseline import NetworkXChain

        class FixedProposal(random.Random):
            def __init__(self, source_draws, targets):
                self.source_draws = iter(source_draws)
                self.targets = iter(targets)

            def random(self):
                return next(self.source_draws)

            def choice(self, population):
                target = next(self.targets)
                if target not in population:
                    raise AssertionError('scripted target absent from neighbors')
                return target

        for degrees in ([2]*6, [3,3,2,2,1,1], [3]*4, [1]*4):
            states, rows, index = matrix(degrees)
            m = sum(degrees)//2
            lookup = {state: i for i, state in enumerate(states)}
            prefix = [sum(degrees[:u]) for u in range(len(degrees))]
            for i, state in enumerate(states):
                edges = state_edges(state, index)
                oriented = [edge for u,v in edges for edge in ((u,v),(v,u))]
                counts = Counter()
                for (u,v), (x,y) in itertools.product(oriented, repeat=2):
                    chain = NetworkXChain(len(degrees), edges, 0)
                    # CDF interval midpoints select degree-weighted source
                    # vertices; choice then selects their scripted neighbors.
                    draws = [(prefix[z]+degrees[z]/2)/(2*m) for z in (u,x)]
                    chain.rng = FixedProposal(draws, (v,y))
                    chain.advance(1)
                    mask = sum(1 << index[tuple(sorted(edge))]
                               for edge in chain.graph.edges())
                    counts[lookup[mask]] += 1
                self.assertEqual(sum(counts.values()), 4*m*m)
                for j in range(len(states)):
                    expected = Fraction(m-1,m)*rows[i].get(j,0)
                    if i == j:
                        expected += Fraction(1,m)
                    self.assertEqual(Fraction(counts[j],4*m*m), expected,
                                     (degrees,i,j))


if __name__=='__main__':
    unittest.main()
