#!/usr/bin/env python3
"""Ticket 40 -- SLS spectral factor switches to (yi) rotation-centre
semantics: a_res = 1 - k = A at EVERY squint (A-CROSS verdict
a-cross-verdict-20261007.md, three adversarial tracks + closure round,
user-approved 2026-10-07 22:08).

Oracle discipline (D06-8 style): the reading tests replicate the shipped
pattern integral with an EXTERNALLY supplied spectral factor, so they pin
the K_c/K_a derivation and NOT the integration plumbing.  psi = 0 is the
discrimination anchor where the old linearised law
(a_res = 1 - k/cos^2(psi), code pre-ticket-40) and the new law coincide
bit-exact; 12/26 deg is where the old law diverges (0.1667 / 0.0130 vs
A = 0.2027), so those points are RED on the pre-ticket-40 code.
"""
import dataclasses
import math
import sys
from pathlib import Path

import numpy as np
import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.aasr import (  # noqa: E402
    N_ALIASES,
    N_INTEGRATION_POINTS,
    _pattern,
    aasr_direct,
)
from sss_core.modes import Mode, ModeLibrary  # noqa: E402


@pytest.fixture(scope="module")
def lib():
    return ModeLibrary.from_fixture()


def _lib_with(lib, **geo_overrides):
    """Same helper contract as test_ticket35: swap geometry fields only."""
    return dataclasses.replace(
        lib, geo=dataclasses.replace(lib.geo, **geo_overrides)
    )


def _oracle_aasr_db(mode, psi, a_res_factor, prf, lib):
    """Midpoint-rule replication of the shipped integral with the spectral
    factor supplied from OUTSIDE the production K_c/K_a derivation."""
    geo = lib.geo
    vs = geo.vs_mps
    b_d = lib.bandwidth_d_hz(mode, psi)
    f = -b_d / 2.0 + (np.arange(N_INTEGRATION_POINTS) + 0.5) * (b_d / N_INTEGRATION_POINTS)
    ar = a_res_factor * f
    den = float(np.sum(_pattern(ar, vs, geo.D_m) ** 2)) * (b_d / N_INTEGRATION_POINTS)
    num = 0.0
    for m in range(-N_ALIASES, N_ALIASES + 1):
        if m == 0:
            continue  # C&W m!=0 convention (formula-spec §8.13-2)
        num += float(np.sum(_pattern(ar + m * prf, vs, geo.D_m) ** 2)) * (
            b_d / N_INTEGRATION_POINTS
        )
    ratio = num / den
    return 10.0 * math.log10(ratio) if ratio > 0 else float("-inf")


def test_sls_reading_matches_constant_factor_oracle(lib):
    """a_res(SLS, psi) == A at 0/12/26 deg -- the ticket-40 core claim."""
    A_val, k_lib = lib.geo.A, lib.geo.k
    for psi_deg in (0.0, 12.0, 26.0):
        psi = math.radians(psi_deg)
        got = aasr_direct(Mode.SLS, psi, k_lib, 3630.0, lib)["aasr_db"]
        want = _oracle_aasr_db(Mode.SLS, psi, A_val, 3630.0, lib)
        assert got == pytest.approx(want, abs=1e-9), (psi_deg, got, want)


def test_str_readings_untouched_by_sls_change(lib):
    """STR shares the band-integral form with a_res = 1 and never enters
    the SLS branch: readings must equal the oracle at that factor.  (SPT
    uses the collapsed Eq.(7) form with no band integral -- out of this
    oracle's scope and pinned by test_spt_edge_worst_binding.)"""
    for psi_deg in (0.0, 12.0):
        psi = math.radians(psi_deg)
        got = aasr_direct(Mode.STR, psi, lib.geo.k, 2300.0, lib)["aasr_db"]
        want = _oracle_aasr_db(Mode.STR, psi, 1.0, 2300.0, lib)
        assert got == pytest.approx(want, abs=1e-9), (psi_deg, got, want)


def test_no_squint_domain_boundary_for_any_sliding_k(lib):
    """(yi) semantics: a_res = 1 - k > 0 for every psi and every k < 1, so
    aasr_direct(SLS, .) never raises inside the envelope -- including the
    lowered-A library whose OLD acos(sqrt(k)) boundary (18.435 deg at
    A = 0.10) sat inside the guard (red on pre-ticket-40 code)."""
    lib_low = _lib_with(lib, A=0.10)
    for l in (lib, lib_low):
        for psi_deg in (0.0, 12.0, 18.5, 26.0, 26.8):
            out = aasr_direct(Mode.SLS, math.radians(psi_deg), l.geo.k, 2300.0, l)
            assert math.isfinite(out["aasr_db"]), (psi_deg, l.geo.A)


def test_degenerate_k_ge_one_raises(lib):
    """The domain guard survives at the family corner only: k >= 1 leaves
    the sliding family (spotlight limit / beyond), a_res = 1 - k <= 0."""
    assert math.isfinite(aasr_direct(Mode.SLS, 0.0, 0.9999, 2300.0, lib)["aasr_db"])
    with pytest.raises(ValueError, match="a_res"):
        aasr_direct(Mode.SLS, 0.0, 1.0, 2300.0, lib)


def test_grid_dense_table_matches_constant_factor_oracle(lib):
    """The four-key grid's SLS dense cells must be the NEW-law values:
    cell(i, j) == oracle(SLS, psi_dense[i], 1 - k_dense[j]) -- white-box
    against grid._dense, red on pre-ticket-40 code wherever psi is large."""
    from sss_core.aasr import AASRGrid, GridAxes, PRF_KEYS_HZ

    prf = 2300.0
    grid = AASRGrid(lib, axes=GridAxes(rho_req=(0.5, 3.0), psi_deg=(0.0, 12.0, 26.0), k=(0.0, lib.geo.k)))
    table = grid._dense[(Mode.SLS, prf)]
    psi_dense = grid._psi_dense
    k_dense = grid._k_dense
    checked = 0
    for i in range(0, len(psi_dense), 4):  # sample the dense psi axis
        for j in (0, len(k_dense) - 1):
            want = _oracle_aasr_db(Mode.SLS, math.radians(float(psi_dense[i])), 1.0 - float(k_dense[j]), prf, lib)
            got = float(table[i, j])
            assert got == pytest.approx(want, abs=1e-6), (i, j, psi_dense[i], k_dense[j], got, want)
            checked += 1
    assert checked >= 4
    assert prf in PRF_KEYS_HZ
