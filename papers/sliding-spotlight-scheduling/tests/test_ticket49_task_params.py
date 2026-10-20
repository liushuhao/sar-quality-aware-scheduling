#!/usr/bin/env python3
"""Ticket 49 -- B-full task-level mode parameters (formula-spec §8.17).

The task law replaces the library design point as the mode parameter source:
SLS sets ``A_task = 2*rho_req*cos(psi_sel)/D`` (the dwell consumes
``rho_eff = rho_req*cos(psi_sel)`` in the Kim checker), SPT sets
``beta_task = lambda*sec(psi_sel)/(2*rho_req)`` (the dwell consumes the tan
difference), and both are solved AT the evaluation reference instant, whose
squint has exactly one source (``geometry.squint_at``).

Every test below states the mutation that turns it RED.  The mutation record
is not decoration: a test whose mutation leaves it green is a test that
cannot witness the code it claims to pin.

Coverage map (brief items 1-10):
  1  delivery round trip ................ test_delivery_law_round_trip
  2  zero-squint anchor (ulp=0) ......... test_zero_squint_anchor_is_the_library_world
  3  old-family path bit-identical ...... test_old_family_path_is_bit_identical
  4  AASR rho-flat / half-update red .... test_aasr_sls_is_rho_flat_...,
                                          test_aasr_half_update_..._red
  5  no re-route in the task path ....... test_task_aasr_path_never_calls_route_mode
  6  SPT envelope formation guard ....... test_spt_task_span_envelope_fails_loud, ...
  7  clip redefinition two-way .......... test_resolution_clip_*
  8  l_az directionality (R53) .......... test_laz_shortens_..., test_laz_is_inert_for_spt
  9  fixed-geometry monotonic readings .. test_fixed_geometry_sls_readings,
                                          test_fixed_geometry_spt_readings
 10  evaluator end-to-end threading ..... test_evaluator_dwell_equals_task_law
 11  C3/C4 task-law reference (§8.17-13)
    ..................................... test_c3_c4_reference_is_the_task_law_envelope,
                                          test_c3_c4_reference_skips_inapplicable_modes,
                                          test_evaluator_c3_c4_no_false_violation_...

Extra guards added after the implement-round directed review:
  * consumed-parameter delivery identity (not a same-helper re-derivation);
  * SPT start-domain clamp BEFORE the end-check (the guard would otherwise
    drop whole transit windows, measured 128/252 on R2F_seed200);
  * anchor/evaluator dwell parity.
"""
import ast
import math
import struct
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.aasr import aasr_direct  # noqa: E402
from sss_core.anchor import anchor_on_manifest  # noqa: E402
from sss_core.duration import (  # noqa: E402
    SQUINT_ENVELOPE_DEG,
    duration_scene_s,
    kim_checker_scene_sls,
    mode_squint_envelope_rad,
    spt_start_squint_limit,
    task_rho_ach,
    task_sls_factor,
    task_spt_span,
)
from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.predicates import (  # noqa: E402
    _t_env_max,
    c3_energy_normalized,
    c4_memory_normalized,
)
from sss_core.windows import (  # noqa: E402
    resolution_clip,
    spt_task_start_domain,
)

TOL = 1e-12  # formula-spec §8.17-1 / §8.17-12 tolerance


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


def ulp(a: float, b: float) -> int:
    """Bit distance between two doubles (the ticket's bitwise caliber)."""
    ia = struct.unpack("<q", struct.pack("<d", float(a)))[0]
    ib = struct.unpack("<q", struct.pack("<d", float(b)))[0]
    return abs(ia - ib)


# ── 1. delivery law round trip (SLS + SPT, at the solve point) ───────────

@pytest.mark.parametrize(
    "mode,psi_deg,rho",
    [
        (Mode.SLS, 0.0, 0.5),
        (Mode.SLS, 12.0, 0.5),
        (Mode.SLS, 26.9, 0.5),
        # 45 deg is algebraically fine for the delivery law (the A_task guard
        # is the (0,1) one); the SLS ENVELOPE rejects it at the dwell, which
        # is the mode-applicability rule of §8.17-9, not the parameter law.
        (Mode.SLS, 45.0, 0.5),
        (Mode.SPT, 0.0, 0.3),
        (Mode.SPT, 12.0, 0.3),
        (Mode.SPT, 26.9, 0.3),
        # 45 deg is NOT a valid SPT solve point: the §8.17-11 guard fires at
        # the span formation point (see the envelope tests below), so the
        # round trip is taken just inside the admissible domain.
        (Mode.SPT, 42.0, 0.6),
    ],
)
def test_delivery_law_round_trip(lib, mode, psi_deg, rho):
    """``|rho_ach(psi_sel) - rho_req| <= 1e-12`` (§8.17-1).

    MUTATION (observed RED): replace ``task_rho_ach``'s body with the library
    caliber ``lib.rho_az(mode)/cos(psi)`` -- SLS residuals become ~0.09-0.11 m
    and SPT the same order; the assertion fires on the first member.
    """
    psi = math.radians(psi_deg)
    assert abs(task_rho_ach(mode, rho, psi, lib) - rho) <= TOL


