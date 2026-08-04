"""Verify scenario pkl files: counts, structure, and window alignment."""
import sys, pickle
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

SCENARIOS_DIR = Path(__file__).resolve().parent / "scenarios"

GROUPS_EXPECTED = {
    "S1": 50, "S2": 50, "S3": 50, "S4": 50,
    "S5": 50, "S6": 50, "S7": 50, "S8": 50,
}
TOTAL_EXPECTED = sum(GROUPS_EXPECTED.values())  # 400

print("=" * 70)
print("SCENARIO PKL VERIFICATION")
print("=" * 70)

# ── 1. Count pkls per group ──
print("\n[1] Pkl counts per group:")
total = 0
counts = {}
for group in sorted(GROUPS_EXPECTED.keys()):
    gdir = SCENARIOS_DIR / group
    if not gdir.exists():
        print(f"  {group}: MISSING dir")
        counts[group] = 0
        continue
    pkls = sorted(gdir.glob("*.pkl"))
    counts[group] = len(pkls)
    total += len(pkls)
    expected = GROUPS_EXPECTED[group]
    status = "OK" if len(pkls) == expected else f"MISMATCH (expected {expected})"
    print(f"  {group}: {len(pkls)} pkls - {status}")
print(f"  TOTAL: {total} (expected {TOTAL_EXPECTED})")

if total != TOTAL_EXPECTED:
    print("\n!!! Total count mismatch - regeneration needed !!!")
    sys.exit(1)

# ── 2. Subconfig distribution per group ──
print("\n[2] Subconfig distribution per group:")
for group in sorted(GROUPS_EXPECTED.keys()):
    gdir = SCENARIOS_DIR / group
    pkls = sorted(gdir.glob("*.pkl"))
    sub_counts = Counter()
    for p in pkls:
        # e.g. "S1-A_seed00.pkl" -> "S1-A"
        parts = p.stem.split("_seed")
        if parts:
            sub_counts[parts[0]] += 1
    subs = dict(sub_counts)
    print(f"  {group}: {subs}")

# ── 3. Sample one pkl per group for structure check ──
print("\n[3] Sample structure check (one pkl per group):")
required_keys = {"targets", "windows", "windows_by_target", "instrument",
                 "n_targets", "seed", "stats", "satellite", "config"}
all_ok = True
for group in sorted(GROUPS_EXPECTED.keys()):
    gdir = SCENARIOS_DIR / group
    pkls = sorted(gdir.glob("*.pkl"))
    if not pkls:
        continue
    sample = pkls[0]
    with open(sample, "rb") as f:
        data = pickle.load(f)
    keys = set(data.keys())
    missing = required_keys - keys
    if missing:
        print(f"  {group}/{sample.name}: MISSING keys {missing}")
        all_ok = False
        continue
    stats = data["stats"]
    sat = data["satellite"]
    print(f"  {group}/{sample.name}: "
          f"n_targets={data['n_targets']}, "
          f"alt={sat['altitude_km']}km, "
          f"n_windows={stats['total_windows']}, "
          f"visible={stats['n_with_windows']}/{stats['n_targets_total']}")

if not all_ok:
    print("\n!!! Structure check FAILED !!!")
    sys.exit(1)

# ── 4. Window time alignment check (10s grid) ──
print("\n[4] Window time alignment to 10s grid (3 samples per group):")
ALIGNMENT_S = 10
EPOCH = datetime(2026, 6, 15, 0, 0, 0)

def is_aligned(dt, step_s=ALIGNMENT_S, epoch=EPOCH):
    if dt is None:
        return False
    delta = (dt - epoch).total_seconds()
    # Round to nearest 1 second to avoid float noise
    delta_round = round(delta)
    return (delta_round % step_s) == 0

alignment_issues = 0
sim_boundary_endings = 0  # windows whose t_end equals simulation t_end (expected)
total_windows_checked = 0
for group in sorted(GROUPS_EXPECTED.keys()):
    gdir = SCENARIOS_DIR / group
    pkls = sorted(gdir.glob("*.pkl"))
    # Check 3 samples per group
    sample_indices = [0, len(pkls)//2, len(pkls)-1]
    group_issues = 0
    group_boundary = 0
    group_windows = 0
    for idx in sample_indices:
        with open(pkls[idx], "rb") as f:
            data = pickle.load(f)
        sim_t_end = data["config"]["t_end"]  # simulation end time
        for w in data["windows"]:
            group_windows += 1
            # If t_end == simulation t_end, it's an expected boundary, skip
            if w.t_end == sim_t_end:
                group_boundary += 1
                continue
            # Check t_start, t_end, t_optimal alignment
            if not is_aligned(w.t_start):
                group_issues += 1
                if group_issues <= 2:
                    print(f"  {group}/{pkls[idx].name}: t_start NOT aligned: {w.t_start}")
            elif not is_aligned(w.t_end):
                group_issues += 1
                if group_issues <= 2:
                    print(f"  {group}/{pkls[idx].name}: t_end NOT aligned: {w.t_end}")
            elif not is_aligned(w.t_optimal):
                group_issues += 1
                if group_issues <= 2:
                    print(f"  {group}/{pkls[idx].name}: t_optimal NOT aligned: {w.t_optimal}")
    total_windows_checked += group_windows
    alignment_issues += group_issues
    sim_boundary_endings += group_boundary
    status = "OK" if group_issues == 0 else f"{group_issues} misaligned"
    print(f"  {group}: {group_windows} windows checked - {status} ({group_boundary} sim-boundary)")

print(f"\n  Total windows checked: {total_windows_checked}")
print(f"  Total misaligned: {alignment_issues}")

# ── 5. Altitude and instrument consistency ──
print("\n[5] Altitude/instrument consistency (all groups):")
altitudes = set()
incidence_ranges = set()
for group in sorted(GROUPS_EXPECTED.keys()):
    gdir = SCENARIOS_DIR / group
    pkls = sorted(gdir.glob("*.pkl"))
    if not pkls:
        continue
    with open(pkls[0], "rb") as f:
        data = pickle.load(f)
    altitudes.add(data["satellite"]["altitude_km"])
    inst = data["instrument"]
    incidence_ranges.add((inst.incidence_min, inst.incidence_max))
print(f"  Altitudes seen: {altitudes}")
print(f"  Incidence ranges seen: {incidence_ranges}")

# ── 6. Summary ──
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"  Total pkls: {total}/{TOTAL_EXPECTED}")
print(f"  Structure check: {'PASS' if all_ok else 'FAIL'}")
print(f"  Window alignment: {'PASS' if alignment_issues == 0 else f'FAIL ({alignment_issues} issues)'}")
print(f"  Altitudes: {altitudes}")
print(f"  Incidence ranges: {incidence_ranges}")
ok = (total == TOTAL_EXPECTED) and all_ok and (alignment_issues == 0)
print(f"\n  OVERALL: {'PASS - ready for experiments' if ok else 'FAIL - needs regeneration'}")
sys.exit(0 if ok else 1)
