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
    ap.add_argument(
        "--freeze-dwell", action="store_true",
        help="fixed-dwell ablation: hold dwell at its zero-squint value "
             "at every consumption point (panel R1 comparison arm)",
    )
    args = ap.parse_args(argv)

    import pymoo

    assert pymoo.__version__ == PYMOO_PINNED, (
        f"pymoo {pymoo.__version__} != pinned {PYMOO_PINNED}"
    )

    manifest = load_manifest(Path(args.manifest))
    if not manifest["tasks"]:
        print("D11 EXIT 10: scenario has zero served tasks", file=sys.stderr)
        return EXIT_ZERO_SERVED

    lib = ModeLibrary.from_fixture()

    # R12 (ticket 25): an all-infeasible scenario must reach the
    # empty-front branch, not die inside the seed encoder.  With every
    # task unschedulable the greedy anchor serves nothing, so the seed
    # row would carry cv=1.0 and the seed-CV assertion would turn the
    # distinguishing exit 11 into a crash (exit 1).
    sp = SchedulingProblem(manifest, lib, freeze_durations=args.freeze_dwell)
    if not any(p.schedulable for p in sp.plans):
        print(
            "D11 EXIT 11: no feasible individual can exist "
            "(every task has an empty feasible set)",
            file=sys.stderr,
        )
        return EXIT_EMPTY_FRONT

    # anchor seed (D12-1/2): encode the greedy anchor solution as population
    # row 0, with the fail-loud CV/f1 dual check inside run_nsga2
    anchor = anchor_on_manifest(manifest, lib, freeze_durations=args.freeze_dwell)
    seed_vec = (
        encode_seed_individual(sp, anchor.starts) if anchor.starts else None
    )
    result = run_nsga2(
        manifest, lib, seed=args.seed, pop_size=args.pop,
        generations=args.gen, seed_individual=seed_vec,
        anchor_f1_star=anchor.f1_star,
        freeze_durations=args.freeze_dwell,
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
        "anchor_seeded": True,
        "anchor_f1_star": anchor.f1_star,
        "anchor_served": len(anchor.starts),
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
    }
    if args.out:
        outdir = Path(args.out)
        outdir.mkdir(parents=True, exist_ok=True)
        outpath = outdir / f"pilot_{manifest['scenario']['family_code']}_seed{args.seed}.json"
        outpath.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"pilot front written: {outpath}")
    print(f"front_size={len(feasible)} "
          f"max_f1_star={max(r['f1_star'] for r in feasible):.4f} "
          f"(anchor {anchor.f1_star:.4f}, search-only "
          f"{result.search_only_max_f1_star if result.search_only_max_f1_star is not None else float('nan'):.4f}) "
          f"promotion={result.promotion_decision}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
