#!/usr/bin/env python3
"""Ticket 35 -- dead-branch fixes in ``generate_real_scenario``.

Two defects, both OUTSIDE the frozen parameter domain (neither changes any
number in ``experiments/v3_results/``):

* fix 1 -- ``scenarios.py:573``: the SPT footprint-failure counter
  ``fp_fail`` was incremented but never initialised, so the first
  footprint failure raised ``UnboundLocalError`` instead of counting.
* fix 2 -- ``scenarios.py:629-644``: the AASR out-of-domain ``except``
  branch appended ``-inf``, which made an unserviceable sample the BEST
  one under the ``max()`` gate -- the direction was reversed.  An
  out-of-domain sample is +inf (never passes), matching ``nsga2.py:195``
  and ``recompute_r_fam.py:109``.

Each test reproduces the FULL trigger condition of its defect (not merely
the assertion's shape), so reverting either fix turns the test RED:

* fix 1 fixture: SPT mode is reached only through the fine band
  (rho 0.3-0.6 -> rho_az(SPT)=0.3), and the scene size must exceed the
  per-pass bound ``r0_pass * theta_a``.  At the frozen 570 km orbit that
  bound is >= 4080 m while the fine band draws at most 3000 m, so the
  branch is DEAD on the frozen platform.  Dropping the orbit to 250 km
  lowers the bound to ~1570 m, which the SAME band crosses -- the
  fixture reproduces the accident's whole condition set (SPT routing +
  per-pass r0 threading + oversize scene), not a synthetic stub.
* fix 2 fixture: ``aasr_direct`` raises for SLS only when
  ``a_res = 1 - Kc/Ka = 1 - k/cos^2(psi) <= 0``, i.e.
  ``|psi| >= acos(sqrt(k))``.  On the frozen library k = 1 - A gives that
  boundary 26.757 deg, which sits OUTSIDE the envelope guard
  (26.9 deg envelope * (1 - 0.01) = 26.631 deg) -- the cascade filters it
  out first, so the branch is DEAD on the frozen library.  Lowering A to
  0.10 pulls the boundary to 18.435 deg, INSIDE the guard, so real
  enumerated windows reach the raise.  Both the raise and the physical
  meaning are asserted: the fixed code emits ZERO windows containing an
  out-of-domain sample, while the reverted code emits many.
"""
import dataclasses
import math
import sys
from datetime import datetime
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.duration import mode_squint_envelope_rad  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.realwindows import KeplerianElement  # noqa: E402
from sss_core.windows import footprint_ok  # noqa: E402
import sss_core.scenarios as S  # noqa: E402

EPOCH = datetime(2026, 1, 1)


def _platform(altitude_m: float):
    """Design orbit at an arbitrary altitude; only the altitude varies."""
    return (
        KeplerianElement(
            semi_major_axis=6_371_000.0 + altitude_m,
            eccentricity=0.001,
            inclination=math.radians(45.0),
            raan=0.0,
            arg_perigee=0.0,
            true_anomaly=0.0,
            epoch=EPOCH,
        ),
        EPOCH,
    )


def _lib_with(lib: ModeLibrary, **geo_overrides) -> ModeLibrary:
    """Swap geometry fields only -- routing keys (rho_req bands) are
    fixture-bound and deliberately NOT moved, so the SPT tier the fixture
    reaches is the same tier production reaches."""
    return dataclasses.replace(lib, geo=dataclasses.replace(lib.geo, **geo_overrides))


# ── fix 1: fp_fail initialisation ────────────────────────────────────────

