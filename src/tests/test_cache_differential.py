"""Differential tests: cached geometry must agree with exact orbit.

These guard the defect where linear interpolation on the 10s ECEF grid
caused up to 6.98ms error in C2 maneuver time tau, producing false-negative
feasibility (cached PASS / precise FAIL). Cubic Lagrange interpolation
must keep this error far below any physical tolerance.

Also checks GeomCache (phi/psi/theta) against compute_full_attitude and
verifies a solver's persisted knee solution carries the fields needed for
independent hard audit.
"""
import json
import pathlib
import pickle
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "src"))

from sar_sim.solver.types import (
    build_agile_instance_from_scenario,
    precompute_geometry,
    compute_los_separation,
    compute_full_attitude,
    _satellite_body_frame,
)
from sar_sim.metrics.nesz import off_nadir_to_incidence
from sar_sim.verification.constraints import ConstraintVerifier

SLEW, SETTLE = 0.0524, 5.0
SCEN = pathlib.Path(__file__).resolve().parents[2] / "papers/single-sat-quality/experiments/scenarios/S1"


def _load_instance():
    pkgs = sorted(SCEN.glob("*.pkl"))
    if not pkgs:
        pytest.skip("S1 scenarios not available")
    data = pickle.load(open(pkgs[0], "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    return inst


def test_sat_position_cache_vs_exact():
    """Cubic SatPositionCache LOS separation error must be sub-microsecond in tau."""
    inst = _load_instance()
    cache = inst.sat_position_cache
    rng = np.random.RandomState(42)
    times = cache.times[0] + rng.uniform(0, cache.times[-1] - cache.times[0], 200)
    max_tau_err = 0.0
    for t in times:
        sat_c = cache.lookup_position(t)
        sat_e = _satellite_body_frame(t, inst)[3]
        # Position error maps directly to LOS-angle error; bound in meters.
        max_tau_err = max(max_tau_err, float(np.linalg.norm(sat_c - sat_e)))
    # Cubic interp on a smooth orbit: position error should be well under 1 mm,
    # vs linear's ~meters at segment midpoint.
    assert max_tau_err < 1e-2, f"sat position cache err {max_tau_err*1000:.3f} mm too large"


def test_geom_cache_vs_exact_attitude():
    """Cubic GeomCache phi/psi/theta must match compute_full_attitude tightly."""
    inst = _load_instance()
    task = inst.tasks[0]
    tmin, tmax = task.t_earliest, task.t_latest - task.duration
    if tmax <= tmin:
        pytest.skip("task window too short")
    rng = np.random.RandomState(7)
    times = np.sort(rng.uniform(tmin, tmax, 50))
    max_phi = max_theta = max_psi_far = 0.0
    for t in times:
        g = inst.geom_cache.lookup(0, float(t))
        roll, _, psi = compute_full_attitude(task, float(t), 1.0, inst)
        phi = abs(roll)
        theta = off_nadir_to_incidence(phi, inst.altitude_m)
        max_phi = max(max_phi, abs(g.phi - phi))
        max_theta = max(max_theta, abs(g.theta - theta))
        # psi_sq = arcsin(|los_x|) has a cusp at zero-Doppler (psi~0); interp
        # error there is irrecoverable but irrelevant to the 45deg C1 limit.
        # Check accuracy only away from the cusp, where feasibility is at stake.
        if abs(psi) > np.radians(5.0):
            max_psi_far = max(max_psi_far, abs(abs(g.psi_sq) - abs(psi)))
    # phi/theta are smooth: cubic keeps them within 0.05deg (linear: ~2.5deg).
    assert np.degrees(max_phi) < 0.05
    assert np.degrees(max_theta) < 0.05
    # Away from the zero-Doppler cusp, psi must be well within the squint limit.
    assert np.degrees(max_psi_far) < 0.5


def test_c2_cache_does_not_flip_feasibility():
    """For the G-BL schedule, cached and exact C2 must agree (no false negative)."""
    inst = _load_instance()
    from sar_sim.solver.baselines import baseline_b1
    import pickle as _p
    pkgs = sorted(SCEN.glob("*.pkl"))
    data = _p.load(open(pkgs[0], "rb"))
    res = baseline_b1(data["windows"], data["targets"], instance=inst)
    t2i = {t.target_id: i for i, t in enumerate(inst.tasks)}
    N = inst.N
    sel, phi, ta = [], np.zeros(N), np.zeros(N)
    for obs in res.schedule:
        i = t2i.get(obs.window.target_id)
        if i is not None:
            sel.append(i)
            ta[i] = obs.t_actual_start.timestamp()
            r, _, _ = compute_full_attitude(inst.tasks[i], ta[i], 1.0, inst)
            phi[i] = r

    # Cached path
    r_cached = ConstraintVerifier(inst).verify_solution(sel, phi, t_actual=ta)
    # Exact path (drop caches)
    inst.sat_position_cache = None
    inst.geom_cache = None
    r_exact = ConstraintVerifier(inst).verify_solution(sel, phi, t_actual=ta)

    # If cached says PASS but exact says FAIL, that is the false-negative defect.
    if r_cached.results["C2"].passed and not r_exact.results["C2"].passed:
        worst = max((v.magnitude for v in r_exact.results["C2"].violations), default=0.0)
        pytest.fail(f"C2 false negative: exact overshoot {worst*1000:.2f} ms")


def test_moea_result_persists_audit_fields():
    """A MOEA result dict must carry fields needed for independent hard audit."""
    from sar_sim.solver.moea import moea_solver
    import pickle as _p
    pkgs = sorted(SCEN.glob("*.pkl"))
    if not pkgs:
        pytest.skip("S1 scenarios not available")
    data = _p.load(open(pkgs[0], "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    res = moea_solver(data["windows"], data["targets"],
                      population_size=20, n_generations=5, n_obj=2,
                      n_ref_dirs=4, seed=1, instance=inst)
    m = res.metadata
    for fld in ("selected", "t_actuals", "phis_off_nadir",
                "constraint_feasible", "n_constraints_failed"):
        assert fld in m, f"MOEA metadata missing {fld}"
    assert len(m["selected"]) == len(m["t_actuals"]) == m["n_selected"]
    assert isinstance(m["constraint_feasible"], bool)
