"""
Generate S5 scenarios: N=20, Sentinel-1 params, theta_ref ablation.
S5-A: theta_ref=20°, S5-B: theta_ref=25°, S5-C: theta_ref=30° (baseline),
S5-D: theta_ref=35°, S5-E: theta_ref=40°
10 seeds each = 50 scenarios total.

Based on generate_scenarios.py from t_57dc6648.
Uses the same orbit/propagation but varies theta_ref for NESZ.
"""
import sys, os, pickle, random, time, json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
OUTPUT_DIR = Path(r"PROJECT / "experiments\scenarios\S5"")

from sar_sim.types import GroundTarget, SARInstrument, KeplerianElement, ObservationWindow
from sar_sim.generator.orbit import propagate_orbit, kepler_to_eci
from sar_sim.generator.target import lat_lon_to_ecef, eci_to_ecef_rotation, EARTH_EQUATORIAL_RADIUS
from sar_sim.generator.visibility import (
PROJECT = Path(__file__).resolve().parent
    _compute_off_nadir_angle, _off_nadir_to_incidence,
    _determine_look_direction, _check_geometric_constraints
)

# --- Constants (matches generate_scenarios.py from t_57dc6648) ---
ORBIT_ALTITUDE_KM = 600.0
ORBIT_INCLINATION_DEG = 97.8
LTAN_HOURS = 6.0
SIM_DURATION_ORBITS = 2
TIMESTEP_SEC = 60

INSTRUMENT = SARInstrument(
    incidence_min=15.0, incidence_max=50.0,
    look_direction="both", antenna_type="reflector", min_elevation=5.0,
)

# S5 groups: theta_ref values
THETA_REF_GROUPS = {
    "S5-A": 20.0,
    "S5-B": 25.0,
    "S5-C": 30.0,
    "S5-D": 35.0,
    "S5-E": 40.0,
}
N_SEEDS = 10
N_TARGETS = 20

# --- Orbit Setup ---
def make_orbit(epoch=None):
    if epoch is None:
        epoch = datetime(2026, 6, 15, 0, 0, 0)
    a = (ORBIT_ALTITUDE_KM * 1000.0) + EARTH_EQUATORIAL_RADIUS
    return KeplerianElement(
        semi_major_axis=a, eccentricity=0.0,
        inclination=np.radians(ORBIT_INCLINATION_DEG),
        raan=np.radians(LTAN_HOURS * 15.0),
        arg_perigee=0.0, true_anomaly=0.0, epoch=epoch,
    )

# --- Target Generation (copied from generate_scenarios.py) ---
def generate_targets(n, orbit_elements, instrument, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    R_e = EARTH_EQUATORIAL_RADIUS
    h = ORBIT_ALTITUDE_KM * 1000.0
    ratio = R_e / (R_e + h)
    sin_eta_max = ratio * np.sin(np.radians(instrument.incidence_max))
    sin_eta_max = np.clip(sin_eta_max, -1.0, 1.0)
    eta_max_deg = np.degrees(np.arcsin(sin_eta_max))
    swath_half_km = h / 1000.0 * np.tan(np.radians(eta_max_deg))
    swath_half_deg = swath_half_km / 111.32
    mu = 3.986004418e14
    a = orbit_elements.semi_major_axis
    period_s = 2 * np.pi * np.sqrt(a**3 / mu)
    t_start = orbit_elements.epoch
    t_end = t_start + timedelta(seconds=period_s)
    states = propagate_orbit(orbit_elements, t_start, t_end, timedelta(seconds=30))
    track_points = []
    e2 = 0.00669437999014
    for state in states:
        R = eci_to_ecef_rotation(state.time.timestamp())
        sat_ecef = R @ state.position
        x, y, z = sat_ecef[0], sat_ecef[1], sat_ecef[2]
        r_xy = np.sqrt(x**2 + y**2)
        lon = np.degrees(np.arctan2(y, x))
        lat = np.degrees(np.arctan2(z, r_xy * (1 - e2)))
        track_points.append((float(lat), float(lon)))
    targets = []
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
            priority=random.randint(1, 10), min_elevation=instrument.min_elevation,
        ))
    return targets

