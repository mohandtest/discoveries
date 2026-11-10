#!/usr/bin/env python3
"""Controlled, unattended overnight benchmark campaign.

Phases (config.json):
  0  build + regression (exact counts vs known values, abort on mismatch)
  1  reliability: 200 independent FPRAS runs on n=36 and n=40 (<=20 cores)
  2  ground truth: exact n=44, single process, 128-bit arithmetic, 3h timeout,
     RAM-monitored
  3  validation: 200 independent FPRAS runs on n=44 (vs fresh truth)
  4  scaling: FPRAS on n=48..64 across families (2 erdos-renyi densities +
     ladders with closed-form truth)

Safety:
  - hard deadline (config.deadline_hours) — remaining phases are skipped
  - RAM ceiling checked before every launch; phase 2 has a monitor thread
    that kills the exact run if the cgroup approaches the kill threshold
  - every trial is a genuinely independent complete estimator run
    (fresh chains, full annealing schedule, one process)
  - results.csv (one row per trial) and status.json are written atomically

Usage: python3 runner.py [config.json]
"""
import csv
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
START = time.time()
LOCK = threading.Lock()


def cfg():
    with open(os.path.join(BASE, sys.argv[1] if len(sys.argv) > 1 else "config.json")) as f:
        return json.load(f)


def mem_gb():
    try:
        for p in ("/sys/fs/cgroup/memory.current",
                  "/sys/fs/cgroup/memory/memory.usage_in_bytes"):
            if os.path.exists(p):
                return int(open(p).read()) / 2**30
    except Exception:
        pass
    return 0.0


def save_status(status):
    tmp = os.path.join(BASE, "status.json.tmp")
    with open(tmp, "w") as f:
        json.dump(status, f, indent=1)
    os.replace(tmp, os.path.join(BASE, "status.json"))


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(os.path.join(BASE, "runner.log"), "a") as f:
        f.write(line + "\n")


