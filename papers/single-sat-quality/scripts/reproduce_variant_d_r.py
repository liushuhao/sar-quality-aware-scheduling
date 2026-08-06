#!/usr/bin/env python3
"""Reproduce variant-D per-task corr(f2_i, f3_i) on real post-hoc geometry.

Variant D optimizes only f1 (f2/f3 constant 1.0 during search). After the
search, we take the reported knee schedule, look up the true incidence angle
theta and squint psi_sq at each selected task's observation time from the
precomputed geometry cache, and compute

    f2_i = sin(theta_i) * cos(psi_sq,i)
    f3_i = cos(theta_i)^3 * cos(psi_sq,i)^3

exactly as decode_solution() does for the physical solvers. The pooled
Pearson r over these per-task pairs is what supports the paper's claim that
variant-D schedules still exhibit r ~ +0.95.

Usage:
    PYTHONPATH=<repo>/src python scripts/reproduce_variant_d_r.py [S1 S2 ...]
"""
import sys, pickle, json, time, math, gc, os
from pathlib import Path
from collections import OrderedDict
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance, precompute_geometry

# reuse the variant-D runner verbatim
sys.path.insert(0, str(PROJECT / "experiments"))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "run_d", PROJECT / "experiments" / "run_moea_3obj_no_physics.py")
run_d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_d)

GROUPS = ["S1", "S2", "S3", "S4"]
# mirror original runner: minimize(..., seed=seed or 1) with seed=None
SEED = None


def pearson(xs, ys):
    x = np.asarray(xs, dtype=float); y = np.asarray(ys, dtype=float)
    return float(np.corrcoef(x, y)[0, 1])


def run_class(cls, out):
    """Run one class; append per-task points to out['raw'][cls] and checkpoint
    after every scenario (resumable: skips scenarios already recorded)."""
    pkgs = sorted((PROJECT / "experiments" / "scenarios" / cls).glob("*.pkl"))
    raw = out["raw"].setdefault(cls, [])  # list of [scenario, [f2...], [f3...]]
    done = {row[0] for row in raw}
    t0 = time.time()
    for k, pkl in enumerate(pkgs):
        if pkl.name in done:
            continue
        try:
            with open(pkl, "rb") as f:
                data = pickle.load(f)
            windows, targets = data.get("windows", []), data.get("targets", [])
            gbl = baseline_b1(windows, targets)
            instance = build_agile_instance(
                windows, targets,
                max_slew_rate=run_d.SLEW_RATE, settle_time=run_d.SETTLE_TIME)
            precompute_geometry(instance, step_s=10.0)
            target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
            x0 = np.zeros(2 * instance.N); seen = set()
            for obs in gbl.schedule:
                tid = obs.window.target_id
                if tid in target_to_idx and tid not in seen:
                    idx = target_to_idx[tid]; seen.add(idx)
                    x0[idx] = 1.0
                    span = instance.tasks[idx].time_span
                    tau = ((obs.t_actual_start.timestamp()
                            - instance.tasks[idx].t_earliest) / span
                           if span > 0 else 0.5)
                    x0[instance.N + idx] = max(0, min(1, tau))
            hotstart = x0 if seen else None

            result = run_d.moea_solver_no_physics(
                windows, targets,
                population_size=run_d.MOEA_PARAMS["population_size"],
                n_generations=run_d.MOEA_PARAMS["n_generations"],
                n_obj=3, n_ref_dirs=12,
                max_slew_rate=run_d.SLEW_RATE, settle_time=run_d.SETTLE_TIME,
                hotstart_individual=hotstart, instance=instance,
                seed=SEED,
            )
            f2s, f3s = _geom_from_schedule(result.schedule, instance)
        except Exception as e:
            print(f"  [{cls} {pkl.name}] ERROR {type(e).__name__}: {e}",
                  flush=True)
            f2s, f3s = [], []
        raw.append([pkl.name, f2s, f3s])
        _save(out)
        del instance, result, windows, targets, gbl
        gc.collect()
        if (k + 1) % 5 == 0:
            npts = sum(len(r[1]) for r in raw)
            print(f"  [{cls} {k+1}/{len(pkgs)}] {time.time()-t0:.0f}s "
                  f"pooled n={npts}", flush=True)
    f2_all = [v for r in raw for v in r[1]]
    f3_all = [v for r in raw for v in r[2]]
    r = pearson(f2_all, f3_all) if f2_all else float("nan")
    return {"class": cls, "n_scenarios": len(pkgs),
            "n_done": len(raw), "n_points": len(f2_all), "r_pooled": r,
            "f2_mean": float(np.mean(f2_all)) if f2_all else None,
            "f3_mean": float(np.mean(f3_all)) if f3_all else None,
            "elapsed_s": round(time.time() - t0, 1)}


