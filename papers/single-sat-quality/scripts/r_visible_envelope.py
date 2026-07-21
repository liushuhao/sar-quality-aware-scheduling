#!/usr/bin/env python3
"""r_visible: corr(f2, f3) over visible geometry envelope, with C7 filter.

FIX (DA CRITICAL 2): original r_visible included |psi|>45deg points (not
C7-schedule-feasible). Now reports r_visible_all (all points) AND
r_visible_c7 (|psi_sq|<=45deg only, C7-feasible). If r_visible_c7 ~= r_solver
(0.93-0.98), the active-selection claim collapses to constraint-imposed.
"""
import pickle, sys, json
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJ.parent.parent / "src"))
sys.path.insert(0, str(_PROJ.parent.parent))

from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.metrics.nesz import off_nadir_to_incidence

PROJECT = _PROJ
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
OUT = PROJECT / "experiments" / "results" / "r_visible_envelope.json"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
STEP_S = 10.0
DEG = np.pi / 180.0
C7_LIM = 45.0 * DEG
GROUPS = ["S1", "S2", "S3", "S4"]
N_PER_GROUP = 5


def scenario_r_visible(pkl_path):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=STEP_S)
    f2_all, f3_all, f2_c7, f3_c7 = [], [], [], []
    psi_abs, theta_list = [], []
    for i, task in enumerate(instance.tasks):
        t = task.t_earliest
        while t <= task.t_latest:
            try:
                geom = instance.geom_cache.lookup(i, t)
                phi = abs(geom.phi)
                psi = geom.psi_sq
                theta = off_nadir_to_incidence(phi)
                s_th = np.sin(theta)
                c_psi = np.cos(psi)
                f2v = s_th * c_psi
                f3v = np.cos(theta) ** 3 * c_psi ** 3
                f2_all.append(f2v)
                f3_all.append(f3v)
                psi_abs.append(abs(psi))
                theta_list.append(np.degrees(theta))
                if abs(psi) <= C7_LIM:
                    f2_c7.append(f2v)
                    f3_c7.append(f3v)
            except Exception:
                pass
            t = t + STEP_S
    f2a, f3a = np.array(f2_all), np.array(f3_all)
    f2c, f3c = np.array(f2_c7), np.array(f3_c7)
    psi_abs = np.array(psi_abs)
    theta_deg = np.array(theta_list)
    if len(f2_all) < 5:
        return None
    r_all = float(np.corrcoef(f2a, f3a)[0, 1])
    r_c7 = float(np.corrcoef(f2c, f3c)[0, 1]) if len(f2c) >= 5 else None
    return {
        "n_points_all": int(len(f2_all)),
        "n_points_c7": int(len(f2c)),
        "r_visible_all": r_all,
        "r_visible_c7": r_c7,
        "psi_abs_deg_p95_all": float(np.degrees(np.percentile(psi_abs, 95))),
        "psi_abs_deg_p95_c7": float(np.degrees(np.percentile(psi_abs[psi_abs <= C7_LIM], 95))) if (psi_abs <= C7_LIM).sum() > 0 else None,
        "theta_deg_mean": float(theta_deg.mean()),
    }


results = {}
for group in GROUPS:
    d = SCENARIOS_DIR / group
    pkls = sorted(d.glob("*.pkl"))[:N_PER_GROUP]
    if not pkls:
        continue
    print(f"\n=== {group}: {len(pkls)} scenarios ===")
    rs = []
    for pkl in pkls:
        r = scenario_r_visible(pkl)
        if r is None:
            print(f"  {pkl.name}: SKIP")
            continue
        r_c7_str = f"{r['r_visible_c7']:+.4f}" if r['r_visible_c7'] is not None else "N/A"
        print(f"  {pkl.name}: r_all={r['r_visible_all']:+.4f} r_c7={r_c7_str}  n_c7={r['n_points_c7']}/{r['n_points_all']}")
        rs.append(r)
    if rs:
        results[group] = {
            "r_visible_all_mean": float(np.mean([r["r_visible_all"] for r in rs])),
            "r_visible_c7_mean": float(np.mean([r["r_visible_c7"] for r in rs if r["r_visible_c7"] is not None])),
            "n_scenarios": len(rs),
            "per_scenario": rs,
        }
        print(f"  -> {group} mean r_all={results[group]['r_visible_all_mean']:+.4f} r_c7={results[group]['r_visible_c7_mean']:+.4f}")

summary = {g: {k: v for k, v in s.items() if k != "per_scenario"} for g, s in results.items()}
out = {"r_null": -0.51, "r_solver_empirical": [0.93, 0.98],
       "results": results, "summary": summary,
       "note": "r_visible_c7 = |psi|<=45deg (C7-feasible). r_visible_c7 ~= r_solver (0.93) -> constraint-imposed (Q3 i). r_visible_c7 ~= r_null (-0.51) -> active selection (solver converges low-squint from wide C7-feasible envelope)."}
json.dump(out, open(OUT, "w"), indent=2)
print(f"\n=== SUMMARY ===")
print(f"r_null=-0.51, r_solver=0.93-0.98")
for g, s in summary.items():
    print(f"  {g}: r_all={s['r_visible_all_mean']:+.4f}  r_c7={s['r_visible_c7_mean']:+.4f}")
print(f"\nSaved: {OUT}")
