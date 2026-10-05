"""Real-orbit window geometry kernel -- FORK MANIFEST entry F-02 (ticket 16).

Source (frozen @ ``paper2-m1-baseline``, commit 60ee1e8):
  * ``src/sar_sim/generator/orbit.py``       -- Keplerian -> ECI propagation
  * ``src/sar_sim/generator/visibility.py``  -- GEOMETRY SUBSET only
  * ``src/sar_sim/generator/target.py``      -- two ECEF helpers + WGS-84 chain

Registered in ``FORK_MANIFEST.md`` BEFORE the copy (write-back clause 1:
register -> copy -> guard).  Numeric identity is asserted bit-for-bit by
``tests/test_fork_identity_realwindows.py``.

WHAT IS DELIBERATELY NOT HERE
  * ``find_visibility_windows`` / ``visibility_matrix`` -- they return the
    shared ``ObservationWindow`` and would carry a SECOND window semantics
    into the fork, against the ticket's "no private reimplementation" rule.
    Window semantics (mask verdicts, disposition counts) belong to
    ``sss_core.predicates`` alone.
  * ``EARTH_RADIUS_MEAN_M`` -- excluded by F-01; this module reads the fork's
    own ``sss_core.geometry.R_EARTH_M`` (same 6371000.0, pinned by the
    constant dual-source guard) so there is no second Earth radius.

TWO SQUINTS, AND THEY ARE NOT THE SAME QUANTITY
  The shared ``squint_deg`` returned here is the FULL along-track off-nadir
  angle at the target: measured over 600 s it spans 6.542-19.843 deg and
  barely moves within a window.  ``sss_core.geometry.squint_at(t)`` is the
  in-window excursion about ``t_ca`` (+-12 deg swing).  They cannot be
  converted into one another by any calibration -- measured on the same
  target, ``dt=0`` gives 12.749 vs 0.000 deg.

  CONSEQUENCE: the incidence leg of the window cascade consumes the vector
  ``incidence_deg`` from here; the MODE-ENVELOPE leg must consume
  ``sss_core.geometry.squint_at``, because that is the squint that drives
  ``duration_scene_s`` and the AASR bandwidth.  Feeding the vector squint
  into an envelope test is a category error, not an approximation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import numpy as np

from .geometry import R_EARTH_M

__all__ = [
    "MU_EARTH",
    "KeplerianElement",
    "ECIState",
    "solve_kepler",
    "kepler_to_eci",
    "propagate_orbit",
    "lat_lon_to_ecef",
    "compute_earth_rotation_angle",
    "eci_to_ecef_rotation",
    "satellite_to_target_vector",
    "GroundTarget",
]


# ── WGS-84 chain (required by lat_lon_to_ecef) ──────────────────────────
EARTH_EQUATORIAL_RADIUS = 6378137.0  # meters
EARTH_FLATTENING = 1.0 / 298.257223563
EARTH_POLAR_RADIUS = EARTH_EQUATORIAL_RADIUS * (1.0 - EARTH_FLATTENING)
EARTH_E2 = 1.0 - (EARTH_POLAR_RADIUS**2) / (EARTH_EQUATORIAL_RADIUS**2)


def geodetic_normal(lat: float, lon: float) -> np.ndarray:
    """Unit normal used for the incidence angle -- an APPROXIMATION, not the
    true WGS-84 ellipsoid normal.

    Ticket 24: the incidence angle is measured against THIS approximation
    rather than against the geocentric radius direction.  The two are NOT the
    same direction: they agree exactly at the equator and at the poles and
    differ by at most 0.1251 deg, the maximum sitting near lat +-60 (0.0144 deg
    at 20, 0.0414 deg at 30, 0.0960 deg at 45 -- see the measurement below).
    It is also NOT the true ellipsoid normal, which for geodetic latitude
    (lat, lon) points along
    [cos(lat)cos(lon), cos(lat)sin(lon), sin(lat)].

    Measured deviation from that true normal (audit4 C5, reproduced here):
    0 deg at the equator and poles, rising to a MAXIMUM 0.1249 deg (450 arcsec)
    near 30 deg latitude, and ~0.109 deg (393 arcsec) at 20 deg -- the dense
    domain's centre.  The previous docstring claimed "up to ~0.19 deg at
    mid-latitudes"; that figure did not reproduce and the "WGS-84 ellipsoid"
    wording overstated the caliber.

    No criterion impact: the incidence band edges are tested with margin many
    orders above this residual, and the r0 -> T_cos propagation is ~0.15%.
    Callers must treat this as a documented approximation, not an exact normal.
    """
    lat_r, lon_r = np.radians(lat), np.radians(lon)
    sin_lat, cos_lat = np.sin(lat_r), np.cos(lat_r)
    p = EARTH_EQUATORIAL_RADIUS / np.sqrt(1.0 - EARTH_E2 * sin_lat**2)
    n = np.array([
        cos_lat * np.cos(lon_r) / p,
        cos_lat * np.sin(lon_r) / p,
        sin_lat / p * (1.0 - EARTH_E2) / (1.0 - EARTH_E2 * sin_lat**2),
    ])
    return n / np.linalg.norm(n)


MU_EARTH = 3.986004418e14  # m^3/s^2


# ── types (fork-local, not copied) ───────────────────────────────────────
# Both are pure frozen dataclasses in the shared library with no method
# dependencies beyond __post_init__ validation, so defining them here severs
# the type boundary instead of dragging it across (FORK_MANIFEST F-02).

@dataclass(frozen=True)
class KeplerianElement:
    """Classical Keplerian orbital elements (fork-local, F-02)."""

    semi_major_axis: float
    eccentricity: float
    inclination: float
    raan: float
    arg_perigee: float
    true_anomaly: float
    epoch: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __post_init__(self):
        if self.eccentricity < 0 or self.eccentricity >= 1:
            raise ValueError(
                f"eccentricity must be in [0, 1), got {self.eccentricity}"
            )
        if self.semi_major_axis <= 0:
            raise ValueError(
                f"semi_major_axis must be > 0, got {self.semi_major_axis}"
            )


@dataclass(frozen=True)
class ECIState:
    """Earth-Centered Inertial state vector (fork-local, F-02)."""

    position: np.ndarray
    velocity: np.ndarray
    time: datetime

    def __post_init__(self):
        if self.position.shape != (3,):
            raise ValueError("position must be shape (3,)")
        if self.velocity.shape != (3,):
            raise ValueError("velocity must be shape (3,)")


@dataclass(frozen=True)
class GroundTarget:
    """Ground target for real-window geometry (fork-local, F-02).

    Only the fields the geometry chain actually reads: position and the
    identity.  The shared type's scheduling fields (priority, revisit) are
    not part of the geometry fork -- this paper carries priority in the
    scenario manifest, not in the target record.
    """

    target_id: str
    lat: float
    lon: float
    altitude_m: float = 0.0

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError(f"lat out of range: {self.lat}")
        if not (-180 <= self.lon <= 180):
            raise ValueError(f"lon out of range: {self.lon}")


# ── orbit.py (verbatim fork) ─────────────────────────────────────────────

def solve_kepler(M: float, e: float, tol: float = 1e-12, max_iter: int = 100) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E."""
    E = M + e * np.sin(M) + 0.5 * e**2 * np.sin(2 * M)
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        f_prime = 1.0 - e * np.cos(E)
        delta = f / f_prime
        E -= delta
        if abs(delta) < tol:
            return E
    return E


