#!/usr/bin/env python3
"""Ticket 03 -- duration closed forms, margin pads, Kim SAT checker.

Assertion discipline (formula-spec v1.0.1 §7): Kim REPORTED values
(SAT 8.38/8.18/8.08/8.13 s, ``literature/fulltext/kim2021_aerospace_fulltext.txt``
line 1302) are asserted via the dual-convention band [8.0, 8.9] s + ordering
(direction) ONLY -- no tight tolerance (<5% forbidden, §7(c)).  Tight
assertions are reserved for (a) formula-INTERNAL identities and (b) the
formula-spec §6 registered derivations (table 2/3 values, themselves
double-verified by two fresh reviews at ticket 01).

Fixture naming note: ``platform_kim2021.json`` field
``sat_calibration.squint_staring_per_target_s`` is a naming relic -- the
four values are scene-level SLIDING-SPOTLIGHT SATs (Kim p.20 "images are
taken in sliding spotlight mode"); the taking-side formula chain is
formula-spec §4.1 / §6 table 3 exclusively.

Mutation evidence (inverse-assertion discipline, recorded in ticket 03):
  M1  rho_az(SLS) with A -> 1            => test_rho_az_strict_ordering RED
  M2  duration_scene_s(SLS) drops 1/A    => test_table2_point_components RED
Run log archived in the ticket body.
"""
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import (  # noqa: E402
    INTER_TASK_PAD_FRACTION_KIM,
    PAD_ALARM_THRESHOLD,
    SAT_MARGIN_KIM,
    WINDOW_TAIL_PAD_FROZEN,
    MarginPads,
    duration_point_s,
    duration_scene_s,
    duration_spt_exact_s,
    freeze_window_tail_pad,
    kim_checker_scene_sls,
    kim_eq23_theta_s1,
    measure_closure_error,
    pad_window_tail,
    scene_minus_point_delta_s,
)
from sss_core.fixture import fixture_value, load_platform_fixture  # noqa: E402
from sss_core.geometry import DerivedGeometry, look_geometry  # noqa: E402
from sss_core.modes import SPT_DESIGN_RHO_M, Mode, ModeLibrary, sec2  # noqa: E402

KIM_SAT_FOUR = [8.38, 8.18, 8.08, 8.13]  # targets 1-4, txt:1302
KIM_SAT_BAND = (8.0, 8.9)                # formula-spec §7 dual-convention band


@pytest.fixture(scope="module")
def geo() -> DerivedGeometry:
    return DerivedGeometry.from_fixture()


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


# ── derived geometry sanity (SANITY-layer band/identity assertions) ──────

def test_derived_geometry_sanity_bands(geo):
    """Formula-spec §7 derived values: band assertions only (no tight fits)."""
    _, _, r0 = look_geometry(geo.altitude_m, geo.theta_inc_deg)
    assert abs(r0 - geo.R0_m) < 1e-9
    assert abs(geo.R0_m / 1e3 - 775.43) / 775.43 < 1e-3       # §7: 775.43 km
    assert 7570.0 < geo.vs_mps < 7586.0                        # §7: 7578.05 inertial
    assert abs(geo.r0_m / 1e3 - 197.12) / 197.12 < 1e-3        # §7: 197.12 km
    assert 0.0 < geo.A < 1.0
    assert abs(geo.A - 0.202683) < 1e-6


def test_identity_theta_a_over_A_equals_lambda_over_2rho(geo):
    """Formula-spec §6 table 5: theta_a/A == lambda/(2*0.5).

    Formula-internal identity (§7(b)): A = 2*rho/D and D = lambda/theta_a
    force theta_a/A = lambda/(2 rho).  Floating-point divide/multiply round
    trips allow 1-ulp drift, hence the 1e-12 relative slack.
    """
    assert abs(geo.theta_a_rad / geo.A - geo.wavelength_m / (2.0 * geo.rho_design_m)) <= (
        1e-12 * geo.wavelength_m
    )


def test_fixture_null_fields_fail_loud():
    """Ticket-02 rule: Kim-unpublished parameters stay null and raise."""
    fx = load_platform_fixture()
    with pytest.raises(ValueError, match="prf_hz"):
        fixture_value(fx["modes"], "prf_hz")
    with pytest.raises(ValueError, match="sliding_factor_k_ladder"):
        fixture_value(fx["modes"], "sliding_factor_k_ladder")


# ── per-mode azimuth resolution ordering (formula-spec §3/§6 table 1) ────

def test_rho_az_strict_ordering(lib):
    """STR > SLS > SPT strictly, on the library design points (§6 table 1).

    Library: STR = D/2 = 2.46690 m, SLS = A*D/2 = 0.50000 m,
    SPT = lambda/(2*beta_span) = 0.30000 m.  The SPT point is the ticket-01
    library constant (0.3 m), NOT Kim's single 0.5 m design point (which
    would tie SLS == SPT and is forbidden for ordering, §6 设计约束登记).
    """
    rho_str = lib.rho_az(Mode.STR)
    rho_sls = lib.rho_az(Mode.SLS)
    rho_spt = lib.rho_az(Mode.SPT)
    assert rho_str > rho_sls > rho_spt
    assert abs(rho_str - 2.46690) < 1e-4
    assert abs(rho_sls - 0.50000) < 1e-4
    assert abs(rho_spt - SPT_DESIGN_RHO_M) < 1e-9
    assert lib.rho_ordering_strict()


