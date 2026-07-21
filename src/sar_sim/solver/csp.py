"""CSP formulation for SAR observation scheduling.

Models the scheduling problem as a Weighted Maximum Clique, where:
- Nodes = observation windows, weighted by priority/elevation
- Edges = compatible (non-conflicting) pairs
- Solution = maximum-weight independent set
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np

from sar_sim.types import (
    ObservationWindow,
    ScheduledObservation,
    SolverResult,
    GroundTarget,
)


@dataclass
class CSPInstance:
    """A CSP instance ready for solving.

    windows: all candidate observation windows
    weights: weight for each window (higher = more desirable)
    compatibility: NxN boolean matrix, True if windows i,j are compatible
    target_map: target_id -> GroundTarget lookup
    """
    windows: List[ObservationWindow]
    weights: np.ndarray
    compatibility: np.ndarray
    target_map: dict


def build_csp_instance(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
) -> CSPInstance:
    """Build a CSP instance from raw observation windows.

    Compatibility rule: two windows are compatible if:
    - They target different ground points, OR
    - They don't overlap in time for same satellite

    Weight = priority * (1 + elevation/90) — favors high-priority
    targets and good observation geometry.

    Args:
        windows: all candidate observation windows
        targets: all ground targets

    Returns:
        CSPInstance
    """
    n = len(windows)

    # Build target lookup
    target_map = {t.target_id: t for t in targets}

    # Compute weights
    weights = np.zeros(n)
    for i, w in enumerate(windows):
        priority = target_map[w.target_id].priority
        # Normalize elevation: 10-90 degrees → ~0.11 to ~1.0
        elev_factor = max(0.1, w.elevation / 90.0)
        weights[i] = priority * (1.0 + elev_factor)

    # Build compatibility matrix
    compatibility = np.ones((n, n), dtype=bool)

    # Group windows by satellite for temporal conflict check
    by_sat = {}
    for i, w in enumerate(windows):
        by_sat.setdefault(w.satellite_id, []).append(i)

    for sat_id, indices in by_sat.items():
        m = len(indices)
        for a_idx in range(m):
            for b_idx in range(a_idx + 1, m):
                i = indices[a_idx]
                j = indices[b_idx]
                w_i = windows[i]
                w_j = windows[j]

                # Same satellite, overlapping times → conflict
                if w_i.t_start < w_j.t_end and w_j.t_start < w_i.t_end:
                    compatibility[i, j] = False
                    compatibility[j, i] = False

    return CSPInstance(
        windows=windows,
        weights=weights,
        compatibility=compatibility,
        target_map=target_map,
    )


def schedule_from_indices(
    windows: List[ObservationWindow],
    selected_indices: List[int],
) -> List[ScheduledObservation]:
    """Convert a solution (list of selected window indices) to ScheduledObservations.

    Args:
        windows: all candidate windows
        selected_indices: indices of selected windows

    Returns:
        list of ScheduledObservation
    """
    result = []
    for idx in selected_indices:
        w = windows[idx]
        result.append(
            ScheduledObservation(
                window=w,
                t_actual_start=w.t_start,
                t_actual_end=w.t_end,
            )
        )
    return result


def compute_solution_score(
    csp: CSPInstance,
    selected_indices: List[int],
) -> float:
    """Compute the objective score for a solution.

    Score = sum of weights of selected windows.

    Args:
        csp: the CSP instance
        selected_indices: indices of selected windows

    Returns:
        score (float)
    """
    return float(np.sum(csp.weights[selected_indices]))


def validate_solution(
    csp: CSPInstance,
    selected_indices: List[int],
) -> Tuple[bool, str]:
    """Validate that a solution is feasible (no conflicts).

    Args:
        csp: the CSP instance
        selected_indices: proposed solution indices

    Returns:
        (is_valid, message)
    """
    n = len(selected_indices)
    for i in range(n):
        for j in range(i + 1, n):
            if not csp.compatibility[selected_indices[i], selected_indices[j]]:
                return False, (
                    f"Conflict between window {selected_indices[i]} "
                    f"and {selected_indices[j]}"
                )
    return True, "Valid solution"
