#!/usr/bin/env python3
"""Ticket 30 (g): machine anchor for the v3 real-window verdicts.

Audit4 B8 found that ``claim_trace.json`` carries no experimental numbers at
all -- ALIVE/DEAD, no_promotion, MDE and delta are all recomputable but none
of them has a drift gate.  This script is that gate: it recomputes every
paper-level reading of the real-window world from the PROMOTED artifacts in
``experiments/v3_results/`` and asserts the registered value.

Read-only.  Touches nothing under ``experiments/``.

CALIBER (inherited from ``recompute_r_fam.py``, ticket 23, and ticket 28's
per-window reference fix):

  * R_fam = max-min of unenforced ``aasr_direct_db`` over
    task x 11 in-window starts x routed mode x the task's own registered
    production PRF, sampling PER WINDOW (each enumerated transit has its own
    zero and slant range), out-of-domain samples excluded;
  * every consumed f_q is the raw R-family quantity (NOT normalised -- the
    R family expands per-window R0 so f_q ranges 31-111 against the M family's
    [0,1]); cross-family and cross-caliber mixing is forbidden;
  * the front is filtered at cv <= 1e-9 before every richness count, the same
    caliber CALIBRATION_PREREG used, because front_size == pop_size is
    duplicate-target survival under ULP-level non-domination, not richness.

Every expectation below is HARDCODED here, never read out of the artifacts
under test: a verifier that copies its expectations from its subject verifies
nothing.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_v3_verdicts.py

rc:
  0  every registered reading reproduces
  1  drift (an artifact moved under a registered verdict)
  2  missing artifacts / unusable environment
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK.parent.parent / "src"))

V3 = FORK / "experiments" / "v3_results"
TIERS = ("matrix", "matrix_p80g120", "matrix_p160g240")
BASE, MID, TOP = TIERS

# --- registered expectations (ticket 30 item g; audit4 B8) ----------------
R_FAM_BASE = {"R1C": 3.9998, "R2F": 9.7524, "R3H": 11.9886}      # +-0.02 dB
R_FAM_MAX = {"R1C": 3.9998, "R2F": 12.1261, "R3H": 11.9886}      # +-0.02 dB
# R2F per-seed MIN is 8.2652 dB and must NOT be mistaken for the base-seed or
# the max reading; the three aggregates are different numbers and this gate
# pins all of them so a future run cannot quietly swap them.
R_FAM_PER_SEED_MIN = {"R1C": 3.9968, "R2F": 8.2652, "R3H": 9.3293}
BASE_SEEDS = {"R1C": 100, "R2F": 200, "R3H": 300}
PROMOTION_SPREAD_MAX_DB = 3.98        # <= 3.98; measured 3.9722
R3H_FRONT_MED = {"matrix": 1.0, "matrix_p160g240": 140.0}       # +-0.5
R3H_DISTINCT_FQ_MED = {"matrix": 1.0, "matrix_p160g240": 99.0}  # +-0.5
R1C_ANCHOR_F1 = 1.0                   # exactly, all 30 units
R1C_BASE_FRONT_MIN, R1C_BASE_FRONT_MAX = 28, 40   # base tier only
DELTA_DB = 6.0                        # registered R-family effect size
MDE80 = {"R2F": 4.87, "R3H": 13.87}   # +-0.01
DQ_SD = {"R2F": 5.67, "R3H": 16.14}   # +-0.01
POWER_AT_DELTA = {"R2F": 0.92, "R3H": 0.29}        # +-0.01
R3H_SEEDS_FOR_80PCT = 54             # cost anchor, not executed
N_SEEDS = 10
T_CRIT_95_DF9 = 1.8331                # one-sided alpha 0.05, df = n-1 = 9
T_CRIT_80_DF9 = 0.8834

_fails: list[str] = []
_n = 0


def check(name: str, got, expect, tol: float = 0.0) -> None:
    global _n
    _n += 1
    if isinstance(expect, bool):
        ok = got is expect
    elif isinstance(expect, (int, float)):
        ok = got is not None and abs(float(got) - float(expect)) <= tol
    else:
        ok = got == expect
    if not ok:
        _fails.append(f"{name}: got {got!r}, registered {expect!r} (tol {tol})")
    print(f"{'PASS' if ok else 'FAIL'}   {name:52} got={got!r} want={expect!r}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def front_of(art: dict) -> list:
    return [r for r in art["front"] if abs(r["cv"]) <= 1e-9]


def distinct_fq(art: dict) -> int:
    return len({round(r["f_q"], 6) for r in front_of(art)})


def dq_all(art: dict):
    """The prereg estimand: max f_q over the front minus the anchor point's."""
    f1a = art["anchor_f1_star"]
    afq = None
    for r in art["front"]:
        if abs(r["f1_star"] - f1a) <= 1e-9:
            afq = r["f_q"]
    if afq is None or not art["front"]:
        return None
    return max(r["f_q"] for r in art["front"]) - afq