def test_beta_span_spt_design_point(lib):
    """beta_span(0.3 m) = 2.9603 deg, reachable inside the +-12 deg envelope
    (formula-spec §6 table 5: beta_span <= 2 x 12 deg)."""
    assert abs(math.degrees(lib.beta_span_spt_rad) - 2.9603) < 1e-3
    assert lib.beta_span_spt_rad <= 2.0 * math.radians(12.0)


# ── point-target components (formula-spec §6 table 2, ±0.5% band) ────────

def test_table2_point_components(lib):
    """§6 table 2 point-target dwell values (spec-registered derivations).

    Columns: T(psi=0) and T(psi=12 deg) under the frozen inertial V_s.
    """
    psi12 = math.radians(12.0)
    expected = {
        (Mode.STR, 0.0): 0.643,
        (Mode.STR, psi12): 0.672,
        (Mode.SLS, 0.0): 3.172,
        (Mode.SLS, psi12): 3.315,
        (Mode.SPT, 0.0): 5.288,
        (Mode.SPT, psi12): 5.527,
    }
    for (mode, psi), ref in expected.items():
        got = duration_point_s(mode, psi, lib)
        assert abs(got - ref) / ref < 5e-3, (mode, psi, got, ref)
    # SPT point uses the exact tan-difference; table 2's linearized value
    # must agree with it to <<0.5% at the span edges.
    assert abs(duration_spt_exact_s(psi12, lib) - 5.527) / 5.527 < 5e-3


def test_scene_minus_point_component_identity(lib):
    """D03-3: T_scene - T_point == the registered delta EXACTLY (to fp)."""
    for psi_deg in (-12.0, -6.0, 0.0, 6.0, 12.0):
        psi = math.radians(psi_deg)
        for mode in Mode:
            delta = scene_minus_point_delta_s(mode, psi, lib)
            lhs = duration_scene_s(mode, psi, lib) - duration_point_s(mode, psi, lib)
            assert abs(lhs - delta) < 1e-12 * max(1.0, abs(delta)), (mode, psi_deg)


# ── analytic special cases (ticket 03: >= 2 groups, hand double-computed) ─

def test_analytic_special_zero_squint_str_scene(lib):
    """Zero-squint STR scene dwell, hand-computed expectation.

    Hand derivation: R0*theta_a = 775426.14 m * 0.0062831853 rad = 4872.15 m;
    /Vs = 4872.15/7578.057 = 0.64288 s; + Wa/Vs = 5000/7578.057 = 0.65974 s
    => 1.30262 s.
    """
    got = duration_scene_s(Mode.STR, 0.0, lib)
    assert abs(got - 1.30262) < 2e-4


def test_analytic_special_spt_symmetry_and_zero_squint(lib):
    """SPT tan-difference: even in psi_bar (symmetric geometry), exact zero-
    squint value.

    Hand derivation: T(0) = 2*R0*tan(beta_span/2)/Vs with beta_span =
    lambda/0.6 = 0.05166667 rad; tan(0.02583333) = 0.02583908;
    2*775426.14*0.02583908/7578.057 = 5.28803 s.
    """
    psi = math.radians(9.0)
    assert duration_spt_exact_s(psi, lib) == duration_spt_exact_s(-psi, lib)
    got = duration_spt_exact_s(0.0, lib)
    assert abs(got - 5.28803) < 2e-4
    # analytic zero-squint scene ratio: T_SLS / T_STR == 1/A exactly
    # (identical numerator structure at psi=0, sec^2(0)=1)
    ratio = duration_scene_s(Mode.SLS, 0.0, lib) / duration_scene_s(Mode.STR, 0.0, lib)
    assert abs(ratio - 1.0 / lib.geo.A) < 1e-12


# ── Kim full-curvature checker (formula-spec §6 table 3 registered chain) ─

def test_kim_checker_table3_registered_values(geo):
    """Checker reproduces formula-spec §6 table 3 registered derivations.

    These are spec-internal values (NOT literature fits): L_broad=48,717 m,
    dtheta=2.8695 deg, L_squint12=50,696 m, SAT@12 x1.25=8.362 s,
    SAT@0 x1.25=8.036 s.
    """
    ck0 = kim_checker_scene_sls(0.0, 0.5, geo)
    ck12 = kim_checker_scene_sls(math.radians(12.0), 0.5, geo)
    assert abs(ck0["L_m"] - 48717.0) < 5.0
    assert abs(math.degrees(ck0["dtheta_broad_rad"]) - 2.8695) < 5e-4
    assert abs(ck12["L_m"] - 50696.0) < 5.0
    assert abs(ck12["sat_margined_s"] - 8.362) < 5e-3
    assert abs(ck0["sat_margined_s"] - 8.036) < 5e-3
    # r0 chain consistency with the §7 SANITY value
    assert abs(ck0["r0_m"] / 1e3 - 197.12) / 197.12 < 1e-3


