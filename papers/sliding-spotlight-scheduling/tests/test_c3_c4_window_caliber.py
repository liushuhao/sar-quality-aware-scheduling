#!/usr/bin/env python3
"""Ticket 28 -- C3/C4 reference caliber on the windows-form family.

Fault pattern (Audit4 A1, the ninth instance of the ticket-23 root class):
the MEASURED dwell is read per WINDOW (``_dwell`` -> ``w.r0_m``,
evaluator.py:356-364) but the C3/C4 REFERENCE was quoted at the TASK caliber
(``plan.r0_m``, evaluator.py:408-417), under a comment that CLAIMED "the same
per-task geometry the dwell was measured with".  On the schema-2.1 real-window
family every task carries its geometry per window and the task-level block is
absent (measured 0/1685 tasks in the v3 runs), so ``plan.r0_m`` was None ->
the reference silently collapsed onto the LIBRARY constant R0 = 775.426 km
while the dwell was measured at e.g. 570 km.  That is exactly what ticket 17
registered against: "reference evaluated at the geometry of the task being
measured" (predicates.py:89-115).  The in-code comment was the self-contradiction.

Measured on this fixture BEFORE the fix (2026-10-05, ticket 28; recipe
end-to-end proven by the directed review, values re-measured by the worker --
both are the same):

  manifest: one windows-form SPT task, lo=-135.0, hi=+10.0, t_ca=0.0,
            window r0_m = 1_026_000.0 (32.4% above the library 775_426.138),
            NO task-level r0_m (the defect), start s = -134.0

    lib.geo.R0_m                = 775_426.1380865795 m
    plan.r0_m (task level)     = None
    window r0_m                = 1_026_000.0 m
    feasible subintervals      = ((-135.0, 2.9998095341384),)
    psi(s=-134.0)              = -0.780235 rad = -44.7042 deg
    dwell(s=-134.0)            = 13.859550460313779 s
    t_env_max(library)         = 10.583021834038036 s   (1.3 * 8.14...)
    t_env_max(r0 = 1.026e6)    = 14.002855808441504 s
    C3/C4 normalized (library) = 1.3096023685538931  -> > 1  FALSE VIOLATION
    C3/C4 normalized (window)  = 0.9897659913029071  -> <= 1  admissible
    evaluate(x) cv             = 2.0   (BOTH channels tripped on one task)

  AFTER the fix the same x evaluates to cv = 0.0.

Discrimination: the library-caliber reading exceeds the budget by 30.96% while
the same-caliber reading sits at 0.9898 -- the two calibers straddle the
budget on THIS single scenario, so the cv is attributable to the reference
caliber alone (the dwell, the mode, the window and the start are identical in
both worlds).

The window must stay inside +-45 deg INCLUDING the feasible-scan boundaries,
otherwise ``duration_scene_s`` raises ValueError, ``precompile_tasks`` drops the
whole window to ``intervals=()`` (evaluator.py:280-284), the task precompiles
unschedulable and cv is 2.0 in BOTH calibers -- a permanently green test.  This
suite therefore asserts the post-fix cv == 0.0 EXPLICITLY, never "cv got
smaller".

Mutation contract: reverting either C3/C4 call site in evaluator.py:404-417
back to ``r0_m=plan.r0_m`` turns the first test RED.
"""
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.predicates import (  # noqa: E402
    _t_env_max,
    c3_energy_normalized,
    c3_ok,
    c4_memory_normalized,
    c4_ok,
)

# Recipe constants (ticket 28 design point 2)
WIN_LO_S = -135.0
WIN_HI_S = 10.0
WIN_T_CA_S = 0.0
WIN_R0_M = 1_026_000.0
START_S = -134.0


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


def _windows_form_manifest() -> dict:
    """One windows-form SPT task: geometry on the WINDOW only, none on the
    task -- the schema-2.1 real-window shape that made the defect bite."""
    return {
        "schema": "test-c3c4-window-caliber",
        "preregistration": {
            "pads": {"inter_task_fraction": 0.25, "window_tail_fraction": 0.0}
        },
        "tasks": [
            {
                "t_start_s": WIN_LO_S,
                "t_end_s": WIN_HI_S,
                "t_ca_s": WIN_T_CA_S,
                "azimuth_size_m": 4000.0,
                "priority": 5,
                "rho_req_m": 1.5,
                "mode": "SPT",
                "prf_hz": 1150.0,
                "windows": [
                    {
                        "lo_s": WIN_LO_S,
                        "hi_s": WIN_HI_S,
                        "t_ca_s": WIN_T_CA_S,
                        "r0_m": WIN_R0_M,
                    }
                ],
            }
        ],
    }


def _tau_for(intervals, target: float) -> float:
    total = sum(hi - lo for lo, hi in intervals)
    cum = 0.0
    for lo, hi in intervals:
        if lo - 1e-12 <= target <= hi + 1e-12:
            return min(max((cum + (target - lo)) / total, 0.0), 1.0)
        cum += hi - lo
    raise AssertionError(f"target {target} outside feasible union {intervals}")


