"""MOEA solver for agile SAR scheduling via pymoo (NSGA-III).

Formulates the tri-objective scheduling problem (P) from the formalization
as a pymoo.Problem, then solves with NSGA-III to find the Pareto frontier.

Decision variables:
  Single-satellite (2N encoding, n_sats=1):
    x[0..N-1]    ∈ [0,1]   task selection (>0.5 = selected)
    τ[0..N-1]    ∈ [0,1]   normalized observation time
      → t_actual_i = t_earliest_i + τ_i * (t_latest_i - d_i - t_earliest_i)

  Multi-satellite (3N encoding, n_sats>1):
    x[0..N-1]    ∈ [0,1]   task selection (>0.5 = selected)
    τ[0..N-1]    ∈ [0,1]   normalized observation time
    sat[0..N-1]  ∈ [0,1]   satellite assignment (discretized to 0..n_sats-1)
      → sat_id_i = floor(sat_i * n_sats)

Geometry (off-nadir φ, squint ψ_sq) is derived from t_actual via compute_full_attitude().
This replaces the old 3N Plan-A encoding (x + direction + phi_abs).

Objectives (v2026-06-22: split by physical mechanism, not spatial direction):
  f1 = Σ x_i * p_i                        coverage-weighted profit (O1)
  f2 = Σ x_i * sin(θ_i)·cos(ψ_sq,i)       geometric resolution (ground-range × azimuth) (O2)
  f3 = Σ x_i * cos³(θ_i)·cos³(ψ_sq,i)     NESZ radiometric quality (O3)

MOEA-2 optimizes (f1, f2); MOEA-3 optimizes (f1, f2, f3).
Both depend on θ and ψ_sq via observation time t_i, making them
geometrically coupled but physically orthogonal (f2 resists small θ
via sinθ, f3 favors small θ via cos³θ).

Constraints (penalty-based):
  MOEA-2: t_actual within at least one visibility window
  MOEA-3: resolution requirement (θ(φ) ≥ θ_min_res) — incidence computed from φ
  C3: attitude transition feasibility (LOS-angle model via compute_transition_time)
      Multi-sat: C3 checked per-satellite (within each sat's task group)
  C4: energy budget — per-satellite for multi-sat, global for single-sat
  C5: memory budget — per-satellite for multi-sat, global for single-sat
  C6: no target duplication across satellites (multi-sat only)
  C7: squint angle ≤ max_squint_deg (from SARInstrument)
"""

from dataclasses import dataclass, field
import math
import numpy as np
from typing import List, Dict, Optional, Tuple

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from sar_sim.types import ObservationWindow, GroundTarget, ScheduledObservation, SolverResult
from sar_sim.metrics.nesz import (
    quality_score,
    off_nadir_to_incidence,
)

# ─── Shared types (extracted to solver/types.py for pymoo-free imports) ──
from sar_sim.solver.types import (
    AgileTask,
    AgileSARInstance,
    build_agile_instance,
    compute_transition_time,
    compute_full_attitude,
    compute_los_separation,  # cached LOS computation
    precompute_geometry,
)

# Precomputed constant for hot-path
_MAX_SQUINT_RAD = np.radians(45.0)


# ─── pymoo Problem ───────────────────────────────────────────────────────

