"""Per-mode quality metric family and f_Q aggregation (spec D6).

Formula sources: formula-spec v1.0.1 §3 (per-mode rho_a, achieved), §5
(RASR), §8.3 (SPT achieved = library constant, not the requirement),
§8.5 (NESZ ~ R^3 with the g_T dwell term the ONE self-derived factor --
its verification belongs here).  Ticket-05 decisions D05-1..8 (registered
in the ticket body after the pre-implementation gate review):

* D05-2 ROLE SPLIT -- cost kernel vs radiometric kernel.  The scheduled
  dwell that enters f1 costs, C2 transfers and window checks is the
  SCENE-level closure (D03-3).  The radiometric dwell gain g_T is the
  POINT-target ratio T_point(mode)/T_point(STR): the scene term Wa/Vs is
  beam-surveillance overhead, not per-target integrated-pulse energy (a
  scene reference would break the radiometric monotonicity -- SPT scene
  dwell is SHORTER than SLS because its beam parks instead of sweeping).
* D05-3 CONSTRUCTIVE COUPLING (registered counter-evidence) -- to within
  0.02% (SPT tan-exact vs sec^2 linearisation), g_T,point equals
  rho_a,STR/rho_a,ach: the dwell gain carries no information beyond the
  mode ordering.  It is retained because its semantic leg is independent
  (integrated-pulse ENERGY vs geometric sampling); the spec-D6 exit
  channel (``g_t_enabled=False``) is the clean fallback should a reviewer
  reject the redundancy.
* D05-4 t-invariance -- the sec^2 squint factor cancels inside g_T (exactly
  for SLS/STR, to 0.02% for SPT) and rho_rg, R are planar-layer constants,
  so f_Q,i is TIME-INVARIANT at this layer; solution dependence of f_Q
  enters only through the selected set (matters for the HV envelope).
* D05-5 DOUBLE WEIGHTING NOTE (spec D6 / A6(3), required defence) --
  rho_a,ach embeds a 1/rho_req-type implicit priority weighting (finer
  requirements pay longer dwells via the mapping, so f1--f_Q trade-offs
  are real), and g_T adds an effective rho_a^2 azimuth weighting on top
  (via D05-3).  Papers must state BOTH, not only the first.
* D05-6 dimension normalisation -- q_rad = g_T * (R_ref/R)^3 is
  dimensionless (R_ref = R0, frozen); planar identity (R_ref/R)^3 ==
  (cos(theta_i)/cos(theta_i,ref))^3, the same normalisation shape as
  Paper 1's quality_score.  A fixed positive factor preserves the Pareto
  set and normalized HV.  f_Q is in m^-2 as the ticket requires.
* D05-8 aggregation contract -- f_Q = (1/|S|) * sum f_Q,i over the
  SELECTED set (mean, never sum); an empty selection RAISES (fail-loud);
  the mean is regression-guarded by its duplication-idempotency property.
* D05-7 RASR -- injectable pure function: neither PRF nor the range AAP
  G_r is published by Kim, so both are parameters.  The dynamic-range
  probe runs with Song Table 1 PRF {1150, 2300} Hz (mapping reference,
  literature/fulltext/song2025_sensors_sparse.txt line 376-377) and a
  registered placeholder range pattern; the probe verdict is INITIAL and
  must be re-checked once ticket 06 freezes PRF in the manifest.
"""
from __future__ import annotations

import math

from .duration import duration_point_s
from .modes import Mode, ModeLibrary

SPEED_OF_LIGHT_M_S = 299792458.0  # [教科书] SI exact value

# D05-7 placeholder range-pattern assumption (NOT a fixture value; Kim
# publishes no range beamwidth).  Registered so the RASR probe numbers are
# traceable to an explicit assumption.
RASR_PLACEHOLDER_RANGE_BEAMWIDTH_DEG = 2.0
RASR_REFERENCE_PRF_HZ = (1150.0, 2300.0)  # Song 2025 Table 1, mapping reference


# ── ground-range resolution (D05-1) ──────────────────────────────────────

def range_bandwidth_hz(lib: ModeLibrary, theta_inc_deg: float | None = None) -> float:
    """[自推导·设计锚] B_rg = c / (2 * rho_rg,design * sin(theta_inc)).

    Derived from the fixture design anchor (0.5 m x 0.5 m at 45 deg
    incidence); SANITY-layer, frozen (formula-spec §7 discipline).
    """
    theta_inc = math.radians(lib.geo.theta_inc_deg if theta_inc_deg is None else theta_inc_deg)
    return SPEED_OF_LIGHT_M_S / (2.0 * lib.geo.rho_design_m * math.sin(theta_inc))


