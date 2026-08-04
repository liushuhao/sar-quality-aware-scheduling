#!/usr/bin/env python3
"""
5 figures for IJAE small paper on agile SAR satellite scheduling.
Output: papers/single-sat-quality/figures/fig{1-5}_*.pdf, .png
"""

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scienceplots
from matplotlib import gridspec
import matplotlib.ticker as ticker
import numpy as np
import json, os, sys, warnings
from collections import defaultdict
from pathlib import Path

# Import figure export helpers from scipilot-figure-skill (global skill)
SCIPLOT = os.path.expanduser('~/.claude/skills/scipilot-figure-skill/scripts')
if os.path.isdir(SCIPLOT):
    sys.path.insert(0, SCIPLOT)
    from export_figure import export_figure
    def save_publication_figure(fig, basename, formats=None, dpi=300, **kw):
        return export_figure(fig, basename, formats=formats, dpi=dpi, **kw)
else:
    # Fallback: minimal save
    def save_publication_figure(fig, basename, formats=None, dpi=300, **kw):
        paths = []
        for fmt in (formats or ['pdf', 'png']):
            p = f"{basename}.{fmt}"
            fig.savefig(p, dpi=dpi, bbox_inches='tight', **{k: v for k, v in kw.items() if k != 'pad_inches'})
            paths.append(p)
        return paths

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ──
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "experiments", "results")
FIG_DIR = os.path.join(PROJECT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

BASELINES_PATH = os.path.join(RESULTS, "baselines_200.json")
B2_PATH = os.path.join(RESULTS, "b2_profit_bl", "_progress.json")
MOEA2_PATH = os.path.join(RESULTS, "moea_2obj", "_progress.json")
MOEA3_PATH = os.path.join(RESULTS, "moea_3obj", "_progress.json")
STATS_PATH = os.path.join(RESULTS, "statistical_results.json")

# ── Style ──
plt.style.use(['science', 'nature'])
plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 10, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'figure.dpi': 150,
    'text.usetex': False,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
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
    paths = save_publication_figure(
        fig, os.path.join(FIG_DIR, name),
        formats=['pdf', 'png'], dpi=300, pad_inches=0.05
    )
    for p in paths:
        p_obj = Path(p)
        print(f"  ✓ {p_obj.name}: {p_obj.stat().st_size:,d} bytes")
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

def _cliffs_delta(a, b):
    """Return Cliff's delta for two independent samples."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if not len(a) or not len(b):
        return np.nan
    differences = a[:, None] - b[None, :]
    return (np.sum(differences > 0) - np.sum(differences < 0)) / differences.size


def _delta_magnitude(delta):
    """Classify Cliff's delta using the standard 0.147/0.33/0.474 cutoffs."""
    magnitude = abs(delta)
    if magnitude < 0.147:
        return "negligible"
    if magnitude < 0.33:
        return "small"
    if magnitude < 0.474:
        return "medium"
    return "large"


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

save_figure(fig, "fig2_squint_effect")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 2: [REMOVED — merged into Fig 3]
#  (MOEA-2 vs MOEA-3 overlay now included in Fig 3)
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 2 (merged from former Fig 2 + Fig 3): Pareto Front — Dual-panel
#  f1-f2 / f1-f3 on S4 representative, with MOEA-2 vs MOEA-3 overlay
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 2: Pareto Front (merged, incl. MOEA-2 vs MOEA-3 overlay) ──")
# Use S4 (dense regime) — consistent with body text claim (§6.3)
s4_keys = [k for k in common_keys if scenario_group(k) == "S4"
           and "MOEA-2" in results[k] and "MOEA-3" in results[k]]
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
    m2_entry = results[rep_key].get("MOEA-2")  # may be None if only MOEA-3 available
    # Frontier data lives as three parallel lists, not a tuple-zipped 'frontier' key.
    ff1_m3 = m3_entry.get("frontier_f1") or []
    ff2_m3 = m3_entry.get("frontier_f2") or []
    ff3_m3 = m3_entry.get("frontier_f3") or []
    if m2_entry:
        ff1_m2 = m2_entry.get("frontier_f1") or []
        ff2_m2 = m2_entry.get("frontier_f2") or []
        ff3_m2 = m2_entry.get("frontier_f3") or []
    else:
        ff1_m2 = ff2_m2 = ff3_m2 = []
    marker_styles = {"G-BL": 's', "G-SM": '^', "GA-P-BL": 'D'}

    # (a) f1-f2 — MOEA-3 frontier + MOEA-2 overlay + baselines
    if ff1_m3:
        # Draw a faint connecting line for the MOEA-3 frontier, then the points.
        order = sorted(range(len(ff1_m3)), key=lambda i: ff1_m3[i])
        ax1.plot([ff1_m3[i] for i in order], [ff2_m3[i] for i in order],
                 c='#0072B2', linewidth=0.6, alpha=0.4, zorder=2)
        ax1.scatter(ff1_m3, ff2_m3, c='#0072B2', s=10, alpha=0.6,
                    edgecolors='none', label='MOEA-3 frontier', zorder=3)
    # MOEA-2 overlay (lighter, smaller)
    if ff1_m2:
        order2 = sorted(range(len(ff1_m2)), key=lambda i: ff1_m2[i])
        ax1.plot([ff1_m2[i] for i in order2], [ff2_m2[i] for i in order2],
                 c='#CC79A7', linewidth=0.5, alpha=0.3, zorder=2)
        ax1.scatter(ff1_m2, ff2_m2, c='#CC79A7', s=6, alpha=0.4,
                    edgecolors='none', label='MOEA-2 frontier', zorder=3)
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
    # Deduplicate: MOEA-2 and MOEA-3 appear twice (once per panel)
    seen = set()
    unique_h, unique_l = [], []
    for h, l in zip(handles, labels):
        if l not in seen:
            seen.add(l)
            unique_h.append(h)
            unique_l.append(l)
    ax1.legend().set_visible(False)  # suppress the per-axes auto-legend
    fig.legend(unique_h, unique_l,
               loc='lower center', bbox_to_anchor=(0.5, -0.02),
               ncol=5, frameon=True, framealpha=0.9, fontsize=7,
               borderaxespad=0.0)
    if stats_data and "effect_sizes" in stats_data:
        for k, v in stats_data["effect_sizes"].items():
            if "MOEA-2_f2_vs_GBL_f2" in k:
                ax1.text(0.98, 0.97, f"MOEA-2 vs G-BL: δ={v['cliff_delta']:+.3f} ({v['magnitude']})",
                        transform=ax1.transAxes, fontsize=7, ha='right', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                break
        for k, v in stats_data["effect_sizes"].items():
            if "MOEA2_f2_vs_MOEA3_f2" in k or "MOEA-2_f2_vs_MOEA-3_f2" in k:
                ax1.text(0.98, 0.88, f"MOEA-2 vs MOEA-3: δ={v['cliff_delta']:+.3f} ({v['magnitude']})",
                        transform=ax1.transAxes, fontsize=7, ha='right', va='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                break

    # (b) f1-f3 — MOEA-3 frontier + MOEA-2 overlay + baselines
    if ff1_m3:
        order = sorted(range(len(ff1_m3)), key=lambda i: ff1_m3[i])
        ax2.plot([ff1_m3[i] for i in order], [ff3_m3[i] for i in order],
                 c='#0072B2', linewidth=0.6, alpha=0.4, zorder=2)
        ax2.scatter(ff1_m3, ff3_m3, c='#0072B2', s=10, alpha=0.6,
                    edgecolors='none', label='MOEA-3 frontier', zorder=3)
    # MOEA-2 overlay (lighter, smaller)
    if ff1_m2:
        order2 = sorted(range(len(ff1_m2)), key=lambda i: ff1_m2[i])
        ax2.plot([ff1_m2[i] for i in order2], [ff3_m2[i] for i in order2],
                 c='#CC79A7', linewidth=0.5, alpha=0.3, zorder=2)
        ax2.scatter(ff1_m2, ff3_m2, c='#CC79A7', s=6, alpha=0.4,
                    edgecolors='none', label='MOEA-2 frontier', zorder=3)
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

    save_figure(fig, "fig4_solver_profiles")
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
    ax_left.text(0.02, 0.02, r"$\circ$ per-scenario HV (outliers beyond $1.5\times\mathrm{IQR}$)",
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
        colors = ['#808080' if ('MOEA-2' in p[0] and 'MOEA-3' in p[0]) else '#0072B2' for p in pairs]
        ax_right.barh(y_positions, deltas, height=0.6, color=colors, alpha=0.8, edgecolor='white')
        ax_right.axvline(x=0, color='black', linewidth=0.8)
        ax_right.axvspan(-0.147, 0.147, alpha=0.08, color='#808080')
        ax_right.annotate("negligible effect",
                          xy=(0.0, len(pairs) - 0.5), xytext=(0, 3),
                          textcoords='offset points', ha='center', va='bottom',
                          fontsize=6.5, color='#555')
        # Direction-of-effect annotation: Cliff's δ is computed as A(row) - A(col)
        # (Vargha-Delaney, scaled), so positive bars mean the ROW solver has higher
        # HV. Placed in the right strip above the existing MOEA-2-vs-MOEA-3 callout
        # so the two annotations don't collide.
        ax_right.text(0.98, 0.16,
                      r"$\delta > 0$  $\rightarrow$  row solver" "\n" "          has higher HV",
                      transform=ax_right.transAxes, fontsize=6.5,
                      ha='right', va='bottom', style='italic', color='#555')
        ax_right.set_yticks(y_positions)
        ax_right.set_yticklabels(labels, fontsize=6.5)
        ax_right.set_xlabel(r"Cliff's $\delta$ (effect size)", fontsize=9)
        ax_right.set_title("Pairwise effect sizes", fontsize=10)
        # Annotation: place the MOEA-2 vs MOEA-3 label OUTSIDE the bar (to the right
        # of the bar tip), so it never sits on top of the orange rectangle.
        for i, (label, d) in enumerate(zip(labels, deltas)):
            if 'MOEA-2' in label and 'MOEA-3' in label:
                ax_right.annotate(f"MOEA-2 vs MOEA-3: δ={d:+.2f} (small)",
                                 xy=(d, i), xytext=(8, 0), textcoords='offset points',
                                 fontsize=7, va='center', ha='left',
                                 color='#555', fontweight='normal')

    if "friedman" in stats_data:
        fp = stats_data["friedman"]["p_value"]
        fp_str = "p<0.001" if fp < 0.001 else f"p={fp:.3f}"
        # Place in the upper-LEFT of the HV panel (away from MOEA-2/MOEA-3 boxes).
        ax_left.text(0.02, 0.95, f"Friedman {fp_str}", transform=ax_left.transAxes,
                    ha='left', va='top', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))

    save_figure(fig, "fig1_hypervolume")
else:
    print("  ⚠ No HV data — skipping Fig 4")

# ═══════════════════════════════════════════════════════════════════════════
#  FIGURE 5: 3-panel objective boxplots + logistic regression
#  3×2 grid (3 objectives × 2 scenario-group pairs) + bottom full-width panel
#  Shared y-axis per row; all panels for a given objective share the same scale.
# ═══════════════════════════════════════════════════════════════════════════
print("── Fig 5: 3-Objective Boxplots + Logistic Regression ──")

def _normalized_metric(entry, metric, solver_name):
    """Return per-task mean for f2/f3 (auto-detect SUM vs MEAN); raw for f1."""
    val = float(entry.get(metric, 0.0) or 0.0)
    n = int(entry.get("n_selected", 0) or 1)
    if metric in ("f2", "f3") and solver_name in ("MOEA-2", "MOEA-3") and val > 1.0 and n > 0:
        return val / n
    return val

objectives = ["f1", "f2", "f3"]
obj_labels = {
    "f1": r"$f_1^*$ (Norm. Profit)",
    "f2": r"$f_2$ (Geom. Quality)",
    "f3": r"$f_3$ (NESZ Quality)",
}
group_pairs = [("S1", "S2"), ("S3", "S4")]
pair_labels = ["S1–S2", "S3–S4"]
pair_n_labels = ["n≈20–100", "n≈300–500"]

# Collect data: obj_data[obj][pair_idx][solver] = list of values
obj_data = {}
for obj in objectives:
    obj_data[obj] = {}
    for pi, (g1, g2) in enumerate(group_pairs):
        obj_data[obj][pi] = {}
        for solver in SOLVERS:
            vals = []
            for k in common_keys:
                g = results[k]["group"]
                if g in (g1, g2) and solver in results[k]:
                    if obj == "f1":
                        v = results[k][solver].get("f1", 0.0) or 0.0
                    else:
                        v = _normalized_metric(results[k][solver], obj, solver)
                    vals.append(v)
            obj_data[obj][pi][solver] = vals

# Determine y-limits per objective (shared across both columns)
obj_ylim = {}
for obj in objectives:
    all_vals = []
    for pi in range(2):
        for solver in SOLVERS:
            all_vals.extend(obj_data[obj][pi][solver])
    if all_vals:
        vmin = np.percentile(all_vals, 1)
        vmax = np.percentile(all_vals, 99)
        margin = (vmax - vmin) * 0.15 or 0.05
        obj_ylim[obj] = (vmin - margin, vmax + margin)
    else:
        obj_ylim[obj] = (0, 1)

fig = plt.figure(figsize=(8, 10.5))
gs = gridspec.GridSpec(4, 2, height_ratios=[1, 1, 1, 0.9],
                       hspace=0.35, wspace=0.20,
                       left=0.09, right=0.95, top=0.96, bottom=0.08)

for oi, obj in enumerate(objectives):
    for pi in range(2):
        ax = fig.add_subplot(gs[oi, pi])
        box_data = [obj_data[obj][pi][s] for s in SOLVERS]
        bp = ax.boxplot(box_data, positions=range(len(SOLVERS)),
                        patch_artist=True, widths=0.55,
                        medianprops={'color': 'black', 'linewidth': 1.2},
                        flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.3})
        for i, solver in enumerate(SOLVERS):
            bp['boxes'][i].set_facecolor(SOLVER_COLORS[solver])
            bp['boxes'][i].set_alpha(0.7)
        ax.set_xticklabels(SOLVERS, rotation=30, ha='right', fontsize=7)
        ax.set_title(f"{pair_labels[pi]} ({pair_n_labels[pi]})", fontsize=10)
        ax.yaxis.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        ax.set_ylim(obj_ylim[obj])

        # Per-pair effect size: MOEA-2 vs G-BL
        delta = _cliffs_delta(
            np.asarray(obj_data[obj][pi]["MOEA-2"]),
            np.asarray(obj_data[obj][pi]["G-BL"])
        )
        if np.isfinite(delta):
            ax.text(0.98, 0.96,
                    f"MOEA-2 vs G-BL\nδ={delta:+.2f} ({_delta_magnitude(delta)})",
                    transform=ax.transAxes, fontsize=6.5, ha='right', va='top',
                    color='#444',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                              edgecolor='#B0B0B0', linewidth=0.5, alpha=0.85))

    # Row label (shared y-axis label)
    fig.text(0.01, 0.5 * (gs[oi, 0].y0 + gs[oi, 0].y1),
             obj_labels[obj], fontsize=9, ha='left', va='center', rotation=90)

# ── Bottom panel: Logistic regression for f1* deficit ──
ax_log = fig.add_subplot(gs[3, :])
from scipy.optimize import minimize

# Compute deficit per scenario
deficit_data = []
n_targets_list = []
for k in common_keys:
    if "MOEA-2" in results[k] and "G-BL" in results[k]:
        f1_moea = results[k]["MOEA-2"].get("f1", 0.0) or 0.0
        n_t = results[k].get("G-BL", {}).get("n_targets", 0)
        deficit = 1.0 if f1_moea < 0.95 else 0.0
        deficit_data.append((n_t, deficit))
        n_targets_list.append(n_t)

n_vals = np.asarray([d[0] for d in deficit_data])
deficit_vals = np.asarray([d[1] for d in deficit_data])

# Fit logistic regression: p(deficit) = 1 / (1 + exp(-(alpha + beta * N)))
def neg_log_likelihood(params, x, y):
    alpha, beta = params
    p = 1.0 / (1.0 + np.exp(-(alpha + beta * x)))
    # Avoid log(0)
    eps = 1e-12
    return -np.sum(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

result = minimize(neg_log_likelihood, x0=[-2.0, 0.01], args=(n_vals, deficit_vals),
                  method='Nelder-Mead')
alpha_opt, beta_opt = result.x

# Generate fitted curve
n_smooth = np.linspace(10, 550, 200)
p_smooth = 1.0 / (1.0 + np.exp(-(alpha_opt + beta_opt * n_smooth)))

# Bootstrap CI for N50
n_bootstrap = 1000
n50_samples = []
rng = np.random.default_rng(42)
n_unique = len(deficit_data)
for _ in range(n_bootstrap):
    idx = rng.integers(0, n_unique, n_unique)
    x_boot = n_vals[idx]
    y_boot = deficit_vals[idx]
    try:
        res = minimize(neg_log_likelihood, x0=[-2.0, 0.01], args=(x_boot, y_boot),
                       method='Nelder-Mead')
        a, b = res.x
        if b > 0:  # Only valid if slope is positive
            n50 = -a / b
            n50_samples.append(n50)
    except Exception:
        pass

n50_est = -alpha_opt / beta_opt
n50_lower = np.percentile(n50_samples, 2.5) if n50_samples else np.nan
n50_upper = np.percentile(n50_samples, 97.5) if n50_samples else np.nan

# Scatter: per-scenario deficit (jittered for visibility)
jitter = rng.uniform(-8, 8, len(n_vals))
ax_log.scatter(n_vals + jitter, deficit_vals, alpha=0.3, s=8, c='#555',
               edgecolors='none', label='Per-scenario deficit')

# Fitted curve
ax_log.plot(n_smooth, p_smooth, 'k-', linewidth=1.8, label='Logistic fit')

# N50 marker
ax_log.axvline(x=n50_est, color='#D55E00', linestyle='--', linewidth=1.2,
               label=f'$N_{{50}} \\approx {n50_est:.0f}$')
if not np.isnan(n50_lower) and not np.isnan(n50_upper):
    ax_log.axvspan(n50_lower, n50_upper, alpha=0.08, color='#D55E00')
    ax_log.annotate(f'95% CI [{n50_lower:.0f}, {n50_upper:.0f}]',
                    xy=(n50_est, 0.5), xytext=(n50_est + 50, 0.55),
                    fontsize=7, color='#D55E00',
                    arrowprops=dict(arrowstyle='->', color='#D55E00', lw=0.8))

ax_log.set_xlabel('Number of targets $N$', fontsize=9)
ax_log.set_ylabel('$P(f_1^* < 0.95)$', fontsize=9)
ax_log.set_title('Multi-objective advantage transition', fontsize=10)
ax_log.set_xlim(10, 550)
ax_log.legend(fontsize=7, loc='upper right', ncol=3)
ax_log.yaxis.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
ax_log.text(0.02, 0.98,
            r"$\circ$ per-scenario $f_1^*$ deficit (MOEA-2 vs G-BL, $f_1^*<0.95$)",
            transform=ax_log.transAxes, fontsize=6.5, ha='left', va='top',
            style='italic', color='#555')

save_figure(fig, "fig3_scale_sensitivity")

# ── Done ──
print("\n" + "=" * 50)
print(f"All figures saved to {FIG_DIR}")
for i in range(1, 6):
    pdf = os.path.join(FIG_DIR, f"fig{i}_*.pdf")
    import glob
    matches = glob.glob(pdf)
    if matches:
        print(f"  {os.path.basename(matches[0])}: {os.path.getsize(matches[0]):,d} bytes")
print("=" * 50)
