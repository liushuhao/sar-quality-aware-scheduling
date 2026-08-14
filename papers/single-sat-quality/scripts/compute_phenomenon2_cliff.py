#!/usr/bin/env python3
"""§6.4 Phenomenon 2: per-group f2/f3 Cliff's delta, MOEA-3 vs MOEA-2.

Reproduces the per-group deltas cited in §6.4 (-0.945/-0.183 for f2;
+0.993/+0.310/+0.114/+0.126 for f3) from the FINAL corrected snapshots.
Standard Cliff's delta: (n_x>y - n_x<y) / (n_x * n_y), using the knee-solution
f2/f3 per scenario. Also prints pooled deltas to cross-check against
statistical_results.json.
"""
import json, sys, subprocess
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
PROJECT = _PROJ / "papers" / "single-sat-quality"
RESULTS_DIR = PROJECT / "experiments" / "results"

GROUPS = ["S1", "S2", "S3", "S4"]
OBJS = ["f1", "f2", "f3"]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except Exception:
        return "unknown"


def load(snap_name):
    d = json.load(open(RESULTS_DIR / snap_name))
    return d.get("completed", {})


def cliff_delta(a, b):
    # a, b equal-length arrays of knee f for MOEA-3, MOEA-2 per scenario
    # PAIRED comparison (same scenario set): delta = (gt - lt) / n
    # (same basis as statistical_analysis.py line 309)
    n = len(a)
    if n == 0:
        return None
    diff = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    gt = (diff > 0).sum()
    lt = (diff < 0).sum()
    return (gt - lt) / n


def main():
    m3 = load("moea_3obj/_progress.json")
    m2 = load("moea_2obj/_progress.json")
    out = {"git_commit": _git_commit(), "per_group": {}, "pooled": {}}

    for group in GROUPS:
        keys = sorted(k for k in m3 if k.startswith(group + "/"))
        g_out = {}
        for obj in OBJS:
            a = np.array([m3[k][obj] for k in keys if k in m2])
            b = np.array([m2[k][obj] for k in keys if k in m2])
            d = cliff_delta(a, b)
            g_out[obj] = None if d is None else round(d, 3)
        out["per_group"][group] = g_out
        print(f"{group}: f2={g_out['f2']} f3={g_out['f3']}", flush=True)

    for obj in OBJS:
        a = np.array([m3[k][obj] for k in m3 if k in m2])
        b = np.array([m2[k][obj] for k in m3 if k in m2])
        d = cliff_delta(a, b)
        out["pooled"][obj] = None if d is None else round(d, 3)
        print(f"pooled {obj}: {out['pooled'][obj]}", flush=True)

    json.dump(out, open(RESULTS_DIR / "phenomenon2_cliff.json", "w", encoding="utf-8"), indent=2)
    print(f"Wrote {RESULTS_DIR / 'phenomenon2_cliff.json'}")


if __name__ == "__main__":
    main()
