# FPRAS Benchmark — Perfect Matching Counting in General Graphs

First implementation worldwide of the FPRAS for counting perfect matchings in
general graphs (OpenAI, Sept 2026; simplified proof: Liu & Meng, arXiv:2610.26803,
Oct 2026). Question investigated: **is the proof's machinery a practical
algorithm or an asymptote trophy?**

## What was implemented

1. **The paper's kernel K, verbatim** (`chain.py`): paired chain (M1, M2) on
   perfect matchings of K_n — two-edge switches (Metropolis), holds, and cycle
   exchanges on discrepancy cycles (always accepted).
   Verified: stationarity on weighted K_4 (TV = 0.0014 vs exact law);
   irreducibility on the chordless C_6 (the paper's own motivating obstruction);
   exact preservation of w(M1)·w(M2) under exchanges.
2. **Plain annealing counter** (`anneal.py`): the paper's outer schedule
   (nonedge weight b^{-j}, b = 1+1/n), ratio observables, product estimator
   Ẑ = (n-1)!! · Π R̂_j — with *practical* parameters instead of proof parameters.
3. **Three structural variants testing the paper's replication machinery**
   (`chain.py: ReplicatedChain`, `windowed.py`, `hierarchy.py`): same-weight
   replica exchanges, sliding-window cross-level chain, static full-hierarchy
   chain.

## Headline results (single-pair annealing, pure Python, laptop)

| instance | exact | estimate | rel. err | wall time |
|---|---|---|---|---|
| K_8, K_12 | 105 / 10395 | exact | 0.000 | < 1 s |
| G(8,0.3) — Z=1 | 1 | 1.08 | 0.08 | 0.2 s |
| G(16,0.3) — Z=4 | 4 | 4.04 | 0.01 | 1.1 s |
| G(20,0.25) — Z=16 | 16 | 15.45 ± 2.0 | 0.03 | 12 s |
| C_18 (chordless, Z=2) | 2 | 2.05 ± 0.25 | 0.02 | 4 s |
| C_20 (chordless, Z=2) | 2 | 2.01 ± 0.10 | 0.004 | 5 s |
| C_24 (chordless, Z=2) | 2 | 2.00 ± 0.23 | 0.000 | 22 s |
| Ladder 2×12 (Z=233) | 233 | 255 ± 36 | 0.095 (<1σ) | 20 s |
| G(24,0.5) | > 2²⁴ states | 26.3M ± 2.0M | run-spread 0.19 | 50 s |
| C_30 / C_40 | 2 | 1.47±0.44 / 2.30±1.05 | noisy | 41 / 105 s |

Envelope: **excellent through n ≈ 24** on all graph families including the
theory's pathological instances; degradation begins ~n ≈ 30 on adversarial
(chordless-cycle) instances at ~100 s budgets. Exact DP is already infeasible
at n = 24+ (2²⁴ subset states), so the sampler operates where no exact method
exists.

## The proof's parameters vs. practice

The worst-case guarantee requires q = 32·(10n)^80·(D+1)^9 ≈ **10⁷³·n¹¹⁶**
replicas per level (D = 10⁸(n+1)⁴), ~2n·log(2D·4^Q) ≈ 17,000 levels for n=18,
and chain lengths ∝ J·(Λ + log(1/ξ)). None of this is needed in practice on
tested instances: **q = 2 and ~10³–10⁵ total steps suffice**. The proof
structure is worst-case armor, not engineering guidance.

## Negative results (why the naive simplifications fail)

1. **Same-weight replica exchanges destroy the estimate.** With q replicas
   exchanging with each other at equal weights, the ensemble homogenizes and
   freezes (all replicas identical → exchanges no-op, switches rejected at late
   stages): q=8 underestimates ~10×, q=32 returns literally 0.
2. **Sliding-window cross-level chains underperform**: the window must
   re-equilibrate after every slide; per-level compute dilutes below the
   relaxation needs (empirically ~10 stages of lag vs 1 stage of schedule).
3. **Static full hierarchy** (paper structure, q=2, 1.5M steps) still gives
   ~300 update visits per level — three orders of magnitude too few; per-stage
   ratio means are healthy (0.65–0.72) but the product amplifies the residual
   lag into underflow. The theory compensates with 17k levels × astronomic q.

**Lesson:** the paper's *kernel and outer schedule* are the practical artifact;
its *replication architecture* exists to make the mixing proof close in the
worst case. Stripping the armor is not just safe on tested instances — it is
the only way to run at all.

## Meta-finding for the discovery-map thesis

This was the cleanest test of "are the repo's runnable-looking results
runnable?" Verdict: **yes, with surgery**. The result is not an asymptote
trophy — its core moves (cycle-exchange kernel, annealing schedule, telescoping
ratio observables) transfer directly to code and perform at n where exact
methods die. But nothing in the paper tells you which parts are load-bearing:
that required implementation + ablation (this repo). "Proof-to-production"
needs a constants-extraction stage that no current pipeline performs.

## Files

- `exact.py` — subset-DP exact counter + closed forms (validated)
- `chain.py` — paired kernel K (verified) + replicated variant
- `anneal.py` — plain annealing counter (the practical winner)
- `windowed.py`, `awindow.py`, `hierarchy.py` — structural variants (negative)
- `test_chain.py` — unit tests (all pass)
- `bench.py` … `bench7.py` — experiment sequence
- `results.csv` — main benchmark table
