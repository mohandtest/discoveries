# Assessment of the fixed-degree prototype

The prototype is useful for small-network structural exploration and testing
sampling implementations. It is not a validated scientific testing service.
The most promising demonstrated application is **descriptive triangle structure
in recorded animal associations**. Domain mechanisms and rare-tail reliability
remain unresolved. All computations here were serial, local validation; no
remote server was contacted and no running benchmark was modified.

## What was built and tested

The original standard-library CLI remains usable. It now reports accepted and
attempted counts, runtime/Python/source provenance, ordinary split R-hat,
descriptive batch ESS, and an unknown tail MCSE when every indicator is identical.
It retains the historical basic R-hat field for compatibility. Its default
initialization is still the observed graph; the separate public-data runner
provides a second initialization strategy.

`production_audit.py` enumerates actual calls to `network_null.attempt` for every
proposal from every graph in six selected degree sequences: **133 states**.
Exact rational matrices have unit row sums, symmetry, degree preservation and
connected support. Tests independently enumerate all possible edge subsets and
check every possible four-edge-difference transition. Cases include regular,
heterogeneous, complete/frozen and matching graphs. These are exhaustive within
the selected sequences, not over all degree sequences. Exact floating probability
propagation reports worst-start TV and multiple-statistic tail errors at
0, 1, 5, 10, 50 and 100 attempts.

A separate exhaustive optional test drives the **installed NetworkX code** with
scripted random proposals for every oriented edge pair in 91 small graphs.
Both kernels have the same stationary target but different self-loop mass;
this is a matched-null/attempt-budget comparison, not identical random walks.
Tests also exercise frozen graphs (no hanging), known observable values,
dependence warnings and sampled six-node frequencies. The complete suite has
**16 passing tests** under the Python/NetworkX versions recorded in `results/environment.json`. Without optional NetworkX, its two baseline
tests skip and the core tests remain runnable.

## Results and negative findings

[Measured tables](results/MEASURED_RESULTS.md) are generated from saved results,
not manually transcribed. [Public raw draws](results/public_study/samples.csv),
[public summary/config](results/public_study/summary.json),
[exact matrices and distributions](results/production_exact.json),
[calibration raw draws](results/calibration/raw.csv), and
[calibration summary](results/calibration/summary.json) are retained.

For public inputs, the primary exploratory statistic was triangles. Additional
observables are non-induced four-cycles, number of components (including
isolates), edges shared with the observed graph, and sum of endpoint degree
products. Components permit disconnected graphs rather than discarding them.
Four-cycle counts include chorded cycles; degree-product is a surrogate for
assortativity only when endpoint degree variance is nonzero.

Each dataset/engine/budget uses four seeded chains, alternating observed and
Havel–Hakimi realizations **with each label's degree checked**. These are two
starting structures, not four independent stationary starts or optimized extremes.
A sweep is `m` primitive attempted proposals. Short: 20 burn sweeps, 2 between
samples. Long: 80 burn sweeps, 8 between samples. Each retains 200 samples/chain.
Seeds and starts are saved. Seeds are reused across budgets and engines; no
independent-error z-scores are claimed for their differences.

- Karate: observed 45 triangles, null means 39.30–39.58 and exploratory upper
  tails 0.111–0.120. This is a useful negative example, not evidence of excess
  triangles at a conventional 5% reference threshold.
- Florentine: observed 3 triangles, null means 2.52–2.62 and tails 0.493–0.523.
  Degrees explain a similar triangle count under this null. The selected subset
  is not a census of all families or a model of political/social mechanisms.
- Dolphins: observed 95 triangles versus null means 34.00–34.24. Every run had
  zero upper-tail hits in 800 correlated retained draws. This substantial
  descriptive contrast is stable across these budgets and implementations.
  **The tail probability is unresolved**: no zero-probability claim, binomial
  bound on correlated samples, or calibrated significance claim follows.

Exact mixing varies even among tiny cases. At 50 production attempts the
worst-start TV is about 0.00000229 on degree-2 six-node graphs but 0.00588 on
`[4,3,3,2,2,2]`. Tiny-graph budgets cannot be transferred to public networks.
Full-distribution convergence and agreement of one observable are different.

