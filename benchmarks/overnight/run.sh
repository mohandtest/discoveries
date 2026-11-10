#!/bin/sh
# Overnight benchmark campaign launcher. Safe against SSH disconnects:
#   tmux new -s overnight './run.sh'
# or: nohup ./run.sh > campaign.log 2>&1 &
# Compilation happens in runner.py phase 0 (uses ./fpras.c if present,
# else ../fpras.c — repo checkout vs deployed layout).
cd "$(dirname "$0")"
mkdir -p graphs
exec python3 runner.py config.json
