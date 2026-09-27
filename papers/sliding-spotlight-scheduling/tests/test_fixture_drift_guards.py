#!/usr/bin/env python3
"""Drift guards for Kim-derived constants hard-referenced in code.

Final-review major fix (D3 reference-not-copy discipline): these constants
are DERIVED from fixture values; if the fixture is ever re-extracted, the
code must turn red here instead of silently drifting.  Each guard asserts
code constant == fixture value (values currently identical by audit).
"""
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.fixture import fixture_value, load_platform_fixture  # noqa: E402
from sss_core.geometry import squint_envelope_deg  # noqa: E402
from sss_core.maneuver import FALLBACK_MANEUVER_S, SETTLE_S  # noqa: E402
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
    assert (lo, hi) == (-12.0, 12.0)  # the value the hard-coded sites assume


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
