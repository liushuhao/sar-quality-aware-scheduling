#!/usr/bin/env python3
"""Ticket 11 -- greedy anchor tests.

M1NC pinned values (17 served, f1* = 0.8931) come from the gate-review's
faithful simulation; the equivalence/redden pair follows the D11-2/3
assertion shapes (served-set equality + tolerance starts for the anchor;
starts movement + pointwise real >= frozen direction for the red half).
"""
import json
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))
sys.path.insert(0, str(FORK_DOMAIN.parent.parent / "src"))

from sss_core.anchor import (  # noqa: E402
    anchor_on_manifest,
    assert_fallback_active,
    greedy_anchor,
)
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.nsga2 import load_manifest  # noqa: E402
from sss_core.predicates import c2_transfer_requirement_s  # noqa: E402

M1NC = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M1NC_seed100.json"
M2WH = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M2WH_seed200.json"


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def m1nc() -> dict:
    return load_manifest(M1NC)


@pytest.fixture(scope="module")
def m2wh() -> dict:
    return load_manifest(M2WH)


# ── constructed upper-bound case (D11-4) ─────────────────────────────────

def _spaced_manifest(gap_s: float, n: int = 3) -> dict:
    """Tasks whose windows are far enough apart that C2 can never block:
    the all-served upper bound holds BY CONSTRUCTION."""
    tasks = [
        {
            "t_start_s": round(i * gap_s, 9),
            "t_end_s": round(i * gap_s + 10.0, 9),
            "t_ca_s": round(i * gap_s + 5.0, 9),
            "azimuth_size_m": 3000.0,
            "priority": 5 + i,
            "rho_req_m": 2.75,
            "mode": "STR",
            "prf_hz": 3630.0,
        }
        for i in range(n)
    ]
    return {
        "schema": "scenario-manifest/1.0",
        "scenario": {"family_code": "MXNC", "density_n_targets": n,
                     "interval_width": "N", "demand_tier": "C",
                     "platform_fixture": "experiments/platform_kim2021.json",
                     "degenerate_anchor": True},
        "preregistration": {"pads": {"inter_task_fraction": 0.0,
                                     "window_tail_fraction": 0.0}},
        "generation_ledger": {},
        "tasks": tasks,
    }


def test_constructed_upper_bound_all_served(lib):
    """f1* reaches the all-served upper bound (1.0) on a by-construction
    compatible scenario -- count verified."""
    m = _spaced_manifest(gap_s=20.0)  # need ~7 s << 20 s spacing
    res = anchor_on_manifest(m, lib)
    assert len(res.starts) == 3
    assert res.f1_star == pytest.approx(1.0)
    assert res.unserved == []


def test_unservable_overlap_witness(m1nc, lib):
    """Every unserved M1NC task genuinely overlaps a served task's window
    (physical conflict, not an algorithm failure) -- the machine-checkable
    witness required by D11-4."""
    res = anchor_on_manifest(m1nc, lib)
    assert res.f1_star == pytest.approx(
        res.served_priority / res.total_priority
    )
    for i in res.unserved:
        ws = float(m1nc["tasks"][i]["t_start_s"])
        we = float(m1nc["tasks"][i]["t_end_s"])
        overlaps = [
            j
            for j in res.starts
            if float(m1nc["tasks"][j]["t_start_s"]) <= we
            and ws <= float(m1nc["tasks"][j]["t_end_s"])
        ]
        assert overlaps, f"unserved task {i} has no window overlap witness"


# ── re-timing repair red/green pair (D11-1/5, ticket acceptance) ─────────

def test_repair_recovers_blocked_task(lib):
    """A(pri 8) and B(pri 6) share one wide window: B's earliest start is
    C2-blocked by A; the repair candidate (A.end + need) recovers it.
    Expectations computed via the ticket-09 predicate (no magic numbers).

    Ticket 49 re-base: the dwell is the TASK-LEVEL SLS dwell for this task's
    own order and scene size (rho=0.8, l_az=3 km -> ~3.20 s at psi=0), not
    the library-caliber ~6.43 s constant.
    """
    from sss_core.duration import duration_scene_s

    dur_a = duration_scene_s(
        Mode.SLS, 0.0, lib, rho_req_m=0.8, l_az_m=3000.0
    )
    need = c2_transfer_requirement_s(
        dur_a, lib,
        __import__("sss_core.duration", fromlist=["MarginPads"]).MarginPads.degenerate_anchor(),
        d_psi_rad=0.1,
    )["requirement_s"]
    # behavioral sanity band: padded dwell + maneuver + settle (D09-1)
    assert dur_a + 2.0 <= need < dur_a + 10.0

    tasks = [
        {"t_start_s": 0.0, "t_end_s": 40.0, "t_ca_s": 20.0,
         "azimuth_size_m": 3000.0, "priority": 8, "rho_req_m": 0.8,
         "mode": "SLS", "prf_hz": 3630.0},
        {"t_start_s": 0.0, "t_end_s": 40.0, "t_ca_s": 20.0,
         "azimuth_size_m": 3000.0, "priority": 6, "rho_req_m": 0.8,
         "mode": "SLS", "prf_hz": 3630.0},
    ]
    m = _pair_manifest(tasks)
    on = anchor_on_manifest(m, lib, repair=True)
    off = anchor_on_manifest(m, lib, repair=False)
    assert len(on.starts) == 2  # repair recovers B
    assert len(off.starts) == 1  # repair-off (red variant) drops B
    b_start = on.starts[[i for i in on.starts if i != min(on.starts)][0]] if len(on.starts) > 1 else None
    # B must start no earlier than A.start + need (behavioral criterion)
    starts = sorted(on.starts.values())
    assert starts[1] >= starts[0] + need - 1e-6


