#!/usr/bin/env python3
"""Ticket 10 -- NSGA-II assembly tests (T0 seam).

Guards: decode_tau contract (projection, empty-set raise, boundary clamp),
decode-site consistency + the mechanical source-scan ban on foreign linear
tau decodes (D10-4), predicate-source identity (D09-6), pilot end-to-end on
the M1NC anchor scenario, and same-seed bit-identical fronts (spec 确定性).
"""
import json
import random
import sys
from pathlib import Path

import pytest

FORK_DOMAIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK_DOMAIN))
sys.path.insert(0, str(FORK_DOMAIN.parent.parent / "src"))

from sss_core.evaluator import (  # noqa: E402
    SchedulingProblem,
    decode_solution,
    decode_tau,
    precompile_tasks,
)
from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.nsga2 import load_manifest, run_nsga2  # noqa: E402
from sss_core.predicates import c2_transfer_ok  # noqa: E402

MANIFEST_M1NC = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M1NC_seed100.json"


@pytest.fixture(scope="module")
def lib() -> ModeLibrary:
    return ModeLibrary.from_fixture()


@pytest.fixture(scope="module")
def manifest() -> dict:
    return load_manifest(MANIFEST_M1NC)


@pytest.fixture(scope="module")
def problem(manifest, lib) -> SchedulingProblem:
    return SchedulingProblem(manifest, lib)


# ── decode_tau contract (D10-2/3) ────────────────────────────────────────

def test_decode_tau_projects_into_intervals():
    intervals = ((0.0, 3.0), (10.0, 12.0), (30.0, 30.5))
    rng = random.Random(20260927)
    for _ in range(1000):
        tau = rng.random()
        t = decode_tau(tau, intervals)
        assert any(lo <= t <= hi for lo, hi in intervals), (tau, t)
    assert decode_tau(0.0, intervals) == 0.0
    assert decode_tau(1.0, intervals) == 30.5  # last-interval clamp


def test_decode_tau_empty_raises():
    with pytest.raises(ValueError, match="zero-measure"):
        decode_tau(0.5, ())
    with pytest.raises(ValueError, match="zero-measure"):
        decode_tau(0.5, ((2.0, 2.0),))


def test_decode_tau_measure_walk_order():
    """Measure-preserving: tau in the first interval's measure share lands
    in the first interval."""
    intervals = ((0.0, 3.0), (10.0, 12.0))
    assert decode_tau(0.5, intervals) < 3.0  # 1.5/5.0 share
    assert decode_tau(0.9, intervals) >= 10.0


# ── decode-site consistency (D10-4) ──────────────────────────────────────

def test_decode_sites_agree(problem):
    """Site 1 (evaluate) and site 2 (decode_solution) produce identical
    starts for the same decision vector."""
    rng = random.Random(7)
    for _ in range(20):
        x = [rng.random() for _ in range(2 * problem.n)]
        ev = problem.evaluate(x)
        rec = decode_solution(problem, x)
        assert ev["starts"] == rec["starts"]
        assert ev["f1_star"] == rec["f1_star"]


def test_selected_starts_inside_precompiled_intervals(problem):
    """>= 1000 random chromosomes: every decoded start lands inside its
    task's precompiled feasible subintervals (ticket acceptance)."""
    rng = random.Random(11)
    count = 0
    for _ in range(110):
        x = [rng.random() for _ in range(2 * problem.n)]
        starts = problem.decode_starts(x)
        for i, s in starts.items():
            intervals = problem.plans[i].intervals
            assert any(lo <= s <= hi for lo, hi in intervals), (i, s)
            count += 1
    assert count >= 1000, count


def test_source_scan_bans_foreign_linear_tau_decode():
    """D10-4 mechanical guard: the Paper-1 linear decode pattern
    (``t_earliest``/``time_span`` arithmetic) may only appear in the
    decode-site owner file (evaluator.py)."""
    root = FORK_DOMAIN / "sss_core"
    offenders = []
    for py in root.rglob("*.py"):
        if "__pycache__" in py.parts or py.name == "evaluator.py":
            continue
        src = py.read_text(encoding="utf-8")
        if "time_span" in src:
            offenders.append(py.name)
    assert not offenders, offenders


def test_predicate_source_identity(problem):
    """The evaluator consumes the ticket-09 predicates (same module), never
    a local copy (D09-6)."""
    import sss_core.predicates as pred

    assert c2_transfer_ok.__module__ == "sss_core.predicates"
    assert problem.c2_uses_predicate_source()
    assert pred.c2_transfer_ok is c2_transfer_ok


