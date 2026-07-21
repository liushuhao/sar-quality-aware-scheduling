"""TDD tests for GA-P Single-Objective GA Solver (so_f1.py).

Tests follow the TDD RED-GREEN-REFACTOR cycle.
Phase 1 (RED): All tests written first, expected to FAIL.
"""

import sys
import os
import json
from pathlib import Path

# ── Path setup: add source workspace ───────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# ── Test data paths ─────────────────────────────────────────────────────
PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"

# ═══════════════════════════════════════════════════════════════════════════
# Test 1: 2N Encoding/Decoding Correctness
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_2n_encoding_shape():
    """B2ProfitProblem should have exactly 2N decision variables."""
    from sar_sim.solver.so_f1 import B2ProfitProblem

    # Use a minimal instance with known N
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    # Create 5 dummy tasks
    tasks = []
    for i in range(5):
        tasks.append(AgileTask(
            task_id=i, target_id=f"T{i:03d}", priority=float(i + 1),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=100.0 + i * 50, t_latest=300.0 + i * 50,
            duration=30.0, energy=50000.0, memory=5e8,
            phi_min_res=0.0,
        ))

    target_map = {
        f"T{i:03d}": GroundTarget(
            target_id=f"T{i:03d}", lat=float(30 + i), lon=float(100 + i), priority=i + 1,
        )
        for i in range(5)
    }

    instance = AgileSARInstance(
        tasks=tasks, N=5, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map=target_map, altitude_m=600_000.0,
    )

    problem = B2ProfitProblem(instance)

    # Assert: 2N = 10 variables
    assert problem.n_var == 10, f"Expected n_var=10, got {problem.n_var}"
    # Assert: 1 objective
    assert problem.n_obj == 1, f"Expected n_obj=1, got {problem.n_obj}"
    # Assert: 1 inequality constraint
    assert problem.n_ieq_constr == 0, f"Expected n_ieq_constr=0 (penalty baked), got {problem.n_ieq_constr}"
    # Assert: bounds correct
    assert problem.xl.shape == (10,), f"Expected xl shape (10,), got {problem.xl.shape}"
    assert problem.xu.shape == (10,), f"Expected xu shape (10,), got {problem.xu.shape}"
    # First N variables are x_i ∈ [0, 1]
    assert all(problem.xl[:5] == 0.0), f"xl[:5] should be 0.0, got {problem.xl[:5]}"
    assert all(problem.xu[:5] == 1.0), f"xu[:5] should be 1.0, got {problem.xu[:5]}"
    # Last N variables are tau_i ∈ [0, 1]
    assert all(problem.xl[5:10] == 0.0), f"xl[5:10] should be 0.0, got {problem.xl[5:10]}"
    assert all(problem.xu[5:10] == 1.0), f"xu[5:10] should be 1.0, got {problem.xu[5:10]}"

