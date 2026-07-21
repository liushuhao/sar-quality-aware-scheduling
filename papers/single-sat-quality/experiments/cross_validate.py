"""
Cross-validation script: compare paper claims with actual experiment data.
"""
import json
import os
import numpy as np
from collections import defaultdict
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, 'results')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

# ==============================================================
# 1. Load all data
# ==============================================================
stats = load_json(os.path.join(RESULTS, 'statistical_results.json'))
moea2 = load_json(os.path.join(RESULTS, 'moea_2obj', '_progress.json'))
moea3 = load_json(os.path.join(RESULTS, 'moea_3obj', '_progress.json'))
b2 = load_json(os.path.join(RESULTS, 'b2_profit_bl', '_progress.json'))
baselines = load_json(os.path.join(RESULTS, 'baselines_200.json'))

# Ablation files
ablation_files = {
    'A (full physical)': os.path.join(RESULTS, 'moea_3obj', '_progress.json'),
    'B (no squint)': os.path.join(RESULTS, 'moea_3obj_no_squint', '_progress.json'),
    'C (no incidence)': os.path.join(RESULTS, 'moea_3obj_no_incidence', '_progress.json'),
    'D (no physics)': os.path.join(RESULTS, 'moea_3obj_no_physics', '_progress.json'),
}
ablation_data = {k: load_json(v) for k, v in ablation_files.items()}

# ==============================================================
# 2. Helper: extract per-scenario f1/f2/f3 from progress files
# ==============================================================
def get_scenario_key(key):
    """Extract group (S1/S2/S3/S4) from scenario key."""
    return key.split('/')[0]

def extract_progress_values(progress_data, solver_type='moea'):
    """
    Extract per-scenario f1, f2, f3 from _progress.json.
    Returns dict: group -> list of {f1, f2, f3, n_selected, ...}
    """
    groups = defaultdict(list)
    for key, entry in progress_data['completed'].items():
        group = get_scenario_key(key)
        groups[group].append({
            'key': key,
            'f1': entry['f1'],
            'f1_raw': entry.get('f1_raw', entry['f1']),
            'f1_gbl': entry.get('f1_gbl', None),
            'f2': entry['f2'],
            'f3': entry['f3'],
            'n_selected': entry.get('n_selected', None),
            'n_targets': entry.get('n_targets', None),
        })
    return dict(groups)

# ==============================================================
# 3. Check seed counts
# ==============================================================
print("=" * 80)
print("CHECK 1: SEED COUNTS")
print("=" * 80)

for name, data in [('MOEA-2', moea2), ('MOEA-3', moea3), ('B2-GA', b2)]:
    total = len(data['completed'])
    groups = defaultdict(int)
    for key in data['completed']:
        groups[get_scenario_key(key)] += 1
    print(f"\n{name}: {total} total scenarios")
    for g in sorted(groups):
        print(f"  {g}: {groups[g]} scenarios")

# Count baseline scenarios
print(f"\nBaselines (G-BL, G-SM): {len(baselines)} total scenarios")
b_groups = defaultdict(int)
for key in baselines:
    b_groups[get_scenario_key(key)] += 1
for g in sorted(b_groups):
    print(f"  {g}: {b_groups[g]} scenarios")

# Count ablation scenarios
print(f"\nAblation variants:")
for variant, data in ablation_data.items():
    total = len(data['completed'])
    groups = defaultdict(int)
    for key in data['completed']:
        groups[get_scenario_key(key)] += 1
    print(f"  {variant}: {total} total scenarios")
    for g in sorted(groups):
        print(f"    {g}: {groups[g]} scenarios")

# ==============================================================
# 4. Check f1*, f2, f3 values from _progress.json vs paper tables
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 2: f1*, f2, f3 VALUES (Table tab:solver-profiles, S4 only)")
print("=" * 80)

