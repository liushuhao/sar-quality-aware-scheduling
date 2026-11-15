"""TDD tests for run_baselines_v4.py (run_scenario) output structure.

run_scenario runs the production G-BL (b1) / G-SM (b3) construction path and
returns the persisted per-scenario dict. Assert the exact structure that
baselines_200.json consumes: f1/f1_raw/f1_gbl/f2/f3/n_selected/n_targets/
runtime_s. (Legacy schedule_* metadata fields were removed with the
run_baselines_300->v4 refactor; no production consumer reads them.)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

PROJECT = Path(__file__).resolve().parent.parent.parent / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"

sys.path.insert(0, str(PROJECT / "experiments"))
from run_baselines_v4 import run_scenario


def _run(solver):
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_scenario(sample)
    return result[solver]


def test_b1_output_structure():
    """run_scenario G-BL entry has the production persisted fields."""
    b1 = _run("b1")
    for f in ["f1", "f1_raw", "f1_gbl", "f2", "f3", "n_selected", "n_targets", "runtime_s"]:
        assert f in b1, f"b1 must contain '{f}'"
    assert isinstance(b1["f1"], (int, float))
    assert isinstance(b1["n_selected"], int)
    assert b1["n_selected"] > 0
    assert b1["n_targets"] > 0
    # G-BL is its own reference: f1_normalized == 1.0
    assert abs(b1["f1"] - 1.0) < 1e-9
    assert abs(b1["f1_raw"] - b1["f1_gbl"]) < 1e-9


def test_b3_output_structure():
    """run_scenario G-SM entry has the production persisted fields."""
    b3 = _run("b3")
    for f in ["f1", "f1_raw", "f1_gbl", "f2", "f3", "n_selected", "n_targets", "runtime_s"]:
        assert f in b3, f"b3 must contain '{f}'"
    assert isinstance(b3["f1"], (int, float))
    assert 0.0 <= b3["f1"] <= 1.5  # normalized against G-BL, may exceed 1.0 slightly
    assert isinstance(b3["n_selected"], int)


def test_no_legacy_schedule_fields():
    """Legacy schedule_* metadata was removed; ensure it does not resurface."""
    b1 = _run("b1")
    for f in ["schedule_incidence_deg", "schedule_phis_off_nadir", "schedule_t_actuals"]:
        assert f not in b1, f"legacy field '{f}' should not be present"
