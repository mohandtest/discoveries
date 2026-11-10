# Campaign patterns (proven in passes #1–2)

## Tolerant ladder

A shell script runs cases sequentially; every case's failure is
logged, never fatal:

```
=== TAG: <args> ===
TAG: exit nonzero -- <why>
TAG FAILED (logged, continuing)
```

The `FAILED (logged, continuing)` line is a **contract** —
supervisors regex it for rerun lists. Keep it byte-stable.

## Supervisor

nohup'd python3 watching the ladder log: bounds each case at a wall
clock (kills via /proc basename scan on overrun), detects ladder
death (idle log + no live process), then after LADDER COMPLETE (or
death) reruns capped cases standalone (reduced starts /
threshold-only modes, inside a time bound), consolidates the final
table, writes DONE.flag. Reference: `graph-sampling/gs_supervise2.py`.

## Threshold-only measurement (the `--t25only` pattern)

When full propagation is bandwidth-bound, measure the theorem's own
threshold only. Decide by measured s/step × predicted steps; document
pre-outcome; state in the report what was measured vs extrapolated.

## Fold

scp per-case artifacts down; consolidate with a table script **tested
against synthetic/partial/sentinel rows before the real rows land**;
placeholders in the results doc are replaced only when rows exist.

## Watchers

Background `sleep N && ssh ...` shells to report events —
conveniences, never the record (incident #7).
