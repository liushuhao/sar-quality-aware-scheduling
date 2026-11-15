"""Orbital mechanics: Keplerian-to-ECI propagation.

Uses Newton-Raphson to solve Kepler's equation, then converts
Keplerian elements to ECI state vectors.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Tuple

from sar_sim.types import KeplerianElement, ECIState

# Earth gravitational parameter (m^3/s^2)
MU_EARTH = 3.986004418e14


def solve_kepler(M: float, e: float, tol: float = 1e-12, max_iter: int = 100) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E.

    Uses Newton-Raphson: E_{n+1} = E_n - (E_n - e*sin(E_n) - M) / (1 - e*cos(E_n))

    Args:
        M: mean anomaly (radians)
        e: eccentricity [0, 1)
        tol: convergence tolerance
        max_iter: maximum iterations

    Returns:
        E: eccentric anomaly (radians)
    """
    # Initial guess: E0 = M + e*sin(M) + 0.5*e^2*sin(2M) (good for moderate e)
    E = M + e * np.sin(M) + 0.5 * e**2 * np.sin(2 * M)
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        f_prime = 1.0 - e * np.cos(E)
        delta = f / f_prime
        E -= delta
        if abs(delta) < tol:
            return E
    return E  # Return best estimate if not converged


def _rgf(phi: float) -> np.ndarray:
    """Rotation about z-axis (RAAN)."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _rgi(phi: float) -> np.ndarray:
    """Rotation about x-axis (inclination)."""
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _rgu(phi: float) -> np.ndarray:
    """Rotation about z-axis (argument of perigee)."""
    return _rgf(phi)


def kepler_to_eci(elements: KeplerianElement, t: datetime = None) -> ECIState:
    """Convert Keplerian elements to ECI state at time t.

    Args:
        elements: orbital elements at epoch
        t: target time (default: elements.epoch)

    Returns:
        ECIState with position and velocity
    """
    if t is None:
        t = elements.epoch

    dt = (t - elements.epoch).total_seconds()

    # Mean motion (rad/s)
    n = np.sqrt(MU_EARTH / elements.semi_major_axis**3)

    # Mean anomaly at t
    M = elements.true_anomaly + n * dt

    # Handle multi-revolution: mean anomaly wrapping
    M = M % (2 * np.pi)

    # Solve Kepler's equation
    E = solve_kepler(M, elements.eccentricity)

    # True anomaly
    nu = 2.0 * np.arctan2(
        np.sqrt(1.0 + elements.eccentricity) * np.sin(E / 2.0),
        np.sqrt(1.0 - elements.eccentricity) * np.cos(E / 2.0),
    )

    # Distance
    r = elements.semi_major_axis * (1.0 - elements.eccentricity * np.cos(E))

    # Position in perifocal frame
    x_peri = r * np.cos(nu)
    y_peri = r * np.sin(nu)
    r_peri = np.array([x_peri, y_peri, 0.0])

    # Velocity in perifocal frame
    p = elements.semi_major_axis * (1.0 - elements.eccentricity**2)
    vx_peri = -np.sqrt(MU_EARTH / p) * np.sin(nu)
    vy_peri = np.sqrt(MU_EARTH / p) * (elements.eccentricity + np.cos(nu))
    v_peri = np.array([vx_peri, vy_peri, 0.0])

    # Rotation: 3-1-3 (RAAN → inclination → arg_perigee)
    R = _rgu(elements.arg_perigee) @ _rgi(elements.inclination) @ _rgf(elements.raan)

    pos_eci = R @ r_peri
    vel_eci = R @ v_peri

    return ECIState(position=pos_eci, velocity=vel_eci, time=t)


def propagate_orbit(
    elements: KeplerianElement,
    t_start: datetime,
    t_end: datetime,
    step: timedelta = timedelta(seconds=60),
) -> list[ECIState]:
    """Generate ECI states at regular time steps over an interval.

    Args:
        elements: orbital elements at epoch
        t_start: start of propagation
        t_end: end of propagation
        step: time step

    Returns:
        list of ECIState, one per time step
    """
    states = []
    t = t_start
    while t <= t_end:
        state = kepler_to_eci(elements, t)
        states.append(state)
        t += step
    return states