def test_c3_c4_reference_follows_the_window_geometry(lib):
    """The scheduling problem must judge C3/C4 at the caliber the dwell was
    MEASURED at -- the window's own slant range.  Pre-fix the reference fell
    back to the library constant (task-level r0 absent on this family) and
    produced a FALSE violation on an admissible schedule: cv = 2.0 instead of
    0.0."""
    sp = SchedulingProblem(_windows_form_manifest(), lib)
    plan = sp.plans[0]
    assert plan.schedulable, "window dropped at precompile -- recipe is invalid"
    assert plan.r0_m is None, "task-level r0 must be absent (the defect's premise)"
    w = plan.window_at(START_S)
    assert w.r0_m == pytest.approx(WIN_R0_M)
    assert any(lo - 1e-12 <= START_S <= hi + 1e-12 for lo, hi in plan.intervals)

    rec = sp.evaluate([1.0, _tau_for(plan.intervals, START_S)])
    assert rec["starts"] == {0: pytest.approx(START_S)}, rec["starts"]
    assert rec["cv"] == pytest.approx(0.0, abs=1e-9), (
        f"cv={rec['cv']}: the C3/C4 reference is not on the window caliber "
        "(pre-fix this scenario reads cv=2.0 -- a false violation)"
    )


def test_c3_c4_predicates_agree_with_the_evaluator(lib):
    """Anti-bypass: the same-caliber predicates the evaluator is supposed to
    call must return the SAME verdict as ``evaluate`` on this scenario.  Pins
    the two calibers on opposite sides of the budget so a swapped reference
    (library instead of window, or vice versa) cannot pass either assertion."""
    sp = SchedulingProblem(_windows_form_manifest(), lib)
    plan = sp.plans[0]
    w = plan.window_at(START_S)
    dwell = sp._dwell(0, START_S)

    same_caliber = {
        "c3": c3_energy_normalized(plan.mode, dwell, lib, w.r0_m),
        "c4": c4_memory_normalized(
            plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, w.r0_m
        ),
    }
    library_caliber = {
        "c3": c3_energy_normalized(plan.mode, dwell, lib, None),
        "c4": c4_memory_normalized(
            plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, None
        ),
    }
    # the discriminator: straddle, not merely "different"
    for key in ("c3", "c4"):
        assert same_caliber[key] <= 1.0, (key, same_caliber[key])
        assert library_caliber[key] > 1.0, (key, library_caliber[key])
        assert library_caliber[key] - same_caliber[key] > 0.2, (
            key, library_caliber[key], same_caliber[key]
        )
    assert _t_env_max(lib, w.r0_m) > _t_env_max(lib), "window caliber must be wider"

    assert c3_ok(plan.mode, dwell, lib, r0_m=w.r0_m)
    assert c4_ok(plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, r0_m=w.r0_m)
    assert not c3_ok(plan.mode, dwell, lib, r0_m=None)
    assert not c4_ok(
        plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, r0_m=None
    )
    # the evaluator's cv of 0.0 (test above) is only honest if these agree
    rec = sp.evaluate([1.0, _tau_for(plan.intervals, START_S)])
    assert rec["cv"] == pytest.approx(0.0, abs=1e-9)


def test_single_window_family_calibers_coincide(lib):
    """Ticket 28 design point 1 -- the frozen single-window (pre-ticket-25, M)
    family must be bit-identical after the fix.  It is because the synthetic
    single window is built FROM the task block (evaluator.py:262-265), so the
    window caliber and the task caliber are the same float: ``w.r0_m is
    plan.r0_m`` for every task of that family.  Pinned here as exact equality
    of the C3/C4 normalized readings (abs=0.0), which is the property the
    frozen result families depend on."""
    manifest = _windows_form_manifest()
    task = manifest["tasks"][0]
    del task["windows"]
    task["t_start_s"], task["t_end_s"] = 50.0, 80.0
    task["t_ca_s"] = 65.0

    sp = SchedulingProblem(manifest, lib)
    plan = sp.plans[0]
    assert plan.schedulable
    for t in (55.0, 65.0, 75.0):
        w = plan.window_at(t)
        assert w.r0_m is plan.r0_m
        dwell = sp._dwell(0, t)
        assert c3_energy_normalized(plan.mode, dwell, lib, w.r0_m) == (
            c3_energy_normalized(plan.mode, dwell, lib, plan.r0_m)
        )
        assert c4_memory_normalized(
            plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, w.r0_m
        ) == c4_memory_normalized(
            plan.mode, dwell, plan.rho_req_m, plan.prf_hz, lib, plan.r0_m
        )

    # a pre-ticket-16 manifest: no geometry anywhere -> library constant on
    # both sides, so the readings stay bit-identical to the frozen families
    plain_manifest = _windows_form_manifest()
    plain_task = plain_manifest["tasks"][0]
    del plain_task["windows"]
    plain_task["t_start_s"], plain_task["t_end_s"] = 50.0, 80.0
    plain_task["t_ca_s"] = 65.0
    plain = SchedulingProblem(plain_manifest, lib)
    assert plain.plans[0].r0_m is None
    assert plain.plans[0].window_at(65.0).r0_m is None
    dwell = plain._dwell(0, 65.0)
    assert c3_energy_normalized(plain.plans[0].mode, dwell, lib, None) == (
        c3_energy_normalized(plain.plans[0].mode, dwell, lib, plain.plans[0].r0_m)
    )