Repeated calibration covers three degree sequences, both triangle-extreme
starts, three burns, 100 replicates/group, four chains and 40 draws/chain
(spacing one): **1,800 trials and 288,000 raw measurements**. A fixed toy gate
requires ordinary split R-hat ≤ 1.05 for each statistic that exact enumeration
says varies; if such a statistic is constant in the trajectories it fails.
This exclusion is **oracle-assisted**, deliberately not a deployable criterion.
Time-averaged TV refers to the expected distribution of retained states, not
empirical histogram TV or TV at the burn endpoint.

On the regular case with no burn, gate passes occurred in 10/100 and 12/100
trials despite time-averaged TV 0.0903 and 0.0844 (> the prespecified 0.05 failure
threshold). At burn 50 it passed only 5/100 and 10/100 despite TV below 0.0000002.
On both heterogeneous cases it never passed, even for near-stationary
initialization distributions. This gate has both false reassurance and very
poor power; it should not select budgets automatically.

Nominal 95% Student-t intervals for the exact triangle mean, using four chain
means (3 degrees of freedom), covered truth in **82–99 of 100 trials per group**.
These finite repeated-run rates have sampling error (at 95/100, binomial SE
about 2.2 percentage points); they are not universal calibration estimates.
Common starts, short correlated chains, nonnormal means and burn bias can all
matter. Even after burn 50, the regular extreme groups gave 89/100 and 96/100
coverage. More retained draws and a small R-hat do not establish reliable MCSE.
Batch ESS is descriptive only and does not correct these intervals.

## What remains unresolved

There is no general mixing bound, scalable exact validation, rank-normalized
R-hat/tail ESS implementation, rare-event estimator, or scientifically justified
connected/weighted/directed/bipartite/spatial null. Public trials do not isolate
burn and spacing effects because both budgets increase together. Four chains
provide few degrees of freedom for SE estimation. All public examples are small
convenience datasets. No claim about production-scale performance is supported;
NetworkX tracing overhead rules out speed conclusions.

The [research review](RESEARCH_REVIEW.md) evaluates existing implementations and
applications in social, protein, neural, affiliation and infrastructure networks.
Directed C. elegans and bipartite Davis data were deliberately deferred. A
protein-interaction application needs an assay-specific graph and constraints;
a dolphin behavioral application needs original observation/spatial/group data.
These require new modeling and validation, not just more runs of this kernel.

## Reproduce

Run from `graph-sampling/`. Saved inputs require no network. NetworkX is optional
for the original CLI/exact audit, mandatory for the research runner and calibration.
Use a new output path; experiment writers refuse to replace existing results.
Generated summary values/raw draws are deterministic for the recorded Python
and NetworkX versions, aside from runtime fields. Cross-version RNG details may
change trajectories. `results/environment.json` records versions, base commit,
source and artifact hashes; it describes local source hashes, not just base HEAD.

```sh
python3 -m unittest discover -v
python3 -m venv work/venv
work/venv/bin/pip install -r requirements-research.txt
work/venv/bin/python -m unittest discover -v
python3 production_audit.py work/reproduced_exact.json
work/venv/bin/python calibration_study.py work/reproduced_calibration
work/venv/bin/python run_research.py work/reproduced_public
python3 analyze_research.py
python3 verify_results.py
# Optional: refresh environment.json after your own experiment run.
work/venv/bin/python record_environment.py
python3 network_null.py data/dolphins.edgelist --chains 4 --burn 12720 --samples 200 --thin 1272 --csv work/dolphin_cli.csv > work/dolphin_cli.json
```

`verify_results.py` checks recorded hashes, rational matrices and raw-to-summary
consistency offline. It intentionally fails if recorded sources/results change.
`analyze_research.py` regenerates the table from the committed canonical result
paths; compare new directories with those paths, excluding timing fields.
`prepare_data.py` and [data provenance](data/PROVENANCE.md) describe optional
source regeneration. `work/` is ignored. No full upstream checkout, dependency
environment or executable binary is included in the results.