def test_str_has_no_task_parameter(lib):
    """STR's resolution is antenna-fixed (D/2); a task rho is a caller bug.

    MUTATION (observed RED): make the STR branch ignore ``rho_req_m`` -- the
    pytest.raises below stops seeing the ValueError.
    """
    with pytest.raises(ValueError, match="no task-level mode parameter"):
        duration_scene_s(Mode.STR, 0.0, lib, rho_req_m=2.5)
    with pytest.raises(ValueError, match="no task-level mode parameter"):
        task_rho_ach(Mode.STR, 2.5, 0.0, lib)


def test_consumed_parameter_is_the_guarded_one(lib, monkeypatch):
    """The §8.17-12 check reads the CONSUMED parameter, not a re-derivation of
    the same helper (the implement-round review's correction).  SLS: the
    checker's returned rotation radius reconstructs ``A_implied``; SPT: the
    span actually handed to ``_tan_diff_s`` is inverted back to a resolution.

    MUTATION (observed RED, both arms): drop the ``cos(psi)`` from
    ``task_sls_factor`` (law vs slot disagree) -> the SLS raise; make
    ``task_spt_span`` return the library design span (slot disagrees with the
    order) -> the SPT raise.  A check that only re-derived ``rho`` from the
    same helper would stay green on the SLS mutation.
    """
    import sss_core.duration as dur_mod

    psi = math.radians(12.0)
    # consistent world: no raise
    duration_scene_s(Mode.SLS, psi, lib, rho_req_m=0.5)
    duration_scene_s(Mode.SPT, psi, lib, rho_req_m=0.4)

    orig_sls = dur_mod.task_sls_factor
    monkeypatch.setattr(
        dur_mod, "task_sls_factor", lambda rho, p, geo: 2.0 * rho / geo.D_m
    )
    with pytest.raises(ValueError, match="delivery identity violated"):
        duration_scene_s(Mode.SLS, psi, lib, rho_req_m=0.5)
    monkeypatch.setattr(dur_mod, "task_sls_factor", orig_sls)

    monkeypatch.setattr(
        dur_mod, "task_spt_span", lambda rho, p, geo: lib.beta_span_spt_rad
    )
    with pytest.raises(ValueError, match="delivery identity violated"):
        duration_scene_s(Mode.SPT, psi, lib, rho_req_m=0.4)


# ── 2. zero-squint anchor: the frozen world is a special case ────────────

def test_zero_squint_anchor_is_the_library_world(lib):
    """``A_task == geo.A`` bitwise at the §8.17-3 special-case condition
    ``rho_req = 0.5*sec(psi_sel)``, and the task-law dwell equals the library
    production chain to ulp=0 at 0/12/26.9 deg.

    MUTATION (observed RED): drop the ``cos(psi)`` from ``A_task`` -- at 12 deg
    A_task becomes 0.19825..., the consumed/slot identity fires and the
    dwells separate (ulp >> 0).  Dropping the ``rho_eff = rho*cos(psi)``
    substitution in the checker has the same effect.
    """
    geo = lib.geo
    assert task_sls_factor(0.5, 0.0, geo) == geo.A  # exact, not approx
    for psi_deg in (0.0, 12.0, 26.9):
        psi = math.radians(psi_deg)
        rho = 0.5 / math.cos(psi)  # the special-case condition, §8.17-3
        task_dwell = duration_scene_s(Mode.SLS, psi, lib, rho_req_m=rho)
        lib_dwell = duration_scene_s(Mode.SLS, psi, lib)
        assert ulp(task_dwell, lib_dwell) == 0, (psi_deg, task_dwell, lib_dwell)
    # SPT: the library design point is rho = 0.3, so the zero-squint task span
    # IS the library span bitwise.
    assert task_spt_span(0.3, 0.0, geo) == lib.beta_span_spt_rad
    assert duration_scene_s(Mode.SPT, 0.0, lib, rho_req_m=0.3) == (
        duration_scene_s(Mode.SPT, 0.0, lib)
    )


# ── 3. old-family path bit-identical (rho=None, l_az=None) ───────────────

OLD_PATH_PINS = {
    # captured from the pre-ticket-49 HEAD (a3a7122) production chain
    (Mode.STR, 0.0): 1.3027299992939185,
    (Mode.STR, 12.0): 1.3317780758268154,
    (Mode.SLS, 0.0): 6.428930538022892,
    (Mode.SLS, 12.0): 6.6897980536095405,
    (Mode.SLS, 26.9): 7.915288848765346,
    (Mode.SPT, 0.0): 5.287977996696454,
    (Mode.SPT, 12.0): 5.527057109815375,
}


