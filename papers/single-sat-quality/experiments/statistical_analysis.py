#!/usr/bin/env python3
"""
Statistical analysis pipeline for 5-solver comparison on 300 scenarios.

Loads results from:
  experiments/results/baselines_200.json    → G-BL, G-SM
  experiments/results/b2_profit/_progress.json → GA-P
  experiments/results/moea_2obj/_progress.json → MOEA-2
  experiments/results/moea_3obj/_progress.json → MOEA-3

Outputs:
  experiments/results/statistical_results.json  — per-scenario HV, p-values, effect sizes
  experiments/results/solver_summary.csv        — solver × scenario_group summary
"""
import json, os, sys
from collections import defaultdict
from itertools import combinations

import numpy as np
from scipy import stats as scipy_stats

# ── Paths ──
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "experiments", "results")

BASELINES_PATH = os.path.join(RESULTS, "baselines_200.json")
B2_PATH = os.path.join(RESULTS, "b2_profit_bl", "_progress.json")
MOEA2_PATH = os.path.join(RESULTS, "moea_2obj", "_progress.json")
MOEA3_PATH = os.path.join(RESULTS, "moea_3obj", "_progress.json")

OUT_JSON = os.path.join(RESULTS, "statistical_results.json")
OUT_CSV = os.path.join(RESULTS, "solver_summary.csv")

# ── Utility ──
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def scenario_group(key):
    """Extract scenario group (S1-S6) from key like 'S1/S1-A_seed00.pkl'"""
    return key.split("/")[0]

def n_targets_from_key(key):
    """Best-effort n_targets from scenario group label"""
    # The actual n_targets is inside the result data, but group gives rough estimate
    mapping = {"S1": 20, "S2": 100, "S3": 300, "S4": 500, "S5": 20, "S6": 20}
    g = scenario_group(key)
    return mapping.get(g, 0)

# ── 1. Load all data ──
print("Loading data...")

# Baselines: nested dict {scenario_key: {b1: {...}, b2: {...}, b3: {...}}}
bl_data = load_json(BASELINES_PATH)
print(f"  Baselines: {len(bl_data)} scenarios")

# GA-P-BL: {completed: {scenario_key: {f1,f2,f3,...}}}
b2_raw = load_json(B2_PATH)
b2_data = b2_raw.get("completed", {})
print(f"  GA-P-BL: {len(b2_data)} scenarios")

# MOEA-2: {completed: {scenario_key: {f1,f2,f3,frontier_f1,frontier_f2,frontier_f3,...}}}
m2_raw = load_json(MOEA2_PATH)
m2_data = m2_raw.get("completed", {})
print(f"  MOEA-2: {len(m2_data)} scenarios")

# MOEA-3: same structure
m3_raw = load_json(MOEA3_PATH)
m3_data = m3_raw.get("completed", {})
print(f"  MOEA-3: {len(m3_data)} scenarios")

# ── 1b. Cross-family pkl_sha1 consistency guard ──
# Families MUST run on the same pkl bytes to be comparable; a regenerated pkl
# applied to only one family makes pairwise tests / Table 1 meaningless.
# See _provenance.check_pkl_sha1_consistency for semantics.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _provenance import check_pkl_sha1_consistency
check_pkl_sha1_consistency({
    "G-BL/G-SM": {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
                  for k, v in bl_data.items()},
    "GA-P-BL": {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
                for k, v in b2_data.items()},
    "MOEA-2": {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
               for k, v in m2_data.items()},
    "MOEA-3": {k: (v.get("pkl_sha1") if isinstance(v, dict) else None)
               for k, v in m3_data.items()},
}, label="cross-family")

# ── 2. Collect per-scenario results ──
# Structure: results[scenario_key] = {
#   "G-BL": {"f1":..., "f2":..., "f3":..., "n_targets":..., "n_selected":..., "runtime_s":..., "frontier": [(f1,f2,f3)]},
#   "G-SM": {...}, "GA-P-BL": {...}, "MOEA-2": {...}, "MOEA-3": {...},
#   "group": "S1",
# }

SOLVERS = ["G-BL", "G-SM", "GA-P-BL", "MOEA-2", "MOEA-3"]
results = {}

