#!/usr/bin/env python3
"""P1-2: Random-search baseline. Quick test on S1 only.
Samples random τ ∈ [0,1]^N and evaluates f1*, f2, f3.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))

from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.baselines import baseline_b1

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-2_random_search"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
N_SAMPLES = 5000  # Quick test (roadmap says 20K, but we're testing)

def evaluate_schedule(instance, tau):
    """Given tau ∈ [0,1]^N, decode schedule and compute objectives.
    Returns (f1_raw, f1_star, f2, f3, n_selected, feasible).
    """
    N = instance.N
    # Decode: task i is selected if tau[i] > 0.3 (arbitrary threshold to get ~50% selection)
    # Sort selected tasks by tau value (which encodes start time within window)
    selected_idx = np.where(tau[:N] > 0.3)[0]
    if len(selected_idx) == 0:
        return 0, 0, 0, 0, 0, False

    # Sort by tau (observation order)
    order = selected_idx[np.argsort(tau[selected_idx])]

    # Check C3 feasibility (simplified: just check time ordering)
    # Full C3 check would require actual geometry computation
    # For random search, accept if basic ordering works
    feasible = True
    current_time = 0
    n_sel = 0
    for idx in order:
        task = instance.tasks[idx]
        start_time = task.t_earliest + tau[N + idx] * (task.t_latest - task.t_earliest)
        if start_time >= current_time:
            n_sel += 1
            current_time = start_time + task.duration
        else:
            feasible = False
            break

    if not feasible or n_sel == 0:
        return 0, 0, 0, 0, 0, False

    # Compute quality scores from precomputed geometry
    f2_vals, f3_vals = [], []
    for idx in order[:n_sel]:
        task = instance.tasks[idx]
        # Use task's precomputed theta/psi values at the selected time
        # Simplified: use task's geometric properties
        theta = task.incidence_angle if hasattr(task, 'incidence_angle') else 0.5
        psi_sq = task.squint_angle if hasattr(task, 'squint_angle') else 0.1
        f2_vals.append(np.sin(theta) * np.cos(psi_sq))
        f3_vals.append(np.cos(theta)**3 * np.cos(psi_sq)**3)

    f1_raw = n_sel * 5.0  # Simplified: 5 points per task
    f2 = np.mean(f2_vals) if f2_vals else 0
    f3 = np.mean(f3_vals) if f3_vals else 0
    return f1_raw, f1_raw, f2, f3, n_sel, True

# Run on S1 scenarios
pkls = sorted((SCENARIOS_DIR / "S1").glob("*.pkl"))[:10]
results = []

for pkl in pkls:
    print(f"  {pkl.name}...", end=" ", flush=True)
    with open(pkl, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n = data.get("n_targets", len(targets))

    # Get G-BL baseline for f1 normalization
    gbl = baseline_b1(windows, targets)
    f1_gbl = len(gbl.schedule) * 5.0

    instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)

    f1_vals, f2_vals, f3_vals = [], [], []
    feasible_count = 0
    t0 = time.time()
    for _ in range(N_SAMPLES):
        tau = np.random.random(2 * instance.N)
        f1_r, f1_s, f2, f3, nsel, feas = evaluate_schedule(instance, tau)
        if feas:
            feasible_count += 1
            f1_vals.append(f1_s / f1_gbl if f1_gbl > 0 else 0)
            f2_vals.append(f2)
            f3_vals.append(f3)
    rt = time.time() - t0

    entry = {
        "scenario": pkl.name, "n": n, "f1_gbl": f1_gbl,
        "n_samples": N_SAMPLES, "feasible_count": feasible_count,
        "f1_star_best": float(np.max(f1_vals)) if f1_vals else 0,
        "f1_star_mean": float(np.mean(f1_vals)) if f1_vals else 0,
        "f1_star_std": float(np.std(f1_vals)) if f1_vals else 0,
        "f2_best": float(np.max(f2_vals)) if f2_vals else 0,
        "f2_mean": float(np.mean(f2_vals)) if f2_vals else 0,
        "f3_best": float(np.max(f3_vals)) if f3_vals else 0,
        "runtime_s": round(rt, 3),
    }
    results.append(entry)
    print(f"best_f1*={entry['f1_star_best']:.3f} feasible={feasible_count}/{N_SAMPLES}")

# Summary
print(f"\n{'='*60}")
print("Random search on S1:")
if results:
    best_f1s = [r["f1_star_best"] for r in results]
    print(f"  Best f1*: {np.mean(best_f1s):.3f}±{np.std(best_f1s):.3f}")

with open(RESULTS_DIR / "p1-2_s1_quick.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved.")