def test_old_family_path_is_bit_identical(lib):
    """``rho_req_m=None`` / ``l_az_m=None`` must reproduce the pre-ticket-49
    chain BITWISE (the old families' comparability contract).

    MUTATION (observed RED): make ``None`` fall back to any value other than
    the library constants (e.g. l_az None -> 3000 m), or route the None rho
    through the task law with a default rho -- every pin separates by >> 0 ulp.
    """
    for (mode, deg), want in OLD_PATH_PINS.items():
        psi = math.radians(deg)
        got = duration_scene_s(mode, psi, lib)
        assert got == want, (mode, deg, got, want)
        assert duration_scene_s(mode, psi, lib, rho_req_m=None, l_az_m=None) == want
    # checker default: scene_wa_m=None is exactly geo.scene_wa_m
    got = kim_checker_scene_sls(math.radians(12.0), 0.5, lib.geo)["sat_raw_s"]
    want = kim_checker_scene_sls(
        math.radians(12.0), 0.5, lib.geo, scene_wa_m=lib.geo.scene_wa_m
    )["sat_raw_s"]
    assert got == want


# ── 4. AASR: rho-flat under a consistent caliber, half-update is red ─────

def _task_sls_aasr_db(lib, psi_rad: float, rho: float, prf: float) -> float:
    a_task = task_sls_factor(rho, psi_rad, lib.geo)
    return aasr_direct(
        Mode.SLS, psi_rad, 1.0 - a_task, prf, lib,
        rho_zero_task_m=a_task * lib.geo.D_m / 2.0,
    )["aasr_db"]


@pytest.mark.parametrize("psi_deg", [0.0, 12.0, 26.9])
@pytest.mark.parametrize("prf", [1150.0, 3630.0])
def test_aasr_sls_is_rho_flat_under_consistent_caliber(lib, psi_deg, prf):
    """§8.17-6: with k AND B_D both from the task law, ``a_res*B_D`` is
    rho-independent, so AASR_SLS depends only on (psi, PRF).  Measured spread
    ~1e-15 dB; the assertion bound 1e-9 dB is still six orders tighter than
    any physical channel.

    MUTATION (observed RED): keep the task k but call ``aasr_direct`` without
    ``rho_zero_task_m`` (B_D stays at the library caliber = the half update) --
    the next test measures a 5.10-22.87 dB spread on this same sample set.
    """
    vals = [
        _task_sls_aasr_db(lib, math.radians(psi_deg), rho, prf)
        for rho in (0.3, 0.45, 0.6, 1.0)
    ]
    assert max(vals) - min(vals) <= 1e-9, (psi_deg, prf, vals)


@pytest.mark.parametrize("psi_deg", [0.0, 12.0])
@pytest.mark.parametrize("prf", [1150.0, 3630.0])
def test_aasr_half_update_is_discriminating_red(lib, psi_deg, prf):
    """The half update (task k, library B_D) manufactures a large spurious
    rho dependence -- the real risk §8.17-6 registers, and the reason the
    consistency test above cannot be satisfied by accident.  Measured spread
    5.70/22.01 dB at 12 deg (1150/3630 Hz).

    MUTATION (observed RED): make ``aasr_direct`` unconditionally use
    ``lib.bandwidth_d_hz`` even when ``rho_zero_task_m`` is given -- this
    test's spread collapses to ~0 and the ``> 1.0`` assertion fires.
    """
    mixed = []
    for rho in (0.3, 0.45, 0.6, 1.0):
        a_task = task_sls_factor(rho, math.radians(psi_deg), lib.geo)
        mixed.append(
            aasr_direct(
                Mode.SLS, math.radians(psi_deg), 1.0 - a_task, prf, lib
            )["aasr_db"]
        )
    assert max(mixed) - min(mixed) > 1.0, (psi_deg, prf, mixed)
    # and the task-caliber argument is SLS-only: no silent acceptance
    with pytest.raises(ValueError, match="SLS-only"):
        aasr_direct(Mode.STR, 0.0, 0.0, prf, lib, rho_zero_task_m=0.5)
    with pytest.raises(ValueError, match="SLS-only"):
        aasr_direct(Mode.SPT, 0.0, 0.0, prf, lib, rho_zero_task_m=0.5)


# ── 5. the task AASR path never re-routes ────────────────────────────────

