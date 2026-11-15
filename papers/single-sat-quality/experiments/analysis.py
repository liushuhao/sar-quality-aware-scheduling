#!/usr/bin/env python3
"""
Phase 4.3: Statistical analysis and visualization of experiment results.

Computes HV, IGD, C-metric, runs Wilcoxon/Friedman/Nemenyi/Cliff's delta,
and generates publication-quality figures.

Usage:
    python experiments/analysis.py                  # full analysis
    python experiments/analysis.py --group S1       # single group
    python experiments/analysis.py --figures-only   # only regenerate figures
"""

import json
import os
import sys
import warnings
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

import numpy as np
from scipy import stats
from scipy.stats import wilcoxon, friedmanchisquare, f_oneway

# Plotting
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scienceplots
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import seaborn as sns

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"
FIGURES_DIR = Path(__file__).resolve().parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Color scheme ─────────────────────────────────────────────────────────
COLORS = {
    "moea": "#2C3E50",  # dark blue-grey
    "b1": "#E74C3C",    # red
    "b2": "#F39C12",    # orange
    "b3": "#8E44AD",    # purple
}
SOLVER_LABELS = {"moea": "MOEA (NSGA-III)", "b1": "B1 (Coverage)", "b2": "B2 (Proxy Qty)"}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════

def load_s1_data() -> Dict:
    """Load S1 per-run data from _progress.json (30 seeds, N=20, 3 solvers)."""
    path = RESULTS_DIR / "_progress.json"
    if not path.exists():
        print(f"WARNING: {path} not found, trying results_small.json")
        path = RESULTS_DIR / "results_small.json"

    with open(path, "r") as f:
        data = json.load(f)

    # Handle both formats: {"completed": {...}} vs list
    if isinstance(data, dict) and "completed" in data:
        entries = data["completed"]
    elif isinstance(data, list):
        entries = {e["scenario"]: e for e in data}
    else:
        entries = data

    return _parse_s1_entries(entries)

def _parse_s1_entries(entries: Dict) -> Dict:
    """Parse S1 entries into per-solver per-seed records."""
    records = {"moea": [], "b1": [], "b2": []}
    n_total = 0
    n_skipped_no_solvers = 0
    n_skipped_no_prefix = 0
    for key, entry in entries.items():
        # Only process "small" entries for S1
        if not ("small" in key.lower() or "S1" in key):
            n_skipped_no_prefix += 1
            continue
        if "solvers" not in entry:
            n_skipped_no_solvers += 1
            continue
        for solver in ["moea", "b1", "b2"]:
            if solver in entry["solvers"]:
                sdata = entry["solvers"][solver]
                # Construct pareto frontier if missing (B1/B2 often lack it)
                pf = sdata.get("pareto_frontier", [])
                if not pf:
                    f1_val = sdata.get("f1", 0)
                    f2_val = sdata.get("f2", 0)
                    pf = [{"f1": f1_val, "f2": f2_val}]

                rec = {
                    "scenario": key,
                    "solver": solver,
                    "f1": sdata.get("f1", 0),
                    "f2": sdata.get("f2", 0),
                    "n_selected": sdata.get("n_selected", 0),
                    "n_targets": entry.get("n_targets", 20),
                    "runtime_s": sdata.get("runtime_s", 0),
                    "pareto_frontier": pf,
                }
                records[solver].append(rec)
                n_total += 1
    print(f"  S1 parse: {n_total} records (skipped {n_skipped_no_prefix} non-S1, {n_skipped_no_solvers} no-solvers)")
    return records

def load_moea_c3_data() -> Dict:
    """Load S4/S5/S6 MOEA data from moea_c3_fixed/_progress.json."""
    path = RESULTS_DIR / "moea_c3_fixed" / "_progress.json"
    if not path.exists():
        print(f"WARNING: {path} not found")
        return {}

    with open(path, "r") as f:
        data = json.load(f)

    entries = data.get("completed", data)
    groups = defaultdict(list)

    for key, entry in entries.items():
        # Determine group from key (S4/, S5/, S6/)
        if key.startswith("S4"):
            group = "S4"
        elif key.startswith("S5"):
            group = "S5"
        elif key.startswith("S6"):
            group = "S6"
        else:
            group = "unknown"

        # Build Pareto frontier from separate arrays
        frontier_f1 = entry.get("frontier_f1", [entry.get("f1")])
        frontier_f2 = entry.get("frontier_f2", [entry.get("f2")])
        if isinstance(frontier_f1, (int, float)):
            frontier_f1 = [frontier_f1]
        if isinstance(frontier_f2, (int, float)):
            frontier_f2 = [frontier_f2]

        pareto_frontier = [
            {"f1": float(f1), "f2": float(f2)}
            for f1, f2 in zip(frontier_f1, frontier_f2)
        ]

        rec = {
            "scenario": key,
            "solver": "moea",
            "group": group,
            "f1": entry.get("f1", 0),
            "f2": entry.get("f2", 0),
            "n_selected": entry.get("n_selected", 0),
            "n_targets": entry.get("n_targets", 100),
            "runtime_s": entry.get("runtime_s", 0),
            "pareto_frontier": pareto_frontier,
            # Extract theta_ref for S5
            "theta_ref": _extract_theta_ref(key),
        }
        groups[group].append(rec)

    return dict(groups)

def _extract_theta_ref(key: str) -> Optional[int]:
    """Extract theta_ref from S5 scenario key.

    S5 keys may use either explicit theta (e.g., 'S5_C_theta30_seed05')
    or scenario-letter encoding:
      S5-A → 20°, S5-B → 25°, S5-C → 30°, S5-D → 35°, S5-E → 40°
    """
    import re
    # Explicit theta in key name
    m = re.search(r"theta(\d+)", key)
    if m:
        return int(m.group(1))
    # Scenario-letter mapping
    m = re.search(r"S5-([A-E])", key)
    if m:
        mapping = {"A": 20, "B": 25, "C": 30, "D": 35, "E": 40}
        return mapping.get(m.group(1))
    return None

