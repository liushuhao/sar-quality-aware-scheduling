"""Window-domain precompilation: feasible subinterval unions + predicates.

Turns the implicit dwell domain ``t in [a, w_e] with t + T(t) <= w_e`` into
an explicit union of maximal feasible subintervals (spec Solution #2, D9).

Contract (ticket 04 decisions D04-1..6):

* D04-1  Feasibility is the CLOSED set ``{g <= 0}`` with ``g(t) = t +
  T_eff(t) - w_e``; a boundary root (g == 0) is feasible (the schedule
  point may end exactly at the window end).  Expected fixture sets are
  therefore closed intervals -- the prototype's literal open-interval
  notation (0,9)U(19,40) is re-derived analytically as [0,9]U[19,40].
* D04-2  Enumerators consume an ALREADY-PADDED effective-duration callable;
  pad policy belongs to the caller (production wraps
  ``pad_window_tail(T(t), MarginPads.standard())``, the M?NC anchor passes
  the degenerate zero pads).  All predicates share the atomic
  :func:`feasible_at` (single predicate source, spec D9).
* D04-4  The root set is complete RELATIVE TO THE SCAN GRID plus stationary
  refinement: g-value sign changes on the grid, g'-sign-change brackets
  (kink-aware -- a |g'| jump without a zero is still a candidate bracket),
  and local-minimum refinement that recovers feasible slivers narrower
  than the grid step.  Degenerate (measure-zero) feasible points are
  returned as [x*, x*] intervals and counted, never silently dropped.
* D04-5  The non-convex fixtures in the test suite are SYNTHETIC stress
  constructions: under physical squint rates (|T'| << 1, ~0.03 s/s for the
  Kim SLS tier) g is strictly increasing and every window is a single
  interval.  No physical claim of non-convex dwell windows is made or may
  be derived from those fixtures.

The single-dip lemma (spec D9 / steel-man A15): endpoint-check sufficiency
relies on the squint angle having at most one local |psi| minimum inside
the window (the planar geometry layer keeps incidence CONSTANT, so the
incidence-monotonicity leg is trivially satisfied here).  Windows that
violate it fall back to full-aperture stepping; the fallback is exposed
through a diagnostic counter, never silent.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from scipy.optimize import brentq

from .duration import MarginPads, mode_squint_envelope_rad, pad_window_tail
from .modes import Mode, ModeLibrary

__all__ = [
    "FeasibleWindows",
    "feasible_subintervals",
    "windows_with_dip_guard",
    "feasible_at",
    "window_start_ok",
    "window_end_ok",
    "window_feasibility",
    "footprint_ok",
    "scan_span_reachable",
    "scan_rate_ok",
    "effective_duration_fn",
    "intersect_intervals",
    "mask_intervals",
]


@dataclass(frozen=True)
class FeasibleWindows:
    """Union of maximal feasible subintervals of [t_start, window_end]."""

    intervals: tuple[tuple[float, float], ...]
    n_boundary_roots: int
    n_degenerate_points: int

    def __bool__(self) -> bool:
        """True iff the feasible set is non-empty (non-degenerate)."""
        return any(hi > lo for lo, hi in self.intervals)

    def contains(self, t: float, tol: float = 1e-12) -> bool:
        return any(lo - tol <= t <= hi + tol for lo, hi in self.intervals)


def effective_duration_fn(duration, pads: MarginPads):
    """Wrap a bare duration with the caller's window-tail pad (D04-2)."""
    return lambda t: pad_window_tail(duration(t), pads)


def _derivative(g, x: float, h: float) -> float:
    return (g(x + h) - g(x - h)) / (2.0 * h)


