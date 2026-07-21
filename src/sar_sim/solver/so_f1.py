"""GA-P: Single-Objective Profit Maximizer (so_f1.py).

Implements the GA-P baseline from the problem formalization (§6 GA-P):
    max f1(x,t) = Σ x_i * p_i   s.t. MOEA-2--C6

A single-objective GA (pymoo GA) searches observation times t_i
within each task's visibility window.  Only coverage profit f1 is
maximised — no quality objectives (f2/f3).

Decision variables (2N encoding):
    x[0:N]     ∈ [0,1]   task selection (>0.5 = selected)
    τ[N:2N]    ∈ [0,1]   normalized time → t_i^actual

Two baseline comparisons from the formalization (§6):
    G-BL→GA-P gap  = value of t_i search freedom
    GA-P→MOEA-2 gap  = value of NESZ quality awareness
"""

import math
import numpy as np
from typing import List, Optional, Tuple

from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from sar_sim.types import ObservationWindow, GroundTarget, ScheduledObservation, SolverResult
from sar_sim.metrics.nesz import off_nadir_to_incidence, quality_score

from sar_sim.solver.types import (
    AgileTask,
    AgileSARInstance,
    build_agile_instance,
    compute_full_attitude,
    compute_los_separation,  # cached LOS computation
    precompute_geometry,
)

# Precomputed constants for hot-path
_MAX_SQUINT_RAD = np.radians(45.0)


# ═══════════════════════════════════════════════════════════════════════════
# B2ProfitProblem — pymoo Problem
# ═══════════════════════════════════════════════════════════════════════════

