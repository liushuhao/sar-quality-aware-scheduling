#!/usr/bin/env python3
"""
5 figures for IJAE small paper on agile SAR satellite scheduling.
Output: papers/single-sat-quality/figures/fig{1-5}_*.pdf, .png
"""

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.ticker as ticker
import numpy as np
import json, os, warnings
from collections import defaultdict

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ──
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "experiments", "results")
FIG_DIR = os.path.join(PROJECT, "docs", "small-paper-figures")
os.makedirs(FIG_DIR, exist_ok=True)

BASELINES_PATH = os.path.join(RESULTS, "baselines_200.json")
B2_PATH = os.path.join(RESULTS, "b2_profit_bl", "_progress.json")
MOEA2_PATH = os.path.join(RESULTS, "moea_2obj", "_progress.json")
MOEA3_PATH = os.path.join(RESULTS, "moea_3obj", "_progress.json")
STATS_PATH = os.path.join(RESULTS, "statistical_results.json")

# ── Style ──
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 9,
    'axes.titlesize': 10, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.bbox': 'tight',
    'axes.grid': False, 'axes.spines.top': False, 'axes.spines.right': False,
})

SOLVERS = ["G-BL", "G-SM", "GA-P-BL", "MOEA-2", "MOEA-3"]
SOLVER_COLORS = {
    "G-BL": "#E69F00", "G-SM": "#56B4E9", "GA-P-BL": "#009E73",
    "MOEA-2": "#CC79A7", "MOEA-3": "#0072B2",
}
# Scenario-group palette — qualitative, colorblind-safe, distinct from solver palette.
# Used by Fig 1(c) so that S1–S4 are visually separable.
GROUP_COLORS = {"S1": "#E69F00", "S2": "#56B4E9", "S3": "#009E73", "S4": "#CC79A7"}
SCENARIO_GROUPS = ["S1", "S2", "S3", "S4"]


def scenario_group(key):
    return key.split("/")[0]

def _pkl_sha1(p):
    import hashlib
    with open(p, 'rb') as f: return hashlib.sha1(f.read()).hexdigest()[:8]

def save_figure(fig, name):
    for ext in ['.pdf', '.png']:
        path = os.path.join(FIG_DIR, name + ext)
        fig.savefig(path, bbox_inches='tight', pad_inches=0.05)
    size_pdf = os.path.getsize(os.path.join(FIG_DIR, name + '.pdf'))
    size_png = os.path.getsize(os.path.join(FIG_DIR, name + '.png'))
    print(f"  ✓ {name}.pdf: {size_pdf:,d} bytes\n  ✓ {name}.png: {size_png:,d} bytes")
    plt.close(fig)

def _f2_normalized(entry, solver_name):
    """Get per-task f2 mean, auto-detecting SUM vs MEAN format.

    Old solver (pre-refactor): f2 stored as SUM (>1.0 for any real scenario).
    New solver (post-refactor): f2 stored as MEAN (∈ [0,1] per task).

    Detection: if f2 > 1.0, it's SUM → divide by n_selected.
               if f2 ≤ 1.0, it's already MEAN → return as-is.
    """
    f2_raw = entry.get("f2", 0) or 0
    n = entry.get("n_selected", 0) or 1
    if solver_name in ("MOEA-2", "MOEA-3") and f2_raw > 1.0 and n > 0:
        return f2_raw / n
    return f2_raw

