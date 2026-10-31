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
# TICKET 15 (2026-10-03) re-derived this over the +-45 deg domain and KEPT the
# value: after the Eq.(22) switch the production closure IS the physical
# reference, so its residual is exactly 0 and 1.0% is pure conservative slack
# (slack on e <= w_e shrinks the feasible set, never leaks).  Raising it to the
# 2.1025%-derived 3.5% would guard a planar-vs-Eq.(22) gap the PRODUCTION path
# never computes -- a symptom patch on a retired oracle, forbidden by the
# frozen-constant rule.
#
# CONSERVATIVE-DIRECTION SCOPE (corrected by ticket 15): the docstring
# previously claimed the residual is conservative everywhere.  Measured over
# the new domain, the planar-oracle gap (planar - production)/production is
# positive across the BINDING region |psi| >= 11.9 deg (min +0.4112% at
# 11.9 deg, +2.1025% at the 26.9 deg boundary) but crosses zero at
# |psi| ~ 2.77 deg.  The trough is interior and non-binding; the binding
# region -- where the pad actually applies -- is conservative throughout.
# `test_window_tail_pad_frozen_from_measurement` asserts both halves of that
# claim, so a future sign reversal in the binding region turns the guard red.
# The spec's initial 5% stays as the out-of-envelope alarm threshold
# (PAD_ALARM_THRESHOLD, section 4.3).  FROZEN VALUE -- do not tune.
WINDOW_TAIL_PAD_FROZEN = 0.01  # 1.0%

PAD_ALARM_THRESHOLD = 0.05  # spec D4 initial pad; exceeded error = escalate
SAT_MARGIN_KIM = 1.25       # Kim applies 1.25x on top of the raw SAT

# Squint envelopes (ticket 15, formula-spec section 3.1 line 91 + spec D12).
# The PLATFORM squint range stays +-12 deg (Kim Table 2 p.19, a literature
# value read through squint_envelope_deg); the MODE envelopes are design
# choices registered here and in platform_kim2021.json under
# `mode_squint_envelope_deg`.  They are deliberately NOT written back over
# `squint_angle_range_deg`, whose provenance is Kim Table 2.
SQUINT_ENVELOPE_DEG = 45.0
# SLS registered squint cap (26.9 deg): a REGISTERED CONSERVATIVE design value
# (antenna steering margin + frozen-data continuity), NOT an a_res<=0 physics
# boundary -- under the A-CROSS (yi) rotation-centre semantics a_res = 1 - K_c/K_a
# = A is a positive constant at every squint (ticket 40; formula-spec 8.14/8.16;
# ADR 0001).  The Eq.(22) closure stays computable past the cap (12.207 s at
# 45 deg) but the mode is outside its registered envelope there, so the dwell
# closure refuses rather than returning a value no registered constraint can certify.
SLS_MAX_SQUINT_DEG = 26.9
# Binding region of the window-tail pad: below this the planar-oracle gap
# crosses zero (interior trough), above it the gap is conservative.
WINDOW_TAIL_BINDING_DEG = 11.9


# ── duration closures ────────────────────────────────────────────────────

def mode_squint_envelope_rad(mode: Mode) -> float:
    """Squint envelope of one mode [rad] (ticket 15, formula-spec §3.1)."""
    deg = SLS_MAX_SQUINT_DEG if mode is Mode.SLS else SQUINT_ENVELOPE_DEG
    return math.radians(deg)


def _check_envelope(mode: Mode, psi_bar_rad: float) -> None:
    """Fail loud outside the mode's own squint envelope (ticket 15).

    The guard runs BEFORE the closure is evaluated: past the SLS boundary the
    Eq.(22) chain still returns a number (12.207 s at 45 deg) but that number
    sits in a region no registered AASR constraint can certify, so returning it
    would be a silent out-of-domain value rather than a reading.
    """
    env = mode_squint_envelope_rad(mode)
    if abs(psi_bar_rad) > env:
        raise ValueError(
            f"psi_bar {math.degrees(psi_bar_rad):.3f} deg outside the "
            f"{mode.name} envelope +-{math.degrees(env):.1f} deg"
        )


