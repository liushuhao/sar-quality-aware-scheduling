#!/usr/bin/env python3
"""Verify gate CLI (ticket 12, spec D11).

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src:papers/sliding-spotlight-scheduling \
        "/d/Program Files/Python/python" \
        papers/sliding-spotlight-scheduling/scripts/run_verify.py \
        --pilot papers/sliding-spotlight-scheduling/experiments/results/pilot/pilot_M1NC_seed100.json \
        --manifest papers/sliding-spotlight-scheduling/experiments/results/scenarios/M1NC_seed100.json

Exit codes: 0 = no FAIL (REPORT/A6 escalations are records, not failures);
20 = at least one FAIL.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=60)
    ap.add_argument("--out", default=str(
        FORK / "experiments" / "results" / "verify" / "report_pilot.json"))
    ap.add_argument("--skip-shared-tests", action="store_true")
    args = ap.parse_args(argv)

    import os

    if os.environ.get("PYTHONHASHSEED") != "0":
        print("run_verify requires PYTHONHASHSEED=0 (D10-8/D12-5 run convention)",
              file=sys.stderr)
        return 2

    from sss_core.verify import EXIT_FAIL, EXIT_PASS, run_gate

    report, code = run_gate(
        Path(args.pilot), Path(args.manifest),
        pop_size=args.pop, generations=args.gen,
        run_shared_tests=not args.skip_shared_tests,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    for step in report["steps"]:
        print(f"[{step['status']:6s}] {step['step']}")
        if step["status"] == "FAIL":
            print(f"         {step['detail']}")
    if report["action_required"]:
        print("[ACTION ] A6 scatter precheck triggered the preregistered "
              "口径重议 escalation -- analysis layer must respond (record, "
              "not a gate failure)")
    print(f"verify report: {out} (PASS={report['n_pass']} "
          f"REPORT={report['n_report']} FAIL={report['n_fail']})")
    return EXIT_PASS if code == 0 else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
