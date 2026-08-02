"""Baseline solvers for agile SAR scheduling comparison.

G-BL — No Quality Awareness (Fixed Nadir-Looking Greedy):
    Maximizes coverage profit with fixed side-looking angle (no angle
    selection). Greedy selection by earliest start time with C2 transition
    enforcement. Represents the standard AEOSSP formulation applied to SAR.

G-SQ — Proxy Quality (He2024IDRL-style) [DEPRECATED — not in current paper]:
    Single-objective with "coverage completeness" proxy as quality.
    f2_proxy = Σ x_i (count of scheduled tasks), which provides
    no discrimination beyond f1. Shows that optical-domain quality
    proxies are vacuous when applied to SAR.
    NOTE: G-SQ is equivalent to G-BL in practice — both maximize coverage
    profit without quality awareness. Removed from paper; kept for reference.

G-SM — Squint-Minimized Greedy:
    Greedy scheduling that selects the observation time within each task's
    visibility window that minimizes the squint angle ψ_sq (and thus
    maximizes azimuth resolution quality f3 = Σ cos ψ_sq).
    Uses GeomCache to evaluate squint at sampling points;
    falls back to θ-tracking for C2 feasibility when GeomCache unavailable.
"""

from dataclasses import dataclass, replace
from datetime import timedelta, datetime, timezone
import math
import numpy as np
from typing import List, Optional, Dict, Tuple

from sar_sim.types import (
    ObservationWindow,
    GroundTarget,
    ScheduledObservation,
    SolverResult,
)
from sar_sim.metrics.nesz import (
    quality_score,
    elevation_to_off_nadir,
    incidence_to_off_nadir,
    off_nadir_to_incidence,
)
from sar_sim.metrics.coverage import compute_f1_coverage
from sar_sim.solver.csp import (
    CSPInstance,
    build_csp_instance,
    schedule_from_indices,
    compute_solution_score,
    validate_solution,
)
from sar_sim.solver.types import (
    AgileSARInstance,
    GeomCache,
    _satellite_body_frame,
    _lat_lon_to_ecef,
    compute_los_separation,
)


@dataclass
class BaselineResult:
    """Structured result from a baseline solver.

    Mirrors SolverResult but carries both objectives for comparison.
    """
    schedule: List[ScheduledObservation]
    f1: float      # coverage profit
    f2: float      # geometric resolution (post-hoc)
    n_scheduled: int
    solver_name: str
    metadata: dict


# ─── C2 Attitude Transition Enforcement ──────────────────────────────────

# Scheduler-side guard band on the C2 gap test. The verifier recomputes gaps
# in float epoch seconds while the baseline mixes datetime arithmetic; the
# two can disagree by a few microseconds per boundary. A 10 ms pad (≈0.2 %
# of the 5 s settle time) makes every accepted schedule verify clean without
# meaningfully reducing schedulable density. It is applied only to the
# feasibility comparison, never added to the reported tau.
_C2_GATE_EPS = 0.01

def _c2_transition_los(
    target_id_a: str,
    t_a_s: float,
    target_id_b: str,
    t_b_s: float,
    instance: AgileSARInstance,
    max_slew_rate: float,
    settle_time: float,
) -> float:
    """Compute C2 transition time using full 3-axis LOS angular separation.

    Delegates to :func:`compute_los_separation`, the same cached LOS model
    used by the MOEA evaluator and the independent C2 verifier, so all three
    components agree bit-for-bit on tau (Eq. 4 in problem_formalization.md):

        tau = arccos(l_a . l_b / (|l_a| * |l_b|)) / omega_max + tau_settle

    Args:
        target_id_a, target_id_b: target identifiers
        t_a_s, t_b_s: observation times (epoch seconds)
        instance: problem instance with target_map and orbital params
        max_slew_rate: max angular rate (rad/s)
        settle_time: post-maneuver settling (s)

    Returns:
        transition time in seconds
    """
    task_a = instance.target_map[target_id_a]
    task_b = instance.target_map[target_id_b]
    target_a_ecef = _lat_lon_to_ecef(task_a.lat, task_a.lon)
    target_b_ecef = _lat_lon_to_ecef(task_b.lat, task_b.lon)
    tid_to_task = {t.target_id: t for t in instance.tasks}
    a_task = tid_to_task[target_id_a]
    b_task = tid_to_task[target_id_b]
    if instance.sat_position_cache is not None and instance.target_ecef_map:
        delta_eta = compute_los_separation(a_task, t_a_s, b_task, t_b_s, instance)
    else:
        _, _, _, sat_a_ecef = _satellite_body_frame(t_a_s, instance)
        _, _, _, sat_b_ecef = _satellite_body_frame(t_b_s, instance)
        los_a = target_a_ecef - sat_a_ecef
        los_b = target_b_ecef - sat_b_ecef
        cos_eta = np.dot(los_a, los_b) / (
            np.linalg.norm(los_a) * np.linalg.norm(los_b))
        cos_eta = np.clip(cos_eta, -1.0, 1.0)
        delta_eta = float(np.arccos(cos_eta))
    return delta_eta / max_slew_rate + settle_time