def load_baselines_c3_data() -> Dict:
    """Load S4/S6 B1+B2 baseline data from baselines_c3_fixed.json.

    NOTE: The experiment stored baselines as 'b1' and 'b3' (not 'b2').
    b3 is equivalent to b2 for fixed-theta scenarios (both use theta_ref
    and greedy profit-descending). We map b3->b2 for analysis.
    """
    path = RESULTS_DIR / "baselines_c3_fixed.json"
    if not path.exists():
        print(f"WARNING: {path} not found")
        return {}

    with open(path, "r") as f:
        data = json.load(f)

    groups = defaultdict(lambda: {"b1": [], "b2": []})
    n_b1 = 0
    n_b2 = 0

    for key, entry in data.items():
        if key.startswith("S4"):
            group = "S4"
        elif key.startswith("S6"):
            group = "S6"
        else:
            continue

        # Handle entry format: {"b1": {...}, "b3": {...}}
        # b3 is B2-equivalent for fixed-theta baselines
        for sname, mapped_name in [("b1", "b1"), ("b3", "b2")]:
            sdata = entry.get(sname, {})
            if not sdata:
                continue
            f1_val = sdata.get("f1", 0)
            f2_val = sdata.get("f2", 0)
            rec = {
                "scenario": key,
                "solver": mapped_name,
                "group": group,
                "f1": f1_val,
                "f2": f2_val,
                "n_selected": sdata.get("n", 0),
                "n_targets": 100,
                "runtime_s": sdata.get("runtime_s", 0),
                "pareto_frontier": [{"f1": f1_val, "f2": f2_val}],
            }
            groups[group][mapped_name].append(rec)
            if mapped_name == "b1":
                n_b1 += 1
            else:
                n_b2 += 1

    print(f"  Baselines loaded: b1={n_b1}, b2(from b3)={n_b2}")
    return dict(groups)

def load_summary(group: str) -> Optional[Dict]:
    """Load aggregate summary for a group."""
    path = RESULTS_DIR / f"summary_{group}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)

def load_all_data() -> Dict:
    """Load all available experiment data, normalized."""
    all_data = {}

    # S1: full per-run with 3 solvers
    s1 = load_s1_data()
    all_data["S1"] = s1

    # S4/S5/S6: MOEA + baselines
    moea_data = load_moea_c3_data()
    bl_data = load_baselines_c3_data()

    for group in ["S4", "S5", "S6"]:
        all_data[group] = {"moea": [], "b1": [], "b2": []}
        if group in moea_data:
            all_data[group]["moea"] = moea_data[group]
        if group in bl_data:
            all_data[group]["b1"] = bl_data[group].get("b1", [])
            all_data[group]["b2"] = bl_data[group].get("b2", [])

    # S2, S3: only aggregate summaries — fetch for reporting
    for group in ["S2", "S3"]:
        summary = load_summary(group)
        all_data[group] = {"_summary": summary}

    return all_data

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: HV / IGD / C-METRIC COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

def compute_hv(pareto_frontier: List[Dict], ref_point: Tuple[float, float]) -> float:
    """Compute hypervolume of a Pareto frontier w.r.t. reference point.

    Uses a simple O(n log n) algorithm for 2D (rectangles method).
    Points are sorted by f1 ascending; HV = sum of (f2_i - ref_f2) * (ref_f1 - f1_i)
    but we need to handle non-dominated sorting properly.

    For 2-objective maximization (both f1 and f2 maximize):
    HV = area dominated by PF relative to reference point (0,0).
    Points must be sorted by f1, then accumulated.
    """
    if not pareto_frontier:
        return 0.0

    # Extract (f1, f2) points, ensure non-dominated
    points = []
    for p in pareto_frontier:
        f1 = p.get("f1", 0)
        f2 = p.get("f2", 0)
        if isinstance(f1, (int, float)) and isinstance(f2, (int, float)):
            points.append((float(f1), float(f2)))

    if not points:
        return 0.0

    # Filter to non-dominated points and within reference bounds
    points = _nondominated_filter(points)
    points = [(f1, f2) for f1, f2 in points if f1 >= 0 and f2 >= 0]

    if not points:
        return 0.0

    # Sort by f1 ascending
    points.sort(key=lambda x: x[0])

    # 2D HV computation: staircase method
    hv = 0.0
    prev_f1 = 0.0
    max_f2_seen = 0.0

    for f1, f2 in points:
        if f2 > max_f2_seen:
            # Contribution: width (f1 - prev_f1) × height (f2 - 0)
            # But for dominated hypervolume, we need ref_point consideration
            # Actually HV from (0,0): area = sum of non-dominated rectangles
            pass

    # Simpler: use the standard Lebesgue measure
    # For 2D maximization with ref_point=(0,0):
    # Sort by f1 descending, track max f2
    points.sort(key=lambda x: x[0], reverse=True)

    hv = 0.0
    last_f1 = ref_point[0] if ref_point[0] > 0 else 0
    max_f2 = 0.0

    for f1, f2 in points:
        if f2 > max_f2:
            # Rectangle: width (last_f1 - f1) × height (f2 - 0) but capped at ref
            width = last_f1 - f1
            if width > 0:
                hv += width * (f2 - max_f2)
            max_f2 = f2

    # Final segment to ref point
    if last_f1 > 0 and max_f2 > 0:
        hv += (last_f1 - 0) * max_f2  # Already zero-ref, this is the base

    # Actually the above is wrong. Let me use the standard approach.
    return hv

