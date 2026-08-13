"""TDD tests for post-hoc f2/f3 in baseline metadata (Step 3).

Tests follow strict RED-GREEN-REFACTOR cycle.
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from sar_sim.types import GroundTarget, ObservationWindow, ScheduledObservation
from sar_sim.solver.types import (
    AgileSARInstance,
    AgileTask,
    GeomCache,
    precompute_geometry,
)
from sar_sim.solver.baselines import baseline_b1, baseline_b2, baseline_b3


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


_WINDOW_TIME = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: G-BL metadata has f1, f2, f3
# ═══════════════════════════════════════════════════════════════════════════

def test_b1_metadata_has_f1_f2_f3():
    """G-BL BaselineResult.metadata must contain 'f1', 'f2', 'f3' keys."""
    window = _make_window("T000")
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)

    result = baseline_b1([window], [target])

    assert "f1" in result.metadata, "G-BL metadata should have 'f1'"
    assert "f2" in result.metadata, "G-BL metadata should have 'f2'"
    assert "f3" in result.metadata, "G-BL metadata should have 'f3'"
    # f1 should match the BaselineResult.f1
    assert abs(result.metadata["f1"] - result.f1) < 0.001, (
        f"metadata.f1={result.metadata['f1']} != result.f1={result.f1}"
    )
    # f2 should match BaselineResult.f2
    assert abs(result.metadata["f2"] - result.f2) < 0.001, (
        f"metadata.f2={result.metadata['f2']} != result.f2={result.f2}"
    )
    # f3 is post-hoc NESZ radiometric; should be >= 0
    assert result.metadata["f3"] >= 0, f"f3 should be >= 0, got {result.metadata['f3']}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: GA-P metadata has f1, f2, f3
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_metadata_has_f1_f2_f3():
    """GA-P BaselineResult.metadata must contain 'f1', 'f2', 'f3' keys."""
    window = _make_window("T000")
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)

    result = baseline_b2([window], [target], solver="greedy_weighted")

    assert "f1" in result.metadata, "GA-P metadata should have 'f1'"
    assert "f2" in result.metadata, "GA-P metadata should have 'f2'"
    assert "f3" in result.metadata, "GA-P metadata should have 'f3'"
    assert result.metadata["f3"] >= 0, f"f3 should be >= 0, got {result.metadata['f3']}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: G-SM metadata has f1, f2, f3
# ═══════════════════════════════════════════════════════════════════════════

def test_b3_metadata_has_f1_f2_f3():
    """G-SM BaselineResult.metadata must contain 'f1', 'f2', 'f3' keys."""
    window = _make_window("T000")
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)

    result = baseline_b3([window], [target])

    assert "f1" in result.metadata, "G-SM metadata should have 'f1'"
    assert "f2" in result.metadata, "G-SM metadata should have 'f2'"
    assert "f3" in result.metadata, "G-SM metadata should have 'f3'"
    assert result.metadata["f3"] >= 0, f"f3 should be >= 0, got {result.metadata['f3']}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 4: Post-hoc f2 > 0 when tasks are selected
# ═══════════════════════════════════════════════════════════════════════════

def test_posthoc_f2_not_zero():
    """When tasks are selected and geom_cache available, post-hoc f2 should be > 0."""
    from sar_sim.solver.types import build_agile_instance, precompute_geometry
    
    # Two non-conflicting windows
    dt = _WINDOW_TIME
    w1 = ObservationWindow(
        satellite_id="SAT-1", target_id="T001",
        t_start=dt, t_end=dt + timedelta(seconds=300),
        t_optimal=dt + timedelta(seconds=150),
        elevation=60.0, off_nadir_angle=30.0,
        look_direction="right", duration_min=30.0,
    )
    w2 = ObservationWindow(
        satellite_id="SAT-1", target_id="T002",
        t_start=dt + timedelta(seconds=400),
        t_end=dt + timedelta(seconds=700),
        t_optimal=dt + timedelta(seconds=550),
        elevation=45.0, off_nadir_angle=35.0,
        look_direction="right", duration_min=30.0,
    )
    t1 = GroundTarget(target_id="T001", lat=30.0, lon=100.0, priority=8)
    t2 = GroundTarget(target_id="T002", lat=31.0, lon=101.0, priority=7)

    instance = build_agile_instance([w1, w2], [t1, t2])
    precompute_geometry(instance, step_s=10.0)
    
    result = baseline_b1([w1, w2], [t1, t2], geom_cache=instance.geom_cache, instance=instance)

    # G-BL greedy should select at least 1 task
    assert result.n_scheduled >= 1, "Expected at least 1 scheduled task"
    assert result.f2 > 0, f"f2 should be > 0 when tasks are scheduled, got {result.f2}"
    assert result.metadata["f2"] > 0, (
        f"metadata.f2 should be > 0, got {result.metadata['f2']}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 5: selected_task_indices in metadata
# ═══════════════════════════════════════════════════════════════════════════

def test_selected_indices_in_metadata():
    """G-BL/GA-P/G-SM metadata must contain 'selected_task_indices' list."""
    w1 = ObservationWindow(
        satellite_id="SAT-1", target_id="T001",
        t_start=_WINDOW_TIME,
        t_end=_WINDOW_TIME + timedelta(seconds=300),
        t_optimal=_WINDOW_TIME + timedelta(seconds=150),
        elevation=60.0, off_nadir_angle=30.0,
        look_direction="right", duration_min=30.0,
    )
    w2 = ObservationWindow(
        satellite_id="SAT-1", target_id="T002",
        t_start=_WINDOW_TIME + timedelta(seconds=400),
        t_end=_WINDOW_TIME + timedelta(seconds=700),
        t_optimal=_WINDOW_TIME + timedelta(seconds=550),
        elevation=45.0, off_nadir_angle=35.0,
        look_direction="right", duration_min=30.0,
    )
    t1 = GroundTarget(target_id="T001", lat=30.0, lon=100.0, priority=8)
    t2 = GroundTarget(target_id="T002", lat=31.0, lon=101.0, priority=7)

    for solver_fn, name in [(baseline_b1, "G-BL"), (baseline_b2, "G-SQ"), (baseline_b3, "G-SM")]:
        kwargs = {}
        if name == "G-SQ":
            kwargs["solver"] = "greedy_weighted"
        result = solver_fn([w1, w2], [t1, t2], **kwargs)

        assert "selected_task_indices" in result.metadata, (
            f"{name} metadata should have 'selected_task_indices'"
        )
        indices = result.metadata["selected_task_indices"]
        assert isinstance(indices, list), (
            f"{name} selected_task_indices should be a list, got {type(indices)}"
        )
        assert len(indices) == result.n_scheduled, (
            f"{name} selected_task_indices len={len(indices)} != n_scheduled={result.n_scheduled}"
        )
        # All indices should be target_id strings
        for idx in indices:
            assert isinstance(idx, str), (
                f"{name} each index should be a string (target_id), got {type(idx)}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# Test 6: MOEA-baseline C2 transition time agreement (Option B verification)
# ═══════════════════════════════════════════════════════════════════════════


def test_c2_transition_agreement_moea_vs_baseline():
    """MOEA compute_transition_time() and baseline _c2_transition_los()
    must produce identical results for the same target pair."""
    import math
    from sar_sim.solver.types import (
        build_agile_instance,
        compute_transition_time,
    )
    from sar_sim.solver.baselines import _c2_transition_los

    # Two widely separated targets
    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    targets = [
        GroundTarget("T001", lat=35.0, lon=139.0, priority=1),  # Tokyo
        GroundTarget("T002", lat=48.8, lon=2.3, priority=1),     # Paris
    ]

    windows = [
        _make_window("T001", dt=t0, duration=300),
        _make_window("T002", dt=t0 + timedelta(seconds=600), duration=300),
    ]

    instance = build_agile_instance(windows, targets)
    max_slew = instance.max_slew_rate
    settle = instance.settle_time

    # Extract AgileTask objects
    task_a = instance.tasks[0]
    task_b = instance.tasks[1]

    # Off-nadir angles
    phi_a = math.radians(windows[0].off_nadir_angle)
    phi_b = math.radians(windows[1].off_nadir_angle)

    # MOEA transition time
    tau_moea = compute_transition_time(
        task_a, phi_a, task_b, phi_b, max_slew, settle, instance=instance,
    )

    # Baseline transition time (using t_earliest = observation times)
    t_a_s = task_a.t_earliest
    t_b_s = task_b.t_earliest
    tau_baseline = _c2_transition_los(
        task_a.target_id, t_a_s,
        task_b.target_id, t_b_s,
        instance, max_slew, settle,
    )

    # Must agree to within floating-point tolerance
    assert abs(tau_moea - tau_baseline) < 1e-10, (
        f"MOEA tau={tau_moea:.10f} != baseline tau={tau_baseline:.10f} "
        f"(diff={abs(tau_moea - tau_baseline):.2e})"
    )

    # Both should be non-zero for targets at different locations
    assert tau_moea > settle, f"Expected tau > settle_time={settle}, got {tau_moea}"


def test_c2_legacy_fallback_no_instance():
    """When instance=None, baselines fall back to simple phi-diff (backward compat)."""
    from sar_sim.solver.baselines import _enforce_c2_transitions

    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    w1 = _make_window("T001", dt=t0, duration=300)
    w2 = _make_window("T002", dt=t0 + timedelta(seconds=600), duration=300)

    obs1 = ScheduledObservation(
        window=w1,
        t_actual_start=w1.t_start,
        t_actual_end=w1.t_end,
    )
    obs2 = ScheduledObservation(
        window=w2,
        t_actual_start=w2.t_start,
        t_actual_end=w2.t_end,
    )

    # Should work without instance (legacy phi-diff fallback)
    result = _enforce_c2_transitions([obs1, obs2], instance=None)
    assert len(result) == 2, f"Legacy fallback should keep both, got {len(result)}"
