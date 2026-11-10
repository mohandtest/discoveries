# ROADMAP — work done, work next, where this could go

Last updated: 2026-11-10

## Standing mission

Keep reading the papers in OpenAI's [openai/math](https://github.com/openai/math)
release, pick implementable results, and produce **constants reports**:
implementations that answer *does this algorithm actually run, and at
what cost?* — benchmarked against exact ground truth, audited
adversarially, reported honestly (negative results included).

Protocol per result: map → research incumbents → pick → implement +
unit-verify → benchmark against exact truth → invite adversarial
audits → write the report → commit everything.

## Publication policy (as of 2026-11-10) — READ FIRST

**This is private work. No public artifacts without an explicit go.**

- **Do not open issues on openai/math** (no issue linking our
  implementation, no notifying the paper authors).
- **Do not submit PRs to networkx or any upstream** (no
  `count_perfect_matchings` PR, nothing else).
- **Do not publish on arXiv** or anywhere else.
- This repository is the private working record. The "where we could
  contribute" notes below exist so the options survive review — they
  are **not** acted on.

## Work done

### Algorithm #1 — FPRAS for counting perfect matchings (complete)

- Mapped all 373 result families (`discovery-map/`); picked the
  general-graph perfect-matching FPRAS (OpenAI Sept 2026; simplified
  proof Liu & Meng, arXiv:2610.26803): fresh, celebrated, zero
  implementations anywhere.
- Implemented: Python kernel + annealing counter, C binary
  (`fpras.c`) with the 128-bit reachable-state exact DP.
- Survived two adversarial audits: external issue #1 (barbell truth,
  n=2 hang, infeasibility overstatement) and the pre-launch subagent
  audit (uint64 overflow at n≥44 → 128-bit fix).
- Overnight campaigns (2026-11-10, server): 920 + 200 trials,
  zero failures. **First exact ground truth at n=44:**
  G(44,.5) s42 = 38,960,201,918,564,595,040 (1217.5 s, 1,129,482,570
  reachable states, reproduced bit-identically in an independent rerun).
- Validation over 600 independent runs: coverage 84–93.5% at ε=0.25,
  z = +0.48 at n=44 (unbiased); ladders confirm sparse-instance failure
  of the guarantee shape (16–25% coverage).
- Root-caused and fixed a hash-clustering bug that had inflated every
  exact timing above n≈32: corrected curve 0.2 s (n=24) → 123 s (n=40)
  → 1217.5 s (n=44); **corrected crossover: exact DP practical through
  n=44, FPRAS ~1,270× faster there, necessary beyond** (n=48 exact is
  RAM-infeasible, >400 GiB).
- Living constants report: `fpras-benchmark/README.md`. Raw campaign
  data: `benchmarks/overnight/campaign1/`, `campaign2/`.

### Algorithm #1.5 — degree-preserving graph sampling (#131) (owned, planned)

- Foundation built and verified (Nov 10): exhaustive small-graph
  enumeration by degree sequence, exact TV mixing curves, jump-chain
  bias audit, karate-club triangle-null prototype, 11 passing tests.
  Docs corrected: the uniform-quadruple lazy kernel is **the chain the
  #131 preprint analyzes** (TV(1/4) ≤ 2n⁸) — see `graph-sampling/`.
- Planned pass-2 measurement campaign (not yet run):
  1. Exact enumeration ground truth to n≈10–12 (sparse regular +
     heterogeneous sequences); exact TV curves across n, degree,
     heterogeneity → the first *measured* mixing curve for the
     KTV-resolution chain: 2n⁸ vs reality.
  2. Two-kernel comparison (paper's quadruple chain vs practitioner
     edge-pair chain, both in the codebase) + NetworkX
     `double_edge_swap` as incumbent, matched workloads.
  3. Karate demo upgraded to a calibrated claim with measured
     burn-in constants; adversarial audit; report.
- Paper reading: the #131 exact sampler is a rare-residual-mixture
  construction (t = O(n⁸) chain steps + a bias-correction branch with
  probability 2^−O(n²)) — expected-polynomial on paper, pure armor in
  practice. The practical content is the finite-time law; measure it.

## Current writing task (scoped down)

**Constants report (algorithm #1):** for now, a **simple draft only**,
living in this repo — the standalone arXiv-note narrative of what we
measured. No submission anywhere. Suggested home: `reports/` when
written; `fpras-benchmark/README.md` remains the living report.

## Where we could contribute (recorded only — do NOT act yet)

- **networkx**: `count_perfect_matchings` — the reachable-state DP
  (measured: n=44 in 20 min / 48 GiB; the ×6.9-per-4-vertices growth
  law; RAM ceiling guidance). Natural PR when the public phase starts.
- **openai/math**: an issue linking our implementation + benchmarks
  for the perfect-matching FPRAS family; separately, one for #131
  after pass 2. Would also notify Liu & Meng (arXiv:2610.26803).
- **arXiv**: the standalone constants report (draft above).
- Context for the eventual public phase: OpenAI funds vetting
  workshops; the community conversation (HN, MathOverflow) is the
  audience for exactly this artifact class.

## Later algorithm candidates (ranked, from the discovery map)

1. **Near-linear general-graph matching** — market leader (kidney
   exchange, allocation, alignment vs Blossom V); hardest constants;
   the "single finite program" paper.
2. **Deterministic factorization over F_p** — chains off the Quasi-RH
   result; verifiable against FLINT/PARI randomized baselines.
3. **Mean-payoff games** — quasipolynomial; verification-tooling angle.