def test_task_aasr_path_never_calls_route_mode(lib, monkeypatch):
    """§8.17-6 "禁重路由": the mode is a caller input in the B-full world;
    ``route_mode`` is a ticket-08 selection key and must not reappear inside
    ``aasr_direct``.  Pinned structurally (AST) AND behaviourally
    (monkeypatched to raise).

    MUTATION (observed RED): add ``mode = route_mode(...)`` inside
    ``aasr_direct`` -- the AST scan finds the call and the behavioural call
    raises.
    """
    import sss_core.aasr as aasr_mod

    tree = ast.parse(Path(aasr_mod.__file__).read_text(encoding="utf-8"))
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "aasr_direct"
    )
    called = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "route_mode":
                called.append(f.id)
            elif isinstance(f, ast.Attribute) and f.attr == "route_mode":
                called.append(f.attr)
    assert not called, f"aasr_direct calls route_mode: {called}"

    def boom(*a, **k):  # pragma: no cover - only reached on mutation
        raise AssertionError("route_mode reached from the task AASR path")

    monkeypatch.setattr(aasr_mod, "route_mode", boom)
    a_task = task_sls_factor(0.45, 0.1, lib.geo)
    out = aasr_direct(
        Mode.SLS, 0.1, 1.0 - a_task, 1150.0, lib,
        rho_zero_task_m=a_task * lib.geo.D_m / 2.0,
    )
    assert math.isfinite(out["aasr_db"])


# ── 6. SPT envelope at the beta_task formation point (§8.17-11) ──────────

def test_spt_task_span_envelope_fails_loud(lib):
    """``|psi_sel| + beta_task/2 <= 45 deg`` is enforced WHERE beta forms.

    psi=44 deg, rho=0.3 gives beta/2 = 2.058 deg -> 46.058 deg > 45.

    MUTATION (observed RED): delete the guard in ``task_spt_span`` -- the
    ValueError disappears and the closure silently returns an out-of-envelope
    span (the exact silent-out-of-domain failure §8.17-11 registers).
    """
    psi_bad = math.radians(44.0)
    with pytest.raises(ValueError, match="envelope"):
        task_spt_span(0.3, psi_bad, lib.geo)
    # the dwell path must inherit the same refusal
    with pytest.raises(ValueError, match="envelope"):
        duration_scene_s(Mode.SPT, psi_bad, lib, rho_req_m=0.3)
    # ... and the in-envelope corner still evaluates
    beta_ok = task_spt_span(0.3, math.radians(40.0), lib.geo)
    assert beta_ok > 0.0
    assert math.degrees(math.radians(40.0) + beta_ok / 2.0) < SQUINT_ENVELOPE_DEG


def test_spt_envelope_error_carries_the_violation_text(lib):
    """The guard's ValueError must quote the offending total angle (the brief
    requires the out-of-range value in the message).

    MUTATION (observed RED): raise a generic message -- the formatted value
    string is absent.
    """
    psi = math.radians(44.0)
    beta = lib.geo.wavelength_m / (2.0 * 0.3 * math.cos(psi))
    total = math.degrees(abs(psi) + beta / 2.0)
    with pytest.raises(ValueError) as err:
        task_spt_span(0.3, psi, lib.geo)
    msg = str(err.value)
    assert f"{total:.3f}" in msg
    assert f"{SQUINT_ENVELOPE_DEG:.1f}" in msg


def test_spt_start_domain_clamp_keeps_the_window(lib):
    """The implement-round review's B1: the guard must not delete whole
    transit windows.  A window whose ends sit outside the task envelope must
    be CLAMPED to ``|psi| <= psi_star`` before the end-check, so the speakers
    remain schedulable and every kept endpoint satisfies the guard.

    MUTATION (observed RED): remove the ``spt_task_start_domain`` call in
    ``precompile_tasks`` -- the raw window's edge sample raises inside the
    duration closure, ``except ValueError`` maps it to an empty feasible set,
    and ``tests``/``schedulable`` flips to False (pre-fix behavior: a whole
    window lost for 128 of 252 SPT windows on R2F_seed200).
    """
    psi_star = spt_start_squint_limit(0.3, lib.geo)
    assert 0.0 < psi_star < math.radians(SQUINT_ENVELOPE_DEG)
    # widen a window far past the task envelope: |t - t_ca| = 110 s gives
    # |psi| ~ 47 deg at this geometry
    man = {
        "schema": "test",
        "preregistration": {
            "pads": {"inter_task_fraction": 0.0, "window_tail_fraction": 0.0}
        },
        "tasks": [
            {
                "t_start_s": -60.0, "t_end_s": 160.0, "t_ca_s": 50.0,
                "azimuth_size_m": 2000.0, "priority": 5, "rho_req_m": 0.3,
                "mode": "SPT", "prf_hz": 3630.0,
            }
        ],
    }
    sp = SchedulingProblem(man, lib)
    plan = sp.plans[0]
    assert plan.schedulable, "window dropped instead of clamped (B1 mutation)"
    assert plan.intervals
    for lo, hi in plan.intervals:
        for t in (lo, hi):
            psi = squint_at(t, plan.windows[0].t_ca_s, lib.geo)
            beta = task_spt_span(0.3, psi, lib.geo)  # must not raise
            assert abs(psi) + beta / 2.0 <= math.radians(SQUINT_ENVELOPE_DEG) + 1e-12
    # the raw out-of-envelope edge would raise if it ever reached the closure
    with pytest.raises(ValueError, match="envelope"):
        duration_scene_s(Mode.SPT, math.radians(47.0), lib, rho_req_m=0.3)
    # and the domain helper itself is a strict subset of the input
    dom = spt_task_start_domain(((-60.0, 160.0),), 0.3, 50.0, None, lib)
    assert dom and dom[0][0] > -60.0 and dom[0][1] < 160.0


