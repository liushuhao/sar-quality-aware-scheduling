"""Coverage metrics for SAR scheduling evaluation.

Measures what fraction of targets are observed and how well.
"""

from typing import List, Dict, Set, Any, Optional
from sar_sim.types import ScheduledObservation, GroundTarget


def compute_f1_coverage(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
    target_id_to_priority: Optional[Dict[str, float]] = None,
) -> float:
    """Compute f1 = Σ p_i for scheduled tasks (O1 from problem formalization).

    This is the canonical f1 (coverage-weighted profit) definition from
    the problem formalization: f1 = Σ x_i · p_i where x_i = 1 if task i
    is scheduled. Both MOEA and all baselines MUST use this same function
    to ensure fair comparison.

    Args:
        observations: scheduled observations
        targets: all ground targets (used to build priority lookup if
                 target_id_to_priority is not provided)
        target_id_to_priority: optional pre-built lookup map

    Returns:
        f1 value (sum of priorities of scheduled targets)
    """
    if target_id_to_priority is None:
        target_id_to_priority = {t.target_id: t.priority for t in targets}

    f1 = 0.0
    counted = set()
    for obs in observations:
        tid = obs.target_id
        if tid in target_id_to_priority and tid not in counted:
            f1 += target_id_to_priority[tid]
            counted.add(tid)
    return f1


def coverage_ratio(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
) -> float:
    """Fraction of targets that have at least one observation.

    Args:
        observations: scheduled observations
        targets: all ground targets

    Returns:
        coverage ratio in [0, 1]
    """
    if not targets:
        return 1.0

    observed_ids = set(obs.target_id for obs in observations)
    return len(observed_ids) / len(targets)


def priority_weighted_coverage(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
) -> float:
    """Priority-weighted coverage: high-priority targets count more.

    Args:
        observations: scheduled observations
        targets: all ground targets

    Returns:
        weighted coverage in [0, 1], where 1.0 = all targets observed
    """
    if not targets:
        return 1.0

    target_map = {t.target_id: t for t in targets}
    observed_ids = set(obs.target_id for obs in observations)

    total_weight = sum(t.priority for t in targets)
    if total_weight == 0:
        return 0.0

    covered_weight = sum(
        target_map[tid].priority
        for tid in observed_ids
        if tid in target_map
    )

    return covered_weight / total_weight


def observation_counts(
    observations: List[ScheduledObservation],
) -> Dict[str, int]:
    """Count observations per target.

    Args:
        observations: scheduled observations

    Returns:
        dict mapping target_id to observation count
    """
    counts = {}
    for obs in observations:
        counts[obs.target_id] = counts.get(obs.target_id, 0) + 1
    return counts


def observed_targets_set(
    observations: List[ScheduledObservation],
) -> Set[str]:
    """Set of target IDs that have at least one observation."""
    return set(obs.target_id for obs in observations)


def unobserved_targets(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
) -> List[str]:
    """List target IDs that received no observations.

    Args:
        observations: scheduled observations
        targets: all ground targets

    Returns:
        list of unobserved target IDs
    """
    observed = observed_targets_set(observations)
    return [t.target_id for t in targets if t.target_id not in observed]


def coverage_summary(
    observations: List[ScheduledObservation],
    targets: List[GroundTarget],
) -> Dict[str, Any]:
    """Compute a comprehensive coverage summary.

    Args:
        observations: scheduled observations
        targets: all ground targets

    Returns:
        dict with coverage metrics
    """
    return {
        "coverage_ratio": coverage_ratio(observations, targets),
        "priority_weighted_coverage": priority_weighted_coverage(observations, targets),
        "n_total_targets": len(targets),
        "n_observed_targets": len(observed_targets_set(observations)),
        "n_unobserved_targets": len(unobserved_targets(observations, targets)),
        "n_total_observations": len(observations),
    }
