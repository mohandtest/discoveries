# Factory state — the restart-recovery point

Any session resuming work reads this file first and trusts it over its
own memory. Updated at every phase transition and committed with it.

## Loop position

**Pass #3 — near-linear general-graph matching — P0 SELECT (queued).**
Start condition: pass #2 closes (close-out below). Then the loop runs
autonomously; after each P5 it continues to the next queue item.

## Work queue

1. [pass #3] near-linear general-graph matching (ROADMAP candidate #1 —
   the approved pilot)
2. [done 2026-11-10] constants report, algorithm #1 — drafted at
   `reports/algo1-fpras-constants-DRAFT.md` (user go received)
3. [pass #4+] deterministic F_p factorization; mean-payoff games
   (ROADMAP candidates #2–3)
4. [pass #5?] **k-server → KV-cache eviction for local LLM inference**
   (user eureka lens, 2026-11-10): the log²(k+1)-competitive randomized
   k-server pair (`Squared-logarithmic-randomized-k-server...` +
   `Uniform-computation-of-the-squared-logarithmic-k-server-bound...`,
   whose main theorem — polynomial preprocessing + per-request cost —
   was verified verbatim from the paper source). First theory-backed KV
   eviction policy + first implementation of optimal-order k-server;
   ground truth = offline OPT by DP on small traces. Runner-up from
   the same hunt: ω ≤ 9/4 matrix multiplication (needs verification
   more than benchmarking; expected honest NO_ADVANTAGE for local
   sizes). Ranked behind the matching pilot; user can direct a jump.
4. [task] factory improvements queued by retrospectives (none yet)

## Directives (user injections — recorded, then followed)

- 2026-11-10 — formalize the protocol as an autonomous factory loop;
  pilot it on near-linear matching; non-parallel; user out of the loop
  by default. (standing)
- 2026-11-10 — **novelty is the primary criterion for what this project
  takes on** (user standing priority). Market × implementability act as
  gates; novelty decides. (standing)
- Publication policy as in ROADMAP: private work, no external
  artifacts without explicit go. (standing)
- 2026-11-10 — go for the algorithm-#1 constants report draft
  (previously parked on user hold); executed same day.
- 2026-11-10 — **eureka lens: prefer results that improve running
  LLMs locally** (new selection criterion alongside novelty-first; the
  k-server→KV candidate was added to the queue under it).

## Next actions (on pass-#3 start)

1. Load skills `factory-loop` and `factory-researcher`; read
   `factory/phases/P0-SELECT.md`.
2. Failure-aware retrieval: `python3 factory/memory/memory.py similar
   'graph matching'` — pack hits into the briefs.
3. Dispatch the researcher on the paper:
   `math/preprints/Almost-Linear-Time-Maximum-Cardinality-Matching-in-Sparse-General-Graphs-September-24-2026/`
   (result family #120; map analysis in `discovery-map/report_tcs.txt`;
   incumbents: Blossom V and successors).
4. Dispatch the practical-goals briefing; pick per **novelty first**
   (standing user priority; market × implementability as gates); state
   both novelty axes; record pick + rationale here and in ROADMAP;
   create `matching/`.

## Pass #2 close-out (blocks the pilot)

1. Audit applied pre-close (commit 313c622): reporting/orchestration
   blockers fixed; consolidation crash-proofed against t25only rows.
2. Campaign completion: supervisor v2 → capped-case reruns → `DONE.flag`
   (fold via `graph-sampling/fold_campaign.sh`).
3. Fold landed rows → replace the remaining placeholder in
   `graph-sampling/results/MIXING_RESULTS.md` → final assessment vs
   the pre-registered bands (n11d2 already in band, 3.03 sweeps) →
   closing commit.
4. Record outcomes in memory (`observation` rows for landed rows; set
   the sweep-law hypothesis status against the landed bands); close
   the pass #2 entry in `factory/JOURNAL.md`; mark Phase C complete
   in ROADMAP.
5. Then: pass #3 P0 starts, autonomously.
