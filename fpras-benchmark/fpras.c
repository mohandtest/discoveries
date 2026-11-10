/* fpras.c — exact perfect-matching counting (reachable-state DP) and the
 * OpenAI/Liu-Meng (2026) FPRAS (paired-chain annealing) in one program, so
 * both run on the identical graph.
 *
 * Modes:
 *   ./fpras --edges graphs/g24_p50_s42.edges --mode both
 *   ./fpras --edges ... --mode fpras --replicas 8 --samples 1024 --burn 1024
 *
 * Exact: memoized DP over reachable subsets (remove lowest unmatched vertex +
 * a partner). Visits only reachable states, not all 2^n.
 *
 * FPRAS: outer annealing schedule (nonedge weight b^-j, b = 1+1/n),
 * paired chain kernel: 1/3 two-edge switch on M1 (Metropolis), 1/3 hold,
 * 1/3 cycle exchange on a uniform discrepancy cycle (always accepted).
 * Estimator: R_j = E[b^{-k(M)}], Z_hat = (n-1)!! * prod R_hat_j.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

/* ---------- xorshift128+ RNG ---------- */
static uint64_t s[2];
static inline uint64_t next_u64(void) {
    uint64_t x = s[0], y = s[1];
    s[0] = y;
    x ^= x << 23;
    s[1] = x ^ y ^ (x >> 17) ^ (y >> 26);
    return s[1] + y;
}
static inline double next_double(void) { return (next_u64() >> 11) * (1.0 / 9007199254740992.0); }
static inline uint32_t next_below(uint32_t n) { return (uint32_t)(next_u64() % n); }

/* ---------- graph ---------- */
static int nverts;
static uint64_t *adj;         /* bitmask neighbors (n <= 64) */
static int nedges;
static char gname[256];

/* ---------- exact reachable-state DP ---------- */
typedef struct { uint64_t key; uint64_t val; int used; } slot;
static slot *table;
static size_t tcap, tsize;
static uint64_t states_visited;

static void tinit(size_t cap) {
    tcap = cap; tsize = 0;
    table = calloc(cap, sizeof(slot));
    if (!table) { fprintf(stderr, "OOM hash table\n"); exit(1); }
}
static uint64_t *tget(uint64_t key) {
    size_t i = (size_t)(key * 0x9E3779B97F4A7C15ULL) & (tcap - 1);
    while (table[i].used) {
        if (table[i].key == key) return &table[i].val;
        i = (i + 1) & (tcap - 1);
    }
    return NULL;
}
static void tput(uint64_t key, uint64_t val) {
    if (tsize * 10 >= tcap * 7) { fprintf(stderr, "hash table full\n"); exit(1); }
    size_t i = (size_t)(key * 0x9E3779B97F4A7C15ULL) & (tcap - 1);
    while (table[i].used) {
        if (table[i].key == key) { table[i].val = val; return; }
        i = (i + 1) & (tcap - 1);
    }
    table[i].used = 1; table[i].key = key; table[i].val = val; tsize++;
}

static uint64_t exact_rec(uint64_t S) {
    if (S == 0) return 1;   /* base case: empty set has one (empty) matching */
    uint64_t *hit = tget(S);
    if (hit) return *hit;
    states_visited++;
    int low = __builtin_ctzll(S);
    uint64_t rest = S ^ (1ULL << low);
    uint64_t m = adj[low] & rest;
    uint64_t tot = 0;
    while (m) {
        uint64_t j = m & (~m + 1);
        tot += exact_rec(S ^ (1ULL << low) ^ j);
        m ^= j;
    }
    tput(S, tot);
    return tot;
}

static void run_exact(void) {
    size_t cap = 1024;
    while (cap < (1ULL << 26)) cap <<= 1;   /* start reasonable, we grow-in-advance below */
    /* estimate: allocate big upfront for known sizes; restart if full is fine */
    cap = 1ULL << 26;                        /* 64M slots * 24B = 1.5 GB max */
    tinit(cap);
    states_visited = 0;
    clock_t t0 = clock();
    uint64_t count = exact_rec((1ULL << nverts) - 1);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("mode=exact vertices=%d edges=%d exact=%llu states=%llu seconds=%.3f\n",
           nverts, nedges, (unsigned long long)count,
           (unsigned long long)states_visited, secs);
    free(table);
}

/* ---------- FPRAS ---------- */
static int *M1, *M2;              /* partner arrays */

