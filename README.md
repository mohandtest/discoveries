# math-discovery

Independent analysis, mapping, and first-executable-artifact work on
[openai/math](https://github.com/openai/math) — OpenAI's September–October 2026
release of 721 machine-generated mathematical manuscripts (373 result families,
~42% Lean-formalized), produced by an internal frontier model.

The `math/` checkout is **not included** in this repository (gitignored; it is
~3.7 GB). Clone it separately if you want the source papers:

```sh
git clone --depth 1 https://github.com/openai/math.git
```

## What we've worked on

### 1. `discovery-map/` — mapping all 373 result families

A full map of the collection: every result family with its **finding**, the
**proof approach** used, and the **transferable lesson**. Built by extracting
the catalogue (`overview.tex`, `CONTENTS.md`) into per-subject data files and
analyzing each subject cluster, with deep-dives into the actual preprint PDFs
for the most significant results.

- **`README.md`** — the synthesis: the ten recurring proof techniques across
  all 17 subjects, the dependency chains between discoveries (e.g.,
  zero-free region → deterministic polynomial factorization over F_p),
  implementability tiers, and reliability notes (including OpenAI's own
  retraction of three Hodge-conjecture papers for a sign error).
- **`report_*.txt`** (8 files) — per-subject-cluster reports covering all 373
  families with Finding / Approach / Lesson entries.
- **`subject*.txt`** (17 files) — extracted catalogue data, one file per subject.

Key conclusions: the collection's dominant technique is **certificate-based
proof** (finite checkable artifacts replacing intricate arguments); most
headline results are asymptote-only (ω ≤ 9/4, integer multiplication with
κ = 2^−182), but a substantial cluster is genuinely implementable; nobody in
the public conversation was executing the algorithms — everyone was verifying
the proofs.

### 2. `fpras-benchmark/` — first implementation of the perfect-matching FPRAS

The cleanest test of the "runnable-looking results" thesis: OpenAI's September
2026 FPRAS for counting perfect matchings in **general graphs** (a 20-year-open
problem; Jerrum–Sinclair–Vigoda handled only the bipartite case in 2004) had,
at time of work, a community-simplified proof (arXiv:2610.26803) but **no
implementation anywhere**. We implemented it and benchmarked it.

- **`README.md`** — full write-up: what was implemented, verified, and measured.
- `chain.py` — the paper's Markov kernel (two-edge switches + cycle exchanges
  on discrepancy cycles), unit-verified: exact stationary law (TV = 0.0014),
  irreducibility on the chordless 6-cycle, exact weight-product preservation.
- `anneal.py` — plain annealing counter with the paper's outer schedule and
  practical parameters (**the practical winner**).
- `exact.py` — subset-DP exact counter, used as ground truth.
- `windowed.py`, `hierarchy.py`, `awindow.py` — faithful structural variants
  of the paper's replication machinery (documented negative results).
- `test_chain.py`, `bench*.py`, `results.csv` — tests, experiment sequence,
  benchmark table.

Headline numbers (pure Python, laptop): correct to 0–3% relative error through
n ≈ 24 on every graph family tested — including the theory's pathological
chordless cycles — in seconds, where exact dynamic programming is already
infeasible (2²⁴ states). Three scientific findings: (1) the proof's worst-case
constants (~10⁷³ replicas, ~17,000 levels) are pure armor — q = 2 and ~10³–10⁵
steps suffice in practice; (2) the naive simplifications genuinely fail
(same-weight replica exchanges homogenize and freeze the ensemble, returning
zero), so the paper's structure is load-bearing *as a proof* but wrong *as a
design*; (3) the meta-thesis is calibrated — the repo's algorithms are runnable,
but only after a surgery step (identify load-bearing components) that no
automated pipeline currently performs.

## Meta-thesis

The scarce artifact in the openai/math ecosystem is not proof verification
(the community and OpenAI-funded workshops are doing that) — it is
**constants reports**: implementations that answer "does this algorithm
actually run, and at what cost?" This repository contains the first one, plus
the map that ranks which results deserve the next ones.

## Reproducibility

- Discovery map: derived entirely from the public `openai/math` checkout.
- FPRAS benchmark: `python3 test_chain.py` (unit tests), then
  `python3 bench.py` … `bench7.py` (experiments). Pure Python 3, no
  dependencies beyond the standard library.