def ground_range_resolution_m(lib: ModeLibrary, theta_inc_deg: float | None = None) -> float:
    """[教科书] rho_gr = c / (2 * B_rg_fixed * sin(theta_i)).

    B_rg is a FIXED instrument parameter, frozen at the design incidence
    (D05-1); only the projection sin(theta_i) varies with the queried
    angle.  At the design point this reduces constructively to
    rho_rg,design (the planar layer keeps theta_i constant, so rho_rg is a
    constant here; scene-centre semantics -- the near/far-edge incidence
    variation belongs to the RASR evaluation region).
    """
    theta_inc = math.radians(lib.geo.theta_inc_deg if theta_inc_deg is None else theta_inc_deg)
    b_rg = range_bandwidth_hz(lib)  # frozen at the design incidence
    return SPEED_OF_LIGHT_M_S / (2.0 * b_rg * math.sin(theta_inc))


# ── radiometric factor (D05-2/3/6) ───────────────────────────────────────

def dwell_gain(mode: Mode, psi_bar_rad: float, lib: ModeLibrary) -> float:
    """g_T = T_point(mode) / T_point(STR) -- integrated-pulse-energy ratio.

    Point-target reference (D05-2); == 1 for STR, == 1/A for SLS (exact),
    and within 0.02% of rho_a,STR/rho_a,SPT for SPT (D05-3 identity).
    """
    if mode is Mode.STR:
        return 1.0
    ref = duration_point_s(Mode.STR, psi_bar_rad, lib)
    return duration_point_s(mode, psi_bar_rad, lib) / ref


def q_rad(
    mode: Mode,
    psi_bar_rad: float,
    r_m: float,
    lib: ModeLibrary,
    g_t_enabled: bool = True,
) -> float:
    """Dimensionless radiometric factor (D05-6): g_T * (R_ref/R)^3.

    ``g_t_enabled=False`` is the spec-D6 exit channel: q_rad degrades to
    the pure range term while f_Q stays mode-dependent through rho_a,ach.
    """
    factor = (lib.geo.R0_m / r_m) ** 3
    if g_t_enabled:
        factor *= dwell_gain(mode, psi_bar_rad, lib)
    return factor


# ── f_Q per task + aggregation (D05-4/8) ─────────────────────────────────

def f_q_per_task(
    mode: Mode,
    psi_bar_rad: float,
    r_m: float,
    lib: ModeLibrary,
    g_t_enabled: bool = True,
) -> float:
    """f_Q,i = (rho_rg * rho_a,ach)^-1 * q_rad  [m^-2]  (spec D6)."""
    rho_rg = ground_range_resolution_m(lib)
    rho_a = lib.rho_az(mode)
    return (rho_rg * rho_a) ** -1 * q_rad(mode, psi_bar_rad, r_m, lib, g_t_enabled)


def f_q_aggregate(f_q_values) -> float:
    """f_Q = (1/|S|) * sum over the SELECTED set (spec D6, gate-review R1).

    Mean, never sum: f1 already grows with selection, a summing f_Q would
    degenerate in the same direction.  Empty selection raises (D05-8).
    Idempotency under duplication (mean(S U S) == mean(S)) is the
    regression property that pins the mean -- a sum aggregation doubles
    under duplication and turns that test red.
    """
    values = list(f_q_values)
    if not values:
        raise ValueError(
            "f_Q aggregate of an EMPTY selection is undefined "
            "(fail-loud contract, D05-8); callers must guard"
        )
    return sum(values) / len(values)


# ── HV reference envelope (spec D6, blueprint §5.2) ─────────────────────

def f_q_envelope(f_q_values) -> tuple[float, float]:
    """(min, max) of f_Q over the MODE-LIBRARY reachable envelope.

    Domain (D05-4): every task x every library mode -- NEVER a single
    mode's own best (that would erase cross-mode differences in HV
    pooling, spec D6 禁令).
    """
    values = list(f_q_values)
    if not values:
        raise ValueError("HV envelope over an empty set is undefined")
    return min(values), max(values)


# ── RASR (D05-7, formula-spec §5 Eq.(11)) ────────────────────────────────

def gr_placeholder(
    theta_off_boresight_rad: float,
    theta_3db_deg: float = RASR_PLACEHOLDER_RANGE_BEAMWIDTH_DEG,
) -> float:
    """Placeholder two-way range pattern sinc^2(0.886 theta / theta_3dB).

    REGISTERED ASSUMPTION (not fixture data): theta_3dB = 2.0 deg.  Used
    only by the dynamic-range probe until a sourced range antenna model
    exists.
    """
    x = 0.886 * math.pi * theta_off_boresight_rad / math.radians(theta_3db_deg)
    if abs(x) < 1e-12:
        return 1.0
    s = math.sin(x) / x
    return s * s


