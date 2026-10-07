#!/usr/bin/env python3
"""Ticket 23 -- per-task R0 threading (R14+R15+eighth instance) tests.

Root pattern: any quantity benchmarked against the library geometry decouples
from the measured quantity once per-task geometry is injected.  These tests
pin (a) the None->library fallback caliber, (b) the per-task override, (c)
the production threading at the evaluator C2 pair, the anchor placement, the
promotion readout, and (d) the static allowlist that keeps a ninth instance
from landing silently.

Mutation contract (ticket 23 acceptance): reverting any single threading
site (or making boundary_rate/footprint_ok/aasr_direct ignore r0_m) must
turn the corresponding test RED.
"""
import ast
import math
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))

from sss_core.aasr import aasr_direct  # noqa: E402
from sss_core.anchor import greedy_anchor  # noqa: E402
from sss_core.duration import MarginPads  # noqa: E402
from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.maneuver import boundary_rate  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.nsga2 import promotion_spread_db  # noqa: E402
from sss_core.predicates import c2_transfer_requirement_s  # noqa: E402
from sss_core.windows import footprint_ok  # noqa: E402


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


PSI = math.radians(6.0)


# ── unit: the three functions honor r0_m ─────────────────────────────────

def test_boundary_rate_r0_threading(lib):
    """None -> library lever (calibration caliber); explicit r0 scales the
    lever exactly 1/r0; STR stays 0 regardless."""
    lever_lib = lib.geo.vs_mps * math.cos(PSI) / lib.geo.R0_m
    assert boundary_rate(Mode.SPT, PSI, lib) == pytest.approx(lever_lib)
    assert boundary_rate(Mode.SPT, PSI, lib, r0_m=None) == pytest.approx(lever_lib)
    assert boundary_rate(Mode.SPT, PSI, lib, r0_m=0.5 * lib.geo.R0_m) == pytest.approx(
        2.0 * lever_lib
    )
    assert boundary_rate(Mode.SPT, PSI, lib, r0_m=2.0 * lib.geo.R0_m) == pytest.approx(
        0.5 * lever_lib
    )
    assert boundary_rate(Mode.STR, PSI, lib, r0_m=0.5 * lib.geo.R0_m) == 0.0


def test_footprint_ok_r0_threading(lib):
    """SPT bound L_az <= r0*theta_a moves with the task's own range; STR/SLS
    stay by-construction True."""
    l_az = 0.9 * lib.geo.R0_m * lib.geo.theta_a_rad
    assert footprint_ok(Mode.SPT, l_az, lib)
    assert footprint_ok(Mode.SPT, l_az, lib, r0_m=None)
    # halving the range halves the bound: the same scene no longer fits
    assert not footprint_ok(Mode.SPT, l_az, lib, r0_m=0.5 * lib.geo.R0_m)
    assert footprint_ok(Mode.SPT, l_az, lib, r0_m=2.0 * lib.geo.R0_m)
    assert footprint_ok(Mode.STR, 9999.0, lib, r0_m=0.5 * lib.geo.R0_m)
    assert footprint_ok(Mode.SLS, 9999.0, lib, r0_m=0.5 * lib.geo.R0_m)


def test_aasr_direct_r0_threading(lib):
    """r0 enters AASR only through the SPT aliasing term (kat0 ∝ wa/r0);
    SLS/STR are exactly r0-invariant at a given squint (K_c/K_a = k
    cancels -- gate-review Y3; ticket 40 (yi) semantics)."""
    prf = 1150.0
    # threading sanity: explicit r0 == library R0 gives identical readings
    base = aasr_direct(Mode.SPT, PSI, lib.geo.k, prf, lib, spt_scene_wa_m=3000.0)
    same = aasr_direct(
        Mode.SPT, PSI, lib.geo.k, prf, lib, spt_scene_wa_m=3000.0,
        r0_m=lib.geo.R0_m,
    )
    assert base["aasr_db"] == pytest.approx(same["aasr_db"], abs=0.0)
    # sensitivity exists on SPT ...
    near = aasr_direct(
        Mode.SPT, PSI, lib.geo.k, prf, lib, spt_scene_wa_m=3000.0,
        r0_m=0.8 * lib.geo.R0_m,
    )
    assert near["aasr_db"] != pytest.approx(base["aasr_db"])
    # ... and NOT on SLS/STR (r0-invariant at given psi)
    for mode in (Mode.SLS, Mode.STR):
        b = aasr_direct(mode, PSI, lib.geo.k, prf, lib)
        o = aasr_direct(mode, PSI, lib.geo.k, prf, lib, r0_m=0.5 * lib.geo.R0_m)
        assert b["aasr_db"] == pytest.approx(o["aasr_db"], abs=0.0)


