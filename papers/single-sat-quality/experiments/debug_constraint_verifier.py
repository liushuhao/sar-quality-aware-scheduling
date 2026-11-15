"""Debug ConstraintVerifier: which constraint fails on MOEA frontier?"""
import sys, pickle, time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
PAPER_DIR = PROJECT.parent
WORKSPACE = PAPER_DIR.parent.parent
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
windows = data["windows"]
targets = data["targets"]

gbl = baseline_b1(windows, targets)
instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
precompute_geometry(instance, step_s=10.0)

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
print(f"Frontier size: {len(frontier)}")

# Verify with ConstraintVerifier
verifier = ConstraintVerifier(instance)
verified = verifier.verify_frontier(frontier)

# Count failures per constraint
from collections import Counter
fail_counts = Counter()
fail_details = []
for i, (sol, rpt) in enumerate(verified):
    if not rpt.overall_pass:
        for cname, passed in rpt.checks.items() if hasattr(rpt, 'checks') else []:
            if not passed:
                fail_counts[cname] += 1
        fail_details.append((i, rpt))

print(f"\nFeasible: {sum(1 for _, r in verified if r.overall_pass)}/{len(verified)}")
print(f"Infeasible: {sum(1 for _, r in verified if not r.overall_pass)}/{len(verified)}")

# Print report structure
if verified:
    _, sample_rpt = verified[0]
    print(f"\nReport attributes: {dir(sample_rpt)}")
    print(f"\nSample report (solution 0):")
    print(f"  overall_pass: {sample_rpt.overall_pass}")
    if hasattr(sample_rpt, 'checks'):
        print(f"  checks: {sample_rpt.checks}")
    if hasattr(sample_rpt, 'violations'):
        print(f"  violations: {sample_rpt.violations}")
    if hasattr(sample_rpt, 'details'):
        print(f"  details: {sample_rpt.details}")
    # Print all non-private attrs
    for attr in vars(sample_rpt):
        if not attr.startswith('_'):
            val = getattr(sample_rpt, attr)
            if not callable(val):
                print(f"  {attr}: {val}")

# Show first few failures in detail
print(f"\n--- First 3 infeasible solutions (detailed) ---")
for i, (sol, rpt) in enumerate(verified):
    if not rpt.overall_pass:
        print(f"\n  Solution {i}: f1={sol.get('f1',0):.2f}, n_tasks={sol.get('n_tasks',0)}")
        for attr in vars(rpt):
            if not attr.startswith('_'):
                val = getattr(rpt, attr)
                if not callable(val):
                    print(f"    {attr}: {val}")
        if i >= 2:
            break

# Also verify G-BL solution for comparison
print("\n--- G-BL solution verification ---")
gbl_frontier = [{
    "f1": gbl.f1, "f2": 0, "f3": 0,
    "n_tasks": gbl.n_scheduled,
    "selected": [target_to_idx[obs.window.target_id] for obs in gbl.schedule
                 if obs.window.target_id in target_to_idx],
    "phis": [],
}]
gbl_verified = verifier.verify_frontier(gbl_frontier)
for i, (sol, rpt) in enumerate(gbl_verified):
    print(f"  G-BL: overall_pass={rpt.overall_pass}")
    for attr in vars(rpt):
        if not attr.startswith('_'):
            val = getattr(rpt, attr)
            if not callable(val):
                print(f"    {attr}: {val}")