def feasible_subintervals(
    effective_duration,
    t_start: float,
    window_end: float,
    *,
    n_scan: int = 200,
    tol_g: float = 1e-9,
    merge_tol: float = 1e-9,
    xtol: float = 1e-12,
) -> FeasibleWindows:
    """All-root enumeration of ``{t in [a, b] : g(t) <= 0}``, g = t + T - b.

    Three passes (D04-4): (1) grid sign changes of g -> brentq polish;
    (2) g' sign-change brackets -> local minima of g -> feasible slivers
    narrower than the grid are recovered by outward bracket expansion,
    near-zero minima become degenerate points; (3) endpoint enumeration.
    Maximal intervals are assembled by midpoint classification between
    consecutive boundary candidates (closed convention, D04-1).
    """
    a, b = float(t_start), float(window_end)
    if not a < b:
        # Non-degenerate domain required: zero-length and negative-length are
        # both invalid input, and NaN lands here too (every NaN comparison is
        # False). ValueError -- not a numerical fault from deeper in -- is what
        # evaluator.precompile_tasks already maps to "no feasible subintervals".
        raise ValueError("window domain empty: t_start >= window_end")
    g = lambda t: t + effective_duration(t) - window_end

    if n_scan < 1:
        # Grid density, not a domain property: the step below is (b - a) / n_scan
        # and the grid index below that is gv[-1], so either side of 1 crashes
        # inside the kernel (ZeroDivisionError / IndexError) instead of reaching
        # the caller's `except ValueError`.
        raise ValueError(f"n_scan must be >= 1: got {n_scan}")
    step = (b - a) / n_scan
    h_diff = step / 10.0
    if h_diff == 0.0:
        # span > 0 but subnormal: the grid step underflows so the derivative
        # pass would divide by zero, which the caller's `except ValueError`
        # cannot catch. Same rejection, same reason.
        raise ValueError("window domain too narrow: finite-difference step underflows to 0")
    grid = [a + i * step for i in range(n_scan + 1)]
    gv = [g(x) for x in grid]

    roots: list[float] = []

    def try_root(lo: float, hi: float) -> None:
        glo, ghi = g(lo), g(hi)
        if glo == 0.0:
            roots.append(lo)
        if glo * ghi < 0.0:
            roots.append(float(brentq(g, lo, hi, xtol=xtol)))

    # pass 1: g sign changes between adjacent grid points
    for i in range(n_scan):
        try_root(grid[i], grid[i + 1])
    if gv[-1] == 0.0:
        roots.append(b)

    # pass 2: stationary points of g via g' sign-change brackets (kink-aware;
    # a grid derivative of exactly 0.0 still classifies as min/max-like)
    degenerate: list[float] = []
    dprev = _derivative(g, grid[0], h_diff)
    for i in range(n_scan):
        dnext = _derivative(g, grid[i + 1], h_diff)
        if dprev != dnext and dprev * dnext <= 0.0:
            lo, hi = grid[i], grid[i + 1]
            x_star = None
            if dprev <= 0.0 <= dnext and (dprev < 0.0 or dnext > 0.0):
                # local-minimum-like bracket: the only stationary class that
                # can create (narrow) feasible slivers or tangent points
                try:
                    x_star = float(
                        brentq(lambda t: _derivative(g, t, h_diff), lo, hi, xtol=xtol)
                    )
                except ValueError:
                    x_star = min((lo, hi), key=g)
            if x_star is not None:
                g_star = g(x_star)
                if g_star < -tol_g:
                    # feasible dip: recover its two edges by outward brackets
                    try_root(lo, x_star)
                    try_root(x_star, hi)
                elif abs(g_star) <= tol_g:
                    degenerate.append(x_star)  # exact tangency -> measure-zero point
        dprev = dnext

    # pass 3: endpoint roots
    if abs(gv[0]) <= tol_g:
        roots.append(a)
    if abs(gv[-1]) <= tol_g:
        roots.append(b)

    # dedupe boundary candidates within merge_tol
    deduped: list[float] = []
    for r in sorted(roots):
        if not deduped or r - deduped[-1] > merge_tol:
            deduped.append(r)

    # assemble maximal feasible runs by midpoint classification; dedupe
    # candidates so a root landing on a domain bound never spawns a
    # spurious zero-width pair
    candidates = sorted(set(deduped) | {a, b})
    intervals: list[tuple[float, float]] = []
    for left, right in zip(candidates, candidates[1:]):
        if g((left + right) / 2.0) <= 0.0:
            intervals.append((left, right))
    for x in degenerate:
        if a <= x <= b and not any(lo <= x <= hi for lo, hi in intervals):
            intervals.append((x, x))

    return FeasibleWindows(
        intervals=tuple(intervals),
        n_boundary_roots=len(deduped),
        n_degenerate_points=len(degenerate),
    )