# Paper claims for S4:
# G-BL:    f1*=1.00,            f2=0.580±0.025, f3=0.210±0.071
# G-SM:    f1*=0.61±0.09,       f2=0.506±0.035, f3=0.356±0.075
# GA-P-BL: f1*=1.18±0.26,       f2=0.580±0.024, f3=0.203±0.073
# MOEA-2:  f1*=0.98±0.05,       f2=0.589±0.021, f3=0.169±0.066
# MOEA-3:  f1*=0.98±0.06,       f2=0.589±0.021, f3=0.170±0.066

paper_claims_s4 = {
    'G-BL':    {'f1': (1.00, 0.00), 'f2': (0.580, 0.025), 'f3': (0.210, 0.071)},
    'G-SM':    {'f1': (0.61, 0.09),  'f2': (0.506, 0.035), 'f3': (0.356, 0.075)},
    'GA-P-BL': {'f1': (1.18, 0.26),  'f2': (0.580, 0.024), 'f3': (0.203, 0.073)},
    'MOEA-2':  {'f1': (0.98, 0.05),  'f2': (0.589, 0.021), 'f3': (0.169, 0.066)},
    'MOEA-3':  {'f1': (0.98, 0.06),  'f2': (0.589, 0.021), 'f3': (0.170, 0.066)},
}

# G-BL from baselines (b1)
# G-SM from baselines (b3)
b1_s4 = []
b3_s4 = []
for key, entry in baselines.items():
    if get_scenario_key(key) == 'S4':
        b1_s4.append(entry['b1'])
        b3_s4.append(entry['b3'])

b1_f1 = [e['f1'] for e in b1_s4]
b1_f2 = [e['f2'] for e in b1_s4]
b1_f3 = [e['f3'] for e in b1_s4]

b3_f1 = [e['f1'] for e in b3_s4]
b3_f2 = [e['f2'] for e in b3_s4]
b3_f3 = [e['f3'] for e in b3_s4]

print(f"\nG-BL (S4, n={len(b1_s4)}):")
print(f"  f1* = {np.mean(b1_f1):.4f} ± {np.std(b1_f1):.4f}  (paper: 1.00 ± 0.00)")
print(f"  f2  = {np.mean(b1_f2):.4f} ± {np.std(b1_f2):.4f}  (paper: 0.580 ± 0.025)")
print(f"  f3  = {np.mean(b1_f3):.4f} ± {np.std(b1_f3):.4f}  (paper: 0.210 ± 0.071)")

print(f"\nG-SM (S4, n={len(b3_s4)}):")
print(f"  f1* = {np.mean(b3_f1):.4f} ± {np.std(b3_f1):.4f}  (paper: 0.61 ± 0.09)")
print(f"  f2  = {np.mean(b3_f2):.4f} ± {np.std(b3_f2):.4f}  (paper: 0.506 ± 0.035)")
print(f"  f3  = {np.mean(b3_f3):.4f} ± {np.std(b3_f3):.4f}  (paper: 0.356 ± 0.075)")

# GA-P-BL (b2_profit_bl)
b2_groups = extract_progress_values(b2, 'single')
b2_s4 = b2_groups.get('S4', [])
b2_f1 = [e['f1'] for e in b2_s4]
b2_f2 = [e['f2'] for e in b2_s4]
b2_f3 = [e['f3'] for e in b2_s4]
print(f"\nGA-P-BL (S4, n={len(b2_s4)}):")
print(f"  f1* = {np.mean(b2_f1):.4f} ± {np.std(b2_f1):.4f}  (paper: 1.18 ± 0.26)")
print(f"  f2  = {np.mean(b2_f2):.4f} ± {np.std(b2_f2):.4f}  (paper: 0.580 ± 0.024)")
print(f"  f3  = {np.mean(b2_f3):.4f} ± {np.std(b2_f3):.4f}  (paper: 0.203 ± 0.073)")

