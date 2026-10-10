#!/usr/bin/env python3
"""fig-4 budget-ladder frontier convergence (W3, outline section 6.3 /
obligations B10 + A1/D-5/D-6 travel faces).

Data-source whitelist: reads ONLY experiments/v3_results/ (the three promoted
budget tiers).  No v2 sources.

Content: median front size and median distinct-fq count per tier for the two
families that carry the registered SEARCH-ARTIFACT verdicts.  The rising tail
at the top tier is the visual counterpart of the NOT-PLATEAUED qualifier that
every frontier reading in the paper must carry.

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig4_budget_ladder.py
stdout is the provenance record -- archive it next to the figure.
"""
from __future__ import annotations

import glob
import json
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V3 = FORK / "experiments" / "v3_results"
TIERS = ("matrix", "matrix_p80g120", "matrix_p160g240")
TIER_LABELS = ("40/60", "80/120", "160/240")
OUT = FORK / "paper" / "figures" / "fig4_budget_ladder.pdf"


def front_of(art: dict) -> list:
    return [r for r in art["front"] if abs(r["cv"]) <= 1e-9]


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), sharex=True)
    colors = {"R2F": "#0072B2", "R3H": "#D55E00"}
    styles = {"R2F": "-", "R3H": "--"}
    x = range(len(TIERS))
    for fam in ("R2F", "R3H"):
        med_front, med_distinct = [], []
        for tier in TIERS:
            arts = [json.loads(Path(p).read_text(encoding="utf-8"))
                    for p in sorted(glob.glob(str(V3 / tier / f"pilot_{fam}_seed*.json")))]
            med_front.append(statistics.median(len(front_of(a)) for a in arts))
            med_distinct.append(statistics.median(
                len({round(r["f_q"], 6) for r in front_of(a)}) for a in arts))
        axes[0].plot(x, med_front, styles[fam], color=colors[fam], marker="o",
                     markersize=4, linewidth=1.4, label=fam)
        axes[1].plot(x, med_distinct, styles[fam], color=colors[fam], marker="s",
                     markersize=4, linewidth=1.4, label=fam)
        print(f"# {fam} median front: " +
              ", ".join(f"{t}={v:.1f}" for t, v in zip(TIER_LABELS, med_front)))
        print(f"# {fam} median distinct-fq: " +
              ", ".join(f"{t}={v:.1f}" for t, v in zip(TIER_LABELS, med_distinct)))

    axes[0].set_xticks(list(x), TIER_LABELS)
    axes[1].set_xticks(list(x), TIER_LABELS)
    axes[0].set_ylabel("median front size (CV-filtered)")
    axes[1].set_ylabel("median distinct-$f_q$ count")
    for ax in axes:
        ax.set_xlabel("population / generations budget tier")
        ax.set_xlim(-0.2, len(TIERS) - 0.8)
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"# written {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
