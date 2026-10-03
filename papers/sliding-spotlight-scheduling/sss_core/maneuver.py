"""Inter-task maneuver closure (spec D5): jerk-limited three-segment model.

Ticket-07 decisions D07-1..7 (registered after the pre-implementation gate
review):

* D07-1 boundary angular rates share ONE planar lever
  ``omega = (Vs/R0) * cos(psi_bar)`` scaled by the mode's beam-steering
  fraction -- STR: 0 (body-fixed antenna), SLS: k (sliding spotlight slides
  the beam at the k fraction of the apparent rate; with A = r0/(R0+r0) the
  slide rate k*Vs/R0 follows from formula-spec §2 exactly), SPT: 1 (staring
  locks on the target).  ``omega_SLS == k * omega_SPT`` is therefore an
  EXACT identity at any squint.  DERIVATION STATUS (audit-corrected
  2026-09-29, ticket 13): the cos^1 lever is NOT the analytic derivative
  of the registered planar relations -- d/dt of this module's own squint
  model squint_at = atan(Vs*t'/R0) gives exactly (Vs/R0)*cos^2(psi_bar),
  and implicit differentiation of the ticket's tan(psi) = (s-x_t)*
  cos(psi)/R0 form gives (Vs/R0)*cos^3(psi)/(1+sin^2(psi)).  The cos^1
  lever OVERESTIMATES the true rate by 1/cos(psi_bar) (+2.2% at the
  +-12 deg envelope edge, exact at 0) -- a conservative upper bound,
  retained: it is consumed by the calibration path only, and the armed
  maneuver FALLBACK (4.07 s constant) means production C2 assembly never
  consumes these numbers.  Convention note: Song Eq.(1) writes
  k_theta = k*v_g/R0 with the ECEF ground speed v_g; the production chain
  uses the frozen inertial Vs (ticket-03 D03-5, ~4.7% difference,
  registered).
* D07-2 SETTLE ACCOUNTING -- Kim Table 3 arithmetic proves the reported
  RMT excludes stabilisation time (32.77 SAT + 5.60 RMT + 3x2 s = 44.37 s
  total, exact; scenario 2 likewise).  The calibration therefore compares
  model vs RMT with BOTH sides excluding settle, and the fallback bound
  (4.07 s, pure maneuver) must be assembled with the 2 s settle at the C2
  consumption layer (ticket 09), never baked in here.  This reconciles the
  spec's "fallback conservative bound + enlarged settle" wording: the
  settle is an explicit C2 term, and the 4.07 s envelope (three-axis
  measured worst case) is deliberately NOT magnified further.
* D07-3 angle-phase time = max of the jerk-only rest-to-rest bound
  ``(32*theta/j)^(1/3)`` (coefficient independently re-derived: four
  jerk bang-bang phases give theta = 2*j*tau^3, T = 4*tau) and the
  acceleration bang-bang bound ``2*sqrt(theta/alpha)``.  The rate-profile
  trapezoid form (theta/alpha + alpha/j) is NOT a rest-to-rest angle
  formula and is excluded (it would only dominate beyond ~28 deg sweeps,
  outside the +-12 deg envelope).
* D07-4 alpha_max is COMPUTED from the fixture (CMG yaw-axis torque over
  yaw-axis MoI, 60/500 -- the z axis is the azimuth execution axis;
  per-axis convention registered, the roll-axis minimum was rejected as
  the wrong axis).  j_max = 25 rad/s^3 is a module-level SANITY constant
  (Fig. 17b realized-peak proxy, NOT a published limit); the fixture null
  stays null.  Inside the operational envelope the acceleration term
  dominates and the jerk term is not binding, and the fallback covers the
  assumption risk.
* D07-5 signs are carried until ``d_omega = |omega_end - omega_start|``;
  taking magnitudes there is safe because the apparent-rate sign is
  geometrically invariant along a prograde pass (registered against future
  reverse-scan extensions).
* D07-6 the Kim Eq.(25)-(29) attitude-quaternion / rotation-centre chain
  belongs to the implementation-layer checker and C1b consumers; the
  boundary rates here are the optimizer-layer planar convention (spec D4
  layering), deliberately not the attitude chain.
* D07-7 the closure returns the BARE maneuver time; the 25% C2 pad is
  applied by the consumption layer (ticket 09), never baked in here.  The
  fallback bound is the worst MEASURED Kim RMT (4.07 s, scenario 2,
  txt-anchored) rather than a model multiplier -- the multiplier variant
  (3.0 x 0.46 s = 1.39 s) would not even cover Kim's own shortest RMT
  (1.84 s) and was rejected at gate review.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

from .fixture import fixture_value, load_platform_fixture
from .modes import Mode, ModeLibrary

# D07-4: SANITY-layer jerk assumption (Fig. 17b realized-peak proxy).
J_MAX_RAD_S3 = 25.0

# D07-2/7: preregistered fallback -- worst MEASURED Kim RMT (scenario 2,
# Table 3, p.29; fixture rmt_reference.scenario2_rmt_per_transition_s max).
FALLBACK_MANEUVER_S = 4.07
FALLBACK_TRIGGER_RATIO = 0.5  # predicted/measured must reach 50% to stand alone
SETTLE_S = 2.0  # Kim stabilization time (Table 2); added at the C2 layer


def alpha_max_rad_s2() -> float:
    """CMG yaw-axis angular acceleration bound, computed from the fixture
    (D07-4): tau_z / I_z = 60 Nm / 500 kgm^2."""
    fx = load_platform_fixture()
    tau_z = float(fixture_value(fx["platform"], "cmg_max_torque_nm")[2])
    i_z = float(fixture_value(fx["platform"], "satellite_moi_kgm2")[2])
    return tau_z / i_z


def boundary_rate(
    mode: Mode,
    psi_bar_rad: float,
    lib: ModeLibrary,
    r0_m: float | None = None,
) -> float:
    """|dpsi/dt| of the beam pointing at the aperture centre (D07-1).

    ``r0_m`` is the slant range of the task the rate is quoted for; None
    falls back to the library R0, which is the calibration caliber (Kim RMT
    comparison) -- per-task production consumers must pass their own range
    (residual R14: the lever drifted +-42% against per-task geometry).
    """
    r0 = lib.geo.R0_m if r0_m is None else r0_m
    lever = lib.geo.vs_mps * math.cos(psi_bar_rad) / r0
    if mode is Mode.STR:
        return 0.0
    if mode is Mode.SLS:
        return lib.geo.k * lever
    if mode is Mode.SPT:
        return lever
    raise ValueError(f"unknown mode {mode!r}")


def _rate_change_time(d_omega: float, alpha: float, j_max: float) -> float:
    """Jerk-limited time to change the angular rate by d_omega (D07-5:
    d_omega arrives as an absolute value)."""
    if d_omega <= 0.0:
        return 0.0
    tau = alpha / j_max  # jerk-phase duration to reach full alpha
    if d_omega <= alpha * alpha / j_max:
        return 2.0 * math.sqrt(d_omega / j_max)  # acceleration triangle
    return d_omega / alpha + tau  # trapezoidal acceleration


def _angle_rest_time(theta: float, alpha: float, j_max: float) -> float:
    """Minimum rest-to-rest time for a fixed-angle slew (D07-3): the max of
    the jerk-only and acceleration bang-bang bounds."""
    if theta <= 0.0:
        return 0.0
    jerk_bound = (32.0 * theta / j_max) ** (1.0 / 3.0)
    accel_bound = 2.0 * math.sqrt(theta / alpha)
    return max(jerk_bound, accel_bound)


def maneuver_time(
    d_psi_rad: float,
    omega_start_rad_s: float,
    omega_end_rad_s: float,
    lib: ModeLibrary,
) -> dict:
    """Bare inter-task maneuver time [s] (D07-3/5/7).

    Decoupled two-phase model: a jerk-limited rate change followed by a
    jerk/acceleration-limited rest-to-rest slew over the remaining angle,
    crediting the angle swept during the rate change at the average rate
    (floored at zero).  No pads, no settle -- those belong to the C2
    consumption layer (ticket 09).
    """
    alpha = alpha_max_rad_s2()
    d_omega = abs(omega_end_rad_s - omega_start_rad_s)  # D07-5
    t_rate = _rate_change_time(d_omega, alpha, J_MAX_RAD_S3)
    swept = 0.5 * (abs(omega_start_rad_s) + abs(omega_end_rad_s)) * t_rate
    theta_rem = max(0.0, abs(d_psi_rad) - swept)
    t_angle = _angle_rest_time(theta_rem, alpha, J_MAX_RAD_S3)
    return {
        "t_maneuver_s": t_rate + t_angle,
        "t_rate_s": t_rate,
        "t_angle_s": t_angle,
        "d_omega_rad_s": d_omega,
        "theta_rem_rad": theta_rem,
    }


@dataclass(frozen=True)
class ManeuverCalibration:
    """Calibration verdict against a Kim RMT measurement (D07-2)."""

    predicted_s: float
    kim_rmt_s: float
    ratio: float
    fallback_active: bool
    fallback_bound_s: float  # pure maneuver; settle added at the C2 layer


def calibrate_against_kim(
    lib: ModeLibrary,
    d_psi_rad: float,
    kim_rmt_s: float,
) -> ManeuverCalibration:
    """Compare the model against one Kim RMT measurement (both sides
    WITHOUT settle, D07-2) and arm the preregistered fallback with a
    visible warning -- never a silent degradation."""
    pred = maneuver_time(d_psi_rad, 0.0, 0.0, lib)["t_maneuver_s"]
    ratio = pred / kim_rmt_s if kim_rmt_s > 0 else float("inf")
    fallback = ratio < FALLBACK_TRIGGER_RATIO
    if fallback:
        warnings.warn(
            f"D5 maneuver model under-predicts Kim RMT "
            f"({pred:.3f} s vs {kim_rmt_s:.2f} s, ratio {ratio:.2f} < "
            f"{FALLBACK_TRIGGER_RATIO}); PREREGISTERED FALLBACK ACTIVE "
            f"(bound {FALLBACK_MANEUVER_S} s per transition, settle added "
            "at the C2 layer) -- not a silent degradation",
            stacklevel=2,
        )
    return ManeuverCalibration(
        predicted_s=pred,
        kim_rmt_s=kim_rmt_s,
        ratio=ratio,
        fallback_active=fallback,
        fallback_bound_s=FALLBACK_MANEUVER_S,
    )


def maneuver_time_production(
    d_psi_rad: float,
    omega_start_rad_s: float,
    omega_end_rad_s: float,
    lib: ModeLibrary,
    calibration: ManeuverCalibration,
) -> dict:
    """C2-facing maneuver time with the fallback armed (D07-2/7): the bare
    model time when the calibration stands alone, the measured envelope
    otherwise.  Settle is NOT included -- it is a separate, explicit C2
    term."""
    if calibration.fallback_active:
        return {"t_maneuver_s": FALLBACK_MANEUVER_S, "source": "fallback"}
    t = maneuver_time(d_psi_rad, omega_start_rad_s, omega_end_rad_s, lib)
    return {"t_maneuver_s": t["t_maneuver_s"], "source": "model"}