def _enforce_c2_transitions(
    observations: List[ScheduledObservation],
    max_slew_rate: float = 0.0524,   # approx 3 deg/s
    settle_time: float = 5.0,        # seconds
    instance: Optional[AgileSARInstance] = None,
) -> List[ScheduledObservation]:
    """Filter observations to satisfy C2 attitude transition feasibility.

    Sorts by start time, then greedily keeps observations that have
    sufficient inter-observation gap for attitude slewing.

    When ``instance`` is provided, uses the FULL 3-axis LOS angular
    separation model (Eq. 4 from problem_formalization.md):
        tau = max(|delta_phi|, |delta_theta|, |delta_psi|) / omega_max + tau_settle
    This is unified with the MOEA transition model.
    When ``instance`` is None, falls back to simple phi-diff.

    **Start-time flexibility**: If the gap at the solver-assigned start time
    is insufficient, the observation start is delayed within [t_start, t_end]
    to make room for the transition. Task is only rejected if no feasible
    start time exists within the window.

    If the window carries an off_nadir_angle, it is used directly;
    otherwise the incidence angle (from elevation) is converted to
    off-nadir via incidence_to_off_nadir.

    Args:
        observations: schedule from a baseline solver
        max_slew_rate: max angular slew rate (rad/s)
        settle_time: post-maneuver settling time (s)
        instance: optional AgileSARInstance for full 3-axis LOS model

    Returns:
        filtered list of ScheduledObservation (C2-feasible subset)
    """
    if len(observations) <= 1:
        return observations

    # Sort by actual start time
    sorted_obs = sorted(observations, key=lambda o: o.t_actual_start)

    # Normalize first observation end to start + duration (window span may
    # differ from the acquisition duration). Reject if its window is too short.
    first = sorted_obs[0]
    fd = first.window.duration_min
    if (first.window.t_end - first.window.t_start).total_seconds() + 1e-6 < fd:
        # Try dropping first and recursing on the rest
        return _enforce_c2_transitions(sorted_obs[1:], max_slew_rate,
                                       settle_time, instance)
    first_end = first.t_actual_start + timedelta(seconds=fd)
    if first_end != first.t_actual_end:
        from dataclasses import replace as _replace
        first = _replace(first, t_actual_end=first_end)
    feasible = [first]
    for i in range(1, len(sorted_obs)):
        prev = feasible[-1]
        curr = sorted_obs[i]
        duration = curr.window.duration_min

        # The observation always occupies exactly `duration` seconds from
        # its start (NOT window span — window can be shorter or longer than
        # the acquisition). Normalize both ends. A window shorter than the
        # acquisition cannot host it: skip.
        if (curr.window.t_end - curr.window.t_start).total_seconds() + 1e-6 < duration:
            continue
        curr_end = curr.t_actual_start + timedelta(seconds=duration)

        def _tau_at(t_start: datetime) -> float:
            if instance is None:
                phi_prev = _window_off_nadir(prev.window)
                phi_curr = _window_off_nadir(curr.window)
                return abs(phi_prev - phi_curr) / max_slew_rate + settle_time
            return _c2_transition_los(
                prev.window.target_id, prev.t_actual_start.timestamp(),
                curr.window.target_id, t_start.timestamp(),
                instance, max_slew_rate, settle_time,
            )

        # Fixed-point: delaying the start also changes the LOS geometry
        # (satellite moves), so tau must be recomputed at the delayed time.
        t_start = curr.t_actual_start
        for _ in range(8):
            gap = (t_start - prev.t_actual_end).total_seconds()
            tau = _tau_at(t_start)
            if gap >= tau:
                break
            # Push start out to cover tau at the delayed geometry. Add the
            # gate epsilon so the verifier's float/timestamp rounding cannot
            # reopen a sub-centisecond violation.
            pushed = max(
                curr.window.t_start,
                prev.t_actual_end + timedelta(seconds=tau + _C2_GATE_EPS),
            )
            if pushed <= t_start + timedelta(microseconds=1):
                break  # no further movement — accept
            t_start = pushed
        else:
            # Did not converge within window — reject.
            continue

        # Final guard: if even after the fixed-point the decoded gap does
        # not genuinely cover tau (within the gate epsilon), reject.
        if (t_start - prev.t_actual_end).total_seconds() + _C2_GATE_EPS < _tau_at(t_start):
            continue

        t_end = t_start + timedelta(seconds=duration)
        if t_end > curr.window.t_end + timedelta(microseconds=1):
            # No feasible start time within window — reject.
            continue

        if t_start == curr.t_actual_start and curr_end == curr.t_actual_end:
            feasible.append(curr)
        else:
            from dataclasses import replace
            feasible.append(replace(
                curr, t_actual_start=t_start, t_actual_end=t_end,
            ))

    return feasible


