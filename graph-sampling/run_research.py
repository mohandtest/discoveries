#!/usr/bin/env python3
"""Fixed configuration public-data sensitivity study. Serial, local, small graphs.

Run from graph-sampling; results path must be new. See STUDY_REPORT.md.
"""
import argparse
import csv
import hashlib
import inspect
import json
import platform
import random
import statistics
import time
from pathlib import Path
import networkx as nx
from diagnostics import summarize
from network_null import adjacency, attempt, read_graph
from nx_baseline import NetworkXChain
from observables import measure


class ProductionChain:
    def __init__(self,n,edges,seed):
        self.edges = list(edges)
        self.adj = adjacency(n,edges)
        self.rng = random.Random(seed)

    def advance(self,budget):
        return sum(attempt(self.edges,self.adj,self.rng) for _ in range(budget))

    def adjacency(self):
        return self.adj


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--samples',type=int,default=200)
    a = p.parse_args()
    if a.samples < 4:
        p.error('need at least four samples')
    a.output.mkdir(exist_ok=False)
    config = dict(chains=4, samples=a.samples, seed=20261120,
                  budgets=[dict(name='short',burn_sweeps=20,spacing_sweeps=2),
                           dict(name='long',burn_sweeps=80,spacing_sweeps=8)],
                  datasets=['karate','florentine','dolphins'],
                  metrics=['triangles','four_cycles','components','edge_overlap','degree_product'])
    summary = dict(config=config, python=platform.python_version(), networkx=nx.__version__,
                   nx_source_sha256=hashlib.sha256(inspect.getsource(nx.double_edge_swap).encode()).hexdigest(),
                   source_sha256={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in
                                  ['network_null.py','run_research.py','nx_baseline.py','diagnostics.py','observables.py']}, runs=[])
    (a.output/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.output/'samples.csv').open('x',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=['dataset','budget','engine','chain','seed','start','sample','attempts','accepted']+config['metrics'])
        writer.writeheader()
        for di, name in enumerate(config['datasets']):
            path = Path('data')/f'{name}.edgelist'
            labels, observed_edges = read_graph(path)
            n,m = len(labels),len(observed_edges)
            degrees = [len(x) for x in adjacency(n,observed_edges)]
            hh = nx.havel_hakimi_graph(degrees)
            assert [hh.degree(u) for u in range(n)] == degrees
            hh_edges = sorted(tuple(sorted(e)) for e in hh.edges())
            observed = measure(adjacency(n,observed_edges),observed_edges)
            for budget in config['budgets']:
                burn,thin = budget['burn_sweeps']*m,budget['spacing_sweeps']*m
                for engine, cls in [('production',ProductionChain),('networkx',NetworkXChain)]:
                    tic = time.perf_counter()
                    chains, info = [], []
                    for c in range(config['chains']):
                        seed = config['seed']+100*di+c
                        start = 'observed' if c%2==0 else 'havel_hakimi'
                        initial = observed_edges if start=='observed' else hh_edges
                        sampler = cls(n,initial,seed)
                        accepted = sampler.advance(burn)
                        values = []
                        for j in range(a.samples):
                            accepted += sampler.advance(thin)
                            adj = sampler.adjacency()
                            assert [len(x) for x in adj] == degrees
                            metrics = measure(adj,observed_edges)
                            values.append(metrics)
                            writer.writerow(dict(dataset=name,budget=budget['name'],engine=engine,chain=c,seed=seed,
                                                 start=start,sample=j,attempts=burn+(j+1)*thin,accepted=accepted,**metrics))
                        chains.append(values)
                        info.append(dict(seed=seed,start=start,initial=measure(adjacency(n,initial),observed_edges),
                                         attempts=burn+a.samples*thin,accepted=accepted))
                    run = dict(dataset=name,nodes=n,edges=m,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                               budget=budget['name'],engine=engine,burn=burn,thin=thin,chains=info,observed=observed,
                               seconds=time.perf_counter()-tic,
                               statistics={key:summarize([[v[key] for v in chain] for chain in chains],observed[key]) for key in observed})
                    summary['runs'].append(run)
                    print(name,budget['name'],engine,run['statistics']['triangles'],flush=True)
                    (a.output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
