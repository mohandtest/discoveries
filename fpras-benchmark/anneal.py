"""Annealing-based approximate counter for perfect matchings, using the
paired-chain kernel of Liu-Meng (2026) with practical (non-proof) parameters.

Variant A (plain annealing):
  - Complete graph K_n weights: graph edges w=1, nonedges w = b^{-j} at stage j,
    b = 1 + 1/n  (the paper's outer schedule).
  - R_j = Z_{j+1}/Z_j = E_{pi_j}[b^{-k(M)}], k(M) = # nonedges in M.
  - Z_hat = (n-1)!! * prod_j R_hat_j.

Variant B adds the paper's completion + marking + rebalancing (tunable D).
"""
import math
import random

from chain import PairedChain, ReplicatedChain


def make_weight_matrix(edges, n, exponent, b):
    """Weights at outer stage `exponent`: 1 on graph edges, b^{-exponent} on nonedges."""
    inG = [[False] * n for _ in range(n)]
    for u, v in edges:
        inG[u][v] = inG[v][u] = True
    W = [[1.0] * n for _ in range(n)]
    if exponent > 0:
        w = b ** (-exponent)
        for i in range(n):
            for j in range(i + 1, n):
                if not inG[i][j]:
                    W[i][j] = W[j][i] = w
    return W, inG


def anneal_count(edges, n, eps=0.25, samples=256, burn=64, thin=1,
                 replicas=8, seed=0, J_cap=None, J_override=None):
    """Returns dict with estimate stats and diagnostics."""
    b = 1.0 + 1.0 / n
    ln_b = math.log(b)
    if J_override is not None:
        J = J_override
    else:
        J = math.ceil((n / 2.0 * math.log(n) - math.log(eps / 32.0)) / ln_b)
        if J_cap is not None:
            J = min(J, J_cap)
    Z0 = math.prod(range(1, n, 2))

    inG = [[False] * n for _ in range(n)]
    for u, v in edges:
        inG[u][v] = inG[v][u] = True

    ests = []
    diag = {"stages": J, "steps_per_replica": 0, "zero_mass_late": []}
    for rep in range(replicas):
        rng = random.Random(seed * 100003 + rep)
        W0, _ = make_weight_matrix(edges, n, 0, b)
        ch = PairedChain(n, W0, rng)
        logZ = math.log(Z0)
        steps = 0
        for j in range(J):
            Wj, _ = make_weight_matrix(edges, n, j, b)
            ch.set_weights(Wj)
            for _ in range(burn):
                ch.step()
                steps += 1
            acc = 0.0
            taken = 0
            while taken < samples:
                ch.step()
                steps += 1
                if steps % thin == 0:
                    k = ch.nonedge_count(ch.M1, inG)
                    acc += b ** (-k)
                    taken += 1
            est = acc / samples
            if est <= 0:
                est = 1e-300
            logZ += math.log(est)
            if j >= J - 10:
                diag["zero_mass_late"].append(est)
        diag["steps_per_replica"] = steps
        ests.append(math.exp(logZ))

    mean = sum(ests) / len(ests)
    if len(ests) > 1:
        var = sum((z - mean) ** 2 for z in ests) / (len(ests) - 1)
        se = math.sqrt(var / len(ests))
    else:
        se = 0.0
    return {"mean": mean, "se": se, "ests": ests, "diag": diag}


def anneal_count_replicated(edges, n, q=8, eps=0.25, samples=256, burn=64,
                            replicas=8, seed=0, J_override=None):
    """Variant A' : same outer schedule, but a ReplicatedChain with q matchings;
    each step contributes q observables (one per replica)."""
    b = 1.0 + 1.0 / n
    ln_b = math.log(b)
    if J_override is not None:
        J = J_override
    else:
        J = math.ceil((n / 2.0 * math.log(n) - math.log(eps / 32.0)) / ln_b)
    Z0 = math.prod(range(1, n, 2))

    inG = [[False] * n for _ in range(n)]
    for u, v in edges:
        inG[u][v] = inG[v][u] = True

    def nonedges(M):
        k = 0
        for i in range(n):
            j = M[i]
            if j > i and not inG[i][j]:
                k += 1
        return k

    ests = []
    steps_last = 0
    for rep in range(replicas):
        rng = random.Random(seed * 100003 + rep)
        W0, _ = make_weight_matrix(edges, n, 0, b)
        ch = ReplicatedChain(n, W0, rng, q=q)
        logZ = math.log(Z0)
        steps = 0
        for j in range(J):
            Wj, _ = make_weight_matrix(edges, n, j, b)
            ch.set_weights(Wj)
            for _ in range(burn):
                ch.step()
                steps += 1
            acc = 0.0
            taken = 0
            while taken < samples:
                ch.step()
                steps += 1
                if steps % thin_default == 0:
                    obs = [b ** (-nonedges(M)) for M in ch.Ms]
                    acc += sum(obs)
                    taken += q
            est = acc / taken
            if est <= 0:
                est = 1e-300
            logZ += math.log(est)
        steps_last = steps
        ests.append(math.exp(logZ))

    mean = sum(ests) / len(ests)
    var = sum((z - mean) ** 2 for z in ests) / (len(ests) - 1)
    return {"mean": mean, "se": math.sqrt(var / len(ests)), "ests": ests,
            "diag": {"stages": J, "steps_per_replica": steps_last}}


thin_default = 1
