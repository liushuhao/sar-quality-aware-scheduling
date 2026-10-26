#!/usr/bin/env python3
"""Pilot runner (ticket 10): one NSGA-II run over a scenario manifest.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src:papers/sliding-spotlight-scheduling \
        "/d/Program Files/Python/python" \
        papers/sliding-spotlight-scheduling/scripts/run_pilot.py \
        --manifest papers/sliding-spotlight-scheduling/experiments/results/scenarios/M1NC_seed100.json \
        --seed 100 --pop 40 --gen 60 \
        --out papers/sliding-spotlight-scheduling/experiments/results/pilot

Exit codes (D11, distinguishing): 0 success; 10 zero-served scenario;
11 empty front (no feasible individual); 2 usage/setup error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

from sss_core.anchor import anchor_on_manifest  # noqa: E402
from sss_core.nsga2 import CV_DUST_TOL  # noqa: E402 -- ticket 14 tolerance chain
from sss_core.evaluator import SchedulingProblem  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.nsga2 import (  # noqa: E402
    PYMOO_PINNED,
    encode_seed_individual,
    load_manifest,
    run_nsga2,
)

EXIT_OK = 0
EXIT_ZERO_SERVED = 10
EXIT_EMPTY_FRONT = 11
EXIT_USAGE = 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=60)
    ap.add_argument("--out", default=None)
    freeze_group = ap.add_mutually_exclusive_group()
    freeze_group.add_argument(
        "--freeze-dwell", action="store_true",
        help="fixed-dwell ablation: hold dwell at its zero-squint value "
             "at every consumption point (panel R1 comparison arm; the "
             "registered caliber)",
    )
    freeze_group.add_argument(
        "--freeze-caliber", choices=["zero", "conservative"], default=None,
        help="ignition arm R87-03b: frozen-dwell caliber.  'zero' = the "
             "registered zero-squint value (same as --freeze-dwell); "
             "'conservative' = the longer of the two window-endpoint dwells "
             "clamped to the admissible start domain, derived from the same "
             "registered constants.",
    )
    ap.add_argument(
        "--no-anchor-seed", action="store_true",
        help="ignition arm R87-04: skip the greedy anchor and its encoded "
             "population row 0 -- the NSGA-II initial population is purely "
             "random (anchor-free control).  anchor_f1_star stays null and "
             "search_only stays null.",
    )
    ap.add_argument(
        "--s-factor", type=float, default=1.0,
        help="ticket 48 demand-sweep slack: scale every task's rho_req_m "
             "by this factor IN MEMORY after load (task population, "
             "priorities, and mode assignments stay exactly the manifest's; "
             "only the ordered resolution moves).  1.0 = the order as "
             "placed.  Recorded in the payload as s_factor when != 1.0.",
    )
    args = ap.parse_args(argv)

    # ignition arm R87-03b: normalize the frozen-dwell caliber to one local.
    # "conservative" is threaded as the string; True/False keep the
    # registered zero-squint / endogenous semantics bit-for-bit.
    if args.freeze_caliber == "conservative":
        freeze = "conservative"
    elif args.freeze_caliber == "zero":
        freeze = True
    else:
        freeze = args.freeze_dwell

    import pymoo

    assert pymoo.__version__ == PYMOO_PINNED, (
        f"pymoo {pymoo.__version__} != pinned {PYMOO_PINNED}"
    )

    manifest = load_manifest(Path(args.manifest))
    if not manifest["tasks"]:
        print("D11 EXIT 10: scenario has zero served tasks", file=sys.stderr)
        return EXIT_ZERO_SERVED

    # ticket 48 sweep: scale the ORDER, never the population.  Done once,
    # here, before any consumer (SchedulingProblem, greedy anchor, run_nsga2)
    # touches the dict -- all three read this same in-memory object (no
    # reload seam).  Tasks without rho_req_m are skipped by the same per-task
    # gate the clip itself uses.
    if args.s_factor != 1.0:
        n_scaled = 0
        for t in manifest["tasks"]:
            if t.get("rho_req_m") is not None:
                t["rho_req_m"] = args.s_factor * float(t["rho_req_m"])
                n_scaled += 1
        print(
            f"ticket-48 sweep: rho_req_m scaled by s={args.s_factor} "
            f"on {n_scaled}/{len(manifest['tasks'])} tasks (population fixed)",
            flush=True,
        )

    lib = ModeLibrary.from_fixture()

    # R12 (ticket 25): an all-infeasible scenario must reach the
    # empty-front branch, not die inside the seed encoder.  With every
    # task unschedulable the greedy anchor serves nothing, so the seed
    # row would carry cv=1.0 and the seed-CV assertion would turn the
    # distinguishing exit 11 into a crash (exit 1).
    sp = SchedulingProblem(manifest, lib, freeze_durations=freeze)
    if not any(p.schedulable for p in sp.plans):
        print(
            "D11 EXIT 11: no feasible individual can exist "
            "(every task has an empty feasible set)",
            file=sys.stderr,
        )
        return EXIT_EMPTY_FRONT

    # anchor seed (D12-1/2): encode the greedy anchor solution as population
    # row 0, with the fail-loud CV/f1 dual check inside run_nsga2.
    # ignition arm R87-04: --no-anchor-seed skips the anchor entirely (the
    # initial population is purely random); anchor_f1_star stays null.
    anchor = (
        None if args.no_anchor_seed
        else anchor_on_manifest(manifest, lib, freeze_durations=freeze)
    )
    seed_vec = (
        encode_seed_individual(sp, anchor.starts)
        if anchor is not None and anchor.starts else None
    )
    result = run_nsga2(
        manifest, lib, seed=args.seed, pop_size=args.pop,
        generations=args.gen, seed_individual=seed_vec,
        anchor_f1_star=anchor.f1_star if anchor is not None else None,
        freeze_durations=freeze,
    )
    feasible = [r for r in result.front if r["cv"] <= CV_DUST_TOL]
    if not feasible:
        print("D11 EXIT 11: no feasible individual survived", file=sys.stderr)
        return EXIT_EMPTY_FRONT

    payload = {
        "schema": "pilot-result/1.1",
        "manifest": str(args.manifest),
        "seed": args.seed,
        "pop_size": args.pop,
        "generations": args.gen,
        "pymoo": PYMOO_PINNED,
        "anchor_seeded": seed_vec is not None,
        "anchor_f1_star": anchor.f1_star if anchor is not None else None,
        "anchor_served": len(anchor.starts) if anchor is not None else 0,
        "dwell_caliber": (
            "conservative" if freeze == "conservative"
            else ("zero" if freeze else "endogenous")
        ),
        "front_size": len(feasible),
        "front": feasible,
        "max_f1_star_on_front": max(r["f1_star"] for r in feasible),
        "search_only_max_f1_star": result.search_only_max_f1_star,
        "promotion": {
            "spread_db": result.promotion_spread_db,
            "decision": result.promotion_decision,
            "threshold_db": 6.0,
        },
        "violation_stats": {
            "max_cv_on_reported_front": max(r["cv"] for r in feasible),
            "all_cv_zero": True,
        },
        # ticket 48 world marker: every run through this revision is the
        # single-objective model (f_q is a reading, promotion decision is
        # the registered void marker).  Unconditional, so no consumer can
        # mistake a new pilot for a double-objective frozen record.
        "single_objective": True,
    }
    if args.s_factor != 1.0:
        # provenance of the sweep arm; absence = the order as placed (1.0)
        payload["s_factor"] = args.s_factor
    if args.out:
        outdir = Path(args.out)
        outdir.mkdir(parents=True, exist_ok=True)
        outpath = outdir / f"pilot_{manifest['scenario']['family_code']}_seed{args.seed}.json"
        outpath.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"pilot front written: {outpath}")
    anchor_txt = (
        "no-anchor-seed" if anchor is None else f"anchor {anchor.f1_star:.4f}"
    )
    print(f"front_size={len(feasible)} "
          f"max_f1_star={max(r['f1_star'] for r in feasible):.4f} "
          f"({anchor_txt}, search-only "
          f"{result.search_only_max_f1_star if result.search_only_max_f1_star is not None else float('nan'):.4f}) "
          f"promotion={result.promotion_decision}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
