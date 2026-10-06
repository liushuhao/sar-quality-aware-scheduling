"""Scenario family generator ``M<d><i><r>`` (spec D2/D10, ticket 08).

Family code ``M<density 1-4><interval N|W><demand C|F|H>``; densities
20/100/300/500 inherit the Paper-1 gradient.  Preregistration lives in
``experiments/scenario_manifest_template.json`` (seed convention
``variant_index*100 + seed_index``; rho_req tiers bind BY REFERENCE to
``experiments/platform_kim2021.json#resolution.rho_req_bands`` -- values
are never copied here).

Ticket-08 decisions D08-1..10 (post gate-review; the review FAILED the
original design and forced two real fixes):

* D08-1 bands frozen by THIS ticket: coarse [2.5, 3.0] m (ENTIRELY inside
  the STR routing tier -- the original [1.0, 3.0] proposal leaked
  [1.0, 2.4669) into SLS and broke the M?NC all-STR anchor; reviewer
  recomputed on the frozen router), fine [0.3, 0.6] m (spans the SPT/SLS
  routing boundary so the F tier mixes modes on its own), boundary zone
  [0.45, 0.55] m (cheap-ablation prereg).  The 0.6 m upper edge is a
  registered design convention (no Kim source), like the SPT 0.3 library
  point.
* D08-2 per-task AASR gate: the SPT worst-edge evaluation uses the TASK's
  own azimuth extent (aasr_direct(spt_scene_wa_m=...)), not the platform
  5 km default -- a 1-3 km fine-demand scene is AASR-feasible while the
  5 km default is not; the platform default stays over-conservative for
  smaller scenes, never the reverse.
* D08-5 squint convention: with the frozen inertial Vs the squint rate is
  Vs/R0 = 0.56 deg/s, so the N window spans +-3.36 deg and the W window
  +-11.20 deg (both inside the +-12 deg envelope, asserted at generation).
* D08-6 priority = randint(1, 10), the exact Paper-1 convention
  (generate_all_scenarios.py:133), keeping the f1 axis same-source.
* D08-9 removals are FIRST-MATCH cascaded (below_finest -> footprint ->
  aasr) and the manifest must satisfy sum(buckets) + served == drawn.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from .aasr import AASR_THRESHOLD_DB, aasr_direct, route_mode
from .duration import SQUINT_ENVELOPE_DEG, MarginPads, duration_scene_s
from .fixture import fixture_value, load_platform_fixture
from .geometry import look_geometry, squint_at
from .modes import Mode, ModeLibrary
from .windows import footprint_ok

FORK_DOMAIN = Path(__file__).resolve().parent.parent
RESULTS_DIR = FORK_DOMAIN / "experiments" / "results" / "scenarios"

# D08-9: variant registry (seed = variant_index * 100 + seed_index);
# the five ticket variants span the density gradient and all three demand
# tiers (M4WH: the original M4WW slip used an invalid demand letter 'W' --
# legal demand letters are C/F/H only)
VARIANT_REGISTRY = {
    1: ("M1NC", 20, "N", "C"),   # degenerate anchor (narrow + coarse -> all STR)
    2: ("M2WH", 100, "W", "H"),
    3: ("M3NC", 300, "N", "C"),
    4: ("M2WF", 100, "W", "F"),
    5: ("M4WH", 500, "W", "H"),
    # probe amendment 2026-09-30 (analysis_prereg.json
    # amendment_20260930_probe_density): post-hoc WH-family density sweep
    # below M2WH; NOT part of the frozen matrix (indexes 1-5 unchanged)
    6: ("P6WH", 20, "W", "H"),
    7: ("P7WH", 40, "W", "H"),
    8: ("P8WH", 60, "W", "H"),
    9: ("P9WH", 80, "W", "H"),
}

# keys 6-8 are whitelist-only entries for the density probe (their variant
# indexes live in VARIANT_REGISTRY); the frozen prereg densities 1-4 stand
DENSITY_BY_INDEX = {1: 20, 2: 100, 3: 300, 4: 500, 6: 40, 7: 60, 8: 80}
INTERVAL_HALF_WIDTH_S = {"N": 6.0, "W": 20.0}  # D08-5: +-3.36 / +-11.20 deg
PASS_HORIZON_S = 300.0
PRF_PRODUCTION_HZ = 3630.0  # platform operating point (design convention)

ANCHOR_T_DISPERSION_LIMIT = 1.10  # spec D10 / Testing Decisions (preregistered)
H_MIX_DOCUMENTED_RANGE = (0.35, 0.65)  # documentation value; the test asserts
# the EXACT Bernoulli realization count for the seed (D08-9)


# ── real-window family R<density><requirement> (ticket 16, redesigned 25) ─
#
# The 300 s box retires here: each task's windows come from the three-leg
# cascade (incidence mask n mode envelope n end-check, ticket 25 AD-6 adds
# the incidence leg to the intersection) over REAL enumerated transits.
#
# Ticket 25 redesign (spec amendment v0.6, all numbers probe-measured on the
# frozen design orbit, 2026-10-05):
#   AD-2  transits are ENUMERATED from the ground track, not sampled at
#         epoch + {0,600} s (which is 37.5 deg of true anomaly -- an
#         arbitrary phase point; measured 0/8 clusters servable vs 6/8
#         under enumeration).  Per target: coarse incidence scan over the
#         registered span, in-band runs refined by a 33-point local grid
#         per edge (resolution enum_step_s/32 ~= 0.47 s), runs clustered
#         into passes by the gap-merge threshold (robust 150..1200 s,
#         measured identical counts; NOT a physical lower bound).  The two
#         in-band flanks of one pass merge into one pass because the
#         sub-band nadir middle is far shorter than the threshold.
#   AD-4  single dense domain: centre (20N, 0E), 1000 km side, 5x5 grid at
#         250 km spacing (measured 25/25 nodes carry >=1 in-band transit;
#         300 km grid lacks incidence heterogeneity, 2000 km exceeds the
#         longest single-pass window).
#   AD-5  density ladder re-based to 20/50/100 (single-transit STR capacity
#         24 => ceil(N/24) passes; N>=150 needs more passes than the
#         registered 3-day span provides).  R4H (N=500) is retired.
#   AD-9  the schedule span IS the enumeration span: 3 days (>= 1 ground
#         track repeat; the two-body propagator repeats its track every
#         14.97 orbits ~= 23.93 h, measured).
R_DOMAIN_CENTRE_DEG = (20.0, 0.0)
R_DOMAIN_SIDE_KM = 1000.0
R_GRID_N = 5
R_GRID_SPACING_KM = 250.0
R_SCATTER_HALF_CELL_KM = 125.0   # jitter within the node's own cell
R_KM_PER_DEG_LAT = 111.32        # [教科书] meridian km per degree
R_SPAN_DAYS = 3.0                # AD-9: registered schedule/enumeration span
R_SPAN_S = R_SPAN_DAYS * 86400.0
R_ENUM_STEP_S = 15.0             # coarse scan step (runs are >= ~85 s wide)
R_GAP_MERGE_S = 300.0            # registered band parameter, NOT a physical bound
R_GAP_MERGE_ROBUST_S = (150.0, 600.0, 1200.0)  # measured: same pass counts
R_PASS_SPAN_S = 120.0            # per-side propagation span around t_ca
R_PROP_STEP_S = 1.0              # geometry sampling step
R_INCIDENCE_BAND_DEG = (30.0, 60.0)
# Fractional guard inside the mode envelope.  The sampling grid and the
# end-check bracket can each land a hair outside; 1% is far above both
# (the sampling step is ~0.4% of the envelope at n_scan=240) and far below
# any physically meaningful narrowing.
R_ENVELOPE_GUARD_FRACTION = 0.01
R_DENSITY_BY_INDEX = {1: 20, 2: 50, 3: 100}
R_FAMILY_REGISTRY = {
    1: ("R1C", 20, "C"),
    2: ("R2F", 50, "F"),
    3: ("R3H", 100, "H"),
}


def load_rho_bands() -> dict:
    """Bind the frozen bands BY REFERENCE; fail loud if still pending
    (D08-10, manifest-template completeness rule)."""
    fx = load_platform_fixture()
    bands = fx["resolution"]["rho_req_bands"]
    if str(bands.get("status", "")).startswith("pending"):
        raise ValueError(
            "rho_req bands are still pending_D2_mapping_ticket: scenario "
            "generation must refuse to run (manifest-template completeness "
            "rule, D08-10)"
        )
    return {
        "coarse": tuple(float(v) for v in bands["coarse_band_m"]["value"]),
        "fine": tuple(float(v) for v in bands["fine_band_m"]["value"]),
        "boundary_zone": tuple(float(v) for v in bands["boundary_zone_m"]["value"]),
    }


def generate_scenario(
    family_code: str,
    density_n: int,
    interval: str,
    demand_tier: str,
    seed: int,
    variant_index: int | None = None,
    lib: ModeLibrary | None = None,
) -> dict:
    """Generate one scenario instance and return its manifest (dict).

    Determinism: the ONLY stochastic source is ``random.Random(seed)``,
    consumed in a fixed per-target order (demand -> size -> t_ca ->
    priority; the H Bernoulli draw precedes the demand draw), so the same
    seed reproduces the manifest byte-identically (spec 确定性).
    """
    if demand_tier not in ("C", "F", "H"):
        raise ValueError(f"invalid demand tier {demand_tier!r}")
    if interval not in INTERVAL_HALF_WIDTH_S:
        raise ValueError(f"invalid interval {interval!r}")
    if density_n not in DENSITY_BY_INDEX.values():
        raise ValueError(f"invalid density {density_n}")
    lib = lib or ModeLibrary.from_fixture()
    bands = load_rho_bands()  # D08-10 fail loud
    half_w = INTERVAL_HALF_WIDTH_S[interval]
    psi_max_window = abs(squint_at(half_w, 0.0, lib.geo))
    if psi_max_window > math.radians(SQUINT_ENVELOPE_DEG):
        raise ValueError(
            f"window exceeds the +-{SQUINT_ENVELOPE_DEG:.0f} deg squint envelope "
            "(D08-5 guard, ticket-15 widened)"
        )

    rng = random.Random(seed)
    tasks = []
    removals = {"below_finest": 0, "footprint": 0, "aasr": 0}
    h_draws = 0  # exact Bernoulli realization count (D08-9)
    dispersion = 1.0
    anchor = family_code.endswith("NC")

    for _ in range(density_n):
        # H: per-target Bernoulli(p=0.5) BEFORE the demand draw (fixed order)
        if demand_tier == "H":
            use_coarse = rng.random() < 0.5
            h_draws += int(use_coarse)
            band = bands["coarse"] if use_coarse else bands["fine"]
        else:
            band = bands["coarse"] if demand_tier == "C" else bands["fine"]
        rho_req = rng.uniform(*band)
        # size convention (D08-2 rationale): fine-resolution targets are
        # physically smaller scenes; the AASR/footprint gates remove the rest
        if band == bands["coarse"]:
            l_az_m = rng.uniform(2000.0, 5000.0)
        else:
            l_az_m = rng.uniform(1000.0, 3000.0)
        t_ca = rng.uniform(half_w, PASS_HORIZON_S - half_w)  # D08-7
        priority = rng.randint(1, 10)  # D08-6, Paper-1 convention

        # first-match removal cascade (D08-9)
        if rho_req < lib.rho_az(Mode.SPT) - 1e-12:
            removals["below_finest"] += 1
            continue
        mode = route_mode(rho_req, lib)
        if not footprint_ok(mode, l_az_m, lib):
            removals["footprint"] += 1
            continue
        psi_edge = squint_at(half_w, 0.0, lib.geo)
        aasr = aasr_direct(
            mode,
            psi_edge,
            lib.geo.k,
            PRF_PRODUCTION_HZ,
            lib,
            spt_scene_wa_m=(l_az_m if mode is Mode.SPT else None),
        )["aasr_db"]
        if not (aasr <= AASR_THRESHOLD_DB):
            removals["aasr"] += 1
            continue

        t0, t1 = t_ca - half_w, t_ca + half_w
        # window dwell dispersion (anchor property; sampled edges+centre)
        if anchor:
            ts = [t0, t_ca, t1]
            durs = [duration_scene_s(mode, _squint_at(t, t_ca, lib.geo), lib) for t in ts]
            dispersion = max(dispersion, max(durs) / min(durs))
        tasks.append(
            {
                "t_start_s": round(t0, 9),
                "t_end_s": round(t1, 9),
                "t_ca_s": round(t_ca, 9),
                "azimuth_size_m": round(l_az_m, 6),
                "priority": priority,
                "rho_req_m": round(rho_req, 9),
                "mode": mode.name,
                "prf_hz": PRF_PRODUCTION_HZ,
            }
        )

    assert sum(removals.values()) + len(tasks) == density_n  # D08-9 ledger
    pads = MarginPads.degenerate_anchor() if anchor else MarginPads.standard()
    manifest = {
        "schema": "scenario-manifest/1.0",
        "scenario": {
            "family_code": family_code,
            "density_n_targets": density_n,
            "interval_width": interval,
            "demand_tier": demand_tier,
            "platform_fixture": "experiments/platform_kim2021.json",
            "degenerate_anchor": anchor,
        },
        "preregistration": {
            "seed": seed,
            "variant_index": variant_index,
            "seed_rule": "variant_index*100 + seed_index (ticket-02 template)",
            "rho_req_bands_source": (
                "experiments/platform_kim2021.json#resolution.rho_req_bands "
                "(bound by reference, frozen by ticket 08)"
            ),
            "pads": {
                "inter_task_fraction": pads.inter_task_fraction,
                "window_tail_fraction": pads.window_tail_fraction,
            },
            "prf_production_hz": PRF_PRODUCTION_HZ,
            "priority_convention": "randint(1,10) (Paper-1 generate_all_scenarios.py:133)",
        },
        "generation_ledger": {
            "n_drawn": density_n,
            "removals": removals,
            "n_served": len(tasks),
            "h_coarse_draws": h_draws,
            "anchor_t_dispersion_max_min": round(dispersion, 9),
            "anchor_t_dispersion_limit": ANCHOR_T_DISPERSION_LIMIT,
        },
        "tasks": tasks,
    }
    if anchor:
        assert dispersion <= ANCHOR_T_DISPERSION_LIMIT, dispersion
    return manifest


from .geometry import squint_at as _squint_at  # D10-7 single source


# ── real-window family generator (ticket 16; transit enumeration per 25) ─

def _ecef_track(elements, epoch, times_s):
    """Satellite ECEF position/velocity at the given offsets (s since epoch).

    One ``kepler_to_eci`` call per time -- the frozen F-02 propagation path,
    reused verbatim; only the per-target geometry (vector norms and dots) is
    vectorized downstream.  The coarse scan grid is shared by EVERY target
    in the scenario, so this cost is paid once per scenario, not per target.
    Returns ``(positions, velocities)`` as (N, 3) arrays.
    """
    import numpy as np
    from datetime import timedelta, timezone

    from .realwindows import eci_to_ecef_rotation, kepler_to_eci

    pos = np.empty((len(times_s), 3))
    vel = np.empty((len(times_s), 3))
    for k, t in enumerate(times_s):
        st = kepler_to_eci(elements, epoch + timedelta(seconds=float(t)))
        # same frame pinning as realwindows.satellite_to_target_vector (R21)
        tt = (
            st.time.replace(tzinfo=timezone.utc)
            if st.time.tzinfo is None else st.time
        )
        rot = eci_to_ecef_rotation(tt.timestamp())
        pos[k] = rot @ st.position
        vel[k] = rot @ st.velocity
    return pos, vel


def _incidence_deg_array(sat_ecef, target):
    """Vectorized incidence [deg] of one target against a precomputed track.

    Same definition as ``realwindows._target_incidence_angle``: the angle
    between the WGS-84 geodetic normal and the target->satellite unit
    vector, acos, [0, 180].  A guard test pins the array readout to the
    scalar path (<= 1e-9 deg)."""
    import numpy as np

    from .realwindows import geodetic_normal, lat_lon_to_ecef

    tgt = lat_lon_to_ecef(target.lat, target.lon, target.altitude_m)
    up = geodetic_normal(target.lat, target.lon)
    los = sat_ecef - tgt[None, :]
    norm = np.linalg.norm(los, axis=1)
    cos_inc = np.einsum("ij,j->i", los / norm[:, None], up)
    return np.degrees(np.arccos(np.clip(cos_inc, -1.0, 1.0)))


def _vector_squint_deg_array(sat_ecef, sat_vel_ecef, target):
    """Vectorized VECTOR-squint [deg] (the full along-track off-nadir angle).

    Mirrors the ``squint_deg`` element of
    ``realwindows.satellite_to_target_vector``; used ONLY to locate each
    pass's closest-approach time, never as an envelope quantity."""
    import numpy as np

    from .realwindows import lat_lon_to_ecef

    tgt = lat_lon_to_ecef(target.lat, target.lon, target.altitude_m)
    los = tgt[None, :] - sat_ecef            # satellite -> target
    norm = np.linalg.norm(los, axis=1)
    track = sat_vel_ecef / np.linalg.norm(sat_vel_ecef, axis=1)[:, None]
    along = np.abs(np.einsum("ij,ij->i", los / norm[:, None], track))
    return np.degrees(np.arcsin(np.clip(along, 0.0, 1.0)))


