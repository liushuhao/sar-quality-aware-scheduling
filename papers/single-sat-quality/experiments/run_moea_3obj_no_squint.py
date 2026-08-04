#!/usr/bin/env python3
"""
MOEA-3 ablation variant B: NO SQUINT (squint component removed from f2/f3).

Differences from baseline (run_moea_3obj.py):
  - f2 = Σ sin(θ_i)                 (no cos(ψ_sq) term)
  - f3 = Σ cos³(θ_i)                (no cos³(ψ_sq) term)

This isolates the contribution of squint-angle modeling to f2/f3.
Compared to baseline, if squint modeling matters, f2/f3 should drop.

DOES NOT MODIFY main moea.py. Solver is implemented in a new module
(sar_sim.solver.moea_no_squint) that imports the original class and
overrides _evaluate() with a modified f2/f3.

See handoffs/ablation-study-naming.md for full naming convention.
"""
import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import math
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from pymoo.core.problem import Problem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

from sar_sim.solver.moea import (
    moea_solver,
    _build_schedule_from_moea,
    decode_solution,
    solutions_to_frontier,
)
from sar_sim.solver.types import (
    AgileTask,
    AgileSARInstance,
    build_agile_instance_from_scenario,
    compute_full_attitude,
    compute_los_separation,
    precompute_geometry,
)
from sar_sim.metrics.nesz import off_nadir_to_incidence
from sar_sim.types import ObservationWindow, GroundTarget
from sar_sim.verification.constraints import ConstraintVerifier

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "moea_3obj_no_squint"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MOEA_PARAMS = {
    "population_size": 100,
    "n_generations": 200,
    "n_obj": 3,
}
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0

MAX_SQUINT_RAD = np.radians(45.0)


# ─── Variant B: SARSchedulingProblem with f2=sinθ, f3=cos³θ ──────

class SARSchedulingProblemNoSquint(Problem):
    """Variant B: f2 = Σ sin(θ), f3 = Σ cos³(θ). No squint component.

    All other logic (encoding, constraints, decoding) is identical to
    SARSchedulingProblem — only the f2/f3 numerators are changed.
    """

    def __init__(self, instance: AgileSARInstance, penalty_coeff: float = 1e5,
                 n_obj: int = 3, f1_gbl: float = 1.0):
        self.instance = instance
        self.penalty_coeff = penalty_coeff
        self.n_obj = n_obj
        self.f1_gbl = max(f1_gbl, 1.0)

        N = instance.N
        n_var = 2 * N
        xl = np.zeros(n_var)
        xu = np.ones(n_var)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_ieq_constr=1,
            xl=xl, xu=xu,
        )

    def _decode_t_actual(self, tau_i: float, task: AgileTask) -> float:
        return task.t_earliest + tau_i * task.time_span

    def _evaluate(self, X, out, *args, **kwargs):
        """Identical to baseline except f2 = Σ sin(θ), f3 = Σ cos³(θ)."""
        n_pop = X.shape[0]
        N = self.instance.N
        inst = self.instance

        f1 = np.zeros(n_pop)
        f2_num = np.zeros(n_pop)   # VARIANT: sin(θ) only
        f3_num = np.zeros(n_pop)   # VARIANT: cos³(θ) only
        n_sel = np.zeros(n_pop)
        G = np.zeros(n_pop)

        for p in range(n_pop):
            x_bin = X[p, :N]
            tau = X[p, N:2*N]
            selected = x_bin > 0.5

            t_actual_dict: Dict[int, float] = {}
            phi_dict: Dict[int, float] = {}
            squint_dict: Dict[int, float] = {}

            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    t_act = self._decode_t_actual(tau[i], task)
                    t_actual_dict[i] = t_act

                    f1[p] += task.priority
                    n_sel[p] += 1

                    if inst.geom_cache is not None:
                        geom = inst.geom_cache.lookup(i, t_act)
                        phi_dict[i] = geom.phi
                        squint_dict[i] = geom.psi_sq
                        # VARIANT B: f2 = sin(θ) only, f3 = cos³(θ) only
                        f2_num[p] += math.sin(geom.theta)
                        f3_num[p] += math.cos(geom.theta) ** 3
                    else:
                        roll, _, psi_sq = compute_full_attitude(task, t_act, 1.0, inst)
                        phi_dict[i] = abs(roll)
                        squint_dict[i] = psi_sq
                        theta_i = off_nadir_to_incidence(phi_dict[i], inst.altitude_m)
                        f2_num[p] += math.sin(theta_i)
                        f3_num[p] += math.cos(theta_i) ** 3

            # Constraints (identical to baseline)
            g = 0.0

            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    t_act = t_actual_dict[i]
                    wt = task.window_times
                    if wt:
                        in_any_window = False
                        min_dist = float("inf")
                        for w_start, w_end in wt:
                            if w_start <= t_act <= w_end:
                                in_any_window = True
                                break
                            if t_act < w_start:
                                min_dist = min(min_dist, w_start - t_act)
                            elif t_act > w_end:
                                min_dist = min(min_dist, t_act - w_end)
                            else:
                                min_dist = 0.0
                        if not in_any_window:
                            g += min_dist / max(task.duration, 1.0)

            # C2: transition feasibility
            sel_indices = [i for i in range(N) if selected[i]]
            if len(sel_indices) > 1:
                sel_indices.sort(key=lambda i: t_actual_dict[i])
                for k in range(len(sel_indices) - 1):
                    i_a = sel_indices[k]
                    i_b = sel_indices[k + 1]
                    task_a = inst.tasks[i_a]
                    task_b = inst.tasks[i_b]
                    t_a = t_actual_dict[i_a]
                    t_b = t_actual_dict[i_b]

                    delta_eta = compute_los_separation(task_a, t_a, task_b, t_b, inst)
                    tau_trans = delta_eta / inst.max_slew_rate + inst.settle_time
                    # RDR-004: penalise decoded-time gap directly
                    gap = t_b - (t_a + task_a.duration)
                    if gap < tau_trans:
                        g += (tau_trans - gap) / max(task_b.duration, 1.0)

            energy_used = sum(task.energy for i, task in enumerate(inst.tasks) if selected[i])
            if energy_used > inst.energy_budget:
                g += (energy_used - inst.energy_budget) / inst.energy_budget

            memory_used = sum(task.memory for i, task in enumerate(inst.tasks) if selected[i])
            if memory_used > inst.memory_budget:
                g += (memory_used - inst.memory_budget) / inst.memory_budget

            if n_sel[p] == 0:
                g += 1e5

            G[p] = g

        f1_norm = f1 / self.f1_gbl
        f2_mean = np.divide(f2_num, n_sel, out=np.zeros_like(f2_num), where=n_sel > 0)
        f3_mean = np.divide(f3_num, n_sel, out=np.zeros_like(f3_num), where=n_sel > 0)
        if self.n_obj >= 3:
            out["F"] = np.column_stack([-f1_norm, -f2_mean, -f3_mean])
        else:
            out["F"] = np.column_stack([-f1_norm, -f2_mean])
        out["G"] = G.reshape(-1, 1)


