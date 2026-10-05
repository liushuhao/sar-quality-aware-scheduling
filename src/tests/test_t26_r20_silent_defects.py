"""Ticket 26 / R20 — the two silent shared-library defects, made loud.

R20 (residual ledger, 2026-10-04) recorded a latent group in ``src/sar_sim/``
whose Paper1 numbers were safe (the generator chain is fronted by the
elevation guard at ``visibility.py:183``) but whose *live* edges silently
produced wrong values:

1. ``verification/constraints.py::verify_c1_incidence_squint`` returned C1
   PASS for an observation moment outside the registered window.  Two paths
   reach that PASS: (a) a folded phi from a below-horizon moment converts
   into the incidence band (elev=-40deg -> 49.98deg vs a true 134.5deg), and
   (b) ``GeomCache.lookup`` silently clamps an out-of-window ``t_actual`` to
   the nearest in-window sample, which *looks* legal.  The guard cannot live
   in the converter (ticket 24 proved folded and near-side angles are
   indistinguishable on (phi, h)), so it goes in front, in the verify layer.
2. ``solver/so_f1.py`` recomputed f2 from elevation when ``geom_cache`` was
   missing, assuming cos(psi)=1 — a silent +10.9% bias.  Both fallbacks now
   raise; every standard runner calls ``precompute_geometry`` first (R20
   grep evidence).

Measured pre-fix state (probes ``.remember/tmp/t26_probe{,2,3}.py``, run
against the unmodified tree before this change landed):

    t_actual=950.0  (50 s before t_earliest=1000.0)  -> C1 passed=True viol=0
    t_actual=1220.0 (50 s after  t_latest-dur=1170.0) -> C1 passed=True viol=0
    no-cache b2_profit_solver_bl_seeded -> DID NOT RAISE, n_sel=20,
                                            f2=0.5376162392660337

Both are the exact states the mutation proofs below roll the code back to.

Mutation proofs (the discriminating mechanism, per the ticket's acceptance):

* ``test_c1_rejects_out_of_window_observation_moment`` / ``..._folded_phi...``
  go red if the window-containment block in ``verify_c1_incidence_squint``
  is deleted or its bound is widened past 1e-9.  Rolling back to the
  pre-fix code restores ``passed=True`` on an out-of-window ``t_actual``
  whose clamped lookup geometry is entirely in-band — the assertion is on
  ``passed is False``, so it flips on the rollback, not on a numeric drift.
* ``test_so_f1_*_raises_without_geom_cache`` go red if the ``elif sel:``
  guard is restored to the elevation-based body: the pre-fix code returns a
  SolverResult with ``f2=0.5376`` instead of raising, so ``pytest.raises``
  fails.

No-regression guard: ``test_so_f1_standard_path_is_bit_identical`` pins the
exact repr of f1/f2/f3 for the cached path (pre-fix values above), so a
fix that perturbs the normal path cannot hide behind the raise.
"""

import pathlib
import pickle
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "src"))

from sar_sim.solver.types import (  # noqa: E402
    AgileSARInstance,
    AgileTask,
    build_agile_instance_from_scenario,
    compute_full_attitude,
    precompute_geometry,
)
from sar_sim.types import GroundTarget  # noqa: E402
from sar_sim.verification.constraints import verify_c1_incidence_squint  # noqa: E402
from sar_sim.solver.baselines import baseline_b1  # noqa: E402

SCEN_S1 = (pathlib.Path(__file__).resolve().parents[2] /
           "papers/single-sat-quality/experiments/scenarios/S1")
SCEN_S5 = (pathlib.Path(__file__).resolve().parents[2] /
           "papers/single-sat-quality/experiments/scenarios/S5")

# Bounds of the hand-built fixture below (also the GeomCache grid extent:
# the cache spans [t_earliest, t_latest - duration]).
T_EARLIEST = 1000.0
T_LATEST_MINUS_DUR = 1170.0


