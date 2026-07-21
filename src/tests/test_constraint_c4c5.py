"""TDD tests for C4/C5 constraint enforcement in baselines (Step 3).

Tests follow strict RED-GREEN-REFACTOR cycle.
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sar_sim.types import GroundTarget, ObservationWindow
from sar_sim.solver.types import (
    AgileSARInstance,
    AgileTask,
    precompute_geometry,
)
from sar_sim.solver.baselines import baseline_b1, baseline_b2, baseline_b3


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

_WINDOW_TIME = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _make_window(target_id, offset_min=0, elevation=45.0):
    """Create a minimal ObservationWindow with a time offset."""
    start = _WINDOW_TIME + timedelta(minutes=offset_min)
    return ObservationWindow(
        satellite_id="SAT-1",
        target_id=target_id,
        t_start=start,
        t_end=start + timedelta(seconds=300),
        t_optimal=start + timedelta(seconds=150),
        elevation=elevation,
        off_nadir_angle=30.0,
        look_direction="right",
        duration_min=30.0,
    )


def _make_targets_and_windows(n_tasks=5):
    """Create non-overlapping windows and targets for testing C4/C5."""
    windows = []
    targets = []
    for i in range(n_tasks):
        tid = f"T{i:03d}"
        windows.append(_make_window(tid, offset_min=i * 10))
        targets.append(GroundTarget(
            target_id=tid,
            lat=30.0 + i * 0.5,
            lon=100.0 + i * 0.5,
            priority=10 - i,  # descending priority
        ))
    return windows, targets


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: G-BL energy budget enforced — over-budget drops low-priority tasks
# ═══════════════════════════════════════════════════════════════════════════

def test_b1_energy_budget_enforced():
    """When energy_budget is tight, G-BL drops lowest-priority tasks first."""
    windows, targets = _make_targets_and_windows(n_tasks=5)
    # With 5 tasks, each at 50k energy → total 250k
    # Budget = 120k → only 2 tasks can fit (T000 priority=10, T001 priority=9)
    # T004 would be dropped first (lowest priority=6)

    result = baseline_b1(
        windows, targets,
        energy_budget=120_000.0,
        energy_per_obs=50_000.0,
    )

    assert result.n_scheduled <= 3, (
        f"With budget 120k, at most 2-3 tasks should fit (energy=50k each). "
        f"Got {result.n_scheduled}"
    )
    # Energy should be within budget
    assert result.n_scheduled * 50_000.0 <= 120_000.0, (
        f"Energy used ({result.n_scheduled * 50_000}) exceeds budget (120_000)"
    )
    # Higher priority tasks should be selected before lower priority ones
    selected_ids = result.metadata["selected_task_indices"]
    for tid in selected_ids:
        assert tid in {"T000", "T001", "T002"}, (
            f"Low priority task {tid} selected before high priority ones. "
            f"Selected: {selected_ids}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: G-BL memory budget enforced
# ═══════════════════════════════════════════════════════════════════════════

def test_b1_memory_budget_enforced():
    """When memory_budget is tight, G-BL drops lowest-priority tasks first."""
    windows, targets = _make_targets_and_windows(n_tasks=5)
    # Memory per obs = 5e8, budget = 12e8 → at most 2 tasks fit

    result = baseline_b1(
        windows, targets,
        memory_budget=12e8,
        memory_per_obs=5e8,
    )

    assert result.n_scheduled <= 3, (
        f"With memory budget 12e8, at most 2-3 tasks should fit. "
        f"Got {result.n_scheduled}"
    )
    assert result.n_scheduled * 5e8 <= 12e8, (
        f"Memory used ({result.n_scheduled * 5e8}) exceeds budget (12e8)"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: G-SM energy budget enforced (with geom_cache)
# ═══════════════════════════════════════════════════════════════════════════

def test_b3_energy_budget_enforced():
    """G-SM energy budget enforcement works with squint minimization."""
    windows, targets = _make_targets_and_windows(n_tasks=4)

    # Build instance with GeomCache for G-SM squint minimization
    t_ref = _WINDOW_TIME.timestamp()
    instance_tasks = []
    max_t = 0.0
    for t_i, tg in enumerate(targets):
        t_earliest = t_ref + t_i * 600  # 10 min apart
        max_t = max(max_t, t_earliest + 300)
        instance_tasks.append(AgileTask(
            task_id=t_i, target_id=tg.target_id, priority=float(tg.priority),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=t_earliest, t_latest=t_earliest + 300,
            duration=30.0, energy=50_000.0, memory=5e8,
            phi_min_res=0.0,
        ))
    instance = AgileSARInstance(
        tasks=instance_tasks, N=len(instance_tasks),
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={tg.target_id: tg for tg in targets},
        altitude_m=600_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t_ref,
    )
    precompute_geometry(instance, step_s=10.0)

    result = baseline_b3(
        windows, targets,
        instance=instance,
        geom_cache=instance.geom_cache,
        energy_budget=80_000.0,  # Only 1 task at 50k
        energy_per_obs=50_000.0,
    )

    assert result.n_scheduled <= 2, (
        f"With energy budget 80k, at most 1-2 tasks should fit. "
        f"Got {result.n_scheduled}"
    )
    assert result.n_scheduled * 50_000.0 <= 80_000.0, (
        f"Energy used exceeds budget"
    )
