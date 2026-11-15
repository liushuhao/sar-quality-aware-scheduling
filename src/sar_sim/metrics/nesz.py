"""NESZ (Noise Equivalent Sigma Zero) quality metric for SAR scheduling.

Implements the incidence-angle-dependent NESZ model from the problem
formalization (Eq. 2):

    NESZ(θ) = K_NESZ / cos³θ

where θ is the incidence angle derived from the full 3-D off-nadir angle
(the squint/along-track component is contained in θ, so no separate
squint factor is needed; see RDR-066).
The normalized quality score (diagnostic only, NOT used as optimization target):

    q(θ) = cos³θ / cos³θ_ref

The actual optimization targets (O2, O3) use separate formulas:
  f2 = Σ sinθ_elev,i · cosψ_sq,i     geometric resolution (elevation-plane incidence)
  f3 = Σ cos³ξ_i                      NESZ radiometric quality (ξ = full off-nadir, R³ factor)

f3 = cos³ξ equals cos³θ_elev·cos³ψ (elevation-plane incidence × squint) by
the exact identity cosθ_elev·cosψ = cosξ; using the full off-nadir angle
avoids double-counting the squint contribution. f2 uses the elevation-plane
angle θ_elev for the cross-track ground-range projection (see RDR-066).
"""

import numpy as np
from typing import List

from sar_sim.types import ScheduledObservation


# ─── Physical constants / defaults ───────────────────────────────────────

# Default K_NESZ: calibrated to Sentinel-1 IW mode.
#   NESZ(θ_ref=30°) = K_NESZ / cos³30° ≈ 4.1e-3 / 0.6495 ≈ 6.3e-3
#   → 10·log₁₀(6.3e-3) ≈ −22 dB  (matches Sentinel-1 IW specification)
# For ICEYE sensitivity analysis, model users should calibrate K_NESZ
# separately (ICEYE X-band NESZ ≈ −18 to −20 dB at 30°).
_K_NESZ_DEFAULT = 4.1e-3  # linear (≈ −23.9 dB at nadir; −22 dB NESZ at 30°)

# Reference incidence angle for normalization (radians).  30° is the
# canonical reference used in Sentinel-1 and ICEYE product documentation.
_THETA_REF_DEG = 30.0
_THETA_REF = np.radians(_THETA_REF_DEG)
_COS3_THETA_REF = np.cos(_THETA_REF) ** 3  # cached for q(θ) computation


def elevation_to_off_nadir(elevation_deg: float) -> float:
    """Convert elevation (degrees above horizon) to incidence angle (radians from nadir).

    For flat-Earth approximation: θ_incidence = 90° − elevation.
    This matches the convention in the formalization where θ increases
    away from nadir.

    Args:
        elevation_deg: satellite elevation angle in degrees [0, 90]

    Returns:
        incidence angle in radians
    """
    return np.radians(90.0 - elevation_deg)


def incidence_to_elevation(theta_rad: float) -> float:
    """Convert incidence angle (radians from nadir) to elevation (degrees).

    Inverse of elevation_to_off_nadir.
    """
    return 90.0 - np.degrees(theta_rad)


# ─── Earth-curvature-aware off-nadir ↔ incidence conversion ──────────────

# Earth mean radius in meters (WGS-84 volumetric mean radius).
# Uses the volumetric mean (∛(a²·b)) rather than the equatorial radius,
# minimizing average error in the spherical-Earth φ↔θ conversion across
# all latitudes. The equatorial radius (6,378,137 m) is used elsewhere
# for ECEF coordinate transforms and orbit mechanics.
EARTH_RADIUS_MEAN_M = 6371000.0  # WGS-84 volumetric mean radius

# Default satellite orbital altitude for LEO SAR (meters).
# Typical LEO SAR platforms: Sentinel-1 ≈ 693 km, ICEYE ≈ 500–600 km,
# Capella ≈ 500 km, TerraSAR-X ≈ 514 km. 693 km matches the paper's Sentinel-1.
_DEFAULT_ALTITUDE_M = 693_000.0


def off_nadir_to_incidence(
    phi_rad: float,
    altitude_m: float = _DEFAULT_ALTITUDE_M,
) -> float:
    """Convert off-nadir angle φ to incidence angle θ with Earth curvature.

    For a spherical Earth with radius R_e and satellite at altitude h,
    the incidence angle measured at the ground is:

        θ = arcsin( (R_e + h) / R_e · sin(φ) )

    This is the inverse of the standard viewing geometry relationship.
    For flat-Earth approximation (h ≪ R_e), θ ≈ φ.  The correction
    grows with φ: at φ=30° and h=600 km, incidence is ≈ 33.2° (Δ ≈ 3.2°).

    Args:
        phi_rad: off-nadir angle in radians (measured from nadir at satellite)
        altitude_m: satellite orbital altitude in meters

    Returns:
        incidence angle in radians
    """
    factor = (EARTH_RADIUS_MEAN_M + altitude_m) / EARTH_RADIUS_MEAN_M
    return float(np.arcsin(np.clip(factor * np.sin(phi_rad), -1.0, 1.0)))


