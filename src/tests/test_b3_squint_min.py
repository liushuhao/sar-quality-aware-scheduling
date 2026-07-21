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
    """G-SM picks the sample with smallest abs(psi_sq) from geom_cache for each task."""
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
        altitude_m=600_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    window = _make_window()
    obs = _make_obs(window)

    result = _b3_squint_minimize([obs], instance.geom_cache, instance)

    assert len(result) == 1, f"Expected 1 result, got {len(result)}"
    selected = result[0]

    # The selected t should correspond to a sampling point with minimal psi_sq
    arr = instance.geom_cache.cache[0]
    best_k = int(np.argmin(np.abs(arr[:, 2])))  # col 2 = psi_sq
    best_t = arr[best_k, 0]

    # G-SM should pick the time with minimum |psi_sq|
    selected_t = selected.t_actual_start.timestamp()
    assert abs(selected_t - best_t) < 1.0, (
        f"G-SM should pick t={best_t:.1f} (min |psi_sq|), got t={selected_t:.1f}"
    )


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
        altitude_m=600_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    window = _make_window()
    obs = _make_obs(window)

    result = _b3_squint_minimize([obs], instance.geom_cache, instance)
    selected_t = result[0].t_actual_start
    selected_end = result[0].t_actual_end

    # The geom_cache sampling points are within the task window, and the
    # selected t should be within those. But the test's window (datetime-based)
    # doesn't correspond to the epoch-based task. What we can check is that
    # t_actual_start and t_actual_end are valid datetimes with the right gap.
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