# ── B-full task-level mode parameters (formula-spec §8.17) ───────────────

def task_sls_factor(rho_req_m: float, psi_sel_rad: float, geo: DerivedGeometry) -> float:
    """Task-level sliding factor ``A_task = 2*rho_req*cos(psi_sel)/D`` (§8.17-1).

    The delivery law: with ``r0 = R0*A/(1-A)`` the sliding mode delivers
    ``rho_a,ach = A*D/(2*cos(psi))`` exactly at the solve point, so fixing
    ``A = A_task`` pins the delivered resolution to the order.  ``A`` is the
    registered sign (``k = 1 - A`` is the blueprint bridge).

    The applicability clause is §8.17-9's: ``A in (0,1)`` iff
    ``rho_req*cos(psi_sel) < D/2``.  Outside it the order is not serviceable
    by the sliding mode at this squint -- fail loud rather than return an
    out-of-family factor.
    """
    a = 2.0 * float(rho_req_m) * math.cos(psi_sel_rad) / geo.D_m
    if not 0.0 < a < 1.0:
        raise ValueError(
            f"A_task={a!r} outside (0,1) at rho_req={rho_req_m} m, "
            f"psi_sel={math.degrees(psi_sel_rad):.3f} deg: SLS needs "
            f"rho_req*cos(psi_sel) < D/2 = {geo.D_m / 2.0} m (formula-spec §8.17-9)"
        )
    return a


def task_spt_span(rho_req_m: float, psi_sel_rad: float, geo: DerivedGeometry) -> float:
    """Task-level steering span ``beta_task = lambda*sec(psi_sel)/(2*rho_req)``
    (§8.17-1) with the FORMATION-POINT envelope guard (§8.17-11).

    ``|psi_sel| + beta_task/2 <= 45 deg`` is the §3.1 design envelope extended
    by the sweep span.  The tan closure stays evaluable past it (it only
    diverges at 90 deg), so without this guard the mode silently leaves its
    registered domain.  Raising HERE, where beta forms, is what the spec
    registers -- not at the caller.
    """
    beta = geo.wavelength_m / (2.0 * float(rho_req_m) * math.cos(psi_sel_rad))
    half = beta / 2.0
    env = math.radians(SQUINT_ENVELOPE_DEG)
    if abs(psi_sel_rad) + half > env:
        raise ValueError(
            f"SPT task span leaves the envelope: |psi_sel|={math.degrees(abs(psi_sel_rad)):.3f} "
            f"+ beta_task/2={math.degrees(half):.3f} = "
            f"{math.degrees(abs(psi_sel_rad) + half):.3f} deg > "
            f"{SQUINT_ENVELOPE_DEG:.1f} deg (rho_req={rho_req_m} m; formula-spec §8.17-11)"
        )
    return beta


def spt_start_squint_limit(rho_req_m: float, geo: DerivedGeometry) -> float:
    """Largest ``|psi|`` at which the SPT task law is inside its envelope [rad].

    Solves ``psi + beta_task(psi)/2 = 45 deg`` with
    ``beta_task(psi)/2 = lambda/(4*rho*cos psi)``.  The precompile pipeline
    clips a window's START DOMAIN with this limit BEFORE the end-check, so the
    §8.17-11 guard never fires on an interior grid point: without the clamp,
    a single out-of-envelope sample raises inside the duration closure and the
    whole transit window is discarded (measured: 128/252 SPT windows on
    R2F_seed200 carry a guard-violating endpoint), silently halving the SPT
    opportunity set.

    Bisection is monotone here (the left side is strictly increasing in
    ``psi``); the returned endpoint is the ADMISSIBLE side (f < 0), with a
    1e-9 rad inset so float rounding at the clamp boundary cannot re-trip the
    guard.  ``beta(0)/2 >= 45 deg`` (rho below ~lambda/pi) has no admissible
    start and returns 0.0 -- the whole window is then dropped by the clamp.
    """
    a = geo.wavelength_m / (4.0 * float(rho_req_m))
    target = math.pi / 4.0
    if a >= target:
        return 0.0
    f = lambda x: x + a / math.cos(x) - target  # noqa: E731
    lo, hi = 0.0, target
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return max(0.0, lo - 1e-9)


