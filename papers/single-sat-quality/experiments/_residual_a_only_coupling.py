#!/usr/bin/env python3
"""RES1 (panel 20261031 residual): variant-A-only within-schedule f2-f3 correlation.

Mirrors scripts/compute_schedule_correlation.py exactly (same objective
caliber, same knee-solution source, same pooled + per-schedule statistics),
restricted to variant-A scenarios ("-A_" keys) -- the pure density axis where
the geometry definition is identical across classes. Read-only: prints and
writes nothing except stdout; the verify gate recomputes the same numbers
inline for its assertions.
"""
import pickle, sys, math
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
RESULTS_DIR = PROJECT / "experiments" / "results"
GROUPS = ["S1", "S2", "S3", "S4"]
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0


def f2_new(g):
    import math
    return math.sqrt(max(g.cos_psi ** 2 - math.cos(g.phi) ** 2, 0.0))


def f3_new(g):
    return math.cos(g.phi) ** 3


def pearson(x, y):
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


def main():
    import json
    prog = json.load(open(RESULTS_DIR / "moea_3obj" / "_progress.json"))
    completed = prog.get("completed", {})
    out = {}
    for group in GROUPS:
        F2, F3, sched_rs = [], [], []
        n_sched = 0
        for key, v in sorted(completed.items()):
            if not key.startswith(group + "/") or "-A_" not in key:
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
        entry = {
            "r": pearson(F2, F3), "n_tasks": len(F2), "n_schedules": n_sched,
            "per_schedule_mean": float(np.mean(sched_rs)) if sched_rs else float("nan"),
            "fisher_z_mean": float(np.arctanh(np.asarray(sched_rs)).mean()) if sched_rs else float("nan"),
        }
        print(f"A-only {group}: r={entry['r']:+.4f} n_tasks={entry['n_tasks']} "
              f"n_sched={entry['n_schedules']} per_sched_mean={entry['per_schedule_mean']:+.4f} "
              f"fisher_z={entry['fisher_z_mean']:+.4f}", flush=True)
        out[group] = entry
    dest = RESULTS_DIR / "schedule_correlation_a_only.json"
    json.dump({"source": "moea_3obj/_progress.json variant-A keys only",
               "caliber": "scripts/compute_schedule_correlation.py (pooled per-task + per-schedule)",
               "classes": out}, open(dest, "w", encoding="utf-8"), indent=2)
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