# ── violation semantics (D10-2/5) ────────────────────────────────────────

def test_empty_selection_is_cv_violation(problem):
    x = [0.0] * (2 * problem.n)
    ev = problem.evaluate(x)
    assert ev["n_selected"] == 0
    assert ev["cv"] >= 1.0
    assert ev["f_q"] == 1.0  # placeholder, not NaN


def test_unschedulable_selection_violation(problem):
    """Selecting an unschedulable task (if any exists) costs CV; a task
    with empty windows is never silently scheduled."""
    unsched = [p for p in problem.plans if not p.schedulable]
    if not unsched:
        pytest.skip("M1NC has no unschedulable tasks (expected for the anchor)")
    x = [0.0] * (2 * problem.n)
    x[unsched[0].index] = 1.0
    ev = problem.evaluate(x)
    assert ev["cv"] >= 1.0


# ── pilot end-to-end + determinism (D10-8/D11) ───────────────────────────

def test_pilot_end_to_end_m1nc(manifest, lib):
    """N=20 anchor scenario: a small deterministic run must produce a
    non-empty feasible front (|front| >= 1, CV == 0)."""
    result = run_nsga2(manifest, lib, seed=100, pop_size=20, generations=30)
    feasible = [r for r in result.front if r["cv"] == 0.0]
    assert len(feasible) >= 1
    assert result.all_cv_zero


def test_same_seed_bit_identical_front(manifest, lib):
    """Same seed -> identical front (objective values and starts)."""
    a = run_nsga2(manifest, lib, seed=100, pop_size=20, generations=30)
    b = run_nsga2(manifest, lib, seed=100, pop_size=20, generations=30)
    ja = json.dumps([(r["f1_star"], r["f_q"], r["starts"]) for r in a.front], sort_keys=True)
    jb = json.dumps([(r["f1_star"], r["f_q"], r["starts"]) for r in b.front], sort_keys=True)
    assert ja == jb


