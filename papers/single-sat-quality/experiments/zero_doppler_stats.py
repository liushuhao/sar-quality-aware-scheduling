#!/usr/bin/env python3
"""Compute zero-Doppler crossing statistics from scenario pkls (UC-1 provenance).

Reproduces the Chinese paper §5.2 numbers: per-class fraction of visibility
windows whose 10s-grid min |psi_sq| crosses zero-Doppler, and median of the
per-window min |psi_sq|. Output: experiments/results/zero_doppler_stats.json

Paper claims (small-paper-ijae-zh.tex §5.2, L463-465):
  S1--S4: 15.1%/17.2%/14.9%/14.9%, 45,345 windows total,
  median min|psi_sq| approx 27--30 deg.
"""
import pickle, math, sys, json
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

STEP_S = 10.0
EPS_CROSS = 1e-6  # radians; |psi_sq| below this counts as crossing zero-Doppler
GROUPS = ["S1", "S2", "S3", "S4"]
SCEN_DIR = Path(__file__).resolve().parent / "scenarios"
OUT = Path(__file__).resolve().parent / "results" / "zero_doppler_stats.json"


def main():
    total_windows = 0
    per_class = {}
    for g in GROUPS:
        n_cross = 0
        n_w = 0
        mins = []
        for pkl in sorted((SCEN_DIR / g).glob("*.pkl")):
            with open(pkl, "rb") as f:
                data = pickle.load(f)
            inst = build_agile_instance_from_scenario(data, max_slew_rate=0.0524, settle_time=5.0)
            precompute_geometry(inst, step_s=STEP_S)
            for i, task in enumerate(inst.tasks):
                arr = inst.geom_cache.cache[i]
                for ws, we in task.window_times:
                    n_w += 1
                    mask = (arr[:, 0] >= ws) & (arr[:, 0] <= we)
                    if mask.sum() >= 2:
                        min_psi = float(np.abs(arr[mask, 2]).min())
                    else:
                        # Coarse grid: sample window at 10s resolution.
                        pts = max(2, int((we - ws) / STEP_S) + 1)
                        vals = [abs(inst.geom_cache.lookup(i, tt).psi_sq)
                                for tt in np.linspace(ws, we, pts)]
                        min_psi = min(vals)
                    mins.append(min_psi)
                    if min_psi < EPS_CROSS:
                        n_cross += 1
        per_class[g] = {
            "windows": n_w,
            "zero_doppler_crossing_frac": n_cross / n_w,
            "median_min_psi_deg": float(np.median(mins) * 180.0 / math.pi),
        }
        total_windows += n_w
        print(f"{g}: windows={n_w} "
              f"crossing={per_class[g]['zero_doppler_crossing_frac']*100:.1f}% "
              f"median_min_psi={per_class[g]['median_min_psi_deg']:.0f} deg")

    overall = {
        "total_windows": total_windows,
        "per_class": per_class,
        "step_s": STEP_S,
        "eps_cross_rad": EPS_CROSS,
        "note": "min |psi_sq| evaluated on the 10s geometry grid within each "
                "visibility window; crossing = min below 1e-6 rad.",
    }
    OUT.write_text(json.dumps(overall, indent=2), encoding="utf-8")
    print(f"TOTAL windows: {total_windows}")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
