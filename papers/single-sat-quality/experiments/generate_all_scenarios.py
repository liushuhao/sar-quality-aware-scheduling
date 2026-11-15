"""
Phase 6: Comprehensive Scenario Generator for S1-S6
====================================================
Generates all 6 scenario groups per experiment-design.md §2.4.

For EOS-Bench sourced scenarios (S2-A/B/C, S3-A/B/C/D/E), generates
self-built fallbacks with matching distribution types.

Output: .pkl files in experiments/scenarios/S1/ through S6/
Each .pkl contains: targets, windows, windows_by_target, instrument,
                    n_targets, seed, stats, config, satellite
"""

import sys, os, pickle, random, time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

# ─── Path Setup ──────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from sar_sim.types import GroundTarget, SARInstrument, KeplerianElement, ObservationWindow
from sar_sim.generator.orbit import propagate_orbit
from sar_sim.generator.target import lat_lon_to_ecef, eci_to_ecef_rotation, EARTH_EQUATORIAL_RADIUS
from sar_sim.metrics.nesz import EARTH_RADIUS_MEAN_M
from sar_sim.generator.visibility import (
    _compute_off_nadir_angle, _off_nadir_to_incidence,
    _determine_look_direction, _check_geometric_constraints
)

PROJECT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = PROJECT / "experiments" / "scenarios"
MU_EARTH = 3.986004418e14
DEFAULT_EPOCH = datetime(2026, 6, 15, 0, 0, 0)

# ─── Satellite Parameter Sets ────────────────────────────────────────────
SENTINEL1 = {
    "altitude_km": 693.0,
    "incidence_min": 18.0,
    "incidence_max": 47.0,
    "inclination_deg": 97.8,
    "name": "Sentinel-1",
}
ICEYE = {
    "altitude_km": 550.0,
    "incidence_min": 15.0,
    "incidence_max": 35.0,
    "inclination_deg": 97.6,
    "name": "ICEYE",
}

# ══════════════════════════════════════════════════════════════════════════
# Orbit & Visibility Utilities (adapted from generate_s4_s6.py)
# ══════════════════════════════════════════════════════════════════════════

def make_orbit(altitude_km: float, ltan: float = 6.0,
               epoch: datetime = None) -> KeplerianElement:
    """Create sun-synchronous orbit at given altitude."""
    if epoch is None:
        epoch = DEFAULT_EPOCH
    semi_major_axis = (altitude_km * 1000.0) + EARTH_EQUATORIAL_RADIUS
    inclination = np.radians(97.8 if altitude_km >= 500 else 97.6)
    raan = np.radians(ltan * 15.0)
    return KeplerianElement(
        semi_major_axis=semi_major_axis, eccentricity=0.0,
        inclination=inclination, raan=raan,
        arg_perigee=0.0, true_anomaly=0.0, epoch=epoch,
    )

def get_swath_params(altitude_km: float, incidence_max: float) -> Tuple[float, float]:
    """Compute swath half-width in km and degrees."""
    R_e = EARTH_RADIUS_MEAN_M
    h = altitude_km * 1000.0
    ratio = R_e / (R_e + h)
    sin_eta_max = ratio * np.sin(np.radians(incidence_max))
    sin_eta_max = np.clip(sin_eta_max, -1.0, 1.0)
    eta_max_deg = np.degrees(np.arcsin(sin_eta_max))
    swath_half_km = altitude_km * np.tan(np.radians(eta_max_deg))
    swath_half_deg = swath_half_km / 111.32
    return swath_half_km, swath_half_deg