def _window_off_nadir(w) -> float:
    """Extract off-nadir angle (radians) from an observation window.

    Prefers the window's native off_nadir_angle (if set and > 0);
    falls back to converting the incidence angle derived from elevation.
    """
    if hasattr(w, 'off_nadir_angle') and w.off_nadir_angle > 0:
        return np.radians(w.off_nadir_angle)
    # Fall back: elevation → incidence → off-nadir
    theta = elevation_to_off_nadir(w.elevation)
    return incidence_to_off_nadir(theta)


# ─── Post-hoc helpers (Step 3) ────────────────────────────────────────────

def _compute_f2_f3_posthoc(
    observations: List[ScheduledObservation],
    geom_cache: Optional[GeomCache],
    instance: Optional[AgileSARInstance],
) -> Tuple[float, float]:
    """Compute post-hoc f2 (mean geometric resolution) and f3 (mean NESZ radiometric).

    f2 = mean(sin(θ_i) · cos(ψ_sq,i))   — geometric resolution
    f3 = mean(cos³(θ_i) · cos³(ψ_sq,i)) — NESZ radiometric quality

    Uses GeomCache if available; returns (0.0, 0.0) otherwise.

    Args:
        observations: selected scheduled observations
        geom_cache: precomputed geometry cache (or None)
        instance: AgileSARInstance for target_id → task_idx mapping (or None)

    Returns:
        (f2, f3) tuple
    """
    if geom_cache is None or instance is None:
        return 0.0, 0.0

    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}
    f2 = 0.0
    f3 = 0.0
    n = 0
    for obs in observations:
        target_id = obs.window.target_id
        if target_id not in target_to_idx:
            continue
        task_idx = target_to_idx[target_id]
        t_act = obs.t_actual_start.timestamp()
        gp = geom_cache.lookup(task_idx, t_act)
        sin_theta = math.sin(gp.theta)
        cos_theta_3 = math.cos(gp.theta) ** 3
        cos_psi_3 = gp.cos_psi ** 3
        f2 += sin_theta * gp.cos_psi
        f3 += cos_theta_3 * cos_psi_3
        n += 1
    if n > 0:
        f2 /= n
        f3 /= n
    return f2, f3


def _build_metadata(
    observations: List[ScheduledObservation],
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    f1: float,
    f2: float,
    f3: float,
    extra: dict,
) -> dict:
    """Build enriched metadata dict with f1/f2/f3/selected_task_indices.

    Args:
        observations: selected scheduled observations
        windows: all candidate windows
        targets: all ground targets
        f1: coverage profit
        f2: geometric resolution
        f3: NESZ radiometric (0.0 if not computed)
        extra: solver-specific metadata dict (may be empty)

    Returns:
        enriched metadata dict
    """
    target_ids = [obs.window.target_id for obs in observations]
    return {
        "n_selected": len(observations),
        "n_total_windows": len(windows),
        "n_total_targets": len(targets),
        "f1": f1,
        "f2": f2,
        "f3": f3,
        "selected_task_indices": target_ids,
        **extra,
    }


# ─── C3/C4 Budget Enforcement (Step 3) ────────────────────────────────────

def _resolve_budgets(
    instance: Optional[AgileSARInstance],
    kwargs: dict,
) -> Tuple[float, float, float, float]:
    """Resolve C3/C4 budgets and per-observation costs.

    When an ``instance`` is built from a scenario it carries finite
    ``energy_budget`` / ``memory_budget`` and per-task costs; the baseline
    must honour these (the MOEA penalises them). Defaulting to inf here let
    dense G-BL/G-SM schedules exceed the 200-observation budget that the
    scenario enforces, inflating f1_gbl. Explicit kwargs override instance.
    """
    if instance is not None:
        energy_budget = kwargs.pop("energy_budget", instance.energy_budget)
        memory_budget = kwargs.pop("memory_budget", instance.memory_budget)
        per_e = instance.tasks[0].energy if instance.tasks else 50_000.0
        per_m = instance.tasks[0].memory if instance.tasks else 5e8
        energy_per_obs = kwargs.pop("energy_per_obs", per_e)
        memory_per_obs = kwargs.pop("memory_per_obs", per_m)
    else:
        energy_budget = kwargs.pop("energy_budget", float("inf"))
        memory_budget = kwargs.pop("memory_budget", float("inf"))
        energy_per_obs = kwargs.pop("energy_per_obs", 50_000.0)
        memory_per_obs = kwargs.pop("memory_per_obs", 5e8)
    return energy_budget, memory_budget, energy_per_obs, memory_per_obs


