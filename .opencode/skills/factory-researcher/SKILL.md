---
name: Factory Researcher
description: Dispatch the researcher subagent (P0) that turns openai/math papers into an implementation brief — result statement, kernel, ground-truth options, incumbents, both novelty axes, verdict.
---

# Researcher dispatch (P0)

1. Run `python3 factory/memory/memory.py similar '<candidate topic>'`
   first — pack any failures/lessons into the brief.
2. Read `references/researcher-prompt.md`, fill every {slot} with real
   context (paper paths from `math/`, project pointers, constraints),
   then dispatch ONE subagent, foreground. A subagent is only as good
   as its brief — pack it fully.
3. After it returns: save as `{pass-dir}/RESEARCH_BRIEF.md`,
   spot-check the load-bearing citations against the actual paper,
   then dispatch the practical-goals briefing (skill
   `factory-practical`).

The researcher reads the PAPER (primary source) — not earlier agents'
summaries of it. That is the first link of the assumption-drift
defense.
