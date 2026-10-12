#!/usr/bin/env python3
"""fig-5 promotion two-axis verdict (W3, outline section 6.2 / obligations
B11 + B12).

Data-source whitelist: reads ONLY experiments/v3_results/ -- panel (a)
recomputes the model-level structural bound R_fam per family from the promoted
scenarios via the REGISTERED caliber (imports ``family_r`` from
``scripts/recompute_r_fam.py``, the ticket-23/41 measurement route: task x 11
in-window starts x routed mode at the task's PRF, per-task r0, out-of-domain
excluded); panel (b) reads promotion.spread_db of all 90 promoted units.  No
v2 sources.

Two-axis discipline (B11, axis separation): panel (a) is the STRUCTURAL axis
(model-level statement only); panel (b) is the READING axis (90/90
no_promotion).  The figure deliberately does not merge them into one claim.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src:papers/sliding-spotlight-scheduling \
        "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig5_promotion_two_axis.py
stdout is the provenance record -- archive it next to the figure.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
sys.path.insert(0, str(FORK / "scripts"))
REPO = FORK.parents[1]
sys.path.insert(0, str(REPO / "src"))

from recompute_r_fam import FAMILIES, family_r  # noqa: E402
from sss_core.modes import ModeLibrary  # noqa: E402

V3 = FORK / "experiments" / "v3_results"
OUT = FORK / "paper" / "figures" / "fig5_promotion_two_axis.pdf"
REGISTERED = {"R1C": 3.9998, "R2F": 8.7407, "R3H": 10.91}   # verify_v3_verdicts pins +-0.02 dB
THRESHOLD_DB = 6.0


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10"],
        "mathtext.fontset": "cm", "axes.unicode_minus": False,
        "font.size": 9.5, "axes.labelsize": 9.5, "axes.titlesize": 9.5,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8.5,
        "axes.linewidth": 0.8, "lines.linewidth": 1.4,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.constrained_layout.use": True,
    })

    lib = ModeLibrary.from_fixture()
    scen = V3 / "scenarios"
    rfam = {}
    for code, base_seed in FAMILIES.items():
        base = next(p for p in sorted(scen.glob(f"{code}_seed*.json"))
                    if p.stem.endswith(f"seed{base_seed}"))
        manifest = json.loads(base.read_text(encoding="utf-8"))
        val, n_used, n_excl = family_r(manifest, lib, per_task_r0=True)
        rfam[code] = val
        print(f"# R_fam({code}, base seed, registered caliber) = {val:.4f} dB "
              f"[registered {REGISTERED[code]}], samples={n_used}, excluded={n_excl}")
        if abs(val - REGISTERED[code]) > 0.02:
            print(f"# MISMATCH vs registration for {code} -- failing loud", file=sys.stderr)
            return 1

    spreads, tiers, fams = [], [], []
    for tier in ("matrix", "matrix_p80g120", "matrix_p160g240"):
        for p in sorted(glob.glob(str(V3 / tier / "pilot_*.json"))):
            a = json.loads(Path(p).read_text(encoding="utf-8"))
            spreads.append(a["promotion"]["spread_db"])
            tiers.append(tier)
            fams.append(p.split("pilot_")[1].split("_seed")[0])
    decisions = {json.loads(Path(p).read_text(encoding="utf-8"))["promotion"]["decision"]
                 for p in glob.glob(str(V3 / "matrix_p160g240" / "pilot_*.json"))}
    print(f"# reading axis: {len(spreads)} units, decisions={sorted(decisions)}, "
          f"max spread={max(spreads):.4f} dB")

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(4.8, 2.3))
    codes = ["R1C", "R2F", "R3H"]
    bar_colors = ["#CC79A7" if rfam[c] < THRESHOLD_DB else "#0072B2" for c in codes]
    axa.bar(codes, [rfam[c] for c in codes], color=bar_colors, width=0.55)
    axa.axhline(THRESHOLD_DB, color="black", linewidth=0.9, linestyle=":")
    axa.text(-0.42, THRESHOLD_DB + 0.25, f"threshold\n{THRESHOLD_DB:.1f} dB", fontsize=8,
             ha="left", va="bottom")
    for i, c in enumerate(codes):
        verdict = "STRUCTURAL DEAD" if rfam[c] < THRESHOLD_DB else "descriptively ALIVE"
        axa.text(i, rfam[c] + 0.3, f"{rfam[c]:.2f}", ha="center", fontsize=8)
        if rfam[c] < THRESHOLD_DB:
            # short bar: a rotated label would overrun it -- park the verdict
            # in the free upper-left corner, coloured like its bar
            axa.text(-0.44, 11.55, verdict, ha="left", va="top", fontsize=8,
                     color="#CC79A7")
        else:
            axa.text(i, 0.3, verdict, ha="center", fontsize=8, rotation=90,
                     color="white")
    axa.set_ylabel("model-level $R_{fam}$ (dB)")
    axa.set_title("(a) structural axis (model-level)", fontsize=9)
    axa.set_ylim(0, 12.5)
    from matplotlib.ticker import MaxNLocator
    axa.yaxis.set_major_locator(MaxNLocator(5))

    tier_of = {t: i for i, t in enumerate(("matrix", "matrix_p80g120", "matrix_p160g240"))}
    jit = {"R1C": -0.22, "R2F": 0.0, "R3H": 0.22}
    fam_colors = {"R1C": "#CC79A7", "R2F": "#0072B2", "R3H": "#D55E00"}
    for s, t, f in zip(spreads, tiers, fams):
        axb.scatter(tier_of[t] + jit[f], s, s=14, color=fam_colors[f], alpha=0.75,
                    linewidths=0)
    axb.axhline(THRESHOLD_DB, color="black", linewidth=0.9, linestyle=":")
    axb.text(2.28, THRESHOLD_DB + 0.12, "threshold 6.0 dB", fontsize=8, ha="right")
    axb.set_xticks(range(3), ["40/60", "80/120", "160/240"])
    axb.set_ylabel("promotion spread (dB),\nraw units")
    axb.set_title("(b) reading axis: 90/90 no_promotion", fontsize=9)
    axb.set_ylim(0, 7)
    handles = [plt.Line2D([], [], marker="o", ls="", color=fam_colors[f], label=f)
               for f in ("R1C", "R2F", "R3H")]
    axb.legend(handles=handles, frameon=False, loc="upper left")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
