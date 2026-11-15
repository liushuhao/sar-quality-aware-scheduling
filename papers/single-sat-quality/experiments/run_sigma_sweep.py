#!/usr/bin/env python3
"""Sigma sensitivity sweep: MOEA-2 + MOEA-3 on S1-S4 with σ ∈ {0.1, 0.3, 0.5, 0.7}.

Usage:
  python papers/single-sat-quality/experiments/run_sigma_sweep.py
  python papers/single-sat-quality/experiments/run_sigma_sweep.py --groups S3 S4
  python papers/single-sat-quality/experiments/run_sigma_sweep.py --sigmas 0.1 0.7

Output:
  experiments/results/sigma_sweep/
    sigma_0.1/moea_2obj/_progress.json
    sigma_0.1/moea_3obj/_progress.json
    sigma_0.3/moea_2obj/_progress.json
    ...
    sweep_summary.json         # aggregated across all sigma values
"""

import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT.parent.parent  # planning paper/
sys.path.insert(0, str(REPO_ROOT / "src"))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "sigma_sweep"


def _atomic_write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
SOLVER_SEED = 42  # fixed seed for reproducibility across sigma values

# Default params matching the paper
MOEA_PARAMS = {
    "population_size": 100,
    "n_generations": 200,
    "n_ref_dirs": 12,
}

SIGMA_VALUES = [0.1, 0.3, 0.5, 0.7]
SOLVERS = [
    {"name": "moea_2obj", "n_obj": 2},
    {"name": "moea_3obj", "n_obj": 3},
]
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


def get_all_scenarios():
    groups = OrderedDict()
    for group in GROUPS:
        d = SCENARIOS_DIR / group
        if d.is_dir():
            pkgs = sorted(d.glob("*.pkl"))
            if pkgs:
                groups[group] = pkgs
    return groups


def build_hotstart(windows, targets, instance):
    """Encode G-BL solution as a 2N chromosome."""
    gbl = baseline_b1(windows, targets, max_slew_rate=instance.max_slew_rate,
                      settle_time=instance.settle_time,
                      geom_cache=instance.geom_cache, instance=instance)
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


def run_one(pkl_path: Path, sigma: float, n_obj: int) -> dict:
    """Run a single solver scenario with given sigma and n_obj."""
    pkl_sha1 = _pkl_sha1(pkl_path)

    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)

    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    scenario_seed = data.get("seed", 0)

    # Build instance from the scenario's real orbit params (inclination/RAAN/
    # epoch).  build_agile_instance defaults (RAAN=0, epoch=0) would misalign the
    # ECI->ECEF geometry and give wrong incidence/squint, breaking the f2/f3
    # values and the low-squint convergence seen in the main experiment.
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)

    # Build hot-start
    hotstart = build_hotstart(windows, targets, instance)

    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=MOEA_PARAMS["population_size"],
        n_generations=MOEA_PARAMS["n_generations"],
        n_obj=n_obj,
        n_ref_dirs=MOEA_PARAMS["n_ref_dirs"],
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        hotstart_individual=hotstart,
        hotstart_sigma=sigma,
        instance=instance,
        seed=SOLVER_SEED,
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
        "scenario_seed": scenario_seed,
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
        "n_obj": n_obj,
        "sigma": sigma,
        "solver_version": _git_commit(),
        "pkl_sha1": pkl_sha1,
    }


