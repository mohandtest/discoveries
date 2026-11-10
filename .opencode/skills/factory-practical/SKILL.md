---
name: Factory Practical Goals
description: Dispatch the practical-goals briefing subagent (P0) — what constants to measure, ground-truth design, real-world claims, OSS contribution targets (recorded only, never acted on).
---

# Practical-goals dispatch (P0, briefing only)

1. Read `references/practical-prompt.md`, fill every {slot} (researcher
   brief, project context, policy), dispatch ONE subagent, foreground.
2. After it returns: save as `{pass-dir}/PRACTICAL_BRIEF.md`; the
   orchestrator picks per **novelty first** (standing user priority),
   with market × implementability as gates, and records the rationale
   + both novelty axes in `factory/STATE.md`.

This role is the map, not the driver: contribution targets it
identifies go to ROADMAP "where we could contribute" — recorded, never
acted on (publication policy: private work, explicit go required).
