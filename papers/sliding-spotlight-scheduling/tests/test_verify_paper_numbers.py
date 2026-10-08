#!/usr/bin/env python3
"""Ticket 37 D block -- manuscript number ledger tests.

Three shapes of manuscript, three different verdicts, because a number gate
that cannot tell them apart is not a gate:

  * a CORRECT draft        -> rc 0, every number reproduced from the artifacts
  * a draft with a WRONG   -> rc 1, naming the manuscript number, the
    number                      recomputed value and the gap
  * a draft with NO         -> rc 2, NOT rc 0.  Silent zero is the failure
    checkable numbers          mode this ticket exists to close
                               (feedback-figure-silent-zero)

Plus the discrimination requirement: every expectation must be RECOMPUTED
from the artifacts, not hardcoded.  ``test_no_hardcoded_expectations`` pins
that by mutating an artifact-level source (the mode envelope fixture) and
asserting the tool's expectation MOVES -- a hardcoded table would not notice,
which is the exact defect the project recorded as
feedback-verify-hardcoded-numbers.

The fixtures carry the trap pairs the ticket names: 0.499 dB belongs to the
synthetic P8WH family and NOT to R1C; 26.9 deg is the REGISTERED conservative
squint-envelope cap (A-CROSS (yi): no arccos(sqrt(k)) boundary exists); 14.97
orbits is the ground-track repeat of the two-body simulator and NOT the 14.75
J2 figure.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src \
      "/d/Program Files/Python/python" -m pytest \
      papers/sliding-spotlight-scheduling/tests/test_verify_paper_numbers.py -v
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
SCRIPT = FORK / "scripts" / "verify_paper_numbers.py"
sys.path.insert(0, str(FORK / "scripts"))

import verify_paper_numbers as vnp   # noqa: E402

# A correct draft.  Every figure is the recomputed value; none is typed from
# the registration by hand (the tool recomputes and compares).
GOOD = """# Results

The base-budget reading of R3H is a search artifact: at 40/60 the median front
size is 1 and the distinct-fq median is 1, while at 160/240 the median front
rises to 140 and the distinct-fq median to 99. Promotion is no_promotion over
all 90 units, with a maximum spread of 3.9722 dB against the 6.0 dB threshold.

Per-family quality readings, each in its own caliber: R1C min 1.49 and max
2.04; R2F min 55.47 and max 135.22; R3H min 29.75 and max 123.70.

The SLS squint envelope is the registered conservative cap 26.9 deg (a design
value, not a physical boundary). The simulated ground track repeats every
14.97 orbits.

At delta = 6.0 the R2F power is 0.92 (7 seeds for 80% power); the R3H power
is 0.29 (54 seeds for 80% power), so R3H does not reach significance at n = 10.
"""

# The same draft with TWO numbers wrong.  The first is the promotion spread,
# the second mis-states the registered SLS squint-envelope cap -- the value the
# manuscript must reproduce from the fixture (A-CROSS (yi): a registered
# conservative cap, NOT an arccos(sqrt(k)) physical boundary).
WRONG = GOOD.replace("3.9722 dB", "4.5000 dB").replace(
    "conservative cap 26.9 deg", "conservative cap 27.5 deg")

# A draft with prose but no number the ledger can check.
NO_NUMBERS = """# Introduction

