#!/usr/bin/env python3
"""Ticket 48 -- the per-task resolution hard constraint (clip) tests.

Root pattern (acceptance items 2/12/14/15): a constraint whose only
observable is "violations = 0" cannot distinguish a real clip from a
zero-squint no-op (route_mode already routes on the zero-squint value, so a
constant-true constraint would pass the same reading).  These tests pin the
discriminating structure: the feasible measure STRICTLY decreases, the kept
set is exactly the |psi| <= psi_max region of the single squint source, the
clip dominates whole-window dropping, both precompile paths (production and
frozen-dwell) carry the same constraint, and manifests without rho_req_m
keep their pre-ticket feasible set bit-for-bit (constructor included -- the
first cut guarded the clip but still KeyError'd at TaskPlan construction).
"""
import copy
import math
import random
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))
sys.path.insert(0, str(FORK_DOMAIN.parent.parent / "src"))

from sss_core.anchor import anchor_on_manifest  # noqa: E402
from sss_core.duration import mode_squint_envelope_rad  # noqa: E402
from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.nsga2 import (  # noqa: E402
    PROMOTION_VOID_SINGLE_OBJECTIVE,
    load_manifest,
    run_nsga2,
)
from sss_core.windows import clip_to_squint_span, resolution_clip  # noqa: E402

MANIFEST_M1NC = (
    FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M1NC_seed100.json"
)
MANIFEST_R1C = (
    FORK_DOMAIN / "experiments" / "v3_results" / "scenarios" / "R1C_seed100.json"
)

TOL = 1e-12  # the registered source-floor tolerance (ticket 48 item 6)


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def m1nc() -> dict:
    return load_manifest(MANIFEST_M1NC)


@pytest.fixture(scope="module")
def r1c() -> dict:
    return load_manifest(MANIFEST_R1C)


def measure(intervals) -> float:
    if not intervals:
        return 0.0
    return sum(hi - lo for lo, hi in intervals)


def strip_rho(manifest: dict) -> dict:
    m = copy.deepcopy(manifest)
    for t in m["tasks"]:
        t.pop("rho_req_m", None)
    return m


def scaled_rho(manifest: dict, s: float) -> dict:
    m = copy.deepcopy(manifest)
    for t in m["tasks"]:
        if t.get("rho_req_m") is not None:
            t["rho_req_m"] = s * float(t["rho_req_m"])
    return m


# ── geometry clause: clip_to_squint_span ─────────────────────────────────

def test_clip_keeps_exactly_the_psi_max_region(lib):
    """Measure identity + membership: kept measure equals the input's
    intersection with [t_ca-span, t_ca+span], and every kept boundary point's
    squint (via the single source ``squint_at``) obeys |psi| <= psi_max."""
    geo = lib.geo
    rng = random.Random(48)
    for _ in range(200):
        t_ca = rng.uniform(-50.0, 50.0)
        r0 = rng.uniform(5e5, 9e5)
        psi_max = rng.uniform(0.05, 1.2)
        span = r0 * math.tan(psi_max) / geo.vs_mps
        ivs = []
        for _ in range(3):
            a = rng.uniform(t_ca - 2 * span, t_ca + 2 * span)
            b = a + rng.uniform(0.0, span)
            ivs.append((a, b))
        ivs = tuple(ivs)
        kept = clip_to_squint_span(ivs, t_ca, r0, geo.vs_mps, psi_max)
        # measure identity: kept == input ∩ span-box
        want = 0.0
        for a, b in ivs:
            lo2, hi2 = max(a, t_ca - span), min(b, t_ca + span)
            if hi2 > lo2:
                want += hi2 - lo2
        assert measure(kept) == pytest.approx(want, abs=1e-9)
        for s in (lo for lo, _ in kept):
            assert abs(squint_at(s, t_ca, geo, r0_m=r0)) <= psi_max + 1e-12
            assert abs(s - t_ca) <= span + 1e-9


