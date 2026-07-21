#!/usr/bin/env python3
"""C-4 / R3-1 control: hot-start vs random-init MOEA-2 at S3 and S4.

FIX 2026-07-20: incremental save per seed + resume. A kill mid-run loses at
most one seed.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJ.parent.parent / "src"))
sys.path.insert(0, str(_PROJ.parent.parent))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance, precompute_geometry

PROJECT = _PROJ
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-1_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 100, 200
N_SCENARIOS = 5
N_SEEDS = 3
GROUPS = ["S3", "S4"]


def build_hotstart(windows, targets):
    gbl = baseline_b1(windows, targets)
    instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
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
    return x0 if seen else None


def run_one(pkl_path, mode, seed):
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    hs = build_hotstart(windows, targets) if mode == "hot" else None
    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=POP, n_generations=GEN,
        n_obj=2, n_ref_dirs=12,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=hs, seed=seed,
    )
    rt = time.time() - t0
    meta = result.metadata
    return {
        "mode": mode, "seed": seed,
        "f1": float(meta.get("f1", 0)),
        "f2": float(meta.get("f2", 0)),
        "n_selected": int(meta.get("n_selected", 0)),
        "runtime_s": round(rt, 1),
    }


partial_path = RESULTS_DIR / "s3_s4_control.json"
out = {"params": {"pop": POP, "gen": GEN, "n_scenarios": N_SCENARIOS, "n_seeds": N_SEEDS},
       "results": {}, "summary": {}}
if partial_path.exists():
    try:
        out = json.load(open(partial_path, encoding="utf-8"))
        print(f"Resumed: {sum(len(v) for v in out.get('results',{}).values())} runs done")
    except Exception:
        pass
all_results = out.setdefault("results", {})

for group in GROUPS:
    d = SCENARIOS_DIR / group
    pkls = sorted(d.glob("*.pkl"))[:N_SCENARIOS]
    if not pkls:
        continue
    runs = all_results.setdefault(group, [])
    done = {(r["scenario"], r["seed"]) for r in runs}
    print(f"\nGroup {group}: {len(pkls)} scenarios x {N_SEEDS} seeds x 2 modes")
    for i, pkl in enumerate(pkls):
        for seed in range(N_SEEDS):
            if (pkl.name, seed) in done:
                print(f"  [{i+1}/{len(pkls)}] {pkl.name} seed{seed} SKIP (done)")
                continue
            print(f"  [{i+1}/{len(pkls)}] {pkl.name} seed{seed}", end=" ", flush=True)
            rh = run_one(pkl, "hot", seed)
            rr = run_one(pkl, "random", seed)
            print(f"hot={rh['f1']:.3f} random={rr['f1']:.3f} d={rh['f1']-rr['f1']:.3f}")
            runs.append({"scenario": pkl.name, "seed": seed, "hot": rh, "random": rr})
            json.dump(out, open(partial_path, "w"), indent=2)

summary = {}
for group, rs in all_results.items():
    hot_f1 = np.array([r["hot"]["f1"] for r in rs])
    rand_f1 = np.array([r["random"]["f1"] for r in rs])
    summary[group] = {
        "hot_f1_mean": float(hot_f1.mean()), "hot_f1_std": float(hot_f1.std()),
        "random_f1_mean": float(rand_f1.mean()), "random_f1_std": float(rand_f1.std()),
        "delta_mean": float((hot_f1 - rand_f1).mean()), "n": len(rs),
    }
out["summary"] = summary
json.dump(out, open(partial_path, "w"), indent=2)
print("\n=== SUMMARY ===")
for g, s in summary.items():
    print(f"{g}: hot={s['hot_f1_mean']:.3f}+/-{s['hot_f1_std']:.3f}  random={s['random_f1_mean']:.3f}+/-{s['random_f1_std']:.3f}  d={s['delta_mean']:.3f}")
print(f"\nSaved: {partial_path}")