def _enforce_c3c4(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
    energy_budget: float = float("inf"),
    memory_budget: float = float("inf"),
    energy_per_obs: float = 50_000.0,
    memory_per_obs: float = 5e8,
) -> List[ScheduledObservation]:
    """Drop lowest-priority observations until energy & memory budgets satisfied.

    Iteratively removes the observation with the lowest target priority
    until both energy_used <= energy_budget and memory_used <= memory_budget.

    Args:
        observations: selected scheduled observations
        targets: ground targets (for priority lookup)
        energy_budget: maximum energy allowed (default: inf = no limit)
        memory_budget: maximum memory allowed (default: inf = no limit)
        energy_per_obs: energy consumed per observation (ignored if instance used)
        memory_per_obs: memory consumed per observation (ignored if instance used)

    Returns:
        budget-compliant subset of observations
    """
    if not observations:
        return observations

    # Build target_id → priority lookup
    priority_map = {t.target_id: t.priority for t in targets}

    # Sort by priority ascending (lowest first for dropping)
    sorted_obs = sorted(
        observations,
        key=lambda o: priority_map.get(o.window.target_id, 0),
    )

    # Track cumulative usage
    n = len(sorted_obs)
    energy_used = n * energy_per_obs
    memory_used = n * memory_per_obs

    # Drop lowest-priority tasks until budgets satisfied
    while sorted_obs and (energy_used > energy_budget or memory_used > memory_budget):
        sorted_obs.pop(0)  # remove lowest priority
        energy_used -= energy_per_obs
        memory_used -= memory_per_obs

    return sorted_obs


# ─── G-BL: No Quality Awareness (Fixed Nadir-Looking Greedy) ───────────────

