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
matplotlib.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})
import matplotlib.pyplot as plt

from scipy.stats import wilcoxon

PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "experiments" / "results"
FIG_DIR = PROJECT / "figures"
BASELINES_PATH = RESULTS / "baselines_200.json"

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
    """Return normalized metrics keyed by variant and scenario."""
    with open(BASELINES_PATH) as f:
        baselines = json.load(f)
    gbl_profit = {key: entry["b1"]["f1_raw"] for key, entry in baselines.items()}

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
            f1_raw = float(entry.get("f1_raw", entry.get("f1", 0.0)))
            f1_ref = float(gbl_profit.get(key, 0.0))
            if f1_ref <= 0:
                raise KeyError(f"Missing positive G-BL reference profit for {key}")
            entries[key] = {
                "cls": cls,
                "f1": f1_raw / f1_ref,
                "f2": _get_per_task(entry, "f2", n_sel),
                "f3": _get_per_task(entry, "f3", n_sel),
                "n_sel": n_sel,
            }
        data[vid] = entries
        print(f"  {vid}: {len(entries)} entries")

    # Cross-variant + G-BL pkl_sha1 consistency: paired per-scenario comparison
    # requires all variants + the baseline reference on the same pkls.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _provenance import check_pkl_sha1_consistency
    _raw = {}
    for vid, dname in VARIANT_DIRS.items():
        with open(RESULTS / dname / "_progress.json") as f:
            completed = json.load(f).get("completed", {})
        _raw[vid] = {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
                     for k, v in completed.items()}
    _raw["G-BL"] = {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
                    for k, v in baselines.items()}
    check_pkl_sha1_consistency(_raw, label="ablation-fig6")
    return data


def compute_degradations(data: dict) -> tuple[dict, dict]:
    """Return degradation percentages and paired Wilcoxon p-values."""
    metrics = ["f1", "f2", "f3"]
    variants_non_a = ["B", "C", "D"]

    result = {}
    pvalues = {}
    for metric in metrics:
        result[metric] = {}
        pvalues[metric] = {}
        for v in variants_non_a:
            result[metric][v] = {}
            pvalues[metric][v] = {}
            for cls in CLASSES:
                paired_keys = [
                    k for k in data["A"]
                    if data["A"][k]["cls"] == cls and k in data[v]
                ]
                a_vals = np.asarray([data["A"][k][metric] for k in paired_keys])
                v_vals = np.asarray([data[v][k][metric] for k in paired_keys])
                if len(a_vals) and np.mean(a_vals) > 0:
                    deg = (np.mean(a_vals) - np.mean(v_vals)) / np.mean(a_vals) * 100.0
                    result[metric][v][cls] = round(deg, 1)
                    differences = a_vals - v_vals
                    if np.allclose(differences, 0.0):
                        pvalues[metric][v][cls] = 1.0
                    else:
                        pvalues[metric][v][cls] = float(
                            wilcoxon(a_vals, v_vals).pvalue
                        )
                else:
                    result[metric][v][cls] = 0.0
                    pvalues[metric][v][cls] = 1.0
    return result, pvalues


def generate_figure(degs: dict, pvalues: dict) -> None:
    """Generate grouped degradation bars; mark significant f1 comparisons."""
    variants = ["B", "C", "D"]
    # Distinct from the solver palette used in Figs. 1--5. This palette passes
    # the dataviz CVD/lightness/chroma/contrast validator on a light surface.
    colors = {"B": "#AA3377", "C": "#228833", "D": "#3366AA"}
    hatches = {"B": "///", "C": "\\\\", "D": ".."}
    variant_labels = {"B": "no squint", "C": "no incidence", "D": "no physics"}
    metrics = ["f1", "f2", "f3"]
    metric_labels = {
        "f1": r"$f_1^*$ degradation (%)",
        "f2": r"$f_2$ degradation (%)",
        "f3": r"$f_3$ degradation (%)",
    }

    fig, axes = plt.subplots(len(metrics), 1, figsize=(8, 5.8), sharex=True)

    x = np.arange(len(CLASSES))
    width = 0.8 / len(variants)

    for mi, metric in enumerate(metrics):
        ax = axes[mi]
        for vi, v in enumerate(variants):
            offset = (vi - len(variants) / 2 + 0.5) * width
            vals = [degs[metric][v].get(cls, 0.0) for cls in CLASSES]
            bars = ax.bar(
                x + offset, vals, width, label=variant_labels[v],
                color=colors[v], hatch=hatches[v], edgecolor="white",
                linewidth=0.6, alpha=0.9,
            )
            # Statistical claim in the paper concerns normalized profit f1*.
            # Mark only those pre-specified A-vs-variant comparisons that pass
            # the manuscript's Bonferroni threshold (p < 0.005).
            if metric == "f1":
                for cls, bar in zip(CLASSES, bars):
                    if pvalues[metric][v].get(cls, 1.0) < 0.005:
                        y = bar.get_height()
                        offset_pts = 3 if y >= 0 else -9
                        ax.annotate(
                            "*", xy=(bar.get_x() + bar.get_width() / 2, y),
                            xytext=(0, offset_pts), textcoords="offset points",
                            ha="center", va="bottom" if y >= 0 else "top",
                            fontsize=10, fontweight="bold", color="#222",
                        )
        ax.axhline(y=0, color="#555", linewidth=0.6)
        ax.set_ylabel(metric_labels[metric], fontsize=9)
        ax.grid(axis="y", color="#D0D0D0", linewidth=0.5, alpha=0.55)

    # Collect legend handles from the first subplot
    handles = []
    labels = []
    for vi, v in enumerate(variants):
        bar = axes[0].containers[vi]
        handles.append(bar)
        labels.append(variant_labels[v])

    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.06),
               ncol=3, frameon=True, framealpha=0.9, fontsize=7.5,
               borderaxespad=0.0)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels([CLASS_LABELS[c] for c in CLASSES], fontsize=9)
    fig.text(
        0.5, 0.02,
        r"* paired Wilcoxon vs A, $p<0.005$ (Bonferroni threshold); negative = variant outperforms A",
        ha="center", va="bottom", fontsize=7, color="#444",
    )

    fig.tight_layout(rect=(0, 0.08, 1, 1), pad=1.0)
    out = FIG_DIR / "fig6_ablation.pdf"
    preview = FIG_DIR / "fig6_ablation.png"
    fig.savefig(str(out), dpi=300, bbox_inches="tight")
    fig.savefig(str(preview), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {out} ({out.stat().st_size} bytes)")
    print(f"  -> {preview} ({preview.stat().st_size} bytes)")


def main():
    print("Loading ablation data...")
    data = load_all()
    print("Computing degradations...")
    degs, pvalues = compute_degradations(data)
    for metric in ["f1", "f2", "f3"]:
        for cls in CLASSES:
            vals = {v: degs[metric][v][cls] for v in ["B", "C", "D"]}
            print(f"  {metric} {cls}: B={vals['B']:+.1f}% C={vals['C']:+.1f}% D={vals['D']:+.1f}%")
    print("\nGenerating figure...")
    generate_figure(degs, pvalues)
    print("Done.")


if __name__ == "__main__":
    main()