def _loess(x, y, frac=0.6, n_pts=100):
    """Tricube-weighted LOESS smooth for (x, y) scatter data.

    Returns (x_smooth, y_smooth) for plotting a trend line.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    span = int(np.ceil(frac * n))
    x_smooth = np.linspace(x.min(), x.max(), n_pts)
    y_smooth = np.zeros(n_pts)
    for i, xi in enumerate(x_smooth):
        dist = np.abs(x - xi)
        idx = np.argpartition(dist, span)[:span]
        d_span = dist[idx]
        d_max = d_span.max()
        if d_max < 1e-10:
            y_smooth[i] = np.mean(y[idx])
        else:
            w = (1 - (d_span / d_max) ** 3) ** 3  # tricube
            w /= w.sum()
            y_smooth[i] = np.sum(w * y[idx])
    return x_smooth, y_smooth


# ═══════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════
print("Loading data...")
with open(BASELINES_PATH) as f: bl_data = json.load(f)
with open(B2_PATH) as f: b2_raw = json.load(f)
with open(MOEA2_PATH) as f: m2_raw = json.load(f)
with open(MOEA3_PATH) as f: m3_raw = json.load(f)
b2_data = b2_raw.get("completed", b2_raw)
m2_data = m2_raw.get("completed", m2_raw)
m3_data = m3_raw.get("completed", m3_raw)

if os.path.exists(STATS_PATH):
    with open(STATS_PATH) as f: stats_data = json.load(f)
else:
    stats_data = None

# Unify into results dict: results[scenario_key][solver] = {f1, f2, f3, ...}
results = defaultdict(dict)
for key in bl_data:
    g = scenario_group(key)
    results[key]["G-BL"] = bl_data[key]["b1"]
    results[key]["G-SM"] = bl_data[key]["b3"]
    results[key]["group"] = g
for key in b2_data:
    results[key]["GA-P-BL"] = b2_data[key]
    if "group" not in results[key]:
        results[key]["group"] = scenario_group(key)
for key in m2_data:
    results[key]["MOEA-2"] = m2_data[key]
for key in m3_data:
    results[key]["MOEA-3"] = m3_data[key]

# For per-scenario HV bars: build the HV mapping from per-scenario HV data if available
if stats_data and "per_scenario_hv" in stats_data:
    per_scenario_hv = stats_data["per_scenario_hv"]
else:
    per_scenario_hv = {}

common_keys = [k for k in results if all(s in results[k] for s in SOLVERS)]
print(f"Loaded: {len(bl_data)} scenarios, {len(common_keys)} common (all 5 solvers)")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 1: Squint Awareness — G-SM vs G-BL (3-panel)
# ═══════════════════════════════════════════════════════════════════════════
print("\n── Fig 1: Squint Awareness ──")
fig = plt.figure(figsize=(11, 4.2))
gs = gridspec.GridSpec(1, 3, width_ratios=[1, 0.8, 1], wspace=0.4,
                        left=0.05, right=0.95, top=0.88, bottom=0.15)

keys_bl_sq = [k for k in common_keys if all(s in results[k] for s in ["G-BL", "G-SM"])]
f3_bl = [results[k]["G-BL"]["f3"] for k in keys_bl_sq]
f3_sq = [results[k]["G-SM"]["f3"] for k in keys_bl_sq]

# (a) f3 scatter
ax_a = fig.add_subplot(gs[0])
lim_min = min(min(f3_bl), min(f3_sq)) * 0.9
lim_max = max(max(f3_bl), max(f3_sq)) * 1.05
n_targets = [results[k].get("G-BL", {}).get("n_targets", 20) for k in keys_bl_sq]
sc = ax_a.scatter(f3_bl, f3_sq, c=n_targets, cmap='viridis', s=18, alpha=0.7, edgecolors='none')
ax_a.plot([lim_min, lim_max], [lim_min, lim_max], 'k--', linewidth=0.8)
ax_a.set_xlim(lim_min, lim_max); ax_a.set_ylim(lim_min, lim_max)
ax_a.set_xlabel("G-BL  $f_3$ (NESZ)", fontsize=9)
ax_a.set_ylabel("G-SM  $f_3$ (NESZ)", fontsize=9)
ax_a.set_title("(a) NESZ improvement", fontsize=10)
cbar = plt.colorbar(sc, ax=ax_a, shrink=0.8)
cbar.set_label("N targets", size=8)
# δ annotation — upper-right is the cleanest area in panel (a); upper-left sits
# on top of the dense yellow N=500 cluster, and lower corners collide with data.
if stats_data and "effect_sizes" in stats_data:
    es = stats_data["effect_sizes"]
    for k, v in es.items():
        if "GSM_f3_vs_GBL_f3" in k or (("G-SM" in k or "GSM" in k) and "f3" in k):
            ax_a.text(0.98, 0.97, f"Cliff's δ = {v['cliff_delta']:+.3f} ({v['magnitude']})",
                     transform=ax_a.transAxes, fontsize=7, ha='right', va='top',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            break

below = sum(1 for i in range(len(f3_bl)) if f3_sq[i] > f3_bl[i])
ax_a.text(0.98, 0.88, f"G-SM better: {below}/{len(f3_bl)}", transform=ax_a.transAxes,
          fontsize=7, va='top', ha='right',
          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# (b) Δf1* histogram
ax_b = fig.add_subplot(gs[1])
delta_f1 = [(results[k]["G-BL"]["f1_raw"] - results[k]["G-SM"]["f1_raw"]) /
            max(results[k]["G-BL"]["f1_raw"], 1.0) for k in keys_bl_sq]
ax_b.hist(delta_f1, bins=25, color='#56B4E9', alpha=0.7, edgecolor='white', linewidth=0.3)
mean_d = np.mean(delta_f1); med_d = np.median(delta_f1)
ax_b.axvline(x=mean_d, color='#D55E00', linestyle='-', linewidth=1.2, label=f'Mean={mean_d:.2f}')
ax_b.axvline(x=med_d, color='#009E73', linestyle=':', linewidth=1.2, label=f'Med={med_d:.2f}')
ax_b.set_xlabel("$\\Delta f_1^*$ (profit loss)", fontsize=9)
ax_b.set_ylabel("Frequency", fontsize=9)
ax_b.set_title("(b) Profit loss distribution", fontsize=10)
ax_b.legend(fontsize=7)

# (c) Δf1* vs N — with LOESS trend
ax_c = fig.add_subplot(gs[2])
all_deltas = []
all_ns = []
for group in SCENARIO_GROUPS:
    gk = [k for k in keys_bl_sq if results[k]["group"] == group]
    if gk:
        g_delta = [(results[k]["G-BL"]["f1_raw"] - results[k]["G-SM"]["f1_raw"]) /
                    max(results[k]["G-BL"]["f1_raw"], 1.0) for k in gk]
        n_vals = [results[k].get("G-BL", {}).get("n_targets", 20) for k in gk]
        # Jitter x positions around discrete group centers to reduce overplotting
        group_x = {"S1": 20, "S2": 100, "S3": 300, "S4": 500}
        jittered = [group_x.get(group, 0) * (1 + np.random.uniform(-0.08, 0.08)) for _ in gk]
        ax_c.scatter(jittered, g_delta, c=GROUP_COLORS.get(group, '#999'), s=25, alpha=0.6,
                    edgecolors='none', label=group)
        all_deltas.extend(g_delta)
        all_ns.extend(n_vals)

# LOESS trend line
if len(all_ns) > 10:
    x_sm, y_sm = _loess(all_ns, all_deltas, frac=0.5, n_pts=80)
    ax_c.plot(x_sm, y_sm, 'k-', linewidth=1.5, alpha=0.7, label='LOESS trend')

ax_c.axhline(y=0, color='gray', linestyle='--', linewidth=0.6)
ax_c.set_xscale('log')
ax_c.set_xticks([20, 100, 300, 500])
ax_c.set_xticklabels(["S1\n(20)", "S2\n(100)", "S3\n(300)", "S4\n(500)"])
ax_c.set_xlim(15, 550)
ax_c.set_xlabel("Scenario class (N targets)", fontsize=9)
ax_c.set_ylabel("$\\Delta f_1^*$ (profit loss)", fontsize=9)
ax_c.set_title("(c) Profit loss vs. scenario scale", fontsize=10)
ax_c.legend(fontsize=7)

save_figure(fig, "fig1_squint_effect")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 2: MOEA-2 vs MOEA-3 — Dual Pareto front overlay (S4 representative)
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 2: MOEA-2 vs MOEA-3 Pareto Overlay ──")
# Use S4 (dense regime) — where the near-identity claim is most consequential
s4_keys = [k for k in common_keys if scenario_group(k) == "S4"
           and "MOEA-2" in results[k] and "MOEA-3" in results[k]]
# Pick the scenario with most MOEA-3 frontier points for visual richness
def _n_frontier(k):
    return len(results[k]["MOEA-3"].get("frontier_f1") or [])
s4_keys.sort(key=_n_frontier, reverse=True)
rep_key_s4 = s4_keys[0] if s4_keys else None

if rep_key_s4:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    plt.subplots_adjust(wspace=0.30, top=0.86, bottom=0.22, left=0.07, right=0.97)

    m2_entry = results[rep_key_s4]["MOEA-2"]
    m3_entry = results[rep_key_s4]["MOEA-3"]
    ff1_m2 = m2_entry.get("frontier_f1") or []
    ff2_m2 = m2_entry.get("frontier_f2") or []
    ff3_m2 = m2_entry.get("frontier_f3") or []
    ff1_m3 = m3_entry.get("frontier_f1") or []
    ff2_m3 = m3_entry.get("frontier_f2") or []
    ff3_m3 = m3_entry.get("frontier_f3") or []

    marker_styles = {"G-BL": 's', "G-SM": '^', "GA-P-BL": 'D'}

    # (a) f1-f2
    for ff1, ff2, color, label in [
        (ff1_m2, ff2_m2, SOLVER_COLORS["MOEA-2"], 'MOEA-2 frontier'),
        (ff1_m3, ff2_m3, SOLVER_COLORS["MOEA-3"], 'MOEA-3 frontier'),
    ]:
        if ff1:
            order = sorted(range(len(ff1)), key=lambda i: ff1[i])
            ax1.plot([ff1[i] for i in order], [ff2[i] for i in order],
                     c=color, linewidth=0.5, alpha=0.35, zorder=2)
            ax1.scatter(ff1, ff2, c=color, s=8, alpha=0.5,
                        edgecolors='none', zorder=3)
    for solver in ["G-BL", "G-SM", "GA-P-BL"]:
        if solver in results[rep_key_s4]:
            r = results[rep_key_s4][solver]
            ax1.scatter(r["f1"], r["f2"], c=SOLVER_COLORS[solver],
                       marker=marker_styles.get(solver, 'o'), s=90,
                       edgecolors='black', linewidth=1.2, label=solver, zorder=5)
    ax1.set_xlabel("$f_1^*$ (Norm. Profit)", fontsize=9)
    ax1.set_ylabel("$f_2$ (Geom. Quality)", fontsize=9)
    ax1.set_title(f"(a) $f_1^*$–$f_2$, S4 ($N=500$)", fontsize=10)

    # (b) f1-f3
    for ff1, ff3, color, label in [
        (ff1_m2, ff3_m2, SOLVER_COLORS["MOEA-2"], 'MOEA-2 frontier'),
        (ff1_m3, ff3_m3, SOLVER_COLORS["MOEA-3"], 'MOEA-3 frontier'),
    ]:
        if ff1:
            order = sorted(range(len(ff1)), key=lambda i: ff1[i])
            ax2.plot([ff1[i] for i in order], [ff3[i] for i in order],
                     c=color, linewidth=0.5, alpha=0.35, zorder=2)
            ax2.scatter(ff1, ff3, c=color, s=8, alpha=0.5,
                        edgecolors='none', zorder=3)
    for solver in ["G-BL", "G-SM", "GA-P-BL"]:
        if solver in results[rep_key_s4]:
            r = results[rep_key_s4][solver]
            ax2.scatter(r["f1"], r["f3"], c=SOLVER_COLORS[solver],
                       marker=marker_styles.get(solver, 'o'), s=90,
                       edgecolors='black', linewidth=1.2, label=solver, zorder=5)
    ax2.set_xlabel("$f_1^*$ (Norm. Profit)", fontsize=9)
    ax2.set_ylabel("$f_3$ (NESZ)", fontsize=9)
    ax2.set_title(f"(b) $f_1^*$–$f_3$, S4 ($N=500$)", fontsize=10)

    # Shared legend
    handles, labels = ax1.get_legend_handles_labels()
    # Deduplicate: MOEA-2 and MOEA-3 appear twice (once per panel)
    seen = set()
    unique_h, unique_l = [], []
    for h, l in zip(handles, labels):
        if l not in seen:
            seen.add(l)
            unique_h.append(h)
            unique_l.append(l)
    ax1.legend().set_visible(False)
    ax2.legend().set_visible(False)
    fig.legend(unique_h, unique_l,
               loc='lower center', bbox_to_anchor=(0.5, -0.02),
               ncol=5, frameon=True, framealpha=0.9, fontsize=7,
               borderaxespad=0.0)

    # δ annotation
    if stats_data and "effect_sizes" in stats_data:
        for k, v in stats_data["effect_sizes"].items():
            if "MOEA2_f2_vs_MOEA3_f2" in k or "MOEA-2_f2_vs_MOEA-3_f2" in k:
                ax1.text(0.98, 0.97, f"δ(f2)={v['cliff_delta']:+.3f} ({v['magnitude']})",
                        transform=ax1.transAxes, fontsize=7, ha='right', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                break

    save_figure(fig, "fig2_solver_profiles")
else:
    print("  ⚠ No S4 data for Fig 2 — skipping")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 3: Pareto Front — Dual-panel f1-f2 / f1-f3 on S4 representative
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 3: Pareto Front ──")
# Use S4 (dense regime) — consistent with body text claim (§6.3, L771-772)
s4_keys = [k for k in common_keys if scenario_group(k) == "S4" and "MOEA-3" in results[k]]
def _f1_spread(k):
    fr = results[k]["MOEA-3"].get("frontier_f1") or []
    return (max(fr) - min(fr)) if fr else 0.0
s4_keys.sort(key=_f1_spread, reverse=True)
rep_key = s4_keys[0] if s4_keys else (common_keys[0] if common_keys else None)
group_label = "S4 ($N=500$)"

if rep_key:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    # bottom=0.22 reserves a strip below the axes for the shared horizontal legend.
    plt.subplots_adjust(wspace=0.30, top=0.86, bottom=0.22, left=0.07, right=0.97)
    m3_entry = results[rep_key]["MOEA-3"]
    # Frontier data lives as three parallel lists, not a tuple-zipped 'frontier' key.
    ff1 = m3_entry.get("frontier_f1") or []
    ff2 = m3_entry.get("frontier_f2") or []
    ff3 = m3_entry.get("frontier_f3") or []
    marker_styles = {"G-BL": 's', "G-SM": '^', "GA-P-BL": 'D'}

    # (a) f1-f2
    if ff1:
        # Draw a faint connecting line for the frontier, then the points.
        order = sorted(range(len(ff1)), key=lambda i: ff1[i])
        ax1.plot([ff1[i] for i in order], [ff2[i] for i in order],
                 c='#0072B2', linewidth=0.6, alpha=0.4, zorder=2)
        ax1.scatter(ff1, ff2, c='#0072B2', s=10, alpha=0.6,
                    edgecolors='none', label='MOEA-3 frontier', zorder=3)
    for solver in ["G-BL", "G-SM", "GA-P-BL"]:
        if solver in results[rep_key]:
            r = results[rep_key][solver]
            ax1.scatter(r["f1"], r["f2"], c=SOLVER_COLORS[solver],
                       marker=marker_styles.get(solver, 'o'), s=90,
                       edgecolors='black', linewidth=1.2, label=solver, zorder=5)
    ax1.set_xlabel("$f_1^*$ (Norm. Profit)", fontsize=9)
    ax1.set_ylabel("$f_2$ (Geom. Quality)", fontsize=9)
    ax1.set_title("(a) $f_1^*$–$f_2$: profit vs geometric quality", fontsize=10)
    # Build a single shared horizontal legend below both subplots. We do this once
    # by reading handles from ax1 (handles from ax2 would duplicate the same series
    # since both panels plot the same frontier + baselines). Anchored to the figure
    # (bbox_to_anchor is in figure-fraction coords) so it never overlaps either
    # panel's y-axis label or any data.
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend().set_visible(False)  # suppress the per-axes auto-legend
    fig.legend(handles, labels,
               loc='lower center', bbox_to_anchor=(0.5, -0.02),
               ncol=4, frameon=True, framealpha=0.9, fontsize=7,
               borderaxespad=0.0)
    if stats_data and "effect_sizes" in stats_data:
        for k, v in stats_data["effect_sizes"].items():
            if "MOEA-2_f2_vs_GBL_f2" in k:
                ax1.text(0.98, 0.97, f"δ = {v['cliff_delta']:+.3f} ({v['magnitude']})",
                        transform=ax1.transAxes, fontsize=7, ha='right', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                break

    # (b) f1-f3
    if ff1:
        order = sorted(range(len(ff1)), key=lambda i: ff1[i])
        ax2.plot([ff1[i] for i in order], [ff3[i] for i in order],
                 c='#0072B2', linewidth=0.6, alpha=0.4, zorder=2)
        ax2.scatter(ff1, ff3, c='#0072B2', s=10, alpha=0.6,
                    edgecolors='none', label='MOEA-3 frontier', zorder=3)
    for solver in ["G-BL", "G-SM", "GA-P-BL"]:
        if solver in results[rep_key]:
            r = results[rep_key][solver]
            ax2.scatter(r["f1"], r["f3"], c=SOLVER_COLORS[solver],
                       marker=marker_styles.get(solver, 'o'), s=90,
                       edgecolors='black', linewidth=1.2, label=solver, zorder=5)
    ax2.set_xlabel("$f_1^*$ (Norm. Profit)", fontsize=9)
    ax2.set_ylabel("$f_3$ (NESZ)", fontsize=9)
    ax2.set_title("(b) $f_1^*$–$f_3$: profit vs NESZ quality", fontsize=10)
    # No legend on ax2 — see shared legend on ax1.
    ax2.legend().set_visible(False)
    if stats_data and "effect_sizes" in stats_data:
        for k, v in stats_data["effect_sizes"].items():
            if "GSM_f3_vs_GBL_f3" in k:
                ax2.text(0.98, 0.97, f"δ = {v['cliff_delta']:+.3f} ({v['magnitude']})",
                        transform=ax2.transAxes, fontsize=7, ha='right', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                break

    save_figure(fig, "fig3_pareto_front")
else:
    print("  ⚠ No data for Fig 3 — skipping")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 4: Statistical Validation — HV boxplot + δ forest plot
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 4: Statistical Validation ──")
if stats_data and "per_scenario_hv" in stats_data:
    fig = plt.figure(figsize=(8, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.2, 1], wspace=0.35,
                           left=0.07, right=0.97, top=0.90, bottom=0.12)

    # LEFT: HV boxplot
    ax_left = fig.add_subplot(gs[0])
    solver_hvs = {s: [] for s in SOLVERS}
    for sc_key, sc_hv in per_scenario_hv.items():
        for solver in SOLVERS:
            if solver in sc_hv:
                solver_hvs[solver].append(sc_hv[solver])

    bp = ax_left.boxplot([solver_hvs[s] for s in SOLVERS],
                          patch_artist=True, widths=0.55,
                          medianprops={'color': 'black', 'linewidth': 1.2},
                          flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.3})
    for i, solver in enumerate(SOLVERS):
        bp['boxes'][i].set_facecolor(SOLVER_COLORS[solver])
        bp['boxes'][i].set_alpha(0.7)
    ax_left.set_xticklabels(SOLVERS, fontsize=8)
    ax_left.set_ylabel("Hypervolume", fontsize=9)
    ax_left.set_title("Hypervolume distribution (reference)", fontsize=10)
    # Annotation: clarify that the small grey dots are per-scenario outliers, not
    # data noise. Placed at the lower-left so it never collides with the upper-left
    # Friedman box. Reference note ("reference") in the title signals that HV is a
    # secondary metric, not a decision objective.
    ax_left.text(0.02, 0.02, "○ per-scenario HV (outliers beyond 1.5×IQR)",
                transform=ax_left.transAxes, fontsize=6.5, ha='left', va='bottom',
                style='italic', color='#555')

    # RIGHT: δ forest plot
    ax_right = fig.add_subplot(gs[1])
    if "pairwise_wilcoxon" in stats_data:
        pw = stats_data["pairwise_wilcoxon"]
        pairs = []
        for k, v in pw.items():
            if isinstance(v, dict) and "cliffs_delta" in v and "_vs_" in k:
                s1, s2 = k.split("_vs_")
                if s1 in SOLVERS and s2 in SOLVERS:
                    pairs.append((k, v["cliffs_delta"], v.get("p_value", 1.0)))
        pairs.sort(key=lambda x: abs(x[1]))
        y_positions = list(range(len(pairs)))
        labels = [f"{p[0].split('_vs_')[0]} vs {p[0].split('_vs_')[1]}" for p in pairs]
        deltas = [p[1] for p in pairs]
        # Highlight MOEA-2 vs MOEA-3
        colors = ['#D55E00' if ('MOEA-2' in p[0] and 'MOEA-3' in p[0]) else '#0072B2' for p in pairs]
        ax_right.barh(y_positions, deltas, height=0.6, color=colors, alpha=0.8, edgecolor='white')
        ax_right.axvline(x=0, color='black', linewidth=0.8)
        ax_right.axvspan(-0.147, 0.147, alpha=0.05, color='green')
        # Direction-of-effect annotation: Cliff's δ is computed as A(row) - A(col)
        # (Vargha-Delaney, scaled), so positive bars mean the ROW solver has higher
        # HV. Placed in the right strip above the existing MOEA-2-vs-MOEA-3 callout
        # so the two annotations don't collide.
        ax_right.text(0.98, 0.16,
                      "δ > 0  →  row solver\n          has higher HV",
                      transform=ax_right.transAxes, fontsize=6.5,
                      ha='right', va='bottom', style='italic', color='#555')
        ax_right.set_yticks(y_positions)
        ax_right.set_yticklabels(labels, fontsize=6.5)
        ax_right.set_xlabel("Cliff's δ (effect size)", fontsize=9)
        ax_right.set_title("Pairwise effect sizes", fontsize=10)
        # Annotation: place the MOEA-2 vs MOEA-3 label OUTSIDE the bar (to the right
        # of the bar tip), so it never sits on top of the orange rectangle.
        for i, (label, d) in enumerate(zip(labels, deltas)):
            if 'MOEA-2' in label and 'MOEA-3' in label:
                ax_right.annotate(f"MOEA-2 vs MOEA-3: δ={d:+.2f} (negligible)",
                                 xy=(d, i), xytext=(8, 0), textcoords='offset points',
                                 fontsize=7, va='center', ha='left',
                                 color='#D55E00', fontweight='bold')

    if "friedman" in stats_data:
        fp = stats_data["friedman"]["p_value"]
        fp_str = "p<0.001" if fp < 0.001 else f"p={fp:.3f}"
        # Place in the upper-LEFT of the HV panel (away from MOEA-2/MOEA-3 boxes).
        ax_left.text(0.02, 0.95, f"Friedman {fp_str}", transform=ax_left.transAxes,
                    ha='left', va='top', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))

    save_figure(fig, "fig4_hypervolume")
else:
    print("  ⚠ No HV data — skipping Fig 4")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 5: Quality Boxplots — f2 faceted by scenario group
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 5: Quality Boxplots ──")
fig, axes = plt.subplots(2, 2, figsize=(7.5, 7.5), sharey=True)
plt.subplots_adjust(hspace=0.35, wspace=0.15, top=0.93, bottom=0.08, left=0.10, right=0.95)

group_f2 = {g: {s: [] for s in SOLVERS} for g in SCENARIO_GROUPS}
for k in common_keys:
    g = results[k]["group"]
    if g in group_f2:
        for s in SOLVERS:
            if s in results[k]:
                group_f2[g][s].append(_f2_normalized(results[k][s], s))

group_n_map = {"S1": "n≈20", "S2": "n≈100", "S3": "n≈300", "S4": "n≈500"}

for idx, group in enumerate(SCENARIO_GROUPS):
    row, col = divmod(idx, 2)
    ax = axes[row][col]
    box_data = [group_f2[group][s] for s in SOLVERS if group_f2[group][s]]
    bp = ax.boxplot(box_data, positions=range(len(SOLVERS)),
                     patch_artist=True, widths=0.55,
                     medianprops={'color': 'black', 'linewidth': 1.2},
                     flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.3})
    for i, solver in enumerate(SOLVERS):
        bp['boxes'][i].set_facecolor(SOLVER_COLORS[solver])
        bp['boxes'][i].set_alpha(0.7)
    ax.set_xticklabels(SOLVERS, rotation=30, ha='right', fontsize=7)
    ax.set_title(f"{group} ({group_n_map[group]})", fontsize=10)
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
    # δ annotation per panel
    if stats_data and "effect_sizes" in stats_data:
        for k, v in stats_data["effect_sizes"].items():
            if "MOEA-2_f2_vs_GBL_f2" in k:
                ax.text(0.98, 0.15, f"δ={v['cliff_delta']:+.2f}", transform=ax.transAxes,
                       fontsize=7, ha='right', color='#555')
                break

fig.supylabel("$f_2$ (Geometric Quality)", fontsize=10)
# Shared caption at the figure bottom: the small grey dots in every panel are
# boxplot fliers (per-scenario outliers beyond 1.5×IQR), not data noise. One
# caption is enough because all four subplots use identical flier rendering.
fig.text(0.5, 0.015,
         "○ grey markers = per-scenario $f_2$ values beyond $1.5\\times\\mathrm{IQR}$ (outliers)",
         ha='center', va='bottom', fontsize=7, style='italic', color='#555')
save_figure(fig, "fig5_scale_sensitivity")

# ── Done ──
print("\n" + "=" * 50)
print(f"All figures saved to {FIG_DIR}")
for i in range(1, 6):
    for prefix in [f"fig{i}"]:
        pdf = os.path.join(FIG_DIR, f"{prefix}_*.pdf")
        import glob
        matches = glob.glob(pdf)
        if matches:
            print(f"  {os.path.basename(matches[0])}: {os.path.getsize(matches[0]):,d} bytes")
print("=" * 50)
