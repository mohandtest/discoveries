# P2 — MEASURE (methodology: skill `factory-measurer`; ops: `server-ops`)

**Benchmark gate — factory law: no large server run without**

1. small-instance validation against known truth (local, first),
2. a baseline (incumbent tool or exact ground truth),
3. a measured resource estimate (states, s/step, RAM, predicted wall
   time) — caps follow from it and are documented BEFORE outcomes.

Then, in order:

1. **Pre-register predictions before measuring** — bands in the
   results doc, committed before any outcome lands. Out-of-band rows
   refute the law and are reported as such (a favorable miss is still
   a miss).
2. **Exact ground truth** on identical saved instances, same machine;
   instances committed to the repo.
3. **Evidence-based caps/kills** — measured arithmetic stated before
   the kill (the n10d3/n10d4 pattern: s/step × predicted steps).
4. **Campaign** per server-ops patterns: tolerant ladder + supervisor
   + DONE.flag; fold machinery tested against synthetic/partial data
   BEFORE the real rows land.
5. **Analysis** per factory-measurer standards; record outcomes as
   **observations** in memory with provenance (commit, env, dataset,
   seed) — never as conclusions.

**Negative outcomes are legitimate terminal states**: NO_ADVANTAGE,
INCORRECT, INCONCLUSIVE end the pass honestly if that is what the
data says — record, report, proceed to P3/P4 with the honest version.

Exit: results doc finalized (measured table, no placeholders), raw
artifacts + observations committed.
