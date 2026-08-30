#!/usr/bin/env python3
"""Panel-20260830 N1/N8/N17 corrected envelope statistics under PRODUCTION
geometry (build_agile_instance_from_scenario) and the current (post-RDR-066)
objective caliber:
  f2 = sqrt(cos^2 psi_sq - cos^2 phi)
  f3 = cos^3(phi)

Reports per group:
  - corr(f2,f3) over all window grid points and within |psi|<=45 deg
    (window generation already filters; the split mirrors the paper's
    visibility-envelope sampling frame)
  - max |psi_sq| reached within window intervals (effective envelope)
  - within-window psi sweep percentiles, window width percentiles
  - 30 s psi drift percentiles
  - psi p95 over all grid points
5 scenarios per density class, 10 s grid (same frame as r_visible_envelope).
"""
import pickle, sys, json
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[1]
# Pickle source: first-party scenario files from this repo's generator.
sys.path.insert(0, str(_PROJ.parents[1] / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SCEN = _PROJ / "experiments" / "scenarios"
SLEW, SETTLE = 0.0524, 5.0
STEP = 10.0
out = {}

for g in ["S1", "S2", "S3", "S4"]:
    widths, sweeps, drift30, psi_pts = [], [], [], []
    f2_all, f3_all, f2_c, f3_c = [], [], [], []
    for p in sorted((SCEN / g).glob("*.pkl"))[:5]:
        data = pickle.load(open(p, "rb"))
        inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW, settle_time=SETTLE)
        precompute_geometry(inst, step_s=STEP)
        for i, task in enumerate(inst.tasks):
            for w in task.windows:
                ws, we = w.t_start.timestamp(), w.t_end.timestamp()
                psis, f2s, f3s = [], [], []
                t = ws
                while t <= we:
                    try:
                        gm = inst.geom_cache.lookup(i, t)
                        psi = abs(gm.psi_sq)
                        phi = abs(gm.phi)
                        f2 = float(np.sqrt(max(gm.cos_psi**2 - np.cos(phi)**2, 0.0)))
                        f3 = float(np.cos(phi)**3)
                        psis.append(np.degrees(psi))
                        f2s.append(f2); f3s.append(f3)
                    except Exception:
                        pass
                    t += STEP
                if len(psis) >= 2:
                    widths.append((we - ws) / 60.0)
                    sweeps.append(max(psis) - min(psis))
                    for k in range(len(psis) - 3):
                        drift30.append(abs(psis[k + 3] - psis[k]))
                    psi_pts += psis
                    f2_all += f2s; f3_all += f3s
                    for ps, a, b in zip(psis, f2s, f3s):
                        if ps <= 45.0:
                            f2_c.append(a); f3_c.append(b)
    psi_pts = np.array(psi_pts)
    out[g] = {
        "r_all": round(float(np.corrcoef(f2_all, f3_all)[0, 1]), 4),
        "r_psi_le_45": round(float(np.corrcoef(f2_c, f3_c)[0, 1]), 4),
        "n_points_all": len(f2_all), "n_points_le45": len(f2_c),
        "psi_max": round(float(psi_pts.max()), 2),
        "psi_p95": round(float(np.percentile(psi_pts, 95)), 2),
        "sweep_med": round(float(np.median(sweeps)), 2),
        "sweep_p95": round(float(np.percentile(sweeps, 95)), 2),
        "width_med_min": round(float(np.median(widths)), 2),
        "drift30_med": round(float(np.median(drift30)), 2),
        "drift30_p95": round(float(np.percentile(drift30, 95)), 2),
    }
    print(g, out[g], flush=True)

json.dump(out, open(_PROJ / "experiments" / "results" / "envelope_caliber2026.json", "w"), indent=2)
print("Wrote envelope_caliber2026.json")
