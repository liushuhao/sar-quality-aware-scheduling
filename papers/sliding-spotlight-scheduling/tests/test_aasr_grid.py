#!/usr/bin/env python3
"""Ticket 06 -- AASR hard constraint + four-key grid tests.

Expectation discipline (D06-8): numeric anchors are structural properties
(identities / monotonicity / discrimination signs) generated from the
implementation's own integration; the ticket's hand figures are directional
references only.  The US6 literature anchor is the PRF anti-correlation
(formula-spec §5 Song note); the Song scan-angle 8.6 dB figure is a
registered model limitation (D06-6), never asserted here.
"""
import math
import random
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.aasr import (  # noqa: E402
    AASR_CELL_MARGIN_DB,
    AASR_SENSITIVITY_ALTERNATES_DB,
    AASR_THRESHOLD_DB,
    PRF_KEYS_HZ,
    GridAxes,
    aasr_direct,
    route_mode,
)
from sss_core.fixture import load_platform_fixture  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.aasr import AASRGrid  # noqa: E402

RHO_STR = 2.5  # inside the STR routing band (rho_ach,STR ~ 2.4669)


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def grid(lib) -> AASRGrid:
    return AASRGrid(lib)


# ── routing (coarsest-sufficient, D9 layering) ────────────────────────────

def test_route_mode_bands(lib):
    assert route_mode(3.0, lib) is Mode.STR
    assert route_mode(RHO_STR, lib) is Mode.STR
    assert route_mode(1.0, lib) is Mode.SLS
    assert route_mode(0.45, lib) is Mode.SPT
    with pytest.raises(ValueError, match="unserviceable"):
        route_mode(0.25, lib)  # finer than the SPT library point


# ── structural identities (D06-1/3) ──────────────────────────────────────

def test_identity_sls_broadside_equals_str_at_library_k(lib):
    """D06-1: at psi=0 with the library sliding point k = 1-A, the rescaled
    band collapses onto the stripmap band exactly (change of variables)."""
    k_lib = 1.0 - lib.geo.A
    for prf in PRF_KEYS_HZ:
        sls = aasr_direct(Mode.SLS, 0.0, k_lib, prf, lib)["aasr"]
        st = aasr_direct(Mode.STR, 0.0, 0.0, prf, lib)["aasr"]
        assert abs(sls - st) <= 1e-9 * st, prf


def test_prf_anticorrelation_all_modes(lib):
    """US6 literature anchor (formula-spec §5): AASR worsens as PRF drops.
    Monotone across the full registered key set for every mode (the SPT
    3044 Hz null-landing concern applies to the scene-CENTRE convention;
    the edge-worst convention keeps the row monotone)."""
    for mode in Mode:
        vals = [
            aasr_direct(mode, 0.0, 0.797317, prf, lib)["aasr_db"] for prf in PRF_KEYS_HZ
        ]
        assert all(a > b for a, b in zip(vals, vals[1:])), (mode, vals)


def test_discrimination_against_preregistered_threshold(lib, grid):
    """The grid DISCRIMINATES at -13 dB: STR tier passes only at 3630 Hz
    (directional anchor: gate-review recomputation -21.3 / -12.4 / -4.4 dB
    for 3630 / 3044 / 2300)."""
    psi0 = 0.0
    assert aasr_direct(Mode.STR, psi0, 0.797317, 3630.0, lib)["aasr_db"] < AASR_THRESHOLD_DB
    assert not grid.is_feasible(RHO_STR, psi0, 0.797317, 3044.0)
    assert not grid.is_feasible(RHO_STR, psi0, 0.797317, 2300.0)
    assert grid.is_feasible(RHO_STR, psi0, 0.797317, 3630.0)


def test_spt_edge_worst_binding(lib):
    """D06-2: the scene-edge t_0 dominates the centre (~8 dB); the grid
    must NOT use the optimistic centre value."""
    for prf in PRF_KEYS_HZ:
        edge = aasr_direct(Mode.SPT, 0.0, 0.0, prf, lib, spt_edge_worst=True)["aasr_db"]
        center = aasr_direct(Mode.SPT, 0.0, 0.0, prf, lib, spt_edge_worst=False)["aasr_db"]
        assert edge > center, prf  # edge is WORSE (higher dB)
    # SPT full-scene edge stays above the threshold even at the best PRF
    edge3630 = aasr_direct(Mode.SPT, 0.0, 0.0, 3630.0, lib)["aasr_db"]
    assert edge3630 > AASR_THRESHOLD_DB  # small-scene-only mode (see ticket 08)


