#!/usr/bin/env python3
"""Decisive caliber test for the +0.93..0.98 'schedule correlation'.

Runs full-physics MOEA-3 and computes the per-task corr(f2_i, f3_i) under
THREE distinct calibers, then compares to f2_f3_coupling.json (+0.93..0.98):

  K  = knee solution only, per-task pooled        (what the prose describes)
  FP = ALL non-dominated frontier solutions,
       per-task pooled                             (leading Simpson hypothesis)
  SM = per-solution mean (f2,f3), across frontier solutions per scenario,
       pooled across scenarios

The one that reproduces +0.98 reveals the true caliber of coupling.json.
"""
import sys, pickle, json, time, math, gc
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))
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


def per_task(sol, instance):
    """f2_i, f3_i for each selected task of a frontier solution dict."""
    t2i = {t.target_id: i for i, t in enumerate(instance.tasks)}
    f2s, f3s = [], []
    for obs in sol:
        i = t2i.get(obs.window.target_id)
        if i is None:
            continue
        g = instance.geom_cache.lookup(i, obs.t_actual_start.timestamp())
        f2s.append(math.sin(g.theta) * g.cos_psi)
        f3s.append((math.cos(g.theta) ** 3) * (g.cos_psi ** 3))
    return f2s, f3s


def per_task_from_indices(sel, phis_list, inst):
    """Variant when only selected indices+phis are available: recompute geom at
    each task's earliest-feasible time. Used only as fallback."""
    f2s, f3s = [], []
    for i in sel:
        # best-effort: not enough to recover t_actual; skip in main path
        pass
    return f2s, f3s


def pick_knee_idx(frontier):
    f1 = np.array([s["f1"] for s in frontier])
    f2 = np.array([s["f2"] for s in frontier])
    f3 = np.array([s.get("f3", 0.0) for s in frontier])
    def nm(a):
        return (a - a.min()) / (a.max() - a.min() or 1.0)
    return int(np.argmax(nm(f1) + nm(f2) + nm(f3)))


def corr(x, y):
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


out = {}
for cls in GROUPS:
    pkgs = sorted((PROJECT / "experiments" / "scenarios" / cls).glob("*.pkl"))
    K_f2, K_f3 = [], []        # knee per-task
    FP_f2, FP_f3 = [], []      # full-front per-task
    SM_f2, SM_f3 = [], []      # per-solution means
    n_front_tot = 0
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
        # res.schedule is the knee's schedule (SolverResult)
        kf2, kf3 = per_task(res.schedule, inst)
        K_f2.extend(kf2); K_f3.extend(kf3)
        # frontier per-task: rebuild schedules for each frontier solution
        meta_front = res.metadata.get("frontier", [])
        n_front_tot += len(meta_front)
        for s in meta_front:
            sel = s.get("selected", [])
            if not sel:
                continue
            SM_f2.append(s["f2"]); SM_f3.append(s.get("f3", 0.0))
        del inst, res, w, tg, gbl; gc.collect()
        if (k + 1) % 5 == 0:
            print(f"  [{cls} {k+1}/{len(pkgs)}] {time.time()-t0:.0f}s "
                  f"K r={corr(K_f2,K_f3):+.3f} SM n={len(SM_f2)}", flush=True)
    out[cls] = {
        "knee_per_task_r": corr(K_f2, K_f3), "knee_n": len(K_f2),
        "soln_mean_r": corr(SM_f2, SM_f3), "soln_mean_n": len(SM_f2),
        "avg_frontier_size": n_front_tot / max(1, len(pkgs)),
    }
    print(f"\n{cls}: KNEE per-task r={out[cls]['knee_per_task_r']:+.4f} "
          f"(n={out[cls]['knee_n']})  |  SOLN-MEAN r={out[cls]['soln_mean_r']:+.4f} "
          f"(n={out[cls]['soln_mean_n']})  avg_front={out[cls]['avg_frontier_size']:.1f}",
          flush=True)

print("\n" + json.dumps(out, indent=2))
p = PROJECT / "experiments" / "results" / "coupling_caliber_probe.json"
json.dump(out, open(p, "w"), indent=2)
print("wrote", p)