def add_single_point(results_dict, key, solver, f1, f2, f3, n_targets, n_selected, runtime_s):
    if key not in results_dict:
        results_dict[key] = {}
    results_dict[key][solver] = {
        "f1": f1, "f2": f2, "f3": f3,
        "n_targets": n_targets, "n_selected": n_selected,
        "runtime_s": runtime_s,
        "frontier": [(f1, f2, f3)],  # single point = frontier of size 1
    }

def add_moea_frontier(results_dict, key, solver, entry):
    """Add MOEA result with actual Pareto frontier."""
    if key not in results_dict:
        results_dict[key] = {}
    n_targets = entry.get("n_targets", 0)
    n_selected = entry.get("n_selected", 0)
    runtime_s = entry.get("runtime_s", 0)
    frontier_f1 = entry.get("frontier_f1", [])
    frontier_f2 = entry.get("frontier_f2", [])
    frontier_f3 = entry.get("frontier_f3", [])
    if frontier_f1:
        frontier = list(zip(frontier_f1, frontier_f2, frontier_f3))
    else:
        # Fallback: single point from f1,f2,f3
        frontier = [(entry.get("f1", 0), entry.get("f2", 0), entry.get("f3", 0))]
    results_dict[key][solver] = {
        "f1": entry.get("f1", 0),
        "f2": entry.get("f2", 0),
        "f3": entry.get("f3", 0),
        "n_targets": n_targets,
        "n_selected": n_selected,
        "runtime_s": runtime_s,
        "frontier": frontier,
        "n_frontier": entry.get("n_frontier", len(frontier)),
    }

# Baselines: G-BL = b1, G-SM = b3 (skip b2 = old greedy_weighted)
for key, scenario in bl_data.items():
    if "b1" in scenario:
        b1 = scenario["b1"]
        add_single_point(results, key, "G-BL", b1["f1"], b1["f2"], b1["f3"],
                        b1.get("n_targets", 0), b1.get("n_selected", 0), b1.get("runtime_s", 0))
    if "b3" in scenario:
        b3 = scenario["b3"]
        add_single_point(results, key, "G-SM", b3["f1"], b3["f2"], b3["f3"],
                        b3.get("n_targets", 0), b3.get("n_selected", 0), b3.get("runtime_s", 0))

# GA-P-BL
for key, entry in b2_data.items():
    add_single_point(results, key, "GA-P-BL", entry["f1"], entry["f2"], entry["f3"],
                    entry.get("n_targets", 0), entry.get("n_selected", 0), entry.get("runtime_s", 0))

# MOEA-2
for key, entry in m2_data.items():
    add_moea_frontier(results, key, "MOEA-2", entry)

# MOEA-3
for key, entry in m3_data.items():
    add_moea_frontier(results, key, "MOEA-3", entry)

# Add group label
for key in results:
    results[key]["group"] = scenario_group(key)

print(f"\nMerged: {len(results)} scenarios with data")
for solver in SOLVERS:
    count = sum(1 for v in results.values() if solver in v)
    print(f"  {solver}: {count} scenarios")

# Filter to scenarios where ALL 5 solvers have data
common = [k for k, v in results.items() if all(s in v for s in SOLVERS)]
print(f"\nCommon scenarios (all 5 solvers): {len(common)}")

# ── 3. Hypervolume computation ──
def compute_hv(frontier, ref_point):
    """
    Compute 3D hypervolume for a set of points.
    Simple grid-free approach: sort by f1 descending, integrate.
    All objectives are maximized after normalization.
    ref_point is the nadir (worst possible).
    """
    if not frontier:
        return 0.0
    # Convert to numpy, keep only points that dominate ref_point
    pts = np.array([p for p in frontier if all(p[i] >= ref_point[i] for i in range(3))])
    if len(pts) == 0:
        return 0.0
    # Sort by f1 descending
    pts = pts[pts[:, 0].argsort()[::-1]]
    hv = 0.0
    prev_f1 = 1.0  # max normalized f1
    # For each f3 slice, compute 2D area in (f1, f2) plane
    unique_f3 = sorted(set(pts[:, 2]), reverse=True)
    for i, f3_val in enumerate(unique_f3):
        mask = pts[:, 2] >= f3_val
        if not np.any(mask):
            continue
        subset = pts[mask]
        # 2D HV for this f3 slice: sort by f1 desc, integrate running-max f2
        # (a point dominated in (f1,f2) by a higher-f1 point adds no area)
        sorted_idx = subset[:, 0].argsort()[::-1]
        f1_prev = 1.0
        f2_prev = ref_point[1]
        area = 0.0
        for idx in sorted_idx:
            f1_cur = subset[idx, 0]
            f2_cur = subset[idx, 1]
            f2_eff = max(f2_cur, f2_prev)
            area += (f1_prev - f1_cur) * (f2_eff - ref_point[1])
            f1_prev = f1_cur
            f2_prev = f2_eff
        f3_next = unique_f3[i+1] if i+1 < len(unique_f3) else ref_point[2]
        hv += area * (f3_val - f3_next)
    return hv