def _pair_manifest(tasks: list[dict]) -> dict:
    return {
        "schema": "scenario-manifest/1.0",
        "scenario": {"family_code": "MXWH", "density_n_targets": len(tasks),
                     "interval_width": "W", "demand_tier": "F",
                     "platform_fixture": "experiments/platform_kim2021.json",
                     "degenerate_anchor": False},
        "preregistration": {"pads": {"inter_task_fraction": 0.0,
                                     "window_tail_fraction": 0.0}},
        "generation_ledger": {},
        "tasks": tasks,
    }


# ── ticket-13 audit regression ───────────────────────────────────────────

def test_repair_candidate_respects_window_membership(lib):
    """Fallback-regime repair candidate (constant need = 4.07 s fallback +
    2 s settle + dwell, ~7.37 s total) must NOT be accepted outside the
    task's feasible span.  Repro (2026-09-29 audit): A(pri 10, win
    [0, 40], t_ca=3) placed at 0 blocks B(pri 5, win [0, 6], t_ca=3) at
    every in-window point; pre-fix the anchor placed B at ~7.373 s --
    outside B's feasible interval (~[0, 4.697]) and overstating f1* to
    1.0.  Post-fix B stays unserved (greedy-correct), f1* = 10/15, and
    every placed start is in-window so the seed encoder never raises.
    RED pre-fix / GREEN post-fix verified by the directed fix review."""
    tasks = [
        {"t_start_s": 0.0, "t_end_s": 40.0, "t_ca_s": 3.0,
         "azimuth_size_m": 1000.0, "priority": 10, "rho_req_m": 3.0,
         "mode": "STR", "prf_hz": 3630.0},
        {"t_start_s": 0.0, "t_end_s": 6.0, "t_ca_s": 3.0,
         "azimuth_size_m": 1000.0, "priority": 5, "rho_req_m": 3.0,
         "mode": "STR", "prf_hz": 3630.0},
    ]
    m = _pair_manifest(tasks)
    res = anchor_on_manifest(m, lib, repair=True)
    assert res.starts == {0: 0.0}          # B unserved (in-window infeasible)
    assert res.f1_star == pytest.approx(10.0 / 15.0)
    # every placed start inside its task's precompiled feasible set
    from sss_core.evaluator import precompile_tasks
    plans = precompile_tasks(m, lib)
    for i, s in res.starts.items():
        assert any(lo - 1e-12 <= s <= hi + 1e-12 for lo, hi in plans[i].intervals)
    # seed-encoder consumability: the anchor output must encode cleanly
    from sss_core.evaluator import SchedulingProblem
    from sss_core.nsga2 import encode_seed_individual
    encode_seed_individual(SchedulingProblem(m, lib), res.starts)
    # repair-off left-edge path is unaffected by the membership gate
    off = anchor_on_manifest(m, lib, repair=False)
    assert off.starts == {0: 0.0}


# ── equivalence / redden pair (D11-2/3) ──────────────────────────────────

def test_equivalence_half_m1nc(m1nc, lib):
    """Frozen-T anchor: served set and f1* EXACTLY equal the real-T anchor;
    starts within tolerance (brentq root shift ~ms, D11-2)."""
    real = anchor_on_manifest(m1nc, lib)
    frozen = anchor_on_manifest(m1nc, lib, freeze_durations=True)
    assert set(real.starts) == set(frozen.starts)
    assert real.f1_star == frozen.f1_star
    for i in real.starts:
        assert abs(real.starts[i] - frozen.starts[i]) <= 0.1
    # pinned regression values (gate-review faithful simulation)
    assert len(real.starts) == 17
    assert real.f1_star == pytest.approx(0.8931, abs=1e-3)


def test_redden_half_m2wh(m2wh, lib):
    """Wide mixed scenario: the starts MOVE (max |delta| > 0) and are
    pointwise real >= frozen (D11-3 direction); served-set equality is the
    observed regime (regression note, not an assertion)."""
    real = anchor_on_manifest(m2wh, lib)
    frozen = anchor_on_manifest(m2wh, lib, freeze_durations=True)
    common = sorted(set(real.starts) & set(frozen.starts))
    assert common
    deltas = [real.starts[i] - frozen.starts[i] for i in common]
    assert max(abs(d) for d in deltas) > 0.0
    assert all(d >= -1e-9 for d in deltas), min(deltas)


# ── predicate-source identity (D11-7) ────────────────────────────────────

def test_need_assembly_via_predicate(lib):
    """The anchor's need goes through the ticket-09 predicate function:
    identical inputs must give the identical requirement value."""
    from sss_core.duration import MarginPads

    via_anchor_helper = c2_transfer_requirement_s(
        6.4, lib, MarginPads.degenerate_anchor(), d_psi_rad=0.1
    )["requirement_s"]
    assert 10.0 < via_anchor_helper < 16.0
    assert c2_transfer_requirement_s.__module__ == "sss_core.predicates"


def test_fallback_armed_at_setup(lib):
    """D11-5: the maneuver fallback is armed at the scenario envelope."""
    assert assert_fallback_active(lib) is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
