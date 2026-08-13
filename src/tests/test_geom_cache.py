"""TDD tests for geometry precomputation (GeomCache).

Tests follow the TDD RED-GREEN-REFACTOR cycle.
Phase 1 (RED): All tests written first, expected to FAIL because
GeomPoint, GeomCache, and precompute_geometry do not exist yet.
"""

import sys
import numpy as np
from pathlib import Path

# ── Path setup: add source workspace ───────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from sar_sim.types import GroundTarget
from sar_sim.solver.types import (
    AgileSARInstance,
    AgileTask,
    compute_full_attitude,
    GeomPoint,
    GeomCache,
    precompute_geometry,
)
from sar_sim.metrics.nesz import off_nadir_to_incidence, quality_score

# ═══════════════════════════════════════════════════════════════════════════
# Test 1: Basic precomputation on minimal instance
# ═══════════════════════════════════════════════════════════════════════════


def test_precompute_basic():
    """对最小合法 instance（1 任务 × 1 窗口），预计算返回非空 cache."""
    # Build a minimal instance with 1 task
    target = GroundTarget(
        target_id="T000", lat=30.0, lon=100.0, priority=10,
    )
    t_start = 1000.0
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_start, t_latest=t_start + 200.0,
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
        orbit_ref_time_s=t_start,
    )

    # Precompute
    precompute_geometry(instance, step_s=10.0)

    # Assertions
    assert instance.geom_cache is not None, "geom_cache should not be None after precompute"
    assert len(instance.geom_cache.cache) == 1, (
        f"cache should have 1 entry (1 task), got {len(instance.geom_cache.cache)}"
    )
    arr = instance.geom_cache.cache[0]
    assert arr.ndim == 2, f"cache[0] should be 2D, got ndim={arr.ndim}"
    assert arr.shape[1] == 6, f"cache[0] should have 6 columns, got {arr.shape[1]}"
    # With t_max - t_min = 170s, step=10 → ceil(170/10)+1 = 18 points
    assert arr.shape[0] >= 2, (
        f"cache[0] should have at least 2 points, got {arr.shape[0]}"
    )
    # Check no NaN
    assert not np.any(np.isnan(arr)), "cache should contain no NaN values"


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: Lookup accuracy at exact sampling points
# ═══════════════════════════════════════════════════════════════════════════


def test_lookup_accuracy():
    """采样点精确命中时，lookup 返回值 ≈ compute_full_attitude 直接算的值（误差 < 0.001 rad）."""
    target = GroundTarget(
        target_id="T000", lat=30.0, lon=100.0, priority=10,
    )
    t_start = 1000.0
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_start, t_latest=t_start + 300.0,
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
        orbit_ref_time_s=t_start,
    )

    precompute_geometry(instance, step_s=10.0)
    cache = instance.geom_cache

    # Pick the exact time at the midpoint of the grid
    arr = cache.cache[0]
    mid_idx = len(arr) // 2
    t_mid = arr[mid_idx, 0]

    # Lookup at exact grid point
    gp = cache.lookup(0, t_mid)

    # Compute directly with compute_full_attitude (phi_signed=1.0 as spec says)
    roll, pitch, squint = compute_full_attitude(task, t_mid, 1.0, instance)

    # phi: abs(roll)
    assert abs(gp.phi - abs(roll)) < 0.001, (
        f"phi mismatch: lookup={gp.phi:.6f}, direct={abs(roll):.6f}, diff={gp.phi - abs(roll):.6f}"
    )
    # psi_sq: squint
    assert abs(gp.psi_sq - squint) < 0.001, (
        f"psi_sq mismatch: lookup={gp.psi_sq:.6f}, direct={squint:.6f}"
    )
    # cos_psi: cos(squint)
    assert abs(gp.cos_psi - np.cos(squint)) < 0.001, (
        f"cos_psi mismatch: lookup={gp.cos_psi:.6f}, direct={np.cos(squint):.6f}"
    )
    # theta: off_nadir_to_incidence(abs(roll))
    theta_direct = off_nadir_to_incidence(abs(roll), instance.altitude_m)
    assert abs(gp.theta - theta_direct) < 0.001, (
        f"theta mismatch: lookup={gp.theta:.6f}, direct={theta_direct:.6f}"
    )
    # q_nesz: quality_score(theta)
    q_direct = quality_score(theta_direct)
    assert abs(gp.q_nesz - q_direct) < 0.001, (
        f"q_nesz mismatch: lookup={gp.q_nesz:.6f}, direct={q_direct:.6f}"
    )
    # t should match
    assert abs(gp.t - t_mid) < 0.001, f"t mismatch: {gp.t} != {t_mid}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: Interpolation between sampling points
