#!/usr/bin/env python3
"""RES2 (panel 20261031 residual): within-instance search-stochasticity quantification.

R1-07 follow-up: the main experiment solves each scenario once per stochastic
configuration. This runner repeats the two NSGA-III solvers on one variant-A
scenario per density class and measures the run-to-run spread of the knee
values relative to the between-scenario spread reported in the paper.

Deliberately does NOT pin the operator-level entropy (np.random.default_rng):
the quantity being measured is exactly the unpinned draw-to-draw variability.
Instance build mirrors experiments/run_moea_3obj.py::run_one (scenario ->
build_agile_instance_from_scenario -> precompute_geometry -> G-BL hot-start).

Output: experiments/results/replicate_variance_20261031/_progress.json
"""
import json, os, pickle, sys, time
from collections import OrderedDict
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.moea import moea_solver
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "replicate_variance_20261031"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
POP, GEN, N_REF_DIRS = 100, 200, 12
SCENARIOS = ["S1-A_seed00.pkl", "S2-A_seed00.pkl", "S3-A_seed00.pkl", "S4-A_seed00.pkl"]
SOLVERS = [("MOEA-2", 2), ("MOEA-3", 3)]
REPEATS = 5


def _atomic_write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def run_one(pkl_path: Path, n_obj: int) -> dict:
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows, targets = data["windows"], data["targets"]
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    gbl = baseline_b1(windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
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
    hotstart = x0 if seen else None

    t0 = time.time()
    result = moea_solver(
        windows, targets,
        population_size=POP, n_generations=GEN, n_obj=n_obj,
        n_ref_dirs=N_REF_DIRS, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=hotstart, instance=instance,
    )
    rt = time.time() - t0
    meta = result.metadata
    return {
        "f1": float(meta.get("f1", 0.0)),
        "f1_raw": float(meta.get("f1_raw", 0.0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0.0)),
        "f3": float(meta.get("f3", 0.0)),
        "n_selected": int(meta.get("n_selected", 0)),
        "n_frontier": int(meta.get("n_frontier", len(meta.get("frontier", [])))),
        "runtime_s": round(rt, 1),
    }


def main():
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(line_buffering=True)
        except Exception:
            pass
    progress_file = RESULTS_DIR / "_progress.json"
    if progress_file.exists():
        progress = json.loads(progress_file.read_text(encoding="utf-8"))
    else:
        progress = {"completed": OrderedDict(), "config": {
            "scenarios": SCENARIOS, "solvers": [s for s, _ in SOLVERS],
            "repeats": REPEATS, "pop": POP, "gen": GEN,
            "n_ref_dirs": N_REF_DIRS, "entropy": "unpinned (measured)"}}
    completed = progress["completed"]

    total = len(SCENARIOS) * len(SOLVERS) * REPEATS
    done = 0
    for pkl_name in SCENARIOS:
        group = pkl_name.split("-")[0]
        pkl_path = SCENARIOS_DIR / group / pkl_name
        for solver_name, n_obj in SOLVERS:
            for rep in range(REPEATS):
                key = f"{group}/{solver_name}/rep{rep:02d}"
                if key in completed:
                    done += 1
                    continue
                entry = run_one(pkl_path, n_obj)
                entry["scenario"] = pkl_name
                entry["solver"] = solver_name
                entry["repeat"] = rep
                completed[key] = entry
                done += 1
                progress["completed"] = completed
                _atomic_write_json(progress_file, progress)
                print(f"[{done}/{total}] {key}: f1={entry['f1']:.4f} f2={entry['f2']:.4f} "
                      f"f3={entry['f3']:.4f} n={entry['n_selected']} t={entry['runtime_s']}s", flush=True)
    print(f"Done: {done}/{total} -> {progress_file}")


if __name__ == "__main__":
    main()
