#!/usr/bin/env python3
"""C3 probe: recompute f3 with the corrected formula (drop spurious cos^3 psi)
on saved solutions + re-run greedy baselines. Compare headline metrics."""
import json, pickle, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry, compute_full_attitude
from sar_sim.metrics.nesz import off_nadir_to_incidence
from sar_sim.solver.baselines import baseline_b1, baseline_b3

RES = Path(__file__).resolve().parent / "results"
SCEN = RES.parent / "scenarios"
SLEW, SETTLE = 0.0524, 5.0


def load_sol(path):
    d = json.load(open(path))
    return d["completed"] if set(d) == {"completed"} else d


def f3_of_obs(instance, task, obs_time, phi, mode):
    roll, _, psi = compute_full_attitude(task, float(obs_time), 1.0, instance)
    theta = off_nadir_to_incidence(abs(roll), instance.altitude_m)
    c = math.cos(theta) ** 3
    cp = math.cos(psi) ** 3
    if mode == "code":
        return c * cp
    return c  # correct: drop the spurious cos^3 psi


def solver_f3(instance, task_indices, times, phis, mode):
    vals = [f3_of_obs(instance, instance.tasks[i], t, p, mode)
            for i, t, p in zip(task_indices, times, phis)]
    return float(np.mean(vals)) if vals else 0.0


def gbl_schedule(inst, windows, targets):
    res = baseline_b1(windows, targets, instance=inst)
    out = []
    for obs in res.schedule:
        t = obs.t_actual_start
        ts = t.timestamp() if hasattr(t, "timestamp") else t
        out.append((obs.window.target_id, ts))
    return out


def gsm_schedule(inst, windows, targets):
    res = baseline_b3(windows, targets, instance=inst)
    out = []
    for obs in res.schedule:
        t = obs.t_actual_start
        ts = t.timestamp() if hasattr(t, "timestamp") else t
        out.append((obs.window.target_id, ts))
    return out


def build(scen_pkl):
    data = pickle.load(open(scen_pkl, "rb"))
    inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE)
    precompute_geometry(inst, step_s=10.0)
    tid2idx = {t.target_id: i for i, t in enumerate(inst.tasks)}
    return inst, tid2idx, data


def main():
    m3 = load_sol(RES / "_snapshot_final_moea_3obj.json")
    m2 = load_sol(RES / "_snapshot_final_moea_2obj.json")
    classes = ["S1", "S4"]
    sample = {"S1": ["S1-A_seed00", "S1-A_seed01", "S1-A_seed02"],
              "S4": ["S4-A_seed00", "S4-A_seed01", "S4-A_seed02"]}
    for cls in classes:
        rows = {"MOEA3_code": [], "MOEA3_corr": [], "MOEA2_code": [], "MOEA2_corr": [],
                "GBL_code": [], "GBL_corr": [], "GSM_code": [], "GSM_corr": []}
        for scen in sample[cls]:
            pkl = SCEN / cls / f"{scen}.pkl"
            if not pkl.exists():
                print(f"skip {pkl}"); continue
            inst, tid2idx, data = build(pkl)
            for name, snap in (("MOEA3", m3), ("MOEA2", m2)):
                rec = snap.get(f"{cls}/{scen}.pkl")
                if not rec:
                    continue
                rows[f"{name}_code"].append(solver_f3(inst, rec["selected"], rec["t_actuals"], rec["phis_off_nadir"], "code"))
                rows[f"{name}_corr"].append(solver_f3(inst, rec["selected"], rec["t_actuals"], rec["phis_off_nadir"], "correct"))
            # greedy baselines: rerun schedules, then recompute f3 both ways
            windows = data.get("windows", []); targets = data.get("targets", [])
            for bname, fn in (("GBL", gbl_schedule), ("GSM", gsm_schedule)):
                sched = fn(inst, windows, targets)
                tid2idx_local = tid2idx
                times = [t for _, t in sched]
                idxs = [tid2idx_local[tid] for (tid, _) in sched]
                geom_phis = []
                for (tid, tt) in sched:
                    task = inst.tasks[tid2idx_local[tid]]
                    roll, _, _ = compute_full_attitude(task, tt, 1.0, inst)
                    geom_phis.append(roll)
                rows[f"{bname}_code"].append(solver_f3(inst, idxs, times, geom_phis, "code"))
                rows[f"{bname}_corr"].append(solver_f3(inst, idxs, times, geom_phis, "correct"))
        # aggregate
        print(f"=== {cls} (3 scenarios, mean over scenarios) ===")
        for k in ["MOEA3", "MOEA2", "GBL", "GSM"]:
            c = np.mean(rows[f"{k}_code"]); r = np.mean(rows[f"{k}_corr"])
            print(f"  {k}: code_f3={c:.4f}  correct_f3={r:.4f}  ratio_corr/code={r/c:.3f}")
        mc = np.mean(rows["MOEA3_code"]); mr = np.mean(rows["MOEA3_corr"])
        bc = np.mean(rows["GBL_code"]); br = np.mean(rows["GBL_corr"])
        m2c = np.mean(rows["MOEA2_code"]); m2r = np.mean(rows["MOEA2_corr"])
        print(f"  MOEA3 vs GBL: code gain={(mc-bc)/bc*100:+.1f}%  correct gain={(mr-br)/br*100:+.1f}%")
        print(f"  MOEA3 vs MOEA2: code gain={(mc-m2c)/m2c*100:+.1f}%  correct gain={(mr-m2r)/m2r*100:+.1f}%")


if __name__ == "__main__":
    main()
