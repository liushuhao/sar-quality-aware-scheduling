#!/usr/bin/env python3
"""P1-1: Random-initialized MOEA-2 control experiment (full run).
Compares hotstart vs random-init across all S1-S4 scenarios.
3 random seeds per scenario for random-init.
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

def build_hotstart(windows, targets):
    """Encode G-BL solution as chromosome."""
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

# Collect scenarios
groups = OrderedDict()
for g in ["S1", "S2", "S3", "S4"]:
    d = SCENARIOS_DIR / g
    if d.is_dir():
        pkgs = sorted(d.glob("*.pkl"))
        if pkgs:
            groups[g] = pkgs

print(f"Groups: {dict((g, len(ps)) for g, ps in groups.items())}")
print("="*60)

all_results = {"hotstart": {}, "random_init": {}}
N_RANDOM_SEEDS = 3  # 3 random seeds per scenario

for group, pkls in groups.items():
    print(f"\n{'='*60}")
    print(f"Group {group}: {len(pkls)} scenarios")

    for i, pkl in enumerate(pkls):
        print(f"  [{i+1}/{len(pkls)}] {pkl.name}...", end=" ", flush=True)

        # Hotstart run (once per scenario)
        with open(pkl, 'rb') as f:
            data = pickle.load(f)
        windows = data.get("windows", [])
        targets = data.get("targets", [])
        hs = build_hotstart(windows, targets)
        r_hot = run_one(pkl, hotstart_individual=hs)
        all_results["hotstart"][f"{group}/{pkl.name}"] = r_hot

        # Random-init runs (N_RANDOM_SEEDS per scenario)
        r_rand_list = []
        for rs in range(N_RANDOM_SEEDS):
            r_rand = run_one(pkl, hotstart_individual=None)
            r_rand_list.append(r_rand)

        # Average across random seeds
        all_results["random_init"][f"{group}/{pkl.name}"] = {
            "runs": r_rand_list,
            "f1_mean": float(np.mean([r["f1"] for r in r_rand_list])),
            "f1_std": float(np.std([r["f1"] for r in r_rand_list])),
            "f2_mean": float(np.mean([r["f2"] for r in r_rand_list])),
            "f3_mean": float(np.mean([r["f3"] for r in r_rand_list])),
        }

        print(f"hot:f1*={r_hot['f1']:.2f} rand:f1*={all_results['random_init'][f'{group}/{pkl.name}']['f1_mean']:.2f}")

# Summary stats
print(f"\n{'='*60}")
print("SUMMARY by group:")
for group in ["S1", "S2", "S3", "S4"]:
    hot_f1 = [r["f1"] for k, r in all_results["hotstart"].items() if k.startswith(group)]
    rand_f1 = [r["f1_mean"] for k, r in all_results["random_init"].items() if k.startswith(group)]
    hot_f2 = [r["f2"] for k, r in all_results["hotstart"].items() if k.startswith(group)]
    rand_f2 = [r["f2_mean"] for k, r in all_results["random_init"].items() if k.startswith(group)]
    if hot_f1:
        print(f"  {group}: hotstart f1*={np.mean(hot_f1):.3f}±{np.std(hot_f1):.3f}, f2={np.mean(hot_f2):.4f}")
        print(f"         random    f1*={np.mean(rand_f1):.3f}±{np.std(rand_f1):.3f}, f2={np.mean(rand_f2):.4f}")
        print(f"         Δf1*={np.mean(rand_f1)-np.mean(hot_f1):.3f}")

# Save
out_path = RESULTS_DIR / "p1-1_results.json"
with open(out_path, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\nSaved to {out_path}")