class SARSchedulingProblem(Problem):
    """Tri-objective agile SAR scheduling problem for pymoo.

    Encoding (2N variables):
      x[0:N]     ∈ [0,1]     task selection (>0.5 = selected)
      τ[N:2N]    ∈ [0,1]     normalized observation time
        → t_actual_i = a_i + τ_i * (b_i - d_i - a_i)

    Geometry (off-nadir φ, squint ψ_sq) is derived from t_actual via compute_full_attitude().
    Roll (off-nadir φ) and squint (ψ_sq) are computed from the full 3-axis
    LOS geometry at the actual observation time.

    Three objectives (maximized via negation for pymoo minimization):
      f1 = Σ x_i · p_i                          coverage profit (O1)
      f2 = Σ x_i · sin(θ_i)·cos(ψ_sq,i)        geometric resolution (O2)
      f3 = Σ x_i · cos³(θ_i)·cos³(ψ_sq,i)      NESZ radiometric (O3)
    where φ_i, θ_i, ψ_sq_i come from compute_full_attitude(task, t_actual, ...)
    """

    def __init__(self, instance: AgileSARInstance, penalty_coeff: float = 1e5,
                 n_obj: int = 3, f1_gbl: float = 1.0, n_sats: int = 1):
        self.instance = instance
        self.penalty_coeff = penalty_coeff
        self.n_obj = n_obj
        self.f1_gbl = max(f1_gbl, 1.0)  # avoid div by zero
        self.n_sats = n_sats

        N = instance.N
        # Variables: N selection + N tau + N sat_assignment = 2N + N_sat_vars
        # When n_sats=1, sat vars are omitted (backward compatible 2N encoding)
        # When n_sats>1, sat vars ∈ [0,1] discretized to 0..n_sats-1
        if n_sats > 1:
            n_var = 3 * N  # 2N + N (sat assignment)
        else:
            n_var = 2 * N  # backward-compatible 2N
        # xl, xu: all variables in [0, 1]
        xl = np.zeros(n_var)
        xu = np.ones(n_var)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_ieq_constr=1,  # one aggregated constraint violation
            xl=xl,
            xu=xu,
        )

    def _decode_t_actual(self, tau_i: float, task: AgileTask) -> float:
        """Decode tau in [0,1] to actual start time (epoch seconds)."""
        return task.t_earliest + tau_i * task.time_span

    def _evaluate(self, X, out, *args, **kwargs):
        """Evaluate population.  X shape: (pop_size, 2N) or (pop_size, 3N)."""
        n_pop = X.shape[0]
        N = self.instance.N
        inst = self.instance
        n_sats = self.n_sats

        f1 = np.zeros(n_pop)  # coverage profit (normalized by f1_gbl)
        f2_num = np.zeros(n_pop)  # numerator for mean geometric resolution
        f3_num = np.zeros(n_pop)  # numerator for mean NESZ radiometric
        n_sel = np.zeros(n_pop)   # denominator (task count)
        G  = np.zeros(n_pop)  # constraint violation

        for p in range(n_pop):
            x_bin = X[p, :N]          # task selection
            tau = X[p, N:2*N]        # normalized time

            # Threshold binary: >0.5 = selected
            selected = x_bin > 0.5

            # ── Decode satellite assignments (multi-sat only) ──────────
            sat_id = np.zeros(N, dtype=np.int32)
            if n_sats > 1:
                sat_raw = X[p, 2*N:3*N]
                sat_id = np.clip(np.floor(sat_raw * n_sats).astype(np.int32), 0, n_sats - 1)

            # Pre-compute actual times and geometry for selected tasks
            t_actual_dict: Dict[int, float] = {}
            phi_dict: Dict[int, float] = {}
            squint_dict: Dict[int, float] = {}

            # ── Merged: geometry lookup + objectives in single pass ──
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
                        f2_num[p] += math.sin(geom.theta) * geom.cos_psi
                        f3_num[p] += (math.cos(geom.theta) ** 3) * (geom.cos_psi ** 3)
                    else:
                        roll, _, psi_sq = compute_full_attitude(task, t_act, 1.0, inst)
                        phi_dict[i] = abs(roll)
                        squint_dict[i] = psi_sq
                        theta_i = off_nadir_to_incidence(phi_dict[i], inst.altitude_m)
                        cos_psi_i = math.cos(squint_dict[i])
                        f2_num[p] += math.sin(theta_i) * cos_psi_i
                        f3_num[p] += (math.cos(theta_i) ** 3) * (cos_psi_i ** 3)

            # ── Constraints ─────────────────────────────────────────
            g = 0.0

            # MOEA-2 + MOEA-3: each selected task's |φ| must be in [φ_min_i, φ_max_i]
            # and ≥ φ_min_res.
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

                    # MOEA-2: t_actual must be within at least one visibility window
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

                    # C7: squint angle constraint
                    if squint_dict[i] > _MAX_SQUINT_RAD:
                        g += squint_dict[i] - _MAX_SQUINT_RAD

            # C6: no target duplication across satellites (multi-sat only)
            if n_sats > 1:
                target_sat_map: Dict[str, int] = {}  # target_id → first sat_id
                for i in range(N):
                    if selected[i]:
                        tid = inst.tasks[i].target_id
                        sid = int(sat_id[i])
                        if tid in target_sat_map and target_sat_map[tid] != sid:
                            g += self.penalty_coeff  # hard C6 violation
                        else:
                            target_sat_map[tid] = sid

            # C3: transition feasibility between consecutive selected tasks
            sel_indices = [i for i in range(N) if selected[i]]
            if n_sats > 1:
                # Per-satellite C3: group tasks by satellite, check within each
                sat_groups: Dict[int, List[int]] = {}
                for i in sel_indices:
                    sid = int(sat_id[i])
                    sat_groups.setdefault(sid, []).append(i)

                for sid, task_idxs in sat_groups.items():
                    if len(task_idxs) > 1:
                        task_idxs.sort(key=lambda i: t_actual_dict[i])
                        for k in range(len(task_idxs) - 1):
                            i_a = task_idxs[k]
                            i_b = task_idxs[k + 1]
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
            elif len(sel_indices) > 1:
                # Original single-satellite C3
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

            # C4: energy budget (per-sat for multi-sat, global for single-sat)
            if n_sats > 1:
                per_sat_energy = np.zeros(n_sats)
                per_sat_budget = inst.energy_budget / n_sats
                for i in range(N):
                    if selected[i]:
                        sid = int(sat_id[i])
                        per_sat_energy[sid] += inst.tasks[i].energy
                for sid in range(n_sats):
                    if per_sat_energy[sid] > per_sat_budget:
                        g += (per_sat_energy[sid] - per_sat_budget) / max(per_sat_budget, 1.0)
            else:
                energy_used = sum(task.energy for i, task in enumerate(inst.tasks) if selected[i])
                if energy_used > inst.energy_budget:
                    g += (energy_used - inst.energy_budget) / inst.energy_budget

            # C5: memory budget (per-sat for multi-sat, global for single-sat)
            if n_sats > 1:
                per_sat_memory = np.zeros(n_sats)
                per_sat_mem_budget = inst.memory_budget / n_sats
                for i in range(N):
                    if selected[i]:
                        sid = int(sat_id[i])
                        per_sat_memory[sid] += inst.tasks[i].memory
                for sid in range(n_sats):
                    if per_sat_memory[sid] > per_sat_mem_budget:
                        g += (per_sat_memory[sid] - per_sat_mem_budget) / max(per_sat_mem_budget, 1.0)
            else:
                memory_used = sum(task.memory for i, task in enumerate(inst.tasks) if selected[i])
                if memory_used > inst.memory_budget:
                    g += (memory_used - inst.memory_budget) / inst.memory_budget

            # ── At-least-1-task penalty ────────────────────────────
            if n_sel[p] == 0:
                g += 1e5

            G[p] = g

        # pymoo always minimizes; we convert maximization via negation
        # f1: normalized by G-BL reference (f1_gbl)
        # f2, f3: means (per-task averages), f2=f3=0 when n_selected=0
        f1_norm = f1 / self.f1_gbl
        f2_mean = np.divide(f2_num, n_sel, out=np.zeros_like(f2_num), where=n_sel > 0)
        f3_mean = np.divide(f3_num, n_sel, out=np.zeros_like(f3_num), where=n_sel > 0)
        if self.n_obj >= 3:
            out["F"] = np.column_stack([-f1_norm, -f2_mean, -f3_mean])
        else:
            out["F"] = np.column_stack([-f1_norm, -f2_mean])  # MOEA-2: f1+f2 (geometric resolution)
        out["G"] = G.reshape(-1, 1)