# ── 7. resolution_clip redefinition (§8.17-12) ───────────────────────────

def test_resolution_clip_str_arm_keeps_ticket48_semantics(lib):
    """STR is untouched by B-full: the ticket-48 library-caliber clip still
    bites (order finer than D/2 = the empty set; a satisfiable order narrows).

    MUTATION (observed RED): route STR through the new identity branch --
    the empty-set assertion becomes a non-empty tuple.
    """
    ivs = ((0.0, 100.0),)
    assert resolution_clip(ivs, Mode.STR, 2.0, 50.0, None, lib) == ()
    clipped = resolution_clip(ivs, Mode.STR, 2.5, 50.0, None, lib)
    assert clipped != ivs
    assert 0.0 < sum(hi - lo for lo, hi in clipped) < 100.0


def test_resolution_clip_sls_spt_do_not_shrink(lib):
    """The task law delivers the order at EVERY solve point, so the old
    library-caliber clip would falsely narrow (or empty) the feasible set:
    rho_req=0.45 is finer than the SLS library value 0.5, and 0.25 finer than
    the SPT design point 0.3 -- the old clip returns () for both (that
    reverted formula is pinned below as the discriminator).

    MUTATION (observed RED): restore the ticket-48 body for SLS/SPT -- both
    identity assertions become () instead of the input.
    """
    ivs = ((0.0, 100.0),)
    assert lib.rho_az(Mode.SLS) / 0.45 > 1.0  # the old clip would return ()
    assert lib.rho_az(Mode.SPT) / 0.25 > 1.0
    assert resolution_clip(ivs, Mode.SLS, 0.45, 50.0, None, lib) == ivs
    assert resolution_clip(ivs, Mode.SPT, 0.25, 50.0, None, lib) == ivs
    # a coarse order that the old clip would have kept narrowed is also
    # returned unchanged (the layer no longer shapes the set at all)
    assert resolution_clip(ivs, Mode.SLS, 0.55, 50.0, None, lib) == ivs


# ── 8. l_az threading (R53, §8.17-8) ─────────────────────────────────────

def test_laz_shortens_sls_and_str_dwell(lib):
    """5 km -> 1 km shortens the scene coverage term; SLS magnitude is the
    registered -40.3..-40.5% band, STR strictly decreases too (its drop
    depends on the theta_a term, so only the sign is asserted there).

    MUTATION (observed RED): ignore ``l_az_m`` (fall back to the 5 km
    constant) -- both dwells stop moving and the strict inequality fires.
    """
    for mode in (Mode.STR, Mode.SLS):
        for deg in (0.0, 12.0):
            psi = math.radians(deg)
            a = duration_scene_s(mode, psi, lib, l_az_m=5000.0)
            b = duration_scene_s(mode, psi, lib, l_az_m=1000.0)
            assert b < a, (mode, deg, a, b)
    for deg in (0.0, 12.0):
        psi = math.radians(deg)
        a = duration_scene_s(Mode.SLS, psi, lib, l_az_m=5000.0)
        b = duration_scene_s(Mode.SLS, psi, lib, l_az_m=1000.0)
        rel = (b - a) / a
        assert -0.406 <= rel <= -0.402, (deg, rel)


def test_laz_is_inert_for_spt_and_none_means_library(lib):
    """SPT is a parked beam: the scene extent is a footprint question, not a
    dwell term, so l_az must be inert there.  ``None`` is the library 5 km
    constant bitwise (the old-path contract).

    MUTATION (observed RED): feed ``l_az_m`` into the SPT tan-difference span
    -- the equality breaks.
    """
    psi = math.radians(12.0)
    for rho in (None, 0.4):
        a = duration_scene_s(Mode.SPT, psi, lib, rho_req_m=rho, l_az_m=1000.0)
        b = duration_scene_s(Mode.SPT, psi, lib, rho_req_m=rho, l_az_m=5000.0)
        assert a == b
    for mode in (Mode.STR, Mode.SLS):
        assert duration_scene_s(mode, psi, lib, l_az_m=None) == duration_scene_s(
            mode, psi, lib, l_az_m=lib.geo.scene_wa_m
        )


# ── 9. fixed-geometry monotonic readings (ticket items 3/4) ──────────────

