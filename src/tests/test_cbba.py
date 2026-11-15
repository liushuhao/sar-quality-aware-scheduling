"""TDD tests for CBBA (Consensus-Based Bundle Algorithm) solver.

Follows strict RED-GREEN-REFACTOR cycle.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# Test helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_window(target_id, sat_id, theta_deg):
    """Create a minimal window dict matching pilot runner format."""
    return {
        "target_id": target_id,
        "sat_id": sat_id,
        "t_start": 0.0,
        "t_end": 120.0,
        "theta_deg": theta_deg,
    }


def _make_target(tid, priority=1.0):
    """Create a minimal target dict matching pilot runner format."""
    return {"id": tid, "lat_deg": 0.0, "lon_deg": 0.0, "priority": priority}


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: Scoring function
# ═══════════════════════════════════════════════════════════════════════════

def test_compute_score_exists():
    """compute_score must be importable."""
    from sar_sim.solver.cbba import compute_score  # noqa: F401


def test_score_at_reference_theta():
    """At theta_ref=30deg, q(theta)=1.0, so score = priority."""
    from sar_sim.solver.cbba import compute_score

    target = _make_target(0, priority=5.0)
    theta_ref = math.radians(30.0)
    score = compute_score(target, theta_ref)
    assert score == pytest.approx(5.0)


def test_score_decreases_with_theta():
    """Score should decrease as incidence angle increases."""
    from sar_sim.solver.cbba import compute_score

    target = _make_target(0, priority=1.0)
    score_20 = compute_score(target, math.radians(20.0))
    score_40 = compute_score(target, math.radians(40.0))
    assert score_20 > score_40


def test_score_zero_at_grazing():
    """At theta=90deg, cos^3(theta)=0, score=0."""
    from sar_sim.solver.cbba import compute_score

    target = _make_target(0, priority=10.0)
    score = compute_score(target, math.radians(90.0))
    assert score == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: cbba_solver — bundle building
# ═══════════════════════════════════════════════════════════════════════════

def test_single_target_bundle():
    """One target, one satellite: target should be assigned."""
    from sar_sim.solver.cbba import cbba_solver

    targets = [_make_target(0, priority=5.0)]
    windows = [_make_window(0, 0, 30.0)]
    result = cbba_solver(windows, targets, n_sats=1)
    assert result["n_scheduled"] == 1
    assert result["f1_raw"] == pytest.approx(5.0)


def test_bundle_size_limit():
    """Bundle should not exceed bundle_size."""
    from sar_sim.solver.cbba import cbba_solver

    n = 50
    targets = [_make_target(i, priority=1.0) for i in range(n)]
    windows = [_make_window(i, 0, 30.0) for i in range(n)]
    result = cbba_solver(windows, targets, n_sats=1, bundle_size=10)
    assert result["n_scheduled"] <= 10


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: Consensus & Dedup
# ═══════════════════════════════════════════════════════════════════════════

def test_dedup_across_satellites():
    """Each target assigned to at most one satellite."""
    from sar_sim.solver.cbba import cbba_solver

    targets = [_make_target(0, priority=5.0)]
    windows = [
        _make_window(0, 0, 30.0),
        _make_window(0, 1, 30.0),
    ]
    result = cbba_solver(windows, targets, n_sats=2)
    assert result["n_scheduled"] == 1  # not duplicated


def test_multi_sat_distribution():
    """Multiple satellites distribute targets, no duplicates."""
    from sar_sim.solver.cbba import cbba_solver

    n_targets = 20
    targets = [_make_target(i, priority=1.0) for i in range(n_targets)]
    windows = []
    for i in range(n_targets):
        sat_id = i % 4  # each target visible to exactly one sat
        windows.append(_make_window(i, sat_id, 30.0))
    result = cbba_solver(windows, targets, n_sats=4, bundle_size=10)
    schedule = result["schedule"]
    target_ids = [s["target_id"] for s in schedule]
    assert len(target_ids) == len(set(target_ids)), "duplicate targets!"


def test_empty_input():
    """No windows should yield empty result."""
    from sar_sim.solver.cbba import cbba_solver

    result = cbba_solver([], [], n_sats=2)
    assert result["n_scheduled"] == 0
    assert result["f1_raw"] == 0.0
    assert result["converged"] is True


def test_convergence_within_max_rounds():
    """Algorithm should converge within max_rounds."""
    from sar_sim.solver.cbba import cbba_solver

    n_targets = 20
    targets = [_make_target(i, priority=1.0) for i in range(n_targets)]
    windows = []
    for i in range(n_targets):
        for s in range(4):
            windows.append(_make_window(i, s, 30.0))
    result = cbba_solver(windows, targets, n_sats=4, max_rounds=10, bundle_size=5)
    assert result["n_rounds"] <= 10
    assert result["n_scheduled"] <= 20


def test_priority_ordering():
    """Higher priority targets should be preferred over lower priority."""
    from sar_sim.solver.cbba import cbba_solver

    targets = [
        _make_target(0, priority=1.0),
        _make_target(1, priority=10.0),
        _make_target(2, priority=2.0),
    ]
    windows = [
        _make_window(0, 0, 30.0),
        _make_window(1, 0, 30.0),
        _make_window(2, 0, 30.0),
    ]
    result = cbba_solver(windows, targets, n_sats=1, bundle_size=1)
    assert result["n_scheduled"] == 1
    scheduled = result["schedule"]
    assert scheduled[0]["target_id"] == 1  # highest priority


def test_better_quality_wins():
    """When two sats see same target, sat with lower theta (better quality) wins."""
    from sar_sim.solver.cbba import cbba_solver

    targets = [_make_target(0, priority=10.0)]
    windows = [
        _make_window(0, 0, 20.0),  # better quality (lower theta)
        _make_window(0, 1, 45.0),  # worse quality
    ]
    result = cbba_solver(windows, targets, n_sats=2)
    assert result["n_scheduled"] == 1
    scheduled = result["schedule"]
    assert scheduled[0]["sat_id"] == 0  # sat 0 wins with better quality


def test_invisible_target_skipped():
    """Target without visibility window should not be assigned."""
    from sar_sim.solver.cbba import cbba_solver

    targets = [_make_target(0, priority=5.0)]
    windows = []  # no windows
    result = cbba_solver(windows, targets, n_sats=1)
    assert result["n_scheduled"] == 0