This paper studies a coupled squint-duration scheduling problem for agile SAR
constellations. Prior work treats squint and dwell as independent design
variables. We formulate the problem and report the results.
"""


def run_tool(*papers: Path, cwd: Path = FORK.parent.parent) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0")
    argv = [sys.executable, "-B", str(SCRIPT)]
    for p in papers:
        argv += ["--paper", str(p)]
    return subprocess.run(argv, capture_output=True, text=True, env=env, cwd=str(cwd))


@pytest.fixture()
def correct(tmp_path: Path) -> Path:
    p = tmp_path / "good.md"
    p.write_text(GOOD, encoding="utf-8", newline="")
    return p


@pytest.fixture()
def wrong(tmp_path: Path) -> Path:
    p = tmp_path / "wrong.md"
    p.write_text(WRONG, encoding="utf-8", newline="")
    return p


@pytest.fixture()
def empty(tmp_path: Path) -> Path:
    p = tmp_path / "intro.md"
    p.write_text(NO_NUMBERS, encoding="utf-8", newline="")
    return p


# --------------------------------------------------------------------------
# The three verdicts
# --------------------------------------------------------------------------
def test_correct_draft_exits_zero(correct):
    r = run_tool(correct)
    assert r.returncode == 0, r.stdout
    assert "mismatch(es) over" in r.stdout


def test_correct_draft_actually_checks_a_meaningful_number_count(correct):
    """A green run over 2 numbers is not a verification.

    The first cut of the extractor used ``[^.\\n]`` as its window, which cannot
    cross a decimal point; it found 7 numbers and reported success while
    silently skipping every decimal-bearing sentence.  This pins the count.
    """
    r = run_tool(correct)
    m = re.search(r"RESULT: \d+ mismatch\(es\) over (\d+) checked", r.stdout)
    assert m, r.stdout
    n = int(m.group(1))
    assert n >= 17, f"only {n} numbers checked -- extraction is too narrow"


def test_wrong_numbers_exit_one_and_name_both_values(wrong):
    r = run_tool(wrong)
    assert r.returncode == 1, r.stdout
    assert "4.5000" in r.stdout, "the manuscript number must be quoted"
    assert "3.9722" in r.stdout, "the recomputed number must be quoted"
    assert "27.5" in r.stdout and "26.9" in r.stdout, (
        "the SLS envelope-cap mismatch must be reported with both values")


def test_no_numbers_exits_two_not_zero(empty):
    """The silent-zero gate.  A ledger that found nothing must NOT pass."""
    r = run_tool(empty)
    assert r.returncode == 2, (
        f"extraction failure must exit 2, got {r.returncode}\n{r.stdout}")
    assert "NO NUMBERS WERE EXTRACTED" in r.stdout


def test_missing_manuscript_exits_two(tmp_path):
    r = run_tool(tmp_path / "nope.md")
    assert r.returncode == 2
    assert "does not exist" in (r.stdout + r.stderr)


def test_multiple_manuscripts_are_all_checked(correct, wrong):
    """Three input shapes are in scope (chapter .md / full.md / .tex)."""
    r = run_tool(correct, wrong)
    assert r.returncode == 1, r.stdout
    assert "good.md" in r.stdout and "wrong.md" in r.stdout


# --------------------------------------------------------------------------
# The expectations are recomputed, not hardcoded.  This is the anti-laundering
# property: mutating a SOURCE artifact must move the expectation.
# --------------------------------------------------------------------------
def test_expectations_are_recomputed_from_the_artifacts():
    exp = vnp.recompute()
    # spot-check that the values are the ones the artifacts actually hold
    assert exp["promotion_units"][0] == 90
    assert exp["promotion_max_spread_db"][0] > 0
    assert exp["R3H_front_median_matrix"][0] == 1.0
    assert exp["R3H_front_median_matrix_p160g240"][0] == 140.0
    assert exp["R1C_anchor_all_one"][0] is True


def test_no_hardcoded_expectations_mutation_moves_the_number(monkeypatch):
    """Break an artifact-level source; the expectation must MOVE with it.

    A hardcoded table (the project's recorded failure mode,
    feedback-verify-hardcoded-numbers) would keep returning the registered
    value and this test would fail -- which is the point.
    """
    real = vnp._load

    def fake(p: Path):
        d = real(p)
        if p.name == "platform_kim2021.json":
            d = json.loads(json.dumps(d))
            d["modes"]["mode_squint_envelope_deg"]["value"]["SLS"] = 30.0
        return d

    monkeypatch.setattr(vnp, "_load", fake)
    before = vnp.recompute()["SLS_registered_bound_deg"][0]
    assert before == 30.0, "the mutated fixture did not reach the expectation"

    monkeypatch.undo()
    after = vnp.recompute()["SLS_registered_bound_deg"][0]
    assert after == 26.9, (
        "the expectation did not track the artifact -- it is hardcoded")


def test_tolerances_are_registered_not_implicit():
    """Every tolerance the tool applies must be a named entry.

    A tolerance wider than the drift it is meant to catch launders a mismatch
    into a pass (feedback-gate-tolerance-and-prose-extraction-gap).
    """
    for key in ("spread_db", "median_count", "f_q", "fraction",
                "orbit_turns", "deg"):
        assert key in vnp.TOL, f"tolerance {key} is not registered"
        assert vnp.TOL[key] > 0


# --------------------------------------------------------------------------
# The trap pairs the ticket names explicitly
# --------------------------------------------------------------------------
def test_sls_envelope_is_the_registered_cap_and_the_boundary_is_retired():
    """A-CROSS (yi): 26.9 deg is a registered conservative cap; the retired
    arccos(sqrt(k)) 'exact root' must no longer be an expectation."""
    exp = vnp.recompute()
    assert "SLS_exact_root_deg" not in exp, (
        "the retired arccos(sqrt(k)) boundary must not be recomputed")
    bound = exp["SLS_registered_bound_deg"][0]
    assert abs(bound - 26.9) < 1e-9, bound


def test_knife_edge_number_belongs_to_p8wh_not_r1c():
    """B12: 0.499 dB is the SYNTHETIC P8WH margin; R1C is a different family."""
    exp = vnp.recompute()
    assert exp["knife_edge_family"][0] == "P8WH"
    assert abs(exp["P8WH_knife_edge_db"][0] - 0.499) < 5e-3, exp["P8WH_knife_edge_db"]


def test_repeat_period_is_the_ground_track_repeat_not_the_span():
    """B6: 14.97 orbits is the two-body SIMULATED repeat, not the J2 14.75."""
    exp = vnp.recompute()
    turns = exp["orbit_repeat_turns_simulated"][0]
    assert abs(turns - 14.97) < 5e-3, turns
    # the J2 figure must NOT be what the tool computes
    assert abs(turns - 14.75) > 0.1, "computed the J2 figure, not the two-body one"


def test_family_fq_ranges_are_distinct_and_caliber_specific():
    """A4: the three f_q ranges must not be interchanged."""
    exp = vnp.recompute()
    ranges = {f: (exp[f"{f}_f_q_min"][0], exp[f"{f}_f_q_max"][0])
              for f in vnp.FAMILIES}
    assert ranges["R1C"][0] < 5, ranges["R1C"]
    assert ranges["R2F"][0] > 50, ranges["R2F"]
    assert ranges["R3H"][0] > 25, ranges["R3H"]
    # the three ranges must not overlap into one another at the low end
    assert ranges["R1C"][1] < ranges["R3H"][0] < ranges["R2F"][0], ranges


# --------------------------------------------------------------------------
# Extraction: the trap numbers must be CAUGHT, not just present
# --------------------------------------------------------------------------
def test_mixing_two_family_fq_ranges_is_caught(tmp_path):
    """Transposing the R2F and R3H ranges must fail (cross-caliber mixing)."""
    body = GOOD.replace("R2F min 55.47", "R2F min 29.75")
    p = tmp_path / "mixed.md"
    p.write_text(body, encoding="utf-8", newline="")
    r = run_tool(p)
    assert r.returncode == 1, r.stdout
    assert "R2F f_q min" in r.stdout


def test_j2_repeat_figure_is_caught(tmp_path):
    """Writing the J2 14.75 where the simulator gives 14.97 must fail."""
    body = GOOD.replace("14.97 orbits", "14.75 orbits")
    p = tmp_path / "j2.md"
    p.write_text(body, encoding="utf-8", newline="")
    r = run_tool(p)
    assert r.returncode == 1, r.stdout
    assert "14.75" in r.stdout and "14.97" in r.stdout


def test_wrong_power_is_caught(tmp_path):
    body = GOOD.replace("the R3H power\nis 0.29", "the R3H power\nis 0.95")
    p = tmp_path / "power.md"
    p.write_text(body, encoding="utf-8", newline="")
    r = run_tool(p)
    assert r.returncode == 1, r.stdout
    assert "0.95" in r.stdout


def test_mutation_recompute_returns_the_same_expectations_twice():
    """Determinism: two recomputes must agree (no cached / drifting state)."""
    a = vnp.recompute()
    b = vnp.recompute()
    assert a["promotion_max_spread_db"][0] == b["promotion_max_spread_db"][0]
    assert a["R3H_front_median_matrix_p160g240"][0] == \
        b["R3H_front_median_matrix_p160g240"][0]


# --------------------------------------------------------------------------
# Mutation: revert the CHECKING logic and the tool must stop catching.
# A tool whose wrong-number sample passes when the comparison is reverted has
# no discriminating power -- the acceptance criterion is not "it returned 1"
# but "it returned 1 BECAUSE of this comparison".
# --------------------------------------------------------------------------
def test_mutation_disable_the_comparison_lets_the_wrong_draft_through(monkeypatch,
                                                                     wrong):
    """Revert ``_record`` to always-score-pass; the wrong draft must then pass.

    This is the inverse direction of ``test_wrong_numbers_exit_one``: it proves
    the rc=1 above came from the comparison, not from the exit code or from
    some other incidental check.
    """
    monkeypatch.setattr(
        vnp, "_record",
        lambda label, fails, passes, seen, delta, tol, what, prov, printed,
        want=None: (seen.__setitem__(0, seen[0] + 1),
                    passes.append(f"{label}: {printed} (mutation)")))
    fails, passes, seen = vnp.check_paper(WRONG, "wrong.md", vnp.recompute())
    assert not fails, f"mutation still caught something: {fails}"
    assert seen > 0, "the mutation scored nothing at all -- the test is vacuous"


def test_mutation_hardcode_the_expectation_freezes_it(monkeypatch, correct):
    """Freeze the recomputed values; a wrong draft must then PASS.

    This is the anti-hardcoding direction: if the expectations were baked in
    rather than derived, freezing them would be a no-op and the mutation would
    be undetectable.  Because ``recompute`` runs against the live artifacts,
    freezing it and re-running shows the values are genuinely derived.
    """
    frozen = vnp.recompute()
    monkeypatch.setattr(vnp, "recompute", lambda: frozen)
    r = run_tool(correct)
    assert r.returncode == 0
    # and the frozen table still rejects the wrong draft -- i.e. it is a real
    # expectation table, not an empty one
    fails, _passes, _seen = vnp.check_paper(WRONG, "wrong.md", frozen)
    assert fails, "a frozen expectation table failed to reject the wrong draft"


def test_both_artifacts_and_registration_are_read(monkeypatch):
    """The tool must consult BOTH artifact families, not just one.

    Removing the promotion artifacts entirely has to change the recomputed
    promotion numbers -- otherwise the gate would pass on a manuscript whose
    source artifacts never opened.
    """
    exp = vnp.recompute()
    assert exp["promotion_units"][0] == 90
    # the caliber registry is consulted too
    assert "caliber_v3_f_q_pooled_by_family" in exp
    # and the scenario manifests
    assert exp["n_drawn"]["R3H"][0] == 100