def _ground_track_passes(
    elements, epoch, target, track_times, track_ecef, band, step_s, gap_merge_s,
):
    """Enumerate the target's in-band transit passes over the span (AD-2).

    Returns a list of passes, each ``(seg_lo, seg_hi, runs)`` where ``runs``
    are the refined in-band runs (absolute seconds since epoch) clustered
    into ONE pass by ``gap_merge_s``.  A pass's two in-band flanks (the
    incidence dips below the band at the near-nadir middle) merge because
    that middle is far shorter than the threshold; two distinct passes are
    hours apart, so the threshold cannot merge them -- both properties are
    guard-tested, not assumed.  Edge refinement resolution: step_s / 32
    (a 33-point local grid per edge).
    """
    import numpy as np

    inc = _incidence_deg_array(track_ecef, target)
    ok = (inc >= band[0]) & (inc <= band[1])

    # maximal in-band runs on the grid
    runs = []
    start = None
    for k in range(len(ok)):
        if ok[k] and start is None:
            start = k
        elif not ok[k] and start is not None:
            runs.append((start, k - 1))
            start = None
    if start is not None:
        runs.append((start, len(ok) - 1))

    def local_track(t_a, t_b):
        loc = np.linspace(t_a, t_b, 33)
        pos, _ = _ecef_track(elements, epoch, loc)
        return loc, _incidence_deg_array(pos, target)

    refined = []
    for i0, i1 in runs:
        lo, hi = float(track_times[i0]), float(track_times[i1])
        if lo > 0.0:
            loc, loc_inc = local_track(lo - step_s, lo)
            inside = (loc_inc >= band[0]) & (loc_inc <= band[1])
            if inside.any():
                lo = float(loc[int(np.argmax(inside))])
        if hi < float(track_times[-1]):
            loc, loc_inc = local_track(hi, hi + step_s)
            inside = (loc_inc >= band[0]) & (loc_inc <= band[1])
            if inside.any():
                hi = float(loc[len(inside) - 1 - int(np.argmax(inside[::-1]))])
        if hi > lo:
            refined.append((lo, hi))

    passes = []
    for lo, hi in refined:
        if passes and lo - passes[-1][1] < gap_merge_s:
            passes[-1][1] = hi
            passes[-1][2].append((lo, hi))
        else:
            passes.append([lo, hi, [(lo, hi)]])
    return [(lo, hi, tuple(rs)) for lo, hi, rs in passes]