# ─── Post-processing: decode solutions ───────────────────────────────────

def _build_schedule_from_moea(
    instance: AgileSARInstance,
    selected_indices: List[int],
    t_actuals: List[float],
) -> List[ScheduledObservation]:
    """Convert MOEA solution indices and times into ScheduledObservation list.

    For each selected task, finds the window that best contains t_actual.

    Args:
        instance: the agile SAR instance
        selected_indices: task indices selected in the solution
        t_actuals: actual observation times (one per selected task)

    Returns:
        list of ScheduledObservation, sorted by start time
    """
    from datetime import datetime, timedelta, timezone

    observations = []
    for idx, t_act in zip(selected_indices, t_actuals):
        task = instance.tasks[idx]

        # Find the window that best contains t_act
        best_window = None
        best_dist = float("inf")
        wt = task.window_times
        if wt:
            for (w_start, w_end), w in zip(wt, task.windows):
                if w_start <= t_act <= w_end:
                    best_window = w
                    break
                dist = min(abs(t_act - w_start), abs(t_act - w_end))
                if dist < best_dist:
                    best_dist = dist
                    best_window = w
        else:
            for w in task.windows:
                w_start = w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start
                w_end = w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end
                if w_start <= t_act <= w_end:
                    best_window = w
                    break
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

    # Sort by start time for downstream processing
    observations.sort(key=lambda o: o.t_actual_start)
    return observations


