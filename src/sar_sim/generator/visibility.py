"""Satellite-to-target visibility computation.

Determines when a satellite can observe a ground target,
computing access windows, optimal observation times,
off-nadir angles, incidence angles, and side-looking direction.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from sar_sim.types import (
    ECIState,
    GroundTarget,
    ObservationWindow,
    KeplerianElement,
    SARInstrument,
)
from sar_sim.generator.orbit import propagate_orbit, kepler_to_eci
from sar_sim.generator.target import (
    lat_lon_to_ecef,
    eci_to_ecef_rotation,
    EARTH_EQUATORIAL_RADIUS,
)


def _compute_off_nadir_angle(
    sat_ecef: np.ndarray, target_ecef: np.ndarray
) -> float:
    """Compute off-nadir angle: angle between nadir and line-of-sight.

    Nadir = vector from satellite to Earth center = -sat_ecef
    Off-nadir = angle between nadir and satellite-to-target vector.

    Returns:
        off-nadir angle in degrees
    """
    los = target_ecef - sat_ecef  # line-of-sight, satellite → target
    nadir = -sat_ecef              # satellite → Earth center

    cos_off_nadir = np.dot(los, nadir) / (
        np.linalg.norm(los) * np.linalg.norm(nadir)
    )
    cos_off_nadir = np.clip(cos_off_nadir, -1.0, 1.0)
    return np.degrees(np.arccos(cos_off_nadir))


def _off_nadir_to_incidence(
    off_nadir_deg: float, sat_altitude_m: float
) -> float:
    """Convert off-nadir angle to incidence angle using Earth curvature.

    Off-nadir (η) is the satellite-centered angle between nadir and LOS.
    Incidence (θ_i) is the target-centered angle between local vertical and LOS.

    From the law of sines in the satellite-center-target triangle:
        sin(θ_i) = (R_e + h) / R_e · sin(η)

    Args:
        off_nadir_deg: off-nadir angle in degrees
        sat_altitude_m: satellite altitude above Earth surface in meters

    Returns:
        incidence angle in degrees
    """
    if off_nadir_deg <= 0.0:
        return 0.0

    R_e = EARTH_EQUATORIAL_RADIUS
    R = R_e + sat_altitude_m
    ratio = R / R_e

    sin_incidence = ratio * np.sin(np.radians(off_nadir_deg))
    sin_incidence = np.clip(sin_incidence, -1.0, 1.0)
    return np.degrees(np.arcsin(sin_incidence))


def _determine_look_direction(
    sat_ecef: np.ndarray, sat_vel_ecef: np.ndarray, target_ecef: np.ndarray
) -> str:
    """Determine whether target is on left or right side of track.

    In ECEF frame:
      - track direction ≈ satellite velocity
      - nadir = -sat_ecef (from satellite to Earth center)
      - cross-track = track × nadir (right side of track by convention)
      - look_sign = dot(los, cross-track): positive = right, negative = left

    Returns:
        "left" or "right"
    """
    los = target_ecef - sat_ecef
    track = sat_vel_ecef
    nadir = -sat_ecef

    # Cross-track: right side of satellite track
    # Standard coordinate frame: +Z = nadir, +X = track, +Y = cross-track (right)
    # Y = Z × X = nadir × track
    cross_track = np.cross(nadir, track)

    side = np.dot(los, cross_track)
    if side >= 0:
        return "right"
    else:
        return "left"


def satellite_to_target_vector(
    satellite_state: ECIState, target: GroundTarget
) -> tuple[np.ndarray, np.ndarray, float, float, float, str, float]:
    """Compute the satellite-to-target vector, elevation, off-nadir, incidence, squint, and look direction.

    Args:
        satellite_state: ECI position/velocity at a given time
        target: ground target

    Returns:
        (sat_to_target_ecef, target_ecef, elevation_deg, off_nadir_deg, incidence_deg, look_direction, squint_deg)
    """
    # Target position in ECEF
    target_ecef = lat_lon_to_ecef(target.lat, target.lon)

    # ECI → ECEF rotation for this timestep
    R_eci_to_ecef = eci_to_ecef_rotation(
        satellite_state.time.timestamp()
    )

    # Satellite position and velocity in ECEF
    sat_ecef = R_eci_to_ecef @ satellite_state.position
    sat_vel_ecef = R_eci_to_ecef @ satellite_state.velocity

    # Vector from satellite to target (ECEF)
    sat_to_target_ecef = target_ecef - sat_ecef
    distance = np.linalg.norm(sat_to_target_ecef)

    # Elevation angle
    h_sat = np.linalg.norm(sat_ecef) - EARTH_EQUATORIAL_RADIUS
    sin_elev = (h_sat**2 + 2 * EARTH_EQUATORIAL_RADIUS * h_sat - distance**2) / (
        2 * EARTH_EQUATORIAL_RADIUS * distance
    )
    sin_elev = np.clip(sin_elev, -1.0, 1.0)
    elevation_deg = np.degrees(np.arcsin(sin_elev))

    # Off-nadir angle (satellite-centered)
    off_nadir_deg = _compute_off_nadir_angle(sat_ecef, target_ecef)

    # Incidence angle (target-centered) — convert using Earth curvature
    incidence_deg = _off_nadir_to_incidence(off_nadir_deg, h_sat)

    # Look direction
    look = _determine_look_direction(sat_ecef, sat_vel_ecef, target_ecef)

    # Squint angle (along-track component of LOS)
    # Squint = arcsin(|los_along| / |los|)
    los_unit = sat_to_target_ecef / distance
    track_dir = sat_vel_ecef / np.linalg.norm(sat_vel_ecef)
    los_along = np.dot(los_unit, track_dir)
    squint_deg = np.degrees(np.arcsin(np.clip(abs(los_along), 0.0, 1.0)))

    return sat_to_target_ecef, target_ecef, elevation_deg, off_nadir_deg, incidence_deg, look, squint_deg


def _check_geometric_constraints(
    elevation: float,
    incidence: float,
    look: str,
    instrument: SARInstrument,
    squint: float = 0.0,
) -> bool:
    """Check if a timestep's geometry passes the SAR instrument constraints.

    Args:
        elevation: elevation angle (degrees)
        incidence: incidence angle at the target (degrees)
        look: "left" or "right"
        instrument: SAR instrument configuration
        squint: squint angle (degrees) — along-track LOS component

    Returns:
        True if all constraints are satisfied
    """
    if elevation < instrument.min_elevation:
        return False
    if not (instrument.incidence_min <= incidence <= instrument.incidence_max):
        return False
    if look == "left" and not instrument.can_look_left:
        return False
    if look == "right" and not instrument.can_look_right:
        return False
    if squint > instrument.max_squint_deg:
        return False
    return True


def find_visibility_windows(
    elements: KeplerianElement,
    satellite_id: str,
    target: GroundTarget,
    t_start: datetime,
    t_end: datetime,
    step: timedelta = timedelta(seconds=30),
    instrument: Optional[SARInstrument] = None,
) -> List[ObservationWindow]:
    """Find all visibility windows between a satellite and ground target.

    A visibility window is a continuous period where the satellite
    is above the minimum elevation angle AND satisfies SAR-specific
    geometric constraints (incidence angle range, side-looking direction).

    Args:
        elements: satellite orbital elements
        satellite_id: identifier for this satellite
        target: ground target
        t_start: search start time
        t_end: search end time
        step: time discretization step
        instrument: SAR instrument configuration. If None, uses
            permissive default (incidence 0–90°, both-side looking).

    Returns:
        list of ObservationWindow
    """
    if instrument is None:
        instrument = SARInstrument.permissive()

    states = propagate_orbit(elements, t_start, t_end, step)
    windows = []

    in_window = False
    window_start = None
    best_elev = -999.0
    best_off_nadir = 0.0
    best_look = "right"
    best_time = None

    for state in states:
        _, _, elev, off_nadir, incidence, look, squint = satellite_to_target_vector(state, target)

        if _check_geometric_constraints(elev, incidence, look, instrument, squint):
            if not in_window:
                # Start of new window
                in_window = True
                window_start = state.time
                best_elev = elev
                best_off_nadir = off_nadir
                best_look = look
                best_time = state.time
            else:
                # Continue window — update best if this point is better
                # Use elevation as primary quality metric (higher = better)
                if elev > best_elev:
                    best_elev = elev
                    best_off_nadir = off_nadir
                    best_look = look
                    best_time = state.time
        else:
            if in_window:
                # End of window
                in_window = False
                windows.append(
                    ObservationWindow(
                        satellite_id=satellite_id,
                        target_id=target.target_id,
                        t_start=window_start,
                        t_end=state.time,
                        t_optimal=best_time,
                        elevation=best_elev,
                        off_nadir_angle=best_off_nadir,
                        look_direction=best_look,
                    )
                )

    # Close final window if still open
    if in_window:
        windows.append(
            ObservationWindow(
                satellite_id=satellite_id,
                target_id=target.target_id,
                t_start=window_start,
                t_end=t_end,
                t_optimal=best_time,
                elevation=best_elev,
                off_nadir_angle=best_off_nadir,
                look_direction=best_look,
            )
        )

    return windows


def visibility_matrix(
    elements_list: List[KeplerianElement],
    satellite_ids: List[str],
    targets: List[GroundTarget],
    t_start: datetime,
    t_end: datetime,
    step: timedelta = timedelta(seconds=60),
    instruments: Optional[Dict[str, SARInstrument]] = None,
) -> dict:
    """Compute full visibility matrix: all windows for all sat-target pairs.

    Args:
        elements_list: orbital elements for each satellite
        satellite_ids: satellite identifiers
        targets: ground targets
        t_start, t_end: search interval
        step: time resolution
        instruments: optional dict mapping satellite_id → SARInstrument.
            Satellites without an entry use permissive default (0–90°, both-side).

    Returns:
        dict mapping (satellite_id, target_id) -> list of ObservationWindow
    """
    if instruments is None:
        instruments = {}

    matrix = {}
    for elements, sat_id in zip(elements_list, satellite_ids):
        instr = instruments.get(sat_id)
        for target in targets:
            windows = find_visibility_windows(
                elements, sat_id, target, t_start, t_end, step, instr
            )
            matrix[(sat_id, target.target_id)] = windows
    return matrix
