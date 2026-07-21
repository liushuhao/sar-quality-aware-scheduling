"""
Phase 4.2 Scenario Generator for S4, S5, S6
============================================
Adapted from t_57dc6648/generate_scenarios.py (proven working).

Generates:
- S4: ICEYE at 550km, N=100, 5 distributions × 10 seeds = 50 scenarios
- S5: Reuses existing S1 scenarios (θ_ref ablation)
- S6: Bilateral Sentinel-1, N=100, 5 distributions × 10 seeds = 50 scenarios
"""

import sys, os, pickle, random, time, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sar_sim.types import GroundTarget, SARInstrument, KeplerianElement, ObservationWindow
from sar_sim.generator.orbit import propagate_orbit, kepler_to_eci
from sar_sim.generator.target import lat_lon_to_ecef, eci_to_ecef_rotation, EARTH_EQUATORIAL_RADIUS
from sar_sim.generator.visibility import (
PROJECT = Path(__file__).resolve().parent.parent
    _compute_off_nadir_angle, _off_nadir_to_incidence,
    _determine_look_direction, _check_geometric_constraints
)

OUTPUT_DIR = Path(r"PROJECT / "experiments\scenarios"")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Orbit Setup ────────────────────────────────────────────────────────
def make_orbit(altitude_km: float, ltan: float = 6.0, epoch: datetime = None) -> KeplerianElement:
    if epoch is None:
        epoch = datetime(2026, 6, 15, 0, 0, 0)
    semi_major_axis = (altitude_km * 1000.0) + EARTH_EQUATORIAL_RADIUS
    inclination = np.radians(97.8 if altitude_km >= 500 else 97.6)
    raan = np.radians(ltan * 15.0)
    return KeplerianElement(
        semi_major_axis=semi_major_axis, eccentricity=0.0,
        inclination=inclination, raan=raan,
        arg_perigee=0.0, true_anomaly=0.0, epoch=epoch,
    )

# ─── Target Generation ──────────────────────────────────────────────────
def generate_targets_along_track(n: int, orbit_elements: KeplerianElement,
                                  instrument: SARInstrument, seed: int = None,
                                  dist_type: str = "uniform") -> List[GroundTarget]:
    """Generate N targets along ground track with cross-track offsets."""
    if seed is not None:
        random.seed(seed + 10000)  # offset from scenario seed
        np.random.seed(seed + 10000)
    
    R_e = EARTH_EQUATORIAL_RADIUS
    h = (orbit_elements.semi_major_axis - R_e)
    altitude_km = h / 1000.0
    ratio = R_e / (R_e + h)
    sin_eta_max = ratio * np.sin(np.radians(instrument.incidence_max))
    sin_eta_max = np.clip(sin_eta_max, -1.0, 1.0)
    eta_max_deg = np.degrees(np.arcsin(sin_eta_max))
    swath_half_km = altitude_km * np.tan(np.radians(eta_max_deg))
    swath_half_deg = swath_half_km / 111.32
    
    # Propagate orbit for one period for ground track
    mu = 3.986004418e14
    a = orbit_elements.semi_major_axis
    period_s = 2 * np.pi * np.sqrt(a**3 / mu)
    t_start = orbit_elements.epoch
    t_end = t_start + timedelta(seconds=period_s)
    
    states = propagate_orbit(orbit_elements, t_start, t_end, timedelta(seconds=30))
    
    e2 = 0.00669437999014
    track_points = []
    for state in states:
        R = eci_to_ecef_rotation(state.time.timestamp())
        sat_ecef = R @ state.position
        x, y, z = sat_ecef[0], sat_ecef[1], sat_ecef[2]
        r_xy = np.sqrt(x**2 + y**2)
        lon = np.degrees(np.arctan2(y, x))
        lat = np.degrees(np.arctan2(z, r_xy * (1 - e2)))
        track_points.append((float(lat), float(lon)))
    
    if len(track_points) < 10:
        raise RuntimeError(f"Too few track points: {len(track_points)}")
    
    # Distribution types
    targets = []
    if dist_type == "uniform":
        # Simple random sampling along track
        for i in range(n):
            idx = random.randint(0, len(track_points) - 1)
            track_lat, track_lon = track_points[idx]
            cross_offset_km = random.uniform(-swath_half_km, swath_half_km)
            cross_offset_deg = cross_offset_km / 111.32
            cos_lat = max(np.cos(np.radians(track_lat)), 0.1)
            lat = track_lat + random.uniform(-0.5, 0.5) * cross_offset_deg
            lon = track_lon + cross_offset_deg / cos_lat
            lat = max(-90.0, min(90.0, lat))
            lon = (lon + 180) % 360 - 180
            targets.append(GroundTarget(
                target_id=f"T{i:04d}", lat=float(lat), lon=float(lon),
                priority=random.randint(1, 10),
                min_elevation=instrument.min_elevation,
            ))
    elif dist_type == "clustered":
        # Few cluster centers, then scatter around them
        n_clusters = 5
        centers = random.sample(track_points, n_clusters)
        per_cluster = n // n_clusters
        idx = 0
        for clat, clon in centers:
            count = per_cluster + (1 if idx < n % n_clusters else 0)
            for _ in range(count):
                lat = clat + random.uniform(-swath_half_deg, swath_half_deg)
                lon = clon + random.uniform(-swath_half_deg, swath_half_deg)
                lat = max(-90.0, min(90.0, lat))
                lon = (lon + 180) % 360 - 180
                targets.append(GroundTarget(
                    target_id=f"T{idx:04d}", lat=float(lat), lon=float(lon),
                    priority=random.randint(1, 10),
                    min_elevation=instrument.min_elevation,
                ))
                idx += 1
    elif dist_type == "mixed":
        # Half random, half clustered
        n_random = n // 2
        n_clustered = n - n_random
        # Random half
        for i in range(n_random):
            idx = random.randint(0, len(track_points) - 1)
            track_lat, track_lon = track_points[idx]
            cross_offset_km = random.uniform(-swath_half_km, swath_half_km)
            cross_offset_deg = cross_offset_km / 111.32
            cos_lat = max(np.cos(np.radians(track_lat)), 0.1)
            lat = track_lat + random.uniform(-0.5, 0.5) * cross_offset_deg
            lon = track_lon + cross_offset_deg / cos_lat
            lat = max(-90.0, min(90.0, lat))
            lon = (lon + 180) % 360 - 180
            targets.append(GroundTarget(
                target_id=f"T{i:04d}", lat=float(lat), lon=float(lon),
                priority=random.randint(1, 10),
                min_elevation=instrument.min_elevation,
            ))
        # Clustered half
        n_c = 3
        centers = random.sample(track_points, n_c)
        per = n_clustered // n_c
        for ci, (clat, clon) in enumerate(centers):
            count = per + (1 if ci < n_clustered % n_c else 0)
            for _ in range(count):
                lat = clat + random.uniform(-swath_half_deg, swath_half_deg)
                lon = clon + random.uniform(-swath_half_deg, swath_half_deg)
                lat = max(-90.0, min(90.0, lat))
                lon = (lon + 180) % 360 - 180
                targets.append(GroundTarget(
                    target_id=f"T{len(targets):04d}", lat=float(lat), lon=float(lon),
                    priority=random.randint(1, 10),
                    min_elevation=instrument.min_elevation,
                ))
    else:
        raise ValueError(f"Unknown distribution: {dist_type}")
    
    return targets

