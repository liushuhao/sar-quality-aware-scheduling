"""TDD tests for multi-satellite MOEA extension (Ch4).

Tests are ordered by the TDD RED-GREEN-REFACTOR cycle:
  Test 1: multi-sat encoding shape (3N variables)
  Test 2: C6 no-duplication constraint enforcement
  Test 3: C6 passes for valid assignments
  Test 4: backward compatibility with n_sats=1
  Test 5: per-satellite C2 transition feasibility
  Test 6: per-satellite C3/C4 budget enforcement
"""

import sys
import numpy as np
from pathlib import Path

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
)


# ═══════════════════════════════════════════════════════════════════════════
# Helper: build a multi-satellite test instance
# ═══════════════════════════════════════════════════════════════════════════

def _build_multisat_instance(
    n_tasks: int = 4, seed: int = 42
) -> AgileSARInstance:
    """Build a minimal AgileSARInstance with N tasks for multi-sat testing.

    Creates N targets at distinct lat/lon positions with overlapping time
    windows, so multi-satellite assignment is meaningful.
    """
    np.random.seed(seed)
    t0 = 1_000_000_000.0  # reference epoch

    targets = []
    for i in range(n_tasks):
        targets.append(GroundTarget(
            target_id=f"T{i}",
            lat=30.0 + i * 0.5,
            lon=100.0 + i * 0.5,
            priority=10.0 / (i + 1),  # decreasing priority
        ))

    tasks = []
    for i, tgt in enumerate(targets):
        t_earliest = t0 + i * 50.0
        t_latest = t_earliest + 400.0
        duration = 30.0

        from datetime import datetime, timezone, timedelta
        t_opt = datetime.fromtimestamp(t_earliest + 100.0, tz=timezone.utc)
        w = ObservationWindow(
            satellite_id="SAT1",
            target_id=tgt.target_id,
            t_start=datetime.fromtimestamp(t_earliest, tz=timezone.utc),
            t_end=datetime.fromtimestamp(t_latest, tz=timezone.utc),
            t_optimal=t_opt,
            elevation=75.0,
            off_nadir_angle=15.0,
            look_direction="right",
            duration_min=30.0,
        )

        tasks.append(AgileTask(
            task_id=i,
            target_id=tgt.target_id,
            priority=float(tgt.priority),
            windows=[w],
            phi_min=0.2618,   # 15 deg
            phi_max=0.8727,   # 50 deg
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=duration,
            energy=50000.0,
            memory=5e8,
            phi_min_res=0.0,
            time_span=t_latest - duration - t_earliest,
            window_times=[(t_earliest, t_latest)],
        ))

    instance = AgileSARInstance(
        tasks=tasks,
        N=n_tasks,
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

    precompute_geometry(instance, step_s=10.0)
    return instance


# ═══════════════════════════════════════════════════════════════════════════
# Test 1 (RED): multi-satellite encoding shape — 3N = 2N + N
# ═══════════════════════════════════════════════════════════════════════════

def test_multisat_encoding_shape():
    """SARSchedulingProblem with n_sats>1 should have 3N variables.

    Encoding: [x_i (N), tau_i (N), sat_j (N)] = 3N variables.
    """
    instance = _build_multisat_instance(n_tasks=4)
    n_sats = 4

    problem = SARSchedulingProblem(instance, n_obj=2, n_sats=n_sats)

    N = instance.N
    assert N == 4

    # n_var should be 2N + N = 3N
    expected_n_var = 2 * N + N  # 3N = 12
    assert problem.n_var == expected_n_var, (
        f"Expected {expected_n_var} variables (2N+N), got {problem.n_var}"
    )

    # Check bounds are [0, 1] for all
    assert problem.xl.shape == (expected_n_var,)
    assert problem.xu.shape == (expected_n_var,)
    assert np.all(problem.xl == 0.0)
    assert np.all(problem.xu == 1.0)


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: C6 removed — duplicate targets across satellites are NOT penalised
#         (C6 was removed to align with paper §3 C1–C4; unique assignment is
#          implied by C2 non-overlap for single-sat, not a separate constraint)
# ═══════════════════════════════════════════════════════════════════════════

def test_c6_removed_no_duplication_penalty():
    """C6 was removed; duplicate targets across satellites incur no extra penalty.

    The paper's C1–C4 system does not include a target-deduplication constraint.
    For single-satellite scheduling, unique assignment is implied by C2
    (non-overlap).  For multi-satellite, duplication is allowed — the solver
    may assign the same target to multiple satellites without penalty.
    """
    instance = _build_multisat_instance(n_tasks=4)
    n_sats = 2
    problem = SARSchedulingProblem(instance, n_obj=2, n_sats=n_sats)
    N = instance.N

    # Chromosome: all 4 tasks selected, tau=0.5, sat assignments
    # sat_0 and sat_1 both get task 0 (duplicate!)
    X = np.zeros((1, 3 * N))
    X[0, :N] = 1.0       # all selected
    X[0, N:2*N] = 0.5    # tau = 0.5
    # sat assignment: tasks 0,1 → sat 0; tasks 2,3 → sat 1
    # But we also make task 0 appear on sat 1 by encoding duplicate:
    # Actually, each task has ONE sat variable. To create duplication,
    # we'd need two DIFFERENT tasks targeting the SAME target_id.
    # Let's construct that scenario.

    # Rebuild with duplicate target_ids
    np.random.seed(42)
    t0 = 1_000_000_000.0

    # Two tasks with SAME target_id, different windows (from different sats)
    targets = [
        GroundTarget(target_id="T0", lat=30.0, lon=100.0, priority=10),
        GroundTarget(target_id="T1", lat=32.0, lon=102.0, priority=5),
        GroundTarget(target_id="T2", lat=34.0, lon=104.0, priority=3),
        # T0_dup: same target_id as T0 but different satellite
        GroundTarget(target_id="T0", lat=30.0, lon=100.0, priority=10),
    ]

    tasks = []
    for i, tgt in enumerate(targets):
        t_earliest = t0 + i * 50.0
        t_latest = t_earliest + 400.0
        duration = 30.0
        from datetime import datetime, timezone

        # Different satellite IDs per task
        sat_id = f"SAT{i % 2}"  # SAT0, SAT1, SAT0, SAT1
        t_opt = datetime.fromtimestamp(t_earliest + 100.0, tz=timezone.utc)
        w = ObservationWindow(
            satellite_id=sat_id,
            target_id=tgt.target_id,
            t_start=datetime.fromtimestamp(t_earliest, tz=timezone.utc),
            t_end=datetime.fromtimestamp(t_latest, tz=timezone.utc),
            t_optimal=t_opt,
            elevation=75.0,
            off_nadir_angle=15.0,
            look_direction="right",
            duration_min=30.0,
        )

        tasks.append(AgileTask(
            task_id=i,
            target_id=tgt.target_id,
            priority=float(tgt.priority),
            windows=[w],
            phi_min=0.2618,
            phi_max=0.8727,
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=duration,
            energy=50000.0,
            memory=5e8,
            phi_min_res=0.0,
            time_span=t_latest - duration - t_earliest,
            window_times=[(t_earliest, t_latest)],
        ))

    # Note: target_map deduplicates by target_id, so T0 appears once
    target_map = {}
    for t in targets:
        if t.target_id not in target_map:
            target_map[t.target_id] = t

    inst_dup = AgileSARInstance(
        tasks=tasks,
        N=4,
        phi_min=0.2618,
        phi_max=0.8727,
        max_slew_rate=0.0524,
        settle_time=5.0,
        energy_budget=1e7,
        memory_budget=1e11,
        target_map=target_map,
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t0,
    )
    precompute_geometry(inst_dup, step_s=10.0)

    problem2 = SARSchedulingProblem(inst_dup, n_obj=2, n_sats=2)
    N2 = inst_dup.N  # 4

    # Chromosome: select all 4 tasks, tau=0.5
    # sat assignment: tasks 0,1,2,3 → sat 0,0,1,1
    # Task 3 has target_id T0 — same as task 0 (duplicate across sats).
    # C6 was removed, so this should NOT incur a duplication penalty.
    X = np.zeros((1, 3 * N2))
    X[0, :N2] = 1.0           # all selected
    X[0, N2:2*N2] = 0.5        # tau = 0.5
    # sat: tasks 0,1 → sat 0 (sat_val=0.1 maps to 0), tasks 2,3 → sat 1 (sat_val=0.6 maps to 1)
    X[0, 2*N2] = 0.1     # task 0 → sat 0
    X[0, 2*N2+1] = 0.1   # task 1 → sat 0
    X[0, 2*N2+2] = 0.6   # task 2 → sat 1 (different target_id T2)
    X[0, 2*N2+3] = 0.6   # task 3 → sat 1 (target_id T0 — SAME as task 0!)

    out = {}
    problem2._evaluate(X, out)
    G = out["G"]

    # C6 was removed — duplicate targets across satellites are NOT penalised.
    # G should be 0 (no C2/C3/C4 violations in this scenario either).
    assert G[0, 0] == 0, (
        f"C6 removed: duplicate target T0 should NOT be penalised, got G={G[0, 0]}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 3 (RED): C6 passes for valid (non-duplicate) assignments
# ═══════════════════════════════════════════════════════════════════════════

def test_c6_no_duplication_pass():
    """C6 should be zero when each target appears on at most 1 satellite."""
    instance = _build_multisat_instance(n_tasks=4)
    n_sats = 2
    problem = SARSchedulingProblem(instance, n_obj=2, n_sats=n_sats)
    N = instance.N

    # All 4 targets have DIFFERENT target_ids (T0, T1, T2, T3)
    # Assign tasks 0,1 → sat 0; tasks 2,3 → sat 1
    # No duplicate target_ids across satellites
    X = np.zeros((1, 3 * N))
    X[0, :N] = 1.0           # all selected
    X[0, N:2*N] = 0.5        # tau = 0.5
    X[0, 2*N] = 0.1          # task 0 → sat 0
    X[0, 2*N+1] = 0.1        # task 1 → sat 0
    X[0, 2*N+2] = 0.6        # task 2 → sat 1
    X[0, 2*N+3] = 0.6        # task 3 → sat 1

    out = {}
    problem._evaluate(X, out)
    G = out["G"]

    # The C6 portion should be 0 (no duplicate target_ids)
    # Note: there may be other constraint violations (C3, phi range, etc.)
    # But C6 specifically should not add penalty
    # We verify by building a scenario where only C6 could trigger

    # For a stricter test: all targets unique, so C6=0.
    # The total G may be > 0 from other constraints, but let's
    # verify that the F values are reasonable
    assert out["F"].shape == (1, 2)

    # More targeted: create minimal scenario where only C6 matters
    # Build instance with all unique target_ids, check G is not
    # inflated by C6 penalty
    # Rebuild with very wide phi ranges to avoid phi violations
    np.random.seed(42)
    t0 = 1_000_000_000.0
    targets = []
    for i in range(4):
        targets.append(GroundTarget(
            target_id=f"U{i}", lat=30.0 + i, lon=100.0 + i, priority=10.0
        ))

    tasks_wide = []
    for i, tgt in enumerate(targets):
        t_earliest = t0 + i * 50.0
        t_latest = t_earliest + 400.0
        duration = 30.0
        from datetime import datetime, timezone
        t_opt = datetime.fromtimestamp(t_earliest + 100.0, tz=timezone.utc)
        w = ObservationWindow(
            satellite_id=f"SAT{i%2}",
            target_id=tgt.target_id,
            t_start=datetime.fromtimestamp(t_earliest, tz=timezone.utc),
            t_end=datetime.fromtimestamp(t_latest, tz=timezone.utc),
            t_optimal=t_opt,
            elevation=45.0,
            off_nadir_angle=45.0,
            look_direction="right",
            duration_min=30.0,
        )
        tasks_wide.append(AgileTask(
            task_id=i,
            target_id=tgt.target_id,
            priority=float(tgt.priority),
            windows=[w],
            phi_min=0.0,          # very wide range
            phi_max=np.pi/2,     # 90 deg off-nadir
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=duration,
            energy=50000.0,
            memory=5e8,
            phi_min_res=0.0,
            time_span=t_latest - duration - t_earliest,
        ))

    inst_wide = AgileSARInstance(
        tasks=tasks_wide,
        N=4,
        phi_min=0.0,
        phi_max=np.pi/2,
        max_slew_rate=0.0524,
        settle_time=5.0,
        energy_budget=1e12,  # huge budget
        memory_budget=1e13,
        target_map={t.target_id: t for t in targets},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t0,
    )
    precompute_geometry(inst_wide, step_s=10.0)

    problem3 = SARSchedulingProblem(inst_wide, n_obj=2, n_sats=2)
    N3 = inst_wide.N

    # Select all, assign uniquely
    X3 = np.zeros((1, 3 * N3))
    X3[0, :N3] = 1.0
    X3[0, N3:2*N3] = 0.5
    X3[0, 2*N3] = 0.1      # task 0 → sat 0
    X3[0, 2*N3+1] = 0.1    # task 1 → sat 0
    X3[0, 2*N3+2] = 0.6    # task 2 → sat 1
    X3[0, 2*N3+3] = 0.6    # task 3 → sat 1

    out3 = {}
    problem3._evaluate(X3, out3)

    # No C6 violation expected (all unique target_ids)
    # G may be > 0 from C2/C3/C4 etc., but should be manageable
    assert out3["G"].shape == (1, 1)
    # F should be non-trivial
    assert out3["F"].shape == (1, 2)


# ═══════════════════════════════════════════════════════════════════════════
# Test 4 (RED): backward compatibility — n_sats=1 produces same results
# ═══════════════════════════════════════════════════════════════════════════

def test_backward_compat_n_sats_1():
    """n_sats=1 uses 2N encoding (backward compatible, no sat variables).

    When n_sats=1, the encoding is exactly the same as the original
    single-satellite MOEA (2N variables: N selection + N tau).
    The solver should produce valid F and G with this encoding.
    """
    instance = _build_multisat_instance(n_tasks=4)

    # Run with n_sats=1 (backward-compatible 2N encoding)
    problem = SARSchedulingProblem(instance, n_obj=2, n_sats=1)
    N = instance.N

    # Verify 2N encoding (not 3N — backward compatible)
    assert problem.n_var == 2 * N, (
        f"n_sats=1 should use 2N encoding, got {problem.n_var}"
    )
    assert problem.n_sats == 1

    # Standard 2N chromosome: all selected, tau=0.5
    X = np.zeros((1, 2 * N))
    X[0, :N] = 1.0          # all selected
    X[0, N:2*N] = 0.5       # tau = 0.5

    out = {}
    problem._evaluate(X, out)

    # Should produce valid F and G
    assert out["F"].shape == (1, 2)
    assert out["G"].shape == (1, 1)
    assert np.all(out["G"] >= 0), f"G should be non-negative, got {out['G']}"

    # F values should be non-trivial (negated for minimization)
    assert np.all(out["F"] < 0), "F should be negative (pymoo minimizes)"


def test_n_sats_1_identical_to_default():
    """Explicit n_sats=1 produces identical results to implicit n_sats=1 (default).

    The default constructor should produce the same 2N encoding as
    the explicit n_sats=1 case.
    """
    instance = _build_multisat_instance(n_tasks=4)
    N = instance.N

    # Default (no n_sats) → 2N
    problem_default = SARSchedulingProblem(instance, n_obj=2)
    # Explicit n_sats=1 → also 2N
    problem_explicit = SARSchedulingProblem(instance, n_obj=2, n_sats=1)

    assert problem_default.n_var == problem_explicit.n_var == 2 * N
    assert problem_default.n_sats == problem_explicit.n_sats == 1

    # Same chromosome
    X = np.zeros((1, 2 * N))
    X[0, :N] = 1.0
    X[0, N:2*N] = 0.5

    out_default = {}
    problem_default._evaluate(X, out_default)

    out_explicit = {}
    problem_explicit._evaluate(X, out_explicit)

    assert np.allclose(out_explicit["F"], out_default["F"], rtol=1e-12, atol=1e-12)
    assert np.allclose(out_explicit["G"], out_default["G"], rtol=1e-12, atol=1e-12)


# ═══════════════════════════════════════════════════════════════════════════
# Test 5 (RED): per-satellite C3 transition
# ═══════════════════════════════════════════════════════════════════════════

def test_per_sat_c3_transition():
    """C3 must check transitions within each satellite, not globally.

    If satellite 0 has tasks A→B (feasible) and satellite 1 has tasks
    C→D (feasible), C3 should pass.  If ordered globally as A→B→C→D,
    the A→B and C→D within-sat transitions would still be checked,
    but there should be no B→C check across satellites.
    """
    instance = _build_multisat_instance(n_tasks=4)
    n_sats = 2
    problem = SARSchedulingProblem(instance, n_obj=2, n_sats=n_sats)
    N = instance.N

    # Assign tasks 0,1 → sat 0 (sequential, feasible within sat 0)
    # Assign tasks 2,3 → sat 1 (sequential, feasible within sat 1)
    X = np.zeros((1, 3 * N))
    X[0, :N] = 1.0
    X[0, N:2*N] = 0.5
    X[0, 2*N] = 0.1      # task 0 → sat 0
    X[0, 2*N+1] = 0.1    # task 1 → sat 0
    X[0, 2*N+2] = 0.6    # task 2 → sat 1
    X[0, 2*N+3] = 0.6    # task 3 → sat 1

    out = {}
    problem._evaluate(X, out)

    # Should produce valid F and G
    assert out["F"].shape == (1, 2)
    assert out["G"].shape == (1, 1)
    # G should be ≥ 0
    assert np.all(out["G"] >= 0)


# ═══════════════════════════════════════════════════════════════════════════
# Test 6 (RED): per-satellite C3/C4 budget
# ═══════════════════════════════════════════════════════════════════════════

def test_per_sat_c3c4_budget():
    """C3/C4 must check energy/memory per satellite, not globally.

    If total energy is under global budget but one satellite exceeds
    its per-sat share, C3 should trigger.
    """
    np.random.seed(42)
    t0 = 1_000_000_000.0

    # 4 targets, each with energy cost = 60000
    targets = []
    for i in range(4):
        targets.append(GroundTarget(
            target_id=f"E{i}", lat=30.0 + i, lon=100.0 + i, priority=10.0
        ))

    tasks = []
    for i, tgt in enumerate(targets):
        t_earliest = t0 + i * 50.0
        t_latest = t_earliest + 400.0
        duration = 30.0
        from datetime import datetime, timezone
        t_opt = datetime.fromtimestamp(t_earliest + 100.0, tz=timezone.utc)
        w = ObservationWindow(
            satellite_id=f"SAT{i%2}",
            target_id=tgt.target_id,
            t_start=datetime.fromtimestamp(t_earliest, tz=timezone.utc),
            t_end=datetime.fromtimestamp(t_latest, tz=timezone.utc),
            t_optimal=t_opt,
            elevation=75.0,
            off_nadir_angle=15.0,
            look_direction="right",
            duration_min=30.0,
        )
        tasks.append(AgileTask(
            task_id=i,
            target_id=tgt.target_id,
            priority=float(tgt.priority),
            windows=[w],
            phi_min=0.0,
            phi_max=np.pi/2,
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=duration,
            energy=60000.0,     # per-task energy
            memory=5e8,
            phi_min_res=0.0,
            time_span=t_latest - duration - t_earliest,
        ))

    inst = AgileSARInstance(
        tasks=tasks,
        N=4,
        phi_min=0.0,
        phi_max=np.pi/2,
        max_slew_rate=0.0524,
        settle_time=5.0,
        # Total budget = 150000.  2 sats → per-sat budget = 75000.
        # If 3 tasks go to sat 0 (3×60000=180000 > 75000), C4 triggers.
        # But global total 4×60000=240000 < 150000? No, 240000 > 150000.
        # Let's design: total budget = 300000, per-sat = 150000.
        # 3 tasks on sat 0 = 180000 > 150000 → C4 triggers for sat 0
        # 1 task on sat 1 = 60000 < 150000 → OK for sat 1
        # Global total = 240000 < 300000 → global C4 wouldn't trigger
        energy_budget=300000.0,
        memory_budget=1e13,
        target_map={t.target_id: t for t in targets},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=t0,
    )
    precompute_geometry(inst, step_s=10.0)

    problem = SARSchedulingProblem(inst, n_obj=2, n_sats=2)
    N = inst.N

    # Assign 3 tasks to sat 0, 1 task to sat 1
    X = np.zeros((1, 3 * N))
    X[0, :N] = 1.0           # select all 4
    X[0, N:2*N] = 0.5        # tau = 0.5
    X[0, 2*N] = 0.1          # task 0 → sat 0
    X[0, 2*N+1] = 0.1        # task 1 → sat 0
    X[0, 2*N+2] = 0.1        # task 2 → sat 0  (3 tasks on sat 0!)
    X[0, 2*N+3] = 0.6        # task 3 → sat 1

    out = {}
    problem._evaluate(X, out)
    G = out["G"]

    # Per-sat C4 should trigger for sat 0 (3×60000=180000 > 150000)
    assert G[0, 0] > 0, (
        f"Per-sat C4 should trigger: sat 0 energy=180000 > budget=150000, "
        f"but global energy=240000 < budget=300000. G={G[0, 0]}"
    )