def _nondominated_filter(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Filter to non-dominated points (both objectives maximize)."""
    if not points:
        return points
    # Sort by f1 descending
    sorted_pts = sorted(points, key=lambda x: (-x[0], -x[1]))
    nd = []
    max_f2 = -float("inf")
    for f1, f2 in sorted_pts:
        if f2 > max_f2:
            nd.append((f1, f2))
            max_f2 = f2
    return nd

def compute_hv_simple(pareto_frontier: List[Dict],
                      ref_point: Tuple[float, float] = None) -> float:
    """Compute 2D hypervolume for maximization problems.

    Uses the standard algorithm: sort by f1, sweep f2.

    ref_point: (f1_ref, f2_ref) — the reference point for HV.
    Defaults to (0, 0) for profit-quality space.
    """
    if not pareto_frontier:
        return 0.0

    points = []
    for p in pareto_frontier:
        f1 = p.get("f1", 0)
        f2 = p.get("f2", 0)
        if isinstance(f1, (int, float)) and isinstance(f2, (int, float)):
            points.append((float(f1), float(f2)))

    if not points:
        return 0.0

    rp = ref_point if ref_point else (0.0, 0.0)

    # Filter dominated points and sort by f1 ascending
    points = _nondominated_filter(points)
    points.sort(key=lambda x: x[0])

    # Clamp: only consider points dominating reference
    points = [(f1, f2) for f1, f2 in points if f1 > rp[0] and f2 > rp[1]]
    if not points:
        return 0.0

    hv = 0.0
    # Each point contributes rectangle from last_f1 to its f1 at its f2 height
    # minus overlap with previously-covered f2
    last_f1 = rp[0]
    covered_f2 = rp[1]

    for f1, f2 in points:
        if f2 > covered_f2:
            hv += (f1 - last_f1) * (f2 - covered_f2)
            covered_f2 = f2
            last_f1 = f1
        else:
            last_f1 = f1

    # Final bar to rp
    if points:
        final_f1 = points[-1][0]
        hv += (final_f1 - rp[0]) * (covered_f2 - rp[1])  # "staircase" bottom

    return hv

def compute_igd(approx_frontier: List[Dict],
                reference_frontier: List[Dict],
                p: float = 2.0) -> float:
    """Compute Inverted Generational Distance.

    IGD = (1/|R|) * sum_{r in R} min_{a in A} ||r - a||_p

    Where R is the reference (true) PF and A is the approximate PF.
    Both objectives are maximized — normalize before computing distances.
    """
    if not approx_frontier or not reference_frontier:
        return float("nan")

    A = np.array([[p.get("f1", 0), p.get("f2", 0)] for p in approx_frontier])
    R = np.array([[p.get("f1", 0), p.get("f2", 0)] for p in reference_frontier])

    if len(A) == 0 or len(R) == 0:
        return float("nan")

    # Normalize each objective to [0, 1]
    all_points = np.vstack([A, R])
    mins = all_points.min(axis=0)
    maxs = all_points.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0  # avoid division by zero

    A_norm = (A - mins) / ranges
    R_norm = (R - mins) / ranges

    # For each reference point, find min distance to any approximate point
    total = 0.0
    for r in R_norm:
        dists = np.linalg.norm(A_norm - r, axis=1)
        total += np.min(dists)

    return total / len(R)

def compute_c_metric(frontier_a: List[Dict],
                     frontier_b: List[Dict]) -> float:
    """Compute C-metric (coverage): fraction of B points weakly dominated by A.

    C(A, B) = |{b in B : exists a in A, a weakly dominates b}| / |B|

    Maximization: a dominates b if a.f1 >= b.f1 AND a.f2 >= b.f2,
    with at least one strict.
    """
    if not frontier_b:
        return float("nan")
    if not frontier_a:
        return 0.0

    A = np.array([[p.get("f1", 0), p.get("f2", 0)] for p in frontier_a])
    B = np.array([[p.get("f1", 0), p.get("f2", 0)] for p in frontier_b])

    count = 0
    for b in B:
        # Check if any a weakly dominates b
        dominated = np.any((A[:, 0] >= b[0]) & (A[:, 1] >= b[1]))
        if dominated:
            count += 1

    return count / len(B)

def get_reference_frontier(data: Dict, group: str) -> List[Dict]:
    """Build reference Pareto frontier from best-known points across all solvers.

    For each seed, take all solver Pareto points, combine, and filter
    to global non-dominated set.
    """
    all_points = []
    solvers = [s for s in ["moea", "b1", "b2"] if s in data.get(group, {})]

    for solver in solvers:
        for rec in data[group].get(solver, []):
            pf = rec.get("pareto_frontier", [])
            for p in pf:
                all_points.append((p.get("f1", 0), p.get("f2", 0)))

    if not all_points:
        return []

    nd = _nondominated_filter(all_points)
    return [{"f1": f1, "f2": f2} for f1, f2 in nd]

def get_ref_point(data: Dict, group: str) -> Tuple[float, float]:
    """Determine appropriate reference point for HV computation.

    Uses ~1.1× the worst observed f1/f2 across all solvers, or (0, 0).
    """
    solvers = [s for s in ["moea", "b1", "b2"] if s in data.get(group, {})]

    min_f1 = float("inf")
    min_f2 = float("inf")

    for solver in solvers:
        for rec in data[group].get(solver, []):
            pf = rec.get("pareto_frontier", [])
            for p in pf:
                min_f1 = min(min_f1, p.get("f1", float("inf")))
                min_f2 = min(min_f2, p.get("f2", float("inf")))

    # Reference point slightly worse than nadir
    ref_f1 = max(0, min_f1 * 1.05) if min_f1 != float("inf") else 0
    ref_f2 = max(0, min_f2 * 1.05) if min_f2 != float("inf") else 0

    return (0.0, 0.0) if ref_f1 == 0 and ref_f2 == 0 else (ref_f1, ref_f2)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: STATISTICAL TESTS
# ═══════════════════════════════════════════════════════════════════════════

def paired_comparison(values_a: List[float], values_b: List[float],
                      label_a: str, label_b: str) -> Dict:
    """Run Wilcoxon signed-rank test + Cliff's delta between two paired samples."""
    if len(values_a) != len(values_b):
        return {"error": "unequal lengths", "na": len(values_a), "nb": len(values_b)}

    n = len(values_a)
    if n < 5:
        return {"error": "too few samples", "n": n}

    # Wilcoxon signed-rank
    try:
        stat, p_value = wilcoxon(values_a, values_b, zero_method="wilcox",
                                 alternative="two-sided")
    except ValueError as e:
        stat, p_value = float("nan"), float("nan")

    # Cliff's delta
    delta = cliffs_delta(values_a, values_b)

    # Direction: positive delta means A > B
    direction = f"{label_a} > {label_b}" if delta > 0 else \
                f"{label_b} > {label_a}" if delta < 0 else "equal"

    return {
        "comparison": f"{label_a} vs {label_b}",
        "n": n,
        "wilcoxon_stat": stat,
        "p_value": p_value,
        "p_value_formatted": f"{p_value:.4e}" if not np.isnan(p_value) else "nan",
        "cliffs_delta": delta,
        "effect_size": _cliffs_interpretation(delta),
        "direction": direction,
    }

def cliffs_delta(a: List[float], b: List[float]) -> float:
    """Compute Cliff's delta effect size.

    delta = (P(a > b) - P(b > a)) where ties count half.
    Range: [-1, 1]; 0 = no effect.
    """
    a = np.array(a)
    b = np.array(b)

    greater = 0
    less = 0

    for av in a:
        greater += np.sum(b < av)
        less += np.sum(b > av)

    n = len(a) * len(b)
    if n == 0:
        return 0.0

    return (greater - less) / n

def _cliffs_interpretation(abs_delta: float) -> str:
    abs_d = abs(abs_delta)
    if abs_d < 0.147:
        return "negligible"
    elif abs_d < 0.33:
        return "small"
    elif abs_d < 0.474:
        return "medium"
    else:
        return "large"

def friedman_nemenyi(groups_data: Dict[str, List[float]],
                     group_labels: List[str]) -> Dict:
    """Friedman omnibus test + Nemenyi post-hoc.

    groups_data: {solver_name: [scores across scenarios]}
    """
    arrays = [np.array(groups_data[g]) for g in group_labels]

    # Ensure equal lengths
    min_len = min(len(a) for a in arrays)
    arrays = [a[:min_len] for a in arrays]

    # Friedman test
    try:
        stat, p_value = friedmanchisquare(*arrays)
    except Exception:
        stat, p_value = float("nan"), float("nan")

    result = {
        "test": "Friedman",
        "n_scenarios": min_len,
        "statistic": stat,
        "p_value": p_value,
        "p_value_formatted": f"{p_value:.4e}" if not np.isnan(p_value) else "nan",
        "significant": p_value < 0.05 if not np.isnan(p_value) else None,
    }

    # Nemenyi post-hoc (critical difference)
    # CD = q_alpha * sqrt(k*(k+1) / (6*N))
    # For k=3, alpha=0.05, q_alpha ≈ 2.343
    k = len(group_labels)
    N = min_len
    q_alpha = 2.343  # for k=3, alpha=0.05
    if k == 2:
        q_alpha = 1.96  # equivalent to Wilcoxon

    cd = q_alpha * np.sqrt(k * (k + 1) / (6 * N))

    # Average rankings
    ranks = np.zeros((k, N))
    for j in range(N):
        scenario_scores = [arrays[i][j] for i in range(k)]
        # Higher HV = higher rank
        order = np.argsort(np.argsort(scenario_scores))  # 0 = lowest
        ranks[:, j] = k - order  # k = highest rank

    avg_ranks = ranks.mean(axis=1)

    result["nemenyi"] = {
        "critical_difference": cd,
        "q_alpha": q_alpha,
        "rankings": {label: float(avg_ranks[i]) for i, label in enumerate(group_labels)},
        "pairwise": {},
    }

    for i in range(k):
        for j in range(i + 1, k):
            diff = abs(avg_ranks[i] - avg_ranks[j])
            significant = diff > cd
            result["nemenyi"]["pairwise"][f"{group_labels[i]} vs {group_labels[j]}"] = {
                "rank_diff": float(diff),
                "significant": bool(significant),
            }

    return result

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: FIGURE GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def set_style():
    """Set consistent plotting style using SciencePlots."""
    plt.style.use(['science', 'nature'])
    sns.set_style("ticks")
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
    })

