#!/usr/bin/env python3
"""Random-init Variant D: does no-physics solver converge low-squint WITHOUT hot-start?

Distinguishes DA MAJOR 3/4/5:
- (i) solver-convergence: random-init D still low-squint (f2 ~= 0.594 like hot-start)
- (ii) hot-start residue: random-init D explores high-psi (f2 << 0.594)

f2 = mean(sin(theta)*cos(psi)) over selected tasks (post-hoc geometric).
high-psi -> cos(psi) small -> f2 small. If random-init D f2 ~= 0.594 (hot-start D
value) -> (i) objective-neutrality survives. If << 0.594 -> (ii) hot-start residue.
"""
import pickle, json, sys, time
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJ.parent.parent / "src"))
sys.path.insert(0, str(_PROJ.parent.parent))
sys.path.insert(0, str(_PROJ / "experiments"))

from sar_sim.solver.baselines import baseline_b1
from run_moea_3obj_no_physics import moea_solver_no_physics

PROJECT = _PROJ
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "variant_d_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 100, 200
N_SCENARIOS = 5
N_SEEDS = 3
GROUPS = ["S3", "S4"]


def run_one(pkl_path, seed):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    from sar_sim.solver.types import build_agile_instance, precompute_geometry
    gbl = baseline_b1(windows, targets)
    gbl_f1 = max(float(gbl.f1), 1.0)
    t0 = time.time()
    result = moea_solver_no_physics(
        windows, targets,
        population_size=POP, n_generations=GEN,
        n_obj=3, n_ref_dirs=12,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=None, seed=seed, f1_gbl=gbl_f1,
    )
    rt = time.time() - t0
    meta = result.metadata
    return {
        "seed": seed,
        "f1": float(meta.get("f1", 0)),
        "f2": float(meta.get("f2", 0)),
        "f3": float(meta.get("f3", 0)),
        "n_selected": int(meta.get("n_selected", 0)),
        "runtime_s": round(rt, 1),
    }


partial_path = RESULTS_DIR / "full.json"
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
    print(f"\nGroup {group}: {len(pkls)} scenarios x {N_SEEDS} seeds (random-init D)")
    for i, pkl in enumerate(pkls):
        for seed in range(N_SEEDS):
            if (pkl.name, seed) in done:
                print(f"  [{i+1}/{len(pkls)}] {pkl.name} seed{seed} SKIP")
                continue
            print(f"  [{i+1}/{len(pkls)}] {pkl.name} seed{seed}", end=" ", flush=True)
            r = run_one(pkl, seed)
            print(f"f1={r['f1']:.3f} f2={r['f2']:.4f} n={r['n_selected']}")
            runs.append({"scenario": pkl.name, **r})
            json.dump(out, open(partial_path, "w"), indent=2)

summary = {}
for group, rs in all_results.items():
    f1 = np.array([r["f1"] for r in rs])
    f2 = np.array([r["f2"] for r in rs])
    summary[group] = {
        "f1_mean": float(f1.mean()), "f1_std": float(f1.std()),
        "f2_mean": float(f2.mean()), "f2_std": float(f2.std()),
        "n": len(rs),
    }
out["summary"] = summary
json.dump(out, open(partial_path, "w"), indent=2)
print("\n=== SUMMARY (random-init Variant D) ===")
print("Hot-start D f2 ~= 0.594 (low-squint). If random-init D f2 ~= 0.594 -> (i) objective-neutrality. If << 0.594 -> (ii) hot-start residue.")
for g, s in summary.items():
    print(f"  {g}: f1={s['f1_mean']:.3f}+/-{s['f1_std']:.3f}  f2={s['f2_mean']:.4f}+/-{s['f2_std']:.4f}")
print(f"\nSaved: {partial_path}")
