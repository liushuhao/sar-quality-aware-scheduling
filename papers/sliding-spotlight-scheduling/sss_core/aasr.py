"""AASR hard constraint + four-key lookup grid + promotion scatter (spec D7).

Formula source (FROZEN): formula-spec v1.0.1 §5 -- Song 2025 Eq.(6)
(stripmap), Eq.(7) (spotlight/staring, t_0-dependent), Eq.(9)-(10)
(sliding/TOPS family, spectral-axis rescale f' = (1 - K_c/K_a)(f - f_ac)).
Ticket-06 decisions D06-1..9 (registered in the ticket after the
pre-implementation gate review):

* D06-1  processed bandwidth B_D = Vs*cos(psi)/rho_ach(mode) -- derived
  EXACTLY from the frozen duration chain (T = lambda*R*sec^2/(D*A*Vs)
  times K_a = 2 Vs^2 cos^3/(lambda R0)), so the squint factor is cos^1
  (not cos^3), and the bandwidth is ACHIEVED-resolution based (spec D6
  product semantics; requirement-based bandwidth would be narrower and
  anti-conservative).  The beta_req key routes to a mode via
  beta = lambda/(2 rho) (§8.5); it is a routing key, not a physics key.
  Structural identity (audit-corrected 2026-09-29, ticket 13): at
  psi = 0 with k = k_lib the SLS band folds exactly onto the STR band
  (B_D ratio 1/(1-k_lib) = 1/A folds the ambiguity pattern onto itself),
  so AASR_SLS(k_lib, 0) == AASR_STR to 0.000 dB (verified at 1150/2300/
  3630 Hz).  The ORIGINAL registration wording ("a_res = 1 at psi = 0 /
  k = 0 implies AASR_SLS == AASR_STR") is FALSE: at k = 0 the SLS
  bandwidth is ~A-fold narrower, and measured AASR differs by up to
  8 dB (e.g. +10.64 vs +2.58 dB at 1150 Hz).
* D06-2  SPT (Eq.(7)) is evaluated at the WORST azimuth scene EDGE
  (|K_a t_0|max = (2 Vs/lambda) * (Wa/2)/R0): the scene-centre value is
  ~8 dB optimistic and would leak infeasible edge targets through the
  hard constraint (anti-conservative, D7 violation).
* D06-3  K_c = (2 Vs/lambda) * k_theta * cos(psi)  =>  K_c/K_a = k/cos^2(psi)
  (the exact rate keeps a_res > 0 up to psi ~ 18.4 deg at k = 0.9; the
  Song cos^3 / small-angle readings go negative only beyond psi ~ 15.1
  deg -- audit 2026-09-30 re-registration: the old "goes negative at
  the k=0.9/psi=12 deg corner" quote was not reproducible (+0.038/+0.10
  measured there)); a_res > 0 is a domain guard.
* D06-4  PRF keys (Kim publishes none; sourced per ticket-06 mandate):
  1150 / 2300 Hz  Song 2025 Table 1 (in-house fulltext, txt:376-383);
  3044 Hz  TerraSAR-X concurrent-imaging effective PRF (Kraus et al.,
  IEEE 2022, web-sourced mapping reference);
  3630 Hz  TerraSAR-X spotlight acquisition parameter at 43 deg incidence
  (ESA TDX mission presentation, web-sourced mapping reference;
  corroboration Steinbrecher 2014 >=3100 Hz, Kraus 2016 staring-spotlight
  optimization).  Non-key PRF queries raise (no extrapolation, D7
  discipline 2).
* D06-5  threshold: AASR <= -13 dB (preregistered main value).  Source:
  Villano 2016 (DLR dissertation) discusses -13 dB as the boundary of
  typical AASR requirements; the figure's lineage is the uniform-aperture
  first sidelobe (-13.26 dB).  -10/-14 exist ONLY as sensitivity
  alternates (spec D7: no post-hoc tuning).
* D06-6  the Song "8.6 dB degradation beyond 1 deg scan" anchor is NOT
  reproducible under the M=1 uniform-aperture model (its mechanism is the
  sparse-array scan-dependent element pattern, Song p.8/Fig.6) -- it is a
  documented model limitation here, never a test assertion.  The US6
  literature anchor is the PRF anti-correlation (avoiding the 3044 Hz
  pattern-null landing for SPT, which is real physics, not a bug).
* D06-7  cell bound = max over the corner set of the continuous axes
  (rho_req is constant within a routed band, so 2 axes x 2 = 4 corners);
  conservatism is tested by random IN-CELL sampling (interior <= bound),
  not by a single constructed case.  US6 tolerance concretely: direct <=
  bound pointwise and bound - direct <= the in-cell spread.
* D06-8  numeric test expectations are generated from the implementation's
  own integration plus structural properties (identities / monotonicity /
  symmetry); the ticket's hand figures are directional references only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .modes import Mode, ModeLibrary

# ── registered constants (D06-4/5) ───────────────────────────────────────

PRF_KEYS_HZ = (1150.0, 2300.0, 3044.0, 3630.0)
PRF_PROVENANCE = {
    1150.0: "Song 2025 Table 1 (SS1), literature/fulltext/song2025_sensors_sparse.txt:376-383",
    2300.0: "Song 2025 Table 1 (SS2), literature/fulltext/song2025_sensors_sparse.txt:376-383",
    3044.0: (
        "TerraSAR-X concurrent-imaging effective PRF, Kraus et al. 2022 IEEE "
        "(https://ieeexplore.ieee.org/iel7/36/9633014/09668948.pdf); "
        "web-sourced mapping reference (ticket 06 D06-4)"
    ),
    3630.0: (
        "TerraSAR-X spotlight acquisition parameter @43deg incidence, ESA TDX "
        "mission presentation (https://eo4society.esa.int/wp-content/uploads/"
        "2019/01/TDXMission_IHajnsek.pdf); corroboration: Steinbrecher 2014 "
        ">=3100 Hz (https://elib.dlr.de/91122/1/p189-steinbrecher.pdf), Kraus "
        "2016 (https://elib.dlr.de/92033/1/Kraus2016.pdf); web-sourced mapping "
        "reference (ticket 06 D06-4)"
    ),
}

AASR_THRESHOLD_DB = -13.0  # preregistered main value (D06-5)
AASR_SENSITIVITY_ALTERNATES_DB = (-10.0, -14.0)  # sensitivity table ONLY

# default axes (module-level so the preregistration is inspectable); a grid
# instance binds its OWN axis copies -- densified variants never mutate these.
# The rho_req domain STARTS at the finest serviceable tier (SPT library point
# 0.3 m): requirements below it are unserviceable and raise at routing time
# (ticket 08 removes them at scenario generation).
# OPERATIVE DENSITY NOTE (D7 discipline 3, applied 2026-09-27 during ticket
# 06 verification BEFORE any experiment consumed the grid): the initial
# 24x25x19 grid failed the halving-stability bound (flip rate 1.67% > 0.5%),
# so the operative density was escalated to 24x37x28 and then the k axis
# was further densified 28 -> 55 (D06 addendum 5: the k = 1-A library
# design point must sit in a cell whose BOUND, not just direct value,
# clears -13 dB); the flip check must hold against its own 2x
# densification.  Actual operative axes: rho 24 x psi 37 x k 55
# (audit-corrected from the stale "24x37x28" wording, 2026-09-29).
RHO_REQ_AXIS_DEFAULT = tuple(round(0.3 + i * (3.0 - 0.3) / 23, 6) for i in range(24))
PSI_AXIS_DEG_DEFAULT = tuple(round(-12.0 + i * 24.0 / 36, 6) for i in range(37))
K_AXIS_DEFAULT = tuple(round(i * 0.9 / 54, 6) for i in range(55))  # k in [0, 0.9];
# k-cell width 0.0167: the SLS library design point k = 1-A must sit in a
# cell tight enough that its bound (not just its direct value) clears -13 dB

# D06-7 amendment (re-registered 2026-09-29, ticket-13 audit): the
# original justification -- a measured interior k-resonance peak of
# 8.96 dB vs an 8.79 dB sampled max -- DOES NOT REPRODUCE under the
# shipped physics: exhaustive k-scans (901 points x PRF {1150, 2300,
# 3630} Hz at psi = 0, plus dense psi rows) find AASR(k) monotone
# DECREASING with the maximum at the k = 0 endpoint, so the corner/
# block-max bound is already conservative in the current code (the
# resonance was real in the pre-fix code state that motivated the
# margin; the D06-2/D06-3 corrections apparently removed it).
# The +1.0 dB margin is RETAINED unchanged as frozen conservative
# slack: it only shrinks the feasible set, and it keeps the bound
# robust against any future structural change of the k-axis shape.
# In-cell spans measured <= 0.8 dB at mid-grid; bound - direct =
# 1.0-1.7 dB at mid-grid but up to 6.64 dB at grid corners (worst:
# STR/3044 Hz/psi=12 deg; corner-biased 400-sample scan, audit
# 2026-09-30 re-registration) -- slack grows away from mid-grid in the
# conservative direction; bound >= direct held 400/400.
AASR_CELL_MARGIN_DB = 1.0

N_INTEGRATION_POINTS = 256
N_ALIASES = 6  # |m| <= 6 (sinc^4 decay; D06-9)


def _sinc(x):
    out = np.ones_like(x)
    small = np.abs(x) < 1e-12
    xs = np.where(small, 1.0, x)
    out = np.sin(np.pi * xs) / (np.pi * xs)
    return np.where(small, 1.0, out)


def _pattern(f_rel_hz, vs_mps: float, d_m: float):
    """Two-way azimuth power pattern at RELATIVE Doppler (D06-1):

    G(f) = sinc^2(D f / (2 Vs)) -- the M=1 uniform-aperture simplification
    anchored on formula-spec §5 G_e = sinc^2 structure (no published AAP
    decomposition; the sparse-array scan-dependent element pattern of Song
    is out of scope, D06-6).
    """
    return _sinc(d_m * np.asarray(f_rel_hz) / (2.0 * vs_mps)) ** 2


def route_mode(rho_req_m: float, lib: ModeLibrary) -> Mode:
    """Coarsest-sufficient routing (coarse -> fine, first tier satisfying
    rho_ach <= rho_req).  Footprint legality is a ticket-08 generation-time
    concern and intentionally NOT here (single-predicate layering, D9)."""
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        if lib.rho_az(mode) <= rho_req_m + 1e-12:
            return mode
    raise ValueError(
        f"rho_req={rho_req_m} m is finer than the best library tier "
        f"({lib.rho_az(Mode.SPT)} m): unserviceable -- ticket 08 removes "
        "such targets at scenario generation"
    )


def aasr_direct(
    mode: Mode,
    psi_bar_rad: float,
    k: float,
    prf_hz: float,
    lib: ModeLibrary,
    spt_edge_worst: bool = True,
    spt_scene_wa_m: float | None = None,
) -> dict:
    """Direct AASR (power ratio) for one library mode (D06-1/2/3).

    ``spt_scene_wa_m`` (ticket 08 D08-2, D06-2 amendment): per-scene
    azimuth extent for the SPT worst-edge evaluation; default None keeps
    the frozen platform-level scene_wa_m (5 km) -- the generator passes
    the per-task L_az (a 1-3 km scene IS its own worst edge; the 5 km
    default is over-conservative, never under-conservative, for smaller
    scenes)."""
    geo = lib.geo
    vs, lam, r0 = geo.vs_mps, geo.wavelength_m, geo.R0_m
    rho_ach = lib.rho_az(mode)
    cos_psi = math.cos(psi_bar_rad)

    if mode is Mode.SPT:
        # Eq.(7): the integrand is independent of f_a; worst azimuth edge
        wa = geo.scene_wa_m if spt_scene_wa_m is None else float(spt_scene_wa_m)
        kat0 = (2.0 * vs / lam) * (wa / 2.0) / r0 if spt_edge_worst else 0.0
        m = np.array([i for i in range(-N_ALIASES, N_ALIASES + 1) if i != 0], dtype=float)
        p = _pattern(m * prf_hz - kat0, vs, geo.D_m)
        num = float(np.sum(p**2))
        den = float(_pattern(np.array(-kat0), vs, geo.D_m) ** 2)
        ratio = num / den
    else:
        b_d = vs * cos_psi / rho_ach  # D06-1
        if mode is Mode.SLS:
            k_a = 2.0 * vs * vs * cos_psi**3 / (lam * r0)
            k_c = (2.0 * vs / lam) * (k * vs / r0) * cos_psi
            a_res = 1.0 - k_c / k_a
            if a_res <= 0.0:
                raise ValueError(
                    f"a_res = 1 - Kc/Ka = {a_res} <= 0 outside the physical "
                    "sliding domain (D06-3 guard)"
                )
        elif mode is Mode.STR:
            a_res = 1.0
        else:  # pragma: no cover
            raise ValueError(f"unknown mode {mode!r}")

        f = -b_d / 2.0 + (np.arange(N_INTEGRATION_POINTS) + 0.5) * (b_d / N_INTEGRATION_POINTS)
        ar = a_res * f
        den = float(np.sum(_pattern(ar, vs, geo.D_m) ** 2)) * (b_d / N_INTEGRATION_POINTS)
        num = 0.0
        for m in range(-N_ALIASES, N_ALIASES + 1):
            if m == 0:
                continue  # standard C&W convention: Song prints sum over m in
                # Z, but including m=0 would force AASR >= 1 (registered)
            num += float(np.sum(_pattern(ar + m * prf_hz, vs, geo.D_m) ** 2)) * (
                b_d / N_INTEGRATION_POINTS
            )
        ratio = num / den
    return {
        "aasr": ratio,
        "aasr_db": 10.0 * math.log10(ratio) if ratio > 0 else float("-inf"),
        "mode": mode,
        "prf_hz": prf_hz,
    }


# ── four-key lookup grid (D06-4/7) ───────────────────────────────────────

@dataclass(frozen=True)
class GridAxes:
    """Axis copies bound to one grid instance (densified variants never
    mutate the module-level preregistration)."""

    rho_req: tuple = RHO_REQ_AXIS_DEFAULT
    psi_deg: tuple = PSI_AXIS_DEG_DEFAULT
    k: tuple = K_AXIS_DEFAULT


class AASRGrid:
    """Preregistered lookup grid over (rho_req, psi, k, PRF).

    rho_req routes to a mode; within a routed band the physics is
    rho_req-independent, so each cell bound = max over the 4 corners of
    (psi, k) at the routed mode.  Axis-POINT values are precomputed once
    (numpy-vectorized integration) and cells are pure lookups.  Hard
    verdicts use the CELL UPPER BOUND (conservative, D7 discipline 1);
    out-of-domain queries raise (discipline 2); halving stability is
    exposed for the verify gate (discipline 3).
    """

    def __init__(self, lib: ModeLibrary, axes: GridAxes | None = None):
        self.lib = lib
        self.axes = axes or GridAxes()
        psi_ax = self.axes.psi_deg
        k_ax = self.axes.k
        modes = sorted({route_mode(r, lib) for r in self.axes.rho_req[:-1]}, key=lambda m: m.value)
        self._modes = modes

        # D06-7 (amended, gate-review F6 confirmed non-monotone k structure):
        # the cell bound is the max over a 3x-densified (psi, k) sub-grid per
        # cell -- corners PLUS two interior sub-points per axis -- because
        # pure corner maxima UNDER-estimate interior resonance peaks on the
        # k axis (measured violation: interior 8.96 dB vs corner max 8.79).
        # The residual risk (sub-midpoint extrema) is covered empirically by
        # the halving-stability check (D7 discipline 3).
        # k carries the resonance-steep structure (measured sub-sample
        # overshoot up to 1.08 dB at PRF keys near the pattern null), so the
        # k axis is refined 5x while the smooth psi axis stays at 3x
        self._n_sub_psi = 3
        self._n_sub_k = 5
        self._psi_dense = np.linspace(
            psi_ax[0], psi_ax[-1], self._n_sub_psi * (len(psi_ax) - 1) + 1
        )
        self._k_dense = np.linspace(k_ax[0], k_ax[-1], self._n_sub_k * (len(k_ax) - 1) + 1)
        # dense dB table: (mode, prf) -> ndarray (len(psi_dense), len(k_dense))
        self._dense: dict[tuple, np.ndarray] = {}
        for prf in PRF_KEYS_HZ:
            for mode in modes:
                self._dense[(mode, prf)] = self._build_dense(mode, prf)

    def _build_dense(self, mode: Mode, prf_hz: float) -> np.ndarray:
        """Vectorized AASR_dB over the dense (psi, k) sub-grid (psi chunks
        bound the tensor size).  SPT is the Eq.(7) collapsed form: it has no
        band integral and no k dependence, so its dense table is a single
        (psi-, k-invariant) constant per PRF."""
        if mode is Mode.SPT:
            val = aasr_direct(mode, 0.0, 0.0, prf_hz, self.lib)["aasr_db"]
            return np.full((len(self._psi_dense), len(self._k_dense)), val)
        geo = self.lib.geo
        vs, lam, r0 = geo.vs_mps, geo.wavelength_m, geo.R0_m
        rho_ach = self.lib.rho_az(mode)
        psi_rad = np.radians(self._psi_dense)
        cos_psi = np.cos(psi_rad)
        k_arr = np.asarray(self._k_dense)
        f = -1.0 + (np.arange(N_INTEGRATION_POINTS) + 0.5) * (2.0 / N_INTEGRATION_POINTS)
        # midpoint rule, identical sampling to aasr_direct (scaled per psi)
        table = np.empty((len(self._psi_dense), len(self._k_dense)))
        chunk = 32
        for j0 in range(0, len(self._psi_dense), chunk):
            cp = cos_psi[j0 : j0 + chunk][:, None]  # (nc, 1)
            b_d = vs * cp / rho_ach  # (nc, 1)
            fr = (b_d * 0.5)[:, :, None] * f[None, None, :]  # (nc, 1, n_f) over +-B_D/2
            if mode is Mode.SLS:
                k_a = 2.0 * vs * vs * cp**3 / (lam * r0)
                k_c = (2.0 * vs / lam) * (k_arr[None, :] * vs / r0) * cp
                a_res = 1.0 - k_c / k_a  # (nc, n_k)
            else:
                a_res = np.ones((cp.shape[0], len(k_arr)))
            ar = a_res[:, :, None] * fr  # (nc, n_k, n_f)
            with np.errstate(divide="ignore", invalid="ignore"):
                den = np.sum(_pattern(ar, vs, geo.D_m) ** 2, axis=2)
                num = np.zeros_like(den)
                for m in range(-N_ALIASES, N_ALIASES + 1):
                    if m == 0:
                        continue  # C&W convention (see aasr_direct note)
                    num += np.sum(_pattern(ar + m * prf_hz, vs, geo.D_m) ** 2, axis=2)
                ratio = num / den
            ratio = np.where(a_res > 0.0, ratio, np.inf)  # outside sliding domain
            with np.errstate(divide="ignore"):
                table[j0 : j0 + chunk, :] = 10.0 * np.log10(ratio)
        return table

    # -- domain guards -----------------------------------------------------
    def _domain_check(self, rho_req_m, psi_bar_rad, k, prf_hz) -> None:
        if prf_hz not in PRF_KEYS_HZ:
            raise ValueError(f"PRF {prf_hz} Hz is not a registered key {PRF_KEYS_HZ}")
        if not (self.axes.rho_req[0] - 1e-9 <= rho_req_m <= self.axes.rho_req[-1] + 1e-9):
            raise ValueError(f"rho_req {rho_req_m} m outside grid domain")
        if not (-12.0 - 1e-9 <= math.degrees(psi_bar_rad) <= 12.0 + 1e-9):
            raise ValueError("psi_bar outside the +-12 deg platform envelope")
        if not (0.0 - 1e-12 <= k <= self.axes.k[-1] + 1e-12):
            raise ValueError(f"k = {k} outside the grid domain [0, {self.axes.k[-1]}]")
        route_mode(rho_req_m, self.lib)  # unserviceable requirements raise

    def _locate(self, rho_req_m, psi_bar_rad, k, prf_hz):
        """(mode, i_psi, i_k) for a query -- the MODE routes by the EXACT
        query rho (tier boundaries fall inside axis cells, and the bound
        must be the routed mode's physics, never a neighbour's).  The cell
        is the CONTAINING interval (bisect), so the bound always covers the
        query point (final-review minor fix; previously nearest-axis-point
        could pick a neighbouring cell not containing the query)."""
        deg = math.degrees(psi_bar_rad)
        i_psi = (
            __import__("bisect").bisect_right(self.axes.psi_deg, deg) - 1
        )
        i_psi = max(0, min(i_psi, len(self.axes.psi_deg) - 2))
        i_k = __import__("bisect").bisect_right(self.axes.k, k) - 1
        i_k = max(0, min(i_k, len(self.axes.k) - 2))
        mode = route_mode(rho_req_m, self.lib)
        return mode, i_psi, i_k

    def _cell_bound(self, rho_req_m, psi_bar_rad, k, prf_hz) -> float:
        mode, i_psi, i_k = self._locate(rho_req_m, psi_bar_rad, k, prf_hz)
        np_, nk = self._n_sub_psi, self._n_sub_k
        block = self._dense[(mode, prf_hz)][
            np_ * i_psi : np_ * i_psi + np_ + 1, nk * i_k : nk * i_k + nk + 1
        ]
        return float(block.max()) + AASR_CELL_MARGIN_DB  # D06-7 margin

    def point_corners(self, rho_req_m, psi_bar_rad, k, prf_hz) -> list[float]:
        """Direct AASR at the 4 cell corners (US6 in-cell-spread check)."""
        self._domain_check(rho_req_m, psi_bar_rad, k, prf_hz)
        mode, i_psi, i_k = self._locate(rho_req_m, psi_bar_rad, k, prf_hz)
        dense = self._dense[(mode, prf_hz)]
        np_, nk = self._n_sub_psi, self._n_sub_k
        return [
            float(dense[np_ * i_psi + dp, nk * i_k + dk])
            for dp in (0, np_)
            for dk in (0, nk)
        ]

    # -- queries ------------------------------------------------------------
    def query_bound_db(self, rho_req_m, psi_bar_rad, k, prf_hz) -> float:
        """Cell-upper-bound AASR in dB (hard-constraint input, discipline 1)."""
        self._domain_check(rho_req_m, psi_bar_rad, k, prf_hz)
        return self._cell_bound(rho_req_m, psi_bar_rad, k, prf_hz)

    def is_feasible(self, rho_req_m, psi_bar_rad, k, prf_hz,
                    threshold_db: float = AASR_THRESHOLD_DB) -> bool:
        """Hard constraint on the cell UPPER bound (conservative)."""
        return self.query_bound_db(rho_req_m, psi_bar_rad, k, prf_hz) <= threshold_db

    def direct_db(self, rho_req_m, psi_bar_rad, k, prf_hz) -> float:
        """Direct (unbounded) AASR in dB at the routed mode."""
        self._domain_check(rho_req_m, psi_bar_rad, k, prf_hz)
        mode = route_mode(rho_req_m, self.lib)
        return aasr_direct(mode, psi_bar_rad, k, prf_hz, self.lib)["aasr_db"]

    def promotion_scatter_db(self, candidates) -> dict:
        """D7 / steel-man A13: UNENFORCED AASR values over candidate
        schedules -- promotion statistics run on this unconstrained
        distribution (a threshold-filtered sample is capped at the
        threshold and the promotion could never trigger)."""
        vals = [self.direct_db(*c) for c in candidates]
        if not vals:
            raise ValueError("promotion scatter over an EMPTY candidate set")
        return {"values_db": vals, "max_db": max(vals), "min_db": min(vals), "n": len(vals)}

    def halving_stability(self, samples, threshold_db: float = AASR_THRESHOLD_DB) -> dict:
        """D7 discipline 3: feasibility-flag flip rate between this grid and
        a 2x-densified rebuild; preregistered bound = 0.5% flip rate,
        exceeding BLOCKS and escalates the grid density."""
        def densify(axis):
            n = len(axis) - 1
            return tuple(
                round(axis[0] + i * (axis[-1] - axis[0]) / (2 * n), 9) for i in range(2 * n + 1)
            )

        fine_axes = GridAxes(
            rho_req=self.axes.rho_req,
            psi_deg=densify(self.axes.psi_deg),
            k=densify(self.axes.k),
        )
        fine = AASRGrid(self.lib, fine_axes)
        flips = 0
        for rho, psi, k, prf in samples:
            if self.is_feasible(rho, psi, k, prf, threshold_db) != fine.is_feasible(
                rho, psi, k, prf, threshold_db
            ):
                flips += 1
        rate = flips / len(samples)
        return {
            "n_samples": len(samples),
            "flips": flips,
            "flip_rate": rate,
            "within_preregistered_bound": rate <= 0.005,
        }
