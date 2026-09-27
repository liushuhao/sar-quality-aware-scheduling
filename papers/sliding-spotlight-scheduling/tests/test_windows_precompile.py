#!/usr/bin/env python3
"""Ticket 04 -- window-domain precompilation tests.

Fixture discipline (D04-1..6, registered in the ticket):
* expected feasible sets are CLOSED (g<=0 convention); the prototype's
  literal (0,9)U(19,40) re-derives analytically to [0,9]U[19,40];
* non-convex fixtures are SYNTHETIC stress constructions -- physical
  squint rates keep g strictly increasing (single interval), so no
  physical non-convexity claim may be built on them;
* the enumerator consumes already-padded effective durations; fixtures
  inject bare durations (pad = 0) to keep exact-set expectations honest.

Mutation evidence (inverse-assertion, recorded in ticket 04): the NAIVE
single-bisection oracle implemented in this test file MISSES three of the
four roots of the tangent-sliver fixture while the enumerator recovers the
exact set -- see test_naive_bisection_misses_sliver (red by construction).
"""
import math
import random
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import MarginPads, duration_scene_s, pad_window_tail  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.windows import (  # noqa: E402
    FeasibleWindows,
    feasible_at,
    feasible_subintervals,
    footprint_ok,
    scan_rate_ok,
    scan_span_reachable,
    window_end_ok,
    window_feasibility,
    window_start_ok,
    windows_with_dip_guard,
)


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


# ── fixtures (synthetic stress constructions, D04-1/4/5) ─────────────────

def _u_quartic_duration():
    """U-union fixture: g(t) = 1e-5 t(t-9)(t-19)(t-40), T := g + 40 - t.

    Analytic sign analysis (c > 0, leading +): g < 0 on (0,9) and (19,40),
    g > 0 on (9,19), g = 0 exactly at t in {0, 9, 19, 40}.  Expected CLOSED
    feasible set [0,9] U [19,40].  T >= 0 on [0,40] (T(40) = 0 exactly),
    T > 0 on [0,40).  provenance: expectation re-derived from the
    construction; the (0,9)U(19,40) figure originates from the ideaspark
    prototype 32-grid observation (non-physical ground truth).
    """
    c = 1e-5

    def g(t):
        return c * t * (t - 9.0) * (t - 19.0) * (t - 40.0)

    return lambda t: g(t) + 40.0 - t, g


def _tangent_sliver_duration(delta=1e-4):
    """Tangency fixture: g = min((t-10)^2 - delta^2, (t-25)(t-35)).

    Analytic roots {10-delta, 10+delta, 25, 35}; expected feasible set
    [10-delta, 10+delta] U [25, 35].  The 2e-4 sliver is far below any
    naive single-bisection resolution; g_min = -1e-8 sits below tol_g.
    """

    def g(t):
        return min((t - 10.0) ** 2 - delta * delta, (t - 25.0) * (t - 35.0))

    return lambda t: g(t) + 40.0 - t, g


def _double_dip_step_fixture():
    """Fallback fixture: multi-dip squint + piecewise T with analytic set.

    T(t) = 8 for t<=12, 26 for 12<t<20, 8 for t>=20  =>
    g = t + T - 40 <= 0  on  [0,14] U [20,32]  (analytic, closed: the
    t>=20 stretch satisfies t <= 32, not 40).  squint |psi| =
    |0.1 sin(pi t/10)| has interior minima at t=10/20/30 (multi-dip) ->
    the dip guard MUST fall back to stepping.
    """

    def duration(t):
        if t <= 12.0:
            return 8.0
        if t < 20.0:
            return 26.0
        return 8.0

    squint = lambda t: 0.1 * math.sin(math.pi * t / 10.0)
    return duration, squint


# ── U-union fixture: exact set equality (headline acceptance) ────────────

def test_u_shape_union_exact_set_equality():
    """Exact CLOSED set equality [0,9] U [19,40] + non-empty (D04-1)."""
    duration, _ = _u_quartic_duration()
    fw = feasible_subintervals(duration, 0.0, 40.0)
    assert bool(fw)
    assert len(fw.intervals) == 2, fw.intervals
    (lo1, hi1), (lo2, hi2) = fw.intervals
    assert lo1 == pytest.approx(0.0, abs=1e-9)
    assert hi1 == pytest.approx(9.0, abs=1e-9)
    assert lo2 == pytest.approx(19.0, abs=1e-9)
    assert hi2 == pytest.approx(40.0, abs=1e-9)
    assert fw.n_boundary_roots == 4
    # the 9 physically-infeasible prototype start points stay OUT
    for t in (9.5, 10.0, 12.0, 15.0, 18.0, 18.9):
        assert not fw.contains(t)


