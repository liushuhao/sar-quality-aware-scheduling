"""Dwell-duration closed forms (scene-level), margin pads, Kim SAT checker.

Formula source (FROZEN): formula-spec v1.0.1 §4 (duration family), §6
(expectation tables), §7 (SANITY discipline).  Ticket-03 decisions
(`.scratch/sliding-spotlight-scheduling/issues/03-*.md`, gate-review
2026-09-27):

* D03-1 checker construction: the Kim full-curvature scene checker is the
  SYMMETRIC-alpha form L(psi_bar) = R0*[tan(psi_bar+alpha/2) -
  tan(psi_bar-alpha/2)] + Wa with alpha = dtheta_broad + theta_a and R0
  from Eq.(2)-(3) -- the ONLY construction that reproduces the registered
  formula-spec §6 table 3/4 values (L@12deg = 50,696 m, SAT@12deg x1.25 =
  8.362 s; independent fresh recomputation <0.3 m agreement).  The literal
  §4.3 Eq.(20)-(23) rotating-centre chain is kept ONLY as an internal
  identity check (its two Eq.(22) forms coincide at the quadratic root);
  it is never asserted against Kim values.
* D03-3 optimizer dwell = SCENE-LEVEL closures (the scheduled task is a
  5x5 km scene; the Kim Table 3 fixture is scene-level).  The point-target
  values of §6 table 2 survive as exact component identities
  T_scene - Wa/(A*Vs)*sec^2 == T_point.  The blueprint-recommended
  "point-target + scene delta into the margin pad" variant is rejected:
  Wa/(A*Vs) ~= 3.26 s ~= 103% of the point dwell cannot live inside a 5%
  model-error pad.
* D03-5 production V_s = inertial (frozen SANITY value); ECEF is
  evidence-only for the dual-convention band assertion.

SAT literature anchor: Kim Table 3 per-target SAT 8.38/8.18/8.08/8.13 s
(``literature/fulltext/kim2021_aerospace_fulltext.txt`` line 1302; the
fixture field name ``squint_staring_per_target_s`` is a naming relic --
these are scene-level SLIDING-SPOTLIGHT SATs, Kim p.20).  Assertions
against them are band assertions per formula-spec §7 only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .geometry import DerivedGeometry
from .modes import Mode, ModeLibrary, sec2

# C2 inter-task transfer pad: Kim's "a margin of 25% is considered in
# addition to the SAT" (kim2021 p.7 / p.11 definitions; p.19 parameter and
# p.25 results restatement also state it — four places total, ticket 21;
# fixture sat_margin_fraction).
INTER_TASK_PAD_FRACTION_KIM = 0.25

# Window-tail pad (spec D4): covers the duration-MODEL error at the window
# end check e <= w_e.  Frozen from the checker measurement below (ticket
# 03, freeze-before-run): measured max |rel err| = 0.4185% (SLS closure vs
# symmetric-alpha checker at psi_bar = +-12 deg; STR split form residual
# 2e-6, SPT exact 0) x 1.5 = 0.63% -> rounded UP to the 0.5% grid = 1.0%.
# Residual direction: the SLS closure OVERestimates the checker at the
# envelope edges (conservative -- feasible set shrinks, never leaks); a
# -0.02% near-broadside underestimate exists and is covered by the pad.
# The spec's initial 5% stays as the out-of-envelope alarm threshold
# (PAD_ALARM_THRESHOLD, §4.3).  FROZEN VALUE -- do not tune.
WINDOW_TAIL_PAD_FROZEN = 0.01  # 1.0%

PAD_ALARM_THRESHOLD = 0.05  # spec D4 initial pad; exceeded error = escalate
SAT_MARGIN_KIM = 1.25       # Kim applies 1.25x on top of the raw SAT


# ── duration closures ────────────────────────────────────────────────────

def duration_scene_s(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Scene-level dwell [s] (ticket 03 D03-3; formula-spec §4.2 structure).

    STR: R*theta_a/Vs * sec^2(psi_bar) + Wa/Vs   (split form: the stripmap
         beam is body-fixed, so the scene-transit term Wa/Vs carries NO
         squint scaling; only the beam-transit term is sec^2 inflated.
         Residual vs the tan-exact scene transit is 2e-6 @12 deg -- sec^2
         is second-order exact across the 0.36 deg beamwidth.)
    SLS: (R*theta_a + Wa)/(A*Vs) * sec^2(psi_bar)  (the sliding beam SWEEPS
         the scene azimuth extent, so Wa shares the sec^2 scaling; matches
         the symmetric-alpha checker to +0.42% @12 deg, formula-spec §6
         table 4's 0.44% register.)
    SPT: exact tan-difference over beta_span (Kim Eq.(10)-(11)); the beam is
         parked on the scene, so scene == point; an azimuth extent larger
         than the footprint R*theta_a is INFEASIBILITY (C1b footprint
         predicate, tickets 04/08), never a longer dwell.
    """
    geo = lib.geo
    if mode is Mode.STR:
        return (
            geo.R0_m * geo.theta_a_rad / geo.vs_mps * sec2(psi_bar_rad)
            + geo.scene_wa_m / geo.vs_mps
        )
    if mode is Mode.SLS:
        return (
            (geo.R0_m * geo.theta_a_rad + geo.scene_wa_m)
            / (geo.A * geo.vs_mps)
            * sec2(psi_bar_rad)
        )
    if mode is Mode.SPT:
        return _tan_diff_s(psi_bar_rad, lib.beta_span_spt_rad, geo.R0_m, geo.vs_mps)
    raise ValueError(f"unknown mode {mode!r}")


