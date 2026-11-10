# Discovery Map — OpenAI/math repository (721 manuscripts, 373 result families)

Maps every result family by **finding → approach → lesson**. Detailed per-subject
reports live alongside this file; this document is the cross-cutting synthesis.

## Coverage

| Subject file | Families | Report |
|---|---|---|
| Theoretical computer science | 41 | `report_tcs.txt` |
| Algebraic & complex geometry + Algebra | 54 | `report_algebra.txt` |
| Number theory + Mathematical logic | 37 | `report_numbertheory_logic.txt` |
| Differential geometry + Convex/metric geometry | 44 | `report_geometry.txt` |
| Probability/stat mech + Mathematical physics | 54 | `report_prob_physics.txt` |
| Combinatorics + Dynamical systems | 49 | `report_combinatorics.txt` |
| Analysis + Functional analysis + PDE | 43 | `report_analysis_pde.txt` |
| Topology + Group theory + Operator algebras | 51 | `report_topology_groups_oa.txt` |

Source catalogue: `math/overview.tex` (subject-grouped family descriptions),
`math/CONTENTS.md` (all 721 abstracts). Verification state: ~176 papers carry
machine-checked Lean formalizations (~42% of families); catalogue in
`math/lean/formalization.yaml`.

---

## I. The master technique map

Ten method families recur across all 17 subjects. This is the real transferable
content of the collection — the headline theorems are instances of these.

### 1. Certificate-based proof: replace cleverness with a checkable object
The single most pervasive technique. A hard inequality becomes: exhibit a finite,
machine-checkable artifact whose verification is routine.
- **Interpolation determinants** (number theory): an integer determinant with
  forced divisibility ~log U against an interpolation size ~(3/4)·log U. Powers
  Catalan's irrationality, µ(π) = 2, and the Siegel-zero exclusion.
- **Fourier/atomic certificates** (geometry): circle packing at π/(2√3) via
  rigorous interval arithmetic; universal optimality of the triangular lattice
  via Gaussian Fourier minorants; Mahler conjecture via Hermite/divided-difference
  spectral comparison.
- **Rational certification** (physics): the Laughlin gap transport is certified
  with explicit rational bounds under disorder.
- **Lesson:** when the collection proves something "impossible-sounding," look
  for the certificate. Any pipeline that can *search* for certificates (as the
  generating model apparently did) inherits this power.

### 2. Algebraic substitution + interpolation parameter
The house style behind the "impossible" TCS breakthroughs (ETH false, integer
multiplication below n log n, ω ≤ 9/4): rewrite a hard sum/expression so that
it decomposes conditionally, then interpolate along a free parameter to make the
decomposition exact. "Separate shared legs first, then count" (tensor tactics);
"recursive restructuring of data movement" (multiplication on tapes).

### 3. Compute the probabilistic quantity directly (don't derandomize by PRG)
L = RL = BPL is proved by *exactly* estimating acceptance probabilities in
log space — finite matrix inverses, conditional averaging, budgeted row
estimation — not by constructing pseudorandom generators. Same pattern in the
counting SAT algorithm: shared linear summaries + rational interpolation count
satisfying assignments in 2^(n/(log n)²).

### 4. Mean-square/duality iteration (the analytic engine)
Embed a hard sum in a family of twists → prove a mean square → Poisson-summation
into theta coefficients → iterate the dual estimate. This one engine produces
the Quasi-RH zero-free region (Re s > 11/12), the Landau–Siegel zero exclusion,
Patterson moments — and, downstream, deterministic polynomial factorization
over F_p and deterministic primality/R Tonelli–Shanks. **Uniformity over all
characters is exactly what makes the outputs effective.**

### 5. Monotone functionals along flows
Ricci flow extension (monotone "static functional" + bubble trees), Gromov-style
sweeps with entropy/degree induction for scalar-curvature inequalities, gradient
semigroup monotonicity for SK cutoff (n^{2/3} criticality), variance inequalities
in moment coordinates for log-Brunn–Minkowski. Pattern: find what increases and
prevent it from blowing up before the singular time.

### 6. Compactness + stability = rigidity
"Classification plus an L² gap yields stability" recurs in RCD spaces, Einstein
manifolds, optimal transport (sharp 1/3 stability of Brenier maps), Banach
space geometry. **Caveat:** compactness arguments are non-constructive — the
Hadwiger counterexample proof passes through analytic limits and is explicitly
*not* machine-checkable, a deliberate reliability trade documented below.

### 7. Cohomology as lattice arithmetic
The BSD cluster treats the leading-term formula as an identity of determinant
volumes between Kummer/Selmer cohomology lattices and integral analytic objects,
with auxiliary-prime switching to kill error divisors. Rank statements come from
Euler systems; exact constants from congruence bookkeeping.

