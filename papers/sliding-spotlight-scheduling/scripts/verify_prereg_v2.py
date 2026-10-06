#!/usr/bin/env python3
"""Check the prereg v2 freeze against the frozen artifacts.

Distinct from ``verify_ticket22_adjudications.py``, which validates the
TICKET-22 ADJUDICATION (a historical record: it correctly still reflects the
n=30 stratum that note assumed).  This script validates the FREEZE, whose
operative stratum is n=20 because the freeze's own rule puts M2WF in the
structural-null layer.

Read-only: touches nothing under ``experiments/results/``.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_prereg_v2.py

rc:
  0  every registered number reproduces
  1  drift (the freeze is stale -- do not run the experiment against it)
  2  missing artifacts
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

from scipy import stats  # noqa: E402

RESULTS = FORK / "experiments" / "results"
MATRIX = RESULTS / "matrix"
FREEZE = FORK / "experiments" / "analysis_prereg_v2.json"

_fails: list[str] = []
_n = 0


def check(name, got, expect, tol=0.0):
    global _n
    _n += 1
    if isinstance(expect, (int, float)) and not isinstance(expect, bool):
        ok = got is not None and abs(float(got) - float(expect)) <= tol
    else:
        ok = got == expect
    if not ok:
        _fails.append(f"{name}: got {got!r}, expected {expect!r}")
    print(f"{'PASS' if ok else 'FAIL'}   {name:44} got={got!r} want={expect!r}")


def dq_all_of(art: dict):
    """max f_q over the front minus the anchor point's f_q (None if evicted)."""
    f1a = art["anchor_f1_star"]
    afq = None
    for r in art["front"]:
        if abs(r["f1_star"] - f1a) <= 1e-9:
            afq = r["f_q"]
            break
    if afq is None:
        return None
    return max(r["f_q"] for r in art["front"]) - afq


