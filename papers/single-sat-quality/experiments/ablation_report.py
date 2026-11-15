"""Ablation report generator: convert compare_variants() output to Markdown.

Output is designed to be pasted directly into the IJAE paper §X.X
ablation section. See handoffs/ablation-study-naming.md.
"""
import math
import os
from typing import Dict

from analyze_ablation import VARIANT_LABELS, _METRIC_FIELDS


# ─── Value formatting ───────────────────────────────────────────────────

def format_value(value, field_name: str) -> str:
    """Format a metric value based on the field type.

    - means: 4 decimal places
    - degradation_pct: 1 decimal + %
    - pvalue: scientific notation
    - missing/NaN: em-dash
    """
    if value is None:
        return "—"
    try:
        if math.isnan(value) or math.isinf(value):
            return "—"
    except TypeError:
        return "—"

    if field_name.endswith("_pvalue"):
        return f"{value:.1e}"
    elif field_name.endswith("_degradation_pct"):
        return f"{value:.1f}%"
    elif field_name.endswith("_mean") or field_name.endswith("_std"):
        return f"{value:.4f}"
    else:
        return str(value)


# ─── Markdown rendering ─────────────────────────────────────────────────

def render_markdown(table: Dict[str, Dict[str, dict]]) -> str:
    """Render a compare_variants() table as a Markdown report.

    For each class, produces a table with:
    - One row per metric (f1, f2, f3, n_selected)
    - One column per non-baseline variant showing "(value | deg% p=X)"
    - Plus a baseline (A) column for reference
    """
    if not table:
        return "# Ablation Study Report\n\nNo data available.\n"

    lines: list = []
    lines.append("# Ablation Study Report")
    lines.append("")
    lines.append("Comparison of MOEA-3 variants (A=full, B=no ψ, C=no θ, D=no physics)")
    lines.append("Each cell shows: value | degradation% vs A | p-value")
    lines.append("")

    variant_ids = list(VARIANT_LABELS.keys())
    classes = sorted(table.keys())

    for cls in classes:
        lines.append(f"## Class {cls}")
        lines.append("")
        if cls not in table:
            lines.append("_(no data)_")
            lines.append("")
            continue

        cls_table = table[cls]

        # Build header row
        header = ["Metric", "A (baseline)"]
        non_baseline = [v for v in variant_ids if v != "A" and v in cls_table]
        header.extend([f"{v} ({VARIANT_LABELS.get(v, v)})" for v in non_baseline])
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join(["---"] * len(header)) + "|")

        # Build rows
        for field in _METRIC_FIELDS:
            mean_key = f"{field}_mean"
            deg_key = f"{field}_degradation_pct"
            pval_key = f"{field}_pvalue"

            a_val = cls_table.get("A", {}).get(mean_key)
            row_cells = [field, format_value(a_val, mean_key)]
            for v in non_baseline:
                v_val = cls_table[v].get(mean_key)
                deg = cls_table[v].get(deg_key)
                pv = cls_table[v].get(pval_key)
                # Format as "value | deg% | p=X"
                if v_val is None:
                    row_cells.append("—")
                else:
                    cell = format_value(v_val, mean_key)
                    if deg is not None:
                        cell += f" | {format_value(deg, deg_key)}"
                    if pv is not None and isinstance(pv, float):
                        cell += f" | p={format_value(pv, pval_key)}"
                    row_cells.append(cell)
            lines.append("| " + " | ".join(row_cells) + " |")

        # n_scenarios row
        n_cells = ["n_scenarios", str(cls_table.get("A", {}).get("n_scenarios", "—"))]
        for v in non_baseline:
            n_cells.append(str(cls_table[v].get("n_scenarios", "—")))
        lines.append("| " + " | ".join(n_cells) + " |")
        lines.append("")

    return "\n".join(lines)


# ─── File output ────────────────────────────────────────────────────────

def save_report(table: Dict[str, Dict[str, dict]], out_path: str) -> None:
    """Write the markdown report to a file."""
    md = render_markdown(table)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)


# ─── CLI entry point ────────────────────────────────────────────────────

def main():
    import argparse
    from pathlib import Path
    from analyze_ablation import load_progress, compare_variants, VARIANT_DIRS

    PROJECT = Path(__file__).resolve().parent.parent
    RESULTS = PROJECT / "experiments" / "results"

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(RESULTS / "ablation_summary.md"))
    args = parser.parse_args()

    variants = {}
    for vid, dirname in VARIANT_DIRS.items():
        fp = RESULTS / dirname / "_progress.json"
        try:
            variants[vid] = load_progress(str(fp))
            print(f"Loaded {vid}: {len(variants[vid])} scenarios")
        except FileNotFoundError as e:
            print(f"[SKIP] {vid}: {e}")

    if not variants:
        print("No variant data. Aborting.")
        return

    table = compare_variants(variants)
    save_report(table, args.out)
    print(f"\nReport saved to: {args.out}")


if __name__ == "__main__":
    main()
