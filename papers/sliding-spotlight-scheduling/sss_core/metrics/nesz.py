"""NESZ cos^3 incidence kernel — FORKED copy for Paper 2 (sliding-spotlight scheduling).

Fork provenance (ADR GRILL-002, FORK_MANIFEST.md item F-01):
    source of copy : src/sar_sim/metrics/nesz.py @ tag paper2-m1-baseline (60ee1e8)
    copied symbols : _K_NESZ_DEFAULT, _THETA_REF_DEG, _THETA_REF, _COS3_THETA_REF,
                     nesz_linear, nesz_db, quality_score
    not copied     : elevation/incidence converters (Paper 2 consumes its own orbit
                     geometry builder); aggregate_quality / quality_summary (depend on
                     the shared sar_sim.types.ScheduledObservation -- copying would
                     drag the shared type across the fork boundary).

Drift policy: the mathematical body of every copied function must stay
numerically identical to the shared-lib original; identity is enforced by
papers/sliding-spotlight-scheduling/tests/test_fork_identity_nesz.py.
Editing the math here without a recorded manifest write-back is a violation.

Model (Eq. 2, problem formalization):

    NESZ(theta) = K_NESZ / cos^3(theta)

where theta is the incidence angle. The normalized quality score (diagnostic
only, NOT used as optimization target):

    q(theta) = cos^3(theta) / cos^3(theta_ref)

Paper 2 note: the Paper 2 objective f_Q is a separate per-mode quantity
(pixel-area inverse, spec D6) and must NOT be confused with this diagnostic
q(theta); this module only locks the cos^3 radiometric kernel.
"""

import numpy as np


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

    This function is retained for diagnostic purposes only. The Paper 2
    optimization target f_Q uses a separate per-mode formula (spec D6);
    the Paper 1 targets f2/f3 also use separate formulas (see the shared
    module docstring).

    Args:
        theta_rad: incidence angle from nadir, in radians

    Returns:
        unitless quality score
    """
    cos_theta = np.cos(theta_rad)
    if cos_theta <= 1e-15:
        return 0.0
    return (cos_theta ** 3) / _COS3_THETA_REF
