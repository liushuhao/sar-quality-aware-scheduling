"""Quick debug: which constraint fails?"""
import sys, pickle
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
WORKSPACE = PROJECT.parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "src"))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier
import numpy as np

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

pkl = PROJECT / "scenarios" / "S1" / "S1-A_seed00.pkl"
with open(pkl, "rb") as f:
    data = pickle.load(f)
windows, targets = data["windows"], data["targets"]

gbl = baseline_b1(windows, targets)
instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
precompute_geometry(instance, step_s=10.0)

print(f"instance.phi_min={instance.phi_min:.4f} ({np.degrees(instance.phi_min):.1f}deg)")
print(f"instance.phi_max={instance.phi_max:.4f} ({np.degrees(instance.phi_max):.1f}deg)")
print(f"instance.altitude_m={instance.altitude_m}")

# Hotstart
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

result = moea_solver(
    windows, targets,
    population_size=100, n_generations=200, n_obj=3, n_ref_dirs=12,
    max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
    hotstart_individual=hotstart, instance=instance,
)
meta = result.metadata
frontier = meta.get("frontier", [])

verifier = ConstraintVerifier(instance)
verified = verifier.verify_frontier(frontier)

# Check first 3 solutions
for i, (sol, rpt) in enumerate(verified[:3]):
    print(f"\nSolution {i}: overall_pass={rpt.overall_pass}, n_passed={rpt.n_passed}, n_failed={rpt.n_failed}")
    for cname, cr in rpt.results.items():
        if not cr.passed:
            print(f"  {cname}: FAILED - {cr.total_checks} checks, {len(cr.violations)} violations")
            for v in cr.violations[:2]:
                print(f"    {v.description}")
        else:
            print(f"  {cname}: PASSED")

    # Also print phi values for this solution
    selected = sol["selected"]
    phis = sol["phis"]
    print(f"  selected={selected[:5]}..., phis[:5]={phis[:5] if len(phis)>=5 else phis}")