def test_kim_checker_monotonic_in_squint(geo):
    """SAT strictly increasing in |psi_bar| over the envelope (sec^2 convexity)."""
    sats = [
        kim_checker_scene_sls(math.radians(p), 0.5, geo)["sat_margined_s"]
        for p in (0.0, 3.0, 6.0, 9.0, 12.0)
    ]
    assert all(a < b for a, b in zip(sats, sats[1:]))


def test_kim_sat_fixture_band_and_direction(geo):
    """Kim Table 3 SAT four values: band + ordering assertions (§7-compliant).

    Band: each reported value inside the dual-convention coverage band
    [8.0, 8.9] s (formula-spec §7).  Direction: under the §7 attribution
    vector {t1,t2,t3,t4} = {12, 8, 0, 4} deg (assumption for attribution
    only), the model must reproduce Kim's reported ordering
    t1 > t2 > t4 > t3 (8.38 > 8.18 > 8.13 > 8.08).  No tight tolerances.
    """
    for kim_s in KIM_SAT_FOUR:
        assert KIM_SAT_BAND[0] <= kim_s <= KIM_SAT_BAND[1]
    attribution = {1: 12.0, 2: 8.0, 3: 0.0, 4: 4.0}
    predicted = {
        t: kim_checker_scene_sls(math.radians(p), 0.5, geo)["sat_margined_s"]
        for t, p in attribution.items()
    }
    # Kim order: t1 > t2 > t4 > t3
    assert predicted[1] > predicted[2] > predicted[4] > predicted[3]
    # model band over the envelope must itself sit inside the dual band
    model_vals = [
        kim_checker_scene_sls(math.radians(p), 0.5, geo)["sat_margined_s"]
        for p in (0.0, 12.0)
    ]
    assert KIM_SAT_BAND[0] <= min(model_vals) and max(model_vals) <= KIM_SAT_BAND[1]


def test_kim_checker_eq23_internal_identity(geo):
    """Eq.(23) rotating-centre chain: the two Eq.(22) forms coincide at the
    root to machine precision (D03-1: internal identity ONLY, never
    asserted against Kim values)."""
    for psi_s0_deg in (12.0, 6.0, 0.0):
        eq = kim_eq23_theta_s1(math.radians(psi_s0_deg), 0.5, geo)
        assert eq["identity_rel_gap"] < 1e-9
        # end squint descends from start without leaving the tan domain
        assert eq["theta_s1_rad"] < math.radians(psi_s0_deg) + 1e-12
        assert abs(eq["theta_s1_rad"]) < math.pi / 2.0


# ── margin pads (spec D4 layering) ────────────────────────────────────────

def test_margin_pads_layering():
    """C2 inter-task = Kim 25%; window tail = frozen measured bound;
    M?NC degenerate anchor = both zero (spec D4)."""
    std = MarginPads.standard()
    anchor = MarginPads.degenerate_anchor()
    assert std.inter_task_fraction == INTER_TASK_PAD_FRACTION_KIM == 0.25
    assert std.window_tail_fraction == WINDOW_TAIL_PAD_FROZEN
    assert anchor.inter_task_fraction == 0.0 and anchor.window_tail_fraction == 0.0
    # tail pad application inflates dwell; anchor pad is a no-op
    assert pad_window_tail(10.0, std) == pytest.approx(10.1)
    assert pad_window_tail(10.0, anchor) == 10.0


def test_window_tail_pad_frozen_from_measurement(lib):
    """Frozen pad >= measured max error and follows the registered rule
    ceil_to_0.5pct(max x 1.5); alarm threshold stays above it (spec D4
    freeze-before-run: the calibration is re-derived here as evidence)."""
    cal = freeze_window_tail_pad(lib)
    assert cal["max_abs_rel_err"] <= WINDOW_TAIL_PAD_FROZEN
    assert cal["frozen_pad"] == pytest.approx(WINDOW_TAIL_PAD_FROZEN)
    assert WINDOW_TAIL_PAD_FROZEN < PAD_ALARM_THRESHOLD
    # residual direction: at the envelope edges (where the tail pad binds)
    # the SLS closure OVERestimates the checker (conservative, feasible set
    # shrinks); the small near-broadside underestimate (-0.02%) is covered
    # by the frozen pad in both directions.
    sls_errs = [
        (abs(r["psi_bar_deg"]), r["rel_err"])
        for r in measure_closure_error(lib)
        if r["mode"] == "SLS"
    ]
    edge = [e for a, e in sls_errs if a > 11.9]
    assert min(edge) > 0.0
    assert min(e for _, e in sls_errs) > -WINDOW_TAIL_PAD_FROZEN


def test_sat_margin_constant(lib):
    """Kim's 1.25 margin is applied OUTSIDE the raw SAT (p.7/p.11)."""
    geo = lib.geo
    raw = kim_checker_scene_sls(0.0, 0.5, geo)
    assert raw["sat_margined_s"] == raw["sat_raw_s"] * SAT_MARGIN_KIM


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
