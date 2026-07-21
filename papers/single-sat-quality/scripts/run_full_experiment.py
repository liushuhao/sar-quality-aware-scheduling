"""
Phase 4.2 Full Experiment Runner: MOEA + B1 + B2 on all 300 scenarios (S1-S6).

Handles both legacy directories (small/medium/large) and new S4/S5/S6 groups.
Skips already-completed scenarios (tracked in _progress.json).
Saves progress after each scenario for crash-resilience.
"""
import pickle, json, time, sys, os, traceback
from pathlib import Path
from datetime import datetime
import numpy as np
PROJECT = Path(__file__).resolve().parent

# --- Paths ---
SCENARIO_DIR = Path(r"PROJECT / "experiments\scenarios"")
RESULTS_DIR = Path(r"PROJECT / "experiments\results"")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

PROGRESS_FILE = RESULTS_DIR / "_progress.json"
SOLVERS = ["moea", "b1", "b2"]

# --- Progress persistence ---
def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            try:
                return json.load(f)
            except:
                return {"completed": {}}
    return {"completed": {}}

def save_progress(progress):
    tmp = str(PROGRESS_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(progress, f, indent=2)
    os.replace(tmp, PROGRESS_FILE)  # atomic on Windows

# --- Solver wrappers ---
# Reuse EARTH_R and ORBIT_ALT from baselines runner
EARTH_R = 6378137.0
ORBIT_ALT = 600_000.0

def run_moea(windows, targets, seed):
    from sar_sim.solver.moea import moea_solver
    t0 = time.perf_counter()
    result = moea_solver(windows, targets, population_size=100, n_generations=200,
                         seed=seed, n_ref_dirs=12)
    elapsed = time.perf_counter() - t0
    meta = result.metadata
    frontier = meta.get("frontier", [])
    return {
        "solver": "moea_nsga3",
        "f1": meta["f1"], "f2": meta["f2"],
        "n_selected": meta["n_selected"],
        "n_frontier_points": meta["n_frontier_points"],
        "runtime_s": round(elapsed, 3),
        "pareto_frontier": [{"f1": s["f1"], "f2": s["f2"], "n_tasks": s["n_tasks"]}
                            for s in frontier],
        "schedule_summary": {"n_scheduled": meta["n_selected"],
                             "pop_size": meta["population_size"],
                             "n_generations": meta["n_generations"]},
    }

def run_b1(windows, targets, seed):
    from sar_sim.solver.baselines import baseline_b1
    from sar_sim.metrics.nesz import off_nadir_to_incidence
    t0 = time.perf_counter()
    result = baseline_b1(windows, targets, seed=seed)
    elapsed = time.perf_counter() - t0
    angles = []
    for obs in result.schedule:
        elev = obs.window.elevation
        phi = np.radians(90.0 - elev)
        theta = off_nadir_to_incidence(phi, ORBIT_ALT)
        angles.append(round(np.degrees(theta), 2))
    return {
        "solver": "b1_coverage_only",
        "f1": round(result.f1, 4), "f2": round(result.f2, 4),
        "n_selected": result.n_scheduled,
        "runtime_s": round(elapsed, 3),
        "incidence_angles_deg": angles,
        "c3_enforced": result.metadata.get("c3_enforced", False),
    }

def run_b2(windows, targets, seed):
    from sar_sim.solver.baselines import baseline_b2
    from sar_sim.metrics.nesz import off_nadir_to_incidence
    t0 = time.perf_counter()
    result = baseline_b2(windows, targets, seed=seed)
    elapsed = time.perf_counter() - t0
    angles = []
    for obs in result.schedule:
        elev = obs.window.elevation
        phi = np.radians(90.0 - elev)
        theta = off_nadir_to_incidence(phi, ORBIT_ALT)
        angles.append(round(np.degrees(theta), 2))
    return {
        "solver": "b2_proxy_quality",
        "f1": round(result.f1, 4), "f2": round(result.f2, 4),
        "f2_proxy": result.metadata.get("f2_proxy", 0),
        "n_selected": result.n_scheduled,
        "runtime_s": round(elapsed, 3),
        "incidence_angles_deg": angles,
        "c3_enforced": result.metadata.get("c3_enforced", False),
    }

SOLVER_RUNNERS = {"moea": run_moea, "b1": run_b1, "b2": run_b2}

# --- Scenario discovery ---
def discover_scenarios():
    """Discover all .pkl scenario files, mapped by group."""
    groups = {}
    pending_dirs = []
    if (SCENARIO_DIR / "small").exists():
        pending_dirs.append(("S1", SCENARIO_DIR / "small"))
    if (SCENARIO_DIR / "medium").exists():
        pending_dirs.append(("S2", SCENARIO_DIR / "medium"))
    if (SCENARIO_DIR / "large").exists():
        pending_dirs.append(("S3", SCENARIO_DIR / "large"))
    for g in ["S4", "S5", "S6"]:
        d = SCENARIO_DIR / g
        if d.exists():
            pending_dirs.append((g, d))
    for group, d in pending_dirs:
        pkls = sorted([f for f in d.glob("*.pkl") if not f.name.startswith(".")])
        # Filter out duplicates (alternating_seed*)
        pkls = [f for f in pkls if not f.name.startswith("alternating")]
        groups[group] = pkls
    return groups

# --- Process one scenario ---
RESULT_KEYS = []  # populated by first result

def process_scenario(pkl_path, group, progress):
    scenario_key = f"{group}/{pkl_path.name}"
    if scenario_key in progress.get("completed", {}):
        return None  # skip

    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        targets = data['targets']
        windows = data['windows']
        scenario_seed = data.get('seed', 0)
        n_targets = data.get('n_targets', len(targets))
        solver_seed = int(scenario_seed) + 100

        result = {
            "scenario": scenario_key, "n_targets": n_targets,
            "n_windows": len(windows), "seed": scenario_seed,
            "timestamp": datetime.now().isoformat(), "solvers": {},
        }
        # Store extra metadata if present
        for k in ["scenario_group", "theta_ref"]:
            if k in data:
                result[k] = data[k]

        for solver_name in SOLVERS:
            try:
                runner = SOLVER_RUNNERS[solver_name]
                sr = runner(windows, targets, solver_seed)
                result["solvers"][solver_name] = sr
            except Exception as e:
                result["solvers"][solver_name] = {
                    "error": str(e), "traceback": traceback.format_exc()}

        return result
    except Exception as e:
        return {"scenario": scenario_key, "error": str(e),
                "traceback": traceback.format_exc()}

# --- Main ---
def main():
    print("=" * 70)
    print(f"Phase 4.2 Full Experiment Runner (All Groups)")
    print(f"Start: {datetime.now().isoformat()}")
    print(f"SAR_SIM_SRC: {SAR_SIM_SRC}")
    print("=" * 70)

    groups = discover_scenarios()
    total = sum(len(v) for v in groups.values())
    print(f"\nDiscovered {total} scenarios across {len(groups)} groups:")
    for g, files in sorted(groups.items()):
        print(f"  {g}: {len(files)} scenarios")
    print()

    progress = load_progress()
    already = len(progress.get("completed", {}))
    print(f"Already completed: {already}")
    print()

    processed = 0
    skipped = 0
    failed = 0
    start_time = time.time()

    for group in sorted(groups.keys()):
        files = groups[group]
        if not files:
            continue
        print(f"\n{'='*60}")
        print(f"Group: {group} ({len(files)} scenarios)")
        print(f"{'='*60}")

        for i, pkl_path in enumerate(files):
            fname = pkl_path.name
            scenario_key = f"{group}/{fname}"

            if scenario_key in progress.get("completed", {}):
                skipped += 1
                if skipped <= 5 or skipped % 10 == 0:
                    print(f"  [{i+1}/{len(files)}] SKIP {fname} (already done)")
                continue

            print(f"  [{i+1}/{len(files)}] {fname}", end=" ", flush=True)

            result = process_scenario(pkl_path, group, progress)
            if result is None:
                skipped += 1
                print("SKIP")
                continue

            if "error" in result:
                failed += 1
                progress.setdefault("failed", {})[scenario_key] = result
                print(f"FAILED: {result['error'][:80]}")
            else:
                processed += 1
                progress.setdefault("completed", {})[scenario_key] = result
                # Print summary
                parts = []
                for sn in SOLVERS:
                    s = result["solvers"].get(sn, {})
                    if "error" in s:
                        parts.append(f"{sn}=ERR")
                    else:
                        parts.append(f"{sn}:f1={s['f1']:.1f},f2={s['f2']:.2f},rt={s['runtime_s']:.1f}s")
                print("|".join(parts))

            # Save progress after EVERY scenario for crash resilience
            save_progress(progress)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"DONE: {processed} processed, {skipped} skipped, {failed} failed")
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Progress saved to: {PROGRESS_FILE}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
