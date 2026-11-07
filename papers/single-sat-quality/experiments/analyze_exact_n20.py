#!/usr/bin/env python3
"""N11 (panel 2026-11-07 R3-Q1 / editorial): exact optimum coverage profit at
N=20, as the external anchor for the greedy coverage baseline.

Two-part answer:
  1. Scenarios where G-BL selects ALL targets: f1_raw = sum of all priorities
     is the absolute upper bound (one observation per target max), so the
     anchor is provably optimal — no solver needed.
  2. Scenarios where G-BL misses targets: CP-SAT exact model. Candidates =
     (task, 10s-grid time) satisfying C1 (theta band via
     off_nadir_to_incidence, |psi_sq| <= 45 deg, window containment with
     duration). Arc c1->c2 exists iff time-ordered and the C2 transition
     fits (gap = t2 - t1 - dur(i1) >= LOS/rate + settle, mirroring the
     solver's RDR-004 check). AddCircuit with self-loops for unselected
     candidates; maximize total selected priority.

Output: per-scenario exact_raw vs G-BL f1_raw, gap = (exact - gbl)/exact.
Sanity: exact >= gbl must hold (G-BL is feasible).
"""
import json, pickle, sys
from pathlib import Path
import math
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from ortools.sat.python import cp_model

from sar_sim.solver.types import build_agile_instance_from_scenario, precompute_geometry
from sar_sim.solver.types import compute_los_separation
from sar_sim.metrics.nesz import off_nadir_to_incidence

PROJECT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = PROJECT / "experiments" / "scenarios"
RES = PROJECT / "experiments" / "results"
SLEW_RATE, SETTLE_TIME = 0.0524, 5.0
GRID_S = 10.0
DURATION = 30.0
THETA_MIN, THETA_MAX = 15.0, 50.0
SQUINT_MAX = 45.0
TIME_LIMIT_S = 120


def candidates_for(instance, data):
    """C1-eligible (task_idx, t_epoch) grid candidates."""
    windows_by_tid = {}
    for w in data["windows"]:
        windows_by_tid.setdefault(w.target_id, []).append(w)
    tasks = instance.tasks
    cands = []
    for i, task in enumerate(tasks):
        for w in windows_by_tid.get(task.target_id, []):
            t0 = w.t_start.timestamp()
            t1 = w.t_end.timestamp() - DURATION
            t = math.ceil(t0 / GRID_S) * GRID_S
            while t <= t1:
                g = instance.geom_cache.lookup(i, t)
                theta = math.degrees(off_nadir_to_incidence(g.phi))
                if THETA_MIN <= abs(theta) <= THETA_MAX and abs(math.degrees(g.psi_sq)) <= SQUINT_MAX:
                    cands.append((i, t))
                t += GRID_S
    return cands


def solve_exact(instance, cands):
    n = len(cands)
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{k}") for k in range(n)]
    # arc literals: (from, to) including depot 0; self-loop = unselected
    arcs = []
    for a in range(n):
        arcs.append((a + 1, a + 1, x[a].Not()))
        arcs.append((0, a + 1, model.NewBoolVar("")))
        arcs.append((a + 1, 0, model.NewBoolVar("")))
    for a in range(n):
        ia, ta = cands[a]
        ta_end = ta + instance.tasks[ia].duration
        for b in range(n):
            if a == b:
                continue
            ib, tb = cands[b]
            if tb <= ta:
                continue
            delta = compute_los_separation(instance.tasks[ia], ta, instance.tasks[ib], tb, instance)
            tau = delta / instance.max_slew_rate + instance.settle_time
            if (tb - ta_end) >= tau:
                lit = model.NewBoolVar("")
                arcs.append((a + 1, b + 1, lit))
                model.AddImplication(lit, x[a])
                model.AddImplication(lit, x[b])
    model.AddCircuit(arcs)
    model.Add(sum(x) >= 1)
    for i in range(instance.N):
        model.Add(sum(x[k] for k, c in enumerate(cands) if c[0] == i) <= 1)
    model.Maximize(sum(instance.tasks[c[0]].priority * x[k] for k, c in enumerate(cands)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_LIMIT_S
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, status
    sel = [cands[k] for k in range(n) if solver.Value(x[k])]
    raw = sum(instance.tasks[i].priority for i, _ in sel)
    return {"raw": int(raw), "n_selected": len(sel),
            "optimal": status == cp_model.OPTIMAL}, status


def main():
    baselines = json.load(open(RES / "baselines_200.json", encoding="utf-8"))
    s1 = {k: v["b1"] for k, v in baselines.items() if k.startswith("S1/")}
    todo = sorted(k for k, v in s1.items() if v["n_selected"] < v["n_targets"])
    print("incomplete S1 scenarios: %d/50 (others provably optimal)" % len(todo))

    out = {"n_incomplete": len(todo), "scenarios": {}}
    for n, key in enumerate(todo):
        with open(SCENARIOS_DIR / key, "rb") as fh:
            data = pickle.load(fh)
        instance = build_agile_instance_from_scenario(data, max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME)
        precompute_geometry(instance, step_s=GRID_S)
        cands = candidates_for(instance, data)
        res, status = solve_exact(instance, cands)
        gbl_raw = int(s1[key]["f1_raw"])
        rec = {"gbl_raw": gbl_raw, "n_candidates": len(cands), "status": str(status)}
        if res:
            rec.update(res)
            rec["gap_pct"] = round(100.0 * (res["raw"] - gbl_raw) / res["raw"], 2)
            assert res["raw"] >= gbl_raw, "exact below feasible G-BL"
        out["scenarios"][key] = rec
        print("[%d/%d] %s cands=%d exact=%s gbl=%d gap=%s%% optimal=%s" % (
            n + 1, len(todo), key, len(cands),
            res["raw"] if res else "FAIL", gbl_raw,
            rec.get("gap_pct"), res["optimal"] if res else "-"))

    gaps = [v["gap_pct"] for v in out["scenarios"].values() if "gap_pct" in v]
    out["gap_pct_mean"] = float(np.mean(gaps)) if gaps else None
    out["gap_pct_max"] = float(np.max(gaps)) if gaps else None
    print("gap mean=%.2f%% max=%.2f%% (n=%d)" % (
        out["gap_pct_mean"] or 0, out["gap_pct_max"] or 0, len(gaps)))
    with open(RES / "exact_n20.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("saved: %s" % (RES / "exact_n20.json"))


if __name__ == "__main__":
    main()
