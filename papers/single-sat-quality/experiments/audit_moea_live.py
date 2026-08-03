#!/usr/bin/env python3
"""Live MOEA audit: re-run MOEA exactly as the pipeline runner does
(G-BL hot-start x0, pop 100 / gen 200, saved seed) on one scenario per
class, then audit the selected knee solution for the G-SM/GA-P-BL defect
class: out-of-window times, |phi| outside [15,50] deg, C3 shortfalls,
hard time overlaps. Compares re-run f1/f2/f3 against the saved progress
entry to confirm pipeline fidelity.
"""
import argparse
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np

PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance_from_scenario, compute_full_attitude, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
BIG = 5.0


def audit_schedule(schedule, inst):
    t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
    N = inst.N
    phi_arr = np.zeros(N)
    t_arr = np.zeros(N)
    sel = []
    xwin = 0
    for obs in schedule:
        i = t2i.get(obs.window.target_id)
        if i is None:
            continue
        t = obs.t_actual_start.timestamp()
        roll, _, _ = compute_full_attitude(inst.tasks[i], t, 1.0, inst)
        sel.append(i)
        phi_arr[i] = roll
        t_arr[i] = t
        if not any(ws <= t <= we for ws, we in inst.tasks[i].window_times):
            xwin += 1
    c1p = sum(1 for i in sel
              if abs(phi_arr[i]) < inst.phi_min or abs(phi_arr[i]) > inst.phi_max)
    rep = ConstraintVerifier(inst).verify_solution(sel, phi_arr, t_arr)
    # C2 = maneuver/non-overlap (transition), C3 = energy, C4 = memory.
    mags = [v.magnitude for v in rep.results["C2"].violations]
    c3fail = 0 if rep.results["C3"].passed else len(rep.results["C3"].violations)
    c4fail = 0 if rep.results["C4"].passed else len(rep.results["C4"].violations)
    order = sorted(((i, float(t_arr[i])) for i in sel), key=lambda p: p[1])
    overlap = 0
    for k in range(len(order) - 1):
        ia, ta = order[k]
        ib, tb = order[k + 1]
        if tb < ta + inst.tasks[ia].duration:
            overlap += 1
    return {
        "nsel": len(sel), "xwin": xwin, "c1p": c1p,
        "c2big": sum(1 for m in mags if m > BIG),
        "c2tiny": sum(1 for m in mags if m <= BIG),
        "c3fail": c3fail, "c4fail": c4fail,
        "worst": max(mags, default=0.0),
        "overlap": overlap,
        "pairs": max(len(sel) - 1, 0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", default="S1,S2,S3,S4")
    ap.add_argument("--nobj", type=int, default=3)
    ap.add_argument("--pat", default="A_seed00")
    args = ap.parse_args()

    prog = json.load(open(PAPER_DIR / f"experiments/results/moea_{args.nobj}obj/_progress.json",
                          encoding="utf-8"))["completed"]

    for cls in args.classes.split(","):
        fp = PAPER_DIR / f"experiments/scenarios/{cls}/{cls}-{args.pat}.pkl"
        key = f"{cls}/{fp.name}"
        data = pickle.load(open(fp, "rb"))
        alt_m = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
        inst = build_agile_instance_from_scenario(
            data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
            altitude_m=alt_m)
        precompute_geometry(inst, step_s=10.0)

        # hot-start x0 from G-BL, exactly as run_moea_3obj.py builds it
        b1 = baseline_b1(data["windows"], data["targets"], instance=inst)
        t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
        x0 = np.full(2 * inst.N, 0.5)
        x0[: inst.N] = 0.0
        seen = set()
        for obs in b1.schedule:
            idx = t2i.get(obs.window.target_id)
            if idx is not None and idx not in seen:
                seen.add(idx)
                x0[idx] = 1.0
                span = inst.tasks[idx].time_span
                tau = ((obs.t_actual_start.timestamp() - inst.tasks[idx].t_earliest) / span
                       if span > 0 else 0.5)
                x0[inst.N + idx] = max(0.0, min(1.0, tau))

        seed = prog.get(key, {}).get("seed", 1)
        t0 = time.time()
        res = moea_solver(data["windows"], data["targets"],
                          population_size=100, n_generations=200, n_obj=args.nobj,
                          n_ref_dirs=12, seed=seed,
                          max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                          hotstart_individual=x0, instance=inst)
        rt = time.time() - t0
        md = res.metadata
        a = audit_schedule(res.schedule, inst)
        saved = prog.get(key, {})
        print(f"\n=== {key} | MOEA-{args.nobj} | N={inst.N} | {rt:.0f}s ===")
        print(f"rerun : f1={md['f1']:.4f} f2={md['f2']:.4f} f3={md['f3']:.4f} nsel={md['n_selected']}")
        print(f"saved : f1={saved.get('f1')} f2={saved.get('f2')} f3={saved.get('f3')} nsel={saved.get('n_selected')}")
        print(f"audit : xWin={a['xwin']} C1ppr={a['c1p']} C2big={a['c2big']} "
              f"C2tiny={a['c2tiny']} C3fail={a['c3fail']} C4fail={a['c4fail']} "
              f"worst={a['worst']:.1f}s "
              f"overlap={a['overlap']}/{a['pairs']} pairs")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
