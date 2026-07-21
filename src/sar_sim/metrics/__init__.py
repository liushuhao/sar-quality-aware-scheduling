"""Metrics package: evaluation and benchmarking pipeline."""

from sar_sim.metrics.coverage import (
    coverage_ratio,
    compute_f1_coverage,
    priority_weighted_coverage,
    observation_counts,
    observed_targets_set,
    unobserved_targets,
    coverage_summary,
)
from sar_sim.metrics.timeliness import (
    revisit_intervals,
    max_revisit,
    mean_revisit,
    timeliness_violations,
    timeliness_summary,
)
from sar_sim.metrics.utilization import (
    satellite_utilization,
    observation_count_per_satellite,
    memory_usage,
    target_distribution,
    utilization_summary,
)
from sar_sim.metrics.pipeline import evaluate_schedule, compare_solvers
from sar_sim.metrics.nesz import (
    nesz_linear,
    nesz_db,
    quality_score,
    quality_score_from_elevation,
    elevation_to_off_nadir,
    incidence_to_elevation,
    aggregate_quality,
    quality_summary,
)
