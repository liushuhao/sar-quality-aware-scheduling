"""Multi-MOEA solver factory: NSGA-II, MOEA/D, NSGA-III comparison.

Provides a unified interface for running multiple multi-objective
evolutionary algorithms on the same agile SAR scheduling problem,
with Hypervolume (HV) and Inverted Generational Distance (IGD)
metrics for quantitative comparison.

Algorithm comparison:
    compare_algorithms(windows, targets, algorithms=[...])
        → dict with per-algorithm frontiers + HV/IGD comparison table

Individual solver:
    multi_moea_solver(windows, targets, algorithm="nsga3", ...)
        → SolverResult (same interface as moea_solver)

All algorithms share:
    - Same SARSchedulingProblem (2N encoding: x + tau)
    - Same population_size and n_generations
    - Same seed for reproducibility
    - SolverResult output with frontier in metadata
"""

from dataclasses import dataclass, field
import math
import numpy as np
from typing import List, Dict, Optional, Tuple

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.decomposition.tchebicheff import Tchebicheff
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.indicators.hv import HV
from pymoo.indicators.igd import IGD

from sar_sim.types import (
    ObservationWindow,
    GroundTarget,
    ScheduledObservation,
    SolverResult,
)
from sar_sim.solver.types import (
    AgileSARInstance,
    build_agile_instance,
    compute_full_attitude,
    compute_los_separation,
)
from sar_sim.solver.moea import (
    SARSchedulingProblem,
    decode_solution,
    solutions_to_frontier,
    _build_schedule_from_moea,
)
from sar_sim.metrics.nesz import quality_score, off_nadir_to_incidence


# ─── Constraint-Free Problem Wrapper (for MOEA/D) ────────────────────────