# MOEA-2
m2_groups = extract_progress_values(moea2)
m2_s4 = m2_groups.get('S4', [])
m2_f1 = [e['f1'] for e in m2_s4]
m2_f2 = [e['f2'] for e in m2_s4]
m2_f3 = [e['f3'] for e in m2_s4]
print(f"\nMOEA-2 (S4, n={len(m2_s4)}):")
print(f"  f1* = {np.mean(m2_f1):.4f} ± {np.std(m2_f1):.4f}  (paper: 0.98 ± 0.05)")
print(f"  f2  = {np.mean(m2_f2):.4f} ± {np.std(m2_f2):.4f}  (paper: 0.589 ± 0.021)")
print(f"  f3  = {np.mean(m2_f3):.4f} ± {np.std(m2_f3):.4f}  (paper: 0.169 ± 0.066)")

# MOEA-3
m3_groups = extract_progress_values(moea3)
m3_s4 = m3_groups.get('S4', [])
m3_f1 = [e['f1'] for e in m3_s4]
m3_f2 = [e['f2'] for e in m3_s4]
m3_f3 = [e['f3'] for e in m3_s4]
print(f"\nMOEA-3 (S4, n={len(m3_s4)}):")
print(f"  f1* = {np.mean(m3_f1):.4f} ± {np.std(m3_f1):.4f}  (paper: 0.98 ± 0.06)")
print(f"  f2  = {np.mean(m3_f2):.4f} ± {np.std(m3_f2):.4f}  (paper: 0.589 ± 0.021)")
print(f"  f3  = {np.mean(m3_f3):.4f} ± {np.std(m3_f3):.4f}  (paper: 0.170 ± 0.066)")

# ==============================================================
# 5. Check Table tab:scale-sensitivity
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 3: SCALE SENSITIVITY (Table tab:scale-sensitivity)")
print("=" * 80)

# Compute G-BL f2 per group (from baselines)
gbl_f2_by_group = defaultdict(list)
for key, entry in baselines.items():
    g = get_scenario_key(key)
    gbl_f2_by_group[g].append(entry['b1']['f2'])

# Compute MOEA-2 f1* and f2 per group
for g in ['S1', 'S2', 'S3', 'S4']:
    m2_g = m2_groups.get(g, [])
    m2_f1_g = [e['f1'] for e in m2_g]
    m2_f2_g = [e['f2'] for e in m2_g]
    gbl_f2_g = gbl_f2_by_group.get(g, [])
    
    m2_f1_mean = np.mean(m2_f1_g)
    m2_f1_std = np.std(m2_f1_g)
    m2_f2_mean = np.mean(m2_f2_g)
    gbl_f2_mean = np.mean(gbl_f2_g)
    
    pct_improvement = (m2_f2_mean - gbl_f2_mean) / gbl_f2_mean * 100
    pct_active_tradeoff = sum(1 for f in m2_f1_g if f < 0.95) / len(m2_f1_g) * 100
    
    print(f"\n{g}:")
    print(f"  MOEA-2 f1* = {m2_f1_mean:.4f} ± {m2_f1_std:.4f}")
    print(f"  MOEA-2 f2  = {m2_f2_mean:.4f}")
    print(f"  G-BL f2    = {gbl_f2_mean:.4f}")
    print(f"  f2 improvement = {pct_improvement:+.1f}%")
    print(f"  % f1* < 0.95  = {pct_active_tradeoff:.0f}%")

# Paper claims:
# S1: f1*=0.69±0.30, +8.0%, 82%
# S2: f1*=0.83±0.23, +4.4%, 64%
# S3: f1*=0.97±0.04, +1.6%, 14%
# S4: f1*=0.98±0.05, +1.5%, 20%

# ==============================================================
# 6. Check HV table (tab:hv)
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 4: HYPERVOLUME TABLE (Table tab:hv)")
print("=" * 80)

paper_hv = {
    'G-SM':    (0.188, 0.041),
    'MOEA-3':  (0.163, 0.043),
    'MOEA-2':  (0.158, 0.037),
    'G-BL':    (0.129, 0.018),
    'GA-P-BL': (0.108, 0.033),
}

