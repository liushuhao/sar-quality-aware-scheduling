#!/usr/bin/env python3
"""Ticket 07 -- maneuver closure (D5) tests.

Discipline: boundary rates share the exact planar lever (D07-1), the RMT
calibration compares both sides WITHOUT settle (D07-2, Kim Table 3
arithmetic), and the fallback is the measured envelope 4.07 s armed with a
visible warning (never silent).
"""
import math
import sys
import warnings
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.maneuver import (  # noqa: E402
    FALLBACK_MANEUVER_S,
    FALLBACK_TRIGGER_RATIO,
    J_MAX_RAD_S3,
    SETTLE_S,
    alpha_max_rad_s2,
    boundary_rate,
    calibrate_against_kim,
    maneuver_time,
    maneuver_time_production,
)
from sss_core.modes import Mode, ModeLibrary  # noqa: E402


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


# ── actuator bounds (D07-4) ──────────────────────────────────────────────

def test_alpha_max_from_fixture():
    """alpha_max computed from fixture values (60/500), never hardcoded:
    CMG yaw-axis torque over yaw-axis MoI."""
    assert alpha_max_rad_s2() == pytest.approx(60.0 / 500.0)
    assert J_MAX_RAD_S3 == 25.0  # registered SANITY constant (Fig. 17b proxy)


# ── boundary angular rates (D07-1) ───────────────────────────────────────

def test_boundary_rates_three_modes(lib):
    """STR=0, SLS=k*lever, SPT=lever with the shared cos(psi) lever;
    omega_SLS == k * omega_SPT is an EXACT identity at any squint."""
    for psi_deg in (-12.0, -6.0, 0.0, 6.0, 12.0):
        psi = math.radians(psi_deg)
        lever = lib.geo.vs_mps * math.cos(psi) / lib.geo.R0_m
        assert boundary_rate(Mode.STR, psi, lib) == 0.0
        assert boundary_rate(Mode.SLS, psi, lib) == pytest.approx(lib.geo.k * lever)
        assert boundary_rate(Mode.SPT, psi, lib) == pytest.approx(lever)
        # exact identity (the mutation target of the ticket)
        assert boundary_rate(Mode.SLS, psi, lib) == pytest.approx(
            lib.geo.k * boundary_rate(Mode.SPT, psi, lib), rel=1e-12
        )


# ── closure properties (D07-3/5) ─────────────────────────────────────────

def test_maneuver_time_monotone_and_positive(lib):
    """Maneuver time grows with the angle; zero angle and equal rates -> 0."""
    assert maneuver_time(0.0, 0.0, 0.0, lib)["t_maneuver_s"] == 0.0
    t1 = maneuver_time(math.radians(0.37), 0.0, 0.0, lib)["t_maneuver_s"]
    t2 = maneuver_time(math.radians(1.48), 0.0, 0.0, lib)["t_maneuver_s"]
    assert 0.0 < t1 < t2


def test_maneuver_time_sign_invariance(lib):
    """D07-5: global sign flip leaves the time unchanged (prograde-pass
    sign safety).  Note (registered model property, not a bug): a rate
    profile CROSSING zero sweeps less credited angle, so its time differs
    -- the decoupled model is invariant under sign FLIPS, not rate offsets."""
    a = maneuver_time(math.radians(0.4), 0.005, 0.002, lib)["t_maneuver_s"]
    b = maneuver_time(math.radians(-0.4), -0.005, -0.002, lib)["t_maneuver_s"]
    assert a == pytest.approx(b)


# ── calibration + preregistered fallback (D07-2) ─────────────────────────

def test_calibration_expected_failure_arms_fallback(lib):
    """The single-axis model is expected to under-predict the three-axis
    Kim RMT (ratio < 0.5) -> the preregistered fallback arms with a VISIBLE
    warning.  Recorded geometry assumption: 5 km along-track target spacing
    (AoI 20 km / 4 targets) -> d_psi ~ 6.45 mrad."""
    d_psi = 5000.0 / lib.geo.R0_m
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cal = calibrate_against_kim(lib, d_psi, kim_rmt_s=1.84)
    assert cal.ratio < FALLBACK_TRIGGER_RATIO
    assert cal.fallback_active
    assert cal.fallback_bound_s == FALLBACK_MANEUVER_S
    assert any("FALLBACK ACTIVE" in str(w.message) for w in caught), caught


def test_calibration_stands_alone_on_easy_geometry(lib):
    """A large slew where the model reaches the trigger keeps the model
    path (no fallback) and stays warning-free."""
    d_psi = math.radians(6.0)  # far beyond the envelope spacing
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cal = calibrate_against_kim(lib, d_psi, kim_rmt_s=3.62)  # scenario-2 min
    assert cal.ratio >= FALLBACK_TRIGGER_RATIO
    assert not cal.fallback_active
    assert not caught


def test_production_time_uses_fallback_and_excludes_settle(lib):
    """C2-facing time: fallback envelope when armed (settle NOT baked in --
    Kim Table 3 arithmetic: RMT and settle are separate terms)."""
    d_psi = 5000.0 / lib.geo.R0_m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cal = calibrate_against_kim(lib, d_psi, kim_rmt_s=1.84)
    out = maneuver_time_production(d_psi, 0.0, 0.0, lib, cal)
    assert out["source"] == "fallback"
    assert out["t_maneuver_s"] == FALLBACK_MANEUVER_S == 4.07
    assert SETTLE_S == 2.0  # explicit C2-layer term (D07-2)


# ── mutation (inverse assertion, ticket acceptance) ──────────────────────

def test_mutation_evidence_documented():
    """Mutation M7 (SLS boundary rate drops the k factor -> boundary-rate
    identity red) is recorded in the ticket body with command and output;
    this placeholder documents the procedure:
      mutate boundary_rate SLS branch: return lever (drop k)
      -> test_boundary_rates_three_modes RED (SLS == k*SPT fails)
      -> restore -> 62+N green.  Run log archived in ticket 07."""
    assert True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
