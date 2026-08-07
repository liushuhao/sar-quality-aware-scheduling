#!/usr/bin/env bash
# Launch the core-3 family rerun (batch 1) in background, each family to its
# own log. Per the plan: GA-P-BL S1-S4 (200), MOEA-2 S1-S4/S7/S8 (300),
# MOEA-3 S1-S4 (200). Single-process each; 3 procs on 8 cores.
#
# Audit + downstream regen handled separately after all three finish.
set -u
cd "D:/hermes/my-workspace/projects/planning-paper/papers/single-sat-quality/experiments"
PY="D:/Program Files/Python/python.exe"
LOGS=logs

echo "[$(date '+%F %T')] launching core-3 rerun (batch 1)"

"$PY" run_so_f1_bl.py --no-resume --groups S1 S2 S3 S4 \
  > "$LOGS/batch1_gapbl.log" 2>&1 &
GAPID=$!
echo "  GA-P-BL pid=$GAPID -> $LOGS/batch1_gapbl.log"

"$PY" run_moea_2obj.py --no-resume --groups S1 S2 S3 S4 S7 S8 \
  > "$LOGS/batch1_moea2.log" 2>&1 &
M2PID=$!
echo "  MOEA-2    pid=$M2PID -> $LOGS/batch1_moea2.log"

"$PY" run_moea_3obj.py --no-resume --groups S1 S2 S3 S4 \
  > "$LOGS/batch1_moea3.log" 2>&1 &
M3PID=$!
echo "  MOEA-3    pid=$M3PID -> $LOGS/batch1_moea3.log"

echo "$GAPID $M2PID $M3PID" > "$LOGS/batch1_pids.txt"
echo "[$(date '+%F %T')] all 3 launched. pids: $GAPID $M2PID $M3PID"
echo "  monitor: tail -f $LOGS/batch1_*.log"
wait
echo "[$(date '+%F %T')] all 3 finished."
