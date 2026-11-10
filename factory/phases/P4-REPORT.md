# P4 — REPORT

The constants report is the deliverable. Structure (exemplar:
`fpras-benchmark/README.md`):

1. What the paper guarantees vs what was measured — always separated.
2. The constants table (measured, with the exact ground truth used and
   the measurement definition stated — checkpoint grids, units,
   granularity).
3. Practical guidance the numbers support (burn-ins, crossovers,
   budgets) — explicitly not the proof parameters (armor ≠ guidance).
4. **Negative results and caveats at the same prominence as wins** —
   including NO_ADVANTAGE / INCORRECT / INCONCLUSIVE terminations when
   they happened, and prediction misses in either direction.
5. Correction discipline: superseded claims get a loud correction
   section, never a quiet edit.
6. Raw-data pointers so every number is checkable.

Record the pass's conclusions in memory, each linked to the
observations it rests on (kind `conclusion`, `--evidence`). Closing
commit.
