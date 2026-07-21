"""Ablation analysis: load and compare A/B/C/D MOEA variants.

Outputs per-class, per-variant metric tables for the IJAE paper §X.X
ablation section. See handoffs/ablation-study-naming.md for variant
definitions.
"""
import json
import math
import os
from collections import defaultdict, OrderedDict
from typing import Dict, List

import numpy as np
from scipy import stats


# Variant directory names (must match run_*.py RESULTS_DIR)
VARIANT_DIRS = OrderedDict([
    ("A", "moea_3obj"),
    ("B", "moea_3obj_no_squint"),
    ("C", "moea_3obj_no_incidence"),
    ("D", "moea_3obj_no_physics"),
])

VARIANT_LABELS = {
    "A": "full (sinθ·cosψ, cos³θ·cos³ψ)",
    "B": "no ψ (sinθ, cos³θ)",
    "C": "no θ (cosψ, cos³ψ)",
    "D": "no physics (1, 1)",
}


# ─── Data loading ────────────────────────────────────────────────────────

def load_progress(json_path: str) -> Dict[str, dict]:
    """Read _progress.json, return the 'completed' dict.

    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"_progress.json not found: {json_path}")
    with open(json_path) as f:
        data = json.load(f)
    return data.get("completed", {})


# ─── Aggregation ─────────────────────────────────────────────────────────

def aggregate_by_class(completed: Dict[str, dict]) -> Dict[str, Dict[str, dict]]:
    """Group entries by scenario class (S1, S2, ...).

    Returns: {class_name: {scenario_key: entry_dict}}
    """
    grouped: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for key, entry in completed.items():
        if "/" not in key:
            continue
        cls = key.split("/")[0]
        grouped[cls][key] = entry
    return dict(grouped)


# ─── Metric helpers ──────────────────────────────────────────────────────

def compute_per_task_f1(entry: dict) -> float:
    """f1_per_task = f1_raw / n_selected, or 0 if n_selected=0."""
    n_sel = entry.get("n_selected", 0)
    if n_sel <= 0:
        return 0.0
    # Use f1_raw if available (variants B/C/D), else compute from f1 and f1_gbl
    f1_raw = entry.get("f1_raw")
    if f1_raw is None:
        f1_raw = entry.get("f1", 0.0) * max(entry.get("f1_gbl", 100.0), 1.0)
    return f1_raw / n_sel


def compute_degradation_pct(baseline: float, variant: float) -> float:
    """degradation = (baseline - variant) / baseline × 100.

    Positive means variant is worse. Negative means variant is better.
    Returns 0.0 if baseline=0 (avoid div by zero).
    """
    if baseline == 0:
        return 0.0
    return (baseline - variant) / baseline * 100.0


# ─── Statistics ──────────────────────────────────────────────────────────

def wilcoxon_pvalue(a: List[float], b: List[float]) -> float:
    """Wilcoxon signed-rank p-value (paired, non-parametric).
    Returns 1.0 if arrays are empty or all differences are zero."""
    if len(a) == 0 or len(a) != len(b):
        if len(a) == 0:
            return 1.0
        raise ValueError(f"wilcoxon_pvalue: mismatched lengths ({len(a)} vs {len(b)})")
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    if np.std(a_arr) == 0 and np.std(b_arr) == 0:
        return 1.0  # both constant — no evidence of difference
    res = stats.wilcoxon(a_arr, b_arr)
    p = float(res.pvalue)
    if math.isnan(p) or math.isinf(p):
        return 1.0
    return p


# ─── Comparison ──────────────────────────────────────────────────────────

_METRIC_FIELDS = ["f1_raw", "f1_per_task", "f2", "f3", "n_selected"]


def _summarize_one(entry: dict) -> dict:
    """Compute per-entry derived metrics."""
    f1_raw = entry.get("f1_raw")
    if f1_raw is None:
        f1_norm = entry.get("f1", 0.0)
        f1_ref = entry.get("f1_gbl", 100.0)
        f1_raw = f1_norm * max(f1_ref, 1.0)
    return {
        "f1_raw": f1_raw,
        "f1_per_task": compute_per_task_f1(entry),
        "f2": entry.get("f2", 0.0),
        "f3": entry.get("f3", 0.0),
        "n_selected": entry.get("n_selected", 0),
    }

def compare_variants(variants: Dict[str, Dict[str, dict]]) -> Dict[str, Dict[str, dict]]:
    """Compute per-class, per-variant metric means + degradation vs A.

    Args:
        variants: {variant_id: completed_dict}

    Returns:
        {class: {variant_id: {metric: value_or_paired_degradation}}}

    For variant A: values are means.
    For variants B/C/D: values are means + paired degradation_pct vs A + p_value.
    """
    # 1. Aggregate by class for each variant
    grouped = {v: aggregate_by_class(c) for v, c in variants.items()}
    classes = sorted(set().union(*(g.keys() for g in grouped.values())))

    table: Dict[str, Dict[str, dict]] = {}

    for cls in classes:
        # Use A's keys as reference for paired comparison
        a_keys = sorted(grouped.get("A", {}).get(cls, {}).keys())
        row: Dict[str, dict] = {}

        for variant_id, class_data in grouped.items():
            class_entries = class_data.get(cls, {})

            # Mean values
            means: Dict[str, float] = {}
            for field in _METRIC_FIELDS:
                vals = []
                for k in class_entries:
                    e = class_entries[k]
                    if field == "f1_per_task":
                        vals.append(compute_per_task_f1(e))
                    elif field == "f1_raw":
                        raw = e.get("f1_raw")
                        if raw is None:
                            raw = e.get("f1", 0.0)
                        vals.append(raw)
                    else:
                        v = e.get(field, 0)
                        vals.append(v)
                means[f"{field}_mean"] = float(np.mean(vals)) if vals else 0.0
                means[f"{field}_std"] = float(np.std(vals)) if vals else 0.0

            entry_dict: dict = dict(means)
            entry_dict["n_scenarios"] = len(class_entries)

            # Paired degradation vs A (only for non-baseline variants)
            if variant_id != "A" and a_keys:
                for field in _METRIC_FIELDS:
                    a_vals = []
                    v_vals = []
                    for k in a_keys:
                        if k in class_entries:
                            a_e = grouped["A"][cls][k]
                            v_e = class_entries[k]
                            if field == "f1_per_task":
                                a_vals.append(compute_per_task_f1(a_e))
                                v_vals.append(compute_per_task_f1(v_e))
                            elif field == "n_selected":
                                a_vals.append(a_e.get("n_selected", 0))
                                v_vals.append(v_e.get("n_selected", 0))
                            elif field == "f1_raw":
                                a_raw = a_e.get("f1_raw")
                                if a_raw is None:
                                    a_raw = a_e.get("f1", 0.0)
                                v_raw = v_e.get("f1_raw")
                                if v_raw is None:
                                    v_raw = v_e.get("f1", 0.0)
                                a_vals.append(a_raw)
                                v_vals.append(v_raw)
                            else:
                                a_vals.append(a_e.get(field, 0))
                                v_vals.append(v_e.get(field, 0))
                    if a_vals:
                        a_mean = float(np.mean(a_vals))
                        v_mean = float(np.mean(v_vals))
                        deg = compute_degradation_pct(a_mean, v_mean)
                        p = wilcoxon_pvalue(a_vals, v_vals)
                        entry_dict[f"{field}_degradation_pct"] = deg
                        entry_dict[f"{field}_pvalue"] = p

            row[variant_id] = entry_dict

        table[cls] = row

    return table


# ─── CLI entry point ─────────────────────────────────────────────────────

def main():
    import argparse
    from pathlib import Path

    PROJECT = Path(__file__).resolve().parent.parent
    RESULTS = PROJECT / "experiments" / "results"

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-csv", default=str(PROJECT / "experiments" / "results" / "ablation_summary.csv"))
    parser.add_argument("--out-md", default=str(PROJECT / "experiments" / "results" / "ablation_summary.md"))
    args = parser.parse_args()

    # Load all 4 variants
    variants: Dict[str, Dict[str, dict]] = {}
    for vid, dirname in VARIANT_DIRS.items():
        fp = RESULTS / dirname / "_progress.json"
        print(f"Loading {vid} from {fp} ...")
        try:
            variants[vid] = load_progress(str(fp))
            print(f"  {vid}: {len(variants[vid])} scenarios")
        except FileNotFoundError as e:
            print(f"  [SKIP] {vid}: {e}")
            continue

    if not variants:
        print("No variant data found. Aborting.")
        return

    print("\n=== Comparing variants ===\n")
    table = compare_variants(variants)

    # Print summary to stdout
    for cls in sorted(table.keys()):
        print(f"\n--- Class {cls} ---")
        for vid in VARIANT_DIRS:
            if vid not in table.get(cls, {}):
                continue
            row = table[cls][vid]
            n = row.get("n_scenarios", 0)
            print(f"  {vid}: n={n}, "
                  f"f1={row.get('f1_mean', 0):.4f}, "
                  f"f2={row.get('f2_mean', 0):.4f}, "
                  f"f3={row.get('f3_mean', 0):.4f}, "
                  f"n_sel={row.get('n_selected_mean', 0):.1f}")

    # Save CSV
    import csv
    with open(args.out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["class", "variant", "n_scenarios"]
        for field in _METRIC_FIELDS:
            header.extend([f"{field}_mean", f"{field}_std"])
        for field in _METRIC_FIELDS:
            header.extend([f"{field}_deg_pct_vs_A", f"{field}_pvalue_vs_A"])
        writer.writerow(header)
        for cls in sorted(table.keys()):
            for vid in VARIANT_DIRS:
                if vid not in table[cls]:
                    continue
                row = table[cls][vid]
                line = [cls, vid, row.get("n_scenarios", 0)]
                for field in _METRIC_FIELDS:
                    line.append(f"{row.get(f'{field}_mean', 0):.6f}")
                    line.append(f"{row.get(f'{field}_std', 0):.6f}")
                for field in _METRIC_FIELDS:
                    deg = row.get(f"{field}_degradation_pct", "")
                    pv = row.get(f"{field}_pvalue", "")
                    line.append(f"{deg:.4f}" if isinstance(deg, float) else "")
                    line.append(f"{pv:.4e}" if isinstance(pv, float) else "")
                writer.writerow(line)
    print(f"\nCSV saved to: {args.out_csv}")


if __name__ == "__main__":
    main()
