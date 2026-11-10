"""Windowed cross-level chain — a practical miniature of the paper's replicated
sampler (Liu-Meng Sec. 3): matchings live at several *adjacent annealing
levels* simultaneously; pair updates happen between adjacent levels with
Metropolis acceptance for pi_a (x) pi_b, same-level cycle exchanges, and
two-edge switches. Samples are drawn from the top level only.

This tests whether the paper's key structural idea — level-heterogeneous
replication — has practical value over plain single-pair annealing.
"""
import math
import random


def random_matching(n, rng):
    v = list(range(n))
    rng.shuffle(v)
    M = [0] * n
    for i in range(0, n, 2):
        M[v[i]] = v[i + 1]
        M[v[i + 1]] = v[i]
    return M


def cycles_between(A, B, n):
    unvisited = {i for i in range(n) if A[i] != B[i]}
    out = []
    while unvisited:
        v0 = unvisited.pop()
        cyc = [v0]
        cur = v0
        take_A = True
        while True:
            cur = A[cur] if take_A else B[cur]
            take_A = not take_A
            if cur == v0:
                break
            cyc.append(cur)
            unvisited.discard(cur)
            assert len(cyc) <= n
        out.append(cyc)
    return out


def exchange(A, B, cyc):
    for k in range(len(cyc)):
        u, v = cyc[k], cyc[(k + 1) % len(cyc)]
        if k % 2 == 0:
            B[u], B[v] = v, u
        else:
            A[u], A[v] = v, u


class WindowedChain:
    def __init__(self, n, levels, q, rng):
        """levels: number of annealing levels kept (window width)."""
        self.n = n
        self.levels = levels
        self.q = q
        self.rng = rng
        # weights[j] for j in 0..levels-1 (level 0 = lowest annealing stage)
        self.Ws = [None] * levels
        self.Ms = [[random_matching(n, rng) for _ in range(q)]
                   for _ in range(levels)]
        self.n_switch_acc = 0
        self.n_cross = 0

    def set_weights(self, Ws):
        self.Ws = Ws

    def _weight(self, lvl, M):
        W = self.Ws[lvl]
        w = 1.0
        for i in range(self.n):
            j = M[i]
            if j > i:
                w *= W[i][j]
        return w

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
            self.n_switch_acc += 1
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
        """Exchange a discrepancy cycle between level lvl and lvl+1.
        Metropolis for pi_lvl (x) pi_{lvl+1}: ratio along the cycle is
        prod_{Pc} w_{l+1}(e)/w_l(e) * prod_{Qc} w_l(e)/w_{l+1}(e), where Pc are
        the lower-level matching's edges on the cycle."""
        i = self.rng.randrange(self.q)
        j = self.rng.randrange(self.q)
        A = self.Ms[lvl][i]      # lower level
        B = self.Ms[lvl + 1][j]  # higher level
        cycs = cycles_between(A, B, self.n)
        if not cycs:
            return
        cyc = self.rng.choice(cycs)
        Wa, Wb = self.Ws[lvl], self.Ws[lvl + 1]
        log_ratio = 0.0
        for k in range(len(cyc)):
            u, v = cyc[k], cyc[(k + 1) % len(cyc)]
            if k % 2 == 0:   # A's edge moves to B's slot
                log_ratio += math.log(Wb[u][v]) - math.log(Wa[u][v])
            else:
                log_ratio += math.log(Wa[u][v]) - math.log(Wb[u][v])
        self.n_cross += 1
        if log_ratio >= 0 or self.rng.random() < math.exp(log_ratio):
            exchange(A, B, cyc)

    def step(self):
        r = self.rng.random()
        lvl = self.rng.randrange(self.levels)
        if r < 0.4:
            self._switch(lvl, self.rng.randrange(self.q))
        elif r < 0.7:
            self._same_level_exchange(lvl)
        else:
            if lvl < self.levels - 1:
                self._cross_level_exchange(lvl)

    def refresh_bottom(self):
        """Re-sample the bottom level from uniform (paper's base refresh)."""
        for i in range(self.q):
            self.Ms[0][i] = random_matching(self.n, self.rng)

    def slide(self, W_new_bottom):
        """Advance the window by one stage: drop the bottom level, push a copy
        of the top level up, set the new bottom level's weights."""
        top = self.Ms[-1]
        self.Ms.pop(0)
        self.Ms.append([M[:] for M in top])
        self.Ws.pop(0)
        self.Ws.append(W_new_bottom)