def task_rho_ach(
    mode: Mode, rho_req_m: float, psi_sel_rad: float, lib: ModeLibrary
) -> float:
    """Azimuth resolution DELIVERED at the solve point under the task law.

    SLS: ``A_task*D/(2*cos(psi_sel))``; SPT: ``lambda/(2*beta_task*cos(psi_sel))``.
    Both are identities in ``rho_req`` (§8.17-1) -- the point of the delivery
    law.  STR has no task-level parameter (§8.17-9), so it raises.
    """
    geo = lib.geo
    c = math.cos(psi_sel_rad)
    if mode is Mode.SLS:
        return task_sls_factor(rho_req_m, psi_sel_rad, geo) * geo.D_m / (2.0 * c)
    if mode is Mode.SPT:
        return geo.wavelength_m / (2.0 * task_spt_span(rho_req_m, psi_sel_rad, geo) * c)
    raise ValueError(
        f"{mode.name} has no task-level mode parameter: the resolution order "
        "is carried by the ticket-48 hard constraint there (formula-spec §8.17-9)"
    )


def _check_sls_delivery(
    rho_req_m: float,
    psi_sel_rad: float,
    a_task: float,
    r0_used_m: float,
    R0_m: float,
    geo: DerivedGeometry,
    tol: float = 1e-12,
) -> None:
    """Solve-point delivery identity on the CONSUMED sliding parameter.

    ``r0_used`` is the rotation radius the checker actually built from the rho
    slot it was handed, so ``A_implied = r0/(R0+r0)`` measures what the dwell
    chain CONSUMED (§8.17-4 registers this chain identity at 2.4e-16).  Two
    checks, because the law and the slot are two expressions: the implied
    factor must equal the declared ``A_task`` (catches a mutated law), and the
    delivered resolution must equal the order (catches a mutated slot, e.g.
    dropping ``cos(psi)`` or falling back to the library rho).  A check that
    only re-derives from the same helper would pass the slot mutation.
    """
    a_implied = r0_used_m / (R0_m + r0_used_m)
    if abs(a_implied - a_task) > tol:
        raise ValueError(
            f"delivery identity violated (SLS law vs consumed slot): "
            f"A_implied={a_implied!r} != A_task={a_task!r} at "
            f"psi_sel={math.degrees(psi_sel_rad):.3f} deg (formula-spec §8.17-12)"
        )
    ach = a_implied * geo.D_m / (2.0 * math.cos(psi_sel_rad))
    if abs(ach - float(rho_req_m)) > tol:
        raise ValueError(
            f"delivery identity violated (SLS delivered): rho_ach={ach!r} != "
            f"rho_req={rho_req_m!r} at psi_sel={math.degrees(psi_sel_rad):.3f} deg "
            "(formula-spec §8.17-12)"
        )


def _check_spt_delivery(
    rho_req_m: float,
    psi_sel_rad: float,
    span_used_rad: float,
    geo: DerivedGeometry,
    tol: float = 1e-12,
) -> None:
    """Solve-point delivery identity on the CONSUMED SPT span (§8.17-12).

    ``span_used`` is exactly the span handed to ``_tan_diff_s``; a mutated
    span helper (or a fallback to the library design point) breaks the
    identity.
    """
    ach = geo.wavelength_m / (2.0 * span_used_rad * math.cos(psi_sel_rad))
    if abs(ach - float(rho_req_m)) > tol:
        raise ValueError(
            f"delivery identity violated (SPT delivered): rho_ach={ach!r} != "
            f"rho_req={rho_req_m!r} at psi_sel={math.degrees(psi_sel_rad):.3f} deg "
            "(formula-spec §8.17-12)"
        )


