#!/usr/bin/env python3
"""Ticket 62 follow-up wave (user ruling, 2026-10-25): pure-plan C2 violation caliber.

The legacy ``violating_pairs`` / ``adjacent_pairs`` / ``violation_rate``
fields were counted INSIDE the drop-later repair traversal, so tasks dropped
by the repair mask some violating pairs and the reading under-counts.  This
script recomputes the pure-plan caliber (before any repair, over the sorted
planned adjacent pairs) for every stored unit of BOTH fixed-dwell arms
(zero: raw/<f>_seed*/, conservative: raw/conservative/<f>_seed*/), then:

  1. patches ``counterfactual_units.json`` in place (both trees): appends
     ``violating_pairs_pure`` / ``adjacent_pairs_pure`` /
     ``violation_rate_pure`` only -- old fields and row order untouched,
     one ``.bak`` backup taken the first time;
  2. rebuilds ``counterfactual_fd/counterfactual_summary.json``: every old
     field preserved as-is, plus ``violation_rate_pure_median/min/max``,
     ``violating_pairs_pure_total``, ``adjacent_pairs_pure_total`` and
     ``units_with_zero_violation_pure`` per family (median/sum/count, same
     aggregation style as the original summarize_7a), with the conservative
     arm's aggregates under a top-level ``conservative`` key.

The violation predicate is NOT reimplemented here: the pure verdict comes
from ``run_counterfactual_fd.replay_real`` itself (same
``c2_transfer_requirement_s`` / ``schedule_conflict`` call chain), so the
runner and this recompute cannot drift.  Idempotent: every run recomputes
from the files' current state (no accumulation).  raw/ stays read-only.

Usage (repo root):
    PYTHONPATH="src;papers/sliding-spotlight-scheduling" "/d/Program Files/Python/python" \
        papers/sliding-spotlight-scheduling/scripts/recount_counterfactual_pure.py
"""
from __future__ import annotations

import json
import shutil
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))
sys.path.insert(0, str(FORK / "scripts"))

from run_counterfactual_fd import (  # noqa: E402
    FAMILIES, SEED_BASE, V5, best_front_member, lib_and_problem, replay_real,
)

OUT = V5 / "counterfactual_fd"
SUMMARY = OUT / "counterfactual_summary.json"
# (arm label, raw root, units path)
ARMS = (
    ("zero", OUT / "raw", OUT / "counterfactual_units.json"),
    ("conservative", OUT / "raw" / "conservative",
     OUT / "conservative" / "counterfactual_units.json"),
)
PURE_KEYS = ("violating_pairs_pure", "adjacent_pairs_pure", "violation_rate_pure")


def pure_fields(manifest_path: Path, pilot_path: Path) -> dict:
    """Pure-plan triple for one stored pilot, via the runner's own replay."""
    problem = lib_and_problem(manifest_path)
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    member = best_front_member(pilot)
    replay = replay_real(problem, member["starts"])
    return {k: replay[k] for k in PURE_KEYS}


def patch_units(units_path: Path, raw_root: Path) -> int:
    """Append the pure triple to every unit row in place; returns rows patched."""
    rows = json.loads(units_path.read_text(encoding="utf-8"))
    bak = units_path.with_suffix(units_path.suffix + ".bak")
    if not bak.exists():
        shutil.copyfile(units_path, bak)
    patched = 0
    for row in rows:
        if "error" in row:
            continue
        fam, seed = row["family"], row["seed"]
        pilot = raw_root / f"{fam}_seed{seed}" / f"pilot_{fam}_seed{seed}.json"
        man = V5 / "scenarios" / f"{fam}_seed{seed}.json"
        row.update(pure_fields(man, pilot))
        patched += 1
    units_path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return patched


def _family_block(xs: list) -> dict:
    """Legacy aggregates (summarize_7a style) + the new pure aggregates."""
    gaps = [u["coverage_gap_pp"] for u in xs]
    rates = [u["violation_rate"] for u in xs]
    vp = [u["violating_pairs"] for u in xs]
    ap_ = [u["adjacent_pairs"] for u in xs]
    rates_p = [u["violation_rate_pure"] for u in xs]
    vp_p = [u["violating_pairs_pure"] for u in xs]
    ap_p = [u["adjacent_pairs_pure"] for u in xs]
    return {
        "n_units": len(xs),
        "gap_pp_median": round(statistics.median(gaps), 2),
        "gap_pp_min": round(min(gaps), 2),
        "gap_pp_max": round(max(gaps), 2),
        "violation_rate_median": round(statistics.median(rates), 4),
        "violation_rate_min": round(min(rates), 4),
        "violation_rate_max": round(max(rates), 4),
        "violating_pairs_total": sum(vp),
        "adjacent_pairs_total": sum(ap_),
        "units_with_zero_violation": sum(1 for v in vp if v == 0),
        "violation_rate_pure_median": round(statistics.median(rates_p), 4),
        "violation_rate_pure_min": round(min(rates_p), 4),
        "violation_rate_pure_max": round(max(rates_p), 4),
        "violating_pairs_pure_total": sum(vp_p),
        "adjacent_pairs_pure_total": sum(ap_p),
        "units_with_zero_violation_pure": sum(1 for v in vp_p if v == 0),
    }


def rebuild_summary(units_by_arm: dict) -> None:
    """Keep the existing summary verbatim; add pure keys per family, and a
    top-level ``conservative`` section holding that arm's full aggregates."""
    summary = json.loads(SUMMARY.read_text(encoding="utf-8")) if SUMMARY.exists() else {}
    for fam in FAMILIES:
        xs = [u for u in units_by_arm["zero"] if u["family"] == fam]
        block = _family_block(xs)
        summary.setdefault(fam, {})
        summary[fam]["violation_rate_pure_median"] = block["violation_rate_pure_median"]
        summary[fam]["violation_rate_pure_min"] = block["violation_rate_pure_min"]
        summary[fam]["violation_rate_pure_max"] = block["violation_rate_pure_max"]
        summary[fam]["violating_pairs_pure_total"] = block["violating_pairs_pure_total"]
        summary[fam]["adjacent_pairs_pure_total"] = block["adjacent_pairs_pure_total"]
        summary[fam]["units_with_zero_violation_pure"] = block["units_with_zero_violation_pure"]
    summary["conservative"] = {
        fam: _family_block([u for u in units_by_arm["conservative"]
                            if u["family"] == fam])
        for fam in FAMILIES
    }
    SUMMARY.write_text(json.dumps(summary, indent=1), encoding="utf-8")


def main() -> int:
    units_by_arm: dict = {}
    for arm, raw_root, units_path in ARMS:
        n = patch_units(units_path, raw_root)
        print(f"# {arm}: patched {n} units in {units_path.relative_to(V5)}")
        units_by_arm[arm] = json.loads(units_path.read_text(encoding="utf-8"))
    rebuild_summary(units_by_arm)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))  # re-read for honest printout
    print("# zero arm (pure caliber):")
    for fam in FAMILIES:
        b = summary[fam]
        print(f"  {fam}: violating_pairs_pure_total={b['violating_pairs_pure_total']} "
              f"adjacent_pairs_pure_total={b['adjacent_pairs_pure_total']} "
              f"violation_rate_pure_median={b['violation_rate_pure_median']}")
    print("# conservative arm (pure caliber):")
    for fam in FAMILIES:
        b = summary["conservative"][fam]
        print(f"  {fam}: violating_pairs_pure_total={b['violating_pairs_pure_total']} "
              f"adjacent_pairs_pure_total={b['adjacent_pairs_pure_total']} "
              f"violation_rate_pure_median={b['violation_rate_pure_median']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
