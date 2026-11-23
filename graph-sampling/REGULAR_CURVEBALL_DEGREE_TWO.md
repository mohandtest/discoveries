# Degree-two case of the regular Curveball spectral-gap conjecture

**Status: proof candidate for independent review, 2026-11-24.** This is an analytical extension of an existing conjecture, not a claim of a peer-reviewed or formally verified result. No new numerical experiments, simulation, or benchmark are used. The argument depends on the published symmetry reduction and finite certificates of Short, and on the classical split-and-merge spectrum of Hanlon/Jiang.

## 1. Background and precise target

OpenAI/math result family #131, [Polynomial mixing of the switch chain for every graphical degree sequence](https://github.com/openai/math/tree/main/preprints), resolves the Kannan–Tetali–Vempala conjecture by establishing polynomial mixing for the degree-preserving switch chain. The present project studies the practical constants and alternative kernels in graph-sampling/.

Mark T. Short, [Sharp spectral gaps for the switch and Curveball chains on every graphical degree sequence](https://zenodo.org/records/23295359), subsequently gives sharp worst-case gaps for the uniform-quadruple switch and uniform-pair undirected Curveball kernels. For Curveball the universal lower bound is $2/\binom n2$.

Short's November 13, 2026 paper, [The Curveball chain on regular graphs: spectral gap at most 2/n and a comparison with random transpositions](https://github.com/sevenevesai/RegularCurveballGap), asks whether the much stronger equality

$$
\operatorname{gap}(K)=2/n
$$

holds for all regular degree sequences, with $n\ge4$, $1\le d\le n-2$ and $nd$ even (Conjecture 9.1 in the inspected version). It establishes the upper bound, equality for perfect matchings and their complements, and computer-assisted certificates for all regular degrees through $n=11$. It does not establish the equality for degree two for general $n$.

Write $\Omega_{n,d}$ for the labeled simple undirected $d$-regular graphs, with uniform stationary law $\pi$. For a pivot pair $a=\{u,v\}$ let $E_a$ be conditional uniform averaging on its Curveball fiber: preserve all edges off the two pivots, their mutual edge, and their common neighbors; redistribute their exclusive neighbors uniformly subject to their degrees. Define

$$
K=\binom n2^{-1}\sum_a E_a,\qquad
H=\sum_a(I-E_a)=\binom n2(I-K).
$$

Thus the conjecture is $\operatorname{gap}(H)=n-1$. Each $E_a$ is an orthogonal projection, so $K$ is positive semidefinite.

Short proves that $n-1$ is an eigenvalue of $H$ on centered edge indicators. His comparison with random transpositions gives $H\succeq \frac12 L_T$, where $L_T=\sum_a(I-T_a)$ and $T_a$ swaps vertex labels. The symmetric-group representation decomposition then yields $H\succeq(n-1)I$ outside the isotypic sectors for $(n)$ and $(n-1,1)$. Those remaining sectors can be studied entirely on functions invariant under the stabilizer of one root vertex (see the source's sections comparison and rooted).

The source also identifies a barrier to strengthening the original local $H^2$ inequalities separately. Here we instead exploit the cycle structure peculiar to $d=2$.

**Proposed theorem.** For every $n\ge4$ for which the indicated degree is in the nontrivial range,

$$
\operatorname{gap}(K)=2/n
\quad\text{on }\Omega_{n,2}\text{ and }\Omega_{n,n-3}.
$$

The argument below covers $n\ge12$ analytically; $4\le n\le11$ is supplied by Short's existing finite certificates. In particular, the infinite-family assertion is not just an extrapolation of small numerical data.

## 2. Exact cycle-partition reduction

A 2-regular simple graph is a union of unoriented cycles, each of length at least three. Let $\lambda=(a_1,\ldots,a_r)$ denote the unordered list of cycle lengths, and let $c_j$ count parts of size $j$. Put

$$
\mathcal A_n=\{\lambda\vdash n:c_1=c_2=0\}.
$$

A fixed partition in this set has

$$
\frac{n!}{\prod_{j\ge3}(2j)^{c_j}c_j!}
$$

labeled graph realizations: partition the vertices into components, and give each component an unoriented cyclic ordering. Consequently the law on shapes is proportional to

$$
w(\lambda)=\prod_{j\ge3}\frac{(1/2)^{c_j}}{j^{c_j}c_j!}.
$$

This is the Ewens cycle law with parameter $1/2$, conditioned on $\mathcal A_n$.

Use off-diagonal rates of the continuous-time generator $-H$ (so rates are measured before division by $\binom n2$). For two specified distinct cycles of lengths $a,b$, every one of the $ab$ cross-cycle pivot pairs has four distinct exclusive neighbors. Of its six equiprobable redistributions, two preserve the two cycle lengths and four merge the cycles. Hence the merge rate is $2ab/3$.

For pivots on the same cycle of length $\ell=a+b$, a split into $a,b\ge3$ is possible exactly when both arcs between the pivots have length at least three. Both pivots then have two exclusive neighbors, and two of the six redistributions split the cycle into the two arc lengths. There are $\ell$ unordered pivot pairs at those arc lengths if $a\ne b$, and $\ell/2$ if $a=b$. The rates are therefore

| Shape operation | Rate for a specified cycle or cycle pair |
|---|---:|
| Merge $a,b$ | $2ab/3$ |
| Split $\ell=a+b$, $a\ne b$ | $\ell/3$ |
| Split $\ell=2a$ | $\ell/6$ |

Sum these contributions over all qualifying cycles and cycle pairs, including repeated sizes. Pivots sharing an edge or a neighbor cannot split into two simple cycles; all remaining shape-preserving trades have no effect on shape functions. This accounts for all off-diagonal shape transitions.

## 3. Unrooted sector via the Ewens spectrum

Let $P$ be the classical Metropolis random-transposition chain lumped by permutation cycle type, with stationary Ewens parameter $1/2$. In Jiang's convention this is $\theta=2$, NOT $\theta=1/2$. Let

$$
L=\binom n2(I-P).
$$

Its merge rates are $ab$; its split rates are $\ell/2$ for unequal parts and $\ell/4$ for equal parts. These follow from selecting a transposition uniformly, accepting merges with probability one and splits with probability $1/2$.

Let $L_{\mathcal A}$ be the reflected restriction to $\mathcal A_n$: attempted exits to the complement become holds. Section 2 proves the exact identity

$$
H_{\mathrm{shape}}=\frac23 L_{\mathcal A}.
$$

### 3.1. Spectrum and the first four modes

Hanlon's spectrum, as stated in Jiang [equation (7), Section 4](https://arxiv.org/abs/1204.1671), at $\theta=2$ gives the eigenvalues of $L$ indexed by all partitions $\nu\vdash n$:

$$
\Lambda_\nu=\binom n2-\sum_i\binom{\nu_i}{2}
+\frac12\sum_i(i-1)\nu_i.
$$

For $n\ge12$, the four smallest (counting multiplicity) are those indexed by $(n),(n-1,1),(n-2,2),(n-2,1,1)$:

$$
0,\quad n-\frac12,\quad 2n-3,\quad 2n-\frac32.
$$

Every other partition has first part at most $n-3$ and is dominated by $(n-3,3)$. The dominance monotonicity of the spectrum (Jiang, Lemma 4.1) therefore gives

$$
\Lambda_\nu\ge\Lambda_{(n-3,3)}=3n-\frac{15}{2}.
$$

This is strictly above the first four values for the range in question.

We also need the subspace of the four lowest eigenfunctions, not just their eigenvalues. Write $x=c_1$, $y=c_2$, $b=\binom{x}{2}$. A direct calculation using the merge and split rates gives

$$
\begin{aligned}
L1&=0,\\
Lx&=(n-1/2)x-n/2,\\
Lb&=(2n-2)b-\tfrac12(n-1)x-\tfrac12 y,\\
Ly&=(2n-5/2)y-b+\tfrac12x-n/2.
\end{aligned}
$$

For example, merging a singleton with a nonsingleton has rate $x(n-x)$ and reduces $x$ by one; merging two singletons has rate $\binom x2$ and reduces $x$ by two; splitting a cycle of length at least three to create a singleton has total rate $(n-x-2y)/2$, while splitting a 2-cycle has total rate $y/2$ and creates two singletons. These give the identities for $x$ and $b$. For $y$, merges destroy 2-cycles at aggregate rate in count units $2y(n-2)$, except the separate creation term $\binom x2$ from two singleton merges. Splits produce 2-cycles at aggregate rate in count units $(n-x-2y)/2$ (a 4-cycle splitting into two 2-cycles contributes twice); splitting a 2-cycle removes one at rate $y/2$. This gives the last identity.

Thus the span of $1,x,b,y$ is invariant. These four functions are independent for $n\ge12$, as can be seen on partitions $(n),(n-1,1),(n-2,1,1),(n-2,2)$ with respectively distinct $(x,b,y)$. The induced two-dimensional block for $b,y$ modulo $1,x$ has diagonal entries $2n-2,2n-5/2$ and off-diagonal product $1/2$, hence eigenvalues $2n-3,2n-3/2$. Together with the identities for $1,x$ this identifies the span as exactly the four lowest modes. No identification of individual Jack eigenfunctions is needed.

### 3.2. Zero extension and the boundary correction

Let $\mu$ denote the unrestricted Ewens law, and let $f$ be centered under $\mu(\cdot\mid\mathcal A_n)$. Extend it by zero outside $\mathcal A_n$, obtaining $F$. Since $x=b=y=0$ on $\mathcal A_n$, $F$ is orthogonal in $L^2(\mu)$ to all four low modes (to $1$ by centering). Consequently

$$
\langle F,LF\rangle_\mu
\ge(3n-15/2)\|F\|_\mu^2.
$$

One cannot transfer this bound unchanged to a reflected chain: a zero extension adds killing energy at the boundary. Define

$$
r(\lambda)=\sum_{\eta\notin\mathcal A_n}q(\lambda,\eta),
$$

where $q$ denotes the off-diagonal rate of $-L$. For $\lambda\in\mathcal A_n$, only splits can exit. A cycle of length at least five can split off a part of size 1 or 2, each at rate at most half its length. A 4-cycle has exit rate $4/2+4/4=3$, and a 3-cycle has exit rate $3/2$ (the split 1+2 must not be counted twice). Thus $r(\lambda)\le n$.

Writing $\pi_{\mathcal A}=\mu(\cdot\mid\mathcal A_n)$, detailed balance gives

$$
\frac{\langle F,LF\rangle_\mu}{\mu(\mathcal A_n)}
=\langle f,L_{\mathcal A}f\rangle_{\pi_{\mathcal A}}
+\mathbb E_{\pi_{\mathcal A}}[r f^2].
$$

This identity includes the entire boundary term with coefficient one: the two orientations in the Dirichlet form cancel its factor $1/2$.

Since $\|F\|_\mu^2=\mu(\mathcal A_n)\|f\|_{\pi_{\mathcal A}}^2$,

$$
\langle f,H_{\mathrm{shape}}f\rangle_{\pi_{\mathcal A}}
\ge\frac23(3n-15/2-n)\|f\|_{\pi_{\mathcal A}}^2
=\left(\frac{4n}{3}-5\right)\|f\|_{\pi_{\mathcal A}}^2.
$$

The right-hand coefficient is at least $n-1$ precisely for $n\ge12$. This closes the unrooted, centered symmetry sector for that range.

## 4. Rooted variation: a separate merge-only inequality

Let a graph have cycles of lengths $a_1,\ldots,a_r$. A rooted isomorphism class of a 2-regular graph is specified by its shape and the length of the root's cycle. For each fixed shape write $f_i=f(\lambda,a_i)$; equal-size cycles have equal values.

Average over all relabelings (equivalently average over the root location conditional on the shape). The invariant unrooted functions form an orthogonal subspace of the rooted functions; its orthogonal complement consists exactly of functions satisfying

$$
\sum_i a_i f_i=0\quad\text{for every shape}.
$$

Both subspaces are $H$-invariant because $H$ commutes with relabelings and is self-adjoint. The conditional squared norm is $\sum_i(a_i/n) f_i^2$.

For a specified pair of cycles $i,j$, a cross-cycle Curveball merge has rate $2a_i a_j/3$. If the root is in either cycle before merging, its resulting rooted class is identical: the merged shape with root in the cycle of length $a_i+a_j$. Call the common resulting value $g_{ij}$. Conditional root probabilities are $a_i/n$ and $a_j/n$. The merge contributes at least

$$
\frac{2a_i a_j}{3n}
\left[a_i(f_i-g_{ij})^2+a_j(f_j-g_{ij})^2\right]
$$

to the shape-conditional Dirichlet energy, ignoring nonnegative contributions with the root elsewhere.

To justify summation: compute the full Dirichlet form by summing stationary flow times squared difference over each unordered transition once. Orient merge/split edges from the larger number of components toward the smaller; reversibility identifies the reverse split contribution. Sum all merge rates, retaining their multiplicities even if they land in the same rooted class. All same-component-count transitions and the root-elsewhere terms may be discarded for a lower bound. One can equivalently average over a uniformly random root independently of the labeled graph, because the rooted function at a fixed root and its random-root version have the same quadratic form by relabeling symmetry.

Minimizing the weighted quadratic over $g_{ij}$ yields

$$
a_i(f_i-g_{ij})^2+a_j(f_j-g_{ij})^2
\ge\frac{a_i a_j}{a_i+a_j}(f_i-f_j)^2.
$$

Every $a_i,a_j\ge3$, so $a_i a_j/(a_i+a_j)\ge3/2$. Hence the retained energy at each shape is bounded below by

$$
\frac1n\sum_{i<j} a_i a_j(f_i-f_j)^2.
$$

The exact weighted variance identity gives

$$
\begin{aligned}
\sum_{i<j}a_i a_j(f_i-f_j)^2
&=n\sum_i a_i f_i^2-\left(\sum_i a_i f_i\right)^2\\
&=n\sum_i a_i f_i^2.
\end{aligned}
$$

Averaging over shapes now proves

$$
\boxed{\langle f,Hf\rangle_\pi\ge n\|f\|_\pi^2}
$$

on the rooted variation sector. This argument uses no estimate on individual split rates, no asymptotic approximation, and no numerical data.

## 5. Combine the sectors

The unrooted and rooted-variation pieces are orthogonal and invariant. On their centered sum, Sections 3 and 4 give

$$
\mu_{\mathrm{rooted}}\ge
\min\{4n/3-5,n\}\ge n-1\quad(n\ge12).
$$

By Short's rooted reduction, the remaining isotypic components are already bounded below by $n-1$. The known edge-indicator eigenvalue supplies the upper bound, so

$$
\operatorname{gap}(H)=n-1,\qquad
\operatorname{gap}(K)=2/n.
$$

Complementation preserves every Curveball fiber up to bijection and interchanges degrees $2$ and $n-3$. The chains are conjugate, giving the second infinite family. The finite cases $n\le11$ follow from Short's published certificates; they have not been rerun in this work.

## 6. Significance and limitations

The proposed result establishes a linear relaxation time $n/2$ for these two degrees, versus the universal relaxation bound $\binom n2/2$. The ratio of the bounds is $(n-1)/2$. At $n=10,000$ this is $4,999.5$; the old upper bound is $24,997,500$ trades and the candidate exact relaxation time is $5,000$ trades.

The standard worst-start total-variation certificate, with $M=|\Omega_{n,2}|$, is

$$
t_{\mathrm{mix}}(\varepsilon)
\le\left\lceil \frac n2
\log\frac{\sqrt{M-1}}{2\varepsilon}\right\rceil
$$

(clamped at zero). In particular $\log M=O(n\log n)$, giving $O(n^2\log n)$ for fixed error; this does not prove $O(n\log n)$ TV mixing or cutoff. No empirical wall-clock speedup follows from a spectral-gap improvement.

The all-regular conjecture remains open. The degree-two proof works because the graph-shape and rooted-shape coordinates are completely described by cycle lengths. A higher-degree graph has no comparable exact partition reduction in this argument.

Prior literature has established split-and-merge chains and their spectra. The proposed contribution here is the identification of the restricted shape kernel, the low-mode annihilation with controlled boundary cost, and the merge-only inequality for rooted variation, combined with Short's symmetry theorem. Novelty beyond the cited papers has not been exhaustively established. This is a candidate for a research note, subject to independent scrutiny.

## 7. Reviewer checklist

- Check each of the six possible exclusive-neighbor allocations for distinct cycles and for same-cycle nonadjacent, non-common-neighbor pivots; confirm the factors $2/3$ and $1/3$.
- Check all multiplicities for repeated cycle sizes and equal-size splits.
- Verify the Ewens parameter convention ($\theta=2$ in Jiang) and the generator normalization $\binom n2$.
- Verify the four low-mode generator identities and dominance order for all other partitions; check orthogonality of the zero extension.
- Check the boundary correction for 3- and 4-cycles and the Dirichlet normalization.
- Check that rooting at a uniformly random vertex conditional on shape gives the fixed-root invariant quadratic form, and that conditional-mean-zero functions form an invariant subspace.
- Check detailed balance and absence of double counting in the oriented merge energy, including when the root lies in equal-size cycles.
- Verify reliance on Short's exact finite certificates and complement conjugacy. No new certificates are supplied.
- Audit prior literature before claiming novelty or submitting externally.

## References

1. OpenAI/math, result family #131, September 25, 2026. [Repository](https://github.com/openai/math).
2. Mark T. Short, *Sharp spectral gaps for the switch and Curveball chains on every graphical degree sequence*, October 2026. [Zenodo](https://zenodo.org/records/23295359), [source](https://github.com/sevenevesai/SharpSwitchGap).
3. Mark T. Short, *The Curveball chain on regular graphs: spectral gap at most 2/n and a comparison with random transpositions*, November 13, 2026. [Paper and programs](https://github.com/sevenevesai/RegularCurveballGap). Relevant source sections: [setup](https://github.com/sevenevesai/RegularCurveballGap/blob/main/paper/sections/setup.tex), [comparison](https://github.com/sevenevesai/RegularCurveballGap/blob/main/paper/sections/comparison.tex), [rooted](https://github.com/sevenevesai/RegularCurveballGap/blob/main/paper/sections/rooted.tex), [expansion](https://github.com/sevenevesai/RegularCurveballGap/blob/main/paper/sections/expansion.tex), [open problems](https://github.com/sevenevesai/RegularCurveballGap/blob/main/paper/sections/open.tex).
4. Phil Hanlon, *A Markov chain on the symmetric group and Jack symmetric functions*, Discrete Mathematics 99 (1992), 123–140.
5. Yunjiang Jiang, *Mixing time of Metropolis chain based on random transposition walk converging to multivariate Ewens distribution*, Annals of Applied Probability 25 (2015), 1581–1615, DOI 10.1214/14-AAP1031, [arXiv:1204.1671](https://arxiv.org/abs/1204.1671). Theorem 2.1, equation (7), Lemma 4.1.