# --- Batch Visibility (copied from generate_scenarios.py) ---
def compute_batch_visibility(orbit_elements, satellite_id, targets, instrument, t_start, t_end, step):
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
    h_sat_m = ORBIT_ALTITUDE_KM * 1000.0
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
            if _check_geometric_constraints(elev, incidence, look, instrument):
                if not in_window[tid]:
                    in_window[tid] = True
                    window_start[tid] = state.time
                    best_elev[tid] = elev
                    best_off_nadir[tid] = off_nadir
                    best_look[tid] = look
                    best_time[tid] = state.time
                elif elev > best_elev[tid]:
                    best_elev[tid] = elev
                    best_off_nadir[tid] = off_nadir
                    best_look[tid] = look
                    best_time[tid] = state.time
            elif in_window[tid]:
                in_window[tid] = False
                results[tid].append(ObservationWindow(
                    satellite_id=satellite_id, target_id=tid,
                    t_start=window_start[tid], t_end=state.time,
                    t_optimal=best_time[tid], elevation=best_elev[tid],
                    off_nadir_angle=best_off_nadir[tid], look_direction=best_look[tid],
                    duration_min=30.0,
                ))
    for tgt in targets:
        tid = tgt.target_id
        if in_window[tid]:
            results[tid].append(ObservationWindow(
                satellite_id=satellite_id, target_id=tid,
                t_start=window_start[tid], t_end=t_end,
                t_optimal=best_time[tid], elevation=best_elev[tid],
                off_nadir_angle=best_off_nadir[tid], look_direction=best_look[tid],
                duration_min=30.0,
            ))
    return results

# --- Scenario Generation ---
def generate_one_scenario(group_id, theta_ref, seed):
    random.seed(seed)
    np.random.seed(seed)
    epoch = datetime(2026, 6, 15, 0, 0, 0)
    orbit = make_orbit(epoch)
    a = orbit.semi_major_axis
    mu = 3.986004418e14
    period_s = 2 * np.pi * np.sqrt(a**3 / mu)
    t_start = epoch
    t_end = epoch + timedelta(seconds=SIM_DURATION_ORBITS * period_s)
    step = timedelta(seconds=TIMESTEP_SEC)
    satellite_id = "SAT-01"
    targets = generate_targets(N_TARGETS, orbit, INSTRUMENT, seed=seed)
    t0 = time.time()
    windows_dict = compute_batch_visibility(orbit, satellite_id, targets, INSTRUMENT, t_start, t_end, step)
    compute_time = time.time() - t0
    all_windows = []
    for wlist in windows_dict.values():
        all_windows.extend(wlist)
    n_with = sum(1 for wlist in windows_dict.values() if len(wlist) > 0)
    return {
        "targets": targets, "windows": all_windows,
        "windows_by_target": windows_dict,
        "config": {"t_start": t_start, "t_end": t_end, "period_s": period_s,
                    "n_orbits_simulated": SIM_DURATION_ORBITS, "theta_ref": theta_ref},
        "satellite": {"id": satellite_id, "altitude_km": ORBIT_ALTITUDE_KM,
                       "inclination_deg": ORBIT_INCLINATION_DEG, "ltan_h": LTAN_HOURS},
        "instrument": INSTRUMENT, "seed": seed, "n_targets": N_TARGETS,
        "scenario_group": group_id, "theta_ref": theta_ref,
        "stats": {"n_targets_total": N_TARGETS, "n_with_windows": n_with,
                   "total_windows": len(all_windows), "compute_time_s": compute_time},
    }

# --- Main ---
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(THETA_REF_GROUPS) * N_SEEDS
    completed = 0
    t0 = time.time()
    print(f"Generating S5 scenarios: {len(THETA_REF_GROUPS)} groups x {N_SEEDS} seeds = {total}")
    for group_id, theta_ref in THETA_REF_GROUPS.items():
        for seed in range(N_SEEDS):
            fname = f"{group_id}_seed{seed:02d}.pkl"
            fpath = OUTPUT_DIR / fname
            if fpath.exists():
                print(f"  [SKIP] {fname} exists")
                completed += 1
                continue
            scenario = generate_one_scenario(group_id, theta_ref, seed)
            with open(fpath, "wb") as f:
                pickle.dump(scenario, f, protocol=pickle.HIGHEST_PROTOCOL)
            s = scenario["stats"]
            print(f"  [{completed+1}/{total}] {fname}: {s['n_with_windows']}/{s['n_targets_total']} visible, "
                  f"{s['total_windows']} windows, theta_ref={theta_ref}°")
            completed += 1
    print(f"Done: {completed} scenarios in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
