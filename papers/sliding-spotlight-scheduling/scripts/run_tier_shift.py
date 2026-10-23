#!/usr/bin/env python3
"""Panel T19 empirical arm (2026-10-24): tier-bound sensitivity of the R1C
floor step, via demand-grid shift over the frozen scenario population.

The coarse requirement tier [2.5, 3.0] m is a template knob, not physics:
multiplying the whole tier by 1/phi is arithmetically identical to reading
the SAME frozen manifests at demand factors s/phi (requirements, modes,
windows, priorities all unchanged -- run_pilot's --s-factor multiplies
rho_req_m in memory only).  The all-STR control family therefore admits an
exact in-sweep tier-shift experiment: run the frozen R1C scenarios at the
shifted grid points and watch the floor step move to the cell predicted by
s* = rho_floor / (tier_top / phi).

Two s* constants are reported and must not be conflated:
  template  : tier_top = 3.0 m (the frozen template bound)
  realized  : tier_top = max realized coarse rho over the ten R1C manifests
              (the bound the arithmetic of the actual task set sees)

Arms (phi = multiplicative tier shift, tier -> [2.5/phi, 3.0/phi]):
  phi=1.10 : step expected to move right (s_grid=0.9 cell all-infeasible)
  phi=0.90 : step expected to leave the grid (no infeasible cell)

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_tier_shift.py --phi 1.1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
OUT = V5 / "tier_shift"

FAMILY = "R1C"
SEED_BASE = 100
GRID = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0]
RHO_FLOOR_M = 2.4669   # stripmap antenna floor (paper Section 3.1)
TIER_TOP_M = 3.0       # coarse tier upper bound (frozen template)
REALIZED_R1C_RHO_MAX_M = 2.961  # max realized coarse rho over R1C manifests


def realized_rho_max() -> float:
    best = 0.0
    for k in range(10):
        m = json.loads(
            (V5 / "scenarios" / f"{FAMILY}_seed{SEED_BASE + k}.json").read_text(
                encoding="utf-8"))
        best = max(best, max(float(t["rho_req_m"]) for t in m["tasks"]))
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phi", type=float, default=1.10)
    args = ap.parse_args()
    phi = args.phi

    OUT.mkdir(parents=True, exist_ok=True)
    arm = f"phi{str(phi).replace('.', '_')}"
    results_path = OUT / f"tier_shift_{arm}.json"
    # unit records always a flat list under "units"; the aggregate dict is
    # written once at the end -- resume reads "units" (gate-review fix: the
    # previous draft mixed a bare list (mid-run) with a dict (final))
    results = []
    if results_path.exists():
        prev = json.loads(results_path.read_text(encoding="utf-8"))
        results = prev["units"] if isinstance(prev, dict) else prev
    done = {(r["seed"], r["s_eff"]) for r in results}

    rho_max_realized = realized_rho_max()
    s_star_template = RHO_FLOOR_M / (TIER_TOP_M / phi)
    s_star_realized = RHO_FLOOR_M / (rho_max_realized / phi)

    for s in GRID:
        s_eff = round(s / phi, 6)
        for k in range(10):
            seed = SEED_BASE + k
            if (seed, s_eff) in done:
                continue
            manifest = V5 / "scenarios" / f"{FAMILY}_seed{seed}.json"
            # per-s_eff output dir: run_pilot names outputs family+seed
            # only, so distinct s_eff values must not share a directory
            unit_dir = OUT / arm / f"s{str(s_eff).replace('.', '_')}"
            unit_dir.mkdir(parents=True, exist_ok=True)
            t0 = time.time()
            cmd = [
                sys.executable, str(FORK / "scripts" / "run_pilot.py"),
                "--manifest", str(manifest),
                "--seed", str(seed), "--pop", "40", "--gen", "60",
                "--s-factor", str(s_eff),
                "--out", str(unit_dir),
            ]
            import os
            env = {**os.environ, "PYTHONHASHSEED": "0"}
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
            wall_s = time.time() - t0
            if proc.returncode not in (0, 11):
                # 0 = solved, 11 = no feasible individual (a reading, not an
                # error); anything else fails loud, never silently aggregated
                print(f"# HARD FAIL seed{seed} s_eff={s_eff}: rc={proc.returncode}\n"
                      f"{proc.stderr[-400:]}", flush=True)
                return 2
            rec = {"phi": phi, "seed": seed, "s_grid": s, "s_eff": s_eff,
                   "rc": proc.returncode, "wall_s": wall_s}
            if proc.returncode == 0:
                pj = unit_dir / f"pilot_{FAMILY}_seed{seed}.json"
                pilot = json.loads(pj.read_text(encoding="utf-8"))
                rec["max_f1_star_on_front"] = pilot["max_f1_star_on_front"]
                rec["anchor_f1_star"] = pilot["anchor_f1_star"]
            results.append(rec)
            results_path.write_text(
                json.dumps({"units": results}, indent=1), encoding="utf-8")
            cov = rec.get("max_f1_star_on_front")
            print(f"# phi={phi} seed{seed} s_grid={s} s_eff={s_eff}: "
                  f"rc={proc.returncode} cov={cov if cov is not None else 'INFEASIBLE'} "
                  f"wall={wall_s:.0f}s", flush=True)

    # aggregate: per grid point, median coverage or all-infeasible status
    agg = {}
    for s in GRID:
        sub = [r for r in results if r["s_grid"] == s]
        infeas = sum(1 for r in sub if r["rc"] == 11)
        feas = [r["max_f1_star_on_front"] for r in sub if r["rc"] == 0]
        xs = sorted(feas)
        med = xs[len(xs) // 2] if xs and len(xs) % 2 else (
            0.5 * (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) if xs else None)
        agg[str(s)] = {"n_seeds": len(sub), "n_infeasible": infeas,
                       "median_coverage": med}
    payload = {
        "phi": phi,
        "tier_top_template_m": TIER_TOP_M / phi,
        "tier_top_realized_m": rho_max_realized / phi,
        "predicted_s_star_template": s_star_template,
        "predicted_s_star_realized": s_star_realized,
        "grid": GRID, "agg": agg, "units": results,
    }
    results_path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"# predicted s* (template top): {s_star_template:.4f}  "
          f"(realized top): {s_star_realized:.4f}")
    for s in GRID:
        a = agg[str(s)]
        print(f"#   s_grid={s} (s_eff={round(s/phi,4)}): infeasible "
              f"{a['n_infeasible']}/{a['n_seeds']} median={a['median_coverage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
