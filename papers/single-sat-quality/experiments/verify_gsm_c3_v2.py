#!/usr/bin/env python3
"""G-SM constraint audit v2: severity-stratified.

Round-1 finding: verifier's per-task C1 bounds and sub-second C3 margins
fire on the G-BL control too (model artifacts). This version reports:

  M1  C3 (paper C2) transition violations, split:
        - tiny  (margin <= 5 s): candidate-time tau drift, also on G-BL
        - large (margin >  5 s): real infeasibility
  M2  C1 paper-level: |phi| outside instance [15 deg, 50 deg]
        (distinct from verifier's per-task window-metadata bounds)
  M3  G-SM cross-window jumps: t_actual landed outside obs.window range
        (direct quantification of qwen audit finding 🟡-8)
"""
import argparse
import pickle
import sys
import time
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np

PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sar_sim.solver.baselines import baseline_b1, baseline_b3
from sar_sim.solver.types import (
    build_agile_instance,
    compute_full_attitude,
    precompute_geometry,
)
from sar_sim.verification.constraints import ConstraintVerifier

SLEW_RATE = 0.0524
SETTLE_TIME = 5.0
GROUPS = ["S1", "S2", "S3", "S4"]
BIG_MARGIN_S = 5.0


def audit(result, instance):
    t2i = {t.target_id: i for i, t in enumerate(instance.tasks)}
    N = instance.N
    phi = np.zeros(N)
    t_act = np.zeros(N)
    sel = []
    out_of_win = 0
    for obs in result.schedule:
        i = t2i.get(obs.window.target_id)
        if i is None:
            continue
        t = obs.t_actual_start.timestamp()
        roll, _, _ = compute_full_attitude(instance.tasks[i], t, 1.0, instance)
        sel.append(i)
        phi[i] = roll
        t_act[i] = t
        ws = obs.window.t_start.timestamp()
        we = obs.window.t_end.timestamp()
        if t < ws - 1e-6 or t > we + 1e-6:
            out_of_win += 1

    rep = ConstraintVerifier(instance).verify_solution(sel, phi, t_act)
    c3 = rep.results["C3"]
    mags = [v.magnitude for v in c3.violations]
    c3_tiny = sum(1 for m in mags if m <= BIG_MARGIN_S)
    c3_big = sum(1 for m in mags if m > BIG_MARGIN_S)
    worst = max(mags, default=0.0)

    phi_lo, phi_hi = instance.phi_min, instance.phi_max
    c1_paper = sum(1 for i in sel if abs(phi[i]) < phi_lo or abs(phi[i]) > phi_hi)

    return {
        "n_sel": len(sel),
        "c3_tiny": c3_tiny,
        "c3_big": c3_big,
        "c3_worst": worst,
        "c1_paper": c1_paper,
        "out_of_win": out_of_win,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=10)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    scen = OrderedDict()
    for g in GROUPS:
        files = sorted((PAPER_DIR / "experiments" / "scenarios" / g).glob("*.pkl"))
        scen[g] = files if args.all else files[: args.per]

    total = sum(len(v) for v in scen.values())
    print(f"G-SM audit v2: {total} scenarios, big-margin threshold {BIG_MARGIN_S:.0f}s\n")
    hdr = f"{'scenario':<22} {'N':>4} {'nsel':>5} | {'C3big':>6} {'C3tiny':>7} {'worst_s':>8} | {'C1ppr':>6} {'xWin':>5}"
    print(f"{hdr}\n{'-' * len(hdr)}")

    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    n = 0
    t0 = time.time()
    for g, files in scen.items():
        for fp in files:
            n += 1
            with open(fp, "rb") as f:
                data = pickle.load(f)
            alt_m = float(data.get("satellite", {}).get("altitude_km", 693.0)) * 1000.0
            instance = build_agile_instance(
                data["windows"], data["targets"],
                max_slew_rate=SLEW_RATE, settle_time=SETTLE_TIME, altitude_m=alt_m)
            precompute_geometry(instance, step_s=10.0)

            b1 = baseline_b1(data["windows"], data["targets"], max_slew_rate=SLEW_RATE,
                             settle_time=SETTLE_TIME,
                             geom_cache=instance.geom_cache, instance=instance)
            b3 = baseline_b3(data["windows"], data["targets"], max_slew_rate=SLEW_RATE,
                             settle_time=SETTLE_TIME,
                             geom_cache=instance.geom_cache, instance=instance)
            r1 = audit(b1, instance)
            r3 = audit(b3, instance)

            print(f"{'G-BL ' + fp.name:<22} {instance.N:>4} {r1['n_sel']:>5} | "
                  f"{r1['c3_big']:>6} {r1['c3_tiny']:>7} {r1['c3_worst']:>8.1f} | "
                  f"{r1['c1_paper']:>6} {r1['out_of_win']:>5}")
            print(f"{'G-SM ' + fp.name:<22} {instance.N:>4} {r3['n_sel']:>5} | "
                  f"{r3['c3_big']:>6} {r3['c3_tiny']:>7} {r3['c3_worst']:>8.1f} | "
                  f"{r3['c1_paper']:>6} {r3['out_of_win']:>5}")
            for solver, r in (("G-BL", r1), ("G-SM", r3)):
                for k in ("c3_big", "c3_tiny", "c1_paper", "out_of_win"):
                    agg[g][solver][k] += r[k]
                agg[g][solver]["scen_with_big"] += 1 if r["c3_big"] else 0
                agg[g][solver]["worst"] = max(agg[g][solver]["worst"], r["c3_worst"])
            sys.stdout.flush()

    dt = time.time() - t0
    print(f"\n{'=' * 72}")
    print(f"Per-class totals ({n} scenarios, {dt:.0f}s)")
    print(f"{'class':<6} {'solver':<7} {'C3big':>7} {'scen_w_big':>11} {'worst_s':>9} "
          f"{'C3tiny':>8} {'C1ppr':>7} {'xWin':>6}")
    for g in GROUPS:
        for solver in ("G-BL", "G-SM"):
            a = agg[g][solver]
            if not a:
                continue
            print(f"{g:<6} {solver:<7} {a['c3_big']:>7} {a['scen_with_big']:>11} "
                  f"{a['worst']:>9.1f} {a['c3_tiny']:>8} {a['c1_paper']:>7} {a['out_of_win']:>6}")


if __name__ == "__main__":
    main()
