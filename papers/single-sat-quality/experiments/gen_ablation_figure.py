"""Ablation chart generator for IJAE paper Fig. X.

Produces a grouped bar chart showing per-class degradation (%) of B, C, D
variants relative to baseline A, for f1, f2, and f3 metrics.

TDD: tests/test_gen_ablation_figure.py (4 tests, all pass).
"""
import json
import sys
from pathlib import Path
from collections import OrderedDict
from typing import Dict, List, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

# Project root
PROJECT = Path(__file__).resolve().parent.parent
EXP = PROJECT / "experiments"

sys.path.insert(0, str(EXP))


# ─── Color map (非基准变体) ───────────────────────────────────────────

def get_bar_colors(variants: List[str]) -> Dict[str, str]:
    """Return color map for non-baseline variants."""
    colors = OrderedDict([("B", "#E69F00"),  # orange
                          ("C", "#56B4E9"),  # blue
                          ("D", "#009E73")])  # green
    return {v: colors[v] for v in variants if v in colors}


# ─── Data preparation ──────────────────────────────────────────────────

def prepare_bar_data(table: Dict[str, Dict[str, dict]],
                     classes: List[str],
                     variants: List[str],
                     metrics: List[str]) -> Dict[str, Dict[str, np.ndarray]]:
    """Extract per-variant, per-metric degradation arrays for bar plotting.

    Args:
        table: compare_variants() output  {class: {variant: {metric: val}}}
        classes: ["S1", "S2", ...]
        variants: ["B", "C", "D"]  (excludes A)
        metrics: ["f1_raw_degradation_pct", ...]

    Returns:
        {variant: {metric: np.ndarray of length len(classes)}}
    """
    bar_data: Dict[str, Dict[str, np.ndarray]] = {}
    for v in variants:
        bar_data[v] = {}
        for m in metrics:
            arr = np.zeros(len(classes))
            for ci, cls in enumerate(classes):
                if cls in table and v in table[cls]:
                    arr[ci] = table[cls][v].get(m, 0.0)
            bar_data[v][m] = arr
    return bar_data


# ─── Chart generation ──────────────────────────────────────────────────

def gen_ablation_figure(table: Dict[str, Dict[str, dict]],
                        classes: List[str],
                        variants: List[str],
                        metrics: List[str],
                        out_path: str) -> None:
    """Generate a grouped bar chart of per-class degradation.

    Each metric (f1, f2, f3) gets a subplot row; each variant (B, C, D)
    is a bar group within each class.

    Args:
        table: compare_variants() output
        classes: class labels like ["S1 ($N=20$)", ...]
        variants: ["B", "C", "D"]
        metrics: ["f1_raw_degradation_pct", ...]
        out_path: output PDF path
    """
    bar_data = prepare_bar_data(table, classes, variants, metrics)
    colors = get_bar_colors(variants)

    n_metrics = len(metrics)
    n_classes = len(classes)
    n_variants = len(variants)

    fig, axes = plt.subplots(n_metrics, 1, figsize=(7, 2.2 * n_metrics),
                             sharex=True)
    if n_metrics == 1:
        axes = [axes]

    x = np.arange(n_classes)
    width = 0.8 / n_variants

    metric_labels = {
        "f1_raw_degradation_pct": r"$f_1^*$ degradation (\%)",
        "f2_degradation_pct": r"$f_2$ degradation (\%)",
        "f3_degradation_pct": r"$f_3$ degradation (\%)",
    }

    for mi, metric in enumerate(metrics):
        ax = axes[mi]
        for vi, v in enumerate(variants):
            offset = (vi - n_variants / 2 + 0.5) * width
            vals = bar_data[v][metric]
            ax.bar(x + offset, vals, width, label=v, color=colors[v],
                   edgecolor="white", linewidth=0.5, alpha=0.9)
        ax.set_ylabel(metric_labels.get(metric, metric))
        ax.axhline(y=0, color="grey", linewidth=0.5)
        ax.legend(loc="upper right", fontsize=8, ncol=n_variants)
        ax.grid(axis="y", alpha=0.3)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(classes, fontsize=9)

    fig.tight_layout(pad=1.0)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ─── Real-data loader ──────────────────────────────────────────────────

def load_real_table() -> Tuple[Dict, List[str], List[str], List[str]]:
    """Load A/B/C/D ablation data and compute degradation table."""
    from analyze_ablation import load_progress, compare_variants, VARIANT_DIRS

    variants = {}
    for vid, dirname in VARIANT_DIRS.items():
        fp = EXP / "results" / dirname / "_progress.json"
        variants[vid] = load_progress(str(fp))

    table = compare_variants(variants)

    classes = [c for c in sorted(table.keys()) if c in ('S1','S2','S3','S4')]
    plot_variants = ["B", "C", "D"]
    metrics = ["f1_raw_degradation_pct", "f2_degradation_pct",
               "f3_degradation_pct"]

    return table, classes, plot_variants, metrics


# ─── CLI ───────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(PROJECT / "docs" /
                         "small-paper-figures" / "fig6_ablation.pdf"))
    parser.add_argument("--classes", nargs="*", default=None,
                        help="Class labels (default: S1-S4)")
    args = parser.parse_args()

    table, classes, variants, metrics = load_real_table()
    # Pretty labels for x-axis
    class_labels = {
        "S1": "S1 ($N{=}20$)",
        "S2": "S2 ($N{=}100$)",
        "S3": "S3 ($N{=}300$)",
        "S4": "S4 ($N{=}500$)",
    }
    labels = [class_labels.get(c, c) for c in classes]

    print(f"Generating ablation chart: {len(classes)} classes, "
          f"{len(variants)} variants, {len(metrics)} metrics")
    gen_ablation_figure(table, labels, variants, metrics, args.out)
    print(f"Saved to: {args.out}")


if __name__ == "__main__":
    main()
