#!/usr/bin/env python3
"""Repeated short-chain coverage and false-reassurance experiment with exact truth.

Fixed diagnostic gate: all nonconstant statistic split R-hats <= 1.05;
constant-with-exact-variation statistics fail. This is an oracle-assisted toy gate, since exact variation is known.
Gate uses triangles, four-cycles,
edge overlap and degree product, never exact TV. Coverage uses four independent
chain means and Student-t critical value 3.182446 (3 df); not a guaranteed CI.
"""
import argparse
import csv
import json
import math
import statistics as st
from pathlib import Path
from diagnostics import summarize
from network_null import adjacency
from observables import measure
from production_audit import matrix, propagate, state_edges
from run_research import ProductionChain


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path, default=Path('results/calibration'))
    output = parser.parse_args().output
    output.mkdir(exist_ok=False)
    results = []
    with (output/'raw.csv').open('x',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['case','burn','start','replicate','chain','seed','sample','triangles','four_cycles','edge_overlap','degree_product'])
        for case,degrees in enumerate(([2]*6,[3,3,2,2,1,1],[4,3,3,2,2,2])):
            states, rows, index = matrix(degrees)
            edges = [state_edges(s,index) for s in states]
            reference = edges[0]
            metrics = [measure(adjacency(len(degrees),e),reference) for e in edges]
            truth = st.mean(v['triangles'] for v in metrics)
            # Choose triangle extremes; all four chains share a start, deliberately.
            starts = [min(range(len(states)),key=lambda i:metrics[i]['triangles']),
                      max(range(len(states)),key=lambda i:metrics[i]['triangles'])]
            for burn in [0,5,50]:
                for start in starts:
                    # Distribution averaged over all retained time points, not TV at burn.
                    prob = [float(i==start) for i in range(len(states))]
                    averaged = [0.0]*len(states)
                    for step in range(burn+40+1):
                        if step > burn:
                            averaged = [a+p/40 for a,p in zip(averaged,prob)]
                        prob = propagate(prob,rows)
                    tv = sum(abs(p-1/len(states)) for p in averaged)/2
                    for rep in range(100):
                        chains = []
                        for c in range(4):
                            seed = 900000+10000000*case+10000*burn+1000*start+4*rep+c
                            sampler = ProductionChain(len(degrees),edges[start],seed)
                            sampler.advance(burn)
                            values = []
                            for j in range(40):
                                sampler.advance(1)
                                v = measure(sampler.adjacency(),reference)
                                values.append(v)
                                writer.writerow([case,burn,start,rep,c,seed,j]+[v[k] for k in ['triangles','four_cycles','edge_overlap','degree_product']])
                            chains.append(values)
                        summaries = {k:summarize([[v[k] for v in chain] for chain in chains],metrics[start][k]) for k in ['triangles','four_cycles','edge_overlap','degree_product']}
                        active = [k for k in summaries if len({v[k] for v in metrics})>1]
                        gate = all(summaries[k]['split_rhat'] is not None and summaries[k]['split_rhat']<=1.05 for k in active)
                        t = summaries['triangles']
                        results.append(dict(case=case,degrees=degrees,exact_triangle_mean=truth,burn=burn,start=start,replicate=rep,mean=t['mean'],mcse=t['mcse_mean'],
                                            covered=abs(t['mean']-truth)<=3.182446*t['mcse_mean'], gate_pass=gate,
                                            exact_time_averaged_tv=tv,
                                            rhat={k:v['split_rhat'] for k,v in summaries.items()}))
    summary = dict(config=dict(degree_sequences=[[2]*6,[3,3,2,2,1,1],[4,3,3,2,2,2]],replicates=100,chains=4,samples=40,thin=1,burns=[0,5,50],
                               seed_formula='900000+10000000*case+10000*burn+1000*start+4*replicate+chain',t_critical=3.182446,tv_failure_threshold=0.05,rhat_threshold=1.05),
                   results=results)
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
