#!/usr/bin/env python3
"""Run G-BL + G-SM baselines on S7/S8 only, append to separate output file."""
import pickle, json, sys, time
from pathlib import Path
from collections import OrderedDict

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "baselines_S7S8.json"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
GROUPS = ["S7", "S8"]

def _to_dict(r, f1_gbl: float, n_targets: int, runtime_s: float, normalized_f1: float) -> dict:
    """Build result dict aligned with baselines_200.json schema.

    f3 / n_selected live in r.metadata (NOT as direct attributes), so they
    must be extracted via metadata.get(...). The previous _to_dict used
    getattr(r, 'f3', None) which silently returned None for every scenario.
    """
    f1_raw = float(r.f1)
    return {
        "f1": normalized_f1,            # normalized to G-BL reference
        "f1_raw": f1_raw,
        "f1_gbl": f1_gbl,
        "f2": float(r.f2),
        "f3": float(r.metadata.get("f3", 0.0)),
        "n_selected": int(r.metadata.get("n_selected", 0)),
        "n_targets": n_targets,
        "runtime_s": round(runtime_s, 4),
    }

def main():
    results = OrderedDict()
    if OUT_PATH.exists():
        with open(OUT_PATH) as f:
            results = OrderedDict(json.load(f))
        # Drop any entries whose b1.f3 is None (legacy bug from old _to_dict)
        bad = [k for k, v in results.items() if "b1" not in v or v["b1"].get("f3") is None]
        if bad:
            print(f"Dropping {len(bad)} entries with None f3 (legacy bug)")
            for k in bad:
                del results[k]
        print(f"Resuming, {len(results)} valid existing")
    for group in GROUPS:
        d = SCENARIOS_DIR / group
        pkgs = sorted(d.glob("*.pkl"))
        print(f"\n=== {group}: {len(pkgs)} scenarios ===")
        for pkl in pkgs:
            key = f"{group}/{pkl.name}"
            if key in results and "b1" in results[key] and results[key]["b1"].get("f3") is not None:
                continue
            with open(pkl, "rb") as f:
                data = pickle.load(f)
            windows, targets = data.get("windows", []), data.get("targets", [])
            n_targets = len(targets)
            instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
            precompute_geometry(instance, step_s=10.0)
            t0 = time.time()
            b1 = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, geom_cache=instance.geom_cache, instance=instance)
            t_b1 = time.time() - t0
            t0 = time.time()
            b3 = baseline_b3(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, geom_cache=instance.geom_cache, instance=instance)
            t_b3 = time.time() - t0
            f1_gbl = max(float(b1.f1), 1.0)
            results[key] = {
                "b1": _to_dict(b1, f1_gbl, n_targets, t_b1, 1.0),       # G-BL is the reference
                "b3": _to_dict(b3, f1_gbl, n_targets, t_b3, float(b3.f1) / f1_gbl),
            }
            print(f"  {pkl.name}: b1_f1={results[key]['b1']['f1_raw']:.0f} f3={results[key]['b1']['f3']:.2f} | "
                  f"b3_f1={results[key]['b3']['f1_raw']:.0f} f3={results[key]['b3']['f3']:.2f} "
                  f"({t_b1:.1f}s/{t_b3:.1f}s)")
            with open(OUT_PATH, "w") as f:
                json.dump(results, f, indent=2)
    print(f"\nDone. Total {len(results)} entries in {OUT_PATH}")

if __name__ == "__main__":
    main()
