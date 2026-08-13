"""TDD tests for MOEA refactoring: GeomCache + MOEA-2 (f1+f2) + post-hoc f3.

Tests follow the TDD RED-GREEN-REFACTOR cycle.
"""

import sys
import numpy as np
from pathlib import Path

# ── Path setup: add source workspace ───────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from sar_sim.types import GroundTarget, ObservationWindow
from sar_sim.solver.types import (
    AgileSARInstance,
    AgileTask,
    precompute_geometry,
)
from sar_sim.solver.moea import (
    SARSchedulingProblem,
    decode_solution,
    solutions_to_frontier,
    moea_solver,
)

# ═══════════════════════════════════════════════════════════════════════════
# Helper: build a minimal 2-task instance with precomputed geometry
# ═══════════════════════════════════════════════════════════════════════════

def _build_2task_instance(seed: int = 42) -> AgileSARInstance:
    """Build a minimal AgileSARInstance with 2 tasks and precomputed geom_cache."""
    np.random.seed(seed)

    t0 = 1_000_000_000.0  # reference epoch

    # Create 2 targets at distinct lat/lon for distinct geometry
    targets = [
        GroundTarget(target_id="T0", lat=30.0, lon=100.0, priority=10),
        GroundTarget(target_id="T1", lat=32.0, lon=102.0, priority=5),
    ]

    # Create two tasks with simple time windows
    tasks = []
    for i, tgt in enumerate(targets):
        t_earliest = t0 + i * 200.0
        t_latest = t_earliest + 300.0

        # Create a dummy ObservationWindow list
        from datetime import datetime, timezone, timedelta
        t_opt = datetime.fromtimestamp(t_earliest + 125.0, tz=timezone.utc)
        w = ObservationWindow(
            satellite_id="SAT1",
            target_id=tgt.target_id,
            t_start=datetime.fromtimestamp(t_earliest, tz=timezone.utc),
            t_end=datetime.fromtimestamp(t_latest, tz=timezone.utc),
            t_optimal=t_opt,
            elevation=75.0,  # high elevation -> low phi
            off_nadir_angle=15.0,
            look_direction="right",
            duration_min=30.0,
        )

        tasks.append(AgileTask(
            task_id=i,
            target_id=tgt.target_id,
            priority=float(tgt.priority),
            windows=[w],
            phi_min=0.2618,   # 15 deg off-nadir
            phi_max=0.8727,   # 50 deg off-nadir
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=30.0,
            energy=50000.0,
            memory=5e8,
            phi_min_res=0.0,
            time_span=t_latest - 30.0 - t_earliest,  # precomputed
        ))

    instance = AgileSARInstance(
        tasks=tasks,
        N=2,
        phi_min=0.2618,
        phi_max=0.8727,
        max_slew_rate=0.0524,
        settle_time=5.0,
        energy_budget=1e7,
        memory_budget=1e11,
        target_map={t.target_id: t for t in targets},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t0,
    )

    # Precompute geometry (Step 1 deliverable)
    precompute_geometry(instance, step_s=10.0)

    return instance


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: MOEA-2 (n_obj=2) optimizes f1 and f2 (geometric resolution)
# ═══════════════════════════════════════════════════════════════════════════

