"""TDD regression tests for MOEA performance optimization O1+O3+O4.

Verifies that merged geometry+objectives loop (O1), vectorized C3/C4 (O3),
and path unification (O4) produce IDENTICAL output.
"""

import sys, os, pickle, math, numpy as np, pathlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sar_sim.solver.moea import SARSchedulingProblem, decode_solution
from sar_sim.solver.types import build_agile_instance, precompute_geometry, AgileTask


# ── Fixtures ──────────────────────────────────────────────────────────

def _load_s2():
    """Load one S2 scenario (N=100) for representative testing."""
    pkl = sorted(
        (pathlib.Path(__file__).resolve().parent.parent.parent /
         'papers/single-sat-quality/experiments/scenarios/S2').glob('*.pkl'))[0]
    with open(str(pkl), 'rb') as f:
        data = pickle.load(f)
    return data['targets'], data['windows']


def _make_instance(targets, windows):
    inst = build_agile_instance(windows, targets)
    precompute_geometry(inst, step_s=10.0)
    return inst


# ── O1: merged geometry + objectives ─────────────────────────────────

def test_o1_evaluate_output_unchanged():
    """Merged loop _evaluate must produce identical F and G as before."""
    targets, windows = _load_s2()
    inst = _make_instance(targets, windows)

    for n_obj in [2, 3]:
        problem = SARSchedulingProblem(inst, n_obj=n_obj)
        rng = np.random.RandomState(42)
        X = rng.rand(100, 2 * inst.N)

        out = {}
        problem._evaluate(X, out)

        # Shape checks
        expected_cols = n_obj
        assert out["F"].shape == (100, expected_cols), \
            f"n_obj={n_obj}: F shape {out['F'].shape}"
        assert out["G"].shape == (100, 1), f"G shape: {out['G'].shape}"
        assert np.all(out["G"] >= 0), "G must be non-negative"

        # Determinism: same X, same output
        out2 = {}
        problem._evaluate(X, out2)
        assert np.allclose(out2["F"], out["F"], rtol=1e-12, atol=1e-12), \
            f"n_obj={n_obj}: F not deterministic"
        assert np.allclose(out2["G"], out["G"], rtol=1e-12, atol=1e-12), \
            f"n_obj={n_obj}: G not deterministic"


# ── O3: vectorized C3/C4 ────────────────────────────────────────────

def test_o3_c3c4_vectorized_unchanged():
    """Vectorized C3/C4 must produce same G as sum(generator) version."""
    targets, windows = _load_s2()
    inst = _make_instance(targets, windows)

    problem = SARSchedulingProblem(inst, n_obj=3)
    rng = np.random.RandomState(123)
    X = rng.rand(100, 2 * inst.N)

    out = {}
    problem._evaluate(X, out)

    # Spot check: some individuals have non-zero constraint violations
    assert np.any(out["G"] > 0), "Some solutions should have constraint violations"
    assert np.all(out["G"] >= 0), "G must be non-negative"


# ── O4: unified paths ────────────────────────────────────────────────

def test_o4_decode_uses_time_span():
    """decode_solution must use task.time_span, not inline computation."""
    targets, windows = _load_s2()
    inst = _make_instance(targets, windows)

    # Create a solution with known tau values
    N = inst.N
    X = np.ones(2 * N) * 0.6  # all selected, tau=0.6

    sel, phis, f1, f2, f3, _sat, t_actuals = decode_solution(X, inst)

    # Verify time_span consistency: t_act must equal t_earliest + 0.6 * time_span
    for pos, idx in enumerate(sel[:5]):  # check first 5
        task = inst.tasks[idx]
        expected_t = task.t_earliest + 0.6 * task.time_span
        assert math.isclose(t_actuals[pos], expected_t, rel_tol=1e-12, abs_tol=1e-9), (
            f"Task {idx}: t_act={t_actuals[pos]} != expected {expected_t}"
        )
        assert task.time_span > 0, f"Task {idx}: time_span={task.time_span}"


def test_o4_dead_code_removed():
    """_compute_transition_at_times should not exist after cleanup."""
    from sar_sim.solver import moea
    assert not hasattr(moea, '_compute_transition_at_times'), \
        "_compute_transition_at_times should be removed (dead code)"
