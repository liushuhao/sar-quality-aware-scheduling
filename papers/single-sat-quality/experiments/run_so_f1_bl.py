#!/usr/bin/env python3
"""Run GA-P-BL (GA-P with G-BL hot-start) on all 300 scenarios.

Runs G-BL first to seed the GA population, then runs GA-P-BL to refine f1.
Saves incremental progress to experiments/results/b2_profit_bl/_progress.json.
"""

import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.solver.so_f1 import b2_profit_solver_bl_seeded

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "b2_profit_bl"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GA_PARAMS = {"population_size": 100, "n_generations": 200}
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

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

GIT_COMMIT = _git_commit()

def get_all_scenarios():
    groups = OrderedDict()
    for group_name in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        d = SCENARIOS_DIR / group_name
        if d.is_dir():
            pkgs = sorted(d.glob("*.pkl"))
            if pkgs:
                groups[group_name] = pkgs
    return groups

def run_one(pkl_path: Path) -> dict:
    pkl_sha1 = _pkl_sha1(pkl_path)
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)

    # Extract orbit parameters from scenario so GeomCache matches visibility windows
    sat = data.get("satellite", {})
    config = data.get("config", {})
    orbit_inclination_rad = np.radians(sat.get("inclination_deg", 97.8))
    orbit_raan_rad = np.radians(sat.get("ltan_h", 6.0) * 15.0)
    t_start = config.get("t_start")
    orbit_epoch_s = t_start.timestamp() if hasattr(t_start, "timestamp") else float(t_start)

    # Compute G-BL reference f1 for normalization.
    # IMPORTANT: build the instance first and pass it to baseline_b1 so the
    # G-BL schedule and f1 are computed with the same C2 transition model
    # and target set as the GA-P-BL solver.  Calling baseline_b1(windows,
    # targets) without an instance yields a different (incomparable) f1
    # because it includes targets filtered out during build_agile_instance
    # and uses the legacy phi-diff C2 model.
    from sar_sim.solver.baselines import baseline_b1
    from sar_sim.solver.types import build_agile_instance, precompute_geometry
    instance = build_agile_instance(
        windows, targets,
        orbit_raan_rad=orbit_raan_rad,
        orbit_epoch_s=orbit_epoch_s,
        orbit_inclination_rad=orbit_inclination_rad,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
    )
    precompute_geometry(instance, step_s=10.0)
    gbl = baseline_b1(windows, targets, instance=instance)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    gbl_f1 = 0.0
    seen = set()
    for obs in gbl.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx and tid not in seen:
            seen.add(tid)
            gbl_f1 += instance.tasks[target_to_idx[tid]].priority
    f1_gbl = max(gbl_f1, 1.0)

    t0 = time.time()
    result = b2_profit_solver_bl_seeded(
        windows, targets,
        population_size=GA_PARAMS["population_size"],
        n_generations=GA_PARAMS["n_generations"],
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        orbit_raan_rad=orbit_raan_rad,
        orbit_epoch_s=orbit_epoch_s,
        orbit_inclination_rad=orbit_inclination_rad,
    )
    rt = time.time() - t0

    meta = result.metadata
    f1_raw = float(meta.get("f1", 0.0))
    return {
        "seed": seed,
        "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": f1_raw / f1_gbl if f1_gbl > 0 else f1_raw,  # normalized
        "f1_raw": f1_raw,
        "f1_gbl": f1_gbl,
        "f2": float(meta.get("f2", 0.0)),
        "f3": float(meta.get("f3", 0.0)),
        "runtime_s": round(rt, 3),
        "n_frontier": 1,
        "solver": "b2_profit_bl_seeded",
        "solver_version": GIT_COMMIT,
        "params": dict(GA_PARAMS),
        "pkl_sha1": pkl_sha1,
        "selected": meta.get("selected", []),
        "t_actuals": meta.get("t_actuals", []),
        "phis_off_nadir": meta.get("phis_off_nadir", []),
        "constraint_feasible": meta.get("constraint_feasible", True),
        "n_constraints_failed": meta.get("n_constraints_failed", 0),
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GA-P-BL: GA-P with G-BL hot-start")
    parser.add_argument("--groups", nargs="+", help="Groups to process (S1-S6)")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    args = parser.parse_args()

    all_groups = get_all_scenarios()
    if args.groups:
        groups = {k: v for k, v in all_groups.items() if k in args.groups}
    else:
        groups = all_groups

    total_scenarios = sum(len(files) for files in groups.values())
    print(f"GA-P-BL experiment: {len(groups)} groups, {total_scenarios} total")
    print(f"  Params: pop={GA_PARAMS['population_size']}, gen={GA_PARAMS['n_generations']}")
    print(f"  git_commit: {GIT_COMMIT}")
    print(f"  Output: {RESULTS_DIR / '_progress.json'}\n")

    progress_file = RESULTS_DIR / "_progress.json"
    if args.resume and progress_file.exists():
        with open(progress_file) as f:
            progress = json.load(f)
        completed = progress.get("completed", {})
        print(f"Resuming: {len(completed)} already completed")
    else:
        progress = {"completed": OrderedDict()}
        completed = progress["completed"]

    total_run = len(completed)
    for group_name, files in groups.items():
        for fpath in files:
            key = f"{group_name}/{fpath.name}"
            if key in completed:
                continue
            try:
                result = run_one(fpath)
                if result is not None:
                    completed[key] = result
                    total_run += 1
                if total_run <= 3 or total_run % 10 == 0:
                    print(f"  [{total_run}/{total_scenarios}] {fpath.name}: "
                          f"f1={result['f1']:.1f} n={result['n_selected']} "
                          f"t={result['runtime_s']:.1f}s")
            except Exception as e:
                print(f"  [ERR] {fpath.name}: {e}")
                import traceback; traceback.print_exc()
                continue
            progress["completed"] = completed
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2, default=str)

    print(f"\nGA-P-BL experiment complete! {len(completed)}/{total_scenarios}")

if __name__ == "__main__":
    main()
