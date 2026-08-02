import pickle, sys
from pathlib import Path
import numpy as np
from datetime import timedelta
ROOT = Path(r"D:/hermes/my-workspace/projects/planning paper")
sys.path.insert(0, str(ROOT / "src"))
from sar_sim.solver.baselines import baseline_b1, _c2_transition_los
from sar_sim.solver.types import build_agile_instance, compute_full_attitude, precompute_geometry, compute_los_separation
from sar_sim.verification.constraints import ConstraintVerifier

SLEW = 0.0524
SETTLE = 5.0
pkl = ROOT / "papers/single-sat-quality/experiments/scenarios/S3/S3-A_seed00.pkl"
data = pickle.load(open(pkl, "rb"))
alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000
inst = build_agile_instance(data["windows"], data["targets"],
                            max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
precompute_geometry(inst, step_s=10.0)
r = baseline_b1(data["windows"], data["targets"], instance=inst)

# Reconstruct: verify each consecutive pair and compare tau at assigned vs delayed
t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
sched = sorted(r.schedule, key=lambda o: o.t_actual_start)
print(f"G-BL schedule size: {len(sched)}")
print(f"{'pair':40s} {'gap':>8s} {'tau@verif':>10s} {'tau@build':>10s} {'mag':>7s} delayed?")
for k in range(len(sched) - 1):
    pa = sched[k]; pb = sched[k+1]
    ta = pa.t_actual_start.timestamp(); tb = pb.t_actual_start.timestamp()
    ga = (tb - (ta + inst.tasks[t2i[pa.window.target_id]].duration))
    ia = t2i[pa.window.target_id]; ib = t2i[pb.window.target_id]
    tau_v = compute_los_separation(inst.tasks[ia], ta, inst.tasks[ib], tb, inst)/SLEW + SETTLE
    # tau build would have used candidate w.t_start for b
    t_b_cand = pb.window.t_start.timestamp()
    tau_b = _c2_transition_los(pa.window.target_id, ta, pb.window.target_id, t_b_cand, inst, SLEW, SETTLE)
    delayed = abs(tb - t_b_cand) > 1e-6
    mag = max(0.0, tau_v - ga)
    flag = "  <-- VIOL" if mag > 1e-6 else ""
    if mag > 1e-6 or delayed:
        print(f"{pa.window.target_id[:18]}->{pb.window.target_id[:18]:18s} {ga:8.2f} {tau_v:10.3f} {tau_b:10.3f} {mag:7.3f} {delayed}{flag}")

# Full verify
phi = np.zeros(inst.N); ta_arr = np.zeros(inst.N); sel = []
for obs in sched:
    i = t2i[obs.window.target_id]; t = obs.t_actual_start.timestamp()
    roll,_,_ = compute_full_attitude(inst.tasks[i], t, 1.0, inst)
    sel.append(i); phi[i] = roll; ta_arr[i] = t
rep = ConstraintVerifier(inst).verify_solution(sel, phi, ta_arr)
c2 = rep.results["C2"]
print(f"\nC2 passed={c2.passed} checks={c2.total_checks} violations={len(c2.violations)}")
for v in c2.violations[:10]:
    print(f"  {inst.tasks[v.task_ids[0]].target_id} -> {inst.tasks[v.task_ids[1]].target_id}  mag={v.magnitude:.6f}s")
print("MAGS:", sorted(round(v.magnitude,4) for v in c2.violations))