class B2ProfitProblem(Problem):
    """Single-objective: maximise f1 (coverage profit) only.

    Encoding (2N):
      x[0:N]   ∈ [0,1]   task selection (threshold 0.5)
      τ[N:2N]  ∈ [0,1]   normalised observation time

    τ_i maps to actual start time:
      t_i = t_earliest_i + τ_i * (t_latest_i − d_i − t_earliest_i)

    Geometry at t_i is computed via ``compute_full_attitude()``.
    Constraints MOEA-2--C6 are enforced via aggregated penalty (same as MOEA).
    """

    def __init__(self, instance: AgileSARInstance, penalty_coeff: float = 1e5):
        self.instance = instance
        self.penalty_coeff = penalty_coeff

        N = instance.N
        n_var = 2 * N

        # xl, xu: [0,1] for all variables
        xl = np.zeros(n_var)
        xu = np.ones(n_var)

        super().__init__(
            n_var=n_var,
            n_obj=1,             # single-objective
            n_ieq_constr=0,       # penalty baked into objective (avoids empty-solution domination)
            xl=xl,
            xu=xu,
        )

    # ── helpers ────────────────────────────────────────────────────────

    def _decode_t_actual(self, tau_i: float, task: AgileTask) -> float:
        """Decode tau in [0,1] to actual start time (seconds, epoch)."""
        return task.t_earliest + tau_i * task.time_span

    def _compute_los_separation(
        self,
        task_a: AgileTask, t_a: float,
        task_b: AgileTask, t_b: float,
    ) -> float:
        """Angular separation (rad) between two LOS vectors at given times.

        Uses precomputed caches (target ECEF, satellite orbit) when available.
        Falls back to the original 3-axis orbital model otherwise.
        """
        return compute_los_separation(task_a, t_a, task_b, t_b, self.instance)

    # ── evaluate ───────────────────────────────────────────────────────

    def _evaluate(self, X, out, *args, **kwargs):
        """Evaluate population.  X shape: (pop_size, 2N)."""
        n_pop = X.shape[0]
        N = self.instance.N
        inst = self.instance

        # f1 = coverage profit (negated for pymoo minimisation)
        f1 = np.zeros(n_pop)
        # G  = aggregated constraint violation
        G = np.zeros(n_pop)

        for p in range(n_pop):
            x_bin = X[p, :N]          # task selection
            tau   = X[p, N:2*N]       # normalised time

            selected = x_bin > 0.5
            sel_indices = [i for i in range(N) if selected[i]]

            # ── f1: coverage profit ─────────────────────────────────
            for i in range(N):
                if selected[i]:
                    f1[p] += inst.tasks[i].priority
            # Negate for minimisation
            f1[p] = -f1[p]

            # ── Constraints ─────────────────────────────────────────
            g = 0.0

            # Pre-compute actual start time and off-nadir for each
            # selected task
            t_actual_list: List[float] = []
            phi_list: List[float] = []

            for i in range(N):
                if selected[i]:
                    task = inst.tasks[i]
                    t_act = self._decode_t_actual(tau[i], task)
                    t_actual_list.append(t_act)

                    # Look up precomputed geometry (GeomCache, Step 1)
                    # Fallback to compute_full_attitude if cache unavailable
                    if inst.geom_cache is not None:
                        geom = inst.geom_cache.lookup(i, t_act)
                        phi = geom.phi
                        squint = geom.psi_sq
                        theta_i = geom.theta  # precomputed incidence angle
                    else:
                        roll, _, squint = compute_full_attitude(
                            task, t_act, 1.0, inst)
                        phi = abs(roll)
                        theta_i = off_nadir_to_incidence(phi, inst.altitude_m)
                    phi_list.append(phi)

                    # MOEA-2: time must be within at least one actual visibility window
                    wt = task.window_times
                    if wt:
                        in_any = False
                        min_dist = float("inf")
                        for w_start, w_end in wt:
                            if w_start <= t_act <= w_end:
                                in_any = True
                                break
                            dist = min(abs(t_act - w_start), abs(t_act - w_end))
                            if dist < min_dist:
                                min_dist = dist
                        if not in_any:
                            g += min_dist / max(task.duration, 1.0)
                    #
                    # C7: squint angle constraint
                    if squint > _MAX_SQUINT_RAD:
                        g += squint - _MAX_SQUINT_RAD
                    #
                    # MOEA-3: resolution constraint — check that the
                    # actual incidence angle meets the minimum.
                    # theta_i from GeomCache (precomputed); theta_min from task (precomputed).
                    if theta_i < task.theta_min_res:
                        g += (task.theta_min_res - theta_i) / max(task.theta_min_res, 0.001)

                    # Note: we do NOT check phi against task.phi_min/phi_max
                    # because those bounds are derived from flat-Earth
                    # elevation at the window midpoint and don't match the
                    # full 3-axis geometry.  The time-window check (MOEA-2) and
                    # resolution check (MOEA-3) are sufficient.

            # C3: transition feasibility between consecutive tasks
            if len(sel_indices) > 1:
                # Build ordered list with times (sorted by t_actual)
                ordered = sorted(
                    zip(sel_indices, t_actual_list, phi_list),
                    key=lambda x: x[1],
                )

                for k in range(len(ordered) - 1):
                    i_a = ordered[k][0]
                    i_b = ordered[k + 1][0]
                    t_a = ordered[k][1]
                    task_a = inst.tasks[i_a]
                    task_b = inst.tasks[i_b]

                    # Required transition time
                    delta_eta = self._compute_los_separation(
                        task_a, t_a, task_b, ordered[k + 1][1],
                    )
                    tau_trans = (delta_eta / inst.max_slew_rate
                                 + inst.settle_time)

                    # Task A ends at t_a + duration
                    t_end_a = t_a + task_a.duration

                    # Task B can be delayed within its window
                    earliest_start_b = max(task_b.t_earliest,
                                           t_end_a + tau_trans)

                    if earliest_start_b + task_b.duration <= task_b.t_latest:
                        # Feasible by delaying B — no penalty
                        continue

                    # Infeasible even with max delay
                    excess = ((earliest_start_b + task_b.duration)
                              - task_b.t_latest)
                    g += excess / max(task_b.duration, 1.0)

            # C4: energy budget
            energy_used = sum(
                inst.tasks[i].energy for i in range(N) if selected[i])
            if energy_used > inst.energy_budget:
                g += (energy_used - inst.energy_budget) / inst.energy_budget

            # C5: memory budget
            memory_used = sum(
                inst.tasks[i].memory for i in range(N) if selected[i])
            if memory_used > inst.memory_budget:
                g += (memory_used - inst.memory_budget) / inst.memory_budget

            G[p] = g

        # Apply penalty to f1 (baked into objective, no separate G output)
        out["F"] = (f1 + self.penalty_coeff * G).reshape(-1, 1)


