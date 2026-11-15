"""Greedy heuristic solver for SAR observation scheduling.

Simple, fast baseline: select windows by weight/priority until all
satellites are fully booked or no compatible windows remain.
"""

from typing import List
import numpy as np

from sar_sim.types import ObservationWindow, ScheduledObservation, SolverResult
from sar_sim.solver.csp import (
    CSPInstance,
    build_csp_instance,
    schedule_from_indices,
    compute_solution_score,
    validate_solution,
)


def greedy_weighted(
    csp: CSPInstance,
) -> List[int]:
    """Weighted greedy: select highest-weight window, then
    iteratively add the highest-weight compatible window.

    Args:
        csp: the CSP instance

    Returns:
        list of selected window indices (sorted)
    """
    n = len(csp.windows)

    if n == 0:
        return []

    # Sort by weight descending
    order = list(np.argsort(-csp.weights))
    selected = []
    available = [True] * n

    for idx in order:
        if not available[idx]:
            continue

        # Check compatibility with all previously selected
        compatible = all(
            csp.compatibility[idx, s] for s in selected
        )

        if compatible:
            selected.append(idx)
            # Mark conflicting windows as unavailable
            for j in range(n):
                if not csp.compatibility[idx, j]:
                    available[j] = False

    return sorted(selected)


def greedy_solver(
    windows: List[ObservationWindow],
    targets: List,
    **kwargs,
) -> SolverResult:
    """Greedy solver entry point.

    Args:
        windows: candidate observation windows
        targets: ground targets (for priority weighting)
        **kwargs: ignored (for interface uniformity)

    Returns:
        SolverResult
    """
    csp = build_csp_instance(windows, targets)
    selected = greedy_weighted(csp)
    is_valid, msg = validate_solution(csp, selected)

    schedule = schedule_from_indices(windows, selected)
    score = compute_solution_score(csp, selected)

    return SolverResult(
        schedule=tuple(schedule),
        score=score,
        metadata={
            "solver": "greedy_weighted",
            "n_selected": len(selected),
            "n_total": len(windows),
            "valid": is_valid,
        },
    )


def greedy_by_satellite(
    csp: CSPInstance,
    min_gap_seconds: float = 0.0,
) -> List[int]:
    """Per-satellite greedy: for each satellite independently,
    greedily select non-overlapping windows.

    Args:
        csp: the CSP instance
        min_gap_seconds: minimum gap between consecutive observations

    Returns:
        list of selected window indices
    """
    # Group windows by satellite
    by_sat = {}
    for i, w in enumerate(csp.windows):
        by_sat.setdefault(w.satellite_id, []).append(i)

    selected = []

    for sat_id, indices in by_sat.items():
        # Sort by weight descending
        sat_order = sorted(indices, key=lambda i: -csp.weights[i])
        sat_selected = []

        for idx in sat_order:
            w = csp.windows[idx]
            can_add = True
            for s in sat_selected:
                sw = csp.windows[s]
                # Check temporal overlap
                overlap_in_time = (
                    w.t_start < sw.t_end and sw.t_start < w.t_end
                )
                if overlap_in_time:
                    can_add = False
                    break

                # Compute gap between non-overlapping windows
                if w.t_end <= sw.t_start:
                    gap = sw.t_start.timestamp() - w.t_end.timestamp()
                else:
                    gap = w.t_start.timestamp() - sw.t_end.timestamp()

                if gap < min_gap_seconds:
                    can_add = False
                    break
            if can_add:
                sat_selected.append(idx)

        selected.extend(sat_selected)

    return sorted(selected)
