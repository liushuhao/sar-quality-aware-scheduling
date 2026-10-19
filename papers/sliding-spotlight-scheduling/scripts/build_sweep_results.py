#!/usr/bin/env python3
"""Aggregate the ticket-48 demand sweep (L7) into the coverage-vs-order
curve (build_v2_results.py pattern).

Reads every s-point directory under ``experiments/v4_results/sweep/``,
joins each pilot artifact with its payload provenance (s_factor), and
emits per-(family, s) readings plus the preregistered shape checks
(ticket 48 item 17, frozen before data):

  C1  monotone non-decreasing median coverage over the whole frozen grid
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
if str(FORK) not in sys.path:
    # fulfillment_ratio imports sss_core (ticket 48 item 20 caliber);
    # the aggregator previously needed no solver imports
    sys.path.insert(0, str(FORK))

S_GRID = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0]
FAMILIES = ("R1C", "R2F", "R3H")


def s_dir_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


_LIB = None


def fulfillment_ratio(artifact_path: Path, s: float) -> float:
    """Ticket 48 item 20 registered caliber (review P1 fix): per served
    task, the ACHIEVED-window f_q (actual squint, as the evaluator scores
    it) over the task's best-REACHABLE-window f_q (each window scored at
    its zero-squint best point, max over windows) -- a <=1 ratio, averaged
    over served tasks and over the tie-set records."""
    import sys as _sys

    from sss_core.evaluator import SchedulingProblem
    from sss_core.geometry import squint_at
    from sss_core.nsga2 import load_manifest
    from sss_core.quality import f_q_per_task

    global _LIB
    if _LIB is None:
        from sss_core.modes import ModeLibrary

        _LIB = ModeLibrary.from_fixture()
    art = json.loads(artifact_path.read_text(encoding="utf-8"))
    manifest = load_manifest(
        V4 / "scenarios" / Path(art["manifest"]).name
    )
    if s != 1.0:
        for t in manifest["tasks"]:
            if t.get("rho_req_m") is not None:
                t["rho_req_m"] = s * float(t["rho_req_m"])
    sp = SchedulingProblem(manifest, _LIB)

    def fq(mode, psi, w):
        r0 = _LIB.geo.R0_m if w.r0_m is None else w.r0_m
        return f_q_per_task(mode, psi, r0, _LIB)

    per_record = []
    for rec in art["front"]:
        ratios = []
        for k, start in rec["starts"].items():
            plan = sp.plans[int(k)]
            w_sel = plan.window_at(start)
            psi = squint_at(start, w_sel.t_ca_s, _LIB.geo, r0_m=w_sel.r0_m)
            got = fq(plan.mode, psi, w_sel)
            cap = max(fq(plan.mode, 0.0, w) for w in plan.windows)
            if cap > 0:
                ratios.append(got / cap)
        if ratios:
            per_record.append(statistics.fmean(ratios))
    return statistics.fmean(per_record) if per_record else float("nan")


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
            covs, fq_readings, front_sizes, fulfill = [], [], [], []
            # exit-11 seeds (no feasible individual survived) are a RECORDED
            # outcome at tight s, not missing data: they enter the curve as
            # zero coverage -- the order is unsatisfiable, nothing is served
            n_exit11 = sum(1 for e in exits.get(fam, []) if e == 11)
            # census + orphan guard (independent-review finding): an exit-11
            # unit must NOT have an artifact (a stale one would be
            # double-counted as zero AND read as data), and every family
            # must account for all SEEDS_PER_VARIANT units.  Ledger keys are
            # "<fam>_<seed>" (no "_seed" segment); artifact names carry
            # "seed<seed>.json".
            artifacts = sorted(sdir.glob(f"pilot_{fam}_seed*.json"))
            e11_seeds = {k.rsplit("_", 1)[1]
                         for k, r in progress["units"].items()
                         if k.startswith(fam + "_") and r["exit"] == 11}
            orphans = [a.name for a in artifacts
                       if any(a.name.endswith(f"seed{sd}.json")
                              for sd in e11_seeds)]
            if orphans:
                print(f"ORPHAN ARTIFACTS for exit-11 units of {fam} at s={s}: "
                      f"{orphans}", file=sys.stderr)
                return 1
            accounted = len(artifacts) + n_exit11
            if accounted != 10:
                print(f"CENSUS BREAK: {fam} at s={s}: {len(artifacts)} artifacts "
                      f"+ {n_exit11} exit-11 != 10 units", file=sys.stderr)
                return 1
            covs = [0.0] * n_exit11
            for _ in range(n_exit11):
                # quality reading is NOT-APPLICABLE for an unservable seed --
                # 0.0 would read as "served at zero quality" (review P2-8)
                fq_readings.append(None)
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
                fulfill.append(fulfillment_ratio(f, s))
            families[fam][s] = {
                "n_artifacts": len(covs) - n_exit11,
                "n_exit11_no_feasible": n_exit11,
                "exit_codes": sorted(exits.get(fam, [])),
                "coverage_per_seed": covs,
                "coverage_median": statistics.median(covs) if covs else None,
                "coverage_min": min(covs) if covs else None,
                "coverage_max": max(covs) if covs else None,
                # RAW aggregate f_q (absolute m^-2-scale quantity, NOT a
                # ratio); None for unservable seeds
                "f_q_absolute_mean_per_seed": fq_readings,
                # ticket 48 item 20 registered caliber: per served task,
                # achieved-window f_q over its best-reachable-window f_q
                # (<=1), averaged over the tie set; median over seeds
                "f_q_fulfillment_ratio_per_seed": fulfill,
                "f_q_fulfillment_ratio_median": (
                    statistics.median(fulfill) if fulfill else None
                ),
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