print("\nActual HV from statistical_results.json:")
for solver, info in stats['hv_by_solver'].items():
    print(f"  {solver}: mean={info['mean']:.4f}, std={info['std']:.4f}")

print("\nPaper claims vs actual:")
for solver, (p_mean, p_std) in paper_hv.items():
    actual = stats['hv_by_solver'].get(solver, {})
    if actual:
        a_mean = actual['mean']
        a_std = actual['std']
        delta_mean = a_mean - p_mean
        print(f"  {solver}: paper={p_mean:.3f}±{p_std:.3f}, actual={a_mean:.3f}±{a_std:.3f}, Δ={delta_mean:+.3f}")

# ==============================================================
# 7. Check Friedman / Wilcoxon stats
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 5: FRIEDMAN / WILCOXON STATISTICS")
print("=" * 80)

print(f"\nFriedman test:")
print(f"  Paper: χ²=517.54, p≈10^(-110)")
print(f"  Actual: statistic={stats['friedman']['statistic']:.4f}, p={stats['friedman']['p_value']:.4e}")

print(f"\nMOEA-2 vs MOEA-3 (paper claims δ=-0.14, p=0.0014):")
mw = stats['pairwise_wilcoxon']['MOEA-2_vs_MOEA-3']
print(f"  Actual: statistic={mw['statistic']}, p={mw['p_value']:.6e}, cliffs_delta={mw['cliffs_delta']}")
print(f"  greater={mw['greater']}, less={mw['less']}, equal={mw['equal']}")

# ==============================================================
# 8. Check MOEA-2 vs MOEA-3 near-identity
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 6: MOEA-2 vs MOEA-3 NEAR-IDENTITY")
print("=" * 80)

# Compare per-scenario f1, f2, f3 values
all_m2_keys = set(moea2['completed'].keys())
all_m3_keys = set(moea3['completed'].keys())
common_keys = all_m2_keys & all_m3_keys

m2_f1_all = []
m3_f1_all = []
m2_f2_all = []
m3_f2_all = []
m2_f3_all = []
m3_f3_all = []

for key in common_keys:
    m2_f1_all.append(moea2['completed'][key]['f1'])
    m3_f1_all.append(moea3['completed'][key]['f1'])
    m2_f2_all.append(moea2['completed'][key]['f2'])
    m3_f2_all.append(moea3['completed'][key]['f2'])
    m2_f3_all.append(moea2['completed'][key]['f3'])
    m3_f3_all.append(moea3['completed'][key]['f3'])

m2_f1_arr = np.array(m2_f1_all)
m3_f1_arr = np.array(m3_f1_all)
m2_f2_arr = np.array(m2_f2_all)
m3_f2_arr = np.array(m3_f2_all)
m2_f3_arr = np.array(m2_f3_all)
m3_f3_arr = np.array(m3_f3_all)

print(f"\nPaired scenarios: {len(common_keys)}")
print(f"\nf1* comparison:")
print(f"  MOEA-2 mean = {np.mean(m2_f1_arr):.4f} ± {np.std(m2_f1_arr):.4f}")
print(f"  MOEA-3 mean = {np.mean(m3_f1_arr):.4f} ± {np.std(m3_f1_arr):.4f}")
diff_f1 = m2_f1_arr - m3_f1_arr
print(f"  Mean diff (M2-M3) = {np.mean(diff_f1):.4f} ± {np.std(diff_f1):.4f}")
print(f"  Correlation = {np.corrcoef(m2_f1_arr, m3_f1_arr)[0,1]:.4f}")

