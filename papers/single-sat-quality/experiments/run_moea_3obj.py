#!/usr/bin/env python3
"""Phase 7c: Run MOEA-3obj (MOEA-3: f1 profit + f2 geometric res + f3 NESZ radiometric).

Uses NSGA-III with population=100, generations=200, n_obj=3.
Saves incremental progress to experiments/results/moea_3obj/_progress.json.
"""
import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sar_sim.solver.moea import moea_solver

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "moea_3obj"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MOEA_PARAMS = {
    "population_size": 100,
    "n_generations": 200,
    "n_obj": 3,
}
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
    for group in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        d = SCENARIOS_DIR / group
        if d.is_dir():
            pkgs = sorted(d.glob("*.pkl"))
            if pkgs:
                groups[group] = pkgs
    return groups

def run_one(pkl_path: Path) -> dict:
    pkl_sha1 = _pkl_sha1(pkl_path)

    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)

    t0 = time.time()
    # ── Hot-start: encode G-BL solution as chromosome ──────────────────
    hotstart = None
    from sar_sim.solver.baselines import baseline_b1
    from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
    gbl = baseline_b1(windows, targets)
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
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
    if seen:
        hotstart = x0

    result = moea_solver(
        windows, targets,
        population_size=MOEA_PARAMS["population_size"],
        n_generations=MOEA_PARAMS["n_generations"],
        n_obj=MOEA_PARAMS["n_obj"],
        n_ref_dirs=12,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        hotstart_individual=hotstart,
        instance=instance,
    )
    rt = time.time() - t0

    meta = result.metadata
    f1_norm = float(meta.get("f1", 0.0))
    f1_raw = float(meta.get("f1_raw", 0.0))
    f1_gbl = float(meta.get("f1_gbl", 1.0))
    f2 = float(meta.get("f2", 0.0))
    f3 = float(meta.get("f3", 0.0))
    n_selected = int(meta.get("n_selected", 0))

    raw_frontier = meta.get("frontier", [])
    frontier_safe = []
    for sol in raw_frontier:
        entry = {
            "f1": float(sol.get("f1", 0)),
            "f2": float(sol.get("f2", 0)),
            "f3": float(sol.get("f3", 0)),
            "n_tasks": int(sol.get("n_tasks", 0)),
        }
        frontier_safe.append(entry)

    return {
        "seed": seed,
        "n_targets": n_targets,
        "n_selected": n_selected,
        "f1": f1_norm,
        "f1_raw": f1_raw,
        "f1_gbl": f1_gbl,
        "f2": f2,
        "f3": f3,
        "runtime_s": round(rt, 3),
        "n_frontier": len(frontier_safe),
        "frontier_f1": [s["f1"] for s in frontier_safe],
        "frontier_f2": [s["f2"] for s in frontier_safe],
        "frontier_f3": [s["f3"] for s in frontier_safe],
        "n_obj": 3,
        "solver": "c2_moea_3obj",
        "solver_version": GIT_COMMIT,
        "params": dict(MOEA_PARAMS),
        "pkl_sha1": pkl_sha1,
        "selected": meta.get("selected", []),
        "t_actuals": meta.get("t_actuals", []),
        "phis_off_nadir": meta.get("phis_off_nadir", []),
        "constraint_feasible": bool(meta.get("constraint_feasible", True)),
        "n_constraints_failed": int(meta.get("n_constraints_failed", 0)),
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", nargs="+", help="Groups to process")
    parser.add_argument("--resume", action="store_true", default=True,
                        help="Resume from existing progress (default: True)")
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Start fresh")
    args = parser.parse_args()

    all_groups = get_all_scenarios()
    if args.groups:
        groups = {k: v for k, v in all_groups.items() if k in args.groups}
    else:
        groups = all_groups

    total_scenarios = sum(len(files) for files in groups.values())
    print(f"MOEA-3obj experiment: {len(groups)} groups, {total_scenarios} total scenarios")
    print(f"  Objectives: f1 (profit) + f2 (geometric res) + f3 (NESZ radiometric)")
    print(f"  Params: pop={MOEA_PARAMS['population_size']}, "
          f"gen={MOEA_PARAMS['n_generations']}, n_obj={MOEA_PARAMS['n_obj']}")
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
    total_errors = 0
    group_counts = {}

    for group_name, files in groups.items():
        group_counts[group_name] = len(files)
        print(f"\n{'='*60}")
        print(f"=== {group_name}: {len(files)} scenarios ===")
        print(f"{'='*60}")

        for fpath in files:
            key = f"{group_name}/{fpath.name}"
            if key in completed:
                continue

            try:
                result = run_one(fpath)
                if result is not None:
                    completed[key] = result
                    total_run += 1
                else:
                    total_errors += 1
                    continue

                if total_run <= 3 or total_run % 10 == 0:
                    print(f"  [{total_run}/{total_scenarios}] {fpath.name}: "
                          f"f1={result['f1_raw']:.0f}, f2={result['f2']:.2f}, "
                          f"f3={result['f3']:.4f}, "
                          f"n={result['n_selected']}, "
                          f"frontier={result['n_frontier']}, "
                          f"t={result['runtime_s']:.1f}s")
            except Exception as e:
                print(f"  [ERR] {fpath.name}: {e}")
                total_errors += 1
                import traceback
                traceback.print_exc()
                continue

            progress["completed"] = completed
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2, default=str)

        grp_keys = [k for k in completed if k.startswith(group_name + "/")]
        if grp_keys:
            f1s = [completed[k]["f1_raw"] for k in grp_keys]
            f2s = [completed[k]["f2"] for k in grp_keys]
            f3s = [completed[k].get("f3", 0) for k in grp_keys]
            ns = [completed[k]["n_selected"] for k in grp_keys]
            rts = [completed[k]["runtime_s"] for k in grp_keys]
            print(f"  -> {group_name} summary ({len(grp_keys)}/{group_counts[group_name]}):")
            print(f"     f1={np.mean(f1s):.1f}+-{np.std(f1s):.1f}, "
                  f"f2={np.mean(f2s):.2f}+-{np.std(f2s):.2f}, "
                  f"f3={np.mean(f3s):.4f}+-{np.std(f3s):.4f}, "
                  f"n={np.mean(ns):.1f}+-{np.std(ns):.1f}, "
                  f"t={np.mean(rts):.1f}s")

    progress["stats"] = {
        "total_scenarios": total_scenarios,
        "completed": len(completed),
        "errors": total_errors,
        "params": MOEA_PARAMS,
        "git_commit": GIT_COMMIT,
    }
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)

    print(f"\n{'='*60}")
    print(f"MOEA-3obj experiment complete!")
    print(f"  Completed: {len(completed)}/{total_scenarios}")
    print(f"  Errors: {total_errors}")
    print(f"  Results: {progress_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