def _count_abs_squint_minima(squint_fn, a: float, b: float, n: int) -> int:
    """Local minima of |psi(t)| on a grid (the single-dip lemma's object)."""
    h = (b - a) / n
    vals = [abs(squint_fn(a + i * h)) for i in range(n + 1)]
    d = [vals[i + 1] - vals[i] for i in range(n)]
    return sum(1 for i in range(n - 1) if d[i] < 0.0 < d[i + 1])


def windows_with_dip_guard(
    squint_fn,
    effective_duration,
    t_start: float,
    window_end: float,
    *,
    n_scan: int = 200,
    n_step: int = 200,
    tol_g: float = 1e-9,
):
    """Enumerate windows under the single-dip lemma; step as degraded fallback.

    Returns ``(FeasibleWindows, diagnostics)`` where diagnostics carries
    ``n_squint_dips`` and ``n_dip_fallback`` (0/1) -- the fallback is never
    silent (ticket 04 acceptance: fallback trigger count observable).
    Stepped endpoints are grid-accurate (within one step), which the test
    suite bounds against analytically known sets.
    """
    a, b = float(t_start), float(window_end)
    if n_scan < 1:
        # Feeds _count_abs_squint_minima's (b - a) / n: zero divides, and a
        # negative value leaves the index walk with nothing to read.
        raise ValueError(f"n_scan must be >= 1: got {n_scan}")
    if n_step < 1:
        # Only the degraded (multi-dip) path uses n_step, but a guard that only
        # fires on the path you happen to take is not a guard.
        raise ValueError(f"n_step must be >= 1: got {n_step}")
    dips = _count_abs_squint_minima(squint_fn, a, b, n_scan)
    diagnostics = {"n_squint_dips": dips, "n_dip_fallback": 0}
    if dips <= 1:
        return (
            feasible_subintervals(effective_duration, a, b, n_scan=n_scan, tol_g=tol_g),
            diagnostics,
        )
    # degraded path: full-aperture stepping (D9 / steel-man A15)
    diagnostics["n_dip_fallback"] = 1
    g = lambda t: t + effective_duration(t) - window_end
    step = (b - a) / n_step
    grid = [a + i * step for i in range(n_step + 1)]
    intervals: list[tuple[float, float]] = []
    run_start = None
    for i, x in enumerate(grid):
        feasible = g(x) <= 0.0
        if feasible and run_start is None:
            run_start = x
        if not feasible and run_start is not None:
            intervals.append((run_start, grid[i - 1]))
            run_start = None
    if run_start is not None:
        intervals.append((run_start, b))
    return (
        FeasibleWindows(
            intervals=tuple(intervals),
            n_boundary_roots=sum(1 for lo, hi in intervals for _ in (0, 1) if a < lo < hi < b),
            n_degenerate_points=0,
        ),
        diagnostics,
    )


# ── atomic predicates (single predicate source, spec D9) ────────────────