class ConstraintFreeSARSchedulingProblem(SARSchedulingProblem):
    """Constraint-free SARSchedulingProblem for MOEA/D compatibility.

    pymoo's MOEA/D implementation does not support constrained problems
    (asserts ``not problem.has_constraints()``).  This wrapper sets
    ``n_ieq_constr=0`` and bakes constraint violations into the
    objectives as additive penalty terms, so the problem is formally
    unconstrained while preserving the original constraint structure.

    The penalty is weighted by ``penalty_coeff`` (same as the original
    problem) and added to all objectives so that infeasible solutions
    are dominated by feasible ones in the multi-objective sense.
    """

    def __init__(self, instance: AgileSARInstance, penalty_coeff: float = 1e5,
                 n_obj: int = 3):
        self.instance = instance
        self.penalty_coeff = penalty_coeff
        self.n_obj = n_obj

        N = instance.N
        n_var = 2 * N
        xl = np.zeros(n_var)
        xu = np.ones(n_var)

        # n_ieq_constr=0 — no constraints, penalty baked into objectives
        Problem.__init__(
            self,
            n_var=n_var,
            n_obj=n_obj,
            n_ieq_constr=0,
            xl=xl,
            xu=xu,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        """Evaluate with penalty merged into objectives."""
        # Call parent evaluate (2N encoding) to get F and G
        n_pop = X.shape[0]
        N = self.instance.N
        inst = self.instance

        f1 = np.zeros(n_pop)
        f2_num = np.zeros(n_pop)
        f3_num = np.zeros(n_pop)
        n_sel = np.zeros(n_pop)
        G  = np.zeros(n_pop)

        for p in range(n_pop):
            x_bin = X[p, :N]
            tau = X[p, N:2*N]
            selected = x_bin > 0.5

            # Pre-compute actual times and geometry
            t_actual_dict = {}
            phi_dict = {}
            squint_dict = {}

            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    t_act = task.t_earliest + tau[i] * (
                        task.t_latest - task.duration - task.t_earliest)
                    t_actual_dict[i] = t_act
                    roll, _, psi_sq = compute_full_attitude(
                        task, t_act, 1.0, inst)
                    phi_dict[i] = abs(roll)
                    squint_dict[i] = psi_sq

            # Objectives (accumulated numerators for mean computation)
            n_sel[p] = 0
            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    f1[p] += task.priority
                    n_sel[p] += 1
                    theta_i = off_nadir_to_incidence(phi_dict[i], inst.altitude_m)
                    cos_psi = math.cos(squint_dict[i])
                    f2_num[p] += math.sin(theta_i) * cos_psi
                    f3_num[p] += (math.cos(theta_i) ** 3) * (cos_psi ** 3)

            # Constraints (same as parent, using 2N decode)
            g = 0.0
            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    phi_abs_val = phi_dict[i]
                    if phi_abs_val < task.phi_min:
                        g += task.phi_min - phi_abs_val
                    if phi_abs_val > task.phi_max:
                        g += phi_abs_val - task.phi_max
                    if phi_abs_val < task.phi_min_res:
                        g += task.phi_min_res - phi_abs_val

                    # MOEA-2: t_actual in window
                    t_act = t_actual_dict[i]
                    if task.windows:
                        in_any = any(
                            (w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start)
                            <= t_act <=
                            (w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end)
                            for w in task.windows
                        )
                        if not in_any:
                            min_dist = float("inf")
                            for w in task.windows:
                                ws = w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start
                                we = w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end
                                min_dist = min(min_dist, abs(t_act - ws), abs(t_act - we))
                            g += min_dist / max(task.duration, 1.0)

                    # C7: squint
                    if squint_dict[i] > np.radians(45.0):
                        g += squint_dict[i] - np.radians(45.0)

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
                    t_end_a = t_a + task_a.duration
                    earliest_start_b = max(task_b.t_earliest, t_end_a + tau_trans)
                    if earliest_start_b + task_b.duration <= task_b.t_latest:
                        continue
                    excess = (earliest_start_b + task_b.duration) - task_b.t_latest
                    g += excess / max(task_b.duration, 1.0)

            energy_used = sum(inst.tasks[i].energy for i in range(N) if selected[i])
            if energy_used > inst.energy_budget:
                g += (energy_used - inst.energy_budget) / inst.energy_budget

            memory_used = sum(inst.tasks[i].memory for i in range(N) if selected[i])
            if memory_used > inst.memory_budget:
                g += (memory_used - inst.memory_budget) / inst.memory_budget

            G[p] = g

        # Bake penalty into objectives (no separate G output)
        penalty = self.penalty_coeff * G
        f2_mean = np.divide(f2_num, n_sel, out=np.zeros_like(f2_num), where=n_sel > 0)
        if self.n_obj >= 3:
            f3_mean = np.divide(f3_num, n_sel, out=np.zeros_like(f3_num), where=n_sel > 0)
            out["F"] = np.column_stack([-f1 + penalty, -f2_mean + penalty, -f3_mean + penalty])
        else:
            out["F"] = np.column_stack([-f1 + penalty, -f2_mean + penalty])


# ─── Algorithm Configuration ──────────────────────────────────────────────

@dataclass
class AlgorithmConfig:
    """Configuration for a single MOEA algorithm run."""
    algorithm: str                   # "nsga2", "moead", "nsga3"
    population_size: int = 100
    n_generations: int = 200
    n_ref_dirs: int = 99             # partitions for Das-Dennis → pop_size ≈ n_ref_dirs+1
    n_neighbors: int = 20            # MOEA/D neighborhood size
    seed: Optional[int] = None


# ─── Algorithm Builders ──────────────────────────────────────────────────

def _build_algorithm(
    config: AlgorithmConfig,
    ref_dirs: Optional[np.ndarray],
) -> object:
    """Build a pymoo algorithm instance from configuration.

    Args:
        config: algorithm configuration
        ref_dirs: pre-computed reference directions (required for MOEAD/NSGA3)

    Returns:
        pymoo Algorithm instance
    """
    algo = config.algorithm.lower()

    if algo == "nsga2":
        return NSGA2(
            pop_size=config.population_size,
            eliminate_duplicates=True,
        )

    elif algo == "moead":
        if ref_dirs is None:
            raise ValueError("MOEA/D requires reference directions")
        return MOEAD(
            ref_dirs=ref_dirs,
            n_neighbors=config.n_neighbors,
            decomposition=Tchebicheff(),
            prob_neighbor_mating=0.9,
        )

    elif algo == "nsga3":
        if ref_dirs is None:
            raise ValueError("NSGA-III requires reference directions")
        return NSGA3(
            pop_size=config.population_size,
            ref_dirs=ref_dirs,
            eliminate_duplicates=True,
        )

    else:
        raise ValueError(
            f"Unknown algorithm: {algo}. "
            f"Supported: nsga2, moead, nsga3"
        )


# ─── Unified Solver Entry Point ──────────────────────────────────────────

def multi_moea_solver(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    algorithm: str = "nsga3",
    population_size: int = 100,
    n_generations: int = 200,
    seed: Optional[int] = None,
    n_ref_dirs: int = 99,
    n_neighbors: int = 20,
    n_obj: int = 3,
    resolution_reqs: Optional[List[float]] = None,
    prebuilt_instance: Optional[AgileSARInstance] = None,
    **kwargs,
) -> SolverResult:
    """Unified MOEA solver supporting NSGA-II, MOEA/D, NSGA-III.

    All algorithms share the same problem formulation (2N encoding: x + tau),
    termination criterion, and output format for fair comparison.

    Args:
        windows: candidate observation windows
        targets: ground targets
        algorithm: "nsga2", "moead", or "nsga3" (default: "nsga3")
        population_size: population size (default 100)
        n_generations: number of generations (default 200)
        seed: random seed for reproducibility
        n_ref_dirs: Das-Dennis partitions for reference directions
            (NSGA-III and MOEA/D only; pop_size ≈ n_ref_dirs + 1 for 2-obj)
        n_neighbors: MOEA/D neighborhood size (ignored for NSGA2/NSGA3)
        n_obj: number of objectives (2 or 3)
        resolution_reqs: per-task resolution constraint minima (off-nadir, rad)
        **kwargs: passed to build_agile_instance

    Returns:
        SolverResult with Pareto frontier in metadata["frontier"]
    """
    algo_key = algorithm.lower()

    if seed is not None:
        np.random.seed(seed)

    # Build problem instance (shared across all algorithms)
    if prebuilt_instance is not None:
        instance = prebuilt_instance
    else:
        instance = build_agile_instance(
            windows, targets,
            resolution_reqs=resolution_reqs,
            **kwargs,
        )

    if instance.N == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={
                "solver": f"moea_{algo_key}",
                "algorithm": algo_key,
                "n_tasks": 0,
                "frontier": [],
            },
        )

    # Reference directions for decomposition-based algorithms
    ref_dirs = None
    if algo_key in ("moead", "nsga3"):
        # Das-Dennis: n_ref_dirs partitions → (n_ref_dirs + 1) directions for 2-obj
        ref_dirs = get_reference_directions(
            "das-dennis", n_obj, n_partitions=n_ref_dirs,
        )
        # Ensure population_size matches ref_dirs count for NSGA3/MOEAD
        if algo_key == "nsga3" and population_size != len(ref_dirs):
            population_size = len(ref_dirs)

    # Create pymoo problem — use constraint-free wrapper for MOEA/D
    # (pymoo's MOEAD does not support constrained problems)
    if algo_key == "moead":
        problem = ConstraintFreeSARSchedulingProblem(instance, n_obj=n_obj)
    else:
        problem = SARSchedulingProblem(instance, n_obj=n_obj)

    # Build algorithm
    config = AlgorithmConfig(
        algorithm=algo_key,
        population_size=population_size,
        n_generations=n_generations,
        n_ref_dirs=n_ref_dirs,
        n_neighbors=n_neighbors,
        seed=seed,
    )
    algo = _build_algorithm(config, ref_dirs)

    # Termination
    termination = get_termination("n_gen", n_generations)

    # Run optimization
    res = minimize(
        problem,
        algo,
        termination,
        seed=seed or 1,
        verbose=False,
        save_history=False,
    )

    # Decode Pareto frontier
    frontier = solutions_to_frontier(res.X, instance)

    # Select knee solution as representative
    if frontier:
        f1_vals = np.array([s["f1"] for s in frontier])
        f2_vals = np.array([s["f2"] for s in frontier])
        f1_range = f1_vals.max() - f1_vals.min() or 1.0
        f2_range = f2_vals.max() - f2_vals.min() or 1.0
        f1_norm = (f1_vals - f1_vals.min()) / f1_range
        f2_norm = (f2_vals - f2_vals.min()) / f2_range
        knee_idx = int(np.argmax(f1_norm + f2_norm))
        best = frontier[knee_idx]

        # Build schedule from knee solution (2N encoding)
        knee_x = res.X[knee_idx]
        knee_tau = knee_x[instance.N:2*instance.N]
        knee_t_actuals = []
        for i in best["selected"]:
            task = instance.tasks[i]
            t_act = task.t_earliest + knee_tau[i] * (
                task.t_latest - task.duration - task.t_earliest)
            knee_t_actuals.append(t_act)
        schedule = tuple(_build_schedule_from_moea(
            instance, best["selected"], knee_t_actuals,
        ))
    else:
        best = {"f1": 0.0, "f2": 0.0, "n_tasks": 0, "selected": [], "phis": []}
        schedule = ()

    return SolverResult(
        schedule=schedule,
        score=best["f1"] + best["f2"],
        metadata={
            "solver": f"moea_{algo_key}",
            "algorithm": algo_key,
            "n_tasks": instance.N,
            "n_selected": best["n_tasks"],
            "f1": best["f1"],
            "f2": best["f2"],
            "n_generations": n_generations,
            "population_size": population_size,
            "frontier": frontier,
            "n_frontier_points": len(frontier),
        },
    )