def test_runner_exit_codes(tmp_path, lib):
    """D11 distinguishing exits: 10 for a zero-served scenario, 0 for the
    pilot (11 needs an all-infeasible manifest, constructed here)."""
    from scripts.run_pilot import main as pilot_main

    empty = {
        "schema": "scenario-manifest/1.0",
        "scenario": {"family_code": "M0NC", "density_n_targets": 0,
                     "interval_width": "N", "demand_tier": "C",
                     "platform_fixture": "experiments/platform_kim2021.json",
                     "degenerate_anchor": True},
        "preregistration": {"pads": {"inter_task_fraction": 0.0,
                                     "window_tail_fraction": 0.0}},
        "generation_ledger": {},
        "tasks": [],
    }
    p_empty = tmp_path / "empty.json"
    p_empty.write_text(json.dumps(empty), encoding="utf-8")
    assert pilot_main(["--manifest", str(p_empty), "--seed", "1",
                       "--pop", "5", "--gen", "2"]) == 10

    manifest = load_manifest(MANIFEST_M1NC)
    p_ok = tmp_path / "m1nc.json"
    p_ok.write_text(json.dumps(manifest), encoding="utf-8")
    out = tmp_path / "pilot"
    rc = pilot_main(["--manifest", str(p_ok), "--seed", "100",
                     "--pop", "20", "--gen", "30", "--out", str(out)])
    assert rc == 0
    files = list(out.glob("pilot_*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["front_size"] >= 1
    assert payload["violation_stats"]["all_cv_zero"] is True


def test_precompile_respects_manifest_pads(manifest, lib):
    """The window-tail pad comes from the manifest (D10-8 single source):
    M1NC carries the degenerate zero pads -> padded == bare dwell."""
    plans = precompile_tasks(manifest, lib)
    assert all(p.schedulable for p in plans)
    assert manifest["preregistration"]["pads"]["window_tail_fraction"] == 0.0


# ── ticket 14: cv-dust tolerance (W/H matrix blocker) ────────────────────

M2WH_PATH = FORK_DOMAIN / "experiments" / "results" / "scenarios" / "M2WH_seed200.json"


def test_cv_dust_seed_passes_tolerance(lib):
    """Ticket 14: boundary-exact M2WH anchor starts used to carry CV dust
    ~1.4e-14 (the C2 positive part had no floor against the anchor fits()
    admission tolerance); pymoo's INTERNAL feasibility filter (strict
    CV==0 on the optimal-set extraction) treated the seed as infeasible,
    emptying the result front -- and the strict construction assert
    crashed run_pilot before any W/H-band experiment could run.  With the
    C2_TOL_S source floor the seed is cv EXACTLY 0.0 and a tiny NSGA run
    completes with a non-empty feasible front."""
    from sss_core.anchor import anchor_on_manifest
    from sss_core.evaluator import SchedulingProblem
    from sss_core.nsga2 import encode_seed_individual, run_nsga2

    man = load_manifest(M2WH_PATH)
    sp = SchedulingProblem(man, lib)
    anchor = anchor_on_manifest(man, lib)
    x = encode_seed_individual(sp, anchor.starts)
    ev = sp.evaluate(x)
    assert ev["cv"] == 0.0                 # exact zero, not dust
    res = run_nsga2(man, lib, seed=200, pop_size=10, generations=5,
                    seed_individual=x, anchor_f1_star=anchor.f1_star)
    assert res.anchor_seeded and res.front and res.all_cv_zero


def test_genuine_violation_seed_still_red(lib):
    """Ticket 14 anti-fixture: a seed with a REAL conflict (two tasks at
    the same start -> overlap + C2 deficit ~ several seconds, orders of
    magnitude above CV_DUST_TOL) must still fail construction."""
    import pytest as _pytest

    from sss_core.evaluator import SchedulingProblem
    from sss_core.nsga2 import CV_DUST_TOL, encode_seed_individual, run_nsga2

    tasks = [
        {"t_start_s": 0.0, "t_end_s": 40.0, "t_ca_s": 3.0,
         "azimuth_size_m": 1000.0, "priority": 10, "rho_req_m": 3.0,
         "mode": "STR", "prf_hz": 3630.0},
        {"t_start_s": 0.0, "t_end_s": 40.0, "t_ca_s": 3.0,
         "azimuth_size_m": 1000.0, "priority": 5, "rho_req_m": 3.0,
         "mode": "STR", "prf_hz": 3630.0},
    ]
    man = {
        "schema": "scenario-manifest/1.0",
        "scenario": {"family_code": "MXWN", "density_n_targets": 2,
                     "interval_width": "N", "demand_tier": "C",
                     "platform_fixture": "experiments/platform_kim2021.json",
                     "degenerate_anchor": False},
        "preregistration": {"pads": {"inter_task_fraction": 0.0,
                                     "window_tail_fraction": 0.0}},
        "generation_ledger": {},
        "tasks": tasks,
    }
    sp = SchedulingProblem(man, lib)
    both_at_zero = {0: 0.0, 1: 0.0}          # same-start conflict by hand
    x = encode_seed_individual(sp, both_at_zero)
    ev = sp.evaluate(x)
    assert ev["cv"] > CV_DUST_TOL            # genuine, not dust
    _pytest.raises(AssertionError, run_nsga2, man, lib, seed=1,
                   pop_size=4, generations=1, seed_individual=x)



# ── ticket 25: multi-window measure seam in the seed encoder ─────────────

def test_encode_seed_round_trips_all_anchor_starts_on_realwindow(lib):
    """Field regression (v3 matrix, 2026-10-05): 18/30 units died at the
    D12-1 round-trip assert because an anchor start sitting EXACTLY on an
    interval's left edge of a multi-window task loses ~1 ulp through
    ``tau*total`` and the measure-walk flips it into the PREVIOUS interval
    -- a different transit hours away (R2F 7/10, R3H 10/10 crash rate).
    The encoder must reproduce EVERY anchor start on a dense real-window
    manifest; decode_tau itself stays untouched (frozen path, MUST-3)."""
    import math

    from datetime import datetime

    from sss_core.anchor import anchor_on_manifest
    from sss_core.realwindows import KeplerianElement
    from sss_core.scenarios import generate_real_scenario
    from sss_core.nsga2 import encode_seed_individual

    a = 6_371_000.0 + lib.geo.altitude_m
    epoch = datetime(2026, 1, 1)
    plat = (
        KeplerianElement(
            semi_major_axis=a, eccentricity=0.001,
            inclination=math.radians(45.0), raan=0.0, arg_perigee=0.0,
            true_anomaly=0.0, epoch=epoch,
        ),
        epoch,
    )
    # the exact field case that crashed: R2F seed 200 (7/10 seeds died)
    m = generate_real_scenario("R2F", 50, "F", 200, 2, lib=lib, platform=plat)
    anchor = anchor_on_manifest(m, lib)
    assert anchor.starts, "fixture produced an empty anchor"
    sp = SchedulingProblem(m, lib)
    x = encode_seed_individual(sp, anchor.starts)
    for i, start in anchor.starts.items():
        back = decode_tau(x[sp.n + i], sp.plans[i].intervals)
        assert abs(back - start) <= 1e-9, (i, start, back)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