def rasr(
    r_m: float,
    prf_hz: float,
    incidence_fn,
    boresight_incidence_rad: float,
    gr_pattern=gr_placeholder,
    n_ambiguities: int = 5,
    min_ground_incidence_rad: float = math.radians(0.5),
    altitude_m: float | None = None,
) -> float:
    """Range-ambiguity ratio, formula-spec §5 Eq.(11) [Song 2025 p.6].

    RASR = sum_{m!=0} G_r^2(theta_r(r_m)) cos(theta_i(r_m)) /
           (r_m^3 sin(theta_i(r_m)))   /   same term at r,
    r_m = r + m c/(2 PRF).  ``incidence_fn`` maps slant range -> incidence
    angle; ``boresight_incidence_rad`` is the scene-centre reference the
    off-boresight angle is measured against; ``gr_pattern`` is injectable
    (no published range AAP).  Numeric conventions (registered, D05-7):
    ambiguous ranges with NO ground intercept (r_m <= altitude in the
    planar model) and near-nadir points (theta_i < 0.5 deg, where the
    grazing term degenerates and the mainlobe gain is nil) contribute
    zero.  Callers evaluate at the scene near/far edges and take the
    WORST (formula-spec §5 evaluation-region rule).
    """
    c_over_2prf = SPEED_OF_LIGHT_M_S / (2.0 * prf_hz)

    def _term(rr: float) -> float:
        if altitude_m is not None and rr <= altitude_m:
            return 0.0  # no ground intercept for that ambiguous pulse
        ti = incidence_fn(rr)
        if ti < min_ground_incidence_rad:
            return 0.0
        off = abs(ti - boresight_incidence_rad)
        g2 = gr_pattern(off) ** 2
        return g2 * math.cos(ti) / (rr ** 3 * math.sin(ti))

    num = sum(
        _term(r_m + m * c_over_2prf)
        for m in range(-n_ambiguities, n_ambiguities + 1)
        if m != 0
    )
    return num / _term(r_m)


def rasr_scene_worst(
    r_near_m: float,
    r_far_m: float,
    prf_hz: float,
    incidence_fn,
    gr_pattern=gr_placeholder,
    n_ambiguities: int = 5,
    altitude_m: float | None = None,
) -> dict:
    """Worst (largest) RASR over the scene near/far edges (formula-spec §5).

    The boresight reference is the SCENE-CENTRE incidence (the beam points
    at the scene centre; the edges are off-boresight).
    """
    boresight = incidence_fn(0.5 * (r_near_m + r_far_m))
    near = rasr(
        r_near_m, prf_hz, incidence_fn, boresight, gr_pattern, n_ambiguities, altitude_m=altitude_m
    )
    far = rasr(
        r_far_m, prf_hz, incidence_fn, boresight, gr_pattern, n_ambiguities, altitude_m=altitude_m
    )
    worst = max(near, far)
    return {
        "rasr_near": near,
        "rasr_far": far,
        "rasr_worst": worst,
        "rasr_worst_db": 10.0 * math.log10(worst) if worst > 0 else float("-inf"),
    }


def rasr_dynamic_range_probe(lib: ModeLibrary, prf_hz_list=RASR_REFERENCE_PRF_HZ) -> dict:
    """INITIAL dynamic-range probe over the PRF reference set (D05-7).

    Placeholder G_r + mapping-reference PRF -- the recorded verdict is
    provisional and MUST be re-checked after ticket 06 freezes PRF.
    """
    geo = lib.geo
    h = geo.altitude_m
    g0 = h * math.tan(math.radians(geo.theta_inc_deg))
    half = geo.scene_wa_m / 2.0

    def incidence_from_slant(r: float) -> float:
        # planar inverse of r = h / cos(theta_i)
        return math.acos(max(-1.0, min(1.0, h / r)))

    r_near = h / math.cos(math.atan((g0 - half) / h))
    r_far = h / math.cos(math.atan((g0 + half) / h))

    rows = []
    for prf in prf_hz_list:
        for mode in Mode:
            # the RASR chain is mode-independent in this layer (no azimuth
            # coupling in Eq.(11)); the mode loop documents that explicitly
            rows.append(
                {
                    "prf_hz": prf,
                    "mode": mode.name,
                    **rasr_scene_worst(
                        r_near, r_far, prf, incidence_from_slant, altitude_m=h
                    ),
                }
            )
    db = [r["rasr_worst_db"] for r in rows if math.isfinite(r["rasr_worst_db"])]
    return {
        "rows": rows,
        "min_db": min(db),
        "max_db": max(db),
        "dynamic_range_db": max(db) - min(db),
        "provisional": True,
    }
