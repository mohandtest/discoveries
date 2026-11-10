# Overnight Benchmark Campaign — Perfect Matching Counting

A controlled, unattended 8-hour benchmark for the FPRAS (OpenAI/Liu–Meng 2026)
against an exact 128-bit counter, run on the 24-core / 360 GB / 10 GB-disk
server. Built after an external review identified (a) a uint64 overflow in the
exact counter (n≥44 counts exceed 1.8e19) and (b) the need for genuine
coverage statistics — independent complete estimator runs, not chain samples.

## Campaign results (2026-11-10) — completed, zero failed trials

Two unattended runs; raw data in `campaign1/` (phases 1–4, 920 trials)
and `campaign2/` (phase 2/3 rerun with the hash-fixed binary, 200
trials + exact). Summary:

- **Phase 1** (400 runs): G(36,.5) coverage **91.5%** at ε=0.25,
  G(40,.5) **93.5%**; mean |rel err| ≈ 0.12; zero failures
- **Phase 2** (ground truth): **G(44,.5) s42 has 38,960,201,918,564,595,040
  perfect matchings**, exact DP in **1217.5 s** (~48 GiB) — the first
  128-bit-safe exact count at n=44. (Campaign 1's attempt stalled on the
  pre-fix hash-clustering bug — see `fpras-benchmark/README.md` — and was
  killed to protect the budget; the fixed binary re-ran it cleanly.)
  The g40 truth also re-verified identically in **123 s** (was 46.6 min
  pre-fix; the bug inflated every exact timing above n≈32).
- **Phase 3** (200 runs vs fresh truth): coverage **84.0%**, mean
  |rel err| 0.136, worst 0.57, **z = +0.48** (unbiased)
- **Phase 4** (320 runs): n=48–64 dense graphs 1.2–2.8 s/run, zero
  failures; ladders confirm the sparse-variance warning (coverage 16%/25%)

Interpretation and corrected timing curves live in
`../../fpras-benchmark/README.md`.

## What runs tonight

| Phase | Experiment | Policy |
|---|---|---|
| 0 | build + regression: exact counts vs known values on g24/g28/g32/g36 | abort on any mismatch |
| 1 | reliability: **200 independent FPRAS runs** on g36 and g40 | ≤ 20 concurrent |
| 2 | ground truth: **exact n=44**, single process, `__int128` counts | 3 h timeout, RAM-monitored, killed above 330 GB |
| 3 | validation: **200 independent FPRAS runs** on n=44 vs fresh truth | ≤ 20 concurrent |
| 4 | scaling: FPRAS on n=48/52/56/64 × {G(n,0.5), G(n,0.3)} + ladders 2×24, 2×28 (closed-form truth) | 32 trials each |

n=48 exact counting is deliberately **excluded** (memory too uncertain with
24-byte 128-bit slots; needs a modular-arithmetic implementation — future work).

## Safety rules (enforced by runner.py)

- **8-hour hard deadline** — remaining phases are marked `skipped_deadline`
- **RAM ceiling 280 GB** checked before every launch (waits if breached)
- **RAM kill 330 GB** — monitor thread samples the cgroup every 20 s during
  the exact run and kills it before the LXC OOMs
- every trial is a **genuinely independent complete estimator run**: one
  process, fresh chains, full annealing schedule, own seed
- small logs only (results ≈ 1k rows, status.json, runner.log)

## Files

- `config.json` — graphs, seeds, run counts, timeouts, resource budgets
- `runner.py` — the campaign driver (all phases, guards, atomic status writes)
- `run.sh` — entry point (compiles, then execs runner.py)
- `analyze.py` — coverage / error / runtime report → `summary.csv`
- `deploy.sh` — ships code + graphs to the server (`test:~/overnight/`)
- `results.csv`, `status.json`, `runner.log`, `summary.csv` — generated at
  runtime, committed after the campaign
- `fpras.c` — canonical source lives in `../../fpras-benchmark/fpras.c`

## Reproduce

```sh
# from the server, inside tmux:
cd ~/overnight && tmux new -s overnight './run.sh'
```

Local smoke test (all phases at toy scale):

```sh
cp -r benchmarks/overnight /tmp/ovtest && cd /tmp/ovtest
# edit config.json: regression=[g24], phase1 trials=8 (g24), phase3=[], phase4=[]
./run.sh && python3 analyze.py
```

## Metrics reported by analyze.py

- **coverage ±25%** (empirical): fraction of independent runs within the
  nominal (1±ε) interval, ε = 0.25 — the paper's guarantee shape
- mean / worst relative error against exact truth
- **z-mean**: (mean estimate − truth) / (std/√trials) — systematic bias test
- mean runtime per independent run; failures recorded separately

**Expectation-setting (audit finding #14):** sparse structured graphs
(ladders, ~70 edges at n=48) show much higher estimator variance than dense
graphs — smoke tests saw rel-err up to 0.69 and ±25% coverage of 0–25% at
`samples=1024`. That is the estimator's true behavior at this budget, not a
malfunction; dense graphs behave far better (g36 preview: mean +1.1%,
spread −24%..+29%). Phase 4 ladder rows should be read with this in mind.