# ── production threading: evaluator C2 pair ──────────────────────────────

def _manifest_with_r0(lib, r0_factor):
    """Minimal two-task manifest whose tasks carry r0_m = factor * R0."""
    return {
        "schema": "test",
        "preregistration": {
            "pads": {"inter_task_fraction": 0.25, "window_tail_fraction": 0.0}
        },
        "tasks": [
            {
                # narrow windows: at r0 = 0.5*R0 a wide window swings the
                # edge squint past the +-45 deg envelope and the task
                # precompiles unschedulable
                "t_start_s": 50.0, "t_end_s": 80.0, "t_ca_s": 65.0,
                "azimuth_size_m": 4000.0, "priority": 5,
                # SLS: the boundary rate is k*lever -- STR would be exactly
                # 0 in BOTH calibers and the omega discriminator would die
                "rho_req_m": 2.0, "mode": "SLS", "prf_hz": 1150.0,
                **({"r0_m": r0_factor * lib.geo.R0_m} if r0_factor else {}),
            },
            {
                # adjacent to task 1 so the C2 gap (a few seconds) can
                # actually straddle the two calibers
                "t_start_s": 64.0, "t_end_s": 90.0, "t_ca_s": 77.0,
                "azimuth_size_m": 4000.0, "priority": 5,
                "rho_req_m": 2.0, "mode": "SLS", "prf_hz": 1150.0,
                **({"r0_m": r0_factor * lib.geo.R0_m} if r0_factor else {}),
            },
        ],
    }


