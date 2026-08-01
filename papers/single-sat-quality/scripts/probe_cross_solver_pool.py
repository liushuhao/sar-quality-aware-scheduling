#!/usr/bin/env python3
"""Test the last plausible caliber for the lost +0.93..0.98:

pool per-task (f2_i, f3_i) across ALL solvers' schedules (G-BL, G-SM,
MOEA-3), not just one solver. G-SM's deliberate zero-squint selections
and the MOEAs' low-squint knees may jointly push the pooled correlation
positive — the "solver-selected schedules" (plural) reading of the prose.

S1 only (fast signal).
"""
import sys, pickle, json, time, math, gc
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "experiments"))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.moea import moea_solver

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "run_d", PROJECT / "experiments" / "run_moea_3obj_no_physics.py")
run_d = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(run_d)

PKLS = sorted((PROJECT / "experiments" / "scenarios" / "S1").glob("*.pkl"))
POP, GEN, REFS = 100, 200, 12


def per_task(schedule, instance):
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


def hotstart(inst, gbl):
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
    return x0 if seen else None


def corr(x, y):
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


POOL = {"GBL": [[], []], "GSM": [[], []], "MOEA3": [[], []], "ALL": [[], []]}
t0 = time.time()
for k, pkl in enumerate(PKLS):
    with open(pkl, "rb") as f:
        data = pickle.load(f)
    w, tg = data["windows"], data["targets"]
    inst = build_agile_instance(w, tg, max_slew_rate=run_d.SLEW_RATE,
                                settle_time=run_d.SETTLE_TIME)
    precompute_geometry(inst, step_s=10.0)

    gbl = baseline_b1(w, tg, instance=inst, geom_cache=inst.geom_cache)
    gsm = baseline_b3(w, tg, instance=inst, geom_cache=inst.geom_cache)
    m3 = moea_solver(w, tg, population_size=POP, n_generations=GEN,
                     seed=None, n_ref_dirs=REFS, n_obj=3,
                     hotstart_individual=hotstart(inst, gbl),
                     max_slew_rate=run_d.SLEW_RATE,
                     settle_time=run_d.SETTLE_TIME)

    for name, res in (("GBL", gbl), ("GSM", gsm), ("MOEA3", m3)):
        f2, f3 = per_task(res.schedule, inst)
        POOL[name][0].extend(f2); POOL[name][1].extend(f3)
        POOL["ALL"][0].extend(f2); POOL["ALL"][1].extend(f3)

    del inst, gbl, gsm, m3, w, tg; gc.collect()
    if (k + 1) % 5 == 0:
        print(f"  [{k+1}/{len(PKLS)}] {time.time()-t0:.0f}s", flush=True)

out = {}
for name, (f2, f3) in POOL.items():
    out[name] = {"r": corr(f2, f3), "n": len(f2)}
    print(f"{name}: r={out[name]['r']:+.4f} n={out[name]['n']}", flush=True)
json.dump(out, open(PROJECT / "experiments" / "results" /
                    "cross_solver_pool_probe.json", "w"), indent=2)
print("done")
