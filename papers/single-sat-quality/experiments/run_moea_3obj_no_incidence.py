#!/usr/bin/env python3
"""
MOEA-3 ablation variant C: NO INCIDENCE (incidence component removed from f2/f3).

Differences from baseline (run_moea_3obj.py):
  - f2 = Σ cos(ψ_sq,i)              (no sin(θ) term)
  - f3 = Σ cos³(ψ_sq,i)             (no cos³(θ) term)

Isolates the contribution of incidence-angle (θ) modeling to f2/f3.
"""
import pickle, json, sys, os, time, hashlib, subprocess
from pathlib import Path
from collections import OrderedDict
import math
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

from sar_sim.solver.moea import _build_schedule_from_moea, solutions_to_frontier
from sar_sim.solver.types import (
    AgileTask, AgileSARInstance, build_agile_instance_from_scenario,
    compute_full_attitude, compute_los_separation, precompute_geometry,
)
from sar_sim.metrics.nesz import off_nadir_to_incidence
from sar_sim.types import ObservationWindow, GroundTarget, SolverResult
from sar_sim.verification.constraints import ConstraintVerifier

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results" / "moea_3obj_no_incidence"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MOEA_PARAMS = {"population_size": 100, "n_generations": 200, "n_obj": 3}
SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
MAX_SQUINT_RAD = np.radians(45.0)


class SARSchedulingProblemNoIncidence(Problem):
    """Variant C: f2 = Σ cos(ψ), f3 = Σ cos³(ψ). No incidence (θ) component."""

    def __init__(self, instance, penalty_coeff=1e5, n_obj=3, f1_gbl=1.0):
        self.instance = instance
        self.penalty_coeff = penalty_coeff
        self.n_obj = n_obj
        self.f1_gbl = max(f1_gbl, 1.0)
        N = instance.N
        super().__init__(n_var=2*N, n_obj=n_obj, n_ieq_constr=1, xl=np.zeros(2*N), xu=np.ones(2*N))

    def _decode_t_actual(self, tau_i, task):
        return task.t_earliest + tau_i * task.time_span

    def _evaluate(self, X, out, *args, **kwargs):
        n_pop = X.shape[0]
        N = self.instance.N
        inst = self.instance
        f1 = np.zeros(n_pop)
        f2_num = np.zeros(n_pop)   # VARIANT: cos(ψ) only
        f3_num = np.zeros(n_pop)   # VARIANT: cos³(ψ) only
        n_sel = np.zeros(n_pop)
        G = np.zeros(n_pop)

        for p in range(n_pop):
            x_bin = X[p, :N]
            tau = X[p, N:2*N]
            selected = x_bin > 0.5
            t_actual_dict, phi_dict, squint_dict = {}, {}, {}

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
                        f2_num[p] += geom.cos_psi
                        f3_num[p] += geom.cos_psi ** 3
                    else:
                        roll, _, psi_sq = compute_full_attitude(task, t_act, 1.0, inst)
                        phi_dict[i] = abs(roll)
                        squint_dict[i] = psi_sq
                        cos_psi = math.cos(psi_sq)
                        f2_num[p] += cos_psi
                        f3_num[p] += cos_psi ** 3

            g = 0.0
            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    t_act = t_actual_dict[i]
                    wt = task.window_times
                    if wt:
                        in_any = False
                        min_dist = float("inf")
                        for w_start, w_end in wt:
                            if w_start <= t_act <= w_end:
                                in_any = True; break
                            if t_act < w_start: min_dist = min(min_dist, w_start - t_act)
                            elif t_act > w_end: min_dist = min(min_dist, t_act - w_end)
                        if not in_any: g += min_dist / max(task.duration, 1.0)

            sel_indices = [i for i in range(N) if selected[i]]
            if len(sel_indices) > 1:
                sel_indices.sort(key=lambda i: t_actual_dict[i])
                for k in range(len(sel_indices) - 1):
                    i_a, i_b = sel_indices[k], sel_indices[k+1]
                    task_a, task_b = inst.tasks[i_a], inst.tasks[i_b]
                    t_a, t_b = t_actual_dict[i_a], t_actual_dict[i_b]
                    delta_eta = compute_los_separation(task_a, t_a, task_b, t_b, inst)
                    tau_trans = delta_eta / inst.max_slew_rate + inst.settle_time
                    # RDR-004: penalise decoded-time gap directly
                    gap = t_b - (t_a + task_a.duration)
                    if gap < tau_trans:
                        g += (tau_trans - gap) / max(task_b.duration, 1.0)

            energy_used = sum(task.energy for i, task in enumerate(inst.tasks) if selected[i])
            if energy_used > inst.energy_budget: g += (energy_used - inst.energy_budget) / inst.energy_budget
            memory_used = sum(task.memory for i, task in enumerate(inst.tasks) if selected[i])
            if memory_used > inst.memory_budget: g += (memory_used - inst.memory_budget) / inst.memory_budget
            if n_sel[p] == 0: g += 1e5
            G[p] = g

        f1_norm = f1 / self.f1_gbl
        f2_mean = np.divide(f2_num, n_sel, out=np.zeros_like(f2_num), where=n_sel > 0)
        f3_mean = np.divide(f3_num, n_sel, out=np.zeros_like(f3_num), where=n_sel > 0)
        if self.n_obj >= 3:
            out["F"] = np.column_stack([-f1_norm, -f2_mean, -f3_mean])
        else:
            out["F"] = np.column_stack([-f1_norm, -f2_mean])
        out["G"] = G.reshape(-1, 1)


