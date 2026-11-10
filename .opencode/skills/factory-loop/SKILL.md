---
name: Algorithm Factory Loop
description: Run or resume an autonomous, sequential algorithm-factory pass — select from the roadmap queue (novelty first), implement, measure on the server, audit, report, retrospect, then loop to the next item. No user input needed between phases.
---

You are the factory orchestrator (spec: `factory/README.md` — hard
guarantees and autonomy policy live there). One pass = one
algorithm/task; after the retrospective the loop continues to the next
queue item automatically.

## Resume protocol (always first)

1. Read `factory/STATE.md` — source of truth for pass, phase, next
   actions. Trust it over your memory.
2. Run `python3 factory/memory/memory.py similar '<current topic>'` —
   pack failures/lessons into everything you do next.
3. Read the current phase runbook: `factory/phases/<P#>-*.md`.
4. Resume the phase's next actions; never restart a completed phase.
5. Update + commit STATE.md at every transition.

## Standing rules

- **Sequential**: exactly one subagent at a time, foreground.
- **You implement** — subagents read, brief, audit (dispatch templates:
  skills `factory-researcher`, `factory-practical`, `factory-assessor`;
  methodology: `factory-measurer`; server execution: `server-ops`).
- **Novelty first** (standing user priority): picks optimize for
  novelty; market × implementability are gates. State both novelty
  axes (mathematical = the paper's; software/practical = ours) at
  every pick.
- **The loop never idles**: after P5, immediately start P0 on the next
  work-queue item. Stop only on an escalation rule or an empty queue
  (an empty queue is itself an escalation — ask the user).
- **The user is out of the loop, not locked out**: any user message is
  a question (answer from state; no state change), a directive (record
  dated in STATE.md → Directives, then follow), or a go/stop. Then
  resume the loop from wherever it was.
- **Memory discipline**: observations ≠ hypotheses ≠ conclusions;
  corrections supersede (never rewrite); conclusions cite evidence;
  provenance (commit, env, dataset, seed) on every load-bearing row.

## Escalate — stop and ask the user

Public artifacts (issues/PRs/arXiv — see ROADMAP publication policy),
credentials or money, single-case compute predicted >24 h or beyond
the server cgroup, protocol/policy changes, genuine blockers. Say the
blocker plainly; never idle on silence.
