#!/usr/bin/env python3
"""Platform-model figure: per-mode f_q versus squint (ticket 50 phase 2).

Role after the single-axis repositioning: this is a PLATFORM MODEL figure, not
a result axis. It shows that the per-task quality model exists, that its
per-mode levels are library-caliber constants, and that it is squint-invariant
by design (D05-4: the sec^2 squint factor cancels inside g_T exactly for
SLS/STR and to better than 0.1% for SPT; rho_rg and R are layer constants).
Nothing is optimised against it and no trade-off is read off it -- the level
differences are what the reported readings are measured against.

Data-source whitelist note: computes from the FROZEN platform fixture via
``sss_core`` only (ModeLibrary.from_fixture + quality.f_q_per_task) -- the same
frozen constants the formulation chapter states. No result directory (v2/v3/
v4/v5) is read, so this figure cannot go stale with a re-run.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src:papers/sliding-spotlight-scheduling \
        "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig3_quality_vs_squint.py
stdout is the provenance record -- archive it next to the figure.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
REPO = FORK.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sss_core.geometry import squint_at  # noqa: E402
from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.quality import f_q_per_task  # noqa: E402

OUT = FORK / "paper" / "figures" / "fig3_quality_vs_squint.pdf"


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
    squints = [i * 1.0 for i in range(0, 46)]          # 0..45 deg
    colors = {"STR": "#0072B2", "SLS": "#D55E00", "SPT": "#009E73"}
    styles = {"STR": "-", "SLS": "--", "SPT": "-."}

    fig, ax = plt.subplots(figsize=(3.85, 2.65))
    consts = {}
    for mode in (Mode.STR, Mode.SLS, Mode.SPT):
        ys = []
        for deg in squints:
            psi = math.radians(deg)
            # squint_at at t=t_ca is the zero-squint reference; here we feed the
            # off-axis angle directly through the same per-task formula the
            # evaluator uses (f_q_per_task takes psi_bar and slant range).
            ys.append(f_q_per_task(mode, psi, lib.geo.R0_m, lib))
        consts[mode.name] = ys[0]
        ax.plot(squints, ys, styles[mode.name], color=colors[mode.name],
                linewidth=1.4, label=mode.name)
        print(f"# {mode.name}: f_q(0 deg) = {ys[0]:.4f}  f_q(45 deg) = {ys[-1]:.4f}  "
              f"drift = {100.0 * (ys[-1] - ys[0]) / ys[0]:+.3f}%")

    r = {a: consts[a] / consts["STR"] for a in ("SLS", "SPT")}
    print(f"# magnitude ratios vs STR: SLS {r['SLS']:.1f}x  SPT {r['SPT']:.1f}x  "
          f"SPT/SLS {consts['SPT'] / consts['SLS']:.1f}x")

    ax.set_xlabel("beam-centre squint $\\bar\\psi$ (deg)")
    ax.set_ylabel("per-task $f_q$ ($\\mathrm{m}^{-2}$, non-normalised)")
    ax.set_xlim(0, 45)
    ax.set_ylim(0, 60)
    ax.set_xticks([0, 15, 30, 45])
    ax.legend(frameon=False, loc="center right")
    ax.annotate("squint-invariant by design:\nthe levels, not the slopes,\n"
                "are platform constants",
                xy=(1.5, 34), fontsize=8, color="0.35", va="top")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
