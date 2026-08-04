"""Cache vs precise geometry divergence for C2.

For each saved GA-P-BL solution, recompute every consecutive transition's
required slew time tau two ways:
  cached  — sat_position_cache on a 10 s grid (linear interp), solver path
  precise — no cache, compute_los_separation calls _satellite_body_frame

Flags the dangerous direction: cached C2 PASSES but precise C2 FAILS
(false negative). Reports the worst |tau_precise - tau_cached| so an
interpolation safety margin can be sized.

Pickle note: .pkl scenario files are produced by this repo's own
generate_all_scenarios pipeline (trusted local data), not external input.
"""
import json, pickle, sys, time
from pathlib import Path
import numpy as np

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sar_sim.solver.types import (
    build_agile_instance_from_scenario, precompute_geometry,
    compute_los_separation,
)

SLEW, SETTLE = 0.0524, 5.0
SNAP = PAPER / "experiments/results/_snapshot_audit.json"

prog = json.load(open(SNAP, encoding="utf-8"))["completed"]
print(f"solutions: {len(prog)}\n")

fn_c2 = []
all_gaps = []
worst_gap = 0.0
worst_gap_at = None
worst_precise_viol = 0.0

t0 = time.time()
for key, e in prog.items():
    data = pickle.load(open(PAPER / "experiments/scenarios" / key, "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)

    sel = list(e["selected"]); ta = list(e["t_actuals"])
    order = sorted(sel, key=lambda i: float(ta[sel.index(i)]))
    pairs = [(order[k], order[k+1]) for k in range(len(order)-1)]

    # cached path
    precompute_geometry(inst, step_s=10.0)
    eta_c = np.array([
        compute_los_separation(inst.tasks[a], float(ta[sel.index(a)]),
                               inst.tasks[b], float(ta[sel.index(b)]), inst)
        for a, b in pairs])
    # precise path
    inst.sat_position_cache = None
    inst.geom_cache = None
    eta_p = np.array([
        compute_los_separation(inst.tasks[a], float(ta[sel.index(a)]),
                               inst.tasks[b], float(ta[sel.index(b)]), inst)
        for a, b in pairs])

    tau_c = eta_c / SLEW + SETTLE
    tau_p = eta_p / SLEW + SETTLE
    gaps = np.abs(tau_p - tau_c)
    all_gaps.append(gaps)
    if gaps.size:
        j = int(np.argmax(gaps))
        if gaps[j] > worst_gap:
            worst_gap = float(gaps[j]); worst_gap_at = (key, pairs[j])

    cached_pass = bool(np.all(tau_c <= [
        float(ta[sel.index(b)]) - (float(ta[sel.index(a)]) + inst.tasks[a].duration)
        for a, b in pairs])) if pairs else True
    precise_viol = 0.0
    for (a, b), tp in zip(pairs, tau_p):
        avail = float(ta[sel.index(b)]) - (float(ta[sel.index(a)]) + inst.tasks[a].duration)
        precise_viol = max(precise_viol, tp - avail)
    if precise_viol > worst_precise_viol:
        worst_precise_viol = precise_viol
    if cached_pass and precise_viol > 0:
        fn_c2.append((key, len(sel), precise_viol))

dt = time.time() - t0
gaps = np.concatenate(all_gaps) if all_gaps else np.array([0.0])
print(f"transitions: {len(gaps)}")
print(f"worst |tau_p-tau_c| = {worst_gap*1000:.3f} ms at {worst_gap_at}")
print(f"mean = {gaps.mean()*1000:.4f} ms | p99 = {np.percentile(gaps,99)*1000:.4f} ms | max = {gaps.max()*1000:.4f} ms")
print(f"worst precise C2 overshoot (cached-pass sols): {worst_precise_viol*1000:.3f} ms")
print(f"\nFALSE NEGATIVES (cached PASS, precise FAIL): {len(fn_c2)}")
for x in fn_c2[:30]:
    print("  ", x)
print(f"\naudit {dt:.0f}s")
