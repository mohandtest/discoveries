# Mixing-curve campaign results (2026-11-10)

Measured constants for the uniform-quadruple lazy switch chain — the exact
kernel analyzed by OpenAI/math #131 (*Polynomial mixing of the switch chain
for every graphical degree sequence*, TV(1/4) ≤ 2n⁸) — plus the real-network
applications that turn the constants into practice.

Tooling: `switch_exact.c` (exact enumeration of all labeled graphs with a
degree sequence + exact transition graph + exact probability propagation;
fork-parallel on the server, 22 cores). **Verification:** the C reproduces
`exact_mixing.py` — an independent Python implementation — at n=6 d=2
(70 states, TV@10 = 0.628441, TV@100 = 0.019548) *and at n=8 d=2*
(3,507 states: TV@50/100/250/500 = 0.687280/0.379801/0.056616/0.001909,
identical to six digits); state counts match `enumerate_degrees`
(17/27/15) and the labeled 2-regular sequence (70/3,507/30,016/286,884 at
n=6/8/9/10); the n=6 triangle-study (a third implementation) agrees; and
the complement symmetry d↔n−1−d is observed exactly (n8d3 ≡ n8d4:
19,355 states, identical mixing times).
Campaign run on the 24-core server, 22 cores per case, canonical + 32 random
starts (8 at the n=12 frontier). "t(1/4)" = first attempt count at which
TV-to-uniform ≤ 1/4, maximized over sampled starts (not all starts — the
proven bound is worst-case over everything).

## 1. Exact mixing constants (ladder results/mixing/)

