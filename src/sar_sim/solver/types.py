"""Shared types for agile SAR scheduling solvers.

These types are free of pymoo dependencies.  They can be imported
by any module (e.g. constraint verification) without triggering a
pymoo import cascade.

Types extracted from moea.py to eliminate the ConstraintVerifier's
transitive dependency on pymoo.
"""

from dataclasses import dataclass, field
import numpy as np
from typing import List, Dict, Optional, Tuple

from sar_sim.types import ObservationWindow, GroundTarget
from sar_sim.metrics.nesz import (
    elevation_to_off_nadir,
    off_nadir_to_incidence,
    quality_score,
)
from bisect import bisect_left

# ─── Physical constants ──────────────────────────────────────────────────
MU_EARTH = 3.986004418e14      # Earth gravitational parameter (m^3/s^2)
EARTH_RADIUS_M = 6378137.0     # WGS-84 equatorial radius (m) — for orbit calcs & ECEF only
# NOTE: EARTH_RADIUS_M uses the WGS-84 equatorial radius (6,378,137 m).
# For φ↔θ (off-nadir ↔ incidence) Earth-curvature conversion, use the
# volumetric mean radius EARTH_RADIUS_MEAN_M (6,371,000 m) from
# sar_sim.metrics.nesz. Do NOT use this equatorial constant for φ↔θ conversion.
OMEGA_EARTH = 7.2921159e-5     # Earth rotation rate (rad/s)

# Typical SAR satellite orbit: sun-synchronous, dawn-dusk, ~97.8° inclination
DEFAULT_INCLINATION_RAD = np.radians(97.8)


# ─── Agile SAR Problem Data Types ─────────────────────────────────────────

@dataclass
class AgileTask:
    """An agile SAR observation task with off-nadir-angle-dependent quality.

    Maps a ground target to its observation geometry, derived from
    existing sar_sim ObservationWindow data.
    """
    task_id: int
    target_id: str
    priority: float
    windows: List[ObservationWindow]
    # For each window, record the min/max achievable off-nadir angle
    phi_min: float  # lowest phi achievable (best NESZ) -- at max elevation
    phi_max: float  # highest phi achievable (worst NESZ) -- at min elevation
    t_earliest: float  # earliest possible start time (epoch seconds) across all windows
    t_latest: float    # latest possible start time
    duration: float             # observation duration (seconds)
    energy: float      # energy consumption per observation
    memory: float      # memory consumption per observation
    phi_min_res: float = 0.0  # minimum phi required by resolution constraint (MOEA-3)
    # ── Precomputed fields (populated by build_agile_instance) ─────────
    theta_min_res: float = 0.0    # off_nadir_to_incidence(phi_min_res, alt) — constant per task
    time_span: float = 0.0        # t_latest - duration - t_earliest — constant per task
    window_times: List[Tuple[float, float]] = field(default_factory=list)
    # list of (w_start_float, w_end_float) for each window — avoids hasattr+timestamp in hot loop


@dataclass
class AgileSARInstance:
    """Complete agile SAR scheduling problem instance.

    Aggregates all tasks, satellite parameters, and constraint bounds.
    """
    tasks: List[AgileTask]
    N: int                               # number of tasks
    phi_min: float                       # global off-nadir angle min (rad)
    phi_max: float                       # global off-nadir angle max (rad)
    max_slew_rate: float                 # max attitude slew rate (rad/s)
    settle_time: float                   # post-maneuver settling (s)
    energy_budget: float                 # E_max
    memory_budget: float                 # M_max
    target_map: Dict[str, GroundTarget]  # target_id -> GroundTarget
    altitude_m: float = 693_000.0        # satellite orbital altitude (m)
    # ── Orbital parameters for 3-axis attitude computation ──────────────
    orbit_inclination_rad: float = DEFAULT_INCLINATION_RAD  # orbit inclination
    orbit_period_s: float = 5800.0       # orbital period (s), computed from altitude
    orbit_ref_time_s: float = 0.0        # epoch seconds of ascending-node reference (phase=0)
    orbit_raan_rad: float = 0.0          # RAAN (radians) — needed for correct ECI position
    orbit_epoch_s: float = 0.0           # orbit epoch as Unix timestamp — for ECI→ECEF rotation
    geom_cache: Optional["GeomCache"] = None  # precomputed geometry cache
    target_ecef_map: Dict[str, np.ndarray] = field(default_factory=dict)
    sat_position_cache: Optional["SatPositionCache"] = None


