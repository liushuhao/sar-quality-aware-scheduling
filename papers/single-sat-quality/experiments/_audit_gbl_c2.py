import pickle, sys
from pathlib import Path
import numpy as np
ROOT = Path(r"D:/hermes/my-workspace/projects/planning paper")
sys.path.insert(0, str(ROOT / "src"))
from sar_sim.solver.baselines import baseline_b1, _c2_transition_los
from sar_sim.solver.types import build_agile_instance, compute_full_attitude, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

SLEW = 0.0524
SETTLE = 5.0
scen_dir = ROOT / "papers/single-sat-quality/experiments/scenarios"
tot = 0
viol_scen = 0
allv = []
for cls in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
    d = scen_dir / cls
    if not d.exists():
        continue
    for pkl in sorted(d.glob("*.pkl")):
        data = pickle.load(open(pkl, "rb"))
        alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000
        inst = build_agile_instance(data["windows"], data["targets"],
                                    max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
        precompute_geometry(inst, step_s=10.0)
        r = baseline_b1(data["windows"], data["targets"], instance=inst)
        t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
        N = inst.N
        phi = np.zeros(N)
        ta = np.zeros(N)
        sel = []
        for obs in r.schedule:
            i = t2i.get(obs.window.target_id)
            if i is None:
                continue
            t = obs.t_actual_start.timestamp()
            roll, _, _ = compute_full_attitude(inst.tasks[i], t, 1.0, inst)
            sel.append(i)
            phi[i] = roll
            ta[i] = t
        rep = ConstraintVerifier(inst).verify_solution(sel, phi, ta)
        c2 = rep.results["C2"]
        tot += 1
        if not c2.passed:
            viol_scen += 1
            for v in c2.violations:
                allv.append((cls, pkl.name, v.magnitude,
                             inst.tasks[v.task_ids[0]].target_id,
                             inst.tasks[v.task_ids[1]].target_id,
                             float(ta[v.task_ids[0]]), float(ta[v.task_ids[1]]),
                             inst.tasks[v.task_ids[0]].duration))
print(f"scenarios={tot} c2_violating={viol_scen}")
allv.sort(key=lambda x: -x[2])
import collections
by_cls = collections.Counter(v[0] for v in allv)
print("violations by class:", dict(by_cls))
print("worst 20:")
for v in allv[:20]:
    print(f"  {v[0]} {v[1]} mag={v[2]:.4f}s {v[3]}->{v[4]} ta={v[5]:.2f}/{v[6]:.2f} dur={v[7]}")
