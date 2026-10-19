#!/usr/bin/env python3
"""Aggregate the ticket-48 demand sweep (L7) into the coverage-vs-order
curve (build_v2_results.py pattern).

Reads every s-point directory under ``experiments/v4_results/sweep/``,
joins each pilot artifact with its payload provenance (s_factor), and
emits per-(family, s) readings plus the preregistered shape checks
(ticket 48 item 17, frozen before data):

  C1  monotone non-decreasing median coverage over s in {0.8 .. 1.5}
  C2  saturation arm: median(s=2.0) >= median(s=1.5)
  C3  tighter-than-platform arm: median(s=0.8) < median(s=1.0)

Exit codes: 0 all checks pass; 1 any check fails (never silent).
Usage (repo root): python papers/sliding-spotlight-scheduling/scripts/build_sweep_results.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V4 = FORK / "experiments" / "v4_results"
SWEEP = V4 / "sweep"

S_GRID = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0]
FAMILIES = ("R1C", "R2F", "R3H")


def s_dir_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def main() -> int:
    families: dict[str, dict[float, dict]] = {f: {} for f in FAMILIES}
    for s in S_GRID:
        sdir = SWEEP / s_dir_name(s)
        if not sdir.is_dir():
            print(f"MISSING s-point directory: {sdir}", file=sys.stderr)
            return 1
        # per-seed outcomes from the driver ledger (exit 11 = no feasible
        # individual: a recorded outcome at tight s, not a crash)
        progress = json.loads((sdir / "_progress.json").read_text(encoding="utf-8"))
        exits: dict[str, list[int]] = {}
        for key, rec in progress["units"].items():
            fam = key.split("_")[0]
            exits.setdefault(fam, []).append(rec["exit"])
        for fam in FAMILIES:
            covs, fq_readings, front_sizes = [], [], []
            # exit-11 seeds (no feasible individual survived) are a RECORDED
            # outcome at tight s, not missing data: they enter the curve as
            # zero coverage -- the order is unsatisfiable, nothing is served
            n_exit11 = sum(1 for e in exits.get(fam, []) if e == 11)
            covs = [0.0] * n_exit11
            for _ in range(n_exit11):
                fq_readings.append(0.0)
                front_sizes.append(0)
            for f in sorted(sdir.glob(f"pilot_{fam}_seed*.json")):
                art = json.loads(f.read_text(encoding="utf-8"))
                s_payload = float(art.get("s_factor", 1.0))
                if abs(s_payload - s) > 1e-12:
                    print(
                        f"PROVENANCE MISMATCH: {f.name} payload s={s_payload} "
                        f"!= directory s={s}",
                        file=sys.stderr,
                    )
                    return 1
                covs.append(art["max_f1_star_on_front"])
                front_sizes.append(art["front_size"])
                fq = [r["f_q"] for r in art["front"]]
                fq_readings.append(statistics.fmean(fq) if fq else float("nan"))
            families[fam][s] = {
                "n_artifacts": len(covs) - n_exit11,
                "n_exit11_no_feasible": n_exit11,
                "exit_codes": sorted(exits.get(fam, [])),
                "coverage_per_seed": covs,
                "coverage_median": statistics.median(covs) if covs else None,
                "coverage_min": min(covs) if covs else None,
                "coverage_max": max(covs) if covs else None,
                "f_q_reading_mean_per_seed": fq_readings,
                "front_size_median": statistics.median(front_sizes) if front_sizes else None,
            }

    checks = {}
    for fam in FAMILIES:
        med = {s: families[fam][s]["coverage_median"] for s in S_GRID}
        if any(v is None for v in med.values()):
            checks[fam] = "INCOMPLETE: at least one s point has zero artifacts"
            continue
        monotone = all(
            med[a] <= med[b] + 1e-12 for a, b in zip(S_GRID[:-1], S_GRID[1:])
        )
        saturates = med[2.0] >= med[1.5] - 1e-12
        tight_arm_drops = med[0.8] < med[1.0]
        checks[fam] = {
            "C1_monotone_s<=2.0": monotone,
            "C2_saturation_2.0>=1.5": saturates,
            "C3_tight_arm_drops(0.8<1.0)": tight_arm_drops,
            "coverage_median_by_s": {str(s): med[s] for s in S_GRID},
        }

    out = V4 / "sweep_results.json"
    out.write_text(
        json.dumps(
            {"s_grid": S_GRID, "families": families, "checks": checks},
            indent=2, sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    for fam in FAMILIES:
        med = families[fam]
        row = " ".join(
            f"s={s}:{med[s]['coverage_median']:.4f}" if med[s]["coverage_median"] is not None
            else f"s={s}:--"
            for s in S_GRID
        )
        print(f"{fam}: {row}")
        print(f"  checks: {checks[fam]}")
    print(f"written: {out}")
    ok = all(
        isinstance(v, dict)
        and v["C1_monotone_s<=2.0"]
        and v["C2_saturation_2.0>=1.5"]
        and v["C3_tight_arm_drops(0.8<1.0)"]
        for v in checks.values()
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
