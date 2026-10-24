#!/usr/bin/env python3
"""Ticket 61 -- generator-side task-law duration caliber (R61).

Pins the adjudicated caliber-parameter design (2026-10-24, scoped review
in ``.scratch/sliding-spotlight-scheduling/t61-exec/review.md``): the two
dwell sites in ``sss_core/scenarios.py`` -- the anchor window-dwell
dispersion (~:236) and the real-window end-check lambda (~:605) --
consume the task's OWN order only under the explicit
``duration_caliber="task-law"``.  The default ``"library"`` is the
pre-ticket-61 call bit-for-bit, so the frozen v3/v5 worlds keep their
byte-regeneration guarantee (the ticket-35 dead-branch guard, untouched
here, is the byte-level pin of that default).

Evaluator contract mirrored (evaluator.py:263/:291-301/:423-429):
manifest-rounded order in (``round(rho_req,9)`` / ``round(l_az_m,6)``),
STR never receives rho (``duration_scene_s`` raises on STR+rho,
duration.py:333-339 -- the ticket-48 clip carries the order there),
``l_az_m`` is passed unconditionally.
"""
import math
import sys
from datetime import datetime
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import duration_scene_s  # noqa: E402
from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.realwindows import KeplerianElement  # noqa: E402
from sss_core.scenarios import (  # noqa: E402
    generate_real_scenario,
    generate_scenario,
)

# Anchor + fine tier: the fine band [0.3, 0.6] spans the SPT/SLS routing
# boundary (test_scenarios.py:51-62), so one scenario yields BOTH an SLS
# and an SPT task; the "NC" suffix makes it a degenerate anchor, i.e. it
# exercises the site-1 dispersion dwell.
ANCHOR_F = ("T61WFNC", 60, "W", "F", 6100, 61)
# Anchor + coarse tier: narrow window + coarse band -> every served task
# is STR (test_scenarios.py:65-84), exercising the site-1 STR convention.
ANCHOR_C = ("T61NC", 20, "N", "C", 6200, 62)


def _platform():
    """Design orbit: 570 km, 45 deg inclination (test_scenarios.py:195)."""
    lib = ModeLibrary.from_fixture()
    a = 6_371_000.0 + lib.geo.altitude_m
    epoch = datetime(2026, 1, 1)
    el = KeplerianElement(
        semi_major_axis=a, eccentricity=0.001,
        inclination=math.radians(45.0), raan=0.0, arg_perigee=0.0,
        true_anomaly=0.0, epoch=epoch,
    )
    return (el, epoch), lib


def _gen(args, **kw):
    fam, den, itv, dem, seed, vi = args
    return generate_scenario(fam, den, itv, dem, seed, vi, **kw)


# ── (3) default IS the library caliber, bit-identical ────────────────────

def test_default_caliber_is_library_and_bit_identical():
    """Default == explicit "library" on BOTH generators; anything else
    raises.  The byte-level pin against the frozen v3 manifests stays
    with test_ticket35_deadbranch (scoped-run partner, unmodified)."""
    lib = ModeLibrary.from_fixture()
    assert _gen(ANCHOR_F, lib=lib) == _gen(
        ANCHOR_F, lib=lib, duration_caliber="library")
    plat, lib = _platform()
    args = ("R1C", 20, "C", 100, 1)
    assert generate_real_scenario(*args, lib=lib, platform=plat) == (
        generate_real_scenario(
            *args, lib=lib, platform=plat, duration_caliber="library")
    )
    with pytest.raises(ValueError, match="invalid duration caliber"):
        _gen(ANCHOR_F, lib=lib, duration_caliber="tasklaw")  # not the token
    with pytest.raises(ValueError, match="invalid duration caliber"):
        generate_real_scenario(
            *args, lib=lib, platform=plat, duration_caliber="")


# ── (1) task-law generator dwell == evaluator._dwell (SLS and SPT) ───────

def _first_task(manifest, mode_name):
    for i, t in enumerate(manifest["tasks"]):
        if t["mode"] == mode_name:
            return i, t
    raise AssertionError(f"no {mode_name} task served -- fixture lost its "
                         f"subject (modes: {[t['mode'] for t in manifest['tasks']]})")


