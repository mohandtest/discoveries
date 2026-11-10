#!/usr/bin/env python3
"""Supervisor v2.1: the single campaign-orchestration process.

1. Bounds each in-ladder case at BOUND_S wall seconds (killed cases fall
   through the ladder's tolerant run(), logged as capped).
2. v2.1: ladder-death check — if the log goes idle with no live
   switch_exact and no LADDER COMPLETE, treat the ladder as dead and
   proceed to the rerun phase (the FAILED lines in the log define the
   rerun list either way).
3. After LADDER COMPLETE (or death): reruns every capped case
   standalone (up to RERUN_S each), overwriting its result file.
4. Consolidates the final table and writes DONE.flag.

Replaces gs_supervise.py + gs_finalize.sh. Run with nohup.

Deployment note: the campaign-#2 instance running on the server is
v2.0 (no death check); the ladder is monitored manually during that
campaign window, so the delta is accepted. Future campaigns deploy
this file as-is.
"""
import glob
import os
import re
import subprocess
import time

BOUND_S = 5400    # 90 min per in-ladder case
RERUN_S = 14400   # 4 h per standalone rerun
DEAD_S = 1800     # log idle + no live process for 30 min -> ladder dead
HOME = os.path.expanduser('~')
GS = f'{HOME}/gs'
LOG = f'{GS}/results/ladder.log'

CASES = {
    'n10d3':  ['--n', '10', '--regular', '3', '--starts', '8'],
    'n10d4':  ['--n', '10', '--regular', '4', '--starts', '8', '--t25only'],
    'n11d2':  ['--n', '11', '--regular', '2', '--starts', '8'],
    'n12d2':  ['--n', '12', '--regular', '2', '--starts', '4', '--t25only'],
    'n8het':  ['--n', '8', '--degrees', '6,5,5,4,4,4,3,3', '--starts', '8'],
    'n10het': ['--n', '10', '--degrees', '5,4,4,3,3,3,2,2,2,2', '--starts', '8'],
    'n11het': ['--n', '11', '--degrees', '6,4,4,4,3,3,3,3,2,2,2', '--starts', '8'],
    # n12d2/n10d4 measured at the theorem threshold (t(1/4) only): full
    # t(0.05) propagation is bandwidth-bound (n10d4: 66.5M states measured,
    # ~44 s/step at 22 workers -> 5-10 h). t25-only at 4-8 workers fits the
    # 4 h rerun bound. n12het left out (same cost model as n12d2 with less
    # marginal value; documented via extrapolation).
}


def any_switch_exact_alive():
    for p in glob.glob('/proc/[0-9]*/cmdline'):
        try:
            exe = open(p, 'rb').read().split(b'\0')[0]
            if os.path.basename(exe.decode()) == 'switch_exact':
                return True
        except (OSError, ValueError, IndexError):
            pass
    return False


def kill_all_switch_exact():
    for p in glob.glob('/proc/[0-9]*/cmdline'):
        try:
            exe = open(p, 'rb').read().split(b'\0')[0]
            if os.path.basename(exe.decode()) == 'switch_exact':
                os.kill(int(p.split('/')[2]), 9)
        except (OSError, ValueError, IndexError):
            pass


def main():
    last_tag, tag_since = None, time.time()
    log_mtime = os.path.getmtime(LOG)
    dead = False
    while True:
        try:
            log = open(LOG).read()
            mtime = os.path.getmtime(LOG)
        except OSError:
            time.sleep(60)
            continue
        if 'LADDER COMPLETE' in log:
            break
        # v2.1: ladder-death check (idle log + no live process)
        if (mtime == log_mtime and time.time() - mtime > DEAD_S
                and not any_switch_exact_alive()):
            dead = True
            print(f'{time.strftime("%F %T")} ladder appears dead '
                  f'(no COMPLETE, log idle {DEAD_S}s, no live process) '
                  '-- proceeding to reruns', flush=True)
            break
        log_mtime = mtime
        tags = re.findall(r'^=== (\w+):', log, re.M)
        cur = tags[-1] if tags else None
        if cur != last_tag:
            last_tag, tag_since = cur, time.time()
        elif time.time() - tag_since > BOUND_S:
            print(f'{time.strftime("%F %T")} capping {cur} '
                  f'({BOUND_S}s bound)', flush=True)
            kill_all_switch_exact()
            tag_since = time.time()
        time.sleep(60)

    capped = re.findall(r'^(\w+) FAILED \(logged, continuing\)', log, re.M)
    print(f'{time.strftime("%F %T")} ladder complete; capped cases to '
          f'rererun standalone: {capped}', flush=True)
    for tag in capped:
        if tag not in CASES:
            continue
        print(f'{time.strftime("%F %T")} rerunning {tag} standalone '
              f'(<= {RERUN_S}s)', flush=True)
        with open(f'{GS}/results/mixing/{tag}.txt', 'w') as out, \
             open(f'{GS}/results/mixing/{tag}.err', 'w') as err:
            try:
                subprocess.run([f'{GS}/switch_exact'] + CASES[tag], cwd=GS,
                               stdout=out, stderr=err,
                               env=dict(os.environ, SWITCH_CORES='22'),
                               timeout=RERUN_S)
            except subprocess.TimeoutExpired:
                print(f'{time.strftime("%F %T")} {tag} rerun bound hit '
                      f'({RERUN_S}s) -- documented as extrapolation',
                      flush=True)
    with open(f'{GS}/results/final_table.txt', 'w') as out:
        subprocess.run(['python3', f'{GS}/mixing_table.py'], cwd=GS,
                       stdout=out, stderr=subprocess.STDOUT)
    with open(f'{GS}/DONE.flag', 'w') as f:
        f.write(time.strftime('%F %T')
                + (' LADDER-DEAD\n' if dead else '\n'))
    print(f'{time.strftime("%F %T")} ALL DONE', flush=True)


if __name__ == '__main__':
    main()
