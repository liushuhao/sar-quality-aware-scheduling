#!/usr/bin/env python3
"""Recompute scale-sensitivity table + N50 from post-fix MOEA-2 rerun data.

Outputs (stdout, tab-separated, ready to paste into the paper):
  per-class f1* (MOEA-2), f2 gain vs G-BL, fraction f1*<0.95, N50 logistic fit.

Paper table shape (tab:scale-sensitivity):
  Class | N | f1* (MOEA-2) | f2 improvement | % f1*<0.95
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
from collections import defaultdict

PAPER = Path(__file__).resolve().parent.parent
RESULTS = PAPER / "experiments" / "results"

N_BY_CLASS = {"S1": 20, "S2": 100, "S7": 150, "S8": 200, "S3": 300, "S4": 500}
CLASS_ORDER = ["S1", "S2", "S7", "S8", "S3", "S4"]

moea2 = json.load(open(RESULTS / "moea_2obj" / "_progress.json", encoding="utf-8"))["completed"]
bl = json.load(open(RESULTS / "baselines_200.json", encoding="utf-8"))
bl78 = json.load(open(RESULTS / "baselines_S7S8.json", encoding="utf-8"))

by_class = defaultdict(list)
for key, v in moea2.items():
    cls = key.split("/")[0]
    by_class[cls].append(v)

bl_all = {**bl, **bl78}

print(f"{'Class':<6}{'N':>5}{'f1*':>10}{'f2 gain':>10}{'% f1*<0.95':>12}")
rows = []
for cls in CLASS_ORDER:
    if cls not in by_class or not by_class[cls]:
        print(f"{cls}: no MOEA-2 data yet", file=sys.stderr)
        continue
    vals = by_class[cls]
    f1s = np.array([v["f1"] for v in vals])
    f2m = np.mean([v["f2"] for v in vals])
    b1 = [bl_all[k]["b1"] for k in bl_all if k.startswith(cls)]
    f2b = np.mean([e["f2"] for e in b1])
    f1_mean, f1_sd = f1s.mean(), f1s.std(ddof=1)
    gain = (f2m / f2b - 1) * 100
    frac = (f1s < 0.95).mean() * 100
    rows.append((cls, f1_mean, f1_sd))
    print(f"{cls:<6}{N_BY_CLASS[cls]:>5}{f1_mean:>8.3f}±{f1_sd:.2f}{gain:>9.1f}%{frac:>11.0f}%")

if len(rows) >= 4:
    xs = np.array([N_BY_CLASS[c] for c, _, _ in rows])
    fracs = np.array([(np.array([v["f1"] for v in by_class[c]]) < 0.95).mean() for c, _, _ in rows])
    try:
        def logistic(n, n50, k):
            return 1.0 / (1.0 + np.exp(-k * (n - n50)))
        popt, _ = curve_fit(logistic, xs, fracs, p0=[140, 0.01], maxfev=20000)
        print(f"\nN50 ≈ {popt[0]:.0f} targets (k={popt[1]:.4f})", file=sys.stderr)
    except Exception as e:
        print(f"\nN50 fit failed: {e}", file=sys.stderr)