def test_fixed_geometry_sls_readings(lib):
    """Ticket face value (fixed geometry, psi=0): rho 0.6 -> 0.3 gives
    A_task 0.243220 -> 0.121610 and a LONGER dwell (ratio 2.0012 -- not
    exactly 2: the Wa term is additive and alpha is affine in 1/A, §8.17-4).

    MUTATION (observed RED): remove the task law from the SLS dwell (library
    A pinned) -- the dwell stops responding to rho, ratio -> 1.
    """
    psi = 0.0
    a6 = task_sls_factor(0.6, psi, lib.geo)
    a3 = task_sls_factor(0.3, psi, lib.geo)
    assert a6 == pytest.approx(0.2432200764069517, rel=1e-12)
    assert a3 == pytest.approx(0.12161003820347585, rel=1e-12)
    assert a3 < a6
    t6 = duration_scene_s(Mode.SLS, psi, lib, rho_req_m=0.6)
    t3 = duration_scene_s(Mode.SLS, psi, lib, rho_req_m=0.3)
    assert t3 > t6
    assert t3 / t6 == pytest.approx(2.0012, abs=1e-3)


def test_fixed_geometry_spt_readings(lib):
    """SPT: finer order widens beta (2x at rho halving) and raises the dwell.

    MUTATION (observed RED): keep the library beta_span regardless of rho --
    the span ratio collapses to 1 and the dwell is rho-invariant.
    """
    b6 = task_spt_span(0.6, 0.0, lib.geo)
    b3 = task_spt_span(0.3, 0.0, lib.geo)
    assert b3 == pytest.approx(2.0 * b6, rel=1e-12)
    t6 = duration_scene_s(Mode.SPT, 0.0, lib, rho_req_m=0.6)
    t3 = duration_scene_s(Mode.SPT, 0.0, lib, rho_req_m=0.3)
    assert t3 > t6
    assert t3 / t6 == pytest.approx(2.0, rel=5e-3)


# ── 10. evaluator end-to-end: the solve point IS the evaluated start ─────

def _manifest(mode: str, rho: float, az_m: float) -> dict:
    return {
        "schema": "test",
        "preregistration": {
            "pads": {"inter_task_fraction": 0.0, "window_tail_fraction": 0.0}
        },
        "tasks": [
            {
                "t_start_s": 20.0,
                "t_end_s": 80.0,
                "t_ca_s": 50.0,
                "azimuth_size_m": az_m,
                "priority": 5,
                "rho_req_m": rho,
                "mode": mode,
                "prf_hz": 3630.0,
            }
        ],
    }


@pytest.mark.parametrize("mode,rho", [("SLS", 0.4), ("SPT", 0.4)])
def test_evaluator_dwell_equals_task_law(lib, mode, rho):
    """The evaluator's ``_dwell`` must equal the direct task-law call at the
    SAME squint source (``squint_at`` at the selected start) bitwise.  The
    plan must also stay SCHEDULABLE: the old library-caliber clip emptied
    this task (rho 0.4 is finer than the SLS library value 0.5 and than the
    SPT design point 0.3).

    THREADING, NOT THE LAW: both sides resolve through the same
    ``duration_scene_s``, so this equality can only witness that the call
    sites agree -- the law's discriminating power lives in
    ``test_delivery_law_round_trip``, ``test_fixed_geometry_sls_readings`` /
    ``test_fixed_geometry_spt_readings`` and
    ``test_zero_squint_anchor_is_the_library_world``.  The inequality below
    (vs the library dwell) is the part that separates this test from a
    same-helper tautology.

    MUTATION (observed RED): drop ``rho_req_m``/``l_az_m`` from the evaluator's
    ``duration_scene_s`` call -- the value falls back to the library caliber
    and the bitwise equality fails (and the inequality vs the library dwell
    flips).
    """
    man = _manifest(mode, rho, az_m=2500.0)
    sp = SchedulingProblem(man, lib)
    assert sp.plans[0].schedulable
    start = 55.0
    w = sp.plans[0].window_at(start)
    psi = squint_at(start, w.t_ca_s, lib.geo, r0_m=w.r0_m)
    expected = duration_scene_s(
        Mode[mode], psi, lib, r0_m=w.r0_m, rho_req_m=rho, l_az_m=2500.0
    )
    assert sp._dwell(0, start) == expected
    library_dwell = duration_scene_s(Mode[mode], psi, lib, r0_m=w.r0_m, l_az_m=2500.0)
    assert sp._dwell(0, start) != library_dwell


