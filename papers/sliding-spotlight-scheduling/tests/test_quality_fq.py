#!/usr/bin/env python3
"""Ticket 05 -- per-mode quality metric family + f_Q aggregation tests.

Assertion anchors are the gate-review-recomputed exact values (psi=0,
R=R0, point-reference g_T, D05-2/6):
    g_T   = {STR 1.0, SLS 4.9338 (=1/A), SPT 8.2248}
    f_Q,i = {STR 0.811, SLS 19.735, SPT 54.832} m^-2
The D05-3 identity (g_T == rho_a,STR/rho_a,ach to 0.02%) and the D05-4
t-invariance of f_Q,i are asserted as registered properties.
"""
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import duration_point_s  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.quality import (  # noqa: E402
    dwell_gain,
    f_q_aggregate,
    f_q_envelope,
    f_q_per_task,
    ground_range_resolution_m,
    q_rad,
    range_bandwidth_hz,
    rasr_dynamic_range_probe,
    rasr_scene_worst,
)

MODES = (Mode.STR, Mode.SLS, Mode.SPT)
FQ_ANCHORS = {Mode.STR: 0.811, Mode.SLS: 19.735, Mode.SPT: 54.832}
GT_ANCHORS = {Mode.STR: 1.0, Mode.SLS: 4.9338, Mode.SPT: 8.2248}


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


# ── rho_rg (D05-1) ────────────────────────────────────────────────────────

def test_rho_rg_design_anchor_and_bandwidth(lib):
    """Constructive identity: rho_rg == 0.5 m at the design incidence;
    B_rg back-derived ~ 424 MHz (reviewer-recomputed 423.97, c exact SI)."""
    assert ground_range_resolution_m(lib) == pytest.approx(0.5, rel=1e-12)
    b_rg = range_bandwidth_hz(lib)
    assert abs(b_rg - 423.97e6) / 423.97e6 < 2e-3
    # incidence convention sanity: away from the design incidence the
    # textbook shape responds (shallower incidence -> longer ground
    # projection -> COARSER rho_rg)
    assert ground_range_resolution_m(lib, theta_inc_deg=40.0) > 0.5


# ── g_T (D05-2/3/4) ──────────────────────────────────────────────────────

def test_gT_point_reference_anchors(lib):
    """D05-2 point-reference anchors: STR=1, SLS=1/A exact, SPT 8.2248."""
    psi = 0.0
    assert dwell_gain(Mode.STR, psi, lib) == 1.0
    assert dwell_gain(Mode.SLS, psi, lib) == pytest.approx(1.0 / lib.geo.A, rel=1e-12)
    assert dwell_gain(Mode.SPT, psi, lib) == pytest.approx(GT_ANCHORS[Mode.SPT], rel=2e-4)
    # radiometric monotonicity: finer mode -> larger integration gain
    assert dwell_gain(Mode.SLS, psi, lib) > 1.0 < dwell_gain(Mode.SPT, psi, lib)


def test_gT_constructive_coupling_identity(lib):
    """D05-3: g_T,point == rho_a,STR/rho_a,ach to 0.02% over the envelope
    (registered counter-evidence; retention rationale in the module)."""
    for psi_deg in (-12.0, -6.0, 0.0, 6.0, 12.0):
        psi = math.radians(psi_deg)
        for mode in (Mode.SLS, Mode.SPT):
            lhs = dwell_gain(mode, psi, lib)
            rhs = lib.rho_az(Mode.STR) / lib.rho_az(mode)
            assert abs(lhs - rhs) / rhs <= 3e-4, (mode, psi_deg, lhs, rhs)


def test_gT_sls_sec2_cancellation_exact(lib):
    """D05-4: the SLS/STR ratio cancels sec^2 to machine precision across
    the squint envelope (f_Q,i t-invariance leg 1)."""
    vals = [dwell_gain(Mode.SLS, math.radians(p), lib) for p in (0.0, 6.0, 12.0)]
    assert max(vals) - min(vals) <= 1e-9 * vals[0]


# ── US5 assertions ────────────────────────────────────────────────────────

def test_us5_pixel_area_monotonicity(lib):
    """Same geometry, cross-mode pixel area strictly ordered STR>SLS>SPT."""
    rho_rg = ground_range_resolution_m(lib)
    areas = {m: rho_rg * lib.rho_az(m) for m in MODES}
    assert areas[Mode.STR] > areas[Mode.SLS] > areas[Mode.SPT]


def test_us5_fQ_dimension_and_exact_anchors(lib):
    """f_Q in m^-2; exact anchors {0.811, 19.735, 54.832} (D05-6)."""
    for mode in MODES:
        got = f_q_per_task(mode, 0.0, lib.geo.R0_m, lib)
        assert got == pytest.approx(FQ_ANCHORS[mode], rel=2e-3), mode
        assert got > 0.0
    # cross-mode spread ~1.8 orders of magnitude (A6 magnitude-ratio precheck)
    spread = math.log10(FQ_ANCHORS[Mode.SPT] / FQ_ANCHORS[Mode.STR])
    assert 1.5 < spread < 2.2


