#!/usr/bin/env python3
"""Panel-20260830 offline statistics from persisted progress JSONs.

Outputs experiments/results/panel20260830_extra.json:
  1. Selector sensitivity (S2): for MOEA-3/MOEA-2 frontiers, re-select under
     best-f1 / best-f2 / best-f3 / knee rules per scenario; class means.
  2. Tail risk (S4): 10th percentile across scenarios of knee f2/f3 per group.
  3. Phenomenon-2 Cliff's delta both formulas (paired sign vs classic),
     per group (N11).
  4. f3 margins under knee selectors (asymmetric vs unified U3/U2) — N13.
"""
import json
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
R = PROJECT / "experiments" / "results"
GROUPS = ["S1", "S2", "S3", "S4"]

m2 = json.load(open(R / "moea_2obj/_progress.json"))["completed"]
m3 = json.load(open(R / "moea_3obj/_progress.json"))["completed"]
bl = json.load(open(R / "baselines_200.json"))


def group_keys(g):
    return sorted(k for k in m3 if k.startswith(g + "/") and k in m2)


def pick(fronts, rule):
    f1, f2, f3 = fronts
    if rule == "best-f1":
        i = int(np.argmax(f1))
    elif rule == "best-f2":
        i = int(np.argmax(f2))
    elif rule == "best-f3":
        i = int(np.argmax(f3))
    elif rule in ("knee3", "knee2"):
        def nm(v):
            rng = v.max() - v.min()
            return (v - v.min()) / rng if rng else np.zeros_like(v)
        s = nm(f1) + nm(f2)
        if rule == "knee3":
            s = s + nm(f3)
        i = int(np.argmax(s))
    return float(f1[i]), float(f2[i]), float(f3[i])


def classic_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return float((gt - lt) / (len(a) * len(b)))


out = {"selector_sensitivity": {}, "tail_risk": {}, "cliff_delta": {}, "f3_margins": {}}

for g in GROUPS:
    ks = group_keys(g)
    ss = {}
    for solver, coll in [("MOEA-3", m3), ("MOEA-2", m2)]:
        for rule in ["knee3", "knee2", "best-f1", "best-f2", "best-f3"]:
            vals = {"f1": [], "f2": [], "f3": []}
            for k in ks:
                e = coll[k]
                fronts = (np.array(e["frontier_f1"]), np.array(e["frontier_f2"]),
                          np.array(e["frontier_f3"]))
                r = pick(fronts, rule)
                vals["f1"].append(r[0]); vals["f2"].append(r[1]); vals["f3"].append(r[2])
            ss[f"{solver}_{rule}"] = {o: round(float(np.mean(v)), 4) for o, v in vals.items()}
    out["selector_sensitivity"][g] = ss

    tr = {}
    for obj in ["f2", "f3"]:
        v = np.array([m3[k][obj] for k in ks])
        tr[f"MOEA-3_{obj}"] = {"p10": round(float(np.percentile(v, 10)), 4),
                               "mean": round(float(v.mean()), 4)}
        vg = np.array([bl[k]["b1"][obj] for k in ks if k in bl and "b1" in bl[k]])
        tr[f"G-BL_{obj}"] = {"p10": round(float(np.percentile(vg, 10)), 4),
                             "mean": round(float(vg.mean()), 4)}
    out["tail_risk"][g] = tr

    cd = {}
    for obj in ["f1", "f2", "f3"]:
        a = np.array([m3[k][obj] for k in ks])
        b = np.array([m2[k][obj] for k in ks])
        d = a - b
        cd[obj] = {
            "classic": round(classic_delta(a, b), 3),
            "paired_sign": round(float(((d > 0).sum() - (d < 0).sum()) / len(d)), 3),
        }
    out["cliff_delta"][g] = cd

    mg = {}
    for rule in ["knee3", "knee2"]:
        a = np.array([pick((np.array(m3[k]["frontier_f1"]), np.array(m3[k]["frontier_f2"]),
                            np.array(m3[k]["frontier_f3"])), rule)[2] for k in ks])
        b = np.array([pick((np.array(m2[k]["frontier_f1"]), np.array(m2[k]["frontier_f2"]),
                            np.array(m2[k]["frontier_f3"])), rule)[2] for k in ks])
        mg[rule] = {"m3_mean": round(float(a.mean()), 4), "m2_mean": round(float(b.mean()), 4),
                    "margin_pct": round(float((a.mean() / b.mean() - 1) * 100), 2)}
    asym_a = np.array([m3[k]["f3"] for k in ks])
    asym_b = np.array([m2[k]["f3"] for k in ks])
    mg["asymmetric_paper"] = {"m3_mean": round(float(asym_a.mean()), 4),
                              "m2_mean": round(float(asym_b.mean()), 4),
                              "margin_pct": round(float((asym_a.mean() / asym_b.mean() - 1) * 100), 2)}
    out["f3_margins"][g] = mg

json.dump(out, open(R / "panel20260830_extra.json", "w", encoding="utf-8"), indent=2)

for g in GROUPS:
    print(f"== {g} ==")
    print("  knee3 M3:", out["selector_sensitivity"][g]["MOEA-3_knee3"],
          " best-f1 M3:", out["selector_sensitivity"][g]["MOEA-3_best-f1"])
    print("  cliff M3vsM2:", out["cliff_delta"][g])
    print("  f3 margins:", out["f3_margins"][g])
    print("  tail:", out["tail_risk"][g])
print("Wrote", R / "panel20260830_extra.json")
