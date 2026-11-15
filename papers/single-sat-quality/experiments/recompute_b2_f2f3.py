#!/usr/bin/env python3
"""Re-evaluate GA-P-BL (b2_profit_bl) f2/f3 under the f96674f elevation-plane
formulas without re-running the 200-scenario GA (schedule is unchanged; only
the post-hoc f2/f3 metric changed).

f2 = sqrt(max(cos_psi^2 - cos^2(phi), 0)), f3 = cos^3(phi), mean over selected.
In-place updates b2_profit_bl/_progress.json (git-tracked, restorable).

Usage:
  python recompute_b2_f2f3.py            # all scenarios
  python recompute_b2_f2f3.py --test 1   # first N scenarios only (verify)
"""
import pickle, json, sys, math
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJ / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry

SCEN_DIR = _PROJ / "papers" / "single-sat-quality" / "experiments" / "scenarios"
PROG = _PROJ / "papers" / "single-sat-quality" / "experiments" / "results" / "b2_profit_bl" / "_progress.json"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0


def recompute(entry):
    g, fname = entry["_key"].split("/", 1)
    with open(SCEN_DIR / g / fname, "rb") as f:
        data = pickle.load(f)
    instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
    precompute_geometry(instance, step_s=10.0)
    sel = entry["selected"]
    t_acts = entry["t_actuals"]
    f2 = f3 = 0.0
    n = 0
    for i, t_act in zip(sel, t_acts):
        geom = instance.geom_cache.lookup(i, t_act)
        f2 += math.sqrt(max(geom.cos_psi ** 2 - math.cos(geom.phi) ** 2, 0.0))
        f3 += math.cos(geom.phi) ** 3
        n += 1
    return (f2 / n, f3 / n) if n else (0.0, 0.0)


def main():
    d = json.load(open(PROG, encoding="utf-8"))
    completed = d["completed"]
    limit = None
    if "--test" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--test") + 1])
    keys = list(completed.keys())[:limit]
    for k in keys:
        entry = completed[k]
        entry["_key"] = k
        old_f2, old_f3 = entry.get("f2", 0), entry.get("f3", 0)
        nf2, nf3 = recompute(entry)
        entry["f2"] = round(nf2, 12)
        entry["f3"] = round(nf3, 12)
        entry["f2_f3_recompute"] = "f96674f"
        print(f"{k}: f2 {old_f2:.4f}->{nf2:.4f}  f3 {old_f3:.4f}->{nf3:.4f}  n_sel={len(entry['selected'])}")
    json.dump(d, open(PROG, "w", encoding="utf-8"), indent=2)
    print(f"wrote {len(keys)} entries to {PROG}")


if __name__ == "__main__":
    main()