def test_u_shape_fixture_duration_positivity():
    """T >= 0 on [0,40] with T(40) = 0 exactly, T > 0 on [0,40) (D04-5)."""
    duration, _ = _u_quartic_duration()
    grid = [i * 0.05 for i in range(801)]
    assert all(duration(t) >= 0.0 for t in grid)
    assert all(duration(t) > 0.0 for t in grid if t < 40.0)
    assert duration(40.0) == 0.0


# ── tangency fixture: sliver recovery + naive-bisection red evidence ─────

def test_tangent_double_root_sliver_recovered():
    """Exact recovery of the 2e-4 sliver + [25,35] (analytic roots).

    Runs on BOTH the default grid (a scan point lands at t=10 by fp
    alignment, pass 1 catches it) and a deliberately MISALIGNED grid
    (n_scan=198: grid neighbours of 10 sit at ~9.90/10.10 with g>0), where
    only the stationary-refinement pass can recover the sliver.
    """
    delta = 1e-4
    duration, _ = _tangent_sliver_duration(delta)
    for n_scan in (200, 198):
        fw = feasible_subintervals(duration, 0.0, 40.0, n_scan=n_scan)
        assert len(fw.intervals) == 2, (n_scan, fw.intervals)
        (lo1, hi1), (lo2, hi2) = fw.intervals
        assert lo1 == pytest.approx(10.0 - delta, abs=1e-7)
        assert hi1 == pytest.approx(10.0 + delta, abs=1e-7)
        assert lo2 == pytest.approx(25.0, abs=1e-9)
        assert hi2 == pytest.approx(35.0, abs=1e-9)


def test_naive_bisection_misses_sliver():
    """Red evidence: a naive single-bisection implementation cannot recover
    the tangent-sliver root set (misses >= 3 of 4 roots)."""
    delta = 1e-4
    duration, g = _tangent_sliver_duration(delta)

    def naive_single_bisection(a, b, n_grid=32):
        step = (b - a) / n_grid
        prev, prev_t = g(a), a
        for i in range(1, n_grid + 1):
            t = a + i * step
            cur = g(t)
            if prev == 0.0:
                return prev_t
            if prev * cur < 0.0:
                lo, hi = prev_t, t
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    if g(lo) * g(mid) <= 0.0:
                        hi = mid
                    else:
                        lo = mid
                return 0.5 * (lo + hi)
            prev, prev_t = cur, t
        return None

    got = naive_single_bisection(0.0, 40.0)
    expected = {10.0 - delta, 10.0 + delta, 25.0, 35.0}
    # decisive: the naive root set (a single point) recovers at most ONE of
    # the four true roots -- the other three are silently lost
    assert got is not None
    assert sum(1 for e in expected if abs(got - e) < 1e-6) <= 1
    assert len(expected) == 4


# ── dip guard + degraded stepping path ───────────────────────────────────

def test_single_dip_guard_physical_window(lib):
    """Physical squint (single |psi| dip) -> root-based path, no fallback."""
    geo = lib.geo

    def squint(t):
        return math.atan(geo.vs_mps * (t - 20.0) / geo.R0_m)

    duration = lambda t: duration_scene_s(Mode.SLS, abs(squint(t)), lib)
    fw, diag = windows_with_dip_guard(squint, duration, 0.0, 40.0)
    assert diag["n_squint_dips"] <= 1
    assert diag["n_dip_fallback"] == 0
    assert bool(fw)
    assert len(fw.intervals) == 1  # physical g strictly increasing


def test_multi_dip_degenerates_to_stepping_with_analytic_set():
    """Synthetic multi-dip squint: assertion triggers (count >= 1) and the
    stepped result equals the analytic set [0,14] U [20,32] within a step."""
    duration, squint = _double_dip_step_fixture()
    fw, diag = windows_with_dip_guard(squint, duration, 0.0, 40.0, n_step=200)
    assert diag["n_squint_dips"] >= 2
    assert diag["n_dip_fallback"] == 1  # observable fallback counter
    step = 40.0 / 200
    assert len(fw.intervals) == 2, fw.intervals
    (lo1, hi1), (lo2, hi2) = fw.intervals
    assert abs(lo1 - 0.0) <= step
    assert abs(hi1 - 14.0) <= step
    assert abs(lo2 - 20.0) <= step
    assert abs(hi2 - 32.0) <= step
    # grid labels must agree with the analytic predicate pointwise
    analytic = lambda t: t + duration(t) - 40.0 <= 0.0
    n = 400
    for i in range(n + 1):
        t = 40.0 * i / n
        assert fw.contains(t) == analytic(t) or abs(
            (t + duration(t)) - 40.0
        ) <= 40.0 / n, t