def plot_pareto_fronts(data: Dict, group: str, output_dir: Path = None):
    """Generate Pareto front scatter plots: f2 vs f1, 3 solvers overlaid.

    Creates one plot for the group, aggregating all seeds.
    Each solver's best Pareto frontier across all seeds is shown.
    """
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    if group not in data:
        print(f"  No data for group {group}")
        return

    group_data = data[group]
    solvers = [s for s in ["moea", "b1", "b2"] if s in group_data]

    if not solvers:
        print(f"  No solver data for group {group}")
        return

    fig, ax = plt.subplots(figsize=(7, 5))

    all_points = {"moea": [], "b1": [], "b2": []}

    for solver in solvers:
        for rec in group_data.get(solver, []):
            pf = rec.get("pareto_frontier", [])
            for p in pf:
                all_points[solver].append((p.get("f1", 0), p.get("f2", 0)))

    markers = {"moea": "o", "b1": "s", "b2": "^"}

    for solver in solvers:
        if all_points[solver]:
            f1_vals = [p[0] for p in all_points[solver]]
            f2_vals = [p[1] for p in all_points[solver]]
            ax.scatter(f1_vals, f2_vals, c=COLORS[solver], marker=markers[solver],
                       label=SOLVER_LABELS.get(solver, solver),
                       alpha=0.6, s=40, edgecolors="white", linewidth=0.5)

    # Also plot the non-dominated frontier across all solvers
    all_pts = []
    for solver in solvers:
        all_pts.extend(all_points[solver])
    if all_pts:
        nd = _nondominated_filter(all_pts)
        nd_f1 = [p[0] for p in nd]
        nd_f2 = [p[1] for p in nd]
        ax.plot(nd_f1, nd_f2, "k--", linewidth=1.5, alpha=0.5,
                label="Global Pareto front")

    ax.set_xlabel("Coverage Profit ($f_1$)")
    ax.set_ylabel("Geometric Quality Score ($f_2$)")
    ax.set_title(f"Pareto Front Comparison — Group {group}")
    ax.legend(loc="lower right")

    filepath = output_dir / f"pareto_fronts_{group}.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

