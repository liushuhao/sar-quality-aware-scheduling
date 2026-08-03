#!/usr/bin/env python3
"""Audit SAVED GA-P-BL solutions (b2_profit_bl/_progress.json) for the same
defect class found in G-SM: observation times outside any visibility window,
|phi| outside the paper C1 envelope [15 deg, 50 deg], C2 maneuver/non-overlap
violations, and the hard C3 (energy) / C4 (memory) budgets. Uses stored
selected / t_actuals / phis_off_nadir, so results reflect exactly the
solutions behind the paper's numbers.
"""
import json
import pickle
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
BIG = 5.0

prog = json.load(open(PAPER_DIR / "experiments/results/b2_profit_bl/_progress.json",
                      encoding="utf-8"))["completed"]
print(f"GA-P-BL saved solutions: {len(prog)}\n")

agg = defaultdict(lambda: defaultdict(int))
worst_per_class = defaultdict(float)
rows_bad = []
t0 = time.time()
for n, (key, e) in enumerate(prog.items(), 1):
    cls = key.split("/")[0]
    pkl = PAPER_DIR / "experiments" / "scenarios" / key
    with open(pkl, "rb") as f:
        data = pickle.load(f)
    alt_m = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, altitude_m=alt_m)
    precompute_geometry(inst, step_s=10.0)
    sel = list(e["selected"])
    ta = list(e["t_actuals"])
    phis = list(e["phis_off_nadir"])

    xwin = c1p = 0
    N = inst.N
    phi_arr = np.zeros(N)
    t_arr = np.zeros(N)
    for i, t, ph in zip(sel, ta, phis):
        wt = inst.tasks[i].window_times
        if not any(ws <= t <= we for ws, we in wt):
            xwin += 1
        if abs(ph) < inst.phi_min or abs(ph) > inst.phi_max:
            c1p += 1
        phi_arr[i] = ph
        t_arr[i] = t

    rep = ConstraintVerifier(inst).verify_solution(sel, phi_arr, t_arr)
    # C2 = attitude maneuver + non-overlap (the transition/overlap class).
    # C3 = energy budget, C4 = memory budget; both are hard constraints.
    mags = [v.magnitude for v in rep.results["C2"].violations]
    big = sum(1 for m in mags if m > BIG)
    tiny = sum(1 for m in mags if m <= BIG)
    worst = max(mags, default=0.0)
    c3fail = 0 if rep.results["C3"].passed else len(rep.results["C3"].violations)
    c4fail = 0 if rep.results["C4"].passed else len(rep.results["C4"].violations)

    a = agg[cls]
    a["scen"] += 1
    a["nsel"] += len(sel)
    a["xwin"] += xwin
    a["c1p"] += c1p
    a["c2big"] += big
    a["c2tiny"] += tiny
    a["c3fail"] += c3fail
    a["c4fail"] += c4fail
    worst_per_class[cls] = max(worst_per_class[cls], worst)
    if xwin or c1p or big or c3fail or c4fail:
        rows_bad.append((key, len(sel), xwin, c1p, big, c3fail, c4fail, worst))

    if n % 50 == 0:
        print(f"  ...{n}/{len(prog)}", flush=True)

dt = time.time() - t0
print(f"\n{'=' * 66}")
print(f"GA-P-BL audit ({len(prog)} scenarios, {dt:.0f}s)")
print(f"{'class':<6} {'scen':>5} {'nsel':>6} {'xWin':>6} {'C1ppr':>6} "
      f"{'C2big':>6} {'C2tiny':>7} {'C3fail':>7} {'C4fail':>7} {'worst_s':>8}")
for cls in sorted(agg):
    a = agg[cls]
    print(f"{cls:<6} {a['scen']:>5} {a['nsel']:>6} {a['xwin']:>6} {a['c1p']:>6} "
          f"{a['c2big']:>6} {a['c2tiny']:>7} {a['c3fail']:>7} {a['c4fail']:>7} "
          f"{worst_per_class[cls]:>8.1f}")
print(f"\nscenarios with any issue: {len(rows_bad)}")
for r in rows_bad[:20]:
    print(f"  {r[0]}: nsel={r[1]} xWin={r[2]} C1ppr={r[3]} C2big={r[4]} "
          f"C3fail={r[5]} C4fail={r[6]} worst={r[7]:.1f}s")