def baseline_b1(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    seed: Optional[int] = None,
    max_slew_rate: float = 0.0524,
    settle_time: float = 5.0,
    geom_cache: Optional[GeomCache] = None,
    instance: Optional[AgileSARInstance] = None,
    **kwargs,
) -> BaselineResult:
    """G-BL: Fixed nadir-looking greedy scheduling (no quality awareness).

    Schedules observations at fixed side-looking angle (no angle selection).
    Greedy selection: sorts windows by earliest start time, then iteratively
    adds observations that satisfy C2 attitude transition feasibility.

    No quality awareness — all observations use the window's native off-nadir
    angle; there is no angle optimization for NESZ quality.

    Args:
        windows: candidate observation windows
        targets: ground targets
        seed: random seed (ignored — deterministic)
        max_slew_rate: max angular slew rate (rad/s)
        settle_time: post-maneuver settling time (s)

    Returns:
        BaselineResult with f1, f2, and schedule
    """
    if not windows:
        return BaselineResult(
            schedule=[], f1=0.0, f2=0.0, n_scheduled=0,
            solver_name="G-BL (coverage-only, fixed-nadir)",
            metadata=_build_metadata(
                [], windows, targets, 0.0, 0.0, 0.0,
                {"quality_aware": False, "c3_enforced": True},
            ),
        )

    # Sort windows by start time (earliest first)
    sorted_windows = sorted(windows, key=lambda w: w.t_start)

    # Greedy selection: add window if C2-feasible AND task not already scheduled
    selected: List[ScheduledObservation] = []
    last_obs: Optional[ScheduledObservation] = None
    scheduled_targets: set = set()

    for w in sorted_windows:
        # deduplicate: skip if target already scheduled
        if w.target_id in scheduled_targets:
            continue
        # Window must be long enough to host a duration_min acquisition.
        if (w.t_end - w.t_start).total_seconds() + 1e-6 < w.duration_min:
            continue
        if last_obs is not None:
            # Fixed-point: delaying within the window changes LOS geometry;
            # recompute tau at the candidate start until the gap closes.
            t_start = w.t_start
            for _ in range(8):
                if instance is not None:
                    tau = _c2_transition_los(
                        last_obs.window.target_id,
                        last_obs.t_actual_start.timestamp(),
                        w.target_id, t_start.timestamp(),
                        instance, max_slew_rate, settle_time,
                    )
                else:
                    phi_prev = _window_off_nadir(last_obs.window)
                    phi_curr = _window_off_nadir(w)
                    tau = abs(phi_prev - phi_curr) / max_slew_rate + settle_time
                gap = (t_start - last_obs.t_actual_end).total_seconds()
                if gap >= tau:
                    break
                pushed = max(
                    w.t_start,
                    last_obs.t_actual_end + timedelta(seconds=tau + _C2_GATE_EPS),
                )
                if pushed <= t_start + timedelta(microseconds=1):
                    break
                t_start = pushed
            else:
                continue  # did not converge
            # Final guard against residual rounding violations.
            if ((t_start - last_obs.t_actual_end).total_seconds() + _C2_GATE_EPS
                    < _c2_transition_los(
                        last_obs.window.target_id,
                        last_obs.t_actual_start.timestamp(),
                        w.target_id, t_start.timestamp(),
                        instance, max_slew_rate, settle_time,
                    ) if instance is not None else False):
                continue
            t_end = t_start + timedelta(seconds=w.duration_min)
            if t_end > w.t_end + timedelta(microseconds=1):
                continue  # cannot fit within window
            obs = ScheduledObservation(
                window=w, t_actual_start=t_start, t_actual_end=t_end,
            )
        else:
            obs = ScheduledObservation(
                window=w,
                t_actual_start=w.t_start,
                t_actual_end=w.t_start + timedelta(seconds=w.duration_min),
            )

        selected.append(obs)
        scheduled_targets.add(w.target_id)
        last_obs = obs

    # ── C3/C4: enforce energy and memory budgets ──────────────────────────
    energy_budget, memory_budget, energy_per_obs, memory_per_obs = \
        _resolve_budgets(instance, kwargs)
    selected = _enforce_c3c4(
        selected, targets, energy_budget, memory_budget,
        energy_per_obs, memory_per_obs,
    )

    # f1 = coverage profit (O1: pure priority sum)
    f1 = compute_f1_coverage(selected, targets)

    # f2, f3 = post-hoc geometric resolution + NESZ radiometric quality
    f2, f3 = _compute_f2_f3_posthoc(selected, geom_cache, instance)

    return BaselineResult(
        schedule=selected,
        f1=f1,
        f2=f2,
        n_scheduled=len(selected),
        solver_name="G-BL (coverage-only, fixed-nadir)",
        metadata=_build_metadata(
            selected, windows, targets, f1, f2, f3,
            {"quality_aware": False, "c3_enforced": True},
        ),
    )


# ─── G-SQ: Proxy Quality (He2024IDRL-style) ────────────────────────────────

def baseline_b2(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    solver: str = "greedy_weighted",
    seed: Optional[int] = None,
    geom_cache: Optional[GeomCache] = None,
    instance: Optional[AgileSARInstance] = None,
    **solver_kwargs,
) -> BaselineResult:
    """G-SQ: Proxy quality scheduling (He2024IDRL-style).

    Uses the existing sar_sim solvers to maximize coverage profit.
    The second objective f2_proxy = Σ x_i (task count) is computed
    post-hoc. Since any task selected contributes 1 to both objectives,
    f2_proxy provides no additional discrimination — this is the
    fundamental limitation of optical-domain quality proxies for SAR.

    Equivalence: G-SQ is equivalent to G-BL in practice — both maximize
    coverage profit without quality awareness. The only difference is
    that G-SQ records f2_proxy as a separate metric. This is a "found"
    equivalence: G-SQ's proxy quality provides zero additional optimization
    capability beyond what G-BL already achieves.

    The actual (physical) geometric resolution f2 and NESZ radiometric f3 are
    against the MOEA results.

    Args:
        windows: candidate observation windows
        targets: ground targets
        solver: which solver to use
        seed: random seed
        **solver_kwargs: passed to the underlying solver

    Returns:
        BaselineResult with f1, f2, f2_proxy, and schedule
    """
    from sar_sim.solver import greedy_solver, ga_solver

    if seed is not None:
        np.random.seed(seed)

    if solver == "greedy_weighted":
        result = greedy_solver(windows, targets)
    elif solver == "ga":
        result = ga_solver(windows, targets, seed=seed, **solver_kwargs)
    elif solver == "ilp":
        try:
            from sar_sim.solver import ilp_solver
            result = ilp_solver(windows, targets, **solver_kwargs)
        except ImportError:
            result = greedy_solver(windows, targets)
    else:
        result = greedy_solver(windows, targets)

    observations = list(result.schedule)

    # ── C2: enforce attitude transition feasibility ──────────────────
    # Filter to keep only C2-feasible sequence (consistent with MOEA)
    observations = _enforce_c2_transitions(observations, instance=instance)

    # ── C3/C4: enforce energy and memory budgets ──────────────────────────
    energy_budget, memory_budget, energy_per_obs, memory_per_obs = \
        _resolve_budgets(instance, solver_kwargs)
    observations = _enforce_c3c4(
        observations, targets, energy_budget, memory_budget,
        energy_per_obs, memory_per_obs,
    )

    # f1 = coverage profit (O1 from formalspec: pure priority sum)
    # Recomputing after C2 filtering to reflect actual scheduled set.
    # Uses the canonical compute_f1_coverage() — same function as MOEA.
    f1 = compute_f1_coverage(observations, targets)

    # f2_proxy = count of scheduled tasks (He2024IDRL-style proxy)
    f2_proxy = len(observations)

    # f2, f3 = post-hoc geometric resolution + NESZ radiometric quality
    f2, f3 = _compute_f2_f3_posthoc(observations, geom_cache, instance)

    return BaselineResult(
        schedule=observations,
        f1=f1,
        f2=f2,  # geometric resolution (for comparison)
        n_scheduled=len(observations),
        solver_name="G-SQ (proxy quality)",
        metadata=_build_metadata(
            observations, windows, targets, f1, f2, f3,
            {
                "solver": solver,
                "quality_aware": False,
                "f2_proxy": f2_proxy,
                "f2_actual_nesz": f2,
                "c3_enforced": True,
            },
        ),
    )