# ═══════════════════════════════════════════════════════════════════════════
# Solution decoding
# ═══════════════════════════════════════════════════════════════════════════

def _decode_b2_solution(
    X: np.ndarray,
    instance: AgileSARInstance,
) -> Tuple[List[int], List[float], List[float], float]:
    """Decode a GA-P chromosome into interpretable form.

    Args:
        X: solution vector (length 2N)
        instance: agile SAR instance

    Returns:
        (selected_indices, t_actuals, phis, f1)
    """
    N = instance.N
    x_bin = X[:N]
    tau = X[N:2*N]

    selected = []
    t_actuals = []
    phis = []
    f1 = 0.0

    for i in range(N):
        if x_bin[i] > 0.5:
            selected.append(i)
            task = instance.tasks[i]
            t_act = task.t_earliest + tau[i] * task.time_span
            t_actuals.append(t_act)

            # Use GeomCache (Step 1) if available, else fall back
            if instance.geom_cache is not None:
                geom = instance.geom_cache.lookup(i, t_act)
                phis.append(geom.phi)
            else:
                roll, _, _squint = compute_full_attitude(task, t_act, 1.0, instance)
                phis.append(abs(roll))
            f1 += task.priority

    return selected, t_actuals, phis, f1


def _build_schedule_from_b2(
    instance: AgileSARInstance,
    selected_indices: List[int],
    t_actuals: List[float],
) -> List[ScheduledObservation]:
    """Build ScheduledObservation list from GA-P solution."""
    from sar_sim.types import ScheduledObservation
    from datetime import datetime, timedelta, timezone

    observations = []
    for idx, t_act in zip(selected_indices, t_actuals):
        task = instance.tasks[idx]

        # Find the window that best contains t_act
        best_window = None
        best_dist = float("inf")
        for w in task.windows:
            w_start = w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start
            w_end = w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end
            if w_start <= t_act <= w_end:
                # This window contains t_act
                best_window = w
                break
            # Track closest window
            dist = min(abs(w_start - t_act), abs(w_end - t_act))
            if dist < best_dist:
                best_dist = dist
                best_window = w

        if best_window is not None:
            obs_start = datetime.fromtimestamp(t_act, tz=timezone.utc)
            obs_end = obs_start + timedelta(seconds=task.duration)
            observations.append(ScheduledObservation(
                window=best_window,
                t_actual_start=obs_start,
                t_actual_end=obs_end,
            ))

    observations.sort(key=lambda o: o.t_actual_start)
    return observations


# ═══════════════════════════════════════════════════════════════════════════
# Main solver entry point
# ═══════════════════════════════════════════════════════════════════════════

