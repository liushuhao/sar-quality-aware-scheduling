#!/usr/bin/env python3
"""P1-1: Random-initialized MOEA-2 control experiment.
Disables hot-start from G-BL, uses random initialization instead.
Runs on one S1 scenario first as a smoke test.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

# Path: archive script at experiments/archive/ → project root is 5 levels up
_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-1_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

def run_one(pkl_path: Path, hotstart: bool = False):
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)

    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)

    # Build hotstart if requested (original behavior)
    hotstart_individual = None
    if hotstart:
        from sar_sim.solver.baselines import baseline_b1
        gbl = baseline_b1(windows, targets)
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
        if seen:
            hotstart_individual = x0

    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=100,
        n_generations=200,
        n_obj=2,
        n_ref_dirs=12,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        hotstart_individual=hotstart_individual,
    )
    rt = time.time() - t0

    meta = result.metadata
    return {
        "seed": seed,
        "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0)),
        "f1_raw": float(meta.get("f1_raw", 0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0)),
        "f3": float(meta.get("f3", 0)),
        "runtime_s": round(rt, 3),
        "hotstart": hotstart,
        "n_frontier": len(meta.get("frontier", [])),
    }

# Smoke test: run one S1 scenario with and without hotstart
pkl = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
print(f"Running: {pkl}")
print("With hotstart (original)...")
r_hot = run_one(pkl, hotstart=True)
print(f"  f1*={r_hot['f1']:.3f}, f2={r_hot['f2']:.4f}, f3={r_hot['f3']:.4f}, n_sel={r_hot['n_selected']}, rt={r_hot['runtime_s']:.0f}s")

print("Without hotstart (random init)...")
r_rand = run_one(pkl, hotstart=False)
print(f"  f1*={r_rand['f1']:.3f}, f2={r_rand['f2']:.4f}, f3={r_rand['f3']:.4f}, n_sel={r_rand['n_selected']}, rt={r_rand['runtime_s']:.0f}s")

print(f"\nDifference: f1* Δ={r_rand['f1']-r_hot['f1']:.3f}, f2 Δ={r_rand['f2']-r_hot['f2']:.4f}")

# Save
with open(RESULTS_DIR / "smoke_test.json", "w") as f:
    json.dump({"hotstart": r_hot, "random_init": r_rand}, f, indent=2)
print(f"Saved to {RESULTS_DIR / 'smoke_test.json'}")