# ═══════════════════════════════════════════════════════════════════════════


def test_interpolation_monotonic():
    """插值在相邻采样点之间平滑，无 NaN."""
    target = GroundTarget(
        target_id="T000", lat=30.0, lon=100.0, priority=10,
    )
    t_start = 1000.0
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_start, t_latest=t_start + 300.0,
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
        orbit_ref_time_s=t_start,
    )

    precompute_geometry(instance, step_s=10.0)
    cache = instance.geom_cache
    arr = cache.cache[0]

    # Pick two adjacent grid points and interpolate at midpoint
    k = len(arr) // 2
    t_lo = arr[k, 0]
    t_hi = arr[k + 1, 0]
    t_mid = (t_lo + t_hi) / 2.0

    gp = cache.lookup(0, t_mid)

    # No NaN in result
    assert not np.isnan(gp.phi), "phi should not be NaN"
    assert not np.isnan(gp.psi_sq), "psi_sq should not be NaN"
    assert not np.isnan(gp.cos_psi), "cos_psi should not be NaN"
    assert not np.isnan(gp.theta), "theta should not be NaN"
    assert not np.isnan(gp.q_nesz), "q_nesz should not be NaN"

    # Interpolated values should be between lo and hi (monotonic check for phi, theta, q)
    # For phi (monotonically increasing or decreasing, we check between)
    phi_lo, phi_hi = arr[k, 1], arr[k + 1, 1]
    assert min(phi_lo, phi_hi) <= gp.phi <= max(phi_lo, phi_hi), (
        f"phi interpolation out of bounds: lo={phi_lo:.6f}, mid={gp.phi:.6f}, hi={phi_hi:.6f}"
    )

    # q_nesz monotonic check
    q_lo, q_hi = arr[k, 5], arr[k + 1, 5]
    assert min(q_lo, q_hi) <= gp.q_nesz <= max(q_lo, q_hi), (
        f"q_nesz interpolation out of bounds: lo={q_lo:.6f}, mid={gp.q_nesz:.6f}, hi={q_hi:.6f}"
    )

    # t should be exact
    assert abs(gp.t - t_mid) < 0.01, f"t mismatch: {gp.t} != {t_mid}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 4: Boundary clamping
# ═══════════════════════════════════════════════════════════════════════════


def test_boundary_clamp():
    """t_actual 超出窗口返回最近端点值."""
    target = GroundTarget(
        target_id="T000", lat=30.0, lon=100.0, priority=10,
    )
    t_start = 1000.0
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=t_start, t_latest=t_start + 200.0,
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
        orbit_ref_time_s=t_start,
    )

    precompute_geometry(instance, step_s=10.0)
    cache = instance.geom_cache
    arr = cache.cache[0]

    # t_actual < t_min → should return first row's values
    t_before = arr[0, 0] - 50.0
    gp_before = cache.lookup(0, t_before)
    assert gp_before.phi == arr[0, 1], (
        f"Before clamp: phi={gp_before.phi} != first_row_phi={arr[0, 1]}"
    )
    assert gp_before.psi_sq == arr[0, 2], "psi_sq should match first row when before window"

    # t_actual > t_max → should return last row's values
    t_after = arr[-1, 0] + 50.0
    gp_after = cache.lookup(0, t_after)
    assert gp_after.phi == arr[-1, 1], (
        f"After clamp: phi={gp_after.phi} != last_row_phi={arr[-1, 1]}"
    )
    assert gp_after.psi_sq == arr[-1, 2], "psi_sq should match last row when after window"


# ═══════════════════════════════════════════════════════════════════════════
# Test 5: Empty tasks — no crash
# ═══════════════════════════════════════════════════════════════════════════


def test_empty_tasks():
    """0 任务 instance 不崩溃，cache 为空 list."""
    instance = AgileSARInstance(
        tasks=[], N=0,
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=0.0,
    )

    # Should not raise
    precompute_geometry(instance, step_s=10.0)

    assert instance.geom_cache is not None, "geom_cache should be set even for empty instance"
    assert len(instance.geom_cache.cache) == 0, (
        f"cache should be empty for 0 tasks, got {len(instance.geom_cache.cache)}"
    )