def _rgf(phi: float) -> np.ndarray:
    """Rotation about z-axis (RAAN)."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _rgi(phi: float) -> np.ndarray:
    """Rotation about x-axis (inclination)."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _rgu(phi: float) -> np.ndarray:
    """Rotation about z-axis (argument of perigee)."""
    return _rgf(phi)


def kepler_to_eci(elements: KeplerianElement, t: datetime = None) -> ECIState:
    """Convert Keplerian elements to ECI position/velocity at time t."""
    if t is None:
        t = elements.epoch
    dt = (t - elements.epoch).total_seconds()
    n = np.sqrt(MU_EARTH / elements.semi_major_axis**3)
    M = (elements.true_anomaly + n * dt) % (2 * np.pi)
    E = solve_kepler(M, elements.eccentricity)
    nu = 2.0 * np.arctan2(
        np.sqrt(1.0 + elements.eccentricity) * np.sin(E / 2.0),
        np.sqrt(1.0 - elements.eccentricity) * np.cos(E / 2.0),
    )
    r = elements.semi_major_axis * (1.0 - elements.eccentricity * np.cos(E))
    x_peri = r * np.cos(nu)
    y_peri = r * np.sin(nu)
    r_peri = np.array([x_peri, y_peri, 0.0])
    p = elements.semi_major_axis * (1.0 - elements.eccentricity**2)
    vx_peri = -np.sqrt(MU_EARTH / p) * np.sin(nu)
    vy_peri = np.sqrt(MU_EARTH / p) * (elements.eccentricity + np.cos(nu))
    v_peri = np.array([vx_peri, vy_peri, 0.0])
    R = _rgu(elements.arg_perigee) @ _rgi(elements.inclination) @ _rgf(elements.raan)
    return ECIState(position=R @ r_peri, velocity=R @ v_peri, time=t)