def test_evaluator_str_arm_threads_laz_but_not_rho(lib):
    """STR: l_az reaches the Wa/Vs term, rho never reaches the closure
    (passing it would raise -- the fail-loud proof that the evaluator does
    not blanket-forward the order).

    MUTATION (observed RED): blanket-forward ``rho_req_m`` for every mode --
    the first ``_dwell`` raises ValueError instead of returning a number.
    """
    man = _manifest("STR", 2.6, az_m=2000.0)
    sp = SchedulingProblem(man, lib)
    start = 55.0
    w = sp.plans[0].window_at(start)
    psi = squint_at(start, w.t_ca_s, lib.geo, r0_m=w.r0_m)
    assert sp._dwell(0, start) == duration_scene_s(
        Mode.STR, psi, lib, r0_m=w.r0_m, l_az_m=2000.0
    )
    assert sp._dwell(0, start) != duration_scene_s(Mode.STR, psi, lib, r0_m=w.r0_m)


def test_anchor_and_evaluator_agree_on_the_task_dwell(lib):
    """The greedy anchor places against the same task-level dwell the
    evaluator scores (ticket 16's parity contract, now carrying rho/l_az).

    THREADING, NOT THE LAW: the two sides meet in ``duration_scene_s``, so
    the equality witnesses parameter threading; the law itself is pinned by
    ``test_delivery_law_round_trip`` and the fixed-geometry reading tests.

    MUTATION (observed RED): drop rho/l_az from ``anchor.dwell_at`` -- the
    anchor's dwell falls back to the library caliber and the equality fails.
    """
    man = _manifest("SLS", 0.4, az_m=2500.0)
    anchor = anchor_on_manifest(man, lib)
    assert 0 in anchor.starts
    sp = SchedulingProblem(man, lib)
    start = anchor.starts[0]
    assert sp._dwell(0, start) == duration_scene_s(
        Mode.SLS,
        squint_at(start, 50.0, lib.geo),
        lib,
        rho_req_m=0.4,
        l_az_m=2500.0,
    )


# ── 11. C3/C4 reference under the task law (§8.17-13) ────────────────────

# The registered adjudication point: the SPT library design order, where the
# task-law dwell at the feasibility boundary exceeds the library reference by
# 1.274x (the false-violation mechanism this section fixes).
RHO_817_13 = 0.300907


def test_c3_c4_reference_is_the_task_law_envelope(lib):
    """§8.17-13: with an order given, the reference is the LARGEST task-law
    dwell across the modes that can serve it, each on its own envelope
    geometry.  For this order that is SLS at its 26.9 deg edge:

        ref library caliber            10.583021834038036 s
        ref task law                   14.91418667795154 s  (SLS @ 26.9 deg)
        SPT task-law dwell @ psi_star  13.48289626614966 s  (psi* = 42.9828 deg)

    The brief's shorthand "the boundary point reads ~1.0" does not hold for
    the SPT boundary: SLS's edge dominates at this order, so the SPT point
    reads 0.9040316148169288 -- still <= 1 (no false violation), and the
    reference is ATTAINED exactly (c4 = 1.0) at the SLS edge.  The c3 weight
    ladder puts that attaining point at 1.15/1.3, not 1.0.

    MUTATION (observed RED, two-sided): revert the reference to the library
    caliber (``rho_req_ref_m=None`` / ``rho_req_m=None``) and the same SPT
    point reads 1.274011948343978 > 1 -- the exact false violation.
    """
    psi_star = spt_start_squint_limit(RHO_817_13, lib.geo)
    assert math.degrees(psi_star) == pytest.approx(42.98282655779045, abs=1e-12)
    spt_edge = duration_scene_s(Mode.SPT, psi_star, lib, rho_req_m=RHO_817_13)
    assert spt_edge == pytest.approx(13.48289626614966, rel=1e-12)

    # None keeps the pre-ticket-49 reference bit-for-bit
    assert _t_env_max(lib) == 10.583021834038036
    assert _t_env_max(lib, rho_req_m=None) == _t_env_max(lib)

    ref_task = _t_env_max(lib, rho_req_m=RHO_817_13)
    assert ref_task == pytest.approx(14.91418667795154, rel=1e-12)
    assert ref_task > spt_edge > _t_env_max(lib)

    # the reference is attained at the SLS 26.9 deg edge -> c4 exactly 1.0
    sls_edge = mode_squint_envelope_rad(Mode.SLS)
    sls_dwell = duration_scene_s(Mode.SLS, sls_edge, lib, rho_req_m=RHO_817_13)
    assert sls_dwell == ref_task
    assert c4_memory_normalized(
        Mode.SLS, sls_dwell, RHO_817_13, 3630.0, lib, rho_req_ref_m=RHO_817_13
    ) == 1.0
    assert c3_energy_normalized(
        Mode.SLS, sls_dwell, lib, rho_req_m=RHO_817_13
    ) == pytest.approx(1.15 / 1.3, rel=1e-15)

    # two-sided discrimination at the SPT boundary point
    task_c4 = c4_memory_normalized(
        Mode.SPT, spt_edge, RHO_817_13, 3630.0, lib, rho_req_ref_m=RHO_817_13
    )
    lib_c4 = c4_memory_normalized(Mode.SPT, spt_edge, RHO_817_13, 3630.0, lib)
    assert task_c4 == pytest.approx(0.9040316148169288, rel=1e-12)
    assert lib_c4 == pytest.approx(1.274011948343978, rel=1e-12)
    assert task_c4 <= 1.0 < lib_c4
    task_c3 = c3_energy_normalized(
        Mode.SPT, spt_edge, lib, rho_req_m=RHO_817_13
    )
    lib_c3 = c3_energy_normalized(Mode.SPT, spt_edge, lib)
    assert task_c3 == pytest.approx(0.9040316148169292, rel=1e-12)
    assert lib_c3 == pytest.approx(1.2740119483439785, rel=1e-12)
    assert task_c3 <= 1.0 < lib_c3

    # an interior point is strictly below the boundary (dwell monotone)
    interior = duration_scene_s(
        Mode.SPT, math.radians(12.0), lib, rho_req_m=RHO_817_13
    )
    assert interior == pytest.approx(5.633558259422425, rel=1e-12)
    assert c4_memory_normalized(
        Mode.SPT, interior, RHO_817_13, 3630.0, lib,
        rho_req_ref_m=RHO_817_13,
    ) == pytest.approx(0.3777315103444978, rel=1e-12)


