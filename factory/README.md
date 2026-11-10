# The Algorithm Factory

An autonomous, sequential loop that turns results from the
[openai/math](https://github.com/openai/math) catalogue into **constants
reports** — implementations that answer *"does this algorithm actually
run, and at what cost?"* — one algorithm per pass, run end-to-end by the
orchestrator with no user input needed between passes or phases.

This is the 8-step protocol of `AGENTS.md` formalized. Passes #1
(perfect-matching FPRAS) and #2 (degree-preserving graph sampling) ran it
manually; their outcomes are the design evidence: two adversarial audits
that caught real bugs, three harness restarts survived by on-disk state,
two evidence-based process kills that recovered hours of wall time.
Pass #3 pilots the formal loop.

## Design constraints (why it looks like this)

- **Sequential only.** The environment allows one LLM connection: exactly
  one subagent at a time, in the foreground. Never dispatch in parallel.
- **The orchestrator implements.** Implementations need full session
  context and iterative debugging (the hash-clustering root-cause took
  profiles + git history + a control experiment). Fresh subagents inherit
  none of that. Subagents read, brief, and audit; the orchestrator
  builds.
- **Briefs carry everything.** A subagent is only as good as its brief.
  Every dispatch must contain: mission, verified-facts-so-far (what not
  to redo), files, constraints, and the deliverable format. The role
  skills below are the templates.
- **Autonomous within the standing policy.** The publication policy in
  `ROADMAP.md` is the boundary. Inside it, the orchestrator decides:
  which candidate to run, kill-or-ride compute calls, caps, reruns,
  commits, pushes, and when to proceed to the next pass.
- **State lives on disk.** Everything survives harness restarts: this
  spec, `STATE.md`, `JOURNAL.md`, server-side DONE.flags and logs.

## The loop

```
P0 SELECT → P1 IMPLEMENT → P2 MEASURE → P3 ASSESS → P4 REPORT → P5 RETRO
      ▲                                                              │
      └──────────────────── next ROADMAP candidate ◄──────────────────┘
```

| Phase | Who | Entry | Exit |
|---|---|---|---|
| **P0 SELECT** | researcher subagent → practical-goals subagent → orchestrator picks | ROADMAP candidate ranking | pick + rationale recorded in `STATE.md`; brief committed in the pass dir |
| **P1 IMPLEMENT** | orchestrator | pick recorded | kernel + unit tests passing (stationarity, invariants, closed-form regressions); independent cross-check where feasible; kernel↔paper correspondence documented |
| **P2 MEASURE** | orchestrator, measurer methodology | implementable + verified kernel | campaign complete; results doc finalized with measured constants |
| **P3 ASSESS** | assessor subagent → orchestrator fixes | results doc drafted (code frozen) | verdict SHIP; every blocking finding fixed |
| **P4 REPORT** | orchestrator | SHIP | constants report committed: empirical-vs-guarantee language, negative results, correction discipline |
| **P5 RETRO** | orchestrator | report committed | `JOURNAL.md` entry with factory metrics; ROADMAP updated; `STATE.md` reset for next pass |

Per-phase runbooks: `factory/phases/` (one short file per phase). The
`factory-loop` skill is the entry point.

**The loop is continuous by design.** P5's exit transition is "begin P0
of the next item," automatically — the retrospective is a phase, not a
finish line. The fuel is the **work queue** in `factory/STATE.md`:
ROADMAP algorithm candidates, ROADMAP writing tasks, improvements
queued by past retrospectives, and user directives. The loop stops only
when an escalation rule fires or the queue is empty (an empty queue is
itself an escalation — ask the user).

## Roles

| Role | Runs as | Produces | Hard constraints |
|---|---|---|---|
| **Researcher** | subagent (fresh context) | implementation brief: result statement, kernel, ground-truth options, incumbents, verdict | reads the actual papers in `math/`; web-searches incumbents; quotes load-bearing claims |
| **Practical-goals** | subagent (briefing only) | ranked experiment options: which constants, which ground truth, real-world claims, contribution targets | **no action, ever** — contribution targets are recorded in ROADMAP, not acted on |
| **Implementer** | the orchestrator itself | code + tests + docs | never a fresh subagent |
| **Measurer** | orchestrator (methodology) | campaign data + analysis | pre-registration discipline; negative results included |
| **Assessor** | subagent (fresh context) | severity-rated findings + SHIP/FIX-FIRST verdict | report only; dispatched before every closing commit |

Dispatch templates: skills `factory-researcher`, `factory-practical`,
`factory-measurer`, `factory-assessor`.

## Hard guarantees (factory law)

1. **Independent verification is mandatory.** The assessor can REJECT
   an implementation even when every implementer-written test passes —
   tests can encode the same misreading they should catch. The assessor
   verifies against primary sources (the paper, the raw data), not the
   chain of agent artifacts, and writes its own small independent tests
   where feasible. A pass advances on the assessor's SHIP verdict,
   never on green tests alone.
2. **Benchmark gate before expensive campaigns.** No large server run
   without: (a) small-instance validation against known truth, (b) a
   baseline (incumbent tool or exact ground truth), (c) a measured
   resource estimate (states, s/step, RAM, predicted wall time). Caps
   follow from that estimate and are documented before outcomes.
3. **Explicit novelty check.** Every pick states two axes separately:
   (a) the *mathematical* novelty — the paper's, credited to it; (b)
   the *software/practical* contribution — the constants report. A
   useful software contribution does not require mathematical novelty,
   but the two must never be conflated.
4. **Negative outcomes are legitimate terminal states.** NO_ADVANTAGE
   (measured honestly against the baseline), INCORRECT (implementation
   refuted by independent verification), and INCONCLUSIVE (evidence
   insufficient) end a pass in the journal like any other result —
   recorded, reported, never concealed or spun.

## Assumption-drift defense (the echo-chamber risk)

Agents reinforce one another's assumptions: a researcher misreads a
theorem, the implementer builds the wrong algorithm, the measurer
benchmarks it faithfully, and the assessor trusts the original
interpretation. Countermeasures, built into the role briefs:

- Every role receives **primary sources**, not only the previous
  agent's summary: the researcher reads the paper; the implementer
  documents kernel↔paper correspondence from the paper itself; the
  measurer reads raw output files; the assessor re-derives claims from
  the paper and the raw data.
- The assessor is the designated circuit breaker: fresh context,
  adversarial stance, rejection authority (law 1).
- The measurer records **observations** — raw, provenance-tagged;
  hypotheses and conclusions live as separate linked rows that can be
  refuted or superseded. A failed benchmark can never become a verified
  algorithmic fact through repeated agent summaries.

## Structured memory (SQLite + FTS5; RAG only when proven necessary)

`factory/memory/` — SQLite (`factory.db`) for experiments, findings,
decisions, failures, and provenance; retrieval via FTS5 keyword search
(`memory.py`). Git + Markdown remain the canonical research artifacts
(code, reports, STATE.md, JOURNAL.md); the DB is the operational
memory that survives agent sessions. `factory.db` is generated
(gitignored) — `memory.py init && python3 seed.py` restores the
founding memories; rows accumulate across sessions in the working
copy.

Implementation order (memory first, RAG later):

1. **In place at formalization**: STATE.md + JOURNAL.md + SQLite
   tables + FTS5 keyword retrieval, seeded with passes #1–2.
2. **Failure-aware retrieval before every subagent dispatch**:
   `memory.py similar '<topic>'` answers *have we attempted something
   mathematically or structurally similar? what went wrong, and what
   evidence established the failure?* — and the hits go into the brief.
3. Semantic/embedding retrieval only when keyword search demonstrably
   misses (then measure the miss).
4. Memory quality evaluated by questions with known answers from
   earlier experiments (retrieval precision; unsupported-claim checks).

No vector database (Chroma/Pinecone/…): not justified by corpus size.

## Autonomy policy

**Decide autonomously** (no user input):
- Which candidate to run (per the ROADMAP ranking: market ×
  implementability × novelty)
- Kill-or-ride compute decisions — with measured arithmetic recorded
  before the kill
- Evidence-based caps and reruns, documented before outcomes
- All repo work: implement, test, measure, docs, commits, pushes to the
  private repo
- Dispatching role subagents (one at a time, foreground)
- Proceeding to the next pass when one closes

**Escalate — stop and ask the user clearly:**
- Any public artifact: issues on openai/math, PRs to upstreams (networkx
  included), arXiv, anything not this private repo
- Credentials, accounts, or money
- Compute outside standing bounds: any single case predicted >24 h
  (cap it and document instead), anything beyond the server's 360 GB
  cgroup, or non-server compute infrastructure
- Changes to this protocol or the ROADMAP policy itself
- A genuine blocker (say so plainly; don't idle)

## User injections (out of the loop, not locked out)

The user is **out of the loop by default** — no phase waits for input —
but may interject at any moment. Treat every user message as one of:

1. **Question** — answer it from `STATE.md` and the repo; do not change
   loop state. Then carry on.
2. **Directive** — record it (dated) in `STATE.md` → *Directives*, then
   follow it. Directives override autonomous picks and re-rank the
   queue; one that changes policy also updates `ROADMAP.md`/this spec.
3. **Go / stop** — proceed with or halt the current phase.

Interjections are asynchronous overrides, never required steps. After
handling one, the loop resumes from wherever it was.

## State protocol (restart-tolerance)

- **`factory/STATE.md`** — the live state machine: current pass, phase,
  next actions, open decisions, pointers. Updated at every transition,
  committed with it. **First thing any session reads to resume.**
- **`factory/JOURNAL.md`** — one retrospective entry per pass with the
  factory metrics; the factory measuring itself.
- **`factory/memory/`** — structured operational memory (SQLite +
  FTS5; see the memory section above).
- **`ROADMAP.md`** — sequencing, publication policy, candidate ranking
  (SELECT's standing input from the user).
- **Server** — DONE.flags + logs are the ground truth for compute state;
  local watchers are conveniences, never the record.

## Factory metrics (recorded per pass in `JOURNAL.md`)

- Audits run → findings by severity → **bugs-caught-per-audit**
- Predictions pre-registered → **landed in-band / out-of-band**
- Kill/cap decisions → **wall-time recovered or wasted**
- **Restarts survived** (did `STATE.md` + server state recover the pass?)
- Negative results recorded (a factory that only reports wins is lying)

## Skills (`.opencode/skills/`)

| Skill ID | Load when |
|---|---|
| `factory-loop` | starting or resuming any pass — the master runbook |
| `factory-researcher` | P0 researcher dispatch |
| `factory-practical` | P0 practical-goals dispatch |
| `factory-measurer` | P2 campaign methodology |
| `factory-assessor` | P3 audit dispatch |
| `server-ops` | any server execution (every campaign) |

## History

- **Pass #1** — FPRAS for counting perfect matchings (pre-factory,
  complete; the protocol's proof of concept)
- **Pass #2** — degree-preserving graph sampling, result family #131
  (pre-factory, closing; pre-registration + evidence-based caps were
  invented here and are now factory law)
- **Pass #3** — near-linear general-graph matching (the pilot of the
  formal loop)
