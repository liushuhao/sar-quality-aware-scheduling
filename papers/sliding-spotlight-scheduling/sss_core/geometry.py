"""Look geometry and derived SANITY-layer platform quantities.

Formula source (FROZEN): papers/sliding-spotlight-scheduling/formulas/
formula-spec.md v1.0.1 -- §4.1 Eq.(2)-(3), §6 reference geometry, §7 SANITY
table.  Blueprint formulas are never used anywhere in sss_core (blueprint
§2.2(c) falsified, formula-spec §8.1).

SANITY-layer discipline (formula-spec §7): derived quantities (V_s, R0, D,
A, r0) may back band / identity assertions only -- never tight literature
fits -- and are frozen once frozen (retuning = new blocking gate).

Constants marked [教科书] are standard geophysical constants, not platform
parameters, hence not fixture entries.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .fixture import fixture_value, load_platform_fixture

R_EARTH_M = 6_371_000.0           # [教科书] mean Earth radius (IUGG reference)
MU_EARTH_M3_S2 = 3.986004418e14   # [教科书] geocentric gravitational constant


def look_geometry(altitude_m: float, theta_inc_deg: float) -> tuple[float, float, float]:
    """Kim Eq.(2)-(3): ``(theta_look_deg, beta_deg, R0_m)`` from h and incidence.

    Full-curvature (spherical Earth) slant range to the scene centre.
    """
    theta_inc = math.radians(theta_inc_deg)
    theta_look = math.asin(R_EARTH_M / (R_EARTH_M + altitude_m) * math.sin(theta_inc))
    beta = theta_inc - theta_look
    r0_m = (R_EARTH_M + altitude_m) * math.sin(beta) / math.sin(theta_inc)
    return math.degrees(theta_look), math.degrees(beta), r0_m


def squint_at(t: float, t_ca: float, lib_geo) -> float:
    """Planar squint angle [rad] at time t for a target whose closest
    approach is t_ca (single shared source: window precompilation, the
    evaluator dwell chain and the scenario generator all consume THIS
    function -- ticket 10 D10-7)."""
    return math.atan(lib_geo.vs_mps * (t - t_ca) / lib_geo.R0_m)


def vs_inertial(altitude_m: float) -> float:
    """[自推导·轨道力学] circular-orbit inertial speed (formula-spec §7 SANITY).

    Production squint convention (ticket 03 decision D03-5): the inertial
    figure is the frozen production value; the ECEF variant is evidence-only.
    """
    return math.sqrt(MU_EARTH_M3_S2 / (R_EARTH_M + altitude_m))


@dataclass(frozen=True)
class DerivedGeometry:
    """SANITY-layer derived platform geometry (formula-spec §7, frozen).

    Built exclusively from fixture-published values via formula-spec
    formulas -- no number in the derivation chain is invented.
    """

    altitude_m: float
    theta_inc_deg: float
    wavelength_m: float
    theta_a_rad: float
    scene_wa_m: float
    rho_design_m: float
    R0_m: float
    vs_mps: float
    D_m: float
    A: float          # sliding-spotlight factor A in (0,1); k == 1 - A
    r0_m: float

    @property
    def k(self) -> float:
        """Blueprint-notation sliding factor k == 1 - A (formula-spec §0.3)."""
        return 1.0 - self.A

    @classmethod
    def from_fixture(cls) -> "DerivedGeometry":
        fx = load_platform_fixture()
        platform = fx["platform"]
        h_m = float(fixture_value(platform, "altitude_km")) * 1000.0
        theta_inc_deg = float(
            fixture_value(fx["sat_calibration"]["scenario_geometry"], "incidence_angle_deg")
        )
        lambda_m = float(fixture_value(platform, "wavelength_m"))
        theta_a_rad = math.radians(float(fixture_value(platform, "antenna_beamwidth_deg")))
        rho_design = float(fixture_value(fx["resolution"], "resolution_m"))
        wa_m = float(fixture_value(fx["scene"], "scene_size_km")) * 1000.0

        _, _, R0_m = look_geometry(h_m, theta_inc_deg)
        vs_mps = vs_inertial(h_m)
        D_m = lambda_m / theta_a_rad          # formula-spec §7: D = lambda/theta_a
        A = 2.0 * rho_design / D_m            # formula-spec §7: A = 2*rho_kim/D
        if not 0.0 < A < 1.0:
            raise ValueError(f"derived sliding factor A={A} outside (0,1)")
        r0_m = A * R0_m / (1.0 - A)           # formula-spec §7: r0 = A*R0/(1-A)
        return cls(
            altitude_m=h_m,
            theta_inc_deg=theta_inc_deg,
            wavelength_m=lambda_m,
            theta_a_rad=theta_a_rad,
            scene_wa_m=wa_m,
            rho_design_m=rho_design,
            R0_m=R0_m,
            vs_mps=vs_mps,
            D_m=D_m,
            A=A,
            r0_m=r0_m,
        )
