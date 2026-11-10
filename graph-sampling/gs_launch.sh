#!/bin/sh
# Server launch: build, regression-gate, then the mixing ladder (22 cores)
# and the dolphins tail quantification concurrently. Run inside tmux.
cd ~/gs || exit 1
mkdir -p results/mixing
gcc -O2 -o switch_exact switch_exact.c -lm || { echo BUILD_FAILED; exit 1; }
./switch_exact --n 6 --regular 2 --starts 8 > results/gate.txt 2>&1
grep -q "t_mix(0.25)=50 t_mix(0.05)=100" results/gate.txt \
  || { echo GATE_FAILED; cat results/gate.txt; exit 1; }
echo GATE_OK

python3 dolphins_tail.py > results/dolphins_tail.json 2> results/dolphins_tail.err &
DOL=$!

SWITCH_CORES=22 sh mixing_ladder.sh > results/ladder.log 2>&1
echo LADDER_EXIT=$?

wait $DOL
echo DOLPHINS_EXIT=$?
echo ALL_DONE