# ── property test: 4 families, analytic/oracle cross-verification ────────

def _oracle_intervals(g, a, b, n=4000):
    """Independent dense-sampling oracle (coarse guard, test-local)."""
    step = (b - a) / n
    ts = [a + i * step for i in range(n + 1)]
    mask = [g(t) <= 0.0 for t in ts]
    out = []
    start = None
    for i, m in enumerate(mask):
        if m and start is None:
            start = ts[i]
        if not m and start is not None:
            out.append((start, ts[i - 1]))
            start = None
    if start is not None:
        out.append((start, b))
    return out


def _expected_intervals(g, a, b, roots):
    """Assemble expected intervals from ANALYTIC roots + feasible domain
    bounds (independent of the implementation's assembly internals)."""
    cands = sorted(set(roots) | {a, b})
    ivs = []
    for lo, hi in zip(cands, cands[1:]):
        if hi > lo and g((lo + hi) / 2.0) <= 0.0:
            ivs.append((lo, hi))
    return ivs


def test_root_set_property_test_four_families():
    """>=100 random windows; 0/1/2-root classes each >=20, each class reached
    by CONSTRUCTION (parameters are drawn conditioned on the target root
    count, so the class prior is exact, not statistical); analytic exact
    sets for linear/quadratic/quartic families + dense-oracle agreement for
    all; seed pinned (spec 确定性)."""
    rng = random.Random(20260927)

    plan = [0] * 30 + [1] * 30 + [2] * 30 + [4] * 20  # 110 windows
    rng.shuffle(plan)

    results = []  # (family, fw, expected_roots, g, a, b)
    got_class = {0: 0, 1: 0, 2: 0}
    n_nonempty = 0

    for target in plan:
        a = rng.uniform(0.0, 10.0)
        span = rng.uniform(20.0, 40.0)
        b = a + span
        if target == 0:
            # linear T with g(b) < 0: fully feasible, ZERO boundary roots
            T0 = rng.uniform(2.0, 10.0)
            m = -(T0 / span) - rng.uniform(0.02, 0.30)
            duration = lambda t, T0=T0, m=m, a=a: T0 + m * (t - a)
            g = lambda t, T0=T0, m=m, a=a, b=b: t + T0 + m * (t - a) - b
            r = (b - T0 + m * a) / (1.0 + m)
            expected = [] if r > b + 1e-9 else [r]
        elif target == 1:
            # linear T with crossing strictly inside (a, b)
            T0 = rng.uniform(2.0, 10.0)
            m = -(T0 / span) + rng.uniform(0.05, 0.40)
            assert -1.0 < m < 1.0
            duration = lambda t, T0=T0, m=m, a=a: T0 + m * (t - a)
            g = lambda t, T0=T0, m=m, a=a, b=b: t + T0 + m * (t - a) - b
            r = (b - T0 + m * a) / (1.0 + m)
            expected = [r] if a - 1e-9 <= r <= b + 1e-9 else []
        elif target == 2:
            # convex U with BOTH crossings forced inside by construction:
            # g(a) = (T0-span)(1-u) > 0 since u > 1; vertex value < 0
            T0 = rng.uniform(2.0, 8.0)
            tm = a + span * rng.uniform(0.45, 0.60)
            u = rng.uniform(1.3, 5.0)
            c = (span - T0) / ((tm - a) ** 2) * u
            duration = lambda t, T0=T0, c=c, tm=tm: T0 + c * (t - tm) ** 2
            A_, B_ = c, 1.0 - 2.0 * c * tm
            C_ = c * tm * tm + T0 - b
            disc = B_ * B_ - 4.0 * A_ * C_
            assert disc > 1e-6, "construction must keep clear of tangency"
            sq = math.sqrt(disc)
            expected = sorted(
                r for r in ((-B_ - sq) / (2 * A_), (-B_ + sq) / (2 * A_))
                if a - 1e-9 <= r <= b + 1e-9
            )
            assert len(expected) == 2, (a, span, tm, c, expected)
            g = lambda t, d=duration, b=b: t + d(t) - b
        else:  # random quartic: 4 analytic roots, exact-set equality
            r1, r2, r3, r4 = sorted(rng.uniform(a + 1.0, a + span - 1.0) for _ in range(4))
            if min(r2 - r1, r4 - r3) < 1.0:
                continue
            c = rng.uniform(5e-5, 2e-4)
            g = lambda t, c=c, rs=(r1, r2, r3, r4): c * math.prod(t - r for r in rs)
            b = max(t - g(t) for t in [a + i * span / 500.0 for i in range(501)]) + 1.0
            duration = lambda t, g=g, b=b: g(t) + b - t
            expected = [r1, r2, r3, r4]

        got_class[len(expected)] = got_class.get(len(expected), 0) + 1
        fw = feasible_subintervals(duration, a, b)
        results.append((target, fw, expected, g, a, b))
        if bool(fw):
            n_nonempty += 1

    assert len(results) >= 100
    for cls in (0, 1, 2):
        assert got_class[cls] >= 20, (cls, got_class)
    assert n_nonempty >= 20  # non-empty count recorded (no all-empty fake green)

    tol_grid = 40.0 / 4000 * 2.0
    for target, fw, expected, gfun, a, b in results:
        # analytic exact-set equality (all constructed families here):
        # root count AND the assembled interval set, including feasible
        # domain bounds
        assert fw.n_boundary_roots == len(expected), (target, fw, expected)
        want_ivs = _expected_intervals(gfun, a, b, expected)
        assert len(fw.intervals) == len(want_ivs), (target, fw, want_ivs)
        for (flo, fhi), (wlo, whi) in zip(fw.intervals, want_ivs):
            assert flo == pytest.approx(wlo, abs=1e-6), (target, flo, wlo)
            assert fhi == pytest.approx(whi, abs=1e-6), (target, fhi, whi)
        # dense-oracle agreement (independent implementation, coarse guard)
        orc = _oracle_intervals(gfun, a, b)
        wide = [iv for iv in fw.intervals if iv[1] > iv[0]]
        assert len(orc) == len(wide), (target, fw, orc)
        for (olo, ohi), (flo, fhi) in zip(orc, wide):
            assert olo == pytest.approx(flo, abs=tol_grid)
            assert ohi == pytest.approx(fhi, abs=tol_grid)


