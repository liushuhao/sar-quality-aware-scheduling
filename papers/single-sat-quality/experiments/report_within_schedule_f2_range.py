#!/usr/bin/env python3
"""DA-13 (panel 20261103): pooled within-schedule f2 component range.

Recomputes, from the main-run result sets (same as Table 1), the pooled
min/max of the per-task f2 component sqrt(max(cos^2 psi - cos^2 phi, 0))
over all scheduled (selected, t_actual) pairs in S1-S4, to adjudicate the
printed "pooled range 0.65" against the HV normalization bounds f2 in
[0.11, 0.56].

Output: experiments/results/within_schedule_f2_range.json
"""
import json, os, pickle, sys
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "within_schedule_f2_range.json"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0


def main():
    comp = json.load(open(RESULTS_DIR / "moea_3obj/_progress.json"))["completed"]
    all_f2 = []
    per_group = {}
    for group in ("S1", "S2", "S3", "S4"):
        gvals = []
        for key, v in sorted(comp.items()):
            if not key.startswith(group + "/"):
                continue
            pkl = SCENARIOS_DIR / group / key.split("/")[1]
            if not pkl.exists():
                continue
            sel, tats = v.get("selected", []), v.get("t_actuals", [])
            if not sel or len(sel) != len(tats):
                continue
            data = pickle.load(open(pkl, "rb"))
            inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
            precompute_geometry(inst, step_s=10.0)
            for i, t in zip(sel, tats):
                g = inst.geom_cache.lookup(int(i), float(t))
                val = g.cos_psi ** 2 - np.cos(g.phi) ** 2
                if val > 0:
                    gvals.append(float(np.sqrt(val)))
        per_group[group] = {"n": len(gvals), "min": float(np.min(gvals)),
                            "max": float(np.max(gvals))}
        all_f2.extend(gvals)
        print(f"{group}: n={len(gvals)} min={np.min(gvals):.4f} max={np.max(gvals):.4f}", flush=True)
    out = {"caliber": "per-task f2 component sqrt(max(cos2psi-cos2phi,0)) at scheduled (task,time) pairs, MOEA-3 main run S1-S4",
           "groups": per_group,
           "pooled_min": float(np.min(all_f2)), "pooled_max": float(np.max(all_f2)),
           "pooled_range": float(np.max(all_f2) - np.min(all_f2))}
    tmp = OUT_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, OUT_PATH)
    print(f"pooled range = {out['pooled_range']:.4f} -> {OUT_PATH}")


if __name__ == "__main__":
    main()