def decode_solution(
    X: np.ndarray,
    instance: AgileSARInstance,
    f1_gbl: float = 1.0,
    n_sats: int = 1,
) -> Tuple[List[int], np.ndarray, float, float, float, List[int]]:
    """Decode a pymoo solution vector into interpretable form.

    Args:
        X: solution vector of length 2N or 3N (new encoding)
        instance: the agile SAR instance
        f1_gbl: G-BL f1 reference for normalization
        n_sats: number of satellites (1 = 2N encoding, >1 = 3N encoding)

    Returns:
        (selected_task_indices, off_nadir_angles, f1_norm, f2_mean, f3_mean, sat_assignments)
    """
    N = instance.N
    x_bin = X[:N]
    tau = X[N:2*N]

    sat_ids = []
    if n_sats > 1 and len(X) >= 3 * N:
        sat_raw = X[2*N:3*N]
        sat_ids = np.clip(np.floor(sat_raw * n_sats).astype(int), 0, n_sats - 1).tolist()
    else:
        sat_ids = [0] * N

    selected = []
    phis = []
    t_actuals = []
    f1_raw = 0.0
    f2_num = 0.0
    f3_num = 0.0
    n_sel = 0

    for i in range(N):
        if x_bin[i] > 0.5:
            selected.append(i)
            task = instance.tasks[i]
            t_act = task.t_earliest + tau[i] * task.time_span
            t_actuals.append(t_act)
            n_sel += 1

            if instance.geom_cache is not None:
                geom = instance.geom_cache.lookup(i, t_act)
                phis.append(geom.phi)
                f2_num += math.sin(geom.theta) * geom.cos_psi
                f3_num += (math.cos(geom.theta) ** 3) * (geom.cos_psi ** 3)
            else:
                roll, _, psi_sq = compute_full_attitude(task, t_act, 1.0, instance)
                phis.append(abs(roll))
                theta = off_nadir_to_incidence(abs(roll), instance.altitude_m)
                f2_num += math.sin(theta) * math.cos(psi_sq)
                f3_num += (math.cos(theta) ** 3) * (math.cos(psi_sq) ** 3)

            f1_raw += task.priority

    f1_norm = f1_raw / max(f1_gbl, 1.0)
    f2_mean = f2_num / n_sel if n_sel > 0 else 0.0
    f3_mean = f3_num / n_sel if n_sel > 0 else 0.0
    return selected, np.array(phis), f1_norm, f2_mean, f3_mean, sat_ids


def solutions_to_frontier(
    X_pop: np.ndarray,
    instance: AgileSARInstance,
) -> List[dict]:
    """Convert pymoo population to a list of Pareto solutions.

    Args:
        X_pop: population matrix (pop_size × 2N) or single solution (2N,)
        instance: agile SAR instance

    Returns:
        list of dicts with keys: selected, phis, f1, f2, f3, n_tasks
    """
    # Handle 1D input (single solution from single-objective GA)
    if X_pop.ndim == 1:
        X_pop = X_pop.reshape(1, -1)
    frontier = []
    for p in range(X_pop.shape[0]):
        sel, phis, f1, f2, f3, _sat_ids = decode_solution(X_pop[p], instance, getattr(instance, 'f1_gbl', 1.0))
        frontier.append({
            "selected": sel,
            "phis": phis.tolist() if isinstance(phis, np.ndarray) else list(phis),
            "f1": f1,
            "f2": f2,
            "f3": f3,
            "n_tasks": len(sel),
        })
    # Deduplicate by (f1, f2, f3)
    seen = set()
    unique = []
    for s in frontier:
        key = (round(s["f1"], 6), round(s["f2"], 6), round(s["f3"], 6))
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