def moea_solver_no_incidence(windows, targets, **kwargs):
    from sar_sim.solver.baselines import baseline_b1
    population_size = kwargs.get("population_size", 100)
    n_generations = kwargs.get("n_generations", 200)
    seed = kwargs.get("seed")
    n_ref_dirs = kwargs.get("n_ref_dirs", 12)
    n_obj = kwargs.get("n_obj", 3)
    hotstart_individual = kwargs.get("hotstart_individual")
    max_slew_rate = kwargs.get("max_slew_rate", SLEW_RATE)
    settle_time = kwargs.get("settle_time", SETTLE_TIME)
    prebuilt = kwargs.get("instance")

    if seed is not None: np.random.seed(seed)
    if prebuilt is not None: instance = prebuilt
    else:
        instance = build_agile_instance_from_scenario(kwargs.get("scenario"), max_slew_rate=max_slew_rate, settle_time=settle_time)
        precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return SolverResult(schedule=(), score=0.0, metadata={"solver": "moea_nsga3_no_incidence", "n_tasks": 0, "frontier": []})

    f1_gbl = kwargs.get("f1_gbl", 1.0)
    instance.f1_gbl = f1_gbl
    problem = SARSchedulingProblemNoIncidence(instance, n_obj=n_obj, f1_gbl=f1_gbl)
    ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=n_ref_dirs)

    sampling = None
    if hotstart_individual is not None:
        class _HS(Sampling):
            def __init__(self, x0, n_pop): super().__init__(); self.x0, self.n_pop = x0, n_pop
            def _do(self, problem, n_samples, **kwargs):
                pop = np.zeros((self.n_pop, problem.n_var))
                pop[0] = self.x0
                rng = np.random.RandomState()
                for i in range(1, self.n_pop):
                    pop[i] = np.clip(self.x0 + rng.normal(0, 0.5, problem.n_var), 0, 1)
                return pop
        sampling = _HS(hotstart_individual, population_size)

    algorithm = NSGA3(pop_size=population_size, ref_dirs=ref_dirs, sampling=sampling, crossover=SBX(prob=0.9, eta=20), mutation=PM(prob=0.1, eta=20)) if sampling else NSGA3(pop_size=population_size, ref_dirs=ref_dirs, crossover=SBX(prob=0.9, eta=20), mutation=PM(prob=0.1, eta=20))
    res = minimize(problem, algorithm, get_termination("n_gen", n_generations), seed=(seed if seed is not None else 1), verbose=False, save_history=False)

    x_source, frontier = None, []
    if res.X is not None:
        x_source = res.X if res.X.ndim > 1 else res.X.reshape(1, -1)
        frontier = solutions_to_frontier(x_source, instance)
    else:
        try:
            X_pop = res.algorithm.pop.get("X")
            if X_pop is not None and len(X_pop) > 0:
                x_source = X_pop; frontier = solutions_to_frontier(x_source, instance)
        except: pass

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
        f1_norm = (f1_vals - f1_vals.min()) / (f1_vals.max() - f1_vals.min() or 1)
        f2_vals = np.array([s["f2"] for s in frontier])
        f2_norm = (f2_vals - f2_vals.min()) / (f2_vals.max() - f2_vals.min() or 1)
        f3_vals = np.array([s.get("f3", 0) for s in frontier])
        f3_norm = (f3_vals - f3_vals.min()) / (f3_vals.max() - f3_vals.min() or 1)
        knee = int(np.argmax(f1_norm + f2_norm + f3_norm))
        best = frontier[knee]
        rep_x = x_source[knee]
        rep_tau = rep_x[instance.N:2*instance.N]
        rep_t_actuals = [instance.tasks[i].t_earliest + rep_tau[i] * instance.tasks[i].time_span for i in best["selected"]]
        schedule = tuple(_build_schedule_from_moea(instance, best["selected"], rep_t_actuals))
    else:
        best = {"f1": 0.0, "f2": 0.0, "f3": 0.0, "n_tasks": 0, "selected": [], "phis": []}
        schedule = ()

    return SolverResult(
        schedule=schedule, score=best["f1"] + best["f2"] + best.get("f3", 0),
        metadata={
            "solver": "moea_nsga3_no_incidence", "n_tasks": instance.N,
            "n_selected": best["n_tasks"], "f1": best["f1"],
            "f1_raw": best.get("f1", 0) * f1_gbl, "f1_gbl": f1_gbl,
            "f2": best["f2"], "f3": best.get("f3", 0),
            "frontier": frontier, "n_frontier_points": len(frontier), "n_frontier_raw": n_frontier_raw,
            "n_obj": n_obj, "ablation_variant": "C_no_incidence",
            "n_infeasible_filtered": n_infeasible,
            "all_infeasible": all_infeasible,
            "selected": list(best.get("selected", [])),
            "t_actuals": list(best.get("t_actuals", [])),
            "phis_off_nadir": list(best.get("phis", [])),
            "constraint_feasible": not all_infeasible,
            "n_constraints_failed": -1 if all_infeasible else 0,
        }
    )


