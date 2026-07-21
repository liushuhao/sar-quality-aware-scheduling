"""Core data models for SAR simulation platform.

All platform components exchange data through these types.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Tuple
import numpy as np


# ─── Orbital & Geometric Types ──────────────────────────────────────────

@dataclass(frozen=True)
class KeplerianElement:
    """Classical Keplerian orbital elements.

    semi_major_axis: meters
    eccentricity: dimensionless [0, 1)
    inclination: radians
    raan: right ascension of ascending node, radians
    arg_perigee: argument of perigee, radians
    true_anomaly: radians at epoch
    epoch: reference time
    """
    semi_major_axis: float
    eccentricity: float
    inclination: float
    raan: float
    arg_perigee: float
    true_anomaly: float
    epoch: datetime = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __post_init__(self):
        if self.eccentricity < 0 or self.eccentricity >= 1:
            raise ValueError(f"eccentricity must be in [0, 1), got {self.eccentricity}")
        if self.semi_major_axis <= 0:
            raise ValueError(f"semi_major_axis must be > 0, got {self.semi_major_axis}")


@dataclass(frozen=True)
class ECIState:
    """Earth-Centered Inertial state vector (position, velocity).

    position: (x, y, z) in meters
    velocity: (vx, vy, vz) in m/s
    time: datetime of state
    """
    position: np.ndarray
    velocity: np.ndarray
    time: datetime

    def __post_init__(self):
        if self.position.shape != (3,):
            raise ValueError("position must be shape (3,)")
        if self.velocity.shape != (3,):
            raise ValueError("velocity must be shape (3,)")


# ─── Ground Target ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class GroundTarget:
    """Ground observation target.

    target_id: unique identifier
    lat: latitude in degrees [-90, 90]
    lon: longitude in degrees [-180, 180]
    priority: observation priority [1, 10], higher = more important
    min_elevation: minimum elevation angle (deg) for valid observation
    revisit_requirement: maximum allowed revisit interval (seconds)
    """
    target_id: str
    lat: float
    lon: float
    priority: int = 5
    min_elevation: float = 10.0
    revisit_requirement: float = 86400.0  # 24 hours default

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError(f"lat out of range: {self.lat}")
        if not (-180 <= self.lon <= 180):
            raise ValueError(f"lon out of range: {self.lon}")
        if not (1 <= self.priority <= 10):
            raise ValueError(f"priority out of range [1,10]: {self.priority}")


# ─── SAR Instrument ──────────────────────────────────────────────────────

class LookDirection(str, Enum):
    """SAR side-looking direction."""
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class SARInstrument:
    """SAR instrument configuration for a satellite.

    Attributes:
        incidence_min: minimum usable incidence angle (degrees)
        incidence_max: maximum usable incidence angle (degrees)
        look_direction: which side(s) the satellite can look
            "left" / "right" / "both"
        antenna_type: "phased_array" or "reflector"
        min_elevation: minimum elevation angle (degrees)
    """
    incidence_min: float = 15.0
    incidence_max: float = 45.0
    look_direction: str = "right"
    antenna_type: str = "reflector"
    min_elevation: float = 0.0
    max_squint_deg: float = 45.0

    def __post_init__(self):
        if self.incidence_min < 0 or self.incidence_min > 90:
            raise ValueError(f"incidence_min out of range [0, 90]: {self.incidence_min}")
        if self.incidence_max < self.incidence_min or self.incidence_max > 90:
            raise ValueError(f"incidence_max must be in [{self.incidence_min}, 90]: {self.incidence_max}")
        if self.look_direction not in ("left", "right", "both"):
            raise ValueError(f"look_direction must be 'left', 'right', or 'both': {self.look_direction}")
        if self.antenna_type not in ("phased_array", "reflector"):
            raise ValueError(f"antenna_type must be 'phased_array' or 'reflector': {self.antenna_type}")

    @property
    def can_look_left(self) -> bool:
        return self.look_direction in ("left", "both")

    @property
    def can_look_right(self) -> bool:
        return self.look_direction in ("right", "both")

    @classmethod
    def sentinel1_like(cls) -> "SARInstrument":
        """Traditional phased-array, fixed right-looking (Sentinel-1 IW)."""
        return cls(
            incidence_min=18.0,
            incidence_max=47.0,
            look_direction="right",
            antenna_type="phased_array",
            min_elevation=10.0,
        )

    @classmethod
    def iceye_like(cls) -> "SARInstrument":
        """Agile reflector, left+right looking (ICEYE/Capella-like)."""
        return cls(
            incidence_min=15.0,
            incidence_max=35.0,
            look_direction="both",
            antenna_type="reflector",
            min_elevation=5.0,
        )

    @classmethod
    def permissive(cls) -> "SARInstrument":
        """Wide-angle incidence 0–90° + both-side looking for exploratory search — broad but still bounded by Earth geometry."""
        return cls(
            incidence_min=0.0,
            incidence_max=90.0,
            look_direction="both",
            antenna_type="reflector",
            min_elevation=0.0,
        )


# ─── Observation / Scheduling Types ────────────────────────────────────

@dataclass(frozen=True)
class ObservationWindow:
    """A candidate observation opportunity.

    satellite_id: which satellite
    target_id: which target
    t_start: earliest possible observation start
    t_end: latest possible observation end
    t_optimal: time of best observation geometry
    elevation: max elevation angle during window (degrees)
    off_nadir_angle: off-nadir angle at t_optimal (degrees)
        Angle between nadir direction and satellite-to-target vector.
        Related to incidence angle by Earth curvature correction.
    look_direction: which side of track the target lies on ("left"/"right")
    duration_min: minimum required observation duration (seconds)
    """
    satellite_id: str
    target_id: str
    t_start: datetime
    t_end: datetime
    t_optimal: datetime
    elevation: float
    off_nadir_angle: float = 0.0
    look_direction: str = "right"
    duration_min: float = 30.0

    @property
    def duration(self) -> timedelta:
        return self.t_end - self.t_start


@dataclass(frozen=True)
class ScheduledObservation:
    """A scheduled (committed) observation task.

    window: the observation window selected
    t_actual_start: actual scheduled start time
    t_actual_end: actual scheduled end time
    """
    window: ObservationWindow
    t_actual_start: datetime
    t_actual_end: datetime

    @property
    def satellite_id(self) -> str:
        return self.window.satellite_id

    @property
    def target_id(self) -> str:
        return self.window.target_id


@dataclass(frozen=True)
class Conflict:
    """A conflict between two observations.

    obs_a, obs_b: conflicting scheduled observations
    conflict_type: 'temporal', 'resource', 'geometric'
    description: human-readable explanation
    """
    obs_a: ScheduledObservation
    obs_b: ScheduledObservation
    conflict_type: str
    description: str = ""


# ─── Scenario ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ScenarioConfig:
    """Top-level scenario configuration.

    time_start, time_end: simulation time window
    satellites: list of satellite IDs with their orbital elements
    targets: list of ground targets
    """
    time_start: datetime
    time_end: datetime
    satellite_ids: Tuple[str, ...] = ()
    target_ids: Tuple[str, ...] = ()


# ─── Solver ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SolverResult:
    """Output from any solver.

    schedule: list of scheduled observations
    score: objective function value (higher = better)
    metadata: solver-specific diagnostic info
    """
    schedule: Tuple[ScheduledObservation, ...]
    score: float
    metadata: dict = field(default_factory=dict)
