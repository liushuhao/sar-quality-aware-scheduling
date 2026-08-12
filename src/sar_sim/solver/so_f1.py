"""GA-P: Single-Objective Profit Maximizer (so_f1.py).

Implements the GA-P baseline from the problem formalization (§6 GA-P):
    max f1(x,t) = Σ x_i * p_i   s.t. C2--C4

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
from sar_sim.verification.constraints import ConstraintVerifier

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
    Constraints C2--C4 are enforced via aggregated penalty (same as MOEA).
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
                    # Fallback to compute_full_attitude if cache unavailable.
                    # Only phi (off-nadir) is needed here for the C2 transition
                    # model's legacy fallback; C1 (incidence + squint) is
                    # already enforced at window-generation time.
                    if inst.geom_cache is not None:
                        geom = inst.geom_cache.lookup(i, t_act)
                        phi = geom.phi
                    else:
                        roll, _, _ = compute_full_attitude(
                            task, t_act, 1.0, inst)
                        phi = abs(roll)
                    phi_list.append(phi)

                    # Encoding validity: the full observation interval
                    # [t_act, t_act+duration] must lie within one visibility
                    # window (C1 enforced at generation; this catches straddle
                    # or past-end intervals on short windows).
                    in_any, gap = task.interval_window_state(t_act)
                    if not in_any:
                        g += gap / max(task.duration, 1.0)

            # C2: attitude maneuver and non-overlap between consecutive tasks
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
                    t_b = ordered[k + 1][1]
                    task_a = inst.tasks[i_a]
                    task_b = inst.tasks[i_b]

                    # Required transition time
                    delta_eta = self._compute_los_separation(
                        task_a, t_a, task_b, t_b,
                    )
                    tau_trans = (delta_eta / inst.max_slew_rate
                                 + inst.settle_time)

                    # Enforce the transition on the DECODED times directly:
                    # the gap between A's end and B's decoded start must
                    # cover tau_trans. (RDR-004: previously the penalty was
                    # waived whenever B could in principle be delayed within
                    # its window, so decoded schedules kept overlapping
                    # observations and reported metrics used infeasible
                    # timings.)
                    gap = t_b - (t_a + task_a.duration)
                    if gap < tau_trans:
                        g += (tau_trans - gap) / max(task_b.duration, 1.0)

            # C3: energy budget
            energy_used = sum(
                inst.tasks[i].energy for i in range(N) if selected[i])
            if energy_used > inst.energy_budget:
                g += (energy_used - inst.energy_budget) / inst.energy_budget

            # C4: memory budget
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

        # Find the window that best contains the full observation interval
        best_window = None
        best_dist = float("inf")
        for w in task.windows:
            w_start = w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start
            w_end = w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end
            if w_start <= t_act and t_act + task.duration <= w_end:
                # This window contains the full interval
                best_window = w
                break
            # Track closest window
            dist = min(abs(w_start - t_act),
                       abs(w_end - (t_act + task.duration)))
            if dist < best_dist:
                best_dist = dist
                best_window = w

        if best_window is not None:
            # Match the source window's tz. Naive windows use naive
            # fromtimestamp (local) — the exact inverse of naive
            # .timestamp(); utcfromtimestamp would introduce a tz shift.
            if best_window.t_start.tzinfo is not None:
                obs_start = datetime.fromtimestamp(t_act, tz=timezone.utc)
            else:
                obs_start = datetime.fromtimestamp(t_act)
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
    C2--C4 constraints.

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
        seed=(seed if seed is not None else 1),
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
            cos_xi_3 = math.cos(geom.phi) ** 3
            f2_posthoc += math.sqrt(max(geom.cos_psi ** 2 - math.cos(geom.phi) ** 2, 0.0))
            f3_posthoc += cos_xi_3
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
    def __init__(self, x0: np.ndarray, n_pop: int, seed: int = 1):
        super().__init__()
        self.x0 = x0
        self.n_pop = n_pop
        self.seed = seed

    def _do(self, problem, n_samples, **kwargs):
        n_var = problem.n_var
        pop = np.zeros((self.n_pop, n_var))
        pop[0] = self.x0
        # Deterministic RNG (reuse solver seed); previously RandomState() used
        # entropy, making hot-start noise non-reproducible.
        rng = np.random.RandomState(self.seed)
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
    # Build a map: task_idx -> t_actual for computing proper τ values
    t_actual_map = {}
    for k, task_idx in enumerate(hotstart_selected):
        if k < len(hotstart_t_actuals):
            t_actual_map[task_idx] = hotstart_t_actuals[k]
    for i in range(instance.N):
        if i in selected_set:
            x0[i] = 1.0
            task = instance.tasks[i]
            if i in t_actual_map and task.time_span > 0:
                # Compute τ from G-BL's actual observation time so the seed
                # has realistic timings (reduces spurious C2 violations that
                # occurred when τ was hard-coded to 0).
                tau = (t_actual_map[i] - task.t_earliest) / task.time_span
                x0[instance.N + i] = max(0.0, min(1.0, tau))
            else:
                x0[instance.N + i] = 0.5  # mid-range fallback

    problem = B2ProfitProblem(instance)
    # Use HotStartSampling: seed entire population around G-BL solution
    algorithm = GA(
        pop_size=population_size,
        sampling=_HotStartSampling(x0, population_size, (seed if seed is not None else 1)),
        crossover=SBX(prob=0.9, eta=20),
        mutation=PM(prob=0.1, eta=20),
        eliminate_duplicates=False,
    )

    res = minimize(
        problem, algorithm,
        get_termination("n_gen", n_generations),
        seed=(seed if seed is not None else 1),
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
            cos_xi_3 = math.cos(geom.phi) ** 3
            f2_posthoc += math.sqrt(max(geom.cos_psi ** 2 - math.cos(geom.phi) ** 2, 0.0))
            f3_posthoc += cos_xi_3
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

    # Post-hoc constraint verification (with t_actual for C2).
    # Unlike MOEA (which filters out infeasible frontier solutions), GA-P is
    # single-objective with one best solution — we repair via delay-repair
    # (_enforce_c2_transitions) and recompute f1/f2/f3, rather than discard.
    if sel:
        phi_full = np.zeros(instance.N, dtype=float)
        t_actual_full = np.zeros(instance.N, dtype=float)
        for idx, task_idx in enumerate(sel):
            phi_full[task_idx] = phis[idx] if idx < len(phis) else 0.0
            t_actual_full[task_idx] = t_acts[idx] if idx < len(t_acts) else 0.0
        verifier = ConstraintVerifier(instance)
        report = verifier.verify_solution(sel, phi_full, t_actual=t_actual_full)
        meta["constraint_feasible"] = report.overall_pass
        meta["n_constraints_failed"] = report.n_failed

        # If C2 violated, repair by enforcing transitions and recompute
        if not report.overall_pass and "C2" in report.results and not report.results["C2"].passed:
            from sar_sim.solver.baselines import _enforce_c2_transitions
            repaired = _enforce_c2_transitions(list(schedule), instance=instance)
            if len(repaired) < len(schedule):
                schedule = tuple(repaired)
                # Recompute f1/f2/f3 from repaired schedule
                target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
                f1 = 0.0
                f2_num = 0.0
                f3_num = 0.0
                n_repaired = 0
                for obs in repaired:
                    tid = obs.window.target_id
                    if tid not in target_to_idx:
                        continue
                    task_idx = target_to_idx[tid]
                    task = instance.tasks[task_idx]
                    f1 += task.priority
                    t_act = obs.t_actual_start
                    t_act_float = t_act.timestamp() if hasattr(t_act, 'timestamp') else float(t_act)
                    if instance.geom_cache is not None:
                        geom = instance.geom_cache.lookup(task_idx, t_act_float)
                        f2_num += math.sqrt(max(geom.cos_psi ** 2 - math.cos(geom.phi) ** 2, 0.0))
                        f3_num += math.cos(geom.phi) ** 3
                    n_repaired += 1
                if n_repaired > 0:
                    f2_posthoc = f2_num / n_repaired
                    f3_posthoc = f3_num / n_repaired
                meta["f1"] = float(f1)
                meta["f2"] = f2_posthoc
                meta["f3"] = f3_posthoc
                meta["n_selected"] = n_repaired
                meta["repaired"] = True
                # Re-verify after repair using the repaired schedule's own
                # times (rebuild t_actual rather than reuse pre-repair values).
                repaired_idx = []
                repaired_t = np.zeros(instance.N, dtype=float)
                repaired_phi = np.zeros(instance.N, dtype=float)
                for obs in repaired:
                    tid = obs.window.target_id
                    if tid not in target_to_idx:
                        continue
                    ti = target_to_idx[tid]
                    repaired_idx.append(ti)
                    tt = obs.t_actual_start
                    repaired_t[ti] = tt.timestamp() if hasattr(tt, 'timestamp') else float(tt)
                    if instance.geom_cache is not None:
                        repaired_phi[ti] = instance.geom_cache.lookup(ti, repaired_t[ti]).phi
                report2 = verifier.verify_solution(
                    repaired_idx, repaired_phi, t_actual=repaired_t,
                )
                meta["constraint_feasible"] = report2.overall_pass
                meta["n_constraints_failed"] = report2.n_failed
    else:
        meta["constraint_feasible"] = True
        meta["n_constraints_failed"] = 0

    # Note: sel/phis/t_acts are NOT updated after repair; downstream must
    # use schedule + meta, not these locals.
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
    orbit_raan_rad: Optional[float] = None,
    orbit_epoch_s: Optional[float] = None,
    orbit_inclination_rad: Optional[float] = None,
    **kwargs,
) -> SolverResult:
    """GA-P with G-BL hot-start: seed GA population from G-BL schedule."""
    from sar_sim.solver.baselines import baseline_b1

    if orbit_raan_rad is not None:
        kwargs["orbit_raan_rad"] = orbit_raan_rad
    if orbit_epoch_s is not None:
        kwargs["orbit_epoch_s"] = orbit_epoch_s
    if orbit_inclination_rad is not None:
        kwargs["orbit_inclination_rad"] = orbit_inclination_rad

    # Build instance first (needed for unified C3 transition model)
    instance = build_agile_instance(windows, targets, **kwargs)
    precompute_geometry(instance, step_s=10.0)

    b1 = baseline_b1(windows, targets, instance=instance)
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}

    # Recompute G-BL f1 using only tasks present in the instance, so it is
    # directly comparable to the GA's f1 (which also only counts instance
    # tasks).  b1.f1 may include observations for targets filtered out
    # during build_agile_instance, making it incomparable.
    gbl_f1 = 0.0
    for obs in b1.schedule:
        tid = obs.window.target_id
        if tid in target_to_idx:
            gbl_f1 += instance.tasks[target_to_idx[tid]].priority

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
                # Pass G-BL's actual observation time so the GA seed has
                # realistic τ values (not τ=0 which causes spurious C2
                # violations and poor hot-start quality).
                t_act = obs.t_actual_start
                t_act_float = t_act.timestamp() if hasattr(t_act, 'timestamp') else float(t_act)
                hotstart_t_actuals.append(t_act_float)

    result = ga_hotstart_solver(
        windows, targets,
        hotstart_selected=hotstart_selected,
        hotstart_t_actuals=hotstart_t_actuals,
        population_size=population_size,
        n_generations=n_generations,
        seed=seed,
        instance=instance,
        **kwargs,
    )

    # "Never worse than G-BL" guarantee: if the GA result (after repair)
    # has lower f1 than G-BL, return G-BL's schedule with proper metadata.
    ga_f1 = float(result.metadata.get("f1", 0.0))
    if ga_f1 < gbl_f1 and b1.schedule:
        # Rebuild metadata from G-BL schedule using the same instance
        gbl_sel = []
        gbl_t_acts = []
        gbl_phis = []
        gbl_f1_recomputed = 0.0
        gbl_f2 = 0.0
        gbl_f3 = 0.0
        gbl_n = 0
        seen_gbl = set()
        for obs in b1.schedule:
            tid = obs.window.target_id
            if tid not in target_to_idx:
                continue
            task_idx = target_to_idx[tid]
            if task_idx in seen_gbl:
                continue
            seen_gbl.add(task_idx)
            task = instance.tasks[task_idx]
            gbl_sel.append(task_idx)
            t_act = obs.t_actual_start
            t_act_float = t_act.timestamp() if hasattr(t_act, 'timestamp') else float(t_act)
            gbl_t_acts.append(t_act_float)
            gbl_f1_recomputed += task.priority
            if instance.geom_cache is not None:
                geom = instance.geom_cache.lookup(task_idx, t_act_float)
                gbl_phis.append(geom.phi)
                gbl_f2 += math.sqrt(max(geom.cos_psi ** 2 - math.cos(geom.phi) ** 2, 0.0))
                gbl_f3 += math.cos(geom.phi) ** 3
            gbl_n += 1
        if gbl_n > 0:
            gbl_f2 /= gbl_n
            gbl_f3 /= gbl_n

        # Verify G-BL schedule constraints
        from sar_sim.verification.constraints import ConstraintVerifier
        phi_full = np.zeros(instance.N, dtype=float)
        t_actual_full = np.zeros(instance.N, dtype=float)
        for idx, task_idx in enumerate(gbl_sel):
            phi_full[task_idx] = gbl_phis[idx] if idx < len(gbl_phis) else 0.0
            t_actual_full[task_idx] = gbl_t_acts[idx] if idx < len(gbl_t_acts) else 0.0
        verifier = ConstraintVerifier(instance)
        report = verifier.verify_solution(gbl_sel, phi_full, t_actual=t_actual_full)

        result.metadata["f1"] = gbl_f1_recomputed
        result.metadata["f2"] = gbl_f2
        result.metadata["f3"] = gbl_f3
        result.metadata["n_selected"] = gbl_n
        result.metadata["selected"] = gbl_sel
        result.metadata["t_actuals"] = gbl_t_acts
        result.metadata["phis_off_nadir"] = gbl_phis
        result.metadata["constraint_feasible"] = report.overall_pass
        result.metadata["n_constraints_failed"] = report.n_failed
        result.metadata["used_gbl_fallback"] = True
        result = SolverResult(
            schedule=b1.schedule,
            score=gbl_f1_recomputed,
            metadata=result.metadata,
        )

    return result