def duration_point_s(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Point-target dwell [s] (formula-spec §6 table 2; internal component)."""
    geo = lib.geo
    if mode is Mode.STR:
        return geo.R0_m * geo.theta_a_rad / geo.vs_mps * sec2(psi_bar_rad)
    if mode is Mode.SLS:
        return geo.R0_m * geo.theta_a_rad / (geo.A * geo.vs_mps) * sec2(psi_bar_rad)
    if mode is Mode.SPT:
        return duration_scene_s(mode, psi_bar_rad, lib)
    raise ValueError(f"unknown mode {mode!r}")


def scene_minus_point_delta_s(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Exact T_scene - T_point increment [s] (D03-3 component identity).

    STR: Wa/Vs (no squint scaling -- body-fixed beam, ground scene transit).
    SLS: Wa/(A*Vs)*sec^2 (beam-swept scene extent).
    SPT: 0 (parked beam; scene == point).
    """
    geo = lib.geo
    if mode is Mode.STR:
        return geo.scene_wa_m / geo.vs_mps
    if mode is Mode.SLS:
        return geo.scene_wa_m / (geo.A * geo.vs_mps) * sec2(psi_bar_rad)
    if mode is Mode.SPT:
        return 0.0
    raise ValueError(f"unknown mode {mode!r}")


def _tan_diff_s(psi_bar_rad: float, span_rad: float, r_m: float, vs_mps: float) -> float:
    """R*[tan(psi+span/2) - tan(psi-span/2)]/Vs -- exact flat-earth transit."""
    hi = psi_bar_rad + span_rad / 2.0
    lo = psi_bar_rad - span_rad / 2.0
    for x in (hi, lo):
        if abs(math.cos(x)) < 1e-12:
            raise ValueError("tan-difference singular: angle -> +-90 deg")
    return r_m * (math.tan(hi) - math.tan(lo)) / vs_mps


def duration_spt_exact_s(psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Public alias for the exact SPT tan-difference dwell (Kim Eq.(10)-(11))."""
    return _tan_diff_s(
        psi_bar_rad, lib.beta_span_spt_rad, lib.geo.R0_m, lib.geo.vs_mps
    )


# ── Kim full-curvature scene checker (D03-1) ─────────────────────────────

def kim_checker_scene_sls(
    psi_bar_rad: float, rho_req_m: float, geo: DerivedGeometry
) -> dict:
    """Scene-level sliding-spotlight SAT via the symmetric-alpha construction.

    Chain (formula-spec §4.1/§4.3, D03-1): Eq.(14) alpha_req = lambda/(2 rho)
    -> Eq.(16) r0 = R0*theta_a/(alpha_req - theta_a) -> Eq.(18)
    dtheta_broad = (R0*theta_a + Wa)/r0 -> alpha = dtheta_broad + theta_a ->
    Eq.(22) first form with the scene edges symmetric about psi_bar ->
    SAT = L/Vs (raw; x1.25 margin separate).
    """
    theta_a = geo.theta_a_rad
    alpha_req = geo.wavelength_m / (2.0 * rho_req_m)
    r0 = geo.R0_m * theta_a / (alpha_req - theta_a)
    dtheta_broad = (geo.R0_m * theta_a + geo.scene_wa_m) / r0
    alpha = dtheta_broad + theta_a
    hi = psi_bar_rad + alpha / 2.0
    lo = psi_bar_rad - alpha / 2.0
    if abs(math.cos(hi)) < 1e-12 or abs(math.cos(lo)) < 1e-12:
        raise ValueError("checker domain: squint + alpha/2 reaches 90 deg")
    big_l = geo.R0_m * (math.tan(hi) - math.tan(lo)) + geo.scene_wa_m
    sat_raw = big_l / geo.vs_mps
    return {
        "L_m": big_l,
        "alpha_rad": alpha,
        "dtheta_broad_rad": dtheta_broad,
        "r0_m": r0,
        "sat_raw_s": sat_raw,
        "sat_margined_s": sat_raw * SAT_MARGIN_KIM,
    }


def kim_eq23_theta_s1(
    psi_s0_rad: float, rho_req_m: float, geo: DerivedGeometry
) -> dict:
    """Eq.(20)-(23) rotating-centre chain -- INTERNAL identity check (D03-1).

    Solves the Eq.(23) quadratic (root inside the required squint range) and
    returns both Eq.(22) forms evaluated at the root.  The two forms must
    coincide to machine precision at the exact root (table-5-style identity
    assertion); this chain is NOT asserted against Kim published values.
    """
    theta_a = geo.theta_a_rad
    half = theta_a / 2.0
    alpha = (
        psi_s0_rad
        + half
        - math.asin(math.sin(psi_s0_rad + half) - geo.wavelength_m / (2.0 * rho_req_m))
    )
    r0 = geo.R0_m * theta_a / (alpha - theta_a)
    q = geo.R0_m + r0
    tan_half = math.tan(half)
    p = math.tan(psi_s0_rad + half)
    s = math.tan(psi_s0_rad)
    a_q = tan_half
    b_q = r0 / q + (geo.scene_wa_m / q + (geo.R0_m / q) * p - s) * tan_half
    c_q = (geo.R0_m / q) * tan_half - s + geo.scene_wa_m / q + (geo.R0_m / q) * p
    disc = b_q * b_q - 4.0 * a_q * c_q
    if disc < 0.0:
        raise ValueError("Eq.(23) discriminant negative -- no real end squint")
    sq = math.sqrt(disc)
    roots = ((-b_q + sq) / (2.0 * a_q), (-b_q - sq) / (2.0 * a_q))
    # Root selection: end squint lies within the required range, i.e. the
    # beam axis descends from theta_s0 by alpha - theta_a without leaving
    # the +-90 deg tan domain (formula-spec Eq.(23) "two roots, take the one
    # inside the required squint interval").
    chosen = None
    for t in roots:
        theta_s1 = math.atan(t)
        if abs(theta_s1) < math.pi / 2.0 and t <= s:
            chosen = t
            break
    if chosen is None:
        raise ValueError("Eq.(23): no admissible root inside the squint range")
    l_form1 = geo.R0_m * (p - (chosen - tan_half) / (1.0 + chosen * tan_half)) + geo.scene_wa_m
    l_form2 = q * (s - chosen)
    return {
        "alpha_rad": alpha,
        "r0_m": r0,
        "tan_theta_s1": chosen,
        "theta_s1_rad": math.atan(chosen),
        "L_form1_m": l_form1,
        "L_form2_m": l_form2,
        "identity_rel_gap": abs(l_form1 - l_form2) / abs(l_form2),
    }


# ── margin pads (spec D4, ticket 03 layering) ────────────────────────────

@dataclass(frozen=True)
class MarginPads:
    """Margin-pad layering: C2 inter-task pad vs window-tail model-error pad.

    standard           -- C2 = Kim 25%, tail = frozen measured bound.
    degenerate_anchor  -- M?NC anchor: BOTH pads zero (spec D4; aligns the
                          fixed-duration regression semantics of Paper 1's
                          deterministic slew+settle C2).
    """

    inter_task_fraction: float
    window_tail_fraction: float

    @classmethod
    def standard(cls) -> "MarginPads":
        return cls(INTER_TASK_PAD_FRACTION_KIM, WINDOW_TAIL_PAD_FROZEN)

    @classmethod
    def degenerate_anchor(cls) -> "MarginPads":
        return cls(0.0, 0.0)


def pad_window_tail(duration_s: float, pads: MarginPads) -> float:
    """Inflate a dwell by the window-tail pad (e <= w_e check input)."""
    return duration_s * (1.0 + pads.window_tail_fraction)


# ── pad calibration measurement (freeze evidence, ticket 03) ─────────────

def measure_closure_error(lib: ModeLibrary, n_grid: int = 25) -> list[dict]:
    """Scene-closure vs exact/checker relative error over the squint envelope.

    Rows: STR closure vs tan-exact scene transit; SLS closure vs the Kim
    symmetric-alpha checker at the SLS library resolution; SPT closure vs
    its own exact tan form (identity, error ~0).  The frozen window-tail
    pad = max |rel err| x 1.5, rounded UP to the 0.5% grid.
    """
    geo = lib.geo
    rows = []
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        for i in range(n_grid + 1):
            psi = math.radians(-12.0 + 24.0 * i / n_grid)
            closure = duration_scene_s(mode, psi, lib)
            if mode is Mode.STR:
                exact = (
                    _tan_diff_s(psi, geo.theta_a_rad, geo.R0_m, geo.vs_mps)
                    + geo.scene_wa_m / geo.vs_mps
                )
            elif mode is Mode.SLS:
                exact = kim_checker_scene_sls(psi, lib.rho_az(Mode.SLS), geo)["sat_raw_s"]
            else:
                exact = duration_spt_exact_s(psi, lib)
            rows.append(
                {
                    "mode": mode.name,
                    "psi_bar_deg": math.degrees(psi),
                    "closure_s": closure,
                    "reference_s": exact,
                    "rel_err": (closure - exact) / exact,
                }
            )
    return rows


def freeze_window_tail_pad(lib: ModeLibrary, n_grid: int = 25) -> dict:
    """Recompute the calibration and return the frozen-pad justification."""
    rows = measure_closure_error(lib, n_grid)
    worst = max(rows, key=lambda r: abs(r["rel_err"]))
    max_abs = abs(worst["rel_err"])
    grid = 0.005
    frozen = math.ceil(max_abs * 1.5 / grid) * grid
    return {
        "worst_row": worst,
        "max_abs_rel_err": max_abs,
        "frozen_pad": frozen,
        "rule": "ceil_to_0.5pct(max_abs_rel_err * 1.5)",
    }
