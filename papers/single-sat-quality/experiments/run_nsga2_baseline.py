#!/usr/bin/env python3
"""WP1-1c: NSGA-II external baseline for the tri-objective agile SAR problem.

Swap only the evolutionary kernel (NSGA-III -> NSGA-II, pymoo); the encoding,
constraints and evaluation path are identical to the existing MOEA pipeline.
The pymoo Problem (`SARSchedulingProblem`), frontier decoding
(`solutions_to_frontier`), constraint post-filter (`ConstraintVerifier`),
knee rule and schedule construction are imported from `sar_sim.solver.moea`.
The instance is always built with `build_agile_instance_from_scenario`
(orbit-consistent geometry; never the default-orbit `build_agile_instance`).

Scope: sparse classes S1 (N=20) and S2 (N=100), 50 scenarios per class
(5 sub-configs A-E x scenario seeds 00-09), matching the existing runs.
Solver seed is fixed at 1, the pymoo fallback used by every existing MOEA run.

Outputs (experiments/results_nsga2_baseline/):
  _progress.json                  incremental, resumable per-scenario records
  summary_nsga2_baseline.json     per-seed aggregate + class summary + HV

ASCII-only console output (GBK cp936 console safety): no unicode symbols.
"""
import argparse
import hashlib
import json
import os
import pickle
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src"))

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.moea import (
    SARSchedulingProblem,
    solutions_to_frontier,
    _build_schedule_from_moea,
)
from sar_sim.solver.types import (
    build_agile_instance_from_scenario,
    precompute_geometry,
)
from sar_sim.verification.constraints import ConstraintVerifier

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results_nsga2_baseline"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_FILE = RESULTS_DIR / "_progress.json"
SUMMARY_FILE = RESULTS_DIR / "summary_nsga2_baseline.json"

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
POP = 100
GEN = 200
N_OBJ = 3
N_REF_DIRS = 12          # kept in config for parity with the MOEA runs (unused by NSGA-II)
SOLVER_SEED = 1          # pymoo fallback used by the existing MOEA runners
HOTSTART_SIGMA = 0.5
GROUPS = ("S1", "S2")


def _sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _code_stamp():
    """Hash of every file that defines the numbers this runner reports."""
    h = hashlib.sha1()
    rels = [
        "src/sar_sim/solver/moea.py",
        "src/sar_sim/solver/types.py",
        "src/sar_sim/solver/baselines.py",
        "src/sar_sim/verification/constraints.py",
        "papers/single-sat-quality/experiments/run_nsga2_baseline.py",
    ]
    for rel in rels:
        h.update(Path(_REPO / rel).read_bytes())
    return h.hexdigest()


def _git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(_REPO), text=True
        ).strip()[:8]
    except Exception:
        return "unknown"


CODE_STAMP = _code_stamp()
GIT_COMMIT = _git_commit()


def _atomic_write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class _HotStartSampling(Sampling):
    """Identical to the hot-start sampler embedded in moea_solver()."""

    def __init__(self, x0, n_pop, sigma, seed):
        super().__init__()
        self.x0 = np.asarray(x0, dtype=float)
        self.n_pop = n_pop
        self.sigma = sigma
        self.seed = seed

    def _do(self, problem, n_samples, **kwargs):
        pop = np.zeros((self.n_pop, problem.n_var))
        pop[0] = self.x0
        rng = np.random.RandomState(self.seed)
        for i in range(1, self.n_pop):
            noise = rng.normal(0, self.sigma, problem.n_var)
            pop[i] = np.clip(self.x0 + noise, 0.0, 1.0)
        return pop