def propagate_ground_track(orbit: KeplerianElement, n_orbits: int = 2,
                           step: timedelta = timedelta(seconds=10)) -> List[Tuple[float, float]]:
    """Propagate orbit and return ground track as (lat, lon) points."""
    a = orbit.semi_major_axis
    period_s = 2 * np.pi * np.sqrt(a**3 / MU_EARTH)
    t_start = orbit.epoch
    t_end = t_start + timedelta(seconds=n_orbits * period_s)

    states = propagate_orbit(orbit, t_start, t_end, step)
    e2 = 0.00669437999014

    track = []
    for state in states:
        R = eci_to_ecef_rotation(state.time.timestamp())
        sat_ecef = R @ state.position
        x, y, z = sat_ecef[0], sat_ecef[1], sat_ecef[2]
        r_xy = np.sqrt(x**2 + y**2)
        lon = np.degrees(np.arctan2(y, x))
        lat = np.degrees(np.arctan2(z, r_xy * (1 - e2)))
        track.append((float(lat), float(lon)))
    return track

# ══════════════════════════════════════════════════════════════════════════
# Target Generation Functions
# ══════════════════════════════════════════════════════════════════════════

def _clamp_latlon(lat: float, lon: float) -> Tuple[float, float]:
    lat = max(-90.0, min(90.0, lat))
    lon = (lon + 180) % 360 - 180
    return lat, lon

def _scatter_around_track(track: List[Tuple[float, float]],
                           swath_half_deg: float) -> Tuple[float, float]:
    """Pick a random track point and scatter within swath."""
    idx = random.randint(0, len(track) - 1)
    tlat, tlon = track[idx]
    cross_offset = random.uniform(-swath_half_deg, swath_half_deg)
    cos_lat = max(np.cos(np.radians(tlat)), 0.1)
    lat = tlat + random.uniform(-0.5, 0.5) * cross_offset
    lon = tlon + cross_offset / cos_lat
    return _clamp_latlon(lat, lon)

def generate_targets_uniform(n: int, track: List[Tuple[float, float]],
                              swath_half_deg: float) -> List[GroundTarget]:
    """Uniform random targets along ground track."""
    targets = []
    for i in range(n):
        lat, lon = _scatter_around_track(track, swath_half_deg)
        targets.append(GroundTarget(
            target_id=f"T{i:04d}", lat=lat, lon=lon,
            priority=random.randint(1, 10),
        ))
    return targets

def generate_targets_clustered(n: int, track: List[Tuple[float, float]],
                                swath_half_deg: float,
                                n_clusters: int = 5) -> List[GroundTarget]:
    """Clustered targets: n_clusters centers scattered around."""
    if len(track) < n_clusters:
        n_clusters = len(track)
    centers = random.sample(track, n_clusters)
    targets = []
    idx = 0
    per_cluster = n // n_clusters
    remainder = n % n_clusters
    for clat, clon in centers:
        count = per_cluster + (1 if idx < remainder else 0)
        idx += 1
        for _ in range(count):
            lat = clat + random.uniform(-swath_half_deg, swath_half_deg)
            lon = clon + random.uniform(-swath_half_deg, swath_half_deg)
            lat, lon = _clamp_latlon(lat, lon)
            targets.append(GroundTarget(
                target_id=f"T{len(targets):04d}", lat=lat, lon=lon,
                priority=random.randint(1, 10),
            ))
    return targets

def generate_targets_mixed(n: int, track: List[Tuple[float, float]],
                            swath_half_deg: float,
                            n_clusters: int = 3) -> List[GroundTarget]:
    """Mixed: half uniform random, half clustered."""
    n_random = n // 2
    n_clustered = n - n_random

    targets = []
    # Random half
    for i in range(n_random):
        lat, lon = _scatter_around_track(track, swath_half_deg)
        targets.append(GroundTarget(
            target_id=f"T{i:04d}", lat=lat, lon=lon,
            priority=random.randint(1, 10),
        ))
    # Clustered half
    if len(track) < n_clusters:
        n_clusters = len(track)
    centers = random.sample(track, n_clusters)
    per = n_clustered // n_clusters
    rem = n_clustered % n_clusters
    for ci, (clat, clon) in enumerate(centers):
        count = per + (1 if ci < rem else 0)
        for _ in range(count):
            lat = clat + random.uniform(-swath_half_deg, swath_half_deg)
            lon = clon + random.uniform(-swath_half_deg, swath_half_deg)
            lat, lon = _clamp_latlon(lat, lon)
            targets.append(GroundTarget(
                target_id=f"T{len(targets):04d}", lat=lat, lon=lon,
                priority=random.randint(1, 10),
            ))
    return targets

