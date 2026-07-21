"""Standalone ablation figure generator for Fig 6.

Reads A/B/C/D variant _progress.json directly, pairs by scenario key,
computes per-class, per-variant mean degradation vs baseline A.

The MOEA-3 baseline (A) for S1/S2 stores f2/f3 as SUM (old format),
while new-format runs (S3/S4, and all B/C/D variants) store f2/f3 as
per-task MEAN. We detect the format and normalize accordingly.

Output: papers/single-sat-quality/figures/fig6_ablation.pdf
No dependency on analyze_ablation.py — completely self-contained.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "experiments" / "results"
FIG_DIR = PROJECT / "docs" / "small-paper-figures"

VARIANT_DIRS = {
    "A": "moea_3obj",
    "B": "moea_3obj_no_squint",
    "C": "moea_3obj_no_incidence",
    "D": "moea_3obj_no_physics",
}
CLASSES = ["S1", "S2", "S3", "S4"]
CLASS_LABELS = {
    "S1": "S1 ($N{=}20$)",
    "S2": "S2 ($N{=}100$)",
    "S3": "S3 ($N{=}300$)",
    "S4": "S4 ($N{=}500$)",
}


def _is_sum_format(entry: dict) -> bool:
    """Detect if f2/f3 is in SUM format (> 1.0) vs per-task MEAN."""
    f2 = entry.get("f2", 0.0) or 0.0
    return f2 > 1.0


def _get_per_task(entry: dict, metric: str, n_sel: int) -> float:
    """Return per-task value for f2/f3; raw value for f1."""
    val = float(entry.get(metric, 0.0) or 0.0)
    if metric in ("f2", "f3") and _is_sum_format(entry) and n_sel > 0:
        return val / n_sel
    return val


def load_all() -> dict:
    """Return {variant_id: {scenario_key: {cls, f1, f2, f3, n_sel}}}."""
    data = {}
    for vid, dname in VARIANT_DIRS.items():
        fp = RESULTS / dname / "_progress.json"
        with open(fp) as f:
            completed = json.load(f).get("completed", {})
        entries = {}
        for key, entry in completed.items():
            cls = key.split("/")[0]
            if cls not in CLASSES:
                continue
            n_sel = int(entry.get("n_selected", 0))
            f1 = float(entry.get("f1_raw", entry.get("f1", 0.0)))
            if n_sel > 0:
                f1 = f1 / n_sel
            entries[key] = {
                "cls": cls,
                "f1": f1,
                "f2": _get_per_task(entry, "f2", n_sel),
                "f3": _get_per_task(entry, "f3", n_sel),
                "n_sel": n_sel,
            }
        data[vid] = entries
        print(f"  {vid}: {len(entries)} entries")
    return data


def compute_degradations(data: dict) -> dict:
    """Return {metric: {variant: {class: degradation_pct}}}."""
    metrics = ["f1", "f2", "f3"]
    variants_non_a = ["B", "C", "D"]

    result = {}
    for metric in metrics:
        result[metric] = {}
        for v in variants_non_a:
            result[metric][v] = {}
            for cls in CLASSES:
                a_keys = [k for k in data["A"] if data["A"][k]["cls"] == cls]
                a_vals = [data["A"][k][metric] for k in a_keys if k in data[v]]
                v_vals = [data[v][k][metric] for k in a_keys if k in data[v]]
                if a_vals and v_vals and np.mean(a_vals) > 0:
                    deg = (np.mean(a_vals) - np.mean(v_vals)) / np.mean(a_vals) * 100.0
                    result[metric][v][cls] = round(deg, 1)
                else:
                    result[metric][v][cls] = 0.0
    return result


def generate_figure(degs: dict) -> None:
    """Generate grouped bar chart: 3 subplots (f1/f2/f3) × 4 classes."""
    variants = ["B", "C", "D"]
    colors = {"B": "#E69F00", "C": "#56B4E9", "D": "#009E73"}
    metrics = ["f1", "f2", "f3"]
    metric_labels = {
        "f1": r"$f_1$ per task",
        "f2": r"$f_2$ degradation (%)",
        "f3": r"$f_3$ degradation (%)",
    }

    fig, axes = plt.subplots(len(metrics), 1, figsize=(8, 5.5), sharex=True)

    x = np.arange(len(CLASSES))
    width = 0.8 / len(variants)

    for mi, metric in enumerate(metrics):
        ax = axes[mi]
        has_data = False
        for vi, v in enumerate(variants):
            offset = (vi - len(variants) / 2 + 0.5) * width
            vals = [degs[metric][v].get(cls, 0.0) for cls in CLASSES]
            if any(abs(v) > 0.1 for v in vals):
                has_data = True
            ax.bar(x + offset, vals, width, label=v, color=colors[v],
                   edgecolor="white", linewidth=0.5, alpha=0.9)
        ax.axhline(y=0, color="grey", linewidth=0.5)
        ax.set_ylabel(metric_labels.get(metric, metric), fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        if has_data:
            ax.legend(loc="upper right", fontsize=8, ncol=3)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels([CLASS_LABELS[c] for c in CLASSES], fontsize=10)

    fig.tight_layout(pad=1.0)
    out = FIG_DIR / "fig6_ablation.pdf"
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {out} ({out.stat().st_size} bytes)")


def main():
    print("Loading ablation data...")
    data = load_all()
    print("Computing degradations...")
    degs = compute_degradations(data)
    for metric in ["f1", "f2", "f3"]:
        for cls in CLASSES:
            vals = {v: degs[metric][v][cls] for v in ["B", "C", "D"]}
            print(f"  {metric} {cls}: B={vals['B']:+.1f}% C={vals['C']:+.1f}% D={vals['D']:+.1f}%")
    print("\nGenerating figure...")
    generate_figure(degs)
    print("Done.")


if __name__ == "__main__":
    main()
