# Factory journal

One retrospective entry per pass, with the factory metrics. Passes #1
and #2 ran the protocol manually — seeded here because their outcomes
are the design evidence for the formal loop. Metrics live here; the
underlying numbers live in the per-algorithm docs.

## Pass #1 — FPRAS for counting perfect matchings (complete)

Pre-factory. Deliverables: `fpras-benchmark/README.md` (living report)
+ `benchmarks/overnight/campaign{1,2}/` (raw data).

| Metric | Value |
|---|---|
| Audits run | 2 adversarial (external GitHub issue #1; pre-launch subagent) + external reviewer cross-validation |
| Findings | issue #1: wrong barbell truth (225), n=2 hang, overstated infeasibility — all real, all fixed |
| Critical catch | uint64 count overflow at n≥44 — would have corrupted the headline ground truth; fixed pre-launch |
| Bugs-caught-per-audit | 3 (external) + 1 critical (subagent) |
| Post-close discovery | hash-clustering bug inflated exact timings above n≈32 → loud correction section; earlier claims superseded, never quietly edited |
| Negative results | coverage 84–93.5% at ε=0.25 vs nominal 95%; sparse ladders 16–25% — recorded, not hidden |
| Restarts survived | overnight campaigns unattended-safe (server-side state) |

Lessons encoded into the factory: audits BEFORE closing commits;
independent cross-verification; correction discipline; exact ground
truth precedes approximation claims.

## Pass #2 — degree-preserving graph sampling (#131) (in flight)

Pre-factory; invented pre-registration + evidence-based caps — now
factory law. Close this entry when the campaign closes.

| Metric | Value |
|---|---|
| Audits run | validation branch (external reviewer; R-hat calibration, 1,800 trials); adversarial audit pre-close: **13 findings, FIX-FIRST — zero correctness findings in the core machinery**; all blockers were in the reporting/orchestration layer, fixed in `313c622` |
| Findings that mattered | consolidation crash on sentinel `t05=-1` (would have fired exactly when t25only rows land); wrong n⁴/3 constant; checkpoint-vs-hitting-time definition; uncommitted cap evidence |
| Predictions pre-registered | sweep-law bands for all frontier rows (commit `1d32259`), stated before outcomes |
| Bands landed | n11d2: t(1/4)=1,000 vs 660–1,320 — **in band** (3.03 sweeps); t(0.05)=1,000 below its secondary band (favorable miss, reported). Remaining rows in flight |
| Kill/cap decisions | n10d3 killed 29 min before its cap (7.6 s/step arithmetic); n10d4 killed after 66,462,606-state enumeration (~44 s/step); n=12 t(0.05) capped by cost model — all decided + documented before outcomes |
| Wall-time recovered | ~2.5 h of zero-yield grinding avoided; rows delivered by bounded standalone reruns |
| Restarts survived | 3 harness restarts — server state (supervisor, DONE.flags, logs) held the pass |
| Real-world results | dolphins z=12.3 (0/800k draws); karate 12.6% contrast; burn/spacing isolation (thin > burn) |

Lessons: consolidation scripts must handle sentinel/partial rows BEFORE
the rows exist; measured cost models decide kills, not patience;
audits bite in the reporting layer exactly where the implementer's own
tests pass.
