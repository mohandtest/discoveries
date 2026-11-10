"""Paired Markov chain (M1, M2) on perfect matchings of K_n, kernel K from
Liu-Meng (2026), "A simplified proof of the FPRAS for counting perfect matchings":

  with prob 1/3: two-edge switch on M1 (uniform two edges, either alternative
                 pairing w.p. 1/2 each), Metropolis-accepted;
  with prob 1/3: hold;
  with prob 1/3: cycle exchange on a uniformly chosen discrepancy cycle of
                 (M1, M2) — always accepted (preserves w(M1) * w(M2)).

Stationary law: pi x pi, where pi(M) ~ product of edge weights.
"""
import random


class PairedChain:
    def __init__(self, n, W, rng):
        self.n = n
        self.W = W          # n x n weight matrix, symmetric, positive off-diagonal
        self.rng = rng
        self.M1 = self._random_matching()
        self.M2 = self._random_matching()
        self.switches = 0
        self.switch_accepts = 0
        self.exchanges = 0

    def _random_matching(self):
        v = list(range(self.n))
        self.rng.shuffle(v)
        M = [0] * self.n
        for i in range(0, self.n, 2):
            M[v[i]] = v[i + 1]
            M[v[i + 1]] = v[i]
        return M

    def set_weights(self, W):
        self.W = W

    def weight(self, M):
        W = self.W
        w = 1.0
        for i in range(self.n):
            j = M[i]
            if j > i:
                w *= W[i][j]
        return w

    # --- proposals -------------------------------------------------------
    def discrepancy_cycles(self):
        """Alternating even cycles of M1 xor M2, as vertex lists [v0,v1,...]
        where (v0,v1),(v2,v3),... are the M1 edges and (v1,v2),(v3,v0),...
        the M2 edges."""
        M1, M2 = self.M1, self.M2
        unvisited = {i for i in range(self.n) if M1[i] != M2[i]}
        cycles = []
        while unvisited:
            v0 = unvisited.pop()
            cyc = [v0]
            cur = v0
            take_M1 = True
            while True:
                cur = M1[cur] if take_M1 else M2[cur]
                take_M1 = not take_M1
                if cur == v0:
                    break
                cyc.append(cur)
                unvisited.discard(cur)
                assert len(cyc) <= self.n, "alternating walk diverged"
            cycles.append(cyc)
        return cycles

    def _two_edge_switch(self):
        n, M1, W, rng = self.n, self.M1, self.W, self.rng
        a = rng.randrange(n)
        c = rng.randrange(n)
        # c must define a *different* edge than (a, M1[a]):
        while c == a or c == M1[a]:
            c = rng.randrange(n)
        b, d = M1[a], M1[c]
        w_old = W[a][b] * W[c][d]
        if rng.random() < 0.5:
            pairs = ((a, c), (b, d))
        else:
            pairs = ((a, d), (b, c))
        w_new = W[pairs[0][0]][pairs[0][1]] * W[pairs[1][0]][pairs[1][1]]
        self.switches += 1
        if w_new >= w_old or rng.random() < w_new / w_old:
            self.switch_accepts += 1
            if pairs[0] == (a, c):
                M1[a], M1[c] = c, a
                M1[b], M1[d] = d, b
            else:
                M1[a], M1[d] = d, a
                M1[b], M1[c] = c, b

    def _cycle_exchange(self, cyc):
        M1, M2 = self.M1, self.M2
        m = len(cyc)
        self.exchanges += 1
        for k in range(m):
            u = cyc[k]
            v = cyc[(k + 1) % m]
            if k % 2 == 0:          # (u,v) currently an M1 edge -> move to M2
                M2[u], M2[v] = v, u
            else:                   # (u,v) currently an M2 edge -> move to M1
                M1[u], M1[v] = v, u

    def step(self):
        r = self.rng.random()
        if r < 1.0 / 3.0:
            self._two_edge_switch()
        elif r < 2.0 / 3.0:
            pass                    # hold
        else:
            cycs = self.discrepancy_cycles()
            if cycs:
                self._cycle_exchange(self.rng.choice(cycs))

    def nonedge_count(self, M, inG):
        k = 0
        for i in range(self.n):
            j = M[i]
            if j > i and not inG[i][j]:
                k += 1
        return k


class ReplicatedChain:
    """q matchings M_1..M_q, all at the same stage weights.

    Updates (both reversible w.r.t. pi^q):
      - two-edge switch on a uniform random replica (Metropolis);
      - cycle exchange on a uniform discrepancy cycle of a uniform pair
        (M_i, M_j), i != j — always accepted (product preserved).

    This is the practical stand-in for the paper's replicated sampler:
    replica-to-replica exchanges supply the long-range moves that a single
    pair loses once M1 and M2 collapse to the same matching.
    """

    def __init__(self, n, W, rng, q=8):
        self.n = n
        self.W = W
        self.rng = rng
        self.q = q
        self.Ms = [self._random_matching() for _ in range(q)]
        self.exchanges = 0
        self.switches = 0

    def _random_matching(self):
        v = list(range(self.n))
        self.rng.shuffle(v)
        M = [0] * self.n
        for i in range(0, self.n, 2):
            M[v[i]] = v[i + 1]
            M[v[i + 1]] = v[i]
        return M

    def set_weights(self, W):
        self.W = W

    def _cycles_between(self, A, B):
        n = self.n
        unvisited = {i for i in range(n) if A[i] != B[i]}
        cycles = []
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
            cycles.append(cyc)
        return cycles

    def _exchange(self, A, B, cyc):
        m = len(cyc)
        for k in range(m):
            u = cyc[k]
            v = cyc[(k + 1) % m]
            if k % 2 == 0:
                B[u], B[v] = v, u
            else:
                A[u], A[v] = v, u

    def _switch(self, M):
        n, W, rng = self.n, self.W, self.rng
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
        self.switches += 1
        if w_new >= w_old or rng.random() < w_new / w_old:
            if pairs[0] == (a, c):
                M[a], M[c] = c, a
                M[b], M[d] = d, b
            else:
                M[a], M[d] = d, a
                M[b], M[c] = c, b

    def step(self):
        if self.rng.random() < 0.5:
            j = self.rng.randrange(self.q)
            self._switch(self.Ms[j])
        else:
            i = self.rng.randrange(self.q)
            j = self.rng.randrange(self.q - 1)
            if j >= i:
                j += 1
            cycs = self._cycles_between(self.Ms[i], self.Ms[j])
            if cycs:
                self.exchanges += 1
                self._exchange(self.Ms[i], self.Ms[j],
                               self.rng.choice(cycs))
