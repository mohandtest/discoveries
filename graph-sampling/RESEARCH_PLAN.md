# Network null-model research: plan and first exact result

## Goal

Evaluate whether practical diagnostics can identify unreliable degree-preserving graph samples and changes to downstream network conclusions. Develop and assess tools only after establishing correct targets and comparisons. This is a research plan, not a claim of a new algorithm or a validated application.

## First exact audit

Run `python3 triangle_null_study.py`. It enumerates all 70 labeled simple undirected 2-regular graphs on six vertices. Ten are two disjoint triangles; the other 60 are six-cycles. The upper-tail probability of two triangles under the uniform fixed-degree null is 10/70 = 0.142857. If the symmetric kernel is observed only at successful transitions, its stationary distribution is weighted by the number of available transitions and the corresponding tail is 0.2. This is a known pitfall, not a novel result.

Starting from the two-triangle graph, the exact finite-time triangle tail is 0.144592 after 50 attempted steps, close to its limiting value, while the full distribution still has total-variation distance 0.144758. Agreement on a single statistic does not establish global mixing. This calculation includes rejected and lazy steps. The graph is synthetic, and a 0.143 tail is not significant at a 0.05 threshold.

## Research sequence

1. Extend exact enumeration to heterogeneous degree sequences. Verify enumeration against independent brute force for tiny graphs, and test transition row sums, symmetry, connectivity, graph invariants and known tails.
2. Define candidate diagnostics before evaluating them. Compare them with exact total-variation distances and exact motif-tail probabilities over multiple starting graphs, degree sequences and budgets. Report both false reassurance and unnecessary extra computation.
3. Evaluate larger examples with independently initialized chains, multiple summaries and sensitivity to increasing burn-in and spacing. No diagnostic by itself proves convergence. Compare matched null models and attempted-step budgets with a well-documented established implementation.
4. Apply the method to a documented public network, starting with an undirected, unweighted social or biological network. Predefine a question, statistic, null model, preprocessing, and sensitivity analysis. Quantify Monte Carlo uncertainty and dependence. Degree preservation alone does not preserve connectivity, edge weights, direction, temporal structure or other domain constraints.
5. Only extend to directed, bipartite, weighted or time-dependent data with separately specified state spaces, appropriate moves and validation. Reusing the present kernel for these networks is invalid.

Save input provenance, versions, seeds, attempted and accepted moves, runtime, raw results, and code. Report limitations and negative results. Avoid novelty, significance, accuracy or speed claims until supported by reproducible evidence and comparison to prior work.

## References

- Fosdick et al., [Configuring Random Graph Models with Fixed Degree Sequences](https://doi.org/10.1137/16M1087175), SIAM Review, 2018.
- Hobson et al., [A guide to choosing and implementing reference models for social network analysis](https://doi.org/10.1111/brv.12775), Biological Reviews, 2021.
- [NetworKit randomization tutorial](https://networkit.github.io/dev-docs/notebooks/Randomization.html), an existing implementation and baseline to investigate.

The current sampler uses uniform vertex quadruples and is not established to be the chain covered by OpenAI/math result 131. No claimed polynomial mixing bound is inherited here.

## Implemented iteration (2026-11-10)

[STUDY_REPORT.md](STUDY_REPORT.md) records the completed production-kernel audit,
three-sequence repeated calibration, actual NetworkX proposal-loop comparison,
and three public-data examples. These address the initial research sequence on
small cases; they do not resolve general convergence, rare tails or domain
constraints. The diagnostic gate produced both false reassurance and poor power.
Further studies should compare established convergence methods, separate burn
from spacing changes, and specify domain constraints before extending graph type.
