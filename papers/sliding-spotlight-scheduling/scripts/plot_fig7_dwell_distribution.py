#!/usr/bin/env python3
"""fig-7 (R96 figure wave): the endogenous dwell as the schedule consumes it.

The empirical counterpart of the dwell-law figure: for every task of every
served best-covered member at the as-placed requirement (s=1.0, ten seeds
per family, frozen v5 sweep artifacts), the dwell is recomputed with the
production closure AT THE SELECTED START -- the same quantity the evaluator
consumes (per-task order rho_req, per-task along-track scene size
``azimuth_size_m``, the slant range of the window the start falls in, and
the in-window squint ``squint_at`` of the frozen geometry).

Panel (a): the dwell distribution per family and mode (box = quartiles,
whiskers = 5th/95th percentile, thick line = median).  Panel (b): the same
dwells divided by their own zero-squint value at identical window geometry
-- the quantity the fixed-dwell counterfactual freezes -- against the 1.0
reference.

Deterministic recomputation of frozen artifacts under the frozen model:
zero new experiments.  A figure-data receipt covers every caption number.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig7_dwell_distribution.py
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))

V5 = FORK / "experiments" / "v5_results"
OUT = FORK / "paper" / "figures" / "fig7_dwell_distribution.pdf"
RECEIPT = V5 / "figure_data" / "fig7_dwell_distribution.json"

FAM_SEEDS = {"R1C": range(100, 110), "R2F": range(200, 210),
             "R3H": range(300, 310)}
GROUPS = (("R1C", "STR"), ("R2F", "SLS"), ("R2F", "SPT"),
          ("R3H", "STR"), ("R3H", "SLS"), ("R3H", "SPT"))
COLORS = {"R1C": "#0072B2", "R2F": "#D55E00", "R3H": "#009E73"}
PRODUCER = ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
            "papers/sliding-spotlight-scheduling/scripts/plot_fig7_dwell_distribution.py")
CAL_TAG = ("figure receipt / evaluator-consumed dwell caliber / deterministic "
           "recomputation of frozen v5 sweep artifacts, s=1.0, ten seeds")


def _entry(eid, value, unit, source_file, source_path, note=None):
    e = {"id": eid, "value": value, "unit": unit, "caliber_tag": CAL_TAG,
         "produced_by": PRODUCER,
         "source": {"file": source_file, "path": source_path}}
    if note:
        e["note"] = note
    return e


def main() -> int:
    from sss_core.duration import duration_scene_s
    from sss_core.geometry import squint_at
    from sss_core.modes import Mode, ModeLibrary

    lib = ModeLibrary.from_fixture()
    data = {g: {"T": [], "ratio": [], "psi": []} for g in GROUPS}
    n_units = 0
    n_selected_total = 0
    no_window = 0

    for fam, seeds in FAM_SEEDS.items():
        for seed in seeds:
            pilot = json.loads(
                (V5 / "sweep" / "s1_0" / f"pilot_{fam}_seed{seed}.json")
                .read_text(encoding="utf-8"))
            sc = json.loads(
                (V5 / "scenarios" / f"{fam}_seed{seed}.json").read_text(encoding="utf-8"))
            tasks = sc["tasks"]
            best = max(pilot["front"], key=lambda m: (m["f1_star"], -m["cv"]))
            assert len(best["starts"]) == best["n_selected"], \
                f"{fam}/{seed}: starts {len(best['starts'])} != n_selected {best['n_selected']}"
            n_units += 1
            n_selected_total += best["n_selected"]
            for idx, t in best["starts"].items():
                task = tasks[int(idx)]
                win = next((w for w in task["windows"]
                            if w["lo_s"] <= t <= w["hi_s"]), None)
                if win is None:
                    no_window += 1
                    continue
                psi = squint_at(t, win["t_ca_s"], lib.geo, r0_m=win["r0_m"])
                mode = Mode[task["mode"]]  # scenario stores "STR"/"SLS"/"SPT"
                rho = None if mode is Mode.STR else task["rho_req_m"]
                t_real = duration_scene_s(mode, psi, lib, r0_m=win["r0_m"],
                                          rho_req_m=rho,
                                          l_az_m=task["azimuth_size_m"])
                t_zero = duration_scene_s(mode, 0.0, lib, r0_m=win["r0_m"],
                                          rho_req_m=rho,
                                          l_az_m=task["azimuth_size_m"])
                g = (fam, mode.name)
                data[g]["T"].append(t_real)
                data[g]["ratio"].append(t_real / t_zero)
                data[g]["psi"].append(abs(math.degrees(psi)))

    if no_window:
        print(f"ABORT: {no_window} selected starts fell outside every window",
              file=sys.stderr)
        return 1
    print(f"# recomputed {n_selected_total} served tasks over {n_units} units "
          f"(best-covered member per unit, s=1.0)")

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

    fig, (axa, axb) = plt.subplots(
        2, 1, figsize=(3.85, 3.05), sharex=True,
        gridspec_kw={"height_ratios": [1.5, 1.0]})

    receipts = []
    xs = range(len(GROUPS))
    for ax, key, ylab in ((axa, "T", "dwell at the selected start $T$ (s)"),
                          (axb, "ratio",
                           "$T/T(\\bar\\psi\\!=\\!0)$, same geometry\n"
                           "(axis range $[0.8,2.9]$)")):
        boxes, medians = [], []
        for g in GROUPS:
            v = sorted(data[g][key])
            boxes.append(v)
            medians.append(statistics.median(v))
        ax.bxp([{ "whislo": v[int(0.05 * (len(v) - 1))],
                  "whishi": v[int(0.95 * (len(v) - 1))],
                  "fliers": [],
                  "q1": statistics.quantiles(v, n=4)[0],
                  "med": statistics.median(v),
                  "q3": statistics.quantiles(v, n=4)[2],
                  "label": f"{g[0]}\n{g[1]}"}
                 for g, v in zip(GROUPS, boxes)],
                showfliers=False, widths=0.5,
                medianprops=dict(lw=1.6, color="black"),
                boxprops=dict(lw=0.8), whiskerprops=dict(lw=0.8),
                capprops=dict(lw=0.8))
        for i, g in enumerate(GROUPS, start=1):
            ax.plot([i], [medians[i - 1]], marker="_", markersize=12,
                    color=COLORS[g[0]], zorder=4, linestyle="none")
        if key == "T":
            ax.set_ylim(0.0, 14.0)
            ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14])
        else:
            ax.set_ylim(0.8, 2.9)
            ax.axhline(1.0, color="0.45", lw=0.7, ls=":")
            ax.text(0.995, 1.02, "the frozen zero-squint assumption",
                    transform=ax.get_yaxis_transform(), fontsize=6.2,
                    color="0.30", va="bottom", ha="right")
        ax.set_ylabel(ylab, fontsize=8.0)
        ax.text(0.011, 0.955, "(a)" if key == "T" else "(b)",
                transform=ax.transAxes, fontsize=9.5, va="top", ha="left")

    axb.set_xlabel("family \\ mode")

    # receipts: per-group stats + mode-level squint medians
    for g in GROUPS:
        t = sorted(data[g]["T"])
        r = sorted(data[g]["ratio"])
        p = sorted(data[g]["psi"])
        stats = {
            "n": len(t),
            "T_med": round(statistics.median(t), 4),
            "T_p5": round(t[int(0.05 * (len(t) - 1))], 4),
            "T_p95": round(t[int(0.95 * (len(t) - 1))], 4),
            "ratio_med": round(statistics.median(r), 4),
            "ratio_max": round(max(r), 4),
            "psi_med_deg": round(statistics.median(p), 4),
        }
        print(f"# {g}: " + " ".join(f"{k}={v}" for k, v in stats.items()))
        for k, v in stats.items():
            receipts.append(_entry(
                f"fig7.{g[0]}.{g[1]}.{k}", v,
                "deg" if k.startswith("psi") else ("count" if k == "n" else
                                                   ("s" if k.startswith("T")
                                                    else "x")),
                "scripts/plot_fig7_dwell_distribution.py",
                f"data[({g[0]!r},{g[1]!r})]",
                "deterministic recomputation, evaluator-consumed caliber"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps({"figure": "fig7_dwell_distribution",
                                   "entries": receipts}, indent=1),
                       encoding="utf-8")
    print(f"# written {RECEIPT}")

    # silent-zero guard: every group must hold a real population
    empty = [g for g in GROUPS if len(data[g]["T"]) < 50]
    print(f"# groups populated: {len(GROUPS) - len(empty)}/6 "
          f"(min n = {min(len(data[g]['T']) for g in GROUPS)})")
    if empty:
        print(f"ABORT: empty groups {empty}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
