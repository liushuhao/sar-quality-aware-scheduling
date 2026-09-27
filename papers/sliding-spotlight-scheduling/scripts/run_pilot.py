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

from sss_core.modes import ModeLibrary  # noqa: E402
from sss_core.nsga2 import PYMOO_PINNED, load_manifest, run_nsga2  # noqa: E402

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
    result = run_nsga2(manifest, lib, seed=args.seed, pop_size=args.pop,
                       generations=args.gen)
    feasible = [r for r in result.front if r["cv"] == 0.0]
    if not feasible:
        print("D11 EXIT 11: no feasible individual survived", file=sys.stderr)
        return EXIT_EMPTY_FRONT

    payload = {
        "schema": "pilot-result/1.0",
        "manifest": str(args.manifest),
        "seed": args.seed,
        "pop_size": args.pop,
        "generations": args.gen,
        "pymoo": PYMOO_PINNED,
        "front_size": len(feasible),
        "front": feasible,
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
          f"f1_star_range=[{min(r['f1_star'] for r in feasible):.4f}, "
          f"{max(r['f1_star'] for r in feasible):.4f}] "
          f"f_q_range=[{min(r['f_q'] for r in feasible):.4f}, "
          f"{max(r['f_q'] for r in feasible):.4f}]")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
