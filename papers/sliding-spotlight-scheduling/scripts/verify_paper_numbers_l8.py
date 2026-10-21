#!/usr/bin/env python3
"""Ticket 50 (B4) -- L8 / caliber v5 manuscript-number ledger.

Why this file exists
--------------------
``verify_paper_numbers.py`` pins ``experiments/v3_results`` and takes no result
root, so after the paper moved to the L8 world (caliber v5, ticket 49) it kept
returning rc=0 without ever opening an L8 artifact.  "Green but irrelevant" is
worse than a failure because nothing reports it.  This ledger is the L8
counterpart: every number it checks is recomputed from ``experiments/v5_results``
and cross-checked against the per-unit pilots, and it refuses to pass when it
extracts nothing.

What it registers (ticket-50 amendment, analysis_prereg_v2.json)
---------------------------------------------------------------
  * MAIN RESULT FORM: the coverage-demand curve -- per family, the median
    served fraction over the frozen s grid {0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4,
    1.5, 2.0}, one value per s point, at the base budget 40/60.
  * FULFILLMENT RATIO: (i) library f_q, (ii) mean over ALL tie-set members
    (scripts/build_sweep_results.py:75-88), (iii) a REPORTED READING, not an
    optimization target.  A line stating the ratio must carry all three tags.
  * TIE-SET FACTS: every sweep unit is single-objective (n_obj=1), so a front's
    unique f1 count is 1 and "coverage passed/failed" has no meaning; the
    greedy anchor is coverage-optimal in 258 of 260 units.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/verify_paper_numbers_l8.py \
        [--paper paper/main.tex ...]

    Without --paper the tool prints the recomputed readings and exits 0
    (explicit readings-only mode: a banner names the mode, so an empty run can
    never look like a manuscript check).

rc:
  0  readings printed, or every extracted number reproduces
  1  at least one mismatch (the manuscript contradicts the L8 artifacts)
  2  extraction found nothing / the artifacts are unusable -- NOT a pass
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
SWEEP = V5 / "sweep"
AGGREGATE = V5 / "sweep_results.json"
FAMILIES = ("R1C", "R2F", "R3H")
S_GRID = (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0)
N_SEEDS = 10

# Tolerances are registered here, not scattered: a tolerance wider than the
# drift it must catch launders a mismatch into a pass
# (feedback-gate-tolerance-and-prose-extraction-gap).
TOL = {
    "fraction": 5e-3,   # a 3-dp rounding of a coverage / ratio reading
    "metre": 5e-4,      # 4-dp rounding of the STR floor
}


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def s_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def _units(fam: str, s: float) -> "list[Path]":
    return sorted((SWEEP / s_name(s)).glob(f"pilot_{fam}_seed*.json"))


def recompute() -> dict:
    """Recompute the L8 readings from the RAW units, then cross-check the
    aggregate.  Returns {key: (value, provenance)}.

    The cross-check matters: if ``sweep_results.json`` and the pilots disagree,
    every manuscript number derived from either is in doubt, and the tool must
    say so rather than pick one silently.
    """
    exp: dict = {}
    agg = _load(AGGREGATE)
    problems: list = []

    coverage: dict = {}
    fulfill: dict = {}
    exit11: dict = {}
    for fam in FAMILIES:
        for s in S_GRID:
            files = _units(fam, s)
            # exit-11 seeds have NO artifact and count as zero coverage -- a
            # recorded outcome, not missing data (build_sweep_results.py:139)
            n_missing = N_SEEDS - len(files)
            covs = [0.0] * n_missing + [
                _load(p)["max_f1_star_on_front"] for p in files]
            med = statistics.median(covs) if covs else None
            rec = agg["families"][fam][str(s)]
            if med is None or abs(med - rec["coverage_median"]) > 1e-12:
                problems.append(
                    f"{fam} s={s}: raw-unit median {med} != aggregate "
                    f"{rec['coverage_median']}")
            coverage[(fam, s)] = (med, f"median of {len(covs)} raw-unit "
                                       f"max_f1_star_on_front, exit-11 = 0")
            fulfill[(fam, s)] = (
                rec.get("f_q_fulfillment_ratio_median"),
                "sweep_results.f_q_fulfillment_ratio_median (library f_q, "
                "mean over the tie-set, build_sweep_results.py:75-88)")
            exit11[(fam, s)] = (n_missing,
                               "ledger exit-11 count (no artifact by design)")
    exp["coverage_median"] = coverage
    exp["fulfillment_median"] = fulfill
    exp["exit11"] = exit11

    # ---- tie-set facts (W9's anchor and the anchor-optimality reading) ------
    tie_units = vacuous = anchor_opt = 0
    search_wins: list = []
    for fam in FAMILIES:
        for s in S_GRID:
            for p in _units(fam, s):
                art = _load(p)
                if art["promotion"]["decision"] == "vacuous_single_objective":
                    vacuous += 1
                if len({round(r["f1_star"], 12) for r in art["front"]}) == 1:
                    tie_units += 1
                if abs(art["max_f1_star_on_front"] - art["anchor_f1_star"]) <= 1e-12:
                    anchor_opt += 1
                if art["max_f1_star_on_front"] > art["anchor_f1_star"] + 1e-12:
                    search_wins.append(f"{p.name}@{s}")
    exp["sweep_units"] = (sum(len(_units(f, s)) for f in FAMILIES for s in S_GRID),
                          "pilot artifacts under sweep/s*/")
    exp["matrix_units"] = (len(list((V5 / "matrix").glob("pilot_*.json"))),
                           "pilot artifacts under matrix/")
    exp["vacuous_units"] = (vacuous, "promotion.decision == vacuous_single_objective")
    exp["tie_set_units"] = (tie_units, "fronts whose unique f1 count is 1")
    exp["anchor_optimal_units"] = (anchor_opt,
                                   "max_f1_star_on_front == anchor_f1_star")
    exp["search_win_units"] = (sorted(search_wins),
                               "max_f1_star_on_front > anchor_f1_star")

    # ---- the STR library floor (B1's step disclaimer) ----------------------
    sys.path.insert(0, str(FORK))
    sys.path.insert(0, str(FORK.parents[1] / "src"))
    try:
        from sss_core.modes import Mode, ModeLibrary
        lib = ModeLibrary.from_fixture()
        exp["str_floor_m"] = (float(lib.rho_az(Mode.STR)),
                              "ModeLibrary.from_fixture().rho_az(Mode.STR)")
    except Exception as exc:                      # pragma: no cover
        exp["str_floor_m_abort"] = (str(exc), "sss_core import failed")

    exp["_aggregate_problems"] = (problems,
                                  "raw-unit vs sweep_results.json cross-check")
    return exp


# --------------------------------------------------------------------------
# Extraction from the manuscript
# --------------------------------------------------------------------------
_SENT_SPLIT = re.compile(r"(?<=[.;。；])\s+")
_NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(%?)")
_S_TAG = re.compile(r"\bs\s*=\s*(\d(?:\.\d)?)\b|订单原要求|order\s+point",
                    re.IGNORECASE)


def _family_in(sent: str):
    for fam in FAMILIES:
        if fam in sent:
            return fam
    return None


def _s_in(sent: str):
    m = _S_TAG.search(sent)
    if not m:
        return None
    if m.group(1):
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return 1.0                      # "订单原要求" / "order point" == s=1.0


def check_paper(text: str, label: str, exp: dict) -> "tuple[list, list, int]":
    fails: list = []
    passes: list = []
    seen = 0
    # Line scope is kept: the caliber tag must travel on the LINE that states
    # the number (W13/W15a's obligation), and collapsing newlines would let a
    # tag on a later line license the reading.
    for line in text.replace("\\_", "_").splitlines():
        line = re.sub(r"[ \t]+", " ", line)
        if not line.strip():
            continue
        for sent in _SENT_SPLIT.split(line):
            fam, s = _family_in(sent), _s_in(sent)
            # coverage reading: "R3H coverage at s = 1.0 reads 94.8%".  The
            # s-tag itself contains a number, so it is blanked before the
            # reading is taken -- otherwise the extractor would score the tag
            # against the curve (and, with an s-dependent curve, silently
            # "verify" itself).
            if fam and s is not None and re.search(r"coverage|覆盖", sent, re.I):
                idx = sent.lower().find("coverage")
                if idx == -1:
                    idx = sent.find("覆盖")
                tail = re.sub(r"\bs\s*=\s*\d(?:\.\d)?", " ", sent[idx:])
                m = re.search(r"(\d+(?:\.\d+)?)\s*(%?)", tail)
                if m:
                    printed = float(m.group(1))
                    if m.group(2):
                        printed /= 100.0
                    want, prov = exp["coverage_median"][(fam, s)]
                    seen += 1
                    _score(label, fails, passes, printed, want, TOL["fraction"],
                           f"{fam} coverage @ s={s}", prov, m.group(0))
            # fulfillment reading: the three-part tag is mandatory on the line.
            # The s-tag number is blanked first, for the same reason as above.
            fm = re.search(r"(?:fulfillment[-\s]?ratio|兑现率)[^;]{0,40}?"
                           r"(\d+(?:\.\d+)?)",
                           re.sub(r"\bs\s*=\s*\d(?:\.\d)?", " ", sent), re.I)
            if fm and fam and s is not None:
                printed = float(fm.group(1))
                want, prov = exp["fulfillment_median"][(fam, s)]
                seen += 1
                if want is not None:
                    _score(label, fails, passes, printed, want, TOL["fraction"],
                           f"{fam} fulfillment ratio @ s={s}", prov, fm.group(0))
            if fm:
                missing = [n for n, rx in (
                    ("library caliber", r"library[-\s]?caliber|库口径"),
                    ("tie-set mean", r"tie[-\s]?set|全体成员"),
                    ("reading, not a target",
                     r"not\s+an?\s+(?:optimization|optimisation)\s+target|"
                     r"报告读数|非优化目标|不进目标"),
                ) if not re.search(rx, line, re.I)]
                if missing:
                    fails.append(f"{label}: fulfillment-ratio reading lacks "
                                 f"caliber element(s) {missing}  [{line[:90]!r}]")
            # the STR floor (B1: a step, not a continuous degradation)
            sm = re.search(r"STR[^;]{0,60}?(?:floor|地板)[^;]{0,20}?"
                           r"(\d+(?:\.\d+)?)\s*m", sent, re.I)
            if sm and "str_floor_m" in exp:
                printed = float(sm.group(1))
                want, prov = exp["str_floor_m"]
                seen += 1
                _score(label, fails, passes, printed, want, TOL["metre"],
                       "STR library floor", prov, sm.group(0))
    return fails, passes, seen


def _score(label, fails, passes, printed, want, tol, what, prov, printed_raw):
    if want is None:
        fails.append(f"{label}: {what} has no registered L8 reading  [{prov}]")
        return
    delta = printed - float(want)
    if abs(delta) <= tol:
        passes.append(f"{label}: {what} = {printed}  [{prov}]")
    else:
        fails.append(f"{label}: manuscript {printed} vs recomputed {what}="
                     f"{want} (off by {delta:+.4g}, tol {tol})  [{prov}]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", action="append", default=None,
                    help="manuscript file(s) to check; omit for readings only")
    args = ap.parse_args(argv)

    if not AGGREGATE.is_file():
        print(f"ABORT: missing L8 aggregate {AGGREGATE}", file=sys.stderr)
        return 2
    try:
        exp = recompute()
    except Exception as exc:
        print(f"ABORT: could not recompute the L8 expectations: {exc}",
              file=sys.stderr)
        return 2

    problems, _ = exp["_aggregate_problems"]
    if problems:
        print("=== raw units and sweep_results.json DISAGREE ===")
        for p in problems:
            print(f"MISMATCH   {p}")
        print("VERDICT: the L8 artifact and its aggregate disagree -- no number "
              "derived from either can be trusted")
        return 1

    print("=== L8 / caliber v5 recomputed from experiments/v5_results ===")
    print(f"  sweep units      = {exp['sweep_units'][0]}")
    print(f"  matrix units     = {exp['matrix_units'][0]}")
    print(f"  vacuous units    = {exp['vacuous_units'][0]}")
    print(f"  tie-set units    = {exp['tie_set_units'][0]}")
    print(f"  anchor-optimal   = {exp['anchor_optimal_units'][0]}")
    print(f"  search-win units = {exp['search_win_units'][0]}")
    if "str_floor_m" in exp:
        print(f"  STR library floor= {exp['str_floor_m'][0]:.4f} m")
    for fam in FAMILIES:
        vals = ", ".join(
            f"s={s}: cov {exp['coverage_median'][(fam, s)][0]:.4f}"
            + (f" / ful {exp['fulfillment_median'][(fam, s)][0]:.4f}"
               if exp["fulfillment_median"][(fam, s)][0] is not None else "")
            for s in S_GRID)
        print(f"  {fam}: {vals}")

    if not args.paper:
        print("\nMODE: readings only (no --paper supplied) -- this is NOT a "
              "manuscript check")
        return 0

    papers = []
    for a in args.paper:
        p = Path(a)
        if not p.is_file():
            print(f"ABORT: manuscript {a} does not exist", file=sys.stderr)
            return 2
        papers.append(p)

    all_fail: list = []
    all_pass: list = []
    total = 0
    print("\n=== manuscript L8 numbers vs artifacts ===")
    for p in papers:
        fails, passes, seen = check_paper(
            p.read_text(encoding="utf-8", errors="ignore"), p.name, exp)
        all_fail += fails
        all_pass += passes
        total += seen
        print(f"  {p.name}: {seen} L8 number(s) checked, {len(fails)} mismatch(es)")

    print(f"\n=== RESULT: {len(all_fail)} mismatch(es) over {total} checked ===")
    for f in all_fail:
        print(f"FAIL   {f}")
    if total == 0:
        print("VERDICT: NO L8 NUMBERS WERE EXTRACTED -- an extraction failure, "
              "not a pass (the manuscript is still on the v3 world)")
        return 2
    if all_fail:
        print("VERDICT: the manuscript contradicts the L8 artifacts")
        return 1
    print(f"VERDICT: every checked L8 number reproduces ({len(all_pass)} verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