def _postprocess(res, instance, f1_gbl):
    """Mirror of the post-processing block in moea_solver (lines 605-719)."""
    N = instance.N
    x_source = None
    if res.X is not None:
        x_source = res.X
        if x_source.ndim == 1:
            x_source = x_source.reshape(1, -1)
        frontier = solutions_to_frontier(x_source, instance)
    else:
        try:
            pop = res.algorithm.pop
            X_pop = pop.get("X")
            if X_pop is not None and len(X_pop) > 0:
                x_source = X_pop
                frontier = solutions_to_frontier(x_source, instance)
            else:
                frontier = []
        except Exception:
            frontier = []

    n_infeasible = 0
    n_frontier_raw = len(frontier) if frontier else 0
    all_infeasible = False
    if frontier:
        verifier = ConstraintVerifier(instance)
        verified = verifier.verify_frontier(frontier)
        feasible = [sol for sol, rpt in verified if rpt.overall_pass]
        n_infeasible = len(frontier) - len(feasible)
        if feasible:
            feasible_indices = [sol["row"] for sol, rpt in verified if rpt.overall_pass]
            x_source = x_source[feasible_indices] if x_source is not None else None
            frontier = feasible
        else:
            all_infeasible = True

    if frontier and x_source is not None:
        f1_vals = np.array([s["f1"] for s in frontier])
        f1_range = f1_vals.max() - f1_vals.min() or 1.0
        f1_norm = (f1_vals - f1_vals.min()) / f1_range

        f2_vals = np.array([s["f2"] for s in frontier])
        f2_range = f2_vals.max() - f2_vals.min() or 1.0
        f2_norm = (f2_vals - f2_vals.min()) / f2_range

        f3_vals = np.array([s.get("f3", 0.0) for s in frontier])
        f3_range = f3_vals.max() - f3_vals.min() or 1.0
        f3_norm = (f3_vals - f3_vals.min()) / f3_range

        knee_idx = int(np.argmax(f1_norm + f2_norm + f3_norm))
        best = frontier[knee_idx]

        rep_x = x_source[knee_idx]
        rep_tau = rep_x[N:2 * N]
        rep_t_actuals = []
        for i in best["selected"]:
            task = instance.tasks[i]
            rep_t_actuals.append(task.t_earliest + rep_tau[i] * task.time_span)
        schedule = tuple(_build_schedule_from_moea(instance, best["selected"], rep_t_actuals))
    else:
        best = {"f1": 0.0, "f2": 0.0, "f3": 0.0, "n_tasks": 0,
                "selected": [], "phis": [], "t_actuals": []}
        schedule = ()

    score = best["f1"] + best["f2"] + best.get("f3", 0.0)
    return {
        "solver": "nsga2_3obj",
        "n_tasks": N,
        "n_selected": best["n_tasks"],
        "f1": best["f1"],
        "f1_raw": best.get("f1", 0.0) * f1_gbl,
        "f1_gbl": f1_gbl,
        "f2": best["f2"],
        "f3": best.get("f3", 0.0),
        "n_generations": GEN,
        "population_size": POP,
        "frontier": frontier,
        "n_frontier_points": len(frontier),
        "n_frontier_raw": n_frontier_raw,
        "n_obj": N_OBJ,
        "n_sats": 1,
        "n_infeasible_filtered": n_infeasible,
        "all_infeasible": all_infeasible,
        "selected": [int(x) for x in best.get("selected", [])],
        "t_actuals": [float(x) for x in best.get("t_actuals", [])],
        "phis_off_nadir": [float(x) for x in best.get("phis", [])],
        "constraint_feasible": not all_infeasible,
        "n_constraints_failed": -1 if all_infeasible else 0,
        "score": score,
        "schedule_len": len(schedule),
    }


def _solve_nsga2(instance, f1_gbl, hotstart):
    problem = SARSchedulingProblem(instance, n_obj=N_OBJ, f1_gbl=f1_gbl, n_sats=1)
    kwargs = dict(
        pop_size=POP,
        crossover=SBX(prob=0.9, eta=20),
        mutation=PM(prob=0.1, eta=20),
    )
    if hotstart is not None:
        kwargs["sampling"] = _HotStartSampling(hotstart, POP, HOTSTART_SIGMA, SOLVER_SEED)
    algorithm = NSGA2(**kwargs)
    res = minimize(
        problem,
        algorithm,
        get_termination("n_gen", GEN),
        seed=SOLVER_SEED,
        verbose=False,
        save_history=False,
    )
    return _postprocess(res, instance, f1_gbl)


