#!/usr/bin/env python3
"""Ticket 54 step 7a (user ruling P1-8, 2026-10-23): fixed-dwell counterfactual on L8.

For each of the three families x 10 seeds (s=1.0), run the freeze-dwell arm
(dwell held at its zero-squint library value at every consumption point --
the classical fixed-dwell assumption), take its best-covered schedule, then
re-play that schedule against the REAL endogenous dwell:

  * C2 violation rate before repair (pairs violating the transfer bound)
  * greedy time-order repair (drop the later task of any violating pair)
  * repaired coverage vs. the L8 endogenous-dwell arm (coverage gap, pp)

The 2026-10-17 v4 ablation numbers are a different registered world and are
NOT mixed in; this script recomputes everything in the L8 (v5_results) world.

Usage (repo root):
    PYTHONPATH=src:papers/sliding-spotlight-scheduling python \
        papers/sliding-spotlight-scheduling/scripts/run_counterfactual_fd.py \
        --families R1C --seeds 100        # smoke
        --families R1C,R2F,R3H --seeds 100..109  # full 30 units
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
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
SEED_BASE = {"R1C": 100, "R2F": 200, "R3H": 300}  # registered naming: family-coded seed blocks


def lib_and_problem(manifest_path: Path) -> SchedulingProblem:
    # replay world is ALWAYS the real endogenous dwell (freeze_durations
    # stays False) -- the counterfactual contrast is planned-world vs
    # replayed-world; do not thread the caliber through here.
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lib = ModeLibrary.from_fixture()
    return SchedulingProblem(manifest, lib, freeze_durations=False)


def _pair_c2_check(
    problem: SchedulingProblem, ip: int, tp: float, i: int, t: float
) -> tuple[bool, float, float]:
    """C2 transfer verdict for ONE planned adjacent pair (ip@tp -> i@t).

    Single source of truth for the violation predicate: both the pure-plan
    (before any repair) caliber and the drop-later traversal below call this,
    so the two calibers cannot drift.  Returns (violated, requirement_s,
    excess_s) with excess_s = max(0, requirement - gap - C2_TOL_S).
    """
    pa, pb = problem.plans[ip], problem.plans[i]
    wa = pa.window_at(tp)
    wb = pb.window_at(t)
    psi_a = squint_at(tp, wa.t_ca_s, problem.lib.geo, r0_m=wa.r0_m)
    psi_b = squint_at(t, wb.t_ca_s, problem.lib.geo, r0_m=wb.r0_m)
    req = c2_transfer_requirement_s(
        problem._dwell(ip, tp),
        problem.lib,
        problem.pads,
        d_psi_rad=abs(psi_b - psi_a),
        omega_start=boundary_rate(pa.mode, psi_a, problem.lib, r0_m=wa.r0_m),
        omega_end=boundary_rate(pb.mode, psi_b, problem.lib, r0_m=wb.r0_m),
    )
    gap = t - tp
    violated = req["requirement_s"] - gap - C2_TOL_S > 0.0 or schedule_conflict(
        tp, problem._dwell(ip, tp), t, problem._dwell(i, t)
    )
    return violated, req["requirement_s"], max(0.0, req["requirement_s"] - gap - C2_TOL_S)


def replay_real(problem: SchedulingProblem, starts: dict) -> dict:
    """Time-order greedy repair of a planned schedule under the real dwell.

    Returns violation stats BEFORE repair and the repaired coverage.

    Calibers (2026-10-25 ticket 62 wave): ``*_pure`` = before any repair,
    over the planned adjacent pairs -- the honest pre-repair reading; the
    legacy ``violating_pairs`` / ``adjacent_pairs`` / ``violation_rate``
    fields are counted inside the drop-later traversal (dropped tasks mask
    violating pairs, so they under-read) and are kept as legacy.
    """
    sel = []
    for k, t in starts.items():
        plan = problem.plans[int(k)]
        if not plan.schedulable:
            continue
        if not any(lo <= t <= hi for lo, hi in plan.intervals):
            continue
        sel.append((float(t), int(k)))
    sel.sort()

    # pure-plan caliber: every adjacent pair of the SORTED planned sequence,
    # before any repair, decoupled from the traversal below.
    vp_pure = 0
    adj_pairs_pure = 0
    for (tp, ip), (t, i) in zip(sel, sel[1:]):
        adj_pairs_pure += 1
        violated, _req_s, _excess_s = _pair_c2_check(problem, ip, tp, i, t)
        if violated:
            vp_pure += 1

    viol_pairs = 0
    viol_total_s = 0.0
    adj_pairs = 0
    kept: list[tuple[float, int]] = []
    for t, i in sel:
        if kept:
            tp, ip = kept[-1]
            violated, _req_s, excess_s = _pair_c2_check(problem, ip, tp, i, t)
            adj_pairs += 1
            if violated:
                viol_pairs += 1
                viol_total_s += excess_s
                continue  # greedy repair: drop the later task
        kept.append((t, i))

    served = sum(problem.plans[i].priority_f for _, i in kept)
    return {
        "adjacent_pairs": adj_pairs,
        "violating_pairs": viol_pairs,
        "violation_rate": (viol_pairs / adj_pairs) if adj_pairs else 0.0,
        "violating_pairs_pure": vp_pure,
        "adjacent_pairs_pure": adj_pairs_pure,
        "violation_rate_pure": (vp_pure / adj_pairs_pure) if adj_pairs_pure else 0.0,
        "violation_total_s": viol_total_s,
        "repaired_coverage": served / max(problem.total_priority, 1e-12),
        "n_selected_planned": len(sel),
        "n_kept_real": len(kept),
    }


def best_front_member(pilot_json: dict) -> dict:
    front = [m for m in pilot_json["front"] if m["cv"] <= 0.0]
    if not front:
        front = pilot_json["front"]
    return max(front, key=lambda m: (m["f1_star"], -m["cv"]))


def run_unit(family: str, seed: int, pop: int, gen: int, caliber: str) -> dict:
    manifest = V5 / "scenarios" / f"{family}_seed{seed}.json"
    baseline_json = V5 / "sweep" / "s1_0" / f"pilot_{family}_seed{seed}.json"
    raw_dir = RAW / f"{family}_seed{seed}"
    raw_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    freeze_args = (
        ["--freeze-dwell"] if caliber == "zero"
        else ["--freeze-caliber", "conservative"]
    )
    cmd = [
        sys.executable, str(FORK / "scripts" / "run_pilot.py"),
        "--manifest", str(manifest),
        "--seed", str(seed), "--pop", str(pop), "--gen", str(gen),
        "--s-factor", "1.0", *freeze_args,
        "--out", str(raw_dir),
    ]
    env_py = {"PYTHONHASHSEED": "0"}
    import os
    env = {**os.environ, **env_py}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    wall_s = time.time() - t0
    if proc.returncode != 0:
        return {"family": family, "seed": seed, "error": f"run_pilot rc={proc.returncode}",
                "stderr_tail": proc.stderr[-400:], "wall_s": wall_s}

    fd = json.loads((raw_dir / f"pilot_{family}_seed{seed}.json").read_text(encoding="utf-8"))
    base = json.loads(baseline_json.read_text(encoding="utf-8"))
    member = best_front_member(fd)
    problem = lib_and_problem(manifest)
    replay = replay_real(problem, member["starts"])

    planned = member["f1_star"]
    baseline_cov = base["max_f1_star_on_front"]
    return {
        "family": family, "seed": seed, "s": 1.0,
        "fd_planned_coverage": planned,
        "baseline_coverage": baseline_cov,
        "fd_repaired_coverage": replay["repaired_coverage"],
        "coverage_gap_pp": (baseline_cov - replay["repaired_coverage"]) * 100.0,
        "adjacent_pairs": replay["adjacent_pairs"],
        "violating_pairs": replay["violating_pairs"],
        "violation_rate": replay["violation_rate"],
        "violating_pairs_pure": replay["violating_pairs_pure"],
        "adjacent_pairs_pure": replay["adjacent_pairs_pure"],
        "violation_rate_pure": replay["violation_rate_pure"],
        "violation_total_s": replay["violation_total_s"],
        "n_selected_planned": replay["n_selected_planned"],
        "n_kept_real": replay["n_kept_real"],
        "dwell_caliber": caliber,
        "schedule_world": f"frozen-{caliber}",
        "replay_world": "endogenous",
        "wall_s": wall_s,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="R1C,R2F,R3H")
    ap.add_argument("--seeds", default="auto")
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=60)
    ap.add_argument("--caliber", choices=["zero", "conservative"], default="zero",
                    help="frozen-dwell caliber passed to run_pilot "
                         "(zero = --freeze-dwell, the registered zero-squint "
                         "arm; conservative = --freeze-caliber conservative)")
    args = ap.parse_args()

    fams = [f.strip() for f in args.families.split(",")]
    if args.seeds.lower() == "auto":
        seeds = None  # per-family registered blocks (SEED_BASE .. +9)
    elif "-" in args.seeds:
        lo, hi = args.seeds.split("-")
        seeds = list(range(int(lo), int(hi) + 1))
    else:
        seeds = [int(s) for s in args.seeds.split(",")]

    # caliber-scoped artifact routing: the conservative arm writes its own
    # tree (counterfactual_fd/conservative/...), never touching the
    # registered zero-arm files.  MUST run before results_path is computed,
    # or the resume set would be read from the wrong arm (0-unit fake-green).
    global OUT, RAW
    if args.caliber == "conservative":
        OUT = OUT / "conservative"
        RAW = RAW / "conservative"
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    results_path = OUT / "counterfactual_units.json"
    results = []
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
    done = {(r["family"], r["seed"]) for r in results if "error" not in r}

    for fam in fams:
        unit_seeds = seeds if seeds is not None else list(
            range(SEED_BASE[fam], SEED_BASE[fam] + 10))
        for seed in unit_seeds:
            if (fam, seed) in done:
                print(f"# skip {fam} seed{seed} (done)")
                continue
            r = run_unit(fam, seed, args.pop, args.gen, args.caliber)
            results.append(r)
            results_path.write_text(
                json.dumps(results, indent=1), encoding="utf-8")
            if "error" in r:
                print(f"# ERROR {fam} seed{seed}: {r['error']}")
            else:
                print(f"# {fam} seed{seed}: planned={r['fd_planned_coverage']:.4f} "
                      f"repaired={r['fd_repaired_coverage']:.4f} "
                      f"baseline={r['baseline_coverage']:.4f} "
                      f"gap={r['coverage_gap_pp']:.2f}pp "
                      f"viol={r['violating_pairs']}/{r['adjacent_pairs']} "
                      f"({r['violation_rate']*100:.1f}%) wall={r['wall_s']:.0f}s",
                      flush=True)
    print(f"# units complete: {sum(1 for r in results if 'error' not in r)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
