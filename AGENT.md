# AGENT.md — Project Guide for Agents

## What this project is

This workspace is an independent research effort built around
[openai/math](https://github.com/openai/math) — OpenAI's Sept–Oct 2026 release
of 721 machine-generated mathematical manuscripts (373 result families,
~42% Lean-formalized), produced by an internal frontier model.

The project's thesis: **the scarce artifact in this ecosystem is not proof
verification (the community is doing that) but "constants reports" —
implementations that answer "does this algorithm actually run, and at what
cost?"** Papers in the collection give asymptotics; nothing tells you which
proof components are load-bearing in practice. We produce that answer, one
algorithm at a time, with a repeatable protocol.

Deliverables live in **https://github.com/mohandtest/discoveries** (this
directory is that repo's working copy). The `math/` checkout (~3.7 GB) is
gitignored — clone separately if needed.

## Current state (latest first)

- **Overnight benchmark campaign RUNNING** on the remote server (`test`, 24
  cores / 360 GB LXC / Alpine) in a tmux session `overnight`, launched via
  `benchmarks/overnight/run.sh`. Phases: 0 regression gate → 1 reliability
  (200 independent FPRAS runs on g36/g40) → 2 exact n=44 ground truth
  (128-bit, 5.5 h budget) → 3 validation (200 runs on n=44) → 4 scaling
  (n=48–64, two densities + ladders). 8 h hard deadline; RAM ceiling 280 GB,
  kill 330 GB; results in `~/overnight/{results.csv,status.json,runner.log}`
  on the server. When it finishes: run `analyze.py`, commit
  results/status/summary, update READMEs.
- All campaign code audited by an adversarial subagent pass (15 findings,
  all fixed — see git log `5ddb0d2`); pipeline smoke-tested end-to-end.

## Repository layout

```
discovery-map/     — the map of all 373 result families (Phase 1 of effort)
  README.md        — synthesis: 10 recurring techniques, dependency chains,
                     implementability tiers, reliability notes
  report_*.txt(8)  — per-subject-cluster reports: finding/approach/lesson
  subject*.txt(17) — extracted catalogue data
fpras-benchmark/   — algorithm #1: FPRAS for counting perfect matchings
  fpras.c          — C binary: paired-chain FPRAS + exact reachable-state DP
                     (128-bit counts, 24-byte slots, fork-parallel exact)
  chain.py, anneal.py, exact.py, exact2.py, windowed.py, hierarchy.py
  test_chain.py    — unit + regression tests (barbell=225, n=2 hold, etc.)
  bench*.py(1-8)   — experiment sequence; graphs/ = saved inputs g24..g64
  README.md        — the constants report (crossover, coverage, caveats)
benchmarks/overnight/ — the unattended campaign platform
  config.json, runner.py, run.sh, analyze.py, deploy.sh, README.md
README.md          — root: explains the whole effort
```

## How we worked (protocol — follow it for future algorithms)

1. **Map first.** Extract the catalogue (`overview.tex`, `CONTENTS.md`) into
   per-subject files; analyze each cluster (subagents, one at a time —
   concurrency limit is 1 LLM connection); synthesize recurring techniques.
   Result: `discovery-map/`.
2. **Research what already exists** before building (web search): is the
   result implemented? crowded? who are the incumbent tools?
3. **Pick one implementable result** by market × implementability × novelty
   (for #1: the perfect-matching FPRAS — fresh, celebrated, zero
   implementations).
4. **Implement + unit-verify the kernel** (stationarity checks, invariant
   tests, closed-form regression values).
5. **Benchmark against ground truth** — exact counters on identical saved
   graphs, same machine; locate crossovers; report z-scores, coverage, bias.
6. **Invite adversarial audits and fix everything.** This happened twice and
   both were gold: GitHub issue #1 (wrong barbell truth 225, n=2 hang,
   overstated infeasibility) and the pre-launch subagent audit (uint64
   overflow at n≥44 — would have corrupted the headline result; also the
   128-bit pipe protocol was verified above 2^64).
