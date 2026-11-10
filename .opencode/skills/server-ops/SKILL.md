---
name: Server Operations
description: Remote-server execution mechanics for the test box — netns+ssh incantation, scp rules, /proc kill scripts, nohup/tmux, tolerant ladders, supervisors, DONE.flags, RAM limits, incident catalog.
---

# Server operations (the test box)

24 cores, **360 GB cgroup limit** (LXC — `free` shows host RAM; use
`/sys/fs/cgroup/memory.current`), ~10 GB disk, Alpine, python3.12,
gcc 15, tmux (apk). ssh lands as root; binaries at `/root/`.

## Access

```sh
sudo -n ip netns exec vpn su - thor -c 'ssh -o BatchMode=yes test "<cmd>"'
```

scp needs absolute local paths, same netns wrapper.

## Hard rules (each one cost a real incident)

1. **Never inline loops over ssh** — write scripts to files, scp them,
   run them (a `${n}` was once eaten by the quoting layers and four
   jobs silently no-op'd; a `&&` chain once echoed success while
   launching nothing).
2. **Kill by scanning `/proc/*/cmdline` with python3, matching
   program basenames** — busybox `pkill` is unreliable, and a
   substring match once killed the killer itself.
3. **Long jobs: `nohup` inside `tmux`** — ssh disconnects must not be
   load-bearing; supervisors write DONE.flags; logs are the record.
4. **Parallel-exact is RAM-bound, not compute-bound** — forked workers
   each grow a full-size hash table; check the cgroup before scaling
   worker counts.
5. **Local sleep-watchers die with harness restarts** — server-side
   state (supervisors, flags, logs) is what survives; treat watchers
   as conveniences, never the record.

## Before building new orchestration

Read `references/incidents.md` (the catalog: what went wrong → the
rule it produced) and `references/patterns.md` (tolerant ladder,
supervisor, fold — the proven campaign shapes).