def incidence_to_off_nadir(
    theta_rad: float,
    altitude_m: float = _DEFAULT_ALTITUDE_M,
) -> float:
    """Convert incidence angle θ to off-nadir angle φ (inverse of above).

        φ = arcsin( R_e / (R_e + h) · sin(θ) )

    Args:
        theta_rad: incidence angle in radians (measured at ground from nadir)
        altitude_m: satellite orbital altitude in meters

    Returns:
        off-nadir angle in radians
    """
    factor = EARTH_RADIUS_MEAN_M / (EARTH_RADIUS_MEAN_M + altitude_m)
    return float(np.arcsin(np.clip(factor * np.sin(theta_rad), -1.0, 1.0)))


def nesz_linear(theta_rad: float, K_NESZ: float = _K_NESZ_DEFAULT) -> float:
    """Compute NESZ in linear units at incidence angle θ.

    NESZ(θ) = K_NESZ / cos³θ              (Eq. 2, formalization §2.3.1)

    Args:
        theta_rad: incidence angle from nadir, in radians
        K_NESZ: SAR system constant (linear units)

    Returns:
        NESZ in linear units (lower = better sensitivity)
    """
    cos_theta = np.cos(theta_rad)
    if cos_theta <= 1e-15:
        return float("inf")  # grazing incidence → no meaningful observation
    return K_NESZ / (cos_theta ** 3)


def nesz_db(theta_rad: float, K_NESZ: float = _K_NESZ_DEFAULT) -> float:
    """Compute NESZ in dB.

    NESZ_dB = 10 * log10(NESZ_linear)
    Typical values: Sentinel-1 IW ≈ −22 dB, ICEYE ≈ −18 to −20 dB.

    Args:
        theta_rad: incidence angle from nadir, in radians
        K_NESZ: SAR system constant (linear units)

    Returns:
        NESZ in dB (more negative = better sensitivity)
    """
    linear = nesz_linear(theta_rad, K_NESZ)
    if linear <= 0 or np.isinf(linear):
        return 0.0
    return 10.0 * np.log10(linear)


def quality_score(theta_rad: float) -> float:
    """Compute normalized SAR image quality score q(θ) — DIAGNOSTIC ONLY.

    q(θ) = NESZ(θ_ref) / NESZ(θ) = cos³θ / cos³θ_ref       (Eq. 5)

    This function is retained for diagnostic purposes only. The optimization
    targets f2 and f3 use separate formulas (see module docstring).

    Args:
        theta_rad: incidence angle from nadir, in radians

    Returns:
        unitless quality score
    """
    cos_theta = np.cos(theta_rad)
    if cos_theta <= 1e-15:
        return 0.0
    return (cos_theta ** 3) / _COS3_THETA_REF


def quality_score_from_elevation(elevation_deg: float) -> float:
    """Compute quality score directly from elevation angle.

    Convenience wrapper: elevation → incidence → quality_score.

    Args:
        elevation_deg: satellite elevation in degrees

    Returns:
        quality score q(θ)
    """
    theta = elevation_to_off_nadir(elevation_deg)
    return quality_score(theta)


def aggregate_quality(
    observations: List[ScheduledObservation],
) -> float:
    """Compute aggregate diagnostic NESZ quality for a schedule.

    NOTE: This uses the old quality_score() formula and is for diagnostic
    purposes only. The actual f2/f3 optimization targets use different formulas.

    Args:
        observations: list of scheduled observations

    Returns:
        sum of quality scores (higher = better aggregate quality)
    """
    total = 0.0
    for obs in observations:
        elev = obs.window.elevation
        theta = elevation_to_off_nadir(elev)
        total += quality_score(theta)
    return total


def quality_summary(
    observations: List[ScheduledObservation],
) -> dict:
    """Compute a quality summary for a schedule.

    Args:
        observations: list of scheduled observations

    Returns:
        dict with quality metrics
    """
    if not observations:
        return {
            "n_observations": 0,
            "total_quality": 0.0,
            "mean_quality": 0.0,
            "min_quality": 0.0,
            "max_quality": 0.0,
            "mean_nesz_db": 0.0,
        }

    qualities = []
    nesz_values = []
    for obs in observations:
        elev = obs.window.elevation
        theta = elevation_to_off_nadir(elev)
        qualities.append(quality_score(theta))
        nesz_values.append(nesz_db(theta))

    return {
        "n_observations": len(observations),
        "total_quality": float(np.sum(qualities)),
        "mean_quality": float(np.mean(qualities)),
        "min_quality": float(np.min(qualities)),
        "max_quality": float(np.max(qualities)),
        "mean_nesz_db": float(np.mean(nesz_values)),
    }
