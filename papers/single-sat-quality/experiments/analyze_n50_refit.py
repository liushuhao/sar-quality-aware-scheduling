#!/usr/bin/env python3
"""N5 refit (panel 2026-11-07 R1-02 / R2-04): the logistic N50 currently fits
the pooled bound/unbound mix, reporting two mechanisms as one boundary.

This script splits the 200-scenario library by the paper's own §3.3
classification — C3-C4-bound = the G-BL anchor selects exactly the 200-task
ceiling; C2-limited (unbound) = everything else — and refits the deficit
logistic (f1* < 0.95 vs N, MOEA-2, same protocol as scripts/n50_logistic.py:
sigmoid, curve_fit, 1000-resample bootstrap CI, seed 42) on each subset
separately, plus the pooled reference.

Output: experiments/results/n50_refit.json — consumed by the 批B ring when
the §6.3/§7.4/abstract sentences are written; scripts/n50_logistic.json
(R112 single source for gen_all_figures) is intentionally NOT touched.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

PROJ = Path(__file__).resolve().parent.parent
RES = PROJ / "experiments" / "results"
OUT = RES / "n50_refit.json"

DEFICIT_THRESHOLD = 0.95
N_BOOTSTRAP = 1000
BOOT_SEED = 42
GROUP_N = {"S1": 20, "S2": 100, "S7": 150, "S8": 200, "S3": 300, "S4": 500}


def sigmoid(x, a, b):
    return 1.0 / (1.0 + np.exp(-(a + b * x)))


def fit_n50(N, y, rng):
    if len(N) < 4 or len(set(y)) < 2:
        return None
    try:
        popt, _ = curve_fit(sigmoid, N, y, p0=[1.0, -0.01], maxfev=10000)
    except RuntimeError:
        return None
    a, b = popt
    if b >= 0:
        return None
    n50 = -a / b
    boots = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(N), len(N))
        try:
            p, _ = curve_fit(sigmoid, N[idx], y[idx], p0=[a, b], maxfev=10000)
            if p[1] < 0:
                boots.append(-p[0] / p[1])
        except RuntimeError:
            continue
    if len(boots) < 100:
        return {"n50": float(n50), "ci": None, "n_boot_ok": len(boots)}
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"n50": float(n50), "ci": [float(lo), float(hi)],
            "n_boot_ok": len(boots)}


def main():
    baselines = json.load(open(RES / "baselines_200.json", encoding="utf-8"))
    prog = json.load(open(RES / "moea_2obj" / "_progress.json", encoding="utf-8"))["completed"]

    rows = []
    for key, b in baselines.items():
        grp = key.split("/")[0]
        if grp not in GROUP_N or key not in prog:
            continue
        bound = int(b["b1"]["n_selected"]) == 200
        deficit = 1 if float(prog[key]["f1"]) < DEFICIT_THRESHOLD else 0
        rows.append((GROUP_N[grp], bound, deficit))

    N_all = np.array([r[0] for r in rows], dtype=float)
    y_all = np.array([r[2] for r in rows], dtype=float)
    bound_flags = np.array([r[1] for r in rows], dtype=bool)

    rng = np.random.default_rng(BOOT_SEED)
    out = {"threshold": DEFICIT_THRESHOLD, "n_scenarios": len(rows),
           "fits": {}}
    subsets = {
        "pooled": (np.ones(len(rows), dtype=bool), "all scenarios (existing §6.3 fit reference)"),
        "unbound_c2_limited": (~bound_flags, "cap-free subset (R1-02 primary)"),
        "bound_c3_c4": (bound_flags, "ceiling-bound subset (reported separately per R2-04)"),
    }
    for name, (mask, desc) in subsets.items():
        N, y = N_all[mask], y_all[mask]
        entry = {"desc": desc, "n": int(mask.sum()),
                 "deficit_rate": float(y.mean()) if len(y) else None,
                 "by_group": {}}
        for g, n in GROUP_N.items():
            m = N == n
            if m.sum():
                entry["by_group"][g] = {
                    "N": n, "n": int(m.sum()),
                    "deficit": f"{int(y[m].sum())}/{int(m.sum())}"}
        fitres = fit_n50(N, y, np.random.default_rng(BOOT_SEED))
        entry["fit"] = fitres
        out["fits"][name] = entry
        if fitres:
            ci = fitres["ci"]
            print("%-20s n=%3d  N50=%.1f  CI=%s  (boot ok %s)" % (
                name, entry["n"], fitres["n50"],
                "[%s, %s]" % tuple(round(v, 1) for v in ci) if ci else "n/a",
                fitres["n_boot_ok"]))
        else:
            print("%-20s n=%3d  fit degenerate" % (name, entry["n"]))
        for g, d in entry["by_group"].items():
            print("    %s N=%-3d deficit %s" % (g, d["N"], d["deficit"]))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("saved: %s" % OUT)


if __name__ == "__main__":
    main()