def test_clip_keeps_boundary_exact_window():
    """A window ending exactly on the span boundary survives (the 1e-12
    source-floor tolerance is a belt over the boundary, not a margin)."""
    t_ca, r0, vs = 1000.0, 6e5, 7000.0
    psi_max = 0.3
    span = r0 * math.tan(psi_max) / vs
    kept = clip_to_squint_span(((t_ca - span, t_ca + span),), t_ca, r0, vs, psi_max)
    assert len(kept) == 1
    lo, hi = kept[0]
    assert (hi - lo) == pytest.approx(2 * span, rel=1e-12)


def test_clip_drops_subtolerance_slivers():
    """An overlap thinner than the tolerance is degenerate and must not
    reach the decoder as a zero-measure interval (decode_tau raises on
    zero-measure unions)."""
    # scale chosen so 1e-14 is representable next to the boundary
    # (ulp(1.0) ~ 2.2e-16) -- the sliver is real overlap, not float dust
    t_ca = 0.0
    psi_max = math.atan(1.0)  # span = r0*tan(psi_max)/vs = 1.0 s
    # pokes 1e-14 s INTO the box from the right: overlap [1-1e-14, 1]
    sliver_hi = ((1.0 - 1e-14, 5.0),)
    assert clip_to_squint_span(sliver_hi, t_ca, 1.0, 1.0, psi_max) == ()
    # pokes 1e-14 s into the box from the left: overlap [-1, -1+1e-14]
    sliver_lo = ((-5.0, -1.0 + 1e-14),)
    assert clip_to_squint_span(sliver_lo, t_ca, 1.0, 1.0, psi_max) == ()


# ── resolution_clip: the order-aware wrapper ─────────────────────────────

def test_resolution_clip_finer_than_mode_is_empty(lib):
    """STR only: rho_req finer than ``D/2`` is unsatisfiable at EVERY start
    -> empty set, not a crash and not a partial clip.

    Ticket 49 (§8.17-12): SLS/SPT are no longer clipped at the library
    caliber -- the task law delivers the order at every solve point, so a
    requirement "finer than the library value" is serviceable and the layer
    returns the feasible set unchanged.
    """
    ivs = ((0.0, 100.0),)
    assert resolution_clip(
        ivs, Mode.STR, 0.5 * lib.rho_az(Mode.STR), 50.0, None, lib
    ) == ()
    for mode in (Mode.SLS, Mode.SPT):
        assert resolution_clip(
            ivs, mode, 0.5 * lib.rho_az(mode), 50.0, None, lib
        ) == ivs


def test_resolution_clip_clamps_to_mode_envelope(lib):
    """STR: a very coarse order leaves psi_max at the mode's own envelope, so
    the clip coincides with the plain envelope-span clip.  SLS/SPT: the
    B-full layer returns the input unchanged (§8.17-12).
    """
    ivs = ((0.0, 500.0),)
    req = 100.0 * lib.rho_az(Mode.STR)
    got = resolution_clip(ivs, Mode.STR, req, 250.0, 6e5, lib)
    want = clip_to_squint_span(
        ivs, 250.0, 6e5, lib.geo.vs_mps, mode_squint_envelope_rad(Mode.STR)
    )
    assert got == want
    for mode in (Mode.SLS, Mode.SPT):
        assert resolution_clip(
            ivs, mode, 100.0 * lib.rho_az(mode), 250.0, 6e5, lib
        ) == ivs


def test_resolution_clip_none_r0_falls_back_to_library(lib):
    """r0_m=None is the synthetic-family caliber: identical to passing the
    library R0 explicitly (same fallback convention as the dwell chain)."""
    ivs = ((0.0, 500.0),)
    for mode in Mode:
        req = 1.5 * lib.rho_az(mode)
        got = resolution_clip(ivs, mode, req, 250.0, None, lib)
        want = resolution_clip(ivs, mode, req, 250.0, lib.geo.R0_m, lib)
        assert got == want


def test_resolution_clip_of_window_already_inside_span_is_identity(lib):
    mode = Mode.STR
    req = 4.0 * lib.rho_az(mode)
    psi_max = min(
        math.acos(lib.rho_az(mode) / req), mode_squint_envelope_rad(mode)
    )
    span = lib.geo.R0_m * math.tan(psi_max) / lib.geo.vs_mps
    ivs = ((-0.25 * span, 0.25 * span),)
    got = resolution_clip(ivs, mode, req, 0.0, None, lib)
    assert len(got) == 1
    assert got[0][0] == pytest.approx(ivs[0][0], abs=1e-12)
    assert got[0][1] == pytest.approx(ivs[0][1], abs=1e-12)


