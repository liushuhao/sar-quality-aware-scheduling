#!/usr/bin/env python3
"""fig-6 (R96 figure wave): the two construction probes, one ruler.

Both panels share the same axes -- the served priority fraction of the
best-covered member -- and read each probe against the same anchor arm at
the same unit, so the identity line is the reference:

(a) anchor-free random initialization (40 re-run cells, R2F at s=0.9/1.4
    and R3H at s=0.9/1.0): 12 of 40 cells return no feasible individual --
    marked in the strip below the axis, never plotted as zero coverage --
    and on the 28 feasible cells the anchor-free arm never exceeds the
    anchor arm (12.9--54.9 pp below it).
(b) a sixteen-fold evaluation budget (160/240 against the registered
    40/60) on the same 40 cells: every reading coincides with the
    registered arm exactly (gain 0.00 pp on every unit; the search-only
    maximum is empty on every unit).

Data: frozen artifacts only -- ``anchor_free/anchor_free.json`` and
``budget_check/budget_check.json``.  A figure-data receipt covers every
caption number.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig6_construction_probes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
OUT = FORK / "paper" / "figures" / "fig6_construction_probes.pdf"
RECEIPT = V5 / "figure_data" / "fig6_construction_probes.json"

COLORS = {"R1C": "#0072B2", "R2F": "#D55E00", "R3H": "#009E73"}
PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
            "papers/sliding-spotlight-scheduling/scripts/plot_fig6_construction_probes.py")
CAL_TAG = ("figure receipt / construction probes / frozen v5 artifacts, "
           "registered budget 40/60 and 16x check 160/240, ten seeds per cell")


def _entry(eid, value, unit, source_file, source_path, note=None):
    e = {"id": eid, "value": value, "unit": unit, "caliber_tag": CAL_TAG,
         "produced_by": PRODUCER,
         "source": {"file": source_file, "path": source_path}}
    if note:
        e["note"] = note
    return e


def main() -> int:
    af = json.loads((V5 / "anchor_free" / "anchor_free.json").read_text(encoding="utf-8"))
    bc = json.loads((V5 / "budget_check" / "budget_check.json").read_text(encoding="utf-8"))

    feas = [u for u in af if u.get("anchor_free_max_f1_star") is not None]
    infeas = [u for u in af if u.get("anchor_free_max_f1_star") is None]
    pps = [u["free_vs_anchor_arm_pp"] for u in feas]
    assert all(not u["free_beats_anchor_arm"] for u in feas), \
        "anchor-free arm beat the anchor: figure premise broken"
    gains = [u["gain_vs_4060_pp"] for u in bc]
    assert all(g == 0.0 for g in gains), "16x budget moved a unit: premise broken"

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"],
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
        "font.size": 9.5, "axes.labelsize": 9.0, "axes.titlesize": 9.5,
        "xtick.labelsize": 8.0, "ytick.labelsize": 8.0, "legend.fontsize": 7.6,
        "axes.linewidth": 0.8, "lines.linewidth": 1.3,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.formatter.use_mathtext": True,
        "figure.constrained_layout.use": True,
    })

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(3.85, 1.98), sharey=True,
                                   sharex=True)
    lo, hi = 0.55, 1.03
    for ax in (axa, axb):
        ax.plot([lo, hi], [lo, hi], color="0.55", lw=0.7, ls=":", zorder=1)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal")
        ax.set_xticks([0.6, 0.8, 1.0])
        ax.set_yticks([0.6, 0.8, 1.0])
        ax.set_xlabel("anchor arm $\\eta$")

    # (a) anchor-free vs anchor, feasible cells below the identity line
    for u in feas:
        axa.plot(u["anchor_arm_f1_star"], u["anchor_free_max_f1_star"],
                 marker="o", markersize=3.1, markerfacecolor="none",
                 markeredgewidth=0.75, linestyle="none",
                 color=COLORS[u["family"]], zorder=3)
    # the 12 no-feasible-individual cells: evenly spaced marks in a strip
    # below the axis (the frozen records carry rc=11 + stderr only, no
    # anchor value -- so this lane states the count, never a data position)
    for i in range(len(infeas)):
        x = lo + (hi - lo) * (i + 0.5) / len(infeas)
        axa.plot(x, lo - 0.012, marker="x", markersize=3.4, mew=0.8,
                 linestyle="none", color=COLORS["R3H"], clip_on=False,
                 zorder=3)
    axa.set_ylabel("anchor-free arm $\\eta$")
    axa.text(0.04, 0.97, "(a)", transform=axa.transAxes, fontsize=9.5,
             va="top", ha="left")
    # merged note, upper-left above-identity triangle (data-free zone; the
    # below-axis placement used to overprint the tick labels and the xlabel)
    axa.text(0.04, 0.855,
             "28 cells, 0 above\n"
             "the identity line;\n"
             "12 more (all R3H):\n"
             "no feasible individual\n"
             "(marked below the axis,\n"
             "not zero)",
             transform=axa.transAxes, fontsize=6.0, color="0.30",
             va="top", ha="left")

    # (b) 16x budget vs registered: all 40 on the identity line
    for u in bc:
        axb.plot(u["base4060_max_front"], u["max_f1_star_on_front"],
                 marker="o", markersize=3.1, markerfacecolor="none",
                 markeredgewidth=0.75, linestyle="none",
                 color=COLORS[u["family"]], zorder=3)
    axb.text(0.04, 0.97, "(b)", transform=axb.transAxes, fontsize=9.5,
             va="top", ha="left")
    axb.text(0.04, 0.885, "40/40 cells coincide\n(gain 0.00 pp each)",
             transform=axb.transAxes, fontsize=6.4, color="0.30", va="top")
    axb.set_xlabel("registered 40/60 arm $\\eta$")
    axb.set_ylabel("16x budget arm $\\eta$")

    handles = [plt.Line2D([], [], marker="o", linestyle="none",
                          markerfacecolor="none", color=COLORS[f], label=f)
               for f in ("R2F", "R3H")]
    axb.legend(handles=handles, frameon=False, loc="lower right",
               borderaxespad=0.2, handletextpad=0.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")

    receipts = [
        _entry("fig6.af_total_cells", 40, "cells",
               "anchor_free/anchor_free.json", "$.length"),
        _entry("fig6.af_feasible_cells", 28, "cells",
               "anchor_free/anchor_free.json",
               "[?(@.anchor_free_max_f1_star != null)]"),
        _entry("fig6.af_infeasible_cells", 12, "cells",
               "anchor_free/anchor_free.json", "[?(@.rc == 11)]",
               "all R3H; rc=11 'no feasible individual survived'; status, "
               "not zero coverage"),
        _entry("fig6.af_free_vs_anchor_pp_min", round(min(pps), 4), "pp",
               "anchor_free/anchor_free.json", "[].free_vs_anchor_arm_pp"),
        _entry("fig6.af_free_vs_anchor_pp_max", round(max(pps), 4), "pp",
               "anchor_free/anchor_free.json", "[].free_vs_anchor_arm_pp"),
        _entry("fig6.af_beats_anchor_count", 0, "cells",
               "anchor_free/anchor_free.json", "[].free_beats_anchor_arm"),
        _entry("fig6.bc_total_cells", 40, "cells",
               "budget_check/budget_check.json", "$.length"),
        _entry("fig6.bc_gain_nonzero", 0, "cells",
               "budget_check/budget_check.json", "[].gain_vs_4060_pp"),
        _entry("fig6.bc_beats_anchor_count", 0, "cells",
               "budget_check/budget_check.json", "[].search_beats_anchor"),
        _entry("fig6.bc_budget_check", "160/240", "pop/gens",
               "budget_check/budget_check.json", "[].budget"),
        _entry("fig6.af_s_points_R2F", "0.9, 1.4", "s",
               "anchor_free/anchor_free.json",
               "[?(@.family=='R2F')].s", "unique"),
        _entry("fig6.af_s_points_R3H", "0.9, 1.0", "s",
               "anchor_free/anchor_free.json",
               "[?(@.family=='R3H')].s", "unique"),
    ]
    for e in receipts:
        print(f"# receipt {e['id']} = {e['value']}")
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps({"figure": "fig6_construction_probes",
                                   "entries": receipts}, indent=1),
                       encoding="utf-8")
    print(f"# written {RECEIPT}")

    n_a = len(feas) + len(infeas)
    print(f"# plotted (a) {len(feas)} dots + {len(infeas)} strip marks = {n_a}/40; "
          f"(b) {len(bc)}/40 dots")
    if n_a != 40 or len(bc) != 40 or len(feas) != 28:
        print("ABORT: cell counts do not match the frozen artifacts",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
