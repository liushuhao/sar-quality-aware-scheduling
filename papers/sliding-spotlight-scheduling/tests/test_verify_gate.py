#!/usr/bin/env python3
"""Ticket 12 -- verify gate tests.

Heavy steps (shared-library suite, snapshot rebuild) run for real here
only where cheap; the promotion replay uses a minimal synthetic pilot
fixture (D12-7).  The double anti-fixtures of US12 are both covered:
decision tampering (replay FAIL) and AASR headroom (threshold-cap check).
"""
import json
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))
sys.path.insert(0, str(FORK_DOMAIN.parent.parent / "src"))

from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.nsga2 import load_manifest  # noqa: E402
from sss_core.verify import (  # noqa: E402
    aasr_headroom,
    anchor_crosscheck,
    claim_provenance,
    grid_halving,
    m1_double_check,
    predicate_source,
    promotion_replay,
    run_gate,
    scatter_precheck,
    SHARED_LIB_N0,
)

PILOT = FORK_DOMAIN / "experiments" / "results" / "pilot" / "pilot_M1NC_seed100.json"
M1NC = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M1NC_seed100.json"
M2WH = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M2WH_seed200.json"
LITERATURE = FORK_DOMAIN.parents[1] / "literature" / "fulltext"


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def pilot() -> dict:
    return json.loads(PILOT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest() -> dict:
    return load_manifest(M1NC)


@pytest.fixture(scope="module")
def m2wh() -> dict:
    return load_manifest(M2WH)


# ── evidence triple (D12-5) ───────────────────────────────────────────────

def test_m1_double_check_passes_on_clean_repo():
    step = m1_double_check()
    assert step["status"] == "PASS", step


def test_shared_lib_n0_constant():
    """The N0 baseline is the ticket-02 frozen count.

    145 -> 154 on 2026-10-05: ticket 26 added 9 shared-library tests
    (src/tests/test_t26_r20_silent_defects.py, the R20 C1 out-of-window
    guard and the so_f1 fail-loud fallback).
    """
    assert SHARED_LIB_N0 == 154


# ── grid halving (preregistered program) ─────────────────────────────────

def test_grid_halving_preregistered_program(lib):
    step = grid_halving(lib, n_samples=8)  # light sample for unit runtime
    assert step["status"] == "PASS", step
    assert step["detail"]["n_samples"] == 8


# ── predicate source (acceptance item 4) ─────────────────────────────────

def test_predicate_source_step(lib):
    step = predicate_source()
    assert step["status"] == "PASS", step


# ── promotion replay + double anti-fixtures (US12) ───────────────────────

def test_promotion_replay_reproduces_decision(pilot, manifest, lib):
    step = promotion_replay(pilot, manifest, lib)
    assert step["status"] == "PASS", step
    assert step["detail"]["derived_decision"] == "no_promotion"  # M1NC trivial


def test_promotion_replay_tamper_red(pilot, manifest, lib):
    """Anti-fixture 1: a tampered recorded decision MUST fail the replay
    (otherwise the replay cannot detect post-hoc freedom)."""
    tampered = json.loads(json.dumps(pilot))
    tampered["promotion"]["decision"] = "promote"
    step = promotion_replay(tampered, manifest, lib)
    assert step["status"] == "FAIL", step


def test_aasr_headroom_anti_fixture(lib):
    """Anti-fixture 2 (US12): unenforced AASR CAN exceed -13 dB on
    synthetic candidates -- a threshold-capped scatter would be silent."""
    step = aasr_headroom(lib)
    assert step["status"] == "PASS", step


# ── A6 scatter precheck (REPORT semantics) ───────────────────────────────

def test_scatter_precheck_structural_report(m2wh, lib):
    """D05-4 time invariance makes the within-window scatter structurally
    ~0 -> the ratio is far below 0.1 -> the preregistered escalation fires
    as a REPORT (never a FAIL), flagged action_required with the
    structural note."""
    step = scatter_precheck(m2wh, lib)
    assert step["status"] == "REPORT"
    assert step["detail"]["action_required"] is True
    assert step["detail"]["ratio"] < 0.1
    assert "D05-4" in step["detail"]["structural_note"]
    per_mode = step["detail"]["per_mode_mean_f_q"]
    assert len(per_mode) >= 2  # per-mode decomposition registered
    spread = max(per_mode.values()) / min(per_mode.values())
    assert spread > 10  # cross-mode magnitude ratio ~ 1.8 orders (A6 note)


# ── anchor crosscheck + snapshot rebuild ─────────────────────────────────

def test_anchor_crosscheck_passes(pilot, manifest, lib):
    """The double-chain check that exposed the ticket-10 C2 ordering
    defect: front max f1* must reach the anchor's 0.8931."""
    step = anchor_crosscheck(pilot, manifest, lib)
    assert step["status"] == "PASS", step
    assert step["detail"]["anchor_f1_star"] == pytest.approx(0.8931, abs=1e-3)


def test_evaluator_output_matches_frozen_fronts(lib):
    """MUST-3 guard, re-pinned to the ticket-48 world (L7, caliber v4):
    the post-constraint, single-objective evaluator reproduces every frozen
    front record from the frozen manifests.  The pinned world is
    ``experiments/v4_results/`` (constraint armed, n_obj=1): 50 synthetic
    matrix units + the s=1.0 and s=1.2 sweep arms (30 units each).

    Tie-set caliber (ticket 48 item 18): a single-objective rank-0 is the
    set of schedules REACHING the unit's max coverage -- a discrete-objective
    tie set (measured: the whole 40-population at loose orders, down to a
    handful at tight ones).  Every record must equal the unit's max f1*;
    one representative record per unit is fully re-encoded through the
    registered round-trip (1e-9, D12-1) and re-evaluated, so the assertions
    carry that tolerance on f_q and an exact-fraction tolerance on f1.
    A squint/quality-chain drift anywhere flips this red.

    Anti-vacuous: the loop must actually visit all 110 pinned units, verify
    the tie property on every record, and assert the world markers (the
    single_objective flag and the vacuous promotion decision), so an empty
    glob or a stale double-objective artifact cannot pass silently."""
    from sss_core.evaluator import SchedulingProblem
    from sss_core.nsga2 import (
        PROMOTION_VOID_SINGLE_OBJECTIVE,
        encode_seed_individual,
    )

    v4 = FORK_DOMAIN / "experiments" / "v4_results"
    scenarios = v4 / "scenarios"
    units = [(p, 1.0) for p in sorted((v4 / "matrix").glob("pilot_*.json"))]
    units += [(p, 1.0) for p in sorted((v4 / "sweep" / "s1_0").glob("pilot_*.json"))]
    units += [(p, 1.2) for p in sorted((v4 / "sweep" / "s1_2").glob("pilot_*.json"))]
    assert len(units) == 110, f"pinned v4 census changed: {len(units)}"
    families = set()
    for p, s in units:
        art = json.loads(p.read_text(encoding="utf-8"))
        assert art.get("single_objective") is True, p.name
        assert abs(float(art.get("s_factor", 1.0)) - s) <= 1e-12, p.name
        assert art["promotion"]["decision"] == PROMOTION_VOID_SINGLE_OBJECTIVE, p.name
        manifest = load_manifest(scenarios / Path(art["manifest"]).name)
        if s != 1.0:
            # mirror run_pilot's in-memory order scaling (population fixed)
            for t in manifest["tasks"]:
                if t.get("rho_req_m") is not None:
                    t["rho_req_m"] = s * float(t["rho_req_m"])
        families.add(manifest["scenario"]["family_code"])
        sp = SchedulingProblem(manifest, lib)
        front = art["front"]
        assert front, p.name
        for rec in front:
            assert rec["f1_star"] == pytest.approx(
                art["max_f1_star_on_front"], abs=1e-12
            ), p.name
        rec = front[0]
        starts = {int(k): float(v) for k, v in rec["starts"].items()}
        x = encode_seed_individual(sp, starts)
        ev = sp.evaluate(x)
        assert ev["f1_star"] == pytest.approx(rec["f1_star"], abs=1e-9), (
            p.name, rec
        )
        assert ev["f_q"] == pytest.approx(rec["f_q"], abs=1e-9), (
            p.name, rec
        )
        # CV belt: the 1e-9 round-trip start dust can cross a steep C2
        # boundary-rate gradient and produce ~1e-6 s deficits.  Genuine
        # violations are ~seconds (evaluator C2_TOL_S registration), so
        # a 1e-3 belt is three orders below anything real while still
        # catching a violated schedule.
        assert ev["cv"] <= 1e-3, (p.name, rec)
    assert families == {
        "M1NC", "M2WH", "M3NC", "M2WF", "M4WH", "R1C", "R2F", "R3H",
    }, families


def test_gate_aggregation_fail_exits_20(pilot, manifest, lib):
    """Any FAIL step -> exit 20; REPORT steps never fail the gate."""
    real_replay = promotion_replay

    def broken_replay(p, m, l):
        step = real_replay(p, m, l)
        step["status"] = "FAIL"
        return step

    import sss_core.verify as v

    original = v.promotion_replay
    v.promotion_replay = broken_replay
    try:
        report, code = run_gate(
            PILOT, M1NC, lib=lib, pop_size=10, generations=5,
            steps=["promotion_replay", "predicate_source", "scatter_precheck"],
            run_shared_tests=False,
        )
    finally:
        v.promotion_replay = original
    assert code == 20
    assert report["n_fail"] == 1
    assert report["n_report"] == 1  # REPORT does not fail the gate


def test_gate_light_pass(pilot, manifest, lib):
    """Light gate (no shared tests, no snapshot) passes on the seeded
    pilot."""
    report, code = run_gate(
        PILOT, M1NC, lib=lib, pop_size=10, generations=5,
        steps=["predicate_source", "promotion_replay", "aasr_headroom",
               "scatter_precheck", "anchor_crosscheck"],
        run_shared_tests=False,
    )
    assert code == 0, [s for s in report["steps"] if s["status"] == "FAIL"]
    assert report["n_fail"] == 0


def test_claim_provenance_passes_with_sources_present():
    """On a machine with literature/ restored, the provenance gate is green.

    Skipped elsewhere: literature/ is gitignored, and the step's rc=2 ->
    REPORT behaviour is asserted separately below, so a missing source must
    not make this test fail.
    """
    if not LITERATURE.is_dir():
        pytest.skip("literature/ absent; see test_claim_provenance_rc2_is_report")
    step = claim_provenance()
    assert step["status"] == "PASS", step
    assert step["detail"]["exit"] == 0


@pytest.mark.parametrize(
    "rc,expected",
    [(0, "PASS"), (1, "FAIL"), (2, "REPORT"), (3, "FAIL"), (99, "FAIL")],
)
def test_claim_provenance_rc_mapping(monkeypatch, rc, expected):
    """Every rc maps explicitly; an unrecognised rc is FAIL, never PASS.

    The false-green this guards: mapping only rc==1 to FAIL would let a
    verifier that checks nothing (rc=3, empty registry) or that is simply
    broken (unknown rc) report success.
    """
    import subprocess as sp

    import sss_core.verify as v

    def fake_run(argv, **kw):
        return sp.CompletedProcess(argv, rc, "", "")

    monkeypatch.setattr(v.subprocess, "run", fake_run)
    step = v.claim_provenance()
    assert step["status"] == expected, (rc, step)


def test_claim_provenance_rc2_does_not_set_action_required(monkeypatch):
    """rc=2 must be a REPORT that leaves the gate green AND must not raise
    the global action_required flag -- run_verify.py prints a hardcoded
    'A6 scatter precheck' message when that flag is set."""
    import subprocess as sp

    import sss_core.verify as v

    monkeypatch.setattr(
        v.subprocess, "run",
        lambda argv, **kw: sp.CompletedProcess(argv, 2, "", ""),
    )
    step = v.claim_provenance()
    assert step["status"] == "REPORT"
    assert step["detail"]["restore_required"] is True
    assert "action_required" not in step["detail"]


def test_claim_provenance_missing_script_fails(monkeypatch):
    """A missing verifier must FAIL loudly, not raise FileNotFoundError
    and take the whole gate down with a traceback."""
    import sss_core.verify as v

    monkeypatch.setattr(
        v, "FORK_DOMAIN", v.FORK_DOMAIN / "no_such_directory_xyz",
    )
    step = v.claim_provenance()
    assert step["status"] == "FAIL"
    assert "missing" in step["detail"]


# ── domain-suite baseline predicate (ticket 46) ──────────────────────────

def test_domain_counts_is_a_floor_not_an_equality():
    """The suite is expected to GROW, so its pass count is a floor.

    An exact pin fired on every addition and forced a re-pin (tickets 29
    f546573, 30, 40, 44).  A floor still catches tests silently disappearing --
    a net decrease drops below it exactly as reliably as it breaks equality --
    while dropping the false alarm on additions.
    """
    from sss_core.verify import (
        DOMAIN_N0,
        DOMAIN_N0_SKIPPED,
        DOMAIN_N0_XFAILED,
        domain_counts_ok,
    )

    assert domain_counts_ok(DOMAIN_N0 + 3, 0, DOMAIN_N0_SKIPPED, DOMAIN_N0_XFAILED), (
        "adding tests must not fail the gate -- the count is a floor"
    )
    assert domain_counts_ok(DOMAIN_N0, 0, DOMAIN_N0_SKIPPED, DOMAIN_N0_XFAILED)
    assert not domain_counts_ok(
        DOMAIN_N0 - 1, 0, DOMAIN_N0_SKIPPED, DOMAIN_N0_XFAILED
    ), "a net decrease must still fail -- that is the failure the baseline exists for"


@pytest.mark.parametrize(
    "failed,skipped,xfailed",
    [
        (1, 1, 0),  # a failure
        (0, 2, 0),  # an extra conditional skip appeared
        (0, 0, 0),  # the one expected skip disappeared
        (0, 1, 1),  # an xfail appeared
    ],
)
def test_domain_counts_keeps_failures_skips_xfails_exact(failed, skipped, xfailed):
    """Those three stay exact: each drift encodes a real change in condition."""
    from sss_core.verify import DOMAIN_N0, domain_counts_ok

    assert not domain_counts_ok(DOMAIN_N0, failed, skipped, xfailed)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