# ─── HV / IGD Computation ───────────────────────────────────────────────

def compute_hv(
    frontier: List[dict],
    ref_point: Optional[np.ndarray] = None,
) -> float:
    """Compute Hypervolume of a Pareto frontier.

    The hypervolume measures the volume of objective space dominated by
    the frontier, relative to a reference point. Higher HV = better
    (more dominated space).

    In our problem: f1 (coverage profit) and f2 (geometric resolution) are
    maximized. pymoo HV expects minimization, so we negate the objectives
    and use ref_point = (0, 0) (the origin in negated space corresponds
    to f1=0, f2=0 in original space).

    Args:
        frontier: list of dicts with keys "f1", "f2"
        ref_point: reference point in NEGATED objective space.
                   Default: (0, 0) which corresponds to f1=f2=0

    Returns:
        hypervolume value (higher = better)
    """
    if not frontier:
        return 0.0

    # Extract objectives and negate for minimization
    F = np.column_stack([
        [-s["f1"] for s in frontier],
        [-s["f2"] for s in frontier],
    ])

    if ref_point is None:
        ref_point = np.array([0.0, 0.0])

    # Ensure ref_point dominates all points (is worse in all dimensions)
    # For negated objectives: ref_point should be >= all points
    ref_point = np.maximum(ref_point, F.max(axis=0) + 1e-6)

    ind = HV(ref_point=ref_point)
    return float(ind(F))