def _pick_knee(frontier):
    if not frontier:
        return {"f1": 0, "f2": 0, "f3": 0, "selected": []}
    f1 = np.array([s["f1"] for s in frontier])
    f2 = np.array([s["f2"] for s in frontier])
    f3 = np.array([s.get("f3", 0) for s in frontier])
    def norm(a):
        return (a - a.min()) / (a.max() - a.min() or 1)
    knee = int(np.argmax(norm(f1) + norm(f2) + norm(f3)))
    return frontier[knee]


def _geom_from_schedule(schedule, instance):
    """Look up true (theta, psi_sq) at each scheduled observation time."""
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    f2s, f3s = [], []
    for obs in schedule:
        tid = obs.window.target_id
        if tid not in target_to_idx:
            continue
        i = target_to_idx[tid]
        t_act = obs.t_actual_start.timestamp()
        geom = instance.geom_cache.lookup(i, t_act)
        theta = geom.theta
        cos_psi = geom.cos_psi
        f2s.append(math.sin(theta) * cos_psi)
        f3s.append((math.cos(theta) ** 3) * (cos_psi ** 3))
    return f2s, f3s


OUTPATH = PROJECT / "experiments" / "results" / "variant_d_per_task_r.json"


def _save(out):
    # compute summaries from raw, then write atomically
    groups = {}
    all_f2, all_f3 = [], []
    for cls, rows in out["raw"].items():
        f2 = [v for r in rows for v in r[1]]
        f3 = [v for r in rows for v in r[2]]
        all_f2.extend(f2); all_f3.extend(f3)
        groups[cls] = {
            "class": cls, "n_done": len(rows), "n_points": len(f2),
            "r_pooled": pearson(f2, f3) if f2 else float("nan"),
            "f2_mean": float(np.mean(f2)) if f2 else None,
            "f3_mean": float(np.mean(f3)) if f3 else None,
        }
    payload = {"seed": SEED, "params": run_d.MOEA_PARAMS,
               "groups": groups,
               "r_pooled_overall": pearson(all_f2, all_f3) if all_f2 else float("nan"),
               "n_points_overall": len(all_f2)}
    tmp = str(OUTPATH) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, OUTPATH)


def main():
    classes = sys.argv[1:] if len(sys.argv) > 1 else GROUPS
    out = {"seed": SEED, "params": run_d.MOEA_PARAMS, "raw": {}}
    if OUTPATH.exists():
        try:
            prev = json.load(open(OUTPATH))
            # raw not stored in summary json; resume starts fresh per class
        except Exception:
            pass
    for cls in classes:
        print(f"=== {cls} ===", flush=True)
        g = run_class(cls, out)
        print(f"  {cls}: n={g['n_points']} r={g['r_pooled']:+.4f} "
              f"({g['elapsed_s']}s)", flush=True)
    _save(out)
    final = json.load(open(OUTPATH))
    print(f"OVERALL: n={final['n_points_overall']} "
          f"r={final['r_pooled_overall']:+.4f}")
    print("wrote", OUTPATH)


if __name__ == "__main__":
    main()
