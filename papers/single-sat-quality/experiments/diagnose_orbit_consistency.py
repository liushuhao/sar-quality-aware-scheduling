"""Diagnose orbit consistency between propagate_orbit and _satellite_body_frame.

This script checks whether the satellite position computed by
_satellite_body_frame (used in GeomCache) matches the position from
propagate_orbit + eci_to_ecef_rotation (used in visibility window generation).

If they don't match, all GeomCache phi/theta values will be wrong, causing
C1 verification failures and incorrect MOEA optimization.
"""
import sys
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

PROJECT = Path(__file__).resolve().parent  # experiments/
PAPER_DIR = PROJECT.parent  # single-sat-quality/
WORKSPACE = PAPER_DIR.parent.parent  # planning paper/
sys.path.insert(0, str(WORKSPACE / "src"))

from sar_sim.types import KeplerianElement
from sar_sim.generator.orbit import propagate_orbit, kepler_to_eci
from sar_sim.generator.target import eci_to_ecef_rotation, lat_lon_to_ecef
from sar_sim.solver.types import _satellite_body_frame, AgileSARInstance

# ─── Create the same orbit as generate_all_scenarios.py ───
EARTH_EQUATORIAL_RADIUS = 6378137.0
MU_EARTH = 3.986004418e14
DEFAULT_EPOCH = datetime(2026, 6, 15, 0, 0, 0)
ALTITUDE_KM = 693.0
LTAN = 6.0
INCLINATION_DEG = 97.8

semi_major_axis = (ALTITUDE_KM * 1000.0) + EARTH_EQUATORIAL_RADIUS
inclination = np.radians(INCLINATION_DEG)
raan = np.radians(LTAN * 15.0)  # 90° for LTAN=6.0

orbit = KeplerianElement(
    semi_major_axis=semi_major_axis, eccentricity=0.0,
    inclination=inclination, raan=raan,
    arg_perigee=0.0, true_anomaly=0.0, epoch=DEFAULT_EPOCH,
)

# Compute orbit period
R_orbit = semi_major_axis
period_s = 2 * np.pi * np.sqrt(R_orbit**3 / MU_EARTH)

# Create a minimal AgileSARInstance for _satellite_body_frame
instance = AgileSARInstance(
    tasks=[], N=0,
    phi_min=0.2618, phi_max=0.8727,
    max_slew_rate=0.0524, settle_time=5.0,
    energy_budget=1e7, memory_budget=1e11,
    target_map={},
    altitude_m=ALTITUDE_KM * 1000.0,
    orbit_inclination_rad=inclination,
    orbit_period_s=period_s,
    orbit_ref_time_s=DEFAULT_EPOCH.timestamp(),  # orbit epoch = phase reference
    orbit_raan_rad=raan,
    orbit_epoch_s=DEFAULT_EPOCH.timestamp(),
)

print("=" * 70)
print("ORBIT CONSISTENCY DIAGNOSIS")
print("=" * 70)
print(f"  Altitude: {ALTITUDE_KM} km")
print(f"  Inclination: {INCLINATION_DEG}°")
print(f"  RAAN: {np.degrees(raan):.1f}° (LTAN={LTAN}h)")
print(f"  Epoch: {DEFAULT_EPOCH}")
print(f"  Period: {period_s:.1f}s")
print()

# ─── Compare positions at several times ───
t_start = DEFAULT_EPOCH
t_end = t_start + timedelta(seconds=2 * period_s)
step = timedelta(seconds=600)  # check every 10 min

# Get states from propagate_orbit
states = propagate_orbit(orbit, t_start, t_end, step)

print(f"{'Time(s)':>10} | {'Propagate_orbit ECEF':>40} | {'_satellite_body_frame ECEF':>40} | {'Distance(km)':>12}")
print("-" * 110)

max_dist_km = 0.0
for state in states[::6]:  # every 60 min
    t = state.time
    t_s = t.timestamp()

    # Method 1: propagate_orbit + eci_to_ecef_rotation (correct)
    R = eci_to_ecef_rotation(t.timestamp())
    pos_ecef_correct = R @ state.position

    # Method 2: _satellite_body_frame (used in GeomCache)
    _, _, _, pos_ecef_sbf = _satellite_body_frame(t_s, instance)

    dist = np.linalg.norm(pos_ecef_correct - pos_ecef_sbf)
    dist_km = dist / 1000.0
    max_dist_km = max(max_dist_km, dist_km)

    print(f"{t_s:>10.0f} | ({pos_ecef_correct[0]:>11.0f}, {pos_ecef_correct[1]:>11.0f}, {pos_ecef_correct[2]:>11.0f}) | "
          f"({pos_ecef_sbf[0]:>11.0f}, {pos_ecef_sbf[1]:>11.0f}, {pos_ecef_sbf[2]:>11.0f}) | {dist_km:>12.1f}")

print(f"\n  Max position discrepancy: {max_dist_km:.1f} km")
print(f"  Earth radius: {EARTH_EQUATORIAL_RADIUS/1000:.1f} km")

if max_dist_km > 100:
    print("\n  !!! CRITICAL: _satellite_body_frame is inconsistent with propagate_orbit !!!")
    print("  !!! GeomCache phi/theta values will be WRONG !!!")
    print("  !!! Root cause: missing RAAN rotation and/or wrong Earth rotation angle !!!")
    sys.exit(1)
else:
    print("\n  OK: Positions are consistent (discrepancy < 100 km)")
    sys.exit(0)
