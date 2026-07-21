"""Ground target definitions and geometry utilities.
"""

import numpy as np
from datetime import datetime
from typing import List

from sar_sim.types import GroundTarget


# WGS-84 constants
EARTH_EQUATORIAL_RADIUS = 6378137.0  # meters
EARTH_FLATTENING = 1.0 / 298.257223563
EARTH_POLAR_RADIUS = EARTH_EQUATORIAL_RADIUS * (1.0 - EARTH_FLATTENING)
EARTH_E2 = 1.0 - (EARTH_POLAR_RADIUS**2) / (EARTH_EQUATORIAL_RADIUS**2)  # eccentricity^2


def lat_lon_to_ecef(lat: float, lon: float, alt: float = 0.0) -> np.ndarray:
    """Convert latitude/longitude/altitude to ECEF coordinates.

    Args:
        lat: geodetic latitude (degrees)
        lon: longitude (degrees)
        alt: altitude above ellipsoid (meters)

    Returns:
        ECEF position as (3,) numpy array (meters)
    """
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
    """Compute Earth rotation angle for time offset.

    Earth rotation rate: ~7.2921159e-5 rad/s (sidereal)

    Args:
        dt_seconds: time offset from reference (seconds)

    Returns:
        Rotation angle (radians) — positive = eastward rotation
    """
    OMEGA_EARTH = 7.2921159e-5  # rad/s
    return OMEGA_EARTH * dt_seconds


def eci_to_ecef_rotation(dt_seconds: float) -> np.ndarray:
    """3x3 rotation matrix from ECI to ECEF at given time offset.

    Args:
        dt_seconds: seconds from reference epoch

    Returns:
        3x3 rotation matrix
    """
    theta = compute_earth_rotation_angle(dt_seconds)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])


def make_targets(
    target_ids: List[str],
    lats: List[float],
    lons: List[float],
    priorities: List[int] = None,
) -> List[GroundTarget]:
    """Factory to create a list of GroundTargets from parallel arrays.

    Args:
        target_ids: list of target identifiers
        lats: list of latitudes (degrees)
        lons: list of longitudes (degrees)
        priorities: optional list of priorities [1-10]

    Returns:
        list of GroundTarget
    """
    if priorities is None:
        priorities = [5] * len(target_ids)

    if len(target_ids) != len(lats) != len(lons) != len(priorities):
        raise ValueError("All input lists must have the same length")

    return [
        GroundTarget(tid, lat, lon, pri)
        for tid, lat, lon, pri in zip(target_ids, lats, lons, priorities)
    ]