def run_one(key):
    pkl_path = SCENARIOS_DIR / key
    pkl_sha1 = _sha1_file(pkl_path)
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    windows = data.get("windows", [])
    targets = data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)

    t0 = time.time()
    instance = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME
    )
    precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return {
            "seed": seed, "n_targets": n_targets, "n_selected": 0,
            "f1": 0.0, "f1_raw": 0.0, "f1_gbl": 1.0, "f2": 0.0, "f3": 0.0,
            "runtime_s": round(time.time() - t0, 3), "n_frontier": 0,
            "frontier_f1": [], "frontier_f2": [], "frontier_f3": [],
            "n_obj": N_OBJ, "solver": "nsga2_3obj",
            "solver_version": GIT_COMMIT, "code_stamp": CODE_STAMP,
            "pkl_sha1": pkl_sha1, "selected": [], "t_actuals": [],
            "phis_off_nadir": [], "constraint_feasible": False,
            "n_constraints_failed": -1,
        }

    # G-BL anchor: f1 reference for normalization and the hot-start chromosome.
    gbl = baseline_b1(
        windows, targets, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        geom_cache=instance.geom_cache, instance=instance,
    )
    f1_gbl = max(gbl.f1, 1.0)
    instance.f1_gbl = f1_gbl

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
                if span > 0:
                    tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span
                else:
                    tau = 0.5
                x0[instance.N + idx] = max(0.0, min(1.0, tau))
    hotstart = x0 if seen else None

    meta = _solve_nsga2(instance, f1_gbl, hotstart)
    rt = time.time() - t0

    raw_frontier = meta.get("frontier", [])
    frontier_safe = [{
        "f1": float(s.get("f1", 0.0)),
        "f2": float(s.get("f2", 0.0)),
        "f3": float(s.get("f3", 0.0)),
        "n_tasks": int(s.get("n_tasks", 0)),
    } for s in raw_frontier]

    return {
        "seed": seed,
        "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0.0)),
        "f1_raw": float(meta.get("f1_raw", 0.0)),
        "f1_gbl": float(meta.get("f1_gbl", 1.0)),
        "f2": float(meta.get("f2", 0.0)),
        "f3": float(meta.get("f3", 0.0)),
        "runtime_s": round(rt, 3),
        "n_frontier": len(frontier_safe),
        "frontier_f1": [s["f1"] for s in frontier_safe],
        "frontier_f2": [s["f2"] for s in frontier_safe],
        "frontier_f3": [s["f3"] for s in frontier_safe],
        "n_obj": N_OBJ,
        "solver": "nsga2_3obj",
        "solver_version": GIT_COMMIT,
        "code_stamp": CODE_STAMP,
        "params": {"population_size": POP, "n_generations": GEN,
                   "n_obj": N_OBJ, "n_ref_dirs": N_REF_DIRS,
                   "solver_seed": SOLVER_SEED, "hotstart_sigma": HOTSTART_SIGMA},
        "pkl_sha1": pkl_sha1,
        "selected": meta.get("selected", []),
        "t_actuals": meta.get("t_actuals", []),
        "phis_off_nadir": meta.get("phis_off_nadir", []),
        "constraint_feasible": bool(meta.get("constraint_feasible", True)),
        "n_constraints_failed": int(meta.get("n_constraints_failed", 0)),
        "n_infeasible_filtered": int(meta.get("n_infeasible_filtered", 0)),
        "n_frontier_raw": int(meta.get("n_frontier_raw", 0)),
    }


def _scenario_keys(groups):
    keys = []
    for g in groups:
        d = SCENARIOS_DIR / g
        if d.is_dir():
            keys.extend(f"{g}/{p.name}" for p in sorted(d.glob("*.pkl")))
    return keys


def _valid(entry, pkl_path):
    return (entry.get("pkl_sha1") == _sha1_file(pkl_path)
            and entry.get("code_stamp") == CODE_STAMP)


# ---------------------------------------------------------------------------
# Summary: class statistics + coverage-quality exchange rate + Table-4-style HV
# ---------------------------------------------------------------------------

def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _external_frontier(entry):
    f1s = entry.get("frontier_f1") or []
    f2s = entry.get("frontier_f2") or []
    f3s = entry.get("frontier_f3") or []
    if f1s:
        return list(zip(f1s, f2s, f3s))
    return [(entry.get("f1", 0.0), entry.get("f2", 0.0), entry.get("f3", 0.0))]


