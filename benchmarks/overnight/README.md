# Overnight Benchmark Campaign — Perfect Matching Counting

A controlled, unattended 8-hour benchmark for the FPRAS (OpenAI/Liu–Meng 2026)
against an exact 128-bit counter, run on the 24-core / 360 GB / 10 GB-disk
server. Built after an external review identified (a) a uint64 overflow in the
exact counter (n≥44 counts exceed 1.8e19) and (b) the need for genuine
coverage statistics — independent complete estimator runs, not chain samples.

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