def _fixture():
    """One task, one instance with a live GeomCache — mirrors test_geom_cache."""
    target = GroundTarget(target_id="T000", lat=30.0, lon=100.0, priority=10)
    task = AgileTask(
        task_id=0, target_id="T000", priority=10.0,
        windows=[], phi_min=0.3, phi_max=0.8,
        t_earliest=T_EARLIEST, t_latest=T_EARLIEST + 200.0,
        duration=30.0, energy=50000.0, memory=5e8, phi_min_res=0.0,
    )
    instance = AgileSARInstance(
        tasks=[task], N=1,
        phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={"T000": target},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0,
        orbit_ref_time_s=T_EARLIEST,
    )
    precompute_geometry(instance, step_s=10.0)
    return instance, task


# ═══════════════════════════════════════════════════════════════════════════
# Acceptance 1 (RED): the C1 out-of-window false PASS
# ═══════════════════════════════════════════════════════════════════════════

def test_c1_rejects_out_of_window_observation_moment():
    """An out-of-window t_actual must be a C1 violation, not a silent PASS.

    The false green is real, not hypothetical: ``GeomCache.lookup`` clamps
    ``t_actual`` to the nearest grid sample, so an observation 50 s outside
    the window is scored with fully in-window geometry and PASSes C1 with
    zero violations.  Measured pre-fix on both sides of the window:

        t=950.0  (50 s before t_earliest)       -> passed=True viol=0
        t=1220.0 (50 s after  t_latest-dur)    -> passed=True viol=0

    Mutation proof: deleting the window-containment block from
    ``verify_c1_incidence_squint`` restores exactly those two readings and
    turns this assertion red (``passed is False``).
    """
    instance, task = _fixture()
    # In-window phi, so the only thing wrong with these inputs is the time.
    phi_in = float(instance.geom_cache.lookup(0, T_EARLIEST + 60.0).phi)

    before = verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], instance=instance,
        t_actual=np.array([T_EARLIEST - 50.0]),
    )
    after = verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], instance=instance,
        t_actual=np.array([T_LATEST_MINUS_DUR + 50.0]),
    )

    assert not before.passed, "before-window moment silently PASSed C1"
    assert not after.passed, "after-window moment silently PASSed C1"
    assert any("outside" in v.description for v in before.violations)
    assert any("outside" in v.description for v in after.violations)


def test_c1_rejects_folded_phi_below_horizon():
    """Folded phi + an out-of-window moment is caught by the containment check.

    A below-horizon moment (elev=-50deg here) yields phi=140deg; the
    spherical-Earth converter folds it to theta=45.4555deg, inside the
    global [16.68, 58.15]deg band, while the true incidence is 134.5deg --
    far outside.  The folded and near-side angles are indistinguishable on
    (phi, h), so the converter cannot be guarded (ticket 24) and phi stays
    as-is here; the out-of-window moment is the observable that carries the
    violation.

    The second half pins the scope boundary the ticket draws: a folded phi at
    an *in-window* moment must still PASS.  A fix that starts rejecting
    folded phi per se would over-reach past the R20 live edge.
    """
    instance, task = _fixture()
    phi_folded = np.radians(140.0)

    out_of_window = verify_c1_incidence_squint(
        [0], np.array([phi_folded]), [task], instance=instance,
        t_actual=np.array([T_EARLIEST - 50.0]),
    )
    assert not out_of_window.passed, (
        "folded phi with an out-of-window moment silently PASSed C1"
    )

    in_window = verify_c1_incidence_squint(
        [0], np.array([phi_folded]), [task], instance=instance,
        t_actual=np.array([T_EARLIEST + 60.0]),
    )
    assert in_window.passed, (
        "folded phi at an in-window moment must stay PASS -- the guard "
        "belongs in the window check, not in the phi->theta converter"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Acceptance 2 (GREEN, no regression): in-window output stays bit-identical
# ═══════════════════════════════════════════════════════════════════════════

def test_c1_in_window_output_is_unchanged():
    """An in-window sample must reproduce the pre-fix result exactly.

    Pre-fix reading, captured before this change landed:

        constraint='C1' passed=True total_checks=1 violations=0 worst=0.0

    Every field is pinned, including ``total_checks``: the containment check
    is a per-task gate on an existing iteration and must not add a count.
    """
    instance, task = _fixture()
    t_in = T_EARLIEST + 60.0
    phi_in = float(instance.geom_cache.lookup(0, t_in).phi)

    res = verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], instance=instance,
        t_actual=np.array([t_in]),
    )
    assert res.constraint == "C1"
    assert res.passed is True
    assert res.total_checks == 1
    assert len(res.violations) == 0
    assert res.worst_violation_magnitude == 0.0