def moea_solver_no_squint(windows, targets, **kwargs):
    """Variant B solver: f2=sinθ, f3=cos³θ, identical to baseline otherwise.

    Inlines the optimization loop to use SARSchedulingProblemNoSquint.
    Reuses all frontier-decoding logic from the original moea_solver.
    """
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.util.ref_dirs import get_reference_directions
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination
    from sar_sim.types import SolverResult

    population_size = kwargs.get("population_size", 100)
    n_generations = kwargs.get("n_generations", 200)
    seed = kwargs.get("seed")
    n_ref_dirs = kwargs.get("n_ref_dirs", 12)
    n_obj = kwargs.get("n_obj", 3)
    hotstart_individual = kwargs.get("hotstart_individual")
    max_slew_rate = kwargs.get("max_slew_rate", SLEW_RATE)
    settle_time = kwargs.get("settle_time", SETTLE_TIME)
    prebuilt = kwargs.get("instance")

    if seed is not None:
        np.random.seed(seed)

    if prebuilt is not None:
        instance = prebuilt
    else:
        instance = build_agile_instance_from_scenario(
            kwargs.get("scenario"),
            max_slew_rate=max_slew_rate,
            settle_time=settle_time,
        )
        precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={"solver": "moea_nsga3_no_squint", "n_tasks": 0, "frontier": []},
        )

    f1_gbl = kwargs.get("f1_gbl", 1.0)
    instance.f1_gbl = f1_gbl

    problem = SARSchedulingProblemNoSquint(instance, n_obj=n_obj, f1_gbl=f1_gbl)

    ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=n_ref_dirs)

    sampling = None
    if hotstart_individual is not None:
        from pymoo.core.sampling import Sampling
        class _HotStart(Sampling):
            def __init__(self, x0, n_pop):
                super().__init__()
                self.x0 = x0
                self.n_pop = n_pop
            def _do(self, problem, n_samples, **kwargs):
                pop = np.zeros((self.n_pop, problem.n_var))
                pop[0] = self.x0
                rng = np.random.RandomState()
                for i in range(1, self.n_pop):
                    noise = rng.normal(0, 0.5, problem.n_var)
                    pop[i] = np.clip(self.x0 + noise, 0.0, 1.0)
                return pop
        sampling = _HotStart(hotstart_individual, population_size)

    algorithm = NSGA3(
        pop_size=population_size,
        ref_dirs=ref_dirs,
        sampling=sampling,
        crossover=SBX(prob=0.9, eta=20),
        mutation=PM(prob=0.1, eta=20),
    ) if sampling is not None else NSGA3(pop_size=population_size, ref_dirs=ref_dirs, crossover=SBX(prob=0.9, eta=20), mutation=PM(prob=0.1, eta=20))

    termination = get_termination("n_gen", n_generations)

    res = minimize(
        problem, algorithm, termination,
        seed=(seed if seed is not None else 1), verbose=False, save_history=False,
    )

    # Frontier decoding — reuse baseline function (geometry-agnostic)
    x_source = None
    frontier = []
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
        except Exception:
            frontier = []

    # Post-hoc constraint verification: filter infeasible solutions
    n_infeasible = 0
    n_frontier_raw = len(frontier) if frontier else 0
    all_infeasible = False
    if frontier:
        verifier = ConstraintVerifier(instance)
        verified = verifier.verify_frontier(frontier)
        feasible = [sol for sol, rpt in verified if rpt.overall_pass]
        n_infeasible = len(frontier) - len(feasible)
        if feasible:
            feasible_indices = [i for i, (_, rpt) in enumerate(verified) if rpt.overall_pass]
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
        rep_tau = rep_x[instance.N:2*instance.N]
        rep_t_actuals = []
        for i in best["selected"]:
            task = instance.tasks[i]
            t_act = task.t_earliest + rep_tau[i] * task.time_span
            rep_t_actuals.append(t_act)
        schedule = tuple(_build_schedule_from_moea(instance, best["selected"], rep_t_actuals))
    else:
        best = {"f1": 0.0, "f2": 0.0, "f3": 0.0, "n_tasks": 0, "selected": [], "phis": []}
        schedule = ()

    score = best["f1"] + best["f2"] + best.get("f3", 0.0)
    meta = {
        "solver": "moea_nsga3_no_squint",
        "n_tasks": instance.N,
        "n_selected": best["n_tasks"],
        "f1": best["f1"],
        "f1_raw": best.get("f1", 0.0) * f1_gbl,
        "f1_gbl": f1_gbl,
        "f2": best["f2"],
        "f3": best.get("f3", 0.0),
        "n_generations": n_generations,
        "population_size": population_size,
        "frontier": frontier,
        "n_frontier_points": len(frontier),
        "n_frontier_raw": n_frontier_raw,
        "n_obj": n_obj,
        "ablation_variant": "B_no_squint",
        "n_infeasible_filtered": n_infeasible,
        "all_infeasible": all_infeasible,
        "selected": [int(x) for x in best.get("selected", [])],
        "t_actuals": [float(x) for x in best.get("t_actuals", [])],
        "phis_off_nadir": [float(x) for x in best.get("phis", [])],
        "constraint_feasible": not all_infeasible,
        "n_constraints_failed": -1 if all_infeasible else 0,
    }
    return SolverResult(schedule=schedule, score=score, metadata=meta)


