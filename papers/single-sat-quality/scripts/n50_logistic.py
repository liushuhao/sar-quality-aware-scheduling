#!/usr/bin/env python3
"""N50 logistic regression: midpoint of the deficit-proportion transition.

Reproduces the N50 claim in section 6.5 of small-paper-ijae.tex.
Fits p(f1* < 0.95 | N) = sigmoid(a + b*N) to per-scenario MOEA-2 results,
computes N50 = -a/b, and bootstraps a 95% CI (1000 resamples, seed=42).

Data source: experiments/results/moea_2obj/_progress.json (200 scenarios,
4 density classes S1-S4 with N = 20, 100, 300, 500).
Output:     experiments/results/n50_logistic.json
"""
import json
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit

PROJ = Path(__file__).resolve().parent.parent
PROG = PROJ / "experiments" / "results" / "moea_2obj" / "_progress.json"
OUT = PROJ / "experiments" / "results" / "n50_logistic.json"

DEFICIT_THRESHOLD = 0.95
N_BOOTSTRAP = 1000
BOOT_SEED = 42
GROUP_N = {"S1": 20, "S2": 100, "S3": 300, "S4": 500}


def load_data():
    prog = json.load(open(PROG, encoding="utf-8"))
    comp = prog.get("completed", prog)
    N_arr, y_arr = [], []
    for key, val in comp.items():
        if not isinstance(val, dict) or "f1" not in val:
            continue
        grp = key.split("/")[0]
        if grp not in GROUP_N:
            continue
        N_arr.append(GROUP_N[grp])
        y_arr.append(1 if float(val["f1"]) < DEFICIT_THRESHOLD else 0)
    return np.array(N_arr, dtype=float), np.array(y_arr, dtype=float)


def sigmoid(x, a, b):
    return 1.0 / (1.0 + np.exp(-(a + b * x)))


def fit(N, y):
    popt, _ = curve_fit(sigmoid, N, y, p0=[1.0, -0.01], maxfev=10000)
    return popt


def main():
    N, y = load_data()
    print(f"Loaded {len(N)} scenarios")
    for g, n in GROUP_N.items():
        m = N == n
        if m.sum():
            print(f"  {g} (N={n}): deficit {int(y[m].sum())}/{int(m.sum())} "
                  f"= {100*y[m].mean():.0f}%")

    a, b = fit(N, y)
    N50 = -a / b
    print(f"\nFull-data fit: alpha={a:.4f}, beta={b:.4f}, N50={N50:.1f}")

    rng = np.random.RandomState(BOOT_SEED)
    idx = np.arange(len(N))
    N50s = []
    for _ in range(N_BOOTSTRAP):
        s = rng.choice(idx, len(idx), replace=True)
        try:
            aa, bb = fit(N[s], y[s])
            if bb != 0:
                N50s.append(-aa / bb)
        except Exception:
            pass
    N50s = np.array(N50s)
    ci = np.percentile(N50s, [2.5, 97.5])
    print(f"95% CI: [{ci[0]:.0f}, {ci[1]:.0f}] (n_boot={len(N50s)})")

    out = {
        "alpha": float(a), "beta": float(b), "N50": float(N50),
        "ci_low": float(ci[0]), "ci_high": float(ci[1]),
        "n_bootstrap": int(len(N50s)), "n_scenarios": int(len(N)),
        "deficit_threshold": DEFICIT_THRESHOLD, "boot_seed": BOOT_SEED,
        "group_N": GROUP_N,
    }
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
