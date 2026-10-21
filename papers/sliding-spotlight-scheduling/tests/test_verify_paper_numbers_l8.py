#!/usr/bin/env python3
"""Ticket 50 (B4) -- the L8 manuscript-number ledger.

Three manuscript shapes, three verdicts (the ticket-37 discipline for the L8
world): a CORRECT draft passes, a WRONG number fails naming both values, and a
manuscript with no L8 number exits 2 -- not 0 -- because the v3-era text has no
L8 reading in it, and "checked nothing" must never look like a pass.

Plus the anti-laundering property: the expectations are recomputed from the
raw sweep units and cross-checked against ``sweep_results.json``; perturb the
aggregate and the tool must report the disagreement instead of choosing one.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -m pytest \
      papers/sliding-spotlight-scheduling/tests/test_verify_paper_numbers_l8.py -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
SCRIPT = FORK / "scripts" / "verify_paper_numbers_l8.py"
sys.path.insert(0, str(FORK / "scripts"))

import verify_paper_numbers_l8 as v8  # noqa: E402

GOOD = (
    "At the order point the R3H coverage at s = 1.0 reads 94.8% "
    "(L8 caliber v5, nine-point demand grid).\n"
)
WRONG = GOOD.replace("94.8%", "88.0%")
NO_L8 = ("The R3H median front size at 160/240 is 140 and the distinct-fq "
         "median is 99.\n")


def run_tool(*papers: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0")
    argv = [sys.executable, "-B", str(SCRIPT)]
    for p in papers:
        argv += ["--paper", str(p)]
    return subprocess.run(argv, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env,
                          cwd=str(FORK.parent.parent))


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8", newline="")
    return p


# --------------------------------------------------------------------------
# Readings-only mode
# --------------------------------------------------------------------------
def test_readings_only_mode_exits_zero_and_names_the_mode():
    r = run_tool()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "MODE: readings only" in r.stdout
    assert "tie-set units    = 260" in r.stdout
    assert "STR library floor= 2.4669" in r.stdout


# --------------------------------------------------------------------------
# The three verdicts
# --------------------------------------------------------------------------
def test_correct_l8_draft_exits_zero(tmp_path):
    r = run_tool(_write(tmp_path, "good.md", GOOD))
    assert r.returncode == 0, r.stdout
    assert "every checked L8 number reproduces" in r.stdout


def test_wrong_l8_number_exits_one_and_names_both_values(tmp_path):
    r = run_tool(_write(tmp_path, "wrong.md", WRONG))
    assert r.returncode == 1, r.stdout
    assert "88.0" in r.stdout or "0.88" in r.stdout
    assert "0.9484" in r.stdout


def test_manuscript_without_l8_numbers_exits_two(tmp_path):
    """The current (v3-world) manuscript shape: no L8 reading, so NOT a pass."""
    r = run_tool(_write(tmp_path, "intro.md", NO_L8))
    assert r.returncode == 2, r.stdout
    assert "NO L8 NUMBERS WERE EXTRACTED" in r.stdout


# --------------------------------------------------------------------------
# A4: the fulfillment reading must carry its three-part caliber tag
# --------------------------------------------------------------------------
def test_untagged_fulfillment_reading_fails(tmp_path):
    body = ("R3H fulfillment ratio at s = 1.0 is 0.7447 at the order point.\n")
    r = run_tool(_write(tmp_path, "ful.md", body))
    assert r.returncode == 1, r.stdout
    assert "lacks caliber element" in r.stdout


def test_tagged_fulfillment_reading_passes(tmp_path):
    body = ("R3H fulfillment ratio at s = 1.0 is 0.7447 (library caliber f_q, "
            "tie-set members mean; reported reading, not an optimization "
            "target).\n")
    r = run_tool(_write(tmp_path, "ful_ok.md", body))
    assert r.returncode == 0, r.stdout


# --------------------------------------------------------------------------
# The anti-laundering property: expectations are recomputed, and the aggregate
# is cross-checked against the raw units rather than trusted.
# --------------------------------------------------------------------------
def test_expectations_are_recomputed_from_the_raw_units():
    exp = v8.recompute()
    assert exp["sweep_units"][0] == 260
    assert exp["tie_set_units"][0] == 260
    assert exp["anchor_optimal_units"][0] == 258
    assert len(exp["search_win_units"][0]) == 2
    assert abs(exp["coverage_median"][("R2F", 1.0)][0] - 0.9764210609534351) < 1e-12


def test_aggregate_disagreeing_with_the_raw_units_is_reported(monkeypatch):
    real = v8._load

    def fake(p):
        d = real(p)
        if Path(p) == v8.AGGREGATE:
            d = json.loads(json.dumps(d))
            d["families"]["R3H"]["1.0"]["coverage_median"] += 0.01
        return d

    monkeypatch.setattr(v8, "_load", fake)
    exp = v8.recompute()
    problems, _prov = exp["_aggregate_problems"]
    assert problems, "the aggregate/raw-unit disagreement was not detected"


# --------------------------------------------------------------------------
# Ticket 50 phase 2: the tolerance must be finer than the effect it judges.
# The whole non-monotone spread of the R2F curve is under 0.3 pp, so a fixed
# 0.5 pp tolerance would let a draft swap two grid points and still pass.
# --------------------------------------------------------------------------
def test_tolerance_is_half_the_last_printed_digit():
    assert v8._printed_tol("94.8%") == 5e-4      # 0.1 % -> half unit
    assert v8._printed_tol("94.80%") == 5e-5
    assert v8._printed_tol("1.3286") == 5e-5
    assert v8._printed_tol("477,308") == 0.5
    # and the fixed tolerance this replaces was 10x coarser than the effect
    assert v8._printed_tol("97.4%") < (0.9764210609534351 - 0.9737381969424461)


def test_a_swapped_grid_point_is_caught(tmp_path):
    """s=0.9 stated as its s=1.0 value: 97.6 % vs the true 97.37 %."""
    body = "R2F coverage at s = 0.9 reads 97.6%.\n"
    r = run_tool(_write(tmp_path, "swap.md", body))
    assert r.returncode == 1, r.stdout
    assert "0.9737" in r.stdout or "0.973738" in r.stdout


def test_a_correctly_rounded_grid_point_passes(tmp_path):
    body = "R2F coverage at s = 0.9 reads 97.4%.\n"
    r = run_tool(_write(tmp_path, "ok.md", body))
    assert r.returncode == 0, r.stdout


# --------------------------------------------------------------------------
# Ticket 50 phase 2: the new readings registered in the ledger
# --------------------------------------------------------------------------
def test_an_infeasible_point_is_a_checked_fact_not_a_skipped_line(tmp_path):
    good = ("R1C at s = 0.8 has no feasible individual in 10 of 10 seeds.\n")
    assert run_tool(_write(tmp_path, "inf.md", good)).returncode == 0
    bad = ("R1C at s = 0.8 has no feasible individual in 0 of 10 seeds.\n")
    r = run_tool(_write(tmp_path, "inf_bad.md", bad))
    assert r.returncode == 1, r.stdout


def test_demand_and_retention_readings_are_checked(tmp_path):
    body = ("The nine-point tie set serves 477,308 task instances.\n"
            "R3H retention on the STR-clip-only caliber is 71.00%.\n")
    assert run_tool(_write(tmp_path, "dr.md", body)).returncode == 0
    wrong_served = body.replace("477,308", "477,300")
    r = run_tool(_write(tmp_path, "dr_bad1.md", wrong_served))
    assert r.returncode == 1, r.stdout
    wrong_retention = body.replace("71.00%", "70.00%")
    r = run_tool(_write(tmp_path, "dr_bad2.md", wrong_retention))
    assert r.returncode == 1, r.stdout


def test_a_coverage_cost_is_not_scored_against_the_coverage_curve(tmp_path):
    """A cost sentence contains 'coverage' and a number; it is a DIFFERENCE."""
    body = ("R3H coverage cost at the order point is 4.15 pp relative to its "
            "own saturation at s = 2.0.\n")
    r = run_tool(_write(tmp_path, "cost.md", body))
    assert r.returncode == 0, r.stdout


# --------------------------------------------------------------------------
# Ticket 50 phase 2: retired-world tokens (single global ban list)
# --------------------------------------------------------------------------
def test_a_retired_token_beside_an_l8_number_fails(tmp_path):
    body = ("R3H coverage at s = 1.0 reads 94.8%. Over all 90 units the "
            "promotion decision is no_promotion.\n")
    r = run_tool(_write(tmp_path, "rev.md", body))
    assert r.returncode == 1, r.stdout
    assert "old_world_90_units" in r.stdout


def test_a_retired_token_without_any_l8_number_is_pending_not_a_pass(tmp_path):
    body = "Over all 90 units the promotion decision is no_promotion.\n"
    r = run_tool(_write(tmp_path, "rev_only.md", body))
    assert r.returncode == 2, r.stdout
    assert "PENDING" in r.stdout


def test_a_labelled_retracted_comparison_passes(tmp_path):
    body = ("R3H coverage at s = 1.0 reads 94.8%. The L7 tight arm 0.446 is "
            "superseded by the L8 reading.\n")
    r = run_tool(_write(tmp_path, "lab.md", body))
    assert r.returncode == 0, r.stdout


def test_an_unlabelled_retracted_value_fails(tmp_path):
    body = ("R3H coverage at s = 1.0 reads 94.8%. The tight arm measured "
            "0.446 there.\n")
    r = run_tool(_write(tmp_path, "lab_bad.md", body))
    assert r.returncode == 1, r.stdout
    assert "l7_tight_arm_0_446" in r.stdout


# --------------------------------------------------------------------------
# Ticket 50 phase 2: exit-11 is read from the driver ledger, never inferred
# --------------------------------------------------------------------------
def test_exit_census_matches_the_driver_ledger():
    n, keys, seeds = v8._exit_census("R1C", 0.8)
    assert n == 10 and len(keys) == 10 and seeds == set()
    n2, keys2, seeds2 = v8._exit_census("R3H", 0.8)
    assert n2 == 0 and keys2 == set() and len(seeds2) == 10


def test_an_unexpected_exit_code_is_a_crash_not_a_structural_fact(monkeypatch):
    real = v8._load

    def fake(p):
        d = real(p)
        if str(p).endswith("_progress.json") and "s0_9" in str(p).replace(
                "\\", "/"):
            d = json.loads(json.dumps(d))
            key = next(k for k in d["units"] if k.startswith("R3H_"))
            d["units"][key]["exit"] = 1
        return d

    monkeypatch.setattr(v8, "_load", fake)
    with pytest.raises(RuntimeError, match="unexpected exit codes"):
        v8._exit_census("R3H", 0.9)


def test_recompute_reports_the_demand_and_violation_readings():
    exp = v8.recompute()
    assert exp["served_task_instances"][0] == 477308
    assert exp["tie_set_records"][0] == 9430
    assert exp["delivery_cv_max"][0] == 0.0
    assert exp["coverage_cost_pp"]["R3H"][0] == pytest.approx(-4.15, abs=0.005)
    assert exp["coverage_cost_pp"]["R2F"][0] == pytest.approx(-2.36, abs=0.005)
    assert exp["criteria"][0]["R2F"] == {"C1": False, "C2": True, "C3": False}