def compute_igd(
    frontier: List[dict],
    reference_frontier: List[dict],
) -> float:
    """Compute Inverted Generational Distance.

    IGD measures the average distance from reference Pareto front points
    to the nearest point in the computed frontier. Lower IGD = better
    (frontier is closer to the reference).

    Args:
        frontier: computed Pareto frontier (list of dicts with "f1", "f2")
        reference_frontier: reference Pareto front to compare against

    Returns:
        IGD value (lower = better)
    """
    if not frontier or not reference_frontier:
        return float("inf")

    # Extract objectives and negate for minimization
    F = np.column_stack([
        [-s["f1"] for s in frontier],
        [-s["f2"] for s in frontier],
    ])
    PF = np.column_stack([
        [-s["f1"] for s in reference_frontier],
        [-s["f2"] for s in reference_frontier],
    ])

    ind = IGD(PF)
    return float(ind(F))


def build_reference_frontier(
    frontiers: Dict[str, List[dict]],
) -> List[dict]:
    """Build a reference Pareto front by merging and non-dominated sorting.

    Takes frontiers from multiple algorithms, combines them, and extracts
    the non-dominated set as the reference Pareto front.

    Args:
        frontiers: dict mapping algorithm_name → frontier list

    Returns:
        combined non-dominated reference frontier
    """
    all_solutions = []
    for algo_name, frontier in frontiers.items():
        all_solutions.extend(frontier)

    if not all_solutions:
        return []

    # Non-dominated sorting on original (f1, f2) maximization
    # A dominates B if f1_A >= f1_B and f2_A >= f2_B (with at least one >)
    n = len(all_solutions)
    dominated = [False] * n

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            fi1, fi2 = all_solutions[i]["f1"], all_solutions[i]["f2"]
            fj1, fj2 = all_solutions[j]["f1"], all_solutions[j]["f2"]
            # j dominates i?
            if fj1 >= fi1 and fj2 >= fi2 and (fj1 > fi1 or fj2 > fi2):
                dominated[i] = True
                break

    reference = [
        all_solutions[i] for i in range(n) if not dominated[i]
    ]

    # Deduplicate
    seen = set()
    unique = []
    for s in reference:
        key = (round(s["f1"], 6), round(s["f2"], 6))
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


