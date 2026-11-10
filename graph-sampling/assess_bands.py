#!/usr/bin/env python3
"""Assess measured mixing rows against the pre-registered bands.

Prediction-vs-measured is a factory metric (factory/JOURNAL.md). The
bands below were pre-registered BEFORE any of these rows landed
(commit 1d32259); rows completed before pre-registration (n=6..10
d=2..4, n=6 het anchors) have no bands — they generated the sweep law.

Reads results/mixing/<tag>.txt WORST lines; prints in-band / out-of-band
per row (t(1/4) core bands; t(0.05) secondary bands, with '—' for
t25only rows). Exit code 0 always: misses are results, not errors.
"""
import re
import sys
from pathlib import Path

# tag: (t25_lo, t25_hi, t05_lo, t05_hi)
BANDS = {
    'n10d3': (420, 840, 840, 1700),
    'n10d4': (420, 840, 840, 1700),
    'n11d2': (660, 1320, 1300, 2600),
    'n12d2': (990, 1980, 2000, 4000),
    'n8het': (140, 280, 300, 1400),
    'n10het': (420, 1980, 800, 10000),
    'n11het': (420, 1980, 800, 10000),
    'n12het': (420, 1980, 800, 10000),
}


def worst(txt):
    m = re.search(r'WORST t_mix\(0\.25\)=(-?\d+) t_mix\(0\.05\)=(-?\d+)', txt)
    return (int(m.group(1)), int(m.group(2))) if m else None


def verdict(v, lo, hi):
    if lo <= v <= hi:
        return 'IN BAND'
    if v < lo:
        return 'BELOW (favorable)'
    return 'ABOVE (refutes)'


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/mixing')
    print(f"{'case':8} {'t(1/4)':>7} {'band':>11} {'verdict':>18} "
          f"{'t(0.05)':>8} {'band':>13} {'verdict':>18}")
    core_hits = core_total = 0
    for tag, (l25, h25, l05, h05) in BANDS.items():
        f = root / f'{tag}.txt'
        if not f.exists():
            print(f"{tag:8} {'-':>7} {'(no file)':>11} {'IN FLIGHT':>18}")
            continue
        w = worst(f.read_text())
        if not w:
            print(f"{tag:8} {'-':>7} {'(no WORST)':>11} {'IN FLIGHT':>18}")
            continue
        t25, t05 = w
        v25 = verdict(t25, l25, h25)
        core_total += 1
        core_hits += v25.startswith('IN')
        if t05 > 0:
            v05 = verdict(t05, l05, h05)
            band05 = f'{l05}-{h05}'
        else:
            v05, band05 = '— (t25only)', '—'
        print(f"{tag:8} {t25:>7} {f'{l25}-{h25}':>11} {v25:>18} "
              f"{t05:>8} {band05:>13} {v05:>18}")
    print(f'\ncore t(1/4) bands: {core_hits}/{core_total} in band')
    print('misses are results: BELOW = favorable, ABOVE = refutes')


if __name__ == '__main__':
    main()