def b2_profit_solver(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    population_size: int = 100,
    n_generations: int = 200,
    seed: Optional[int] = None,
    **kwargs,
) -> SolverResult:
    """GA-P single-objective GA solver (maximise f1 only).

    Uses pymoo GA with SBX crossover + polynomial mutation to search
    observation times t_i that maximise coverage profit subject to
    MOEA-2--C6 constraints.

    Args:
        windows: candidate observation windows
        targets: ground targets
        population_size: GA population size
        n_generations: number of GA generations
        seed: random seed
        **kwargs: passed to build_agile_instance (e.g. max_slew_rate)

    Returns:
        SolverResult with schedule and metadata
    """
    if seed is not None:
        np.random.seed(seed)

    # Build problem instance
    instance = build_agile_instance(windows, targets, **kwargs)

    # Precompute geometry for all tasks (GeomCache, Step 1)
    precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={"solver": "b2_profit", "n_tasks": 0, "f1": 0.0,
                       "f2": 0.0, "f3": 0.0, "n_selected": 0},
        )

    # Create pymoo problem
    problem = B2ProfitProblem(instance)

    # GA algorithm
    algorithm = GA(
        pop_size=population_size,
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(prob=0.2, eta=10),  # higher mutation → diversity
        eliminate_duplicates=False,     # keeps diverse solutions
    )

    termination = get_termination("n_gen", n_generations)

    res = minimize(
        problem,
        algorithm,
        termination,
        seed=seed or 1,
        verbose=False,
        save_history=False,
    )

    # Decode best solution
    if res.X is not None:
        x_best = res.X.reshape(-1) if res.X.ndim > 1 else res.X
        sel, t_acts, phis, f1 = _decode_b2_solution(x_best, instance)
    else:
        # Fall back to last population
        try:
            pop = res.algorithm.pop
            X_pop = pop.get("X")
            if X_pop is not None and len(X_pop) > 0:
                # Find best (lowest penalty → highest F)
                F_pop = pop.get("F")
                if F_pop is not None:
                    best_idx = int(np.argmin(F_pop[:, 0]))
                else:
                    best_idx = 0
                x_best = X_pop[best_idx]
                sel, t_acts, phis, f1 = _decode_b2_solution(x_best, instance)
            else:
                sel, t_acts, phis, f1 = [], [], [], 0.0
        except Exception:
            sel, t_acts, phis, f1 = [], [], [], 0.0

    # Build schedule
    schedule = tuple(_build_schedule_from_b2(instance, sel, t_acts))

    # ── Post-hoc f2/f3 (Step 4): compute mean after GA convergence ───────
    f2_posthoc = 0.0
    f3_posthoc = 0.0
    if instance.geom_cache is not None and sel:
        n = 0
        for i, t_act in zip(sel, t_acts):
            geom = instance.geom_cache.lookup(i, t_act)
            sin_theta = math.sin(geom.theta)
            cos_theta_3 = math.cos(geom.theta) ** 3
            cos_psi_3 = geom.cos_psi ** 3
            f2_posthoc += sin_theta * geom.cos_psi
            f3_posthoc += cos_theta_3 * cos_psi_3
            n += 1
        if n > 0:
            f2_posthoc /= n
            f3_posthoc /= n
    elif sel:
        # Fallback: compute from elevation
        n = 0
        for obs in schedule:
            elev = obs.window.elevation
            phi = np.radians(90.0 - elev)
            theta = off_nadir_to_incidence(phi, instance.altitude_m)
            f2_posthoc += math.sin(theta)  # cosψ=1 assumed (no squint info)
            n += 1
        if n > 0:
            f2_posthoc /= n

    meta = {
        "solver": "b2_profit",
        "n_tasks": instance.N,
        "n_selected": len(sel),
        "f1": float(f1),
        "f2": f2_posthoc,
        "f3": f3_posthoc,
        "n_generations": n_generations,
        "population_size": population_size,
        "selected": sel,
        "t_actuals": t_acts,
        "phis_off_nadir": phis,
    }

    return SolverResult(
        schedule=schedule,
        score=float(f1),
        metadata=meta,
    )


# ═══════════════════════════════════════════════════════════════════════════
# GA-HS: Hot-Start GA with G-SM initial population seed
# ═══════════════════════════════════════════════════════════════════════════

from pymoo.core.sampling import Sampling

class _HotStartSampling(Sampling):
    """Inject G-SM solution + perturbations as initial GA population."""
    def __init__(self, x0: np.ndarray, n_pop: int):
        super().__init__()
        self.x0 = x0
        self.n_pop = n_pop

    def _do(self, problem, n_samples, **kwargs):
        n_var = problem.n_var
        pop = np.zeros((self.n_pop, n_var))
        pop[0] = self.x0
        rng = np.random.RandomState()
        for i in range(1, self.n_pop):
            noise = rng.normal(0, 0.5, n_var)  # std=0.5: unlock task selection
            pop[i] = np.clip(self.x0 + noise, 0.0, 1.0)
        return pop