def _hv3d(points, ranges):
    """Same 3D HV convention as statistical_analysis.py (Table tab:hv).

    Points are min-max normalized with the global ranges stored in
    statistical_results.json and clipped to the unit box; reference point is
    (0, 0, 0), all objectives maximized.  Algorithm copied verbatim from
    statistical_analysis.compute_hv.
    """
    if not points:
        return 0.0
    (f1lo, f1hi), (f2lo, f2hi), (f3lo, f3hi) = (
        ranges["f1"], ranges["f2"], ranges["f3"])
    norm = []
    for p in points:
        vals = []
        for v, lo, hi in ((p[0], f1lo, f1hi), (p[1], f2lo, f2hi), (p[2], f3lo, f3hi)):
            n = (v - lo) / (hi - lo) if hi > lo else 0.5
            vals.append(min(1.0, max(0.0, n)))
        norm.append(tuple(vals))
    ref_point = (0.0, 0.0, 0.0)
    pts = np.array([p for p in norm if all(p[i] >= ref_point[i] for i in range(3))])
    if len(pts) == 0:
        return 0.0
    pts = pts[pts[:, 0].argsort()[::-1]]
    hv = 0.0
    unique_f3 = sorted(set(pts[:, 2]), reverse=True)
    for i, f3_val in enumerate(unique_f3):
        mask = pts[:, 2] >= f3_val
        if not np.any(mask):
            continue
        subset = pts[mask]
        sorted_idx = subset[:, 0].argsort()[::-1]
        f1_prev = 1.0
        f2_prev = ref_point[1]
        area = 0.0
        for idx in sorted_idx:
            f1_cur = subset[idx, 0]
            f2_cur = subset[idx, 1]
            f2_eff = max(f2_cur, f2_prev)
            area += (f1_prev - f1_cur) * (f2_eff - ref_point[1])
            f1_prev = f1_cur
            f2_prev = f2_eff
        f3_next = unique_f3[i + 1] if i + 1 < len(unique_f3) else ref_point[2]
        hv += area * (f3_val - f3_next)
    return float(hv)