def run_sigma_sweep(sigma_values, groups, solvers, max_scenarios=0):
    """Run sigma sweep across all combinations."""
    all_scenarios = get_all_scenarios()
    # Filter groups and optionally limit scenarios
    filtered = {}
    for g, files in all_scenarios.items():
        if g in groups:
            if max_scenarios > 0:
                filtered[g] = files[:max_scenarios]
            else:
                filtered[g] = files

    total = 0
    for sigma in sigma_values:
        for solver in solvers:
            for gname, files in filtered.items():
                total += len(files)

    print(f"Sigma sweep: {len(sigma_values)} sigma × {len(solvers)} solvers × {len(filtered)} groups = {total} runs")
    print(f"  Sigma values: {sigma_values}")
    print(f"  Solvers: {[s['name'] for s in solvers]}")
    print(f"  Groups: {list(filtered.keys())}")
    print(f"  Solver seed: {SOLVER_SEED}")
    print(f"  Output: {RESULTS_DIR}\n")

    for sigma in sigma_values:
        for solver in solvers:
            solver_name = solver["name"]
            n_obj = solver["n_obj"]
            run_dir = RESULTS_DIR / f"sigma_{sigma}" / solver_name
            run_dir.mkdir(parents=True, exist_ok=True)
            progress_file = run_dir / "_progress.json"

            # Load existing progress
            if progress_file.exists():
                with open(progress_file) as f:
                    progress = json.load(f)
                completed = progress.get("completed", {})
                print(f"[σ={sigma}, {solver_name}] Resuming: {len(completed)} completed")
            else:
                progress = {"completed": OrderedDict()}
                completed = progress["completed"]

            group_counts = {}
            for gname, files in filtered.items():
                group_counts[gname] = len(files)
                print(f"\n  [σ={sigma}, {solver_name}] === {gname}: {len(files)} scenarios ===")

                for fpath in files:
                    key = f"{gname}/{fpath.name}"
                    if key in completed and completed[key].get("pkl_sha1") == _pkl_sha1(fpath):
                        continue

                    try:
                        result = run_one(fpath, sigma, n_obj)
                        if result is not None:
                            completed[key] = result
                        else:
                            continue
                    except Exception as e:
                        print(f"    [ERR] {fpath.name}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue

                    # Incremental save
                    progress["completed"] = completed
                    _atomic_write_json(progress_file, progress)

                # Per-group summary
                grp_keys = [k for k in completed if k.startswith(gname + "/")]
                if grp_keys:
                    f1s = [completed[k]["f1_raw"] for k in grp_keys]
                    f2s = [completed[k]["f2"] for k in grp_keys]
                    f3s = [completed[k].get("f3", 0) for k in grp_keys]
                    ns = [completed[k]["n_selected"] for k in grp_keys]
                    rts = [completed[k]["runtime_s"] for k in grp_keys]
                    print(f"    -> {gname}: f1={np.mean(f1s):.0f}±{np.std(f1s):.0f}, "
                          f"f2={np.mean(f2s):.3f}±{np.std(f2s):.3f}, "
                          f"f3={np.mean(f3s):.4f}±{np.std(f3s):.4f}, "
                          f"n={np.mean(ns):.1f}±{np.std(ns):.1f}, "
                          f"t={np.mean(rts):.0f}s")

            # Final save for this sigma/solver
            progress["stats"] = {
                "sigma": sigma,
                "solver": solver_name,
                "n_obj": n_obj,
                "groups": list(filtered.keys()),
                "total_scenarios": sum(group_counts.values()),
                "completed": len(completed),
                "params": MOEA_PARAMS,
                "solver_seed": SOLVER_SEED,
                "git_commit": _git_commit(),
            }
            _atomic_write_json(progress_file, progress)
            print(f"  [σ={sigma}, {solver_name}] Done: {len(completed)}/{sum(group_counts.values())}\n")

    # Aggregate summary
    aggregate_summary()
    print("Sigma sweep complete!")


def aggregate_summary():
    """Aggregate results across all sigma values into sweep_summary.json."""
    from collections import defaultdict

    summary = defaultdict(lambda: defaultdict(list))
    all_data = []

    for sigma in SIGMA_VALUES:
        for solver in SOLVERS:
            solver_name = solver["name"]
            progress_file = RESULTS_DIR / f"sigma_{sigma}" / solver_name / "_progress.json"
            if not progress_file.exists():
                continue
            with open(progress_file) as f:
                progress = json.load(f)
            for key, result in progress.get("completed", {}).items():
                group = key.split("/")[0]
                entry = {
                    "sigma": sigma,
                    "solver": solver_name,
                    "group": group,
                    "scenario": key,
                    "f1_raw": result["f1_raw"],
                    "f2": result["f2"],
                    "f3": result.get("f3", 0),
                    "n_selected": result["n_selected"],
                    "runtime_s": result["runtime_s"],
                    "n_targets": result["n_targets"],
                }
                all_data.append(entry)
                summary[(sigma, solver_name, group)]["f1_raw"].append(result["f1_raw"])
                summary[(sigma, solver_name, group)]["f2"].append(result["f2"])
                summary[(sigma, solver_name, group)]["f3"].append(result.get("f3", 0))
                summary[(sigma, solver_name, group)]["n_selected"].append(result["n_selected"])

    # Build aggregator table
    aggregator = []
    for (sigma, solver, group), vals in sorted(summary.items()):
        aggregator.append({
            "sigma": sigma,
            "solver": solver,
            "group": group,
            "n": len(vals["f1_raw"]),
            "f1_mean": round(np.mean(vals["f1_raw"]), 1),
            "f1_std": round(np.std(vals["f1_raw"]), 1),
            "f2_mean": round(np.mean(vals["f2"]), 4),
            "f2_std": round(np.std(vals["f2"]), 4),
            "f3_mean": round(np.mean(vals["f3"]), 4),
            "f3_std": round(np.std(vals["f3"]), 4),
            "n_selected_mean": round(np.mean(vals["n_selected"]), 1),
            "n_selected_std": round(np.std(vals["n_selected"]), 1),
        })

    # Compute f2-f3 correlation per sigma×solver×group
    correlations = []
    for (sigma, solver, group), vals in sorted(summary.items()):
        if len(vals["f2"]) >= 3:
            r = np.corrcoef(vals["f2"], vals["f3"])[0, 1]
        else:
            r = None
        correlations.append({
            "sigma": sigma,
            "solver": solver,
            "group": group,
            "n": len(vals["f2"]),
            "r_f2f3": round(r, 4) if r is not None else None,
        })

    sweep_summary = {
        "sigma_values": SIGMA_VALUES,
        "solvers": [s["name"] for s in SOLVERS],
        "groups": GROUPS,
        "solver_seed": SOLVER_SEED,
        "params": MOEA_PARAMS,
        "git_commit": _git_commit(),
        "aggregator": aggregator,
        "correlations": correlations,
        "n_total": len(all_data),
    }

    summary_path = RESULTS_DIR / "sweep_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(sweep_summary, f, indent=2)
    print(f"\nAggregate summary written to {summary_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sigma sensitivity sweep")
    parser.add_argument("--groups", nargs="+", default=GROUPS, help="Scenario groups (default: S1 S2 S3 S4)")
    parser.add_argument("--sigmas", nargs="+", type=float, default=SIGMA_VALUES, help="Sigma values (default: 0.1 0.3 0.5 0.7)")
    parser.add_argument("--solvers", nargs="+", default=["moea_2obj", "moea_3obj"], help="Solvers to run")
    parser.add_argument("--max-scenarios", type=int, default=0, help="Max scenarios per group (0=all)")
    args = parser.parse_args()

    valid_solvers = [s for s in SOLVERS if s["name"] in args.solvers]

    run_sigma_sweep(args.sigmas, args.groups, valid_solvers, args.max_scenarios)

    # Print summary table
    summary_path = RESULTS_DIR / "sweep_summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        print("\n=== AGGREGATE SUMMARY ===")
        print(f"{'sigma':>5} {'solver':>12} {'group':>5} {'f1_mean':>8} {'f2_mean':>8} {'f3_mean':>8} {'n_sel':>6} {'r_f2f3':>8}")
        for a in summary["aggregator"]:
            print(f"{a['sigma']:>5.1f} {a['solver']:>12} {a['group']:>5} {a['f1_mean']:>8.0f} {a['f2_mean']:>8.4f} {a['f3_mean']:>8.4f} {a['n_selected_mean']:>6.1f}  --")
        for c in summary["correlations"]:
            r = f"{c['r_f2f3']:>8.4f}" if c['r_f2f3'] is not None else "    N/A"
            print(f"{c['sigma']:>5.1f} {c['solver']:>12} {c['group']:>5} {'':>8} {'':>8} {'':>8} {'':>6} {r}")


if __name__ == "__main__":
    main()