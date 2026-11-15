#!/usr/bin/env python3
"""P1-2: Random-search baseline — using window-level geometry sampling.
Fixes the evaluator by computing f2/f3 from window geometric data
rather than requiring full C3 constraint checking.
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

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
N_SAMPLES = 5000
N_SCENARIOS = 5

def compute_objectives(windows, targets, selected_indices, instance):
    """Compute f1*, f2, f3 for a set of selected task indices.
    Uses precomputed geometric data from instance.geom_cache.
    """
    if len(selected_indices) == 0:
        return 0, 0, 0

    tasks = instance.tasks
    n_sel = len(selected_indices)
    f1_raw = n_sel * 5.0

    # Extract geometric quantities from the first window of each selected task
    f2_vals, f3_vals = [], []
    for idx in selected_indices:
        task = tasks[idx]
        # Use the optimal off-nadir from window data
        phi = task.phi_min  # best-case off-nadir (from window center)
        theta = np.arcsin(np.sin(phi) * (6371 + instance.altitude_m/1000) / 6371) if phi > 0 else 0.5
        psi_sq = 0.0  # assume zero-squint for random baseline (optimistic)

        f2_vals.append(np.sin(theta) * np.cos(psi_sq))
        f3_vals.append(np.cos(theta)**3 * np.cos(psi_sq)**3)

    f2 = np.mean(f2_vals)
    f3 = np.mean(f3_vals)
    return f1_raw, f2, f3

# Run on S1 scenarios
pkls = sorted((SCENARIOS_DIR / "S1").glob("*.pkl"))[:N_SCENARIOS]
all_results = {}

rng = np.random.default_rng(42)

for pkl in pkls:
    print(f"  {pkl.name}...", end=" ", flush=True)
    with open(pkl, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))

    instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)

    gbl = baseline_b1(windows, targets)
    f1_gbl = len(gbl.schedule) * 5.0

    # Random search: sample N random selection vectors
    t0 = time.time()
    f1_star_vals, f2_vals, f3_vals = [], [], []
    for _ in range(N_SAMPLES):
        # Randomly select 0 to N targets with varying density
        n_select = rng.integers(1, n_targets + 1)
        selected = rng.choice(n_targets, size=n_select, replace=False)
        f1_raw, f2, f3 = compute_objectives(windows, targets, selected, instance)
        f1_star_vals.append(f1_raw / f1_gbl if f1_gbl > 0 else 0)
        f2_vals.append(f2)
        f3_vals.append(f3)

    rt = time.time() - t0

    result = {
        "scenario": pkl.name, "n": n_targets, "f1_gbl": f1_gbl,
        "n_samples": N_SAMPLES, "runtime_s": round(rt, 3),
        "f1_star_best": float(np.max(f1_star_vals)),
        "f1_star_mean": float(np.mean(f1_star_vals)),
        "f1_star_std": float(np.std(f1_star_vals)),
        "f1_star_p90": float(np.percentile(f1_star_vals, 90)),
        "f2_mean": float(np.mean(f2_vals)),
        "f3_mean": float(np.mean(f3_vals)),
    }
    all_results[pkl.name] = result
    print(f"best_f1*={result['f1_star_best']:.3f} p90={result['f1_star_p90']:.3f} mean={result['f1_star_mean']:.3f}")

# Summary
print(f"\nRandom search summary ({N_SCENARIOS} S1 scenarios):")
best = [r["f1_star_best"] for r in all_results.values()]
p90 = [r["f1_star_p90"] for r in all_results.values()]
mean = [r["f1_star_mean"] for r in all_results.values()]
print(f"  Best f1*: {np.mean(best):.3f}±{np.std(best):.3f}")
print(f"  P90 f1*:  {np.mean(p90):.3f}±{np.std(p90):.3f}")
print(f"  Mean f1*: {np.mean(mean):.3f}±{np.std(mean):.3f}")

# Compare with MOEA-2 hotstart results
with open(PROJECT / "experiments" / "results" / "moea_2obj" / "_progress.json") as f:
    moea = json.load(f)
s1_moea_f1 = [e["f1"] for k, e in moea.get("completed", {}).items()
              if k.startswith("S1") and any(k.endswith(pkl.name) for pkl in pkls)]
if s1_moea_f1:
    print(f"  MOEA-2 hotstart f1*: {np.mean(s1_moea_f1):.3f}±{np.std(s1_moea_f1):.3f}")

with open(RESULTS_DIR / "p1-2_s1_random_search.json", "w") as f:
    json.dump(all_results, f, indent=2)
print("Saved.")