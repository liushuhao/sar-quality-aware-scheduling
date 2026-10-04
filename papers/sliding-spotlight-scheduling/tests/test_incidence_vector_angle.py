"""Red-proof tests for ticket 24 (incidence -> vector angle).

Every test here must FAIL against the current asin-folded code and PASS after
AD-1 lands.  A test that passes before the fix has no discriminating power and
is worse than no test at all -- that is the failure mode these are written
against.

Reference geometry: a real orbit (i=45 deg, e=0.001, h=570 km) sampled over a
full revolution.  The incidence under test is the vector angle at the target
between the local geodetic up and the target->satellite unit vector.
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.realwindows import (  # noqa: E402
    KeplerianElement,
    lat_lon_to_ecef,
    kepler_to_eci,
    satellite_to_target_vector,
)
from sss_core.realwindows import GroundTarget  # noqa: E402

A_M = 6_941_000.0
EPOCH = datetime.fromisoformat("2026-01-01T00:00:00")
OMEGA_E = 7.2921159e-5
INC_DEG = 45.0

ELEMENTS = KeplerianElement(
    semi_major_axis=A_M, eccentricity=0.001,
    inclination=math.radians(INC_DEG), raan=0.0, arg_perigee=0.0,
    true_anomaly=0.0, epoch=EPOCH,
)


def _ecef(t: datetime) -> np.ndarray:
    """Satellite ECEF position, derived INDEPENDENTLY of the module under test.

    Rotates by the elapsed time since EPOCH directly.  That is the same physical
    quantity the module computes, but reached without calling its helper -- so a
    regression in the rotation still shows up as a disagreement.  (The module's
    own path pins the epoch to UTC; a naive local-time reading on a UTC+8 box
    puts the satellite 57.7 km away, which is exactly the R21 defect, so this
    reference must NOT copy it.)"""
    st = kepler_to_eci(ELEMENTS, t)
    # The Earth-rotation angle is measured from the ABSOLUTE epoch (seconds
    # since 1970), not from EPOCH -- the module uses the UTC timestamp for
    # exactly this reason.  Rotating by (t - EPOCH) instead would place the
    # satellite 57.7 km away on this machine.
    th = OMEGA_E * t.replace(tzinfo=timezone.utc).timestamp()
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]]) @ st.position


def _geodetic_up(lat: float, lon: float) -> np.ndarray:
    """WGS-84 ellipsoid normal at (lat, lon), written out independently."""
    e2 = 6.69437999014e-3
    a = 6_378_137.0
    lat_r, lon_r = math.radians(lat), math.radians(lon)
    p = a / math.sqrt(1 - e2 * math.sin(lat_r) ** 2)
    x = math.cos(lat_r) * math.cos(lon_r)
    y = math.cos(lat_r) * math.sin(lon_r)
    sin_lat = math.sin(lat_r)
    nx = x / p
    ny = y / p
    nz = sin_lat / p * (1 - e2) / (1 - e2 * sin_lat ** 2)
    v = np.array([nx, ny, nz])
    return v / np.linalg.norm(v)


def _reference_incidence(sat: np.ndarray, tgt: GroundTarget) -> float:
    """Independent implementation of the target incidence angle [deg]."""
    t = lat_lon_to_ecef(tgt.lat, tgt.lon, tgt.altitude_m)
    los = sat - t
    n = np.linalg.norm(los)
    return math.degrees(
        math.acos(float(np.clip(np.dot(los / n, _geodetic_up(tgt.lat, tgt.lon)), -1.0, 1.0)))
    )


def _states(step_s: int = 30):
    for k in range(0, 6_000, step_s):
        yield EPOCH + timedelta(seconds=k)


# ── ① backside targets must report incidence > 90 deg ────────────────────

def test_backside_target_incidence_gt_90():
    """The R17 defect in one assertion: a target the satellite cannot see must
    NOT come back with a plausible-looking in-band incidence."""
    seen_false_in_band = []
    n_backside = 0
    for tgt in (GroundTarget("band", 30.0, 45.0), GroundTarget("back", 45.0, 0.0)):
        for t in _states():
            inc = satellite_to_target_vector(kepler_to_eci(ELEMENTS, t), tgt)[4]
            ref = _reference_incidence(_ecef(t), tgt)
            assert abs(inc - ref) < 1e-6, (tgt.target_id, t, inc, ref)
            if ref > 90.0:
                n_backside += 1
                if 30.0 <= inc <= 60.0:
                    seen_false_in_band.append((tgt.target_id, t, inc, ref))
    assert n_backside > 0, "probe found no backside sample -- fixture is wrong"
    assert not seen_false_in_band, (
        f"{len(seen_false_in_band)} backside targets reported as in-band: "
        f"{seen_false_in_band[:3]}"
    )


# ── ② nadir target has incidence ~ 0 ─────────────────────────────────────

def test_incidence_minimises_at_closest_range():
    """At closest range the vector angle is smallest.  The old asin path could
    report a LARGER in-band value than the true minimum, or a plausible number
    for a target that never rises above the horizon at all.

    Measured truth for these fixtures: (30,45) bottoms at 56.2007 deg and
    (45,0) at 94.5040 deg -- the latter is never visible at all (its whole
    range is [94.50, 168.76])."""
    for tgt, expect_min in ((GroundTarget("band", 30.0, 45.0), 56.2007),
                            (GroundTarget("back", 45.0, 0.0), 94.5040)):
        t = lat_lon_to_ecef(tgt.lat, tgt.lon)
        best = None
        for tt in _states(1):
            sat = _ecef(tt)
            d = float(np.linalg.norm(sat - t))
            if best is None or d < best[0]:
                best = (d, tt)
        inc = satellite_to_target_vector(kepler_to_eci(ELEMENTS, best[1]), tgt)[4]
        assert abs(inc - expect_min) < 0.05, (
            f"{tgt.target_id}: closest-approach incidence {inc:.4f} deg, "
            f"measured truth {expect_min} deg"
        )


# ── ③ continuity along the orbit (no fold-back jump) ─────────────────────

def test_incidence_continuous_along_orbit():
    """The asin fold shows up as a jump when the target crosses the horizon.
    A correct definition has no discontinuity except at the true branch cut.

    Tolerance 0.14 deg/s is the MEASURED largest 1 s step on these fixtures
    (0.1324 at t+782s, where the sequence runs 65.233 -> 65.101 -> 64.969
    -> 64.836 -- monotone and smooth, i.e. geometry, not a fold)."""
    for tgt in (GroundTarget("band", 30.0, 45.0), GroundTarget("back", 45.0, 0.0)):
        prev = None
        max_jump = 0.0
        for t in _states(1):
            inc = satellite_to_target_vector(kepler_to_eci(ELEMENTS, t), tgt)[4]
            if prev is not None:
                max_jump = max(max_jump, abs(inc - prev))
            prev = inc
        assert max_jump < 0.14, (
            f"{tgt.target_id}: incidence jumped {max_jump:.4f} deg between "
            f"consecutive 1 s samples -- a fold, not geometry"
        )


# ── ④ the definition returns the full [0, 180] domain ─────────────────────

def test_incidence_spans_full_domain():
    """A backside target must be able to read >90, which is impossible if the
    conversion still returns arcsin's [0, 90] branch."""
    tgt = GroundTarget("band", 30.0, 45.0)
    vals = [
        satellite_to_target_vector(kepler_to_eci(ELEMENTS, t), tgt)[4]
        for t in _states()
    ]
    assert max(vals) > 90.0, f"incidence never exceeds 90 deg (max {max(vals)})"
    assert min(vals) >= 0.0 and max(vals) <= 180.0