# A constants report for the FPRAS counting perfect matchings in general graphs

**Status: DRAFT, private.** Not for submission anywhere (publication
policy: `ROADMAP.md`). The canonical, always-current version of these
results is the living report: [`fpras-benchmark/README.md`](../fpras-benchmark/README.md).
This note is its standalone narrative form — written for the eventual
public phase, kept in-repo for now. Every number below is traceable to
the living report or the raw campaign CSVs.

## Abstract

The OpenAI mathematics release (Sept 2026) contains a fresh FPRAS for
counting perfect matchings in general graphs, with a simplified proof
by Liu & Meng (arXiv:2610.26803). The result was celebrated and had
**zero implementations anywhere**. We built one: the paired-chain
kernel, an annealing counter, and — as ground truth — an exact
reachable-state dynamic program that turns out to be practical far
beyond the naive 2ⁿ bound. On identical saved graphs and one machine we
measured where exact counting ends and sampling becomes necessary
(**n = 44** on this hardware: the first published-exact perfect-matching
count at that size, 3.90×10¹⁹, reproduced bit-identically), what the
FPRAS costs there (~1 s per run, ~1,270× faster than exact), and how
accurate it is at practical budgets (600 independent runs: unbiased
means on dense graphs, coverage 84–93.5% at ε = 0.25 against a nominal
95%). The proof's replication parameters (~10⁷³ replicas) are worst-case
armor, not guidance: q = 2 and 10³–10⁵ steps suffice on every tested
dense instance — while sparse structured graphs (ladders) sit far
outside the guarantee's shape at the same budgets. An honest correction
is included: our first crossover claim was inflated by a hash bug and
is superseded here.

## 1. The problem and the paper

Counting perfect matchings of a general graph is #P-hard; the classical
FPRAS (Jerrum–Sinclair–Vazirani) is famous but heavy. The new result
(OpenAI, Sept 2026; simplified proof: Liu & Meng, arXiv:2610.26803)
gives a fully polynomial randomized approximation scheme via a paired
chain on perfect matchings of a clique with annealed nonedge weights,
with a worst-case replication architecture of
q = 32·(10n)⁸⁰·(D+1)⁹ ≈ 10⁷³·n¹¹⁶ replicas per level across
~2n·log(2D·4^Q) levels.

Nothing in the ecosystem answered the practitioners' question: *does
this algorithm actually run, and at what cost?* This report is that
answer.

## 2. What we built

1. **The kernel** (`chain.py`, ported to C in `fpras.c`): the paper's
   paired chain (M₁, M₂) — two-edge switches (Metropolis), holds, and
   cycle exchanges on discrepancy cycles (always accepted). Verified
   empirically: stationary-law agreement on weighted K₄ (TV = 0.0014
   over 180k samples — a check, not a proof), a successful cycle
   exchange on the chordless C₆, and exact preservation of
   w(M₁)·w(M₂) under exchanges.
2. **The counter** (`anneal.py`): the paper's outer annealing schedule
   (nonedge weight b⁻ʲ, b = 1+1/n) at practical parameters. This is a
   **heuristic adaptation** — the paper's formal guarantee does not
   transfer to the reduced parameters, and every accuracy claim below
   is empirical.
3. **Ground truth** (`exact.py`, `exact2.py`, `fpras.c`): an exact
   reachable-state DP. The insight that matters: a memoized recursion
   that repeatedly removes the lowest unmatched vertex and a partner
   visits only *reachable* states — 61,233 states for G(24, 0.5) versus
   8.4M even subsets — collapsing the state space by orders of
   magnitude.
4. **Structural variants** (`windowed.py`, `hierarchy.py`): faithful
   practical versions of the paper's replication machinery. Negative
   results (§8).

## 3. Exact ground truth first

Approximation claims need exact truth. The reachable-state DP is
practical far beyond the naive 2ⁿ bound:

| n | 24 | 28 | 32 | 36 | 40 | 44 |
|---|---|---|---|---|---|---|
| reachable states | 61k | 496k | 3.47M | 24.0M | 165M | 1,129,482,570 |
| exact time (single process) | 0.2 s | 0.2 s | 1.3 s | 14.2 s | 123 s | 1217.5 s |

State count grows ×6.9 per 4 vertices — still ~4 orders of magnitude
below the 2⁴⁴ subset bound at n = 44.

**The n = 44 ground truth:** G(44, 0.5), seed 42 has
**38,960,201,918,564,595,040 ≈ 3.90×10¹⁹ perfect matchings** — beyond
uint64 (1.8×10¹⁹), hence 128-bit arithmetic. An independent rerun
reproduced the count bit-identically (1213.5 s). Verified counts at
smaller n were additionally cross-validated against an independent
reviewer's implementation (77,137,026 at n = 24; 26,118,833 for the
seed-4711 fixture).

## 4. The crossover — corrected

Our first published crossover was wrong, and the correction is part of
the result. The DP's hash used the low bits of `key × φ`; the DP's keys
are highly structured (DFS always removes the *lowest* remaining
vertex, so deep states have cleared low bits), and at n = 44 about 4M
states hashed to a **single slot** — linear-probe chains grew to ~20,000
probes per lookup and rising. Every exact timing above n ≈ 32,
including the "46.6 min at n = 40" headline and the "~1,100× gap" built
on it, was an artifact of that clustering. A splitmix64-style finalizer
fixed it; all regression truths reproduce bit-identically and the n = 40
count re-verified equal (179,249,264,420,609,805) — the bug was
performance-only, but our crossover claims were built on it.