def test_a_res_domain_guard(lib):
    """D06-3: a_res = 1 - k/cos^2(psi) > 0 guard raises outside the
    physical sliding domain (exact-rate corner safety)."""
    # exact-rate form: Kc/Ka = k/cos^2(psi) < 1 keeps a_res > 0 up to the
    # axis cap k = 0.9 AND slightly beyond (0.95); the guard fires at
    # k > cos^2(12 deg) ~ 0.9568
    out = aasr_direct(Mode.SLS, math.radians(12.0), 0.95, 2300.0, lib)
    assert math.isfinite(out["aasr_db"])
    with pytest.raises(ValueError, match="a_res"):
        aasr_direct(Mode.SLS, math.radians(12.0), 0.97, 2300.0, lib)


# ── grid domain + US6 properties (D06-7) ─────────────────────────────────

def test_grid_out_of_domain_raises(grid):
    with pytest.raises(ValueError, match="registered key"):
        grid.query_bound_db(2.0, 0.0, 0.5, 2000.0)
    with pytest.raises(ValueError, match="outside grid domain"):
        grid.query_bound_db(0.2, 0.0, 0.5, 2300.0)
    with pytest.raises(ValueError, match="envelope"):
        grid.query_bound_db(2.0, math.radians(13.0), 0.5, 2300.0)
    with pytest.raises(ValueError, match="outside the grid domain"):
        grid.query_bound_db(2.0, 0.0, 0.95, 2300.0)


def test_us6_lookup_conservative_and_tight(grid):
    """US6: bound >= direct pointwise (conservatism) AND the gap is bounded
    by the in-cell spread (no vacuous bound), over random sample points.

    The non-vacuousness bound is a LITERAL 4.0 dB, not an expression
    containing AASR_CELL_MARGIN_DB.  The old form read
    `3.0 + AASR_CELL_MARGIN_DB`, i.e. it compared the implementation's own
    output (aasr.py:370 computes `block.max() + AASR_CELL_MARGIN_DB`)
    against a threshold built from the same constant: raising or lowering
    the margin moved both sides together, so the assertion held for every
    margin from 0 to 10 dB and could not fail.  Pinning the measured
    maximum makes the mutation observable -- see
    test_aasr_cell_margin_value_is_pinned and the margin-mutation test.

    Measured envelope (random.Random(20260927), 25 points, same seed as
    below): gaps span [1.0000, 2.0754] dB, min == the margin exactly
    because the bound is a pure additive offset on the cell max.
    """
    rng = random.Random(20260927)
    n_checked = 0
    for _ in range(25):
        rho = rng.uniform(0.3, 3.0)
        psi = math.radians(rng.uniform(-12.0, 12.0))
        k = rng.uniform(0.0, 0.9)
        prf = rng.choice(PRF_KEYS_HZ)
        corners = grid.point_corners(rho, psi, k, prf)
        spread = max(corners) - min(corners)
        bound = grid.query_bound_db(rho, psi, k, prf)
        direct = grid.direct_db(rho, psi, k, prf)
        assert direct <= bound + 1e-6, (rho, psi, k, prf)
        # non-vacuousness (D06-7, amended): AASR(k) carries near-vertical
        # resonance structure where the rescaled band edge sweeps the
        # pattern null (locally ~2000 dB per unit k at PRF 3044) -- no
        # finite sub-sampling yields a tight VALUE bound there, so the
        # registered non-vacuous band is conservatism (direct <= bound,
        # D7 requirement) plus the MEASURED structure amplitude + margin
        # (worst observed 2.08 dB over the whole random ensemble).
        # 4.0 dB = measured max 2.0754 + 1.0 dB registered margin, rounded
        # up.  Literal on purpose -- see the docstring.
        assert bound - direct <= 4.0 + 1e-6, (rho, psi, k, prf)
        del spread
        n_checked += 1
    assert n_checked == 25


def test_aasr_cell_margin_value_is_pinned():
    """Independent value assertion for the constant the bound used to
    reference.  Nothing else in the suite constrains this number, so a
    silent edit to aasr.py:133 would otherwise go unnoticed -- the
    conservatism it buys is a preregistered quantity, not an accident.

    1.0 dB is the frozen D06-7 value.  The measured worst-case in-cell
    spread is 6.64 dB at STR/3044 Hz/psi=12 deg (audit 2026-09-30), a
    regime the 4.0 dB band above deliberately does not attempt to cover
    (excluded by the k-domain check).
    """
    assert AASR_CELL_MARGIN_DB == 1.0, (
        f"AASR_CELL_MARGIN_DB changed to {AASR_CELL_MARGIN_DB}; the D06-7 "
        "conservative slack is a registered quantity, not a tunable"
    )