def generate_targets_highlat(n: int, track: List[Tuple[float, float]],
                              swath_half_deg: float) -> List[GroundTarget]:
    """Uniform targets at higher latitudes (±40° to ±70°)."""
    targets = []
    for i in range(n):
        # Pick a track point, bias latitude to higher values
        tlat, tlon = random.choice(track)
        # Override latitude with high-latitude range
        lat = random.uniform(40.0, 70.0) * random.choice([1, -1])
        cross_offset = random.uniform(-swath_half_deg, swath_half_deg)
        cos_lat = max(np.cos(np.radians(lat)), 0.1)
        lon = tlon + cross_offset / cos_lat
        lat, lon = _clamp_latlon(lat, lon)
        targets.append(GroundTarget(
            target_id=f"T{i:04d}", lat=lat, lon=lon,
            priority=random.randint(1, 10),
        ))
    return targets

def generate_targets_s5_spread(n: int, track: List[Tuple[float, float]],
                                swath_half_deg: float,
                                along_track_spread_deg: float,
                                base_seed: int) -> List[GroundTarget]:
    """S5: targets within controlled along-track spread, same base positions.

    Uses base_seed for deterministic target anchor positions, then
    scales/scatters them within the specified along-track spread range.
    """
    # Use base_seed to get deterministic anchor points
    rng = random.Random(base_seed + 20000)
    np_rng = np.random.RandomState(base_seed + 20000)

    # Find mid-lon of track
    mid_idx = len(track) // 2
    mid_lat, mid_lon = track[mid_idx]

    targets = []
    for i in range(n):
        # Along-track position: uniform within spread
        along_offset = rng.uniform(-along_track_spread_deg, along_track_spread_deg)
        # Cross-track: scatter within swath
        cross_offset = rng.uniform(-swath_half_deg, swath_half_deg)

        cos_lat = max(np.cos(np.radians(mid_lat)), 0.1)
        lat = mid_lat + rng.uniform(-0.3, 0.3) * cross_offset
        lon = mid_lon + along_offset + cross_offset / cos_lat
        lat, lon = _clamp_latlon(lat, lon)

        targets.append(GroundTarget(
            target_id=f"T{i:04d}", lat=lat, lon=lon,
            priority=rng.randint(1, 10),
        ))
    return targets

