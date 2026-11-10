/* switch_exact.c — exact TV mixing times for the uniform-quadruple lazy
 * switch chain (the kernel analyzed by OpenAI/math #131: TV(1/4) <= 2n^8).
 *
 * For a given labeled degree sequence, enumerate ALL simple graphs
 * realizing it (backtracking; each state produced exactly once),
 * build the exact transition graph of the chain
 *   P(G,G') = 1/q  for each valid ordered (src,dst) pairing move
 *   P(G,G)  = 1 - deg(G)/q,      q = 12 * C(n,4),
 * and propagate probability vectors exactly from several starting
 * states, recording the first hitting times of TV <= 1/4 and TV <= 0.05
 * against the uniform stationary law.
 *
 * Verified against graph-sampling/exact_mixing.py at n=6 d=2
 * (70 states; TV@0=0.985714, TV@100=0.019548) and against
 * degree_switch_probe.enumerate_degrees state counts.
 *
 * Worst-start is approximated by the max over (1 canonical + R random)
 * starts and labeled as such. The proven 2n^8 is printed alongside.
 *
 * Build: gcc -O2 -o switch_exact switch_exact.c -lm
 * Run:   ./switch_exact --n 6 --regular 2
 *        ./switch_exact --n 8 --degrees 4,3,3,2,2,1,1,0 --starts 32
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mman.h>

typedef unsigned __int128 u128;

static int n;
static int slot[20][20];            /* slot[i][j], i<j */
static int degrees[20];

/* ---------- enumeration by backtracking (each state once) ---------- */
static u128 *states; static uint64_t nstates, cap_states;
static int remaining[20];

static void record(u128 mask) {
    if (nstates == cap_states) {
        cap_states = cap_states ? cap_states * 2 : (1 << 16);
        states = realloc(states, cap_states * sizeof(u128));
        if (!states) { fprintf(stderr, "OOM at %llu states\n",
                               (unsigned long long)cap_states); exit(1); }
    }
    states[nstates++] = mask;
}

static void visit(int i, u128 mask) {
    if (i == n) { record(mask); return; }
    int want = remaining[i];
    if (want < 0) return;
    int cands[20], nc = 0;
    for (int j = i + 1; j < n; j++) if (remaining[j] > 0) cands[nc++] = j;
    if (want > nc) return;
    if (want == 0) { visit(i + 1, mask); return; }
    int idx[20];
    for (int k = 0; k < want; k++) idx[k] = k;
    for (;;) {
        u128 m = mask; int ok = 1;
        for (int k = 0; k < want; k++) {
            int j = cands[idx[k]];
            remaining[j]--;
            m |= (u128)1 << slot[i][j];
            if (remaining[j] < 0) ok = 0;
        }
        if (ok) visit(i + 1, m);
        for (int k = 0; k < want; k++) remaining[cands[idx[k]]]++;
        int k = want - 1;
        while (k >= 0 && idx[k] == nc - want + k) k--;
        if (k < 0) break;
        idx[k]++;
        for (int t = k + 1; t < want; t++) idx[t] = idx[t - 1] + 1;
    }
}

/* ---------- open-addressing hash: mask -> index (single hash fn) ----------
 * Keys are u128 masks; we store the full 128-bit key (two uint64 words)
 * and never resize (pre-sized to 4x states in main). */
static uint64_t *hk1, *hk2; static int64_t *hval; static uint64_t hcap;

static inline uint64_t hash128(u128 key) {
    uint64_t x = (uint64_t)key ^ ((uint64_t)(key >> 64) * 0x9E3779B97F4A7C15ULL);
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    return x ^= x >> 33;
}
static void hput(u128 key, int64_t val) {
    uint64_t p = hash128(key) & (hcap - 1);
    while (hval[p] >= 0) p = (p + 1) & (hcap - 1);
    hk1[p] = (uint64_t)key; hk2[p] = (uint64_t)(key >> 64); hval[p] = val;
}
static int64_t hget(u128 key) {
    uint64_t p = hash128(key) & (hcap - 1);
    uint64_t k1 = (uint64_t)key, k2 = (uint64_t)(key >> 64);
    while (hval[p] >= 0) {
        if (hk1[p] == k1 && hk2[p] == k2) return hval[p];
        p = (p + 1) & (hcap - 1);
    }
    return -1;
}