7. **Write the constants report** — honest, empirical-vs-guarantee language,
   negative results included (same-weight replica exchanges collapse to 0;
   windowed/hierarchy variants underperform; proof parameters ~10^73 are
   armor, not guidance).
8. **Commit everything** (code, configs, saved graphs, results; never large
   binaries or the math/ checkout).

## Key findings so far (the substance an agent should know)

- The FPRAS kernel + outer annealing schedule transfer to code and work:
  0–3% error through n≈24 (Python), seconds; C version: n=24–32 head-to-head
  within 1σ of exact truth; exact DP beats FPRAS ≤ n=32; FPRAS ~1,100× faster
  at n=40 (46.6 min exact vs 2.5 s).
- The paper's replication architecture (q=32·(10n)^80(D+1)^9 replicas,
  ~17,000 levels) is worst-case armor: q=2 and 10³–10⁵ steps suffice on all
  tested instances — but naive simplifications genuinely fail (equal-weight
  replica exchanges homogenize and freeze: q=32 returns literally 0).
- Replica-SEs understate error: one 8-replica run was 5σ low vs exact truth;
  hence the 200-independent-run coverage studies in the overnight campaign.
- Exact reachable-state DP is practical far beyond the naive 2^n bound
  (61k states at n=24, 165M at n=40) — arguably a more practical discovery
  than the FPRAS itself; candidate for a networkx contribution
  (`count_perfect_matchings`).
- From the map: next algorithm candidates ranked — near-linear general-graph
  matching (market leader, "single finite program" paper), deterministic
  F_p factorization (chains off Quasi-RH, verifiable vs FLINT), mean-payoff
  games (verification tooling).

## Environment & operations (hard-won specifics)

- **Remote server access**: `sudo -n ip netns exec vpn su - thor -c 'ssh -o
  BatchMode=yes test "<cmd>"'` — needs the sudoers rule for `/usr/sbin/ip`
  (already configured). Server: 24 cores, **360 GB cgroup limit** (LXC —
  `free` shows host RAM 756 GB; use `/sys/fs/cgroup/memory.current`), ~10 GB
  disk, Alpine, python3.12, gcc 15, tmux (apk-added). ssh lands as root;
  binaries at `/root/`. scp via the same netns wrapper.
- **subagents: one at a time, foreground** — the user's API allows one LLM
  connection.
- Shell-quoting through the netns+ssh layers is treacherous: **write scripts
  to files, scp them, run them** — never inline loops over ssh (a `${n}`
  got eaten once and silently no-op'd four jobs; a `&&` chain once prevented
  an orchestrator from launching while echoing success).
- Busybox `pkill` is unreliable there; kill by scanning `/proc/*/cmdline` with
  python3, matching **program basenames** (a substring match once killed the
  killer itself).
- Long jobs on the server: `nohup` inside `tmux` (THP is read-only in the
  LXC; memory-walled parallelism: forked DP workers each grow a full-size
  hash table — parallel-exact is RAM-bound, not compute-bound).
- Local machine is for validation only; heavy compute goes to the server.
- Test everything at toy scale before unattended runs; keep logs small.

## Social record

- GitHub issue #1 on our repo (external audit) — verified, fixed, responded,
  closed courteously (commit `470f1ab`).
- Cross-validated external reviewer's exact counts (77,137,026 /
  26,118,833) — reproduce exactly; their reachable-state DP insight is
  folded into `exact2.py` and the C.
- Community context: openai/math is heavily discussed (HN, MathOverflow);
  OpenAI funds vetting workshops; three Hodge papers were withdrawn in-repo
  for a sign error — treat unformalized claims cautiously and credit audits.

## Immediate next steps (if picking this up fresh)

1. Check campaign results on the server (`~/overnight/`); run `analyze.py`;
   commit `results.csv`, `status.json`, `summary.csv`; update both READMEs
   with the measured coverage table.
2. Write the standalone constants report (arXiv-note shape).
3. Open an issue on openai/math linking the implementation; notify the
   simplified-proof authors (Liu & Meng, arXiv:2610.26803).
4. Draft the networkx PR (`count_perfect_matchings` — reachable-state DP).
5. Start algorithm #2 (near-linear matching) with the same 8-step protocol.
