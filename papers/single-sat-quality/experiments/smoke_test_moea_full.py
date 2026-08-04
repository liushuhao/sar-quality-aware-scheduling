"""Full-param MOEA-3 test on one scenario to verify frontier feasibility."""
import sys, pickle, time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
PAPER_DIR = PROJECT.parent
WORKSPACE = PAPER_DIR.parent.parent
sys.path.insert(0, str(WORKSPACE / "src"))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
import numpy as np

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

pkl = PROJECT / "scenarios" / "S1" / "S1-A_seed00.pkl"
print(f"Full MOEA-3 test on: {pkl.name}")
with open(pkl, "rb") as f:
    data = pickle.load(f)
windows = data["windows"]
targets = data["targets"]
print(f"  n_targets={len(targets)}, n_windows={len(windows)}")

# Build G-BL hotstart (same as run_moea_3obj.py)
gbl = baseline_b1(windows, targets)
instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
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
hotstart = x0 if seen else None
print(f"  G-BL f1={gbl.f1}, hotstart seeded={len(seen)} tasks")

# Full-param MOEA-3
t0 = time.time()
result = moea_solver(
    windows, targets,
    population_size=100, n_generations=200, n_obj=3, n_ref_dirs=12,
    max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    hotstart_individual=hotstart, instance=instance,
)
rt = time.time() - t0
meta = result.metadata
print(f"\nMOEA-3 full-param results (t={rt:.1f}s):")
print(f"  f1_raw={meta.get('f1_raw',0)}, f1_gbl={meta.get('f1_gbl',0)}")
print(f"  f2={meta.get('f2',0)}, f3={meta.get('f3',0)}")
print(f"  n_selected={meta.get('n_selected',0)}")
print(f"  n_frontier_raw={meta.get('n_frontier_raw','MISSING')}")
print(f"  n_frontier_points={meta.get('n_frontier_points',0)} (feasible)")
print(f"  n_infeasible_filtered={meta.get('n_infeasible_filtered',0)}")

# Check frontier details
frontier = meta.get("frontier", [])
print(f"\n  Frontier details ({len(frontier)} points):")
for i, s in enumerate(frontier[:5]):
    print(f"    [{i}] f1={s.get('f1',0):.1f}, f2={s.get('f2',0):.4f}, f3={s.get('f3',0):.4f}, "
          f"n_tasks={s.get('n_tasks',0)}")

if meta.get('n_infeasible_filtered',0) == meta.get('n_frontier_raw',0) and meta.get('n_frontier_raw',0) > 0:
    print("\n  !!! WARNING: ALL frontier points filtered as infeasible !!!")
    print("  This indicates ConstraintVerifier may be too strict or there's a bug.")
elif meta.get('n_frontier_points',0) > 0:
    print(f"\n  OK: {meta.get('n_frontier_points',0)} feasible points in frontier")

print("\nFULL MOEA-3 TEST DONE")