**Corrected reading:** the exact DP is practical through **n = 44**
(1217.5 s, ~48 GiB). The FPRAS is ~160× faster than exact at n = 40 and
**~1,270× at n = 44** (0.96 s per independent run). At n = 48 the
extrapolated ~7.8B reachable states need >400 GiB — beyond this
server — so **n = 44 is the practical exact ceiling on this hardware,
and the FPRAS is necessary beyond it.** Dense-graph scaling with the
FPRAS alone (n = 48–64, both densities, 32 runs each) completes in
1.2–2.8 s per run with zero failures.

## 5. Accuracy at practical budgets

200 independent runs per graph (one process each, sha256-derived
seeds, ε = 0.25, 1024 samples/burn; 600 dense runs total):

| graph | mean \|rel err\| | worst | coverage ±25% | z-mean | mean s |
|---|---|---|---|---|---|
| G(36, .5) | 0.120 | 0.44 | 91.5% | −2.36 | 0.59 |
| G(40, .5) | 0.123 | 0.86 | 93.5% | +0.10 | 0.77 |
| G(44, .5) | 0.136 | 0.57 | 84.0% | +0.48 | 0.96 |
| ladder 24 | 0.562 | 2.40 | 15.6% | −2.40 | 0.78 |
| ladder 28 | 0.552 | 2.94 | 25.0% | −1.92 | 1.11 |

Three readings:

1. **Means are unbiased on dense graphs** (z within ±2.4; +0.48 at
   n = 44). An earlier single 8-replica run that came out 5σ low
   (G(24), seed 4711: 21.3M ± 0.4M against truth 26,118,833) was seed
   luck, not systematic bias.
2. **Per-run error is real and occasionally large** — worst 57% at
   n = 44 — while replica-based standard errors read only a few
   percent. Replica SEs **understate** true error; any accuracy claim
   needs many genuinely independent runs. Budget goes to independent
   runs, not replicas.
3. **Coverage sits below nominal** (84–93.5% against a nominal 95%):
   at this budget the ±25% promise is not delivered as reliably as the
   theory's confidence parameter suggests. This is the honest number a
   practitioner should plan around.

## 6. Where the guarantee shape fails

Sparse structured graphs are a different regime. Ladders at the same
budgets sit far outside ±25% (coverage 16–25%, biased low, mean
relative errors 0.55–0.56). The dense-graph success of the reduced-
parameter sampler does not transfer to sparse instances — consistent
with the fact that the reduced parameter set carries no formal
guarantee at all.

## 7. Proof parameters versus practice

The worst-case replication architecture — ~10⁷³·n¹¹⁶ replicas per
level, ~2n·log(2D·4^Q) levels — was never intended as a configuration.
On every tested dense instance, **q = 2 and 10³–10⁵ steps sufficed**.
That is an observation, **not a theorem**: the reduced-parameter
sampler carries no formal guarantee, and the observed seed-dependent
bias (§5) is consistent with exactly that. The proof's parameters are
armor against adversarial inputs, not guidance for burn-in.

## 8. Negative results

The naive simplifications of the replication machinery genuinely fail:

1. **Same-weight replica exchanges** homogenize and freeze the
   ensemble — q = 8 underestimates by ~10×, q = 32 returns literally 0.
2. **Sliding-window cross-level chains**: per-level compute dilution;
   window re-equilibration lags the schedule by ~10 stages.
3. **Static full hierarchy** at 1.5M steps: ~300 visits per level,
   orders of magnitude below the theory's prescription; per-stage
   ratios look healthy while the product amplifies residual lag into
   underflow.

The lesson: the kernel and the outer annealing schedule are the
practical artifact; the replication architecture exists to close the
worst-case mixing proof.

## 9. Practical guidance

- On dense-ish graphs at this scale class: run the exact reachable-
  state DP through n ≈ 44 (minutes, tens of GiB); switch to the FPRAS
  beyond, at ~1–3 s per run.
- Spend FPRAS budget on **independent runs**, never on replicas or
  replica-weighted machinery; treat replica SEs as lower bounds on
  error.
- Expect the ±25% promise to hold ~84–94% of the time at 1024-sample
  budgets on dense graphs — not 95%.
- Do not trust the reduced-parameter sampler on sparse structured
  graphs without its own validation.
- If you implement a DP over structured keys: beware hash functions
  that respect the structure (§4). We caught it because the timing
  curve looked too slow, not because anything was wrong.

## 10. Provenance, audits, and corrections

- Identical saved graphs (`fpras-benchmark/graphs/`), one machine, one
  binary; raw campaign data in `benchmarks/overnight/campaign1/`
  (920 runs) and `campaign2/` (hash-fixed rerun: n = 44 truth + 200
  scored runs).
- Two adversarial audits shaped the result: an external reviewer's
  issue (barbell truth is 225, not 226; an n = 2 hang; overstated
  infeasibility — all fixed, regression-tested) and a pre-launch
  subagent audit that caught a uint64 overflow at n ≥ 44, which would
  have corrupted the headline count (hence 128-bit arithmetic).
- The hash-bug correction (§4) is deliberately loud: superseded claims
  get a correction section, never a quiet edit.

*Draft date: 2026-11-10. Living report: `fpras-benchmark/README.md`.
Implementation: `fpras-benchmark/` (Python + C). Campaign platform:
`benchmarks/overnight/`.*