### 8. Compilation embeds computation in dynamics
Navier–Stokes as computer: encode a Turing tape in positional real coordinates
(Moore generalized shifts), make it reversible via Bennett/Landauer recording
tables, realize branches by area-preserving box transport with a spatial clock,
close with the identity F = U_t + (U·∇)U − νΔU so a particle entry occurs iff
the machine halts. Group theory uses the same compiler mentality for the
Boone–Higman conjecture ("bounded compiler" into a finitely presented simple
group of type F_∞).

### 9. One master theorem → hardness/structure cluster
The Unique Games Theorem (a deterministic poly-time 3SAT → Unique Games
reduction with the right completeness/soundness) immediately yields: 2-to-1
games with perfect completeness, coloring-3-colorable hardness, Max-Cut beyond
Goemans–Williamson, the Gaussian propeller NP-hardness ratio in geometry.
Similarly the second Kahn–Kalai conjecture closes a whole threshold-theory
cluster, and Lech's conjecture + Serre positivity close a commutative-algebra
cluster including ramified mixed characteristic.

### 10. Spectral/slope dichotomies for arithmetic geometry
The CM Hodge conjecture reduces to surface periods via four-factor "switch"
relations, with descent from a Frobenius-vs-Hecke **slope 0/1 dichotomy**
obtained by counting ordinary isogeny neighbors. Same dichotomy shape appears
in the residually finite 2-group (graded-transfer detection) and Kuga–Satake
degree preservation.

---

## II. Dependency chains (findings that unlock other findings)

1. **Quasi-RH (Re s > 11/12)** → excludes Landau–Siegel zeros → uniform Hecke
   zero-free theorem → constructible auxiliary-prime tables → **deterministic
   polynomial-time complete factorization over F_p** → reproducible CAS
   factoring without randomness. (Deep analytic theorem becomes a branch of an
   algorithm's correctness proof.)
2. **Unique Games Theorem** → 2-to-1 games perfect completeness → coloring
   hardness → Gaussian-propeller geometric hardness ratio.
3. **SK spin glass program** → QAOA provably attains the Parisi ground-state
   energy (depth optimality reduced to synthesizing the classical Parisi
   formula) → guidance for quantum optimization experiments.
4. **Mixing of all orders** → pointwise multiple ergodic averages for every
   mixing system.
5. **Carenini's satisfiability threshold** (credited for priority) → this
   collection proves the random 3-SAT threshold is *computable* with explicit
   finite certificates.

---

## III. Implementability tiers

**Tier 1 — implementable now (real constants, testable):**
near-linear exact max-cardinality matching in sparse general graphs;
(1+ε) edit distance in N^{1+o(1)}; deterministic complete factorization over
F_p; quasipolynomial mean-payoff/parity game solvers; FPRAS cluster (contingency
tables, polymatroid bases, common bases); O(log²k) k-server on finite metrics;
exact uniform sampling of contingency tables; the L=BPL estimator library;
polynomial mixing of the switch chain; linear-variance random k-SAT hitting
times.

**Tier 2 — implementable in principle, astronomically bad constants:**
integer multiplication at κ = 2^−182 below n log n (explicit but useless at any
physical size); subset-sum 2^{0.49n}; exact #k-SAT counting 2^{n/(log n)²};
the UGC reduction blowup.

**Tier 3 — asymptote-only (existence, no competitive crossover):**
ω ≤ 9/4 matrix multiplication; rectangular matrix multiplication; depth-3
circuit lower bounds; most §-asymptotics.

**Tier 4 — negative results (due-diligence tools, kill product ideas):**
H10 over Q undecidable (no universal rational-Diophantine solver, ever);
NP-hardness clusters; QMA-hardness of continuum Coulomb energy; exponential
state lower bounds for two-way automata; the eth-free-but-hard landscape.

**Tier 5 — advisory (changes strategy, not code):**
quantum factoring over a fixed finite gate set with probability one (sharpens
post-quantum migration timelines); QAOA-SK optimality; uniform Laughlin gap
stability (materials/quantum simulation); entanglement with zero distillable
key in local dimension 10 (QKD security margins).

---

## IV. Reliability notes

- The README itself states results are at **different verification stages**;
  "some of the unformalized results could have issues."
- Demonstrated in-repo: three Hodge-conjecture papers (K3 products, split
  abelian eightfolds, Kuga–Satake algebraicity) were **withdrawn Oct 6, 2026**
  for a sign error in a shared stabilization-trace double-point argument —
  a self-correction event worth knowing before building on any specific claim.
- Some results credit external priority (Carenini for the SAT threshold),
  suggesting a mixed provenance; two writeups (zeta zero-free region, CM Hodge)
  were human-edited.
- **Heuristic:** results with Lean formalizations or explicit numerical
  certificates are the safest base; results proved through compactness/
  ultraproduct limits (e.g., Hadwiger counterexample) are the least checkable.

---

## V. How to use this map

- Per-family detail (finding / approach / lesson): open the subject report file.
- Original PDFs: `math/preprints/<title>-<date>/`.
- Formalization status per paper: `math/lean/formalization.yaml`.
- The catalogue's own narrative: `math/overview.pdf`.
