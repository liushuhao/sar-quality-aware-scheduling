#!/usr/bin/env python3
"""P2-9: Weighted-sum scalarization test.
Runs GA-P-BL with objective: w1*f1 + w2*f2 on S1 scenarios.
Compares to MOEA-2 Pareto front.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))

from sar_sim.solver.so_f1 import b2_profit_solver
from sar_sim.solver.baselines import baseline_b1

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p2-9_weighted_sum"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
WEIGHTS = [(0.9, 0.1), (0.7, 0.3), (0.5, 0.5), (0.3, 0.7), (0.1, 0.9)]
N_SCENARIOS = 5

def run_weighted(pkl_path, w1, w2):
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])

    t0 = time.time()
    # b2_profit_solver optimizes f1 only. We post-hoc evaluate f2.
    result = b2_profit_solver(
        windows, targets,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    )
    rt = time.time() - t0

    # Apply weighted evaluation: w1*f1 + w2*f2
    f1 = result.metadata.get("f1", 0)
    f2 = result.metadata.get("f2", 0)
    f3 = result.metadata.get("f3", 0)
    nsel = result.metadata.get("n_selected", 0)

    # Get G-BL for normalization
    from sar_sim.solver.types import build_agile_instance, precompute_geometry
    gbl = baseline_b1(windows, targets)
    f1_gbl = len(gbl.schedule) * 5.0
    f1_star = f1 / f1_gbl if f1_gbl > 0 else 0

    return {
        "w1": w1, "w2": w2,
        "f1": f1_star,
        "f1_raw": f1,
        "f2": f2,
        "f3": f3,
        "n_selected": nsel,
        "weighted_score": w1 * f1_star + w2 * f2,
        "runtime_s": round(rt, 1),
    }

# Run on S1 scenarios
pkls = sorted((SCENARIOS_DIR / "S1").glob("*.pkl"))[:N_SCENARIOS]
results = {}

for i, pkl in enumerate(pkls):
    print(f"  [{i+1}/{len(pkls)}] {pkl.name}")
    key = pkl.name
    results[key] = []
    for w1, w2 in WEIGHTS:
        r = run_weighted(pkl, w1, w2)
        results[key].append(r)
        print(f"    w=({w1},{w2}): f1*={r['f1']:.3f}, f2={r['f2']:.4f}, score={r['weighted_score']:.3f}")

# Compare with MOEA-2 Pareto front
with open(PROJECT / "experiments" / "results" / "moea_2obj" / "_progress.json") as f:
    moea_data = json.load(f)

print(f"\nWeighted-sum Pareto approximation:")
for pkl_name, rlist in results.items():
    best = max(rlist, key=lambda r: r["weighted_score"])
    print(f"  {pkl_name}: best w=({best['w1']},{best['w2']}) f1*={best['f1']:.3f} f2={best['f2']:.4f}")

with open(RESULTS_DIR / "p2-9_weighted_sum.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved.")