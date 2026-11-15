"""TDD tests for GA-P-BL: GA-P with G-BL hot-start seeding.

RED phase: tests must fail before implementation exists.
"""

import sys, os, pickle, numpy as np, pathlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sar_sim.solver.so_f1 import b2_profit_solver_bl_seeded, B2ProfitProblem
from sar_sim.solver.baselines import baseline_b1
from sar_sim.solver.types import build_agile_instance, precompute_geometry
from sar_sim.types import SolverResult


def _load_s5():
    pkl = sorted(
        (pathlib.Path(__file__).resolve().parent.parent.parent /
         'papers/single-sat-quality/experiments/scenarios/S5').glob('*.pkl'))[0]
    with open(str(pkl), 'rb') as f:
        data = pickle.load(f)
    return data['targets'], data['windows']


def test_bl_seeded_not_worse_than_gbl():
    """GA-P-BL f1 >= G-BL f1 (hot-start from best-known feasible solution).

    RED: b2_profit_solver_bl_seeded doesn't exist yet.
    """
    targets, windows = _load_s5()
    gbl = baseline_b1(windows, targets)

    result = b2_profit_solver_bl_seeded(
        windows, targets,
        population_size=100, n_generations=200, seed=0,
    )
    assert result.metadata['f1'] >= gbl.f1, \
        f"GA-P-BL f1={result.metadata['f1']:.0f} < G-BL f1={gbl.f1:.0f}"


def test_bl_seeded_not_worse_than_gbl_multiple():
    """Multiple seeds: GA-P-BL f1 >= G-BL f1 consistently."""
    targets, windows = _load_s5()
    gbl = baseline_b1(windows, targets)

    all_ok = True
    for seed in [0, 42, 101, 256, 789]:
        result = b2_profit_solver_bl_seeded(
            windows, targets, population_size=100, n_generations=200, seed=seed)
        if result.metadata['f1'] < gbl.f1:
            all_ok = False
            print(f'  FAIL seed={seed}: GA-P-BL={result.metadata["f1"]:.0f} < G-BL={gbl.f1:.0f}')
    assert all_ok, "GA-P-BL f1 < G-BL on some seeds"


def test_bl_seeded_output_format():
    """Schema check."""
    targets, windows = _load_s5()
    result = b2_profit_solver_bl_seeded(
        windows, targets, population_size=100, n_generations=200, seed=0)
    assert isinstance(result, SolverResult)
    meta = result.metadata
    for field in ['solver', 'f1', 'f2', 'f3', 'n_selected', 'n_tasks',
                  'selected', 't_actuals', 'n_generations', 'population_size']:
        assert field in meta, f"Missing: {field}"
    assert meta['solver'] in ('b2_profit_bl_seeded', 'ga_hotstart')