# ─── Multi-Algorithm Comparison ──────────────────────────────────────────

def compare_algorithms(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    algorithms: Optional[List[str]] = None,
    population_size: int = 100,
    n_generations: int = 200,
    seeds: Optional[List[int]] = None,
    n_ref_dirs: int = 99,
    n_neighbors: int = 20,
    resolution_reqs: Optional[List[float]] = None,
    **kwargs,
) -> Dict:
    """Run all three MOEA algorithms on the same scenario and compare.

    Computes HV and IGD for each algorithm's Pareto frontier.
    The combined non-dominated set from all algorithms serves as the
    reference front for IGD computation.

    **Feasibility filtering**: After collecting all frontiers, each solution
    is independently verified against constraints MOEA-2-C5 via
    ConstraintVerifier.  Solutions that fail any constraint are marked
    INFEAISIBLE and excluded from HV/IGD computation and the reference
    frontier.  The comparison table reports both raw and feasible
    frontier sizes so the infeasibility rate is visible.

    Args:
        windows: candidate observation windows
        targets: ground targets
        algorithms: list of algorithm names to compare.
                    Default: ["nsga2", "moead", "nsga3"]
        population_size: population size for all algorithms
        n_generations: number of generations for all algorithms
        seeds: per-algorithm seeds (length must match algorithms)
        n_ref_dirs: Das-Dennis partitions for MOEA/D and NSGA-III
        n_neighbors: MOEA/D neighborhood size
        resolution_reqs: per-task resolution constraint minima
        **kwargs: passed to build_agile_instance

    Returns:
        dict with keys:
            - "results": dict mapping algorithm → SolverResult
            - "frontiers": dict mapping algorithm → frontier list (raw)
            - "feasible_frontiers": dict mapping algorithm → feasible-only list
            - "hv": dict mapping algorithm → HV score (feasible only)
            - "igd": dict mapping algorithm → IGD score (feasible only)
            - "reference_frontier": combined reference Pareto front (feasible only)
            - "comparison_table": list of dicts for tabular display
            - "verification": dict mapping algorithm → list of (sol, report)
              pairs for all solutions (for detailed analysis)
    """
    if algorithms is None:
        algorithms = ["nsga2", "moead", "nsga3"]

    if seeds is None:
        seeds = [42] * len(algorithms)
    elif len(seeds) != len(algorithms):
        raise ValueError(
            f"seeds length ({len(seeds)}) must match "
            f"algorithms length ({len(algorithms)})"
        )

    # ── Build problem instance once (shared across all algorithms) ──────
    from sar_sim.verification import ConstraintVerifier

    instance = build_agile_instance(
        windows, targets,
        resolution_reqs=resolution_reqs,
        **kwargs,
    )
    verifier = ConstraintVerifier(instance)

    results: Dict[str, SolverResult] = {}
    frontiers: Dict[str, List[dict]] = {}

    for algo, seed in zip(algorithms, seeds):
        result = multi_moea_solver(
            windows, targets,
            algorithm=algo,
            population_size=population_size,
            n_generations=n_generations,
            seed=seed,
            n_ref_dirs=n_ref_dirs,
            n_neighbors=n_neighbors,
            resolution_reqs=resolution_reqs,
            prebuilt_instance=instance,
            **kwargs,
        )
        results[algo] = result
        frontiers[algo] = result.metadata.get("frontier", [])

    # ── Constraint Verification — verify every solution ─────────────────
    verification_results: Dict[str, List[tuple]] = {}
    feasible_frontiers: Dict[str, List[dict]] = {}
    infeasible_counts: Dict[str, int] = {}
    violation_summary: Dict[str, Dict[str, int]] = {}  # algo → {MOEA-2: n, MOEA-3: n, ...}

    for algo in algorithms:
        frontier = frontiers[algo]
        vr = verifier.verify_frontier(frontier)
        verification_results[algo] = vr

        feasible = []
        infeasible_count = 0
        c_fail_counts: Dict[str, int] = {}

        for sol, report in vr:
            if report.overall_pass:
                feasible.append(sol)
            else:
                infeasible_count += 1
                for c_name, c_result in report.results.items():
                    if not c_result.passed:
                        c_fail_counts[c_name] = c_fail_counts.get(c_name, 0) + 1

        feasible_frontiers[algo] = feasible
        infeasible_counts[algo] = infeasible_count
        violation_summary[algo] = c_fail_counts

    # ── Build reference frontier from FEASIBLE solutions only ───────────
    reference_frontier = build_reference_frontier(feasible_frontiers)

    # ── Compute HV and IGD on FEASIBLE frontiers only ────────────────────
    hv_scores = {}
    igd_scores = {}
    for algo in algorithms:
        ff = feasible_frontiers[algo]
        hv_scores[algo] = compute_hv(ff)
        igd_scores[algo] = compute_igd(ff, reference_frontier)

    # ── Build comparison table with infeasibility stats ──────────────────
    comparison_table = []
    for algo in algorithms:
        # Raw frontier stats (for display)
        f_raw = frontiers[algo]
        n_raw = len(f_raw)
        n_feasible = len(feasible_frontiers[algo])
        n_infeasible = infeasible_counts[algo]

        # Feasible-only objective ranges
        ff = feasible_frontiers[algo]
        f1_vals = [s["f1"] for s in ff] if ff else []
        f2_vals = [s["f2"] for s in ff] if ff else []

        # Format violation summary string
        vsum = violation_summary.get(algo, {})
        if vsum:
            viol_str = ", ".join(
                f"{c}:{cnt}" for c, cnt in sorted(vsum.items())
            )
        else:
            viol_str = "none" if n_infeasible == 0 else "—"

        comparison_table.append({
            "algorithm": algo,
            "n_frontier_points": n_feasible,
            "n_frontier_raw": n_raw,
            "n_infeasible": n_infeasible,
            "f1_max": max(f1_vals) if f1_vals else 0.0,
            "f1_min": min(f1_vals) if f1_vals else 0.0,
            "f2_max": max(f2_vals) if f2_vals else 0.0,
            "f2_min": min(f2_vals) if f2_vals else 0.0,
            "HV": round(hv_scores[algo], 4),
            "IGD": round(igd_scores[algo], 6),
            "violations": viol_str,
        })

    return {
        "results": results,
        "frontiers": frontiers,
        "feasible_frontiers": feasible_frontiers,
        "hv": hv_scores,
        "igd": igd_scores,
        "reference_frontier": reference_frontier,
        "n_reference_points": len(reference_frontier),
        "comparison_table": comparison_table,
        "verification": verification_results,
        "infeasible_counts": infeasible_counts,
        "violation_summary": violation_summary,
    }