# ─── Agile SAR Instance Builder ───────────────────────────────────────────

def build_agile_instance(
    windows: List[ObservationWindow],
    targets: List[GroundTarget],
    phi_min: float = 0.2618,    # 15 deg off-nadir
    phi_max: float = 0.8727,    # 50 deg off-nadir
    max_slew_rate: float = 0.0524,  # 3 deg/s
    settle_time: float = 5.0,
    energy_budget: float = 1e7,
    memory_budget: float = 1e11,
    duration: float = 30.0,
    energy_per_obs: float = 50000.0,
    memory_per_obs: float = 5e8,
    resolution_reqs: Optional[List[float]] = None,
    altitude_m: float = 693_000.0,  # orbital altitude for phi->theta conversion
    orbit_inclination_rad: float = DEFAULT_INCLINATION_RAD,
    orbit_raan_rad: float = 0.0,
    orbit_epoch_s: float = 0.0,
) -> AgileSARInstance:
    """Build an AgileSARInstance from sar_sim observation windows.

    Groups windows by target, extracting off-nadir angle ranges and
    timing information.

    Args:
        windows: all observation windows (multi-satellite; we filter to one satellite)
        targets: ground targets
        phi_min, phi_max: global off-nadir angle bounds (rad)
        max_slew_rate: max attitude slew rate (rad/s)
        settle_time: post-maneuver settling time (s)
        energy_budget, memory_budget: resource limits
        duration: fixed observation duration per task (s)
        energy_per_obs, memory_per_obs: per-observation resource consumption
        resolution_reqs: per-task resolution constraint minima (off-nadir, rad)
        altitude_m: satellite orbital altitude for phi->theta conversion
        orbit_inclination_rad: orbit inclination (radians)
        orbit_raan_rad: RAAN (radians) — needed for correct ECI→ECEF geometry
        orbit_epoch_s: orbit epoch as Unix timestamp — phase reference and
                       ECI→ECEF rotation reference

    Returns:
        AgileSARInstance
    """
    target_map = {t.target_id: t for t in targets}

    # Group windows by target_id
    by_target: Dict[str, List[ObservationWindow]] = {}
    for w in windows:
        by_target.setdefault(w.target_id, []).append(w)

    tasks = []
    for task_idx, (target_id, target_windows) in enumerate(by_target.items()):
        target = target_map[target_id]

        # For each window: off-nadir angle φ = 90° − elevation (flat-Earth).
        # For flat Earth φ = θ (off-nadir equals incidence), so
        # elevation_to_off_nadir() gives the correct off-nadir value.
        # The Earth-curvature correction (φ → θ) is applied later in quality_score.
        phis_min = []
        phis_max = []
        t_earliest = float("inf")
        t_latest = 0.0

        for w in target_windows:
            # At max elevation -> min off-nadir -> best NESZ
            phi_at_optimal = elevation_to_off_nadir(w.elevation)
            # At min elevation -> max off-nadir (boundary of window)
            phi_at_edge = elevation_to_off_nadir(target.min_elevation)

            phis_min.append(phi_at_optimal)
            phis_max.append(phi_at_edge)
            t_earliest = min(t_earliest, w.t_start.timestamp())
            t_latest = max(t_latest, w.t_end.timestamp())

        if not target_windows:
            continue

        # Task-level bounds: best phi from any window, worst phi constraint
        task_phi_min = min(phis_min)
        task_phi_max = max(phis_max)

        # Clamp to global bounds, but ensure task range is valid:
        # if task's achievable range doesn't overlap global range, relax
        if task_phi_min > phi_max:
            task_phi_max = task_phi_min + 0.01  # tiny range
        elif task_phi_max < phi_min:
            task_phi_min = phi_max - 0.01
        else:
            task_phi_min = max(task_phi_min, phi_min)
            task_phi_max = min(task_phi_max, phi_max)
            # Ensure min <= max
            if task_phi_min >= task_phi_max:
                task_phi_max = task_phi_min + 0.01

        phi_min_res_val = resolution_reqs[task_idx] if resolution_reqs else 0.0
        tasks.append(AgileTask(
            task_id=task_idx,
            target_id=target_id,
            priority=float(target.priority),
            windows=target_windows,
            phi_min=task_phi_min,
            phi_max=task_phi_max,
            t_earliest=t_earliest,
            t_latest=t_latest,
            duration=duration,
            energy=energy_per_obs,
            memory=memory_per_obs,
            phi_min_res=phi_min_res_val,
            theta_min_res=off_nadir_to_incidence(phi_min_res_val, altitude_m),
            time_span=t_latest - duration - t_earliest,
            window_times=[(
                w.t_start.timestamp() if hasattr(w.t_start, 'timestamp') else w.t_start,
                w.t_end.timestamp() if hasattr(w.t_end, 'timestamp') else w.t_end,
            ) for w in target_windows],
        ))

    # --- Compute orbital period from altitude (Kepler's third law) ---
    R_orbit = EARTH_RADIUS_M + altitude_m
    orbit_period_s = 2.0 * np.pi * np.sqrt(R_orbit**3 / MU_EARTH)
    # Orbit reference time: use orbit_epoch_s if provided, else earliest task time
    if orbit_epoch_s > 0:
        orbit_ref_time_s = orbit_epoch_s
    else:
        orbit_ref_time_s = min(t.t_earliest for t in tasks) if tasks else 0.0

    return AgileSARInstance(
        tasks=tasks,
        N=len(tasks),
        phi_min=phi_min,
        phi_max=phi_max,
        max_slew_rate=max_slew_rate,
        settle_time=settle_time,
        energy_budget=energy_budget,
        memory_budget=memory_budget,
        target_map=target_map,
        altitude_m=altitude_m,
        orbit_inclination_rad=orbit_inclination_rad,
        orbit_period_s=orbit_period_s,
        orbit_ref_time_s=orbit_ref_time_s,
        orbit_raan_rad=orbit_raan_rad,
        orbit_epoch_s=orbit_epoch_s,
    )


