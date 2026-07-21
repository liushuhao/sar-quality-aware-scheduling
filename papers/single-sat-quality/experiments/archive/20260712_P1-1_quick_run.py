#!/usr/bin/env python3
"""P1-1: Random-initialized MOEA-2 control — quick version.
10 scenarios per group (S1-S4), 3 random seeds each.
"""
import pickle, json, sys, time
from pathlib import Path
from collections import OrderedDict
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(_PROJ))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.baselines import baseline_b1

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-1_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
POP = 100
GEN = 200
N_SCENARIOS = 10
N_RANDOM_SEEDS = 3

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

def run_one(pkl_path: Path, hotstart_individual=None):
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)
    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=POP, n_generations=GEN, n_obj=2, n_ref_dirs=12,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=hotstart_individual,
    )
    rt = time.time() - t0
    meta = result.metadata
    return {
        "seed": seed, "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0)),
        "f1_raw": float(meta.get("f1_raw", 0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0)),
        "f3": float(meta.get("f3", 0)),
        "runtime_s": round(rt, 3),
        "n_frontier": len(meta.get("frontier", [])),
    }

# Collect first N_SCENARIOS per group
groups = OrderedDict()
for g in ["S1", "S2", "S3", "S4"]:
    d = SCENARIOS_DIR / g
    if d.is_dir():
        pkgs = sorted(d.glob("*.pkl"))[:N_SCENARIOS]
        if pkgs:
            groups[g] = pkgs

all_results = {}
for group, pkls in groups.items():
    print(f"\nGroup {group}: {len(pkls)} scenarios")
    for i, pkl in enumerate(pkls):
        print(f"  [{i+1}/{len(pkls)}] {pkl.name}", end=" ", flush=True)
        with open(pkl, 'rb') as f:
            data = pickle.load(f)
        windows = data.get("windows", [])
        targets = data.get("targets", [])

        # Hotstart
        hs = build_hotstart(windows, targets)
        r_hot = run_one(pkl, hotstart_individual=hs)

        # Random init (3 seeds)
        r_rand_list = [run_one(pkl, hotstart_individual=None) for _ in range(N_RANDOM_SEEDS)]

        key = f"{group}/{pkl.name}"
        all_results[key] = {
            "hotstart": r_hot,
            "random_init": r_rand_list,
            "random_f1_mean": float(np.mean([r["f1"] for r in r_rand_list])),
            "random_f1_std": float(np.std([r["f1"] for r in r_rand_list])),
            "random_f2_mean": float(np.mean([r["f2"] for r in r_rand_list])),
            "random_f3_mean": float(np.mean([r["f3"] for r in r_rand_list])),
        }
        print(f"hs:f1*={r_hot['f1']:.2f} rnd:f1*={all_results[key]['random_f1_mean']:.2f}")

# Summary
print(f"\n{'='*60}\nSUMMARY:")
for group in ["S1", "S2", "S3", "S4"]:
    keys = [k for k in all_results if k.startswith(group)]
    if not keys: continue
    hs_f1 = [all_results[k]["hotstart"]["f1"] for k in keys]
    hs_f2 = [all_results[k]["hotstart"]["f2"] for k in keys]
    rd_f1 = [all_results[k]["random_f1_mean"] for k in keys]
    rd_f2 = [all_results[k]["random_f2_mean"] for k in keys]
    print(f"  {group}: hotstart f1*={np.mean(hs_f1):.3f}±{np.std(hs_f1):.3f}  random f1*={np.mean(rd_f1):.3f}±{np.std(rd_f1):.3f}  Δ={np.mean(rd_f1)-np.mean(hs_f1):.3f}")
    print(f"         hotstart f2 ={np.mean(hs_f2):.4f}±{np.std(hs_f2):.4f}  random f2 ={np.mean(rd_f2):.4f}±{np.std(rd_f2):.4f}")

with open(RESULTS_DIR / "p1-1_results_quick.json", "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\nSaved.")