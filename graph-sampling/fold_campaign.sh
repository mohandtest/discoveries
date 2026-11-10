#!/bin/sh
# One-shot fold: pull campaign artifacts from the server, consolidate the
# mixing table locally, print state + any capping events + the table.
# Usage: sh fold_campaign.sh   (from graph-sampling/)
set -e
cd "$(dirname "$0")"
echo "=== server state ==="
sudo -n ip netns exec vpn su - thor -c 'ssh -o BatchMode=yes -o ConnectTimeout=15 test "date -u; ls ~/gs/DONE.flag 2>/dev/null && echo FINALIZED || echo ladder-in-progress; grep -E \"capping|rerunning|ALL DONE|bound hit\" ~/gs/supervise2.log 2>/dev/null | tail -6; grep -cE \"^===\" ~/gs/results/ladder.log"' 2>&1 | tail -10 || echo "(state check skipped -- connection)"
echo "=== pulling per-case results ==="
sudo -n ip netns exec vpn su - thor -c 'cd /home/thor/projects/math-discovery/graph-sampling && scp -q -o BatchMode=yes "test:~/gs/results/mixing/*.txt" results/mixing/ && { scp -q -o BatchMode=yes "test:~/gs/results/mixing/*.err" results/mixing/ || true; }'
ls results/mixing/*.txt | wc -l
echo "=== consolidated table ==="
python3 mixing_table.py
