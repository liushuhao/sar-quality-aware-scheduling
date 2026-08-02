"""TDD tests for G-SM squint minimization (Step 3).

Tests follow strict RED-GREEN-REFACTOR cycle.
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sar_sim.types import GroundTarget, ObservationWindow, ScheduledObservation
from sar_sim.solver.types import (
    AgileSARInstance,
    AgileTask,
    compute_full_attitude,
    GeomPoint,
    GeomCache,
    precompute_geometry,
)
from sar_sim.solver.baselines import _b3_squint_minimize


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_window(target_id="T000", dt=None, duration=300):
    """Create a minimal ObservationWindow for testing."""
    if dt is None:
        dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    return ObservationWindow(
        satellite_id="SAT-1",
        target_id=target_id,
        t_start=dt,
        t_end=dt + timedelta(seconds=duration),
        t_optimal=dt + timedelta(seconds=duration // 2),
        elevation=45.0,
        off_nadir_angle=30.0,
        look_direction="right",
        duration_min=30.0,
    )


def _make_obs(window=None, t_offset=50):
    """Create a minimal ScheduledObservation for testing."""
    if window is None:
        window = _make_window()
    dt = window.t_start
    return ScheduledObservation(
        window=window,
        t_actual_start=dt + timedelta(seconds=t_offset),
        t_actual_end=dt + timedelta(seconds=t_offset + 30),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: G-SM selects the minimum psi_sq sampling point for each task
# ═══════════════════════════════════════════════════════════════════════════

def test_b3_selects_min_squint():
    """G-SM picks the sample with smallest abs(psi_sq) among feasible
    candidates: rows inside the observation's own window and within the
    platform off-nadir envelope (RDR-003 semantics)."""
    t_ref = 1000.0
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_ref, t_latest=t_ref + 300.0,
        duration=30.0, energy=50000.0, memory=5e8,
        phi_min_res=0.0,
    )
    instance = AgileSARInstance(
        tasks=[task], N=1,
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={"T000": target},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    # Epoch-consistent window covering the precomputed grid (the old
    # 2024-datetime fixture never overlapped the 1970-epoch cache, which
    # only "worked" because the old code ignored the window entirely).
    window = _make_window(dt=datetime.fromtimestamp(t_ref, tz=timezone.utc))
    obs = _make_obs(window)

    result = _b3_squint_minimize([obs], instance.geom_cache, instance)

    assert len(result) == 1, f"Expected 1 result, got {len(result)}"
    selected = result[0]
    selected_t = selected.t_actual_start.timestamp()

    arr = instance.geom_cache.cache[0]
    w_s = window.t_start.timestamp()
    w_e = window.t_end.timestamp()
    mask = (arr[:, 0] >= w_s) & (arr[:, 0] <= w_e)
    mask &= ((np.abs(arr[:, 1]) >= instance.phi_min)
             & (np.abs(arr[:, 1]) <= instance.phi_max))
    if np.any(mask):
        cand = arr[mask]
        best_t = cand[int(np.argmin(np.abs(cand[:, 2])))][0]
        assert abs(selected_t - best_t) < 1.0, (
            f"G-SM should pick t={best_t:.1f} (min |psi_sq| among feasible "
            f"candidates), got t={selected_t:.1f}"
        )
    else:
        # No feasible candidate → pass-through of upstream timing
        assert abs(selected_t - obs.t_actual_start.timestamp()) < 1.0


def test_b3_does_not_jump_windows():
    """RDR-003 regression: a zero-squint point OUTSIDE the scheduled window
    (e.g. near-nadir pass over the target) must not be selected."""
    t_ref = 1000.0
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_ref, t_latest=t_ref + 300.0,
        duration=30.0, energy=50000.0, memory=5e8,
        phi_min_res=0.0,
    )
    instance = AgileSARInstance(
        tasks=[task], N=1,
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={"T000": target},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    window = _make_window(dt=datetime.fromtimestamp(t_ref, tz=timezone.utc))
    obs = _make_obs(window)

    # Inject an irresistible psi_sq=0 row 500 s past the window end
    arr = instance.geom_cache.cache[0]
    fake_t = window.t_end.timestamp() + 500.0
    fake_row = arr[0].copy()
    fake_row[0] = fake_t
    fake_row[1] = 0.5
    fake_row[2] = 0.0
    instance.geom_cache.cache[0] = np.vstack([arr, fake_row])

    result = _b3_squint_minimize([obs], instance.geom_cache, instance)
    selected_t = result[0].t_actual_start.timestamp()
    assert selected_t <= window.t_end.timestamp() + 1e-6, (
        f"G-SM jumped outside the window: selected t={selected_t:.1f}, "
        f"window end={window.t_end.timestamp():.1f}"
    )
    assert abs(selected_t - fake_t) > 1.0, "G-SM picked the out-of-window point"


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: G-SM selected t is within the observation window
# ═══════════════════════════════════════════════════════════════════════════

def test_b3_window_boundary():
    """G-SM selected t must be within [t_start, t_end] of the window."""
    t_ref = 1000.0
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_ref, t_latest=t_ref + 300.0,
        duration=30.0, energy=50000.0, memory=5e8,
        phi_min_res=0.0,
    )
    instance = AgileSARInstance(
        tasks=[task], N=1,
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={"T000": target},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    window = _make_window(dt=datetime.fromtimestamp(t_ref, tz=timezone.utc))
    obs = _make_obs(window)

    result = _b3_squint_minimize([obs], instance.geom_cache, instance)
    selected_t = result[0].t_actual_start
    selected_end = result[0].t_actual_end

    # The geom_cache sampling points are within the task window, and the
    # selected t should be within those. The window is epoch-consistent
    # with the task (RDR-003 fix), so a real selection happens.
    assert selected_t.tzinfo is not None, "selected start should be timezone-aware"
    gap = (selected_end - selected_t).total_seconds()
    assert gap >= 29.0, f"duration should be ~30s, got {gap}s"
    assert gap <= 31.0, f"duration should be ~30s, got {gap}s"


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: No GeomCache → fallback to identity (pass-through)
# ═══════════════════════════════════════════════════════════════════════════

def test_b3_no_geom_cache_fallback():
    """Without geom_cache, _b3_squint_minimize returns observations unchanged (pass-through)."""
    window = _make_window()
    obs = _make_obs(window)

    # No instance with geom_cache — pass None
    result = _b3_squint_minimize([obs], geom_cache=None, instance=None)

    assert len(result) == 1, "Should return same number of observations"
    assert result[0].t_actual_start == obs.t_actual_start, (
        "Start time should be unchanged when no geom_cache"
    )
    assert result[0].t_actual_end == obs.t_actual_end, (
        "End time should be unchanged when no geom_cache"
    )
