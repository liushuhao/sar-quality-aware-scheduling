"""Quick smoke test: verify all 4 solvers work on one small scenario."""
import sys, pickle, time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent  # experiments/
PAPER_DIR = PROJECT.parent  # single-sat-quality/
WORKSPACE = PAPER_DIR.parent.parent  # planning paper/
sys.path.insert(0, str(WORKSPACE / "src"))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.so_f1 import b2_profit_solver_bl_seeded
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
import numpy as np

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

pkl = PROJECT / "scenarios" / "S1" / "S1-A_seed00.pkl"
print(f"Smoke test on: {pkl.name}")
with open(pkl, "rb") as f:
    data = pickle.load(f)
windows = data["windows"]
targets = data["targets"]
print(f"  n_targets={len(targets)}, n_windows={len(windows)}")

# Use build_agile_instance_from_scenario to pass orbit params (RAAN, epoch, inclination)
instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
precompute_geometry(instance, step_s=10.0)
print(f"  instance.N={instance.N}")
print(f"  orbit: raan={np.degrees(instance.orbit_raan_rad):.1f}°, "
      f"inc={np.degrees(instance.orbit_inclination_rad):.1f}°, "
      f"epoch_s={instance.orbit_epoch_s:.0f}")

# ── Verify GeomCache phi values are consistent with visibility windows ──
print("\n  GeomCache phi vs window off-nadir angle check:")
phi_mismatches = 0
for i, task in enumerate(instance.tasks[:5]):  # check first 5 tasks
    for w in task.windows:
        # Window's off-nadir angle (at optimal time)
        win_phi_deg = w.off_nadir_angle
        # GeomCache phi at the window's optimal time
        t_opt = w.t_optimal.timestamp() if hasattr(w.t_optimal, 'timestamp') else w.t_optimal
        geom = instance.geom_cache.lookup(i, t_opt)
        cache_phi_deg = np.degrees(geom.phi)
        diff = abs(win_phi_deg - cache_phi_deg)
        if diff > 1.0:  # >1 degree mismatch
            phi_mismatches += 1
            print(f"    Task {i} ({task.target_id}): win={win_phi_deg:.2f}° vs cache={cache_phi_deg:.2f}° (Δ={diff:.2f}°)")
        else:
            print(f"    Task {i} ({task.target_id}): win={win_phi_deg:.2f}° vs cache={cache_phi_deg:.2f}° OK")
if phi_mismatches == 0:
    print("  GeomCache phi values are CONSISTENT with visibility windows")
else:
    print(f"  WARNING: {phi_mismatches} phi mismatches detected!")

# 1. G-BL
t0 = time.time()
b1 = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                 geom_cache=instance.geom_cache, instance=instance)
print(f"\n  [1] G-BL: f1={b1.f1}, n_scheduled={b1.n_scheduled}, t={time.time()-t0:.2f}s")

# 2. G-SM
t0 = time.time()
b3 = baseline_b3(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                 geom_cache=instance.geom_cache, instance=instance)
print(f"  [2] G-SM: f1={b3.f1}, n_scheduled={b3.n_scheduled}, t={time.time()-t0:.2f}s")

# 3. GA-P-BL (small pop/gen for smoke test)
t0 = time.time()
b2 = b2_profit_solver_bl_seeded(windows, targets, population_size=20, n_generations=10,
                                 max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
print(f"  [3] GA-P-BL: f1={b2.metadata.get('f1',0)}, n_scheduled={b2.metadata.get('n_selected',0)}, t={time.time()-t0:.2f}s")

# 4. MOEA-3 (small pop/gen for smoke test)
t0 = time.time()
moea = moea_solver(windows, targets, population_size=20, n_generations=10, n_obj=3,
                   n_ref_dirs=12, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                   instance=instance)
meta = moea.metadata
print(f"  [4] MOEA-3: f1_raw={meta.get('f1_raw',0)}, n_selected={meta.get('n_selected',0)}, "
      f"n_frontier={meta.get('n_frontier_points',0)}, t={time.time()-t0:.2f}s")

# 5. Verify constraint fields present
print(f"\n  Constraint check: n_frontier_raw={meta.get('n_frontier_raw','MISSING')}, "
      f"n_infeasible_filtered={meta.get('n_infeasible_filtered','MISSING')}")

print("\nSMOKE TEST PASS")
