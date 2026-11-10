#!/usr/bin/env python3
"""Check saved hashes, exact matrices and raw-to-summary consistency offline."""
import csv
import hashlib
import json
import math
import statistics as st
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from diagnostics import summarize


def main():
    metadata = json.loads(Path('results/environment.json').read_text())
    for group in ('source_sha256','input_sha256','artifact_sha256'):
        for name, expected in metadata[group].items():
            assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected, name
    for case in json.loads(Path('results/production_exact.json').read_text()):
        rows = [{int(j):Fraction(p) for j,p in row.items()} for row in case['transition_rows']]
        assert len(rows)==case['states']
        for i,row in enumerate(rows):
            assert sum(row.values())==1
            assert all(p==rows[j].get(i,0) for j,p in row.items())
    public = json.loads(Path('results/public_study/summary.json').read_text())
    groups = defaultdict(list)
    with Path('results/public_study/samples.csv').open() as f:
        for r in csv.DictReader(f):
            groups[r['dataset'],r['budget'],r['engine'],int(r['chain'])].append(r)
    for run in public['runs']:
        chains = [groups[run['dataset'],run['budget'],run['engine'],i] for i in range(public['config']['chains'])]
        for i,chain in enumerate(chains):
            assert len(chain)==public['config']['samples']
            accepted = 0
            for j,row in enumerate(chain):
                assert int(row['sample'])==j
                assert int(row['seed'])==run['chains'][i]['seed']
                assert int(row['attempts'])==run['burn']+(j+1)*run['thin']
                assert accepted <= int(row['accepted']) <= int(row['attempts'])
                accepted = int(row['accepted'])
            assert accepted==run['chains'][i]['accepted']
        for metric in public['config']['metrics']:
            recomputed = summarize([[int(r[metric]) for r in chain] for chain in chains],run['observed'][metric])
            assert recomputed==run['statistics'][metric], (run['dataset'],metric)
    groups = defaultdict(list)
    with Path('results/calibration/raw.csv').open() as f:
        for r in csv.DictReader(f):
            key = tuple(int(r[k]) for k in ('case','burn','start','replicate','chain'))
            assert int(r['sample'])==len(groups[key])
            expected_seed = 900000+10000000*key[0]+10000*key[1]+1000*key[2]+4*key[3]+key[4]
            assert int(r['seed'])==expected_seed
            groups[key].append(int(r['triangles']))
    for result in json.loads(Path('results/calibration/summary.json').read_text())['results']:
        key = tuple(result[k] for k in ('case','burn','start','replicate'))
        chains = [groups[key+(i,)] for i in range(4)]
        assert all(len(c)==40 for c in chains)
        mean = st.mean([st.mean(c) for c in chains])
        se = st.stdev([st.mean(c) for c in chains])/2
        assert mean==result['mean'] and se==result['mcse']
        assert (abs(mean-result['exact_triangle_mean'])<=3.182446*se)==result['covered']
    print('All recorded hashes, transition matrices and raw-to-summary checks pass.')


if __name__=='__main__':
    main()
