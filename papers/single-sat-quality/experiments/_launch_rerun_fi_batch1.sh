#!/usr/bin/env bash
# Batch 1 of the full-interval rerun (after P1 fix f1e55e5).
# Core 3 families, single-process each, backgrounded. Baselines need no rerun.
# Each family audited after completion; batch 2 (ablations) follows.
set -u
cd "D:/hermes/my-workspace/projects/planning-paper/papers/single-sat-quality/experiments"
PY="D:/Program Files/Python/python.exe"
LOGS=logs
STAMP=$(date +%Y%m%d_%H%M%S)

echo "[$(date '+%F %T')] launching core-3 full-interval rerun (code f1e55e5)"

"$PY" run_so_f1_bl.py --no-resume --groups S1 S2 S3 S4 \
  > "$LOGS/rerun_fi_gapbl.log" 2>&1 &
GAPID=$!
echo "  GA-P-BL pid=$GAPID"

"$PY" run_moea_2obj.py --no-resume --groups S1 S2 S3 S4 S7 S8 \
  > "$LOGS/rerun_fi_moea2.log" 2>&1 &
M2PID=$!
echo "  MOEA-2    pid=$M2PID"

"$PY" run_moea_3obj.py --no-resume --groups S1 S2 S3 S4 \
  > "$LOGS/rerun_fi_moea3.log" 2>&1 &
M3PID=$!
echo "  MOEA-3    pid=$M3PID"

echo "$GAPID $M2PID $M3PID" > "$LOGS/rerun_fi_pids.txt"
echo "[$(date '+%F %T')] all 3 launched. monitor: tail -f $LOGS/rerun_fi_*.log"
wait
echo "[$(date '+%F %T')] all 3 finished."
