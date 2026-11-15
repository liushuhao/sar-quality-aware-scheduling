#!/usr/bin/env python3
"""Panel-20260830 N14: within-knee-schedule per-task f2-f3 correlation for
ablation variants B (no_squint) and C (no_incidence), with A re-run as the
same-caliber control. Also reports per-group f2/f3 spread to test the
range-compression alternative explanation (dense f2 range ~0.014 mechanically
attenuating r).

Output: experiments/results/schedule_correlation_ablation.json
"""
import pickle, json, sys, subprocess
from pathlib import Path
import numpy as np

_PROJ = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

PROJECT = _PROJ / "papers" / "single-sat-quality"
RESULTS_DIR = PROJECT / "experiments" / "results"
OUT_PATH = RESULTS_DIR / "schedule_correlation_ablation.json"

GROUPS = ["S1", "S2", "S3", "S4"]
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0

VARIANTS = [
    ("A_full_physics", "moea_3obj/_progress.json"),
    ("B_no_squint", "moea_3obj_no_squint/_progress.json"),
    ("C_no_incidence", "moea_3obj_no_incidence/_progress.json"),
]


def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), text=True).strip()[:8]
    except Exception:
        return "unknown"


def pearson(x, y):
    return float(np.corrcoef(np.array(x), np.array(y))[0, 1])


def f2_new(g):
    import math
    return math.sqrt(max(g.cos_psi ** 2 - math.cos(g.phi) ** 2, 0.0))


def f3_new(g):
    import math
    return math.cos(g.phi) ** 3


def main():
    out = {"git_commit": _git_commit(), "variants": {}}
    for variant, prog_rel in VARIANTS:
        prog_path = RESULTS_DIR / prog_rel
        if not prog_path.exists():
            print(f"WARN missing {prog_path}")
            continue
        completed = json.load(open(prog_path)).get("completed", {})
        variant_out = {}
        for group in GROUPS:
            F2, F3 = [], []
            sched_rs = []
            n_sched = 0
            for key, v in sorted(completed.items()):
                if not key.startswith(group + "/"):
                    continue
                pkl = PROJECT / "experiments" / "scenarios" / group / key.split("/")[1]
                if not pkl.exists():
                    continue
                with open(pkl, "rb") as f:
                    data = pickle.load(f)
                inst = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
                precompute_geometry(inst, step_s=10.0)
                sel, t_acts = v.get("selected", []), v.get("t_actuals", [])
                if not sel or len(sel) != len(t_acts):
                    continue
                sf2, sf3 = [], []
                for i, t in zip(sel, t_acts):
                    g = inst.geom_cache.lookup(int(i), float(t))
                    sf2.append(f2_new(g))
                    sf3.append(f3_new(g))
                F2.extend(sf2)
                F3.extend(sf3)
                if len(sf2) >= 3:
                    r = pearson(sf2, sf3)
                    if np.isfinite(r):
                        sched_rs.append(r)
                n_sched += 1
            if not F2:
                print(f"  {variant} {group}: no data")
                continue
            f2a, f3a = np.array(F2), np.array(F3)
            entry = {
                "r": pearson(F2, F3), "n_tasks": len(F2), "n_schedules": n_sched,
                "f2_mean": float(f2a.mean()), "f2_std": float(f2a.std()),
                "f2_range": float(f2a.max() - f2a.min()),
                "f3_mean": float(f3a.mean()), "f3_std": float(f3a.std()),
                "f3_range": float(f3a.max() - f3a.min()),
            }
            if sched_rs:
                rs = np.asarray(sched_rs)
                entry["per_schedule_mean"] = float(rs.mean())
                entry["fisher_z_mean"] = float(np.arctanh(np.clip(rs, -0.999, 0.999)).mean())
            variant_out[group] = entry
            print(f"{variant} {group}: r={entry['r']:+.4f} n={len(F2)} "
                  f"per_sched={entry.get('per_schedule_mean', float('nan')):+.4f} "
                  f"f2_std={entry['f2_std']:.4f} f2_range={entry['f2_range']:.4f}", flush=True)
        out["variants"][variant] = variant_out
    out["sources"] = {v: p for v, p in VARIANTS}
    json.dump(out, open(OUT_PATH, "w", encoding="utf-8"), indent=2)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
