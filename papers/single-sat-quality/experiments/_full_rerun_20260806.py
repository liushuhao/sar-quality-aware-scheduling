#!/usr/bin/env python3
"""Full consistency rerun after window fix c91d398 (2026-08-06).

All solver families run against the regenerated scenario pkls, each
followed by its hard audit (C1-C4 + OOW). Any failed audit stops the
batch so dirty data cannot propagate.

Scope (verified against analysis scripts + old snapshots):
  baselines S1-S4 (200)  + baselines S7/S8 (100)
  GA-P-BL    S1-S6 (300)
  MOEA-2     S1-S4,S7,S8 (300; S5/S6 unused by downstream analyses)
  MOEA-3     S1-S6 (300)
  no_incidence / no_physics / no_squint  S1-S6 (300 each)

Logs: experiments/logs/full_rerun_<family>.log
"""
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parent
RESULTS = EXPERIMENTS / "results"
LOGS = EXPERIMENTS / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
PY = sys.executable
STAMP = "20260806"


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def backup(path: Path):
    """Move stale results aside: the baseline runners have no --no-resume
    and resume purely by key presence (no pkl_sha1 check), so leaving the
    old file in place would silently keep pre-windowfix data."""
    if path.exists():
        bak = path.with_name(path.name + f".bak_pre_windowfix_{STAMP}")
        if not bak.exists():
            shutil.move(str(path), str(bak))
            log(f"moved old -> {bak.name}")
        else:
            path.unlink()
            log(f"removed old {path.name} (backup already exists)")