# ─── Main Solver Entry Point ─────────────────────────────────────────────

def moea_solver(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    population_size: int = 100,
    n_generations: int = 200,
    seed: Optional[int] = None,
    n_ref_dirs: int = 12,
    n_obj: int = 3,
    resolution_reqs: Optional[List[float]] = None,
    hotstart_individual: Optional[np.ndarray] = None,
    hotstart_sigma: float = 0.5,
    n_sats: int = 1,
    **kwargs,
) -> SolverResult:
    """MOEA solver using NSGA-III for multi-objective agile SAR scheduling.

    f1 = normalized coverage profit (f1_raw / f1_G-BL).
    f2 = mean geometric resolution (mean(sinθ·cosψ_sq)).
    f3 = mean NESZ radiometric quality (mean(cos³θ·cos³ψ_sq)).

    Args:
        windows: candidate observation windows
        targets: ground targets
        population_size: NSGA-III population size
        n_generations: number of generations
        seed: random seed
        n_ref_dirs: number of reference directions for NSGA-III (Das-Dennis partitions)
        n_obj: number of objectives (2 = f1+f2 geometric resolution, 3 = f1+f2+f3)
        resolution_reqs: per-target resolution requirements
        hotstart_individual: optional 2N (or 3N for multi-sat) chromosome to seed initial population
        hotstart_sigma: std of Gaussian noise added to hot-start seed (default 0.5)
        n_sats: number of satellites (1 = single-sat, >1 = multi-sat constellation with 3N encoding)
        **kwargs: passed to build_agile_instance

    Returns:
        SolverResult with Pareto frontier in metadata
    """
    if seed is not None:
        np.random.seed(seed)

    # Build problem instance (or reuse pre-built)
    prebuilt = kwargs.pop('instance', None)
    # f1_gbl is a solver-level kwarg; pop it before forwarding the rest to
    # build_agile_instance, which does not accept it.
    f1_gbl_override = kwargs.pop('f1_gbl', None)
    if prebuilt is not None:
        instance = prebuilt
    else:
        instance = build_agile_instance(windows, targets, resolution_reqs=resolution_reqs, **kwargs)
        precompute_geometry(instance, step_s=10.0)

    if instance.N == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={"solver": "moea_nsga3", "n_tasks": 0, "frontier": []},
        )

    # ── Compute f1_gbl (G-BL reference for f1 normalization) ──────
    if f1_gbl_override is not None:
        f1_gbl = f1_gbl_override
    else:
        from .baselines import baseline_b1
        gbl = baseline_b1(windows, targets, instance=instance)
        f1_gbl = max(gbl.f1, 1.0)
    instance.f1_gbl = f1_gbl

    # Create pymoo problem
    problem = SARSchedulingProblem(instance, n_obj=n_obj, f1_gbl=f1_gbl, n_sats=n_sats)

    # NSGA-III with Das-Dennis reference directions
    ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=n_ref_dirs)

    # ── Hot-start injection ────────────────────────────────────────────
    sampling = None
    if hotstart_individual is not None:
        from pymoo.core.sampling import Sampling
        class _MOEAHotStartSampling(Sampling):
            def __init__(self, x0, n_pop, sigma):
                super().__init__()
                self.x0 = x0
                self.n_pop = n_pop
                self.sigma = sigma
            def _do(self, problem, n_samples, **kwargs):
                pop = np.zeros((self.n_pop, problem.n_var))
                pop[0] = self.x0
                rng = np.random.RandomState()
                for i in range(1, self.n_pop):
                    noise = rng.normal(0, self.sigma, problem.n_var)
                    pop[i] = np.clip(self.x0 + noise, 0.0, 1.0)
                return pop
        sampling = _MOEAHotStartSampling(hotstart_individual, population_size, hotstart_sigma)

    algorithm = NSGA3(
        pop_size=population_size,
        ref_dirs=ref_dirs,
        sampling=sampling,
    ) if sampling is not None else NSGA3(
        pop_size=population_size,
        ref_dirs=ref_dirs,
    )

    termination = get_termination("n_gen", n_generations)

    # Run optimization
    res = minimize(
        problem,
        algorithm,
        termination,
        seed=seed or 1,
        verbose=False,
        save_history=False,
    )

    # Decode Pareto frontier
    x_source = None  # Will hold the X matrix used for decoding
    if res.X is not None:
        x_source = res.X
        # pymoo returns 1D for single-solution (e.g., GA); normalize to 2D
        if x_source.ndim == 1:
            x_source = x_source.reshape(1, -1)
        frontier = solutions_to_frontier(x_source, instance)
    else:
        # pymoo may return X=None when no feasible solution found
        # Try to get the last population from the algorithm
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

    # For SolverResult compatibility: pick the "knee" solution
    if frontier and x_source is not None:
        # Normalize objectives to [0, 1] across frontier
        f1_vals = np.array([s["f1"] for s in frontier])
        f1_range = f1_vals.max() - f1_vals.min() or 1.0
        f1_norm = (f1_vals - f1_vals.min()) / f1_range

        if n_obj >= 3:
            # MOEA-3: knee uses f1+f2+f3
            f2_vals = np.array([s["f2"] for s in frontier])
            f2_range = f2_vals.max() - f2_vals.min() or 1.0
            f2_norm = (f2_vals - f2_vals.min()) / f2_range
            f3_vals = np.array([s.get("f3", 0.0) for s in frontier])
            f3_range = f3_vals.max() - f3_vals.min() or 1.0
            f3_norm = (f3_vals - f3_vals.min()) / f3_range
            knee_idx = int(np.argmax(f1_norm + f2_norm + f3_norm))
        else:
            # MOEA-2: knee uses f1+f2
            f2_vals = np.array([s["f2"] for s in frontier])
            f2_range = f2_vals.max() - f2_vals.min() or 1.0
            f2_norm = (f2_vals - f2_vals.min()) / f2_range
            knee_idx = int(np.argmax(f1_norm + f2_norm))
        best = frontier[knee_idx]

        # Build ScheduledObservation list from the representative solution
        rep_x = x_source[knee_idx]
        # Decode t_actuals from 2N encoding
        rep_tau = rep_x[instance.N:2*instance.N]
        rep_t_actuals = []
        for i in best["selected"]:
            task = instance.tasks[i]
            t_act = task.t_earliest + rep_tau[i] * task.time_span
            rep_t_actuals.append(t_act)

        schedule = tuple(_build_schedule_from_moea(
            instance, best["selected"], rep_t_actuals,
        ))
    else:
        best = {"f1": 0.0, "f2": 0.0, "f3": 0.0, "n_tasks": 0, "selected": [], "phis": []}
        schedule = ()

    if n_obj >= 3:
        score = best["f1"] + best["f2"] + best.get("f3", 0.0)
    else:
        score = best["f1"] + best["f2"]

    meta = {
        "solver": "moea_nsga3",
        "n_tasks": instance.N,
        "n_selected": best["n_tasks"],
        "f1": best["f1"],  # normalized f1 (f1_raw / f1_gbl)
        "f1_raw": best.get("f1", 0.0) * f1_gbl,  # actual coverage profit
        "f1_gbl": f1_gbl,
        "f2": best["f2"],  # mean geometric resolution
        "f3": best.get("f3", 0.0),  # mean NESZ radiometric
        "n_generations": n_generations,
        "population_size": population_size,
        "frontier": frontier,
        "n_frontier_points": len(frontier),
        "n_obj": n_obj,
        "n_sats": n_sats,
    }
    if n_obj == 2:
        meta["f3_posthoc"] = best.get("f3", 0.0)

    return SolverResult(
        schedule=schedule,
        score=score,
        metadata=meta,
    )
