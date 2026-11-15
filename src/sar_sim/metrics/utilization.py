"""Resource utilization metrics for SAR scheduling evaluation.

Measures how efficiently satellite resources are used.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from sar_sim.types import ScheduledObservation
from sar_sim.conflict.resource import ResourceBudget, DEFAULT_OBSERVATION_COST_MB


def satellite_utilization(
    observations: List[ScheduledObservation],
    time_start: datetime,
    time_end: datetime,
) -> Dict[str, float]:
    """Compute time utilization per satellite.

    Utilization = fraction of time spent observing.

    Args:
        observations: scheduled observations
        time_start, time_end: planning horizon

    Returns:
        dict mapping satellite_id to utilization [0, 1]
    """
    total_duration = (time_end - time_start).total_seconds()
    if total_duration <= 0:
        return {}

    by_sat = defaultdict(float)
    for obs in observations:
        obs_duration = (obs.t_actual_end - obs.t_actual_start).total_seconds()
        by_sat[obs.satellite_id] += obs_duration

    return {
        sat_id: duration / total_duration
        for sat_id, duration in by_sat.items()
    }


def observation_count_per_satellite(
    observations: List[ScheduledObservation],
) -> Dict[str, int]:
    """Number of observations assigned to each satellite.

    Args:
        observations: scheduled observations

    Returns:
        dict mapping satellite_id to count
    """
    counts = defaultdict(int)
    for obs in observations:
        counts[obs.satellite_id] += 1
    return dict(counts)


def memory_usage(
    observations: List[ScheduledObservation],
    obs_cost_mb: float = DEFAULT_OBSERVATION_COST_MB,
) -> Dict[str, float]:
    """Estimated memory usage per satellite.

    Args:
        observations: scheduled observations
        obs_cost_mb: memory cost per observation (MB)

    Returns:
        dict mapping satellite_id to estimated memory usage (MB)
    """
    usage = defaultdict(float)
    for obs in observations:
        usage[obs.satellite_id] += obs_cost_mb
    return dict(usage)


def target_distribution(
    observations: List[ScheduledObservation],
) -> Dict[str, List[str]]:
    """Which targets each satellite observes.

    Args:
        observations: scheduled observations

    Returns:
        dict mapping satellite_id to list of target_ids
    """
    dist = defaultdict(set)
    for obs in observations:
        dist[obs.satellite_id].add(obs.target_id)
    return {k: sorted(v) for k, v in dist.items()}


def utilization_summary(
    observations: List[ScheduledObservation],
    time_start: datetime,
    time_end: datetime,
    budget: ResourceBudget = None,
) -> Dict[str, Any]:
    """Comprehensive utilization summary.

    Args:
        observations: scheduled observations
        time_start, time_end: planning horizon
        budget: optional resource budget for comparison

    Returns:
        dict with utilization metrics
    """
    if budget is None:
        budget = ResourceBudget()

    utilization = satellite_utilization(observations, time_start, time_end)
    counts = observation_count_per_satellite(observations)
    memory = memory_usage(observations)

    satellite_summaries = {}
    all_satellites = set(
        list(utilization.keys()) +
        list(counts.keys()) +
        list(memory.keys())
    )

    for sat_id in sorted(all_satellites):
        sat_util = utilization.get(sat_id, 0.0)
        sat_count = counts.get(sat_id, 0)
        sat_mem = memory.get(sat_id, 0.0)

        satellite_summaries[sat_id] = {
            "time_utilization": sat_util,
            "observation_count": sat_count,
            "memory_usage_mb": sat_mem,
            "memory_utilization": sat_mem / budget.memory_mb if budget.memory_mb > 0 else 0.0,
            "count_utilization": sat_count / budget.max_observations_per_orbit if budget.max_observations_per_orbit > 0 else 0.0,
        }

    return {
        "n_satellites_used": len(all_satellites),
        "mean_time_utilization": (
            sum(utilization.values()) / len(utilization)
            if utilization else 0.0
        ),
        "total_observations": len(observations),
        "per_satellite": satellite_summaries,
    }