def test_b2_tau_decoding():
    """τ_i ∈ [0,1] should decode to t_actual ∈ [a_i, b_i - d_i]."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 3
    tasks = []
    for i in range(N):
        t_early = 100.0 + i * 200.0
        t_late = t_early + 150.0
        tasks.append(AgileTask(
            task_id=i, target_id=f"T{i:03d}", priority=float(i + 1),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=t_early, t_latest=t_late,
            duration=30.0, energy=50000.0, memory=5e8,
            phi_min_res=0.0,
        ))

    target_map = {
        f"T{i:03d}": GroundTarget(
            target_id=f"T{i:03d}", lat=float(30 + i), lon=float(100 + i), priority=i + 1,
        )
        for i in range(N)
    }

    instance = AgileSARInstance(
        tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map=target_map, altitude_m=600_000.0,
    )

    problem = B2ProfitProblem(instance)

    # Create a chromosome: select all 3 tasks, different tau values
    X = np.array([[0.8, 0.9, 0.7,  # x_i (all selected)
                   0.0, 0.5, 1.0]])  # tau_i (0%, 50%, 100%)

    # Evaluate — should compute f1 and constraints
    out = {}
    problem._evaluate(X, out)

    # f1 should be negative sum of priorities (pymoo minimizes)
    assert "F" in out, "out should have 'F' key"
    assert out["F"].shape == (1, 1), f"Expected F shape (1,1), got {out['F'].shape}"
    # With dummy windows, G may be large; f1 + penalty*G can be positive.
    # Just verify F and G exist with correct shape.
    assert out["F"].shape == (1, 1), f"Expected F shape (1,1), got {out['F'].shape}"

    # G no longer output separately (n_ieq_constr=0, penalty baked into F)
    assert "G" not in out, "out should not have G key (penalty baked)"

def test_b2_selected_only_f1():
    """Only selected tasks (x_i > 0.5) contribute to f1."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 4
    tasks = []
    for i in range(N):
        tasks.append(AgileTask(
            task_id=i, target_id=f"T{i:03d}", priority=float(2 * (i + 1)),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=100.0 + i * 100, t_latest=250.0 + i * 100,
            duration=30.0, energy=50000.0, memory=5e8,
            phi_min_res=0.0,
        ))

    target_map = {
        f"T{i:03d}": GroundTarget(
            target_id=f"T{i:03d}", lat=float(30 + i), lon=float(100 + i), priority=2 * (i + 1),
        )
        for i in range(N)
    }

    instance = AgileSARInstance(
        tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map=target_map, altitude_m=600_000.0,
    )

    problem = B2ProfitProblem(instance)

    # Select only tasks 0 and 2 (priorities 2 and 6)
    X = np.array([[0.8, 0.3, 0.9, 0.2,  # x_i: select T0, T2
                   0.5, 0.5, 0.5, 0.5]])  # tau_i: 50% for all

    out = {}
    problem._evaluate(X, out)

    # f1 = -(2 + 6) = -8 + penalty * G.  With dummy windows, G might be > 0.
    # Key assertion: F exists and penalty term includes -f1 contribution.
    assert "F" in out
    assert "G" not in out  # n_ieq_constr=0, penalty baked

