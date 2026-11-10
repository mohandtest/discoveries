#!/bin/sh
# Mixing-curve ladder for the uniform-quadruple lazy switch chain (#131).
# Runs switch_exact across sizes and degree shapes; each case logs to
# results/mixing/<tag>.txt. Fast cases first; the n=12 frontier last.
# A failed/infeasible case is logged and skipped, never kills the ladder.
# Cores per case: SWITCH_CORES (default 22 on the server).
mkdir -p results/mixing
CORES="${SWITCH_CORES:-8}"
run() {
  tag="$1"; shift
  echo "=== $tag: $* ==="
  if SWITCH_CORES="$CORES" ./switch_exact "$@" > "results/mixing/$tag.txt" 2> "results/mixing/$tag.err"; then
    grep -h "states=\|WORST\|proven" "results/mixing/$tag.txt"
  else
    echo "$tag: exit nonzero -- $(tail -1 "results/mixing/$tag.err")"
    if grep -q "infeasible\|states=0" "results/mixing/$tag.err" "results/mixing/$tag.txt" 2>/dev/null; then
      echo "$tag INFEASIBLE (logged, skipped)"
    else
      echo "$tag FAILED (logged, continuing)"
    fi
  fi
}

# regression gate: must reproduce exact_mixing.py (n=6 d=2: t25=50 t05=100)
run n6d2        --n 6 --regular 2 --starts 32
grep -q "t_mix(0.25)=50 t_mix(0.05)=100" results/mixing/n6d2.txt \
  || { echo "REGRESSION GATE FAILED (n6d2)"; exit 1; }

# heterogeneous anchors (cross-checked vs enumerate_degrees: 17 / 27 / 15)
run n6hetA      --n 6 --degrees 3,3,2,2,1,1 --starts 32
run n6hetB      --n 6 --degrees 4,3,3,2,2,2 --starts 32
run n6hetC      --n 6 --degrees 3,2,2,1,1,1 --starts 32

# dense ladder (n*d must be even: no d=3 at odd n)
run n8d2        --n 8 --regular 2 --starts 32
run n8d3        --n 8 --regular 3 --starts 32
run n8d4        --n 8 --regular 4 --starts 32
run n9d2        --n 9 --regular 2 --starts 32
run n9d4        --n 9 --regular 4 --starts 32
run n10d2       --n 10 --regular 2 --starts 32
run n10d3       --n 10 --regular 3 --starts 32
run n10d4       --n 10 --regular 4 --starts 32
run n11d2       --n 11 --regular 2 --starts 32
run n12d2       --n 12 --regular 2 --starts 8

# heterogeneous / heavy-tail shapes
run n8het       --n 8 --degrees 6,5,5,4,4,4,3,3 --starts 32
run n10het      --n 10 --degrees 5,4,4,3,3,3,2,2,2,2 --starts 32
run n11het      --n 11 --degrees 6,4,4,4,3,3,3,3,2,2,2 --starts 32
run n12het      --n 12 --degrees 5,4,4,4,4,3,3,3,2,2,2,2 --starts 8

echo "LADDER COMPLETE"
