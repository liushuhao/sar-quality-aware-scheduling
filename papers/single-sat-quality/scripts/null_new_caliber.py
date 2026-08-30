#!/usr/bin/env python3
"""Panel-20260830: null correlation under the CURRENT objective caliber
(f2 = sin(gamma)*cos(psi_sq), f3 = cos^3(phi) with cos(phi)=cos(gamma)cos(psi)),
production geometry (build_agile_instance_from_scenario).

Three baselines:
  1. MC uniform independent angles: gamma ~ U[16,41] deg (off-nadir box
     corresponding to incidence 18-47 deg), psi ~ U[-45,45] deg.
  2. MC uniform narrow psi ([-25,25]) for sensitivity.
  3. Empirical-marginal shuffle: window-grid points, psi shuffled relative
     to gamma within group (preserves observed marginals, breaks coupling).

Pickle source: first-party scenario files from this repo's generator.
"""
import pickle, sys, json
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJ.parents[1] / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SCEN = _PROJ / "experiments" / "scenarios"
SLEW, SETTLE, STEP = 0.0524, 5.0, 10.0


def f2f3(gamma, psi, phi):
    f2 = np.sin(gamma) * np.cos(psi)
    f3 = np.cos(phi) ** 3
    return f2, f3


rng = np.random.default_rng(20260830)
N = 2_000_000
g = rng.uniform(np.radians(16), np.radians(41), N)
for tag, lo, hi in [("psi45", -45, 45), ("psi25", -25, 25), ("psi0", 0, 0)]:
    if hi == 0:
        p = np.zeros(N)
    else:
        p = rng.uniform(np.radians(lo), np.radians(hi), N)
    phi = np.arccos(np.cos(g) * np.cos(p))
    a, b = f2f3(g, p, phi)
    print(f"MC null gamma~U[16,41] psi~U[{lo},{hi}]: r = {np.corrcoef(a, b)[0,1]:+.3f}", flush=True)

out = {}
for grp in ["S1", "S2", "S3", "S4"]:
    gammas, psis, phis = [], [], []
    for pk in sorted((SCEN / grp).glob("*.pkl"))[:5]:
        data = pickle.load(open(pk, "rb"))
        inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE)
        precompute_geometry(inst, step_s=STEP)
        for i, task in enumerate(inst.tasks):
            for w in task.windows:
                t = w.t_start.timestamp()
                while t <= w.t_end.timestamp():
                    try:
                        gm = inst.geom_cache.lookup(i, t)
                        ps = abs(gm.psi_sq)
                        ph = abs(gm.phi)
                        ga = np.arccos(np.clip(np.cos(ph) / np.cos(ps), 0, 1))
                        gammas.append(ga); psis.append(ps); phis.append(ph)
                    except Exception:
                        pass
                    t += STEP
    gammas, psis, phis = np.array(gammas), np.array(psis), np.array(phis)
    f2, f3 = f2f3(gammas, psis, phis)
    r_obs = np.corrcoef(f2, f3)[0, 1]
    rs = []
    for _ in range(20):
        idx = rng.permutation(len(psis))
        phi_s = np.arccos(np.cos(gammas) * np.cos(psis[idx]))
        a, b = f2f3(gammas, psis[idx], phi_s)
        rs.append(np.corrcoef(a, b)[0, 1])
    out[grp] = {"r_envelope": round(float(r_obs), 3),
                "r_shuffle_null_mean": round(float(np.mean(rs)), 3),
                "r_shuffle_null_p025": round(float(np.percentile(rs, 2.5)), 3),
                "r_shuffle_null_p975": round(float(np.percentile(rs, 97.5)), 3),
                "gamma_deg_p50": round(float(np.degrees(np.median(gammas))), 1),
                "psi_deg_p50": round(float(np.degrees(np.median(psis))), 1)}
    print(grp, out[grp], flush=True)

json.dump(out, open(_PROJ / "experiments" / "results" / "null_new_caliber2026.json", "w"), indent=2)
print("Wrote null_new_caliber2026.json")