# ─── Experiment runner (mirrors run_moea_3obj.py) ───────────────

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

    result = moea_solver_no_squint(
        windows, targets,
        population_size=MOEA_PARAMS["population_size"],
        n_generations=MOEA_PARAMS["n_generations"],
        n_obj=MOEA_PARAMS["n_obj"],
        n_ref_dirs=12,
        max_slew_rate=SLEW_RATE,
        settle_time=SETTLE_TIME,
        hotstart_individual=hotstart,
        instance=instance,
        scenario=data,
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
        "solver": "c2_moea_3obj_no_squint",
        "ablation_variant": "B_no_squint",
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
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    args = parser.parse_args()

    all_groups = get_all_scenarios()
    if args.groups:
        groups = {k: v for k, v in all_groups.items() if k in args.groups}
    else:
        groups = all_groups

    total_scenarios = sum(len(files) for files in groups.values())
    print(f"MOEA-3obj NO-SQUINT ablation (variant B): {len(groups)} groups, {total_scenarios} scenarios")
    print(f"  Objectives: f1 (profit) + f2_no_squint + f3_no_squint")
    print(f"  Params: pop={MOEA_PARAMS['population_size']}, gen={MOEA_PARAMS['n_generations']}, n_obj={MOEA_PARAMS['n_obj']}")
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
        "ablation_variant": "B_no_squint",
    }
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)

    print(f"\n{'='*60}")
    print(f"MOEA-3obj NO-SQUINT ablation complete!")
    print(f"  Completed: {len(completed)}/{total_scenarios}")
    print(f"  Errors: {total_errors}")
    print(f"  Results: {progress_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