def build_agile_instance_from_scenario(
    scenario: dict,
    **kwargs,
) -> AgileSARInstance:
    """Build an AgileSARInstance from a scenario PKL dict, auto-extracting
    orbit parameters (RAAN, inclination, epoch) from the satellite/config
    fields.

    This ensures _satellite_body_frame uses the same orbit as the
    visibility-window generation, producing consistent phi/theta values.

    Args:
        scenario: dict loaded from a scenario .pkl file, containing keys
            "windows", "targets", "satellite", "config".
        **kwargs: additional arguments forwarded to build_agile_instance
            (e.g. max_slew_rate, settle_time).

    Returns:
        AgileSARInstance with correct orbital parameters.
    """
    import numpy as np

    sat = scenario.get("satellite", {})
    config = scenario.get("config", {})

    inclination_deg = sat.get("inclination_deg", 97.8)
    ltan_h = sat.get("ltan_h", 6.0)
    t_start = config.get("t_start")

    orbit_inclination_rad = np.radians(inclination_deg)
    orbit_raan_rad = np.radians(ltan_h * 15.0)
    orbit_epoch_s = t_start.timestamp() if hasattr(t_start, "timestamp") else float(t_start)

    return build_agile_instance(
        windows=scenario["windows"],
        targets=scenario["targets"],
        orbit_inclination_rad=orbit_inclination_rad,
        orbit_raan_rad=orbit_raan_rad,
        orbit_epoch_s=orbit_epoch_s,
        **kwargs,
    )


# ─── Transition Time Model (full 3-axis) ──────────────────────────────────

