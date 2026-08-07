"""Guard tests for AgileTask.interval_window_state — the full-interval
window containment that replaces the old start-time-only check.

Fault mode (2026-08-07): MOEA/GA window penalties checked only whether the
observation START t_act fell inside a window, not the full 30 s interval.
A zero-length or <30 s window could host an observation whose body extended
outside the window — a real C1/OOW violation invisible to both the solver and
the start-time-only audit. Baselines already enforced this correctly; the
evolutionary solvers did not.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from sar_sim.solver.types import AgileTask  # noqa: E402


def _task(windows, duration=30.0):
    """Build a minimal AgileTask with given window_times (epoch-second pairs)."""
    return AgileTask(
        task_id=0, target_id="T0", priority=1.0, windows=[],
        phi_min=0.0, phi_max=1.0,
        t_earliest=min(w for ws in windows for w in (ws[0],)),
        t_latest=max(w for ws in windows for w in (ws[1],)),
        duration=duration, energy=0.0, memory=0.0,
        time_span=0.0, window_times=[tuple(w) for w in windows],
    )


def test_full_interval_inside_window_passes():
    t = _task([(100.0, 200.0)])
    ok, gap = t.interval_window_state(120.0)  # [120,150] ⊂ [100,200]
    assert ok and gap == 0.0


def test_start_inside_but_end_past_window_fails():
    """The exact regression: t_act=180 starts inside [100,200] but [180,210]
    extends 10 s past the window end. Start-only check would accept it."""
    t = _task([(100.0, 200.0)])
    ok, gap = t.interval_window_state(180.0)
    assert not ok
    assert gap == pytest.approx(10.0)  # shift start earlier by 10 s


def test_zero_length_window_never_hosts_observation():
    """A single-sample visibility window (w_start==w_end) cannot host any
    30 s observation — must be infeasible for every t."""
    t = _task([(500.0, 500.0), (560.0, 570.0)])  # zero + 10 s window
    for tt in (499.0, 500.0, 500.001, 559.0, 560.0, 565.0):
        ok, _ = t.interval_window_state(tt)
        assert not ok, f"t={tt} should not fit in zero/short windows"


def test_boundary_t_start_at_window_start_passes():
    """t_act == w_start with full duration inside is the earliest feasible slot."""
    t = _task([(100.0, 200.0)])
    ok, gap = t.interval_window_state(100.0)  # [100,130] ⊂ [100,200]
    assert ok and gap == 0.0


def test_boundary_end_touches_window_end_passes():
    t = _task([(100.0, 200.0)])
    ok, gap = t.interval_window_state(170.0)  # [170,200] exactly to w_end
    assert ok and gap == 0.0


def test_picks_window_that_fits_among_several():
    t = _task([(100.0, 110.0), (200.0, 300.0)])  # first too short, second fine
    ok, gap = t.interval_window_state(220.0)
    assert ok and gap == 0.0


def test_start_before_window_gives_positive_shift():
    t = _task([(100.0, 200.0)])
    ok, gap = t.interval_window_state(80.0)  # need to shift +20
    assert not ok and gap == pytest.approx(20.0)


def test_no_usable_window_returns_finite_penalty():
    """Only a zero-length window: physically unschedulable. Must return a
    finite (non-inf, non-NaN) penalty so the objective stays defined."""
    t = _task([(500.0, 500.0)])
    ok, gap = t.interval_window_state(500.0)
    assert not ok
    assert gap > 0 and gap != float("inf")
    assert gap == gap  # not NaN
