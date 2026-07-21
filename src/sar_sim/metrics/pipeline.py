"""Metric pipeline runner — evaluates solver outputs comprehensively.

Runs all metrics (coverage, timeliness, utilization) on a schedule
and produces a unified report for benchmarking.
"""

from typing import List, Dict, Any
from datetime import datetime

from sar_sim.types import ScheduledObservation, GroundTarget, SolverResult
from sar_sim.conflict.resource import ResourceBudget
from sar_sim.metrics.coverage import coverage_summary
from sar_sim.metrics.timeliness import timeliness_summary
from sar_sim.metrics.utilization import utilization_summary


def evaluate_schedule(
    result: SolverResult,
    targets: List[GroundTarget],
    time_start: datetime,
    time_end: datetime,
    budget: ResourceBudget = None,
) -> Dict[str, Any]:
    """Run the full metric pipeline on a solver result.

    Args:
        result: solver output (schedule + metadata)
        targets: all ground targets
        time_start, time_end: planning horizon
        budget: resource budget for utilization comparison

    Returns:
        dict with all metrics, solver metadata, and combined report
    """
    observations = list(result.schedule)

    coverage = coverage_summary(observations, targets)
    timeliness = timeliness_summary(observations, targets, time_start, time_end)
    utilization = utilization_summary(observations, time_start, time_end, budget)

    return {
        "solver": result.metadata.get("solver", "unknown"),
        "solver_score": result.score,
        "solver_metadata": result.metadata,
        "coverage": coverage,
        "timeliness": timeliness,
        "utilization": utilization,
        "n_scheduled": len(observations),
    }


def compare_solvers(
    results: Dict[str, SolverResult],
    targets: List[GroundTarget],
    time_start: datetime,
    time_end: datetime,
    budget: ResourceBudget = None,
) -> Dict[str, Any]:
    """Compare multiple solvers against each other.

    Args:
        results: dict mapping solver_name -> SolverResult
        targets: all ground targets
        time_start, time_end: planning horizon
        budget: resource budget

    Returns:
        dict with per-solver evaluations and comparison table
    """
    evaluations = {}
    for name, result in results.items():
        evaluations[name] = evaluate_schedule(
            result, targets, time_start, time_end, budget
        )

    # Build comparison table
    comparison = []
    for name, eval_data in evaluations.items():
        comparison.append({
            "solver": name,
            "score": eval_data["solver_score"],
            "n_scheduled": eval_data["n_scheduled"],
            "coverage": eval_data["coverage"]["coverage_ratio"],
            "priority_coverage": eval_data["coverage"]["priority_weighted_coverage"],
            "violation_rate": eval_data["timeliness"]["violation_rate"],
            "mean_utilization": eval_data["utilization"]["mean_time_utilization"],
        })

    # Sort by score descending
    comparison.sort(key=lambda x: -x["score"])

    return {
        "evaluations": evaluations,
        "comparison": comparison,
        "best_solver": comparison[0]["solver"] if comparison else None,
    }