def test_c1_window_edges_are_inclusive_with_1e9_tolerance():
    """The bound is [t_earliest, t_latest-duration] widened by 1e-9."""
    instance, task = _fixture()
    phi_in = float(instance.geom_cache.lookup(0, T_EARLIEST + 60.0).phi)

    def check(t):
        return verify_c1_incidence_squint(
            [0], np.array([phi_in]), [task], instance=instance,
            t_actual=np.array([t]),
        )

    assert check(T_LATEST_MINUS_DUR).passed, "upper edge must be inclusive"
    assert check(T_EARLIEST).passed, "lower edge must be inclusive"
    # Inside the 1e-9 tolerance, still PASS.
    assert check(T_LATEST_MINUS_DUR + 5e-10).passed
    # One microsecond past it is a violation -- far above any float dust.
    assert not check(T_LATEST_MINUS_DUR + 1e-6).passed


def test_c1_window_check_needs_instance_and_t_actual():
    """Either input missing means no containment check -- status quo preserved.

    C1 squint is enforced on the window-generation side, so a call without
    an instance or without times keeps its old behaviour instead of gaining
    a check it cannot ground.
    """
    instance, task = _fixture()
    phi_in = float(instance.geom_cache.lookup(0, T_EARLIEST + 60.0).phi)
    t_out = T_EARLIEST - 50.0

    assert verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], t_actual=np.array([t_out]),
    ).passed, "no instance -> no containment check"

    assert verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], instance=instance,
    ).passed, "no t_actual -> no containment check"

    # instance present, geom_cache absent, times present: the containment
    # check is grounded in the registered window bounds alone, so it fires.
    bare = AgileSARInstance(
        tasks=[task], N=1, phi_min=0.2618, phi_max=0.8727,
        max_slew_rate=0.0524, settle_time=5.0,
        energy_budget=1e7, memory_budget=1e11,
        target_map={"T000": GroundTarget(
            target_id="T000", lat=30.0, lon=100.0, priority=10)},
        altitude_m=693_000.0,
        orbit_inclination_rad=np.radians(97.8),
        orbit_period_s=5800.0, orbit_ref_time_s=T_EARLIEST,
    )
    assert not verify_c1_incidence_squint(
        [0], np.array([phi_in]), [task], instance=bare,
        t_actual=np.array([t_out]),
    ).passed, "containment check needs only instance + t_actual"


def test_c1_realistic_in_window_sample_is_unchanged():
    """Paper1's own G-BL schedule must still PASS C1 after the fix.

    This is the no-false-positive half: the guard must not flag the real
    schedules whose moments are all inside their registered windows.  Run on
    a committed S1 scenario through the production builder, so the times
    come from G-BL's actual observation starts rather than a hand-written
    fixture.
    """
    data = _load_scenario(SCEN_S1)
    if data is None:
        pytest.skip("S1 scenarios not available")
    inst = _build_s1_instance(data)
    sel, phi, t_actual = _gbl_selection(inst, data)
    if not sel:
        pytest.skip("G-BL selected nothing on this scenario")

    res = verify_c1_incidence_squint(
        sel, phi, inst.tasks, instance=inst, t_actual=t_actual,
    )
    assert res.passed, (
        "in-window G-BL schedule flagged: "
        f"{[v.description for v in res.violations][:3]}"
    )
    assert res.total_checks == len(sel)


