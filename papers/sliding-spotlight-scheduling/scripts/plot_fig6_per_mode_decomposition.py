#!/usr/bin/env python3
"""fig-6 per-mode f_Q decomposition (W3, outline section 6.4 / obligation A5).

Data-source whitelist: mode constants come from the frozen platform fixture via
``sss_core`` (the registered zero-squint library caliber, a6_adjudication_20260929
adjudication 2: STR 0.8107 / SLS 19.7352 / SPT 54.8322); per-family mode shares
come from experiments/v3_results/scenarios manifests.  No v2 sources.

Registered delivery form (adjudication 2): the decomposition is mode share x
mode constant plus the distribution -- this figure draws exactly that, per
family.  The second objective's whole explainability hangs on it.

Usage (repo root):
    PYTHONHASHSEED=0 PYTHONPATH=src:papers/sliding-spotlight-scheduling \
        "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig6_per_mode_decomposition.py
stdout is the provenance record -- archive it next to the figure.
"""
from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FORK))
REPO = FORK.parents[1]
sys.path.insert(0, str(REPO / "src"))

from sss_core.modes import Mode, ModeLibrary  # noqa: E402
from sss_core.quality import f_q_per_task  # noqa: E402

V3 = FORK / "experiments" / "v3_results"
OUT = FORK / "paper" / "figures" / "fig6_per_mode_decomposition.pdf"


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
    consts = {m.name: f_q_per_task(m, 0.0, lib.geo.R0_m, lib)
              for m in (Mode.STR, Mode.SLS, Mode.SPT)}
    for k, v in consts.items():
        print(f"# mode constant f_q({k}) = {v:.4f} m^-2 (zero-squint library caliber)")

    shares = {}
    for fam in ("R1C", "R2F", "R3H"):
        p = sorted(V3.glob("scenarios", )) if False else sorted((V3 / "scenarios").glob(f"{fam}_seed*.json"))[0]
        tasks = json.loads(p.read_text(encoding="utf-8"))["tasks"]
        c = collections.Counter(t["mode"] for t in tasks)
        shares[fam] = {m: c.get(m, 0) / len(tasks) for m in ("STR", "SLS", "SPT")}
        print(f"# {fam} mode shares: " +
              ", ".join(f"{m}={shares[fam][m]:.3f}" for m in ("STR", "SLS", "SPT")))

    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    fams = ["R1C", "R2F", "R3H"]
    colors = {"STR": "#0072B2", "SLS": "#D55E00", "SPT": "#009E73"}
    bottom = [0.0, 0.0, 0.0]
    for m in ("STR", "SLS", "SPT"):
        vals = [shares[f][m] * consts[m] for f in fams]
        ax.bar(fams, vals, bottom=bottom, width=0.5, color=colors[m], label=m,
               edgecolor="white", linewidth=0.4)
        for i, v in enumerate(vals):
            if v > 1.0:
                ax.text(i, bottom[i] + v / 2, f"{v:.1f}", ha="center", va="center",
                        fontsize=8, color="white")
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, f in enumerate(fams):
        ax.text(i, bottom[i] + 1.2, f"$\\bar f_Q$={bottom[i]:.1f}", ha="center", fontsize=8.5)
    ax.set_ylabel("share $\\times$ mode constant\n($\\mathrm{m}^{-2}$, non-normalised)")
    ax.set_ylim(0, 60)
    ax.legend(frameon=False, loc="upper left")
    ax.text(0.30, 0.97,
            "mode share from the promoted\n"
            "scenario manifests; constants are\n"
            "model-level zero-squint values (D05-4)",
            transform=ax.transAxes, fontsize=8, va="top", color="0.35")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"# written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
