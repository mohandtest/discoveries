# AGENTS.md — Project Guide for Agents

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

## Current state

- **Algorithm #1 (perfect-matching FPRAS)** — complete: constants report
  in `fpras-benchmark/README.md`; raw campaign data in
  `benchmarks/overnight/campaign{1,2}/`.
- **Algorithm #2 (degree-preserving graph sampling, result family #131)**
  — in progress: `graph-sampling/` (docs, code, results).
- Status, plan, sequencing, and the publication policy live in
  **`ROADMAP.md`** — not here. Perishable benchmark numbers live in the
  per-algorithm result docs — also not here.

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

## Key findings so far (qualitative — numbers live in the per-algorithm docs)

- The FPRAS kernel + outer annealing schedule transfer to code and work at
  practical parameters, and the exact reachable-state DP is practical far
  beyond the naive 2^n bound. Measured curves, crossovers, and the n=44
  ground truth: `fpras-benchmark/README.md` — see its **correction
  section**: early exact-timing claims there were inflated by a hash bug
  and are superseded; trust only the corrected curve.
- The paper's replication architecture is worst-case armor: tiny replica
  counts and short chains suffice on all tested instances — but naive
  simplifications genuinely fail (equal-weight replica exchanges
  homogenize and freeze; q=32 returns literally 0). Proof parameters
  ~10^73 are armor, not guidance.
- Replica-based standard errors understate true error — accuracy claims
  need many genuinely independent runs (the campaign's 200-run coverage
  studies exist for this reason).
- The switch chain of result family #131 mixes in a few passes over its
  proposal space in practice — measured constants and real-network
  results: `graph-sampling/results/MIXING_RESULTS.md`.
- From the map: next algorithm candidates are ranked in `ROADMAP.md` —
  near-linear general-graph matching, deterministic F_p factorization,
  mean-payoff games.

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
