#!/usr/bin/env python3
"""Validate the f3 proxy's ordering-preservation and conservatism (§3.2).

Panel 20261031 root-cause follow-up (R2-02 branch 1): the manuscript reads f3
= mean(cos^3 xi) as an ordering index and discloses that standard NESZ
expressions add a sin(theta) ground-reference factor the index suppresses.
This script validates two claims on the sparse-regime class (S1):

1. Ordering preservation (by construction, verified numerically): theta =
   arcsin((R_e+H)/R_e * sin(xi)) is monotone in xi, so cos^3(xi)/sin(theta)
   and cos^3(xi) are both decreasing in xi and rank geometries identically.
2. Conservatism of the proxy reading: recomputing the MOEA-3 vs G-BL class-
   means comparison with the retained factor ENLARGES the gain (proxy +40.4%
   -> true +94.3%, ratio of class means), because the greedy baseline's
   earliest-feasible placements sit at higher incidence where the suppressed
   factor penalizes more.

G-BL schedules are regenerated (deterministic greedy) and bit-checked against
the stored baselines_200.json f3 values. Post-hoc evaluation of the already-
selected schedules; the optimizer itself is untouched.

Output: experiments/results/true_nesz_factor_gain.json
"""
import json, math, pickle, sys
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.solver.baselines import baseline_b1

PAPER = _PROJ / "papers" / "single-sat-quality"
RESULTS = PAPER / "experiments" / "results"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
GROUP = "S1"


def proxy_factor(g):
    return math.cos(g.phi) ** 3


def true_factor(g):
    sg = math.sin(g.theta)
    if sg <= 1e-9:
        return 0.0
    return math.cos(g.phi) ** 3 / sg


class Scene:
    def __init__(self, cls, pkl_name):
        with open(PAPER / "experiments" / "scenarios" / cls / pkl_name, "rb") as f:
            self.data = pickle.load(f)
        self.inst = build_agile_instance_from_scenario(
            self.data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
        precompute_geometry(self.inst, step_s=10.0)


def gbl_schedule(sc):
    gbl = baseline_b1(sc.data["windows"], sc.data["targets"],
                      max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME,
                      geom_cache=sc.inst.geom_cache, instance=sc.inst)
    tgt_idx = {t.target_id: i for i, t in enumerate(sc.inst.tasks)}
    sel, ta = [], []
    for obs in gbl.schedule:
        i = tgt_idx.get(obs.window.target_id)
        if i is not None:
            sel.append(i)
            ta.append(obs.t_actual_start.timestamp())
    return sel, ta


def mean_quality(sc, sel, ta, quality):
    return float(np.mean([quality(sc.inst.geom_cache.lookup(int(i), float(t)))
                          for i, t in zip(sel, ta)]))


def main():
    m3 = json.loads((RESULTS / "moea_3obj" / "_progress.json").read_text(encoding="utf-8"))["completed"]
    bl = json.loads((RESULTS / "baselines_200.json").read_text(encoding="utf-8"))
    keys = sorted(k for k in m3 if k.startswith(GROUP + "/") and k in bl)

    m3_p, gbl_p, m3_t, gbl_t = [], [], [], []
    bitmatch = 0
    for k in keys:
        cls, pkl_name = k.split("/")[0], k.split("/")[1]
        sc = Scene(cls, pkl_name)
        sel_m, ta_m = m3[k]["selected"], m3[k]["t_actuals"]
        sel_g, ta_g = gbl_schedule(sc)
        regen = mean_quality(sc, sel_g, ta_g, proxy_factor)
        stored = bl[k]["b1"]["f3"]
        assert abs(regen - stored) < 1e-9, f"G-BL regen mismatch {k}: {regen} vs {stored}"
        bitmatch += 1
        m3_p.append(mean_quality(sc, sel_m, ta_m, proxy_factor))
        gbl_p.append(mean_quality(sc, sel_g, ta_g, proxy_factor))
        m3_t.append(mean_quality(sc, sel_m, ta_m, true_factor))
        gbl_t.append(mean_quality(sc, sel_g, ta_g, true_factor))

    out = {
        "what": "f3 proxy conservatism validation (panel 20261031 root-cause closure)",
        "group": GROUP,
        "n_scenarios": len(keys),
        "gbl_regen_bitmatch": bitmatch,
        "proxy_gain_rom": float(np.mean(m3_p) / np.mean(gbl_p) - 1),
        "true_gain_rom": float(np.mean(m3_t) / np.mean(gbl_t) - 1),
        "calibers": {"proxy": "mean cos^3(xi)  (paper f3)",
                     "true": "mean cos^3(xi)/sin(theta_g)  (retained ground-reference factor)",
                     "gain": "ratio of class means (same caliber as the +40% headline)"},
    }
    dest = RESULTS / "true_nesz_factor_gain.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"proxy gain (rom): {out['proxy_gain_rom'] * 100:+.1f}%")
    print(f"true  gain (rom): {out['true_gain_rom'] * 100:+.1f}%")
    print(f"G-BL regen bit-match: {bitmatch}/{len(keys)}")
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