def propagate_orbit(
    elements: KeplerianElement,
    t_start: datetime,
    t_end: datetime,
    step: timedelta = timedelta(seconds=60),
) -> list[ECIState]:
    """Generate ECI states at regular time steps over an interval."""
    if step <= timedelta(0):
        raise ValueError("propagate_orbit requires a positive step")
    states = []
    t = t_start
    while t <= t_end:
        states.append(kepler_to_eci(elements, t))
        t += step
    return states


# ── target.py (forked helpers + WGS-84 chain) ────────────────────────────

def lat_lon_to_ecef(lat: float, lon: float, alt: float = 0.0) -> np.ndarray:
    """Convert geodetic latitude/longitude/altitude to ECEF (metres)."""
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    N = EARTH_EQUATORIAL_RADIUS / np.sqrt(1.0 - EARTH_E2 * sin_lat**2)
    x = (N + alt) * cos_lat * np.cos(lon_rad)
    y = (N + alt) * cos_lat * np.sin(lon_rad)
    z = (N * (1.0 - EARTH_E2) + alt) * sin_lat
    return np.array([x, y, z])


def compute_earth_rotation_angle(dt_seconds: float) -> float:
    """Earth rotation angle for a time offset (rad, eastward positive)."""
    OMEGA_EARTH = 7.2921159e-5  # rad/s
    return OMEGA_EARTH * dt_seconds


def eci_to_ecef_rotation(dt_seconds: float) -> np.ndarray:
    """3x3 rotation matrix from ECI to ECEF at the given time offset."""
    theta = compute_earth_rotation_angle(dt_seconds)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])


# ── visibility.py (geometry subset) ─────────────────────────────────────

def _compute_off_nadir_angle(
    sat_ecef: np.ndarray, target_ecef: np.ndarray
) -> float:
    """Angle between nadir and line-of-sight [deg].

    NOTE (ticket 24): this is the SATELLITE-CENTRED off-nadir angle.  On its
    own it carries no visibility information -- past the horizon it folds back
    and a target the satellite cannot see reads the same as one it can.  It is
    retained as a reported quantity only; incidence no longer derives from it.
    """
    los = target_ecef - sat_ecef
    nadir = -sat_ecef
    cos_off_nadir = np.dot(los, nadir) / (
        np.linalg.norm(los) * np.linalg.norm(nadir)
    )
    cos_off_nadir = np.clip(cos_off_nadir, -1.0, 1.0)
    return np.degrees(np.arccos(cos_off_nadir))


