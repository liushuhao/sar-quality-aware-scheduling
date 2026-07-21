#!/usr/bin/env python3
"""Baselines runner V4: G-BL + G-SM with geom_cache → correct f3.

Fixes P0-1: passes geom_cache + instance to baseline_b1 so
_compute_f3_posthoc doesn't short-circuit to 0.0.

Output: experiments/results/baselines_200.json
  { "S1/S1-A_seed00.pkl": {"b1": {f1,f2,f3,...}, "b3": {...}}, ... }
"""
import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import build_agile_instance, precompute_geometry

SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "baselines_200.json"

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
# Only S1-S4 are in SPEC v4 paper scope
GROUPS = ["S1", "S2", "S3", "S4"]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True
        ).strip()[:8]
    except Exception:
        return "unknown"


def _pkl_sha1(pkl_path: Path) -> str:
    sha = hashlib.sha1()
    with open(pkl_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def get_all_scenarios() -> OrderedDict:
    groups = OrderedDict()
    for group in GROUPS:
        d = SCENARIOS_DIR / group
        if d.is_dir():
            pkgs = sorted(d.glob("*.pkl"))
            if pkgs:
                groups[group] = pkgs
    return groups


def run_both_baselines(windows, targets, instance, geom_cache) -> dict:
    """Run G-BL (b1) and G-SM (b3) with full geom_cache + instance."""
    t0 = time.time()
    b1 = baseline_b1(
        windows, targets,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        geom_cache=geom_cache,
        instance=instance,
    )
    t1 = time.time() - t0

    t0 = time.time()
    b3 = baseline_b3(
        windows, targets,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        geom_cache=geom_cache,
        instance=instance,
    )
    t3 = time.time() - t0

    n = len(targets)
    f1_gbl = max(float(b1.f1), 1.0)  # G-BL f1 as reference
    return {
        "b1": {
            "f1": 1.0,  # normalized (reference = itself)
            "f1_raw": float(b1.f1),
            "f1_gbl": f1_gbl,
            "f2": float(b1.f2),
            "f3": float(b1.metadata.get("f3", 0.0)),
            "n_selected": int(b1.metadata.get("n_selected", 0)),
            "n_targets": n,
            "runtime_s": round(t1, 4),
        },
        "b3": {
            "f1": float(b3.f1) / f1_gbl,  # normalized
            "f1_raw": float(b3.f1),
            "f1_gbl": f1_gbl,
            "f2": float(b3.f2),
            "f3": float(b3.metadata.get("f3", 0.0)),
            "n_selected": int(b3.metadata.get("n_selected", 0)),
            "n_targets": n,
            "runtime_s": round(t3, 4),
        },
    }


def main():
    # ── Backup existing if present ──
    if OUT_PATH.exists():
        bak = RESULTS_DIR / "baselines_200.json.bak_pre_f3fix"
        import shutil
        shutil.copy2(OUT_PATH, bak)
        print(f"Backed up existing to {bak.name}")

    all_groups = get_all_scenarios()
    total = sum(len(f) for f in all_groups.values())
    print(f"Baselines V4: {len(all_groups)} groups, {total} total scenarios")
    print(f"  G-BL + G-SM with geom_cache → correct f3")
    print(f"  Output: {OUT_PATH}\n")

    results = OrderedDict()
    n_done = 0
    
    # ── Resume: load existing partial results ──
    if OUT_PATH.exists():
        try:
            with open(OUT_PATH) as f:
                existing = json.load(f)
            if isinstance(existing, dict) and len(existing) > 0:
                results = OrderedDict(existing)
                n_done = len([v for v in results.values() if "b1" in v])
                print(f"Resuming: {n_done} already completed")
        except Exception:
            pass  # corrupt file, start fresh

    for group_name, files in all_groups.items():
        print(f"\n{'='*60}")
        print(f"=== {group_name}: {len(files)} scenarios ===")
        print(f"{'='*60}")

        for fpath in files:
            key = f"{group_name}/{fpath.name}"
            if key in results and "b1" in results.get(key, {}):
                continue  # already done
            try:
                with open(fpath, "rb") as f:
                    data = pickle.load(f)

                windows = data.get("windows", [])
                targets = data.get("targets", [])

                # Extract altitude from satellite dict
                sat = data.get("satellite", {})
                alt_km = float(sat.get("altitude_km", 693.0))
                alt_m = alt_km * 1000.0

                # Build instance + precompute geometry
                instance = build_agile_instance(
                    windows, targets,
                    max_slew_rate=SLEW_RATE,
                    settle_time=SETTLE_TIME,
                    altitude_m=alt_m,
                )
                precompute_geometry(instance, step_s=10.0)

                result = run_both_baselines(
                    windows, targets, instance, instance.geom_cache,
                )
                results[key] = result
                n_done += 1

                b1f3 = result["b1"]["f3"]
                b3f3 = result["b3"]["f3"]
                marker = " <<< FIXED" if b1f3 > 0.01 else " <<< STILL ZERO"
                if n_done <= 5 or n_done % 20 == 0 or b1f3 > 0.01:
                    print(f"  [{n_done}/{total}] {fpath.name}: "
                          f"b1 f1={result['b1']['f1']:.0f} f3={b1f3:.2f}{marker} | "
                          f"b3 f1={result['b3']['f1']:.0f} f3={b3f3:.2f}")

                # ── Incremental save (safe against SIGHUP) ──
                with open(OUT_PATH, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, default=str)

            except Exception as e:
                print(f"  [ERR] {fpath.name}: {e}")
                import traceback
                traceback.print_exc()
                results[key] = {"error": str(e)}
                continue

    # ── Save ──
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    # ── Summary ──
    b1_f3s = [v["b1"]["f3"] for v in results.values() if "b1" in v]
    b3_f3s = [v["b3"]["f3"] for v in results.values() if "b3" in v]
    n_fixed = sum(1 for x in b1_f3s if x > 0.01)

    print(f"\n{'='*60}")
    print(f"Baselines V4 complete!")
    print(f"  Scenarios: {n_done}/{total}")
    print(f"  G-BL f3 fixed: {n_fixed}/{len(b1_f3s)}")
    print(f"  G-BL f3 mean: {np.mean(b1_f3s):.2f} ± {np.std(b1_f3s):.2f}")
    print(f"  G-SM f3 mean: {np.mean(b3_f3s):.2f} ± {np.std(b3_f3s):.2f}")
    print(f"  Output: {OUT_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