def _pass_t_ca(elements, epoch, target, seg_lo, seg_hi, track_times, track_vsq):
    """Vector-squint minimum within a pass segment = the pass's t_ca.

    Coarse argmin from the shared track (enum step), then two local
    refinements (enum step / 2 grid, then a +-0.5 s grid at 0.05 s).  Makes
    NO unimodality assumption at the coarse stage (dense sampling).  The
    minimum may sit at a near-nadir point OUTSIDE the incidence band --
    that is fine: t_ca is the closest-approach anchor of the planar squint
    model, not an in-band point (the incidence leg of the cascade
    constrains the windows, AD-6)."""
    import numpy as np

    i0 = int(np.searchsorted(track_times, seg_lo))
    i1 = min(int(np.searchsorted(track_times, seg_hi)) + 1, len(track_times) - 1)
    j = i0 + int(np.argmin(track_vsq[i0:i1 + 1]))
    t0 = float(track_times[j])
    for half, n in ((R_ENUM_STEP_S, 31), (0.5, 21)):
        loc = np.linspace(t0 - half, t0 + half, n)
        pos, vel = _ecef_track(elements, epoch, loc)
        vsq = _vector_squint_deg_array(pos, vel, target)
        t0 = float(loc[int(np.argmin(vsq))])
    return t0