static void random_matching(int *M) {
    int v[64];
    for (int i = 0; i < nverts; i++) v[i] = i;
    for (int i = nverts - 1; i > 0; i--) {
        int j = next_below(i + 1);
        int t = v[i]; v[i] = v[j]; v[j] = t;
    }
    for (int i = 0; i < nverts; i += 2) { M[v[i]] = v[i+1]; M[v[i+1]] = v[i]; }
}

static int nonedge_count(const int *M, const unsigned char *inG) {
    int k = 0;
    for (int i = 0; i < nverts; i++) {
        int j = M[i];
        if (j > i && !inG[i * nverts + j]) k++;
    }
    return k;
}

static int discrepancy_cycle(const int *A, const int *B, int *cyc, int *visited) {
    /* find first unvisited differing vertex, walk its alternating cycle */
    for (int v0 = 0; v0 < nverts; v0++) {
        if (A[v0] == B[v0] || visited[v0]) continue;
        int len = 0, cur = v0, takeA = 1;
        cyc[len++] = v0; visited[v0] = 1;
        while (1) {
            cur = takeA ? A[cur] : B[cur];
            takeA = !takeA;
            if (cur == v0) break;
            cyc[len++] = cur; visited[cur] = 1;
        }
        return len;
    }
    return 0;
}

static void cycle_exchange(int *A, int *B, const int *cyc, int len) {
    for (int k = 0; k < len; k++) {
        int u = cyc[k], v = cyc[(k + 1) % len];
        if (k % 2 == 0) { B[u] = v; B[v] = u; }
        else            { A[u] = v; A[v] = u; }
    }
}

/* W stored as full n x n double matrix per stage (rebuilt each stage: O(n^2),
 * negligible vs chain steps). */
static double *W;