def run_step(name, cmd, logfile):
    log(f"BEGIN {name}: {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    with open(logfile, "w", encoding="utf-8") as f:
        f.write(f"# {name} started {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.flush()
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if r.returncode != 0:
        log(f"!! {name} FAILED exit={r.returncode} ({dt:.0f}s) — see {logfile.name}")
        sys.exit(1)
    log(f"DONE  {name} in {dt:.0f}s")


def audit_progress(progress_path: Path, snapshot_name: str) -> bool:
    snap = RESULTS / f"_snapshot_{snapshot_name}.json"
    conv_log = LOGS / f"{snapshot_name}_snap_conv.log"
    audit_log = LOGS / f"{snapshot_name}_audit.log"
    run_step(
        f"snapshot {snapshot_name}",
        [PY, str(EXPERIMENTS / "progress_to_snapshot.py"), str(progress_path), str(snap)],
        conv_log,
    )
    with open(audit_log, "w", encoding="utf-8") as f:
        f.write(f"# audit {snapshot_name} started {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.flush()
        r = subprocess.run(
            [PY, str(EXPERIMENTS / "_audit_full_hard.py"),
             "--snapshot", str(snap), "--jobs", "6"],
            stdout=f, stderr=subprocess.STDOUT,
        )
    tail = ""
    try:
        tail = "\n".join(open(audit_log, encoding="utf-8").read().splitlines()[-12:])
    except Exception:
        pass
    log(f"audit {snapshot_name} exit={r.returncode}\n{tail}")
    if r.returncode != 0 or "scenarios with any issue: 0" not in tail:
        log(f"!! AUDIT {snapshot_name} FAILED — stopping")
        return False
    return True


def audit_baselines(classes: str, name: str) -> bool:
    logfile = LOGS / f"{name}_audit.log"
    with open(logfile, "w", encoding="utf-8") as f:
        f.write(f"# baseline audit {name} started {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.flush()
        r = subprocess.run(
            [PY, str(EXPERIMENTS / "_audit_baseline_quality.py"), classes],
            stdout=f, stderr=subprocess.STDOUT,
        )
    tail = "\n".join(open(logfile, encoding="utf-8").read().splitlines()[-6:])
    log(f"audit {name} exit={r.returncode}\n{tail}")
    if r.returncode != 0:
        return False
    ok = ("C2fail=0" in tail and "C1fail=0" in tail
          and "OOWscen=0" in tail and "C3fail=0" in tail and "C4fail=0" in tail)
    if not ok:
        log(f"!! BASELINE AUDIT {name} FAILED — stopping")
    return ok


def main():
    log(f"python: {PY}")
    log("=== FULL CONSISTENCY RERUN (window fix) ===")

    # ---- backups (never delete old data) ----
    for p in [
        RESULTS / "baselines_200.json",
        RESULTS / "baselines_S7S8.json",
        RESULTS / "b2_profit_bl" / "_progress.json",
        RESULTS / "moea_2obj" / "_progress.json",
        RESULTS / "moea_3obj" / "_progress.json",
        RESULTS / "moea_3obj_no_incidence" / "_progress.json",
        RESULTS / "moea_3obj_no_physics" / "_progress.json",
        RESULTS / "moea_3obj_no_squint" / "_progress.json",
    ]:
        backup(p)

    # ---- 1. G-BL + G-SM, S1-S4 (200) ----
    run_step("baselines S1-S4",
             [PY, str(EXPERIMENTS / "run_baselines_v4.py")],
             LOGS / "full_rerun_baselines.log")
    if not audit_baselines("S1,S2,S3,S4", "baselines_S1S4"):
        sys.exit(1)

    # ---- 2. G-BL + G-SM, S7/S8 (100) ----
    run_step("baselines S7/S8",
             [PY, str(EXPERIMENTS / "run_baselines_S7S8.py")],
             LOGS / "full_rerun_baselines_S7S8.log")
    if not audit_baselines("S7,S8", "baselines_S7S8"):
        sys.exit(1)

    # ---- 3. GA-P-BL S1-S6 (300) ----
    run_step("GA-P-BL S1-S6",
             [PY, str(EXPERIMENTS / "run_so_f1_bl.py"),
              "--no-resume", "--groups", "S1", "S2", "S3", "S4", "S5", "S6"],
             LOGS / "full_rerun_ga_p_bl.log")
    if not audit_progress(RESULTS / "b2_profit_bl" / "_progress.json", "ga_p_bl"):
        sys.exit(1)

    # ---- 4. MOEA-2 S1-S4,S7,S8 (300) ----
    run_step("MOEA-2",
             [PY, str(EXPERIMENTS / "run_moea_2obj.py"),
              "--no-resume", "--groups", "S1", "S2", "S3", "S4", "S7", "S8"],
             LOGS / "full_rerun_moea_2obj.log")
    if not audit_progress(RESULTS / "moea_2obj" / "_progress.json", "moea_2obj"):
        sys.exit(1)

    # ---- 5. MOEA-3 S1-S6 (300) ----
    run_step("MOEA-3",
             [PY, str(EXPERIMENTS / "run_moea_3obj.py"),
              "--no-resume", "--groups", "S1", "S2", "S3", "S4", "S5", "S6"],
             LOGS / "full_rerun_moea_3obj.log")
    if not audit_progress(RESULTS / "moea_3obj" / "_progress.json", "moea_3obj"):
        sys.exit(1)

    # ---- 6-8. ablations S1-S6 (300 each) ----
    for script, dirname, snap in [
        ("run_moea_3obj_no_incidence.py", "moea_3obj_no_incidence", "no_incidence"),
        ("run_moea_3obj_no_physics.py", "moea_3obj_no_physics", "no_physics"),
        ("run_moea_3obj_no_squint.py", "moea_3obj_no_squint", "no_squint"),
    ]:
        run_step(snap,
                 [PY, str(EXPERIMENTS / script),
                  "--no-resume", "--groups", "S1", "S2", "S3", "S4", "S5", "S6"],
                 LOGS / f"full_rerun_{snap}.log")
        if not audit_progress(RESULTS / dirname / "_progress.json", snap):
            sys.exit(1)

    log("=== ALL FULL RERUNS COMPLETE AND AUDITED CLEAN ===")


if __name__ == "__main__":
    main()