def main() -> int:
    try:
        from sss_core.modes import ModeLibrary
        from scripts.recompute_r_fam import family_r
    except Exception as exc:                                    # pragma: no cover
        print(f"ABORT: cannot load the domain library: {exc}", file=sys.stderr)
        return 2
    try:
        from scipy import stats as scipy_stats
    except Exception as exc:                                    # pragma: no cover
        print(f"ABORT: scipy is required for the power checks: {exc}",
              file=sys.stderr)
        return 2

    scen = V3 / "scenarios"
    for d in (scen, *(V3 / t for t in TIERS)):
        if not d.is_dir():
            print(f"ABORT: missing artifact directory {d}", file=sys.stderr)
            return 2

    lib = ModeLibrary.from_fixture()

    print("=== structural dimension R_fam (per-task r0, per-window sampling) ===")
    for code, seed in BASE_SEEDS.items():
        per_seed = {}
        for p in sorted(scen.glob(f"{code}_seed*.json")):
            r_s, _, _ = family_r(load(p), lib)
            per_seed[p.stem] = r_s
        base = per_seed[f"{code}_seed{seed}"]
        check(f"R_fam_{code}_base_seed{seed}", round(base, 4),
              R_FAM_BASE[code], tol=0.02)
        check(f"R_fam_{code}_max_over_seeds", round(max(per_seed.values()), 4),
              R_FAM_MAX[code], tol=0.02)
        check(f"R_fam_{code}_per_seed_min_not_the_reading",
              round(min(per_seed.values()), 4), R_FAM_PER_SEED_MIN[code], tol=0.02)
        check(f"R_fam_{code}_verdict_base_is_{'ALIVE' if R_FAM_BASE[code] >= DELTA_DB else 'DEAD'}",
              "ALIVE" if base >= DELTA_DB else "DEAD",
              "ALIVE" if R_FAM_BASE[code] >= DELTA_DB else "DEAD")

    print("\n=== promotion: no_promotion over all 90 units, spread below the "
          "registered threshold ===")
    spreads, decisions, n_units = [], [], 0
    for tier in TIERS:
        for p in sorted((V3 / tier).glob("pilot_*.json")):
            a = load(p)
            spreads.append(a["promotion"]["spread_db"])
            decisions.append(a["promotion"]["decision"])
            n_units += 1
    check("promotion_units", n_units, 90)
    check("promotion_all_no_promotion", sorted(set(decisions)),
          ["no_promotion"], tol=0.0)
    check("promotion_max_spread_db_below_threshold",
          round(max(spreads), 4) <= PROMOTION_SPREAD_MAX_DB, True,
          tol=0.0)

    print("\n=== R3H richness at the base and top budget (the search-artifact "
          "signature) ===")
    for tier in (BASE, TOP):
        arts = [load(p) for p in sorted((V3 / tier).glob("pilot_R3H_seed*.json"))]
        check(f"R3H_front_median_{tier}", statistics.median(len(front_of(a))
                                                           for a in arts),
              R3H_FRONT_MED[tier], tol=0.5)
        check(f"R3H_distinct_fq_median_{tier}",
              statistics.median(distinct_fq(a) for a in arts),
              R3H_DISTINCT_FQ_MED[tier], tol=0.5)

    print("\n=== R1C control: the anchor saturates at every budget ===")
    anchors, base_fronts = [], []
    for tier in TIERS:
        for p in sorted((V3 / tier).glob("pilot_R1C_seed*.json")):
            a = load(p)
            anchors.append(a["anchor_f1_star"])
            if tier == BASE:
                base_fronts.append(len(front_of(a)))
    check("R1C_units", len(anchors), 30)
    check("R1C_anchor_f1_star_all_exactly_one", all(x == 1.0 for x in anchors),
          True, tol=0.0)
    check("R1C_base_tier_front_min", min(base_fronts), R1C_BASE_FRONT_MIN)
    check("R1C_base_tier_front_max", max(base_fronts), R1C_BASE_FRONT_MAX)

    print("\n=== registered effect size and its power (top budget, n=10) ===")
    check("registered_delta_db", DELTA_DB, 6.0)
    t_sum = T_CRIT_95_DF9 + T_CRIT_80_DF9
    for code in ("R2F", "R3H"):
        arts = [load(p) for p in sorted((V3 / TOP).glob(f"pilot_{code}_seed*.json"))]
        dq = [dq_all(a) for a in arts]
        check(f"{code}_dq_all_all_defined", None not in dq, True, tol=0.0)
        sd = statistics.stdev(dq)
        check(f"{code}_dq_all_sd", round(sd, 2), DQ_SD[code], tol=0.01)
        mde = t_sum * sd / math.sqrt(N_SEEDS)
        check(f"{code}_mde80", round(mde, 2), MDE80[code], tol=0.01)
        pw = 1 - scipy_stats.nct.cdf(
            T_CRIT_95_DF9, N_SEEDS - 1, DELTA_DB / (sd / math.sqrt(N_SEEDS)))
        check(f"{code}_power_at_delta", round(pw, 2), POWER_AT_DELTA[code],
              tol=0.01)
    r3h_sd = statistics.stdev(
        [dq_all(a) for a in
         (load(p) for p in sorted((V3 / TOP).glob("pilot_R3H_seed*.json")))])
    check("R3H_seeds_for_80pct_power_at_delta",
          math.ceil((t_sum * r3h_sd / DELTA_DB) ** 2), R3H_SEEDS_FOR_80PCT)

    print(f"\n=== RESULT: {len(_fails)} failure(s) over {_n} checks ===")
    for f in _fails:
        print(f"FAIL   {f}")
    if _fails:
        print("VERDICT: the v3 real-window artifacts have DRIFTED from the "
              "registered verdicts -- do not cite them")
        return 1
    print("VERDICT: the v3 real-window verdicts reproduce from the promoted "
          "artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())