def generate_targets_s6_clusters(n: int, track: List[Tuple[float, float]],
                                  swath_half_deg: float,
                                  n_clusters: int,
                                  cluster_size: int) -> List[GroundTarget]:
    """S6: dense along-track clusters for C3 stress testing.

    Clusters are spaced evenly along the orbit track. Targets within
    each cluster are placed close together along-track.
    """
    # Pick n_clusters evenly spaced track points
    step = max(1, len(track) // n_clusters)
    cluster_centers = [track[i * step] for i in range(n_clusters)]

    # Ensure we have enough centers
    if len(cluster_centers) > len(track):
        cluster_centers = track[:n_clusters]

    targets = []
    tid = 0
    cluster_spread = 0.5  # degrees — tight along-track clustering

    for clat, clon in cluster_centers:
        for _ in range(cluster_size):
            # Place target very close to cluster center along-track
            along_offset = random.uniform(-cluster_spread, cluster_spread)
            cross_offset = random.uniform(-swath_half_deg, swath_half_deg)

            cos_lat = max(np.cos(np.radians(clat)), 0.1)
            lat = clat + random.uniform(-0.2, 0.2) * cross_offset
            lon = clon + along_offset + cross_offset / cos_lat
            lat, lon = _clamp_latlon(lat, lon)

            targets.append(GroundTarget(
                target_id=f"T{tid:04d}", lat=lat, lon=lon,
                priority=random.randint(1, 10),
            ))
            tid += 1

        if len(targets) >= n:
            break

    # Fill remaining if needed
    while len(targets) < n:
        lat, lon = _scatter_around_track(track, swath_half_deg)
        targets.append(GroundTarget(
            target_id=f"T{len(targets):04d}", lat=lat, lon=lon,
            priority=random.randint(1, 10),
        ))

    return targets

# ══════════════════════════════════════════════════════════════════════════
# Batch Visibility Computation
# ══════════════════════════════════════════════════════════════════════════

def compute_batch_visibility(orbit: KeplerianElement, satellite_id: str,
                              targets: List[GroundTarget], instrument: SARInstrument,
                              t_start: datetime, t_end: datetime,
                              step: timedelta, altitude_km: float,
                              max_window_width_s: Optional[float] = None
                              ) -> Dict[str, List[ObservationWindow]]:
    """Compute visibility windows for all targets over the time range.

    If max_window_width_s is set, windows are truncated to at most
    that width (centered on t_optimal). Used for S6 narrow-window scenarios.
    """
    states = propagate_orbit(orbit, t_start, t_end, step)
    if len(states) == 0:
        return {}

    target_ecef_map = {tgt.target_id: lat_lon_to_ecef(tgt.lat, tgt.lon) for tgt in targets}
    in_window = {tgt.target_id: False for tgt in targets}
    window_start = {tgt.target_id: None for tgt in targets}
    best_elev = {tgt.target_id: -999.0 for tgt in targets}
    best_off_nadir = {tgt.target_id: 0.0 for tgt in targets}
    best_look = {tgt.target_id: "right" for tgt in targets}
    best_time = {tgt.target_id: None for tgt in targets}
    last_pass_time = {tgt.target_id: None for tgt in targets}
    results = {tgt.target_id: [] for tgt in targets}

    h_sat_m = altitude_km * 1000.0

    for state in states:
        R_eci_to_ecef = eci_to_ecef_rotation(state.time.timestamp())
        sat_ecef = R_eci_to_ecef @ state.position
        sat_vel_ecef = R_eci_to_ecef @ state.velocity

        for tgt in targets:
            tid = tgt.target_id
            target_ecef = target_ecef_map[tid]
            los = target_ecef - sat_ecef
            distance = np.linalg.norm(los)
            sin_elev = (h_sat_m**2 + 2 * EARTH_RADIUS_MEAN_M * h_sat_m - distance**2) / (
                2 * EARTH_RADIUS_MEAN_M * distance)
            sin_elev = np.clip(sin_elev, -1.0, 1.0)
            elev = np.degrees(np.arcsin(sin_elev))
            off_nadir = _compute_off_nadir_angle(sat_ecef, target_ecef)
            incidence = _off_nadir_to_incidence(off_nadir, h_sat_m)
            look = _determine_look_direction(sat_ecef, sat_vel_ecef, target_ecef)

            # Squint angle (along-track LOS component) — must match
            # satellite_to_target_vector() in visibility.py to ensure C1
            # squint filtering is consistent across both code paths.
            los_unit = los / distance
            track_dir = sat_vel_ecef / np.linalg.norm(sat_vel_ecef)
            los_along = np.dot(los_unit, track_dir)
            squint = np.degrees(np.arcsin(np.clip(abs(los_along), 0.0, 1.0)))

            passes = _check_geometric_constraints(elev, incidence, look, instrument, squint)

            if passes:
                last_pass_time[tid] = state.time
                if not in_window[tid]:
                    in_window[tid] = True
                    window_start[tid] = state.time
                    best_elev[tid] = elev
                    best_off_nadir[tid] = off_nadir
                    best_look[tid] = look
                    best_time[tid] = state.time
                else:
                    if elev > best_elev[tid]:
                        best_elev[tid] = elev
                        best_off_nadir[tid] = off_nadir
                        best_look[tid] = look
                        best_time[tid] = state.time
            else:
                if in_window[tid]:
                    in_window[tid] = False
                    results[tid].append(ObservationWindow(
                        satellite_id=satellite_id, target_id=tid,
                        t_start=window_start[tid], t_end=last_pass_time[tid],
                        t_optimal=best_time[tid], elevation=best_elev[tid],
                        off_nadir_angle=best_off_nadir[tid],
                        look_direction=best_look[tid], duration_min=30.0,
                    ))

    # Close any still-open windows
    for tgt in targets:
        tid = tgt.target_id
        if in_window[tid]:
            results[tid].append(ObservationWindow(
                satellite_id=satellite_id, target_id=tid,
                t_start=window_start[tid], t_end=last_pass_time[tid],
                t_optimal=best_time[tid], elevation=best_elev[tid],
                off_nadir_angle=best_off_nadir[tid],
                look_direction=best_look[tid], duration_min=30.0,
            ))

    # Post-process: truncate windows to max width (S6 narrow windows)
    if max_window_width_s is not None:
        for tid in results:
            truncated = []
            for win in results[tid]:
                # Center on t_optimal
                half_width = timedelta(seconds=max_window_width_s / 2)
                new_start = max(win.t_start, win.t_optimal - half_width)
                new_end = min(win.t_end, win.t_optimal + half_width)
                if new_end > new_start:
                    # Create a new window with truncated times
                    truncated.append(ObservationWindow(
                        satellite_id=win.satellite_id,
                        target_id=win.target_id,
                        t_start=new_start,
                        t_end=new_end,
                        t_optimal=win.t_optimal,
                        elevation=win.elevation,
                        off_nadir_angle=win.off_nadir_angle,
                        look_direction=win.look_direction,
                        duration_min=win.duration_min,
                    ))
            results[tid] = truncated

    return results

# ══════════════════════════════════════════════════════════════════════════
# Single Scenario Generator
# ══════════════════════════════════════════════════════════════════════════

def generate_one_scenario(
    n_targets: int,
    seed: int,
    sat_params: dict,  # SENTINEL1 or ICEYE
    dist_type: str = "uniform",
    look_direction: str = "both",
    n_orbits: int = 2,
    n_clusters: int = 5,
    s5_spread_deg: Optional[float] = None,
    s5_base_seed: Optional[int] = None,
    s6_n_clusters: Optional[int] = None,
    s6_cluster_size: Optional[int] = None,
    max_window_width_s: Optional[float] = None,
    high_lat: bool = False,
    max_squint_deg: Optional[float] = None,
) -> dict:
    """Generate a single scenario with the given parameters."""
    random.seed(seed)
    np.random.seed(seed)

    altitude_km = sat_params["altitude_km"]
    incidence_min = sat_params["incidence_min"]
    incidence_max = sat_params["incidence_max"]

    instrument_kwargs = dict(
        incidence_min=incidence_min,
        incidence_max=incidence_max,
        look_direction=look_direction,
        antenna_type="reflector",
        min_elevation=5.0,
    )
    if max_squint_deg is not None:
        instrument_kwargs["max_squint_deg"] = max_squint_deg
    instrument = SARInstrument(**instrument_kwargs)

    orbit = make_orbit(altitude_km, ltan=6.0)

    a = orbit.semi_major_axis
    period_s = 2 * np.pi * np.sqrt(a**3 / MU_EARTH)
    t_start = orbit.epoch
    t_end = t_start + timedelta(seconds=n_orbits * period_s)
    step = timedelta(seconds=10)

    swath_half_km, swath_half_deg = get_swath_params(altitude_km, incidence_max)
    track = propagate_ground_track(orbit, n_orbits=n_orbits, step=step)

    if len(track) < 10:
        raise RuntimeError(f"Too few track points: {len(track)}")

    # Generate targets based on distribution type
    if s5_spread_deg is not None:
        # S5: along-track spread controlled
        targets = generate_targets_s5_spread(
            n_targets, track, swath_half_deg,
            along_track_spread_deg=s5_spread_deg,
            base_seed=s5_base_seed if s5_base_seed is not None else seed,
        )
    elif s6_n_clusters is not None and s6_cluster_size is not None:
        # S6: C3 cluster stress
        targets = generate_targets_s6_clusters(
            n_targets, track, swath_half_deg,
            n_clusters=s6_n_clusters,
            cluster_size=s6_cluster_size,
        )
    elif high_lat:
        targets = generate_targets_highlat(n_targets, track, swath_half_deg)
    elif dist_type == "uniform":
        targets = generate_targets_uniform(n_targets, track, swath_half_deg)
    elif dist_type == "clustered":
        targets = generate_targets_clustered(n_targets, track, swath_half_deg, n_clusters)
    elif dist_type == "mixed":
        targets = generate_targets_mixed(n_targets, track, swath_half_deg, n_clusters=2)
    else:
        raise ValueError(f"Unknown dist_type: {dist_type}")

    # Compute visibility
    t0 = time.time()
    windows_dict = compute_batch_visibility(
        orbit, "SAT-01", targets, instrument,
        t_start, t_end, step, altitude_km,
        max_window_width_s=max_window_width_s,
    )
    compute_time = time.time() - t0

    all_windows = []
    for wlist in windows_dict.values():
        all_windows.extend(wlist)

    n_with = sum(1 for wlist in windows_dict.values() if len(wlist) > 0)

    return {
        "targets": targets,
        "windows": all_windows,
        "windows_by_target": windows_dict,
        "config": {
            "t_start": t_start, "t_end": t_end,
            "period_s": period_s, "n_orbits_simulated": n_orbits,
        },
        "satellite": {
            "id": "SAT-01", "altitude_km": altitude_km,
            "inclination_deg": sat_params["inclination_deg"], "ltan_h": 6.0,
            "name": sat_params["name"],
        },
        "instrument": instrument,
        "seed": seed,
        "n_targets": n_targets,
        "stats": {
            "n_targets_total": n_targets,
            "n_with_windows": n_with,
            "total_windows": len(all_windows),
            "compute_time_s": compute_time,
        },
    }

# ══════════════════════════════════════════════════════════════════════════
# Main: Generate All Scenarios
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("PHASE 6: COMPREHENSIVE SCENARIO GENERATOR (S1-S6)")
    print("Per experiment-design.md §2.4 (revised 2026-06-16)")
    print("=" * 70)

    # ─── Common generation helper ────────────────────────────────────────
    def gen_group(group: str, labels: list, seeds_per: int,
                  param_fn, skip_existing: bool = True):
        """Generate a scenario group.

        param_fn(seed_idx, seed, dist_idx) -> dict of kwargs for generate_one_scenario
        """
        out_dir = OUTPUT_ROOT / group
        out_dir.mkdir(parents=True, exist_ok=True)
        total = 0
        skipped = 0

        for dist_idx, label in enumerate(labels):
            for seed_idx in range(seeds_per):
                seed = dist_idx * 100 + seed_idx
                fname = f"{label}_seed{seed_idx:02d}.pkl"
                fpath = out_dir / fname

                if skip_existing and fpath.exists():
                    skipped += 1
                    continue

                kwargs = param_fn(seed_idx, seed, dist_idx)
                scenario = generate_one_scenario(**kwargs)

                with open(fpath, "wb") as f:
                    pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)

                stats = scenario["stats"]
                print(f"  [{group}] {fname}: {stats['n_with_windows']}/{stats['n_targets_total']} "
                      f"visible, {stats['total_windows']} windows, {stats['compute_time_s']:.1f}s")
                total += 1

        if skipped:
            print(f"  [{group}] Skipped {skipped} existing files")
        print(f"  [{group}] Generated {total} new scenarios\n")

    # ──────────────────────────────────────────────────────────────────────
    # S1: Small (N=20, Sentinel-1, bilateral)
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S1: N=20, Sentinel-1, 693km, bilateral ---")
    s1_labels = ["S1-A", "S1-B", "S1-C", "S1-D", "S1-E"]

    def s1_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 20, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:  # S1-A: Uniform random
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:  # S1-B: Clustered (5 clusters × 4)
            return {**base, "dist_type": "clustered", "n_clusters": 5}
        elif dist_idx == 2:  # S1-C: Mixed (10 random + 2 clusters × 5)
            return {**base, "dist_type": "mixed", "n_clusters": 2}
        elif dist_idx == 3:  # S1-D: Uniform, narrow window (1 orbit)
            return {**base, "dist_type": "uniform", "n_orbits": 1}
        elif dist_idx == 4:  # S1-E: Uniform, wide θ [18°,47°]
            # Already using full Sentinel-1 range
            return {**base, "dist_type": "uniform"}

    gen_group("S1", s1_labels, 10, s1_params)

    # ──────────────────────────────────────────────────────────────────────
    # S2: Medium (N=100, Sentinel-1, bilateral)
    # Note: S2-A/B/C are EOS-Bench sourced → generated as self-built fallback
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S2: N=100, Sentinel-1, 693km, bilateral ---")
    print("  [NOTE] S2-A/B/C: self-built fallback (EOS-Bench not available)")
    s2_labels = ["S2-A", "S2-B", "S2-C", "S2-D", "S2-E"]

    def s2_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 100, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:  # S2-A: Random (EOS-Bench fallback → uniform)
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:  # S2-B: Clustered (EOS-Bench fallback → clustered)
            return {**base, "dist_type": "clustered", "n_clusters": 10}
        elif dist_idx == 2:  # S2-C: Hybrid (EOS-Bench fallback → mixed)
            return {**base, "dist_type": "mixed", "n_clusters": 5}
        elif dist_idx == 3:  # S2-D: Self-built Clustered (10 clusters × 10)
            return {**base, "dist_type": "clustered", "n_clusters": 10}
        elif dist_idx == 4:  # S2-E: Self-built Uniform, high lat (±60°)
            return {**base, "dist_type": "uniform", "high_lat": True}

    gen_group("S2", s2_labels, 10, s2_params)

    # ──────────────────────────────────────────────────────────────────────
    # S3: Medium-Large (N=300, Sentinel-1, bilateral) — transition region
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S3: N=300, Sentinel-1, 693km, bilateral ---")
    s3_labels = ["S3-A", "S3-B", "S3-C", "S3-D", "S3-E"]

    def s3_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 300, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:  # S3-A: Random
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:  # S3-B: Clustered
            return {**base, "dist_type": "clustered", "n_clusters": 20}
        elif dist_idx == 2:  # S3-C: Hybrid
            return {**base, "dist_type": "mixed", "n_clusters": 10}
        elif dist_idx == 3:  # S3-D: Resource-constrained → fewer windows
            return {**base, "dist_type": "uniform", "n_orbits": 1}
        elif dist_idx == 4:  # S3-E: Wide distribution → uniform baseline
            return {**base, "dist_type": "uniform"}

    gen_group("S3", s3_labels, 10, s3_params)

    # ──────────────────────────────────────────────────────────────────────
    # S4: Large (N=500, Sentinel-1, bilateral) — high-density regime
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S4: N=500, Sentinel-1, 693km, bilateral ---")
    s4_labels = ["S4-A", "S4-B", "S4-C", "S4-D", "S4-E"]

    def s4_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 500, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:  # S4-A: Uniform
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:  # S4-B: Clustered (5 × 20)
            return {**base, "dist_type": "clustered", "n_clusters": 5}
        elif dist_idx == 2:  # S4-C: Mixed (50 random + 5 clusters × 10)
            return {**base, "dist_type": "mixed", "n_clusters": 5}
        elif dist_idx == 3:  # S4-D: Uniform, tight θ [18°,25°]
            # Use narrower incidence range on Sentinel-1 platform
            tight_s4 = {**SENTINEL1, "incidence_max": 25.0}
            return {**base, "dist_type": "uniform", "sat_params": tight_s4}
        elif dist_idx == 4:  # S4-E: Uniform, full θ [18°,47°]
            return {**base, "dist_type": "uniform"}

    gen_group("S4", s4_labels, 10, s4_params)

    # ──────────────────────────────────────────────────────────────────────
    # S5: ψ_sq Sensitivity (N=20, Sentinel-1, bilateral)
    # Same base seed, varying along-track spread
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S5: ψ_sq Sensitivity, N=20, Sentinel-1, 693km, bilateral ---")
    s5_spreads = [5.0, 15.0, 25.0, 35.0, 45.0]
    s5_labels = ["S5-A", "S5-B", "S5-C", "S5-D", "S5-E"]

    def s5_params(seed_idx, seed, dist_idx):
        return {
            "n_targets": 20,
            "seed": seed,
            "sat_params": SENTINEL1,
            "look_direction": "both",
            "dist_type": "s5_spread",
            "s5_base_seed": seed_idx,  # Same base within each seed index
            "s5_spread_deg": s5_spreads[dist_idx],
        }

    gen_group("S5", s5_labels, 10, s5_params)

    # ──────────────────────────────────────────────────────────────────────
    # S6: C3 Stress Test (N=20, Sentinel-1, bilateral)
    # Clustered targets with narrow visibility windows
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S6: C3 Stress Test, N=20, Sentinel-1, 693km, bilateral ---")
    s6_configs = [
        ("S6-A", 4, 5, 180),    # 4 clusters × 5 targets, 180s window
        ("S6-B", 4, 5, 90),     # 4 clusters × 5 targets, 90s window
        ("S6-C", 2, 10, 120),   # 2 clusters × 10 targets, 120s window
        ("S6-D", 5, 4, 60),     # 5 clusters × 4 targets, 60s window
        ("S6-E", 10, 2, 120),   # 10 clusters × 2 targets, 120s window
    ]
    s6_labels = [c[0] for c in s6_configs]

    def s6_params(seed_idx, seed, dist_idx):
        _, n_clusters, cluster_size, window_s = s6_configs[dist_idx]
        return {
            "n_targets": 20,
            "seed": seed,
            "sat_params": SENTINEL1,
            "look_direction": "both",
            "dist_type": "s6_clusters",
            "s6_n_clusters": n_clusters,
            "s6_cluster_size": cluster_size,
            "max_window_width_s": float(window_s),
        }

    gen_group("S6", s6_labels, 10, s6_params)

    # ──────────────────────────────────────────────────────────────────────
    # S7: N=150 (intermediate density for N50 CI tightening)
    # S8: N=200 (intermediate density for N50 CI tightening)
    # ──────────────────────────────────────────────────────────────────────
    print("\n--- S7: N=150, Sentinel-1, 693km, bilateral (intermediate density) ---")
    s7_labels = ["S7-A", "S7-B", "S7-C", "S7-D", "S7-E"]

    def s7_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 150, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:
            return {**base, "dist_type": "clustered", "n_clusters": 15}
        elif dist_idx == 2:
            return {**base, "dist_type": "mixed", "n_clusters": 7}
        elif dist_idx == 3:
            return {**base, "dist_type": "clustered", "n_clusters": 15}
        elif dist_idx == 4:
            return {**base, "dist_type": "uniform"}

    gen_group("S7", s7_labels, 10, s7_params)

    print("\n--- S8: N=200, Sentinel-1, 693km, bilateral (intermediate density) ---")
    s8_labels = ["S8-A", "S8-B", "S8-C", "S8-D", "S8-E"]

    def s8_params(seed_idx, seed, dist_idx):
        base = {"n_targets": 200, "seed": seed, "sat_params": SENTINEL1,
                "look_direction": "both"}
        if dist_idx == 0:
            return {**base, "dist_type": "uniform"}
        elif dist_idx == 1:
            return {**base, "dist_type": "clustered", "n_clusters": 15}
        elif dist_idx == 2:
            return {**base, "dist_type": "mixed", "n_clusters": 8}
        elif dist_idx == 3:
            return {**base, "dist_type": "clustered", "n_clusters": 20}
        elif dist_idx == 4:
            return {**base, "dist_type": "uniform"}

    gen_group("S8", s8_labels, 10, s8_params)

    print("\n" + "=" * 70)
    print("ALL SCENARIOS GENERATED")
    print("=" * 70)

if __name__ == "__main__":
    main()
