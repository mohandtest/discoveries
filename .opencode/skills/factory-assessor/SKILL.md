---
name: Factory Assessor
description: Dispatch the adversarial audit subagent before every closing commit — rejection authority, independent verification against primary sources, proven bug classes, severity-rated findings, SHIP/FIX-FIRST verdict.
---

# Assessor dispatch (P3)

1. Freeze code + docs (commit); while the audit runs, touch nothing
   audited.
2. Run `python3 factory/memory/memory.py similar '<pass topic>'` and
   pack the failure classes into the brief.
3. Read `references/assessor-prompt.md`, fill every {slot} (mission,
   verified-already list, files with what to verify), dispatch ONE
   subagent, foreground.

The assessor holds **rejection authority**: SHIP requires independent
verification against the paper and the raw data — every implementer
test passing is NOT sufficient (tests can encode the same misreading
they should catch). INCORRECT is a legitimate verdict and ends the
pass honestly. The assessor is the echo-chamber circuit breaker: it
must re-derive claims from primary sources, not trust the chain of
agent artifacts.

After: fix every CRITICAL/HIGH before the closing commit; document
MEDIUM/LOW honestly; substantial fixes → re-dispatch on the diff.
Record verdict + findings in memory.
