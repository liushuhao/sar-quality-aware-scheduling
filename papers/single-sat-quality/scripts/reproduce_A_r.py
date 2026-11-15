#!/usr/bin/env python3
"""Same-knee, same per-task geometry, same pooled Pearson — but for the
full-physics MOEA-3 (variant A), to compare apples-to-apples against variant D
computed by reproduce_variant_d_r.py. Settles whether the +0.93..0.98 in
f2_f3_coupling.json is a same-caliber per-task-within-knee-schedule correlation.
"""
import sys, pickle, json, time, math, gc, os
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(PROJECT / "experiments"))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.moea import moea_solver

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "run_d", PROJECT / "experiments" / "run_moea_3obj_no_physics.py")
run_d = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(run_d)

GROUPS = sys.argv[1:] or ["S1"]
POP, GEN, REFS = 100, 200, 12


def geom_from_schedule(schedule, instance):
    t2i = {t.target_id: i for i, t in enumerate(instance.tasks)}
    f2s, f3s = [], []
    for obs in schedule:
        i = t2i.get(obs.window.target_id)
        if i is None:
            continue
        g = instance.geom_cache.lookup(i, obs.t_actual_start.timestamp())
        f2s.append(math.sin(g.theta) * g.cos_psi)
        f3s.append((math.cos(g.theta) ** 3) * (g.cos_psi ** 3))
    return f2s, f3s


def pick_knee(frontier):
    if not frontier:
        return None
    f1 = np.array([s["f1"] for s in frontier])
    f2 = np.array([s["f2"] for s in frontier])
    f3 = np.array([s.get("f3", 0.0) for s in frontier])
    def nm(a):
        return (a - a.min()) / (a.max() - a.min() or 1.0)
    return frontier[int(np.argmax(nm(f1) + nm(f2) + nm(f3)))]


def pearson(x, y):
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


out = {}
for cls in GROUPS:
    pkgs = sorted((PROJECT / "experiments" / "scenarios" / cls).glob("*.pkl"))
    F2, F3 = [], []
    t0 = time.time()
    for k, pkl in enumerate(pkgs):
        with open(pkl, "rb") as f:
            data = pickle.load(f)
        w, tg = data["windows"], data["targets"]
        gbl = baseline_b1(w, tg)
        inst = build_agile_instance(w, tg, max_slew_rate=run_d.SLEW_RATE,
                                    settle_time=run_d.SETTLE_TIME)
        precompute_geometry(inst, step_s=10.0)
        t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
        x0 = np.zeros(2 * inst.N); seen = set()
        for obs in gbl.schedule:
            tid = obs.window.target_id
            if tid in t2i and tid not in seen:
                i = t2i[tid]; seen.add(i); x0[i] = 1.0
                sp = inst.tasks[i].time_span
                x0[inst.N + i] = max(0, min(1,
                    (obs.t_actual_start.timestamp() - inst.tasks[i].t_earliest) / sp
                    if sp > 0 else 0.5))
        res = moea_solver(w, tg, population_size=POP, n_generations=GEN,
                          seed=None, n_ref_dirs=REFS, n_obj=3,
                          hotstart_individual=x0 if seen else None,
                          max_slew_rate=run_d.SLEW_RATE,
                          settle_time=run_d.SETTLE_TIME)
        f2s, f3s = geom_from_schedule(res.schedule, inst)
        F2.extend(f2s); F3.extend(f3s)
        del inst, res, w, tg, gbl; gc.collect()
        if (k + 1) % 5 == 0:
            print(f"  [A {cls} {k+1}/{len(pkgs)}] {time.time()-t0:.0f}s "
                  f"n={len(F2)} r={pearson(F2,F3):+.3f}", flush=True)
    out[cls] = {"r": pearson(F2, F3), "n": len(F2),
                "f2": float(np.mean(F2)), "f3": float(np.mean(F3)),
                "elapsed_s": round(time.time() - t0, 1)}
    print(f"A {cls}: r={out[cls]['r']:+.4f} n={out[cls]['n']} "
          f"f2={out[cls]['f2']:.3f} f3={out[cls]['f3']:.3f}", flush=True)

print(json.dumps(out, indent=2))