def _git_commit():
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except: return "unknown"
def _pkl_sha1(p):
    sha = hashlib.sha1()
    with open(p, "rb") as f:
        while c := f.read(8192): sha.update(c)
    return sha.hexdigest()

GIT_COMMIT = _git_commit()

def get_all_scenarios():
    groups = OrderedDict()
    for g in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        d = SCENARIOS_DIR / g
        if d.is_dir():
            pkgs = sorted(d.glob("*.pkl"))
            if pkgs: groups[g] = pkgs
    return groups

def run_one(pkl_path):
    pkl_sha1 = _pkl_sha1(pkl_path)
    with open(pkl_path, 'rb') as f: data = pickle.load(f)
    windows, targets = data.get("windows", []), data.get("targets", [])
    n_targets = data.get("n_targets", len(targets))
    seed = data.get("seed", 0)
    t0 = time.time()

    hotstart = None
    from sar_sim.solver.baselines import baseline_b1
    gbl = baseline_b1(windows, targets)
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    x0 = np.zeros(2 * instance.N); seen = set()
    for obs in gbl.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx and target_to_idx[tid] not in seen:
            idx = target_to_idx[tid]; seen.add(idx)
            x0[idx] = 1.0
            span = instance.tasks[idx].time_span
            tau = (obs.t_actual_start.timestamp() - instance.tasks[idx].t_earliest) / span if span > 0 else 0.5
            x0[instance.N + idx] = max(0, min(1, tau))
    if seen: hotstart = x0

    result = moea_solver_no_incidence(
        windows, targets,
        population_size=MOEA_PARAMS["population_size"], n_generations=MOEA_PARAMS["n_generations"],
        n_obj=MOEA_PARAMS["n_obj"], n_ref_dirs=12,
        max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
        hotstart_individual=hotstart, instance=instance, scenario=data,
    )
    rt = time.time() - t0
    meta = result.metadata

    frontier_safe = [{"f1": float(s.get("f1", 0)), "f2": float(s.get("f2", 0)),
                      "f3": float(s.get("f3", 0)), "n_tasks": int(s.get("n_tasks", 0))}
                     for s in meta.get("frontier", [])]
    return {
        "seed": seed, "n_targets": n_targets,
        "n_selected": int(meta.get("n_selected", 0)),
        "f1": float(meta.get("f1", 0)), "f1_raw": float(meta.get("f1_raw", 0)),
        "f1_gbl": float(meta.get("f1_gbl", 1)),
        "f2": float(meta.get("f2", 0)), "f3": float(meta.get("f3", 0)),
        "runtime_s": round(rt, 3), "n_frontier": len(frontier_safe),
        "frontier_f1": [s["f1"] for s in frontier_safe],
        "frontier_f2": [s["f2"] for s in frontier_safe],
        "frontier_f3": [s["f3"] for s in frontier_safe],
        "n_obj": 3, "solver": "c2_moea_3obj_no_incidence",
        "ablation_variant": "C_no_incidence", "solver_version": GIT_COMMIT,
        "params": dict(MOEA_PARAMS), "pkl_sha1": pkl_sha1,
        "selected": meta.get("selected", []),
        "t_actuals": meta.get("t_actuals", []),
        "phis_off_nadir": meta.get("phis_off_nadir", []),
        "constraint_feasible": bool(meta.get("constraint_feasible", True)),
        "n_constraints_failed": int(meta.get("n_constraints_failed", 0)),
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", nargs="+")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    args = parser.parse_args()

    all_groups = get_all_scenarios()
    groups = {k: v for k, v in all_groups.items() if k in args.groups} if args.groups else all_groups
    total = sum(len(v) for v in groups.values())
    print(f"MOEA-3obj NO-INCIDENCE ablation (variant C): {len(groups)} groups, {total} scenarios")
    print(f"  Output: {RESULTS_DIR / '_progress.json'}\n")

    pf = RESULTS_DIR / "_progress.json"
    if args.resume and pf.exists():
        progress = json.load(open(pf)); completed = progress.get("completed", {})
        print(f"Resuming: {len(completed)} already completed")
    else:
        progress = {"completed": OrderedDict()}; completed = progress["completed"]

    total_run = len(completed); total_err = 0
    for gname, files in groups.items():
        print(f"\n=== {gname}: {len(files)} scenarios ===")
        for fpath in files:
            key = f"{gname}/{fpath.name}"
            if key in completed: continue
            try:
                r = run_one(fpath)
                if r is not None: completed[key] = r; total_run += 1
                else: total_err += 1; continue
                if total_run <= 3 or total_run % 10 == 0:
                    print(f"  [{total_run}/{total}] {fpath.name}: f1={r['f1_raw']:.0f}, f2={r['f2']:.2f}, f3={r['f3']:.4f}, n={r['n_selected']}, t={r['runtime_s']:.1f}s")
            except Exception as e:
                print(f"  [ERR] {fpath.name}: {e}"); total_err += 1; continue
            progress["completed"] = completed
            json.dump(progress, open(pf, "w"), indent=2, default=str)

    progress["stats"] = {"total_scenarios": total, "completed": len(completed), "errors": total_err, "ablation_variant": "C_no_incidence"}
    json.dump(progress, open(pf, "w"), indent=2)
    print(f"\nVariant C complete: {len(completed)}/{total}, errors={total_err}")

if __name__ == "__main__":
    main()
