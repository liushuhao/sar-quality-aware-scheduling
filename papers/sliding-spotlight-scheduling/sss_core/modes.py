"""Imaging-mode library and per-mode azimuth resolution.

Formula source (FROZEN): formula-spec v1.0.1 §3 --

    rho_a,STR = D/2
    rho_a,SLS = A * D/2            (== (1-k) * D/2 under the k bridge)
    rho_a,SPT = lambda / (2 * beta_span)

The SPT design point (0.3 m) is the mode-library constant frozen in
formula-spec §6 table 1 (ticket 01): the library must place the SPT tier
STRICTLY finer than the SLS tier (Kim's single 0.5 m design point would
make SLS == SPT and is forbidden for ordering assertions, §6 设计约束登记).

The mode ordering rho_a,STR > rho_a,SLS > rho_a,SPT is the tier backbone
consumed by the D2 coarsest-sufficient mapping (ticket 08).
"""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass

from .geometry import DerivedGeometry

# formula-spec §6 table 1 (ticket 01 frozen): SPT library design point.
SPT_DESIGN_RHO_M = 0.3


class Mode(enum.Enum):
    STR = "stripmap"
    SLS = "sliding_spotlight"
    SPT = "staring_spotlight"


@dataclass(frozen=True)
class ModeLibrary:
    """Per-mode achieved azimuth resolutions derived from the fixture."""

    geo: DerivedGeometry
    beta_span_spt_rad: float  # SPT library design point (rho = SPT_DESIGN_RHO_M)

    @classmethod
    def from_fixture(cls) -> "ModeLibrary":
        geo = DerivedGeometry.from_fixture()
        beta_span = geo.wavelength_m / (2.0 * SPT_DESIGN_RHO_M)
        return cls(geo=geo, beta_span_spt_rad=beta_span)

    def rho_az(self, mode: Mode) -> float:
        """Achieved azimuth resolution [m] for a library mode (formula-spec §3)."""
        if mode is Mode.STR:
            return self.geo.D_m / 2.0
        if mode is Mode.SLS:
            return self.geo.A * self.geo.D_m / 2.0
        if mode is Mode.SPT:
            return self.geo.wavelength_m / (2.0 * self.beta_span_spt_rad)
        raise ValueError(f"unknown mode {mode!r}")

    def beta_span(self, mode: Mode) -> float:
        """Azimuth steering span [rad] the mode must sweep (formula-spec §4.2)."""
        if mode is Mode.SPT:
            return self.beta_span_spt_rad
        if mode is Mode.SLS:
            # point-target total viewing angle alpha = theta_a / A (formula-spec §5
            # identity); the steering span is the beam-axis part alpha - theta_a.
            return self.geo.theta_a_rad / self.geo.A - self.geo.theta_a_rad
        if mode is Mode.STR:
            return 0.0
        raise ValueError(f"unknown mode {mode!r}")

    def rho_ordering_strict(self) -> bool:
        """True iff STR > SLS > SPT holds strictly (formula-spec §6 table 1)."""
        rho_str = self.rho_az(Mode.STR)
        rho_sls = self.rho_az(Mode.SLS)
        rho_spt = self.rho_az(Mode.SPT)
        return rho_str > rho_sls > rho_spt


def sec2(x_rad: float) -> float:
    """sec^2 with a domain guard (tan undefined at +-pi/2)."""
    c = math.cos(x_rad)
    if abs(c) < 1e-12:
        raise ValueError("sec^2 singular: |psi| -> 90 deg outside squint envelope")
    return 1.0 / (c * c)