# ─── Batch Visibility Computation (from original generator) ────────────
def compute_batch_visibility(orbit_elements, satellite_id, targets, instrument,
                              t_start, t_end, step, altitude_km):
    states = propagate_orbit(orbit_elements, t_start, t_end, step)
    if len(states) == 0:
        return {}
    
    target_ecef_map = {tgt.target_id: lat_lon_to_ecef(tgt.lat, tgt.lon) for tgt in targets}
    in_window = {tgt.target_id: False for tgt in targets}
    window_start = {tgt.target_id: None for tgt in targets}
    best_elev = {tgt.target_id: -999.0 for tgt in targets}
    best_off_nadir = {tgt.target_id: 0.0 for tgt in targets}
    best_look = {tgt.target_id: "right" for tgt in targets}
    best_time = {tgt.target_id: None for tgt in targets}
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
            sin_elev = (h_sat_m**2 + 2 * EARTH_EQUATORIAL_RADIUS * h_sat_m - distance**2) / (
                2 * EARTH_EQUATORIAL_RADIUS * distance)
            sin_elev = np.clip(sin_elev, -1.0, 1.0)
            elev = np.degrees(np.arcsin(sin_elev))
            off_nadir = _compute_off_nadir_angle(sat_ecef, target_ecef)
            incidence = _off_nadir_to_incidence(off_nadir, h_sat_m)
            look = _determine_look_direction(sat_ecef, sat_vel_ecef, target_ecef)
            
            if instrument:
                passes = _check_geometric_constraints(elev, incidence, look, instrument)
            else:
                passes = elev >= 5.0  # basic check
            
            if passes:
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
                        t_start=window_start[tid], t_end=state.time,
                        t_optimal=best_time[tid], elevation=best_elev[tid],
                        off_nadir_angle=best_off_nadir[tid],
                        look_direction=best_look[tid], duration_min=30.0,
                    ))
    
    for tgt in targets:
        tid = tgt.target_id
        if in_window[tid]:
            results[tid].append(ObservationWindow(
                satellite_id=satellite_id, target_id=tid,
                t_start=window_start[tid], t_end=t_end,
                t_optimal=best_time[tid], elevation=best_elev[tid],
                off_nadir_angle=best_off_nadir[tid],
                look_direction=best_look[tid], duration_min=30.0,
            ))
    
    return results

