"""Solver package: CSP formulation + heuristic/exact solvers."""

from sar_sim.solver.csp import (
    CSPInstance,
    build_csp_instance,
    compute_solution_score,
    validate_solution,
    schedule_from_indices,
)
from sar_sim.solver.greedy import (
    greedy_weighted,
    greedy_by_satellite,
    greedy_solver,
)
from sar_sim.solver.ga import ga_solver
from sar_sim.solver.ilp import ilp_solver
from sar_sim.solver.types import (
    AgileTask,
    AgileSARInstance,
    build_agile_instance,
    compute_transition_time,
)
from sar_sim.solver.baselines import (
    baseline_b1,
    baseline_b2,
    BaselineResult,
    compare_with_baselines,
)

# ── MOEA symbols: lazy-imported to avoid triggering pymoo on solver import ─

_LAZY_MOEA = {
    "moea_solver",
    "SARSchedulingProblem",
    "decode_solution",
    "solutions_to_frontier",
}

_LAZY_SOLVER_FACTORY = {
    "multi_moea_solver",
    "compare_algorithms",
    "compute_hv",
    "compute_igd",
    "build_reference_frontier",
    "format_comparison_table",
    "AlgorithmConfig",
}

_LAZY_SO_F1 = {
    "B2ProfitProblem",
    "b2_profit_solver",
}


_LAZY_CBBA = {
    "cbba_solver",
    "compute_score",
}


def __getattr__(name: str):
    if name in _LAZY_MOEA:
        import sar_sim.solver.moea as _moea
        obj = getattr(_moea, name)
        # Cache so subsequent lookups don't re-import
        globals()[name] = obj
        return obj
    if name in _LAZY_SOLVER_FACTORY:
        import sar_sim.solver.solver_factory as _sf
        obj = getattr(_sf, name)
        globals()[name] = obj
        return obj
    if name in _LAZY_SO_F1:
        import sar_sim.solver.so_f1 as _so_f1
        obj = getattr(_so_f1, name)
        globals()[name] = obj
        return obj
    if name in _LAZY_CBBA:
        import sar_sim.solver.cbba as _cbba
        obj = getattr(_cbba, name)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module 'sar_sim.solver' has no attribute '{name}'")


def __dir__() -> list:
    base = dir()  # noqa: F821
    return sorted(set(base) | _LAZY_MOEA | _LAZY_SOLVER_FACTORY | _LAZY_SO_F1 | _LAZY_CBBA)