def test_c1_optimizes_f1_and_f2():
    """n_obj=2 outputs (-f1, -f2), MOEA-2 optimizes geometric resolution."""
    instance = _build_2task_instance()
    problem = SARSchedulingProblem(instance, n_obj=2)

    N = instance.N
    # Compute expected f2 (geometric resolution) at tau=0.6
    f2_expected = 0.0
    for i in range(N):
        task = instance.tasks[i]
        t_act = task.t_earliest + 0.6 * (
            task.t_latest - task.duration - task.t_earliest)
        geom = instance.geom_cache.lookup(i, t_act)
        # RDR-066 elevation-plane caliber: f2 = sqrt(cos²ψ − cos²ξ)
        f2_expected += np.sqrt(max(geom.cos_psi ** 2 - np.cos(geom.phi) ** 2, 0.0))

    pop = np.ones((1, 2 * N)) * 0.6

    out = {}
    problem._evaluate(pop, out)

    assert "F" in out
    F = out["F"]
    assert F.shape == (1, 2)

    f1_norm = -F[0, 0]
    f2_mean = -F[0, 1]  # should be mean f2 (geometric resolution)
    f2_exp_mean = f2_expected / N  # mean, not sum

    assert np.isclose(f1_norm, 15.0 / max(problem.f1_gbl, 1.0))
    assert np.isclose(f2_mean, f2_exp_mean, rtol=1e-5), (
        f"Column 1 should be mean f2 (geometric resolution), got {f2_mean}, expected {f2_exp_mean}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: MOEA-2 frontier contains f1/f2/f3 (f3 post-hoc), all 3 fields
# ═══════════════════════════════════════════════════════════════════════════

def test_c1_frontier_contains_f3_posthoc():
    """2-obj moea_solver metadata has f3_posthoc, frontier has f1/f2/f3.

    f3 is computed from geom_cache but stored post-hoc (not optimized).
    """
    instance = _build_2task_instance()

    N = instance.N
    # Single individual: select both tasks
    X = np.zeros(2 * N)
    X[:N] = 1.0
    X[N:] = 0.5

    frontier = solutions_to_frontier(X, instance)

    assert len(frontier) > 0, "Frontier should not be empty"
    sol = frontier[0]

    # Must have f1, f2, f3 keys
    assert "f1" in sol
    assert "f2" in sol
    assert "f3" in sol

    # f1 should be sum of priorities = 15
    assert np.isclose(sol["f1"], 15.0)

    # f2 should be > 0 (geometric resolution, optimized)
    assert sol["f2"] > 0.0

    # f3 should be >= 0 (NESZ radiometric, computed post-hoc)
    assert sol["f3"] >= 0.0

    # Now verify f2 != f3 (they measure different things)
    assert not np.isclose(sol["f2"], sol["f3"], rtol=1e-5), (
        "f2=%s should differ from f3=%s (different physical quantities)"
        % (sol["f2"], sol["f3"])
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: _evaluate uses geom_cache.lookup, NOT compute_full_attitude
# ═══════════════════════════════════════════════════════════════════════════

def test_geom_cache_used_not_full_attitude():
    """Verify _evaluate uses geom_cache.lookup, not compute_full_attitude."""
    import sar_sim.solver.moea as moea_mod
    from sar_sim.solver.types import compute_full_attitude as cfa_original

    instance = _build_2task_instance()
    problem = SARSchedulingProblem(instance, n_obj=2)

    # Monkey-patch compute_full_attitude to raise if called
    def _fail_if_called(*args, **kwargs):
        raise AssertionError(
            "compute_full_attitude was called - should use geom_cache.lookup instead"
        )

    moea_mod.compute_full_attitude = _fail_if_called

    try:
        N = instance.N
        pop = np.ones((1, 2 * N)) * 0.6  # select both
        out = {}
        problem._evaluate(pop, out)

        # Should reach here without raising
        assert "F" in out
        assert out["F"].shape[1] == 2
    finally:
        # Restore original
        moea_mod.compute_full_attitude = cfa_original


# ═══════════════════════════════════════════════════════════════════════════
# Test 4: MOEA-3 (n_obj=3) unchanged - still outputs (-f1, -f2, -f3)
# ═══════════════════════════════════════════════════════════════════════════

def test_c2_unchanged():
    """n_obj=3 outputs (-f1, -f2, -f3)."""
    instance = _build_2task_instance()
    problem = SARSchedulingProblem(instance, n_obj=3)

    N = instance.N
    # Select both tasks
    pop = np.ones((2, 2 * N)) * 0.6
    pop[0, N:] = 0.3  # different timing

    out = {}
    problem._evaluate(pop, out)

    assert "F" in out
    F = out["F"]
    assert F.shape == (2, 3)

    assert np.all(F < 0)

    # Column 0: -f1 (profit)
    assert np.allclose(-F[:, 0], 15.0)

    # Column 1: -f2 (geometric resolution)
    assert np.all(-F[:, 1] > 0)

    # Column 2: -f3 (NESZ radiometric)
    assert np.all(-F[:, 2] >= 0)
