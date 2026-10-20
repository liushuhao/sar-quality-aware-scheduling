#!/usr/bin/env python3
"""Guard tests for the fixed-dwell ablation switch (panel R1 comparison arm).

The ``freeze_durations`` flag holds the dwell at its zero-squint value at
every consumption point (precompile + C2 + evaluate).  Guards:
  * the flag actually bites: frozen precompile widens the feasible measure
    and frozen dwell differs from the endogenous (squint-dependent) dwell
  * frozen dwell equals the zero-squint closure and is never larger
  * the default path keeps the squint-dependent dwell (flag is opt-in)
"""
import sys
from pathlib import Path

import pytest

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

from sss_core.duration import duration_scene_s  # noqa: E402
from sss_core.evaluator import SchedulingProblem, precompile_tasks  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.nsga2 import load_manifest  # noqa: E402

MANIFEST = FORK / "experiments" / "v3_results" / "scenarios" / "R2F_seed200.json"


@pytest.fixture(scope="module")
def lib():
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def man():
    return load_manifest(MANIFEST)


def _measure(plans):
    return sum(hi - lo for p in plans for lo, hi in (p.intervals or []))


def test_frozen_widens_feasible_measure(lib, man):
    endo = precompile_tasks(man, lib, freeze_durations=False)
    froz = precompile_tasks(man, lib, freeze_durations=True)
    assert _measure(froz) > _measure(endo)


def test_frozen_dwell_is_zero_squint_closure(lib, man):
    endo = SchedulingProblem(man, lib, freeze_durations=False)
    froz = SchedulingProblem(man, lib, freeze_durations=True)
    checked = 0
    for i, p in enumerate(endo.plans):
        if not p.schedulable or not p.intervals:
            continue
        lo, hi = p.intervals[0]
        t = lo + 0.5 * (hi - lo)
        w = p.window_at(t)
        # ticket 49: the frozen arm is the task-level dwell at psi=0 (the
        # library caliber only when the task carries no order/scene size).
        expected = duration_scene_s(
            p.mode, 0.0, lib, r0_m=w.r0_m,
            rho_req_m=(p.rho_req_m if p.mode is not Mode.STR else None),
            l_az_m=p.azimuth_size_m,
        )
        got = froz._dwell(i, t)
        assert abs(got - expected) < 1e-9, (i, got, expected)
        # the endogenous arm never uses a shorter dwell than the frozen one
        assert froz._dwell(i, t) <= endo._dwell(i, t) + 1e-9, i
        checked += 1
    assert checked > 0


def test_default_keeps_squint_dependent_dwell(lib, man):
    endo = SchedulingProblem(man, lib)  # default: freeze_durations=False
    n_diff = 0
    for i, p in enumerate(endo.plans):
        if not p.schedulable or not p.intervals:
            continue
        lo, hi = p.intervals[0]
        t = lo + 0.5 * (hi - lo)
        w = p.window_at(t)
        zero = duration_scene_s(
            p.mode, 0.0, lib, r0_m=w.r0_m,
            rho_req_m=(p.rho_req_m if p.mode is not Mode.STR else None),
            l_az_m=p.azimuth_size_m,
        )
        if abs(endo._dwell(i, t) - zero) > 1e-9:
            n_diff += 1
    assert n_diff > 0, "default arm should use a squint-dependent dwell"