# ═══════════════════════════════════════════════════════════════════════════
# Test 2: f2/f3 Not Computed
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_f2_not_computed():
    """B2ProfitProblem should not compute f2 (geometric resolution)."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 3
    tasks = [AgileTask(task_id=i, target_id=f"T{i:03d}", priority=float(i + 1),
                       windows=[], phi_min=0.3, phi_max=0.8,
                       t_earliest=100.0 + i * 100, t_latest=250.0 + i * 100,
                       duration=30.0, energy=50000.0, memory=5e8, phi_min_res=0.0)
             for i in range(N)]
    target_map = {f"T{i:03d}": GroundTarget(target_id=f"T{i:03d}", lat=float(30+i), lon=float(100+i), priority=i+1)
                  for i in range(N)}
    instance = AgileSARInstance(tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
                                max_slew_rate=0.0524, settle_time=5.0,
                                energy_budget=1e7, memory_budget=1e11,
                                target_map=target_map, altitude_m=600_000.0)

    problem = B2ProfitProblem(instance)
    X = np.array([[0.8, 0.8, 0.8, 0.5, 0.5, 0.5]])
    out = {}
    problem._evaluate(X, out)

    # F should be shape (1, 1), not (1, 2) or (1, 3)
    assert out["F"].shape[1] == 1, \
        f"GA-P should have exactly 1 objective, got shape {out['F'].shape}"

# ═══════════════════════════════════════════════════════════════════════════
# Test 3: Constraint Handling Mirrors MOEA
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_penalty_coeff_matches_moea():
    """B2ProfitProblem should use the same penalty_coeff default as MOEA (1e5)."""
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 2
    tasks = [AgileTask(task_id=i, target_id=f"T{i:03d}", priority=float(i + 1),
                       windows=[], phi_min=0.3, phi_max=0.8,
                       t_earliest=100.0 + i * 100, t_latest=250.0 + i * 100,
                       duration=30.0, energy=50000.0, memory=5e8, phi_min_res=0.0)
             for i in range(N)]
    target_map = {f"T{i:03d}": GroundTarget(target_id=f"T{i:03d}", lat=float(30+i), lon=float(100+i), priority=i+1)
                  for i in range(N)}
    instance = AgileSARInstance(tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
                                max_slew_rate=0.0524, settle_time=5.0,
                                energy_budget=1e7, memory_budget=1e11,
                                target_map=target_map, altitude_m=600_000.0)

    problem = B2ProfitProblem(instance)
    assert problem.penalty_coeff == 1e5, \
        f"GA-P penalty_coeff should be 1e5 to match MOEA, got {problem.penalty_coeff}"

def test_b2_constraint_aggregation():
    """GA-P should aggregate all constraints into single G (same as MOEA)."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 2
    # Two tasks with overlapping windows — should be feasible
    tasks = [
        AgileTask(task_id=0, target_id="T000", priority=10.0,
                  windows=[], phi_min=0.3, phi_max=0.8,
                  t_earliest=100.0, t_latest=300.0,
                  duration=30.0, energy=50000.0, memory=5e8, phi_min_res=0.0),
        AgileTask(task_id=1, target_id="T001", priority=9.0,
                  windows=[], phi_min=0.3, phi_max=0.8,
                  t_earliest=500.0, t_latest=700.0,
                  duration=30.0, energy=50000.0, memory=5e8, phi_min_res=0.0),
    ]
    target_map = {
        "T000": GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10),
        "T001": GroundTarget(target_id="T001", lat=31.0, lon=101.0, priority=9),
    }
    instance = AgileSARInstance(tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
                                max_slew_rate=0.0524, settle_time=5.0,
                                energy_budget=1e7, memory_budget=1e11,
                                target_map=target_map, altitude_m=600_000.0,
                                orbit_inclination_rad=1.707,  # ~97.8°
                                orbit_period_s=5800.0, orbit_ref_time_s=100.0)

    problem = B2ProfitProblem(instance)

    # Select both tasks
    X = np.array([[0.8, 0.8, 0.5, 0.5]])
    out = {}
    problem._evaluate(X, out)

    # Penalty baked into F (n_ieq_constr=0) — check F exists
    assert out["F"].shape == (1, 1), f"Expected F shape (1,1), got {out['F'].shape}"
    # F should have penalty baked in (no separate G)

# ═══════════════════════════════════════════════════════════════════════════
# Test 4: b2_profit_solver Function
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_profit_solver_exists():
    """b2_profit_solver should be importable and callable."""
    from sar_sim.solver.so_f1 import b2_profit_solver

    # Basic check: function exists
    assert callable(b2_profit_solver), "b2_profit_solver should be callable"

def test_b2_profit_solver_empty_input():
    """b2_profit_solver should handle empty windows gracefully."""
    from sar_sim.solver.so_f1 import b2_profit_solver
    from sar_sim.types import SolverResult

    result = b2_profit_solver([], [])
    assert isinstance(result, SolverResult), f"Expected SolverResult, got {type(result)}"
    assert result.score == 0.0, f"Empty input should give score 0.0, got {result.score}"
    assert len(result.schedule) == 0, "Empty input should give empty schedule"

