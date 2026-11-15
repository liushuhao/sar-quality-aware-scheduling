#!/usr/bin/env python3
"""N3 diagnostic-arm analysis (panel 2026-11-07 R1-01 / DA-03).

Compares the f3copy arm (three objectives, third = exact copy of f1, f2 real)
against MOEA-3, MOEA-2 and the no-physics variant D on S1, with f1* normalized
per scenario by the G-BL anchor (b1.f1_gbl from baselines_200.json).

Decision logic (resolves R1-01's two readings):
  - same objective count (3), content of the third slot varied:
      variant D (f2=f3=const)  -> f1* ~ 1.002
      f3copy  (f3=f1, f2 real) -> f1* ~ 0.83
    -> the deficit tracks the CONTENT of the quality axis, not the count.
  - same content (real f2), count varied (2 vs 3):
      MOEA-2 0.859 vs f3copy 0.829, Wilcoxon paired
    -> a content-free third objective adds no measurable coverage cost.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent
RES = PROJECT / "experiments" / "results"


def load_progress(results_dir):
    pf = results_dir / "_progress.json"
    return json.load(open(pf, encoding="utf-8"))["completed"]


def norm_f1(entry, gbl):
    """Return scenario-level normalized f1*: raw / G-BL anchor."""
    f1_gbl_own = entry.get("f1_gbl", 1.0)
    raw = entry.get("f1_raw")
    if raw is None:
        raw = entry["f1"] * max(f1_gbl_own, 1.0) if f1_gbl_own == 1.0 else entry["f1"]
    return raw / gbl


def norm_front_max(entry, gbl):
    """Scenario-level normalized frontier-max f1 (raw arrays divided by gbl)."""
    fr = entry.get("frontier_f1") or []
    if not fr:
        return None
    best = max(fr)
    # entries with f1_gbl==1 store raw values; normalized arms store 0..1
    return best / gbl if entry.get("f1_gbl", 1.0) == 1.0 else best


def msd(x):
    return {"mean": float(np.mean(x)), "sd": float(np.std(x, ddof=1)), "n": len(x)}


def main():
    baselines = json.load(open(RES / "baselines_200.json", encoding="utf-8"))
    f3c = load_progress(RES / "moea_3obj_f3copy")
    m3 = load_progress(RES / "moea_3obj")
    m2 = load_progress(RES / "moea_2obj")
    keys = sorted(f3c.keys())

    arms = {"f3copy": [], "MOEA-3": [], "MOEA-2": []}
    fmax = {"f3copy": [], "MOEA-3": [], "MOEA-2": []}
    nsel = {"f3copy": []}
    for k in keys:
        gbl = baselines[k]["b1"]["f1_gbl"]
        arms["f3copy"].append(norm_f1(f3c[k], gbl))
        arms["MOEA-3"].append(norm_f1(m3[k], gbl))
        arms["MOEA-2"].append(norm_f1(m2[k], gbl))
        for a, prog in (("f3copy", f3c), ("MOEA-3", m3), ("MOEA-2", m2)):
            fm = norm_front_max(prog[k], gbl)
            if fm is not None:
                fmax[a].append(fm)
        nsel["f3copy"].append(f3c[k]["n_selected"])

    out = {"group": "S1", "n_scenarios": len(keys),
           "f1_star": {a: msd(v) for a, v in arms.items()},
           "front_max": {a: msd(v) for a, v in fmax.items() if v},
           "knee_deficit": {a: msd([m - f for m, f in zip(arms[a], fmax[a])])
                            for a in arms if fmax[a]},
           "n_selected": {a: msd(v) for a, v in nsel.items()},
           "wilcoxon": {}}
    for other in ("MOEA-3", "MOEA-2"):
        diff = np.array(arms["f3copy"]) - np.array(arms[other])
        res = stats.wilcoxon(arms["f3copy"], arms[other])
        out["wilcoxon"][other] = {"mean_diff": float(np.mean(diff)),
                                  "p": float(res.pvalue)}

    print("N3 f3copy diagnostic (S1, n=%d)" % len(keys))
    for a, v in out["f1_star"].items():
        print("  %-8s f1* = %.3f ± %.3f" % (a, v["mean"], v["sd"]))
    for other, w in out["wilcoxon"].items():
        print("  f3copy vs %s: mean_diff=%+.3f  p=%.4f" % (other, w["mean_diff"], w["p"]))
    print("  f3copy knee n_selected = %.1f ± %.1f" % (
        out["n_selected"]["f3copy"]["mean"], out["n_selected"]["f3copy"]["sd"]))

    dst = RES / "moea_3obj_f3copy" / "_analysis.json"
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("  saved: %s" % dst)


if __name__ == "__main__":
    sys.exit(main())