static void run_fpras(double eps, int samples, int burn, int replicas, uint64_t seed) {
    double b = 1.0 + 1.0 / nverts;
    double ln_b = log(b);
    int J = (int)ceil((nverts / 2.0 * log(nverts) - log(eps / 32.0)) / ln_b);
    double logZ0 = 0.0;
    for (int k = 1; k < nverts; k += 2) logZ0 += log(k);

    unsigned char *inG = calloc(nverts * nverts, 1);
    for (int i = 0; i < nverts; i++)
        for (int j = 0; j < nverts; j++)
            if (adj[i] & (1ULL << j)) inG[i * nverts + j] = 1;

    W = malloc(nverts * nverts * sizeof(double));
    M1 = malloc(nverts * sizeof(int));
    M2 = malloc(nverts * sizeof(int));
    int *cyc = malloc(nverts * sizeof(int));
    int *visited = malloc(nverts * sizeof(int));

    double *ests = malloc(replicas * sizeof(double));
    clock_t t0 = clock();

    for (int rep = 0; rep < replicas; rep++) {
        s[0] = seed * 1000003ULL + rep * 7919ULL + 88172645463325252ULL;
        s[1] = seed ^ 0x9E3779B97F4A7C15ULL;
        for (int i = 0; i < 20; i++) next_u64();
        random_matching(M1);
        random_matching(M2);
        double logZ = logZ0;
        for (int j = 0; j < J; j++) {
            double w = pow(b, -(double)j);
            for (int i = 0; i < nverts; i++)
                for (int k = 0; k < nverts; k++)
                    W[i * nverts + k] = (inG[i * nverts + k] || i == k) ? 1.0 : w;
            for (int t = 0; t < burn; t++) {
                double r = next_double();
                if (r < 1.0 / 3.0 && nverts >= 4) {
                    int a = next_below(nverts), c = next_below(nverts);
                    while (c == a || c == M1[a]) c = next_below(nverts);
                    int b2 = M1[a], d = M1[c];
                    double w_old = W[a*nverts+b2] * W[c*nverts+d];
                    int p11, p12, p21, p22;
                    if (next_double() < 0.5) { p11=a; p12=c; p21=b2; p22=d; }
                    else                     { p11=a; p12=d; p21=b2; p22=c; }
                    double w_new = W[p11*nverts+p12] * W[p21*nverts+p22];
                    if (w_new >= w_old || next_double() < w_new / w_old) {
                        M1[p11] = p12; M1[p12] = p11;
                        M1[p21] = p22; M1[p22] = p21;
                    }
                } else if (r >= 2.0 / 3.0) {
                    memset(visited, 0, nverts * sizeof(int));
                    int len = discrepancy_cycle(M1, M2, cyc, visited);
                    if (len) cycle_exchange(M1, M2, cyc, len);
                }
            }
            double acc = 0.0;
            for (int t = 0; t < samples; t++) {
                double r = next_double();
                if (r < 1.0 / 3.0 && nverts >= 4) {
                    int a = next_below(nverts), c = next_below(nverts);
                    while (c == a || c == M1[a]) c = next_below(nverts);
                    int b2 = M1[a], d = M1[c];
                    double w_old = W[a*nverts+b2] * W[c*nverts+d];
                    int p11, p12, p21, p22;
                    if (next_double() < 0.5) { p11=a; p12=c; p21=b2; p22=d; }
                    else                     { p11=a; p12=d; p21=b2; p22=c; }
                    double w_new = W[p11*nverts+p12] * W[p21*nverts+p22];
                    if (w_new >= w_old || next_double() < w_new / w_old) {
                        M1[p11] = p12; M1[p12] = p11;
                        M1[p21] = p22; M1[p22] = p21;
                    }
                } else if (r >= 2.0 / 3.0) {
                    memset(visited, 0, nverts * sizeof(int));
                    int len = discrepancy_cycle(M1, M2, cyc, visited);
                    if (len) cycle_exchange(M1, M2, cyc, len);
                }
                acc += pow(b, -(double)nonedge_count(M1, inG));
            }
            logZ += log(acc / samples);
        }
        ests[rep] = exp(logZ);
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    double mean = 0; for (int i = 0; i < replicas; i++) mean += ests[i];
    mean /= replicas;
    double var = 0; for (int i = 0; i < replicas; i++) var += (ests[i]-mean)*(ests[i]-mean);
    double se = replicas > 1 ? sqrt(var / (replicas - 1) / replicas) : 0;

    printf("mode=fpras vertices=%d edges=%d stages=%d replicas=%d "
           "estimate=%.6g se=%.6g seconds=%.2f\n",
           nverts, nedges, J, replicas, mean, se, secs);
    free(inG); free(W); free(M1); free(M2); free(cyc); free(visited); free(ests);
}

/* ---------- input ---------- */
static void load_edges(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    int m;
    if (fscanf(f, "%d %d", &nverts, &m) != 2) { fprintf(stderr, "bad header\n"); exit(1); }
    if (nverts > 64) { fprintf(stderr, "n > 64 unsupported\n"); exit(1); }
    adj = calloc(nverts, sizeof(uint64_t));
    int u, v, cnt = 0;
    while (cnt < m && fscanf(f, "%d %d", &u, &v) == 2) {
        adj[u] |= 1ULL << v; adj[v] |= 1ULL << u; cnt++;
    }
    nedges = cnt;
    snprintf(gname, sizeof gname, "%s", path);
    fclose(f);
}

int main(int argc, char **argv) {
    const char *edges = NULL;
    const char *mode = "both";
    double eps = 0.25, p = 0.5;
    int samples = 1024, burn = 1024, replicas = 8;
    uint64_t seed = 42;
    int gnp_n = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--edges")) edges = argv[++i];
        else if (!strcmp(argv[i], "--gnp")) { gnp_n = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "--p")) p = atof(argv[++i]);
        else if (!strcmp(argv[i], "--mode")) mode = argv[++i];
        else if (!strcmp(argv[i], "--eps")) eps = atof(argv[++i]);
        else if (!strcmp(argv[i], "--samples")) samples = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--burn")) burn = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--replicas")) replicas = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seed")) seed = strtoull(argv[++i], NULL, 10);
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 1; }
    }
    if (edges) load_edges(edges);
    else if (gnp_n) {
        /* deterministic LCG-based G(n,p) (independent of Python's RNG) */
        nverts = gnp_n;
        adj = calloc(nverts, sizeof(uint64_t));
        s[0] = seed | 1; s[1] = seed * 0x9E3779B97F4A7C15ULL | 1;
        nedges = 0;
        for (int i = 0; i < nverts; i++)
            for (int j = i + 1; j < nverts; j++)
                if (next_double() < p) { adj[i] |= 1ULL << j; adj[j] |= 1ULL << i; nedges++; }
        snprintf(gname, sizeof gname, "G(%d,%.2f,lcg%llu)", nverts, p,
                 (unsigned long long)seed);
    } else { fprintf(stderr, "need --edges or --gnp n\n"); return 1; }

    if (!strcmp(mode, "exact") || !strcmp(mode, "both")) run_exact();
    if (!strcmp(mode, "fpras") || !strcmp(mode, "both"))
        run_fpras(eps, samples, burn, replicas, seed);
    return 0;
}