# ── precompile integration: the constraint bites, per-task, both arms ────

def test_precompile_strictly_narrows_on_the_violating_family(lib, r1c):
    """Discrimination reading (item 12): total feasible measure with the
    constraint is STRICTLY below the unconstrained pipeline on a family
    known to violate (R1C 82.7% served-instance violation pre-fix).  A
    zero-squint no-op implementation fails this test while passing any
    'violations = 0' reading."""
    sp = SchedulingProblem(r1c, lib)
    sp0 = SchedulingProblem(strip_rho(r1c), lib)
    total = sum(measure(p.intervals) for p in sp.plans)
    total0 = sum(measure(p.intervals) for p in sp0.plans)
    assert total > 0.0
    assert total < total0, (total, total0)


def test_preclip_is_a_subset_of_the_unconstrained_plans(lib, m1nc):
    sp = SchedulingProblem(m1nc, lib)
    sp0 = SchedulingProblem(strip_rho(m1nc), lib)
    for pa, pb in zip(sp.plans, sp0.plans):
        if not pb.schedulable:
            assert not pa.schedulable
            continue
        for lo, hi in pa.intervals or ():
            assert any(
                lo >= l - TOL and hi <= h + TOL for l, h in pb.intervals
            ), (lo, hi)


def test_precompile_measure_monotone_nondecreasing_in_s(lib, m1nc):
    """Relaxing the order never narrows the feasible set: measures at
    s in {0.8..2.0} are non-decreasing, and s=2.0 saturates at the
    unconstrained total (the envelope, not the order, binds there)."""
    totals = []
    for s in (0.8, 0.9, 1.0, 1.1, 1.3, 2.0):
        sp = SchedulingProblem(scaled_rho(m1nc, s), lib)
        totals.append(sum(measure(p.intervals) for p in sp.plans))
    assert totals == sorted(totals), totals
    sp0 = SchedulingProblem(strip_rho(m1nc), lib)
    assert totals[-1] == pytest.approx(
        sum(measure(p.intervals) for p in sp0.plans), rel=1e-12
    )


def test_manifest_without_rho_req_survives_full_precompile(lib, m1nc):
    """The pre-ticket-25 promise, end to end: with the rho_req_m key REMOVED
    the whole precompile must succeed (the first cut guarded the clip but
    still KeyError'd at TaskPlan construction) and produce the unconstrained
    feasible set bit-for-bit-identical in measure across BOTH arms."""
    m0 = strip_rho(m1nc)
    for freeze in (False, True):
        sp0 = SchedulingProblem(m0, lib, freeze_durations=freeze)
        total0 = sum(measure(p.intervals) for p in sp0.plans)
        assert total0 > 0.0, freeze


def test_anchor_frozen_arm_without_rho_req_survives(lib, m1nc):
    """The frozen-arm precompile (anchor._precompile_frozen) is reachable
    ONLY via anchor_on_manifest -- the SchedulingProblem(freeze_durations)
    arm above does not exercise it.  A no-field manifest must survive it
    too (same KeyError class, different code path)."""
    anchor = anchor_on_manifest(strip_rho(m1nc), lib, freeze_durations=True)
    assert anchor.starts


def test_task_without_rho_req_is_immune_to_other_tasks_orders(lib, m1nc):
    """The compat gate is per-task: an entry without rho_req_m keeps its
    exact pre-ticket feasible set no matter what its neighbours order."""
    m_half = strip_rho(m1nc)
    for t in m_half["tasks"][1:]:
        t["rho_req_m"] = 0.1  # absurdly fine, unsatisfiable for every mode
    sp_ref = SchedulingProblem(strip_rho(m1nc), lib)
    sp_half = SchedulingProblem(m_half, lib)
    assert sp_half.plans[0].rho_req_m is None
    assert measure(sp_half.plans[0].intervals) == pytest.approx(
        measure(sp_ref.plans[0].intervals), abs=0.0
    )
    # sanity: the neighbours' absurd orders DID bite (order finest than any
    # mode's zero-squint resolution -> empty feasible set)
    for p in sp_half.plans[1:]:
        assert not p.schedulable