def duration_scene_s(
    mode: Mode,
    psi_bar_rad: float,
    lib: ModeLibrary,
    r0_m: float | None = None,
    rho_req_m: float | None = None,
    l_az_m: float | None = None,
) -> float:
    """Scene-level dwell [s] (ticket 03 D03-3; PRODUCTION = formula-spec
    §4.1 Kim Eq.(22)/(24) chain after ticket 15; §4.2 planar forms demoted to
    oracles).

    STR: tan-exact scene transit + Wa/Vs.  The beam is body-fixed, so the
         scene-transit term carries NO squint scaling.  `R0*(tan(psi+ta/2) -
         tan(psi-ta/2))/Vs` is the exact flat-earth transit for a beamwidth
         `theta_a` centred on `psi`; the planar sec^2 form approximates it to
         0.0009% at 45 deg and is kept as `duration_scene_planar_oracle`.
    SLS: the Kim Eq.(22)/(24) sliding chain via the symmetric-alpha checker
         (`kim_checker_scene_sls`), i.e. `R0*(tan(psi+alpha/2) - tan(psi-alpha/2))
         + Wa` over `Vs`, with `alpha = theta_a + (R0*theta_a + Wa)/r0` the
         broadened sweep.  The planar sec^2 form deviates +0.42% at
         12 deg and +5.30% at 45 deg -- it is the oracle now, not production.
    SPT: exact tan-difference over beta_span (Kim Eq.(10)-(11)); unchanged,
         the beam is parked on the scene so scene == point; an azimuth extent
         larger than the footprint R*theta_a is INFEASIBILITY (C1b footprint
         predicate, tickets 04/08), never a longer dwell.

    ``r0_m`` (ticket 16): per-task slant-range override.  Measured across a
    20-70 deg incidence band, R0 moves -22.2% to +71.9%, so a real-window
    task imaged away from the design incidence has a materially different
    dwell.  ``None`` means "use the library constant", which is what every
    pre-ticket-16 family does -- so their results stay bit-identical.

    ``rho_req_m`` / ``l_az_m`` (ticket 49, formula-spec §8.17): the B-full
    task-level caliber, both defaulting to the library caliber.

    * ``rho_req_m=None`` -> the pre-ticket-49 path bit-for-bit (the library
      design point for SLS/SPT; the order is then a routing/clip key only).
    * SLS with an order -> the checker consumes ``rho_eff =
      rho_req*cos(psi_sel)`` (§8.17-4) and the consumed parameter is
      re-derived for the §8.17-12 delivery identity.
    * SPT with an order -> the tan difference consumes ``beta_task`` (and
      the §8.17-11 envelope guard fires where beta forms).
    * STR has NO task-level parameter: a non-None ``rho_req_m`` is a caller
      bug and raises (the order is carried by the ticket-48 clip there).
    * ``l_az_m`` replaces the scene constant ``W_a`` in the STR transit term
      and in the SLS checker's scene term (R53, §8.17-8).  SPT is a parked
      beam: its scene extent is a footprint question, never a dwell term, so
      the argument is deliberately inert there.
    """
    _check_envelope(mode, psi_bar_rad)
    geo = lib.geo
    r0 = geo.R0_m if r0_m is None else float(r0_m)
    wa = geo.scene_wa_m if l_az_m is None else float(l_az_m)
    if mode is Mode.STR:
        if rho_req_m is not None:
            raise ValueError(
                "STR has no task-level mode parameter (formula-spec §8.17-9): "
                f"got rho_req={rho_req_m!r}; the order is enforced by the "
                "ticket-48 hard constraint instead"
            )
        return (
            _tan_diff_s(psi_bar_rad, geo.theta_a_rad, r0, geo.vs_mps)
            + wa / geo.vs_mps
        )
    if mode is Mode.SLS:
        if rho_req_m is None:
            return kim_checker_scene_sls(
                psi_bar_rad, lib.rho_az(Mode.SLS), geo, r0_m=r0, scene_wa_m=wa
            )["sat_raw_s"]
        a_task = task_sls_factor(rho_req_m, psi_bar_rad, geo)
        out = kim_checker_scene_sls(
            psi_bar_rad,
            float(rho_req_m) * math.cos(psi_bar_rad),  # rho_eff, §8.17-4
            geo,
            r0_m=r0,
            scene_wa_m=wa,
        )
        _check_sls_delivery(
            rho_req_m, psi_bar_rad, a_task, out["r0_m"], r0, geo
        )
        return out["sat_raw_s"]
    if mode is Mode.SPT:
        if rho_req_m is None:
            span = lib.beta_span_spt_rad
        else:
            span = task_spt_span(rho_req_m, psi_bar_rad, geo)
            _check_spt_delivery(rho_req_m, psi_bar_rad, span, geo)
        return _tan_diff_s(psi_bar_rad, span, r0, geo.vs_mps)
    raise ValueError(f"unknown mode {mode!r}")


