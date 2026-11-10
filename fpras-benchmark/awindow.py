"""Windowed cross-level annealing counter (practical miniature of the paper's
replicated sampler) and comparison against single-pair annealing."""
import math
import random
import sys
import time

sys.path.insert(0, ".")
from windowed import WindowedChain
from anneal import make_weight_matrix


def anneal_windowed(edges, n, W_levels=6, q=2, eps=0.25, samples=1024,
                    burn=128, replicas=6, seed=0, refresh_every=8):
    b = 1.0 + 1.0 / n
    ln_b = math.log(b)
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
    for rep in range(replicas):
        rng = random.Random(seed * 7919 + rep)
        # all levels start at stage-0 weights; the top level tracks stage j
        W0, _ = make_weight_matrix(edges, n, 0, b)
        ch = WindowedChain(n, W_levels, q, rng)
        ch.set_weights([W0[:] and [row[:] for row in W0]
                        for _ in range(W_levels)])
        logZ = math.log(Z0)
        stage_in_window = 0
        for j in range(J):
            # burn-in at current window position
            for s in range(burn):
                ch.step()
                if s % refresh_every == 0:
                    ch.refresh_bottom()
            acc = 0.0
            taken = 0
            steps = 0
            while taken < samples:
                ch.step()
                steps += 1
                if steps % 1 == 0:
                    obs = [b ** (-nonedges(M)) for M in ch.Ms[-1]]
                    acc += sum(obs)
                    taken += q
            est = max(acc / taken, 1e-300)
            logZ += math.log(est)
            # advance the outer schedule by one stage
            stage_in_window += 1
            if j < J - 1:
                if stage_in_window < W_levels:
                    Wnew, _ = make_weight_matrix(edges, n, j + 1, b)
                    ch.Ws[-1] = Wnew
                else:
                    Wnew, _ = make_weight_matrix(edges, n, j + 1, b)
                    ch.slide(Wnew)
                    stage_in_window = W_levels - 1
        ests.append(math.exp(logZ))

    mean = sum(ests) / len(ests)
    var = sum((z - mean) ** 2 for z in ests) / (len(ests) - 1)
    return {"mean": mean, "se": math.sqrt(var / len(ests)), "ests": ests,
            "diag": {"stages": J}}