int main(int argc, char **argv) {
    int regular = -1; char *degs = NULL; int nstarts = 32; uint64_t seed = 42;
    int t25_only = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--n")) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--regular")) regular = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--degrees")) degs = argv[++i];
        else if (!strcmp(argv[i], "--starts")) nstarts = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seed")) seed = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--t25only")) t25_only = 1;
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 1; }
    }
    if (nstarts <= 0) { fprintf(stderr, "bad --starts\n"); return 1; }
    if (n < 4 || n > 16) { fprintf(stderr, "need 4 <= n <= 16\n"); return 1; }
    if (degs) {
        char *s = degs; int i = 0;
        while (*s && i < n) { degrees[i++] = strtol(s, &s, 10); if (*s == ',') s++; }
        if (i != n) { fprintf(stderr, "need %d degrees\n", n); return 1; }
    } else {
        if (regular < 0) { fprintf(stderr, "give --regular d or --degrees list\n"); return 1; }
        for (int i = 0; i < n; i++) degrees[i] = regular;
    }
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += degrees[i];
        if (degrees[i] < 0 || degrees[i] >= n) { fprintf(stderr, "bad degree\n"); return 1; }
    }
    if (sum % 2) { fprintf(stderr, "infeasible: odd degree sum\n"); return 1; }

    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) slot[i][j] = 0;
    int sl = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) slot[i][j] = sl++;

    /* quadruples + the 3 pairings (as slot pairs) */
    static int pa[5000][3][2];
    uint64_t nquad = 0;
    for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++)
      for (int c = b + 1; c < n; c++) for (int d = c + 1; d < n; d++) {
        pa[nquad][0][0] = slot[a][b]; pa[nquad][0][1] = slot[c][d];
        pa[nquad][1][0] = slot[a][c]; pa[nquad][1][1] = slot[b][d];
        pa[nquad][2][0] = slot[a][d]; pa[nquad][2][1] = slot[b][c];
        nquad++;
      }
    double q_inv = 1.0 / (12.0 * (double)nquad);

    for (int i = 0; i < n; i++) remaining[i] = degrees[i];
    visit(0, 0);
    fprintf(stderr, "n=%d states=%llu\n", n, (unsigned long long)nstates);
    if (!nstates) { printf("states=0\n");
        fprintf(stderr, "infeasible: no labeled graphs realize this sequence\n");
        return 1; }

    hcap = 4; while (hcap < nstates * 4) hcap <<= 1;
    hk1 = malloc(hcap * 8); hk2 = malloc(hcap * 8);
    hval = malloc(hcap * 8);
    memset(hval, -1, hcap * 8);
    for (uint64_t s = 0; s < nstates; s++) hput(states[s], (int64_t)s);

    /* transition graph (CSR) */
    uint64_t *sd = calloc(nstates, 8);
    for (uint64_t s = 0; s < nstates; s++) {
        u128 m = states[s]; uint64_t k = 0;
        for (uint64_t qi = 0; qi < nquad; qi++)
            for (int p = 0; p < 3; p++)
                if ((m >> pa[qi][p][0] & 1) && (m >> pa[qi][p][1] & 1))
                    for (int r = 0; r < 3; r++)
                        if (r != p && !(m >> pa[qi][r][0] & 1) && !(m >> pa[qi][r][1] & 1))
                            k++;
        sd[s] = k;
    }
    uint64_t *off = malloc((nstates + 1) * 8); off[0] = 0;
    for (uint64_t s = 0; s < nstates; s++) off[s + 1] = off[s] + sd[s];
    uint64_t *nbr = malloc(off[nstates] * 8);
    uint64_t *fill = calloc(nstates, 8);
    for (uint64_t s = 0; s < nstates; s++) {
        u128 m = states[s];
        for (uint64_t qi = 0; qi < nquad; qi++)
            for (int p = 0; p < 3; p++)
                if ((m >> pa[qi][p][0] & 1) && (m >> pa[qi][p][1] & 1))
                    for (int r = 0; r < 3; r++)
                        if (r != p && !(m >> pa[qi][r][0] & 1) && !(m >> pa[qi][r][1] & 1)) {
                            u128 t = m ^ ((u128)1 << pa[qi][p][0])
                                       ^ ((u128)1 << pa[qi][p][1])
                                       ^ ((u128)1 << pa[qi][r][0])
                                       ^ ((u128)1 << pa[qi][r][1]);
                            int64_t ti = hget(t);
                            if (ti < 0) { fprintf(stderr, "FATAL: neighbor not found\n"); return 1; }
                            nbr[off[s] + fill[s]++] = (uint64_t)ti;
                        }
    }
    /* connectivity */
    char *seen = calloc(nstates, 1);
    uint64_t *stack = malloc(nstates * 8), sp = 0;
    stack[sp++] = 0; seen[0] = 1; uint64_t comp = 0;
    while (sp) {
        uint64_t s = stack[--sp]; comp++;
        for (uint64_t e = off[s]; e < off[s + 1]; e++)
            if (!seen[nbr[e]]) { seen[nbr[e]] = 1; stack[sp++] = nbr[e]; }
    }

    int max_starts = nstarts + 1;
    if ((uint64_t)max_starts > nstates) max_starts = nstates;
    uint64_t *start = malloc(max_starts * 8);
    start[0] = 0;                       /* canonical (backtracking-first) */
    uint64_t rs = seed * 6364136223846793005ULL + 1442695040888963407ULL;
    for (int k = 1; k < max_starts; k++) {
        rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17;
        start[k] = rs % nstates;
    }
    double uniform = 1.0 / nstates;
    const int CAP = 1000000;
    uint64_t totdeg = 0; for (uint64_t s = 0; s < nstates; s++) totdeg += sd[s];
    printf("n=%d degrees=", n);
    for (int i = 0; i < n; i++) printf("%d%s", degrees[i], i + 1 < n ? "," : "");
    printf(" states=%llu quads=%llu avg_state_deg=%.1f connected=%s\n",
           (unsigned long long)nstates, (unsigned long long)nquad,
           (double)totdeg / nstates, comp == nstates ? "yes" : "NO");
    fflush(stdout);

    /* shared result arrays (fork-parallel over starts; the CSR graph is
     * built before forking so workers share it copy-on-write) */
    int *res_t25 = mmap(NULL, sizeof(int) * max_starts, PROT_READ | PROT_WRITE,
                        MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    int *res_t05 = mmap(NULL, sizeof(int) * max_starts, PROT_READ | PROT_WRITE,
                        MAP_SHARED | MAP_ANONYMOUS, -1, 0);

    int cores = 8;
    {   char *ce = getenv("SWITCH_CORES"); if (ce) cores = atoi(ce); }
    if (cores < 1) cores = 1;
    int nworkers = cores < max_starts ? cores : max_starts;
    pid_t *pids = malloc(sizeof(pid_t) * nworkers);
    int launched = 0;
    for (int w = 0; w < nworkers; w++) {
        pid_t pid = fork();
        if (pid == 0) {
            /* worker: starts w, w+nworkers, ... */
            double *p = malloc(nstates * 8), *pn = malloc(nstates * 8);
            for (int k = w; k < max_starts; k += nworkers) {
                memset(p, 0, nstates * 8); p[start[k]] = 1.0;
                int t25 = -1, t05 = -1;
                for (int t = 1; t <= CAP; t++) {
                    memcpy(pn, p, nstates * 8);
                    for (uint64_t s = 0; s < nstates; s++) {
                        double m = p[s]; if (m == 0) continue;
                        pn[s] -= m;
                        pn[s] += m * (1.0 - (double)sd[s] * q_inv);
                        double wgt = m * q_inv;
                        for (uint64_t e = off[s]; e < off[s + 1]; e++) pn[nbr[e]] += wgt;
                    }
                    double *tmp = p; p = pn; pn = tmp;
                    if (t == 1 || t == 2 || t == 5 || t == 10 || t == 25 ||
                        t == 50 || t == 100 || t == 250 || t == 500 ||
                        t == 1000 || t == 2500 || t == 5000 || t == 10000 ||
                        t == 25000 || t == 50000 || t == 100000 ||
                        t == 250000 || t == 500000 || t == 1000000) {
                        double tv = 0;
                        for (uint64_t s = 0; s < nstates; s++) tv += fabs(p[s] - uniform);
                        tv *= 0.5;
                        if (k == 0)
                            fprintf(stderr, "canonical t=%d tv=%.6f\n", t, tv);
                        if (t25 < 0 && tv <= 0.25) t25 = t;
                        if (!t25_only && t05 < 0 && tv <= 0.05) t05 = t;
                        if (tv < 1e-15) {
                            if (t25 < 0) t25 = t;
                            if (t05 < 0) t05 = t;
                            break;
                        }
                    }
                    if (t25 >= 0 && (t25_only || t05 >= 0)) break;
                }
                res_t25[k] = t25; res_t05[k] = t05;
            }
            _exit(0);
        }
        pids[launched++] = pid;
    }
    for (int w = 0; w < launched; w++) waitpid(pids[w], NULL, 0);

    int worst_t25 = -1, worst_t05 = -1;
    for (int k = 0; k < max_starts; k++) {
        int t25 = res_t25[k], t05 = res_t05[k];
        printf("start=%llu t25=%d t05=%d\n",
               (unsigned long long)start[k], t25, t05);
        if (t25 > worst_t25) worst_t25 = t25;
        if (t05 > worst_t05) worst_t05 = t05;
    }
    printf("WORST t_mix(0.25)=%d t_mix(0.05)=%d [max over %d sampled starts, %d cores]\n",
           worst_t25, worst_t05, max_starts, nworkers);
    long long bound = 2 * (long long)pow((double)n, 8.0);
    printf("proven_2n8=%lld overprovision=%.1fx\n", bound,
           worst_t25 > 0 ? (double)bound / worst_t25 : -1.0);
    return 0;
}
