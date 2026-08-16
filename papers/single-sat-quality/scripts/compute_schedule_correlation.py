#!/usr/bin/env python3
"""§6.4 schedule-level f2-f3 correlation from post-RDR-066 progress files.

Per-task f2/f3 within the knee schedule, pooled Pearson per group, computed
from the completed entries of the current-code progress files (which store
selected/t_actuals), NOT the pre-RDR-066 snapshots.

New-caliber objectives (Option 2, RDR-066):
  f2 = sin(theta_elev)*cos(psi)  = sqrt(cos^2 psi - cos^2 xi)
  f3 = cos^3(xi)                  (xi = full off-nadir; no separate squint factor)

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
    ("A_full_physics", "moea_3obj/_progress.json"),
    ("D_no_physics", "moea_3obj_no_physics/_progress.json"),
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
    for variant, prog_rel in VARIANTS:
        prog_path = RESULTS_DIR / prog_rel
        if not prog_path.exists():
            print(f"WARN missing {prog_path}")
            continue
        prog = json.load(open(prog_path))
        completed = prog.get("completed", {})
        variant_out = {}
        for group in GROUPS:
            F2, F3 = [], []
            sched_rs = []
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
                sf2, sf3 = [], []
                for i, t in zip(sel, t_acts):
                    g = inst.geom_cache.lookup(int(i), float(t))
                    sf2.append(f2_new(g))
                    sf3.append(f3_new(g))
                F2.extend(sf2)
                F3.extend(sf3)
                if len(sf2) >= 3:
                    r = pearson(sf2, sf3)
                    if np.isfinite(r):
                        sched_rs.append(r)
                n_sched += 1
            if not F2:
                print(f"  {variant} {group}: no data")
                continue
            entry = {
                "r": pearson(F2, F3), "n_tasks": len(F2), "n_schedules": n_sched,
                "f2_mean": float(np.mean(F2)), "f3_mean": float(np.mean(F3)),
            }
            if sched_rs:
                rs = np.asarray(sched_rs)
                entry["per_schedule_mean"] = float(rs.mean())
                entry["fisher_z_mean"] = float(np.arctanh(rs).mean())
                entry["per_schedule_min"] = float(rs.min())
                entry["per_schedule_max"] = float(rs.max())
            variant_out[group] = entry
            print(f"{variant} {group}: r={entry['r']:+.4f} n_tasks={len(F2)} "
                  f"n_sched={n_sched} per_sched_mean={entry.get('per_schedule_mean', float('nan')):+.4f}",
                  flush=True)
        out["variants"][variant] = variant_out
    out["sources"] = {v: prog_rel for v, prog_rel in VARIANTS}
    json.dump(out, open(OUT_PATH, "w", encoding="utf-8"), indent=2)
    print(f"\nWrote {OUT_PATH}")


def f2_new(g):
    import math
    # Option 2: f2 = sqrt(cos^2 psi - cos^2 xi); xi = full off-nadir = geom.phi
    return math.sqrt(max(g.cos_psi ** 2 - math.cos(g.phi) ** 2, 0.0))


def f3_new(g):
    import math
    return math.cos(g.phi) ** 3


if __name__ == "__main__":
    main()