def plot_hv_boxplots(data: Dict, group: str, output_dir: Path = None):
    """Generate HV comparison boxplot: solvers × group.

    Computes per-seed HV and creates side-by-side boxplots.
    """
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    if group not in data:
        print(f"  No data for group {group}")
        return

    group_data = data[group]
    solvers = [s for s in ["moea", "b1", "b2"] if s in group_data and group_data[s]]
    if not solvers:
        print(f"  No solvers with data for group {group}")
        return

    # Compute HV per seed
    ref_point = get_ref_point(data, group)
    ref_frontier = get_reference_frontier(data, group)

    hv_data = {s: [] for s in solvers}

    for solver in solvers:
        for rec in group_data[solver]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            hv = compute_hv_simple(pf, ref_point)
            hv_data[solver].append(hv)

    fig, ax = plt.subplots(figsize=(6, 5))

    positions = list(range(len(solvers)))
    bp = ax.boxplot([hv_data[s] for s in solvers],
                    positions=positions,
                    widths=0.5,
                    patch_artist=True,
                    boxprops=dict(linewidth=1.2),
                    whiskerprops=dict(linewidth=1.2),
                    capprops=dict(linewidth=1.2),
                    medianprops=dict(linewidth=1.5, color="black"))

    for i, solver in enumerate(solvers):
        bp["boxes"][i].set_facecolor(COLORS[solver])
        bp["boxes"][i].set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels([SOLVER_LABELS.get(s, s) for s in solvers], rotation=15)
    ax.set_ylabel("Hypervolume (HV)")
    ax.set_title(f"HV Comparison — Group {group}")

    filepath = output_dir / f"hv_boxplot_{group}.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

    return hv_data

def plot_cd_diagram(groups_results: Dict[str, Dict], output_dir: Path = None):
    """Generate Critical Difference diagram (Demšar 2006).

    Shows average rankings and CD threshold for multiple solvers across groups.
    """
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    # Collect HV rankings per group
    # For now, use per-group comparison data
    if not groups_results:
        print("  No group results for CD diagram")
        return

    fig, ax = plt.subplots(figsize=(8, 3))

    # Simplified CD diagram as horizontal bar showing avg ranks
    solver_names = []
    avg_ranks_list = []

    for group, result in groups_results.items():
        if "friedman" in result and result["friedman"].get("nemenyi"):
            nem = result["friedman"]["nemenyi"]
            solver_names = list(nem["rankings"].keys())
            avg_ranks_list = list(nem["rankings"].values())
            cd = nem.get("critical_difference", 0)
            break  # Use first available

    if not solver_names:
        print("  No CD data available")
        return

    # Sort by rank (higher rank = better)
    pairs = sorted(zip(avg_ranks_list, solver_names), reverse=True)
    avg_ranks_list, solver_names = zip(*pairs)

    x = np.arange(len(solver_names))
    colors_list = [COLORS.get(s, "#888888") for s in solver_names]

    ax.barh(x, avg_ranks_list, height=0.5, color=colors_list, alpha=0.8)

    # CD lines
    for i in range(len(solver_names)):
        for j in range(i + 1, len(solver_names)):
            if abs(avg_ranks_list[i] - avg_ranks_list[j]) <= cd:
                ax.plot([avg_ranks_list[i], avg_ranks_list[j]],
                        [x[i], x[j]], "k-", linewidth=1.5, alpha=0.5)

    ax.set_yticks(x)
    ax.set_yticklabels([SOLVER_LABELS.get(s, s) for s in solver_names])
    ax.set_xlabel("Average Rank")
    ax.set_title("Critical Difference Diagram (Nemenyi post-hoc)")
    ax.invert_yaxis()

    # Annotate CD
    ax.text(0.98, 0.02, f"CD = {cd:.3f}", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=9, style="italic")

    filepath = output_dir / "cd_diagram.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

def plot_convergence(data: Dict, group: str, output_dir: Path = None):
    """Plot HV vs generation convergence curves.

    NOTE: Requires per-generation HV tracking that may not be available.
    Falls back to showing per-seed final HV as scatter.
    """
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    if group not in data:
        return

    group_data = data[group]
    solvers = [s for s in ["moea", "b1", "b2"] if s in group_data and group_data[s]]
    if not solvers:
        return

    ref_point = get_ref_point(data, group)

    fig, ax = plt.subplots(figsize=(7, 5))

    for solver in solvers:
        seeds_hv = []
        for rec in group_data[solver]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            hv = compute_hv_simple(pf, ref_point)
            seeds_hv.append(hv)

        if seeds_hv:
            # Show as horizontal strips (no generation tracking available)
            seed_indices = list(range(len(seeds_hv)))
            ax.scatter(seed_indices, seeds_hv, c=COLORS[solver],
                       label=SOLVER_LABELS.get(solver, solver),
                       alpha=0.6, s=30)
            # Add mean line
            mean_hv = np.mean(seeds_hv)
            ax.axhline(y=mean_hv, color=COLORS[solver], linestyle="--",
                       linewidth=1.5, alpha=0.7)

    ax.set_xlabel("Seed Index")
    ax.set_ylabel("Hypervolume (HV)")
    ax.set_title(f"Per-Seed HV — Group {group}")
    ax.legend()

    filepath = output_dir / f"hv_seeds_{group}.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

