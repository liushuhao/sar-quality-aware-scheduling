#!/usr/bin/env python3
"""fig-4 (R96 figure wave): the released scenario set, three views.

(a) Target geometry in lon--lat (equal spacing, no projection correction,
    no coastline layer): one representative seed per family, colour = family
    (Fig. 3 coding in the manuscript), marker = mode.  The dense family's
    5x5 node grid at 250 km spacing is visible as structure, not asserted.
(b) Mode composition per family: stacked counts of the same representative
    seed, with the registered per-seed interval annotated alongside.
(c) Passes per task (windows/task), all ten seeds pooled per family, with
    the registered total-window interval annotated.

The target geometry is a registered synthetic template, not a measured
campaign profile -- the caption carries that sentence; nothing here is a
controlled comparison across families (densities and mode composition
covary by design).

Data: frozen scenario manifests only.  A figure-data receipt covers every
caption number.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig4_scenario_set.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V5 = FORK / "experiments" / "v5_results"
OUT = FORK / "paper" / "figures" / "fig4_scenario_set.pdf"
RECEIPT = V5 / "figure_data" / "fig4_scenario_set.json"

REP_SEED = {"R1C": 100, "R2F": 200, "R3H": 300}
SEEDS = {"R1C": range(100, 110), "R2F": range(200, 210), "R3H": range(300, 310)}
FAMILIES = ("R1C", "R2F", "R3H")
COLORS = {"R1C": "#0072B2", "R2F": "#D55E00", "R3H": "#009E73"}
MARKERS = {"STR": "s", "SLS": "^", "SPT": "o"}
MODE_GREY = {"STR": "0.30", "SLS": "0.55", "SPT": "0.78"}  # hatch-free greys
COMP_INTERVAL = {  # mode_decomposition.json > families.<fam>.composition_interval
    # (drawn corrected per the scenario generation ledgers: R1C/R2F draw
    #  their registered ladder counts 20/50 on every seed -- the aggregate
    #  file's "46-50" drawn entry for R2F is the admitted interval, the
    #  scenario manifests' n_drawn is 50 on all ten seeds)
    "R1C": {"drawn": "20-20", "admitted": "20-20", "STR": "20-20",
            "SLS": "0-0", "SPT": "0-0", "windows": "145-162"},
    "R2F": {"drawn": "50-50", "admitted": "46-50", "STR": "0-0",
            "SLS": "9-20", "SPT": "29-40", "windows": "337-391"},
    "R3H": {"drawn": "99-100", "admitted": "99-100", "STR": "41-54",
            "SLS": "15-18", "SPT": "30-40", "windows": "731-779"},
}
PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
            "papers/sliding-spotlight-scheduling/scripts/plot_fig4_scenario_set.py")
CAL_TAG = ("figure receipt / scenario manifests / frozen v5 scenario set, "
           "registered synthetic template")


def _entry(eid, value, unit, source_file, source_path, note=None):
    e = {"id": eid, "value": value, "unit": unit, "caliber_tag": CAL_TAG,
         "produced_by": PRODUCER,
         "source": {"file": source_file, "path": source_path}}
    if note:
        e["note"] = note
    return e


def load(fam, seed):
    return json.loads((V5 / "scenarios" / f"{fam}_seed{seed}.json")
                      .read_text(encoding="utf-8"))


def main() -> int:
    receipts = []
    sc_rep = {f: load(f, REP_SEED[f]) for f in FAMILIES}

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"],
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
        "font.size": 9.0, "axes.labelsize": 9.0, "axes.titlesize": 9.0,
        "xtick.labelsize": 8.0, "ytick.labelsize": 8.0, "legend.fontsize": 7.6,
        "axes.linewidth": 0.8, "lines.linewidth": 1.3,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.formatter.use_mathtext": True,
        "figure.constrained_layout.use": True,
    })

    fig, (axa, axb, axc) = plt.subplots(1, 3, figsize=(7.2, 2.45),
                                        gridspec_kw={"width_ratios":
                                                     [1.25, 1.0, 1.0]})

    # ---- (a) target geometry, lon-lat, representative seeds ---------------
    for fam in FAMILIES:
        for mode in ("STR", "SLS", "SPT"):
            pts = [(t["lon_deg"], t["lat_deg"])
                   for t in sc_rep[fam]["tasks"] if t["mode"] == mode]
            if not pts:
                continue
            axa.plot([p[0] for p in pts], [p[1] for p in pts],
                     marker=MARKERS[mode], markersize=3.4 if mode != "STR" else 2.8,
                     linestyle="none", color=COLORS[fam],
                     markeredgecolor="black", markeredgewidth=0.25,
                     alpha=0.85, label=fam if mode == "STR" else None)
    # domain square of the dense family, from the preregistration block
    # (domain_centre_deg is [lat, lon] -- assign accordingly)
    pre = sc_rep["R3H"]["preregistration"]
    cy, cx = pre["domain_centre_deg"]
    half = pre["domain_side_km"] / 2.0 / 111.32  # km -> deg latitude
    axa.add_patch(plt.Rectangle((cx - half * 1.47, cy - half), half * 2 * 1.47,
                                half * 2, fill=False, lw=0.7, ls="--",
                                color="0.45"))
    axa.text(cx + half * 1.47, cy - half + 0.35,
             f"shared domain: {pre['domain_side_km']:.0f} km side, "
             f"5$\\times$5 nodes @ {pre['grid_spacing_km']:.0f} km",
             fontsize=6.4, color="0.30", ha="right", va="bottom")
    axa.set_xlabel("longitude (deg)")
    axa.set_ylabel("latitude (deg)")
    axa.set_aspect(1.0 / 0.78)  # cosmetic lat stretch, lon-lat equal spacing
    axa.text(0.02, 0.97, "(a)", transform=axa.transAxes, fontsize=9.5,
             va="top", ha="left")
    receipts.append(_entry("fig4.domain_centre_deg", [cx, cy], "deg",
                           f"scenarios/R3H_seed{REP_SEED['R3H']}.json",
                           "preregistration.domain_centre_deg"))
    receipts.append(_entry("fig4.domain_side_km", pre["domain_side_km"], "km",
                           f"scenarios/R3H_seed{REP_SEED['R3H']}.json",
                           "preregistration.domain_side_km"))
    receipts.append(_entry("fig4.grid_spacing_km", pre["grid_spacing_km"], "km",
                           f"scenarios/R3H_seed{REP_SEED['R3H']}.json",
                           "preregistration.grid_spacing_km"))
    receipts.append(_entry("fig4.grid_n", pre["grid_n"], "nodes/side",
                           f"scenarios/R3H_seed{REP_SEED['R3H']}.json",
                           "preregistration.grid_n"))

    # ---- (b) mode composition, representative seed + registered interval --
    ymap = {"R1C": 2, "R2F": 1, "R3H": 0}
    for fam in FAMILIES:
        counts = {m: sum(1 for t in sc_rep[fam]["tasks"] if t["mode"] == m)
                  for m in ("STR", "SLS", "SPT")}
        left = 0
        for m in ("STR", "SLS", "SPT"):
            if counts[m]:
                axb.barh(ymap[fam], counts[m], left=left, height=0.52,
                         color=MODE_GREY[m], edgecolor="black", lw=0.4)
                axb.text(left + counts[m] / 2, ymap[fam], str(counts[m]),
                         ha="center", va="center", fontsize=7.0,
                         color="white" if m == "STR" else "black")
                left += counts[m]
        ci = COMP_INTERVAL[fam]
        axb.text(left + 1.5, ymap[fam],
                 f"{ci['admitted']} admitted/seed\n"
                 f"(STR {ci['STR']} / SLS {ci['SLS']} / SPT {ci['SPT']})",
                 fontsize=6.2, color="0.30", va="center", ha="left")
        receipts.append(_entry(f"fig4.rep_seed_modes.{fam}", counts, "tasks",
                               f"scenarios/{fam}_seed{REP_SEED[fam]}.json",
                               "tasks[].mode"))
        receipts.append(_entry(f"fig4.composition_interval.{fam}",
                               {k: ci[k] for k in ("drawn", "admitted", "STR",
                                                   "SLS", "SPT", "windows")},
                               "per-seed interval",
                               "mode_decomposition.json",
                               f"families.{fam}.composition_interval"))
    axb.set_yticks([2, 1, 0])
    axb.set_yticklabels(FAMILIES[::-1])
    axb.set_xlabel("tasks of the representative seed")
    axb.set_xlim(0, 168)
    axb.set_xticks([0, 50, 100])
    axb.text(0.02, 0.97, "(b)", transform=axb.transAxes, fontsize=9.5,
             va="top", ha="left")

    # ---- (c) passes per task, ten seeds pooled -----------------------------
    for row, fam in enumerate(FAMILIES):
        wpt = []
        for seed in SEEDS[fam]:
            sc = load(fam, seed)
            wpt.extend(len(t["windows"]) for t in sc["tasks"])
        axc.plot([row + ((i % 7) - 3) * 0.021 for i in range(len(wpt))], wpt,
                 marker=".", markersize=1.7, linestyle="none",
                 color=COLORS[fam], alpha=0.30)
        ci = COMP_INTERVAL[fam]
        axc.text(row + 0.28, 16.0,
                 f"{ci['windows']} windows/seed", fontsize=6.2,
                 color="0.30", va="top", ha="left")
        print(f"# (c) {fam}: {len(wpt)} tasks pooled, windows/task "
              f"median {sorted(wpt)[len(wpt)//2]}, max {max(wpt)}")
        receipts.append(_entry(f"fig4.windows_per_task_median.{fam}",
                               sorted(wpt)[len(wpt) // 2], "windows/task",
                               f"scenarios/{fam}_seed*.json",
                               "tasks[].windows.length"))
    axc.set_xticks(range(3))
    axc.set_xticklabels(FAMILIES)
    axc.set_ylabel("windows per task")
    axc.set_ylim(0, 16.8)
    axc.set_xlim(-0.55, 2.75)
    axc.text(0.02, 0.97, "(c)", transform=axc.transAxes, fontsize=9.5,
             va="top", ha="left")

    handles = [plt.Line2D([], [], marker=MARKERS[m], linestyle="none",
                          color="0.35", label=m) for m in ("STR", "SLS", "SPT")]
    handles += [plt.Line2D([], [], marker="s", linestyle="none",
                           color=COLORS[f], label=f) for f in FAMILIES]
    axa.legend(handles=handles, frameon=False, loc="upper left",
               borderaxespad=0.2, handletextpad=0.15, ncol=2,
               columnspacing=0.8, fontsize=6.6)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps({"figure": "fig4_scenario_set",
                                   "entries": receipts}, indent=1),
                       encoding="utf-8")
    print(f"# written {RECEIPT}")

    n_tasks = {f: len(sc_rep[f]["tasks"]) for f in FAMILIES}
    print(f"# representative tasks: {n_tasks}")
    if min(n_tasks.values()) < 20:
        print("ABORT: a representative seed is empty", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