def test_evaluator_c2_pair_threaded_end_to_end(lib):
    """The C2 pair inside SchedulingProblem.evaluate must quote the tasks'
    own ranges (evaluator.py:278-279).  Discriminator: scan task 2's
    feasible starts for one where the per-task-caliber requirement and the
    library-caliber requirement straddle the actual gap (they differ only
    through the omega term -- the dwell is per-task in BOTH worlds, so any
    cv difference is attributable to the call-site threading).  Reverting
    the call-site threading (mutation M2) flips the cv at that x (RED)."""
    import sss_core.evaluator as ev

    near = _manifest_with_r0(lib, 0.5)
    sp = SchedulingProblem(near, lib)
    pa, pb = sp.plans[0], sp.plans[1]
    start1 = 60.0
    # ticket 25: the squint zero is read per window at the start
    psi_a = squint_at(start1, pa.window_at(start1).t_ca_s, lib.geo, r0_m=pa.r0_m)
    dwell1 = sp._dwell(0, start1)

    def req_at(start2, r0_omega):
        # the squint stays PER-TASK in both worlds (ticket-16 threading is
        # not the mutation target): only the boundary-rate omegas vary, so
        # the straddle is attributable to the call-site threading alone
        psi_b = squint_at(start2, pb.window_at(start2).t_ca_s, lib.geo, r0_m=pb.r0_m)
        return c2_transfer_requirement_s(
            dwell1, sp.lib, sp.pads,
            d_psi_rad=abs(psi_b - psi_a),
            omega_start=boundary_rate(pa.mode, psi_a, sp.lib, r0_m=r0_omega),
            omega_end=boundary_rate(pb.mode, psi_b, sp.lib, r0_m=r0_omega),
        )["requirement_s"]

    # Deterministic straddle search: bracket the sign change of
    # f(t) = r_lib(t) - gap(t) coarsely, bisect to 1e-9, then nudge until
    # the omega-driven caliber delta (r_thread - r_lib) clears the tolerance
    # band (it is ~1e-3 s and vanishes on isolated starts where the two
    # rate-change branches agree).
    def f_lib(t):
        return req_at(t, None) - (t - start1)

    a, b = start1 + 4.0, start1 + 16.0
    fa = f_lib(a)
    assert fa * f_lib(b) < 0.0, "requirement/gap curves do not cross in window"
    for _ in range(60):
        m = 0.5 * (a + b)
        if fa * f_lib(m) <= 0.0:
            b = m
        else:
            a, fa = m, f_lib(m)
    t_cross = 0.5 * (a + b)
    chosen = None
    for k in range(200):
        t = t_cross + k * 1e-4
        gap = t - start1
        r_thread, r_lib = req_at(t, pb.r0_m), req_at(t, None)
        if (
            (r_thread - gap) * (r_lib - gap) < 0.0
            and abs(r_lib - gap) > 10 * ev.C2_TOL_S
            and abs(r_thread - gap) > 10 * ev.C2_TOL_S
            and any(lo - 1e-12 <= t <= hi + 1e-12 for lo, hi in pb.intervals)
        ):
            chosen = (t, gap, r_thread, r_lib)
            break
    assert chosen is not None, "no straddling start found in task 2 window"
    start2, gap, r_thread, r_lib = chosen

    def tau_for(plan, target):
        total = sum(hi - lo for lo, hi in plan.intervals)
        cum = 0.0
        for lo, hi in plan.intervals:
            if lo - 1e-12 <= target <= hi + 1e-12:
                return min(max((cum + (target - lo)) / total, 0.0), 1.0)
            cum += hi - lo
        raise AssertionError(f"target {target} outside feasible union")

    x = [0.0] * (2 * sp.n)
    x[0] = x[1] = 1.0
    x[sp.n] = tau_for(pa, start1)
    x[sp.n + 1] = tau_for(pb, start2)
    rec = sp.evaluate(x)
    expected_c2_cv = max(0.0, r_thread - gap - ev.C2_TOL_S)
    assert rec["cv"] == pytest.approx(expected_c2_cv, abs=1e-9), (
        rec["cv"], expected_c2_cv, gap, r_thread, r_lib
    )
    # the two calibers disagree by a discriminating margin on this same
    # plan -- whichever way they straddle, reverting the call-site threading
    # (mutation M2) flips the cv here
    assert abs(r_lib - gap) > 10 * ev.C2_TOL_S


# ── production threading: anchor placement ───────────────────────────────

def test_anchor_placement_moves_with_task_r0(lib):
    """The greedy anchor's fits()/repair C2 checks must quote per-task
    ranges.  Behavioral isolation of the omega term is impossible on this
    path (the dwell co-varies with r0 through the same plan), so the
    threading is pinned two ways: (a) the wrapper passes r0 through
    one-to-one, and (b) a structural test below asserts every
    ``boundary_rate_of`` call site in anchor.py carries the r0_m keyword
    (the mutation red-proof reverts exactly those call sites)."""
    from sss_core.anchor import boundary_rate_of

    # (a) wrapper pass-through — the behavioral placement discriminator is
    # NOT usable here: the dwell co-varies with r0 on the same plan, so a
    # placement difference (or its absence) is not attributable to the
    # omega threading alone; the structural test below pins the call sites.
    psi = math.radians(6.0)
    assert boundary_rate_of(Mode.SPT, psi, lib, r0_m=0.5 * lib.geo.R0_m) == (
        pytest.approx(boundary_rate(Mode.SPT, psi, lib, r0_m=0.5 * lib.geo.R0_m))
    )
    assert boundary_rate_of(Mode.SPT, psi, lib) == pytest.approx(
        boundary_rate(Mode.SPT, psi, lib)
    )
    assert boundary_rate_of(Mode.SPT, psi, lib, r0_m=0.5 * lib.geo.R0_m) != (
        pytest.approx(boundary_rate_of(Mode.SPT, psi, lib))
    )


