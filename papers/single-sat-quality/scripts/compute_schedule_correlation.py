#!/usr/bin/env python3
"""§6.4 schedule-level f2-f3 correlation from FINAL corrected snapshots.

Reproduces scripts/reproduce_A_r.py + reproduce_variant_d_r.py methodology
(per-task f2/f3 within the knee schedule, pooled Pearson per group) WITHOUT
re-running the solver: reads the final audited snapshots
(_snapshot_final_moea_3obj.json for variant A, _snapshot_final_moea_3obj_no_physics
for variant D), which store the knee solution's selected/t_actuals, and
recomputes per-task f2/f3 via geom_cache.

f2 = sin(theta)*cos(psi), f3 = cos(theta)^3 * cos(psi)^3 — same caliber as the
original scripts.

Output:
  experiments/results/schedule_correlation.json
"""
import pickle, json, sys, time, subprocess
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ / "papers" / "single-sat-quality" / "experiments"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "schedule_correlation.json"

GROUPS = ["S1", "S2", "S3", "S4"]
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0

VARIANTS = [
    ("A_full_physics", "_snapshot_final_moea_3obj.json"),
    ("D_no_physics", "_snapshot_final_moea_3obj_no_physics.json"),
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except Exception:
        return "unknown"


def pearson(x, y):
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


def main():
    out = {"git_commit": _git_commit(), "variants": {}}
    for variant, snap_name in VARIANTS:
        snap_path = RESULTS_DIR / snap_name
        if not snap_path.exists():
            print(f"WARN missing {snap_path}")
            continue
        snap = json.load(open(snap_path))
        completed = snap.get("completed", {})
        variant_out = {}
        for group in GROUPS:
            F2, F3 = [], []
            n_sched = 0
            for key, v in sorted(completed.items()):
                if not key.startswith(group + "/"):
                    continue
                pkl_name = key.split("/")[1]
                pkl = PROJECT / "experiments" / "scenarios" / group / pkl_name
                if not pkl.exists():
                    print(f"  WARN missing scenario {pkl}")
                    continue
                with open(pkl, "rb") as f:
                    data = pickle.load(f)
                inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
                precompute_geometry(inst, step_s=10.0)
                sel, t_acts = v.get("selected", []), v.get("t_actuals", [])
                if not sel or len(sel) != len(t_acts):
                    continue
                for i, t in zip(sel, t_acts):
                    g = inst.geom_cache.lookup(int(i), float(t))
                    F2.append(math_sin_theta_cospsi(g))
                    F3.append(math_cos3_cospsi3(g))
                n_sched += 1
            if not F2:
                print(f"  {variant} {group}: no data")
                continue
            variant_out[group] = {
                "r": pearson(F2, F3), "n_tasks": len(F2), "n_schedules": n_sched,
                "f2_mean": float(np.mean(F2)), "f3_mean": float(np.mean(F3)),
            }
            print(f"{variant} {group}: r={variant_out[group]['r']:+.4f} n_tasks={len(F2)} n_sched={n_sched}", flush=True)
        out["variants"][variant] = variant_out
    out["sources"] = {v: snap_name for v, snap_name in VARIANTS}
    json.dump(out, open(OUT_PATH, "w", encoding="utf-8"), indent=2)
    print(f"\nWrote {OUT_PATH}")


def math_sin_theta_cospsi(g):
    import math
    return math.sin(g.theta) * g.cos_psi


def math_cos3_cospsi3(g):
    import math
    return (math.cos(g.theta) ** 3) * (g.cos_psi ** 3)


if __name__ == "__main__":
    main()