# ─── G-SM: Squint-Minimized Greedy ────────────────────────────────

def baseline_b3(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    instrument: Optional[object] = None,
    instance: Optional[AgileSARInstance] = None,
    geom_cache: Optional[GeomCache] = None,
    solver: str = "greedy_weighted",
    seed: Optional[int] = None,
    **solver_kwargs,
) -> BaselineResult:
    """G-SM: Squint-minimized greedy scheduling.

    Same greedy profit-descending selection as G-BL, but after selecting
    tasks, minimizes the squint angle ψ_sq for each observation using
    GeomCache.  This maximizes azimuth resolution quality f3 = Σ cos ψ_sq.

    Key difference from G-BL:
    - G-BL: fixed θ = window's off_nadir angle → f3 = 0
    - G-SM: picks observation time within window that minimizes |ψ_sq| → f3 > 0

    Falls back to θ-tracking for C2 feasibility when GeomCache unavailable.

    Args:
        windows: candidate observation windows
        targets: ground targets
        instrument: SARInstrument (provides incidence_min/max for θ bounds)
        solver: which solver to use
        seed: random seed
        **solver_kwargs: passed to underlying solver

    Returns:
        BaselineResult with f1, f2, and schedule
    """
    from sar_sim.solver import greedy_solver, ga_solver

    if seed is not None:
        np.random.seed(seed)

    if solver == "greedy_weighted":
        result = greedy_solver(windows, targets)
    elif solver == "ga":
        result = ga_solver(windows, targets, seed=seed, **solver_kwargs)
    elif solver == "ilp":
        try:
            from sar_sim.solver import ilp_solver
            result = ilp_solver(windows, targets, **solver_kwargs)
        except ImportError:
            result = greedy_solver(windows, targets)
    else:
        result = greedy_solver(windows, targets)

    observations = list(result.schedule)

    # ── C2: enforce attitude transition feasibility ──────────────────
    observations = _enforce_c2_transitions(observations, instance=instance)

    # ── deduplicate: keep only first occurrence of each task ──────
    seen_targets = set()
    deduped = []
    for obs in observations:
        if obs.window.target_id not in seen_targets:
            seen_targets.add(obs.window.target_id)
            deduped.append(obs)
    observations = deduped

    # ── G-SM: squint minimization (Step 3) ─────────────────────────────
    # If geom_cache is available, pick the sampling point with minimal
    # |psi_sq| for each observation. Falls back to pass-through if
    # geom_cache is None (original θ-tracking behavior preserved via
    # optional theta-opt path below).
    if geom_cache is not None:
        observations = _b3_squint_minimize(observations, geom_cache, instance)
    else:
        # Fallback: original θ-tracking for C2 feasibility
        theta_min_deg = 15.0
        theta_max_deg = 50.0
        if instrument is not None:
            theta_min_deg = instrument.incidence_min
            theta_max_deg = instrument.incidence_max
        observations = _c2_with_theta_opt(
            observations, theta_min_deg, theta_max_deg,
            max_slew_rate=0.0524, settle_time=5.0,
        )

    # ── Re-check C2 after squint/θ optimization (t_actual may have moved) ──
    observations = _enforce_c2_transitions(observations, instance=instance)

    # ── C3/C4: enforce energy and memory budgets ──────────────────────────
    energy_budget, memory_budget, energy_per_obs, memory_per_obs = \
        _resolve_budgets(instance, solver_kwargs)
    observations = _enforce_c3c4(
        observations, targets, energy_budget, memory_budget,
        energy_per_obs, memory_per_obs,
    )

    # f1 = coverage profit (same as G-BL)
    f1 = compute_f1_coverage(observations, targets)

    # f2, f3 = post-hoc geometric resolution + NESZ radiometric quality
    f2, f3 = _compute_f2_f3_posthoc(observations, geom_cache, instance)

    return BaselineResult(
        schedule=observations,
        f1=f1,
        f2=f2,
        n_scheduled=len(observations),
        solver_name="G-SM (squint-minimized)",
        metadata=_build_metadata(
            observations, windows, targets, f1, f2, f3,
            {
                "solver": solver,
                "quality_aware": False,
                "squint_minimized": geom_cache is not None,
                "c3_enforced": True,
            },
        ),
    )