def test_frozen_arm_applies_the_same_constraint(lib, r1c):
    """Item 15: the frozen-dwell ablation's independent precompile carries
    the identical clip -- strictly below its own unconstrained arm (an
    unclipped frozen arm would make the ablation a cross-caliber
    comparison)."""
    sp_frozen = SchedulingProblem(r1c, lib, freeze_durations=True)
    sp0_frozen = SchedulingProblem(strip_rho(r1c), lib, freeze_durations=True)
    total_frozen = sum(measure(p.intervals) for p in sp_frozen.plans)
    total0_frozen = sum(measure(p.intervals) for p in sp0_frozen.plans)
    assert total_frozen > 0.0
    assert total_frozen < total0_frozen, (total_frozen, total0_frozen)


@pytest.mark.parametrize("freeze_durations", [False, True])
def test_anchor_starts_satisfy_the_order(lib, r1c, freeze_durations):
    """Item 3, both arms: every greedy-anchor start images where the
    achieved azimuth resolution obeys the order (the anchor used to take
    the earliest = max-squint point and violated at 85% on R1C)."""
    anchor = anchor_on_manifest(r1c, lib, freeze_durations=freeze_durations)
    assert anchor.starts
    sp = SchedulingProblem(r1c, lib, freeze_durations=freeze_durations)
    tasks = {i: t for i, t in enumerate(r1c["tasks"])}
    for i, start in anchor.starts.items():
        plan = sp.plans[i]
        w = plan.window_at(start)
        psi = abs(squint_at(start, w.t_ca_s, lib.geo, r0_m=w.r0_m))
        req = float(tasks[i]["rho_req_m"])
        assert lib.rho_az(plan.mode) / math.cos(psi) <= req * (1 + TOL), (i, start)


def test_clip_dominates_whole_window_dropping(lib, r1c):
    """Item 14: per task, dropping a window ENTIRELY when any part of it
    violates the order keeps no more measure than clipping -- and strictly
    less somewhere on R1C (the reading that justifies choosing clip)."""
    sp0 = SchedulingProblem(strip_rho(r1c), lib)
    sp = SchedulingProblem(r1c, lib)
    tasks = {i: t for i, t in enumerate(r1c["tasks"])}
    strict = False
    for i, plan0 in enumerate(sp0.plans):
        if not plan0.schedulable:
            continue
        req = float(tasks[i]["rho_req_m"])
        mode = plan0.mode
        drop_total = 0.0
        for lo, hi in plan0.intervals:
            w = plan0.window_at(0.5 * (lo + hi))
            psi_max = min(
                math.acos(lib.rho_az(mode) / req), mode_squint_envelope_rad(mode)
            )
            span = (w.r0_m or lib.geo.R0_m) * math.tan(psi_max) / lib.geo.vs_mps
            t_ca = w.t_ca_s
            inside = lo >= t_ca - span - TOL and hi <= t_ca + span + TOL
            drop_total += (hi - lo) if inside else 0.0
        clip_total = measure(sp.plans[i].intervals)
        assert clip_total >= drop_total - 1e-9, i
        if clip_total > drop_total + 1e-9:
            strict = True
    assert strict, "clip never beat whole-window drop on R1C -- check fixture"


# ── single-objective world markers (ticket 48 items: 目标维度改单) ────────

def test_run_nsga2_single_objective_markers(lib, m1nc):
    """End-to-end smoke at tiny budget: the front carries f_q as a READING
    (schema continuity) and the promotion decision is the registered void
    marker, never promote/no_promotion (which would fabricate a D12-3
    decision the single-objective world cannot make).  Exercises the
    np.atleast_2d extraction too -- pymoo squeezes res.F to 1-D exactly
    when the rank-0 set is a single member, an intermittent shape."""
    result = run_nsga2(m1nc, lib, seed=48, pop_size=10, generations=5)
    assert result.front
    for rec in result.front:
        assert math.isfinite(rec["f_q"]) and rec["f_q"] > 0.0
        assert rec["cv"] <= 1e-9
    assert result.promotion_decision == PROMOTION_VOID_SINGLE_OBJECTIVE
