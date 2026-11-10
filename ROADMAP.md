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

The protocol is formalized as the **algorithm factory** — an
autonomous, sequential loop (`factory/README.md`; live state
`factory/STATE.md`, phase runbooks `factory/phases/`, structured
memory `factory/memory/`, dispatch skills `.opencode/skills/`).
Pass #3 (near-linear matching, candidate 1 below) pilots the formal
loop. **Standing pick criterion: novelty first** (user priority);
market × implementability are gates.

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

### Algorithm #2 — degree-preserving graph sampling (#131) (in progress)

One workstream, two phases: the **#131 mixing-curve campaign is the
remaining measurement phase of this same study**, not a separate effort.
The paper (*Polynomial mixing of the switch chain for every graphical
degree sequence*, the Kannan–Tetali–Vempala resolution) analyzes exactly
the uniform-quadruple lazy kernel in the codebase (TV(1/4) ≤ 2n⁸).

- Phase A — foundation (done, verified): exhaustive small-graph
  enumeration, exact TV machinery, jump-chain bias audit, 16 passing
  tests, kernel↔paper correspondence established.
- Phase B — validation study (done, merged from
  `codex/graph-sampling-validation`, commit `3355993`): exact rational
  transition-matrix audits (6 sequences, 133 states), 1,800-trial
  calibration showing the R-hat gate gives **false reassurance and poor
  power** (never reliable on heterogeneous cases; 95% t-intervals cover
  truth only 82–99/100), NetworkX baseline comparison, and three real
  networks — karate (45 triangles vs null 39.3–39.6, tail ~0.11:
  degrees explain the clustering), florentine (tail ~0.5), **dolphins
  (95 vs null 34.0–34.2, zero upper-tail hits in 800 draws — strong
  descriptive contrast, tail unresolved)**.
- Phase C — the measurement campaign (in flight, 2026-11-10; results in
  `graph-sampling/results/MIXING_RESULTS.md`):
  1. **Practitioner burn-in constants** (running): exact TV(1/4)/TV(0.05)
     mixing times by enumeration at n=6–12 across d=2..4 and heterogeneous
     shapes. Measured so far: t(1/4) = 50/250/250/500 at n=6/8/9/10 —
     ~2× per +1 n, **not** n⁸; complement symmetry d↔n−1−d observed exactly
     (n8d3 ≡ n8d4). Over-provision vs the proven 2n⁸: 67,000–400,000×
     (and growing with n). n=11/12 + heavy-tail rows in flight.
  2. **Dolphins tail quantified (done)**: observed 95 vs null 34.28 ± 4.94
     over 800,000 retained draws — 0 hits (tail < 1.25e-6), z = 12.3.
     Karate contrast: tail 12.6% (z = 1.2). Degrees explain the karate
     club's clustering; they do **not** explain the dolphins'.
  3. **Burn vs spacing isolated (done)**: burn 0→125k moves means ≤ 0.5
     triangles (consistent with measured t_mix); thin=1 biases karate
     −1.39. Rule: budget goes to thinning and chains, not burn-in.
  4. **Throughput (done)**: 161k–200k attempts/s single-core Python; an
     800k-draw null study costs ~5 minutes — the switch chain is not the
     bottleneck at social-network scale.
  Then: adversarial audit → in-repo constants report (private).

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