class Campaign:
    def __init__(self, c):
        self.c = c
        self.graphs_dir = os.path.join(BASE, c["graphs_dir"])
        self.bin = os.path.join(BASE, c["binary"])
        self.deadline = START + c["deadline_hours"] * 3600
        self.known = dict(c.get("known_exact", {}))
        self.status = {"started": time.strftime("%F %T"), "phases": {},
                       "updated": None}
        csv_path = os.path.join(BASE, "results.csv")
        self.csv_new = not os.path.exists(csv_path)
        self.csv_f = open(csv_path, "a", newline="")
        self.w = csv.writer(self.csv_f)
        if self.csv_new:
            self.w.writerow(["phase", "graph", "n", "trial", "seed",
                             "estimate", "runtime_s", "exact", "rel_err"])

    # -- infrastructure ----------------------------------------------------
    def build(self):
        src = os.path.join(BASE, "fpras.c")
        if not os.path.exists(src):
            src = os.path.join(os.path.dirname(BASE), "fpras-benchmark", "fpras.c")
        if not os.path.exists(src):
            log("fpras.c not found in ./ or ../fpras-benchmark/")
            sys.exit(1)
        r = subprocess.run(["gcc", "-O3", "-march=native", "-o", self.bin,
                            src, "-lm"], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"BUILD FAILED:\n{r.stderr}")
            sys.exit(1)
        log("build OK")

    def edge_file(self, g):
        fname = self.c.get("graph_files", {}).get(g, f"{g}.edges")
        return os.path.join(self.graphs_dir, fname)

    def time_left(self):
        return self.deadline - time.time()

    def ram_guard(self, ceiling_gb):
        while mem_gb() > ceiling_gb:
            log(f"RAM guard: {mem_gb():.0f} GB > {ceiling_gb} GB, waiting 60s")
            time.sleep(60)

    # -- experiment primitives ---------------------------------------------
    def exact(self, graph, timeout_s):
        """Single-process exact count with RAM monitor. Returns (count_str, secs)."""
        n = self.c["graph_n"].get(graph)
        cmd = [self.bin, "--edges", self.edge_file(graph), "--mode", "exact"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        stop = threading.Event()

        def monitor():
            while not stop.wait(20):
                m = mem_gb()
                if m > self.c["ram_kill_gb"]:
                    log(f"RAM kill: {m:.0f} GB > {self.c['ram_kill_gb']} GB")
                    proc.kill()
                    stop.set()

        t = threading.Thread(target=monitor, daemon=True)
        t.start()
        try:
            out, err = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            stop.set()
            log(f"exact {graph}: TIMEOUT after {timeout_s}s")
            return None, timeout_s
        stop.set()
        if proc.returncode != 0:
            log(f"exact {graph}: FAILED rc={proc.returncode} {err[:200]}")
            return None, None
        m = re.search(r"exact=(\d+)", out)
        s = re.search(r"seconds=([\d.]+)", out)
        return (m.group(1) if m else None), (float(s.group(1)) if s else None)

    def one_trial(self, phase, graph, seed):
        n = self.c["graph_n"].get(graph, "")
        cmd = [self.bin, "--edges", self.edge_file(graph), "--mode", "fpras",
               "--replicas", "1", "--seed", str(seed),
               "--samples", str(self.c["fpras"]["samples"]),
               "--burn", str(self.c["fpras"]["burn"])]
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=1800)
        except subprocess.TimeoutExpired:
            with LOCK:
                self.w.writerow([phase, graph, n, seed, seed, "TIMEOUT",
                                 round(time.time() - t0, 2),
                                 self.known.get(graph, ""), ""])
            self.csv_f.flush()
            return None
        m = re.search(r"estimate=([\d.e+]+)", r.stdout)
        s = re.search(r"seconds=([\d.]+)", r.stdout)
        if not m:
            with LOCK:
                self.w.writerow([phase, graph, n, seed, seed, "FAILED",
                                 round(time.time() - t0, 2),
                                 self.known.get(graph, ""), ""])
            self.csv_f.flush()
            return None
        est = float(m.group(1))
        rt = float(s.group(1)) if s else time.time() - t0
        exact = self.known.get(graph, "")
        rel = f"{abs(est - float(exact)) / float(exact):.4f}" if exact else ""
        with LOCK:
            self.w.writerow([phase, graph, n, seed, seed, f"{est:.6g}",
                             round(rt, 2), exact, rel])
            self.csv_f.flush()
        return est

    def trials(self, phase, graph, n_trials, seeds_base):
        conc = min(self.c["trial_concurrency"], n_trials)
        with ThreadPoolExecutor(max_workers=conc) as ex:
            futs = [ex.submit(self.one_trial, phase, graph, seeds_base + i)
                    for i in range(n_trials)]
            vals = [f.result() for f in futs]
        return [v for v in vals if v is not None]

    # -- phases -------------------------------------------------------------
    def phase0(self):
        self.build()
        for reg in self.c["regression"]:
            got, secs = self.exact(reg["graph"], 600)
            ok = got == reg["expected"]
            log(f"regression {reg['graph']}: got={got} expected={reg['expected']} "
                f"{'PASS' if ok else 'FAIL'} ({secs if secs is not None else -1:.1f}s)")
            if not ok:
                log("REGRESSION FAILURE — aborting campaign")
                sys.exit(1)
        self.status["phases"]["0_prep"] = {"status": "completed"}
        save_status(self.status)

    def run_phase(self, name):
        ph = self.c["phases"].get(name)
        if not ph:
            self.status["phases"][name] = {"status": "not_in_config"}
            save_status(self.status)
            return
        if self.time_left() < ph["budget_s"]:
            log(f"phase {name}: SKIPPED ({self.time_left()/3600:.2f}h left, "
                f"budget {ph['budget_s']/3600:.2f}h)")
            self.status["phases"][name] = {"status": "skipped_deadline"}
            save_status(self.status)
            return
        st = {"status": "running", "started": time.strftime("%F %T")}
        self.status["phases"][name] = st
        save_status(self.status)
        done = failed = 0
        for exp in ph["experiments"]:
            if self.time_left() < 600:
                log(f"phase {name}: experiment {exp['graph']} skipped (deadline)")
                st.setdefault("skipped", []).append(exp["graph"])
                continue
            self.ram_guard(self.c["ram_ceiling_gb"])
            g = exp["graph"]
            if exp.get("mode") == "exact":
                cnt, secs = self.exact(g, exp.get("timeout_s",
                                                  self.c["phase2_timeout_s"]))
                if cnt:
                    self.known[g] = cnt
                    st[f"exact_{g}"] = cnt
                    st[f"exact_{g}_seconds"] = secs
                    log(f"phase {name}: exact {g} = {cnt} ({secs:.0f}s)")
                    done += 1
                else:
                    failed += 1
                    st[f"exact_{g}"] = "FAILED"
                continue
            base = abs(hash(name + g)) % 90000 + 10000
            vals = self.trials(name, g, exp["trials"], base)
            done += len(vals)
            failed += exp["trials"] - len(vals)
            if vals and g in self.known:
                ex = float(self.known[g])
                errs = [abs(v - ex) / ex for v in vals]
                st[f"{g}_mean_rel_err"] = round(sum(errs) / len(errs), 4)
                st[f"{g}_worst_rel_err"] = round(max(errs), 4)
                st[f"{g}_coverage_eps"] = round(
                    sum(1 for e in errs if e <= self.c["fpras"]["eps"])
                    / len(errs), 4)
            log(f"phase {name}: {g} trials done={len(vals)} failed={failed}")
        st.update({"status": "completed", "ended": time.strftime("%F %T"),
                   "trials_completed": done, "trials_failed": failed})
        save_status(self.status)

    def close(self):
        self.csv_f.close()
        self.status["updated"] = time.strftime("%F %T")
        save_status(self.status)


def main():
    c = cfg()
    camp = Campaign(c)
    log(f"campaign start, deadline in {c['deadline_hours']}h, "
        f"RAM {mem_gb():.0f} GB")
    camp.phase0()
    for name in ("1_reliability", "2_ground_truth", "3_validation",
                 "4_scaling"):
        camp.run_phase(name)
        # keep config.known_exact fresh for later phases (e.g. 3 uses 2's truth)
        c["known_exact"] = camp.known
    camp.close()
    log("campaign complete")


if __name__ == "__main__":
    main()