def _target_incidence_angle(
    sat_ecef: np.ndarray,
    target_ecef: np.ndarray,
    lat: float,
    lon: float,
) -> float:
    """Incidence angle at the target: the vector angle [deg] in [0, 180].

    Ticket 24 / AD-1.  Defined as the angle between the local geodetic normal
    and the target->satellite unit vector.  The previous definition chained
    the off-nadir angle through the law of sines and took an ``arcsin``, which
    returns only the [0, 90] branch: a target on the far side of the Earth
    (true incidence 134.7 deg in the recorded case) came back as a
    plausible-looking 45 deg, i.e. INSIDE the 30-60 deg acquisition band.

    Measured consequence at (45N, 0E) over one revolution: the true incidence
    never leaves [94.7, 168.6] deg -- the target is never visible at all --
    while the old path reported an in-band value at 1200 of 1200 samples.

    Why the definition rather than a horizon guard: the folded off-nadir angle
    and the near-side angle are not distinguishable from ``(off_nadir, h)``
    alone, so a bare off-nadir -> incidence converter cannot carry a
    visibility guard by construction.  Measuring the angle directly removes the
    ambiguity instead of papering over it.
    """
    los = sat_ecef - target_ecef
    norm = np.linalg.norm(los)
    if norm <= 0.0:  # pragma: no cover -- coincident positions are not physical
        return 0.0
    up = geodetic_normal(lat, lon)
    return float(np.degrees(np.arccos(np.clip(np.dot(los / norm, up), -1.0, 1.0))))


def _determine_look_direction(
    sat_ecef: np.ndarray, sat_vel_ecef: np.ndarray, target_ecef: np.ndarray
) -> str:
    """Which side of track the target lies on."""
    los = target_ecef - sat_ecef
    track = sat_vel_ecef
    nadir = -sat_ecef
    cross_track = np.cross(nadir, track)
    side = np.dot(los, cross_track)
    return "right" if side >= 0 else "left"


def satellite_to_target_vector(
    satellite_state: ECIState, target: GroundTarget
) -> tuple[np.ndarray, np.ndarray, float, float, float, str, float]:
    """Satellite-to-target vector, elevation, off-nadir, incidence, squint, look.

    The returned ``squint_deg`` is the FULL along-track off-nadir angle at
    the target -- see the module docstring for why it is NOT interchangeable
    with ``sss_core.geometry.squint_at``.
    """
    target_ecef = lat_lon_to_ecef(target.lat, target.lon, target.altitude_m)
    # ticket 24 / R21: the epoch is naive, so .timestamp() would read it in the
    # machine's LOCAL timezone -- a 120.33 deg phase error on a UTC+8 box, and
    # "byte-identical from seed" would only hold for same-timezone machines.
    # Pin the frame explicitly instead.
    if satellite_state.time.tzinfo is None:
        _t = satellite_state.time.replace(tzinfo=timezone.utc)
    else:
        _t = satellite_state.time
    R_eci_to_ecef = eci_to_ecef_rotation(_t.timestamp())
    sat_ecef = R_eci_to_ecef @ satellite_state.position
    sat_vel_ecef = R_eci_to_ecef @ satellite_state.velocity

    sat_to_target_ecef = target_ecef - sat_ecef
    distance = np.linalg.norm(sat_to_target_ecef)

    h_sat = np.linalg.norm(sat_ecef) - R_EARTH_M
    sin_elev = (h_sat**2 + 2 * R_EARTH_M * h_sat - distance**2) / (
        2 * R_EARTH_M * distance
    )
    sin_elev = np.clip(sin_elev, -1.0, 1.0)
    elevation_deg = np.degrees(np.arcsin(sin_elev))

    off_nadir_deg = _compute_off_nadir_angle(sat_ecef, target_ecef)
    # ticket 24: incidence is the target-side vector angle, NOT a conversion of
    # the off-nadir angle -- see _target_incidence_angle for why.
    incidence_deg = _target_incidence_angle(
        sat_ecef, target_ecef, target.lat, target.lon
    )
    look = _determine_look_direction(sat_ecef, sat_vel_ecef, target_ecef)

    los_unit = sat_to_target_ecef / distance
    track_dir = sat_vel_ecef / np.linalg.norm(sat_vel_ecef)
    los_along = np.dot(los_unit, track_dir)
    squint_deg = np.degrees(np.arcsin(np.clip(abs(los_along), 0.0, 1.0)))

    return (
        sat_to_target_ecef, target_ecef, elevation_deg, off_nadir_deg,
        incidence_deg, look, squint_deg,
    )