Complement symmetry: the chain on (n, d) is isomorphic to the chain on
(n, n−1−d) (a switch in G is a switch in the complement's absent edges), so
d and n−1−d cases coincide exactly — observed: n8d3 ≡ n8d4 (states 19,355,
t = 250/250).

| case | states | t(1/4) | t(0.05) | proven 2n⁸ | over-provision |
|---|---:|---:|---:|---:|---:|
| n=6 d=2 | 70 | 50 | 100 | 3.36e6 | 67,185× |
| n=6 [3,3,2,2,1,1] | 17 | 50 | 250 | 3.36e6 | 67,185× |
| n=6 [3,2,2,1,1,1] | 15 | 50 | 250 | 3.36e6 | 67,185× |
| n=6 [4,3,3,2,2,2] | 27 | 50 | 100 | 3.36e6 | 67,185× |
| n=8 d=2 | 3,507 | 250 | 500 | 3.36e7 | 134,218× |
| n=8 d=3 ≡ d=4 | 19,355 | 250 | 250 | 3.36e7 | 134,218× |
| n=9 d=2 | 30,016 | 250 | 500 | 8.61e7 | 344,374× |
| n=9 d=4 (self-compl. class) | 1,024,380 | 250 | 500 | 8.61e7 | 344,374× |
| n=10 d=2 | 286,884 | 500 | 1,000 | 2.0e8 | 400,000× |
| (n=10 d=3/d=4, n=11, n=12, heavy-tail rows: in flight — table finalized when the ladder completes) | | | | | |

**The sweep law.** Normalizing by C(n,4) — the number of quadruples the
kernel proposes from, i.e. the proposal-space size — collapses the
measurements (t(1/4)/C(n,4)):

| | n=6 | n=8 | n=9 | n=10 |
|---|---|---|---|---|
| d=2 | 3.33 | 3.57 | 1.98 | 2.38 |
| d=3 / d=4 | — | 3.57 | 1.98 (d=4) | in flight |
| heterogeneous | 3.33 | in flight | | |

**t_mix(1/4) ≈ 2–4 passes over the proposal space, uniformly** across
every completed case — all densities, heterogeneous anchors included.
The practitioner unit is therefore "quadruple sweeps," not raw attempt
counts: a handful of sweeps reaches TV ≤ 1/4 on all tested sequences,
versus the folklore "10·m edge swaps" and the proven 2n⁸ (which in sweep
units is ~n⁴/3 — an over-provision growing like n⁴). Heterogeneous
sequences share t(1/4) with regular ones but converge slower in the tail
(t(0.05) up to 16.7 sweeps at n=6) — small lumpy state spaces.

**Pre-registered predictions** (t(1/4) = 2–4 × C(n,4); t(0.05) ≈ 2×
t(1/4) for dense classes, up to ~5× for heterogeneous ones), stated
before the in-flight rows land:

| case | C(n,4) | predicted t(1/4) | predicted t(0.05) |
|---|---:|---:|---:|
| n=10 d=3 / d=4 | 210 | 420–840 | 840–1,700 |
| n=11 d=2 | 330 | 660–1,320 | 1,300–2,600 |
| n=12 d=2 | 495 | 990–1,980 | 2,000–4,000 |
| n=8 het (hub d=6) | 70 | 140–280 | 300–1,400 |
| n=10–12 het (heavy tail) | 210–495 | 420–1,980 | 800–10,000 |

**Evidence-based cap for the giant rows** (decided 11:20–11:35 UTC,
before any of their outcomes): exact propagation is memory-bandwidth-bound
— n10d3's canonical start measured ~7.6 s/step at ~12M states, and n10d4
enumerated at **66,462,606 states** (~44 s/step at 22 workers → t(1/4)
alone would need 5–10 h). For the giant classes the campaign therefore
measures **t(1/4) only** — the theorem's own threshold and the sweep
law's core claim — via a `--t25only` mode at reduced worker counts
(bandwidth splits ~4–5× faster per worker): n10d4 (8 starts) and n=12
d=2 (4 starts) land inside the 4 h rerun bound. t(0.05) for these rows
is documented by the sweep-law extrapolation (t(0.05) ≈ 2× t(1/4)); full
t(0.05) propagation at these sizes is a measurement-infrastructure
limit (10–30 h per start), not a chain property: the sampler itself
runs at ~200k attempts/s regardless of n. n12het is documented by
extrapolation only.

Early shape: t(1/4) grows slowly — 50 (n=6) → 250 (n=8–9) → 500 (n=10) —
tracking C(n,4), **not** n⁸. The practical reading: *a few hundred to a
few thousand attempted switches bring the chain to TV ≤ 1/4 on all
tested sequences — the proven 2n⁸ is armor against adversarial degree
sequences, not guidance for burn-in.* Rows that land outside these
bands refute the sweep law and will be reported as such.

## 2. Dolphins tail quantified (results/dolphins_tail.json)

The validation study's unresolved zero-hit tail, now measured with
16 chains × 2.5M attempted switches (800,000 retained draws):

| | value |
|---|---|
| observed triangles | 95 |
| null mean ± SD | 34.28 ± 4.94 |
| null max in 800k draws | 59 |
| draws ≥ 95 | **0 / 800,000** (empirical tail < 1.25×10⁻⁶) |
| z of observed | **12.3** |
| normal-tail extrapolation | ~10⁻³⁵ (assumes approximate normality; the empirical max supports a far-left tail) |

**Real-world reading:** dolphin association structure is not explained by
the degree sequence alone — the observed clustering is ~12 SD beyond the
degree-preserving null, unreachable in 800k draws. Contrast row (karate,
400k draws): observed 45 vs null 39.34 ± 4.55, tail **12.6%** (z = 1.2) —
degrees *do* explain the karate club's celebrated clustering. Same method,
two textbook networks, opposite conclusions.

## 3. Burn-in vs thinning isolated (results/burn_spacing.json)

The validation study moved burn and spacing together; this grid separates
them (8 chains × 200 draws/cell; reference = the long-run means above):

- **Burn-in barely matters on these networks**: bias stays within ±0.4
  triangles for burn 0 → 125,000 attempted switches (dolphins), ±0.5 (karate)
  — consistent with the measured t(1/4) of hundreds of attempts: the
  observed-graph start is near-stationary almost immediately at these
  sizes/densities.
- **Spacing matters**: thin=1 (consecutive states) biases karate by −1.39
  (~5× the between-chain MCSE) — consecutive retained states are strongly
  autocorrelated (a single switch changes the triangle count by ≤ 2).
- Practical rule: on sparse real networks, spend budget on thinning and
  chains, not burn-in; revisit only if a case is atypical (very dense,
  near-frozen, or strongly structured).

(Note: the burn_spacing.json `bias_vs_ref` fields used reference means
34.0/39.4; the tables above restate bias against the measured long-run
means 34.28/39.34 — differences are within the MCSEs and no conclusion
changes.)

## 4. Throughput

Python production kernel (edge-pair proposal, set-based adjacency):
161k attempts/s (dolphins, n=62 m=159) and 200k/s (karate, n=34 m=78) on
one server core. Combined with the mixing constants: **a full 800k-draw
null study costs ~5 minutes single-core in pure Python** — the switch
chain is not a computational bottleneck at social-network scale.

## Caveats (carried from the study, still true)

- t(1/4) is maximized over *sampled* starts (canonical + 32 random), not
  all starts; the proven bound is worst-case over all starts and all
  graphical sequences. Our measurements bound practice, not the theorem.
- Exact enumeration bounds the ladder to sparse/moderate sequences at
  n ≤ 12; dense large-n cases (and the adversarial sequences the 2n⁸
  bound protects against) are not measured.
- The dolphins normal-tail extrapolation assumes approximate normality;
  the empirical result (0/800k, max 59) is the load-bearing statement.
- Both public networks are small convenience datasets; no claim about
  production-scale performance is made beyond §4.
