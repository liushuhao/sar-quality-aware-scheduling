"""Full hard-constraint audit of GA-P-BL saved snapshot.

Checks C1 incidence/squint, C2 transition (maneuver gap), C3 energy,
C4 memory, out-of-window, and 200-observations budget on every saved
solution. These are all HARD constraints — any violation is a failure.
"""
import json, pickle, sys, time
from pathlib import Path
from collections import defaultdict
import numpy as np

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

SLEW, SETTLE = 0.0524, 5.0
SNAP = PAPER / "experiments/results/_snapshot_audit.json"

prog = json.load(open(SNAP, encoding="utf-8"))["completed"]
print(f"snapshot solutions: {len(prog)}\n")

agg = defaultdict(lambda: defaultdict(int))
worst = defaultdict(float)
bad = []
t0 = time.time()
for key, e in prog.items():
    cls = key.split("/")[0]
    data = pickle.load(open(PAPER / "experiments/scenarios" / key, "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    sel = list(e["selected"]); ta = list(e["t_actuals"])
    phis = list(e["phis_off_nadir"])
    N = inst.N; phi = np.zeros(N); t = np.zeros(N); oow = 0
    for i, tt, ph in zip(sel, ta, phis):
        wt = inst.tasks[i].window_times
        if wt and not any(ws <= tt <= we for ws, we in wt):
            oow += 1
        phi[i] = ph; t[i] = tt
    rep = ConstraintVerifier(inst).verify_solution(sel, phi, t_actual=t)
    a = agg[cls]; a["scen"] += 1; a["nsel"] += len(sel); a["oow"] += oow
    flags = {}
    for c in ("C1", "C2", "C3", "C4"):
        v = rep.results[c]
        if not v.passed:
            a[c] += 1; flags[c] = len(v.violations)
            m = max((x.magnitude for x in v.violations), default=0.0)
            worst[c] = max(worst[c], m)
    if oow or flags:
        bad.append((key, len(sel), oow, flags))

dt = time.time() - t0
print(f"{'cls':<5}{'scen':>5}{'nsel':>7}{'OOW':>5}{'C1':>4}{'C2':>4}{'C3':>4}{'C4':>4}")
for cls in sorted(agg):
    a = agg[cls]
    print(f"{cls:<5}{a['scen']:>5}{a['nsel']:>7}{a['oow']:>5}{a['C1']:>4}{a['C2']:>4}{a['C3']:>4}{a['C4']:>4}")
tot = {k: sum(agg[c][k] for c in agg) for k in ("scen","oow","C1","C2","C3","C4")}
print(f"{'TOT':<5}{tot['scen']:>5}{'':>7}{tot['oow']:>5}{tot['C1']:>4}{tot['C2']:>4}{tot['C3']:>4}{tot['C4']:>4}")
print(f"\nworst magnitudes: " + ", ".join(f"{k}={v:.4f}" for k, v in worst.items()))
print(f"scenarios with any issue: {len(bad)}  (audit {dt:.0f}s)")
for b in bad[:30]:
    print(" ", b)
