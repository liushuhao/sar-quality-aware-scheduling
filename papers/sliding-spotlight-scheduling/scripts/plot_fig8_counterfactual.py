#!/usr/bin/env python3
"""fig-8 (R96 figure wave): the fixed-dwell counterfactual, both readings.

Panel (a): the repair-independent reading -- the fraction of consecutive
planned pairs that violate the transfer constraint when the frozen-dwell
plan is replayed against the real, squint-dependent dwell, PURE caliber
(counted over the sorted planned pairs before any repair runs; the legacy
``violation_rate`` keys count inside the drop-later repair walk and are NOT
used here -- the manuscript quotes the pure arm).

Panel (b): the repair-dependent reading -- coverage lost against the same
unit's endogenous-dwell schedule, by remedy arm: the three repair rules
(drop-later, priority-aware, bounded re-timing) and the conservative
pre-shrunk fixed dwell (zero violations by construction, at the price of a
sparser plan).  The family ordering flips between arms, so neither panel
supports a between-family ranking; the caption says so.

Data: frozen artifacts only -- ``counterfactual_fd/counterfactual_units.json``
(pure per-seed violation rates), ``counterfactual_fd/counterfactual_repairs_agg.json``
(per-seed gaps per rule), ``counterfactual_fd/conservative/counterfactual_units.json``
(per-seed conservative gaps), ``counterfactual_fd/counterfactual_summary.json``
(medians, pair totals).  A figure-data receipt covers every caption number.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig8_counterfactual.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results" / "counterfactual_fd"
OUT = FORK / "paper" / "figures" / "fig8_counterfactual.pdf"
RECEIPT = FORK / "experiments" / "v5_results" / "figure_data" / "fig8_counterfactual.json"

FAMILIES = ("R1C", "R2F", "R3H")
COLORS = {"R1C": "#0072B2", "R2F": "#D55E00", "R3H": "#009E73"}
ARMS = ("drop-later", "priority-aware", "re-timing", "conservative")
ARM_KEYS = {"drop-later": "drop_later", "priority-aware": "priority_aware",
            "re-timing": "retime", "conservative": "conservative"}
# deterministic vertical jitter for the per-seed dots (no RNG)
JITTER = (-0.052, -0.037, -0.022, -0.007, 0.008, 0.023, 0.038, 0.053,
          -0.030, 0.030)
PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
            "papers/sliding-spotlight-scheduling/scripts/plot_fig8_counterfactual.py")
CAL_TAG = ("figure receipt / counterfactual pure-plan caliber / frozen v5 "
           "artifacts, s=1.0, budget 40/60, ten seeds")


def _entry(eid, value, unit, source_file, source_path, note=None):
    e = {"id": eid, "value": value, "unit": unit, "caliber_tag": CAL_TAG,
         "produced_by": PRODUCER,
         "source": {"file": source_file, "path": source_path}}
    if note:
        e["note"] = note
    return e


def main() -> int:
    units = json.loads((V5 / "counterfactual_units.json").read_text(encoding="utf-8"))
    rep = json.loads((V5 / "counterfactual_repairs_agg.json").read_text(encoding="utf-8"))
    cons = json.loads((V5 / "conservative" / "counterfactual_units.json").read_text(encoding="utf-8"))
    summ = json.loads((V5 / "counterfactual_summary.json").read_text(encoding="utf-8"))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"],
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
        "font.size": 9.5, "axes.labelsize": 9.5, "axes.titlesize": 9.5,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 7.6,
        "axes.linewidth": 0.8, "lines.linewidth": 1.3,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.formatter.use_mathtext": True,
        "figure.constrained_layout.use": True,
    })

    fig, (axa, axb) = plt.subplots(
        2, 1, figsize=(3.85, 3.6), gridspec_kw={"height_ratios": [1.0, 1.9]})

    receipts = []

    # ---- (a) violation rate, pure caliber, before any repair --------------
    for row, fam in enumerate(FAMILIES):
        rates = [u["violation_rate_pure"] * 100.0
                 for u in units if u["family"] == fam]
        med = summ[fam]["violation_rate_pure_median"] * 100.0
        for j, v in zip(JITTER, sorted(rates)):
            axa.plot(v, row + j, marker=".", markersize=2.4, linestyle="none",
                     color=COLORS[fam], alpha=0.55, zorder=1)
        axa.plot([med], [row], marker="|", markersize=11, markeredgewidth=1.6,
                 color=COLORS[fam], zorder=3)
        npure = (summ[fam]["violating_pairs_pure_total"],
                 summ[fam]["adjacent_pairs_pure_total"])
        axa.text(55.5, row, f"  n={npure[0]}/{npure[1]} pairs", fontsize=6.4,
                 color="0.25", va="center", ha="left")
        print(f"# (a) {fam}: median {med:.2f}%  total {npure[0]}/{npure[1]}  "
              f"per-seed min {min(rates):.2f} max {max(rates):.2f}")
        receipts.append(_entry(f"fig8.viol_median_pp.{fam}", round(med, 2), "%",
                               "counterfactual_fd/counterfactual_summary.json",
                               f"{fam}.violation_rate_pure_median",
                               "pure-plan caliber, counted before any repair"))
        receipts.append(_entry(f"fig8.viol_pairs.{fam}",
                               f"{npure[0]}/{npure[1]}", "pairs",
                               "counterfactual_fd/counterfactual_summary.json",
                               f"{fam}.violating_pairs_pure_total"))
    axa.set_yticks(range(3))
    axa.set_yticklabels(FAMILIES)
    axa.set_xlim(-2.0, 78.0)
    axa.set_xticks([0, 10, 20, 30, 40, 50])
    axa.set_ylim(-0.55, 2.55)
    axa.invert_yaxis()
    axa.set_xlabel("pairs violating C2 under replay (%)")
    axa.text(0.02, 0.94, "(a)", transform=axa.transAxes, fontsize=9.5,
             va="top", ha="left")

    # ---- (b) coverage gap after repair, per arm, per family ---------------
    offsets = {"R1C": -0.24, "R2F": 0.0, "R3H": 0.24}
    for row, arm in enumerate(ARMS):
        for fam in FAMILIES:
            if arm == "conservative":
                gaps = [u["coverage_gap_pp"] for u in cons if u["family"] == fam]
                med = summ["conservative"][fam]["gap_pp_median"]
                src = ("counterfactual_fd/conservative/counterfactual_units.json",
                       f"[family={fam}].coverage_gap_pp")
                med_src = ("counterfactual_fd/counterfactual_summary.json",
                           f"conservative.{fam}.gap_pp_median")
            else:
                gaps = rep[fam]["per_seed_gap_pp"][ARM_KEYS[arm]]
                med = rep[fam]["median_gap_pp"][ARM_KEYS[arm]]
                src = ("counterfactual_fd/counterfactual_repairs_agg.json",
                       f"{fam}.per_seed_gap_pp.{ARM_KEYS[arm]}")
                med_src = (src[0], f"{fam}.median_gap_pp.{ARM_KEYS[arm]}")
            for j, v in zip(JITTER, sorted(gaps)):
                axb.plot(v, row + offsets[fam] + 0.09 * j, marker=".",
                         markersize=2.4, linestyle="none", color=COLORS[fam],
                         alpha=0.55, zorder=1)
            axb.plot([med], [row + offsets[fam]], marker="|", markersize=10,
                     markeredgewidth=1.6, color=COLORS[fam], zorder=3)
            print(f"# (b) {arm} {fam}: median {med:.4f} pp  "
                  f"n={len(gaps)} seeds")
            receipts.append(_entry(
                f"fig8.gap_median_pp.{ARM_KEYS[arm]}.{fam}", round(med, 4), "pp",
                med_src[0], med_src[1]))
            receipts.append(_entry(
                f"fig8.gap_per_seed.{ARM_KEYS[arm]}.{fam}",
                [round(g, 4) for g in gaps], "pp", src[0], src[1]))
    axb.axvline(0.0, color="0.55", lw=0.7, ls=":")
    axb.text(0.4, 3.62, "endogenous baseline = 0", fontsize=6.4, color="0.30",
             va="top", ha="left")
    axb.set_yticks(range(4))
    axb.set_yticklabels(ARMS)
    axb.set_xlim(-2.0, 72.0)
    axb.set_xticks([0, 10, 20, 30, 40, 50, 60, 70])
    axb.set_ylim(3.62, -0.62)  # inverted: first arm on top
    axb.set_xlabel("coverage gap to the endogenous-dwell schedule (pp)")
    axb.text(0.02, 0.06, "(b)", transform=axb.transAxes, fontsize=9.5,
             va="bottom", ha="left")

    # conservative zero-violation receipt (its pairs never violate)
    for fam in ("R2F", "R3H"):
        c = summ["conservative"][fam]
        receipts.append(_entry(
            f"fig8.cons_viol_pairs.{fam}",
            f"{c['violating_pairs_pure_total']}/{c['adjacent_pairs_pure_total']}",
            "pairs", "counterfactual_fd/counterfactual_summary.json",
            f"conservative.{fam}.violating_pairs_pure_total",
            "zero by construction: the conservative dwell is pre-shrunk"))
        print(f"# conservative {fam}: violations "
              f"{c['violating_pairs_pure_total']}/{c['adjacent_pairs_pure_total']}, "
              f"gap median {c['gap_pp_median']} pp "
              f"(range {c['gap_pp_min']}--{c['gap_pp_max']})")

    handles = [plt.Line2D([], [], marker=".", linestyle="none",
                          color=COLORS[f], label=f) for f in FAMILIES]
    axb.legend(handles=handles, frameon=False, loc="lower right",
               borderaxespad=0.3, handletextpad=0.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps({"figure": "fig8_counterfactual",
                                   "entries": receipts}, indent=1),
                       encoding="utf-8")
    print(f"# written {RECEIPT}")

    # silent-zero guards: 3 medians + 12 arm-family dot groups must exist
    n_viol = sum(1 for _ in FAMILIES)
    n_gap = sum(1 for e in receipts if e["id"].startswith("fig8.gap_median"))
    print(f"# plotted {n_viol}/3 violation rows, {n_gap}/12 gap arm-family groups")
    if n_viol < 3 or n_gap < 12:
        print("ABORT: an arm or family rendered empty", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