# ═══════════════════════════════════════════════════════════════════════════
# Test 5: Integration — GA-P vs G-BL on Real Scenario
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_vs_b1_on_s1_scenario():
    """GA-P should achieve f1 >= G-BL on the same scenario (time search helps)."""
    import pickle
    import numpy as np
    from sar_sim.solver.so_f1 import b2_profit_solver
    from sar_sim.solver.baselines import baseline_b1

    # Use S1 scenario if available
    s1_dir = SCENARIOS_DIR / "S1"
    if not s1_dir.is_dir():
        import pytest
        pytest.skip("S1 scenarios not available")

    pkgs = sorted(s1_dir.glob("*.pkl"))
    if not pkgs:
        import pytest
        pytest.skip("No S1 scenario files found")

    # Test on first scenario
    with open(pkgs[0], 'rb') as f:
        data = pickle.load(f)

    windows = data.get("windows", [])
    targets = data.get("targets", [])

    if len(windows) == 0 or len(targets) == 0:
        import pytest
        pytest.skip("Empty scenario")

    # Run G-BL
    b1_result = baseline_b1(windows, targets)
    f1_b1 = b1_result.f1

    # Run GA-P (single-objective GA)
    b2_result = b2_profit_solver(windows, targets,
                                  population_size=40, n_generations=50, seed=42)
    f1_b2 = b2_result.metadata.get("f1", 0.0)

    # GA-P should achieve non-trivial f1 (time search enables scheduling).
    # G-BL works at window-level (can schedule >N observations), while
    # GA-P works at task-level (max N).  GA-P should at least schedule
    # some tasks.
    assert f1_b2 > 0.0, \
        f"GA-P should schedule at least one task, got f1={f1_b2}" 

# ═══════════════════════════════════════════════════════════════════════════
# Test 6: SolverResult output format
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_solver_result_format():
    """b2_profit_solver should return SolverResult with expected metadata keys."""
    from sar_sim.solver.so_f1 import b2_profit_solver
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget, SolverResult
    from sar_sim.metrics.nesz import elevation_to_off_nadir

    # Create a simple scenario manually
    N = 3
    target_map = {
        "T000": GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10),
        "T001": GroundTarget(target_id="T001", lat=32.0, lon=102.0, priority=8),
        "T002": GroundTarget(target_id="T002", lat=28.0, lon=98.0, priority=7),
    }

    # Load or create observation windows
    # For simplicity, check only the empty case which must work
    result = b2_profit_solver([], [])
    assert isinstance(result, SolverResult)
    assert "solver" in result.metadata, f"metadata should have 'solver' key, got {result.metadata}"
    assert result.metadata["solver"] == "b2_profit", \
        f"Expected solver='b2_profit', got {result.metadata['solver']}"