# ─── G-SM Squint Minimization (Step 3) ──────────────────────────────────────

def _b3_squint_minimize(
    observations: List[ScheduledObservation],
    geom_cache: Optional[GeomCache],
    instance: Optional[AgileSARInstance],
) -> List[ScheduledObservation]:
    """G-SM: For each observation, pick the sampling point in geom_cache with
    minimal |psi_sq| (squint angle), updating t_actual_start and t_actual_end.

    If geom_cache or instance is None, returns observations unchanged
    (fallback / pass-through).

    Args:
        observations: schedule from upstream (after C2 enforcement)
        geom_cache: precomputed geometry cache (GeomCache from Step 1)
        instance: AgileSARInstance (for target_id → task_idx mapping)

    Returns:
        list of ScheduledObservation with squint-minimized timing
    """
    if geom_cache is None or instance is None:
        return observations

    # Build target_id → task_idx mapping from the instance
    target_to_idx = {t.target_id: i for i, t in enumerate(instance.tasks)}

    result = []
    for obs in observations:
        target_id = obs.window.target_id
        if target_id not in target_to_idx:
            # No matching task — pass through unchanged
            result.append(obs)
            continue

        task_idx = target_to_idx[target_id]
        arr = geom_cache.cache[task_idx]

        # Restrict candidates to this observation's own visibility window
        # and to the platform off-nadir envelope (paper C1). The geometry
        # cache spans the entire pass across all windows of the task, so an
        # unrestricted argmin can land at near-nadir times where the target
        # is not observable (RDR-003).
        w_start = obs.window.t_start.timestamp()
        w_end = obs.window.t_end.timestamp()
        mask = (arr[:, 0] >= w_start) & (arr[:, 0] <= w_end)
        phi_min = instance.phi_min
        phi_max = instance.phi_max
        mask &= (np.abs(arr[:, 1]) >= phi_min) & (np.abs(arr[:, 1]) <= phi_max)
        if not np.any(mask):
            # No feasible sample point in this window — keep the upstream
            # (C2-enforced) timing unchanged rather than jumping windows.
            result.append(obs)
            continue
        cand = arr[mask]
        best_k = int(np.argmin(np.abs(cand[:, 2])))
        best_t = cand[best_k, 0]  # column 0 = epoch seconds

        # Convert epoch seconds back to a datetime whose tz matches the
        # source window. pkl scenarios store naive datetimes, and naive
        # .timestamp() interprets them as local time; the exact inverse is
        # naive fromtimestamp(t) (also local) — utcfromtimestamp() would
        # treat the epoch as true UTC and introduce a tz-offset shift on
        # non-UTC machines, pushing acquisitions out of their window.
        ref = obs.window.t_start
        if ref.tzinfo is not None:
            dt_start = datetime.fromtimestamp(best_t, tz=timezone.utc)
        else:
            dt_start = datetime.fromtimestamp(best_t)
        dt_end = dt_start + timedelta(seconds=obs.window.duration_min)

        new_obs = replace(
            obs,
            t_actual_start=dt_start,
            t_actual_end=dt_end,
        )
        result.append(new_obs)

    return result


# ─── C2 with θ optimization (legacy — replaced by _b3_squint_minimize) ────

