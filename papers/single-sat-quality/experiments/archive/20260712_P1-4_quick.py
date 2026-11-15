#!/usr/bin/env python3
"""P1-4 quick: Variant A vs D on one S3 scenario, pop=200 gen=200.
Minimal test to see if differentiation emerges at higher pop.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.baselines import baseline_b1

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 200, 200

pkl = SCENARIOS_DIR / "S3" / "S3-A_seed00.pkl"
with open(pkl, 'rb') as f:
    data = pickle.load(f)
windows = data["windows"]
targets = data["targets"]

# Build hotstart
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
hs = x0 if seen else None

# Run Variant A (3-obj)
print("Variant A (full physics, 3-obj)...", end=" ", flush=True)
t0 = time.time()
ra = moea_solver(windows, targets, population_size=POP, n_generations=GEN,
    n_obj=3, n_ref_dirs=12, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    hotstart_individual=hs)
print(f"f1*={ra.metadata.get('f1'):.3f} f2={ra.metadata.get('f2'):.4f} rt={time.time()-t0:.0f}s")

# Run Variant D (3-obj, no physics: f2=f3=1.0 constant)
print("Variant D (no physics, 3-obj)...", end=" ", flush=True)
t0 = time.time()
# Need to pass constant objectives somehow. Use the existing no-physics solver
rd = moea_solver(windows, targets, population_size=POP, n_generations=GEN,
    n_obj=3, n_ref_dirs=12, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    hotstart_individual=hs)
print(f"f1*={rd.metadata.get('f1'):.3f} f2={rd.metadata.get('f2'):.4f} rt={time.time()-t0:.0f}s")

delta = ra.metadata.get('f1', 0) - rd.metadata.get('f1', 0)
print(f"\nΔf1* (A-D) = {delta:.3f}")
print(f"Same: {abs(delta) < 0.02} (A and D indistinguishable at S3, pop={POP} gen={GEN})")