# ─── Scenario Generation ────────────────────────────────────────────────
def generate_one_scenario(n_targets, seed, altitude_km, incidence_min, incidence_max,
                           look_direction, dist_type="uniform", satellite_id="SAT-01"):
    random.seed(seed)
    np.random.seed(seed)
    
    instrument = SARInstrument(
        incidence_min=incidence_min, incidence_max=incidence_max,
        look_direction=look_direction, antenna_type="reflector", min_elevation=5.0,
    )
    
    epoch = datetime(2026, 6, 15, 0, 0, 0)
    orbit = make_orbit(altitude_km, ltan=6.0, epoch=epoch)
    
    a = orbit.semi_major_axis
    mu = 3.986004418e14
    period_s = 2 * np.pi * np.sqrt(a**3 / mu)
    t_start = epoch
    t_end = epoch + timedelta(seconds=2 * period_s)
    step = timedelta(seconds=60)
    
    targets = generate_targets_along_track(n_targets, orbit, instrument, seed=seed, dist_type=dist_type)
    
    t0 = time.time()
    windows_dict = compute_batch_visibility(orbit, satellite_id, targets, instrument,
                                              t_start, t_end, step, altitude_km)
    compute_time = time.time() - t0
    
    all_windows = []
    for wlist in windows_dict.values():
        all_windows.extend(wlist)
    
    n_with = sum(1 for wlist in windows_dict.values() if len(wlist) > 0)
    
    return {
        "targets": targets, "windows": all_windows,
        "windows_by_target": windows_dict,
        "config": {"t_start": t_start, "t_end": t_end, "period_s": period_s, "n_orbits_simulated": 2},
        "satellite": {"id": satellite_id, "altitude_km": altitude_km,
                       "inclination_deg": 97.8 if altitude_km >= 500 else 97.6, "ltan_h": 6.0},
        "instrument": instrument, "seed": seed, "n_targets": n_targets,
        "stats": {"n_targets_total": n_targets, "n_with_windows": n_with,
                  "total_windows": len(all_windows), "compute_time_s": compute_time},
    }

# ─── Main ────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("S4/S6 SCENARIO GENERATOR")
    print("=" * 60)
    
    # ── S4: ICEYE at 550km, N=100, 5 distributions × 10 seeds ──
    s4_dir = OUTPUT_DIR / "S4"
    s4_dir.mkdir(exist_ok=True)
    s4_dists = ["uniform", "clustered", "mixed", "uniform", "uniform"]
    s4_labels = ["S4-A", "S4-B", "S4-C", "S4-D", "S4-E"]
    
    print("\n--- S4: ICEYE at 550km, N=100 ---")
    for dist_idx, dist_type in enumerate(s4_dists):
        label = s4_labels[dist_idx]
        for seed_idx in range(10):
            seed = dist_idx * 100 + seed_idx
            fname = f"{label}_seed{seed_idx:02d}.pkl"
            fpath = s4_dir / fname
            if fpath.exists():
                print(f"  [EXISTS] {fname}")
                continue
            
            scenario = generate_one_scenario(
                n_targets=100, seed=seed,
                altitude_km=550.0, incidence_min=15.0, incidence_max=35.0,
                look_direction="both", dist_type=dist_type,
            )
            with open(fpath, "wb") as f:
                pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)
            stats = scenario["stats"]
            print(f"  [GEN] {fname}: {stats['n_with_windows']}/{stats['n_targets_total']} visible, "
                  f"{stats['total_windows']} windows, {stats['compute_time_s']:.1f}s")
    
    # ── S6: Sentinel-1 bilateral, N=100, 5 distributions × 10 seeds ──
    s6_dir = OUTPUT_DIR / "S6"
    s6_dir.mkdir(exist_ok=True)
    s6_dists = ["uniform", "clustered", "mixed", "uniform", "clustered"]
    s6_labels = ["S6-A", "S6-B", "S6-C", "S6-D", "S6-E"]
    
    print("\n--- S6: Sentinel-1 bilateral, N=100, 600km ---")
    for dist_idx, dist_type in enumerate(s6_dists):
        label = s6_labels[dist_idx]
        for seed_idx in range(10):
            seed = dist_idx * 100 + seed_idx + 500  # offset
            fname = f"{label}_seed{seed_idx:02d}.pkl"
            fpath = s6_dir / fname
            if fpath.exists():
                print(f"  [EXISTS] {fname}")
                continue
            
            scenario = generate_one_scenario(
                n_targets=100, seed=seed,
                altitude_km=600.0, incidence_min=15.0, incidence_max=50.0,
                look_direction="both", dist_type=dist_type,
            )
            with open(fpath, "wb") as f:
                pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)
            stats = scenario["stats"]
            print(f"  [GEN] {fname}: {stats['n_with_windows']}/{stats['n_targets_total']} visible, "
                  f"{stats['total_windows']} windows, {stats['compute_time_s']:.1f}s")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
