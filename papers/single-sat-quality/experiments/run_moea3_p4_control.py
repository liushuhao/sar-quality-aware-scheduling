#!/usr/bin/env python3
"""F4 matched-reference-point control: MOEA-3 with p=4 (H=15) on S1.

Tests whether the +7% f3 gain of MOEA-3 (p=12, H=91) over MOEA-2 (p=12, H=13)
at S1 survives matching reference-direction count to MOEA-2's order.
Same pop=100, gen=200, G-BL hot-start as the main run.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = Path(__file__).resolve().parent.parent
SCEN = PROJECT / "experiments" / "scenarios" / "S1"
SLEW = 0.0524; SETTLE = 5.0
P_REF = 4  # H = C(3+4-1,4) = 15


def run_one(pkl):
    # pkl files are this repo's own scenario fixtures (scripts/generate_s5_scenarios.py),
    # same trusted source as the main MOEA runners; pickle is used project-wide.
    data = pickle.load(open(pkl, "rb"))
    windows = data.get("windows", []); targets = data.get("targets", [])
    inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE)
    precompute_geometry(inst, step_s=10.0)
    gbl = baseline_b1(windows, targets, max_slew_rate=SLEW, settle_time=SETTLE,
                      geom_cache=inst.geom_cache, instance=inst)
    t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
    x0 = np.zeros(2 * inst.N)
    seen = set()
    for obs in gbl.schedule:
        idx = t2i.get(obs.window.target_id)
        if idx is not None and idx not in seen:
            seen.add(idx); x0[idx] = 1.0
            span = inst.tasks[idx].time_span
            tau = (obs.t_actual_start.timestamp() - inst.tasks[idx].t_earliest) / span if span > 0 else 0.5
            x0[inst.N + idx] = max(0.0, min(1.0, tau))
    res = moea_solver(windows, targets, population_size=100, n_generations=200,
                      n_obj=3, n_ref_dirs=P_REF, max_slew_rate=SLEW, settle_time=SETTLE,
                      hotstart_individual=x0 if seen else None, instance=inst)
    m = res.metadata
    return float(m["f1"]), float(m["f2"]), float(m["f3"]), int(m["n_selected"])


def main():
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    pkgs = sorted(SCEN.glob("*.pkl"))
    if only is not None:
        pkgs = pkgs[:only]
    out = []
    for i, p in enumerate(pkgs):
        t0 = time.time()
        f1, f2, f3, n = run_one(p)
        out.append({"scen": p.name, "f1": f1, "f2": f2, "f3": f3, "n": n, "rt_s": round(time.time()-t0, 1)})
        print(f"{i+1}/{len(pkgs)} {p.name}: f1={f1:.3f} f2={f2:.3f} f3={f3:.3f} n={n} ({time.time()-t0:.0f}s)")
    arr = {k: np.array([r[k] for r in out]) for k in ("f1", "f2", "f3")}
    print(f"\n=== p={P_REF} (H=15) S1 means over {len(out)} scenarios ===")
    for k in ("f1", "f2", "f3"):
        print(f"  {k} = {arr[k].mean():.4f} +/- {arr[k].std(ddof=1):.4f}")
    # compare to stored p=12
    prog = json.load(open(PROJECT / "experiments/results/moea_3obj/_progress.json", encoding="utf-8"))
    comp = prog.get("completed", prog)
    s12 = [v for k, v in comp.items() if k.startswith("S1/")]
    a12 = {k: np.mean([v[k] for v in s12]) for k in ("f1", "f2", "f3")}
    print("\n=== p=12 (H=91) stored S1 means ===")
    for k in ("f1", "f2", "f3"):
        print(f"  {k} = {a12[k]:.4f}")
    print(f"\n  delta f3 (p4 - p12) = {arr['f3'].mean()-a12['f3']:+.4f}")
    json.dump(out, open(PROJECT / "experiments/results/moea_3obj_p4_control.json", "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    main()
