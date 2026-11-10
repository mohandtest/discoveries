# Research review and application choices

Sources checked 2026-11-10. This work implements existing fixed-degree null
models and audits their numerical behavior; it makes no novelty claim.

[Fosdick et al. (2018)](https://arxiv.org/abs/1608.00607) distinguish graph
spaces, labels and proposal rules. Here the target is uniform over **labeled,
simple, undirected graphs with every vertex's exact degree fixed**. Connectivity
is unrestricted. Stub pairing followed by deleting loops/parallel edges changes
degrees and is not a matched substitute. Accepted-transition-only observations
also change stationary weights: the existing exact six-node audit gives a
triangle tail of 1/5 instead of the uniform 1/7. The production sampler retains
rejections. No mixing theorem from OpenAI/math #131 is inherited.

[Hobson et al. (2021)](https://doi.org/10.1111/brv.12775) explain why reference
models must follow the research question and observation process. Our question
is descriptive: does this recorded graph have more triangles than graphs with
the same labeled degree sequence? It is not a test of a social mechanism.
Choosing these datasets and statistics was exploratory; the resulting tails are
not confirmatory scientific p-values. Triangles are the primary public-data
summary; other observables are diagnostic/sensitivity summaries, without
multiple-testing-adjusted discoveries.

[Dutta, Fosdick & Clauset (2023 version)](https://arxiv.org/abs/2105.12120)
already study sampling gaps and convergence detection using assortativity.
Their [ConfigModel_MCMC](https://upasanadutta98.github.io/ConfigModel_MCMC/)
supports multiple configuration spaces with existing convergence heuristics.
It was reviewed, not installed or benchmarked here. Our degree-product sum is
an affine function of degree assortativity when endpoint variance is nonzero
and degrees fixed. On regular graphs it is constant and uninformative.

[NetworkX 3.5 double_edge_swap](https://networkx.org/documentation/networkx-3.5/_modules/networkx/algorithms/swap.html)
is the implemented comparison. Its ordinary API requests successful swaps and
its attempt counter excludes early continues. `nx_baseline.py` instead traces
the actual installed proposal loop and stops before the next iteration, retaining
all rejected proposals. It fails on a different version or an existing tracer.
The sampler code is not copied or reimplemented. Production chooses distinct
edge pairs; NetworkX chooses degree-weighted sources then neighbors, equivalent
to oriented edges with replacement. Exact tests find
`Q = ((m-1)/m) P + I/m` on 91 graphs: same target, slightly different clock.
Budgets match primitive proposal iterations, starts, observables, sample counts,
hardware, and connectivity constraints; trajectories and random draws do not
match. Timings include instrumentation, so no relative-speed claim is warranted.

[NetworKit randomization](https://networkit.github.io/dev-docs/notebooks/Randomization.html)
offers edge switching and Global Curveball, including large-network-oriented
implementations. Its guidance of sweep counts is empirical, not a certificate
for these data. It was reviewed, not benchmarked. There is no demonstrated
performance advantage over these existing tools. A useful role for this project
is an inspectable validation harness and a small-network teaching/prototyping tool.

[Vehtari et al. (2021)](https://arxiv.org/abs/1903.08008) discuss flaws of basic
R-hat and improved rank/folded diagnostics. Our **ordinary split R-hat is not
their rank-normalized implementation**. Batch ESS is a simple nonoverlapping
sqrt(n) batch-means estimate, capped at retained sample count, not bulk/tail ESS.
These cheap warnings are evaluated against exact truth and intentionally do not
produce a convergence certification. Constant traces return unknown, not success.

| Candidate application | Evidence/data fit | Decision and unresolved constraints |
| --- | --- | --- |
| Historic friendship/marriage graphs | Public simple undirected inputs, supported directly by state space | Implemented karate and Florentine. Useful negative/control cases; degrees alone give similar triangle counts. Missing tie strength, family attributes and history limit interpretation. |
| Animal association topology | Public dolphin network has matching graph type and strong descriptive triangle contrast | Implemented. Most promising demonstration here. Sightings, group events, geography and association threshold are not modeled; raw observation data would be needed for a behavioral claim. |
| Protein interactions | Degree-preserving references have established use, e.g. [Friedel & Zimmer (2007)](https://doi.org/10.1186/1471-2105-8-297) | Plausible next study, not validated here. Bait/prey assay restrictions, confidence scores and study bias require a specified release/assay and forbidden-edge constraints. No biological-function inference from these examples. |
| Neural/metabolic/regulatory networks | Common C. elegans data on the [Newman page](https://websites.umich.edu/~mejn/netdata/) are directed and weighted | Deferred. Discarding these attributes changes the question. Electrical-only connectomes could be a future separately specified study; spatial restrictions remain. |
| Affiliations, ecological plant–pollinator graphs | Naturally bipartite; four-cycles meaningful | Deferred: unrestricted switches can violate the partition. Davis southern women was considered but not silently projected or used with this null. |
| Infrastructure/spatial resilience | Public power-grid topology exists | Deferred: degree-only rewirings ignore geography, engineering constraints and connected operation. Components are diagnostic only; no resilience claim is supported. |

The current Python implementation recomputes statistics and is designed for
small networks. Exact state enumeration is exponential; our strongest guarantees
are finite-state checks on tiny cases. An evidence-supported next extension is
additional heterogeneous exact calibrations and external diagnostics/baselines,
followed by a domain-constrained model with its own irreducibility and stationary
target audit. More samples of an inappropriate null do not fix model mismatch.
