# Incident catalog (what went wrong → the rule it produced)

1. **Eaten `${n}` over ssh** — an inline loop variable was consumed by
   the quoting layers; four jobs silently no-op'd.
   → Rule: scripts to files, scp, run. Never inline loops over ssh.
2. **`&&` chain false success** — an orchestrator failed to launch
   while the chain echoed success.
   → Rule: prefer separate commands; verify effects, not exit echoes.
3. **Busybox `pkill` unreliable** — did not kill the target.
   → Rule: `/proc/*/cmdline` scan with python3.
4. **Substring kill** — a pkill pattern matched the killer itself.
   → Rule: match program basenames exactly.
5. **Hash-clustering bug (fpras.c)** — a hash respecting structured
   keys silently clustered; measured as an algorithmic slowdown for
   weeks; inflated exact timings above n≈32; every earlier timing
   claim superseded (loud correction section).
   → Rule: one hash function everywhere; identical probe paths in
   put/get; suspect silent performance failure from data-structure
   assumptions; cross-verify with an independent implementation.
6. **uint64 overflow at n≥44** — caught only by the pre-launch audit;
   would have corrupted the headline result.
   → Rule: boundary-overflow checks at max sizes; audits BEFORE
   closing commits.
7. **Sleep-based local watchers** — died across 3 harness restarts,
   twice reporting nothing while the compute was fine.
   → Rule: server-side state is the record.
8. **Replica/dependent-run SEs understate error** — an 8-replica run
   read 5σ low vs exact truth.
   → Rule: coverage from genuinely independent runs.
9. **Sentinel crash in consolidation (mixing_table.py)** — a
   partial-measurement mode (`t05=-1`) reached the final table only
   after the pre-planned rows landed; the crash would have fired at
   campaign completion. Caught by audit pre-close.
   → Rule: test consolidation against synthetic/sentinel rows BEFORE
   the rows exist.
10. **Uncommitted orchestration + evidence** — the supervisor script
    and the killed-run cost-model evidence lived only in sessions;
    the audit could not verify pre-outcome cap decisions from the repo.
    → Rule: commit orchestration scripts and decision evidence.