def intersect_intervals(*interval_sets) -> tuple[tuple[float, float], ...]:
    """Intersect several unions of closed intervals (ticket 16, cascade 3/3).

    The window of a real-window task is the intersection of three
    independent leg-sets:

      1. incidence mask  -- from ``sss_core.realwindows`` geometry,
      2. mode squint envelope -- ``squint_at(t)`` against the per-mode
         envelope (ticket 15 ``mode_squint_envelope_rad``),
      3. the end-check set -- ``feasible_subintervals`` over the padded dwell.

    Each leg is computed by its OWN owner and this function only intersects;
    it never re-derives a leg's predicate.  That is the "no private
    reimplementation" rule applied structurally rather than by convention --
    a new leg is added by passing another interval set, not by editing here.

    Semantics: closed intervals, zero-length members preserved (a
    measure-zero feasible point is a legitimate degenerate window, D04-1/D04-4),
    and an EMPTY intersection returns an empty tuple -- the caller decides
    whether that means "removed" (generation cascade) or "unschedulable"
    (a CV violation, D10-3).  This function raises on neither.
    """
    live = [tuple(iv) for iv in interval_sets if iv is not None]
    if not live:
        return ()
    live.sort(key=lambda ivs: len(ivs))  # smallest first: cheapest to empty out
    current = live[0]
    for other in live[1:]:
        merged: list[tuple[float, float]] = []
        i = j = 0
        while i < len(current) and j < len(other):
            lo = max(current[i][0], other[j][0])
            hi = min(current[i][1], other[j][1])
            if lo <= hi:
                merged.append((lo, hi))
            if current[i][1] < other[j][1]:
                i += 1
            else:
                j += 1
        current = tuple(merged)
        if not current:
            return ()
    return current


def mask_intervals(span: tuple[float, float], mask_fn, n_scan: int = 200) -> tuple[tuple[float, float], ...]:
    """Sample a boolean mask over a span and return the maximal runs (leg 1/2).

    ``mask_fn(t) -> bool``.  Grid sampling followed by a run merge: the same
    discretisation the end-check path already uses (``feasible_subintervals``
    defaults to n_scan=200), so the legs agree on resolution and no leg is
    silently finer than another.

    The returned runs are INSET by one grid step at each end.  This is not
    cosmetic: a later leg evaluates the dwell closure at the interval
    endpoints, and a run that ends exactly on a mask boundary can land a
    step outside it -- measured, a run ending at the SLS envelope boundary
    overshot by 0.04 deg and the envelope guard raised.  Insetting guarantees
    each leg's consumers stay strictly inside the leg that produced them.
    """
    a, b = float(span[0]), float(span[1])
    if b < a:
        raise ValueError(f"mask span inverted: [{a}, {b}]")
    if n_scan < 0:
        # n_scan == 0 is the defined single-point mode just below; a negative
        # grid size makes the sample loop empty, so this returns no runs for a
        # mask that is true everywhere -- an empty answer that looks normal.
        raise ValueError(f"n_scan must be >= 0: got {n_scan}")
    step = (b - a) / n_scan if n_scan else 0.0
    # inset must absorb grid rounding as well as the step itself: a run
    # closing on the last in-mask sample lands a ULP past the boundary
    # (measured 5.000000000000001 against a <= 5.0 mask), which is enough to
    # make a later leg's own guard raise.
    inset = (1e-9 if step == 0.0 else step) + 8.0 * abs(a + b) * sys.float_info.epsilon
    runs: list[tuple[float, float]] = []
    start: float | None = None
    for i in range(n_scan + 1):
        t = a + i * step
        ok = bool(mask_fn(t))
        if ok and start is None:
            start = t
        elif not ok and start is not None:
            lo, hi = start + inset, t - inset
            if lo <= hi:
                runs.append((lo, hi))
            start = None
    if start is not None:
        lo, hi = start + inset, b - inset
        if lo <= hi:
            runs.append((lo, hi))
    return tuple(runs)


def feasible_at(t: float, effective_duration, window_end: float, tol_g: float = 1e-12) -> bool:
    """Atomic end-check: t + T_eff(t) <= w_e (shared by every consumer)."""
    return t + effective_duration(t) <= window_end + tol_g


def window_start_ok(t: float, t_start: float) -> bool:
    return t >= t_start


def window_end_ok(e: float, window_end: float) -> bool:
    """Imaging end e must respect the window end (counterexample: e=22.0 vs
    w_e=21.5 is a violation -- spec Testing Decisions / q2 evidence)."""
    return e <= window_end


def window_feasibility(
    t: float,
    duration,
    t_start: float,
    window_end: float,
    pads: MarginPads,
) -> bool:
    """Production feasibility of one schedule point (D04-2 pad policy)."""
    if not window_start_ok(t, t_start):
        return False
    effective = effective_duration_fn(duration, pads)
    return feasible_at(t, effective, window_end)