def test_fp_fail_counter_is_initialised_so_spt_footprint_failure_does_not_crash():
    """Fix 1 (scenarios.py:573).  The fixture reproduces the accident's
    full condition set: an SPT-routed task (fine band rho 0.3-0.6 ->
    rho_az(SPT) = 0.3), evaluated against its OWN pass's per-task slant
    range, whose scene exceeds ``r0_pass * theta_a``.

    Before the fix the first such pass raised
    ``UnboundLocalError: cannot access local variable 'fp_fail'``; after
    it the failure is COUNTED and attributed to ``removals["footprint"]``.
    """
    from sss_core.geometry import look_geometry

    lib0 = ModeLibrary.from_fixture()

    # precondition A: the frozen platform cannot reach the branch at all
    # (this is WHY the defect survived every frozen-parameter run)
    fine_hi = 3000.0  # scenarios.py:554 upper draw for the fine band
    r0_frozen = min(
        look_geometry(lib0.geo.altitude_m, inc)[2]
        for inc in S.R_INCIDENCE_BAND_DEG
    )
    assert fine_hi <= r0_frozen * lib0.geo.theta_a_rad, (
        "the frozen platform now reaches the footprint-failure branch -- "
        "this test's 'dead on the frozen domain' premise no longer holds"
    )

    # precondition B: the fixture DOES reach it -- SPT routed, oversize
    assert lib0.rho_az(Mode.SPT) < 0.6, "fine band no longer routes to SPT"
    alt = 250_000.0
    lib = _lib_with(lib0, altitude_m=alt)
    seen = {"spt_fail": 0, "spt_pass": 0, "worst_ratio": 0.0}
    real = S.footprint_ok

    def counting(mode, l_az_m, libx, r0_m=None):
        ok = real(mode, l_az_m, libx, r0_m=r0_m)
        if mode is Mode.SPT:
            seen["spt_pass" if ok else "spt_fail"] += 1
            if r0_m is not None:
                seen["worst_ratio"] = max(
                    seen["worst_ratio"], l_az_m / (r0_m * libx.geo.theta_a_rad)
                )
        return ok

    S.footprint_ok = counting
    try:
        m = S.generate_real_scenario(
            "R2F", 50, "F", 200, 2, lib=lib, platform=_platform(alt)
        )
    finally:
        S.footprint_ok = real

    assert seen["spt_fail"] > 0, (
        "fixture lost the trigger condition -- reverting the fix would be "
        "invisible"
    )
    assert seen["worst_ratio"] > 1.0, (
        "the failing SPT passes were not actually over the footprint bound"
    )
    led = m["generation_ledger"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"], led
    # the branch that USED to crash now attributes removals
    assert led["removals"]["footprint"] > 0, led["removals"]


def test_fp_fail_counter_is_reachable_without_any_monkeypatch():
    """Same defect, no instrumentation: the fixture alone must complete
    the manifest (the pre-fix code raised UnboundLocalError here) and
    report a non-zero footprint attribution."""
    lib0 = ModeLibrary.from_fixture()
    alt = 250_000.0
    m = S.generate_real_scenario(
        "R2F", 50, "F", 200, 2,
        lib=_lib_with(lib0, altitude_m=alt),
        platform=_platform(alt),
    )
    led = m["generation_ledger"]
    assert led["removals"]["footprint"] > 0, led["removals"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"], led


# ── fix 2: AASR out-of-domain sentinel direction ─────────────────────────

def _window_max_abs_squint_deg(window, geo):
    """The 11 samples the generator actually evaluates, read back through
    the same squint model -- no peeking at generator internals."""
    return max(
        abs(math.degrees(S.squint_at(
            window["lo_s"] + (window["hi_s"] - window["lo_s"]) * j / 10,
            window["t_ca_s"], geo, r0_m=window["r0_m"],
        )))
        for j in range(11)
    )


def test_aasr_out_of_domain_sample_is_plus_inf_not_minus_inf():
    """Fix 2 (scenarios.py:629-644).  The except branch must append +inf.

    ``-inf`` is the direction reversal: the gate is
    ``max(aasr_vals) > AASR_THRESHOLD_DB``, so a -inf sample makes an
    UNSERVICEABLE window look like the best-reading one and lets it
    through.  +inf means "infinitely bad" -- the window can never pass.

    The fixture reproduces the whole trigger condition: the SLS
    ``a_res <= 0`` raise boundary (acos(sqrt(k))) is pulled INSIDE the
    envelope guard by lowering A, so enumerated windows really do reach
    the raise.  The discriminator is the emitted manifest: with the fix,
    NO emitted window may contain an out-of-domain sample.
    """
    lib0 = ModeLibrary.from_fixture()

    # precondition A: on the frozen library the raise boundary sits OUTSIDE
    # the envelope guard, so the cascade filters it first -- the branch is
    # dead on the frozen domain and no frozen number can move
    guard = math.degrees(mode_squint_envelope_rad(Mode.SLS)) * (
        1.0 - S.R_ENVELOPE_GUARD_FRACTION
    )
    frozen_boundary = math.degrees(math.acos(math.sqrt(lib0.geo.k)))
    assert frozen_boundary > guard, (
        f"frozen a_res boundary {frozen_boundary:.3f} deg is no longer "
        f"outside the {guard:.3f} deg envelope guard"
    )

    # precondition B: the fixture pulls the boundary inside the guard
    lib = _lib_with(lib0, A=0.10)
    boundary = math.degrees(math.acos(math.sqrt(lib.geo.k)))
    assert boundary < guard, f"boundary {boundary:.3f} deg >= guard {guard:.3f}"

    # the raise is genuinely reached (the branch is not vacuous)
    from sss_core.aasr import aasr_direct
    with pytest.raises(ValueError, match="a_res"):
        aasr_direct(Mode.SLS, math.radians(boundary + 0.5), lib.geo.k,
                    S.PRF_PRODUCTION_HZ, lib)

    m = S.generate_real_scenario(
        "R2F", 50, "F", 200, 2, lib=lib, platform=_platform(570_000.0)
    )
    windows = [w for t in m["tasks"] for w in t["windows"]]
    assert windows, "fixture produced no windows -- the test lost its subject"
    out_of_domain = [
        w for w in windows if _window_max_abs_squint_deg(w, lib.geo) > boundary
    ]
    assert not out_of_domain, (
        f"{len(out_of_domain)}/{len(windows)} emitted windows carry an "
        "out-of-domain AASR sample -- an unserviceable window was emitted, "
        "which is exactly the -inf direction reversal"
    )
    led = m["generation_ledger"]
    assert sum(led["removals"].values()) + led["n_served"] == led["n_drawn"], led


def test_out_of_domain_sentinel_is_infinite_not_minus_infinite():
    """Pin the sentinel DIRECTION at the source, so a future refactor
    cannot re-invert it silently.  Reads the shipped source of the
    generator's AASR sampling loop (the branch is unreachable from a
    unit-level call: ``aasr_direct`` raises before the generator can
    hand it a value)."""
    import inspect
    import re

    src = inspect.getsource(S.generate_real_scenario)
    match = re.search(
        r"except ValueError:.*?aasr_vals\.append\((float\(\"[+-]?inf\"\))\)",
        src,
        re.S,
    )
    assert match, "the AASR out-of-domain except branch is gone"
    assert match.group(1) == 'float("+inf")', (
        f"out-of-domain sentinel is {match.group(1)} -- must be "
        'float("+inf"): an unserviceable sample is infinitely BAD, never '
        "the best reading under the max() gate"
    )


# ── the frozen domain must be untouched ──────────────────────────────────

def test_frozen_domain_scenarios_are_byte_identical_after_both_fixes():
    """Neither defect is reachable on the frozen parameters, so the
    shipped manifests must regenerate byte-identically.  This is the
    invariant that makes both fixes safe to land."""
    import json

    from sss_core.realwindows import kepler_to_eci  # noqa: F401  (import canary)
    from sss_core.duration import MarginPads

    lib = ModeLibrary.from_fixture()
    regen = {}
    for fam, den, tier, seed, vi in (
        ("R1C", 20, "C", 100, 1),
        ("R2F", 50, "F", 200, 2),
        ("R3H", 100, "H", 300, 3),
    ):
        m = S.generate_real_scenario(fam, den, tier, seed, vi, lib=lib,
                                     platform=_platform(570_000.0))
        regen[f"{fam}_seed{seed}"] = m
        path = (
            FORK_DOMAIN / "experiments" / "v3_results" / "scenarios"
            / f"{fam}_seed{seed}.json"
        )
        if not path.is_file():
            continue
        shipped = json.loads(path.read_text(encoding="utf-8"))
        assert m["tasks"] == shipped["tasks"], (
            f"{path.name}: served tasks changed -- a frozen number moved"
        )
        assert m["generation_ledger"] == shipped["generation_ledger"], (
            f"{path.name}: generation ledger changed -- a frozen number moved"
        )
    assert MarginPads.standard().inter_task_fraction == 0.25


def test_footprint_ok_bound_is_the_one_footprint_fail_reads():
    """Anchor the repair against the shipped predicate: fix 1 counts
    failures of ``footprint_ok`` at this pass's own r0 (ticket 23 R15),
    not of the library-R0 fallback used by the synthetic generator."""
    lib = ModeLibrary.from_fixture()
    r0 = lib.geo.R0_m * 0.5
    inside = r0 * lib.geo.theta_a_rad * 0.99
    outside = r0 * lib.geo.theta_a_rad * 1.01
    assert footprint_ok(Mode.SPT, inside, lib, r0_m=r0) is True
    assert footprint_ok(Mode.SPT, outside, lib, r0_m=r0) is False
    # the same scene passes against the LIBRARY r0 -- the split the counter
    # sits downstream of
    assert footprint_ok(Mode.SPT, outside, lib) is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