# ═══════════════════════════════════════════════════════════════════════════
# Acceptance 3: so_f1 no-cache fallback raises instead of biasing f2
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("solver_name", ["bl_seeded", "hotstart"])
def test_so_f1_raises_without_geom_cache(solver_name):
    """A missing geom_cache must crash loudly, not emit a cos(psi)=1 f2.

    Pre-fix, with ``precompute_geometry`` stubbed out, both solvers returned
    a result whose f2 came from ``sin(theta(90 - elevation))`` -- a silent
    +10.9% bias (measured: ``f2=0.5376162392660337``, ``f3=0.0``).

    Mutation proof: restoring the ``elif sel:`` body turns this red, because
    the pre-fix code returns normally instead of raising.
    """
    import sar_sim.solver.so_f1 as so_f1

    data = _load_scenario(SCEN_S1)
    if data is None:
        pytest.skip("S1 scenarios not available")

    original = so_f1.precompute_geometry
    so_f1.precompute_geometry = lambda instance, step_s=10.0: None
    try:
        with pytest.raises(RuntimeError, match="geom_cache"):
            if solver_name == "bl_seeded":
                so_f1.b2_profit_solver_bl_seeded(
                    data["windows"], data["targets"],
                    population_size=20, n_generations=5, seed=7,
                )
            else:
                so_f1.ga_hotstart_solver(
                    data["windows"], data["targets"],
                    hotstart_selected=[], hotstart_t_actuals=[],
                    population_size=20, n_generations=5, seed=7,
                )
    finally:
        so_f1.precompute_geometry = original


def test_so_f1_standard_path_is_bit_identical():
    """The cached path is untouched: f1/f2/f3 reproduce the pre-fix reprs.

    Pre-fix values, S5 first scenario, seed=7, pop=20, gen=10:
        bl_seeded    f1=85.0  f2=0.020207893978938862 f3=0.42745451136059676
        ga_hotstart  f1=8.0   f2=0.021466107370506655 f3=0.45225718200988907

    repr()-level equality, so any arithmetic drift is a failure.
    """
    import sar_sim.solver.so_f1 as so_f1

    data = _load_scenario(SCEN_S5)
    if data is None:
        pytest.skip("S5 scenarios not available")

    bl = so_f1.b2_profit_solver_bl_seeded(
        data["windows"], data["targets"],
        population_size=20, n_generations=10, seed=7,
    ).metadata
    assert bl["f1"] == 85.0
    assert bl["f2"] == 0.020207893978938862
    assert bl["f3"] == 0.42745451136059676
    assert bl["n_selected"] == 15

    hs = so_f1.ga_hotstart_solver(
        data["windows"], data["targets"],
        hotstart_selected=[], hotstart_t_actuals=[],
        population_size=20, n_generations=10, seed=7,
    ).metadata
    assert hs["f1"] == 8.0
    assert hs["f2"] == 0.021466107370506655
    assert hs["f3"] == 0.45225718200988907
    assert hs["n_selected"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_scenario(family_dir):
    pkgs = sorted(family_dir.glob("*.pkl"))
    if not pkgs:
        return None
    return pickle.load(open(str(pkgs[0]), "rb"))


def _build_s1_instance(data):
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=0.0524, settle_time=5.0, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    return inst


def _gbl_selection(inst, data):
    res = baseline_b1(data["windows"], data["targets"], instance=inst)
    t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
    sel, phi, t_actual = [], np.zeros(inst.N), np.zeros(inst.N)
    for obs in res.schedule:
        i = t2i.get(obs.window.target_id)
        if i is not None:
            sel.append(i)
            t_actual[i] = obs.t_actual_start.timestamp()
            roll, _, _ = compute_full_attitude(
                inst.tasks[i], t_actual[i], 1.0, inst)
            phi[i] = roll
    return sel, phi, t_actual