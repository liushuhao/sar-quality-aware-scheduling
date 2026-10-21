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
