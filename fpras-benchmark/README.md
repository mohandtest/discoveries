# FPRAS Benchmark — Perfect Matching Counting in General Graphs

First implementation of the FPRAS for counting perfect matchings in general
graphs (OpenAI, Sept 2026; simplified proof: Liu & Meng, arXiv:2610.26803,
Oct 2026), benchmarked against an optimized exact counter **on identical
saved graphs and the same machine**.

**Status note (post-audit, issue #1):** an external review correctly
identified that our original README overstated exact-DP infeasibility
(the 2^n state bound is not what a memoized recursion visits) and that the
barbell fixture's ground truth was 225, not 226. All corrections are folded
in below; regression tests added. What remains is an **empirical** study of a
**heuristic adaptation** of the paper's sampler — the paper's formal FPRAS
guarantee does not transfer to the reduced parameters used here.

## What was implemented

1. **The paper's kernel K** (`chain.py`, ported to C in `fpras.c`): paired
   chain (M1, M2) on perfect matchings of K_n — two-edge switches
   (Metropolis), holds, and cycle exchanges on discrepancy cycles (always
   accepted). Verified empirically: stationary-law agreement on weighted K_4
   (TV = 0.0014 over 180k samples — an empirical check, not a proof);
   a successful cycle exchange on the chordless C_6 (not a full
   irreducibility proof); exact preservation of w(M1)·w(M2) under exchanges.
2. **Plain annealing counter** (`anneal.py`): the paper's outer schedule
   (nonedge weight b^{-j}, b = 1+1/n) with practical parameters. This is a
   heuristic adaptation; accuracy/confidence claims below are empirical.
3. **Exact counter** (`exact.py` full-table DP; `exact2.py` + `fpras.c`
   memoized reachable-state DP): visits only states reachable by repeatedly
   removing the lowest unmatched vertex and a partner — e.g. 61,233 states
   for G(24,0.5) vs 8.4M even subsets.
4. **Structural variants** (`ReplicatedChain`, `windowed.py`, `hierarchy.py`):
   faithful practical versions of the paper's replication machinery
   (documented negative results).

## Head-to-head on identical saved graphs (C, same machine)

Graphs saved in `graphs/` (seed 42, p=0.5; cross-validated against an
independent reviewer's implementation). 8 replicas, 1024 samples/stage,
1024-step burn-in.

| n | exact | exact time | DP states | FPRAS est. | rel. err | z | FPRAS time |
|---|---|---|---|---|---|---|---|
| 24 | 77,137,026 | 0.21 s | 61,233 | 78.1M ± 3.2M | 0.013 | +0.3 | 0.64 s |
| 28 | 8,698,633,677 | 1.25 s | 495,866 | 8.28B ± 0.56B | 0.048 | −0.8 | 0.95 s |
| 30 | 175,250,798,667 | 1.09 s | 1,295,709 | 167.0B ± 8.2B | 0.047 | −1.0 | 1.16 s |
| 32 | 1,835,224,024,020 | 1.76 s | 3,467,417 | 1.815T ± 0.067T | 0.011 | −0.3 | 1.37 s |

Honest reading: **at these sizes the optimized exact counter beats the FPRAS
on both speed and precision.** The reachable-state count grows
super-exponentially (61k → 3.5M from n=24→32, ×57 per +8 vertices), so the
exact method's cost explodes eventually; the FPRAS's cost grows smoothly
(stages ∝ n² log n). The FPRAS's value case is beyond the exact method's
reachable-state explosion, not at n=24.

**Known failure mode:** a Python-implementation run on
G(24,0.5) seed 4711 (true count 26,118,833, confirmed by two independent
exact implementations) returned 21.3M ± 0.4M — biased low by 5σ — while an
independent run of the same configuration was accurate (26.3M ± 2.0M).
Replica-based standard errors therefore **understate** true error;
seed-dependent annealing bias exists at these budgets and should be quantified
with many independent runs before any accuracy claim.

## Earlier single-pair annealing results (Python, pre-audit, empirical)

Correct count through n ≈ 24 on all tested families (dense, sparse, chordless
cycles, ladders) at 1–100 s cost; degradation ~n ≈ 30 on adversarial
instances. Ladder/barbell/complete-graph closed forms now regression-tested
(barbell = 225; the bridge edge is never usable — issue #1).

## The proof's parameters vs. practice

The worst-case guarantee requires q = 32·(10n)^80·(D+1)^9 ≈ 10⁷³·n¹¹⁶
replicas per level and ~2n·log(2D·4^Q) levels. None of this is needed
empirically on tested instances (q = 2 and ~10³–10⁵ steps suffice) — but that
is an observation, **not** a theorem: the reduced-parameter sampler carries no
formal guarantee, and its observed seed-dependent bias (above) is consistent
with that.

## Negative results (why the naive simplifications fail)

1. Same-weight replica exchanges homogenize and freeze the ensemble
   (q=8 underestimates ~10×, q=32 returns 0).
2. Sliding-window cross-level chains: per-level compute dilution; window
   re-equilibration lags the schedule by ~10 stages.
3. Static full hierarchy at 1.5M steps: ~300 visits per level — orders of
   magnitude below the theory's prescription; per-stage ratio means look
   healthy but the product amplifies residual lag into underflow.

Lesson: the kernel and outer schedule are the practical artifact; the
replication architecture exists to close the worst-case mixing proof.

## Files

- `exact.py`, `exact2.py` — exact counters (full-table and reachable-state DP)
- `chain.py`, `fpras.c` — paired kernel K (C port: exact + FPRAS in one binary)
- `anneal.py` — plain annealing counter (practical winner, heuristic)
- `windowed.py`, `awindow.py`, `hierarchy.py` — structural variants (negative)
- `test_chain.py` — unit + regression tests (all pass, incl. issue #1 fixes)
- `bench.py` … `bench8.py` — experiment sequence; `graphs/` saved inputs
- `results.csv`, `results_head_to_head.csv` — benchmark tables

Rebuild C: `gcc -O2 -o fpras fpras.c -lm`; run:
`./fpras --edges graphs/g32_p50_s42.edges --mode both`.
