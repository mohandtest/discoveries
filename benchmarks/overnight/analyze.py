#!/usr/bin/env python3
"""Analyze overnight campaign results: coverage, errors, runtimes.

Usage: python3 analyze.py [results.csv] [config.json]
Prints a per-graph report and writes summary.csv next to results.csv.
"""
import csv
import json
import math
import os
import statistics
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    res = os.path.join(BASE, sys.argv[1] if len(sys.argv) > 1 else "results.csv")
    with open(os.path.join(BASE, sys.argv[2] if len(sys.argv) > 2 else "config.json")) as f:
        cfg = json.load(f)
    known = dict(cfg["known_exact"])

    # status.json may carry freshly computed truth (phase 2)
    st_path = os.path.join(BASE, "status.json")
    if os.path.exists(st_path):
        with open(st_path) as f:
            st = json.load(f)
        for ph, info in st.get("phases", {}).items():
            for k, v in info.items():
                if k.startswith("exact_") and isinstance(v, str) and v not in ("FAILED",):
                    known[k[len("exact_"):]] = v

    rows = []
    with open(res) as f:
        for r in csv.DictReader(f):
            rows.append(r)

    groups = {}
    for r in rows:
        groups.setdefault((r["phase"], r["graph"]), []).append(r)

    eps = cfg["fpras"]["eps"]
    out = []
    print(f"{'phase':16s} {'graph':10s} {'trials':>6s} {'ok':>6s} {'mean_rel':>9s} "
          f"{'worst_rel':>9s} {'cov±25%':>8s} {'z_mean':>7s} {'mean_s':>8s}")
    for (phase, graph), rs in sorted(groups.items()):
        ests, times, fails = [], [], 0
        for r in rs:
            if r["estimate"].lstrip("-").replace(".", "").isdigit() or \
               ("e+" in r["estimate"] or "e-" in r["estimate"]):
                try:
                    ests.append(float(r["estimate"]))
                    times.append(float(r["runtime_s"]))
                except ValueError:
                    fails += 1
            else:
                fails += 1
        n = len(ests)
        exact = known.get(graph)
        if not ests:
            print(f"{phase:16s} {graph:10s} {len(rs):6d} {0:6d}   (no data)")
            continue
        if exact:
            ex = float(exact)
            errs = [abs(e - ex) / ex for e in ests]
            mean_rel = statistics.mean(errs)
            worst = max(errs)
            cov = sum(1 for e in errs if e <= eps) / n
            z = (statistics.mean(ests) - ex) / (statistics.stdev(ests) / math.sqrt(n)) if n > 1 else float("nan")
            zs = f"{z:+7.2f}"
        else:
            mean_rel = worst = cov = float("nan")
            zs = "  n/a "
        print(f"{phase:16s} {graph:10s} {len(rs):6d} {n:6d} {mean_rel:9.4f} "
              f"{worst:9.4f} {cov:8.4f} {zs} {statistics.mean(times):8.2f}")
        out.append({"phase": phase, "graph": graph, "trials_total": len(rs),
                    "trials_ok": n, "failed": fails,
                    "mean_rel_err": round(mean_rel, 4) if exact else "",
                    "worst_rel_err": round(worst, 4) if exact else "",
                    "coverage_eps25": round(cov, 4) if exact else "",
                    "z_mean": round(z, 2) if exact else "",
                    "mean_runtime_s": round(statistics.mean(times), 2),
                    "exact": exact or ""})

    if out:
        with open(os.path.join(BASE, "summary.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
        print("\nsummary.csv written")


if __name__ == "__main__":
    main()