def footprint_ok(
    mode: Mode,
    l_az_m: float,
    lib: ModeLibrary,
    r0_m: float | None = None,
) -> bool:
    """C1b azimuth-footprint clause, mode-scoped (D04-3).

    SPT: hard bound L_az <= R0*theta_a -- the parked beam must contain the
    scene (formula-spec §4.2: R0*theta_a ~ 4.87 km vs 5 km scene, no
    margin).  ``r0_m`` is the task's own slant range; None falls back to
    the library R0, which is the synthetic-generator caliber only (real
    geometry carries per-task R0, residual R15).  STR/SLS:
    by-construction satisfied -- the scene azimuth extent is already
    inside their dwell closures (T_STR carries Wa/Vs, T_SLS carries Wa
    inside the swept angle), so strip-map-like coverage of extended scenes
    is a dwell question, not a footprint question.  Generic per-target
    L_az != Wa scenes belong to ticket 08.
    """
    if mode is Mode.SPT:
        r0 = lib.geo.R0_m if r0_m is None else r0_m
        return l_az_m <= r0 * lib.geo.theta_a_rad
    if mode in (Mode.STR, Mode.SLS):
        return True
    raise ValueError(f"unknown mode {mode!r}")


def scan_span_reachable(span_rad: float, squint_env_rad: float) -> bool:
    """C1b scan-span clause: required steering span <= 2 x |psi| envelope."""
    return span_rad <= 2.0 * abs(squint_env_rad) + 1e-12


def scan_rate_ok(rate_rad_s: float, max_rate_rad_s) -> bool:
    """C1b beam-scan-rate envelope clause.  The actuator limit is a ticket-07
    wire-in; passing None fails LOUD (no silent skip, ticket-02 discipline)."""
    if max_rate_rad_s is None:
        raise ValueError(
            "scan-rate envelope limit not wired yet (ticket 07 D5 calibration); "
            "refusing a silent skip"
        )
    return abs(rate_rad_s) <= max_rate_rad_s


def clip_to_squint_span(
    intervals, t_ca_s: float, r0_m: float, vs_mps: float, psi_max_rad: float,
    tol: float = 1e-12,
):
    """Ticket 48 geometric clause: keep only the sub-intervals whose squint
    magnitude stays within ``psi_max_rad``.

    The planar squint is ``psi(t) = atan(vs * (t - t_ca) / r0)`` (single
    source: ``geometry.squint_at``), so ``|psi| <= psi_max`` is exactly
    ``|t - t_ca| <= r0 * tan(psi_max) / vs``.  Tolerance is the same source
    floor as the mode-routing comparison (``aasr.route_mode``), not the
    encode round-trip belt.
    """
    span = r0_m * math.tan(psi_max_rad) / vs_mps
    lo_b, hi_b = t_ca_s - span, t_ca_s + span
    out = []
    for a, b in intervals:
        lo2 = a if a > lo_b else lo_b
        hi2 = b if b < hi_b else hi_b
        if hi2 > lo2 + tol:
            out.append((lo2, hi2))
    return tuple(out)


def resolution_clip(ivs, mode, rho_req_m: float, t_ca_s: float, r0_m, lib):
    """Ticket 48: clip a window's feasible set to where the ACHIEVED azimuth
    resolution ``rho_a(mode) / cos(psi)`` is within the ordered ``rho_req``.

    ``route_mode`` routes on the ZERO-SQUINT library value; this enforces the
    same order at the actual imaging squint.  A requirement finer than the
    mode's zero-squint value is unsatisfiable at every start, so the result
    is the empty set.  ``r0_m=None`` falls back to the library R0 (the
    synthetic-family caliber, identical to the dwell chain's own fallback).
    """
    ratio = lib.rho_az(mode) / rho_req_m
    if ratio > 1.0:
        return ()
    psi_max = min(math.acos(min(1.0, ratio)), mode_squint_envelope_rad(mode))
    r0 = lib.geo.R0_m if r0_m is None else float(r0_m)
    return clip_to_squint_span(ivs, t_ca_s, r0, lib.geo.vs_mps, psi_max)