print(f"\nf2 comparison:")
print(f"  MOEA-2 mean = {np.mean(m2_f2_arr):.4f} ± {np.std(m2_f2_arr):.4f}")
print(f"  MOEA-3 mean = {np.mean(m3_f2_arr):.4f} ± {np.std(m3_f2_arr):.4f}")
diff_f2 = m2_f2_arr - m3_f2_arr
print(f"  Mean diff (M2-M3) = {np.mean(diff_f2):.4f} ± {np.std(diff_f2):.4f}")
print(f"  Correlation = {np.corrcoef(m2_f2_arr, m3_f2_arr)[0,1]:.4f}")

print(f"\nf3 comparison:")
print(f"  MOEA-2 mean = {np.mean(m2_f3_arr):.4f} ± {np.std(m2_f3_arr):.4f}")
print(f"  MOEA-3 mean = {np.mean(m3_f3_arr):.4f} ± {np.std(m3_f3_arr):.4f}")
diff_f3 = m2_f3_arr - m3_f3_arr
print(f"  Mean diff (M2-M3) = {np.mean(diff_f3):.4f} ± {np.std(diff_f3):.4f}")
print(f"  Correlation = {np.corrcoef(m2_f3_arr, m3_f3_arr)[0,1]:.4f}")

# ==============================================================
# 9. Ablation table check
# ==============================================================
print("\n" + "=" * 80)
print("CHECK 7: ABLATION TABLE (Table tab:ablation)")
print("=" * 80)

# The ablation data has f1 as raw profit, not normalized f1*.
# We need to normalize using G-BL baseline from baselines_200.json
# Build a lookup of G-BL profit per scenario

gbl_profit = {}
for key, entry in baselines.items():
    gbl_profit[key] = entry['b1']['f1_raw']

for variant_name, data in ablation_data.items():
    print(f"\n--- {variant_name} ---")
    variant_groups = defaultdict(list)
    for key, entry in data['completed'].items():
        group = get_scenario_key(key)
        # Normalize f1: f1* = raw_profit / gbl_profit
        raw_f1 = entry.get('f1_raw', entry['f1'])
        # Handle the ablation data format issue
        f1_gbl = entry.get('f1_gbl', None)
        if f1_gbl is not None and f1_gbl > 1.0:
            # Normal format: f1 is already normalized
            f1_star = entry['f1'] if entry['f1'] <= 2.0 else entry['f1'] / f1_gbl
        else:
            # Ablation format issue: f1 is raw, need to normalize
            gbl_key = key  # Same scenario key
            if gbl_key in gbl_profit:
                f1_star = raw_f1 / gbl_profit[gbl_key]
            else:
                f1_star = raw_f1  # fallback
        
        n_sel = entry.get('n_selected', 0)
        n_tar = entry.get('n_targets', 0)
        f1_per_task = raw_f1 / n_sel if n_sel > 0 else 0
        
        variant_groups[group].append({
            'f1_star': f1_star,
            'f2': entry['f2'],
            'f3': entry['f3'],
            'n_sel': n_sel,
            'n_tar': n_tar,
            'f1_per_task': f1_per_task,
        })
    
    for g in ['S1', 'S2', 'S3', 'S4']:
        items = variant_groups.get(g, [])
        if not items:
            continue
        f1s = [it['f1_star'] for it in items]
        f2s = [it['f2'] for it in items]
        f3s = [it['f3'] for it in items]
        n_sels = [it['n_sel'] for it in items]
        f1_pts = [it['f1_per_task'] for it in items]
        
        print(f"  {g} (n={len(items)}):")
        print(f"    f1* = {np.mean(f1s):.4f} ± {np.std(f1s):.4f}")
        print(f"    f2  = {np.mean(f2s):.4f}")
        print(f"    f3  = {np.mean(f3s):.4f}")
        print(f"    f1/n = {np.mean(f1_pts):.4f} ± {np.std(f1_pts):.4f}")
        print(f"    n_sel = {np.mean(n_sels):.1f} ± {np.std(n_sels):.1f}")

# ==============================================================
# 10. Summary
# ==============================================================
print("\n" + "=" * 80)
print("SUMMARY OF DISCREPANCIES")
print("=" * 80)
