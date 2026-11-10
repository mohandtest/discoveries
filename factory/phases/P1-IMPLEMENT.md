# P1 — IMPLEMENT (orchestrator-only)

Never hand implementation to a fresh subagent — it lacks session
context, and the debugging goes badly. You build.

1. **Retrieval first**:
   `python3 factory/memory/memory.py similar '<kernel topic>'` —
   known hazard classes from earlier passes (hash assumptions,
   overflow at max sizes, precision); address each explicitly.
2. Implement the kernel exactly as the paper states it; document the
   kernel↔paper correspondence in the pass dir **from the paper
   (primary source — not the researcher's brief)**: parameters,
   laziness, proposal distribution, quoted with section refs.
3. Unit-verify before anything else:
   - stationarity / invariant tests
   - closed-form regression values (count small cases by hand)
   - the failure paths (infeasible inputs, degenerate cases)
4. **Independent cross-check** where feasible: a second
   implementation agreeing to all printed digits at ≥2 sizes. This is
   the audit foundation for the whole pass (the `exact_mixing.py`
   pattern: C ↔ Python, six digits, n=6 and n=8).
5. Toy scale first, server later. Commit.

Exit: tests green; correspondence + cross-check docs in the pass dir;
P2's benchmark-gate prerequisites identified (baseline candidate,
small-instance truths).