def normalize_objectives(all_results, common_keys):
    """Normalize f1, f2, f3 to [0,1] where 1 = best.
    f1: maximize → direct normalize
    f2: maximize → direct normalize (Higher f2 = better geometric resolution)
    f3: maximize → direct normalize (Higher f3 = better NESZ)
    """
    # Find global min/max for each objective
    all_f1, all_f2, all_f3 = [], [], []
    for key in common_keys:
        for solver in SOLVERS:
            if solver in all_results[key]:
                r = all_results[key][solver]
                all_f1.append(r["f1"])
                all_f2.append(r["f2"])
                all_f3.append(r["f3"])
                # Also add frontier points for min/max range
                for fp in r.get("frontier", []):
                    all_f1.append(fp[0])
                    all_f2.append(fp[1])
                    all_f3.append(fp[2])

    f1_min, f1_max = min(all_f1), max(all_f1)
    f2_min, f2_max = min(all_f2), max(all_f2)
    f3_min, f3_max = min(all_f3), max(all_f3)

    def norm_f1(x):
        return (x - f1_min) / (f1_max - f1_min) if f1_max > f1_min else 0.5
    def norm_f2(x):
        return (x - f2_min) / (f2_max - f2_min) if f2_max > f2_min else 0.5
    def norm_f3(x):
        return (x - f3_min) / (f3_max - f3_min) if f3_max > f3_min else 0.5

    normalized = {}
    for key in common_keys:
        normalized[key] = {"group": all_results[key]["group"]}
        for solver in SOLVERS:
            if solver in all_results[key]:
                r = all_results[key][solver]
                norm_frontier = [(norm_f1(p[0]), norm_f2(p[1]), norm_f3(p[2])) for p in r["frontier"]]
                normalized[key][solver] = {
                    "f1_raw": r["f1"], "f2_raw": r["f2"], "f3_raw": r["f3"],
                    "f1_norm": norm_f1(r["f1"]),
                    "f2_norm": norm_f2(r["f2"]),
                    "f3_norm": norm_f3(r["f3"]),
                    "frontier_norm": norm_frontier,
                    "n_targets": r["n_targets"],
                    "runtime_s": r["runtime_s"],
                    "n_frontier": r.get("n_frontier", 1),
                }
    return normalized, (f1_min, f1_max, f2_min, f2_max, f3_min, f3_max)

print("\nNormalizing objectives...")
norm_results, obj_ranges = normalize_objectives(results, common)
ref_point = (0.0, 0.0, 0.0)  # worst possible in normalized space

# Compute HV per solver per scenario
hv_data = {solver: [] for solver in SOLVERS}
hv_by_scenario = {}

for key in common:
    hv_by_scenario[key] = {}
    for solver in SOLVERS:
        if solver in norm_results[key]:
            frontier = norm_results[key][solver]["frontier_norm"]
            hv = compute_hv(frontier, ref_point)
            hv_by_scenario[key][solver] = hv
            hv_data[solver].append(hv)
        else:
            hv_data[solver].append(0.0)

print(f"HV means: ", end="")
for solver in SOLVERS:
    vals = hv_data[solver]
    print(f"{solver}={np.mean(vals):.4f} ", end="")
print()

# ── 4. Statistical tests ──
print("\n── Statistical Analysis ──")

# Friedman test
hv_matrix = np.array([hv_data[s] for s in SOLVERS]).T  # scenarios × solvers
friedman_stat, friedman_p = scipy_stats.friedmanchisquare(*[hv_data[s] for s in SOLVERS])
print(f"Friedman test: χ²={friedman_stat:.2f}, p={friedman_p:.6f}")

