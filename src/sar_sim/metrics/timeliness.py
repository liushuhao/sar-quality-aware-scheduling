"""Timeliness metrics for SAR scheduling evaluation.

Measures revisit intervals — how long targets wait between observations.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np

from sar_sim.types import ScheduledObservation, GroundTarget


def revisit_intervals(
    observations: List[ScheduledObservation],
    target_id: str,
) -> List[float]:
    """Compute revisit intervals (seconds) for a specific target.

    Args:
        observations: all scheduled observations
        target_id: the target to compute intervals for

    Returns:
        list of time gaps (seconds) between consecutive observations
    """
    target_obs = sorted(
        [obs for obs in observations if obs.target_id == target_id],
        key=lambda o: o.t_actual_start,
    )

    if len(target_obs) < 2:
        return []

    intervals = []
    for i in range(1, len(target_obs)):
        dt = (target_obs[i].t_actual_start -
              target_obs[i - 1].t_actual_end).total_seconds()
        intervals.append(dt)

    return intervals


def max_revisit(
    observations: List[ScheduledObservation],
    target_id: str,
) -> Optional[float]:
    """Maximum revisit interval for a target.

    Args:
        observations: all scheduled observations
        target_id: the target

    Returns:
        max interval in seconds, or None if < 2 observations
    """
    intervals = revisit_intervals(observations, target_id)
    return max(intervals) if intervals else None


def mean_revisit(
    observations: List[ScheduledObservation],
    target_id: str,
) -> Optional[float]:
    """Mean revisit interval for a target.

    Args:
        observations: all scheduled observations
        target_id: the target

    Returns:
        mean interval in seconds, or None if < 2 observations
    """
    intervals = revisit_intervals(observations, target_id)
    return float(np.mean(intervals)) if intervals else None


def timeliness_violations(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
    time_start: datetime,
    time_end: datetime,
) -> Dict[str, Any]:
    """Check which targets violate their revisit requirement.

    For each target, checks if any revisit interval exceeds
    its revisit_requirement.

    Also checks edge gaps: from time_start to first observation
    and from last observation to time_end.

    Args:
        observations: scheduled observations
        targets: ground targets with revisit_requirement
        time_start: start of planning horizon
        time_end: end of planning horizon

    Returns:
        dict with violation details
    """
    target_map = {t.target_id: t for t in targets}
    violations = []
    compliant = []

    for target in targets:
        obs_list = sorted(
            [o for o in observations if o.target_id == target.target_id],
            key=lambda o: o.t_actual_start,
        )

        if len(obs_list) == 0:
            # No observations at all
            violations.append({
                "target_id": target.target_id,
                "reason": "never_observed",
                "max_required": target.revisit_requirement,
            })
            continue

        # Check gap from start to first observation
        first_gap = (obs_list[0].t_actual_start - time_start).total_seconds()
        last_gap = (time_end - obs_list[-1].t_actual_end).total_seconds()

        max_gap = max(first_gap, last_gap)

        # Check internal gaps
        intervals = revisit_intervals(observations, target.target_id)
        if intervals:
            max_gap = max(max_gap, max(intervals))

        if max_gap > target.revisit_requirement:
            violations.append({
                "target_id": target.target_id,
                "reason": "revisit_exceeded",
                "max_gap_seconds": max_gap,
                "max_required": target.revisit_requirement,
            })
        else:
            compliant.append(target.target_id)

    return {
        "n_violations": len(violations),
        "n_compliant": len(compliant),
        "violation_rate": len(violations) / len(targets) if targets else 0.0,
        "violations": violations,
        "compliant_targets": compliant,
    }


def timeliness_summary(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
    time_start: datetime,
    time_end: datetime,
) -> Dict[str, Any]:
    """Comprehensive timeliness summary.

    Args:
        observations: scheduled observations
        targets: ground targets
        time_start, time_end: planning horizon

    Returns:
        dict with timeliness metrics
    """
    all_intervals = []
    for target in targets:
        intervals = revisit_intervals(observations, target.target_id)
        all_intervals.extend(intervals)

    violations = timeliness_violations(observations, targets,
                                        time_start, time_end)

    return {
        "mean_revisit_seconds": float(np.mean(all_intervals)) if all_intervals else None,
        "max_revisit_seconds": max(all_intervals) if all_intervals else None,
        "median_revisit_seconds": float(np.median(all_intervals)) if all_intervals else None,
        "std_revisit_seconds": float(np.std(all_intervals)) if all_intervals else None,
        "n_observations": len(observations),
        "violation_rate": violations["violation_rate"],
        "n_violations": violations["n_violations"],
    }
