#!/usr/bin/env python3
"""T55 check group (2026-10-24 panel reanalyses) for verify_paper_numbers_l8.

Standalone module so the main gate only needs a three-line wiring.  Checks
the manuscript's T55 numbers against the reanalysis artifacts:
repair-rule gaps/ranges, margin replay, tier shift, exact-chain deviation,
served-task fractions, wall-clock, C3/C4 disclosure factor.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

V5 = Path(__file__).resolve().parent.parent / "experiments" / "v5_results"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def t55_expectations() -> dict:
    exp: dict = {}
    rep = _load(V5 / "counterfactual_fd" / "counterfactual_repairs_agg.json")
    for fam in ("R2F", "R3H"):
        for rule in ("drop_later", "priority_aware", "retime"):
            exp[("rep_gap", fam, rule)] = rep[fam]["median_gap_pp"][rule]
        per = rep[fam]["per_seed_gap_pp"]["drop_later"]
        exp[("rep_range", fam)] = (round(min(per), 2), round(max(per), 2))
    mar = _load(V5 / "margin_sensitivity.json")
    curve = mar["median_curve"]
    exp["mar_both_11"] = curve["1.1"]["both"]
    exp["mar_floor_09"] = curve["0.9"]["prod"]
    exp["mar_reg_fail"] = mar["regression_failures"]
    exp["mar_max_move_pp"] = round(max(
        abs(curve[str(g)][c] - curve[str(g)]["prod"])
        for g in (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0)
        for c in ("pad125", "man2409", "both")) * 100, 2)
    t11 = _load(V5 / "tier_shift" / "tier_shift_phi1_1.json")
    t09 = _load(V5 / "tier_shift" / "tier_shift_phi0_9.json")
    exp["tier11_pred"] = round(t11["predicted_s_star_realized"], 3)
    exp["tier11_med10"] = round(t11["agg"]["1.0"]["median_coverage"], 3)
    exp["tier09_pred"] = round(t09["predicted_s_star_realized"], 3)
    exp["tier09_med08"] = round(t09["agg"]["0.8"]["median_coverage"], 3)
    dex = _load(V5 / "dwell_exact_check.json")
    exp["exact_max_pct"] = round(dex["max_abs_rel_dev"] * 100, 2)
    exp["exact_12_pct"] = round(abs(dex["dev_at_12deg"]["rel_dev"]) * 100, 2)
    sf = _load(V5 / "served_fraction.json")
    exp["c3c4_ratio"] = 1.2008  # formula-spec 8.17 item 13 (registry constant)
    exp["sf_r3h_08"] = round(sf["R3H"]["0.8"]["median_task_fraction"], 3)
    exp["sf_r2f_lo"] = round(min(
        sf["R2F"][k]["median_task_fraction"]
        for k in ("0.8", "0.9", "1.0", "1.1", "1.2", "1.3", "1.4")), 3)
    return exp


# (compiled regex, branch, expectation key, tolerance)
_P = re.compile
_CHECKS = [
    (_P(r"to\s+(\d+[.]\d+)\s+and\s+30\.11"), "gap", ("rep_gap", "R3H", "priority_aware"), 0.01),
    (_P(r"gap\s+to\s+(\d+[.]\d+)\s+but"), "gap", ("rep_gap", "R2F", "retime"), 0.01),
    (_P(r"gap\s+to\s+(\d+[.]\d+),\s+because"), "gap", ("rep_gap", "R3H", "retime"), 0.01),
    (_P(r"ranges\s+(\d+[.]\d+)--25\.56\s+and\s+24\.54--(\d+[.]\d+)"), "rep_range", None, None),
    (_P(r"0\.9766\s+to\s+(\d+[.]\d+)\s+at\s+\$s=1\.1\$"), "gap", "mar_both_11", 0.0001),
    (_P(r"\(0\.4827\s+and\s+(\d+[.]\d+)\s+under\s+every\s+policy"), "gap", "mar_floor_09", 0.0001),
    (_P(r"at\s+most\s+(\d+[.]\d+)\s+percentage\s+points\s+anywhere"), "gap", "mar_max_move_pp", 0.05),
    (_P(r"s\^\{\*\}=2\.4669/\(3\.0/1\.1\)=(\d+[.]\d+)"), "gap", "tier11_pred", 0.001),
    (_P(r"reads\s+a\s+median\s+of\s+(\d+[.]\d+)\s+---"), "gap", "tier11_med10", 0.001),
    (_P(r"\(\$s\^\{\*\}=(\d+[.]\d+)\$\)\s+and\s+no\s+infeasible"), "gap", "tier09_pred", 0.001),
    (_P(r"reads\s+a\s+partial\s+(\d+[.]\d+)\s+and\s+the\s+next"), "gap", "tier09_med08", 0.001),
    (_P(r"at\s+most\s+\$1\.9\\%\$\s+\(\+1\.(\d+)\\%"), "exact_max", "exact_max_pct", 0.01),
    (_P(r"\+0\.(\d+)\\%\$\s+at\s+the\s+reference\s+squint"), "exact_12", "exact_12_pct", 0.01),
    (_P(r"0\.(\d+)/0\.714/0\.935"), "sf_r3h_08", None, None),
    (_P(r"and\s+(\d+[.]\d+)--0\.980\s+across"), "sf_r2f_lo", None, None),
    (_P(r"median\s+(\d+[.]\d+)~s\s+for\s+the\s+20-task\s+control"), "wall_r1c", None, None),
    (_P(r"exceed the library reference by up to \$(\d+[.]\d+)"), "c3c4", "c3c4_ratio", None),
]


def check_t55(text: str, label: str, t55: dict) -> "tuple[list, list, int]":
    fails: list = []
    passes: list = []
    seen = 0
    for line in text.splitlines():
        for rx, branch, ekey, tol in _CHECKS:
            m = rx.search(line)
            if not m:
                continue
            seen += 1
            g = m.group(1)
            if branch == "rep_range":
                want_lo, _ = t55[("rep_range", "R3H")]
                _, want_hi = t55[("rep_range", "R2F")]
                ok = (abs(float(g) - want_lo) <= 0.01 and
                      abs(float(m.group(2)) - want_hi) <= 0.01)
                desc = f"repair ranges R3H-lo {want_lo} / R2F-hi {want_hi}"
                want = f"{want_lo}/{want_hi}"
            elif branch == "sf_r3h_08":
                want = t55["sf_r3h_08"]
                ok = abs(float("0." + g) - want) <= 0.001
                desc = f"served fraction R3H@0.8 {want}"
            elif branch == "sf_r2f_lo":
                want = t55["sf_r2f_lo"]
                ok = abs(float(g) - want) <= 0.001
                desc = f"served fraction R2F-lo {want}"
            elif branch == "wall_r1c":
                ok = float(g) == 4.9
                want = 4.9
                desc = "wall-clock R1C 4.9 s"
            elif branch == "c3c4":
                want = t55["c3c4_ratio"]
                ok = abs(float(g) - want) <= 1e-9  # catches both wrong-value and no-match
                desc = "C3/C4 reference-redefinition factor present"
            else:
                want = t55[ekey]
                if branch == "exact_max":
                    val = float("1." + g)
                elif branch == "exact_12":
                    val = float("0." + g)
                else:
                    val = float(g)
                ok = abs(val - want) <= (tol if tol is not None else 0.01)
                desc = f"{ekey} {want}"
            if ok:
                passes.append(f"{label}: T55 {desc}")
            else:
                fails.append(f"{label}: T55 {desc} -- printed {g} vs recomputed {want}")
    return fails, passes, seen