def _satellite_body_frame(
    obs_time_s: float,
    instance: "AgileSARInstance",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute satellite body-frame axes at observation time.

    Uses a circular-orbit approximation consistent with propagate_orbit:
    the satellite moves in its orbital plane (inclination i, RAAN Ω),
    and the body frame is defined as:

        Z_body = nadir (toward Earth center)
        X_body = along-track (velocity direction)
        Y_body = cross-track = Z_body × X_body (right side)

    The ECI position includes the RAAN rotation, and the ECI→ECEF
    rotation uses the absolute Unix timestamp (matching
    eci_to_ecef_rotation in generator/target.py).  This ensures
    consistency with visibility-window generation.

    Args:
        obs_time_s: observation time (Unix epoch seconds)
        instance: problem instance with orbital params

    Returns:
        (X_body, Y_body, Z_body, pos_ecef) — body axes are unit (3,)
        numpy arrays in ECEF; pos_ecef is the satellite ECEF position (m).
    """
    R_orbit = EARTH_RADIUS_M + instance.altitude_m
    omega = 2.0 * np.pi / instance.orbit_period_s  # orbital angular velocity
    i_rad = instance.orbit_inclination_rad
    raan = instance.orbit_raan_rad
    t_ref = instance.orbit_ref_time_s

    # Orbital phase at observation time (radians from ascending node)
    theta = omega * (obs_time_s - t_ref)

    # Satellite position in perifocal frame (arg_perigee = 0):
    # x = R·cos(θ), y = R·sin(θ), z = 0
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    cos_i = np.cos(i_rad)
    sin_i = np.sin(i_rad)
    cos_raan = np.cos(raan)
    sin_raan = np.sin(raan)

    pos_peri = np.array([R_orbit * cos_theta, R_orbit * sin_theta, 0.0])
    vel_peri = np.array([-R_orbit * omega * sin_theta,
                          R_orbit * omega * cos_theta, 0.0])

    # ECI = R_x(inclination) @ R_z(RAAN) @ perifocal
    # (matches kepler_to_eci rotation: R = R_z(ω) @ R_x(i) @ R_z(Ω),
    #  with arg_perigee ω = 0)
    R_z_raan = np.array([
        [cos_raan, -sin_raan, 0],
        [sin_raan,  cos_raan, 0],
        [0,         0,        1],
    ])
    R_x_inc = np.array([
        [1, 0,      0],
        [0, cos_i, -sin_i],
        [0, sin_i,  cos_i],
    ])
    R_eci = R_x_inc @ R_z_raan

    pos_eci = R_eci @ pos_peri
    vel_eci = R_eci @ vel_peri

    # Earth rotation correction: ECI → ECEF (rotation about z-axis).
    # Use ABSOLUTE Unix timestamp to match eci_to_ecef_rotation()
    # in generator/target.py (which uses OMEGA_EARTH * timestamp).
    earth_angle = OMEGA_EARTH * obs_time_s
    cos_ea = np.cos(earth_angle)
    sin_ea = np.sin(earth_angle)
    R_eci2ecef = np.array([
        [cos_ea,  sin_ea, 0],
        [-sin_ea, cos_ea, 0],
        [0,       0,      1],
    ])

    pos_ecef = R_eci2ecef @ pos_eci
    vel_ecef = R_eci2ecef @ vel_eci

    # Body frame axes (unit vectors, ECEF)
    Z_body = -pos_ecef / np.linalg.norm(pos_ecef)   # nadir
    X_body = vel_ecef / np.linalg.norm(vel_ecef)     # along-track
    Y_body = np.cross(Z_body, X_body)                # cross-track (right)
    Y_body /= np.linalg.norm(Y_body)

    return X_body, Y_body, Z_body, pos_ecef


def _lat_lon_to_ecef(lat_deg: float, lon_deg: float, alt_m: float = 0.0) -> np.ndarray:
    """Convert geodetic lat/lon/alt to ECEF (WGS-84)."""
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)

    # Prime vertical radius of curvature
    e2 = 0.00669437999014  # WGS-84 first eccentricity squared
    N = EARTH_RADIUS_M / np.sqrt(1.0 - e2 * sin_lat**2)

    x = (N + alt_m) * cos_lat * np.cos(lon)
    y = (N + alt_m) * cos_lat * np.sin(lon)
    z = (N * (1.0 - e2) + alt_m) * sin_lat
    return np.array([x, y, z])


def compute_full_attitude(
    task: "AgileTask",
    obs_time_s: float,
    phi_signed: float,
    instance: "AgileSARInstance",
) -> Tuple[float, float, float]:
    """Compute full 3-axis attitude for observing a target.

    Decomposes the line-of-sight vector into body-frame components
    to extract off-nadir φ (roll), pitch (along-track), and squint ψ_sq.

    Body frame (right-handed):
        X = along-track (velocity)
        Y = cross-track (right side)
        Z = nadir (toward Earth center)

    Attitude angles:
        off-nadir φ = atan2(sqrt(los_x²+los_y²), los_z)  — total off-track angle
        pitch       = atan2(los_x, los_z)                  — rotation about Y axis
        squint ψ_sq = arcsin(|los_x|)                      — squint angle (along-track component)

    The squint angle ψ_sq determines azimuth resolution quality:
    smaller squint → better azimuth resolution.

    Args:
        task: the observation task (provides target_id)
        obs_time_s: observation time (epoch seconds)
        phi_signed: signed off-nadir angle (rad) — used to infer sign of roll
        instance: problem instance with target_map and orbital params

    Returns:
        (off_nadir_rad, pitch_rad, squint_rad) — full 3-axis attitude in radians.
        Off-nadir sign matches phi_signed (positive = right-looking).
    """
    # Get target ECEF position
    target = instance.target_map[task.target_id]
    target_ecef = _lat_lon_to_ecef(target.lat, target.lon)

    # Get satellite body frame at observation time
    X_body, Y_body, Z_body, sat_ecef = _satellite_body_frame(obs_time_s, instance)

    # Line-of-sight vector (satellite → target) in ECEF
    los_ecef = target_ecef - sat_ecef
    los_unit = los_ecef / np.linalg.norm(los_ecef)

    # Project LOS onto body-frame axes
    los_x = np.dot(los_unit, X_body)  # along-track component
    los_y = np.dot(los_unit, Y_body)  # cross-track component
    los_z = np.dot(los_unit, Z_body)  # nadir component (positive = toward Earth)

    # Off-nadir φ: rotation about X_body — the total off-track angle
    # arctan2(sqrt(los_x²+los_y²), los_z) gives the total off-track angle
    off_nadir_abs = np.arctan2(np.sqrt(los_x**2 + los_y**2), los_z)

    # Sign: use phi_signed's sign to determine left/right
    off_nadir = np.copysign(off_nadir_abs, phi_signed) if phi_signed != 0 else 0.0

    # Pitch: rotation about Y_body — fore/aft along-track angle
    pitch = np.arctan2(los_x, los_z)

    # Squint angle: arcsin of the along-track LOS component.
    # This is the squint angle ψ_sq that determines azimuth resolution.
    # |los_x| / |los_unit| = |los_x| (since los_unit is normalized).
    psi_sq = float(np.arcsin(abs(los_x)))

    return float(off_nadir), float(pitch), float(psi_sq)


def compute_transition_time(
    task_a: "AgileTask",
    phi_a: float,
    task_b: "AgileTask",
    phi_b: float,
    max_slew_rate: float,
    settle_time: float,
    instance: Optional["AgileSARInstance"] = None,
) -> float:
    """Compute attitude transition time between two observations (Eq. 4).

    When ``instance`` is provided, computes the FULL 3-axis attitude
    difference using the commanded off-nadir φ (from decision variable) plus
    the geometric pitch and squint from orbit geometry.

    Full 3-axis model:
        τ = max(|Δφ|/ω_max, |Δθ_pitch|/ω_max, |Δψ|/ω_max) + τ_settle

    where:
        Δφ     = |φ_a − φ_b|           — commanded off-nadir difference (decision var)
        Δθ_p   = |θ_p,a − θ_p,b|      — geometric pitch difference
        Δψ     = |ψ_a − ψ_b|           — geometric squint (zero-Doppler ≈ 0)

    **Legacy model (instance=None):**
        Only off-nadir angle difference is considered; azimuth/pitch
        are ignored (hardcoded to 0).  This systematically underestimates
        transition times for globally distributed targets.

    Args:
        task_a, task_b: consecutive observation tasks
        phi_a, phi_b: signed off-nadir (roll) angles (rad, bilateral)
        max_slew_rate: max angular rate (rad/s) — same for all axes
        settle_time: post-maneuver settling time (s)
        instance: optional AgileSARInstance for full 3-axis computation

    Returns:
        transition time in seconds
    """
    if instance is not None:
        # ── Full 3-axis LOS angle transition (Eq. 4, revised) ──────
        # Compute LOS vectors from satellite to target at each task's
        # earliest observation time, then use the angular separation
        # between LOS vectors as the required attitude change.
        t_a = task_a.t_earliest
        t_b = task_b.t_earliest

        # Target positions in ECEF
        target_a = instance.target_map[task_a.target_id]
        target_b = instance.target_map[task_b.target_id]
        target_a_ecef = _lat_lon_to_ecef(target_a.lat, target_a.lon)
        target_b_ecef = _lat_lon_to_ecef(target_b.lat, target_b.lon)

        # Satellite positions at observation times
        _, _, _, sat_a_ecef = _satellite_body_frame(t_a, instance)
        _, _, _, sat_b_ecef = _satellite_body_frame(t_b, instance)

        # LOS vectors (satellite → target) in ECEF
        los_a = target_a_ecef - sat_a_ecef
        los_b = target_b_ecef - sat_b_ecef

        # Angular separation between LOS vectors
        # Δη = arccos(l₁ · l₂ / (|l₁| · |l₂|))
        cos_eta = np.dot(los_a, los_b) / (
            np.linalg.norm(los_a) * np.linalg.norm(los_b))
        cos_eta = np.clip(cos_eta, -1.0, 1.0)
        delta_eta = float(np.arccos(cos_eta))

        # τ_trans = Δη / ω_max + τ_settle
        return delta_eta / max_slew_rate + settle_time
    else:
        # ── Legacy simplified model (backward-compatible) ───────────
        d_off_nadir = abs(phi_a - phi_b)
        d_azimuth = 0.0  # hardcoded — ignores pitch axis entirely
        max_delta = max(d_off_nadir, d_azimuth)
        return max_delta / max_slew_rate + settle_time


# ─── Geometry Precomputation (GeomCache) ─────────────────────────────────


@dataclass(frozen=True, slots=True)
class GeomPoint:
    """单个采样时刻的预计算几何."""
    t: float          # epoch seconds
    phi: float        # roll / off-nadir (rad)
    psi_sq: float     # squint angle (rad)
    cos_psi: float    # cos(psi_sq)
    theta: float      # incidence angle at target (rad)
    q_nesz: float     # quality_score(theta) — preserved for diagnostics, not used in f2/f3


class GeomCache:
    """预计算几何表.

    对每个任务，在时间窗口内等距采样，预计算几何量。
    后续通过 lookup(task_idx, t_actual) 查表，支持线性插值。
    """

    cache: List[np.ndarray]
    # cache[i] shape = (N_pts_i, 6)
    # columns: [t, phi, psi_sq, cos_psi, theta, q_nesz]

    def __init__(self, instance: "AgileSARInstance", step_s: float = 10.0):
        """对每个 task 采样 window 内的时刻，计算并存储几何."""
        self.cache = []
        for task in instance.tasks:
            t_min = task.t_earliest
            t_max = task.t_latest - task.duration
            n_pts = max(2, int((t_max - t_min) / step_s) + 1)
            t_grid = np.linspace(t_min, t_max, n_pts)

            rows = []
            for t_k in t_grid:
                roll, _pitch, psi = compute_full_attitude(
                    task, t_k, 1.0, instance,
                )
                phi = abs(roll)
                theta = off_nadir_to_incidence(phi, instance.altitude_m)
                q = quality_score(theta)
                rows.append([t_k, phi, psi, np.cos(psi), theta, q])

            self.cache.append(np.array(rows, dtype=np.float64))

    def lookup(self, task_idx: int, t_actual: float) -> GeomPoint:
        """查表获取 t_actual 时刻的几何量，支持线性插值.

        - 精确命中采样点 → 直接返回
        - 采样点之间 → 线性插值相邻两点
        - 边界外 → clamp 到最近点
        """
        arr = self.cache[task_idx]

        # Boundary clamping
        if t_actual <= arr[0, 0]:
            row = arr[0]
            return GeomPoint(
                t=t_actual, phi=row[1], psi_sq=row[2],
                cos_psi=row[3], theta=row[4], q_nesz=row[5],
            )
        if t_actual >= arr[-1, 0]:
            row = arr[-1]
            return GeomPoint(
                t=t_actual, phi=row[1], psi_sq=row[2],
                cos_psi=row[3], theta=row[4], q_nesz=row[5],
            )

        # Binary search for interval [k, k+1] containing t_actual
        k = bisect_left(arr[:, 0], t_actual) - 1
        # Ensure k is in valid range (bisect_left returns insertion point)
        if k < 0:
            k = 0
        if k >= len(arr) - 1:
            k = len(arr) - 2

        t_lo = arr[k, 0]
        t_hi = arr[k + 1, 0]
        if t_hi == t_lo:
            # Degenerate: duplicate timestamps, return lo
            return GeomPoint(
                t=t_actual, phi=arr[k, 1], psi_sq=arr[k, 2],
                cos_psi=arr[k, 3], theta=arr[k, 4], q_nesz=arr[k, 5],
            )

        alpha = (t_actual - t_lo) / (t_hi - t_lo)
        interp = (1.0 - alpha) * arr[k, 1:] + alpha * arr[k + 1, 1:]

        return GeomPoint(
            t=t_actual,
            phi=float(interp[0]),
            psi_sq=float(interp[1]),
            cos_psi=float(interp[2]),
            theta=float(interp[3]),
            q_nesz=float(interp[4]),
        )


# ─── Satellite Orbit Position Cache ─────────────────────────────────────────

class SatPositionCache:
    """Precomputed satellite ECEF positions + body frame on a time grid.

    The satellite orbit is deterministic: position at time t depends only on
    orbital parameters (period, inclination, reference time).  This cache
    samples the orbit on a uniform grid and provides interpolated lookups,
    eliminating repeated trig calls in C3 transition computation.

    Cache arrays (n_pts × 3):
        times     — time grid (seconds)
        positions — satellite ECEF position (m)
        x_body    — along-track body axis (unit vector, ECEF)
        y_body    — cross-track body axis (unit vector, ECEF)
        z_body    — nadir body axis (unit vector, ECEF)
    """

    def __init__(self, instance: "AgileSARInstance", step_s: float = 10.0):
        if not instance.tasks:
            # Degenerate: no tasks → empty grid
            self.times = np.array([0.0, 1.0])
            self.positions = np.zeros((2, 3))
            self.x_body = np.zeros((2, 3))
            self.y_body = np.zeros((2, 3))
            self.z_body = np.zeros((2, 3))
            return

        t_min = min(t.t_earliest for t in instance.tasks)
        t_max = max(t.t_latest for t in instance.tasks)
        self.step_s = step_s
        self.t_min = t_min
        n_pts = max(2, int((t_max - t_min) / step_s) + 1)
        self.times = np.linspace(t_min, t_max, n_pts)

        pos_list, x_list, y_list, z_list = [], [], [], []
        for t_k in self.times:
            xb, yb, zb, pos = _satellite_body_frame(t_k, instance)
            pos_list.append(pos)
            x_list.append(xb)
            y_list.append(yb)
            z_list.append(zb)

        self.positions = np.array(pos_list, dtype=np.float64)
        self.x_body = np.array(x_list, dtype=np.float64)
        self.y_body = np.array(y_list, dtype=np.float64)
        self.z_body = np.array(z_list, dtype=np.float64)

    # ── internal: interpolate a single (n_pts, 3) array ───────────────

    def _interp(self, arr: np.ndarray, t: float) -> np.ndarray:
        """Return 3-vector at time t by cubic Lagrange interpolation.

        The satellite ECEF trajectory is smooth (trig), so cubic
        interpolation on the uniform grid reduces error from O(h^2)
        (linear) to O(h^4) at the same precompute cost. Boundary
        segments fall back to linear because a 4-point stencil is
        unavailable there.
        """
        times = self.times
        if t <= self.t_min:
            return arr[0].copy()
        if t >= times[-1]:
            return arr[-1].copy()

        k = int((t - self.t_min) / self.step_s)
        if k < 0:
            k = 0
        if k >= len(times) - 1:
            k = len(times) - 2

        # Linear fallback on the two boundary segments.
        if k < 1 or k >= len(times) - 2:
            t_lo = times[k]; t_hi = times[k + 1]
            alpha = (t - t_lo) / (t_hi - t_lo)
            return (1.0 - alpha) * arr[k] + alpha * arr[k + 1]

        # 4-point Lagrange cubic over [k-1, k, k+1, k+2].
        ts = times[k - 1:k + 3]
        result = np.zeros(3, dtype=float)
        for j in range(4):
            w = 1.0
            for m in range(4):
                if m != j:
                    w *= (t - ts[m]) / (ts[j] - ts[m])
            result += w * arr[k - 1 + j]
        return result

    # ── public interfaces ─────────────────────────────────────────────

    def lookup_position(self, t: float) -> np.ndarray:
        """Get satellite ECEF position at time t (3-vector)."""
        return self._interp(self.positions, t)

    def lookup_body_frame(self, t: float) -> Tuple[np.ndarray, np.ndarray,
                                                    np.ndarray, np.ndarray]:
        """Get (X_body, Y_body, Z_body, pos_ecef) at time t.

        Body axes are re-normalised after interpolation to preserve
        unit-vector properties.
        """
        x = self._interp(self.x_body, t)
        y = self._interp(self.y_body, t)
        z = self._interp(self.z_body, t)
        pos = self._interp(self.positions, t)
        # Re-normalise (linear interpolation can shorten unit vectors)
        nx = np.linalg.norm(x)
        ny = np.linalg.norm(y)
        nz = np.linalg.norm(z)
        if nx > 0:
            x /= nx
        if ny > 0:
            y /= ny
        if nz > 0:
            z /= nz
        return x, y, z, pos


def compute_los_separation(
    task_a: "AgileTask",
    t_a: float,
    task_b: "AgileTask",
    t_b: float,
    instance: "AgileSARInstance",
) -> float:
    """LOS angular separation using cached geometry (fast path).

    Uses precomputed target ECEF positions and satellite position cache
    to avoid trig calls in the C3 transition constraint.

    Falls back to original _compute_los_separation-style computation
    when caches are not available.
    """
    # Target ECEF — from cache if available, else compute
    if instance.target_ecef_map:
        pos_a = instance.target_ecef_map[task_a.target_id]
        pos_b = instance.target_ecef_map[task_b.target_id]
    else:
        ta = instance.target_map[task_a.target_id]
        tb = instance.target_map[task_b.target_id]
        pos_a = _lat_lon_to_ecef(ta.lat, ta.lon)
        pos_b = _lat_lon_to_ecef(tb.lat, tb.lon)

    # Satellite positions — from cache if available, else compute
    if instance.sat_position_cache is not None:
        sat_a = instance.sat_position_cache.lookup_position(t_a)
        sat_b = instance.sat_position_cache.lookup_position(t_b)
    else:
        _, _, _, sat_a = _satellite_body_frame(t_a, instance)
        _, _, _, sat_b = _satellite_body_frame(t_b, instance)

    # LOS vectors (sat → target) in ECEF
    los_a = pos_a - sat_a
    los_b = pos_b - sat_b

    # Angular separation (Eq. 4) — manual linalg for 3-vectors
    # avoids np.dot / np.linalg.norm / np.clip dispatch overhead
    dot = float(los_a[0]*los_b[0] + los_a[1]*los_b[1] + los_a[2]*los_b[2])
    norm_a = np.sqrt(float(los_a[0]*los_a[0] + los_a[1]*los_a[1] + los_a[2]*los_a[2]))
    norm_b = np.sqrt(float(los_b[0]*los_b[0] + los_b[1]*los_b[1] + los_b[2]*los_b[2]))
    cos_eta = dot / (norm_a * norm_b)
    # Manual clip for scalar (avoids numpy dispatch)
    if cos_eta > 1.0:
        cos_eta = 1.0
    elif cos_eta < -1.0:
        cos_eta = -1.0
    return float(np.arccos(cos_eta))


def precompute_geometry(
    instance: "AgileSARInstance",
    step_s: float = 10.0,
) -> None:
    """Precompute geometry caches and populate the instance.

    Builds:
      - geom_cache    : per-task geometry (phi, squint, NESZ) on time grid
      - target_ecef_map : fixed target ECEF positions (avoids repeated trig)
      - sat_position_cache : satellite ECEF positions on time grid

    Args:
        instance: problem instance (modified in-place)
        step_s: time sampling step (seconds), default 10 s
    """
    instance.geom_cache = GeomCache(instance, step_s=step_s)

    # Cache target ECEF positions (never change)
    instance.target_ecef_map = {
        tid: _lat_lon_to_ecef(t.lat, t.lon)
        for tid, t in instance.target_map.items()
    }

    # Cache satellite orbit positions on a grid
    instance.sat_position_cache = SatPositionCache(instance, step_s=step_s)