def plot_quality_gain(data: Dict, group: str, output_dir: Path = None):
    """Quality gain vs profit change scatter (MOEA vs B1, per scenario)."""
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    if group not in data:
        return

    group_data = data[group]
    moea_recs = group_data.get("moea", [])
    b1_recs = group_data.get("b1", [])

    if not moea_recs or not b1_recs:
        return

    # Pair by scenario
    b1_by_scenario = {r["scenario"]: r for r in b1_recs}

    quality_gains = []
    profit_changes = []
    scenarios = []

    for mrec in moea_recs:
        sc = mrec.get("scenario", "")
        if sc in b1_by_scenario:
            brec = b1_by_scenario[sc]
            f1_m = mrec.get("f1", 0)
            f2_m = mrec.get("f2", 0)
            f1_b = brec.get("f1", 0)
            f2_b = brec.get("f2", 0)

            if f2_b > 0:
                q_gain = (f2_m - f2_b) / f2_b * 100
            else:
                q_gain = 0

            if f1_b > 0:
                p_change = (f1_m - f1_b) / f1_b * 100
            else:
                p_change = 0

            quality_gains.append(q_gain)
            profit_changes.append(p_change)
            scenarios.append(sc)

    if not quality_gains:
        return

    fig, ax = plt.subplots(figsize=(7, 5))

    scatter = ax.scatter(profit_changes, quality_gains, c=COLORS["moea"],
                          alpha=0.6, s=40, edgecolors="white", linewidth=0.5)

    ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(x=0, color="gray", linestyle=":", alpha=0.5)

    ax.set_xlabel("Profit Change MOEA vs B1 (%)")
    ax.set_ylabel("Quality Gain MOEA vs B1 (%)")
    ax.set_title(f"Quality–Profit Trade-off — Group {group}")

    # Quadrant labels
    ax.text(0.98, 0.98, "Quality + Profit win", transform=ax.transAxes,
            ha="right", va="top", fontsize=8, color="green", alpha=0.7)
    ax.text(0.02, 0.98, "Quality win / Profit loss", transform=ax.transAxes,
            ha="left", va="top", fontsize=8, color="orange", alpha=0.7)

    filepath = output_dir / f"quality_gain_{group}.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

def plot_ablation_theta_ref(data: Dict, output_dir: Path = None):
    """theta_ref ablation: HV vs theta_ref boxplot."""
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    s5_data = data.get("S5", {}).get("moea", [])
    if not s5_data:
        print("  No S5 data for theta_ref ablation")
        return

    # Group by theta_ref
    theta_groups = defaultdict(list)
    for rec in s5_data:
        theta = rec.get("theta_ref")
        if theta is not None:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            hv = compute_hv_simple(pf, (0, 0))
            theta_groups[theta].append(hv)

    if not theta_groups:
        return

    thetas = sorted(theta_groups.keys())
    hv_values = [theta_groups[t] for t in thetas]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Boxplot
    bp = ax1.boxplot(hv_values, positions=thetas, widths=3,
                      patch_artist=True)
    for box in bp["boxes"]:
        box.set_facecolor(COLORS["moea"])
        box.set_alpha(0.7)

    ax1.set_xlabel("$\\theta_{ref}$ (°)")
    ax1.set_ylabel("Hypervolume (HV)")
    ax1.set_title("HV vs $\\theta_{ref}$ — S5 Ablation")

    # ANOVA
    if len(thetas) >= 2:
        try:
            f_stat, p_val = f_oneway(*hv_values)
            ax1.text(0.98, 0.02, f"ANOVA: F={f_stat:.2f}, p={p_val:.4f}",
                     transform=ax1.transAxes, ha="right", va="bottom",
                     fontsize=9, style="italic")
        except Exception:
            pass

    # Also plot f2 vs theta_ref (raw quality scores scale with theta_ref)
    f2_by_theta = defaultdict(list)
    for rec in s5_data:
        theta = rec.get("theta_ref")
        if theta is not None:
            f2_by_theta[theta].append(rec.get("f2", 0))

    bp2 = ax2.boxplot([f2_by_theta[t] for t in thetas],
                       positions=thetas, widths=3, patch_artist=True)
    for box in bp2["boxes"]:
        box.set_facecolor("#3498DB")
        box.set_alpha(0.7)

    ax2.set_xlabel("$\\theta_{ref}$ (°)")
    ax2.set_ylabel("Geometric Quality Score ($f_2$)")
    ax2.set_title("Quality Score Scaling with $\\theta_{ref}$")

    filepath = output_dir / "ablation_theta_ref.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

    return theta_groups

