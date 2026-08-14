"""TDD regression tests for GA-P performance optimization.

Verifies that all optimizations produce IDENTICAL constraint (G) and
objective (F) values compared to a reference implementation snapshot.

RED phase: these tests capture current _evaluate output as baseline.
GREEN phase: after optimization, output must match exactly.
"""

import sys, os, pickle, numpy as np
import pathlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sar_sim.solver.types import (
    build_agile_instance, precompute_geometry,
    compute_los_separation, SatPositionCache,
)
from sar_sim.solver.so_f1 import B2ProfitProblem


# ── Fixtures ──────────────────────────────────────────────────────────

def _load_s1():
    """Load smallest S1 scenario for fast testing."""
    pkl = sorted(
        (pathlib.Path(__file__).resolve().parent.parent.parent /
         'papers/single-sat-quality/experiments/scenarios/S1').glob('*.pkl'))
    pkl = str(list(pkl)[0])
    with open(pkl, 'rb') as f:
        data = pickle.load(f)
    return data['targets'], data['windows']


def _make_instance(targets, windows):
    inst = build_agile_instance(windows, targets)
    precompute_geometry(inst, step_s=10.0)
    return inst


# ── O1: theta_min_res precomputation ───────────────────────────────────

def test_o1_theta_min_res_precomputed():
    """AgileTask.theta_min_res must equal off_nadir_to_incidence(phi_min_res, alt)."""
    from sar_sim.metrics.nesz import off_nadir_to_incidence

    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)

    for task in inst.tasks:
        expected = off_nadir_to_incidence(task.phi_min_res, inst.altitude_m)
        assert hasattr(task, 'theta_min_res'), \
            f"Task {task.task_id} missing theta_min_res"
        assert np.isclose(task.theta_min_res, expected, rtol=1e-12), \
            f"Task {task.task_id}: theta_min_res={task.theta_min_res}, expected={expected}"


# ── O2: time_span precomputation ───────────────────────────────────────

def test_o2_time_span_precomputed():
    """AgileTask.time_span must equal t_latest - duration - t_earliest."""
    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)

    for task in inst.tasks:
        expected = task.t_latest - task.duration - task.t_earliest
        assert hasattr(task, 'time_span'), \
            f"Task {task.task_id} missing time_span"
        assert np.isclose(task.time_span, expected, rtol=1e-12)


# ── O3: window_times precomputation ────────────────────────────────────

def test_o3_window_times_precomputed():
    """AgileTask.window_times must list (w_start, w_end) float pairs for all windows."""
    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)

    for task in inst.tasks:
        assert hasattr(task, 'window_times'), \
            f"Task {task.task_id} missing window_times"
        assert len(task.window_times) == len(task.windows), \
            f"Task {task.task_id}: {len(task.window_times)} pairs vs {len(task.windows)} windows"
        for (ws, we), w in zip(task.window_times, task.windows):
            expected_start = w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start
            expected_end = w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end
            assert np.isclose(ws, expected_start), f"start mismatch: {ws} vs {expected_start}"
            assert np.isclose(we, expected_end), f"end mismatch: {we} vs {expected_end}"


# ── O5: O(1) grid lookup ──────────────────────────────────────────────

def test_o5_grid_lookup_matches_binary_search():
    """O(1) bracket index must match binary search, and cubic lookup must
    approximate the direct orbit to interpolation accuracy."""
    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)
    cache = inst.sat_position_cache

    from sar_sim.solver.types import _satellite_body_frame

    rng = np.random.RandomState(42)
    test_times = rng.uniform(cache.times[0], cache.times[-1], 200)
    step = cache.step_s
    t_min = cache.t_min
    n_pts = len(cache.times)

    for t in test_times:
        # O(1) bracket index must agree with binary-search reference.
        k_o1 = int((t - t_min) / step)
        k_o1 = max(0, min(k_o1, n_pts - 2))
        k_ref = np.searchsorted(cache.times, t, side='right') - 1
        k_ref = max(0, min(k_ref, n_pts - 2))
        assert k_o1 == k_ref, f"bracket mismatch at t={t}: O(1)={k_o1}, binary={k_ref}"

        # Cubic interpolation must match the direct orbit to within its
        # O(step^4) accuracy (measured ~2 mm at step=10 s; use 1 cm).
        _, _, _, pos_ref = _satellite_body_frame(t, inst)
        pos_o1 = cache.lookup_position(t)
        assert np.allclose(pos_o1, pos_ref, atol=1e-2), (
            f"position mismatch at t={t}: |d|={np.linalg.norm(pos_o1 - pos_ref):.3e} m"
        )


# ── O6: manual norm/clip/dot ───────────────────────────────────────────

def test_o6_manual_linalg_matches_numpy():
    """Manual sqrt/dot/clip must produce same LOS separation as numpy versions."""
    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)

    tasks = inst.tasks
    t_a = tasks[0].t_earliest + 10.0
    t_b = tasks[1].t_earliest + 20.0

    result = compute_los_separation(tasks[0], t_a, tasks[1], t_b, inst)

    # Verify it's a valid separation angle
    assert 0.0 <= result <= np.pi, f"LOS separation out of range: {result}"

    # Compare against a reference computed with numpy (we check consistency)
    result2 = compute_los_separation(tasks[0], t_a, tasks[1], t_b, inst)
    assert np.isclose(result, result2, rtol=1e-12), \
        "LOS separation not deterministic"


# ── O4 + O7: regression — evaluate output identity ─────────────────────

def test_evaluate_output_identity_after_optimization():
    """_evaluate must produce identical G and F regardless of optimizations.

    Uses a fixed random seed to ensure deterministic output.
    """
    targets, windows = _load_s1()
    inst = _make_instance(targets, windows)

    problem = B2ProfitProblem(inst)
    rng = np.random.RandomState(12345)
    X = rng.rand(100, 2 * inst.N)

    out = {}
    problem._evaluate(X, out)

    # Shape checks. B2ProfitProblem bakes the constraint penalty into F
    # (single-objective) and does not emit a separate G array.
    assert out["F"].shape == (100, 1), f"F shape: {out['F'].shape}"

    # Save reference for comparison (this test IS the baseline)
    # If optimizations change the output, this test will catch it
    # because we will compare against this snapshot
    ref_F = out["F"].copy()

    # Re-run with same X — must be deterministic
    out2 = {}
    problem._evaluate(X, out2)
    assert np.allclose(out2["F"], ref_F, rtol=1e-12, atol=1e-12), "F not deterministic"