def test_anchor_boundary_rate_call_sites_structural():
    """(b) Every ``boundary_rate_of(...)`` call inside anchor.py must carry
    the ``r0_m=`` keyword (six sites: fits pred/succ, repair).  Reverting
    any one of them to the library caliber is a RED here, because a purely
    behavioral discriminator cannot separate the omega term from the
    co-varying dwell on this path."""
    src = (FORK_DOMAIN / "sss_core" / "anchor.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "boundary_rate_of"
    ]
    assert len(calls) == 6, f"expected 6 call sites, found {len(calls)}"
    naked = [
        ast.unparse(n.args[0]) for n in calls
        if not any(k.arg == "r0_m" for k in n.keywords)
    ]
    assert not naked, f"boundary_rate_of calls missing r0_m: {naked}"


# ── production threading: promotion readout ──────────────────────────────

def test_promotion_spread_moves_with_task_r0(lib):
    """promotion_spread_db must quote per-task ranges: with every plan at
    r0 = 0.5*R0 the SPT aliasing term doubles and the per-candidate max
    reading changes.  Reverting nsga2.py:146 threading makes them equal."""
    manifest = _manifest_with_r0(lib, None)
    near_manifest = _manifest_with_r0(lib, 0.5)
    for m in (manifest, near_manifest):
        for t in m["tasks"]:
            t["mode"] = "SPT"
            t["rho_req_m"] = 1.5
    front = [{"starts": {"0": 75.0, "1": 89.0}}]
    # ticket 25: starts are per-window read; 89.0 sits inside task 1's
    # window [64, 90] near its edge, keeping the squint large enough to
    # witness the aliasing-term change (the old 475.0 was outside every
    # window -- a start no feasible front could ever carry)
    db_lib = promotion_spread_db(SchedulingProblem(manifest, lib), front)
    db_near = promotion_spread_db(SchedulingProblem(near_manifest, lib), front)
    assert db_lib["per_candidate_max_db"] != db_near["per_candidate_max_db"]


# ── static allowlist guard (the root closure) ────────────────────────────

ALLOWED_R0_READS = {
    # file stem -> function names allowed to read geo.R0_m
    "duration": {
        "duration_scene_s",  # None fallback
        "kim_checker_scene_sls",  # None fallback
        "duration_point_s",  # point-target caliber (g_T ratio cancels R0)
        "duration_scene_planar_oracle",  # test oracle, never production
        "duration_spt_exact_s",  # calibration alias
        "kim_eq23_theta_s1",  # D03-1 internal identity check
    },
    "anchor": {"assert_fallback_active"},  # calibration geometry
    "quality": {"q_rad"},  # D05-6 reference normalization (R_ref/R)^3
    "evaluator": {"evaluate"},  # f_q r_m None fallback
    "maneuver": {"boundary_rate"},  # None fallback (this ticket)
    "windows": {"footprint_ok"},  # None fallback (this ticket)
    "aasr": {"aasr_direct", "_build_dense"},  # None fallback / registered grid
    # REPORT mirrors' synthetic-family None fallback (same registration
    # reason as the evaluator f_q fallback)
    "verify": {"scatter_precheck", "_per_mode_means"},
}


def test_no_new_library_r0_reads_outside_allowlist():
    """AST guard: any NEW direct read of ``geo.R0_m`` in sss_core production
    modules outside the pinned allowlist turns RED -- the ninth instance of
    the caliber split cannot land silently."""
    core = FORK_DOMAIN / "sss_core"
    offenders = []
    for py in sorted(core.glob("*.py")):
        if py.name == "geometry.py":
            continue  # the field definition lives here
        tree = ast.parse(py.read_text(encoding="utf-8"))
        parent = {
            c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute) or node.attr != "R0_m":
                continue
            func, cur = None, node
            while cur in parent:
                cur = parent[cur]
                if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func = cur.name
                    break
            if func is None:
                offenders.append(f"{py.stem}:<module-level>")
            elif func not in ALLOWED_R0_READS.get(py.stem, set()):
                offenders.append(f"{py.stem}:{func}")
    assert not offenders, (
        "new library-R0 reads outside the ticket-23 allowlist: "
        f"{sorted(set(offenders))}"
    )