def _c2_with_theta_opt(
    observations: List[ScheduledObservation],
    theta_min_deg: float,
    theta_max_deg: float,
    max_slew_rate: float = 0.0524,
    settle_time: float = 5.0,
) -> List[ScheduledObservation]:
    """C2 filter with θ optimization + start-time flexibility.

    For each consecutive pair, if the transition at native angles and
    assigned start time is infeasible:
    1. Try adjusting CURRENT task's θ to be as close as possible to
       the previous task's θ (minimizing transition cost).
    2. If still infeasible, try delaying the current task's start
       within its window [t_start, t_end].

    This is NOT quality-aware — we pick θ solely to satisfy C2.

    Returns C2-feasible subset (may be shorter than input).
    """
    if len(observations) <= 1:
        return observations

    sorted_obs = sorted(observations, key=lambda o: o.t_actual_start)

    theta_min = np.radians(theta_min_deg)
    theta_max = np.radians(theta_max_deg)

    feasible = [sorted_obs[0]]
    last_phi = _window_off_nadir(feasible[-1].window)
    # Track the actual end time (may change if we delay)
    last_end = feasible[-1].t_actual_end

    for i in range(1, len(sorted_obs)):
        curr = sorted_obs[i]
        phi_native = _window_off_nadir(curr.window)

        # Strategy 1: try native φ at assigned start time
        d_phi = abs(last_phi - phi_native)
        tau = d_phi / max_slew_rate + settle_time
        gap_at_assigned = (curr.t_actual_start - last_end).total_seconds()

        if gap_at_assigned >= tau:
            feasible.append(curr)
            last_phi = phi_native
            last_end = curr.t_actual_end
            continue

        # Strategy 2: try adjusting φ toward last_phi
        phi_adjusted = np.clip(last_phi, theta_min, theta_max)
        d_phi_adj = abs(last_phi - phi_adjusted)
        tau_adj = d_phi_adj / max_slew_rate + settle_time

        if gap_at_assigned >= tau_adj:
            feasible.append(curr)
            last_phi = phi_adjusted
            last_end = curr.t_actual_end
            continue

        # Strategy 3: try delaying start time (with native φ)
        earliest_start = max(curr.window.t_start, last_end + timedelta(seconds=tau))
        new_end = earliest_start + timedelta(seconds=curr.window.duration_min)
        if new_end <= curr.window.t_end:
            delayed = replace(curr, t_actual_start=earliest_start, t_actual_end=new_end)
            feasible.append(delayed)
            last_phi = phi_native
            last_end = new_end
            continue

        # Strategy 4: try delaying + adjusted φ
        if phi_adjusted != phi_native:
            tau_adj2 = d_phi_adj / max_slew_rate + settle_time  # same as tau_adj
            earliest_start2 = max(curr.window.t_start, last_end + timedelta(seconds=tau_adj2))
            new_end2 = earliest_start2 + timedelta(seconds=curr.window.duration_min)
            if new_end2 <= curr.window.t_end:
                delayed2 = replace(curr, t_actual_start=earliest_start2, t_actual_end=new_end2)
                feasible.append(delayed2)
                last_phi = phi_adjusted
                last_end = new_end2
                continue

        # All strategies failed — reject

    return feasible


# ─── Comparison Helper ───────────────────────────────────────────────────

def compare_with_baselines(
    moea_frontier: List[dict],
    b1_result: BaselineResult,
    b2_result: BaselineResult,
) -> dict:
    """Compare MOEA Pareto frontier against G-BL and G-SQ baselines.

    Args:
        moea_frontier: list of dicts from moea_solver metadata["frontier"]
        b1_result: G-BL baseline result
        b2_result: G-SQ baseline result

    Returns:
        comparison dict
    """
    moea_f1 = [s["f1"] for s in moea_frontier] if moea_frontier else []
    moea_f2 = [s["f2"] for s in moea_frontier] if moea_frontier else []
    moea_f3 = [s["f3"] for s in moea_frontier] if moea_frontier else []

    return {
        "moea": {
            "n_solutions": len(moea_frontier),
            "f1_range": [min(moea_f1) if moea_f1 else 0, max(moea_f1) if moea_f1 else 0],
            "f2_range": [min(moea_f2) if moea_f2 else 0, max(moea_f2) if moea_f2 else 0],
            "f3_range": [min(moea_f3) if moea_f3 else 0, max(moea_f3) if moea_f3 else 0],
        },
        "b1": {
            "f1": b1_result.f1,
            "f2": b1_result.f2,
            "n_scheduled": b1_result.n_scheduled,
        },
        "b2": {
            "f1": b2_result.f1,
            "f2": b2_result.f2,
            "f2_proxy": b2_result.metadata.get("f2_proxy", 0),
            "n_scheduled": b2_result.n_scheduled,
        },
    }
