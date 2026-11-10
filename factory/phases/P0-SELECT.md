# P0 — SELECT

Entry: previous pass closed, or factory start. Output feeds P1.

1. Read the work queue + directives in `factory/STATE.md` and the
   candidate ranking in `ROADMAP.md`.
2. **Failure-aware retrieval first**:
   `python3 factory/memory/memory.py similar '<candidate topic>'` —
   has anything mathematically or structurally similar been attempted?
   What went wrong, on what evidence? Pack the hits into every brief
   below.
3. Dispatch the researcher subagent (skill `factory-researcher`) on
   the top candidate's papers. One subagent, foreground.
4. Dispatch the practical-goals briefing (skill `factory-practical`)
   on the researcher's brief.
5. **Novelty check** (from the researcher brief, stated in STATE.md):
   (a) the mathematical novelty — the paper's, credited to it; (b) the
   software/practical contribution — the constants report. **Novelty
   is the primary pick criterion (standing user priority)**; market ×
   implementability are gates. The two axes must never be conflated.
6. Pick. You decide — inside the autonomy policy. Record pick +
   rationale + novelty axes in STATE.md; record the pick as a
   `decision` in memory.
7. Create the pass dir; commit the briefs there.

Exit: STATE.md shows the pick at P1 with next actions.

If the queue item is a *task* (not an algorithm): skip briefs only
where they add nothing — say why in STATE.md — then execute the task
and rejoin the loop at P5.