def test_c3_c4_reference_skips_inapplicable_modes(lib):
    """Modes that cannot serve the order are not part of the admissible
    envelope: at rho=3.0 the SLS task law leaves (0,1) and the SPT span is
    tiny, so the STR 45 deg edge (order-independent) sets the reference.

    MUTATION (observed RED): evaluate SLS unconditionally for every order --
    ``task_sls_factor`` raises inside ``_t_env_max`` instead of returning the
    STR bound (a crash, not a reading).
    """
    with pytest.raises(ValueError, match="outside \\(0,1\\)"):
        task_sls_factor(3.0, mode_squint_envelope_rad(Mode.SLS), lib.geo)
    ref = _t_env_max(lib, rho_req_m=3.0)
    assert ref == duration_scene_s(Mode.STR, math.radians(45.0), lib)
    assert ref == pytest.approx(1.945672951855394, rel=1e-12)
    spt_edge = duration_scene_s(
        Mode.SPT,
        spt_start_squint_limit(3.0, lib.geo),
        lib,
        rho_req_m=3.0,
    )
    assert spt_edge < ref


def test_evaluator_c3_c4_no_false_violation_on_the_task_law(lib):
    """End-to-end: an SPT task whose selected start sits at high squint has a
    task-law dwell ABOVE the library reference (11.3849 s vs 10.5830 s).  The
    library-caliber predicate reads 1.0758 (> 1) there, so the pre-§8.17-13
    evaluator counted a false C3+C4 violation (cv=2); the task-law reference
    reads 0.7634 and the schedule is clean (cv=0).

    MUTATION (observed RED): drop ``rho_req_m=plan.rho_req_m`` /
    ``rho_req_ref_m=plan.rho_req_m`` from the evaluator's C3/C4 call sites --
    cv flips to 2.0 (the two false violations).
    """
    rho = RHO_817_13
    man = {
        "schema": "test",
        "preregistration": {
            "pads": {"inter_task_fraction": 0.0, "window_tail_fraction": 0.0}
        },
        "tasks": [
            {
                "t_start_s": -100.0, "t_end_s": 220.0, "t_ca_s": 50.0,
                "azimuth_size_m": 2000.0, "priority": 5, "rho_req_m": rho,
                "mode": "SPT", "prf_hz": 3630.0,
            }
        ],
    }
    sp = SchedulingProblem(man, lib)
    plan = sp.plans[0]
    assert plan.schedulable
    start = plan.intervals[-1][1]  # rightmost feasible start = highest squint
    w = plan.window_at(start)
    dwell = sp._dwell(0, start)
    assert dwell == pytest.approx(11.384908171973533, rel=1e-12)
    assert dwell > _t_env_max(lib)  # the false-violation premise
    assert c4_memory_normalized(
        Mode.SPT, dwell, rho, 3630.0, lib, r0_m=w.r0_m
    ) > 1.0
    assert c4_memory_normalized(
        Mode.SPT, dwell, rho, 3630.0, lib, r0_m=w.r0_m, rho_req_ref_m=rho
    ) == pytest.approx(0.7633609809111795, rel=1e-12)

    rec = sp.evaluate([1.0, 1.0])
    assert rec["starts"] == {0: pytest.approx(start)}
    assert rec["cv"] == pytest.approx(0.0, abs=1e-9), (
        f"cv={rec['cv']}: the C3/C4 reference is back on the library caliber "
        "(pre-fix this schedule reads cv=2.0 -- a false violation)"
    )
