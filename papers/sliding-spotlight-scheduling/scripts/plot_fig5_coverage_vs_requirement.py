#!/usr/bin/env python3
"""fig-3 (ticket 50 phase 2): coverage versus the demand-tightening factor.

The paper's main result after the repositioning: the required resolution is a
per-task hard constraint, so the question is what tightening it costs in
coverage. The curve is the L8 world (caliber v5): three real-window families x
the nine-point demand grid, single budget 40/60.

Data source: ``experiments/v5_results/sweep_results.json`` (the aggregate), and
nothing else. The service-fraction values are drawn as they are -- no
smoothing, no interpolation, no hidden dip. A grid point where every seed
exited 11 is drawn as "no feasible individual", NOT as a zero-coverage point:
those are different statements (nothing is infeasible about a search that
served less; at R1C s=0.8 the family admits no feasible individual at all).

stdout is the provenance record: archive it next to the figure.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig5_coverage_vs_requirement.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
AGG = FORK / "experiments" / "v5_results" / "sweep_results.json"
OUT = FORK / "paper" / "figures" / "fig5_coverage_vs_requirement.pdf"

FAMILIES = ("R1C", "R2F", "R3H")
S_GRID = (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0)
COLORS = {"R1C": "#0072B2", "R2F": "#D55E00", "R3H": "#009E73"}
MARKERS = {"R1C": "s", "R2F": "^", "R3H": "o"}
STYLES = {"R1C": (0, (1, 1.2)), "R2F": (0, (5, 1.6)), "R3H": "-"}
# deterministic horizontal jitter for the per-seed dots (no RNG: a figure that
# changes between runs cannot be reviewed against a previous version)
JITTER = (-0.052, -0.037, -0.022, -0.007, 0.008, 0.023, 0.038, 0.053,
          -0.030, 0.030)


def load() -> dict:
    return json.loads(AGG.read_text(encoding="utf-8"))


def series(agg: dict, fam: str):
    """(x, median, per-seed, infeasible?) per grid point."""
    xs, meds, seeds, infeas = [], [], [], []
    for s in S_GRID:
        rec = agg["families"][fam][str(s)]
        no_feasible = (rec["n_artifacts"] == 0
                       and rec["n_exit11_no_feasible"] == 10)
        xs.append(s)
        meds.append(None if no_feasible else rec["coverage_median"])
        seeds.append([None] * 10 if no_feasible else rec["coverage_per_seed"])
        infeas.append(no_feasible)
    return xs, meds, seeds, infeas


def main() -> int:
    agg = load()
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

    fig, (ax, axz) = plt.subplots(
        2, 1, figsize=(3.85, 3.55), sharex=True,
        gridspec_kw={"height_ratios": [2.05, 1.15]})

    for fam in FAMILIES:
        xs, meds, seeds, infeas = series(agg, fam)
        # per-seed dots first, so the median line reads on top
        for x, sd in zip(xs, seeds):
            if not sd or sd[0] is None:
                continue
            for j, v in zip(JITTER, sd):
                ax.plot(x + j, v, marker=".", markersize=2.1, linestyle="none",
                        color=COLORS[fam], alpha=0.42, zorder=1)
        px = [x for x, m in zip(xs, meds) if m is not None]
        py = [m for m in meds if m is not None]
        ax.plot(px, py, linestyle=STYLES[fam], marker=MARKERS[fam],
                markersize=4.2, color=COLORS[fam], label=fam, zorder=3)
        # saturation: first grid point reaching the family's own maximum
        if py:
            sat = max(py)
            sat_x = next(x for x, m in zip(px, py) if abs(m - sat) <= 1e-12)
            ax.plot([sat_x], [sat], marker="o", markersize=8.0,
                    markerfacecolor="none", markeredgecolor=COLORS[fam],
                    markeredgewidth=1.0, zorder=2)
            print(f"# {fam}: saturation {sat:.6f} first reached at s={sat_x}; "
                  f"as-placed median {agg['families'][fam]['1.0']['coverage_median']:.6f}")
        if any(infeas):
            x = xs[infeas.index(True)]
            ax.plot([x], [0.0], marker="x", markersize=6.0, mew=1.3,
                    color=COLORS[fam], zorder=4)
            ax.annotate("no feasible individual\n(10/10 seeds, not a\n"
                        "zero-coverage reading)",
                        xy=(x, 0.0), xytext=(x + 0.10, 0.13),
                        fontsize=7.6, color=COLORS[fam],
                        arrowprops=dict(arrowstyle="-", lw=0.6,
                                        color=COLORS[fam]))
            print(f"# {fam}: s={x} has NO feasible individual "
                  "(all seeds exit 11) -- drawn as infeasible, not as 0")
        for x, m in zip(xs, meds):
            if m is None:
                print(f"# {fam} s={x}: infeasible")

    ax.set_ylabel("median served fraction $\eta$")
    # headroom below zero keeps the infeasibility X at its true y=0 position
    # while fully inside the axes rect; without it the lower half of the X is
    # clipped by the bottom spine (clip_on=False would instead draw that half
    # over the x tick labels, and half outside the panel)
    ax.set_ylim(-0.028, 1.03)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(frameon=False, loc="lower right", ncol=1,
              handlelength=2.4, borderaxespad=0.3)
    ax.text(0.02, 0.86, "(a)", transform=ax.transAxes, fontsize=9.5,
            va="top", ha="left")

    # upper-band zoom: R2F and R1C sit inside 3 pp of each other on the full
    # axis, and both R2F dips are under 0.4 pp -- they are only legible here.
    for fam in ("R2F", "R1C"):
        xs, meds, _seeds, _infeas = series(agg, fam)
        px = [x for x, m in zip(xs, meds) if m is not None]
        py = [m for m in meds if m is not None]
        axz.plot(px, py, linestyle=STYLES[fam], marker=MARKERS[fam],
                 markersize=4.2, color=COLORS[fam], zorder=3)
    axz.set_ylim(0.958, 1.004)
    # the y-range is declared in the axis label: a truncated axis that does not
    # say it is truncated is the trap this panel would otherwise set
    axz.set_ylabel("upper-band zoom\n($y\\in[0.958,1.004]$)", fontsize=7.6)
    axz.set_xlabel("demand-tightening factor $s$ (required resolution $\\times s$)")
    axz.set_xticks(list(S_GRID))
    axz.set_xticklabels([f"{s:g}" for s in S_GRID])
    axz.set_yticks([0.96, 0.97, 0.98, 0.99, 1.0])
    axz.text(0.02, 0.10, "(b)", transform=axz.transAxes, fontsize=9.5,
             va="bottom", ha="left")
    axz.text(0.40, 0.10, "dips: anchor construction, unsmoothed",
             transform=axz.transAxes, fontsize=6.4, color="0.32", va="bottom")
    # the zoom carries only the two upper families; without this note a reader
    # can mistake the missing third family for an omission
    axz.text(0.985, 0.83, "(R1C, R2F only)", transform=axz.transAxes,
             fontsize=6.4, color="0.32", va="top", ha="right")
    axz.axvline(1.0, color="0.55", lw=0.7, ls=":")
    axz.annotate("as-placed point", xy=(1.0, 0.9586), xytext=(1.04, 0.9592),
                 fontsize=6.2, color="0.35", va="bottom", ha="left")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")

    # figure-data receipt (R96): every number the caption states, sourced
    # from the same aggregate the curve draws
    receipt_entries = []
    for fam in FAMILIES:
        xs, meds, seeds, infeas = series(agg, fam)
        receipt_entries.append({
            "id": f"fig5.coverage_median.{fam}", "unit": "fraction",
            "value": {str(s): (None if m is None else round(m, 6))
                      for s, m in zip(xs, meds)},
            "caliber_tag": "L8 / caliber v5 / 9-point demand grid / single budget 40-60",
            "produced_by": ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
                            "papers/sliding-spotlight-scheduling/scripts/"
                            "plot_fig5_coverage_vs_requirement.py"),
            "source": {"file": "experiments/v5_results/sweep_results.json",
                       "path": f"families.{fam}.*.coverage_median"},
        })
    receipt_entries.append({
        "id": "fig5.zoom_b_range", "unit": "y-fraction",
        "value": [0.958, 1.004],
        "caliber_tag": "figure receipt / upper-band zoom declaration",
        "produced_by": ("PYTHONHASHSEED=0 \"/d/Program Files/Python/python\" -B "
                        "papers/sliding-spotlight-scheduling/scripts/"
                        "plot_fig5_coverage_vs_requirement.py"),
        "source": {"file": "scripts/plot_fig5_coverage_vs_requirement.py",
                   "path": "axz.set_ylim"},
        "note": ("the control family's s=0.9 median (0.5398) lies outside this "
                 "window and is not drawn in panel (b); its in-range points "
                 "appear for context"),
    })
    rc_path = (FORK / "experiments" / "v5_results" / "figure_data"
               / "fig5_coverage_vs_requirement.json")
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_path.write_text(json.dumps({"figure": "fig5_coverage_vs_requirement",
                                   "entries": receipt_entries}, indent=1),
                       encoding="utf-8")
    print(f"# written {rc_path}")

    # silent-zero guard: a figure that rendered nothing must not look like one
    # that rendered the curve
    got = sum(1 for f in FAMILIES for m in series(agg, f)[1] if m is not None)
    print(f"# plotted {got}/27 family-by-s median points "
          f"({27 - got} infeasible)")
    if got < 26:
        print("ABORT: fewer median points than the registered curve",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
