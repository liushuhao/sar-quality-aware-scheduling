#!/usr/bin/env python3
"""Run G-BL + G-SM baselines on S7/S8 only, append to separate output file."""
import pickle, json, sys, time
from pathlib import Path
from collections import OrderedDict

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import build_agile_instance, precompute_geometry

SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "baselines_S7S8.json"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
GROUPS = ["S7", "S8"]

def _to_dict(r):
    return {k: getattr(r, k, None) for k in ["f1", "f2", "f3", "n_selected", "selected_tasks", "selected_indices", "hv_contrib"]}

def main():
    results = OrderedDict()
    if OUT_PATH.exists():
        with open(OUT_PATH) as f:
            results = OrderedDict(json.load(f))
        print(f"Resuming, {len(results)} existing")
    for group in GROUPS:
        d = SCENARIOS_DIR / group
        pkgs = sorted(d.glob("*.pkl"))
        print(f"\n=== {group}: {len(pkgs)} scenarios ===")
        for pkl in pkgs:
            key = f"{group}/{pkl.name}"
            if key in results:
                continue
            with open(pkl, "rb") as f:
                data = pickle.load(f)
            windows, targets = data.get("windows", []), data.get("targets", [])
            instance = build_agile_instance(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
            precompute_geometry(instance, step_s=10.0)
            t0 = time.time()
            b1 = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, geom_cache=instance.geom_cache, instance=instance)
            t_b1 = time.time() - t0
            t0 = time.time()
            b3 = baseline_b3(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, geom_cache=instance.geom_cache, instance=instance)
            t_b3 = time.time() - t0
            results[key] = {"b1": _to_dict(b1), "b3": _to_dict(b3), "t_b1_s": t_b1, "t_b3_s": t_b3}
            print(f"  {pkl.name}: b1_f1={results[key]['b1']['f1']:.3f} b3_f1={results[key]['b3']['f1']:.3f} ({t_b1:.1f}s/{t_b3:.1f}s)")
            with open(OUT_PATH, "w") as f:
                json.dump(results, f, indent=2)
    print(f"\nDone. Total {len(results)} entries in {OUT_PATH}")

if __name__ == "__main__":
    main()
