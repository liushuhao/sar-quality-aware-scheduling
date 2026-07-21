"""TDD tests for run_so_f1.py schedule metadata.

Test that run_one() output includes schedule metadata fields:
- selected: List[int]     — indices of selected tasks
- t_actuals: List[float]  — actual observation start times
- phis_off_nadir: List[float] — off-nadir angles (degrees)

Phase 1 (RED): Tests written first, expected to FAIL.
"""

import sys
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"

# Import the runner's run_one function
sys.path.insert(0, str(PROJECT / "experiments"))
from run_so_f1 import run_one


def test_b2_ga_output_has_schedule_metadata():
    """run_one() for GA-P GA must contain selected, t_actuals, phis_off_nadir."""
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_one(sample)

    assert "selected" in result, (
        "GA-P GA result missing 'selected' — runner must pass through "
        "selected task indices from solver metadata"
    )
    assert "t_actuals" in result, (
        "GA-P GA result missing 't_actuals'"
    )
    assert "phis_off_nadir" in result, (
        "GA-P GA result missing 'phis_off_nadir'"
    )

    # Type and consistency checks
    sel = result["selected"]
    t_act = result["t_actuals"]
    phis = result["phis_off_nadir"]
    n = result["n_selected"]

    assert isinstance(sel, list), "selected must be a list"
    assert isinstance(t_act, list), "t_actuals must be a list"
    assert isinstance(phis, list), "phis_off_nadir must be a list"

    assert len(sel) == n, (
        f"selected length ({len(sel)}) must equal n_selected ({n})"
    )
    assert len(t_act) == n, (
        f"t_actuals length ({len(t_act)}) must equal n_selected ({n})"
    )
    assert len(phis) == n, (
        f"phis_off_nadir length ({len(phis)}) must equal n_selected ({n})"
    )

    # Element types
    assert all(isinstance(v, int) for v in sel), (
        "selected elements must be int"
    )
    assert all(isinstance(v, (int, float)) for v in t_act), (
        "t_actuals elements must be numeric"
    )
    assert all(isinstance(v, (int, float)) for v in phis), (
        "phis_off_nadir elements must be numeric"
    )


def test_b2_ga_output_preserves_existing_fields():
    """Adding schedule metadata must not remove existing f1/n_selected/n_targets."""
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_one(sample)

    for field in ["n_targets", "n_selected", "f1", "runtime_s", "solver"]:
        assert field in result, f"GA-P GA result must retain '{field}'"
