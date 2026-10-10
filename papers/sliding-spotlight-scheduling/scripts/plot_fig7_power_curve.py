#!/usr/bin/env python3
"""fig-7 power curve (W3, outline section 5.3 / obligation A2 half).

Scipilot data-source whitelist: reads ONLY experiments/v3_results/ (top budget
tier, cv<=1e-9 fronts) plus the frozen registration values from
analysis_prereg_v2.json (alpha, t-critical values, delta).  No v2 sources.

The curve is the registered reproduction route of
amendment_20261005_v3_realwindow.r_family_effect_size.reproduction:
power(delta) = 1 - T(df=9)(t_0.95,9 ; ncp = delta / (sd/sqrt(10))), one-sided.
sd is recomputed per family from dq_all over the 160/240 artifacts.

Caption obligations carried here (A2 honest-reporting): the registered point
(delta = 6.0, power_R3H = 0.29) is marked directly on the curve; the 0.80
convention reference line is drawn; Y axis is fixed to [0, 1].

Usage (repo root):
    PYTHONHASHSEED=0 "/d/Program Files/Python/python" -B \
        papers/sliding-spotlight-scheduling/scripts/plot_fig7_power_curve.py
stdout is the provenance record -- archive it next to the figure.
"""
from __future__ import annotations

import glob
import json
import math
import statistics
import sys
from pathlib import Path

FORK = Path(__file__).resolve().parent.parent
V3 = FORK / "experiments" / "v3_results"
OUT = FORK / "paper" / "figures" / "fig7_power_curve.pdf"

DELTA_LADDER = [2, 3, 4, 4.87, 6.0, 8.0, 10.0, 11.99, 12.13, 13.87, 16.0, 20.0]


def dq_all(art: dict) -> float:
    f1a = art["anchor_f1_star"]
    afq = [r["f_q"] for r in art["front"] if abs(r["f1_star"] - f1a) <= 1e-9]
    return max(r["f_q"] for r in art["front"]) - afq[0]


def main() -> int:
    from scipy import stats as scipy_stats

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    prereg = json.loads((V3.parent / "analysis_prereg_v2.json").read_text(encoding="utf-8"))
    pd_ = prereg["amendment_20261005_v3_realwindow"]["r_family_effect_size"]["power_design"]
    df = int(pd_["df"])
    crit = float(pd_["t_crit_95_df9"])
    delta_registered = float(prereg["amendment_20261005_v3_realwindow"]["r_family_effect_size"]["value"])

    sd = {}
    for fam in ("R2F", "R3H"):
        arts = [json.loads(Path(p).read_text(encoding="utf-8"))
                for p in sorted(glob.glob(str(V3 / "matrix_p160g240" / f"pilot_{fam}_seed*.json")))]
        sd[fam] = statistics.stdev(dq_all(a) for a in arts)
        print(f"# sd(dq_all, {fam}, 160/240, n=10) = {sd[fam]:.4f}")

    def power(delta: float, s: float) -> float:
        return 1.0 - scipy_stats.nct.cdf(crit, df, delta / (s / math.sqrt(10.0)))

    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    # colorblind-safe pair + redundant linestyle encoding
    colors = {"R2F": "#0072B2", "R3H": "#D55E00"}
    styles = {"R2F": "-", "R3H": "--"}
    for fam in ("R2F", "R3H"):
        ys = [power(d, sd[fam]) for d in DELTA_LADDER]
        ax.plot(DELTA_LADDER, ys, styles[fam], color=colors[fam], marker="o",
                markersize=3, linewidth=1.4, label=fam)
        for d, y in zip(DELTA_LADDER, ys):
            print(f"{fam} power({d:.2f}) = {y:.3f}")
    # 0.80 convention reference line
    ax.axhline(0.80, color="grey", linewidth=0.8, linestyle=":", label="80% convention")
    # registered operating point (honest presentation, A2)
    pw_r3h = power(delta_registered, sd["R3H"])
    pw_r2f = power(delta_registered, sd["R2F"])
    ax.plot([delta_registered], [pw_r3h], marker="s", color=colors["R3H"], markersize=6)
    ax.annotate(f"registered $\\delta$={delta_registered:.1f}\nR3H power={pw_r3h:.2f}",
                xy=(delta_registered, pw_r3h), xytext=(delta_registered + 1.2, pw_r3h + 0.12),
                fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate(f"R2F power={pw_r2f:.2f}",
                xy=(delta_registered, pw_r2f), xytext=(delta_registered + 1.2, pw_r2f - 0.16),
                fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.set_xlabel("effect size $\\delta$ ($\\mathrm{m}^{-2}$, R-family $f_q$ units, non-normalised)")
    ax.set_ylabel("power at $n=10$ seeds per family")
    ax.set_ylim(0.0, 1.0)
    ax.set_xlim(left=0.0)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"# written {OUT}")
    print(f"# registered point: delta={delta_registered}, R2F power={pw_r2f:.2f}, R3H power={pw_r3h:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