def generate_real_scenario(
    family_code: str,
    density_n: int,
    demand_tier: str,
    seed: int,
    variant_index: int | None = None,
    lib: ModeLibrary | None = None,
    platform=None,
) -> dict:
    """Generate one R<density><requirement> real-window scenario manifest.

    Ticket 25: each task carries a LIST of transit windows (``windows``:
    ``lo_s``/``hi_s``/``t_ca_s``/``r0_m``/``incidence_deg``/``width_s``,
    one entry per surviving cascade window).  Each window's ``t_ca_s`` is
    ITS OWN pass's squint zero -- reusing one zero across passes would
    mis-derive dwell / envelope / AASR (AD-3).  A window is the four-leg
    cascade ``incidence-band runs n squint envelope n end-check n AASR``
    (AD-6 puts the incidence leg INTO the intersection; R18).

    Determinism: the only stochastic source is ``random.Random(seed)``,
    consumed in a fixed per-target order (scatter -> demand -> size ->
    priority), and the platform orbit is passed in rather than drawn, so
    the same seed reproduces the manifest byte-identically.
    """
    import math as _math
    from datetime import timedelta

    from .duration import MarginPads as _Pads
    from .duration import duration_scene_s, mode_squint_envelope_rad
    from .realwindows import (
        GroundTarget,
        kepler_to_eci,
        satellite_to_target_vector,
    )
    from .windows import (
        effective_duration_fn,
        feasible_subintervals,
        intersect_intervals,
        mask_intervals,
    )
    from .aasr import aasr_direct as _aasr

    if demand_tier not in ("C", "F", "H"):
        raise ValueError(f"invalid demand tier {demand_tier!r}")
    if density_n not in R_DENSITY_BY_INDEX.values():
        raise ValueError(f"invalid density {density_n}")
    lib = lib or ModeLibrary.from_fixture()
    if platform is None:
        raise ValueError(
            "generate_real_scenario requires the platform orbit; refusing to "
            "invent one silently (the geometry is a registered input)"
        )
    elements, epoch = platform
    bands = load_rho_bands()
    pads = _Pads.standard()

    rng = random.Random(seed)
    tasks = []
    removals = {"below_finest": 0, "footprint": 0, "no_window": 0, "aasr": 0}
    # footprint attribution (ticket 23 R15 rule, generalized to N passes):
    # footprint removal iff at least one pass was footprint-evaluable AND
    # every evaluable pass failed; aasr removal iff at least one cascade
    # window REACHED the AASR gate but none survived it; no_window otherwise.
    h_draws = 0
    window_widths = []
    windows_per_task = []

    # shared coarse ECEF track: positions depend only on time, so the
    # kepler_to_eci loop runs ONCE per scenario and every target's incidence
    # is a vectorized read against it
    import numpy as np

    track_times = np.arange(0.0, R_SPAN_S + 0.5 * R_ENUM_STEP_S, R_ENUM_STEP_S)
    track_pos, track_vel = _ecef_track(elements, epoch, track_times)

    n_grid = R_GRID_N * R_GRID_N
    for idx in range(density_n):
        # fixed draw order: grid node -> scatter -> demand -> size -> priority
        node = idx % n_grid
        gi, gj = divmod(node, R_GRID_N)
        lon_scale = R_KM_PER_DEG_LAT * _math.cos(
            _math.radians(R_DOMAIN_CENTRE_DEG[0])
        )
        node_lat = R_DOMAIN_CENTRE_DEG[0] + (gi - R_GRID_N // 2) * (
            R_GRID_SPACING_KM / R_KM_PER_DEG_LAT
        )
        node_lon = R_DOMAIN_CENTRE_DEG[1] + (gj - R_GRID_N // 2) * (
            R_GRID_SPACING_KM / lon_scale
        )
        lat = node_lat + rng.uniform(-1.0, 1.0) * (
            R_SCATTER_HALF_CELL_KM / R_KM_PER_DEG_LAT
        )
        lon = node_lon + rng.uniform(-1.0, 1.0) * (
            R_SCATTER_HALF_CELL_KM / lon_scale
        )
        if demand_tier == "H":
            use_coarse = rng.random() < 0.5
            h_draws += int(use_coarse)
            band = bands["coarse"] if use_coarse else bands["fine"]
        else:
            band = bands["coarse"] if demand_tier == "C" else bands["fine"]
        rho_req = rng.uniform(*band)
        l_az_m = (
            rng.uniform(2000.0, 5000.0) if band == bands["coarse"]
            else rng.uniform(1000.0, 3000.0)
        )
        priority = rng.randint(1, 10)

        if rho_req < lib.rho_az(Mode.SPT) - 1e-12:
            removals["below_finest"] += 1
            continue

        target = GroundTarget(target_id=f"R{idx}", lat=lat, lon=lon)
        mode = route_mode(rho_req, lib)

        track_vsq = _vector_squint_deg_array(track_pos, track_vel, target)
        passes = _ground_track_passes(
            elements, epoch, target, track_times, track_pos,
            R_INCIDENCE_BAND_DEG, R_ENUM_STEP_S, R_GAP_MERGE_S,
        )
        env_rad = mode_squint_envelope_rad(mode)
        env_guard = env_rad * (1.0 - R_ENVELOPE_GUARD_FRACTION)

        fp_evaluable = fp_pass = fp_fail = 0
        task_windows = []
        reached_aasr = False
        for seg_lo, seg_hi, inc_runs in passes:
            t_ca = _pass_t_ca(
                elements, epoch, target, seg_lo, seg_hi, track_times, track_vsq
            )
            try:
                inc_ca = satellite_to_target_vector(
                    kepler_to_eci(elements, epoch + timedelta(seconds=t_ca)),
                    target,
                )[4]
                _, _, r0_pass = look_geometry(lib.geo.altitude_m, inc_ca)
            except ValueError:
                continue
            # ticket 23 (R15) per-pass footprint bound at THIS pass's own
            # closest-approach slant range
            fp_evaluable += 1
            if not footprint_ok(mode, l_az_m, lib, r0_m=r0_pass):
                fp_fail += 1
                continue
            fp_pass += 1

            env_iv = mask_intervals(
                (t_ca - R_PASS_SPAN_S, t_ca + R_PASS_SPAN_S),
                lambda dt, _t=t_ca, _r0=r0_pass: abs(
                    squint_at(dt, _t, lib.geo, r0_m=_r0)
                ) <= env_guard,
                n_scan=240,
            )
            if not env_iv:
                continue
            dur = lambda x, _t=t_ca, _r0=r0_pass: duration_scene_s(
                mode, squint_at(x, _t, lib.geo, r0_m=_r0), lib, r0_m=_r0
            )
            end_iv = []
            for lo, hi in env_iv:
                fw = feasible_subintervals(
                    effective_duration_fn(dur, pads), lo, hi, n_scan=240
                )
                end_iv.extend(fw.intervals)
            if not end_iv:
                continue
            # AD-6 (R18): the incidence leg JOINS the intersection -- the
            # emitted window is physically inside the 30-60 deg band
            window = intersect_intervals(
                tuple(inc_runs), tuple(env_iv), tuple(end_iv)
            )
            if not window:
                continue

            for lo, hi in window:
                reached_aasr = True
                aasr_vals: list[float] = []
                for j in range(11):
                    tt = lo + (hi - lo) * j / 10
                    try:
                        aasr_vals.append(_aasr(
                            mode, squint_at(tt, t_ca, lib.geo, r0_m=r0_pass),
                            lib.geo.k, PRF_PRODUCTION_HZ, lib,
                            spt_scene_wa_m=(l_az_m if mode is Mode.SPT else None),
                            r0_m=r0_pass,
                        )["aasr_db"])
                    except ValueError:
                        # out of the physical sliding domain at this sample:
                        # the window is not serviceable, so it can NEVER pass
                        # the threshold -- +inf, not -inf.  -inf would make an
                        # unserviceable sample the BEST one in the max() below,
                        # i.e. exactly the direction reversal this ticket fixes.
                        # Same convention as nsga2.py:195 and
                        # recompute_r_fam.py:109 (out-of-domain -> excluded /
                        # infinitely bad).
                        aasr_vals.append(float("+inf"))
                if not aasr_vals or max(aasr_vals) > AASR_THRESHOLD_DB:
                    continue
                mid = 0.5 * (lo + hi)
                inc_mid = satellite_to_target_vector(
                    kepler_to_eci(elements, epoch + timedelta(seconds=mid)),
                    target,
                )[4]
                width = hi - lo
                task_windows.append({
                    "lo_s": round(lo, 9),
                    "hi_s": round(hi, 9),
                    "t_ca_s": round(t_ca, 9),
                    "r0_m": round(r0_pass, 6),
                    "incidence_deg": round(inc_mid, 6),
                    "width_s": round(width, 6),
                })

        if task_windows:
            task_windows.sort(key=lambda w: w["lo_s"])
            window_widths.extend(w["width_s"] for w in task_windows)
            windows_per_task.append(len(task_windows))
            tasks.append({
                "t_start_s": task_windows[0]["lo_s"],
                "t_end_s": max(w["hi_s"] for w in task_windows),
                "azimuth_size_m": round(l_az_m, 6),
                "priority": priority,
                "rho_req_m": round(rho_req, 9),
                "mode": mode.name,
                "prf_hz": PRF_PRODUCTION_HZ,
                "lat_deg": round(lat, 6),
                "lon_deg": round(lon, 6),
                "windows": task_windows,
            })
        elif fp_evaluable and fp_pass == 0:
            removals["footprint"] += 1
        elif reached_aasr:
            removals["aasr"] += 1
        else:
            removals["no_window"] += 1

    assert sum(removals.values()) + len(tasks) == density_n, "R-family ledger"
    manifest = {
        "schema": "scenario-manifest/2.1-realwindow",
        "scenario": {
            "family_code": family_code,
            "density_n_targets": density_n,
            "demand_tier": demand_tier,
            "window_semantics": (
                "real-orbit per-transit four-leg cascade (ticket 25)"
            ),
            "platform_fixture": "experiments/platform_kim2021.json",
            # Ticket 16 acceptance item 8: the M-family (Paper-1 lineage) is
            # GLOBALLY DISPERSED inside a synthetic 300 s box; this family is
            # a single dense domain with geometrically determined windows.
            # The same nominal N therefore yields a different overload ratio,
            # and that difference is the density-axis material for the thesis.
            "predecessor_comparison": {
                "predecessor_family": "M<density><interval><demand>",
                "predecessor_topology": "globally dispersed, 300 s synthetic box",
                "this_topology": (
                    "single dense domain (5x5 grid, 250 km spacing, 1000 km "
                    "side, centre 20N/0E), enumerated real-orbit transits"
                ),
                "overload_ratio_served_over_drawn": (
                    round(len(tasks) / density_n, 6) if density_n else 0.0
                ),
                "note": (
                    "window width is a physical quantity here, so overload "
                    "ratio is not comparable to the M-family value at equal N "
                    "without accounting for the geometry"
                ),
            },
        },
        "preregistration": {
            "seed": seed,
            "variant_index": variant_index,
            "seed_rule": "variant_index*100 + seed_index (ticket-02 template)",
            "pads": {
                "inter_task_fraction": pads.inter_task_fraction,
                "window_tail_fraction": pads.window_tail_fraction,
            },
            "prf_production_hz": PRF_PRODUCTION_HZ,
            "priority_convention": "randint(1,10) (Paper-1 generate_all_scenarios.py:133)",
            "domain_centre_deg": list(R_DOMAIN_CENTRE_DEG),
            "domain_side_km": R_DOMAIN_SIDE_KM,
            "grid_n": R_GRID_N,
            "grid_spacing_km": R_GRID_SPACING_KM,
            "scatter_half_cell_km": R_SCATTER_HALF_CELL_KM,
            "grid_assignment_rule": "target i -> node i % 25 (row-major), jitter within own cell",
            "span_days": R_SPAN_DAYS,
            "enum_step_s": R_ENUM_STEP_S,
            "gap_merge_s": R_GAP_MERGE_S,
            "gap_merge_robustness_s": list(R_GAP_MERGE_ROBUST_S),
            "incidence_band_deg": list(R_INCIDENCE_BAND_DEG),
            "pass_enumeration_rule": (
                "per target: coarse incidence scan over the span at "
                "enum_step_s, in-band runs refined by a 33-point local "
                "grid per edge (resolution enum_step_s/32), runs "
                "clustered into passes at gap_merge_s; per pass t_ca = "
                "vector-squint minimum of the segment; windows = "
                "incidence runs n envelope n end-check n AASR (AD-2/AD-6)"
            ),
        },
        "generation_ledger": {
            "n_drawn": density_n,
            "removals": removals,
            "n_served": len(tasks),
            "h_coarse_draws": h_draws,
            "n_windows_total": sum(windows_per_task),
            "windows_per_task_max": max(windows_per_task) if windows_per_task else 0,
            "window_width_s_mean": (
                round(sum(window_widths) / len(window_widths), 6)
                if window_widths else 0.0
            ),
            "window_width_s_min": round(min(window_widths), 6) if window_widths else 0.0,
            "window_width_s_max": round(max(window_widths), 6) if window_widths else 0.0,
        },
        "tasks": tasks,
    }
    return manifest


def write_manifest(manifest: dict, path: Path) -> None:
    """Byte-stable manifest write (sorted keys; the same-seed rerun must
    produce an identical file, spec 确定性)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
