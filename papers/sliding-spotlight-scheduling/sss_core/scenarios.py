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


# ── real-window family R<density><requirement> (ticket 16) ───────────────
#
# The 300 s box retires here: each task's window is the three-leg cascade
# (incidence mask n mode envelope n end-check) computed from real orbit
# geometry, so its width is a physical quantity rather than a constant.
#
# Cluster geometry is PREREGISTERED (ticket acceptance item 5): cluster
# centres on a fixed lat/lon grid, cluster scale L, density N and demand tier
# are all bound before any run, and the seed rule is the matrix convention
# (variant_index*100 + seed_index).
R_CLUSTER_CENTRES_DEG = (
    (56.0, 22.0), (34.0, -118.0), (-12.0, -46.0), (48.0, 121.0),
    (-33.0, 151.0), (20.0, 77.0), (62.0, -70.0), (5.0, 100.0),
)
R_CLUSTER_SCALE_KM = 20.0        # cluster radius; targets scatter inside it
R_PASS_SPAN_S = 120.0            # per-side propagation span around the pass
R_PROP_STEP_S = 1.0              # geometry sampling step
R_PASSES = 2                     # ticket: longest visible window over 2 passes
R_INCIDENCE_BAND_DEG = (30.0, 60.0)
R_DENSITY_BY_INDEX = {1: 20, 2: 100, 3: 300, 4: 500}
R_FAMILY_REGISTRY = {
    1: ("R1C", 20, "C"),
    2: ("R2F", 100, "F"),
    3: ("R3H", 300, "H"),
    4: ("R4H", 500, "H"),
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


# ── real-window family generator (ticket 16) ─────────────────────────────

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

    Each task gets a window that is the three-leg cascade over real orbit
    geometry: incidence mask (from the forked ``realwindows`` kernel) n mode
    squint envelope n end-check.  Nothing here re-derives a leg's predicate;
    the legs are computed by their owners and ``intersect_intervals`` only
    intersects.

    Two squint zero points are registered per task and they are NOT the same
    point (measured: the vector squint minimum sits 600 s away from the
    ``squint_at`` zero).  ``t_ca_s`` is the ``squint_at`` zero that drives the
    dwell; ``vector_squint_min_t_s`` is the vector minimum that the incidence
    mask is evaluated at.

    Determinism: the only stochastic source is ``random.Random(seed)``,
    consumed in a fixed per-target order, and the platform orbit is passed in
    rather than drawn, so the same seed reproduces the manifest byte-identically.
    """
    import math as _math
    from datetime import datetime, timedelta

    from .duration import MarginPads as _Pads
    from .duration import duration_scene_s, mode_squint_envelope_rad, pad_window_tail
    from .realwindows import (
        ECIState,
        GroundTarget,
        KeplerianElement,
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
    step = timedelta(seconds=R_PROP_STEP_S)
    span = timedelta(seconds=R_PASS_SPAN_S)

    rng = random.Random(seed)
    tasks = []
    removals = {"below_finest": 0, "footprint": 0, "no_window": 0, "aasr": 0}
    h_draws = 0
    window_widths = []

    n_clusters = len(R_CLUSTER_CENTRES_DEG)
    for idx in range(density_n):
        # fixed draw order: cluster -> demand -> size -> priority
        clat, clon = R_CLUSTER_CENTRES_DEG[idx % n_clusters]
        # scatter inside the cluster (a few km, well inside R_CLUSTER_SCALE_KM)
        scale = R_CLUSTER_SCALE_KM * 1000.0
        lat = clat + rng.uniform(-1.0, 1.0) * (scale / 111_320.0)
        lon = clon + rng.uniform(-1.0, 1.0) * (
            scale / (111_320.0 * max(_math.cos(_math.radians(clat)), 1e-6))
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
        if not footprint_ok(mode, l_az_m, lib):
            removals["footprint"] += 1
            continue

        # two passes (ticket: longest visible window over 2 orbit passes)
        best = None
        for pass_i in range(R_PASSES):
            t0 = epoch + timedelta(seconds=pass_i * 600.0)
            state = lambda dt, _s=t0: kepler_to_eci(elements, _s + timedelta(seconds=dt))

            def incidence_ok(dt, _st=state, _tg=target):
                try:
                    *_, inc_deg, _look, _sq = satellite_to_target_vector(
                        _st(dt), _tg
                    )
                except ValueError:
                    return False
                return R_INCIDENCE_BAND_DEG[0] <= inc_deg <= R_INCIDENCE_BAND_DEG[1]

            inc_iv = mask_intervals((-R_PASS_SPAN_S, R_PASS_SPAN_S),
                                    incidence_ok, n_scan=240)
            if not inc_iv:
                continue
            # vector-squint minimum inside the incidence leg
            cand = [
                (abs(satellite_to_target_vector(state(0.5 * (lo + hi)), target)[6]), 0.5 * (lo + hi))
                for lo, hi in inc_iv
            ]
            vmin_t, tca = min(cand)

            env_rad = mode_squint_envelope_rad(mode)
            env_iv = mask_intervals(
                (tca - R_PASS_SPAN_S, tca + R_PASS_SPAN_S),
                lambda dt, _t=tca: abs(
                    squint_at(dt, _t, lib.geo)
                ) <= env_rad,
                n_scan=240,
            )
            if not env_iv:
                continue
            dur = lambda x, _t=tca: duration_scene_s(
                mode, squint_at(x, _t, lib.geo), lib
            )
            end_iv = []
            for lo, hi in env_iv:
                fw = feasible_subintervals(
                    effective_duration_fn(dur, pads), lo, hi, n_scan=240
                )
                end_iv.extend(fw.intervals)
            if not end_iv:
                continue
            window = intersect_intervals(
                tuple(env_iv), tuple(end_iv)
            )
            if not window:
                continue
            width = sum(hi - lo for lo, hi in window)
            if best is None or width > best[0]:
                best = (width, window, tca, vmin_t, pass_i)

        if best is None:
            removals["no_window"] += 1
            continue

        width, window, t_ca, vmin_t, pass_i = best
        w_lo = min(lo for lo, _ in window)
        w_hi = max(hi for _, hi in window)
        mid = 0.5 * (w_lo + w_hi)
        # per-task geometry for the manifest (ticket piece 1/3)
        geo_at = satellite_to_target_vector(
            kepler_to_eci(elements, epoch + timedelta(seconds=pass_i * 600.0 + mid)),
            target,
        )
        incidence_deg = geo_at[4]
        _, _, r0_m = look_geometry(lib.geo.altitude_m, incidence_deg)
        aasr_db = _aasr(
            mode, squint_at(mid, t_ca, lib.geo), lib.geo.k,
            PRF_PRODUCTION_HZ, lib,
            spt_scene_wa_m=(l_az_m if mode is Mode.SPT else None),
        )["aasr_db"]
        if not (aasr_db <= AASR_THRESHOLD_DB):
            removals["aasr"] += 1
            continue

        window_widths.append(width)
        tasks.append({
            "t_start_s": round(w_lo, 9),
            "t_end_s": round(w_hi, 9),
            "t_ca_s": round(t_ca, 9),
            "azimuth_size_m": round(l_az_m, 6),
            "priority": priority,
            "rho_req_m": round(rho_req, 9),
            "mode": mode.name,
            "prf_hz": PRF_PRODUCTION_HZ,
            # ── per-task real geometry (ticket 16, piece 1/3) ──
            "r0_m": round(r0_m, 6),
            "incidence_deg": round(incidence_deg, 6),
            "vector_squint_min_t_s": round(vmin_t, 9),
            "lat_deg": round(lat, 6),
            "lon_deg": round(lon, 6),
            "window_width_s": round(width, 6),
        })

    assert sum(removals.values()) + len(tasks) == density_n, "R-family ledger"
    manifest = {
        "schema": "scenario-manifest/2.0-realwindow",
        "scenario": {
            "family_code": family_code,
            "density_n_targets": density_n,
            "demand_tier": demand_tier,
            "window_semantics": "real-orbit three-leg cascade",
            "platform_fixture": "experiments/platform_kim2021.json",
            # Ticket 16 acceptance item 8: the M-family (Paper-1 lineage) is
            # GLOBALLY DISPERSED inside a synthetic 300 s box; this family is
            # REGIONALLY CLUSTERED with geometrically determined windows.  The
            # same nominal N therefore yields a different overload ratio, and
            # that difference is the density-axis material for the thesis.
            # Recorded here rather than in prose so the comparison is
            # greppable alongside the numbers it explains.
            "predecessor_comparison": {
                "predecessor_family": "M<density><interval><demand>",
                "predecessor_topology": "globally dispersed, 300 s synthetic box",
                "this_topology": (
                    "regionally clustered (8 fixed centres, 20 km scale), "
                    "real-orbit windows"
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
            "cluster_centres_deg": [list(c) for c in R_CLUSTER_CENTRES_DEG],
            "cluster_scale_km": R_CLUSTER_SCALE_KM,
            "pass_span_s": R_PASS_SPAN_S,
            "prop_step_s": R_PROP_STEP_S,
            "passes": R_PASSES,
            "incidence_band_deg": list(R_INCIDENCE_BAND_DEG),
            "pass_selection_rule": (
                f"longest visible window over {R_PASSES} passes (D13)"
            ),
        },
        "generation_ledger": {
            "n_drawn": density_n,
            "removals": removals,
            "n_served": len(tasks),
            "h_coarse_draws": h_draws,
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
