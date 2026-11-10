# Degree-preserving graph sampling prototype

Research starter for sampling **labeled simple undirected graphs with a fixed degree sequence**. Runs locally with Python 3 and no dependencies. This is independent of the overnight perfect-matching benchmark.

## Practical null-model study

Start with [NETWORK_PROTOTYPE.md](NETWORK_PROTOTYPE.md) for the standard-library CLI,
[STUDY_REPORT.md](STUDY_REPORT.md) for results and reproduction, and
[RESEARCH_REVIEW.md](RESEARCH_REVIEW.md) for prior work and application choices.
The production edge-pair sampler now has exact audits, a matched-null NetworkX
comparison, repeated uncertainty calibration, and three documented public inputs.
The findings include diagnostic failures and unresolved rare-tail probabilities.

## What is implemented

- A **lazy 4-vertex edge-switch Markov chain**. Select four distinct vertices uniformly, choose one of the three disjoint pairings and one alternative pairing, and swap the two edges only if the source edges exist and the destination edges are absent. Otherwise hold. A separate 1/2 hold coin ensures aperiodicity.
- Exact enumeration of **small d-regular labeled graphs**, validating every reachable state's degree sequence.
- Exhaustive connectivity and transition-reversibility checks for small instances.
- An **exact finite-state probability propagation** benchmark computing total-variation (TV) distance to the uniform distribution from a fixed initial graph. Unlike sampled histogram TV, this isolates actual convergence of the kernel.

The implementation intentionally uses *uniformly chosen vertex quadruples*, not the usual uniformly selected **edge pairs** of a standard double-edge-swap implementation. The result-family #131 polynomial mixing theorem must **not** be assumed to apply unchanged to this specific proposal distribution without a comparison proof. The code demonstrates finite-state behavior, not a general mixing-time guarantee.

## Run

```sh
cd graph-sampling
python3 -m unittest discover -v
python3 degree_switch_probe.py --n 6
python3 degree_switch_probe.py --n 8 --samples 10000 --thin 5
python3 exact_mixing.py --n 6 --degree 2 --steps 0 10 100 1000
```

## Reproduced baseline (seed 42)

| Experiment | Result |
|---|---|
| 6 vertices, degree 2 | 70 labeled graphs |
| 8 vertices, degree 2 | 3,507 labeled graphs |
| 6 vertices, degree 2, exact TV at step 0 | 0.985714 |
| 6 vertices, degree 2, exact TV at step 100 | 0.019548 |
| 6 vertices, degree 2, exact TV at step 1,000 | effectively 0 |

The empirical TV estimate from a single correlated sample histogram additionally contains **finite-sample noise**. It is not a mixing-time estimate. Exact mixing evaluates the full probability distribution but only scales to very small graphs.

## Research questions

1. How do proposal choice, graph size, and degree heterogeneity affect accepted switches per second?
2. How accurately does empirical TV reflect true mixing on small graphs? Establish a finite-sample floor using independent uniform draws.
3. Compare against established implementations (for example NetworkX double-edge swaps) **under matched workloads and carefully distinguished proposal kernels**.
4. Extend to nonregular feasible degree sequences with exhaustive small-instance validation.

## Sources and scope

Motivated by **result family 131** in the [OpenAI/math](https://github.com/openai/math) catalog. This is an independent exploratory implementation, **not** a verified reproduction of the paper's exact transition kernel or its stated polynomial mixing bound. No performance or novelty claims are made.
