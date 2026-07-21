"""Scenario generation — orchestrates orbit, target, visibility into
complete simulation scenarios.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Dict
import random

from sar_sim.types import (
    KeplerianElement,
    GroundTarget,
    ObservationWindow,
    SARInstrument,
    ScenarioConfig,
)
from sar_sim.generator.orbit import kepler_to_eci
from sar_sim.generator.target import make_targets
from sar_sim.generator.visibility import find_visibility_windows, visibility_matrix


# ─── Orbital element presets ────────────────────────────────────────────

def sun_synchronous_orbit(
    altitude_km: float = 600.0,
    ltan: float = 6.0,  # Local Time of Ascending Node (hours)
    eccentricity: float = 0.0,
    epoch: datetime = None,
) -> KeplerianElement:
    """Create a sun-synchronous orbit (SSO).

    SSO: inclination chosen so RAAN precession matches Earth's
    orbital rate (~1 deg/day), keeping LTAN fixed.

    Args:
        altitude_km: orbit altitude (km)
        ltan: local time of ascending node (0-24 hours)
        eccentricity: orbital eccentricity
        epoch: reference epoch

    Returns:
        KeplerianElement for SSO
    """
    if epoch is None:
        epoch = datetime.now(timezone.utc).replace(tzinfo=None)

    semi_major_axis = (altitude_km * 1000.0) + 6378137.0  # Re + altitude

    # Approximate inclination for SSO
    # cos(i) ≈ -2/3 * (a/Re)^(7/2) * (J2 * Re^2 / a^2 * n / omega_sun)^(-1)
    # Simplified formula for SSO inclination:
    if altitude_km < 100:
        inclination = np.radians(97.0)
    elif altitude_km < 500:
        inclination = np.radians(97.5)
    else:
        inclination = np.radians(97.8)

    # RAAN: convert LTAN hours to radians
    # At vernal equinox, LTAN hour H corresponds to RAAN ≈ H * 15 deg
    raan = np.radians(ltan * 15.0)

    return KeplerianElement(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        arg_perigee=0.0,
        true_anomaly=0.0,
        epoch=epoch,
    )


# Need numpy import at module level
import numpy as np


def random_satellites(
    n: int = 3,
    altitude_km_range: Tuple[float, float] = (400.0, 800.0),
    ltan_range: Tuple[float, float] = (0.0, 24.0),
    epoch: datetime = None,
    seed: int = None,
    instrument: SARInstrument = None,
) -> Tuple[List[str], List[KeplerianElement], Dict[str, SARInstrument]]:
    """Generate N random satellites with varied orbits.

    Args:
        n: number of satellites
        altitude_km_range: (min, max) altitude in km
        ltan_range: (min, max) LTAN in hours
        epoch: reference epoch
        seed: random seed for reproducibility
        instrument: SAR instrument config to assign to all satellites.
            If None, uses permissive default (incidence 0–90°, both-side).

    Returns:
        (satellite_ids, orbital_elements, instruments_dict)
    """
    if seed is not None:
        random.seed(seed)

    if epoch is None:
        epoch = datetime.now(timezone.utc).replace(tzinfo=None)

    if instrument is None:
        instrument = SARInstrument.permissive()

    ids = []
    elements = []
    instruments = {}

    for i in range(n):
        alt = random.uniform(*altitude_km_range)
        ltan = random.uniform(*ltan_range)
        ecc = random.uniform(0.0, 0.01)  # nearly circular

        sid = f"SAT-{i+1:02d}"
        ids.append(sid)
        elements.append(
            KeplerianElement(
                semi_major_axis=(alt * 1000.0 + 6378137.0),
                eccentricity=ecc,
                inclination=np.radians(97.0 + random.uniform(-1.0, 1.0)),
                raan=np.radians(ltan * 15.0),
                arg_perigee=random.uniform(0, 2 * np.pi),
                true_anomaly=random.uniform(0, 2 * np.pi),
                epoch=epoch,
            )
        )
        instruments[sid] = instrument

    return ids, elements, instruments


def generate_scenario(
    config: ScenarioConfig,
    satellites: dict,  # satellite_id -> KeplerianElement
    targets: List[GroundTarget],
    step: timedelta = timedelta(seconds=60),
    instruments: Optional[Dict[str, SARInstrument]] = None,
) -> dict:
    """Full scenario generation: orbits + targets → visibility windows.

    Args:
        config: scenario time boundaries
        satellites: map of satellite_id to orbital elements
        targets: list of ground targets
        step: propagation time step
        instruments: optional dict satellite_id → SARInstrument.
            Satellites without an entry use permissive default (0–90°, both-side).

    Returns:
        dict with keys:
          - 'config': ScenarioConfig
          - 'satellites': dict of id -> KeplerianElement
          - 'targets': list of GroundTarget
          - 'windows': dict of (sat_id, target_id) -> list of ObservationWindow
          - 'all_windows': flat list of all ObservationWindow
    """
    sat_ids = list(satellites.keys())
    elements = list(satellites.values())

    windows_matrix = visibility_matrix(
        elements, sat_ids, targets,
        config.time_start, config.time_end, step,
        instruments=instruments,
    )

    all_windows = []
    for key, windows in windows_matrix.items():
        all_windows.extend(windows)

    return {
        "config": config,
        "satellites": satellites,
        "targets": targets,
        "windows": windows_matrix,
        "all_windows": all_windows,
    }