def write_summary(completed, groups):
    stats_path = PROJECT / "experiments" / "results" / "statistical_results.json"
    bl_path = PROJECT / "experiments" / "results" / "baselines_200.json"
    m2_path = PROJECT / "experiments" / "results" / "moea_2obj" / "_progress.json"
    m3_path = PROJECT / "experiments" / "results" / "moea_3obj" / "_progress.json"

    stat = _load_json(stats_path)
    ranges = stat["metadata"]["objective_ranges"]
    bl = _load_json(bl_path)
    m2 = _load_json(m2_path)["completed"]
    m3 = _load_json(m3_path)["completed"]

    summary = {
        "metadata": {
            "scope": "S1-S2 sparse classes, NSGA-II external baseline",
            "solver": "nsga2_3obj",
            "solver_seed": SOLVER_SEED,
            "params": {"population_size": POP, "n_generations": GEN,
                       "n_obj": N_OBJ, "n_ref_dirs_note": "unused by NSGA-II",
                       "crossover": "SBX(prob=0.9, eta=20)",
                       "mutation": "PM(prob=0.1, eta=20)",
                       "hotstart": "G-BL chromosome, sigma=0.5"},
            "git_commit": GIT_COMMIT,
            "code_stamp": CODE_STAMP,
            "hv_convention": ("3D HV, objectives min-max normalized with global "
                              "ranges from statistical_results.json (S1-S4), "
                              "clipped to unit box, ref=(0,0,0); same algorithm "
                              "as statistical_analysis.compute_hv (Table tab:hv)"),
            "exchange_rate_definition": ("mean per-scenario f2 gain vs G-BL (%) "
                                         "divided by mean coverage cost "
                                         "(1 - f1*) in percentage points"),
        },
        "per_seed_nsga2": {},
        "classes": {},
        "external_hv_reproduction_check": {},
    }

    # per-seed aggregate (mean over the 5 sub-configs A-E for each seed)
    for g in groups:
        per_seed = {}
        for s in range(10):
            keys = [k for k in completed
                    if k.startswith(g + "/") and f"_seed{s:02d}" in k]
            if not keys:
                continue
            arr = np.array([[completed[k]["f1"], completed[k]["f2"],
                             completed[k]["f3"], completed[k]["n_selected"]]
                            for k in keys], dtype=float)
            per_seed[f"{s:02d}"] = {
                "n_scenarios": len(keys),
                "f1_star_mean": float(arr[:, 0].mean()),
                "f2_mean": float(arr[:, 1].mean()),
                "f3_mean": float(arr[:, 2].mean()),
                "n_selected_mean": float(arr[:, 3].mean()),
            }
        summary["per_seed_nsga2"][g] = per_seed

    max_hv_diff = 0.0
    for g in groups:
        keys = sorted(k for k in completed if k.startswith(g + "/"))
        if not keys:
            continue
        # keep scenarios present in all four sources
        keys = [k for k in keys
                if k in m2 and k in m3 and k in bl
                and "b1" in bl[k]]
        if not keys:
            continue

        series = {name: {"f1": [], "f2": [], "f3": [], "hv": []}
                  for name in ("G-BL", "MOEA-2", "MOEA-3", "NSGA-II")}
        for k in keys:
            b1 = bl[k]["b1"]
            points = {
                "G-BL": [(b1["f1"], b1["f2"], b1["f3"])],
                "MOEA-2": _external_frontier(m2[k]),
                "MOEA-3": _external_frontier(m3[k]),
                "NSGA-II": _external_frontier(completed[k]),
            }
            for name in series:
                entry = (b1 if name == "G-BL" else
                         m2[k] if name == "MOEA-2" else
                         m3[k] if name == "MOEA-3" else completed[k])
                series[name]["f1"].append(float(entry["f1"]))
                series[name]["f2"].append(float(entry["f2"]))
                series[name]["f3"].append(float(entry.get("f3", 0.0)))
                series[name]["hv"].append(_hv3d(points[name], ranges))

        gbl_f1 = np.array(series["G-BL"]["f1"])
        gbl_f2 = np.array(series["G-BL"]["f2"])
        gbl_f3 = np.array(series["G-BL"]["f3"])

        class_entry = {"n_scenarios": len(keys), "solvers": {}}
        for name, s in series.items():
            f1 = np.array(s["f1"]); f2 = np.array(s["f2"]); f3 = np.array(s["f3"])
            hv = np.array(s["hv"])
            if name == "G-BL":
                gain2 = gain3 = cost = np.nan
                exchange = np.nan
            else:
                gain2 = float(np.nanmean((f2 - gbl_f2) / gbl_f2 * 100.0))
                gain3 = float(np.nanmean((f3 - gbl_f3) / gbl_f3 * 100.0))
                cost = float(np.mean((gbl_f1 - f1) * 100.0))
                exchange = (gain2 / cost) if abs(cost) > 1e-12 else float("nan")
            class_entry["solvers"][name] = {
                "f1_star_mean": float(f1.mean()),
                "f1_star_sd": float(f1.std(ddof=1)),
                "f2_mean": float(f2.mean()),
                "f2_sd": float(f2.std(ddof=1)),
                "f3_mean": float(f3.mean()),
                "f3_sd": float(f3.std(ddof=1)),
                "hv_mean": float(hv.mean()),
                "hv_sd": float(hv.std(ddof=1)),
                "f2_gain_pct_vs_gbl": gain2 if name != "G-BL" else 0.0,
                "f3_gain_pct_vs_gbl": gain3 if name != "G-BL" else 0.0,
                "coverage_cost_pp": cost if name != "G-BL" else 0.0,
                "exchange_rate_f2_pct_per_pp": exchange if name != "G-BL" else None,
            }
        summary["classes"][g] = class_entry

        # Cross-check that the copied HV convention reproduces published
        # per-class Table-4 values for the existing solvers.
        pub = stat.get("per_group", {}).get(g, {})
        for name in ("G-BL", "MOEA-2", "MOEA-3"):
            if name in pub:
                d = abs(class_entry["solvers"][name]["hv_mean"] - pub[name]["hv_mean"])
                max_hv_diff = max(max_hv_diff, d)
        summary["external_hv_reproduction_check"][g] = {
            "published": {n: pub[n]["hv_mean"] for n in pub},
            "recomputed": {n: class_entry["solvers"][n]["hv_mean"]
                           for n in ("G-BL", "MOEA-2", "MOEA-3")},
        }
    summary["external_hv_reproduction_check"]["max_abs_diff"] = max_hv_diff
    summary["external_hv_reproduction_check"]["pass"] = bool(max_hv_diff < 1e-9)

    _atomic_write_json(SUMMARY_FILE, summary)
    return summary


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(line_buffering=True)
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="NSGA-II external baseline (S1-S2)")
    parser.add_argument("--groups", nargs="+", default=list(GROUPS))
    parser.add_argument("--scenarios", nargs="+", default=None,
                        help="explicit keys, e.g. S1/S1-A_seed00.pkl")
    parser.add_argument("--no-resume", dest="resume", action="store_false", default=True)
    parser.add_argument("--max-scenarios", type=int, default=None)
    parser.add_argument("--no-summary", action="store_true")
    args = parser.parse_args()

    if args.scenarios:
        keys = args.scenarios
        groups = sorted({k.split("/")[0] for k in keys})
        for k in keys:
            if not (SCENARIOS_DIR / k).is_file():
                parser.error(f"scenario not found: {k}")
    else:
        groups = args.groups
        keys = _scenario_keys(groups)
    if args.max_scenarios is not None:
        keys = keys[:args.max_scenarios]

    if args.resume and PROGRESS_FILE.exists():
        try:
            progress = _load_json(PROGRESS_FILE)
            completed = progress.get("completed", {})
        except (json.JSONDecodeError, OSError):
            progress = {"completed": OrderedDict()}
            completed = progress["completed"]
    else:
        progress = {"completed": OrderedDict()}
        completed = progress["completed"]

    print(f"NSGA-II baseline: groups={groups} scenarios_planned={len(keys)}")
    print(f"  params: pop={POP} gen={GEN} n_obj={N_OBJ} solver_seed={SOLVER_SEED}")
    print(f"  git={GIT_COMMIT} code_stamp={CODE_STAMP[:12]}")
    print(f"  output: {PROGRESS_FILE}")

    done = 0
    errors = 0
    t_start = time.time()
    for key in keys:
        pkl_path = SCENARIOS_DIR / key
        if args.resume and key in completed and _valid(completed[key], pkl_path):
            done += 1
            continue
        try:
            entry = run_one(key)
        except Exception as exc:
            errors += 1
            print(f"  [ERR] {key}: {exc}")
            import traceback
            traceback.print_exc()
            continue
        completed[key] = entry
        progress["completed"] = completed
        _atomic_write_json(PROGRESS_FILE, progress)
        done += 1
        print(f"  [{done}/{len(keys)}] {key}: f1*={entry['f1']:.3f} "
              f"f2={entry['f2']:.4f} f3={entry['f3']:.4f} "
              f"n={entry['n_selected']} frontier={entry['n_frontier']} "
              f"t={entry['runtime_s']:.1f}s")

    elapsed = time.time() - t_start
    progress["config"] = {
        "groups": groups,
        "scenarios": keys,
        "params": {"population_size": POP, "n_generations": GEN,
                   "n_obj": N_OBJ, "n_ref_dirs": N_REF_DIRS,
                   "solver_seed": SOLVER_SEED, "hotstart_sigma": HOTSTART_SIGMA,
                   "max_slew_rate": SLEW_RATE, "settle_time": SETTLE_TIME},
        "git_commit": GIT_COMMIT,
        "code_stamp": CODE_STAMP,
    }
    progress["stats"] = {
        "planned": len(keys),
        "completed_total": len(completed),
        "errors": errors,
        "elapsed_s": round(elapsed, 1),
    }
    _atomic_write_json(PROGRESS_FILE, progress)

    if not args.no_summary:
        summary = write_summary(completed, groups)
        print(f"Summary: {SUMMARY_FILE}")
        print(f"  HV reproduction check pass={summary['external_hv_reproduction_check']['pass']} "
              f"max_abs_diff={summary['external_hv_reproduction_check']['max_abs_diff']:.2e}")

    print(f"Done: completed={len(completed)} errors={errors} elapsed={elapsed:.1f}s")


if __name__ == "__main__":
    main()