#!/usr/bin/env python3
"""Panel T13 reanalysis (2026-10-24): served-task fraction beside served
priority fraction, per family and grid point (L8 sweep artifacts, no new runs).

Reading convention matches the coverage reading: for each unit the
best-covered tie-set member (max f1_star, cv <= 0), its n_selected over the
manifest's admitted task count; median over the ten seeds of each family.

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_served_fraction.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"

FAMILIES = ("R1C", "R2F", "R3H")
SEED_BASE = {"R1C": 100, "R2F": 200, "R3H": 300}
GRID = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0]


def median(xs: list) -> float:
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def best_member(pilot: dict) -> dict:
    front = [m for m in pilot["front"] if m["cv"] <= 0.0] or pilot["front"]
    return max(front, key=lambda m: (m["f1_star"], -m["cv"]))


def main() -> int:
    out = {}
    for family in FAMILIES:
        out[family] = {}
        for s in GRID:
            sdir = f"s{str(s).replace('.', '_')}"
            rows = []
            n_missing = 0
            for k in range(10):
                seed = SEED_BASE[family] + k
                pj = V5 / "sweep" / sdir / f"pilot_{family}_seed{seed}.json"
                if not pj.exists():
                    # exit-11 unit (no feasible individual): a status, not a
                    # coverage reading -- never averaged (paper discipline)
                    n_missing += 1
                    continue
                pilot = json.loads(pj.read_text(encoding="utf-8"))
                manifest = json.loads(
                    (V5 / "scenarios" / f"{family}_seed{seed}.json").read_text(encoding="utf-8"))
                n_adm = len(manifest["tasks"])
                m = best_member(pilot)
                rows.append({
                    "n_admitted": n_adm,
                    "n_selected": m["n_selected"],
                    "task_fraction": m["n_selected"] / n_adm,
                    "priority_fraction": m["f1_star"],
                })
            feasible = [r for r in rows if r["n_selected"] >= 0]
            # an all-infeasible cell (R1C s=0.8) has no reading at all --
            # recorded as status, mirroring the coverage-curve discipline
            med_task = (round(median([r["task_fraction"] for r in feasible]), 4)
                        if feasible else None)
            med_prio = (round(median([r["priority_fraction"] for r in feasible]), 4)
                        if feasible else None)
            out[family][str(s)] = {
                "median_task_fraction": med_task,
                "median_priority_fraction": med_prio,
                "n_seeds_feasible": len(feasible),
                "n_seeds_infeasible": n_missing,
                "n_selected_min_max": [min(r["n_selected"] for r in feasible),
                                       max(r["n_selected"] for r in feasible)],
                "n_admitted_min_max": [min(r["n_admitted"] for r in feasible),
                                       max(r["n_admitted"] for r in feasible)],
            }
    path = V5 / "served_fraction.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for family in FAMILIES:
        line = " ".join(
            f"{s}:{out[family][str(s)]['median_task_fraction']:.3f}" for s in GRID)
        print(f"# {family} median served-task fraction: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
