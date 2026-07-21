"""Temporal conflict detection.

Detects overlapping observation windows: two observations
cannot be executed simultaneously by the same satellite.
"""

from sar_sim.types import ObservationWindow, ScheduledObservation, Conflict
from typing import List, Tuple


def time_overlap(
    start1, end1, start2, end2
) -> bool:
    """Check if two time intervals overlap.

    Intervals are closed [start, end).

    Returns:
        True if intervals overlap
    """
    return start1 < end2 and start2 < end1


def detect_temporal_conflicts(
    observations: List[ScheduledObservation],
) -> List[Conflict]:
    """Detect pairwise temporal conflicts between scheduled observations.

    Two observations conflict temporally if they are assigned to the same
    satellite and their execution intervals overlap.

    Args:
        observations: list of scheduled observations

    Returns:
        list of Conflict with conflict_type='temporal'
    """
    conflicts = []

    # Group by satellite
    by_satellite = {}
    for obs in observations:
        by_satellite.setdefault(obs.satellite_id, []).append(obs)

    for sat_id, sat_obs in by_satellite.items():
        n = len(sat_obs)
        for i in range(n):
            for j in range(i + 1, n):
                a = sat_obs[i]
                b = sat_obs[j]

                if time_overlap(
                    a.t_actual_start, a.t_actual_end,
                    b.t_actual_start, b.t_actual_end,
                ):
                    conflicts.append(
                        Conflict(
                            obs_a=a,
                            obs_b=b,
                            conflict_type="temporal",
                            description=(
                                f"Satellite {sat_id}: "
                                f"{a.target_id} [{a.t_actual_start} → {a.t_actual_end}] "
                                f"overlaps with "
                                f"{b.target_id} [{b.t_actual_start} → {b.t_actual_end}]"
                            ),
                        )
                    )

    return conflicts


def find_conflicting_windows(
    windows: List[ObservationWindow],
) -> List[Tuple[ObservationWindow, ObservationWindow]]:
    """Find pairs of observation windows from different targets
    that overlap in time for the same satellite.

    This is a pre-scheduling check: if two windows overlap,
    at most one can be scheduled for that satellite.

    Args:
        windows: list of candidate observation windows

    Returns:
        list of (window_a, window_b) conflicting pairs
    """
    pairs = []

    # Group by satellite
    by_satellite = {}
    for w in windows:
        by_satellite.setdefault(w.satellite_id, []).append(w)

    for sat_id, sat_windows in by_satellite.items():
        n = len(sat_windows)
        for i in range(n):
            for j in range(i + 1, n):
                a = sat_windows[i]
                b = sat_windows[j]
                if a.target_id != b.target_id and time_overlap(
                    a.t_start, a.t_end, b.t_start, b.t_end
                ):
                    pairs.append((a, b))

    return pairs
