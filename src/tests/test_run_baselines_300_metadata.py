"""TDD tests for run_baselines_300.py schedule metadata.

Test that run_one() output includes schedule metadata fields:
- schedule_incidence_deg: List[float]  — incidence angles in degrees
- schedule_phis_off_nadir: List[float] — off-nadir angles in degrees
- schedule_t_actuals: List[float] — observation start times (UNIX timestamps)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

PROJECT = Path(__file__).resolve().parent.parent.parent / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"

sys.path.insert(0, str(PROJECT / "experiments"))
from run_baselines_v4 import run_scenario as run_one


def test_b1_output_has_schedule_metadata():
    """run_one() G-BL entry must contain schedule_incidence_deg, schedule_phis_off_nadir,
    and schedule_t_actuals."""
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_one(sample)
    b1 = result["b1"]

    assert "schedule_incidence_deg" in b1
    assert "schedule_phis_off_nadir" in b1
    assert "schedule_t_actuals" in b1

    inc = b1["schedule_incidence_deg"]
    phi = b1["schedule_phis_off_nadir"]
    t_act = b1["schedule_t_actuals"]
    n = b1["n_selected"]

    assert isinstance(inc, list)
    assert isinstance(phi, list)
    assert isinstance(t_act, list)
    assert len(inc) == n
    assert len(phi) == n
    assert len(t_act) == n

    assert all(isinstance(v, (int, float)) for v in inc)
    assert all(isinstance(v, (int, float)) for v in phi)
    assert all(isinstance(v, (int, float)) for v in t_act)


def test_b3_output_has_schedule_metadata():
    """run_one() G-SM entry must contain schedule metadata fields."""
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_one(sample)
    b3 = result["b3"]

    assert "schedule_incidence_deg" in b3
    assert "schedule_phis_off_nadir" in b3
    assert "schedule_t_actuals" in b3

    inc = b3["schedule_incidence_deg"]
    phi = b3["schedule_phis_off_nadir"]
    t_act = b3["schedule_t_actuals"]
    n = b3["n_selected"]

    assert isinstance(inc, list)
    assert isinstance(phi, list)
    assert isinstance(t_act, list)
    assert len(inc) == n
    assert len(phi) == n
    assert len(t_act) == n
    assert all(isinstance(v, (int, float)) for v in inc)
    assert all(isinstance(v, (int, float)) for v in phi)
    assert all(isinstance(v, (int, float)) for v in t_act)


def test_schedule_metadata_preserves_existing_fields():
    """Adding schedule metadata must not remove existing fields."""
    sample = SCENARIOS_DIR / "S1" / "S1-A_seed00.pkl"
    result = run_one(sample)

    for solver_label, entry in [("b1", result["b1"]), ("b3", result["b3"])]:
        for f in ["f1", "f2", "n_selected", "runtime_s", "c3_enforced", "solver"]:
            assert f in entry, f"{solver_label} must retain '{f}'"
