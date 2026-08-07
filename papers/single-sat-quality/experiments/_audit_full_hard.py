"""Full hard-constraint audit of solver saved snapshots (parallel).

Checks C1 incidence/squint, C2 transition (maneuver gap), C3 energy,
C4 memory, out-of-window, and 200-observations budget on every saved
solution. These are all HARD constraints — any violation is a failure.

Parallelized with multiprocessing Pool (one process per core) because the
post-rerun workload is ~1100 entries (MOEA-2/3 + 3 ablations) and each
entry costs ~1.8s serially (~33 min) vs ~4 min on 8 cores.
"""
import json, pickle, sys, time
from pathlib import Path
from collections import defaultdict
import numpy as np
import multiprocessing as mp

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.verification.constraints import ConstraintVerifier

SLEW, SETTLE = 0.0524, 5.0


def audit_one(args):
    """Audit a single scenario entry; returns (key, summary_dict)."""
    key, e = args
    data = pickle.load(open(PAPER / "experiments/scenarios" / key, "rb"))
    alt = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
    inst = build_agile_instance_from_scenario(
        data, max_slew_rate=SLEW, settle_time=SETTLE, altitude_m=alt)
    precompute_geometry(inst, step_s=10.0)
    sel = list(e["selected"]); ta = list(e["t_actuals"])
    phis = list(e["phis_off_nadir"])
    N = inst.N; phi = np.zeros(N); t = np.zeros(N); oow = 0
    for i, tt, ph in zip(sel, ta, phis):
        task = inst.tasks[i]
        wt = task.window_times
        # Full observation interval [tt, tt+duration] must lie in one window
        # (start-only check lets short windows host an OOW observation).
        if wt and not any(ws <= tt and tt + task.duration <= we for ws, we in wt):
            oow += 1
        phi[i] = ph; t[i] = tt
    rep = ConstraintVerifier(inst).verify_solution(sel, phi, t_actual=t)
    flags = {}
    worst_local = {}
    for c in ("C1", "C2", "C3", "C4"):
        v = rep.results[c]
        if not v.passed:
            flags[c] = len(v.violations)
            worst_local[c] = max((x.magnitude for x in v.violations), default=0.0)
    return key, {
        "cls": key.split("/")[0],
        "nsel": len(sel),
        "oow": oow,
        "flags": flags,
        "worst": worst_local,
    }


def main():
    import argparse
    _ap = argparse.ArgumentParser(description="Full hard-constraint audit of saved solver snapshots")
    _ap.add_argument("--snapshot", default=None, help="path to snapshot JSON (default: results/_snapshot_audit.json)")
    _ap.add_argument("--jobs", type=int, default=mp.cpu_count(), help="parallel workers (default: cpu count)")
    _args = _ap.parse_args()
    SNAP = Path(_args.snapshot) if _args.snapshot else PAPER / "experiments/results/_snapshot_audit.json"

    _data = json.load(open(SNAP, encoding="utf-8"))
    prog = _data["completed"] if "completed" in _data else _data
    print(f"snapshot solutions: {len(prog)}\n")

    t0 = time.time()
    with mp.Pool(_args.jobs) as pool:
        results = pool.map(audit_one, list(prog.items()))
    dt = time.time() - t0

    agg = defaultdict(lambda: defaultdict(int))
    worst = defaultdict(float)
    bad = []
    for key, r in results:
        cls = r["cls"]
        a = agg[cls]; a["scen"] += 1; a["nsel"] += r["nsel"]; a["oow"] += r["oow"]
        for c, n in r["flags"].items():
            a[c] += 1
            worst[c] = max(worst[c], r["worst"].get(c, 0.0))
        if r["oow"] or r["flags"]:
            bad.append((key, r["nsel"], r["oow"], r["flags"]))

    print(f"{'cls':<5}{'scen':>5}{'nsel':>7}{'OOW':>5}{'C1':>4}{'C2':>4}{'C3':>4}{'C4':>4}")
    for cls in sorted(agg):
        a = agg[cls]
        print(f"{cls:<5}{a['scen']:>5}{a['nsel']:>7}{a['oow']:>5}{a['C1']:>4}{a['C2']:>4}{a['C3']:>4}{a['C4']:>4}")
    tot = {k: sum(agg[c][k] for c in agg) for k in ("scen", "oow", "C1", "C2", "C3", "C4")}
    print(f"{'TOT':<5}{tot['scen']:>5}{'':>7}{tot['oow']:>5}{tot['C1']:>4}{tot['C2']:>4}{tot['C3']:>4}{tot['C4']:>4}")
    print(f"\nworst magnitudes: " + ", ".join(f"{k}={v:.4f}" for k, v in worst.items()))
    print(f"scenarios with any issue: {len(bad)}  (audit {dt:.0f}s, {_args.jobs} workers)")
    for b in bad[:30]:
        print(" ", b)

    # Non-zero exit on any violation so orchestrators/CI cannot silently
    # consume dirty data (grep-based checks remain for logs).
    n_bad = tot["oow"] + tot["C1"] + tot["C2"] + tot["C3"] + tot["C4"]
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
