# Static degree-sequence sampling guarantees

Status: analytical research note, not a benchmark or a deployed sampler.
No empirical speedup or new universal spectral-gap theorem is claimed.

## Inputs and assumptions

The state space Ω consists of all labeled simple undirected graphs with the
same graphical degree vector d. Connectivity is unrestricted. Let n be the
number of vertices, m the number of edges, and L the unweighted Laplacian of
the graph on Ω whose edges are valid two-edge switches.

We use the published follow-up [Sharp spectral gaps for the switch and
Curveball chains](https://github.com/sevenevesai/SharpSwitchGap), conditional
on its theorems: the first nonzero eigenvalue of L is at least 2, and the
sum of pair conditional-projection complements has gap at least 2.
These are prior results, not independently reproved here. The original
OpenAI/math #131 bound is 2n^8 for the lazy uniform-quadruple chain at TV 1/4.

For singleton Ω return the only realization without sampling.

## 1. Exact kernel comparison

The existing degree_switch_probe.py chooses a quadruple, one of three source
pairings, one of two destination pairings and a fair hold coin.
Each valid directed switch has probability 1/(12 C(n,4)), so its transition
matrix is I-L/(12 C(n,4)). Its relaxation time is at most 6 C(n,4).

The existing network_null.py selects two distinct edges and one of two
alternative pairings. Each valid directed switch has probability
1/[m(m-1)]. The kernel is symmetric but is not explicitly lazy. Add an
independent fair hold coin: P=I-L/[2m(m-1)]. The lazy kernel is positive
semidefinite, reversible and irreducible by switch connectivity. Its
relaxation time is at most m(m-1).

These guarantees refer to a proposed lazy variant, not a silent change
to the existing CLI.

## 2. Disjoint-edge proposals

Let D=C(m,2)-sum_v C(d_v,2). Distinct edges share at most one endpoint,
so D counts unordered vertex-disjoint pairs and depends only on d.

For an edge uv, w(uv)=m-d_u-d_v+1 is its number of disjoint partners.
Select the first edge with probability w/(2D), then a uniform disjoint
second edge. Every ordered pair has probability 1/(2D); every unordered
pair has probability 1/D. Choose one of the two rewirings uniformly,
retain invalid proposals as holds, and apply a fair hold coin.

Every valid transition has probability 1/(4D), and so P=I-L/(4D).
The relaxation bound is 2D. The proposal can alternatively be implemented
by rejection of shared-endpoint pairs before choosing a rewiring, since
the rejection normalizer D is constant. Do NOT condition on successful
rewirings: that normalizer need not be constant.

Run on the graph or its complement, whichever has smaller D. Complementation
is a bijection of state spaces and preserves switch adjacency. The resulting
relaxation bound is 2 min(D,D_complement). A dense complement need not be
materialized if it is not selected. If either D is zero, no valid switch
exists and switch connectivity implies a singleton state space.

The exact off-diagonal clock ratio relative to the original quadruple
kernel is 3 C(n,4)/D. This is not a wall-clock speedup. Indexed weighted
selection is a future implementation option: updating weights is local,
but efficient uniform selection of a disjoint second edge still needs an
appropriate data structure and cost analysis.

## 3. Pruned pair-neighborhood heat bath (Curveball)

For vertices u,v let A=N(u) excluding N(v) and v, and B=N(v) excluding
N(u) and u. Preserve common neighbors and the edge uv. Uniformly choose
|A| vertices from A union B as new exclusive neighbors of u; the rest
become exclusive neighbors of v. This is conditional uniform resampling.

Let H_uv be the conditional-expectation projection for this trade.
It is self-adjoint and positive semidefinite under the uniform target.
The follow-up theorem bounds the gap of sum_uv (I-H_uv) below by 2.

If either pivot is isolated or universal, or |d_u-d_v|>n-4, then at least
one exclusive set must be empty in every realization. To see the last
condition, |A|-|B|=d_u-d_v and |A|+|B|<=n-2. Two positive sizes imply
absolute difference at most n-4. Such a pair has H_uv=I.

Let K be the count of pairs surviving these degree-only filters (some
remaining pairs may still be inactive). Uniformly select among them,
using the heat bath above, including identity outcomes. The removed
summands are zero, so the gap of the averaged kernel is at least 2/K,
giving relaxation at most K/2. No extra lazy coin is required because
the kernel is a convex combination of projections. K=0 implies a
singleton by switch connectivity. The filters are state independent:
do not replace them with a current-graph-dependent active-pair list
without a new reversibility argument.

## 4. Finite-time certificate

For any reversible positive-semidefinite chain here, with relaxation
upper bound R and state-space cardinality S, Cauchy-Schwarz and the
spectral contraction give

    max_x TV(P^t(x,.), uniform) <= sqrt(S)/2 * exp(-t/R).

Thus ceil(R log(sqrt(S)/(2 eps))) steps suffice (clamp at zero).
Shearer's entropy inequality on the edge indicator vector, whose
coordinates occur twice among the vertex incidence vectors, gives
log |Ω| <= (1/2) sum_v log C(n-1,d_v). The edge-count bound is
|Ω| <= C(C(n,2),m). Their minimum can be computed in exact integers
using integer square root. Use this upper bound for S.

The script distinguishes floating-point log estimates from rigorous
integer certificates. For eps=p/q choose the smallest nonnegative
integer k such that 4 p^2 4^k >= S q^2. Since exp(-k)<=2^(-k),
ceil(R k) is sufficient without floating-point rounding. In particular
the sparse m=O(n) lazy-edge bound is O(n^3 log n) at fixed epsilon.
The universal dense quadruple and pair-heat-bath bounds are respectively
O(n^6) and O(n^4), not new asymptotic theorems.

Static arithmetic on committed degree histograms, epsilon=1/4:

| Dataset | Quadruple integer certificate | Lazy edge | Lazy disjoint (best complement) | Pruned Curveball |
|---|---:|---:|---:|---:|
| Dolphins | 1,127,962,590 | 8,466,114 | 7,844,012 | 318,634 |
| Karate | 35,616,768 | 768,768 | 633,600 | 35,904 |
| Florentine | 237,510 | 11,020 | 8,294 | 1,523 |

These are worst-start sufficient iteration budgets conditional on the
cited theorem, not measured mixing times. A heat-bath step is not an
edge-switch step, and neither time nor empirical accuracy is inferred.
For these datasets all pivot pairs survive the degree-only pruning.

## 5. Tight-cut factorization

Sort degrees descending while retaining labels. For any tight
Erdős–Gallai inequality at k<n, let T be the first k vertices, H the
remaining vertices with d_v>=k, and B the remaining vertices with d_v<k.

Equality forces all of the following:
* T is a clique.
* Every vertex in H is joined to every vertex in T.
* Every vertex in B has all its neighbors in T (so no edges within B
  or between B and H).

Proof: the sum of degrees on T is at most k(k-1) plus the sum over
outside vertices of min(k,d_v). Every term's deficit is nonnegative.
Equality means every deficit is zero.

The only free edges are a bipartite graph T x B with row margins
d_u-(k-1)-|H| and column margins d_v, and a graph on H with residual
degrees d_v-k. These are independent constraints. Combining realizations
and adding forced edges gives a bijection between the Cartesian product
of the two factor spaces and Ω. Recurse on H. Sample exact factors
uniformly and independently where feasible. For approximate factors
with certified TV errors eps_i, a product coupling gives total error
at most sum_i eps_i. Each factor needs a sampler with its own valid
guarantee; do not apply an unrestricted simple-graph kernel to bipartite
constraints.

Example d=(7,7,3,3,3,3,1,1,1,1): cut k=2 forces the first pair joined to
each other and all four degree-3 vertices. The four degree-1 vertices
are allocated two to each pivot (6 possibilities). The residual
degree-3 vertices each need one additional edge (3 perfect matchings).
There are exactly 18 realizations, each obtainable by independent uniform
choices, with zero mixing cost. No tight cut occurs in the three
committed public datasets.

This is a candidate integration of known degree-sequence decomposition
and spectral comparison techniques, not a claim of mathematical novelty.
Exact factor samplers, margin-specific mixing bounds, further forced-edge
pruning, and a literature audit of canonical graph decompositions remain
future work.

## Static usage

    python3 graph_sampling_static.py
    python3 graph_sampling_static.py --edges data/dolphins.edgelist
    python3 graph_sampling_static.py --degrees 7 7 3 3 3 3 1 1 1 1

Only deterministic arithmetic and factor descriptions are produced.
No graph sampler is called; no random sampling, benchmark, remote server
operation or test suite is part of this change.
