#!/usr/bin/env python3
"""Consolidate mixing_ladder results into the constants table.

Reads results/mixing/<tag>.txt files written by switch_exact and emits a
markdown + CSV summary: states, t_mix(1/4), t_mix(0.05), the proven 2n^8,
and the over-provision factor. Run after the ladder completes:
    python3 mixing_table.py [results/mixing]
"""
import csv
import re
import sys
from pathlib import Path


def parse(txt):
    head = re.search(r'states=(\d+) quads=(\d+) avg_state_deg=([\d.]+) '
                      r'connected=(\w+)', txt)
    worst = re.search(r'WORST t_mix\(0\.25\)=(-?\d+) t_mix\(0\.05\)=(-?\d+) '
                      r'\[max over (\d+) sampled starts', txt)
    prov = re.search(r'proven_2n8=(\d+) overprovision=([\d.-]+)x', txt)
    deg = re.search(r'degrees=([\d,]+)', txt)
    if not (head and worst and prov):
        return None
    n = int(re.search(r'n=(\d+) degrees=', txt).group(1))
    return {
        'n': n,
        'sequence': deg.group(1),
        'states': int(head.group(1)),
        'avg_state_deg': float(head.group(3)),
        'connected': head.group(4),
        't25': int(worst.group(1)),
        't05': int(worst.group(2)),
        'starts': int(worst.group(3)),
        'proven_2n8': int(prov.group(1)),
        'overprovision': float(prov.group(2)),
    }


def main():
    import math
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/mixing')
    rows = []
    for f in sorted(root.glob('*.txt')):
        r = parse(f.read_text())
        if r:
            r['tag'] = f.stem
            q = math.comb(r['n'], 4)
            r['quads'] = q
            r['t25_per_sweep'] = round(r['t25'] / q, 2) if r['t25'] > 0 else None
            r['t05_per_sweep'] = round(r['t05'] / q, 2) if r['t05'] > 0 else None
            rows.append(r)
    rows.sort(key=lambda r: (r['n'], r['sequence']))
    print(f"{'tag':10} {'n':>2} {'sequence':26} {'states':>10} "
          f"{'t(1/4)':>7} {'t(0.05)':>8} {'sweep25':>8} {'sweep05':>8} "
          f"{'2n^8':>11} {'over':>11}")
    for r in rows:
        seq = r['sequence'] if len(r['sequence']) <= 26 else r['sequence'][:23] + '...'
        # --t25only rows carry t05 = -1 -> sweep ratio None; print a dash
        s25 = f"{r['t25_per_sweep']:.2f}" if r['t25_per_sweep'] is not None else '—'
        s05 = f"{r['t05_per_sweep']:.2f}" if r['t05_per_sweep'] is not None else '—'
        print(f"{r['tag']:10} {r['n']:>2} {seq:26} {r['states']:>10,} "
              f"{r['t25']:>7} {r['t05']:>8} {s25:>8} "
              f"{s05:>8} {r['proven_2n8']:>11,} "
              f"{r['overprovision']:>10.0f}x")
    with open(root / 'mixing_table.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ['tag'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n{len(rows)} cases -> {root / 'mixing_table.csv'}")


if __name__ == '__main__':
    main()