def main() -> int:
    if not FREEZE.is_file():
        print(f"ABORT: no freeze at {FREEZE}", file=sys.stderr)
        return 2
    if not MATRIX.is_dir():
        print(f"ABORT: no matrix artifacts at {MATRIX}", file=sys.stderr)
        return 2
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    pc = freeze["tests"]["primary_comparison"]

    arts = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(MATRIX.glob("pilot_*.json"))]

    print("=== A3 root cause: the coverage comparison is structurally guaranteed")
    units = len(arts)
    ties = sum(
        1 for a in arts
        if abs(a["max_f1_star_on_front"] - a["anchor_f1_star"]) <= 1e-12
    )
    check("units", units, 50)
    check("exact_ties", ties, 49)

    print("\n=== dq_all (the accepted estimand) ===")
    by_fam: dict[str, list[float]] = {}
    lost = 0
    for a in arts:
        code = Path(a["manifest"]).name.rsplit("_seed", 1)[0]
        v = dq_all_of(a)
        if v is None:
            lost += 1
            continue
        by_fam.setdefault(code, []).append(v)
    usable = sum(len(v) for v in by_fam.values())
    nonzero = sum(1 for v in by_fam.values() for x in v if x > 1e-12)
    check("usable_units", usable, 49)
    check("anchor_evicted_units", lost, 1)
    check("dq_all_nonzero", nonzero, 20)
    allv = [x for v in by_fam.values() for x in v]
    check("dq_all_sd", round(statistics.stdev(allv), 3), 0.940, tol=1e-3)

    print("\n=== the freeze's stratum rule, applied as written ===")
    # rule: structural-null iff (all-STR degenerate-anchor family) OR
    #       (median distinct_fq < 2 at the registered base seed/budget)
    med_dq = {}
    for a in arts:
        code = Path(a["manifest"]).name.rsplit("_seed", 1)[0]
        med_dq.setdefault(code, []).append(
            len({round(r["f_q"], 6) for r in a["front"]})
        )
    primary, null = [], []
    for code in sorted(med_dq):
        m = statistics.median(med_dq[code])
        (null if (code.endswith("NC") or m < 2) else primary).append(code)
    check("structural_null_families", null, ["M1NC", "M2WF", "M3NC"])
    check("primary_families", primary, ["M2WH", "M4WH"])
    # the freeze must REGISTER the rule that produced that outcome, and the
    # rule text must be the one the check just applied -- otherwise a gutted
    # rule leaves every downstream number green (measured: it did)
    # Round-3 review finding: `"2" in rule` is satisfied by "20", so a rule
    # with a DIFFERENT threshold stayed green. Parse the number instead.
    import re as _re
    rule = pc["stratum_rule"]
    check("rule_states_both_clauses",
          1 if ("degenerate-anchor" in rule and "distinct_fq" in rule) else 0, 1)
    thr = _re.search(r"distinct_fq\s*<\s*(\d+)", rule)
    check("rule_threshold_is_parseable", 1 if thr else 0, 1)
    check("rule_threshold_value", int(thr.group(1)) if thr else -1, 2)

    pooled = [v for c in primary for v in by_fam[c]]
    check("primary_pooled_n", len(pooled), 20)
    sd = statistics.stdev(pooled)
    check("primary_pooled_sd", round(sd, 5), 0.88042, tol=1e-4)
    mde = (stats.t.ppf(0.95, len(pooled) - 1)
           + stats.t.ppf(0.80, len(pooled) - 1)) * sd / math.sqrt(len(pooled))
    check("mde_80pct", round(mde, 4), 0.5099, tol=1e-3)

    print("\n=== the freeze must not still claim the superseded n=30 stratum ===")
    blob = json.dumps(freeze, ensure_ascii=False)
    check("superseded_note_is_labelled",
          1 if "superseded ticket-22 note" in blob else 0, 1)
    check("consumed_gates_scope_is_narrowed",
          1 if "does NOT validate this freeze" in blob else 0, 1)

    print("\n=== every prediction must carry a refutation ===")
    preds = freeze["predictions"]
    for key in ("P1_front_richness", "P2_quality_headroom", "P3_promotion"):
        check(f"{key}_has_refutation",
              1 if preds[key].get("refutation") else 0, 1)
    check("P4_has_a_refutation",
          1 if preds["P4_capacity"].get("refutation") else 0, 1)
    check("P4_registers_a_serial_bound",
          1 if preds["P4_capacity"].get("quantity")
          and "serial_bound" in json.dumps(freeze["capacity_artifacts"])
          else 0, 1)
    check("unconverged_is_not_refuted",
          1 if "NOT-YET-TESTED" in preds["P1_front_richness"]["critical_caveat"]
          else 0, 1)
    # the serial bound is a registered artifact, not a prose promise
    sb = freeze["capacity_artifacts"]["serial_bound_derivation"][
        "measured_v1_synthetic_families"]
    # Expectations hardcoded, never read out of the freeze under test (same
    # doctrine as verify_v3_verdicts).  The previous round(val,4) vs val
    # compared the freeze to itself and could not see value drift
    # (round-2 pre-writing review, 2026-10-06).
    serial_bound_expected = {
        "M1NC": 0.3435, "M2WF": 0.0372, "M2WH": 0.0303,
        "M3NC": 0.0186, "M4WH": 0.0142,
    }
    check("serial_bound_families_registered", len(sb),
          len(serial_bound_expected))
    for fam, expected in serial_bound_expected.items():
        check(f"serial_bound_{fam}", sb.get(fam), expected, tol=1e-9)

    print(f"\n=== RESULT: {len(_fails)} failure(s) over {_n} checks ===")
    for f in _fails:
        print(f"FAIL   {f}")
    if _fails:
        print("VERDICT: the freeze has DRIFTED from the artifacts -- do not "
              "run the experiment against it")
        return 1
    print("VERDICT: the freeze reproduces from the frozen artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())