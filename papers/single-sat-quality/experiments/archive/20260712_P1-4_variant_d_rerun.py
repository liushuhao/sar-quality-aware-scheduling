#!/usr/bin/env python3
"""P1-4 FIXED 2026-07-20.

FIX 1 (f1 normalization): no_physics solver was returning raw profit (f1_gbl
defaulted to 1.0). Now both solvers receive f1_gbl from the G-BL baseline, so
metadata f1 is normalized (0-1) for both A and D variants.

FIX 2 (incremental save): each scenario dumped to full.json immediately, so
a kill mid-run loses at most one scenario. Resume skips already-done scenarios.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))
sys.path.insert(0, str(_PROJ / "papers" / "single-sat-quality" / "experiments"))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from run_moea_3obj_no_physics import moea_solver_no_physics

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-4_variant_d_rerun"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 200, 400
N_SCENARIOS = 5


def build_hotstart(windows, targets):
    from sar_sim.solver.types import build_agile_instance, precompute_geometry
    gbl = baseline_b1(windows, targets)
    gbl_f1 = max(float(gbl.f1), 1.0)
    instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    x0 = np.zeros(2 * instance.N)
    seen = set()
    for obs in gbl.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx:
            idx = target_to_idx[tid]
            if idx not in seen:
                seen.add(idx)
                x0[idx] = 1.0
                span = instance.tasks[idx].time_span
                tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span if span > 0 else 0.5
                x0[instance.N + idx] = max(0.0, min(1.0, tau))
    return (x0 if seen else None), gbl_f1


def run_variant(pkl_path, variant, n_obj):
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    hs, gbl_f1 = build_hotstart(windows, targets)
    solver = moea_solver if variant == "A_full_physics" else moea_solver_no_physics
    t0 = time.time()
    kw = dict(population_size=POP, n_generations=GEN, n_obj=n_obj, n_ref_dirs=12,
              max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, hotstart_individual=hs)
    if variant != "A_full_physics":
        kw["f1_gbl"] = gbl_f1  # no_physics defaults f1_gbl to 1.0 (raw profit); physics version computes its own G-BL
    result = solver(windows, targets, **kw)
    rt = time.time() - t0
    meta = result.metadata
    return {
        "variant": variant, "n_obj": n_obj,
        "f1": float(meta.get("f1", 0)),
        "f1_raw": float(meta.get("f1_raw", 0)),
        "f1_gbl": float(meta.get("f1_gbl", gbl_f1)),
        "f2": float(meta.get("f2", 0)),
        "f3": float(meta.get("f3", 0)),
        "n_selected": int(meta.get("n_selected", 0)),
        "runtime_s": round(rt, 1),
    }


partial_path = RESULTS_DIR / "full.json"
out = {"params": {"pop": POP, "gen": GEN, "n_scenarios": N_SCENARIOS},
       "results": {}, "summary": {}}
if partial_path.exists():
    try:
        out = json.load(open(partial_path, encoding="utf-8"))
        print(f"Resumed: {sum(len(v) for v in out.get('results',{}).values())} scenarios done")
    except Exception:
        pass
all_results = out.setdefault("results", {})

for group in ["S3", "S4"]:
    d = SCENARIOS_DIR / group
    pkls = sorted(d.glob("*.pkl"))[:N_SCENARIOS]
    if not pkls:
        continue
    runs = all_results.setdefault(group, [])
    done = {r["scenario"] for r in runs}
    print(f"\nGroup {group}: {len(pkls)} scenarios, pop={POP}, gen={GEN}")
    for i, pkl in enumerate(pkls):
        if pkl.name in done:
            print(f"  [{i+1}/{len(pkls)}] {pkl.name} SKIP (done)")
            continue
        print(f"  [{i+1}/{len(pkls)}] {pkl.name}", end=" ", flush=True)
        ra = run_variant(pkl, "A_full_physics", n_obj=3)
        rd = run_variant(pkl, "D_no_physics", n_obj=3)
        delta = ra["f1"] - rd["f1"]
        print(f"A:f1*={ra['f1']:.3f} D:f1*={rd['f1']:.3f} d={delta:.3f}")
        runs.append({"scenario": pkl.name, "A": ra, "D": rd, "delta_f1": delta})
        json.dump(out, open(partial_path, "w"), indent=2)

summary = {}
for group, rs in all_results.items():
    a_f1 = np.array([r["A"]["f1"] for r in rs])
    d_f1 = np.array([r["D"]["f1"] for r in rs])
    summary[group] = {
        "A_f1_mean": float(a_f1.mean()), "A_f1_std": float(a_f1.std()),
        "D_f1_mean": float(d_f1.mean()), "D_f1_std": float(d_f1.std()),
        "delta_mean": float((a_f1 - d_f1).mean()), "n": len(rs),
    }
out["summary"] = summary
json.dump(out, open(partial_path, "w"), indent=2)
print("\n=== SUMMARY ===")
for g, s in summary.items():
    print(f"{g}: A={s['A_f1_mean']:.3f}+/-{s['A_f1_std']:.3f}  D={s['D_f1_mean']:.3f}+/-{s['D_f1_std']:.3f}  d={s['delta_mean']:.3f}")
print(f"\nSaved: {partial_path}")
