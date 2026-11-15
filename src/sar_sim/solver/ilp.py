"""Integer Linear Programming (exact) solver for SAR scheduling.

Uses Google OR-Tools CP-SAT for Maximum Weight Independent Set formulation.
Best for small-to-medium instances (< ~500 windows).
"""

from typing import List, Optional
import numpy as np

from sar_sim.types import (
    ObservationWindow,
    ScheduledObservation,
    SolverResult,
    GroundTarget,
)
from sar_sim.solver.csp import (
    CSPInstance,
    build_csp_instance,
    schedule_from_indices,
    compute_solution_score,
    validate_solution,
)


def ilp_solver(
    windows: List[ObservationWindow],
    targets: List,
    time_limit_seconds: float = 30.0,
    **kwargs,
) -> SolverResult:
    """CP-SAT based exact solver.

    Formulation:
      max sum(weight_i * x_i)
      s.t. x_i + x_j <= 1  for all conflicting pairs (i,j)
           x_i ∈ {0,1}

    Uses or-tools CP-SAT solver with time limit.

    Args:
        windows: candidate observation windows
        targets: ground targets
        time_limit_seconds: solver time limit

    Returns:
        SolverResult
    """
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        raise ImportError(
            "ortools not installed. Install with: pip install ortools"
        )

    csp = build_csp_instance(windows, targets)
    n = len(csp.windows)

    if n == 0:
        return SolverResult(
            schedule=(), score=0.0,
            metadata={"solver": "ilp_cpsat", "n_total": 0, "n_selected": 0, "valid": True},
        )

    model = cp_model.CpModel()

    # Variables
    x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

    # Conflicting pair constraints
    for i in range(n):
        for j in range(i + 1, n):
            if not csp.compatibility[i, j]:
                model.Add(x[i] + x[j] <= 1)

    # Objective: maximize weighted sum
    # CP-SAT uses integer coefficients; scale weights
    max_weight = max(csp.weights) if n > 0 else 1.0
    if max_weight > 0:
        scale = 1000.0 / max_weight  # Scale to ~0-1000 range
    else:
        scale = 1.0

    objective_terms = []
    for i in range(n):
        coeff = int(csp.weights[i] * scale)
        if coeff > 0:
            objective_terms.append(coeff * x[i])

    model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = 4  # Parallel search
    solver.parameters.log_search_progress = False

    status = solver.Solve(model)

    # Extract solution
    selected_indices = [i for i in range(n) if solver.Value(x[i]) == 1]

    schedule = schedule_from_indices(windows, selected_indices)
    score = compute_solution_score(csp, selected_indices)
    is_valid, _ = validate_solution(csp, selected_indices)

    status_map = {
        cp_model.OPTIMAL: "optimal",
        cp_model.FEASIBLE: "feasible",
        cp_model.INFEASIBLE: "infeasible",
        cp_model.MODEL_INVALID: "model_invalid",
        cp_model.UNKNOWN: "unknown",
    }

    return SolverResult(
        schedule=tuple(schedule),
        score=score,
        metadata={
            "solver": "ilp_cpsat",
            "status": status_map.get(status, "unknown"),
            "wall_time": solver.WallTime(),
            "n_selected": len(selected_indices),
            "n_total": n,
            "valid": is_valid,
            "objective_value": solver.ObjectiveValue(),
        },
    )
