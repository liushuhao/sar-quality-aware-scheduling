#!/usr/bin/env python3
"""Monitor GA-P-BL experiment progress and data correctness."""
import json, os, sys
prog = "papers/single-sat-quality/experiments/results/b2_profit_bl/_progress.json"
if not os.path.exists(prog):
    print("Progress file not yet created")
    sys.exit(0)

d = json.load(open(prog))
c = d.get("completed", {})
print("GA-P-BL progress: {} / 300".format(len(c)))

if not c:
    sys.exit(0)

# Group stats
groups = {}
worse_than_gbl = []
infeasible = []
fallback_count = 0
for k, v in c.items():
    g = k.split("/")[0]
    groups.setdefault(g, []).append(v)
    f1 = v.get("f1_raw", 0)
    f1_gbl = v.get("f1_gbl", 0)
    if f1 < f1_gbl:
        worse_than_gbl.append((k, f1, f1_gbl))
    if not v.get("constraint_feasible", True):
        infeasible.append((k, v.get("n_constraints_failed", 0)))
    if v.get("used_gbl_fallback", False):
        fallback_count += 1

print("\nGroup breakdown:")
for g in sorted(groups.keys()):
    items = groups[g]
    f1s = [v.get("f1_raw", 0) for v in items]
    f3s = [v.get("f3", 0) for v in items]
    ns = [v.get("n_selected", 0) for v in items]
    import statistics
    print("  {}: n={}, f1={:.0f}+-{:.0f}, f3={:.3f}+-{:.3f}, n_sel={:.0f}".format(
        g, len(items), statistics.mean(f1s), statistics.stdev(f1s) if len(f1s) > 1 else 0,
        statistics.mean(f3s), statistics.stdev(f3s) if len(f3s) > 1 else 0,
        statistics.mean(ns)))

print("\nData quality:")
print("  f1 < G-BL: {} (should be 0)".format(len(worse_than_gbl)))
for k, f1, gbl in worse_than_gbl[:3]:
    print("    {}: f1={} < gbl={}".format(k, f1, gbl))
print("  infeasible: {}".format(len(infeasible)))
print("  fallback used: {}".format(fallback_count))

# Last 3 entries
print("\nLast 3:")
for k, v in list(c.items())[-3:]:
    print("  {}: f1={} n={} feas={} fb={}".format(
        k, v.get("f1_raw", 0), v.get("n_selected", 0),
        v.get("constraint_feasible", True), v.get("used_gbl_fallback", False)))
