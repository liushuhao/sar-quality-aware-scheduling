#!/usr/bin/env python3
"""
Compute per-group f2, f3 statistics from raw progress files,
then generate Table 1 markdown with f1*/f2/f3 ± std and HV data.
"""
import json
import numpy as np
from collections import defaultdict
import os
from pathlib import Path

PROJECT = str(Path(__file__).resolve().parent.parent)
RESULTS = os.path.join(PROJECT, "experiments", "results")

# Load source data
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Load statistical_results.json for f1 and HV
stats = load_json(os.path.join(RESULTS, "statistical_results.json"))
per_group = stats["per_group"]

# Load raw files for f2, f3
baselines = load_json(os.path.join(RESULTS, "baselines_200.json"))
b2_progress = load_json(os.path.join(RESULTS, "b2_profit_bl", "_progress.json"))
moea2_progress = load_json(os.path.join(RESULTS, "moea_2obj", "_progress.json"))
moea3_progress = load_json(os.path.join(RESULTS, "moea_3obj", "_progress.json"))

# Map user-friendly solver names to raw source + key
SOLVERS = ["G-BL", "G-SM", "GA-P-BL", "MOEA-2", "MOEA-3"]

def scenario_group(key):
    return key.split("/")[0]

# Collect per-scenario f2, f3 raw values
# structure: {group: {solver: {f1_list, f2_list, f3_list}}}
raw_data = defaultdict(lambda: defaultdict(lambda: {"f1": [], "f2": [], "f3": []}))

# G-BL and G-SM from baselines_200.json
for key, scenario in baselines.items():
    g = scenario_group(key)
    if g not in ("S1", "S2", "S3", "S4"):
        continue
    # G-BL = b1
    if "b1" in scenario:
        b1 = scenario["b1"]
        raw_data[g]["G-BL"]["f1"].append(b1.get("f1", 0))
        raw_data[g]["G-BL"]["f2"].append(b1.get("f2", 0))
        raw_data[g]["G-BL"]["f3"].append(b1.get("f3", 0))
    # G-SM = b3
    if "b3" in scenario:
        b3 = scenario["b3"]
        raw_data[g]["G-SM"]["f1"].append(b3.get("f1", 0))
        raw_data[g]["G-SM"]["f2"].append(b3.get("f2", 0))
        raw_data[g]["G-SM"]["f3"].append(b3.get("f3", 0))

# GA-P-BL from b2_profit_bl/_progress.json → completed
for key, entry in b2_progress.get("completed", {}).items():
    g = scenario_group(key)
    if g not in ("S1", "S2", "S3", "S4"):
        continue
    raw_data[g]["GA-P-BL"]["f1"].append(entry.get("f1", 0))
    raw_data[g]["GA-P-BL"]["f2"].append(entry.get("f2", 0))
    raw_data[g]["GA-P-BL"]["f3"].append(entry.get("f3", 0))

# MOEA-2
for key, entry in moea2_progress.get("completed", {}).items():
    g = scenario_group(key)
    if g not in ("S1", "S2", "S3", "S4"):
        continue
    raw_data[g]["MOEA-2"]["f1"].append(entry.get("f1", 0))
    raw_data[g]["MOEA-2"]["f2"].append(entry.get("f2", 0))
    raw_data[g]["MOEA-2"]["f3"].append(entry.get("f3", 0))

# MOEA-3
for key, entry in moea3_progress.get("completed", {}).items():
    g = scenario_group(key)
    if g not in ("S1", "S2", "S3", "S4"):
        continue
    raw_data[g]["MOEA-3"]["f1"].append(entry.get("f1", 0))
    raw_data[g]["MOEA-3"]["f2"].append(entry.get("f2", 0))
    raw_data[g]["MOEA-3"]["f3"].append(entry.get("f3", 0))

# Compute means and stds
GROUPS = ["S1", "S2", "S3", "S4"]
GROUP_LABELS = {"S1": "S1 (N=20)", "S2": "S2 (N=100)", "S3": "S3 (N=300)", "S4": "S4 (N=500)"}

print("=== Per-group sample counts ===")
for g in GROUPS:
    for s in SOLVERS:
        n = len(raw_data[g][s]["f2"])
        print(f"  {g}/{s}: f2={n}, f3={n}, f1={len(raw_data[g][s]['f1'])}")

