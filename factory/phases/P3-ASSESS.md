# P3 — ASSESS (skill: `factory-assessor`)

1. Freeze code + docs (commit). While the audit runs, touch nothing
   audited.
2. Dispatch the assessor with **primary sources** in the brief: the
   paper path, raw-data paths, and memory-surfaced failure classes
   (`memory.py similar '<pass topic>'` → pack hits).
3. The assessor holds **rejection authority** (factory law): SHIP
   requires independent verification against the paper and the raw
   data — every implementer test passing is NOT sufficient (tests can
   encode the same misreading they should catch). INCORRECT is a
   legitimate verdict; it ends the pass at P4 with an honest report.
4. Triage: fix every CRITICAL/HIGH before the closing commit; document
   MEDIUM/LOW honestly (cheap fixes get fixed). Substantial fixes →
   re-dispatch the assessor on the changed files.
5. Record the verdict + findings in memory (audits → findings is a
   factory metric; lessons for anything general).

Echo-chamber defense: the assessor is the designated circuit breaker —
fresh context, adversarial stance, and it must re-derive the claim
from the paper rather than trust the chain of agent artifacts that led
here.

Exit: verdict SHIP — or a negative terminal state, honestly recorded.
