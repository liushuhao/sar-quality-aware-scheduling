#!/usr/bin/env python3
"""Random-search control: random task selections vs G-BL, on current scenarios.

Replaces archive/20260712_P1-2_random_search_v2.py, which assumed uniform
priority 5.0 (false for current scenarios: priorities are {1..10}) and indexed
random draws by data n_targets while instance.tasks can be smaller (targets
dropped for lacking any window). Uses real task priorities so f1* is
comparable with the MOEA runs (same f1_gbl normalization).

Output:
  experiments/results/p1-2_random_search/p1-2_s1_random_search.json
"""
import pickle, json, sys, time, hashlib
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.solver.baselines import baseline_b1

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "p1-2_random_search"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
N_SAMPLES = 5000
N_SCENARIOS = 5
RNG_SEED = 42


def _pkl_sha1(p: Path) -> str:
    sha = hashlib.sha1()
    with open(p, "rb") as f:
        while c := f.read(8192):
            sha.update(c)
    return sha.hexdigest()


def main():
    pkls = sorted((SCENARIOS_DIR / "S1").glob("*.pkl"))[:N_SCENARIOS]
    rng = np.random.default_rng(RNG_SEED)
    all_results = {}

    for pkl in pkls:
        with open(pkl, "rb") as f:
            data = pickle.load(f)
        windows = data.get("windows", [])
        targets = data.get("targets", [])

        instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
        precompute_geometry(instance, step_s=10.0)

        gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                          geom_cache=instance.geom_cache, instance=instance)
        f1_gbl = max(float(gbl.f1), 1.0)
        tasks = instance.tasks
        N = instance.N
        prio = np.array([t.priority for t in tasks])

        t0 = time.time()
        f1_star_vals = []
        for _ in range(N_SAMPLES):
            n_select = rng.integers(1, N + 1)
            sel = rng.choice(N, size=n_select, replace=False)
            f1_star_vals.append(float(prio[sel].sum()) / f1_gbl)
        rt = time.time() - t0

        all_results[pkl.name] = {
            "scenario": pkl.name, "n": N, "n_targets_data": len(targets),
            "f1_gbl": f1_gbl, "n_samples": N_SAMPLES, "runtime_s": round(rt, 3),
            "pkl_sha1": _pkl_sha1(pkl),
            "f1_star_best": float(np.max(f1_star_vals)),
            "f1_star_mean": float(np.mean(f1_star_vals)),
            "f1_star_std": float(np.std(f1_star_vals)),
            "f1_star_p90": float(np.percentile(f1_star_vals, 90)),
        }
        r = all_results[pkl.name]
        print(f"{pkl.name}: n={N} best={r['f1_star_best']:.3f} p90={r['f1_star_p90']:.3f} mean={r['f1_star_mean']:.3f} t={rt:.1f}s", flush=True)

    out = {"params": {"n_samples": N_SAMPLES, "scenarios": f"S1-A_seed00..{N_SCENARIOS-1:02d} ({N_SCENARIOS})",
                      "rng_seed": RNG_SEED, "priority_basis": "real task priorities", "sleuth": "current scenarios"},
           "results": all_results,
           "summary": {
               "f1_star_best_mean": float(np.mean([r["f1_star_best"] for r in all_results.values()])),
               "f1_star_best_std": float(np.std([r["f1_star_best"] for r in all_results.values()], ddof=1)),
               "f1_star_p90_mean": float(np.mean([r["f1_star_p90"] for r in all_results.values()])),
               "f1_star_p90_std": float(np.std([r["f1_star_p90"] for r in all_results.values()], ddof=1)),
               "f1_star_mean_mean": float(np.mean([r["f1_star_mean"] for r in all_results.values()])),
               "f1_star_mean_std": float(np.std([r["f1_star_mean"] for r in all_results.values()], ddof=1)),
           }}
    out_path = RESULTS_DIR / "p1-2_s1_random_search.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), indent=2)
    print("\n=== SUMMARY (5 S1 scenarios) ===")
    s = out["summary"]
    print(f"  Mean f1*: {s['f1_star_mean_mean']:.3f}+/-{s['f1_star_mean_std']:.3f}")
    print(f"  P90 f1*:  {s['f1_star_p90_mean']:.3f}+/-{s['f1_star_p90_std']:.3f}")
    print(f"  Best f1*: {s['f1_star_best_mean']:.3f}+/-{s['f1_star_best_std']:.3f}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