# Pairwise Wilcoxon signed-rank with Bonferroni correction
n_comparisons = len(SOLVERS) * (len(SOLVERS) - 1) // 2
alpha_bonf = 0.05 / n_comparisons
print(f"\nPairwise Wilcoxon (Bonferroni α={alpha_bonf:.5f}):")
wilcoxon_results = {}
for s1, s2 in combinations(SOLVERS, 2):
    d = [hv_by_scenario[k].get(s1, 0) - hv_by_scenario[k].get(s2, 0) for k in common]
    # zero out floating-point noise (G-BL vs GA-P-BL differ by ~1e-17) so it
    # is not treated as a real signed difference
    d = [x if abs(x) > 1e-9 else 0.0 for x in d]
    stat, p = scipy_stats.wilcoxon(d, zero_method="wilcox")
    # Cliff's delta
    n = len(d)
    greater = sum(1 for x in d if x > 0)
    less = sum(1 for x in d if x < 0)
    equal = n - greater - less
    cliff_delta = (greater - less) / (greater + less + equal)  # simplified
    # More precise Cliff's delta
    cliff_delta_eff = (greater - less) / n  # simplified; proper is more complex
    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    bonf_sig = "†" if p < alpha_bonf else ""
    print(f"  {s1} vs {s2}: W={stat:.0f}, p={p:.6f}{sig}, "
          f"Cliff's δ={cliff_delta_eff:.3f}{bonf_sig}")
    wilcoxon_results[f"{s1}_vs_{s2}"] = {
        "statistic": float(stat), "p_value": float(p),
        "significant": bool(p < alpha_bonf),
        "cliffs_delta": float(cliff_delta_eff),
        "greater": greater, "less": less, "equal": equal,
    }

# ── 5. Per-group statistics ──
print("\n── Per-Group HV Summary ──")
groups = sorted(set(results[k]["group"] for k in common))
group_stats = {}
for group in groups:
    group_keys = [k for k in common if results[k]["group"] == group]
    group_stats[group] = {}
    print(f"\n{group} ({len(group_keys)} scenarios):")
    for solver in SOLVERS:
        vals = [hv_by_scenario[k].get(solver, 0) for k in group_keys]
        mean_val = np.mean(vals)
        std_val = np.std(vals, ddof=1)
        # Also compute raw f1 mean
        f1_vals = [results[k][solver]["f1"] for k in group_keys if solver in results[k]]
        f1_mean = np.mean(f1_vals) if f1_vals else 0
        f1_std = np.std(f1_vals, ddof=1) if f1_vals else 0
        group_stats[group][solver] = {
            "hv_mean": float(mean_val), "hv_std": float(std_val),
            "f1_mean": float(f1_mean), "f1_std": float(f1_std),
            "n_scenarios": len(group_keys),
        }
        print(f"  {solver}: HV={mean_val:.4f}±{std_val:.4f}, f1={f1_mean:.1f}±{f1_std:.1f}")

# ── 6. Export ──
output = {
    "metadata": {
        "n_scenarios": len(common),
        "solvers": SOLVERS,
        "objective_ranges": {
            "f1": list(obj_ranges[:2]),
            "f2": list(obj_ranges[2:4]),
            "f3": list(obj_ranges[4:]),
        },
        "reference_point": list(ref_point),
    },
    "friedman": {
        "statistic": float(friedman_stat),
        "p_value": float(friedman_p),
    },
    "pairwise_wilcoxon": wilcoxon_results,
    "per_scenario_hv": {k: hv_by_scenario[k] for k in common},
    "per_group": group_stats,
    "hv_by_solver": {s: {"mean": float(np.mean(hv_data[s])), "std": float(np.std(hv_data[s], ddof=1))} for s in SOLVERS},
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\n✓ Full results: {OUT_JSON}")

# CSV summary
csv_lines = ["solver,group,n_scenarios,hv_mean,hv_std,f1_mean,f1_std"]
for group in sorted(group_stats.keys()):
    for solver in SOLVERS:
        if solver in group_stats[group]:
            gs = group_stats[group][solver]
            csv_lines.append(f"{solver},{group},{gs['n_scenarios']},{gs['hv_mean']:.6f},{gs['hv_std']:.6f},{gs['f1_mean']:.2f},{gs['f1_std']:.2f}")

with open(OUT_CSV, "w", encoding="utf-8") as f:
    f.write("\n".join(csv_lines))
print(f"✓ CSV summary: {OUT_CSV}")

print("\n── Done ──")