# ── e <= w_e counterexample + pad policy (D04-2) + predicates ────────────

def test_window_end_counterexample():
    """e=22.0 > w_e=21.5 must be a violation; boundary equality is legal."""
    assert window_end_ok(21.5, 21.5)
    assert window_end_ok(21.4, 21.5)
    assert not window_end_ok(22.0, 21.5)


def test_pad_policy_consumer_side(lib):
    """D04-2: enumerator takes pre-padded durations; the SAME atomic
    feasible_at backs both the enumeration and the production check."""
    const10 = lambda t: 10.0
    a, w_e = 0.0, 40.5
    # bare (degenerate anchor pads): t=30.5 is feasible (ends exactly at w_e)
    assert window_feasibility(30.5, const10, a, w_e, MarginPads.degenerate_anchor())
    # standard pads: 30.5 + 10*1.01 = 40.6 > 40.5 -> infeasible
    assert not window_feasibility(30.5, const10, a, w_e, MarginPads.standard())
    # enumerator agrees with the predicate on the padded callable
    padded = lambda t: pad_window_tail(const10(t), MarginPads.standard())
    fw = feasible_subintervals(padded, a, w_e)
    assert fw.contains(30.0) and not fw.contains(30.5)


def test_footprint_predicate_mode_scoped(lib):
    """D04-3: hard R0*theta_a bound is SPT-only; STR/SLS by-construction."""
    assert footprint_ok(Mode.SPT, 4800.0, lib)
    assert not footprint_ok(Mode.SPT, 5000.0, lib)  # scene 5 km > 4.87 km
    assert footprint_ok(Mode.STR, 5000.0, lib)
    assert footprint_ok(Mode.SLS, 5000.0, lib)


def test_scan_span_and_rate_predicates():
    assert scan_span_reachable(math.radians(2.9603), math.radians(12.0))
    assert not scan_span_reachable(math.radians(50.0), math.radians(12.0))
    assert scan_rate_ok(0.01, 0.05)
    assert not scan_rate_ok(0.10, 0.05)
    with pytest.raises(ValueError, match="ticket 07"):
        scan_rate_ok(0.01, None)


def test_window_start_predicate():
    assert window_start_ok(5.0, 5.0)
    assert not window_start_ok(4.999, 5.0)
    assert feasible_at(10.0, lambda t: 5.0, 15.0)
    assert not feasible_at(10.0, lambda t: 5.1, 15.0)


def test_empty_window_and_degenerate_point():
    """Fully-infeasible window -> empty (falsy), not an error; exact
    tangency -> degenerate point interval, counted (D04-4)."""
    fw = feasible_subintervals(lambda t: 50.0, 0.0, 40.0)
    assert not bool(fw)
    assert fw.intervals == ()
    # exact tangency: g = (t-10)^2 touches zero from above
    fw2 = feasible_subintervals(lambda t: (t - 10.0) ** 2 + 40.0 - t, 0.0, 40.0)
    assert fw2.n_degenerate_points >= 1
    for lo, hi in fw2.intervals:
        assert lo == pytest.approx(hi, abs=1e-6)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
