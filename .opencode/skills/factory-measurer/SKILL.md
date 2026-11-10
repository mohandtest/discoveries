---
name: Factory Measurer
description: Campaign methodology for factory measurements — benchmark gate (small-instance validation + baseline + resource estimate), pre-registered predictions, evidence-based caps, fold, coverage analysis, negative terminal states.
---

# Measurement methodology (P2)

The sequence lives in `factory/phases/P2-MEASURE.md`. This skill carries
the standards.

**Benchmark gate — no large server run without:** (1) small-instance
validation against known truth (local, first); (2) a baseline
(incumbent tool or exact ground truth); (3) a measured resource
estimate (states, s/step, RAM, predicted wall time) — caps follow from
it and are documented BEFORE outcomes.

Before measuring: read `references/pre-registration.md` and commit the
prediction bands before any outcome lands. Before computing any
accuracy claim: read `references/analysis.md`.

Record outcomes as **observations** in memory with provenance — never
as conclusions. NO_ADVANTAGE / INCORRECT / INCONCLUSIVE are legitimate
terminal states; report them like any other result.