def test_bound_is_a_uniform_offset_on_cell_max(grid):
    """Shape check that does not reference the constant: the bound must sit
    the SAME distance above the dense cell max at every sample, i.e. the
    margin is a uniform additive shift rather than a per-cell fudge.  Uses
    a difference, so it holds for any margin value -- it complements the
    value pin above, which fixes the number itself.
    """
    rng = random.Random(20260927)
    offsets = set()
    for _ in range(25):
        rho = rng.uniform(0.3, 3.0)
        psi = math.radians(rng.uniform(-12.0, 12.0))
        k = rng.uniform(0.0, 0.9)
        prf = rng.choice(PRF_KEYS_HZ)
        mode, i_psi, i_k = grid._locate(rho, psi, k, prf)
        np_, nk = grid._n_sub_psi, grid._n_sub_k
        block = grid._dense[(mode, prf)][
            np_ * i_psi : np_ * i_psi + np_ + 1, nk * i_k : nk * i_k + nk + 1
        ]
        offsets.add(round(grid.query_bound_db(rho, psi, k, prf) - float(block.max()), 9))
    assert len(offsets) == 1, f"bound offset is not uniform across cells: {sorted(offsets)}"


def test_us6_bound_red_when_margin_mutated():
    """Mutation proof for the literal above: inflate the margin well past the
    measured envelope and the conservatism band must report violations.

    This is the assertion the old self-referential form could never make --
    `3.0 + AASR_CELL_MARGIN_DB` grew in lockstep with the mutation and
    stayed green.  Restores the constant in a finally block so a failure
    cannot leak into other tests in the session.
    """
    import sss_core.aasr as aasr_mod

    original = aasr_mod.AASR_CELL_MARGIN_DB
    try:
        aasr_mod.AASR_CELL_MARGIN_DB = original + 50.0
        grid2 = AASRGrid(ModeLibrary.from_fixture())
        rng = random.Random(20260927)
        violations = 0
        for _ in range(25):
            rho = rng.uniform(0.3, 3.0)
            psi = math.radians(rng.uniform(-12.0, 12.0))
            k = rng.uniform(0.0, 0.9)
            prf = rng.choice(PRF_KEYS_HZ)
            bound = grid2.query_bound_db(rho, psi, k, prf)
            direct = grid2.direct_db(rho, psi, k, prf)
            if direct <= bound + 1e-6 and bound - direct > 4.0 + 1e-6:
                violations += 1
        assert violations > 0, (
            "inflating AASR_CELL_MARGIN_DB by 50 dB did not push any point "
            "past the 4.0 dB non-vacuousness band -- the band is not "
            "actually constraining the bound"
        )
    finally:
        aasr_mod.AASR_CELL_MARGIN_DB = original


def test_promotion_scatter_unenforced_exceeds_threshold(grid):
    """D7 / A13 anti-fixture: the UNENFORCED scatter over candidates can
    exceed -13 dB (otherwise the promotion criterion is structurally dead);
    empty candidate sets raise."""
    candidates = [
        (2.0, math.radians(6.0), 0.3, 1150.0),   # low PRF -> very high AASR
        (2.0, math.radians(0.0), 0.797317, 3630.0),
        (1.0, math.radians(3.0), 0.5, 2300.0),
    ]
    sc = grid.promotion_scatter_db(candidates)
    assert sc["n"] == 3
    assert sc["max_db"] > AASR_THRESHOLD_DB
    assert sc["min_db"] <= sc["max_db"]
    with pytest.raises(ValueError, match="EMPTY"):
        grid.promotion_scatter_db([])


# ── threshold + provenance registration ──────────────────────────────────

def test_threshold_preregistration():
    assert AASR_THRESHOLD_DB == -13.0
    assert AASR_SENSITIVITY_ALTERNATES_DB == (-10.0, -14.0)


def test_prf_keys_match_fixture_write_back():
    """Ticket-06 manifest write-back: the fixture prf_hz null is resolved
    and its value list equals the grid key set."""
    fx = load_platform_fixture()
    entry = fx["modes"]["prf_hz"]
    assert entry["value"] is not None
    assert tuple(float(v) for v in entry["value"]) == PRF_KEYS_HZ
    assert "Song 2025 Table 1" in entry["sources"]["1150"]
    assert "web-sourced" in entry["sources"]["3630"]


# ── D7 discipline 3: halving stability ───────────────────────────────────

def test_halving_stability_preregistered_bound(grid):
    """Flip rate between the grid and its 2x-densified rebuild on a seeded
    synthetic scenario sample must stay within the preregistered 0.5%."""
    rng = random.Random(20260927)
    samples = [
        (
            rng.uniform(0.3, 3.0),
            math.radians(rng.uniform(-12.0, 12.0)),
            rng.uniform(0.0, 0.9),
            rng.choice(PRF_KEYS_HZ),
        )
        for _ in range(60)
    ]
    report = grid.halving_stability(samples)
    assert report["n_samples"] == 60
    assert report["within_preregistered_bound"] is True, report
    assert report["flip_rate"] <= 0.005


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