# Build the table data
# For f1, we use per_group from statistical_results.json (already normalized f1*)
# For f2/f3, we compute from raw data

def fmt_val(mean, std, decimals=3):
    """Format mean ± std with sensible precision."""
    if std < 0.001:
        return f"{mean:.{decimals}f}"
    # Match decimal places to std magnitude
    if std < 0.01:
        d = 4
    elif std < 0.1:
        d = 3
    elif std < 1.0:
        d = 2
    else:
        d = 1
    # But for f1*, use 2 decimal places always
    return f"{mean:.{d}f}±{std:.{d}f}"

def fmt_f1(mean, std, decimals=2):
    """Format f1* with 2 decimal places."""
    if std < 0.001:
        return f"{mean:.{decimals}f}"
    return f"{mean:.{decimals}f}±{std:.{decimals}f}"

# Build markdown
lines = []
lines.append("# Table 1: Solver Performance Matrix (per Scenario Group)")
lines.append("")
lines.append("**5 solvers × 4 groups × 3 metrics** (mean ± 1 SD across 50 seeds per group)")
lines.append("")
lines.append("| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |")
lines.append("|:---|:---|:---|:---|:---|")

for solver in SOLVERS:
    cells = []
    for group in GROUPS:
        # f1 from per_group (normalized f1*)
        pg = per_group[group].get(solver, {})
        f1_mean = pg.get("f1_mean", 0)
        f1_std = pg.get("f1_std", 0)
        
        # f2, f3 from raw data
        rd = raw_data[group][solver]
        f2_vals = rd["f2"]
        f3_vals = rd["f3"]
        f2_mean = np.mean(f2_vals) if f2_vals else 0
        f2_std = np.std(f2_vals, ddof=1) if len(f2_vals) > 1 else 0
        f3_mean = np.mean(f3_vals) if f3_vals else 0
        f3_std = np.std(f3_vals, ddof=1) if len(f3_vals) > 1 else 0
        
        cell = f"{fmt_f1(f1_mean, f1_std)} / {fmt_val(f2_mean, f2_std)} / {fmt_val(f3_mean, f3_std)}"
        cells.append(cell)
    
    row = f"| {solver} | " + " | ".join(cells) + " |"
    lines.append(row)

lines.append("")
lines.append("**Footnotes:**")
lines.append("- **f1\\*** = coverage fraction relative to G-BL baseline (f1_raw / f1_G-BL)")
lines.append("- **f2** = comprehensive geometric quality (lower is better)")
lines.append("- **f3** = NESZ radiation quality (lower is better)")
lines.append("- Each cell shows: **f1\\* ± SD / f2 ± SD / f3 ± SD**")
lines.append("- All statistics computed across 50 random seeds per scenario group")
lines.append("")

# HV mini-table
lines.append("## Hypervolume (HV) by Solver and Group")
lines.append("")
lines.append("Normalized 3D HV (reference point: [0, 0, 0], all objectives maximized after normalization).")
lines.append("")
lines.append("| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |")
lines.append("|:---|:---|:---|:---|:---|")

for solver in SOLVERS:
    cells_hv = []
    for group in GROUPS:
        pg = per_group[group].get(solver, {})
        hv_mean = pg.get("hv_mean", 0)
        hv_std = pg.get("hv_std", 0)
        cell = f"{hv_mean:.4f}±{hv_std:.4f}"
        cells_hv.append(cell)
    row = f"| {solver} | " + " | ".join(cells_hv) + " |"
    lines.append(row)

lines.append("")
lines.append("**Note:** Higher HV = better overall multi-objective performance.")
lines.append("")

# Overall HV summary
hv_global = stats.get("hv_by_solver", {})
if hv_global:
    lines.append("## Overall HV (across all 200 scenarios)")
    lines.append("")
    lines.append("| Solver | HV Mean | HV Std |")
    lines.append("|:---|---:|---:|")
    for solver in SOLVERS:
        hv = hv_global.get(solver, {})
        lines.append(f"| {solver} | {hv.get('mean', 0):.4f} | {hv.get('std', 0):.4f} |")
    lines.append("")

# Write file
out_path = os.path.join(PROJECT, "docs", "table1-solver-matrix.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✓ Table written to: {out_path}")
print("\n=== Preview ===")
print("\n".join(lines))
