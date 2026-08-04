#!/usr/bin/env python3
"""Post-MOEA-2 batch launcher: MOEA-3 then the three ablations, each
followed by its hard audit. Designed to be invoked once MOEA-2's rerun
has finished and its audit passed.

Usage: python launch_remaining_reruns.py [--groups S1 S2 S3 S4]
"""
import json, subprocess, sys, time
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
EXPERIMENTS = PAPER / "experiments"
RESULTS = EXPERIMENTS / "results"
PY = sys.executable

GROUPS = ["S1", "S2", "S3", "S4"]


def run(cmd, log):
    print(f"--- {' '.join(cmd)} -> {log.name}", flush=True)
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    print(f"    exit={r.returncode}", flush=True)
    return r.returncode == 0


def audit(progress_path, name):
    snap = RESULTS / f"_snapshot_{name}.json"
    conv_log = EXPERIMENTS / "logs" / f"{name}_snap_conv.log"
    audit_log = EXPERIMENTS / "logs" / f"{name}_audit.log"
    if run([PY, str(EXPERIMENTS / "progress_to_snapshot.py"), str(progress_path), str(snap)], conv_log):
        return run([PY, str(EXPERIMENTS / "_audit_full_hard.py"), "--snapshot", str(snap)], audit_log)
    return False


def main():
    if "--groups" in sys.argv:
        groups = sys.argv[sys.argv.index("--groups") + 1:]
    else:
        groups = GROUPS

    steps = [
        ("run_moea_3obj.py", "moea_3obj", "moea_3obj"),
        ("run_moea_3obj_no_incidence.py", "moea_3obj_no_incidence", "moea_3obj_no_incidence"),
        ("run_moea_3obj_no_physics.py", "moea_3obj_no_physics", "moea_3obj_no_physics"),
        ("run_moea_3obj_no_squint.py", "moea_3obj_no_squint", "moea_3obj_no_squint"),
    ]
    for script, dirname, name in steps:
        prog = RESULTS / dirname / "_progress.json"
        cmd = [PY, str(EXPERIMENTS / script), "--groups"] + groups
        if not run(cmd, EXPERIMENTS / "logs" / f"{dirname}_rerun.log"):
            print(f"!! {script} FAILED — stopping batch", flush=True)
            sys.exit(1)
        print(f"   audit {name}...", flush=True)
        if not audit(prog, name):
            print(f"!! audit {name} FAILED — stopping batch", flush=True)
            sys.exit(1)
        print(f"   {name} OK", flush=True)

    print("ALL REMAINING RERUNS COMPLETE AND AUDITED", flush=True)


if __name__ == "__main__":
    main()
