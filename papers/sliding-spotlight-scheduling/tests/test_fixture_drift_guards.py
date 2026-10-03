#!/usr/bin/env python3
"""Drift guards for Kim-derived constants hard-referenced in code.

Final-review major fix (D3 reference-not-copy discipline): these constants
are DERIVED from fixture values; if the fixture is ever re-extracted, the
code must turn red here instead of silently drifting.  Each guard asserts
code constant == fixture value (values currently identical by audit).
"""
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.fixture import fixture_value, load_platform_fixture  # noqa: E402
from sss_core.geometry import squint_envelope_deg  # noqa: E402
from sss_core.maneuver import FALLBACK_MANEUVER_S, SETTLE_S  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.predicates import CALIBRATION_KIM_RMT_S  # noqa: E402
from sss_core.scenarios import PRF_PRODUCTION_HZ  # noqa: E402


@pytest.fixture(scope="module")
def fx() -> dict:
    return load_platform_fixture()


def test_settle_matches_fixture(fx):
    assert SETTLE_S == float(fixture_value(fx["platform"], "stabilization_time_s"))


def test_fallback_bound_matches_worst_measured_rmt(fx):
    rmt = fx["sat_calibration"]["rmt_reference"]["scenario2_rmt_per_transition_s"]["value"]
    assert FALLBACK_MANEUVER_S == max(float(v) for v in rmt)


def test_calibration_rmt_matches_fixture(fx):
    rmt = fx["sat_calibration"]["rmt_reference"]["scenario1_rmt_per_transition_s"]["value"]
    assert CALIBRATION_KIM_RMT_S == float(rmt[0])


def test_production_prf_is_a_registered_key(fx):
    keys = [float(v) for v in fixture_value(fx["modes"], "prf_hz")]
    assert PRF_PRODUCTION_HZ in keys


def test_squint_envelope_matches_fixture(fx):
    lo, hi = squint_envelope_deg()
    env = fixture_value(fx["modes"], "squint_angle_range_deg")
    assert (lo, hi) == (float(env[0]), float(env[1]))
    assert (lo, hi) == (-12.0, 12.0)  # Kim Table 2 mission range, unchanged


def test_mode_squint_envelope_matches_fixture(fx):
    """Ticket 15: the per-MODE physics envelope is fixture-registered, and
    the code constants must equal it.  This is the single-source binding for
    the former +-12 deg hardcodes."""
    from sss_core.duration import (
        SLS_MAX_SQUINT_DEG,
        SQUINT_ENVELOPE_DEG,
        mode_squint_envelope_rad,
    )

    modes = fixture_value(fx["modes"], "mode_squint_envelope_deg")
    assert float(modes["STR"]) == SQUINT_ENVELOPE_DEG
    assert float(modes["SLS"]) == SLS_MAX_SQUINT_DEG
    assert float(modes["SPT"]) == SQUINT_ENVELOPE_DEG
    assert mode_squint_envelope_rad(Mode.STR) == pytest.approx(
        math.radians(SQUINT_ENVELOPE_DEG)
    )
    assert mode_squint_envelope_rad(Mode.SLS) == pytest.approx(
        math.radians(SLS_MAX_SQUINT_DEG)
    )
    assert mode_squint_envelope_rad(Mode.SPT) == pytest.approx(
        math.radians(SQUINT_ENVELOPE_DEG)
    )


def test_seven_psi_sites_all_track_the_mode_envelope():
    """Ticket 15 acceptance item 16: every former +-12 deg site is bound to
    the envelope, checked by BEHAVIOUR rather than by grepping source."""
    from sss_core.aasr import PSI_AXIS_DEG_DEFAULT, AASRGrid
    from sss_core.duration import SLS_MAX_SQUINT_DEG, SQUINT_ENVELOPE_DEG

    lib = ModeLibrary.from_fixture()
    # (1) grid axis spans the mode envelope
    assert PSI_AXIS_DEG_DEFAULT[0] == pytest.approx(-SQUINT_ENVELOPE_DEG)
    assert PSI_AXIS_DEG_DEFAULT[-1] == pytest.approx(SQUINT_ENVELOPE_DEG)
    # (2) density preserved (0.6667 deg cells), not silently coarsened 3.75x
    cell = PSI_AXIS_DEG_DEFAULT[1] - PSI_AXIS_DEG_DEFAULT[0]
    assert cell == pytest.approx(2.0 * SQUINT_ENVELOPE_DEG / (len(PSI_AXIS_DEG_DEFAULT) - 1))
    assert cell == pytest.approx(24.0 / 36, abs=1e-3)  # the pre-ticket cell size
    # (3) mode-aware domain guard.  rho_req 2.5 routes to STR, so 45 deg is
    # inside its envelope; the same query with an SLS-routed requirement must
    # be refused past 26.9 deg.  (Using one rho_req for both would only ever
    # test whichever mode that requirement routes to.)
    grid = AASRGrid(lib)
    grid.is_feasible(2.5, math.radians(SQUINT_ENVELOPE_DEG), 0.4, 3630.0)  # no raise
    with pytest.raises(ValueError, match="envelope"):
        grid.is_feasible(0.5, math.radians(SLS_MAX_SQUINT_DEG + 1.0), 0.4, 3630.0)
    # (4) scenario window guard uses the widened bound
    from sss_core.geometry import squint_at
    from sss_core.scenarios import INTERVAL_HALF_WIDTH_S

    for interval, half in INTERVAL_HALF_WIDTH_S.items():
        assert abs(squint_at(half, 0.0, lib.geo)) <= math.radians(SQUINT_ENVELOPE_DEG), interval


def test_t_env_max_tracks_the_per_mode_envelope():
    """T_env_max must be the per-mode envelope maximum, not the old 12 deg
    platform edge (a silent return to 6.72 s would under-normalise C3/C4)."""
    from sss_core.duration import duration_scene_s, mode_squint_envelope_rad
    from sss_core.predicates import _scene_durations, _t_env_max

    lib = ModeLibrary.from_fixture()
    d = _scene_durations(lib)
    for mode, edge in d.items():
        assert edge == pytest.approx(
            duration_scene_s(mode, mode_squint_envelope_rad(mode), lib)
        )
    assert _t_env_max(lib) == pytest.approx(max(d.values()))
    assert _t_env_max(lib) == pytest.approx(10.5830, rel=1e-4)


def test_promotion_threshold_mirrors_prereg():
    """The 6.0 dB preregistration is mirrored in two modules -- all three
    registrations must stay identical (final-review minor fix)."""
    import json

    from sss_core.nsga2 import PROMOTION_SPREAD_DB
    from sss_core.verify import PROMOTION_THRESHOLD_DB

    prereg = json.loads(
        (FORK_DOMAIN / "experiments" / "promotion_prereg.json").read_text(encoding="utf-8")
    )
    threshold = float(prereg["criterion"]["threshold_db"])
    assert PROMOTION_SPREAD_DB == PROMOTION_THRESHOLD_DB == threshold


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