def ga_hotstart_solver(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    hotstart_selected: List[int],
    hotstart_t_actuals: List[float],
    population_size: int = 100,
    n_generations: int = 200,
    seed: Optional[int] = None,
    instance: Optional[object] = None,
    **kwargs,
) -> SolverResult:
    """GA with hot-start initialization.

    Encodes a schedule as initial population seed, then runs GA
    to improve f1 via time search.  Same GA parameters as GA-P.
    """
    if seed is not None:
        np.random.seed(seed)

    if instance is None:
        instance = build_agile_instance(windows, targets, **kwargs)
        precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={"solver": "ga_hotstart", "n_tasks": 0, "f1": 0.0,
                       "f2": 0.0, "f3": 0.0, "n_selected": 0},
        )

    # Encode G-BL solution into 2N chromosome
    x0 = np.zeros(2 * instance.N)
    selected_set = set(hotstart_selected)
    for i in range(instance.N):
        if i in selected_set:
            x0[i] = 1.0
            x0[instance.N + i] = 0.0  # τ=0 = earliest feasible time (safe start)
    # τ values (hotstart_t_actuals) are ignored — G-BL uses incompatible C3 model

    problem = B2ProfitProblem(instance)
    # Use HotStartSampling: seed entire population around G-BL solution
    algorithm = GA(
        pop_size=population_size,
        sampling=_HotStartSampling(x0, population_size),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(prob=1.0 / (2 * instance.N), eta=20),
        eliminate_duplicates=False,
    )

    res = minimize(
        problem, algorithm,
        get_termination("n_gen", n_generations),
        seed=seed or 1,
        verbose=False, save_history=False,
    )

    if res.X is not None:
        x_best = res.X.reshape(-1) if res.X.ndim > 1 else res.X
        sel, t_acts, phis, f1 = _decode_b2_solution(x_best, instance)
    else:
        sel, t_acts, phis, f1 = [], [], [], 0.0

    schedule = tuple(_build_schedule_from_b2(instance, sel, t_acts))

    f2_posthoc = 0.0
    f3_posthoc = 0.0
    if instance.geom_cache is not None and sel:
        n_sel = 0
        for i, t_act in zip(sel, t_acts):
            geom = instance.geom_cache.lookup(i, t_act)
            sin_theta = math.sin(geom.theta)
            cos_theta_3 = math.cos(geom.theta) ** 3
            cos_psi_3 = geom.cos_psi ** 3
            f2_posthoc += sin_theta * geom.cos_psi
            f3_posthoc += cos_theta_3 * cos_psi_3
            n_sel += 1
        if n_sel > 0:
            f2_posthoc /= n_sel
            f3_posthoc /= n_sel
    elif sel:
        n_sel = 0
        for obs in schedule:
            elev = obs.window.elevation
            phi = np.radians(90.0 - elev)
            theta = off_nadir_to_incidence(phi, instance.altitude_m)
            f2_posthoc += math.sin(theta)
            n_sel += 1
        if n_sel > 0:
            f2_posthoc /= n_sel

    meta = {
        "solver": "ga_hotstart",
        "n_tasks": instance.N,
        "n_selected": len(sel),
        "f1": float(f1),
        "f2": f2_posthoc,
        "f3": f3_posthoc,
        "n_generations": n_generations,
        "population_size": population_size,
        "selected": sel,
        "t_actuals": t_acts,
        "phis_off_nadir": phis,
    }

    return SolverResult(
        schedule=schedule,
        score=float(f1),
        metadata=meta,
    )


def b2_profit_solver_bl_seeded(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    population_size: int = 100,
    n_generations: int = 200,
    seed: Optional[int] = None,
    **kwargs,
) -> SolverResult:
    """GA-P with G-BL hot-start: seed GA population from G-BL schedule."""
    from sar_sim.solver.baselines import baseline_b1

    # Build instance first (needed for unified C3 transition model)
    instance = build_agile_instance(windows, targets, **kwargs)
    precompute_geometry(instance, step_s=10.0)

    b1 = baseline_b1(windows, targets, instance=instance)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}

    hotstart_selected: List[int] = []
    hotstart_t_actuals: List[float] = []
    seen = set()
    for obs in b1.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx:
            idx = target_to_idx[tid]
            if idx not in seen:
                seen.add(idx)
                hotstart_selected.append(idx)
                hotstart_t_actuals.append(0.0)  # dummy — GA will search time

    return ga_hotstart_solver(
        windows, targets,
        hotstart_selected=hotstart_selected,
        hotstart_t_actuals=hotstart_t_actuals,
        population_size=population_size,
        n_generations=n_generations,
        seed=seed,
        instance=instance,
        **kwargs,
    )