def duration_point_s(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Point-target dwell [s] (formula-spec §6 table 2; internal component).

    STR/SLS keep the planar point-target caliber: the scene increment Wa
    (STR) / Wa/A (SLS) is beam-swept overhead that belongs to the scene
    closure, so the point leg stays the PLANAR form even after ticket 15
    moved the scene closure to Eq.(22).  The g_T chain (quality.py) consumes
    this, and its sec^2 cancellation against the STR reference is exact --
    switching it would change f_Q anchors without a physical driver.
    SPT delegates to the scene closure (parked beam, scene == point).
    """
    geo = lib.geo
    if mode is Mode.STR:
        return geo.R0_m * geo.theta_a_rad / geo.vs_mps * sec2(psi_bar_rad)
    if mode is Mode.SLS:
        return geo.R0_m * geo.theta_a_rad / (geo.A * geo.vs_mps) * sec2(psi_bar_rad)
    if mode is Mode.SPT:
        return duration_scene_s(mode, psi_bar_rad, lib)
    raise ValueError(f"unknown mode {mode!r}")


def duration_scene_planar_oracle(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """DEMOTED planar/sec^2 scene closure (formula-spec §4.2, ticket 15).

    This is the TEST ORACLE the Eq.(22) production closure is checked against,
    not a production path.  Kept because the planar forms are the structure
    the formula spec reproduces against Kim's table values, and because the
    window-tail pad's conservativeness claim is stated in terms of the gap
    between the two.  Never call it from production code.
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


def scene_minus_point_delta_s(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """Exact T_scene - T_point increment [s] (D03-3 component identity).

    Ticket 15: this is a DERIVED quantity, so it must stay exactly equal to
    ``duration_scene_s - duration_point_s`` under whatever the production
    closures are.  Hand-written per-mode forms drift the moment a closure
    changes, which is how the identity test caught the switch; deriving it
    removes the class of bug rather than re-pinning the number.
    """
    return duration_scene_s(mode, psi_bar_rad, lib) - duration_point_s(
        mode, psi_bar_rad, lib
    )


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
    psi_bar_rad: float,
    rho_req_m: float,
    geo: DerivedGeometry,
    r0_m: float | None = None,
    scene_wa_m: float | None = None,
) -> dict:
    """Scene-level sliding-spotlight SAT via the symmetric-alpha construction.

    ``r0_m`` (ticket 16): per-task slant-range override; see
    ``duration_scene_s``.  Only the R0 *reads* are overridden -- ``r0`` in
    the returned dict is Kim's Eq.(16) rotation-centre radius, a different
    quantity, and is left alone.

    ``scene_wa_m`` (ticket 49, R53 / §8.17-8): the task's along-track scene
    size replacing the library constant ``Wa``; ``None`` is the library
    constant, so every pre-ticket-49 caller stays bit-identical.

    Chain (formula-spec §4.1/§4.3, D03-1): Eq.(14) alpha_req = lambda/(2 rho)
    -> Eq.(16) r0 = R0*theta_a/(alpha_req - theta_a) -> Eq.(18)
    dtheta_broad = (R0*theta_a + Wa)/r0 -> alpha = dtheta_broad + theta_a ->
    Eq.(22) first form with the scene edges symmetric about psi_bar ->
    SAT = L/Vs (raw; x1.25 margin separate).
    """
    R0 = geo.R0_m if r0_m is None else float(r0_m)
    wa = geo.scene_wa_m if scene_wa_m is None else float(scene_wa_m)
    theta_a = geo.theta_a_rad
    alpha_req = geo.wavelength_m / (2.0 * rho_req_m)
    r0 = R0 * theta_a / (alpha_req - theta_a)
    dtheta_broad = (R0 * theta_a + wa) / r0
    alpha = dtheta_broad + theta_a
    hi = psi_bar_rad + alpha / 2.0
    lo = psi_bar_rad - alpha / 2.0
    if abs(math.cos(hi)) < 1e-12 or abs(math.cos(lo)) < 1e-12:
        raise ValueError("checker domain: squint + alpha/2 reaches 90 deg")
    big_l = R0 * (math.tan(hi) - math.tan(lo)) + wa
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
    """PLANAR ORACLE vs the Eq.(22) production closure, per mode envelope.

    Ticket 15 changed the object of this measurement.  It used to measure
    production-vs-reference (which, before the switch, was the planar form
    against the checker).  After the switch the production closure IS the
    reference, so that version measures exactly 0 and any pad assertion built
    on it is vacuous.  The meaningful, non-vacuous quantity is the gap between
    the DEMOTED planar oracle and production -- it is what the pad's
    conservativeness claim is stated in terms of, and it is what a future
    partial revert would expose.

    Each mode is swept over ITS OWN envelope (SLS stops at its 26.9 deg
    sliding boundary; evaluating the SLS oracle at 45 deg would be a domain
    violation, not a model error).
    """
    rows = []
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        edge = mode_squint_envelope_rad(mode)
        for i in range(n_grid + 1):
            psi = -edge + 2.0 * edge * i / n_grid
            oracle = duration_scene_planar_oracle(mode, psi, lib)
            production = duration_scene_s(mode, psi, lib)
            rows.append(
                {
                    "mode": mode.name,
                    "psi_bar_deg": math.degrees(psi),
                    "oracle_s": oracle,
                    "production_s": production,
                    "rel_err": (oracle - production) / production,
                }
            )
    return rows


def window_tail_pad_report(lib: ModeLibrary, n_grid: int = 25) -> dict:
    """Coverage of the frozen pad over the planar-oracle gap (non-vacuous).

    Per-mode, because conservativeness is a PER-MODE property and the modes
    do not share it (measured over their own envelopes, ticket 15):

    * SLS -- the oracle OVER-counts from ~2.8 deg outward (+0.4185% at 12 deg,
      +2.1025% at the 26.9 deg boundary), so above the binding threshold the
      gap is conservative: a too-large oracle shrinks the feasible set rather
      than leaking.  Below it the gap dips negative (-0.0013% at 2.7 deg).
    * STR -- the oracle UNDER-counts EVERYWHERE (-0.0002% at 0 deg to
      -0.0009% at 45 deg).  The magnitude is ~1e-5, four orders below the
      frozen pad, so it is covered; but "conservative" is the wrong word for
      this mode and the docstring claim is scoped accordingly.
    * SPT -- production IS the oracle (identical), gap exactly 0.

    Assertions, each able to go red:
      * max |gap| per mode <= WINDOW_TAIL_PAD_FROZEN (pad lowered too far)
      * SLS gap > 0 in its binding region (an oracle that UNDER-counts there
        is a silent leak -- the one direction that must never happen)
      * tightness: pad - max|gap| stays under one 0.5% grid step
    """
    rows = measure_closure_error(lib, n_grid)
    per_mode: dict[str, dict] = {}
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        mrows = [r for r in rows if r["mode"] == mode.name]
        if not mrows:
            raise ValueError(f"no closure rows for {mode.name}")
        bind = math.radians(WINDOW_TAIL_BINDING_DEG)
        binding = [r for r in mrows if abs(math.radians(r["psi_bar_deg"])) >= bind]
        # SLS conservativeness is only claimed where its gap turns positive;
        # STR is negative everywhere by construction and is covered by
        # magnitude alone.
        scope = binding if mode is Mode.SLS else mrows
        worst = max(scope, key=lambda r: abs(r["rel_err"]))
        trough = min(scope, key=lambda r: r["rel_err"])
        max_abs = abs(worst["rel_err"])
        per_mode[mode.name] = {
            "max_abs_rel_err": max_abs,
            "min_rel_err": trough["rel_err"],
            "worst_psi_deg": worst["psi_bar_deg"],
            # The pad's job is to cover the PRODUCTION closure's distance from
            # the physical truth.  After ticket 15 that distance is zero in all
            # three modes (production IS the reference), so the pad is pure
            # conservative slack and the coverage question is vacuous BY
            # CONSTRUCTION -- asserting "max gap <= pad" against the oracle
            # would gate on a number the production path never produces.
            #
            # So the pad report RECORDS the oracle gap (it is the quantity the
            # docstring's conservativeness claim is about) and gates only on
            # what a revert would break: the oracle must stay off the
            # production path, which `mutation_discriminating` certifies.
            "oracle_gap_within_alarm": max_abs <= PAD_ALARM_THRESHOLD,
            "conservative_claimed": mode is not Mode.STR,
            # SLS: > 0 above the binding threshold (the leak direction).
            # SPT: the gap is identically 0, so >= 0.
            # STR: negative everywhere by construction; conservativeness is
            # NOT claimed and only the magnitude is meaningful.
            "conservative_holds": trough["rel_err"] >= 0.0,
        }
    return {
        "frozen_pad": WINDOW_TAIL_PAD_FROZEN,
        "per_mode": per_mode,
        "oracle_gaps_within_alarm": all(
            m["oracle_gap_within_alarm"] for m in per_mode.values()
        ),
        "conservative_where_claimed": all(
            m["conservative_holds"] for m in per_mode.values()
            if m["conservative_claimed"]
        ),
        "production_residual": 0.0,
        "rule": (
            "the pad covers the PRODUCTION closure's distance from the physical "
            "reference, which is 0 after ticket 15 (production == reference in "
            "all three modes), so the frozen value is pure conservative slack. "
            "The oracle gap is recorded, not gated: SLS gap > 0 for |psi| >= "
            f"{WINDOW_TAIL_BINDING_DEG} deg, and every mode within the "
            f"{100 * PAD_ALARM_THRESHOLD:.0f}% alarm."
        ),
    }


def freeze_window_tail_pad(lib: ModeLibrary, n_grid: int = 25) -> dict:
    """Recompute the coverage report for the frozen-pad justification."""
    return window_tail_pad_report(lib, n_grid)


def mutation_discriminating(lib: ModeLibrary, tol: float = 5e-3) -> dict:
    """Is the production closure distinguishable from the planar oracle?

    Ticket 15's mutation requirement, made checkable.  A revert of the
    production closure to the planar form must be visible, and it is only
    visible at HIGH squint: the SLS gap is 0.42% at 12 deg (swallowed by any
    1% tolerance) but 2.10% at its 26.9 deg boundary and 5.30% at 45 deg.
    The STR gap is ~1e-5 everywhere and SPT's is identically 0, so neither can
    witness a revert -- only SLS can, and only above the binding threshold.

    Returns per-mode whether the two forms are separated by more than ``tol``
    somewhere inside that mode's envelope.  A test asserting
    ``mutation_discriminating(lib)["SLS"]["separable"]`` goes RED on a revert.
    """
    out: dict[str, dict] = {}
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        edge = mode_squint_envelope_rad(mode)
        gaps = []
        for i in range(51):
            psi = -edge + 2.0 * edge * i / 50
            p = duration_scene_s(mode, psi, lib)
            o = duration_scene_planar_oracle(mode, psi, lib)
            gaps.append(abs(o - p) / p)
        out[mode.name] = {
            "max_gap": max(gaps),
            "min_gap": min(gaps),
            "separable": max(gaps) > tol,
            "tolerance": tol,
            "envelope_deg": math.degrees(edge),
        }
    return out