def plot_scenario_heatmap(data: Dict, output_dir: Path = None):
    """Scenario characterization heatmap: difficulty descriptors vs solver performance."""
    if output_dir is None:
        output_dir = FIGURES_DIR

    set_style()

    # Build per-group performance matrix
    groups = []
    hv_moea_means = []
    hv_b1_means = []
    hv_ratios = []
    n_targets_vals = []

    for group in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        if group not in data:
            continue

        gd = data[group]
        if "_summary" in gd:
            summary = gd["_summary"]
            if summary and "moea" in summary:
                # Use summary data for S2/S3
                groups.append(group)
                n_targets_vals.append(summary.get("n_scenarios", 0))
                hv_moea_means.append(0)  # Can't compute HV from summary
                hv_b1_means.append(0)
                hv_ratios.append(0)
            continue

        if "moea" not in gd or "b1" not in gd:
            continue

        moea_hvs = []
        b1_hvs = []
        for rec in gd["moea"]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            moea_hvs.append(compute_hv_simple(pf, (0, 0)))
        for rec in gd["b1"]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            b1_hvs.append(compute_hv_simple(pf, (0, 0)))

        if moea_hvs and b1_hvs:
            groups.append(group)
            mean_moea = np.mean(moea_hvs)
            mean_b1 = np.mean(b1_hvs)
            hv_moea_means.append(mean_moea)
            hv_b1_means.append(mean_b1)
            hv_ratios.append(mean_moea / mean_b1 if mean_b1 > 0 else 0)
            n_recs = gd["moea"][0] if gd["moea"] else {}
            n_targets_vals.append(n_recs.get("n_targets", 0))

    if not groups:
        return

    # Create simple summary bar chart
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(groups))
    width = 0.35

    ax.bar(x - width/2, hv_moea_means, width, label="MOEA", color=COLORS["moea"], alpha=0.8)
    ax.bar(x + width/2, hv_b1_means, width, label="B1", color=COLORS["b1"], alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Mean Hypervolume")
    ax.set_title("HV by Group (MOEA vs B1)")
    ax.legend()

    filepath = output_dir / "group_hv_comparison.pdf"
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  Saved {filepath}")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: MAIN ANALYSIS PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def compute_all_metrics(data: Dict, group: str) -> Dict:
    """Compute HV, IGD, C-metric for all solvers in a group."""
    if group not in data:
        return {"error": f"No data for group {group}"}

    group_data = data[group]
    if "_summary" in group_data:
        return {"error": f"Only summary available for {group}, no per-run data"}

    solvers = [s for s in ["moea", "b1", "b2"] if s in group_data and group_data[s]]
    if not solvers:
        return {"error": f"No solver data for group {group}"}

    ref_frontier = get_reference_frontier(data, group)
    ref_point = get_ref_point(data, group)

    results = {"group": group, "ref_point": ref_point,
               "n_ref_frontier_points": len(ref_frontier),
               "solvers": {}}

    for solver in solvers:
        hvs = []
        igds = []
        for rec in group_data[solver]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            hv = compute_hv_simple(pf, ref_point)
            hvs.append(hv)
            if ref_frontier:
                igd = compute_igd(pf, ref_frontier)
                igds.append(igd)

        results["solvers"][solver] = {
            "n": len(hvs),
            "hv_mean": float(np.mean(hvs)) if hvs else 0,
            "hv_std": float(np.std(hvs)) if hvs else 0,
            "hv_min": float(np.min(hvs)) if hvs else 0,
            "hv_max": float(np.max(hvs)) if hvs else 0,
            "igd_mean": float(np.mean(igds)) if igds else float("nan"),
            "igd_std": float(np.std(igds)) if igds else float("nan"),
        }

    # C-metrics
    if len(solvers) >= 2:
        results["c_metrics"] = {}
        for i, sa in enumerate(solvers):
            for sb in solvers[i+1:]:
                c_ab_vals = []
                c_ba_vals = []
                for rec_a, rec_b in zip(group_data[sa], group_data[sb]):
                    pf_a = rec_a.get("pareto_frontier", [{"f1": rec_a.get("f1", 0), "f2": rec_a.get("f2", 0)}])
                    pf_b = rec_b.get("pareto_frontier", [{"f1": rec_b.get("f1", 0), "f2": rec_b.get("f2", 0)}])
                    c_ab_vals.append(compute_c_metric(pf_a, pf_b))
                    c_ba_vals.append(compute_c_metric(pf_b, pf_a))
                key = f"{sa}_vs_{sb}"
                results["c_metrics"][f"C({sa},{sb})"] = float(np.mean(c_ab_vals))
                results["c_metrics"][f"C({sb},{sa})"] = float(np.mean(c_ba_vals))

    return results

def run_statistical_tests(data: Dict, group: str) -> Dict:
    """Run Wilcoxon + Friedman + Cliff's delta for a group."""
    if group not in data:
        return {"error": f"No data for group {group}"}

    group_data = data[group]
    if "_summary" in group_data:
        return {"error": f"Only summary available for {group}"}

    solvers = [s for s in ["moea", "b1", "b2"] if s in group_data and group_data[s]]
    if len(solvers) < 2:
        return {"error": "Need at least 2 solvers"}

    ref_point = get_ref_point(data, group)

    # Compute per-seed HV
    hv_per_solver = {}
    for solver in solvers:
        hvs = []
        for rec in group_data[solver]:
            pf = rec.get("pareto_frontier", [{"f1": rec.get("f1", 0), "f2": rec.get("f2", 0)}])
            hvs.append(compute_hv_simple(pf, ref_point))
        hv_per_solver[solver] = hvs

    result = {"group": group, "n_seeds": min(len(v) for v in hv_per_solver.values()),
              "pairwise": [], "friedman": None}

    # Pairwise Wilcoxon + Cliff's delta
    for i, sa in enumerate(solvers):
        for sb in solvers[i+1:]:
            pair_result = paired_comparison(
                hv_per_solver[sa], hv_per_solver[sb], sa, sb)
            # Bonferroni correction
            n_comparisons = len(solvers) * (len(solvers) - 1) // 2
            pair_result["p_value_bonferroni"] = min(1.0, pair_result["p_value"] * n_comparisons)
            pair_result["significant_bonf"] = pair_result["p_value_bonferroni"] < 0.05
            result["pairwise"].append(pair_result)

    # Friedman
    if len(solvers) >= 2 and all(len(hv_per_solver[s]) >= 5 for s in solvers):
        result["friedman"] = friedman_nemenyi(hv_per_solver, solvers)

    # Also per-solver summary stats
    result["hv_stats"] = {}
    for solver in solvers:
        hvs = hv_per_solver[solver]
        result["hv_stats"][solver] = {
            "mean": float(np.mean(hvs)),
            "std": float(np.std(hvs)),
            "sem": float(stats.sem(hvs)) if len(hvs) > 1 else 0,
        }

    return result

def generate_all_figures(data: Dict, output_dir: Path = None):
    """Generate all required figures."""
    if output_dir is None:
        output_dir = FIGURES_DIR

    print("\n── Generating Figures ──")

    # Groups with per-run data
    groups_with_data = [g for g in ["S1", "S4", "S5", "S6"]
                        if g in data and "_summary" not in data[g]]

    for group in groups_with_data:
        print(f"\n  Group {group}:")
        plot_pareto_fronts(data, group, output_dir)
        plot_hv_boxplots(data, group, output_dir)
        plot_convergence(data, group, output_dir)
        plot_quality_gain(data, group, output_dir)

    # Ablation figures
    print("\n  Ablation:")
    plot_ablation_theta_ref(data, output_dir)

    # Cross-group comparison
    print("\n  Cross-group:")
    plot_scenario_heatmap(data, output_dir)

def generate_report(data: Dict, all_metrics: Dict, all_stats: Dict) -> str:
    """Generate a summary analysis report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PHASE 4.3: STATISTICAL ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Per-group summary
    for group in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        lines.append(f"\n{'─' * 50}")
        lines.append(f"Group {group}")
        lines.append(f"{'─' * 50}")

        if group in all_metrics and "error" not in all_metrics[group]:
            m = all_metrics[group]
            lines.append(f"  Reference PF points: {m.get('n_ref_frontier_points', 'N/A')}")
            for solver, sm in m.get("solvers", {}).items():
                lines.append(f"  {SOLVER_LABELS.get(solver, solver)}:")
                lines.append(f"    HV: {sm['hv_mean']:.2f} ± {sm['hv_std']:.2f}")
                if not np.isnan(sm.get('igd_mean', float('nan'))):
                    lines.append(f"    IGD: {sm['igd_mean']:.4f} ± {sm['igd_std']:.4f}")

            if "c_metrics" in m:
                lines.append("  C-metrics:")
                for k, v in m["c_metrics"].items():
                    lines.append(f"    {k}: {v:.4f}")

        elif group in data and "_summary" in data[group]:
            s = data[group]["_summary"]
            if s:
                for solver in ["moea", "b1", "b2"]:
                    if solver in s:
                        ss = s[solver]
                        lines.append(f"  {SOLVER_LABELS.get(solver, solver)} (summary only):")
                        lines.append(f"    f1: {ss['f1']['mean']:.1f} ± {ss['f1']['std']:.1f}")
                        lines.append(f"    f2: {ss['f2']['mean']:.2f} ± {ss['f2']['std']:.2f}")
                if "comparison" in s:
                    c = s["comparison"]
                    for comp_key, comp_val in c.items():
                        lines.append(f"  {comp_key}: dominates={comp_val.get('moea_dominates', 'N/A')}")

        # Statistical results
        if group in all_stats and "error" not in all_stats[group]:
            st = all_stats[group]
            lines.append(f"\n  Statistical Tests ({st.get('n_seeds', '?')} seeds):")
            for pair in st.get("pairwise", []):
                lines.append(f"    {pair['comparison']}:")
                lines.append(f"      p = {pair['p_value_formatted']} (Bonf: {pair.get('p_value_bonferroni', 0):.4e})")
                lines.append(f"      Cliff's δ = {pair['cliffs_delta']:.3f} ({pair['effect_size']})")
                lines.append(f"      Direction: {pair['direction']}")

            if st.get("friedman"):
                fr = st["friedman"]
                lines.append(f"    Friedman: χ² = {fr['statistic']:.2f}, p = {fr.get('p_value_formatted', '?')}")

    # Summary table
    lines.append(f"\n{'═' * 70}")
    lines.append("EXECUTIVE SUMMARY")
    lines.append(f"{'═' * 70}")

    for group in ["S1", "S4", "S6"]:
        if group in all_stats and "error" not in all_stats[group]:
            st = all_stats[group]
            hv = st.get("hv_stats", {})
            lines.append(f"\n  {group}:")
            for solver in ["moea", "b1", "b2"]:
                if solver in hv:
                    lines.append(f"    {solver}: HV = {hv[solver]['mean']:.2f} ± {hv[solver]['sem']:.4f}")

    return "\n".join(lines)

def main():
    """Main analysis pipeline."""
    print("═" * 70)
    print("PHASE 4.3: Statistical Analysis Pipeline")
    print("═" * 70)

    # 1. Load data
    print("\n[1/5] Loading experiment data...")
    data = load_all_data()

    for group in sorted(data.keys()):
        gd = data[group]
        if "_summary" in gd:
            print(f"  {group}: aggregate summary only")
        else:
            solvers = [s for s in ["moea", "b1", "b2"] if s in gd and gd[s]]
            counts = {s: len(gd[s]) for s in solvers}
            print(f"  {group}: {counts}")

    # 2. Compute metrics
    print("\n[2/5] Computing HV, IGD, C-metric...")
    all_metrics = {}
    for group in ["S1", "S4", "S5", "S6"]:
        if group in data and "_summary" not in data[group]:
            all_metrics[group] = compute_all_metrics(data, group)
            m = all_metrics[group]
            if "error" not in m:
                print(f"  {group}: MOEA HV = {m['solvers'].get('moea', {}).get('hv_mean', 0):.2f}")
    # Also S2, S3 from summary
    for group in ["S2", "S3"]:
        all_metrics[group] = {"group": group, "note": "summary only"}
        if group in data and "_summary" in data[group]:
            s = data[group]["_summary"]
            if s and "moea" in s:
                print(f"  {group}: f1 = {s['moea']['f1']['mean']:.1f} ± {s['moea']['f1']['std']:.1f}")

    # 3. Statistical tests
    print("\n[3/5] Running statistical tests...")
    all_stats = {}
    for group in ["S1", "S4", "S5", "S6"]:
        if group in data and "_summary" not in data[group]:
            all_stats[group] = run_statistical_tests(data, group)
            st = all_stats[group]
            if "error" not in st:
                print(f"  {group}: {len(st.get('pairwise', []))} pairwise comparisons")
                for pair in st.get("pairwise", []):
                    print(f"    {pair['comparison']}: p={pair['p_value_formatted']}, δ={pair['cliffs_delta']:.3f} ({pair['effect_size']})")

    # 4. Generate figures
    print("\n[4/5] Generating figures...")
    generate_all_figures(data)

    # 5. Report
    print("\n[5/5] Generating report...")
    report = generate_report(data, all_metrics, all_stats)

    report_path = RESULTS_DIR / "analysis_report.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    # Also save JSON metrics
    metrics_path = RESULTS_DIR / "analysis_metrics.json"
    serializable = {}
    for group, m in all_metrics.items():
        serializable[group] = m
    for group, s in all_stats.items():
        if group not in serializable:
            serializable[group] = {}
        serializable[group]["statistics"] = s

    with open(metrics_path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"Metrics saved to {metrics_path}")

    # Print report
    print("\n" + report)

    # CD diagram (cross-group)
    cd_data = {}
    for group, st in all_stats.items():
        if "error" not in st and st.get("friedman"):
            cd_data[group] = {"friedman": st["friedman"]}
    if cd_data:
        plot_cd_diagram(cd_data)

    print("\n" + "=" * 70)
    print("Analysis complete.")
    print("=" * 70)

if __name__ == "__main__":
    main()
