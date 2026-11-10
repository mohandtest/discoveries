# Pre-registration template

Before running the campaign, write into the results doc and commit:

1. **The claim/law being tested** — one sentence, in its natural unit
   (e.g. "t(1/4) ≈ 1.5–4 passes over the proposal space"), with the
   measurement definition stated (checkpoint grids, units, granularity
   — an upper bound on a grid is not a hitting time).
2. **Predicted bands per case** — a table: case | natural-unit size |
   predicted range for the headline quantity. Secondary quantities
   (tails, ratios) get their own stated bands.
3. **Decision rules** — what in-band means; that out-of-band rows
   refute the law and will be reported as such (a favorable miss is
   still a miss); what lands INCONCLUSIVE.
4. **Cap decisions** with the measured cost model (s/step, states,
   RAM) — decided BEFORE outcomes; kills only on this arithmetic,
   never on patience.
5. Commit this before the first outcome arrives.

Why: prediction-vs-measured is a factory metric (JOURNAL.md), and it
is what separates a constants report from an anecdote. The n=11 row
landing at 3.03 sweeps inside a pre-registered 660–1,320 band is worth
more than any post-hoc curve fit.