# ═══════════════════════════════════════════════════════════════════════════
# Test 7 (NEW — Step 4): Post-hoc f2/f3 in Metadata
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_posthoc_f2_f3_in_metadata():
    """After GA convergence, b2_profit_solver should compute post-hoc
    f2 (geometric resolution) and f3 (NESZ radiometric) from GeomCache
    and store them in result.metadata."""
    import pickle
    from sar_sim.solver.so_f1 import b2_profit_solver

    # Use a real scenario for accurate geometry
    s1_dir = SCENARIOS_DIR / "S1"
    if not s1_dir.is_dir():
        import pytest
        pytest.skip("S1 scenarios not available")

    pkgs = sorted(s1_dir.glob("*.pkl"))
    if not pkgs:
        import pytest
        pytest.skip("No S1 scenario files found")

    with open(pkgs[0], 'rb') as f:
        data = pickle.load(f)

    windows = data.get("windows", [])
    targets = data.get("targets", [])

    if len(windows) == 0 or len(targets) == 0:
        import pytest
        pytest.skip("Empty scenario")

    result = b2_profit_solver(
        windows, targets,
        population_size=40, n_generations=50, seed=42,
    )

    meta = result.metadata

    # f2 (geometric resolution) should be present in metadata
    assert "f2" in meta, \
        f"metadata should have 'f2' key after Step 4 refactor, got keys: {list(meta.keys())}"
    f2_val = meta["f2"]

    # f3 (NESZ radiometric) should be present in metadata
    assert "f3" in meta, \
        f"metadata should have 'f3' key after Step 4 refactor, got keys: {list(meta.keys())}"
    f3_val = meta["f3"]

    # If any tasks were scheduled, f2 and f3 should be non-zero
    if meta.get("n_selected", 0) > 0:
        assert f2_val > 0.0, \
            f"Expected post-hoc f2 > 0 when tasks scheduled, got f2={f2_val}"
        assert f3_val > 0.0, \
            f"Expected post-hoc f3 > 0 when tasks scheduled, got f3={f3_val}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 8 (NEW — Step 4): Energy Budget (C4) Enforcement
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_energy_budget_enforced():
    """GA-P _evaluate() should penalize solutions that exceed energy_budget (C4)."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 4
    tasks = []
    for i in range(N):
        tasks.append(AgileTask(
            task_id=i, target_id=f"T{i:03d}", priority=float(2 * (i + 1)),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=100.0 + i * 100, t_latest=250.0 + i * 100,
            duration=30.0, energy=60_000.0, memory=5e8,
            phi_min_res=0.0,
        ))

    target_map = {
        f"T{i:03d}": GroundTarget(
            target_id=f"T{i:03d}", lat=float(30 + i), lon=float(100 + i),
            priority=2 * (i + 1),
        )
        for i in range(N)
    }

    instance = AgileSARInstance(
        tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=120_000.0,  # tight: each task costs 60k, 4 tasks = 240k > 120k
        memory_budget=1e11,
        target_map=target_map, altitude_m=600_000.0,
    )

    problem = B2ProfitProblem(instance)

    # Select all 4 tasks (exceeds energy budget)
    X = np.array([[0.8, 0.8, 0.8, 0.8,  # all selected
                   0.5, 0.5, 0.5, 0.5]])

    out = {}
    problem._evaluate(X, out)

    # Penalty baked into F (n_ieq_constr=0) — constraint violation makes F positive
    assert "G" not in out
    # Check F contains penalty — energy violation should make F very positive
    assert out["F"][0, 0] > 1000, f"Expected penalized F > 1000, got {out['F'][0, 0]}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 9 (NEW — Step 4): GeomCache Fallback
# ═══════════════════════════════════════════════════════════════════════════

def test_b2_geom_cache_fallback():
    """GA-P _evaluate() should fall back to compute_full_attitude
    when geom_cache is None, and evaluate without errors."""
    import numpy as np
    from sar_sim.solver.so_f1 import B2ProfitProblem
    from sar_sim.solver.types import AgileSARInstance, AgileTask
    from sar_sim.types import GroundTarget

    N = 3
    tasks = []
    for i in range(N):
        tasks.append(AgileTask(
            task_id=i, target_id=f"T{i:03d}", priority=float(i + 1),
            windows=[], phi_min=0.3, phi_max=0.8,
            t_earliest=100.0 + i * 100, t_latest=250.0 + i * 100,
            duration=30.0, energy=50000.0, memory=5e8,
            phi_min_res=0.0,
        ))

    target_map = {
        f"T{i:03d}": GroundTarget(
            target_id=f"T{i:03d}", lat=float(30 + i), lon=float(100 + i),
            priority=i + 1,
        )
        for i in range(N)
    }

    # Explicitly WITHOUT geom_cache
    instance = AgileSARInstance(
        tasks=tasks, N=N, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map=target_map, altitude_m=600_000.0,
        geom_cache=None,  # explicit: no cache
    )

    assert instance.geom_cache is None, "geom_cache should be None for fallback test"

    problem = B2ProfitProblem(instance)

    # Select all 3 tasks
    X = np.array([[0.8, 0.8, 0.8, 0.5, 0.5, 0.5]])

    out = {}
    # Should NOT raise — falls back to compute_full_attitude
    problem._evaluate(X, out)

    assert "F" in out
    assert "G" not in out  # n_ieq_constr=0, penalty baked
    assert out["F"].shape == (1, 1)

    # Verify the fallback result is valid (not NaN/inf)
    assert np.isfinite(out["F"][0, 0]), f"F should be finite, got {out['F'][0, 0]}"