@pytest.mark.parametrize("mode_name", ["SLS", "SPT"])
def test_tasklaw_generator_dwell_matches_evaluator_dwell(mode_name):
    """Same order in -> same dwell out: at all three dispersion sample
    points (window edges + centre) the site-1 task-law computation equals
    the evaluator's ``_dwell`` BIT-EXACTLY (both consume the manifest-
    rounded order; the SLS delivery identity inside duration_scene_s would
    raise on a 1e-9 rounding slip)."""
    lib = ModeLibrary.from_fixture()
    m = _gen(ANCHOR_F, lib=lib, duration_caliber="task-law")
    led = m["generation_ledger"]
    assert led["anchor_t_dispersion_max_min"] <= led[
        "anchor_t_dispersion_limit"], (
        "task-law dispersion escaped the preregistered 1.10 envelope on "
        "this seed -- the anchor property must survive the caliber switch"
    )
    prob = SchedulingProblem(m, lib)
    i, t = _first_task(m, mode_name)
    mode = Mode[mode_name]
    for tt in (t["t_start_s"], t["t_ca_s"], t["t_end_s"]):
        evaluator_dwell = prob._dwell(i, tt)
        generator_dwell = duration_scene_s(
            mode, squint_at(tt, t["t_ca_s"], lib.geo), lib,
            rho_req_m=t["rho_req_m"], l_az_m=t["azimuth_size_m"],
        )
        assert evaluator_dwell == generator_dwell, (
            f"{mode_name} dwell mismatch at t={tt}: evaluator "
            f"{evaluator_dwell!r} vs generator {generator_dwell!r}"
        )


# ── (2) discrimination: the library caliber is a DIFFERENT dwell ─────────

@pytest.mark.parametrize("mode_name", ["SLS", "SPT"])
def test_library_caliber_dwell_differs_discriminator(mode_name):
    """Red-proof: if the task-law kwargs were dropped (or the default
    silently flipped), this assertion goes red -- the library dwell at the
    design point is NOT the task-law dwell for a routed order."""
    lib = ModeLibrary.from_fixture()
    m = _gen(ANCHOR_F, lib=lib, duration_caliber="task-law")
    _, t = _first_task(m, mode_name)
    mode = Mode[mode_name]
    tt = t["t_ca_s"]  # squint zero: smallest possible dwell difference
    task_law = duration_scene_s(
        mode, squint_at(tt, t["t_ca_s"], lib.geo), lib,
        rho_req_m=t["rho_req_m"], l_az_m=t["azimuth_size_m"],
    )
    library = duration_scene_s(mode, squint_at(tt, t["t_ca_s"], lib.geo), lib)
    assert task_law != library


def test_tasklaw_moves_both_dwell_sites():
    """Generation-level red-proof for BOTH sites: same seed, only the
    caliber flipped -> site 1 moves the anchor dispersion ledger entry,
    site 2 moves the emitted real-window task set.  A dropped kwargs
    wiring turns the corresponding assertion red."""
    lib = ModeLibrary.from_fixture()
    m_lib = _gen(ANCHOR_F, lib=lib)
    m_tl = _gen(ANCHOR_F, lib=lib, duration_caliber="task-law")
    assert m_lib["tasks"] == m_tl["tasks"], (
        "site-1 dwell must NOT change routing/removals (dwell is not a "
        "removal input) -- only the dispersion reading may move"
    )
    assert (m_lib["generation_ledger"]["anchor_t_dispersion_max_min"]
            != m_tl["generation_ledger"]["anchor_t_dispersion_max_min"])

    plat, lib = _platform()
    args = ("R2F", 50, "F", 200, 2)
    r_lib = generate_real_scenario(*args, lib=lib, platform=plat)
    r_tl = generate_real_scenario(
        *args, lib=lib, platform=plat, duration_caliber="task-law")
    assert r_lib["tasks"] != r_tl["tasks"], (
        "site-2 end-check did not consume the order: task-law emitted the "
        "library-caliber windows bit-for-bit"
    )


# ── (4) STR never receives the order (both sites reachable on STR) ───────

def test_str_convention_never_passes_rho():
    """STR tasks under task-law: generation must NOT raise (the generator
    hands STR no order), while the consumed contract keeps raising on a
    direct STR+rho call (duration.py:333-339) -- the two assertions pin
    the convention from both sides."""
    lib = ModeLibrary.from_fixture()
    with pytest.raises(ValueError, match="no task-level"):
        duration_scene_s(Mode.STR, 0.0, lib, rho_req_m=2.75)

    m = _gen(ANCHOR_C, lib=lib, duration_caliber="task-law")
    assert m["tasks"] and all(t["mode"] == "STR" for t in m["tasks"])

    plat, lib = _platform()
    r = generate_real_scenario("R1C", 20, "C", 100, 1, lib=lib,
                               platform=plat, duration_caliber="task-law")
    assert r["tasks"], "site-2 task-law on the coarse tier served nothing"
    led = r["generation_ledger"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"]
