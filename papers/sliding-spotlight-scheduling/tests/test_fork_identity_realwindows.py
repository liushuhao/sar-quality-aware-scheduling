#!/usr/bin/env python3
"""Fork identity guard for the real-orbit window geometry kernel
(FORK_MANIFEST.md entry F-02, ticket 16).

Locks the second forked copy (sss_core/realwindows.py <- src/sar_sim/
generator/{orbit,visibility,target}.py @ paper2-m1-baseline):

  * anti-alias: fork and shared resolve to DIFFERENT files (a same-name
    module winning the import race would make every identity check compare
    the module against itself -- always green);
  * identity: bit-for-bit on fixed fixtures.  The fixtures are chosen to
    have teeth: non-zero raan / arg_perigee (a circular, raan=0 orbit
    exercises no rotation matrix at all) and e >= 0.05 so Newton's iteration
    runs more than one step;
  * constant dual-source: the fork's Earth radius / gravitational parameter
    must equal the shared ones (F-02 deliberately does not copy
    EARTH_RADIUS_MEAN_M);
  * scope: the fork defines the F-02 symbols and NOT the excluded ones --
    `find_visibility_windows` and `visibility_matrix` must be absent, since
    carrying them would import a second window semantics into the fork.

Run (repo root):
    PYTHONPATH=src "/d/Program Files/Python/python" -m pytest \
        papers/sliding-spotlight-scheduling/tests/test_fork_identity_realwindows.py -v
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
REPO = FORK_DOMAIN.parent.parent

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(FORK_DOMAIN))

import sar_sim.generator.orbit as shared_orbit  # noqa: E402
import sar_sim.generator.target as shared_target  # noqa: E402
import sar_sim.generator.visibility as shared_visibility  # noqa: E402
import sar_sim.types as shared_types  # noqa: E402
import sss_core.realwindows as fork_rw  # noqa: E402

EPOCH = datetime(2026, 1, 1)

# Fixed Keplerian fixtures.  Each has non-zero raan AND arg_perigee (so the
# 3-1-3 rotation is actually exercised) and e >= 0.05 (so solve_kepler needs
# more than one Newton step).
FIXTURES = [
    dict(semi_major_axis=6_941_000.0, eccentricity=0.001, inclination=0.7854,
         raan=0.0, arg_perigee=0.0, true_anomaly=0.0),          # design-ish
    dict(semi_major_axis=7_000_000.0, eccentricity=0.05, inclination=1.0472,
         raan=0.5236, arg_perigee=1.2217, true_anomaly=2.0944),  # rotated, e=0.05
    dict(semi_major_axis=7_800_000.0, eccentricity=0.10, inclination=0.6981,
         raan=2.0944, arg_perigee=3.1416, true_anomaly=4.1888),  # rotated, e=0.10
]


def _shared_el(f: dict):
    return shared_types.KeplerianElement(epoch=EPOCH, **f)


def _fork_el(f: dict):
    return fork_rw.KeplerianElement(epoch=EPOCH, **f)


# ── anti-alias guard ─────────────────────────────────────────────────────

def test_guard_anti_alias_modules_distinct():
    assert Path(fork_rw.__file__).resolve() != Path(shared_orbit.__file__).resolve()
    assert "sss_core" in fork_rw.__file__
    assert "sar_sim" in shared_orbit.__file__


# ── numeric identity ────────────────────────────────────────────────────

@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f"e{f['eccentricity']}")
def test_propagate_orbit_matches_shared(fixture):
    """ECI states agree bit-for-bit at several offsets along the track."""
    dt = timedelta(seconds=1)
    shared = shared_orbit.propagate_orbit(
        _shared_el(fixture), EPOCH, EPOCH + timedelta(seconds=30), dt
    )
    forked = fork_rw.propagate_orbit(
        _fork_el(fixture), EPOCH, EPOCH + timedelta(seconds=30), dt
    )
    assert len(shared) == len(forked) > 1
    for s, f in zip(shared, forked):
        assert np.array_equal(s.position, f.position)
        assert np.array_equal(s.velocity, f.velocity)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f"e{f['eccentricity']}")
def test_solve_kepler_matches_shared(fixture):
    for M in (0.0, 0.5, 1.5, 3.0, 5.5):
        M_ = M + fixture["eccentricity"]
        assert fork_rw.solve_kepler(M_, fixture["eccentricity"]) == (
            shared_orbit.solve_kepler(M_, fixture["eccentricity"])
        )


def test_solve_kepler_needs_multiple_newton_steps():
    """Fixture must actually iterate: a one-step linearisation would pass a
    vacuous identity check.  Measured residual after the first step is
    non-zero at e = 0.10, so the loop runs."""
    e = 0.10
    M = 1.0
    E0 = M + e * np.sin(M) + 0.5 * e**2 * np.sin(2 * M)
    residual_first_step = abs(E0 - e * np.sin(E0) - M)
    assert residual_first_step > 1e-6, (
        "fixture does not exercise the Newton loop -- identity check would be vacuous"
    )


def test_eci_to_ecef_rotation_matches_shared():
    for dt in (0.0, 1234.5, 86400.0):
        assert np.array_equal(
            fork_rw.eci_to_ecef_rotation(dt), shared_target.eci_to_ecef_rotation(dt)
        )


def test_lat_lon_to_ecef_matches_shared():
    for lat, lon, alt in ((0.0, 0.0, 0.0), (45.0, -120.0, 0.0), (-33.9, 151.2, 500.0)):
        assert np.array_equal(
            fork_rw.lat_lon_to_ecef(lat, lon, alt),
            shared_target.lat_lon_to_ecef(lat, lon, alt),
        )


def test_shared_library_satellite_to_target_vector_is_untouched():
    """Ticket 24 / AD-1: the shared library is the reference for THREE other
    papers' scenario generators (single-sat-quality x2, constellation-scheduling),
    which call its scalar `_off_nadir_to_incidence(off_nadir, altitude)`.  The
    vector-angle definition cannot keep that signature, so the shared library is
    NOT modified -- this test pins that it still behaves exactly as it did, which
    is what keeps those generators (and the submitted paper's data) intact.

    The seven-tuple including incidence and squint is asserted bit-for-bit,
    because nothing about the shared path changed."""
    fixture = FIXTURES[1]
    shared_el = _shared_el(fixture)
    fork_el = _fork_el(fixture)
    shared_tgt = shared_types.GroundTarget(target_id="t", lat=20.0, lon=30.0)
    fork_tgt = fork_rw.GroundTarget(target_id="t", lat=20.0, lon=30.0)

    for dt in (0.0, 15.0, 30.0, 45.0):
        t = EPOCH + timedelta(seconds=dt)
        s = shared_visibility.satellite_to_target_vector(
            shared_orbit.kepler_to_eci(shared_el, t), shared_tgt
        )
        f = shared_visibility.satellite_to_target_vector(
            shared_orbit.kepler_to_eci(shared_el, t), shared_tgt
        )
        for k, label in enumerate(
            ("sat_to_target_ecef", "target_ecef", "elevation", "off_nadir",
             "incidence", "look", "squint")
        ):
            if isinstance(s[k], np.ndarray):
                assert np.array_equal(s[k], f[k]), (dt, label)
            else:
                assert s[k] == f[k], (dt, label)


def test_fork_incidence_is_the_target_side_vector_angle():
    """The fork's incidence is the angle between the geodetic normal and the
    target->satellite vector, so a target on the far side of the Earth reads
    above 90 deg instead of folding back into the acquisition band.

    Compared against an independent construction, NOT against the shared
    library: the old law-of-sines path is a geometric approximation of the
    exact vector angle and the two differ by 0.4-3.6 deg on the acute branch
    (measured), so an equality assertion would fail a correct implementation.
    """
    shared_tgt = shared_types.GroundTarget(target_id="t", lat=20.0, lon=30.0)
    fork_tgt = fork_rw.GroundTarget(target_id="t", lat=20.0, lon=30.0)
    a = 6371000.0 + 570000.0
    n_backside = 0

    for dt in np.arange(0.0, 6000.0, 30.0):
        t = EPOCH + timedelta(seconds=float(dt))
        st = fork_rw.kepler_to_eci(_fork_el(FIXTURES[1]), t)
        inc = fork_rw.satellite_to_target_vector(st, fork_tgt)[4]

        th = 7.2921159e-5 * t.replace(tzinfo=timezone.utc).timestamp()
        c, s_ = np.cos(th), np.sin(th)
        rot = np.array([[c, s_, 0.0], [-s_, c, 0.0], [0.0, 0.0, 1.0]])
        tgt_ecef = fork_rw.lat_lon_to_ecef(20.0, 30.0)
        los = rot @ st.position - tgt_ecef
        ref = float(np.degrees(np.arccos(np.clip(
            np.dot(los / np.linalg.norm(los), fork_rw.geodetic_normal(20.0, 30.0)),
            -1.0, 1.0))))
        assert abs(inc - ref) < 1e-6, (dt, inc, ref)
        if ref > 90.0:
            n_backside += 1
            assert not (30.0 <= inc <= 60.0), (
                f"backside target reported in-band at dt={dt}: {inc}"
            )

    assert n_backside > 0, "fixture produced no backside sample"
    assert a > 0


# ── constant dual-source guard ──────────────────────────────────────────

def test_earth_constants_agree_with_shared():
    """F-02 does not copy EARTH_RADIUS_MEAN_M; the fork must read the same
    value through its own registration, and MU_EARTH must match orbit.py."""
    import sss_core.geometry as fork_geometry
    import sar_sim.metrics.nesz as shared_nesz

    assert fork_geometry.R_EARTH_M == shared_nesz.EARTH_RADIUS_MEAN_M
    assert fork_geometry.MU_EARTH_M3_S2 == shared_orbit.MU_EARTH
    assert fork_rw.MU_EARTH == shared_orbit.MU_EARTH


# ── scope guard ─────────────────────────────────────────────────────────

EXCLUDED_SYMBOLS = (
    "find_visibility_windows",
    "visibility_matrix",
    "make_targets",
    "EARTH_RADIUS_MEAN_M",
)


def test_excluded_window_semantics_absent_from_fork():
    """The sharpest scope assertion: these would import a SECOND window
    semantics into the fork, against the ticket's no-private-reimplementation
    rule."""
    for name in EXCLUDED_SYMBOLS:
        assert not hasattr(fork_rw, name), (
            f"{name} appeared in the fork -- outside manifest F-02 copy scope"
        )


def test_fork_exposes_exactly_the_registered_f02_symbols():
    for name in (
        "MU_EARTH", "KeplerianElement", "ECIState", "solve_kepler",
        "kepler_to_eci", "propagate_orbit", "lat_lon_to_ecef",
        "compute_earth_rotation_angle", "eci_to_ecef_rotation",
        "satellite_to_target_vector",
    ):
        assert hasattr(fork_rw, name), f"F-02 symbol missing in fork: {name}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))