# ─── Pretty-Print Comparison ─────────────────────────────────────────────

def format_comparison_table(comparison_result: Dict) -> str:
    """Format the comparison result as a human-readable table.

    Includes infeasibility statistics from ConstraintVerifier when present.

    Args:
        comparison_result: output from compare_algorithms()

    Returns:
        formatted multi-line string
    """
    table = comparison_result.get("comparison_table", [])
    if not table:
        return "(no results)"

    lines = []
    lines.append("=" * 90)
    lines.append("Multi-MOEA Comparison: NSGA-II vs MOEA/D vs NSGA-III")
    lines.append("=" * 90)
    lines.append("")

    # Check if verification data is present
    has_verification = "infeasible_counts" in comparison_result

    if has_verification:
        header = (
            f"{'Algorithm':<12} {'#Feas':>5} {'#Raw':>5} {'#Inf':>5} "
            f"{'f1_max':>8} {'f1_min':>8} "
            f"{'f2_max':>8} {'f2_min':>8} {'HV':>10} {'IGD':>10}  Violations"
        )
    else:
        header = (
            f"{'Algorithm':<12} {'#Pts':>5} {'f1_max':>8} {'f1_min':>8} "
            f"{'f2_max':>8} {'f2_min':>8} {'HV':>10} {'IGD':>10}"
        )
    lines.append(header)
    lines.append("-" * 90)

    for row in table:
        if has_verification:
            viol = row.get("violations", "")
            lines.append(
                f"{row['algorithm']:<12} "
                f"{row['n_frontier_points']:>5} "
                f"{row.get('n_frontier_raw', row['n_frontier_points']):>5} "
                f"{row.get('n_infeasible', 0):>5} "
                f"{row['f1_max']:>8.2f} "
                f"{row['f1_min']:>8.2f} "
                f"{row['f2_max']:>8.4f} "
                f"{row['f2_min']:>8.4f} "
                f"{row['HV']:>10.4f} "
                f"{row['IGD']:>10.6f}  "
                f"{viol}"
            )
        else:
            lines.append(
                f"{row['algorithm']:<12} "
                f"{row['n_frontier_points']:>5} "
                f"{row['f1_max']:>8.2f} "
                f"{row['f1_min']:>8.2f} "
                f"{row['f2_max']:>8.4f} "
                f"{row['f2_min']:>8.4f} "
                f"{row['HV']:>10.4f} "
                f"{row['IGD']:>10.6f}"
            )

    lines.append("-" * 90)
    lines.append("HV = Hypervolume (higher = better frontier)")
    lines.append("IGD = Inverted Generational Distance (lower = closer to reference)")
    lines.append(
        f"Reference frontier: {comparison_result.get('n_reference_points', 0)} "
        f"non-dominated points (combined from all algorithms)"
    )

    # ── Infeasibility summary ────────────────────────────────────────────
    if has_verification:
        inf_counts = comparison_result.get("infeasible_counts", {})
        if inf_counts and any(v > 0 for v in inf_counts.values()):
            lines.append("")
            lines.append("Constraint verification summary:")
            for algo in sorted(inf_counts.keys()):
                n_inf = inf_counts[algo]
                vsum = comparison_result.get("violation_summary", {}).get(algo, {})
                if n_inf > 0:
                    vdetail = ", ".join(
                        f"{c}:{n}" for c, n in sorted(vsum.items())
                    ) if vsum else "—"
                    lines.append(
                        f"  {algo}: {n_inf} infeasible solutions "
                        f"(failed constraints: {vdetail})"
                    )
                else:
                    lines.append(f"  {algo}: all feasible")
            lines.append("")
            lines.append("Note: HV and IGD computed on FEASIBLE solutions only.")
            lines.append("      Infeasible solutions are excluded from both the")
            lines.append("      frontier and the reference set for IGD.")

    lines.append("=" * 90)

    return "\n".join(lines)
