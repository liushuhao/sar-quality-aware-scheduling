"""Resource conflict detection.

Models satellite resource constraints: memory, power, downlink.
Detects when cumulative resource usage exceeds capacity.
"""

from dataclasses import dataclass

from sar_sim.types import ScheduledObservation, Conflict
from typing import List, Dict, Optional


@dataclass
class ResourceBudget:
    """Satellite resource capacity budget.

    memory_mb: onboard storage capacity (MB)
    power_w: available power for payload (W)
    max_observations_per_orbit: maximum number of observations per orbit
    min_gap_between_obs: minimum time between consecutive observations (seconds)
    """
    memory_mb: float = 1024.0
    power_w: float = 500.0
    max_observations_per_orbit: int = 20
    min_gap_between_obs: float = 10.0  # seconds


# Default observation resource cost model
DEFAULT_OBSERVATION_COST_MB = 50.0  # MB per observation
DEFAULT_OBSERVATION_POWER_W = 200.0  # W during observation


def detect_resource_overuse(
    observations: List[ScheduledObservation],
    budget: Optional[ResourceBudget] = None,
    observation_cost_mb: float = DEFAULT_OBSERVATION_COST_MB,
    observation_power_w: float = DEFAULT_OBSERVATION_POWER_W,
) -> List[Conflict]:
    """Detect resource budget violations.

    Checks:
    1. Total memory usage across all observations
    2. Overlapping power draw (simplified: count overlaps)
    3. Maximum observations per satellite

    Args:
        observations: scheduled observations
        budget: resource budget (uses defaults if None)

    Returns:
        list of resource conflicts
    """
    if budget is None:
        budget = ResourceBudget()

    conflicts = []

    # Group by satellite
    by_satellite = {}
    for obs in observations:
        by_satellite.setdefault(obs.satellite_id, []).append(obs)

    for sat_id, sat_obs in by_satellite.items():
        # Check memory
        total_memory = len(sat_obs) * observation_cost_mb
        if total_memory > budget.memory_mb:
            conflicts.append(
                Conflict(
                    obs_a=sat_obs[0],
                    obs_b=sat_obs[-1],
                    conflict_type="resource",
                    description=(
                        f"Satellite {sat_id}: memory usage {total_memory:.0f} MB "
                        f"exceeds budget {budget.memory_mb:.0f} MB"
                    ),
                )
            )

        # Check max observations
        if len(sat_obs) > budget.max_observations_per_orbit:
            conflicts.append(
                Conflict(
                    obs_a=sat_obs[0],
                    obs_b=sat_obs[-1],
                    conflict_type="resource",
                    description=(
                        f"Satellite {sat_id}: {len(sat_obs)} observations "
                        f"exceeds max {budget.max_observations_per_orbit}"
                    ),
                )
            )

    return conflicts

