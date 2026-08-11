#!/usr/bin/env python3
"""Regenerate the variant-D (no-physics) random-init control for §6.6.

The previous results/variant_d_random_init/full.json was produced with old code
(git f1a2dd75) and a default-geometry instance (build_agile_instance with
RAAN=0/epoch=0), yielding wrong f2/f3 (~0.55/0.13 instead of the main
experiment's ~0.53/0.45).  This runner calls moea_solver_no_physics with the
scenario's real orbit (from_scenario, correct geometry) and NO G-BL hot start
(random init), matching the main experiment's geometry.

Output: results/variant_d_random_init/full.json
"""
import pickle, json, sys, time, hashlib
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from run_moea_3obj_no_physics import moea_solver_no_physics

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "variant_d_random_init"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT = RESULTS_DIR / "full.json"

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN = 100, 200
N_REF = 12
N_SCENARIOS, N_SEEDS = 5, 3
PLAN = [("S3", 0, 5), ("S4", 0, 5)]


def _pkl_sha1(p: Path) -> str:
    sha = hashlib.sha1()
    with open(p, "rb") as f:
        while c := f.read(8192):
            sha.update(c)
    return sha.hexdigest()


def f1_gbl_for(data):
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    gbl = baseline_b1(data.get("windows", []), data.get("targets", []),
                      max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                      geom_cache=instance.geom_cache, instance=instance)
    return instance, max(float(gbl.f1), 1.0)


def main():
    results = {"S3": [], "S4": []}
    for scale, start, count in PLAN:
        for idx in range(start, start + count):
            pkl = SCENARIOS_DIR / scale / f"{scale}-A_seed{idx:02d}.pkl"
            data = pickle.load(open(pkl, "rb"))
            instance, f1g = f1_gbl_for(data)
            for extra in range(N_SEEDS):
                seed = idx * 100 + extra
                t0 = time.time()
                res = moea_solver_no_physics(
                    data.get("windows", []), data.get("targets", []),
                    population_size=POP, n_generations=GEN, seed=seed,
                    n_ref_dirs=N_REF, n_obj=3, instance=instance, f1_gbl=f1g,
                )
                m = res.metadata
                entry = {
                    "scenario": pkl.name, "seed": idx, "extra_seed": extra,
                    "pkl_sha1": _pkl_sha1(pkl),
                    "f1": float(m.get("f1", 0.0)),
                    "f2": float(m.get("f2", 0.0)),
                    "f3": float(m.get("f3", 0.0)),
                    "n_selected": int(m.get("n_selected", 0)),
                    "runtime_s": round(time.time() - t0, 3),
                }
                results[scale].append(entry)
                print(f"[{scale}-{idx:02d}] x{extra}: f1={entry['f1']:.3f} f2={entry['f2']:.4f} f3={entry['f3']:.4f} n={entry['n_selected']} t={entry['runtime_s']:.0f}s", flush=True)

    summary = {}
    for scale, rows in results.items():
        f1s = np.array([r["f1"] for r in rows]); f2s = np.array([r["f2"] for r in rows])
        summary[scale] = {
            "f1_mean": float(f1s.mean()), "f1_std": float(f1s.std(ddof=1)),
            "f2_mean": float(f2s.mean()), "f2_std": float(f2s.std(ddof=1)),
            "n": len(rows),
        }
    out = {
        "params": {"pop": POP, "gen": GEN, "n_scenarios": N_SCENARIOS, "n_seeds": N_SEEDS,
                   "solver": "moea_nsga3_no_physics (variant D)", "hotstart": "none (random init)",
                   "geometry": "scenario real orbit (from_scenario)"},
        "results": results, "summary": summary,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\n=== SUMMARY ===")
    for scale, s in summary.items():
        print(f"  {scale}: f1={s['f1_mean']:.3f}+/-{s['f1_std']:.3f}  f2={s['f2_mean']:.4f}+/-{s['f2_std']:.4f}  n={s['n']}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
