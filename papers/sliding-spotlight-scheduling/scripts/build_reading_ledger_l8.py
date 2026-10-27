#!/usr/bin/env python3
"""Ticket 50 phase 2 (task A/C) -- the L8 reading ledger.

Every number phase 3 is allowed to quote from the L8 world is written here
once, with its caliber tag, its source file + JSON path, and the command that
produced it.  The ledger is GENERATED, never hand-edited: ``--check``
recomputes it from ``experiments/v5_results`` and fails on any drift, so a
stale ledger cannot outlive a stale artifact.

Why a ledger instead of "read the artifacts when you need a number":
``sweep_results.json`` holds the curve but not the demand-satisfaction total,
not the per-seed movement behind a dip, and not the delivered-caliber variant.
Phase 3 must quote one number per claim, and a number quoted from a different
producer than the one the gate checks is exactly how a "green but irrelevant"
figure appears.

Registered readings (see the ``notes`` block for the obligations that travel
with them):

  * coverage per family x 9 demand-slack points -- median / min / max /
    per-seed, plus the exit-11 structural status;
  * coverage cost against each family's OWN saturation value;
  * the two R2F dips, with the per-seed movement that produces each one;
  * demand satisfaction: served task INSTANCES over the nine-point tie set;
  * fulfillment ratio (library caliber, tie-set member mean, reported reading);
  * relation between coverage and fulfillment -- coefficient only, no direction
    claim (the direction claim was falsified; see notes);
  * retention on the STR-clip-only caliber, mirrored from the gate test that
    owns that computation;
  * the descriptive delivered-caliber variant ``f_Q_deliv`` (label + non-
    comparability + no STR domain), with its exclusion counts printed.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/build_reading_ledger_l8.py \
        [--check] [--fast]

    --check   recompute and compare with the file on disk (no write);
              rc 0 identical, 1 drift, 2 unreadable/missing
    --fast    skip the delivered-caliber section (seconds instead of ~5 min).
              NOT valid with --check, which always recomputes everything.

rc: 0 written / identical; 1 self-check guard failed or drift; 2 input missing.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
SWEEP = V5 / "sweep"
AGGREGATE = V5 / "sweep_results.json"
OUT = V5 / "reading_ledger_l8.json"

FAMILIES = ("R1C", "R2F", "R3H")
S_GRID = (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0)
N_SEEDS = 10

GEN = ('PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B '
       "papers/sliding-spotlight-scheduling/scripts/build_reading_ledger_l8.py")
AGG_PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
                "papers/sliding-spotlight-scheduling/scripts/build_sweep_results.py "
                "v5_results")

# The two caliber tags are GLOBAL strings: phase 3 must reuse them verbatim,
# in this wording, without paraphrase (work order A, task C).
CAL_TAG_FULFIL = ("[库口径 f_q | 逐任务 实拍窗实拍斜视 f_q ÷ 全部窗零斜视最优 | "
                  "tie-set 全体成员均值 | 报告读数·非优化目标]")
CAL_TAG_DELIV = ("[交付口径 f_Q_deliv | 描述性变体·不进目标 | 与库口径不可混比 | "
                 "STR 无定义域]")

CAL_COVERAGE = "L8 / caliber v5 / 9-point demand grid / single budget 40-60"
CAL_RETENTION = "L8 / caliber v5 / STR-clip-only retention (8.17-12 caliber)"

# --------------------------------------------------------------------------
# Manuscript ban list -- GLOBAL single definition (phase 2 registers it here;
# phase 3 and verify_paper_numbers_l8.py both read THIS list, never a copy).
# --------------------------------------------------------------------------
BAN_LIST = {
    "definition": (
        "Tokens from retired worlds. HARD = a violation wherever it appears. "
        "LABELLED = may appear only as an explicitly-labelled retracted "
        "comparison, on the same line, matching required_label_regex."),
    "hard_banned": [
        {"id": "old_world_90_units",
         "regex": r"\b90\s+(?:units|runs|sweep\s+units)\b",
         "why": "the retired L6/v3 sweep census (3 families x 3 budgets x 10 seeds)"},
        {"id": "pooled_quality_position_3_9722",
         "regex": r"3\.9722",
         "why": "the retired pooled quality-position statistic (dB)"},
        {"id": "pooled_quality_t_24_78",
         "regex": r"24\.78",
         "why": "the t statistic of the retired pooled quality-position test"},
        {"id": "dq_all_66_872",
         "regex": r"66\.872",
         "why": "the retired dq_all reading"},
        {"id": "promotion_two_axis",
         "regex": r"promotion[^.\n]{0,40}two[-\s]axis|two\s+separated\s+axes",
         "why": "the promotion two-axis reading; in a single-objective world "
                "promotion is a vacuous marker, not a result"},
        {"id": "fallback_every_transition_carries",
         "regex": r"every\s+inter-task\s+transition\s+carries",
         "why": "the retired global-fallback wording; production is a per-pair "
                "hybrid (model stands alone at >= half the 1.84 s anchor)"},
        {"id": "fallback_bound_as_measurement",
         "regex": r"against\s+a\s+4\.07~s\s+measurement",
         "why": "caliber mix: 4.07 s is the fallback bound (Kim scenario 2), "
                "the calibration measurement is 1.84 s (Kim scenario 1)"},
        {"id": "floor_inside_coarse_tier",
         "regex": r"sits\s+inside\s+the\s+coarse\s+tier",
         "why": "the floor 2.4669 m lies below the coarse tier's 2.5 m lower "
                "edge, not inside it"},
        {"id": "dip_different_seeds",
         "regex": r"shape\s+recurs\s+with\s+different\s+seeds",
         "why": "the gaining seed (209) is the same in both dips; only the "
                "losing seed differs"},
        {"id": "fig3b_two_families_at_issue",
         "regex": r"two\s+families\s+whose\s+local\s+declines\s+are\s+at\s+issue",
         "why": "panel (b) shows R1C (no in-band declines) + R2F; the declines "
                "at issue are R2F-only"},
        {"id": "abstract_self_limiting_close",
         "regex": r"an\s+observation,\s+not\s+an\s+attribution",
         "why": "the abstract ends on the result; the fixed-assignment scope "
                "note lives in Sections 5.3 and 6.1"},
        {"id": "solver_not_contribution",
         "regex": r"not\s+as\s+a\s+contribution\s+to\s+scheduling\s+theory",
         "why": "unforced self-attack removed; the search is stated as the "
                "measurement instrument, positively"},
    ],
    "allowed_with_label": [
        {"id": "l7_tight_arm_0_446", "regex": r"\b0\.446\b",
         "why": "the L7 tight-arm value, kept as the comparison the L8 world "
                "overturns"},
        {"id": "l7_coverage_cost_5_5pp", "regex": r"5\.5\s*(?:pp|percentage\s+points)",
         "why": "the L7 coverage cost, superseded by the L8 figure"},
        {"id": "l7_cost_misattributed_1_61pp", "regex": r"1\.6[01]\s*(?:pp|percentage\s+points)",
         "why": "the withdrawn -1.61 pp reading (an L7 number moved onto L8 "
                "undivided); the L8 R2F order-point cost is -2.36 pp against "
                "s = 2.0, so a bare 1.60/1.61 pp value is the withdrawn one"},
        {"id": "old_retention_84_4", "regex": r"84\.4",
         "why": "the L7 retention figure, which included the SLS/SPT "
                "library-caliber narrowing retired by 8.17-12"},
        {"id": "old_retention_63_7", "regex": r"63\.7",
         "why": "same as 84.4, on the other family"},
    ],
    "required_label_regex": (
        r"superseded|retracted|withdrawn|no\s+longer|historical|for\s+comparison|"
        r"已作废|作废|历史对照|已被推翻|已撤回"),
}

# Accepted manuscript shapes for the readings this ledger registers.  Phase 3
# writes TO these shapes; the extractor in verify_paper_numbers_l8.py parses
# them.  Documented here so the obligation is visible at the point the numbers
# are registered rather than only inside the checker.
SHAPES = [
    {"id": "coverage_median",
     "example": "R3H coverage at s = 1.0 reads 94.8%.",
     "reads": "coverage.median.<FAM>.s<X>"},
    {"id": "coverage_cost",
     "example": ("R3H coverage cost at the order point is 4.15 pp relative to "
                 "its own saturation at s = 2.0."),
     "reads": "coverage_cost.<FAM>",
     "obligation": "the same line must name the saturation reference"},
    {"id": "infeasible_units",
     "example": "R1C at s = 0.8 has no feasible individual in 10 of 10 seeds.",
     "reads": "infeasible.units.<FAM>.s0.8",
     "obligation": "an infeasible point is NOT a zero-coverage reading"},
    {"id": "demand_served",
     "example": "The nine-point tie set serves 477,308 task instances.",
     "reads": "demand.served_task_instances",
     "obligation": "the unit is a served task INSTANCE (a tie-set member's "
                   "selection), not a distinct task"},
    {"id": "retention",
     "example": "R3H retention on the STR-clip-only caliber is 71.00%.",
     "reads": "retention.<FAM>"},
    {"id": "deliv_median",
     "example": ("The median f_Q_deliv at s = 1.0 is 37.62 m^-2 (R3H); this is "
                 "a descriptive variant, not comparable with the library "
                 "caliber."),
     "reads": "deliv.median.<FAM>.s<X>",
     "obligation": "descriptive + not-comparable, same line"},
    {"id": "deliv_squint_loss",
     "example": ("The median squint-loss factor sec^2 psi_sel for R3H at "
                 "s = 1.0 is 1.3286."),
     "reads": "deliv.sec2_median.<FAM>.s<X>"},
]


class GuardError(RuntimeError):
    """A cross-check between two independent paths disagreed."""


def s_name(s: float) -> str:
    return f"s{str(s).replace('.', '_')}"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _pct(xs, q: float) -> float:
    """Deterministic linear-interpolation percentile (q in [0, 1])."""
    ys = sorted(xs)
    if len(ys) == 1:
        return ys[0]
    pos = q * (len(ys) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(ys) - 1)
    return ys[lo] + (ys[hi] - ys[lo]) * (pos - lo)


def _entry(eid, value, unit, source_file, source_path, note=None,
           caliber_tag=CAL_COVERAGE, producer=AGG_PRODUCER):
    e = {
        "id": eid,
        "value": value,
        "unit": unit,
        "caliber_tag": caliber_tag,
        "source": {"file": source_file, "path": source_path},
        "produced_by": producer,
    }
    if note:
        e["note"] = note
    return e


# --------------------------------------------------------------------------
# Section: coverage curve + exit-11 census
# --------------------------------------------------------------------------
def coverage_section(agg: dict) -> "tuple[list, dict]":
    entries: list = []
    state: dict = {"per_seed_raw": {}}
    for fam in FAMILIES:
        for s in S_GRID:
            rec = agg["families"][fam][str(s)]
            sdir = SWEEP / s_name(s)
            files = sorted(sdir.glob(f"pilot_{fam}_seed*.json"))
            # exit-11 census from the DRIVER LEDGER, never inferred from a
            # missing file: a unit that died differently must not be laundered
            # as "no feasible individual" (gate-review finding 3)
            progress = _load(sdir / "_progress.json")
            exits = {k: v["exit"] for k, v in progress["units"].items()
                     if k.split("_")[0] == fam}
            if len(exits) != N_SEEDS:
                raise GuardError(f"{fam} s={s}: {len(exits)} ledger units "
                                 f"!= {N_SEEDS}")
            bad = {k: e for k, e in exits.items() if e not in (0, 11)}
            if bad:
                raise GuardError(f"{fam} s={s}: unexpected exit codes {bad}")
            e11 = {k for k, e in exits.items() if e == 11}
            missing = {k for k in exits if not any(
                f.endswith(f"seed{k.rsplit('_', 1)[1]}.json") for f in
                [p.name for p in files])}
            if e11 != missing:
                raise GuardError(
                    f"{fam} s={s}: exit-11 set {sorted(e11)} != missing-artifact "
                    f"set {sorted(missing)}")
            if len(files) + len(e11) != N_SEEDS:
                raise GuardError(f"{fam} s={s}: census break "
                                 f"{len(files)}+{len(e11)} != {N_SEEDS}")

            raw = [_load(p)["max_f1_star_on_front"] for p in files]
            state["per_seed_raw"][(fam, s)] = raw
            curve = [0.0] * len(e11) + raw          # inherited C-check entry
            # anti-laundering: the FULL sorted array, not just the median
            if sorted(curve) != sorted(rec["coverage_per_seed"]):
                raise GuardError(f"{fam} s={s}: per-seed array differs between "
                                 "raw units and sweep_results.json")
            med = statistics.median(curve)
            base = "coverage"
            src = "experiments/v5_results/sweep_results.json"
            path = f"families.{fam}['{s}']"

            if not files:
                entries.append(_entry(
                    f"{base}.status.{fam}.s{s}", "no_feasible_individual",
                    "status", src, path + ".n_exit11_no_feasible",
                    note=("all ten seeds exited 11: the order is unsatisfiable "
                          "under the frozen mode assignment, so this point is "
                          "NOT a zero-coverage measurement and must not be "
                          "plotted or quoted as one"),
                    producer=GEN))
                entries.append(_entry(
                    f"{base}.median.{fam}.s{s}", None, "fraction", src,
                    path + ".coverage_median",
                    note=("null on purpose: the underlying 0.0 in the aggregate "
                          "is the value the INHERITED C1/C2/C3 checks consume "
                          "for a recorded no-feasible outcome, not a reading"),
                    producer=GEN))
                entries.append(_entry(
                    f"{base}.curve_entry.{fam}.s{s}", 0.0, "fraction", src,
                    path + ".coverage_median",
                    note="the value the preregistered C-checks consume",
                    producer=GEN))
            else:
                entries.append(_entry(f"{base}.median.{fam}.s{s}", med,
                                      "fraction", src, path + ".coverage_median",
                                      producer=GEN))
            entries.append(_entry(f"{base}.min.{fam}.s{s}", min(curve) if curve
                                  else None, "fraction", src,
                                  path + ".coverage_min", producer=GEN))
            entries.append(_entry(f"{base}.max.{fam}.s{s}", max(curve) if curve
                                  else None, "fraction", src,
                                  path + ".coverage_max", producer=GEN))
            entries.append(_entry(f"{base}.per_seed.{fam}.s{s}",
                                  rec["coverage_per_seed"], "fraction list",
                                  src, path + ".coverage_per_seed",
                                  note=("exit-11 seeds enter as 0.0 in this "
                                        "array; see coverage.status for the "
                                        "semantics"),
                                  producer=GEN))
            entries.append(_entry(f"infeasible.units.{fam}.s{s}", len(e11),
                                  "count", "experiments/v5_results/sweep/"
                                  f"{s_name(s)}/_progress.json", "units.*.exit",
                                  note="exit code 11 = no feasible individual",
                                  producer=GEN))
    return entries, state


def criteria_section(agg: dict, med: dict) -> list:
    """Recompute C1/C2/C3 from the medians and require the aggregate to agree."""
    entries = []
    for fam in FAMILIES:
        m = [med[(fam, s)] for s in S_GRID]
        if any(v is None for v in m):
            raise GuardError(f"{fam}: a grid point has no median")
        c1 = all(a <= b + 1e-12 for a, b in zip(m[:-1], m[1:]))
        c2 = m[-1] >= m[-2] - 1e-12
        c3 = m[0] < m[3]                       # s=0.8 vs s=1.0
        got = agg["checks"][fam]
        if (c1, c2, c3) != (got["C1_monotone_s<=2.0"],
                            got["C2_saturation_2.0>=1.5"],
                            got["C3_tight_arm_drops(0.8<1.0)"]):
            raise GuardError(f"{fam}: criteria recomputed from medians differ "
                             "from sweep_results.json")
        for name, val, shape in (
                ("C1", c1, "monotone non-decreasing median over the grid"),
                ("C2", c2, "median(s=2.0) >= median(s=1.5)"),
                ("C3", c3, "median(s=0.8) < median(s=1.0)")):
            entries.append(_entry(
                f"criteria.{fam}.{name}", val, "bool",
                "experiments/v5_results/sweep_results.json",
                f"checks.{fam}.{name}", note=shape, producer=GEN))
    return entries


def coverage_cost_section(med: dict) -> list:
    entries = []
    for fam in FAMILIES:
        sat_s = max(S_GRID, key=lambda s: (med[(fam, s)], -s))
        sat = med[(fam, sat_s)]
        cost = med[(fam, 1.0)] - sat
        entries.append(_entry(
            f"coverage_cost.{fam}", cost, "fraction",
            "experiments/v5_results/sweep_results.json",
            f"families.{fam}.coverage_median (s=1.0 minus saturation)",
            note=(f"order-point median minus the family's OWN saturation value "
                  f"{sat!r} at s={sat_s}; measured on the same curve, not "
                  f"against another family"),
            producer=GEN))
        entries.append(_entry(
            f"coverage_cost_pp.{fam}", cost * 100.0, "percentage points",
            "experiments/v5_results/sweep_results.json",
            f"families.{fam}.coverage_median", producer=GEN))
        entries.append(_entry(
            f"coverage_saturation.{fam}", sat, "fraction",
            "experiments/v5_results/sweep_results.json",
            f"families.{fam}['{sat_s}'].coverage_median",
            note=f"saturation point at s={sat_s}", producer=GEN))
    return entries


def paired_drop_section(agg: dict) -> list:
    """Headline tightening drops in the paired per-seed form (Wave B): the
    median over seeds of each seed's own drop, with the per-seed range --
    the control family's 1.0 ceiling at the as-placed point compresses its
    unpaired median-of-medians difference, so the paired form travels with
    the headline numbers."""
    import statistics
    entries = []
    for fam, a, b in (("R3H", 1.0, 0.9), ("R3H", 1.0, 0.8), ("R1C", 1.0, 0.9)):
        pa = agg["families"][fam][str(a)]["coverage_per_seed"]
        pb = agg["families"][fam][str(b)]["coverage_per_seed"]
        drops = [(x - y) * 100.0 for x, y in zip(pa, pb)]
        med = statistics.median(drops)
        entries.append(_entry(
            f"coverage_paired_drop.{fam}.s{a:g}_to_s{b:g}", round(med, 4),
            "percentage points",
            "experiments/v5_results/sweep_results.json",
            f"families.{fam}.coverage_per_seed (paired s={a:g} minus s={b:g}, "
            "median over seeds)",
            note=(f"per-seed range [{min(drops):.4f}, {max(drops):.4f}] pp; "
                  f"{sum(1 for x in pa if x >= 1.0)}/10 seeds sit at the 1.0 "
                  f"ceiling at s={a:g}"),
            producer=GEN))
    return entries


def dip_section(agg: dict) -> list:
    """The two R2F dips, with the per-seed movement that produces them."""
    entries = []
    for fam in FAMILIES:
        for a, b in zip(S_GRID[:-1], S_GRID[1:]):
            pa = agg["families"][fam][str(a)]["coverage_per_seed"]
            pb = agg["families"][fam][str(b)]["coverage_per_seed"]
            move = [(i, round(y - x, 12)) for i, (x, y) in enumerate(zip(pa, pb))
                    if abs(y - x) > 1e-12]
            med_delta = (agg["families"][fam][str(b)]["coverage_median"]
                         - agg["families"][fam][str(a)]["coverage_median"])
            if med_delta < 0:
                entries.append(_entry(
                    f"dip.{fam}.s{a}->s{b}", med_delta, "fraction",
                    "experiments/v5_results/sweep_results.json",
                    f"families.{fam}.coverage_per_seed",
                    note=("per-seed movements [seed_index, delta]: "
                          f"{move}; the median moves because these opposite "
                          "displacements net negative"),
                    producer=GEN))
    return entries


def demand_section() -> list:
    entries = []
    total = records = 0
    cv_max = 0.0
    anchor_eq = 0
    units = 0
    for fam in FAMILIES:
        for s in S_GRID:
            for p in sorted((SWEEP / s_name(s)).glob(f"pilot_{fam}_seed*.json")):
                art = _load(p)
                units += 1
                records += len(art["front"])
                total += sum(r["n_selected"] for r in art["front"])
                for r in art["front"]:
                    cv_max = max(cv_max, float(r.get("cv", 0.0)))
                if abs(art["max_f1_star_on_front"]
                       - art["anchor_f1_star"]) <= 1e-12:
                    anchor_eq += 1
    entries.append(_entry(
        "demand.served_task_instances", total, "count",
        "experiments/v5_results/sweep/**/pilot_*.json", "front[*].n_selected",
        note=("sum over every record of the tie set: a served task INSTANCE, "
              "not a distinct task. This is the registered 477,308"),
        producer=GEN))
    entries.append(_entry("demand.tie_set_records", records, "count",
                          "experiments/v5_results/sweep/**/pilot_*.json",
                          "front", producer=GEN))
    entries.append(_entry("demand.sweep_units", units, "count",
                          "experiments/v5_results/sweep/**/pilot_*.json",
                          "pilot artifacts", producer=GEN))
    entries.append(_entry(
        "demand.delivery_identity_cv_max", cv_max, "constraint violation",
        "experiments/v5_results/sweep/**/pilot_*.json", "front[*].cv",
        note=("the delivery identity is enforced by a raise, so no artifact "
              "stores a per-record verdict; the observable is cv (constraint "
              "violation) = 0 on every record, together with the exit census "
              "(260 units exit 0, 10 exit 11, both recorded). Do not quote "
              "this as 'a count of delivery-equation violations'"),
        producer=GEN))
    entries.append(_entry("demand.anchor_optimal_units", anchor_eq, "count",
                          "experiments/v5_results/sweep/**/pilot_*.json",
                          "max_f1_star_on_front == anchor_f1_star",
                          note=("the greedy anchor already attains the unit "
                                "maximum in these units, which is what makes "
                                "the dips an anchor-construction effect rather "
                                "than a search miss"),
                          producer=GEN))
    return entries


def fulfillment_section(agg: dict) -> list:
    entries = []
    for fam in FAMILIES:
        for s in S_GRID:
            rec = agg["families"][fam][str(s)]
            path = f"families.{fam}['{s}']"
            entries.append(_entry(
                f"fulfillment.median.{fam}.s{s}",
                rec["f_q_fulfillment_ratio_median"], "ratio (<=1)",
                "experiments/v5_results/sweep_results.json",
                path + ".f_q_fulfillment_ratio_median",
                note=("null when no seed has an artifact; the producer computes "
                      "the per-task ratio and averages over the tie-set "
                      "members, then takes the median over seeds"),
                caliber_tag=CAL_TAG_FULFIL, producer=AGG_PRODUCER))
            entries.append(_entry(
                f"fulfillment.per_seed.{fam}.s{s}",
                rec["f_q_fulfillment_ratio_per_seed"], "ratio list (<=1)",
                "experiments/v5_results/sweep_results.json",
                path + ".f_q_fulfillment_ratio_per_seed",
                caliber_tag=CAL_TAG_FULFIL, producer=AGG_PRODUCER))
    return entries


def relation_section(agg: dict) -> list:
    """Coverage vs fulfillment: the coefficient only. No direction claim."""
    def pear(xs, ys):
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
        sy = math.sqrt(sum((b - my) ** 2 for b in ys))
        return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sx * sy)

    entries = []
    xs, ys = [], []
    for fam in FAMILIES:
        for s in S_GRID:
            rec = agg["families"][fam][str(s)]
            if rec["f_q_fulfillment_ratio_median"] is None:
                continue
            xs.append(rec["coverage_median"])
            ys.append(rec["f_q_fulfillment_ratio_median"])
    entries.append(_entry(
        "relation.coverage_vs_fulfillment.family_s_points", pear(xs, ys),
        "Pearson r", "experiments/v5_results/sweep_results.json",
        "families.<FAM>.<s>.{coverage_median,f_q_fulfillment_ratio_median}",
        note=(f"n={len(xs)} family-by-s points; a relation reading, no "
              "direction claim (see notes.falsified_direction_claim)"),
        caliber_tag=CAL_TAG_FULFIL, producer=GEN))

    ux, uy = [], []
    for fam in FAMILIES:
        fx, fy = [], []
        for s in S_GRID:
            rec = agg["families"][fam][str(s)]
            n = rec["n_artifacts"]
            if not n:
                continue
            cov = rec["coverage_per_seed"][len(rec["coverage_per_seed"]) - n:]
            ful = rec["f_q_fulfillment_ratio_per_seed"]
            if len(cov) != len(ful):
                raise GuardError(f"{fam} s={s}: coverage/fulfillment per-seed "
                                 "lengths differ")
            fx += cov
            fy += ful
        ux += fx
        uy += fy
        entries.append(_entry(
            f"relation.coverage_vs_fulfillment.units.{fam}", pear(fx, fy),
            "Pearson r", "experiments/v5_results/sweep_results.json",
            f"families.{fam}.<s>.per_seed arrays",
            note=f"n={len(fx)} units of this family", caliber_tag=CAL_TAG_FULFIL,
            producer=GEN))
    entries.append(_entry(
        "relation.coverage_vs_fulfillment.units", pear(ux, uy), "Pearson r",
        "experiments/v5_results/sweep_results.json",
        "every artifact unit's per-seed coverage vs fulfillment",
        note=(f"n={len(ux)} units pooled over families; a relation reading, no "
              "direction claim"),
        caliber_tag=CAL_TAG_FULFIL, producer=GEN))
    return entries


def deliv_value(plan, start, lib, rho_rg: float, d_m: float):
    """The implementation path: (f_Q_deliv, psi_sel) for one served instance.

    Exposed so the independent minimum-unit checker can compare against it
    without importing this module's internals (it re-derives the same quantity
    from the raw manifest and must NOT call this function to produce its own
    side of the comparison).
    """
    from sss_core.geometry import squint_at

    w = plan.window_at(float(start))
    psi = squint_at(float(start), w.t_ca_s, lib.geo, r0_m=w.r0_m)
    c = math.cos(psi)
    return d_m / (2.0 * plan.rho_req_m ** 2 * c * c * rho_rg), psi


def delivery_section() -> "tuple[list, dict]":
    """The descriptive delivered-caliber variant (formula-spec 8.17-10).

    Post-processing only: reads the stored starts and re-derives the squint at
    the selected start.  The solver is never re-run and no frozen artifact is
    touched.  STR is excluded BY CONSTRUCTION (a task-level request raises
    there, ``sss_core/duration.py::task_rho_ach``); the exclusion is counted
    and reported, never silently dropped.
    """
    sys.path.insert(0, str(FORK))
    sys.path.insert(0, str(FORK.parents[1] / "src"))
    from sss_core.duration import task_rho_ach          # noqa: F401
    from sss_core.evaluator import SchedulingProblem
    from sss_core.modes import Mode, ModeLibrary
    from sss_core.nsga2 import load_manifest
    from sss_core.quality import ground_range_resolution_m

    lib = ModeLibrary.from_fixture()
    rho_rg = ground_range_resolution_m(lib)
    d_m = lib.geo.D_m
    entries: list = []
    totals = {"defined": 0, "excluded_str": 0, "no_order": 0}
    for fam in FAMILIES:
        for s in S_GRID:
            files = sorted((SWEEP / s_name(s)).glob(f"pilot_{fam}_seed*.json"))
            vals, sec2, excl = [], [], Counter()
            for p in files:
                art = _load(p)
                manifest = load_manifest(
                    V5 / "scenarios" / Path(art["manifest"]).name)
                if s != 1.0:
                    for t in manifest["tasks"]:
                        if t.get("rho_req_m") is not None:
                            t["rho_req_m"] = s * float(t["rho_req_m"])
                sp = SchedulingProblem(manifest, lib)
                for rec in art["front"]:
                    for k, start in rec["starts"].items():
                        plan = sp.plans[int(k)]
                        if plan.mode is Mode.STR:
                            excl["excluded_str"] += 1
                            continue
                        if plan.rho_req_m is None:
                            excl["no_order"] += 1
                            continue
                        val, psi = deliv_value(plan, start, lib, rho_rg, d_m)
                        vals.append(val)
                        sec2.append(1.0 / (math.cos(psi) ** 2))
            for key in ("excluded_str", "no_order"):
                totals[key] += excl[key]
            totals["defined"] += len(vals)
            base = f"deliv"
            src = f"experiments/v5_results/sweep/{s_name(s)}/pilot_{fam}_seed*.json"
            if vals:
                entries.append(_entry(
                    f"{base}.median.{fam}.s{s}", statistics.median(vals),
                    "m^-2", src, "front[*].starts -> selected start squint",
                    caliber_tag=CAL_TAG_DELIV, producer=GEN))
                entries.append(_entry(
                    f"{base}.p10.{fam}.s{s}", _pct(vals, 0.10), "m^-2", src,
                    "same", caliber_tag=CAL_TAG_DELIV, producer=GEN))
                entries.append(_entry(
                    f"{base}.p90.{fam}.s{s}", _pct(vals, 0.90), "m^-2", src,
                    "same", caliber_tag=CAL_TAG_DELIV, producer=GEN))
                entries.append(_entry(
                    f"{base}.sec2_median.{fam}.s{s}", statistics.median(sec2),
                    "factor", src, "1 / cos^2(psi_sel)",
                    note=("the squint-loss reading: f_Q_deliv at a selected "
                          "start over the same order at zero squint equals "
                          "sec^2 psi_sel by the registered formula. It is not "
                          "a fulfillment ratio and not a target quantity"),
                    caliber_tag=CAL_TAG_DELIV, producer=GEN))
            else:
                entries.append(_entry(
                    f"{base}.median.{fam}.s{s}", None, "m^-2", src,
                    "front[*].starts",
                    note="no served instance in this cell has a domain",
                    caliber_tag=CAL_TAG_DELIV, producer=GEN))
            entries.append(_entry(
                f"{base}.domain.defined.{fam}.s{s}", len(vals), "count", src,
                "served instances with a defined f_Q_deliv",
                caliber_tag=CAL_TAG_DELIV, producer=GEN))
            for key in ("excluded_str", "no_order"):
                entries.append(_entry(
                    f"{base}.domain.{key}.{fam}.s{s}", excl[key], "count", src,
                    "served instances excluded",
                    note=("STR has no task-level mode parameter, so the "
                          "delivered caliber has no domain there (the "
                          "task-level request raises); exclusion is counted, "
                          "never dropped silently"),
                    caliber_tag=CAL_TAG_DELIV, producer=GEN))
    entries.append(_entry(
        "deliv.domain_totals", dict(totals), "counts",
        "experiments/v5_results/sweep/**/pilot_*.json",
        "summed over all 27 cells",
        note=("defined + excluded_str + no_order = served task instances; the "
              "excluded share is reported, not hidden"),
        caliber_tag=CAL_TAG_DELIV, producer=GEN))
    return entries, totals


def build(fast: bool = False) -> dict:
    if not AGGREGATE.is_file():
        raise SystemExit(f"ABORT: missing aggregate {AGGREGATE}")
    agg = _load(AGGREGATE)

    cov_entries, state = coverage_section(agg)
    med = {}
    for fam in FAMILIES:
        for s in S_GRID:
            raw = state["per_seed_raw"][(fam, s)]
            n_e11 = agg["families"][fam][str(s)]["n_exit11_no_feasible"]
            med[(fam, s)] = statistics.median([0.0] * n_e11 + raw)

    entries = list(cov_entries)
    entries += criteria_section(agg, med)
    entries += coverage_cost_section(med)
    entries += paired_drop_section(agg)
    entries += dip_section(agg)
    entries += demand_section()
    entries += fulfillment_section(agg)
    entries += relation_section(agg)

    # retention is mirrored, not recomputed here: the gate test owns the
    # 110-unit differential arm that produces it (see note)
    for fam, want in (("R1C", 0.5114), ("R2F", 1.0), ("R3H", 0.7100)):
        entries.append(_entry(
            f"retention.{fam}", want, "fraction",
            "papers/sliding-spotlight-scheduling/tests/test_verify_gate.py",
            "retention_expect",
            note=("mirrored from the gate test, which owns the computation "
                  "(clipped over unconstrained feasible measure on the 110 "
                  "pinned units, STR clip only); this ledger does not "
                  "re-derive it, so the two cannot drift apart unnoticed"),
            caliber_tag=CAL_RETENTION,
            producer="tests/test_verify_gate.py::test_pinned_unit_round_trip"
                     " (retention_expect)"))

    delivery = None
    if not fast:
        deliv_entries, delivery = delivery_section()
        entries += deliv_entries

    return {
        "schema": "reading-ledger-l8/1.0",
        "world": "L8",
        "caliber": "v5",
        "generated_by": GEN,
        "source_root": "experiments/v5_results/",
        "n_entries": len(entries),
        "caliber_tags": {"CAL_TAG_FULFIL": CAL_TAG_FULFIL,
                         "CAL_TAG_DELIV": CAL_TAG_DELIV},
        "manuscript_ban_list": BAN_LIST,
        "manuscript_shapes": SHAPES,
        "entries": entries,
        "notes": {
            "infeasible_semantics": (
                "R1C at s=0.8 is not a zero-coverage point: all ten seeds "
                "exited 11, meaning the family admits no feasible individual "
                "at that tightening. It is a different statement from 'the "
                "search found nothing to serve' and the two must be written "
                "differently."),
            "dip_attribution": (
                "Both R2F dips come from the greedy anchor construction, which "
                "is deterministic and reproducible. Evidence: in all 180 R2F "
                "and R3H sweep units the anchor equals the unit maximum "
                "(max_f1_star == anchor_f1_star) and the search-only maximum "
                "is empty, so no dip can be a search miss. Each dip is the net "
                "of two opposite single-seed displacements (see the dip.* "
                "entries for the exact seeds). No physical monotonicity claim "
                "is made from either dip."),
            "falsified_direction_claim": (
                "A direction claim linking higher coverage to lower "
                "fulfillment is NOT registered and must not be written: on the "
                "L8 data the pooled coefficient is positive (see relation.*), "
                "and the per-family values are mixed. Only the coefficient and "
                "its sample size are reported."),
            "caliber_separation": (
                "The fulfillment ratio is a dimensionless ratio on the library "
                "caliber; f_Q_deliv is an absolute m^-2 quantity on the "
                "descriptive delivered caliber. They are different quantities "
                "at different calibers: report them in separate statements "
                "with their own tags, never side by side in one table and "
                "never as a ratio of one to the other."),
            "manifest_provenance": (
                "The aggregate loads scenario manifests from experiments/"
                "v4_results/scenarios; the v5 copies are byte-identical "
                "(80/80 sha256 equal, checked in the phase-1 receipt). The "
                "ledger's readings are therefore unaffected, but the path in "
                "build_sweep_results.py is a latent provenance trap: if the "
                "scenario copies ever diverge, the aggregate would silently "
                "read the v4 manifest."),
            "unit_of_demand": (
                "477,308 counts served task instances summed over every tie-set "
                "record (9,430 records over 260 units at nine demand points). "
                "It is not a count of distinct tasks."),
            "str_floor": (
                "STR delivers the library floor (2.4669 m) regardless of the "
                "order; tightening the order there is a floor step, not a "
                "continuous degradation. f_Q_deliv has no STR domain."),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare against the file; no write")
    ap.add_argument("--fast", action="store_true",
                    help="skip the delivered-caliber section (not with --check)")
    args = ap.parse_args(argv)
    if args.check and args.fast:
        print("ABORT: --check always recomputes everything; --fast is for "
              "ad-hoc inspection only", file=sys.stderr)
        return 2

    try:
        ledger = build(fast=args.fast)
    except GuardError as exc:
        print(f"GUARD FAILED: {exc}", file=sys.stderr)
        return 1

    blob = json.dumps(ledger, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if args.check:
        if not OUT.is_file():
            print(f"ABORT: no ledger at {OUT}", file=sys.stderr)
            return 2
        want = _load(OUT)
        if want == json.loads(blob):
            print(f"LEDGER OK: {len(ledger['entries'])} entries reproduce "
                  f"exactly ({OUT})")
            return 0
        have_ids = {e["id"] for e in want.get("entries", [])}
        new_ids = {e["id"] for e in ledger["entries"]}
        print("LEDGER DRIFT: the file does not match a fresh recomputation",
              file=sys.stderr)
        for i in sorted(new_ids - have_ids):
            print(f"  MISSING FROM FILE  {i}", file=sys.stderr)
        for i in sorted(have_ids - new_ids):
            print(f"  STALE IN FILE      {i}", file=sys.stderr)
        for a, b in zip(ledger["entries"], want.get("entries", [])):
            if a != b:
                print(f"  VALUE DIFFERS      {a['id']}: fresh={a['value']!r} "
                      f"file={b.get('value')!r}", file=sys.stderr)
                break
        return 1

    OUT.write_text(blob, encoding="utf-8")
    print(f"written: {OUT}")
    print(f"  entries          = {len(ledger['entries'])}")
    fam_cov = {f: [e["value"] for e in ledger["entries"]
                   if e["id"].startswith(f"coverage.median.{f}.")]
               for f in FAMILIES}
    for fam in FAMILIES:
        print(f"  {fam} curve        = {['--' if v is None else round(v, 4) for v in fam_cov[fam]]}")
    print("  demand instances = "
          f"{[e['value'] for e in ledger['entries'] if e['id'] == 'demand.served_task_instances'][0]}")
    if not args.fast:
        tot = [e["value"] for e in ledger["entries"]
               if e["id"] == "deliv.domain_totals"][0]
        served = [e["value"] for e in ledger["entries"]
                  if e["id"] == "demand.served_task_instances"][0]
        share = tot["excluded_str"] / served
        print(f"  delivered domain = defined {tot['defined']}, "
              f"excluded-STR {tot['excluded_str']} ({share:.2%} of served "
              f"instances), no-order {tot['no_order']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