def test_us5_literature_window_kim_05m(lib):
    """US5(3): Kim Table 2 0.5 m design resolution == library rho_a,SLS
    (formula-spec §6 pinned; GF-3 'improved by the factor A' as the second
    source, §0.1/§3)."""
    assert lib.rho_az(Mode.SLS) == pytest.approx(0.5, rel=1e-6)
    assert lib.geo.rho_design_m == 0.5


# ── aggregation + exit channel ────────────────────────────────────────────

def test_fQ_mean_aggregate_and_duplication_idempotency(lib):
    """Mean over the selected set; duplication-idempotent (a SUM switch
    doubles under duplication -> this assertion goes red)."""
    vals = [f_q_per_task(m, 0.0, lib.geo.R0_m, lib) for m in MODES]
    agg = f_q_aggregate(vals)
    assert agg == pytest.approx(sum(vals) / 3.0, rel=1e-12)
    assert f_q_aggregate(vals + vals) == pytest.approx(agg, rel=1e-12)


def test_fQ_empty_selection_raises(lib):
    with pytest.raises(ValueError, match="EMPTY"):
        f_q_aggregate([])


def test_exit_channel_keeps_mode_dependence(lib):
    """Spec-D6 exit channel: with g_T disabled, q_rad degrades to the pure
    range term but f_Q stays mode-dependent via rho_a,ach (same t)."""
    psi, r = 0.0, lib.geo.R0_m
    on = {m: f_q_per_task(m, psi, r, lib, g_t_enabled=True) for m in MODES}
    off = {m: f_q_per_task(m, psi, r, lib, g_t_enabled=False) for m in MODES}
    assert len({round(v, 12) for v in off.values()}) == 3  # mode dependence alive
    # exit channel content: off = on / g_T
    for m in MODES:
        assert off[m] * dwell_gain(m, psi, lib) == pytest.approx(on[m], rel=1e-12)


def test_fQ_t_invariance_at_this_layer(lib):
    """D05-4: f_Q,i is time-invariant at the planar layer (psi enters only
    through g_T, whose SLS sec^2 cancels exactly and SPT to 0.02%)."""
    for mode in (Mode.STR, Mode.SLS):
        vals = [f_q_per_task(mode, math.radians(p), lib.geo.R0_m, lib) for p in (0.0, 12.0)]
        assert abs(vals[0] - vals[1]) / vals[0] <= 1e-9
    spt = [f_q_per_task(Mode.SPT, math.radians(p), lib.geo.R0_m, lib) for p in (0.0, 12.0)]
    assert abs(spt[0] - spt[1]) / spt[0] <= 3e-4


# ── HV reference envelope (D05-4/6, spec D6 禁令) ───────────────────────

def test_hv_envelope_all_modes_not_per_mode_best(lib):
    """HV envelope spans the mode-library reachable set over ALL tasks --
    and differs from every single-mode envelope (per-mode own-best would
    erase cross-mode differences, spec D6)."""
    psi, r = math.radians(8.0), lib.geo.R0_m
    all_vals = [f_q_per_task(m, psi, r, lib) for m in MODES]
    env = f_q_envelope(all_vals)
    assert env == (min(all_vals), max(all_vals))
    for m in MODES:
        single = [f_q_per_task(m, psi, r, lib)] * 3
        assert f_q_envelope(single) != env


def test_hv_envelope_empty_raises():
    with pytest.raises(ValueError):
        f_q_envelope([])


# ── RASR probe (D05-7) ────────────────────────────────────────────────────

def test_rasr_scene_worst_and_dynamic_range_probe(lib):
    """RASR chain computable at the Song reference PRFs; probe records the
    dynamic range with the provisional flag (mandatory ticket-06 recheck).
    """
    geo = lib.geo
    h = geo.altitude_m
    g0 = h * math.tan(math.radians(geo.theta_inc_deg))
    half = geo.scene_wa_m / 2.0
    inc = lambda r: math.acos(max(-1.0, min(1.0, h / r)))
    r_near = h / math.cos(math.atan((g0 - half) / h))
    r_far = h / math.cos(math.atan((g0 + half) / h))

    out = rasr_scene_worst(r_near, r_far, 1150.0, inc, altitude_m=h)
    assert math.isfinite(out["rasr_worst"])
    assert out["rasr_worst"] > 0.0
    assert out["rasr_worst_db"] < -20.0  # range ambiguities negligible here

    probe = rasr_dynamic_range_probe(lib)
    assert probe["provisional"] is True
    assert math.isfinite(probe["dynamic_range_db"])
    # range-ambiguity physics (distinct from the AASR PRF anti-correlation):
    # higher PRF brings the ambiguous returns CLOSER -> RASR worse
    by_prf = {}
    for row in probe["rows"]:
        by_prf.setdefault(row["prf_hz"], []).append(row["rasr_worst"])
    prfs = sorted(by_prf)
    if len(prfs) == 2:
        assert max(by_prf[prfs[0]]) <= max(by_prf[prfs[1]])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
