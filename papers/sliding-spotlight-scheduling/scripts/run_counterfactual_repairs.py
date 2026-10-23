#!/usr/bin/env python3
"""Panel T1 reanalysis (2026-10-24): repair-rule sensitivity of the fixed-dwell gap.

The registered counterfactual (ticket 54 step 7) repairs the replayed
fixed-dwell plan by dropping the LATER task of each violating pair.  The
panel's validated CRITICAL DA2: the 18-30 pp gap is conditional on that
priority-blind rule.  This script reprocesses the SAME stored freeze-dwell
plans (counterfactual_fd/raw/, no new solver runs) under three repair rules:

  (a) drop-later          -- registered rule; per-unit output must reproduce
                             counterfactual_units.json byte-for-byte (regression)
  (b) priority-aware drop -- on a violation between consecutive kept i and
                             candidate j, drop whichever of {i, j} carries the
                             lower priority; dropping i cascades backwards
                             (re-check j against the new predecessor)
  (c) bounded re-timing   -- push the later task j to the earliest feasible
                             start t' >= its original start within its own
                             window intervals (1 s grid) that satisfies C2
                             against the last kept task; drop j only if no
                             such t' exists

Violation statistics are computed BEFORE any repair and are rule-independent.

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_counterfactual_repairs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

from sss_core.evaluator import C2_TOL_S, SchedulingProblem  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.maneuver import boundary_rate  # noqa: E402
from sss_core.geometry import squint_at  # noqa: E402
from sss_core.predicates import c2_transfer_requirement_s, schedule_conflict  # noqa: E402

V5 = FORK / "experiments" / "v5_results"
OUT = V5 / "counterfactual_fd"
RAW = OUT / "raw"
FAMILIES = ("R1C", "R2F", "R3H")
SEED_BASE = {"R1C": 100, "R2F": 200, "R3H": 300}
RETGRID_S = 1.0  # bounded re-timing search grid


def lib_and_problem(manifest_path: Path) -> SchedulingProblem:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lib = ModeLibrary.from_fixture()
    return SchedulingProblem(manifest, lib, freeze_durations=False)


def pair_ok(problem: SchedulingProblem, i: int, tp: float, j: int, t: float) -> bool:
    pa, pb = problem.plans[i], problem.plans[j]
    wa, wb = pa.window_at(tp), pb.window_at(t)
    psi_a = squint_at(tp, wa.t_ca_s, problem.lib.geo, r0_m=wa.r0_m)
    psi_b = squint_at(t, wb.t_ca_s, problem.lib.geo, r0_m=wb.r0_m)
    req = c2_transfer_requirement_s(
        problem._dwell(i, tp),
        problem.lib,
        problem.pads,
        d_psi_rad=abs(psi_b - psi_a),
        omega_start=boundary_rate(pa.mode, psi_a, problem.lib, r0_m=wa.r0_m),
        omega_end=boundary_rate(pb.mode, psi_b, problem.lib, r0_m=wb.r0_m),
    )
    if req["requirement_s"] - (t - tp) - C2_TOL_S > 0.0:
        return False
    return not schedule_conflict(tp, problem._dwell(i, tp), t, problem._dwell(j, t))


def starts_to_sel(problem: SchedulingProblem, starts: dict) -> list:
    sel = []
    for k, t in starts.items():
        plan = problem.plans[int(k)]
        if not plan.schedulable:
            continue
        if not any(lo <= t <= hi for lo, hi in plan.intervals):
            continue
        sel.append((float(t), int(k)))
    sel.sort()
    return sel


def repair_drop_later(problem, sel) -> list:
    """(a) registered rule: greedy pass, drop the later task of a violating pair."""
    kept: list[tuple[float, int]] = []
    for t, i in sel:
        if kept and not pair_ok(problem, kept[-1][1], kept[-1][0], i, t):
            continue
        kept.append((t, i))
    return kept


def repair_priority_aware(problem, sel) -> list:
    """(b) on violation drop the lower-priority endpoint; backward cascade."""
    kept: list[tuple[float, int]] = []
    for t, i in sel:
        while kept and not pair_ok(problem, kept[-1][1], kept[-1][0], i, t):
            pi = problem.plans[kept[-1][1]].priority_f
            pj = problem.plans[i].priority_f
            if pj > pi:  # candidate is dearer: drop the kept predecessor
                kept.pop()
            else:
                break
        if kept and not pair_ok(problem, kept[-1][1], kept[-1][0], i, t):
            continue  # predecessor is dearer or equal: drop j
        kept.append((t, i))
    return kept


def repair_retime(problem, sel) -> list:
    """(c) bounded re-timing: push the later task to the earliest feasible
    start within its own window intervals; drop only if none exists."""
    kept: list[tuple[float, int]] = []
    for t, i in sel:
        if kept and not pair_ok(problem, kept[-1][1], kept[-1][0], i, t):
            plan = problem.plans[i]
            found = None
            for lo, hi in plan.intervals:
                t_try = max(t, lo)
                while t_try <= hi:
                    if pair_ok(problem, kept[-1][1], kept[-1][0], i, t_try):
                        found = t_try
                        break
                    t_try += RETGRID_S
                if found is not None:
                    break
            if found is None:
                continue  # no feasible re-timing: drop j
            kept.append((found, i))
        else:
            kept.append((t, i))
    return kept


def coverage(problem, kept: list) -> float:
    served = sum(problem.plans[i].priority_f for _, i in kept)
    return served / max(problem.total_priority, 1e-12)


def best_front_member(pilot_json: dict) -> dict:
    front = [m for m in pilot_json["front"] if m["cv"] <= 0.0]
    if not front:
        front = pilot_json["front"]
    return max(front, key=lambda m: (m["f1_star"], -m["cv"]))


def median(xs: list) -> float:
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def main() -> int:
    stored = {(r["family"], r["seed"]): r for r in
              json.loads((OUT / "counterfactual_units.json").read_text(encoding="utf-8"))}
    results = []
    for family in FAMILIES:
        for seed in range(SEED_BASE[family], SEED_BASE[family] + 10):
            raw = RAW / f"{family}_seed{seed}" / f"pilot_{family}_seed{seed}.json"
            if not raw.exists():
                print(f"# MISSING raw {raw}")
                continue
            fd = json.loads(raw.read_text(encoding="utf-8"))
            member = best_front_member(fd)
            manifest = V5 / "scenarios" / f"{family}_seed{seed}.json"
            problem = lib_and_problem(manifest)
            sel = starts_to_sel(problem, member["starts"])

            base = stored[(family, seed)]
            baseline_cov = base["baseline_coverage"]

            rep = {}
            for name, fn in (
                ("drop_later", repair_drop_later),
                ("priority_aware", repair_priority_aware),
                ("retime", repair_retime),
            ):
                kept = fn(problem, sel)
                cov = coverage(problem, kept)
                rep[name] = {"repaired_coverage": cov,
                             "n_kept": len(kept),
                             "gap_pp": (baseline_cov - cov) * 100.0}

            # regression: rule (a) must reproduce the registered unit
            regen_diff = abs(rep["drop_later"]["repaired_coverage"]
                             - base["fd_repaired_coverage"])
            reg_ok = regen_diff <= 1e-9

            results.append({
                "family": family, "seed": seed, "s": 1.0,
                "baseline_coverage": baseline_cov,
                "fd_planned_coverage": base["fd_planned_coverage"],
                "violating_pairs": base["violating_pairs"],
                "adjacent_pairs": base["adjacent_pairs"],
                "violation_rate": base["violation_rate"],
                "regression_drop_later_ok": reg_ok,
                "regression_abs_diff": regen_diff,
                **{f"{k}_{stat}": v[stat] for k, v in rep.items() for stat in
                   ("repaired_coverage", "n_kept", "gap_pp")},
            })
            print(f"# {family} seed{seed}: reg_ok={reg_ok} "
                  f"gap drop_later={rep['drop_later']['gap_pp']:.2f} "
                  f"priority={rep['priority_aware']['gap_pp']:.2f} "
                  f"retime={rep['retime']['gap_pp']:.2f} pp", flush=True)

    (OUT / "counterfactual_repairs.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8")

    # family aggregates
    agg = {}
    for family in FAMILIES:
        rows = [r for r in results if r["family"] == family]
        agg[family] = {
            "n_units": len(rows),
            "median_gap_pp": {
                rule: round(median([r[f"{rule}_gap_pp"] for r in rows]), 4)
                for rule in ("drop_later", "priority_aware", "retime")},
            "per_seed_gap_pp": {
                rule: [round(r[f"{rule}_gap_pp"], 4) for r in rows]
                for rule in ("drop_later", "priority_aware", "retime")},
            "retime_kept_equals_drop": sum(
                1 for r in rows if r["retime_n_kept"] == r["drop_later_n_kept"]),
        }
    (OUT / "counterfactual_repairs_agg.json").write_text(
        json.dumps(agg, indent=1), encoding="utf-8")
    print("# aggregates written:", json.dumps(
        {f: agg[f]["median_gap_pp"] for f in FAMILIES}, indent=1))
    bad = [r for r in results if not r["regression_drop_later_ok"]]
    print(f"# regression failures: {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
