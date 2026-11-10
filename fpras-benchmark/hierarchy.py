"""Full-hierarchy chain — faithful practical implementation of the paper's
replicated sampler structure (Liu-Meng Sec. 3, practical parameters).

All J+1 annealing levels exist simultaneously, q matchings per level. One long
chain runs over the whole product space:
  - two-edge switch on a random (level, matching)   [Metropolis]
  - same-level cycle exchange                        [always accepted]
  - adjacent-level cycle exchange                    [Metropolis for pi_j (x) pi_{j+1}]
  - periodic refresh of level 0 from uniform         [paper's base refresh]

Every step contributes an observable b^{-k(M)} at the level touched; level-j
means estimate R_j = Z_{j+1}/Z_j, and Z_hat = (n-1)!! * prod_j R_hat_j.
"""
import math
import random

from windowed import cycles_between, exchange, random_matching


class HierarchyChain:
    def __init__(self, n, Ws, q, rng):
        """Ws: list of (J+1) weight matrices, level j = outer stage j."""
        self.n = n
        self.Ws = Ws
        self.J = len(Ws) - 1
        self.q = q
        self.rng = rng
        self.Ms = [[random_matching(n, rng) for _ in range(q)]
                   for _ in range(self.J + 1)]

    def _switch(self, lvl, idx):
        n, rng = self.n, self.rng
        M = self.Ms[lvl][idx]
        W = self.Ws[lvl]
        a = rng.randrange(n)
        c = rng.randrange(n)
        while c == a or c == M[a]:
            c = rng.randrange(n)
        b, d = M[a], M[c]
        w_old = W[a][b] * W[c][d]
        if rng.random() < 0.5:
            pairs = ((a, c), (b, d))
        else:
            pairs = ((a, d), (b, c))
        w_new = W[pairs[0][0]][pairs[0][1]] * W[pairs[1][0]][pairs[1][1]]
        if w_new >= w_old or rng.random() < w_new / w_old:
            if pairs[0] == (a, c):
                M[a], M[c] = c, a
                M[b], M[d] = d, b
            else:
                M[a], M[d] = d, a
                M[b], M[c] = c, b

    def _same_level_exchange(self, lvl):
        i = self.rng.randrange(self.q)
        j = self.rng.randrange(self.q - 1)
        if j >= i:
            j += 1
        cycs = cycles_between(self.Ms[lvl][i], self.Ms[lvl][j], self.n)
        if cycs:
            exchange(self.Ms[lvl][i], self.Ms[lvl][j], self.rng.choice(cycs))

    def _cross_level_exchange(self, lvl):
        i = self.rng.randrange(self.q)
        j = self.rng.randrange(self.q)
        A = self.Ms[lvl][i]
        B = self.Ms[lvl + 1][j]
        cycs = cycles_between(A, B, self.n)
        if not cycs:
            return A   # still report an observable for this level
        cyc = self.rng.choice(cycs)
        Wa, Wb = self.Ws[lvl], self.Ws[lvl + 1]
        log_ratio = 0.0
        for k in range(len(cyc)):
            u, v = cyc[k], cyc[(k + 1) % len(cyc)]
            if k % 2 == 0:
                log_ratio += math.log(Wb[u][v]) - math.log(Wa[u][v])
            else:
                log_ratio += math.log(Wa[u][v]) - math.log(Wb[u][v])
        if log_ratio >= 0 or self.rng.random() < math.exp(log_ratio):
            exchange(A, B, cyc)
        return A

    def step(self):
        """Returns (level, matching) touched, for observable recording."""
        r = self.rng.random()
        lvl = self.rng.randrange(self.J + 1)
        if r < 0.4:
            idx = self.rng.randrange(self.q)
            self._switch(lvl, idx)
            return lvl, self.Ms[lvl][idx]
        elif r < 0.7:
            self._same_level_exchange(lvl)
            idx = self.rng.randrange(self.q)
            return lvl, self.Ms[lvl][idx]
        else:
            if lvl < self.J:
                M = self._cross_level_exchange(lvl)
                return lvl, M
            return lvl, self.Ms[lvl][self.rng.randrange(self.q)]

    def refresh_bottom(self):
        for i in range(self.q):
            self.Ms[0][i] = random_matching(self.n, self.rng)


def anneal_hierarchy(edges, n, q=2, eps=0.25, steps=2000000, report_every=16,
                    replicas=4, seed=0, refresh_every=200):
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
        rng = random.Random(seed * 104729 + rep)
        Ws = []
        for j in range(J + 1):
            W, _ = __import__("anneal").make_weight_matrix(edges, n, j, b)
            Ws.append(W)
        ch = HierarchyChain(n, Ws, q, rng)
        sums = [0.0] * (J + 1)
        counts = [0] * (J + 1)
        for t in range(steps):
            if t % refresh_every == 0:
                ch.refresh_bottom()
            lvl, M = ch.step()
            if t % report_every == 0:
                sums[lvl] += b ** (-nonedges(M))
                counts[lvl] += 1
        logZ = math.log(Z0)
        worst = 1.0
        for j in range(J):
            if counts[j] == 0 or sums[j] <= 0:
                est = 1e-300
            else:
                est = sums[j] / counts[j]
            worst = min(worst, est)
            logZ += math.log(est)
        ests.append(math.exp(logZ))

    mean = sum(ests) / len(ests)
    var = sum((z - mean) ** 2 for z in ests) / (len(ests) - 1)
    return {"mean": mean, "se": math.sqrt(var / len(ests)), "ests": ests,
            "diag": {"stages": J, "min_stage_mean": worst}}
