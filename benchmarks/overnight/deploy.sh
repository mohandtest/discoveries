#!/bin/sh
# Deploy the overnight campaign to the big server (run from repo root or here).
# Usage: ./deploy.sh
# All graph files are committed under fpras-benchmark/graphs/ (17 files).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$(dirname "$HERE")")"          # repo root
SRC_GRAPHS="$ROOT/fpras-benchmark/graphs"
SRC_C="$ROOT/fpras-benchmark/fpras.c"

ssh -o BatchMode=yes test "mkdir -p ~/overnight/graphs"
scp -q -o BatchMode=yes "$SRC_C" "$HERE/runner.py" "$HERE/run.sh" \
    "$HERE/analyze.py" "$HERE/config.json" test:~/overnight/
scp -q -o BatchMode=yes "$SRC_GRAPHS"/*.edges test:~/overnight/graphs/
# clean stale campaign artifacts so results are a single campaign (audit #12)
ssh -o BatchMode=yes test "cd ~/overnight && rm -f results.csv status.json runner.log summary.csv && chmod +x run.sh && ls graphs | wc -l"
echo "deployed to test:~/overnight — launch with:"
echo "  ssh test 'tmux new -s overnight \"sh ~/overnight/run.sh\"'"
