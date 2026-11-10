#!/bin/sh
# Deploy the overnight campaign to the big server (run from repo root or here).
# Usage: ./deploy.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$(dirname "$HERE")")"          # repo root
SRC_GRAPHS="$ROOT/fpras-benchmark/graphs"
SRC_C="$ROOT/fpras-benchmark/fpras.c"

# graph files needed by config.json that are generated, not committed
python3 - <<'EOF'
import random, os
for (n, p) in ((48, 0.3), (52, 0.3), (56, 0.3), (64, 0.3)):
    tag = int(p * 100)
    path = os.path.join(os.environ.get("SRC_GRAPHS", "."), f"g{n}_p{tag}_s42.edges")
    if os.path.exists(path):
        continue
    rng = random.Random(42)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        f.write("\n".join(f"{u} {v}" for u, v in edges) + "\n")
    print("generated", path)
EOF

ssh -o BatchMode=yes test "mkdir -p ~/overnight/graphs"
scp -q -o BatchMode=yes "$SRC_C" "$HERE/runner.py" "$HERE/run.sh" \
    "$HERE/analyze.py" "$HERE/config.json" test:~/overnight/
scp -q -o BatchMode=yes "$SRC_GRAPHS"/*.edges test:~/overnight/graphs/
echo "deployed to test:~/overnight — launch with:"
echo "  ssh test 'tmux new -s overnight \"sh ~/overnight/run.sh\"'"
